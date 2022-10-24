from collections import UserDict
from queue import Empty
import requests
import pandas as pd 
import json 
import streamlit as st
from Page import UserNotFound
from importlib import reload
reload(UserNotFound)
def getUserID():
    UserDict = st.experimental_get_query_params()
    if UserDict == {}:
        UserLogin_dict = {
            'status': "Not Authorized"
        }
        UserNotFound.App()
        st.stop()

    elif UserDict['ID'][0] == '71unxv':
        UserLogin_dict = {"user_name":"Admin(TEST)",
        "user_id":"MIH",
        "user_email":"irsyadhbtlh96@gmail.com",
        "user_company_name":"PDU",
        "user_cid":"",
        "status":"Authorized"}
        return UserLogin_dict

    elif UserDict != {}:
        # UserDict
        UniqueID = UserDict['ID'][0]
        # print((UniqueID))

        getWellAPI = "http://khansadev.xyz/dome_api/rtdc/get_verifikasi/" + UniqueID
        UserLogin_dict = requests.get(
                getWellAPI
            ).json()
        UserLogin_dict = UserLogin_dict['data']
        UserLogin_dict['status'] = "Authorized"
        return UserLogin_dict

        # print(UserDetail_dict['data'])
        # print(type(UserDetail_dict['data']))
    else :
        UserLogin_dict = {
            'status': "Not Authorized"
        }
        UserNotFound.App()
        st.stop()

    # if UserLogin_dict['status'] == "Not Authorized":

    


def CheckUserPass(username, password):
    with open('/app/Streamlit_App/Auth/UserPassList.json') as json_file:
        data = json.load(json_file)
    Table_DF = pd.DataFrame(dict(data))
    return (not (Table_DF.loc[(Table_DF['1'] == username) & (Table_DF['2'] == password)]).empty)
