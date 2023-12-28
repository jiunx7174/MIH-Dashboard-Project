import streamlit as st
from PDU_Func import Authentification, IO_Data
from Page import ActivityMapping,  ActivityVisualization
from Page import Welcome, PageNotFound
from importlib import reload
import streamlit_ext as ste
reload(ActivityMapping)
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

def showUserInfo(UserAuthDict, container):
    container.markdown("# RTDC App")

    user_info = f"""
    {UserAuthDict["user_name"]} ({UserAuthDict["user_id"]})\n
    {UserAuthDict["user_email"]}\n
    {UserAuthDict["user_company_name"]}\n
    """

    container.markdown(user_info)





st.set_page_config(
    page_title="RTDC App",
    # initial_sidebar_state=st.session_state.sidebar_state, 
    page_icon=None, layout="wide",)

query_params = st.experimental_get_query_params()
UserAuthDict = Authentification.getUserID(query_params)

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

# TODO:
# * add User Module auth


with MenuNavigationContainer:
    AppName = sac.menu([
        sac.MenuItem(type='divider'),
        sac.MenuItem('home', icon='house-fill'),
        sac.MenuItem('Activity Mapping', icon='bi bi-table', disabled=(SelectWell==None or SelectWell=='-')),
        # sac.MenuItem('Activity Mappingx', icon='bi bi-ui-checks'),
        sac.MenuItem('Dashboard', icon='bi bi-graph-up', disabled=(SelectWell==None or SelectWell=='-')),
    ], format_func='title',size='small',index=1, open_all=True, key='Menu')

AppDict = {
    'home': Welcome.App,
    'Activity Mapping': ActivityMapping.App,
    'Dashboard': ActivityVisualization.App,
}

AppDict[AppName]()

# st.write(out)