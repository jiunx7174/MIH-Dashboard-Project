import pandas as pd 
import json 


def CheckUserPass(username, password):
    with open('/app/Streamlit_App/Auth/UserPassList.json') as json_file:
        data = json.load(json_file)
    Table_DF = pd.DataFrame(dict(data))
    return (not (Table_DF.loc[(Table_DF['1'] == username) & (Table_DF['2'] == password)]).empty)
