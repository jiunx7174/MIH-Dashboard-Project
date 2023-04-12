import requests
import pandas as pd
import streamlit as st
import numpy as np
import json
import time
from Page import Welcome
# import datetime
def getColumnRename(Table='ActivityLogTable', scheme="API_To_DF"):
    if Table=='ActivityLogTable':
        ColumnRenameDict = {
                        'id': 'id',
                        'dt': 'DateTime',
                        'date': 'Date',
                        'time': 'Time',
                        'activity': 'Activity',
                        'in_slip_threshold': 'In-Slip Threshold', 
                        'remarks': 'Remarks',
                        'pic': 'PIC',
                        'section': 'Section Size'
                        }
    if scheme=='API_To_DF':
        return ColumnRenameDict
    else:
        ColumnRenameDict = {y: x for x, y in ColumnRenameDict.items()}
        return ColumnRenameDict
# @st.cache_resource
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
    # st.dataframe(CompDF)
    cid = CompDF.loc[CompDF['company_name']==SelectComp, 'cid'].values[0]
    # st.text(cid)
    # print(cid.values[0])


    # st.text(cid)
    GetAvailableWellAPI =  "http://khansadev.xyz/dome_api/rtdc/get_well?cid=" + str(cid)
    AvailableWell_JSON = requests.get(GetAvailableWellAPI).json()
    AvailableWellDF = pd.json_normalize(AvailableWell_JSON, record_path = 'result')
    # st.dataframe(AvailableWellDF)
    if not AvailableWellDF.empty:
        # st.stop()
        # Welcome.App()
        AvailableWellDF['cid'] = cid
        AvailableWellDF = AvailableWellDF.astype({"cid": int,"wid": int, "well_name": 'string', 'active_date': 'datetime64', 'end_date': 'datetime64', 'rig_name':'string'})
    else:
        AvailableWellDF =pd.DataFrame.from_dict({"cid":[],"wid": [], "well_name": [], 'active_date': [], 'end_date': [], 'rig_name':[]})
    return AvailableWellDF

# @st.cache_data
def getWellInfoDict(UserAuthDict, SelectComp, SelectWell):

    SelectWellDF = getAvailableWellDF(SelectComp,UserAuthDict)
    Comp_ID = int(SelectWellDF.loc[SelectWellDF['well_name']==SelectWell, 'cid'].values[0])
    Well_ID = int(SelectWellDF.loc[SelectWellDF['well_name']==SelectWell, 'wid'].values[0])
    WellActiveDate = SelectWellDF.loc[SelectWellDF['well_name']==SelectWell, 'active_date'].tolist()[0]
    WellEndDate = SelectWellDF.loc[SelectWellDF['well_name']==SelectWell, 'end_date'].tolist()[0]
    RigName = SelectWellDF.loc[SelectWellDF['well_name']==SelectWell, 'rig_name']

    SelectWellInfoDict = {
        'cid': Comp_ID,
        'wid': Well_ID,
        'WellName':SelectWell,
        'RigName':RigName,
        'ActiveDate':WellActiveDate,
        'EndDate':WellEndDate
    }
    return SelectWellInfoDict

def DomeCheckTable(wid: int, table_type: str="ActivityLogTable"):
    if table_type=="ActivityLogTable":    
        WellAPI = "http://khansadev.xyz/dome_api/rtdc/Activitylog/cek_table"
        json_queries = {
        "wid": wid
        }

        response = (
            requests.post(
                WellAPI, data=json.dumps(json_queries, indent = 4) 
            )
        )
        print('check ActivityLogTable')
        return dict(response.json())
    
    elif table_type=="ActivitySummaryTable":
        WellAPI = "http://khansadev.xyz/dome_api/rtdc/ActivitySummary/cek_table"
        json_queries = {
        "wid": wid
        }

        response = (
            requests.post(
                WellAPI, data=json.dumps(json_queries, indent = 4) 
            )
        )
        print('check ActivitySummaryTable')
        return dict(response.json())


def DomeCreateTable(wid: int, table_type: str="ActivityLogTable"):
    if table_type=="ActivityLogTable":    
        WellAPI = "http://khansadev.xyz/dome_api/rtdc/Activitylog/create_table"
        json_queries = {
        "wid": wid
        }

        response = (
            requests.post(
                WellAPI, data=json.dumps(json_queries, indent = 4) 
            )
        )
        print('create ActivityLogTable')

        return dict(response.json())
    elif table_type=="ActivitySummaryTable":    
        WellAPI = "http://khansadev.xyz/dome_api/rtdc/ActivitySummary/create_table"
        json_queries = {
        "wid": wid
        }

        response = (
            requests.post(
                WellAPI, data=json.dumps(json_queries, indent = 4) 
            )
        )

        print('create ActivitySummaryTable')
        return dict(response.json())
    
def DomeInsertData(dict_row, table_type="ActivityLogTable"):
    # time.sleep(0.1)
    print("add new data to " + table_type)
    if table_type=="ActivityLogTable":
        AddRowAPI = "http://khansadev.xyz/dome_api/rtdc/Activitylog/create"
        error_msg = ""
        keys_list = ["wid", "dt", "date", "time", "activity",
                            "in_slip_threshold", "remarks", "pic", "section"]
        
        for keys_name in keys_list:
            if keys_name not in dict_row.keys():
                error_msg = error_msg + keys_name + ", "
        if error_msg == "":
            json_queries = json.dumps(
                dict_row,
                indent = 4
            )
            response = (
                requests.post(
                    AddRowAPI, data=json_queries 
                )
            )
            
            return dict(response.json())
        else:
            return error_msg
    elif table_type=="ActivitySummaryTable":
        AddRowAPI = "http://khansadev.xyz/dome_api/rtdc/ActivitySummary/create"
        error_msg = ""
        keys_list = ['wid', 'date', 'time_start', 'time_end', 'duration_minutes', 'hole_depth', 
                        'bit_depth', 'meterage_drilling', 'rotate_drilling_time', 'slide_drilling_time', 
                        'reaming_time', 'connection_time', 'on_bottom_hours', 'stand_duration', 'label_subactivity', 
                        'label_activity', 'stand_meterage_drilling', 'stand_durationx', 'stand_on_bottom', 'pic', 
                        'section', 'remark', 'stand_group']
        
        for keys_name in keys_list:
            if keys_name not in dict_row.keys():
                error_msg = error_msg + keys_name + ", "
        print(dict_row)
        if error_msg == "":
            json_queries = json.dumps(
                dict_row,
                indent = 4
            )
            response = (
                requests.post(
                    AddRowAPI, data=json_queries 
                )
            )
            # print(response)
            return dict(response.json())
        else:
            return error_msg


def DomeDeleteData(dict_row, table_type="ActivityLogTable"):
    

    if table_type=="ActivityLogTable":
        DeleteRowAPI = "http://khansadev.xyz/dome_api/rtdc/Activitylog/delete"
        error_msg = ""
        keys_list = ["wid", "id"]

        
        for keys_name in keys_list:
            if keys_name not in dict_row.keys():
                error_msg = error_msg + keys_name + ", "
        if error_msg == "":
            json_queries = json.dumps(
                dict_row,
                indent = 4
            )
            response = (
                requests.post(
                    DeleteRowAPI, data=json_queries 
                )
            )
            
            return dict(response.json())
        else:
            return error_msg


def DomeGetData(WellInfoDict, UserDateRange, table_type="ActivityLogTable"):
    
    ColumnRenameDict = {'wid': 'wid',
                        'date': 'Date',
                        'time_start': 'Start Time',
                        'time_end': 'End Time',
                        'duration_minutes': 'Duration (Minutes)',
                        'label_subactivity': 'SUB-ACTIVITY',
                        'label_activity': 'ACTIVITY',
                        'stand_durationx': 'CONNECTION-ACTIVITY',
                        'hole_depth': 'Hole Depth (Max)',
                        'bit_depth': 'Bit Depth(mean)',
                        'meterage_drilling': 'Drilling Meterage (m)',
                        'rotate_drilling_time': 'Rotate Drilling Time (Minutes)',
                        'slide_drilling_time': 'Slide Drilling Time (Minutes)',
                        'reaming_time': 'Reaming Time (Minutes)',
                        'connection_time': 'Connection Time (Minutes)',
                        'on_bottom_hours': 'On Bottom state (hrs)',
                        'stand_duration': 'Total Stand Duration (hrs)',
                        'stand_meterage_drilling': 'Total Stand Drilling Meterage (m)',
                        'stand_group': 'Stand Group',
                        'pic': 'PIC',
                        'section': 'Section',
                        'remark': 'Remarks',
                        'stand_on_bottom': 'zeros'}
    ActivityLogColumnRenameDict = {
                            'id': 'id',
                            'dt': 'DateTime',
                            'date': 'Date',
                            'time': 'Time',
                            'activity': 'Activity',
                            'in_slip_threshold': 'In-Slip Threshold', 
                            'remarks': 'Remarks',
                            'pic': 'PIC',
                            'section': 'Section Size'
                            }
    print("get " + table_type + " data/table from DOME")
    if table_type=="ActivityLogTable":

        TableAPI = "http://khansadev.xyz/dome_api/rtdc/Activitylog/get_data"
        # print(wid)
        json_queries = json.dumps(
            {
            "wid": WellInfoDict['wid'],
            "start" : str(UserDateRange['StartDate']) + " " + '00:00:00',
            "end" : str(UserDateRange['EndDate']) + " " + '23:59:00',
            },
            indent = 4
        )
        response = (
            requests.get(
                TableAPI, data=json_queries
            )
        )
        # print(json_queries)
        # print(response)
        if (dict(response.json())['result']) == []:

            out_DF = pd.DataFrame(columns=ActivityLogColumnRenameDict.values())

        else:
            out_DF = pd.DataFrame(dict(response.json())['result'])
    
            # out_DF['date_time'] = pd.to_datetime(out_DF['date'] + " " + out_DF['time'])
            out_DF.rename(columns = ActivityLogColumnRenameDict, inplace = True)
            # st.dataframe(out_DF)
            out_DF = out_DF.sort_values(by='DateTime')
            # out_DF=out_DF.set_index('DateTime')
            # out_DF = out_DF.drop(['id'], 1)
        return out_DF
            # return dict(response.json())['result']

    elif table_type=="Activity Summary":
        TableAPI = "http://khansadev.xyz/dome_api/rtdc/ActivitySummary/get_data"
        # print(wid)
        json_queries = json.dumps(
            {
            "wid": wid,
            "start" : start_date_time,
            "end" : end_date_time
            },
            indent = 4
        )
        response = (
            requests.get(
                TableAPI, data=json_queries
            )
        )
        # print((response.json()))

        ActivitySummary_DF = pd.DataFrame(dict(response.json())['result'])
        # print("TESSSSSSSSSS")
        # print(ActivitySummary_DF.empty)
        if list(ActivitySummary_DF.columns) == []:
            ActivitySummary_DF['wid'] = wid
            ActivitySummary_DF = pd.DataFrame(columns=ColumnRenameDict.values())
        else:
            # ActivitySummary_DF.drop('on_bottom_hours', axis=1, inplace=True)
            ActivitySummary_DF['wid'] = wid
            ActivitySummary_DF.rename(columns = ColumnRenameDict, inplace = True)
            ActivitySummary_DF = ActivitySummary_DF[ColumnRenameDict.values()]
        # ActivitySummary_DF.drop('wid', axis=1, inplace=True)
        # st.dataframe(ActivitySummary_DF)
        ActivitySummary_DF[['Date', 'Start Time', 'End Time']] = ActivitySummary_DF[['Date', 'Start Time', 'End Time']].astype('datetime64') 
        
        list_float = ['Duration (Minutes)', 'Hole Depth (Max)', 'Bit Depth(mean)', 'Drilling Meterage (m)', 'Rotate Drilling Time (Minutes)',
                     'Slide Drilling Time (Minutes)', 'Reaming Time (Minutes)', 'Connection Time (Minutes)', 'On Bottom state (hrs)', 'Total Stand Duration (hrs)',
                     'Total Stand Drilling Meterage (m)']

        ActivitySummary_DF[list_float] = ActivitySummary_DF[list_float].astype('float64') 
        list_string = ["SUB-ACTIVITY","ACTIVITY","CONNECTION-ACTIVITY","PIC",
                        "Section","Remarks","Stand Group"]
        ActivitySummary_DF[list_string] = ActivitySummary_DF[list_string].astype('string') 
        # ActivitySummary_DF
        

        # print(ActivitySummary_DF)
        return ActivitySummary_DF

def DomeGetRealtimeSensorData(WellInfoDict, DateTimeRange):

    Data_params ={
        "wid" : WellInfoDict['wid'],
        "start" : DateTimeRange[0],
        "end" : DateTimeRange[1]
    }
    # now.strftime("%Y-%m-%d, %H:%M:%S")
    # print(Data_params)
    column_list = ["dt", "date", "time", "bitdepth", "md", "blockpos", "rop", "hklda", "woba", "torqa", "rpm", "stppress", "mudflowin",]
    # return None
    WellData = (
        (
            requests.get("http://khansadev.xyz/dome_api/rtdc/get_data", data=json.dumps(Data_params))
        ).text
    )
    print(WellData)
    Data_DF = pd.json_normalize(json.loads(WellData), record_path='result')
    print(Data_DF)
    # print(Data_DF.head(5))
    return Data_DF[column_list]

# def cache_RealTime_Data(well_id, StartDateTime_select, EndDateTime_select):
#     Activity_DF = DomeGetRealtimeSensorData(well_id, StartDateTime_select, EndDateTime_select)
#     Activity_DF['dt'] = Activity_DF['dt'].astype('datetime64')
#     Activity_DF['bitdepth'] = Activity_DF['bitdepth'].astype('float64')
#     Activity_DF['blockpos'] = Activity_DF['blockpos'].astype('float64')
#     Activity_DF['rop'] = Activity_DF['rop'].astype('float64')
#     Activity_DF['hklda'] = Activity_DF['hklda'].astype('float64')
#     Activity_DF['woba'] = Activity_DF['woba'].astype('float64')
#     Activity_DF['torqa'] = Activity_DF['torqa'].astype('float64')
#     Activity_DF['rpm'] = Activity_DF['rpm'].astype('float64')
#     Activity_DF['stppress'] = Activity_DF['stppress'].astype('float64')
#     Activity_DF['mudflowin'] = Activity_DF['mudflowin'].astype('float64')

#     return Activity_DF