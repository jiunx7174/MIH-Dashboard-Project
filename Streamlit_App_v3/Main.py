import sys
# Write print() output to the Docker log line by line instead of in 8 KB blocks,
# so log timestamps match when things happened (same effect as PYTHONUNBUFFERED=1).
try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass
import time
import streamlit as st
from PDU_Func import AppLog
# Application log: Logs/app_streamlit.jsonl + Logs/errors_streamlit.jsonl
# (see Tools/LOGGING.md). setup() runs once per process; every script run below
# gets its own run_id, which is also the error code shown to the user.
AppLog.setup("streamlit")
from PDU_Func import Authentification, IO_Data
from Page import ActivityMapping,  ActivityVisualization, Override, DataAnalytics
from Page import Welcome, PageNotFound
from importlib import reload
import streamlit_ext as ste
def showUserInfo(UserAuthDict, container):
    container.markdown("# RTDC App")

    user_info = f"""
    {UserAuthDict["user_name"]} ({UserAuthDict["user_id"]})\n
    {UserAuthDict["user_email"]}\n
    {UserAuthDict["user_company_name"]}\n
    """
    if 'streamlit_version' in UserAuthDict:
        user_info += f"{UserAuthDict['streamlit_version']}\n"


    container.markdown(user_info)
def init_session():
    if 'AppName' not in st.session_state:
        st.session_state['AppName'] = 'Home'

def changeCompWell():
    list_query_params = [
        'StrtDateRT',
        'StrtTimeRT',
        'EndDateRT',
        'EndTimeRT',
    ]
    for i in list_query_params:
        if i in st.query_params:
            del st.query_params[i]

    list_del = [
        'SectionParamsTable_DataEditor',
        'SectionParamsTable_df',
        'StrtDateRT',
        'StrtTimeRT',
        'EndDateRT',
        'EndTimeRT',
        ]
    for i in list_del:
        if i in st.session_state:
            del st.session_state[i]
    if 'SelComp' in st.session_state:
        st.query_params['SelComp'] = st.session_state['SYNC_SelComp']
    if 'SelWell' in st.session_state:
        st.query_params['SelWell'] = st.session_state['SYNC_SelWell']

    

def setPage(AppName):
    st.session_state['AppName'] = AppName

init_session()


def _session_hash():
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        return AppLog.hash_id(get_script_run_ctx().session_id)
    except Exception:
        return None


_RUN_T0 = time.time()
AppLog.reset_context(run_id=AppLog.new_id(), session=_session_hash(), page=st.session_state['AppName'])
st.set_page_config(
    page_title="RTDC App",
    # initial_sidebar_state=st.session_state.sidebar_state, 
    page_icon=None, layout="wide",)

query_params = st.query_params
UserAuthDict = IO_Data.call_or_stop("Verifikasi login ke DOME", Authentification.getUserID, query_params)
st.session_state['UserAuthDict'] = UserAuthDict
try:
    # who is using the page; the login token (?ID=) and the email are never logged
    AppLog.bind(user_name=UserAuthDict['data'].get('user_name'),
                user_id=UserAuthDict['data'].get('user_id'),
                user_company=UserAuthDict['data'].get('user_company_name'))
except Exception:
    AppLog.bind(user_name="unverified")
if UserAuthDict['verification'] != 'verified':
    # st.stop()
    PageNotFound.App()

UserInfoContainer = st.sidebar.container()
MenuNavigationContainer = st.sidebar.container(border=False)
SelCompWellContainer = st.sidebar.container()


showUserInfo(UserAuthDict['data'], UserInfoContainer)

# with SidebarContainer:
AvailComp_DF = IO_Data.call_or_stop("Memuat daftar company dari DOME", IO_Data.getAvailableCompanyDF, UserAuthDict)
SelectWell = None
SelectComp = None
with SelCompWellContainer:

    SelectComp = ste.selectbox("Select Company",AvailComp_DF['company_name'].tolist(), index=None, key='SelComp', on_change=changeCompWell)
    st.session_state['SelComp'] = st.session_state['SYNC_SelComp'] 
    if SelectComp != None:
        AvailWell_DF = IO_Data.call_or_stop("Memuat daftar well dari DOME", IO_Data.getAvailableWellDF, SelectComp, UserAuthDict)

        SelectWell = ste.selectbox("Select Well", AvailWell_DF['well_name'].tolist(), index=None,key='SelWell', on_change=changeCompWell)
        st.session_state['SelWell'] = st.session_state['SYNC_SelWell']

        if SelectWell == None:
            st.warning("Please select a well")
    else:
        st.sidebar.warning("Please select a company")


with MenuNavigationContainer:

    st.button('Home', use_container_width=True, key='Home', 
              on_click=setPage, args=('Home',), type='primary' if st.session_state['AppName'] == 'Home' else 'secondary')
    st.button('Activity Mapping', use_container_width=True, key='Activity Mapping', disabled=(SelectWell==None or SelectWell=='-'),
              on_click=setPage, args=('Activity Mapping',), type='primary' if st.session_state['AppName'] == 'Activity Mapping' else 'secondary')
    st.button('Dashboard', use_container_width=True, key='Dashboard', disabled=(SelectWell==None or SelectWell=='-'),
              on_click=setPage, args=('Dashboard',), type='primary' if st.session_state['AppName'] == 'Dashboard' else 'secondary')
    
    # st.button('Override', use_container_width=True, key='Override', disabled=(SelectWell==None or SelectWell=='-'),
    #           on_click=setPage, args=('Override',), type='primary' if st.session_state['AppName'] == 'Override' else 'secondary')

if (SelectWell == None) or (SelectWell == None):
    st.stop()
# st.write(st.session_state)
AppDict = {
    'Home': Welcome.App,
    'Activity Mapping': ActivityMapping.App,
    'Dashboard': ActivityVisualization.App,
    'Data Analytics': DataAnalytics.App,
    # 'Override': Override.App,
}
AppLog.bind(page=st.session_state['AppName'], company=SelectComp, well=SelectWell)
_outcome = "stopped"          # st.stop()/st.rerun() end the run without returning
try:
    AppDict[st.session_state['AppName']]()
    _outcome = "ok"
except Exception as e:
    if type(e).__module__.startswith("streamlit"):
        raise
    _outcome = "error"
    _code = AppLog.exception("page_error", e)
    st.error(
        f"Terjadi error di halaman **{st.session_state['AppName']}**.\n\n"
        f"Detail: `{type(e).__name__}: {str(e)[:300]}`\n\n"
        f"Kode error: `{_code}` (sebutkan kode ini saat melapor; detail lengkap ada di log server)."
    )
finally:
    _dur = int((time.time() - _RUN_T0) * 1000)
    AppLog.event("page_run", level="warning" if _dur > 120000 else "info",
                 outcome=_outcome, duration_ms=_dur, slow=_dur > 120000 or None)
