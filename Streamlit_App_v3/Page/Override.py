import streamlit as st
import requests
import time
import pandas as pd 
import json
import numpy as np
from datetime import datetime, timedelta
import datetime as datetime_module
from PDU_Func import Activity, Authentification, IO_Data
from Page.SubPage import RealtimeDataViz
from importlib import reload
reload(IO_Data)
reload(Activity)
reload(RealtimeDataViz)
def DomeRequestPOST(API, Data_params):
    return requests.post(API, data=Data_params)
def DomeRequestGET(API, Data_params):
    return requests.get(API, data=Data_params)
# =================================================================================================

def UpdateOverrideTable(OverideActivity_df, WellInfoDict, PrefixKey):

    OverideActivity_df = OverideActivity_df.copy()
    OverideActivity_df['wid'] = int(WellInfoDict['wid'])
    list_col_str = ['StartDateTime', 'EndDateTime', 'LABEL_ACTIVITY', 'LABEL_SUBACTIVITY', 'PIC']
    OverideActivity_df[list_col_str] = OverideActivity_df[list_col_str].astype(str)
    print(st.session_state[f"{PrefixKey}_DataEditor"])
    list_startdatetime = []
    list_enddatetime = []
    ######### If User Update the Table
    if st.session_state[f"{PrefixKey}_DataEditor"]['edited_rows'] != []:
        for key,val in st.session_state[f"{PrefixKey}_DataEditor"]['edited_rows'].items():
            
            IO_Data.DomeOverrideActivity_Delete(
                    OverideActivity_df.loc[int(key), ['wid','StartDateTime','EndDateTime']].to_json()
                )

            for colname,colval in val.items():
                OverideActivity_df.loc[key, colname] = colval
            IO_Data.DomeOverrideActivity_Insert(
                    OverideActivity_df.loc[int(key), :].to_json()
                )
            list_startdatetime.append(OverideActivity_df.loc[int(key), 'StartDateTime'])
            list_enddatetime.append(OverideActivity_df.loc[int(key), 'EndDateTime'])



    datetime_format = "%Y-%m-%dT%H:%M:%S.%f"
    ######### If User Insert the Table
    if st.session_state[f"{PrefixKey}_DataEditor"]['added_rows'] != []:
        for InsertDict in st.session_state[f"{PrefixKey}_DataEditor"]['added_rows']:
            InsertDict['wid'] = int(int(WellInfoDict['wid']))
            for datetime_key in ['StartDateTime', 'EndDateTime']:
                InsertDict[datetime_key] =  datetime.strptime(InsertDict[datetime_key],datetime_format)
                InsertDict[datetime_key] =  datetime.strftime(InsertDict[datetime_key],"%Y-%m-%d %H:%M:%S")
            IO_Data.DomeOverrideActivity_Insert(InsertDict)
            list_startdatetime.append(InsertDict['StartDateTime'])
            list_enddatetime.append(InsertDict['EndDateTime'])


    ######### If User Delete the Table
    if st.session_state[f"{PrefixKey}_DataEditor"]['deleted_rows'] != []:
        for idxrow in st.session_state[f"{PrefixKey}_DataEditor"]['deleted_rows']:
            IO_Data.DomeOverrideActivity_Delete(
                    OverideActivity_df.loc[int(idxrow), ['wid','StartDateTime','EndDateTime']].to_json()
                )
            list_startdatetime.append(OverideActivity_df.loc[int(idxrow), 'StartDateTime'])
            list_enddatetime.append(OverideActivity_df.loc[int(idxrow), 'EndDateTime'])
    st.toast(list_startdatetime)
    st.toast(list_enddatetime)
    SyncUpdateRealtimeData(WellInfoDict, list_startdatetime, list_enddatetime)
    del st.session_state[f"{PrefixKey}_DataEditor"]
    del st.session_state[f"{PrefixKey}_df"]
    # pass


def OverrideActivityTableWidget(WellInfoDict, container, 
                          PrefixKey = 'OverrideActivityTable' , 
                          TripActivityList='default', DrillActivityList='default', OverrideActivityList='default'):
    if isinstance(TripActivityList, str):
        TripActivityList = ['TRIP IN', 'TRIP OUT', 'WIPER TRIP',]
    if isinstance(DrillActivityList, str):
        DrillActivityList = ["DRILLING FORMATION", 'CIRCULATE HOLE CLEANING','CONNECTION','DRILL OUT CEMENT',]
    if isinstance(OverrideActivityList, str):
        OverrideActivityList = ['CEMENTING JOB', 'CONNECTION', 'LAY DOWN BHA', 'MAKE UP BHA', 'NPT', 'N/D BOP', 
                                'N/U BOP', 'RUNNING CASING IN', 'STATIONARY', 'STUCK PIPE', 'WAIT ON CEMENT', 'RIG REPAIR','N/A', 'OTHER',]

    
    DrillSubActivityList = ['Rotary Drilling','Slide Drilling','Reaming','Wash Up/Down','Connection']
    TripSubActivityList = ['Wash Up/Down','Reaming','Moving','Circulation','Connection','Stationary']
    if f"{PrefixKey}_df" not in st.session_state:
        st.session_state[f"{PrefixKey}_df"] =  IO_Data.DomeOverrideActivity_Get(WellInfoDict)
    OverideActivity_df = st.session_state[f"{PrefixKey}_df"]
    OverrideActivity_ColConfig = {
            "StartDateTime": st.column_config.DatetimeColumn(
                "Start Date Time",
                format="YYYY-MM-DD | HH:mm:ss",
                step=5,
                width="medium",
                required=True,
            ),
            "EndDateTime": st.column_config.DatetimeColumn(
                "End Date Time",
                format="YYYY-MM-DD | HH:mm:ss",
                step=5,
                width="medium",
                required=True,
            ),
            "LABEL_ACTIVITY": st.column_config.SelectboxColumn(
                "Activity",
                options=TripActivityList + DrillActivityList + OverrideActivityList,
                width="medium",
                required=True,
            ),
            "LABEL_SUBACTIVITY": st.column_config.SelectboxColumn(
                "Sub Activity",
                options=DrillSubActivityList + TripSubActivityList+ TripActivityList + DrillActivityList + OverrideActivityList,
                width="medium",
                required=True,
            ),
            "PIC": st.column_config.TextColumn(
                "PIC",
                default=st.session_state['UserAuthDict']['data']['user_id'],
                disabled =True,
            )
        }
    with container.form(f"{PrefixKey}_Form", clear_on_submit=True):
        output = st.data_editor(OverideActivity_df, 
                                column_order=[ 'StartDateTime', 'EndDateTime', 'LABEL_ACTIVITY', 'LABEL_SUBACTIVITY', 'PIC'],
                                hide_index = True,
                                column_config=OverrideActivity_ColConfig,
                                key=f"{PrefixKey}_DataEditor", num_rows='dynamic', use_container_width=True)
        st.form_submit_button("Submit", on_click=UpdateOverrideTable, args=(OverideActivity_df,WellInfoDict,PrefixKey))
# =================================================================================================


def UpdateSectionParamsTable(SectionParamsTable_df, wid, PrefixKey):

    SectionParamsTable_df = SectionParamsTable_df.copy()
    SectionParamsTable_df['wid'] = int(wid)
    list_col_str = ['DateTime', 'Section Size',	'PIC']
    SectionParamsTable_df[list_col_str] = SectionParamsTable_df[list_col_str].astype(str)
    SectionParamsTable_df['In-Slip Threshold'] = SectionParamsTable_df['In-Slip Threshold'].astype(float)
    # SectionParamsTable_df['SectionSize'] = SectionParamsTable_df['SectionSize'].replace('"', '')
    print(st.session_state[f"{PrefixKey}_DataEditor"])
    ## If User Update the Table
    if st.session_state[f"{PrefixKey}_DataEditor"]['edited_rows'] != []:
        for key,val in st.session_state[f"{PrefixKey}_DataEditor"]['edited_rows'].items():
            

            IO_Data.DomeSectionParamsTable_Delete(
                    SectionParamsTable_df.loc[int(key), ['wid','DateTime','Section Size', 'In-Slip Threshold', 'PIC']].to_dict()
                )

            for colname,colval in val.items():
                SectionParamsTable_df.loc[key, colname] = colval
            IO_Data.DomeSectionParamsTable_Insert(
                    SectionParamsTable_df.loc[int(key), :].to_dict()
                )

    

    datetime_format = "%Y-%m-%dT%H:%M:%S.%f"
    ## If User Insert the Table
    if st.session_state[f"{PrefixKey}_DataEditor"]['added_rows'] != []:
        for InsertDict in st.session_state[f"{PrefixKey}_DataEditor"]['added_rows']:
            InsertDict['wid'] = int(wid)
            InsertDict['In-Slip Threshold'] = float(InsertDict['In-Slip Threshold'])
            # InsertDict['SectionSize'] = str(InsertDict['SectionSize']).replace('"', '')
            for datetime_key in ['DateTime']:
                InsertDict[datetime_key] =  datetime.strptime(InsertDict[datetime_key],datetime_format)
                InsertDict[datetime_key] =  datetime.strftime(InsertDict[datetime_key],"%Y-%m-%d %H:%M:%S")
            IO_Data.DomeSectionParamsTable_Insert(InsertDict)

    ## If User Delete the Table
    if st.session_state[f"{PrefixKey}_DataEditor"]['deleted_rows'] != []:
        for idxrow in st.session_state[f"{PrefixKey}_DataEditor"]['deleted_rows']:
            IO_Data.DomeSectionParamsTable_Delete(
                    SectionParamsTable_df.loc[int(idxrow), ['wid','DateTime','Section Size', 'In-Slip Threshold', 'PIC']].to_dict()
                )
    del st.session_state[f"{PrefixKey}_DataEditor"]
    del st.session_state[f"{PrefixKey}_df"]
def SectionParamsTableWidget(WellInfoDict, container, 
                          PrefixKey = 'SectionParamsTable' , 
                          SectionSizeList='default',):
    if isinstance(SectionSizeList, str):
        SectionSizeList=['26"','17-1/2"','12-1/4"','9-7/8"', '7-7/8"', '8.5"','6-3/4"', '6-1/8"','6"', ]


    if f"{PrefixKey}_df" not in st.session_state:
        st.session_state[f"{PrefixKey}_df"] =  IO_Data.DomeSectionParamsTable_Get(WellInfoDict)
    SectionParamsTable_df = st.session_state[f"{PrefixKey}_df"]
    SectionParamsTable_ColConfig = {
            "DateTime": st.column_config.DatetimeColumn(
                "Date Time",
                format="YYYY-MM-DD | HH:mm:ss",
                step=5,
                width="medium",
                required=True,
            ),
            "Section Size": st.column_config.SelectboxColumn(
                "Section Size",
                options=SectionSizeList,
                width="medium",
                required=True,
            ),
            "In-Slip Threshold": st.column_config.NumberColumn(
                "In-Slip Threshold",
                min_value=0,
                max_value=1000,
                step=1,
                format="%.1f",
                width="medium",
                required=True,
            ),
            "PIC": st.column_config.TextColumn(
                "PIC",
                default=st.session_state['UserAuthDict']['data']['user_id'],
                disabled =True,
            )
        }
    with container.form(f"{PrefixKey}_Form", clear_on_submit=True):
        output = st.data_editor(SectionParamsTable_df, 
                                column_order=[ 'DateTime', 'Section Size', 'In-Slip Threshold', 'PIC'],
                                hide_index = True,
                                column_config=SectionParamsTable_ColConfig,
                                key=f"{PrefixKey}_DataEditor", num_rows='dynamic', use_container_width=True)
        st.form_submit_button("Submit", on_click=UpdateSectionParamsTable, args=(SectionParamsTable_df,WellInfoDict['wid'],PrefixKey))
# =================================================================================================
def SyncUpdateRealtimeData(WellInfoDict, list_startdatetime, list_enddatetime):
    print(list_startdatetime)
    print(list_enddatetime)

    # TODO uncomment the code below
    for startdatetime, enddatetime in zip(list_startdatetime, list_enddatetime):
        DomeUpdateRealtimeData(WellInfoDict, startdatetime, enddatetime)

def DomeUpdateRealtimeData(WellInfoDict:dict, 
               startdatetime: str ,
               enddatetime: str ,):

    # WellInfoDict = {
    # "cid": cid,
    # "wid": wid,
    # }
    # TODO change with the SectionParams Table
    SectionParams_DF = IO_Data.DomeSectionParamsTable_Get(WellInfoDict)
    df_list = []


    StartDateTime_obj =  datetime.strptime(startdatetime, '%Y-%m-%d %H:%M:%S')
    EndDateTime_obj =  datetime.strptime(enddatetime, '%Y-%m-%d %H:%M:%S')

    # UserDateRange_Sync = {
    # "StartDate": StartDateTime_obj.date(),
    # "StartTime": StartDateTime_obj.time(),
    # "EndDate": EndDateTime_obj.date(),
    # "EndTime": EndDateTime_obj.time(),
    # }

    # df_list.append(pd.DataFrame.from_records([UserDateRange_Sync]))

# This section is to readjust the startdatetime and enddatetime
    # TODO redefine the startdatetime and enddatetime readjustment
    UserDateRange_Sync = RedefinedUserDateRange(WellInfoDict, {
                                            "StartDate": StartDateTime_obj.date(),
                                            "StartTime": StartDateTime_obj.time(),
                                            "EndDate": EndDateTime_obj.date(),
                                            "EndTime": EndDateTime_obj.time(),
                                            })
    st.toast(UserDateRange_Sync)
    # defined_startdate = StartDateTime_obj.date()
    # defined_starttime = StartDateTime_obj.time()
    # defined_enddate = EndDateTime_obj.date()
    # defined_endtime = EndDateTime_obj.time()

    # # Section Parameter
    # UserDateRange = {
    # "StartDate": datetime.date(2003, 4, 10),
    # "StartTime": datetime.time(10, 51),
    # "EndDate": defined_startdate,
    # "EndTime": defined_starttime
    # }
    # LastActSum = (IO_Data.getBeforeActSum(WellInfoDict,
    #                                        {
    #                                             "StartDate": datetime.date(2003, 4, 10),
    #                                             "StartTime": datetime.time(10, 51),
    #                                             "EndDate": defined_startdate,
    #                                             "EndTime": defined_starttime
    #                                         }, 
    #                                        DrillActivityList='default'))
    # display(LastActSum)
    # UserDateRange = {
    # "StartDate": defined_enddate,
    # "StartTime": defined_endtime,
    # "EndDate": datetime.date(2300, 4, 10),
    # "EndTime": datetime.time(11, 9)
    # }
    # NextActSum = (IO_Data.getNextActSum(WellInfoDict, 
    #                             {
    #                                 "StartDate": defined_enddate,
    #                                 "StartTime": defined_endtime,
    #                                 "EndDate": datetime.date(2300, 4, 10),
    #                                 "EndTime": datetime.time(11, 9)
    #                             }, 
    #                             DrillActivityList='default'))


    # display(NextActSum)
    # StartDateTime_obj =  datetime.strptime(LastActSum['StartDateTime'].values[0], '%Y-%m-%d %H:%M:%S')

    # EndDateTime_obj =  datetime.strptime(NextActSum['EndDateTime'].values[0], '%Y-%m-%d %H:%M:%S')
    # NewUserDateRange = {
    #     "StartDate": StartDateTime_obj.date(),
    #     "StartTime": StartDateTime_obj.time(),
    #     "EndDate": EndDateTime_obj.date(),
    #     "EndTime": EndDateTime_obj.time(),
    #     }
    # DomeGetActivitySummaryData(WellInfoDict, NewUserDateRange)
    
# New startdatetime and enddatetime
    # UserDateRange_Sync = {
    # "StartDate": StartDateTime_obj.date(),
    # "StartTime": StartDateTime_obj.time(),
    # "EndDate": EndDateTime_obj.date(),
    # "EndTime": EndDateTime_obj.time()
    # }
    # df_list.append(pd.DataFrame.from_records([UserDateRange_Sync]))
    RTSensor_DF = IO_Data.DomeGetRealtimeSensorData(WellInfoDict,
                                                        UserDateRange_Sync, 
                                                        hours=0.5, 
                                                        show_progress=False, 
                                                        runOnStreamlit=False,
                                                        )
    RigActivity_DF = (IO_Data.getRigActivity(WellInfoDict, 
                    start_date="2000-01-01 00:00:01", 
                    end_date="2100-01-01 00:00:01"))
    RTSensor_DF = Activity.addRigActivityLabel (
                        RTSensor_DF, 
                        Activity.translateRigActivity2Activity(RigActivity_DF)
                        )
    RTSensor_DF = Activity.addSectionParams (
                        RTSensor_DF, 
                        SectionParams_DF
                        )
    RTSensor_DF = Activity.predictSubActivityLabel(
                        RTSensor_DF, 
                        TripActivityList='default', 
                        DrillActivityList='default', 
                        OverrideActivityList='default')
    Override_df = IO_Data.DomeOverrideActivity_Get(WellInfoDict)
    RTSensor_DF = Activity.Override(RTSensor_DF, Override_df)

    # TODO add the override labelling here

    ActivitySummary_DF= Activity.groupActivity(RTSensor_DF , DrillActivityList='default')
    ActivitySummary_DF = Activity.cleanFalseSensor(ActivitySummary_DF)
    ActivitySummary_DF = Activity.getStandLabel(ActivitySummary_DF)
    # TODO delete the ActivitySummary in startdatetime enddatetime range
    IO_Data.DomeDeleteActivitySummaryData(UserDateRange_Sync, WellInfoDict)
    
    # TODO insert the new ActivitySummary in startdatetime enddatetime range
    IO_Data.DomeInsertActivitySummaryData(WellInfoDict, ActivitySummary_DF )

def Override(RTSensor_df, Override_df, UserDateRange="All"):
    if Override_df.empty:
        return RTSensor_df
    ii = 0
    if UserDateRange != "All":
        StartDateTime =  datetime.combine(UserDateRange['StartDate'], UserDateRange['StartTime'])
        EndDateTime =  datetime.combine(UserDateRange['EndDate'], UserDateRange['EndTime'])
        RTSensor_df = RTSensor_df[(RTSensor_df['dt'] >= StartDateTime) & (RTSensor_df['dt'] < EndDateTime)]

    Override_df = Override_df.reset_index()


    for i,row in Override_df.iterrows():


        start_time_temp = row[ii, 'StartDateTime']
        end_time_temp = row[ii+1, 'EndDateTime']

        idx_logic = (RTSensor_df['dt'] >= start_time_temp) & (RTSensor_df['dt'] < end_time_temp)

        activity_label_temp = Override_df.loc[ii, 'LABEL_ACTIVITY']
        subactivity_label_temp = Override_df.loc[ii, 'LABEL_SUBACTIVITY']
        pic_label_temp = Override_df.loc[ii, 'PIC']
        # section_label_temp = Override_df.loc[ii, 'Section Size']
        # remarks_label_temp = InputActivity_DB.loc[ii, 'Remarks']
        # activity_label_temp = Override_df.loc[ii, 'In-Slip Threshold']

        RTSensor_df.loc[idx_logic, ("Activity")] = activity_label_temp
        RTSensor_df.loc[idx_logic, ("SubActivity")] = subactivity_label_temp
        RTSensor_df.loc[idx_logic, ("PIC")] = pic_label_temp
        # RTSensor_df.loc[idx_logic, ("Section Size")] = section_label_temp
        # RTSensor_df.loc[idx_logic, ("remarks")] = remarks_label_temp
        # RTSensor_df.loc[idx_logic, ("In-Slip Threshold")] = activity_label_temp
        ii = ii+1
    return RTSensor_df











# =================================================================================================
def RedefinedUserDateRange(WellInfoDict, UserDateRange):
    print(UserDateRange)
    defined_startdate = UserDateRange['StartDate']
    defined_starttime = UserDateRange['StartTime']
    defined_enddate = UserDateRange['EndDate']
    defined_endtime = UserDateRange['EndTime']
    # date_temp = datetime_module.date(2023, 1, 1)  # Example date
    # time_temp = datetime.time(12, 0)      # Example time

    UserDateRange = {
      "StartDate":  datetime_module.date(2003, 4, 10),
      "StartTime":  datetime_module.time(10, 51),
      "EndDate": defined_startdate,
      "EndTime": defined_starttime
    }
    LastActSum = (getBeforeActSum(WellInfoDict, UserDateRange, DrillActivityList='default'))
    UserDateRange = {
      "StartDate": defined_enddate,
      "StartTime": defined_endtime,
      "EndDate":  datetime_module.date(2300, 4, 10),
      "EndTime":  datetime_module.time(11, 9)
    }
    NextActSum = (getNextActSum(WellInfoDict, UserDateRange, DrillActivityList='default'))
    StartDateTime_obj =  datetime.strptime(LastActSum['StartDateTime'].values[0], '%Y-%m-%d %H:%M:%S')

    EndDateTime_obj =  datetime.strptime(NextActSum['EndDateTime'].values[0], '%Y-%m-%d %H:%M:%S')
    NewUserDateRange = {
        "StartDate": StartDateTime_obj.date(),
        "StartTime": StartDateTime_obj.time(),
        "EndDate": EndDateTime_obj.date(),
        "EndTime": EndDateTime_obj.time(),
        }
    return NewUserDateRange   
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
        ActSum_df = IO_Data.DomeGetActivitySummaryData(WellInfoDict, UserDateRange)

        # If ActSum_df is not empty, break the loop
        if not ActSum_df.empty:
            break
        
        # Calculate the new StartDate and StartTime by subtracting 3 hours
        start_datetime =  datetime.combine(UserDateRange["StartDate"], UserDateRange["StartTime"])
        new_start_datetime = start_datetime - timedelta(hours=total_hours_adjusted)
        
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
        ActSum_df = IO_Data.DomeGetActivitySummaryData(WellInfoDict, UserDateRange)

        # If ActSum_df is not empty, break the loop
        if not ActSum_df.empty:
            break
        
        # Calculate the new StartDate and StartTime by subtracting 3 hours
        end_datetime =  datetime.combine(UserDateRange["EndDate"], UserDateRange["EndTime"])
        new_end_datetime = end_datetime + timedelta(hours=total_hours_adjusted)
        
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
def getBeforeConnectionDateTime(WellInfoDict, UserDateRange):
    # Initialize variables
    ActSum_df = None
    total_hours_adjusted = 1
    max_hours_to_adjust = 24
    isRun = True

    while isRun:
        # print(UserDateRange)
        # Get Activity Summary Data
        ActSum_df = IO_Data.DomeGetActivitySummaryData(WellInfoDict, UserDateRange)
        
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
        start_datetime =  datetime.combine(UserDateRange["StartDate"], UserDateRange["StartTime"])
        new_start_datetime = start_datetime - timedelta(hours=total_hours_adjusted)
        
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
def getNextConnectionDateTime(WellInfoDict, UserDateRange):
    # Initialize variables
    ActSum_df = None
    total_hours_adjusted = 1
    max_hours_to_adjust = 24
    isRun = True

    while isRun:
        # print(UserDateRange)
        # Get Activity Summary Data
        ActSum_df = IO_Data.DomeGetActivitySummaryData(WellInfoDict, UserDateRange)
        
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
        end_datetime =  datetime.combine(UserDateRange["EndDate"], UserDateRange["EndTime"])
        new_end_datetime = end_datetime + timedelta(hours=3)
        
        # Update the UserDateRange
        UserDateRange["EndDate"] = new_end_datetime.date()
        UserDateRange["EndTime"] = new_end_datetime.time()
        
        # # If we've adjusted more than 24 hours, stop adjusting
        if total_hours_adjusted >= max_hours_to_adjust:
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
def App():
    st.markdown("## Input Parameter")
    UserAuthDict = st.session_state['UserAuthDict']
    SelectComp = st.session_state['SelComp']
    SelectWell = st.session_state['SelWell']
    WellInfoDict = IO_Data.getWellInfoDict(UserAuthDict, SelectComp, SelectWell)
    st.markdown("## Override Activity Table")
    # st.write(WellInfoDict)
    OverrideActivityTableWidget(WellInfoDict, st.container(), 
                          PrefixKey = 'OverrideActivityTable' , 
                          TripActivityList='default', DrillActivityList='default', OverrideActivityList='default')
    st.markdown("## Section Parameter Table")
    SectionParamsTableWidget(WellInfoDict, st.container(), 
                          PrefixKey = 'SectionParamsTable' , 
                          SectionSizeList='default',)

























