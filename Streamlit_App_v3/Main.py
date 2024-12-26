import streamlit as st
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
        st.query_params['SelComp'] = st.session_state['SelComp']
    if 'SelWell' in st.session_state:
        st.query_params['SelWell'] = st.session_state['SelWell']
    #     if st.session_state['SelComp'] == None:
    #         try:
    #             del st.session_state['SelComp']
    #             del st.query_params['SelComp']
    #         except:

            
    # if 'SelWell' in st.session_state:
    #     if st.session_state['SelWell'] == None:
    #         try:
    #             del st.session_state['SelWell']
    #             del st.query_params['SelWell']
    #         except:
    #             st.query_params['SelWell'] = st.session_state['SelWell']
    #     # st.query_params['SelWell'] = st.session_state['SelWell']

    # st.rerun()
    

def setPage(AppName):
    st.session_state['AppName'] = AppName
init_session()
st.set_page_config(
    page_title="RTDC App",
    # initial_sidebar_state=st.session_state.sidebar_state, 
    page_icon=None, layout="wide",)

query_params = st.query_params
UserAuthDict = Authentification.getUserID(query_params)
st.session_state['UserAuthDict'] = UserAuthDict
if UserAuthDict['verification'] != 'verified':
    # st.stop()
    PageNotFound.App()

UserInfoContainer = st.sidebar.container()
MenuNavigationContainer = st.sidebar.container(border=False)
SelCompWellContainer = st.sidebar.container()


showUserInfo(UserAuthDict['data'], UserInfoContainer)

# with SidebarContainer:
AvailComp_DF = IO_Data.getAvailableCompanyDF(UserAuthDict)
SelectWell = None
SelectComp = None
with SelCompWellContainer:
    # try:
    #     indexComp = AvailComp_DF['company_name'].tolist().index(st.query_params['SelComp']) if 'SelComp' in st.query_params else None
    # except:
    #     indexComp = None
    # if 'SelComp' in st.query_params:
    #     st.session_state['SelComp'] = st.query_params['SelComp']
    # indexComp = None
    SelectComp = ste.selectbox("Select Company",AvailComp_DF['company_name'].tolist(), index=None, key='SelComp', on_change=changeCompWell)
    if SelectComp != None:
        AvailWell_DF = IO_Data.getAvailableWellDF(SelectComp, UserAuthDict)
        # if 'SelWell' in st.query_params:
        #     st.session_state['SelWell'] = st.query_params['SelWell']

        # try:
        #     indexWell = AvailWell_DF['well_name'].tolist().index(st.query_params['SelWell']) if 'SelWell' in st.query_params else None
        # except:
        #     indexWell = None
        # indexWell = None


        SelectWell = ste.selectbox("Select Well", AvailWell_DF['well_name'].tolist(), index=None,key='SelWell', on_change=changeCompWell)

        if SelectWell == None:
            st.warning("Please select a well")
    else:
        st.sidebar.warning("Please select a company")


# AppDict = {
#     'Home': [st.Page(Welcome.App, title='Home', icon='🏠')],
#     'Activity Mapping': [st.Page(ActivityMapping.App, title='ActivityMapping', icon='🗺️')],
#     'Dashboard': [st.Page(ActivityVisualization.App, title='Dashboard', icon='📊')],
#     # 'Data Analytics': DataAnalytics.App,
#     # 'Override Activity': Override.App,
# }

# with st.container():
#     pg = st.navigation(
#         [st.Page(Welcome.App, title='Home', icon='🏠', url_path='Home'),
#         st.Page(ActivityMapping.App, title='Activity Mapping', icon='🗺️', url_path='ActivityMapping'),
#         st.Page(ActivityVisualization.App, title='Dashboard', icon='📊', url_path='Dashboard'),
#         ]
#     )
#     pg.run()
with MenuNavigationContainer:
    # st.divider()
    # st.caption("Select M")
    st.button('Home', use_container_width=True, key='Home', 
              on_click=setPage, args=('Home',), type='primary' if st.session_state['AppName'] == 'Home' else 'secondary')
    st.button('Activity Mapping', use_container_width=True, key='Activity Mapping', disabled=(SelectWell==None or SelectWell=='-'),
              on_click=setPage, args=('Activity Mapping',), type='primary' if st.session_state['AppName'] == 'Activity Mapping' else 'secondary')
    st.button('Dashboard', use_container_width=True, key='Dashboard', disabled=(SelectWell==None or SelectWell=='-'),
              on_click=setPage, args=('Dashboard',), type='primary' if st.session_state['AppName'] == 'Dashboard' else 'secondary')

if (SelectWell == None) or (SelectWell == None):
    st.stop()
AppDict = {
    'Home': Welcome.App,
    'Activity Mapping': ActivityMapping.App,
    'Dashboard': ActivityVisualization.App,
    'Data Analytics': DataAnalytics.App,
    'Override Activity': Override.App,
}
AppDict[st.session_state['AppName']]()
# st.write(st.session_state['AppName'])