import streamlit as st 
from PDU_Func import Authentification, IO_Data
from Page import ActivityMapping, ActivityDatabase, ActivityVisualization
from Page import Welcome, PageNotFound
from importlib import reload
reload(ActivityMapping)

from streamlit_extras.no_default_selectbox import selectbox as ext_selectbox
from streamlit_option_menu import option_menu
# def updateQuery(updatedict):
#     for 
#     st.session_state['QueryParams']
def showUserInfo(UserAuthDict, container):
    container.markdown("# RTDC App")

    container.markdown("#### User: ")
    container.text(UserAuthDict["user_name"] + "(" + UserAuthDict["user_id"] + ")")

    container.markdown("#### Email: ")
    container.text(UserAuthDict["user_email"])

    container.markdown("#### Company: ")
    container.text(UserAuthDict["user_company_name"])

def DropDownOnChange():
    if 'IsFormSubmit' in st.session_state:
        del st.session_state['IsFormSubmit']
    st.cache_data.clear()

    


# import importlib
# import sys

# for module in sys.modules.values():
#     importlib.reload(module)


# def CompanySelection():
#     IO_Data.getCompanyList
#     IO_Data.getWellList

# * Initial Layout setting
if 'sidebar_state' not in st.session_state:
    st.session_state.sidebar_state = 'expanded'
st.set_page_config(page_title="Realtime Activity Mapping",initial_sidebar_state=st.session_state.sidebar_state, page_icon=None, layout="wide",)
# hide_streamlit_style = """
#             <style>
#             #MainMenu {visibility: hidden;}
#             footer {visibility: hidden;}
#             </style>
#             """
# st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

# * get User Authentification
# st.session_state['UserAuthDict'] = Authentification.getUserID()
# UserAuthDict = st.session_state['UserAuthDict']
st.session_state['QueryParams'] = st.experimental_get_query_params()
# st.write(st.session_state['QueryParams'])

UserAuthDict = Authentification.getUserID(st.session_state['QueryParams'])

if UserAuthDict['verification'] != 'verified':
    PageNotFound.App()
    st.stop()

# * Display User Info in sidebar
UserInfoContainer = st.sidebar.container()
showUserInfo(UserAuthDict['data'], UserInfoContainer)


# # * dict of available module
PageAppDict={
    # "-":Welcome.App,
    "Activity Mapping Module": ActivityMapping.App,
    "Activity Database Module":ActivityDatabase.App,
    # "Activity Visualization Module":ActivityVisualization.App,
}

 
# ModuleSidebarContainer = st.sidebar.container()
SidebarContainer = st.sidebar.container()

# with SidebarContainer:
AvailComp_DF = IO_Data.getAvailableCompanyDF(UserAuthDict)

SelectComp = SidebarContainer.selectbox("Select Company",['-'] + AvailComp_DF['company_name'].tolist(), key='SelectCompany')

# st.dataframe( IO_Data.getAvailableCompanyDF(UserAuthDict))
if SelectComp != '-':

    AvailWell_DF = IO_Data.getAvailableWellDF(SelectComp, UserAuthDict)
    SelectWell = SidebarContainer.selectbox("Select Well",['-'] + AvailWell_DF['well_name'].tolist(), key='SelectWell')
    # st.text(SelectWell)
    # st.dataframe( IO_Data.getAvailableWellDF(SelectComp, UserAuthDict))
    if SelectWell != '-':
        SelectPageApp = SidebarContainer.selectbox("Select Module",['-']+list(PageAppDict.keys()), key='SelectModule', on_change=DropDownOnChange)
        
        
        if SelectPageApp != '-':
            # if "IsFormSubmit" not in st.session_state:
            #     st.session_state['IsFormSubmit'] = False
            PageAppDict[SelectPageApp](UserAuthDict, SelectComp, SelectWell)
        else:
            Welcome.App()
            st.stop()
    else:
        Welcome.App()
        st.stop()
else:
    Welcome.App()
    st.stop()

# if SelectComp == '-':
#     Welcome.App()
#     st.stop()
# else:
#     SelectWell = SidebarContainer.selectbox("Select Well",['-'] + IO_Data.getAvailableWellDF(SelectComp, UserAuthDict)['well_name'].tolist(), key='SelectWell')
#     if SelectWell == '-':
#         Welcome.App()
#         st.stop()
#         Welcome.App()
#         st.stop()


#     else:
#         SelectPageApp = SidebarContainer.selectbox("Select Module",['-']+list(PageAppDict.keys()), key='SelectModule')
#         if SelectPageApp =='-':
#             Welcome.App()
#             st.stop()
#         else:
#             PageAppDict[SelectPageApp]()
        

