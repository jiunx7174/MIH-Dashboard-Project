import streamlit as st 
from PDU_Func import Authentification, IO_Data
from Page import ActivityMapping, ActivityDatabase, ActivityVisualization
from Page import Welcome, PageNotFound

from streamlit_extras.no_default_selectbox import selectbox as ext_selectbox
from streamlit_option_menu import option_menu

def showUserInfo(UserAuthDict, container):
    container.markdown("# RTDC App")

    container.markdown("#### User: ")
    container.text(UserAuthDict["user_name"] + "(" + UserAuthDict["user_id"] + ")")

    container.markdown("#### Email: ")
    container.text(UserAuthDict["user_email"])

    container.markdown("#### Company: ")
    container.text(UserAuthDict["user_company_name"])
    
def IsSubmitFormTrue():
    st.session_state['IsFormSubmit'] = True

# import importlib
# import sys

# for module in sys.modules.values():
#     importlib.reload(module)


# def CompanySelection():
#     IO_Data.getCompanyList
#     IO_Data.getWellList

# * Initial Layout setting
st.set_page_config(page_title="Realtime Activity Mapping", page_icon=None, layout="wide",)
# hide_streamlit_style = """
#             <style>
#             #MainMenu {visibility: hidden;}
#             footer {visibility: hidden;}
#             </style>
#             """
# st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

# * get User Authentification
UserAuthDict = Authentification.getUserID()
if UserAuthDict['verification'] != 'verified':
    PageNotFound.App()
    st.stop()

# * Display User Info in sidebar
UserInfoContainer = st.sidebar.container()
showUserInfo(UserAuthDict['data'], UserInfoContainer)


# # * dict of available module
PageDict={
    # "-":Welcome.App,
    "Activity Mapping Module": ActivityMapping.App,
    "Activity Database Module":ActivityDatabase.App,
    "Activity Visualization Module":ActivityVisualization.App,
}

# PageDict[st.sidebar.selectbox("Select Module",PageDict.keys(), index=0, key="SelectModule")]()
# out:

if "IsFormSubmit" not in st.session_state:
    st.session_state['IsFormSubmit'] = False
ModuleSidebarContainer = st.sidebar.container()
SidebarContainer = st.sidebar.container()

with SidebarContainer:
    SelectComp = ext_selectbox("Select Company",IO_Data.getAvailableCompanyDF(UserAuthDict)['company_name'], key='SelectCompany')
if SelectComp == None:
    Welcome.App()
        # st.stop()

with SidebarContainer:
    try:
        SelectWell = ext_selectbox("Select Well",IO_Data.getAvailableWellDF(SelectComp, UserAuthDict)['well_name'], key='SelectWell')
    except:
        Welcome.App()

if SelectWell == None:
    Welcome.App()
with SidebarContainer:
    with st.form(key='DateForm'):
        DateCol,TimeCol = st.columns([1,1])

        StartDate = DateCol.date_input("Start Date",key="StartDateValues")
        StartTime = TimeCol.time_input("Start Date",key="StartTimeValues")
        st.form_submit_button(on_click=IsSubmitFormTrue)

if st.session_state['IsFormSubmit']==False:
    Welcome.App()
    # st.stop()

# if SelectWell == None:


        # st.stop()

# with SidebarContainer.form():
#     DateTimeColumn = st.columns([2,1])

#     DateTimeColumn[0].date_input(value=)

# selectbox("Select Company",IO_Data.getCompanyDF(UserAuthDict)['company_name'], key="SelectCompany")
# st.text(Comp)

# st.dataframe(IO_Data.getAvailableCompanyDF(UserAuthDict))
st.dataframe(IO_Data.getAvailableWellDF(SelectComp, UserAuthDict))
# st.sidebar.selectbox("Select Company",PageDict.keys(), index=0, key="SelectModule"

st.json(IO_Data.getWellInfoDict(UserAuthDict, SelectComp, SelectWell))


styles={
    "container": {"padding": "0!important", "background-color": "#fffff"},
    "icon": { "font-size": "15px"}, 
    "nav-link": {"font-size": "15px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
    "nav-link-selected": {"background-color": "#FF7F50"},
}

with st.sidebar:
    selected = option_menu(None, list(PageDict.keys()), styles=styles,
        )
    # selected

PageDict[selected]()