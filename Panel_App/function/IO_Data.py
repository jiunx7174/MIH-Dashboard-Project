import json
import requests
import pandas as pd 


def getAvailableCompanyDF(UserAuthDict):
    UserAuthDict = UserAuthDict['data']
    if UserAuthDict["user_cid"]=='1':
        GetCompAPI = "http://khansadev.xyz/dome_api/rtdc/get_company/" 
    else :
        GetCompAPI = "http://khansadev.xyz/dome_api/rtdc/get_company/" + UserAuthDict["user_cid"]
    # st.text(GetCompAPI)
    CompName_JSON = requests.get(GetCompAPI).json()  

    # st.text(CompName_JSON)

    # st.json(CompName_JSON)
    CompDF = pd.json_normalize(CompName_JSON, record_path = 'result')

    return CompDF
# def getAvailableWellDF(SelectComp,CompDF):
#     # CompDF = getAvailableCompanyDF(UserAuthDict)

#     cid = CompDF.loc[CompDF['company_name']==SelectComp, 'cid'].values

#     GetAvailableWellAPI =  "http://khansadev.xyz/dome_api/rtdc/get_well?cid=" + (cid)
#     AvailableWell_JSON = requests.get(GetAvailableWellAPI).json()

#     AvailableWellDF = pd.json_normalize(AvailableWell_JSON, record_path = 'result')

#     if not AvailableWellDF.empty:
#         # st.stop()
#         # Welcome.App()
#         AvailableWellDF['cid'] = cid
#         AvailableWellDF = AvailableWellDF.astype({"cid": int,"wid": int, "well_name": 'string', 'rig_name':'string'})
#     else:
#         AvailableWellDF =pd.DataFrame.from_dict({"cid":[],"wid": [], "well_name": [], 'active_date': [], 'end_date': [], 'rig_name':[]})
#     return AvailableWellDF
def getAvailableWellDF(SelectComp, AvailComp_DF):
    cid = AvailComp_DF.loc[AvailComp_DF['company_name']==SelectComp, 'cid'].values
    # out = IO_Data.getAvailableWellDF(SelectComp,AvailComp_DF)

    # print(pn.pane.Str(SelectComp))
    if cid != '-':
        GetAvailableWellAPI = ("http://khansadev.xyz/dome_api/rtdc/get_well?cid=" + (cid))[0]
        AvailableWell_JSON = requests.get(GetAvailableWellAPI).json()

        AvailableWellDF = pd.json_normalize(AvailableWell_JSON, record_path = 'result')
        if not AvailableWellDF.empty:
            AvailableWellDF = AvailableWellDF.astype({"cid": int,"wid": int, "well_name": 'string', 'rig_name':'string'})
            return AvailableWellDF
    else:
        return "-"