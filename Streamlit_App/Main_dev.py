import streamlit as st
from Auth import UserAuthFunc
import requests
import pandas as pd
from datetime import datetime, timedelta
from Page import ActivityMapping, ActivitySummary, ActivityDashboard, Welcome
from importlib import reload
reload(UserAuthFunc)


print("start")
UserLogin_dict = UserAuthFunc.getUserID()




st.set_page_config(page_title="Realtime Activity Mapping", page_icon=None, layout="wide",)



hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 
# st.sidebar.image('Streamlit_App/Data/PDU_Logo.jpg',use_column_width ='never', width=200)








    # if ():
# else:
PageList = [
    "Activity Mapping Module",
    "Activity Viewer Table",
    "Summary Dashboard",
]
st.sidebar.markdown("# RTDC App")
st.sidebar.markdown("#### User: ")
st.sidebar.text(UserLogin_dict["user_name"] + "(" + UserLogin_dict["user_id"] + ")")
st.sidebar.markdown("#### Email: ")
st.sidebar.text(UserLogin_dict["user_email"])
st.sidebar.markdown("#### Company: ")
st.sidebar.text(UserLogin_dict["user_company_name"])


NavBar = st.sidebar.selectbox("Select Module:",PageList)


CompName_JSON = requests.get(
        "http://khansadev.xyz/dome_api/rtdc/get_company/" + UserLogin_dict["user_cid"]
    ).json()

# st.text(CompName_JSON)
CompName_DF = pd.json_normalize(CompName_JSON, record_path = 'result')

st.session_state.CompName_Select = st.sidebar.selectbox("Select Company:",["-"] + CompName_DF['company_name'].to_list())

if st.session_state.CompName_Select == "-":
    WellList =["-"]
    Datetime_min = ['-']
    Datetime_max = ['-']
else:
    # print(CompName_DF.loc[CompName_DF['company_name']==st.session_state.CompName_Select, 'cid'].values)
    getWellAPI = "http://khansadev.xyz/dome_api/rtdc/get_well?cid=" + (CompName_DF.loc[CompName_DF['company_name']==st.session_state.CompName_Select, 'cid'].values)
    WellName_JSON = requests.get(
            getWellAPI[0]
        ).json()

    st.session_state.WellName_DF = pd.json_normalize(WellName_JSON, record_path = 'result')

    st.session_state.WellName_DF['active_date'] = st.session_state.WellName_DF['active_date'].astype('datetime64').dt.date
    st.session_state.WellName_DF['end_date'] = st.session_state.WellName_DF['end_date'].astype('datetime64').dt.date

    WellList = st.session_state.WellName_DF['well_name'].to_list()

    # print(st.session_state.WellName_DF[['well_name','wid']])

    st.session_state.WellName_Select = st.sidebar.selectbox("Select Well",['-'] + WellList, key='WellNameSelect')
    if (st.session_state.WellName_Select != '-'):
        CompWell_Name = st.session_state.CompName_Select + '-' + st.session_state.WellName_Select

        st.session_state.Well_ID = (st.session_state.WellName_DF.loc[st.session_state.WellName_DF['well_name']==st.session_state.WellName_Select, 'wid'])
        st.session_state.Well_ID_API = int(st.session_state.Well_ID.values[0])
        # print(st.session_state.Well_ID_API)


################
################
################
################
################

if NavBar == "Activity Mapping Module" and (st.session_state.CompName_Select != '-') and (st.session_state.WellName_Select != '-') :

    reload(ActivityMapping)

    ActivityMapping.App_v07()

elif NavBar == "Activity Viewer Table" and (st.session_state.CompName_Select != '-') and (st.session_state.WellName_Select != '-') :
    reload(ActivitySummary)
    ActivitySummary.App_v02()

elif NavBar == "Summary Dashboard" and (st.session_state.CompName_Select != '-') and (st.session_state.WellName_Select != '-') :
    reload(ActivityDashboard)
    ActivityDashboard.App_v02()

else:
    # st.text('test')
    reload(Welcome)
    Welcome.App()
    # st.markdown("<h1 style='text-align: center; font-size: 130px;margin-top: 300px;'>  Welcome !</h1>", unsafe_allow_html=True)
