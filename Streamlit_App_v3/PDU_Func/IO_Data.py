import requests
import pandas as pd
import streamlit as st
import numpy as np
import json
import time

from datetime import datetime,timedelta
# from stqdm import stqdm

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

def getRigActivity(WellInfoDict, start_date="2000-01-01 00:00:01", end_date="2100-01-01 00:00:01"):
    """
    Retrieves the drilling activity for a specific well within a given time range.

    Parameters:
    - WellInfoDict (dict): A dictionary containing information about the well.
    - start_date (str): The start date of the time range (default: "2000-01-01 00:00:01").
    - end_date (str): The end date of the time range (default: "2100-01-01 00:00:01").

    Returns:
    - dict: A dictionary containing the drilling activity response.

    """
    getRigActAPI = 'https://pdumitradome.id/dome_api/rtdc/get_drilling_activity'
    # getRigActAPI = 'http://khansadev.xyz/dome_api/rtdc/get_drilling_activity'

    getRigActAPI_json = json.dumps(
    {
                    "wid":WellInfoDict['wid'],
                    "start_date":start_date,
                    "end_date":end_date
                    },
    indent = 4
    )
    response = (
            requests.post(
                getRigActAPI, data=getRigActAPI_json 
            )
            )
    # return dict(response.json())
    RigActivityDF = pd.DataFrame(dict(response.json())['data'], columns=['dt', 'actcode', 'activity'])

    RigActivityDF.sort_values(by='dt', inplace=True)
    RigActivityDF.rename(columns={'activity': 'Activity', 'dt':'DateTime'}, inplace=True)
    RigActivityDF['DateTime'] = pd.to_datetime(RigActivityDF['DateTime'])
    RigActivityDF = RigActivityDF.reset_index(drop=True)
    return RigActivityDF


@retry_on_error()
def DomeGetRealtimeRange(WellInfoDict):
    wid = WellInfoDict['wid']
    result = dict(requests.get(f"http://khansadev.xyz/dome_api/rtdc/get_realtime_interval/{wid}").json()['result'])

    date_format = '%Y-%m-%d %H:%M:%S'
    AllRealtime_DF = pd.DataFrame.from_dict([{
        'StartDateTime':datetime.strptime(result['Start'], date_format),
        'EndDateTime':datetime.strptime(result['End'], date_format),
        'Y-Axis':'Realtime',
    }]
    )
    return AllRealtime_DF


def interpolateRealtimeData(realtimeraw):
    # realtimeraw['dt'] = pd.to_datetime(realtimeraw['dt'], format='%Y-%m-%d %H:%M:%S')
    realtimeraw.loc[:, 'dt'] = pd.to_datetime(realtimeraw['dt'], format='%Y-%m-%d %H:%M:%S')

    # realtimeraw['dt_relative'] = (realtimeraw['dt'] - realtimeraw['dt'].min()).dt.total_seconds()
    realtimeraw.loc[:, 'dt_relative'] = (realtimeraw['dt'] - realtimeraw['dt'].min()).dt.total_seconds()

    finalRealtime = pd.DataFrame(
    {
        'dt':pd.date_range(start=realtimeraw['dt'].min(), end=realtimeraw['dt'].max(), freq='5S'),
    }
    )
    finalRealtime['date'] = finalRealtime['dt'].dt.date
    finalRealtime['time'] = finalRealtime['dt'].dt.time
    finalRealtime['dt_relative'] = (finalRealtime['dt'] - finalRealtime['dt'].min()).dt.total_seconds()

    list_cols = ["bitdepth", "md", "blockpos", "rop", "hklda", "woba", "torqa", "rpm", "stppress", "mudflowin"]
    realtimeraw[list_cols] = realtimeraw[list_cols].astype(float)
    for cols in list_cols:
        # realtimeraw[cols] = realtimeraw[cols].astype(float)
        finalRealtime[cols] = np.interp(finalRealtime['dt_relative'], realtimeraw['dt_relative'].values, realtimeraw[cols])
    finalRealtime = finalRealtime.drop('dt_relative',axis=1)
    return finalRealtime
def splitDateTime_BU(UserDateRange, hours=0.5):
    startDateTimeStr = UserDateRange['StartDate'] + ' ' + UserDateRange['StartTime']
    endDateTimeStr = UserDateRange['EndDate'] + ' ' + UserDateRange['EndTime']


    startDateTime = pd.Timestamp(startDateTimeStr)
    endDateTime = pd.Timestamp(endDateTimeStr)
    deltaTime = pd.Timedelta(hours=hours)

    date_ranges = pd.date_range(start=startDateTime, end=endDateTime.floor("H"), freq=deltaTime)

    date_list = date_ranges.tolist() + [endDateTime]
    StartDateTimeList,EndDateTimeList = date_list[:-1],date_list[1:]
    return StartDateTimeList,EndDateTimeList
def splitDateTime(UserDateRange, hours=0.5):
    # Concatenate start date and time, and end date and time
    startDateTimeStr = UserDateRange['StartDate'] + ' ' + UserDateRange['StartTime']
    endDateTimeStr = UserDateRange['EndDate'] + ' ' + UserDateRange['EndTime']

    # Convert to Timestamp
    startDateTime = pd.Timestamp(startDateTimeStr)
    endDateTime = pd.Timestamp(endDateTimeStr)

    # Round down the start time to the nearest hour and round up the end time to the next hour
    startDateTimeRounded = startDateTime.floor('H')
    endDateTimeRounded = endDateTime.ceil('H')

    # Define the time interval
    deltaTime = pd.Timedelta(hours=hours)

    # Generate date ranges
    date_ranges = pd.date_range(start=startDateTimeRounded, end=endDateTimeRounded.floor("H"), freq=deltaTime)

    # Add the rounded end time to the date list
    date_list = date_ranges.tolist()
    if endDateTimeRounded not in date_list:
        date_list.append(endDateTimeRounded)

    StartDateTimeList, EndDateTimeList = date_list[:-1], date_list[1:]

    return StartDateTimeList, EndDateTimeList
@retry_on_error()
def DomeGetRealtimeSensorDataChunk(Data_params):
    # UserDateRange = {
    #         "StartDate": UserDateRange['StartDate'].strftime('%Y-%m-%d'),
    #         "StartTime": UserDateRange['StartTime'].strftime('%H:%M:%S'),
    #         "EndDate": UserDateRange['EndDate'].strftime('%Y-%m-%d'),
    #         "EndTime": UserDateRange['EndTime'].strftime('%H:%M:%S'),
    #         }

    # Data_params ={
    #     "wid" : int(WellInfoDict['wid']),
    #     "start" : str(UserDateRange['StartDate']) + " " + str(UserDateRange['StartTime']),
    #     "end" : str(UserDateRange['EndDate']) + " " + str(UserDateRange['EndTime']),
    # }
    column_list = ["dt", "date", "time", "bitdepth", "md", "blockpos", "rop", "hklda", "woba", "torqa", "rpm", "stppress", "mudflowin",]
    WellData = (
        (
            # requests.get("https://pdumitradome.id/dome_api/rtdc/rtdc/get_data", data=json.dumps(Data_params))
            requests.get("http://khansadev.xyz/dome_api/rtdc/get_data", data=json.dumps(Data_params))
        ).text
    )

    return pd.json_normalize(json.loads(WellData), record_path='result')
@st.cache_data(ttl=60*60*1.5, show_spinner="Downloading Realtime Data...")
def DomeGetRealtimeSensorDataChunk_Cache(Data_params):
    return DomeGetRealtimeSensorDataChunk(Data_params)

    # Realtime_DF['dt'] = Realtime_DF['dt'].astype('datetime64[ns]')
    # start = datetime.strptime(Data_params['start'], '%Y-%m-%d %H:%M:%S')
    # end = datetime.strptime(Data_params['end'], '%Y-%m-%d %H:%M:%S')
    # mask = (Realtime_DF['dt'] > start) & (Realtime_DF['dt'] <= end)
    # filtered_DF = Realtime_DF[mask]
    # return filtered_DF[column_list]
def ShowProgress(container, i, total):

    # ProgressContainer = container.empty()
    # if i ==0:
    #     container.progress(0.0,)
    print(f"{i} - {total} - {np.round((i+1)/total,2)}")
    # print(np.round(i+1/total,2))
    if i > 0 and i < total:
        container.progress(np.round((i+1)/total,2), text=f"Download Realtime Sensor Data, {np.round((i+1)/total*100,0)} % Complete")
    elif i == total:
        container.progress(1.0)
        # container.empty()
        # container.progress(i/total)

def DomeGetRealtimeSensorData(WellInfoDict, UserDateRange, hours=0.5, show_progress=True, container=None):
    UserDateRange = {
            "StartDate": UserDateRange['StartDate'].strftime('%Y-%m-%d'),
            "StartTime": UserDateRange['StartTime'].strftime('%H:%M:%S'),
            "EndDate": UserDateRange['EndDate'].strftime('%Y-%m-%d'),
            "EndTime": UserDateRange['EndTime'].strftime('%H:%M:%S'),
            }

    StartDateTimeList,EndDateTimeList = splitDateTime(UserDateRange, hours=hours)

    column_list = ["dt", "date", "time", "bitdepth", "md", "blockpos", "rop", "hklda", "woba", "torqa", "rpm", "stppress", "mudflowin",]
    Realtime_List = []
    time_elapsed = []
    i = 0
    StartEndList=list(zip(StartDateTimeList,EndDateTimeList))
    # ProgressContainer = st.empty()
    # my_bar = ProgressContainer.progress(0.0,)
    # max_retries=10
    # retry_delay = 5
    if show_progress:
        # container.empty()
        my_bar = container.progress(0.0,)


    for ii in range(len((StartEndList))):
        print(f" Download Realtime Sensor Data, {np.round(ii/len(StartEndList),2)*100} % Complete")
        print(StartEndList[ii])
        # my_bar.progress(np.round(ii/len(StartEndList),2), text=f" Download Realtime Sensor Data, {np.round(ii/len(StartEndList),2)*100} % Complete")
        StartDateTime,EndDateTime = StartEndList[ii]
        loopStartTime = time.time()
        Data_params ={
            "wid" : int(WellInfoDict['wid']),
            "start" : str(StartDateTime),
            "end" : str(EndDateTime),
        }
        Realtime_DF_temp = DomeGetRealtimeSensorDataChunk_Cache(Data_params)
        # Realtime_DF_temp = DomeGetRealtimeSensorDataChunk(Data_params)
        Realtime_DF_temp['dt'] = Realtime_DF_temp['dt'].astype('datetime64[ns]')
        Realtime_List.append(Realtime_DF_temp)

        loopEndTime = time.time()
        i=i+1
        time_elapsed.append(loopEndTime-loopStartTime)
        if show_progress:
            ShowProgress(my_bar, ii, (len((StartEndList))))
    if show_progress:
        container.empty()

    Realtime_DF = pd.concat(Realtime_List, axis=0, ignore_index=True)

    start = str(UserDateRange['StartDate']) + " " + str(UserDateRange['StartTime'])
    end = str(UserDateRange['EndDate']) + " " + str(UserDateRange['EndTime'])
    mask = (Realtime_DF['dt'] > start) & (Realtime_DF['dt'] <= end)
    filtered_DF = Realtime_DF[mask]
    # print( np.mean(time_elapsed))
    # my_bar.progress(1.0)
    # ProgressContainer.empty()
    return interpolateRealtimeData(filtered_DF[column_list])

@retry_on_error()
def DomeRequestGET(API, Data_params):
    return requests.get(API, data=Data_params)
@retry_on_error()
def DomeRequestPOST(API, Data_params):
    return requests.post(API, data=Data_params)


def DomeGetActivityLogData(WellInfoDict, start_date="2000-01-01 00:00:01", end_date="2100-01-01 00:00:01"):
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
    
    # ActivityLogColumns = ['id', 'dt', 'date', 'time', 'activity', 'in_slip_threshold', 'remarks', 'pic', 'section']
    TableAPI = "http://khansadev.xyz/dome_api/rtdc/Activitylog/get_data"

    json_queries = json.dumps(
        {
        "wid": WellInfoDict['wid'],
        "start" : start_date,
        "end" : end_date,
        },
        indent = 4
    )
    response = DomeRequestGET(TableAPI, json_queries)

    if (dict(response.json())['result']) == []:

        ActivityLog_DF = pd.DataFrame(columns=list(ActivityLogColumnRenameDict.keys()))
    else:
        ActivityLog_DF = pd.DataFrame(dict(response.json())['result'])
        ActivityLog_DF = ActivityLog_DF.sort_values(by='dt')

    ActivityLog_DF.rename(columns = ActivityLogColumnRenameDict, inplace = True)
    ActivityLog_DF['DateTime'] = pd.to_datetime(ActivityLog_DF['DateTime'], errors='coerce')
    ActivityLog_DF.reset_index(inplace=True)
    # ActivityLog_DF = ActivityLog_DF.set_index('id')
    return ActivityLog_DF

def DomeInsertActivityLogData(WellInfoDict, ActLogDF):
    ActivityLogColumnRenameDict = {
        'id': 'id',
        'DateTime': 'dt',
        'Date': 'date',
        'Time': 'time',
        'Activity': 'activity',
        'In-Slip Threshold': 'in_slip_threshold',
        'Remarks': 'remarks',
        'PIC': 'pic',
        'Section Size': 'section'
    }
    ActLogDF = ActLogDF.copy()
    

    ActLogDF['wid'] = WellInfoDict['wid']
    keys_list = ["wid", "dt", "date", "time", "activity",
                        "in_slip_threshold", "remarks", "pic", "section"]
    ActLogDF = ActLogDF.rename(columns=ActivityLogColumnRenameDict)
    # st.write(ActLogDF)
    # st.stop()
    ActLogDF = ActLogDF[keys_list]
    # Convert to datetime format before formatting, if necessary
    if ActLogDF['dt'].dtype != 'datetime64[ns]':
        ActLogDF['dt'] = pd.to_datetime(ActLogDF['dt'], errors='coerce')
    ActLogDF['dt'] = ActLogDF['dt'].dt.strftime('%Y-%m-%d %H:%M:%S')

    ActLogDF['date'] = ActLogDF['date'].astype(str)
    ActLogDF['time'] = ActLogDF['time'].astype(str)

    ActLogDF['activity'] = ActLogDF['activity'].astype(str)
    ActLogDF['in_slip_threshold'] = ActLogDF['in_slip_threshold'].astype(str)
    ActLogDF['remarks'] = ActLogDF['remarks'].astype(str)
    ActLogDF['pic'] = ActLogDF['pic'].astype(str)
    ActLogDF['section'] = ActLogDF['section'].astype(str)
    ActLogDF['wid'] = ActLogDF['wid'].astype(int)

    



    AddRowAPI = "http://khansadev.xyz/dome_api/rtdc/Activitylog/create"

    for index, row in ActLogDF.iterrows():



        json_queries = json.dumps(
            row.to_dict(),
            indent = 4
        )

        response = DomeRequestPOST(AddRowAPI, json_queries)
        st.toast(dict(response.json())['message'])
        # st.stop()
    # return dict(response.json())


def DomeDeleteActivityLogData(WellInfoDict, row_id):
    
    DeleteRowAPI = "http://khansadev.xyz/dome_api/rtdc/Activitylog/delete"
    error_msg = ""
    dict_row = {
        "wid": WellInfoDict['wid'],
        "id": row_id,
    }
    if error_msg == "":
        json_queries = json.dumps(
            dict_row,
            indent = 4
        )
        response = (
            DomeRequestPOST(DeleteRowAPI, json_queries)
        )
        
        return dict(response.json())










