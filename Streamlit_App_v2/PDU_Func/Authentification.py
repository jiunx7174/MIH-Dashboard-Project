import streamlit as st 
import requests

def getUserID():
    UserDict = st.experimental_get_query_params()
    if UserDict == {}:
        UserLogin_dict = {
            'data':{},
            'verification': "not verified"
        }
        # UserNotFound.App()
        # st.stop()

    elif UserDict['ID'][0] == '71unxv':
        UserLogin_dict = {
            'data':{"user_name":"Admin(TEST)",
                    "user_id":"MIH",
                    "user_email":"irsyadhbtlh96@gmail.com",
                    "user_company_name":"PDU",
                    "user_cid":"",
                    "status":"Authorized"},
            'verification': 'verified'}

        return UserLogin_dict

    elif UserDict != {}:
        # UserDict
        UniqueID = UserDict['ID'][0]
        # print((UniqueID))

        getWellAPI = "http://khansadev.xyz/dome_api/rtdc/get_verifikasi/" + UniqueID
        UserLogin_dict = requests.get(
                getWellAPI
            ).json()
        # st.json(UserLogin_dict)
        # UserLogin_dict = UserLogin_dict['data']
        # UserLogin_dict['status'] = "Authorized"
        return UserLogin_dict

        # print(UserDetail_dict['data'])
        # print(type(UserDetail_dict['data']))
    # else :
    #     UserLogin_dict = {
    #         'status': "Not Authorized"
    #     }
    #     UserNotFound.App()
    #     st.stop()
    return UserLogin_dict
