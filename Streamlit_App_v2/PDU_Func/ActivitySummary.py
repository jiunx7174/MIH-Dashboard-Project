import pandas as pd
import numpy as np
from datetime import datetime,timedelta
import requests
import json
from PDU_Func import IO_Data
import matplotlib.pyplot as plt
import streamlit as st
def test():
    print("Wakwaw")

def _plotFalseSensor(df):
    # assume df is your dataframe with columns LabelSubActivity and Duration

    # group by LabelSubActivity and calculate count, sum, and mean of Duration
    grouped = df.groupby('LABEL_SubActivity')['Duration'].agg(['count', 'sum', 'mean'])

    # create a bar chart of the count of each LabelSubActivity
    grouped['count'].plot(kind='bar', title='Count of LabelSubActivity')
    plt.show()

    # create a bar chart of the total duration of each LabelSubActivity
    grouped['sum'].plot(kind='bar', title='Total Duration by LabelSubActivity')
    plt.show()

    # create a bar chart of the average duration of each LabelSubActivity
    grouped['mean'].plot(kind='bar', title='Average Duration by LabelSubActivity')

    # show the plots
    plt.show()

def _DataType():
    data_type = {
        "wid": int,
        "date": 'datetime64',
        "time_start": 'datetime64',
        "time_end": 'datetime64',
        "duration_minutes": float,
        "hole_depth": float,
        "bit_depth": float,
        "meterage_drilling": float,
        "rotate_drilling_time": float,
        "slide_drilling_time": float,
        "reaming_time": float,
        "connection_time": float,
        "on_bottom_hours": float,
        "stand_duration": float,
        "label_subactivity": 'string',
        "label_activity": 'string',
        "stand_meterage_drilling": float,
        "stand_durationx": float,
        "stand_on_bottom": float,
        "pic": 'string',
        "section": 'string',
        "remark": 'string',
        "stand_group": 'string',
        'status': 'string',
        }
    # print(type(data))
    return data_type
def _ActivitySummaryColumnRenameDict():
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
                            # "stand_on_bottom":"OnBottomDurationPerStand",
                            "pic":"PIC",
                            "section":"Section",
                            "remark":"Remarks",
                            "stand_group":"Stand Group_Pred",
                            }
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
                            "stand_on_bottom":"LABEL_ConnectionActivity",
                            "pic":"PIC",
                            "section":"Section",
                            "remark":"Remarks",
                            "stand_group":"Stand Group_Pred",
                            }.values(),
        "DataTypeDict":{
                    "wid": 'int',
                    "Date": "datetime64",
                    "StartDateTime": "datetime64",
                    "EndDateTime": "datetime64",
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

class ActivitySummaryTable:
    def __init__(self, WellInfoDict:dict, UserDateRange:dict):
        ColumProperty = _ActivitySummaryColumnRenameDict()
        self.Data = pd.DataFrame(
                    columns = ColumProperty['ColumnName'],
                    # dtype=ColDataType,
                    )
        self.Data = self.Data.astype(ColumProperty['DataTypeDict'])
        self.WellInfoDict = WellInfoDict
        self.UserDateRange = UserDateRange
        
    
    def getActivitySummary(self,ActivityLog_DF, RTSensor_df, MinuteTolerances=1, CleaningIteration=1):
        """
        download the activity summary table from existing server
        there's 3 major funciton in general
        # getGroupDuration
        ## Aggregate lv.1, keep it as it is
        -datetime start 
        -datetime end 
        -date 
        -well name
        -activity
        -sub-activity
        -section size
        -PIC
        -in-slip threshold
        -remarks

        ## Aggregate lv.1, calculate duration
        -Duration 
        -Hole Depth 
        -Bit Depth 
        -Drilling Meterage
        -Rotate Drilling Duration
        -Slide Drilling Duration
        -Reaming Duration
        -Connection Duration

        # LabelStand
        ## Aggregate lv.2
        # Connection Activity
        # On Bottom Duration 
        # Stand Duration 
        """
        UserDateRange = self.UserDateRange
        WellInfoDict = self.WellInfoDict

        # StartDateTime = datetime.strptime(UserDateRange['StartDate'] + " " + UserDateRange['StartTime'], '%Y-%m-%d %H:%M:%S')
        # EndDateTime = datetime.strptime(UserDateRange['EndDate'] + " " + UserDateRange['EndTime'], '%Y-%m-%d %H:%M:%S')
        # StartDateTime = datetime.strptime(UserDateRange['StartDate'] + " " + UserDateRange['StartTime'], '%Y-%m-%d %H:%M:%S')
        # EndDateTime = datetime.strptime(UserDateRange['EndDate'] + " " + UserDateRange['EndTime'], '%Y-%m-%d %H:%M:%S')
        StartDateTime = datetime.combine(UserDateRange['StartDate'], UserDateRange['StartTime'])
        EndDateTime = datetime.combine(UserDateRange['EndDate'], UserDateRange['EndTime'])
        
        # get the ActivitySummaryTable data between the UserDateRange
        temp_ActSum_df = IO_Data.DomeGetData(WellInfoDict, UserDateRange, table_type="Activity Summary")
        
        # If the ActivitySummaryTable between the UserDateRange is exist or partially exist
        # TODO, if we want to fill out a "Gap" ActSumTable case

        if list(temp_ActSum_df.columns) != []:
            self.Data[list(temp_ActSum_df.columns)] = temp_ActSum_df[list(temp_ActSum_df.columns)]
            self.Data['wid'] =  int(WellInfoDict['wid'])
            self.Data['status'] =  "FIRM"
            self.Data['LABEL_All'] = self.Data['LABEL_Activity'] + "--" + self.Data['LABEL_SubActivity']
            # StartDateTime = self.Data['time_end'].max()
            # st.write(self.Data)
            # st.write(self.Data.dtypes)

            StartDateTime = datetime.strptime(self.Data['EndDateTime'].max(), '%Y-%m-%d %H:%M:%S')
            UserDateRange['StartDate'] = StartDateTime.date()
            UserDateRange['StartTime'] = StartDateTime.time()
            # st.text(StartDateTime)

        # if the ActSumTable max end time is outside the UserDateRange, 
        # then ActivityMapping is no longer needed
        if  StartDateTime >= EndDateTime:
            pass

        # get the realtime data
        # RTSensor_df = IO_Data.DomeGetRealtimeSensorData(WellInfoDict, UserDateRange)
        
        #_________________________________________________
        #% labelling the activity data with the ActLogData
        # TODO if the ActivityLog_DF is outside the UserDateRange
        RTSensor_df = getActivityLabel(RTSensor_df, ActivityLog_DF, UserDateRange=UserDateRange)


        #_________________________________________________
        #% apply the PDU mapping logic function
        RTSensor_df = getSubActivityLabel(RTSensor_df)

        
        #_________________________________________________
        #% group and aggregate the Realtime data into ActitivtySummaryTable, this function is categorized as lv.1 aggregate
        ActSum_df = getGroupDuration(RTSensor_df, DrillActivityList='default')


        #_________________________________________________
        #% clean the False/Check and Look and define under the constraint
        ActSum_df = cleanFalseSensor(ActSum_df, MinuteTolerances=MinuteTolerances, CleaningIteration=CleaningIteration)

        #_________________________________________________
        # label the group stand, this function are useful to determine the lv.2 aggregate
        ActSum_df = getStandLabel(ActSum_df)
        ActSum_df['StartDateTime'] = ActSum_df['StartDateTime'].dt.strftime('%Y-%m-%d %H:%M:%S')
        ActSum_df['EndDateTime'] = ActSum_df['EndDateTime'].dt.strftime('%Y-%m-%d %H:%M:%S')


        ActSum_df['wid'] =  int(WellInfoDict['wid'])
        ActSum_df['status'] =  "REVIEW"


        self.Data= pd.concat([self.Data, ActSum_df])

    ## Fill Gap function
    def getActivitySummary_v2(self,ActivityLog_DF, RTSensor_df, MinuteTolerances=1, CleaningIteration=1):
        """
        download the activity summary table from existing server
        there's 3 major funciton in general
        # getGroupDuration
        ## Aggregate lv.1, keep it as it is
        -datetime start 
        -datetime end 
        -date 
        -well name
        -activity
        -sub-activity
        -section size
        -PIC
        -in-slip threshold
        -remarks

        ## Aggregate lv.1, calculate duration
        -Duration 
        -Hole Depth 
        -Bit Depth 
        -Drilling Meterage
        -Rotate Drilling Duration
        -Slide Drilling Duration
        -Reaming Duration
        -Connection Duration

        # LabelStand
        ## Aggregate lv.2
        # Connection Activity
        # On Bottom Duration 
        # Stand Duration 
        """
        UserDateRange = self.UserDateRange
        WellInfoDict = self.WellInfoDict

        # StartDateTime = datetime.strptime(UserDateRange['StartDate'] + " " + UserDateRange['StartTime'], '%Y-%m-%d %H:%M:%S')
        # EndDateTime = datetime.strptime(UserDateRange['EndDate'] + " " + UserDateRange['EndTime'], '%Y-%m-%d %H:%M:%S')
        # StartDateTime = datetime.strptime(UserDateRange['StartDate'] + " " + UserDateRange['StartTime'], '%Y-%m-%d %H:%M:%S')
        # EndDateTime = datetime.strptime(UserDateRange['EndDate'] + " " + UserDateRange['EndTime'], '%Y-%m-%d %H:%M:%S')
        StartDateTime = datetime.combine(UserDateRange['StartDate'], UserDateRange['StartTime'])
        EndDateTime = datetime.combine(UserDateRange['EndDate'], UserDateRange['EndTime'])
        
        # get the ActivitySummaryTable data between the UserDateRange
        temp_ActSum_df = IO_Data.DomeGetData(WellInfoDict, UserDateRange, table_type="Activity Summary")
        
        # If the ActivitySummaryTable between the UserDateRange is exist or partially exist
        # TODO, if we want to fill out a "Gap" ActSumTable case

        if list(temp_ActSum_df.columns) != []:
            self.Data[list(temp_ActSum_df.columns)] = temp_ActSum_df[list(temp_ActSum_df.columns)]
            self.Data['wid'] =  int(WellInfoDict['wid'])
            self.Data['status'] =  "FIRM"
            self.Data['LABEL_All'] = self.Data['LABEL_Activity'] + "--" + self.Data['LABEL_SubActivity']
            # StartDateTime = self.Data['time_end'].max()
            # st.write(self.Data)
            # st.write(self.Data.dtypes)

            StartDateTime = datetime.strptime(self.Data['EndDateTime'].max(), '%Y-%m-%d %H:%M:%S')
            UserDateRange['StartDate'] = StartDateTime.date()
            UserDateRange['StartTime'] = StartDateTime.time()
            # st.text(StartDateTime)

        # if the ActSumTable max end time is outside the UserDateRange, 
        # then ActivityMapping is no longer needed
        if  StartDateTime >= EndDateTime:
            pass

        # get the realtime data
        # RTSensor_df = IO_Data.DomeGetRealtimeSensorData(WellInfoDict, UserDateRange)
        
        #_________________________________________________
        #% labelling the activity data with the ActLogData
        # TODO if the ActivityLog_DF is outside the UserDateRange
        RTSensor_df = getActivityLabel(RTSensor_df, ActivityLog_DF, UserDateRange=UserDateRange)


        #_________________________________________________
        #% apply the PDU mapping logic function
        RTSensor_df = getSubActivityLabel(RTSensor_df)

        
        #_________________________________________________
        #% group and aggregate the Realtime data into ActitivtySummaryTable, this function is categorized as lv.1 aggregate
        ActSum_df = getGroupDuration(RTSensor_df, DrillActivityList='default')


        #_________________________________________________
        #% clean the False/Check and Look and define under the constraint
        ActSum_df = cleanFalseSensor(ActSum_df, MinuteTolerances=MinuteTolerances, CleaningIteration=CleaningIteration)

        #_________________________________________________
        # label the group stand, this function are useful to determine the lv.2 aggregate
        ActSum_df = getStandLabel(ActSum_df)
        ActSum_df['StartDateTime'] = ActSum_df['StartDateTime'].dt.strftime('%Y-%m-%d %H:%M:%S')
        ActSum_df['EndDateTime'] = ActSum_df['EndDateTime'].dt.strftime('%Y-%m-%d %H:%M:%S')


        ActSum_df['wid'] =  int(WellInfoDict['wid'])
        ActSum_df['status'] =  "REVIEW"


        self.Data= pd.concat([self.Data, ActSum_df])


        

    def LabelStand():
        pass

    def Update():
        pass
    def Insert():
        pass
    def Delete():
        pass
                    # if RadioButton=='No/RAW':
                    #     SummaryActivity_DF = Activity.labelStand_v2(Activity.GenerateDuration_DF_v4(Activity_DF))
                    # else:
                    #     SummaryActivity_DF = Activity.labelStand_v2(Activity.cleanFalseSensor((Activity.GenerateDuration_DF_v4(Activity_DF))))

# def getGroupDuration
# def getSubActivityLabel
# def getActivityLabel
def getStandLabel(ActSum_df):

    ActSum_df['DrillingMeteragePerStand'] = np.NaN
    ActSum_df['StandDuration'] = np.NaN
    ActSum_df['OnBottomDurationPerStand'] = np.NaN
    ActSum_df['Stand Group_Pred'] = ""
    # ActSum_df['ConnectionDurationPerStand'] = np.NaN

    ActSum_df = ActSum_df.reset_index(drop=True).fillna(0)

    ii = 0
    for idx,row in ActSum_df[(ActSum_df['LABEL_SubActivity']=='Connection')].iterrows():
        # print(idx)
        if ii==0:

            idx_start = idx + 1

        else:
            idx_end = idx - 1
        
            ActSum_df.loc[idx_start:idx_end, 'Stand Group_Pred'] = 'Stand Group - ' + str(ii)


            OnBottomDurationPerStand =  ActSum_df.loc[idx_start:idx_end, 'RotateDrillingDuration'].sum() + ActSum_df.loc[idx_start:idx_end, 'SlideDrillingDuration'].sum()
            StandDuration =  ActSum_df.loc[idx_start:idx_end+1, 'Duration'].sum()
            DrillingMeteragePerStand = ActSum_df.loc[idx_start:idx_end, 'DrillingMeterage'].sum()


            ActSum_df.loc[idx, 'OnBottomDurationPerStand'] = OnBottomDurationPerStand
            ActSum_df.loc[idx, 'StandDuration'] = StandDuration
            ActSum_df.loc[idx, "DrillingMeteragePerStand"] = DrillingMeteragePerStand

            # print(str(idx_start) + " - " + str(idx_end))
            idx_start = idx + 1

        ii = ii + 1

    
    # ActSum_df['Time_start'] = pd.to_datetime(ActSum_df['date'].dt.strftime('%Y-%m-%d') + " " + ActSum_df['Time_start'], format='%Y-%m-%d %H:%M:%S')
    # ActSum_df['Time_end'] = pd.to_datetime(ActSum_df['date'].dt.strftime('%Y-%m-%d') + " " + ActSum_df['Time_end'])
    return ActSum_df

# TODO, plot the comparison result of cleanFalseSensor Algorithm using _plotFalseSensor()
def cleanFalseSensor(ActSum_df, MinuteTolerances=1, CleaningIteration=1):
    for iter in range(CleaningIteration):
        ActSum_df = ActSum_df.reset_index(drop=True)
        # while ("FALSE/Check" in ActSum_df['LABEL_SubActivity'].values) or ("Look and define" in ActSum_df['LABEL_SubActivity'].values):
        idx_same = ActSum_df.index[
            ((ActSum_df['LABEL_SubActivity']=="Look and define") | (ActSum_df['LABEL_SubActivity']=="FALSE/Check")) & (ActSum_df['Duration'] <= MinuteTolerances)
            ]
        idx_before = idx_same - 1

        idx_same = idx_same[idx_before>=0]
        idx_before = idx_before[idx_before>=0]
        
        ActSum_df.loc[idx_same, 'LABEL_SubActivity'] = ActSum_df.loc[idx_before, 'LABEL_SubActivity'].values
        ActSum_df.loc[idx_same, 'LABEL_All'] = ActSum_df.loc[idx_before, 'LABEL_All'].values

        ActSum_df = ActSum_df.groupby((ActSum_df['LABEL_All'].shift() != ActSum_df['LABEL_All']).cumsum(), as_index=False).agg(
        {'Date': 'max',
        'StartDateTime': 'min',
        'EndDateTime': 'max',
        'Duration': 'sum',
        'Hole_Depth_max': 'max',
        'Bit_Depth_avg': 'mean',
        'DrillingMeterage': 'sum',
        'RotateDrillingDuration': 'sum',
        'SlideDrillingDuration': 'sum',
        'ReamingDuration': 'sum',
        'ConnectionDuration': 'sum',
        'LABEL_SubActivity': 'first',
        'LABEL_Activity': 'first',
        'LABEL_All': 'first',
        'PIC': 'first',
        'InSlip_Treshold': 'first',
        'Remarks': 'first',
        'Section': 'first'}
        )
    return ActSum_df
def getGroupDuration(RTSensor_df , DrillActivityList='default'):
    if DrillActivityList=='default':
        DrillActivityList = ["DRILLING FORMATION", 'CIRCULATE HOLE CLEANING','CONNECTION','DRILL OUT CEMENT',]


    RTSensor_df ['dt'] = pd.to_datetime(RTSensor_df ['dt'])
    RTSensor_df ["LABEL_All"] =RTSensor_df ['SubActivity'].astype(str)+'--'+RTSensor_df ['Activity'].astype(str)
    RTSensor_df ['Activity'] = RTSensor_df ['Activity'].fillna("N/A").astype(str)
    RTSensor_df ['SubActivity'] = RTSensor_df ['SubActivity'].fillna("N/A").astype(str)
    # TODO , a funtion that check the latest hole depth
    Hole_Depth_max = 0
    list_dict_out = []
    for k,DF_Temp in RTSensor_df .groupby((RTSensor_df ['LABEL_All'].shift() != RTSensor_df ['LABEL_All']).cumsum()):

        # if not(("Hole_Depth" in locals()) or ("Hole_Depth" in globals())):
        #     Hole_Depth = 0

        list_temp = []

        # date = DF_Temp.head(1)['date'].values[0]

        # Time_start = pd.to_datetime(date + " " + DF_Temp.head(1)['time'].values[0])
        # Time_end_temp = DF_Temp.tail(1)['time'].values[0]
        # Time_end = pd.to_datetime(DF_Temp.tail(1)['date'].values[0] + " " + str((datetime.strptime(Time_end_temp, "%H:%M:%S") + timedelta(seconds=5)).time()))
        Date = DF_Temp['date'].iloc[0]
        StartDateTime = DF_Temp['dt'].iloc[0]
        EndDateTime = DF_Temp['dt'].iloc[-1]
        # Time_start = DF_Temp.head(1)['time'].values[0]
        # Time_end_temp = DF_Temp.tail(1)['time'].values[0]
        # Time_end = str((datetime.strptime(Time_end_temp, "%H:%M:%S") + timedelta(seconds=5)).time())

        LABEL_Activity = DF_Temp['Activity'].iloc[0]
        LABEL_SubActivity = DF_Temp['SubActivity'].iloc[0]
        section_data = DF_Temp['Section Size'].iloc[0]
        pic_data = DF_Temp['PIC'].iloc[0]
        InSlip_Treshold_data = DF_Temp['In-Slip Threshold'].iloc[0]
        remarks_data = DF_Temp['remarks'].iloc[0]

        # Duration(minutes)
        Duration = (EndDateTime-StartDateTime).total_seconds() / 60.0 


        Hole_Depth_Temp = DF_Temp['md'].max()
        if float(Hole_Depth_Temp)>= float(Hole_Depth_max):
            Hole_Depth_max = Hole_Depth_Temp
        
        Bit_Depth_avg = DF_Temp['bitdepth'].mean()

        DrillingMeterage = np.nan

        RotateDrillingDuration = np.nan
        SlideDrillingDuration = np.nan
        ReamingDuration = np.nan
        ConnectionDuration = np.nan

        # OnBottomHours = np.nan
        # StandDuration = np.nan

        if LABEL_Activity in DrillActivityList:
            DrillingMeterage = round((DF_Temp['md'].max()-DF_Temp['md'].min()),2)

        if LABEL_SubActivity == "Rotary Drilling":
            RotateDrillingDuration = Duration

        if LABEL_SubActivity == "Slide Drilling":
            SlideDrillingDuration = Duration

        if LABEL_SubActivity == "Reaming":
            ReamingDuration = Duration
        if LABEL_SubActivity == "Connection":
            ConnectionDuration = Duration


        list_dict_out.append(
            {
            'Date':Date,
            'StartDateTime':StartDateTime,
            'EndDateTime':EndDateTime,
            'Duration':Duration,
            'Hole_Depth_max':Hole_Depth_max,
            'Bit_Depth_avg':Bit_Depth_avg,
            "DrillingMeterage": DrillingMeterage,
            'RotateDrillingDuration':RotateDrillingDuration,
            'SlideDrillingDuration':SlideDrillingDuration,
            'ReamingDuration':ReamingDuration,
            'ConnectionDuration':ConnectionDuration,
            # 'On Bottom Hours':OnBottomHours,
            # 'Stand Duration': StandDuration,
            'LABEL_SubActivity': LABEL_SubActivity,
            "LABEL_Activity": LABEL_Activity,
            "LABEL_All": LABEL_SubActivity+'--'+LABEL_Activity,
            "PIC":pic_data,
            "InSlip_Treshold":InSlip_Treshold_data,
            "Remarks":remarks_data,
            "Section":section_data,

            }
        )
    ActSum_df = pd.DataFrame.from_dict(list_dict_out,orient='columns')
    listSetDecimals = ['Duration','Hole_Depth_max','Bit_Depth_avg','DrillingMeterage',
                       'RotateDrillingDuration','SlideDrillingDuration','ReamingDuration',
                       'ConnectionDuration','InSlip_Treshold',]
    for ColumnName in listSetDecimals:
        ActSum_df[ColumnName] = np.round(ActSum_df[ColumnName],2)
    # TODO a function that validate the data type output
        # ActSum_df = ActSum_df.astype({'date': np.dtype('<M8[ns]'),
        # 'StartDateTime': np.dtype('<M8[ns]'),
        # 'EndDateTime': np.dtype('<M8[ns]'),
        # 'Duration': np.dtype('float64'),
        # 'Hole_Depth_max': np.dtype('float64'),
        # 'Bit_Depth_avg': np.dtype('float64'),
        # 'DrillingMeterage': np.dtype('float64'),
        # 'RotateDrillingDuration': dtype('float64'),
        # 'SlideDrillingDuration': np.dtype('float64'),
        # 'ReamingDuration': np.dtype('float64'),
        # 'ConnectionDuration': np.dtype('float64'),
        # 'LABEL_SubActivity': 'str',
        # 'LABEL_Activity': 'str',
        # 'PIC': 'str',
        # 'InSlip_Treshold': np.dtype('float64'),
        # 'Remarks': 'str',
        # 'Section': 'str'})
        #     # )
    return ActSum_df
    # RTSensor_df = Activity.GetActivity_DF(Activity_DF, Input_Temp)

    # Activity_DF = Activity.GetSubActivity_DF_v3(Activity_DF)
    
    # if RadioButton=='No/RAW':
    #     SummaryActivity_DF = Activity.labelStand_v2(Activity.GenerateDuration_DF_v4(Activity_DF))
    # else:
    #     SummaryActivity_DF = Activity.labelStand_v2(Activity.cleanFalseSensor((Activity.GenerateDuration_DF_v4(Activity_DF))))

def getSubActivityLabel(RTSensor_df, TripActivityList='default', DrillActivityList='default', OverrideActivityList='default'):
    #TODO makesure the column name and data type is match
    RTSensor_df = RTSensor_df.astype(
        {
            "dt":"datetime64[ns]",
            # "date":"object",
            # "time":"object",
            "bitdepth":"float64",
            "md":"float64",
            "blockpos":"float64",
            "rop":"float64",
            "hklda":"float64", 
            "woba":"float64",
            "torqa":"float64",
            "rpm":"float64",
            "stppress":"float64",
            "mudflowin":"float64",
            # "Activity":"object",
            "In-Slip Threshold":"float64",
            "PIC":'str',
            "remarks":'str',
            "Section Size":'str',
            # "SubActivity":"object",
            # "logic_status":"int64",
            # "isBitDepthMoving":"bool",
            # "LABEL_All":"object",
        }
    )
    if TripActivityList=='default':
        TripActivityList = ['NPT', 'N/D BOP', 'N/U BOP', 'OTHER', 'RUNNING CASING IN', 'STATIONARY', 'STUCK PIPE', 
                            'TRIP IN', 'TRIP OUT', 'WAIT ON CEMENT', 'LAY DOWN BHA', 'MAKE UP BHA', 'WIPER TRIP']
        
    if DrillActivityList=='default':
        DrillActivityList = ["DRILLING FORMATION", 'CIRCULATE HOLE CLEANING','CONNECTION','DRILL OUT CEMENT',]

    if OverrideActivityList=='default':
        OverrideActivityList = ['CEMENTING JOB', 'CONNECTION', 'LAY DOWN BHA', 'MAKE UP BHA', 'NPT', 'N/D BOP', 
                                'N/U BOP', 'RUNNING CASING IN', 'STATIONARY', 'STUCK PIPE', 'WAIT ON CEMENT', 'RIG REPAIR',]

    logic_status = 0
    RTSensor_df["SubActivity"] = "FALSE/Check"
    RTSensor_df["logic_status"] = logic_status

    idx_logic_activity = RTSensor_df["Activity"].isin(
                                                    DrillActivityList
                                                    )
    # print((RTSensor_df.dtypes))

    idx_logic = idx_logic_activity & ((RTSensor_df['woba']>0) & (RTSensor_df['rpm']>10) & (RTSensor_df['stppress']>100) & (RTSensor_df['hklda']>RTSensor_df['In-Slip Threshold']))
    SubActivity_Label = "Rotary Drilling"
    RTSensor_df.loc[idx_logic, "SubActivity"] = SubActivity_Label
    #

    logic_status = logic_status + 1
    RTSensor_df.loc[idx_logic, "logic_status"] = logic_status
    # 1

    logic_status = logic_status + 1
    RTSensor_df.loc[idx_logic, "logic_status"] = logic_status

    idx_logic = idx_logic_activity &(RTSensor_df["SubActivity"] == "FALSE/Check") & ((RTSensor_df['woba']>0) & (RTSensor_df['rpm']<10) & (RTSensor_df['stppress']>100) & (RTSensor_df['hklda']>RTSensor_df['In-Slip Threshold']))
    SubActivity_Label = "Slide Drilling"
    RTSensor_df.loc[idx_logic, "SubActivity"] = SubActivity_Label
    # 2

    logic_status = logic_status + 1
    RTSensor_df.loc[idx_logic, "logic_status"] = logic_status
    
    idx_logic = idx_logic_activity &(RTSensor_df["SubActivity"] == "FALSE/Check") & ((RTSensor_df['woba']==0) & (RTSensor_df['rpm']>10) & (RTSensor_df['stppress']>100) & (RTSensor_df['hklda']>RTSensor_df['In-Slip Threshold']))
    SubActivity_Label = "Reaming"
    RTSensor_df.loc[idx_logic, "SubActivity"] = SubActivity_Label
    #3

    logic_status = logic_status + 1
    RTSensor_df.loc[idx_logic, "logic_status"] = logic_status

    idx_logic = idx_logic_activity &(RTSensor_df["SubActivity"] == "FALSE/Check") & ((RTSensor_df['woba']==0) & (RTSensor_df['rpm']==0) & (RTSensor_df['stppress']>100) & (RTSensor_df['hklda']>RTSensor_df['In-Slip Threshold']))
    SubActivity_Label = "Wash Up/Down"
    RTSensor_df.loc[idx_logic, "SubActivity"] = SubActivity_Label
    #4

    logic_status = logic_status + 1
    RTSensor_df.loc[idx_logic, "logic_status"] = logic_status


    idx_logic = idx_logic_activity &(RTSensor_df["SubActivity"] == "FALSE/Check") & ((RTSensor_df['woba']==0) & (RTSensor_df['rpm']==0) & (RTSensor_df['stppress']<50))
    SubActivity_Label = "Connection"
    RTSensor_df.loc[idx_logic, "SubActivity"] = SubActivity_Label
    #5

    logic_status = logic_status + 1
    RTSensor_df.loc[idx_logic, "logic_status"] = logic_status

    # idx_logic = idx_logic_activity & ((RTSensor_df["SubActivity"] == "FALSE/Check") & (RTSensor_df['hklda']>RTSensor_df['In-Slip Threshold']))
    idx_logic = idx_logic & (RTSensor_df['hklda']>RTSensor_df['In-Slip Threshold'])
    SubActivity_Label="Look and define"
    RTSensor_df.loc[idx_logic, "SubActivity"] = SubActivity_Label
    #6

    logic_status = logic_status + 1
    RTSensor_df.loc[idx_logic, "logic_status"] = logic_status
    #7


    # ############################
    idx_logic_activity_2 = RTSensor_df["Activity"].isin(
        TripActivityList
        )
    RTSensor_df['isBitDepthMoving'] = RTSensor_df['bitdepth'].shift(periods=-1) != RTSensor_df['bitdepth']

    # RTSensor_df["LABEL_SubActivity"] = "Check"
    idx_logic_2 = idx_logic_activity_2 & ((RTSensor_df['isBitDepthMoving']) & (RTSensor_df['hklda']>RTSensor_df['In-Slip Threshold']) & (RTSensor_df['rpm']==0) & (RTSensor_df['mudflowin']>10))
    SubActivity_Label = "Wash Up/Down"
    RTSensor_df.loc[idx_logic_2, "SubActivity"] = SubActivity_Label
    # DisplayDF(RTSensor_df.loc[idx_logic_2, :])
    #

    logic_status = logic_status + 1
    RTSensor_df.loc[idx_logic_2, "logic_status"] = logic_status
    #8
    
    idx_logic_2 = idx_logic_activity_2 &(RTSensor_df["SubActivity"] == "FALSE/Check") & ((RTSensor_df['isBitDepthMoving']) & (RTSensor_df['hklda']>RTSensor_df['In-Slip Threshold']) & (RTSensor_df['rpm']>10) & (RTSensor_df['stppress']>100) & (RTSensor_df['mudflowin']>10))
    SubActivity_Label = "Reaming"
    RTSensor_df.loc[idx_logic_2, "SubActivity"] = SubActivity_Label
    

    logic_status = logic_status + 1
    RTSensor_df.loc[idx_logic_2, "logic_status"] = logic_status
    #9

    idx_logic_2 = idx_logic_activity_2 &(RTSensor_df["SubActivity"] == "FALSE/Check") & ((RTSensor_df['isBitDepthMoving']) & (RTSensor_df['hklda']>RTSensor_df['In-Slip Threshold']) & (RTSensor_df['rpm']<10) & (RTSensor_df['stppress']<100) & (RTSensor_df['mudflowin']<50))
    SubActivity_Label = "Moving"
    RTSensor_df.loc[idx_logic_2, "SubActivity"] = SubActivity_Label

    logic_status = logic_status + 1
    RTSensor_df.loc[idx_logic_2, "logic_status"] = logic_status
    #10

    idx_logic_2 = idx_logic_activity_2 &(RTSensor_df["SubActivity"] == "FALSE/Check") & (~(RTSensor_df['isBitDepthMoving']) & (RTSensor_df['hklda']>RTSensor_df['In-Slip Threshold']) & (RTSensor_df['mudflowin']>10))
    SubActivity_Label = "Circulation"
    RTSensor_df.loc[idx_logic_2, "SubActivity"] = SubActivity_Label
    #

    logic_status = logic_status + 1
    RTSensor_df.loc[idx_logic_2, "logic_status"] = logic_status
    #11

    idx_logic_2 = idx_logic_activity_2 &(RTSensor_df["SubActivity"] == "FALSE/Check") & ((RTSensor_df['mudflowin']<10) & (RTSensor_df['rpm']<10) & (RTSensor_df['hklda']<RTSensor_df['In-Slip Threshold']))
    SubActivity_Label = "Connection"
    RTSensor_df.loc[idx_logic_2, "SubActivity"] = SubActivity_Label
    #

    logic_status = logic_status + 1
    RTSensor_df.loc[idx_logic_2, "logic_status"] = logic_status
    #12

    idx_logic_2 = idx_logic_activity_2 &(RTSensor_df["SubActivity"] == "FALSE/Check") & ((~RTSensor_df['isBitDepthMoving']) & (RTSensor_df['mudflowin']<10) & (RTSensor_df['rpm']<10) & (RTSensor_df['hklda']>RTSensor_df['In-Slip Threshold']))
    SubActivity_Label = "Stationary"
    RTSensor_df.loc[idx_logic_2, "SubActivity"] = SubActivity_Label
    #

    logic_status = logic_status + 1
    RTSensor_df.loc[idx_logic_2, "logic_status"] = logic_status
    #13
    ## force to be same as activity

    idx_logic_3 = RTSensor_df["Activity"].isin(
                                                OverrideActivityList
                                                )
    RTSensor_df.loc[idx_logic_3, "SubActivity"] = RTSensor_df.loc[idx_logic_3, "Activity"]
    #

    logic_status = logic_status + 1
    RTSensor_df.loc[idx_logic_3, "logic_status"] = logic_status
    #14

    # print(RTSensor_df.columns)

    return RTSensor_df

def getActivityLabel (RTSensor_df, InputActivity_DB, UserDateRange="All"):
    ii = 0
    if UserDateRange is not "All":
        StartDateTime = datetime.combine(UserDateRange['StartDate'], UserDateRange['StartTime'])
        EndDateTime = datetime.combine(UserDateRange['EndDate'], UserDateRange['EndTime'])
        RTSensor_df = RTSensor_df[(RTSensor_df['dt'] >= StartDateTime) & (RTSensor_df['dt'] < EndDateTime)]


    print(RTSensor_df['dt'].head(2))
    print(RTSensor_df['dt'].tail(2))
    InputActivity_DB = InputActivity_DB.reset_index()
    # print('test')

    # RTSensor_df['PIC'] = ''
    # RTSensor_df['section'] = ''
    # RTSensor_df['remarks'] = ''
    for i,row in InputActivity_DB.iterrows():
        # if ii<InputActivity_DB.shape[1]:

        try:
            start_time_temp = InputActivity_DB.loc[ii, 'DateTime']
            end_time_temp = InputActivity_DB.loc[ii+1, 'DateTime']
            # print(InputActivity_DB.iloc[ii+1, 0])
            idx_logic = (RTSensor_df['dt'] >= start_time_temp) & (RTSensor_df['dt'] < end_time_temp)
        except:
            start_time_temp = InputActivity_DB.loc[ii, 'DateTime']
            # print(InputActivity_DB.iloc[ii, 0])
            # print('test')
            # end_time_temp = InputActivity_DB.loc[ii+1, 'DateTime']
            # print((RTSensor_df['DateTime'].dtypes))
            # print(type(start_time_temp))
            # print(start_time_temp)
            idx_logic = (RTSensor_df['dt'] >= start_time_temp)
        # print('testttt ardelia')
        # print(InputActivity_DB.columns)
        activity_label_temp = InputActivity_DB.loc[ii, 'Activity']
        pic_label_temp = InputActivity_DB.loc[ii, 'PIC']
        section_label_temp = InputActivity_DB.loc[ii, 'Section Size']
        remarks_label_temp = InputActivity_DB.loc[ii, 'Remarks']

        # print(idx_logic)
        # print('----')
        RTSensor_df.loc[idx_logic, ("Activity")] = activity_label_temp
        RTSensor_df.loc[idx_logic, ("PIC")] = pic_label_temp
        RTSensor_df.loc[idx_logic, ("Section Size")] = section_label_temp
        RTSensor_df.loc[idx_logic, ("remarks")] = remarks_label_temp
        # print(InputActivity_DB)
        activity_label_temp = InputActivity_DB.loc[ii, 'In-Slip Threshold']
        # print(RTSensor_df)
        RTSensor_df.loc[idx_logic, ("In-Slip Threshold")] = activity_label_temp
        ii = ii+1
    
    return RTSensor_df
# %%


def checkActSumDF_old(df):
    df['StartDateTime'] = df['StartDateTime'].astype('datetime64[ns]')
    df['EndDateTime'] = df['EndDateTime'].astype('datetime64[ns]')
    idx_start = 0
    len_date_error = 0
    df = df.reset_index(drop=True)
    for idx,row in df[df['StartDateTime'] > df['EndDateTime']].iterrows():
        df.loc[idx, 'LABEL_SubActivity'] = "Date Error, look and define"
        df.loc[idx, 'LABEL_All'] = df.loc[idx, 'LABEL_SubActivity'] + "--" + df.loc[idx, 'LABEL_Activity']
        len_date_error = len_date_error +1



    df['Diff'] = (df['StartDateTime'].shift(-1) - df['EndDateTime']).dt.total_seconds().astype(float) -5

    len_time_overlap = 0
    for idx,row in df[(df['Diff'] < -5)].iterrows():
        df.loc[idx, 'LABEL_SubActivity'] = "Date Overlap, look and define"
        df.loc[idx+1, 'LABEL_SubActivity'] = "Date Overlap, look and define"
        df.loc[idx, 'LABEL_All'] = df.loc[idx, 'LABEL_SubActivity'] + "--" + df.loc[idx, 'LABEL_Activity']
        len_time_overlap = len_time_overlap+1

    df = df.reset_index(drop=True)
    idx_start = 0
    df_concat_list = []
    len_time_gap = 0
    

        
    for idx,row in df[(df['Diff'] > 0)].iterrows():
        df_concat_list.append(df.loc[idx_start:idx])
        if  df.loc[idx+1, 'LABEL_SubActivity'] not in (["Date Error, look and define","Date Overlap, look and define"]):
            new_row = {
                "wid":row["wid"],
                "Date":row["Date"],
                "LABEL_Activity":row["LABEL_Activity"],
                "StartDateTime":row["EndDateTime"]+ timedelta(seconds=5),
                "EndDateTime":df.loc[idx+1, 'StartDateTime']- timedelta(seconds=5),
                "LABEL_SubActivity":"Time Gap, look and define",
            }
            new_row = pd.DataFrame([new_row])
            new_row['LABEL_All'] = new_row['LABEL_SubActivity'] + "--" + new_row['LABEL_Activity']

            df_concat_list.append(new_row)
            len_time_gap = len_time_gap + 1
        idx_start = idx+1

    df_concat_list.append(df.loc[idx_start:])

        
    dict_out = {
        'len_date_error':len_date_error,
        "len_time_overlap":len_time_overlap,
        "len_time_gap":len_time_gap,
    }
    df_out = pd.concat(df_concat_list, ignore_index=True,axis=0).drop('Duration', axis=1)
    df_out['StartDateTime'] = df_out['StartDateTime'].dt.strftime('%Y-%m-%d %H:%M:%S')
    df_out['EndDateTime'] = df_out['EndDateTime'].dt.strftime('%Y-%m-%d %H:%M:%S')
    return df_out,dict_out
def checkActSumDF(df):
    df['StartDateTime'] = df['StartDateTime'].astype('datetime64[ns]')
    df['EndDateTime'] = df['EndDateTime'].astype('datetime64[ns]')
    # df['ErrorWarning'] = ""
    idx_start = 0
    len_date_error = 0
    df = df.reset_index(drop=True)
    for idx,row in df[df['StartDateTime'] > df['EndDateTime']].iterrows():
        df.loc[idx, 'ErrorWarning'] = "Date Error, look and define"
        len_date_error = len_date_error +1
    df['Diff'] = (df['StartDateTime'].shift(-1) - df['EndDateTime']).dt.total_seconds().astype(float) -5

    len_time_overlap = 0
    for idx,row in df[(df['Diff'] < -5)].iterrows():
        df.loc[idx, 'ErrorWarning'] = "Date Overlap, look and define"
        df.loc[idx+1, 'ErrorWarning'] = "Date Overlap, look and define"
        len_time_overlap = len_time_overlap+1

    df = df.reset_index(drop=True)
    idx_start = 0
    df_concat_list = []
    len_time_gap = 0
    

        
    for idx,row in df[(df['Diff'] > 0)].iterrows():

        df.loc[idx,"ErrorWarning"] = "Time Gap, look and define",
        df.loc[idx+1,"ErrorWarning"] = "Time Gap, look and define",
        len_time_gap = len_time_gap+1
  
    # if (len_date_error ==0) and (len_time_overlap == 0) and (len_time_gap == 0):
    #     print("Drop Error WArning")
        # df = df.drop("ErrorWarning", axis=1)
    df = df.drop("Diff", axis=1)
    df['StartDateTime'] = df['StartDateTime'].dt.strftime('%Y-%m-%d %H:%M:%S')
    df['EndDateTime'] = df['EndDateTime'].dt.strftime('%Y-%m-%d %H:%M:%S')
    return df