import requests
import pandas as pd
import streamlit as st
from Page import Welcome
# import datetime

@st.cache_resource
def getAvailableCompanyDF(UserAuthDict):
    UserAuthDict = UserAuthDict['data']
    GetCompAPI = "http://khansadev.xyz/dome_api/rtdc/get_company/" + UserAuthDict["user_cid"]
    # st.text(GetCompAPI)
    CompName_JSON = requests.get(GetCompAPI).json()  

    # st.text(CompName_JSON)

    # st.json(CompName_JSON)
    CompDF = pd.json_normalize(CompName_JSON, record_path = 'result')
    print('test')
    print('test 2')
    return CompDF

# @st.cache_resource
def getAvailableWellDF(SelectComp,UserAuthDict):
    CompDF = getAvailableCompanyDF(UserAuthDict)
    cid = CompDF.loc[CompDF['company_name']==SelectComp, 'cid']


    # st.text(cid)
    GetAvailableWellAPI =  "http://khansadev.xyz/dome_api/rtdc/get_well?cid=" + str(cid)
    AvailableWell_JSON = requests.get(GetAvailableWellAPI).json()
    AvailableWellDF = pd.json_normalize(AvailableWell_JSON, record_path = 'result')
    # st.dataframe(AvailableWellDF)
    if not AvailableWellDF.empty:
        # st.stop()
        # Welcome.App()
        AvailableWellDF = AvailableWellDF.astype({"wid": int, "well_name": 'string', 'active_date': 'datetime64', 'end_date': 'datetime64', 'rig_name':'string'})
    else:
        AvailableWellDF =pd.DataFrame.from_dict({"wid": [], "well_name": [], 'active_date': [], 'end_date': [], 'rig_name':[]})
    return AvailableWellDF

@st.cache_data
def getWellInfoDict(UserAuthDict, SelectComp, SelectWell):

    SelectWellDF = getAvailableWellDF(SelectComp,UserAuthDict)
    Well_ID = SelectWellDF.loc[SelectWellDF['well_name']==SelectWell, 'wid']
    WellActiveDate = SelectWellDF.loc[SelectWellDF['well_name']==SelectWell, 'active_date']
    WellEndDate = SelectWellDF.loc[SelectWellDF['well_name']==SelectWell, 'end_date']
    RigName = SelectWellDF.loc[SelectWellDF['well_name']==SelectWell, 'rig_name']

    SelectWellInfoDict = {
        'wid': Well_ID,
        'WellName':SelectWell,
        'RigName':RigName,
        'ActiveDate':WellActiveDate,
        'EndDate':WellEndDate
    }
    return SelectWellInfoDict




# def getAvailableWellDF(Comp)
# def