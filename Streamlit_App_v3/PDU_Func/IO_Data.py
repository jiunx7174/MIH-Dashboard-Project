import requests
import pandas as pd
import streamlit as st
import numpy as np
import json
import time
import os

from datetime import datetime,timedelta
# from stqdm import stqdm


def getURLAPI_pdu():
    try:
        with open('app_config.json') as json_file:
            return dict(json.load(json_file))['url_pdu_api']
    except :
        return  "http://pdumitradome.id/dome_api/"
def getURLAPI_FastAPI():
    try:
        with open('app_config.json') as json_file:
            return dict(json.load(json_file))['url_pdu_fastapi']
    except :
        return "http://pdumitradome.id:8090/"
    
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
def DomeRequestGET(API, Data_params):
    print(API)
    print(Data_params)
    return requests.get(API, data=Data_params)
@retry_on_error()
def DomeRequestPOST(API, Data_params):
    print(API)
    print(Data_params)
    return requests.post(API, data=Data_params)

@retry_on_error()
def DomeCheckTable(wid: int, table_type: str="ActivityLogTable"):
    url_pdu_api = getURLAPI_pdu()
    if table_type=="ActivityLogTable":    
        WellAPI = f"{url_pdu_api}rtdc/ActivitylogRT/cek_table"
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
        WellAPI = f"{url_pdu_api}rtdc/ActivitySummaryRT/cek_table"
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
    url_pdu_api = getURLAPI_pdu()
    if table_type=="ActivityLogTable":    
        WellAPI = f"{url_pdu_api}rtdc/ActivitylogRT/create_table"
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
        WellAPI = f"{url_pdu_api}rtdc/ActivitySummaryRT/create_table"
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


def initiateTable(WellInfoDict):
    wid = WellInfoDict['wid']
    for table_type in ['ActivityLogTable', 'ActivitySummaryTable']:
        if DomeCheckTable(wid, table_type)['table'] == 0:
            DomeCreateTable(wid, table_type)

# @retry_on_error()
def getAvailableCompanyDF(UserAuthDict):
    url_pdu_api = getURLAPI_pdu()
    UserAuthDict = UserAuthDict['data']
    if UserAuthDict["user_cid"]=='1':
        GetCompAPI = f"{url_pdu_api}rtdc/get_company/" 
    else :
        GetCompAPI = f"{url_pdu_api}rtdc/get_company/" + UserAuthDict["user_cid"]
    # st.text(GetCompAPI)
    CompName_JSON = requests.get(GetCompAPI).json()  

    # st.text(CompName_JSON)

    # st.json(CompName_JSON)
    CompDF = pd.json_normalize(CompName_JSON, record_path = 'result')

    return CompDF

# @retry_on_error()
def getAvailableWellDF(SelectComp,UserAuthDict):
    url_pdu_api = getURLAPI_pdu()
    CompDF = getAvailableCompanyDF(UserAuthDict)
    # st.dataframe(CompDF)
    cid = CompDF.loc[CompDF['company_name']==SelectComp, 'cid'].values[0]
    # st.text(cid)
    # print(cid.values[0])
    # st.text(cid)
    GetAvailableWellAPI =  f"{url_pdu_api}rtdc/get_well?cid=" + str(cid)
    AvailableWell_JSON = requests.get(GetAvailableWellAPI).json()
    # st.json(AvailableWell_JSON)
    AvailableWellDF = pd.json_normalize(AvailableWell_JSON, record_path = 'result')
    # st.dataframe(AvailableWellDF)
    if not AvailableWellDF.empty:


        AvailableWellDF['cid'] = cid
        AvailableWellDF = AvailableWellDF.astype({"cid": int,"wid": int, "well_name": 'string', 'rig_name':'string', 'active_date':'string', 'end_date':'string'})
    else:
        AvailableWellDF =pd.DataFrame.from_dict({"cid":[],"wid": [], "well_name": [], 'active_date': [], 'end_date': [], 'rig_name':[], 'active_date': [], 'end_date': []})
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
# @retry_on_error()
def getWellInfoDict_byID(cid, wid):
    url_pdu_api = getURLAPI_pdu()
    GetAvailableWellAPI =  f"{url_pdu_api}rtdc/get_well?cid=" + str(cid)
    # print(GetAvailableWellAPI)
    AvailableWell_JSON = requests.get(GetAvailableWellAPI).json()
    # st.json(AvailableWell_JSON)
    SelectWellDF = pd.json_normalize(AvailableWell_JSON, record_path = 'result')
    print("------------------")
    print(SelectWellDF)
    # print(SelectWellDF.loc[SelectWellDF['wid']==str(wid), 'well_name'])

    WellName = SelectWellDF.loc[SelectWellDF['wid']==str(wid), 'well_name'].tolist()[0]
    WellActiveDate = SelectWellDF.loc[SelectWellDF['wid']==str(wid), 'active_date'].tolist()[0]
    WellEndDate = SelectWellDF.loc[SelectWellDF['wid']==str(wid), 'end_date'].tolist()[0]
    RigName = SelectWellDF.loc[SelectWellDF['wid']==str(wid), 'rig_name']

    SelectWellInfoDict = {
        'wid': wid,
        'cid': cid,
        'WellName':WellName,
        'RigName':RigName,
        'ActiveDate':WellActiveDate,
        'EndDate':WellEndDate
    }

    return SelectWellInfoDict
def round_seconds_to_nearest_5_seconds(dt):
    # dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    rounded_seconds = round(dt.second / 5) * 5
    if rounded_seconds >= 60:
        dt += timedelta(minutes=1)
        rounded_seconds = 0
    dt = dt.replace(second=rounded_seconds)
    return dt
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
    url_pdu_api = getURLAPI_pdu()
    # getRigActAPI = 'https://pdumitradome.id/dome_api/rtdc/get_drilling_activity'
    getRigActAPI = f'{url_pdu_api}rtdc/get_drilling_activity'

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
    # RigActivityDF['DateTime'] = RigActivityDF['DateTime'].apply(round_seconds_to_nearest_5_seconds)
    RigActivityDF = RigActivityDF.reset_index(drop=True)
    return RigActivityDF


@retry_on_error()
def DomeGetRealtimeRange(WellInfoDict):
    url_pdu_api = getURLAPI_pdu()
    wid = WellInfoDict['wid']
    result = dict(requests.get(f"{url_pdu_api}rtdc/get_realtime_interval/{wid}").json()['result'])

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
    # Assuming `realtimeraw['dt']` is a Series of datetime objects
    start_time = realtimeraw['dt'].min()
    end_time = realtimeraw['dt'].max()

    # Round the start time to the nearest 5 seconds
    rounded_start_time = start_time - timedelta(seconds=start_time.second % 5,
                                                        microseconds=start_time.microsecond)
    finalRealtime = pd.DataFrame({
        'dt': pd.date_range(start=rounded_start_time, end=end_time, freq='5S'),
    })


    # finalRealtime = pd.DataFrame(
    # {
    #     'dt':pd.date_range(start=realtimeraw['dt'].min(), end=realtimeraw['dt'].max(), freq='5S'),
    # }
    # )
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
@retry_on_error(max_retries=2, retry_interval=1)
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
    # print(Data_params)
    url_pdu_api = getURLAPI_pdu()
    print(f"Request Realtime on :{url_pdu_api}rtdc/get_data")
    print(Data_params)
    column_list = ["dt", "date", "time", "bitdepth", "md", "blockpos", "rop", "hklda", "woba", "torqa", "rpm", "stppress", "mudflowin",]
    WellData = (
        (
            # requests.get("https://pdumitradome.id/dome_api/rtdc/rtdc/get_data", data=json.dumps(Data_params))
            requests.get(f"{url_pdu_api}rtdc/get_data", data=json.dumps(Data_params))
        ).text
    )
    WellData = json.loads(WellData)
    # print(WellData)
    print(WellData['status'])
    if WellData['status'] == 404:
        return pd.DataFrame(columns=column_list)
    else:
        return pd.json_normalize(WellData, record_path='result')
    


# @st.cache_data(
#         # ttl=60*60*1.5,
#         persist=True,
#         show_spinner="Downloading Realtime Data...")
def DomeGetRealtimeSensorDataChunk_DiskCache(Data_params):
    print("====================================")
    print("======== Use Streamlit Cache =======")
    print("====================================")
    return DomeGetRealtimeSensorDataChunk(Data_params)
def DomeGetRealtimeSensorDataChunk_ParquetCache(Data_params):
    print("====================================")
    print("======== Use Parquet Cache =======")
    print("====================================")
    wid = Data_params['wid']
    dir_path = f"Data/RealtimeCache/wid_{wid}"
    StartDateTimeStr = Data_params['start'].replace(' ', '-').replace(':', '')
    EndDateTimeStr = Data_params['end'].replace(' ', '-').replace(':', '')

    ParquetCacheFilepath = dir_path + f"/{Data_params['wid']}_{StartDateTimeStr}_{EndDateTimeStr}.parquet"

    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    if os.path.isfile(ParquetCacheFilepath):
        # print(f"Read from Parquet Cache: {ParquetCacheFilepath}")
        OutputRealtime =  pd.read_parquet(ParquetCacheFilepath)
        return OutputRealtime
    else:
        OutputRealtime = DomeGetRealtimeSensorDataChunk(Data_params)
        OutputRealtime['dt'] = OutputRealtime['dt'].astype('datetime64[ns]')
        
        if OutputRealtime.empty:
            return OutputRealtime
        elif OutputRealtime['dt'].max() >= (datetime.strptime(Data_params['end'], '%Y-%m-%d %H:%M:%S') - timedelta(seconds=20)):

            print("====================================")
            print(f"Save to Parquet Cache: {ParquetCacheFilepath}")
            print("====================================")
            OutputRealtime.to_parquet(ParquetCacheFilepath, compression='gzip')
        else:
            # OutputRealtime.to_parquet(ParquetCacheFilepath, compression='gzip')
            return OutputRealtime



    # OutputRealtime[OutputRealtime['date'].astype(str) == date].to_parquet(ParquetCacheFilepath, compression='gzip')



    # return DomeGetRealtimeSensorDataChunk(Data_params)
# @st.cache_data(
#         ttl=60*60*1.5,
#         # persist=True,
#         show_spinner="Downloading Realtime Data...")
def DomeGetRealtimeSensorDataChunk_SessionCache(Data_params):
    print("====================================")
    print("======== Use Streamlit Cache =======")
    print("====================================")
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

def DomeGetRealtimeSensorData(WellInfoDict, UserDateRange, hours=0.5, show_progress=True,runOnStreamlit=True, _container=None):
    print(WellInfoDict)
    active_start_date = datetime.strptime(WellInfoDict['ActiveDate'], '%Y-%m-%d').date()
    active_end_date = datetime.strptime(WellInfoDict['EndDate'], '%Y-%m-%d').date()
    if active_start_date > UserDateRange['StartDate']:
        UserDateRange['StartDate'] = active_start_date
        UserDateRange['StartTime'] = datetime.strptime("00:00:00", '%H:%M:%S')
    if active_end_date < UserDateRange['EndDate']:
        UserDateRange['EndDate'] = active_end_date
        UserDateRange['EndTime'] = datetime.strptime("23:59:55", '%H:%M:%S')

    UserDateRange = {
            "StartDate": UserDateRange['StartDate'].strftime('%Y-%m-%d'),
            "StartTime": UserDateRange['StartTime'].strftime('%H:%M:%S'),
            "EndDate": UserDateRange['EndDate'].strftime('%Y-%m-%d'),
            "EndTime": UserDateRange['EndTime'].strftime('%H:%M:%S'),
            }
    # active_date_dict = {
    #     "start_date": WellInfoDict['active_date'],
    #     "end_date": WellInfoDict['end_date'],
    # }
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
        my_bar = _container.progress(0.0,)
    if runOnStreamlit:
        ProgressStatus = st.progress(0., text=" Download Realtime Sensor Data, 0 % Complete")

    for ii in range(len((StartEndList))):
        print(f" Download Realtime Sensor Data, {np.round(ii/len(StartEndList),2)*100} % Complete")
        print(StartEndList[ii])
        # my_bar.progress(np.round(ii/len(StartEndList),2), text=f" Download Realtime Sensor Data, {np.round(ii/len(StartEndList),2)*100} % Complete")
        StartDateTime,EndDateTime = StartEndList[ii]
        # loopStartTime = time.time()
        Data_params ={
            "wid" : int(WellInfoDict['wid']),
            "start" : str(StartDateTime),
            "end" : str(EndDateTime),
        }

        
        current_time = datetime.now()
        # Define the 3-hour range before the current time
        hours_before = current_time - timedelta(hours=2)

        # Check if the range matches 3 hours before the current time
        
        if EndDateTime >= hours_before:
            IsStillUpdate = True
        else:
            IsStillUpdate = False
        # print(IsStillUpdate)

        # if runOnStreamlit and IsStillUpdate:
        #     ProgressStatus.progress(np.round(ii/len(StartEndList),2),  text=f" Download Realtime Sensor Data, {np.round(ii/len(StartEndList),2)*100} % Complete")
        #     if IsStillUpdate:
        #         Realtime_DF_temp = DomeGetRealtimeSensorDataChunk_SessionCache(Data_params)
        #     else:
        #         Realtime_DF_temp = DomeGetRealtimeSensorDataChunk_DiskCache(Data_params)

        # else:
        #     Realtime_DF_temp = DomeGetRealtimeSensorDataChunk(Data_params)
        
        if IsStillUpdate and ((EndDateTime - StartDateTime) != timedelta(hours=hours)):
            Realtime_DF_temp = DomeGetRealtimeSensorDataChunk(Data_params)
        else:
            Realtime_DF_temp = DomeGetRealtimeSensorDataChunk_ParquetCache(Data_params)
        if runOnStreamlit :
            ProgressStatus.progress(np.round(ii/len(StartEndList),2),  text=f" Download Realtime Sensor Data, {np.round(ii/len(StartEndList),2)*100} % Complete")

        # else:
        #     Realtime_DF_temp = DomeGetRealtimeSensorDataChunk(Data_params)
        # Realtime_DF_temp = DomeGetRealtimeSensorDataChunk(Data_params)
        # print(Realtime_DF_temp)
        if not Realtime_DF_temp.empty:
            # st.warning(f"No data found for {StartDateTime} - {EndDateTime}")
            # st.stop()
            Realtime_DF_temp['dt'] = Realtime_DF_temp['dt'].astype('datetime64[ns]')
            Realtime_List.append(Realtime_DF_temp)

        # loopEndTime = time.time()
        i=i+1
        # time_elapsed.append(loopEndTime-loopStartTime)
        if show_progress:
            ShowProgress(my_bar, ii, (len((StartEndList))))
    if show_progress:
        _container.empty()
    if Realtime_List == []:
        st.warning(f"No data found for {UserDateRange['StartDate']} {UserDateRange['StartTime']} - {UserDateRange['EndDate']} {UserDateRange['EndTime']}")
        st.stop()
        # return pd.DataFrame(columns=column_list)
    Realtime_DF = pd.concat(Realtime_List, axis=0, ignore_index=True)

    start = str(UserDateRange['StartDate']) + " " + str(UserDateRange['StartTime'])
    end = str(UserDateRange['EndDate']) + " " + str(UserDateRange['EndTime'])
    mask = (Realtime_DF['dt'] > start) & (Realtime_DF['dt'] <= end)
    filtered_DF = Realtime_DF[mask]
    # print( np.mean(time_elapsed))
    # my_bar.progress(1.0)
    # ProgressContainer.empty()
    if runOnStreamlit:
        ProgressStatus.progress(1.,  text="Download Realtime Sensor Data Complete")
        ProgressStatus.empty()
    return interpolateRealtimeData(filtered_DF[column_list])


# Activity Log
def DomeGetActivityLogData(WellInfoDict, start_date="2000-01-01 00:00:01", end_date="2100-01-01 00:00:01"):
    url_pdu_api = getURLAPI_pdu()
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
    TableAPI = f"{url_pdu_api}rtdc/Activitylog/get_data"

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
    url_pdu_api = getURLAPI_pdu()
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

    
    AddRowAPI = f"{url_pdu_api}rtdc/Activitylog/create"

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
    url_pdu_api = getURLAPI_pdu()
    DeleteRowAPI = f"{url_pdu_api}rtdc/Activitylog/delete"
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


# Activity Summary
def DomeGetActivitySummaryData(WellInfoDict, UserDateRange):
    url_pdu_api = getURLAPI_pdu()
    TableAPI = f"{url_pdu_api}rtdc/ActivitySummary/get_data"
    # print(wid)
    json_queries = json.dumps(
        {"wid" : int(WellInfoDict['wid']),
            "start" : str(UserDateRange['StartDate']) + " " + str(UserDateRange['StartTime']),
            "end" : str(UserDateRange['EndDate']) + " " + str(UserDateRange['EndTime']),
        },
        indent = 4
    )

    response = DomeRequestGET(TableAPI, json_queries)
    # print((response.json()))
    
    ActivitySummary_DF = pd.DataFrame(dict(response.json())['result'])
    # print("Columns:")
    # print(ActivitySummary_DF.columns)
    ActivitySummary_DF.rename(columns = ActivitySummaryColumnRenameDict()['ColumnName'], inplace = True)
    
    if ActivitySummary_DF.empty:
        return pd.DataFrame(columns=ActivitySummaryColumnRenameDict()['ColumnName'].values())
    else:
        return ActivitySummary_DF
# def DomeInsertActivitySummaryData():
#     # TODO create API for Activity Summary upload
#     pass
def DomeDeleteActivitySummaryData(DateTimeRangeList, WellInfoDict, runOnStreamlit=False):
    url_pdu_api = getURLAPI_pdu()
    TableAPI = f"{url_pdu_api}rtdc/ActivitySummary/delete"
    if isinstance(DateTimeRangeList, dict):
        ActSum_df = DomeGetActivitySummaryData(WellInfoDict, DateTimeRangeList)
        try:
            DeleteList = ActSum_df['StartDateTime'].astype('str').tolist()
        except:
            print(f"No data to delete | {DateTimeRangeList}")
            pass
    else:
        DeleteList = DateTimeRangeList
    if runOnStreamlit:
        ProgressStatusDelete = st.progress(0., text=f"Delete Activity Summary Data, 0 % Complete")
        i = 0

    for ID_or_timestart in DeleteList:
        if runOnStreamlit:
            i = i+1
            ProgressStatusDelete.progress(np.round(i/len(DeleteList),2), text=f"Delete Activity Summary Data, {ID_or_timestart} - {np.round(i/len(DeleteList),2)*100} % Complete", )
        response = (
            requests.post(
                TableAPI, 
                data=json.dumps(
                                {
                                    "wid": WellInfoDict['wid'],
                                    "time_start":ID_or_timestart
                                },
                                indent = 4
                            ) 
                )
        )
        print(f"{ID_or_timestart} - {response.json()}")

    if runOnStreamlit:
        ProgressStatusDelete.progress(1., text=f"Delete Activity Summary Data Complete")
        ProgressStatusDelete.empty()
    #     # DateTimeRangeList = [DateTimeRangeList]
    # # TODO create API for Activity Summary delete
    # # Delete by range
    # # Delete by list of DateTime
    # pass

def ActivitySummaryColumnRenameDict():
    out= {
        "ColumnName":{"wid":"wid",
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
                            # "stand_on_bottom":"OnBottomDurationPerStand",
                            "connection_activity":"LABEL_ConnectionActivity",
                            "pic":"PIC",
                            "section":"Section",
                            "remark":"Remarks",
                            "stand_group":"Stand Group_Pred",
                            },
        "DataTypeDict":{
                    "wid": 'int',
                    "Date": "datetime64[ns]",
                    "StartDateTime": "datetime64[ns]",
                    "EndDateTime": "datetime64[ns]",
                    "Duration": "float",
                    "Hole_Depth_max": "float",
                    "Bit_Depth_avg": "float",
                    "DrillingMeterage": "float",
                    "RotateDrillingDuration": "float",
                    "SlideDrillingDuration": "float",
                    "ReamingDuration": "float",
                    "ConnectionDuration": "float",
                    "OnBottomDurationPerStand": "float",
                    "StandDuration": "float",
                    "LABEL_SubActivity": "string",
                    "LABEL_Activity": "string",
                    "DrillingMeteragePerStand": "float",
                    "InSlip_Treshold": "float",
                    "PIC": "string",
                    "Section": "string",
                    "Remarks": "string",
                    "Stand Group_Pred": "string",
                    "LABEL_ConnectionActivity":"string",
                    },

    }
    return out
def DomeInsertActivitySummaryData(WellInfoDict, ActSumdf, insert_remark=False, insert_pic=False, runOnStreamlit=False):
    url_pdu_api = getURLAPI_pdu()
    # try:
    # TODO create API for Activity Summary upload
    # st.write(ActSumdf.dtypes)
    ConversionDict = ActivitySummaryColumnRenameDict()
    ActSumdf['wid'] = WellInfoDict['wid']
    if "LABEL_All" in ActSumdf.columns:
        ActSumdf = ActSumdf.drop(['LABEL_All'], axis=1)
    ActSumdf = ActSumdf.rename(
        columns={value: key for key, value in ConversionDict['ColumnName'].items()}
    )
    ActSumdf['stand_on_bottom']=0
    ActSumdf = ActSumdf.astype('string')
    i = 0
    i_end = len(ActSumdf)
    # if progressbar:
    #     ProgressBarContainer = st.session_state['PopUpWindow'].empty()
    #     ProgressBarContainer.progress(0.0)
    keys_list = ['wid', 'date', 'time_start', 'time_end', 'duration_minutes', 'hole_depth', 
                    'bit_depth', 'meterage_drilling', 'rotate_drilling_time', 'slide_drilling_time', 
                    'reaming_time', 'connection_time', 'on_bottom_hours', 'stand_duration', 'label_subactivity', 
                    'label_activity', 'stand_meterage_drilling', 'stand_durationx','connection_activity', 'stand_on_bottom',
                    'section', 'stand_group']
    if insert_remark:
        keys_list.append('remark')
    else:
        keys_list.append('remark')
        ActSumdf['remark'] = ""
    if insert_pic:
        keys_list.append('pic')
    else:
        keys_list.append('pic')
        ActSumdf['pic'] = ""
    # additional_key_list = ['pic', 'remark',] 
    ActSumdf = ActSumdf[keys_list]
    ActSumdf[["pic", "remark"]] = ActSumdf[["pic", "remark"]].fillna("")
    # ActSumdf[additional_key_list] = ""

    if runOnStreamlit:
        ProgressStatusInsert = st.progress(0., text="Upload **Activity Summary** Data, 0 % Complete")

    for idx,row in ActSumdf.iterrows():
        i = i+1
        if runOnStreamlit:
            ProgressStatusInsert.progress(np.round(i/i_end,2), text=f"Upload **New Activity Summary** Data, {np.round(i/i_end,2)*100} % Complete", )
        dict_row = row.to_dict()
        # print(dict_row)
        # IO_Data.DomeInsertData(dict_row, table_type='ActivitySummaryTable')


        AddRowAPI = f"{url_pdu_api}rtdc/ActivitySummary/create"
        json_queries = json.dumps(
                dict_row,
                indent = 4
            )
        
        # st.write(dict_row)
        response = (
            DomeRequestPOST(AddRowAPI, json_queries)
        )
    if runOnStreamlit:
        ProgressStatusInsert.progress(1. , text=f"Upload **New Activity Summary** Data Complete")
        ProgressStatusInsert.empty()
        # st.stop()
        # st.toast(dict(response.json())['message'])


        # if progressbar:
        #     ProgressBarContainer.progress(np.round(i/i_end,2), text=f"Download Realtime Sensor Data, {np.round(i/i_end,2)*100} % Complete")
    
    # if progressbar:
    #     ProgressBarContainer.progress(1)
    #     ProgressBarContainer.success("Upload Success!")
    #     time.sleep(3)
    #     ProgressBarContainer.empty()

def getLastConnectionDateTime(WellInfoDict, UserDateRange):
    # Initialize variables
    ActSum_df = None
    total_hours_adjusted = 1
    max_hours_to_adjust = 24
    isRun = True

    while isRun:
        # print(UserDateRange)
        # Get Activity Summary Data
        ActSum_df = DomeGetActivitySummaryData(WellInfoDict, UserDateRange)
        
        # print(ActSum_df['LABEL_ConnectionActivity'].unique())
        try:
            ActSum_df[['LABEL_Connection', 'LABEL_ConnectionID']] = ActSum_df['LABEL_ConnectionActivity'].str.split('-',n=1, expand=True)
        except:
            ActSum_df[['LABEL_Connection', 'LABEL_ConnectionID']] = None

        # If ActSum_df is not empty, break the loop
        if ("Connection" in ActSum_df['LABEL_Connection'].values) or (len(ActSum_df['LABEL_Activity'].unique())> 1):
            isRun = False
            break
        
        # Calculate the new StartDate and StartTime by subtracting 3 hours
        start_datetime = datetime.datetime.combine(UserDateRange["StartDate"], UserDateRange["StartTime"])
        new_start_datetime = start_datetime - datetime.timedelta(hours=total_hours_adjusted)
        
        # Update the UserDateRange
        UserDateRange["StartDate"] = new_start_datetime.date()
        UserDateRange["StartTime"] = new_start_datetime.time()
        
        # Update the total hours adjusted
        total_hours_adjusted += 1
        
        # # If we've adjusted more than 24 hours, stop adjusting
        if total_hours_adjusted >= max_hours_to_adjust:
            break
    
    # # If ActSum_df is still empty after the loop, return None or handle as needed
    # if ActSum_df.empty:
    #     return None

    # Return the last 'EndDateTime' if ActSum_df is not empty
    if ("Connection" in ActSum_df['LABEL_Connection'].values):

        # LastActSumDateTime = ActSum_df[ActSum_df['LABEL_Connection']=='Connection']
        LastConnectionID = ActSum_df[ActSum_df['LABEL_Connection']=='Connection'].tail(1)
        LastConnectionID = LastConnectionID['LABEL_ConnectionID'].values[0]
        LastConnectionGroup = ActSum_df[ActSum_df['LABEL_ConnectionID']==LastConnectionID]
        

        
        LastActSumDateTime = LastConnectionGroup.head(1)
    else:
        LABEL_Act_temp = list(ActSum_df.tail(1)['LABEL_Activity'].values)[0]
        # display(LABEL_Act_temp)
        LastActSumDateTime = ActSum_df[ActSum_df['LABEL_Activity']==LABEL_Act_temp]
        LastActSumDateTime = LastActSumDateTime.head(1)
    return LastActSumDateTime

def getLastActSum(WellInfoDict, UserDateRange, DrillActivityList='default'):
    """
    This function retrieves the last activity summary for a given well within a specified date range.
    If the activity summary is empty, it adjusts the start date and time by subtracting 3 hours until it finds data or has adjusted a total of 24 hours.
    If the last activity is in the DrillActivityList, it retrieves the last connection date and time.
    
    Parameters:
    WellInfoDict (dict): Dictionary containing well information.
    UserDateRange (dict): Dictionary containing the start and end date and time for the data retrieval.
    DrillActivityList (list, optional): List of drilling activities to check in the last activity summary. Defaults to a predefined list of activities.
    
    Returns:
    DataFrame or None: Returns the last activity summary as a DataFrame if found, else returns None.
    """
    
    # Set default DrillActivityList if not provided
    if DrillActivityList =='default':
        DrillActivityList = ["DRILLING FORMATION", 'CIRCULATE HOLE CLEANING','CONNECTION','DRILL OUT CEMENT']
    
    # Initialize variables
    ActSum_df = None
    total_hours_adjusted = 1
    max_hours_to_adjust = 24

    # Loop until we get a non-empty activity summary or have adjusted the start time by 24 hours
    while ActSum_df is None or ActSum_df.empty:
        # Get Activity Summary Data
        ActSum_df = DomeGetActivitySummaryData(WellInfoDict, UserDateRange)

        # If ActSum_df is not empty, break the loop
        if not ActSum_df.empty:
            break
        
        # Calculate the new StartDate and StartTime by subtracting 3 hours
        start_datetime = datetime.combine(UserDateRange["StartDate"], UserDateRange["StartTime"])
        new_start_datetime = start_datetime - timedelta(hours=total_hours_adjusted)
        
        # Update the UserDateRange
        UserDateRange["StartDate"] = new_start_datetime.date()
        UserDateRange["StartTime"] = new_start_datetime.time()
        
        # Update the total hours adjusted
        total_hours_adjusted += 1
        
        # If we've adjusted more than 24 hours, stop adjusting
        if total_hours_adjusted >= max_hours_to_adjust:
            break
    

    # Get the last row of the activity summary
    LastActSum_df = ActSum_df.tail(1)
    # If ActSum_df is still empty after the loop, return None
    if ActSum_df.empty:
        LastActSum_df = pd.DataFrame({
            # "StartDateTime": [datetime.combine(UserDateRange["StartDate"], UserDateRange["StartTime"])],
            "StartDateTime": [datetime.combine(UserDateRange["StartDate"], UserDateRange["StartTime"])],
            # "StartDateTime": [datetime.combine(UserDateRange["StartDate"], UserDateRange["StartTime"])],
            # "EndDateTime": [datetime.combine(UserDateRange["EndDate"], UserDateRange["EndTime"])],
            'LABEL_Activity': ['N/A'],
        })
        LastActSum_df['StartDateTime'] = LastActSum_df['StartDateTime'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # If the last activity is in the DrillActivityList, get the last connection date and time
    if LastActSum_df['LABEL_Activity'].values[0] in DrillActivityList:
        return getLastConnectionDateTime(WellInfoDict, UserDateRange)
    else:
        return LastActSum_df






def getBeforeConnectionDateTime(WellInfoDict, UserDateRange):
    # Initialize variables
    ActSum_df = None
    total_hours_adjusted = 1
    max_hours_to_adjust = 24
    isRun = True

    while isRun:
        # print(UserDateRange)
        # Get Activity Summary Data
        ActSum_df = DomeGetActivitySummaryData(WellInfoDict, UserDateRange)
        
        # print(ActSum_df['LABEL_ConnectionActivity'].unique())
        try:
            ActSum_df[['LABEL_Connection', 'LABEL_ConnectionID']] = ActSum_df['LABEL_ConnectionActivity'].str.split('-',n=1, expand=True)
        except:
            ActSum_df[['LABEL_Connection', 'LABEL_ConnectionID']] = None

        # If ActSum_df is not empty, break the loop
        if ("Connection" in ActSum_df['LABEL_Connection'].values) or (len(ActSum_df['LABEL_Activity'].unique())> 1):
            isRun = False
            break
        
        # Calculate the new StartDate and StartTime by subtracting 3 hours
        start_datetime = datetime.datetime.combine(UserDateRange["StartDate"], UserDateRange["StartTime"])
        new_start_datetime = start_datetime - datetime.timedelta(hours=total_hours_adjusted)
        
        # Update the UserDateRange
        UserDateRange["StartDate"] = new_start_datetime.date()
        UserDateRange["StartTime"] = new_start_datetime.time()
        
        # Update the total hours adjusted
        total_hours_adjusted = total_hours_adjusted + 1
        
        # # If we've adjusted more than 24 hours, stop adjusting
        if total_hours_adjusted >= max_hours_to_adjust:
            isRun = False
            break
    
    # # If ActSum_df is still empty after the loop, return None or handle as needed
    # if ActSum_df.empty:
    #     return None

    # Return the last 'EndDateTime' if ActSum_df is not empty
    if ("Connection" in ActSum_df['LABEL_Connection'].values):

        # LastActSumDateTime = ActSum_df[ActSum_df['LABEL_Connection']=='Connection']
        LastConnectionID = ActSum_df[ActSum_df['LABEL_Connection']=='Connection'].tail(1)
        LastConnectionID = LastConnectionID['LABEL_ConnectionID'].values[0]
        LastConnectionGroup = ActSum_df[ActSum_df['LABEL_ConnectionID']==LastConnectionID]
        

        
        LastActSumDateTime = LastConnectionGroup.head(1)
    else:
        LABEL_Act_temp = list(ActSum_df.tail(1)['LABEL_Activity'].values)[0]
        # display(LABEL_Act_temp)
        LastActSumDateTime = ActSum_df[ActSum_df['LABEL_Activity']==LABEL_Act_temp]
        LastActSumDateTime = LastActSumDateTime.head(1)
    return LastActSumDateTime

def getNextConnectionDateTime(WellInfoDict, UserDateRange):
    # Initialize variables
    ActSum_df = None
    total_hours_adjusted = 1
    max_hours_to_adjust = 24
    isRun = True

    while isRun:
        # print(UserDateRange)
        # Get Activity Summary Data
        ActSum_df = DomeGetActivitySummaryData(WellInfoDict, UserDateRange)
        
        # print(ActSum_df['LABEL_ConnectionActivity'].unique())
        try:
            ActSum_df[['LABEL_Connection', 'LABEL_ConnectionID']] = ActSum_df['LABEL_ConnectionActivity'].str.split('-',n=1, expand=True)
        except:
            ActSum_df[['LABEL_Connection', 'LABEL_ConnectionID']] = None

        # If ActSum_df is not empty, break the loop
        if ("Connection" in ActSum_df['LABEL_Connection'].values) or (len(ActSum_df['LABEL_Activity'].unique())> 1):
            isRun = False
            break
        
        # Calculate the new StartDate and StartTime by subtracting 3 hours
        end_datetime = datetime.datetime.combine(UserDateRange["EndDate"], UserDateRange["EndTime"])
        new_end_datetime = end_datetime + datetime.timedelta(hours=total_hours_adjusted)

        total_hours_adjusted = total_hours_adjusted + 1
        
        # Update the UserDateRange
        UserDateRange["EndDate"] = new_end_datetime.date()
        UserDateRange["EndTime"] = new_end_datetime.time()
        
        # # If we've adjusted more than 24 hours, stop adjusting
        if total_hours_adjusted >= max_hours_to_adjust:
            isRun = False
            break
    
    # # If ActSum_df is still empty after the loop, return None or handle as needed
    # if ActSum_df.empty:
    #     return None

    # Return the last 'EndDateTime' if ActSum_df is not empty
    if ("Connection" in ActSum_df['LABEL_Connection'].values):

        # LastActSumDateTime = ActSum_df[ActSum_df['LABEL_Connection']=='Connection']
        LastConnectionID = ActSum_df[ActSum_df['LABEL_Connection']=='Connection'].head(1)
        LastConnectionID = LastConnectionID['LABEL_ConnectionID'].values[0]
        LastConnectionGroup = ActSum_df[ActSum_df['LABEL_ConnectionID']==LastConnectionID]
        

        
        LastActSumDateTime = LastConnectionGroup.tail(1)
    else:
        LABEL_Act_temp = list(ActSum_df.head(1)['LABEL_Activity'].values)[0]
        # display(LABEL_Act_temp)
        LastActSumDateTime = ActSum_df[ActSum_df['LABEL_Activity']==LABEL_Act_temp]
        LastActSumDateTime = LastActSumDateTime.head(1)
    return LastActSumDateTime

def getBeforeActSum(WellInfoDict, UserDateRange, DrillActivityList='default'):
    """
    This function retrieves the last activity summary for a given well within a specified date range.
    If the activity summary is empty, it adjusts the start date and time by subtracting 3 hours until it finds data or has adjusted a total of 24 hours.
    If the last activity is in the DrillActivityList, it retrieves the last connection date and time.
    
    Parameters:
    WellInfoDict (dict): Dictionary containing well information.
    UserDateRange (dict): Dictionary containing the start and end date and time for the data retrieval.
    DrillActivityList (list, optional): List of drilling activities to check in the last activity summary. Defaults to a predefined list of activities.
    
    Returns:
    DataFrame or None: Returns the last activity summary as a DataFrame if found, else returns None.
    """
    
    # Set default DrillActivityList if not provided
    if DrillActivityList =='default':
        DrillActivityList = ["DRILLING FORMATION", 'CIRCULATE HOLE CLEANING','CONNECTION','DRILL OUT CEMENT']
    
    # Initialize variables
    ActSum_df = None
    total_hours_adjusted = 1
    max_hours_to_adjust = 24

    # Loop until we get a non-empty activity summary or have adjusted the start time by 24 hours
    while ActSum_df is None or ActSum_df.empty:
        # Get Activity Summary Data
        ActSum_df = DomeGetActivitySummaryData(WellInfoDict, UserDateRange)

        # If ActSum_df is not empty, break the loop
        if not ActSum_df.empty:
            break
        
        # Calculate the new StartDate and StartTime by subtracting 3 hours
        start_datetime = datetime.datetime.combine(UserDateRange["StartDate"], UserDateRange["StartTime"])
        new_start_datetime = start_datetime - datetime.timedelta(hours=total_hours_adjusted)
        
        # Update the UserDateRange
        UserDateRange["StartDate"] = new_start_datetime.date()
        UserDateRange["StartTime"] = new_start_datetime.time()
        
        # Update the total hours adjusted
        total_hours_adjusted += 1
        
        # If we've adjusted more than 24 hours, stop adjusting
        if total_hours_adjusted >= max_hours_to_adjust:
            break
    
    # If ActSum_df is still empty after the loop, return None
    if ActSum_df.empty:
        return None

    # Get the last row of the activity summary
    LastActSum_df = ActSum_df.tail(1)
    
    # If the last activity is in the DrillActivityList, get the last connection date and time
    if LastActSum_df['LABEL_Activity'].values[0] in DrillActivityList:
        return getBeforeConnectionDateTime(WellInfoDict, UserDateRange)
    else:
        return LastActSum_df
def getNextActSum(WellInfoDict, UserDateRange, DrillActivityList='default'):
    """
    This function retrieves the last activity summary for a given well within a specified date range.
    If the activity summary is empty, it adjusts the start date and time by subtracting 3 hours until it finds data or has adjusted a total of 24 hours.
    If the last activity is in the DrillActivityList, it retrieves the last connection date and time.
    
    Parameters:
    WellInfoDict (dict): Dictionary containing well information.
    UserDateRange (dict): Dictionary containing the start and end date and time for the data retrieval.
    DrillActivityList (list, optional): List of drilling activities to check in the last activity summary. Defaults to a predefined list of activities.
    
    Returns:
    DataFrame or None: Returns the last activity summary as a DataFrame if found, else returns None.
    """
    
    # Set default DrillActivityList if not provided
    if DrillActivityList =='default':
        DrillActivityList = ["DRILLING FORMATION", 'CIRCULATE HOLE CLEANING','CONNECTION','DRILL OUT CEMENT']
    
    # Initialize variables
    ActSum_df = None
    total_hours_adjusted = 1
    max_hours_to_adjust = 24

    # Loop until we get a non-empty activity summary or have adjusted the start time by 24 hours
    while ActSum_df is None or ActSum_df.empty:
        # Get Activity Summary Data
        ActSum_df = DomeGetActivitySummaryData(WellInfoDict, UserDateRange)

        # If ActSum_df is not empty, break the loop
        if not ActSum_df.empty:
            break
        
        # Calculate the new StartDate and StartTime by subtracting 3 hours
        end_datetime = datetime.datetime.combine(UserDateRange["EndDate"], UserDateRange["EndTime"])
        new_end_datetime = end_datetime + datetime.timedelta(hours=total_hours_adjusted)
        
        # Update the UserDateRange
        UserDateRange["EndDate"] = new_end_datetime.date()
        UserDateRange["EndTime"] = new_end_datetime.time()
        
        # Update the total hours adjusted
        total_hours_adjusted += 1
        # If we've adjusted more than 24 hours, stop adjusting
        if total_hours_adjusted >= max_hours_to_adjust:
            break
    
    # If ActSum_df is still empty after the loop, return None
    if ActSum_df.empty:
        return None

    # Get the last row of the activity summary
    NextActSum_df = ActSum_df.head(1)
    
    # If the last activity is in the DrillActivityList, get the last connection date and time
    if NextActSum_df['LABEL_Activity'].values[0] in DrillActivityList:
        return getNextConnectionDateTime(WellInfoDict, UserDateRange)
    else:
        return NextActSum_df


# Section Parameter
def DomeSectionParamsTable_Get(WellInfoDict):
    url_pdu_fastapi = getURLAPI_FastAPI()

    API_Request = f"{url_pdu_fastapi}section-params-table/get/"
    json_queries = json.dumps(
        {
            "wid": WellInfoDict['wid'],
            "cid": WellInfoDict['cid'],
        },
        indent = 4
    )
    print('test==========================================================')
    response = DomeRequestPOST(API_Request, json_queries)
    print('test==========================================================')
    print(response)
    SectionParamsTable_df =  pd.DataFrame(response.json())
    # Convert 'wid' to integer
    for colname in ['wid']:
        SectionParamsTable_df[colname] = SectionParamsTable_df[colname].astype(int)

    # Convert 'StartDateTime' and 'EndDateTime' to datetime
    for colname in ['DateTime']:
        SectionParamsTable_df[colname] = pd.to_datetime(SectionParamsTable_df[colname],  format="%Y-%m-%d %H:%M:%S")

    # 'OtherColumn' is already of type string (object in pandas), but if you need to ensure:
    for colname in ['SectionSize',		'PIC']:
        SectionParamsTable_df[colname] = SectionParamsTable_df[colname].astype(str)   
    SectionParamsTable_df['InSlipThreshold'] = SectionParamsTable_df['InSlipThreshold'].astype(float)

    SectionParamsTable_df.rename(columns={'SectionSize': 'Section Size',}, inplace=True)
    SectionParamsTable_df.rename(columns={'InSlipThreshold': 'In-Slip Threshold',}, inplace=True)
    SectionParamsTable_df = SectionParamsTable_df[SectionParamsTable_df['wid'] == WellInfoDict['wid']]

    return SectionParamsTable_df

def DomeSectionParamsTable_Delete(DeleteJSON):
    print("delete: ")
    print(DeleteJSON)
    # DeleteJSON = json.loads(DeleteJSON)
    key_mapping = {'DateTime': 'DateTime', 
                   'Section Size': 'SectionSize',
                   'In-Slip Threshold': 'InSlipThreshold',
                     'PIC': 'PIC',
                     'wid': 'wid',
                   }

    new_dict = {}
    for old_key, new_key in key_mapping.items():
        print(f"{old_key} = {new_key}")
        if old_key in DeleteJSON:
            new_dict[new_key] = DeleteJSON[old_key]
    DeleteJSON = new_dict
    # return None
    url_pdu_fastapi = getURLAPI_FastAPI()

    API_Request = f"{url_pdu_fastapi}section-params-table/delete/"

    # json_queries = json.dumps(
    #     DeleteDict,
    #     indent = 4
    # )
    # print(DomeRequestPOST(API_Request, json_queries))
    if isinstance(DeleteJSON, dict):
        DeleteJSON = json.dumps(
            DeleteJSON,
            indent = 4
        )
    print(DomeRequestPOST(API_Request, DeleteJSON))
def DomeSectionParamsTable_Insert(InsertJSON):
    # InsertJSON = json.loads(InsertJSON)
    key_mapping = {'DateTime': 'DateTime', 
                   'Section Size': 'SectionSize',
                   'In-Slip Threshold': 'InSlipThreshold',
                     'PIC': 'PIC',
                     'wid': 'wid',
                   }

    new_dict = {}
    for old_key, new_key in key_mapping.items():
        if old_key in InsertJSON:
            new_dict[new_key] = InsertJSON[old_key]
    
    InsertJSON = new_dict
    try:
        new_dict['DateTime'] =  datetime.strptime(new_dict['DateTime'],"%Y-%m-%dT%H:%M:%S.%f")
        new_dict['DateTime'] =  datetime.strftime(new_dict['DateTime'],"%Y-%m-%d %H:%M:%S")
    except:
        pass
    print("insert: ")
    print(InsertJSON)
    
    # return None
    url_pdu_fastapi = getURLAPI_FastAPI()

    API_Request = f"{url_pdu_fastapi}section-params-table/insert/"
    if isinstance(new_dict, dict):
        InsertJSON = json.dumps(
            InsertJSON,
            indent = 4
        )
    # print(DomeRequestPOST(API_Request, json_queries))
    print(DomeRequestPOST(API_Request, InsertJSON))


# Override Parameter
def DomeOverrideActivity_Delete(DeleteJSON):
    print("delete: ")
    print(DeleteJSON)
    # return None
    url_pdu_fastapi = getURLAPI_FastAPI()

    API_Request = f"{url_pdu_fastapi}override-activity-table/delete/"

    # json_queries = json.dumps(
    #     DeleteDict,
    #     indent = 4
    # )
    # print(DomeRequestPOST(API_Request, json_queries))
    if isinstance(DeleteJSON, dict):
        DeleteJSON = json.dumps(
            DeleteJSON,
            indent = 4
        )
    print(DomeRequestPOST(API_Request, DeleteJSON))
    
def DomeOverrideActivity_Insert(InsertJSON):
    print("insert: ")
    print(InsertJSON)
    # return None
    url_pdu_fastapi = getURLAPI_FastAPI()

    API_Request = f"{url_pdu_fastapi}override-activity-table/insert/"
    if isinstance(InsertJSON, dict):
        InsertJSON = json.dumps(
            InsertJSON,
            indent = 4
        )
    # print(DomeRequestPOST(API_Request, json_queries))
    print(DomeRequestPOST(API_Request, InsertJSON))

def DomeOverrideActivity_Get(WellInfoDict):
    url_pdu_fastapi = getURLAPI_FastAPI()

    API_Request = f"{url_pdu_fastapi}override-activity-table/get/"
    json_queries = json.dumps(
        {
    "wid": WellInfoDict['wid'],
    "cid": WellInfoDict['cid'],
        },
        indent = 4
    )
    response = DomeRequestPOST(API_Request, json_queries)
    OverideActivity_df =  pd.DataFrame(response.json())
    # Convert 'wid' to integer
    for colname in ['wid']:
        OverideActivity_df[colname] = OverideActivity_df[colname].astype(int)

    # Convert 'StartDateTime' and 'EndDateTime' to datetime
    for colname in ['StartDateTime', 'EndDateTime']:
        # st.write(OverideActivity_df[colname])
        # st.stop()
        OverideActivity_df[colname] = pd.to_datetime(OverideActivity_df[colname], format='mixed')

    # 'OtherColumn' is already of type string (object in pandas), but if you need to ensure:
    for colname in ['LABEL_ACTIVITY', 'LABEL_SUBACTIVITY', 'PIC']:
        OverideActivity_df[colname] = OverideActivity_df[colname].astype(str)   

    return OverideActivity_df



