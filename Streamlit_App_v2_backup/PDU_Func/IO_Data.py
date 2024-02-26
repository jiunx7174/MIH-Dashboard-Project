import requests
import pandas as pd
import streamlit as st
import numpy as np
import json
import time

from datetime import datetime,timedelta
from stqdm import stqdm

# for IO trial
def retry_on_error(max_retries=10, retry_interval=10):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for _ in range(max_retries):
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    print(f"Error: {e}. Retrying in {retry_interval} seconds...")
                    time.sleep(retry_interval)
            raise Exception(f"Function {func.__name__} still failed after {max_retries} retries.")
        return wrapper
    return decorator
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
@retry_on_error()
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
    # st.json(AvailableWell_JSON)
    AvailableWellDF = pd.json_normalize(AvailableWell_JSON, record_path = 'result')
    # st.dataframe(AvailableWellDF)
    if not AvailableWellDF.empty:


        AvailableWellDF['cid'] = cid
        AvailableWellDF = AvailableWellDF.astype({"cid": int,"wid": int, "well_name": 'string', 'rig_name':'string'})
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
@retry_on_error()
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

@retry_on_error()
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

@retry_on_error()
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
            print(json_queries)
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


@retry_on_error()
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
    elif table_type=="ActivitySummaryTable":
        DeleteRowAPI = "http://khansadev.xyz/dome_api/rtdc/ActivitySummary/delete"
        error_msg = ""
        keys_list = ["wid", "time_start"]

        
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
            # return error_msg
    else:
        pass

@retry_on_error()
def DomeGetData(WellInfoDict, UserDateRange, StartTimeExtend = None, EndTimeExtend = None, table_type="ActivityLogTable"):
    # TODO: simplify the column name in activity log, make it only 2 type colname, for calculation and display
    # st.write(1)
    # st.write(UserDateRange)
    ActivitySummaryColumnRenameDict = {"wid":"wid",
                            "date":"Date",
                            "time_start":"StartDateTime",
                            "time_end":"EndDateTime",
                            "duration_minutes":"Duration",
                            "hole_depth":"Hole_Depth_max",
                            "bit_depth":"Bit_Depth_avg",
                            "meterage_drilling":"DrillingMeterage",
                            "rotate_drilling_time":"RotateDrillingDuration",
                            "slide_drilling_time":"SlideDrillingDuration",
                            "reaming_time":"ReamingDuration",
                            "connection_time":"ConnectionDuration",
                            "on_bottom_hours":"OnBottomDurationPerStand",
                            "stand_duration":"StandDuration",
                            "label_subactivity":"LABEL_SubActivity",
                            "label_activity":"LABEL_Activity",
                            "stand_meterage_drilling":"DrillingMeteragePerStand",
                            "stand_durationx":"InSlip_Treshold",
                            "connection_activity":"LABEL_ConnectionActivity",
                            "pic":"PIC",
                            "section":"Section",
                            "remark":"Remarks",
                            "stand_group":"Stand Group_Pred",
                            }
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
    ActivityLogRowEmpty = {
                            'id':[1],
                            'DateTime': UserDateRange['StartDate'].strftime('%Y-%m-%d') + UserDateRange['StartTime'].strftime('%H:%M:%S'),
                            'Date': UserDateRange['StartDate'].strftime('%Y-%m-%d'),
                            'Time': UserDateRange['StartTime'].strftime('%H:%M:%S'),
                            'Activity': ['N/A'],
                            'In-Slip Threshold': [63], 
                            'Remarks': [''],
                            'PIC': [''],
                            'Section Size': ['']
                            }
    print("get " + table_type + " data/table from DOME")
    UserDateRange = {
        "StartDate": UserDateRange['StartDate'].strftime('%Y-%m-%d'),
        "StartTime": UserDateRange['StartTime'].strftime('%H:%M:%S'),
        "EndDate": UserDateRange['EndDate'].strftime('%Y-%m-%d'),
        "EndTime": UserDateRange['EndTime'].strftime('%H:%M:%S'),
        }
    # st.write(UserDateRange)
    # st.write(UserDateRange)
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

            ActivityLog_DF = pd.DataFrame(ActivityLogRowEmpty)
            print(dict(response.json()))
            # ActivityLog_DF = pd.DataFrame(columns=ActivityLogColumnRenameDict.values())
            # ActivityLog_DF = ActivityLog_DF.append(ActivityLog_DF, ignore_index=True)

        else:
            ActivityLog_DF = pd.DataFrame(dict(response.json())['result'])
    
            # ActivityLog_DF['date_time'] = pd.to_datetime(ActivityLog_DF['date'] + " " + ActivityLog_DF['time'])
            ActivityLog_DF.rename(columns = ActivityLogColumnRenameDict, inplace = True)
            # st.dataframe(ActivityLog_DF)
            ActivityLog_DF = ActivityLog_DF.sort_values(by='DateTime')
            # ActivityLog_DF=ActivityLog_DF.set_index('DateTime')
            # ActivityLog_DF = ActivityLog_DF.drop(['id'], 1)
        return ActivityLog_DF
            # return dict(response.json())['result']

    elif table_type=="Activity Summary":
        TableAPI = "http://khansadev.xyz/dome_api/rtdc/ActivitySummary/get_data"
        # print(wid)
        json_queries = json.dumps(
            {"wid" : int(WellInfoDict['wid']),
             "start" : str(UserDateRange['StartDate']) + " " + str(UserDateRange['StartTime']),
             "end" : str(UserDateRange['EndDate']) + " " + str(UserDateRange['EndTime']),
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
        ActivitySummary_DF.rename(columns = ActivitySummaryColumnRenameDict, inplace = True)
        


        
        return ActivitySummary_DF

        # if list(ActivitySummary_DF.columns) == []:
        #     ActivitySummary_DF['wid'] = int(WellInfoDict['wid'])
        #     ActivitySummary_DF = pd.DataFrame(columns=ColumnRenameDict.values())
        # else:
        #     ActivitySummary_DF['wid'] = int(WellInfoDict['wid'])
        #     ActivitySummary_DF.rename(columns = ColumnRenameDict, inplace = True)
        #     ActivitySummary_DF = ActivitySummary_DF[ColumnRenameDict.values()]
        # # ActivitySummary_DF.drop('wid', axis=1, inplace=True)
        # # st.dataframe(ActivitySummary_DF)
        # ActivitySummary_DF[['Date', 'Start Time', 'End Time']] = ActivitySummary_DF[['Date', 'Start Time', 'End Time']].astype('datetime64') 
        
        # list_float = ['Duration (Minutes)', 'Hole Depth (Max)', 'Bit Depth(mean)', 'Drilling Meterage (m)', 'Rotate Drilling Time (Minutes)',
        #              'Slide Drilling Time (Minutes)', 'Reaming Time (Minutes)', 'Connection Time (Minutes)', 'On Bottom state (hrs)', 'Total Stand Duration (hrs)',
        #              'Total Stand Drilling Meterage (m)']

        # ActivitySummary_DF[list_float] = ActivitySummary_DF[list_float].astype('float64') 
        # list_string = ["SUB-ACTIVITY","ACTIVITY","CONNECTION-ACTIVITY","PIC",
        #                 "Section","Remarks","Stand Group"]
        # ActivitySummary_DF[list_string] = ActivitySummary_DF[list_string].astype('string') 
        # # ActivitySummary_DF
        

        # print(ActivitySummary_DF)
        # return ActivitySummary_DF

def DomeGetRealtimeSensorData(WellInfoDict, UserDateRange):
    UserDateRange = {
            "StartDate": UserDateRange['StartDate'].strftime('%Y-%m-%d'),
            "StartTime": UserDateRange['StartTime'].strftime('%H:%M:%S'),
            "EndDate": UserDateRange['EndDate'].strftime('%Y-%m-%d'),
            "EndTime": UserDateRange['EndTime'].strftime('%H:%M:%S'),
            }

    # TODO: uncomment the code below if Realtime Data is ready
    Data_params ={
        "wid" : int(WellInfoDict['wid']),
        "start" : str(UserDateRange['StartDate']) + " " + str(UserDateRange['StartTime']),
        "end" : str(UserDateRange['EndDate']) + " " + str(UserDateRange['EndTime']),
    }
    

    column_list = ["dt", "date", "time", "bitdepth", "md", "blockpos", "rop", "hklda", "woba", "torqa", "rpm", "stppress", "mudflowin",]

    WellData = (
        (
            # requests.get("https://pdumitradome.id/dome_api/rtdc/rtdc/get_data", data=json.dumps(Data_params))
            requests.get("http://khansadev.xyz/dome_api/rtdc/get_data", data=json.dumps(Data_params))
        ).text
    )

    

    Realtime_DF = pd.json_normalize(json.loads(WellData), record_path='result')

    # return Data_DF[column_list]
    # Realtime_DF = pd.read_excel(
    #     "..\\Data\\Master_Report\\KS_ORKA\\AAE-05\\RealTime_test.xlsx", 
    #     # names=['raw']
    # )
    Realtime_DF['dt'] = Realtime_DF['dt'].astype('datetime64[ns]')
    start = datetime.strptime(Data_params['start'], '%Y-%m-%d %H:%M:%S')
    end = datetime.strptime(Data_params['end'], '%Y-%m-%d %H:%M:%S')
    mask = (Realtime_DF['dt'] > start) & (Realtime_DF['dt'] <= end)
    filtered_DF = Realtime_DF[mask]
    return filtered_DF[column_list]

@retry_on_error()
def DomeGetLastStandNumber(wid, SectionSize, BeforeDate):
    RequestDict = {
	"wid":int(wid),
	"section":str(SectionSize),
	"DateTime_Before":str(BeforeDate)
    }
    # st.write(RequestDict)
    DomeGetLastStandAPI = "http://khansadev.xyz/dome_api/rtdc/get_Last_LabelStand"
    # DomeGetLastStandAPI = "https://pdumitradome.id/dome_api/rtdc/get_Last_LabelStand"
    # DomeGetLastStandAPI = "http://khansadev.xyz/dome_api/rtdc/ActivitySummary/create"
    json_queries = json.dumps(
        RequestDict,
        indent = 4
    )

    response = (
        requests.post(
            DomeGetLastStandAPI, data=json_queries 
        )
    )
    if response.json()['result'] != None:
        try:
            return int(response.json()['result']['stand_group'].split('-')[-1])
        except:
            return 0
    else:
        return None


@retry_on_error()
def DomeGetRealtimeRange(wid):
    result = dict(requests.get(f"http://khansadev.xyz/dome_api/rtdc/get_realtime_interval/{wid}").json()['result'])

    date_format = '%Y-%m-%d %H:%M:%S'
    AllRealtime_DF = pd.DataFrame.from_dict([{
        'StartDateTime':datetime.strptime(result['Start'], date_format),
        'EndDateTime':datetime.strptime(result['End'], date_format),
        'Y-Axis':'Realtime',
    }]
    )
    return AllRealtime_DF


def splitDateTime(UserDateRange, hours=0.5):
    startDateTimeStr = UserDateRange['StartDate'] + ' ' + UserDateRange['StartTime']
    endDateTimeStr = UserDateRange['EndDate'] + ' ' + UserDateRange['EndTime']


    startDateTime = pd.Timestamp(startDateTimeStr)
    endDateTime = pd.Timestamp(endDateTimeStr)
    deltaTime = pd.Timedelta(hours=hours)

    date_ranges = pd.date_range(start=startDateTime, end=endDateTime.floor("H"), freq=deltaTime)

    date_list = date_ranges.tolist() + [endDateTime]
    StartDateTimeList,EndDateTimeList = date_list[:-1],date_list[1:]
    return StartDateTimeList,EndDateTimeList
# def cache_RealTime_Data(well_id, StartDateTime_select, EndDateTime_select):
#     Activity_DF = DomeGetRealtimeSensorData(well_id, StartDateTime_select, EndDateTime_select)
#     Activity_DF['dt'] = Activity_DF['dt'].astype('datetime64')
#     Activity_DF['bitdepth'] = Activity_DF['bitdepth'].astyp e('float64')
#     Activity_DF['blockpos'] = Activity_DF['blockpos'].astype('float64')
#     Activity_DF['rop'] = Activity_DF['rop'].astype('float64')
#     Activity_DF['hklda'] = Activity_DF['hklda'].astype('float64')
#     Activity_DF['woba'] = Activity_DF['woba'].astype('float64')
#     Activity_DF['torqa'] = Activity_DF['torqa'].astype('float64')
#     Activity_DF['rpm'] = Activity_DF['rpm'].astype('float64')
#     Activity_DF['stppress'] = Activity_DF['stppress'].astype('float64')
#     Activity_DF['mudflowin'] = Activity_DF['mudflowin'].astype('float64')
def interpolateRealtimeData(realtimeraw):
    realtimeraw['dt'] = pd.to_datetime(realtimeraw['dt'], format='%Y-%m-%d %H:%M:%S')
    realtimeraw['dt_relative'] = (realtimeraw['dt'] - realtimeraw['dt'].min()).dt.total_seconds()
    finalRealtime = pd.DataFrame(
    {
        'dt':pd.date_range(start=realtimeraw['dt'].min(), end=realtimeraw['dt'].max(), freq='5S'),
    }
    )
    finalRealtime['date'] = finalRealtime['dt'].dt.date
    finalRealtime['time'] = finalRealtime['dt'].dt.time
    finalRealtime['dt_relative'] = (finalRealtime['dt'] - finalRealtime['dt'].min()).dt.total_seconds()

    list_cols = ["bitdepth", "md", "blockpos", "rop", "hklda", "woba", "torqa", "rpm", "stppress", "mudflowin"]

    for cols in list_cols:
        realtimeraw[cols] = realtimeraw[cols].astype(float)
        finalRealtime[cols] = np.interp(finalRealtime['dt_relative'], realtimeraw['dt_relative'].values, realtimeraw[cols])
    finalRealtime = finalRealtime.drop('dt_relative',axis=1)
    return finalRealtime
def DomeGetRealtimeSensorData_v2(WellInfoDict, UserDateRange, hours=0.5):
    UserDateRange = {
            "StartDate": UserDateRange['StartDate'].strftime('%Y-%m-%d'),
            "StartTime": UserDateRange['StartTime'].strftime('%H:%M:%S'),
            "EndDate": UserDateRange['EndDate'].strftime('%Y-%m-%d'),
            "EndTime": UserDateRange['EndTime'].strftime('%H:%M:%S'),
            }
    # st.write("texsxt")
    # st.stop()
    StartDateTimeList,EndDateTimeList = splitDateTime(UserDateRange, hours=hours)
    # TODO: uncomment the code below if Realtime Data is ready
    column_list = ["dt", "date", "time", "bitdepth", "md", "blockpos", "rop", "hklda", "woba", "torqa", "rpm", "stppress", "mudflowin",]
    Realtime_List = []
    time_elapsed = []
    i = 0
    StartEndList=list(zip(StartDateTimeList,EndDateTimeList))
    ProgressContainer = st.empty()
    my_bar = ProgressContainer.progress(0.0,)
    max_retries=10
    retry_delay = 5
    for ii in range(len((StartEndList))):
        my_bar.progress(np.round(ii/len(StartEndList),2), text=f"Download Realtime Sensor Data, {np.round(ii/len(StartEndList),2)*100} % Complete")
        StartDateTime,EndDateTime = StartEndList[ii]
        loopStartTime = time.time()
        Data_params ={
            "wid" : int(WellInfoDict['wid']),
            "start" : str(StartDateTime),
            "end" : str(EndDateTime),
        }
        # print(Data_params)
        # st.text(Data_params)
        # if ii>5:
        #     st.stop()
        for attempt in range(max_retries):
            try:
                response = requests.get("http://khansadev.xyz/dome_api/rtdc/get_data", data=json.dumps(Data_params))
                response.raise_for_status()  # Raise an exception for non-2xx status codes
                WellData = json.loads(response.text)

                if WellData['status'] != 200:
                    raise KeyError(WellData['message'])

                Realtime_DF_temp = pd.json_normalize(WellData, record_path='result')
                try:
                    Realtime_DF_temp['dt'] = Realtime_DF_temp['dt'].astype('datetime64[ns]')
                    Realtime_List.append(Realtime_DF_temp)
                except Exception as e:
                    print("error")
                    print(e)
                    print(Realtime_DF_temp)
                break  # Break out of the retry loop if successful
            except Exception as e:
                print(f"Attempt {attempt + 1} failed with error: {str(e)}")
                if attempt < max_retries - 1:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    print("Max retries reached. Exiting.")
                    # Handle the failure or raise an exception if needed

        # WellData = json.loads((
        #     (
        #         # requests.get("https://pdumitradome.id/dome_api/rtdc/rtdc/get_data", data=json.dumps(Data_params))
        #         requests.get("http://khansadev.xyz/dome_api/rtdc/get_data", data=json.dumps(Data_params))
        #     ).text
        # ))
        # if WellData['status'] != 200:
        #     raise KeyError (WellData['message'])
        
        # Realtime_DF_temp = pd.json_normalize((WellData), record_path='result')
        # try:
        #     Realtime_DF_temp['dt'] = Realtime_DF_temp['dt'].astype('datetime64[ns]')
        #     Realtime_List.append(Realtime_DF_temp)
        # except Exception as e:
        #     print("error")
        #     print(e)
        #     print(Realtime_DF_temp)
        loopEndTime = time.time()
        i=i+1
        time_elapsed.append(loopEndTime-loopStartTime)
        # print(f"Iteration {i}: {(loopEndTime-loopStartTime):.4f} seconds")
    Realtime_DF = pd.concat(Realtime_List, axis=0, ignore_index=True)

    start = str(UserDateRange['StartDate']) + " " + str(UserDateRange['StartTime'])
    end = str(UserDateRange['EndDate']) + " " + str(UserDateRange['EndTime'])
    mask = (Realtime_DF['dt'] > start) & (Realtime_DF['dt'] <= end)
    filtered_DF = Realtime_DF[mask]
    print( np.mean(time_elapsed))
    my_bar.progress(1.0)
    ProgressContainer.empty()
    return interpolateRealtimeData(filtered_DF[column_list])