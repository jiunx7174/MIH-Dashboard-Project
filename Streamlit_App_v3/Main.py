import streamlit as st
from PDU_Func import Authentification, IO_Data
from Page import ActivityMapping,  ActivityVisualization, Override, DataAnalytics
from Page import Welcome, PageNotFound
from importlib import reload
import streamlit_ext as ste
reload(ActivityMapping)
reload(ActivityVisualization)
reload(Override)
reload(DataAnalytics)
# reload(ComponentTest)
# reload(ActivityDatabase)
# reload(ComponentTest)

import streamlit_antd_components as sac
# def showUserInfo(UserAuthDict, container):
#     container.markdown("# RTDC App")

#     container.markdown("#### User: ")
#     container.text(UserAuthDict["user_name"] + "(" + UserAuthDict["user_id"] + ")")

#     container.markdown("#### Email: ")
#     container.text(UserAuthDict["user_email"])

#     container.markdown("#### Company: ")
#     container.text(UserAuthDict["user_company_name"])
def setPage(buttonName):
    st.session_state['AppName'] = buttonName
def showUserInfo(UserAuthDict, container):
    container.markdown("# RTDC App")

    user_info = f"""
    {UserAuthDict["user_name"]} ({UserAuthDict["user_id"]})\n
    {UserAuthDict["user_email"]}\n
    {UserAuthDict["user_company_name"]}\n
    """

    container.markdown(user_info)

    # st.markdown("""
    # <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
    # <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>
    # <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>
    # """, unsafe_allow_html=True)



st.set_page_config(
    page_title="RTDC App",
    # initial_sidebar_state=st.session_state.sidebar_state, 
    page_icon=None, layout="wide",)
# addHeader()

# query_params = st.experimental_get_query_params()
query_params = st.query_params
UserAuthDict = Authentification.getUserID(query_params)
st.session_state['UserAuthDict'] = UserAuthDict

if UserAuthDict['verification'] != 'verified':
    PageNotFound.App()
# * Display User Info in sidebar
UserInfoContainer = st.sidebar.container()
showUserInfo(UserAuthDict['data'], UserInfoContainer)

# ModuleSidebarContainer = st.sidebar.container()
MenuNavigationContainer = st.sidebar.container()
SelCompWellContainer = st.sidebar.container()

# with SidebarContainer:
AvailComp_DF = IO_Data.getAvailableCompanyDF(UserAuthDict)
SelectWell = None
SelectComp = None
with SelCompWellContainer:
    SelectComp = ste.selectbox("Select Company",AvailComp_DF['company_name'].tolist(), index=None, key='SelComp')
    if SelectComp != None:
        AvailWell_DF = IO_Data.getAvailableWellDF(SelectComp, UserAuthDict)
        SelectWell = ste.selectbox("Select Well",['-'] + AvailWell_DF['well_name'].tolist(), index=None,key='SelWell')
    else:
        st.sidebar.warning("Please select a company")
# if SelectWell == None:
#     st.warning("Please select a well")
#     st.stop()

# TODO:
# * add User Module auth
# if ('BeforeAppName' not in st.session_state) or (SelectWell==None or SelectWell=='-'):
#     st.session_state.BeforeAppName = 'Home'
# # else:
# st.session_state.AppName = str(st.session_state.BeforeAppName)
# st.sidebar.dataframe(AvailWell_DF[AvailWell_DF['well_name']==SelectWell][['well_name', 'rig_name', 'active_date', 'end_date']].T)
# st.write(st.session_state.Menu)
listbutton = ['Home', 'Activity Mapping', 'Dashboard', 'Data Analytics']
# if 'AppName' in st.session_state:
#     if st.session_state.AppName is '':
#         st.session_state.AppName = 'Home'
#     st.write(st.session_state.AppName)
#     SelMenu = st.session_state['AppName']
# else:
#     SelMenu = 'Home'
# if SelMenu is '':
#     SelMenu = 'Home'

# if 'BeforeAppName' in st.session_state:
#     st.session_state['AppName'] = st.session_state['BeforeAppName']
with MenuNavigationContainer:

    AppName  = sac.menu([
        sac.MenuItem(type='divider'),
        sac.MenuItem('Home', icon='house-fill'),
        sac.MenuItem('Activity Mapping', icon='bi bi-table', disabled=(SelectWell==None or SelectWell=='-')),
        # sac.MenuItem('Activity Mappingx', icon='bi bi-ui-checks'),
        sac.MenuItem('Dashboard', icon='bi bi-graph-up', disabled=(SelectWell==None or SelectWell=='-')),
        # sac.MenuItem('Data Analytics', icon='bi bi-motherboard', disabled=(SelectWell==None or SelectWell=='-')),
        # sac.MenuItem('Override Activity', icon='bi bi-motherboard', disabled=(SelectWell==None or SelectWell=='-')),
    ], format_func='title',size='small', open_all=True,key='AppName')
# st.write(f"Selected Menu: {AppName}")
if AppName is '':
    AppName = 'Home'
if SelectComp != None and SelectWell == None:
    st.sidebar.warning("Please select a well")
    st.stop()
AppDict = {
    'Home': Welcome.App,
    'Activity Mapping': ActivityMapping.App,
    'Dashboard': ActivityVisualization.App,
    'Data Analytics': DataAnalytics.App,
    'Override Activity': Override.App,
}
# st.session_state['BeforeAppName'] = AppName
AppDict[AppName]()

# st.write(out)