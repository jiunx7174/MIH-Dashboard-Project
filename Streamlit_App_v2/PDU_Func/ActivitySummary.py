import pandas as pd
import numpy as np
from datetime import datetime
import requests
import json
from PDU_Func import IO_Data

def test():
    print("Wakwaw")



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


class ActivitySummaryTable:
    def __init__(self, WellInfoDict:dict, UserDateRange:dict):
        ColDataType = _DataType()
        self.Data = pd.DataFrame(
                    columns = ColDataType.keys(),
                    # dtype=ColDataType,
                    )
        self.Data = self.Data.astype(ColDataType)
        self.WellInfoDict = WellInfoDict
        self.UserDateRange = UserDateRange
        
    
    def getActivitySummary(self,ActivityLog_DF, RTSensor_df):
        """
        download the activity summary table from existing server
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
            # StartDateTime = self.Data['time_end'].max()
            StartDateTime = datetime.strptime(self.Data['time_end'].max(), '%Y-%m-%d %H:%M:%S')

        # if the ActSumTable max end time is outside the UserDateRange, 
        # then ActivityMapping is no longer needed
        if  StartDateTime >= EndDateTime:
            return self.Data

        # get the realtime data
        # RTSensor_df = IO_Data.DomeGetRealtimeSensorData(WellInfoDict, UserDateRange)
        
        #%% labelling the activity data with the ActLogData
        # TODO if the ActivityLog_DF is outside the UserDateRange
        RTSensor_df = ActivityLogLabelling (RTSensor_df, ActivityLog_DF)


        #%% apply the PDU mapping logic function
        RTSensor_df = SubActivityMapping(RTSensor_df)


        #%% group and aggregate the Realtime data into ActitivtySummaryTable
        GenerateDuration(RTSensor_df, DrillActivityList='default')

        
        """ 
        TODO 
        create the GroupActivity functioncreate the false sensor cleaning, should be different function(?)
        """
        tail_ActSum_df = GroupSubActivity(RTSensor_df)


        return tail_ActSum_df


        

    def LabelStand():
        pass

    def Update():
        pass
    def Insert():
        pass
    def Delete():
        pass
def GroupSubActivity(RTSensor_df):
    return RTSensor_df

def GenerateDuration(RTSensor_df , DrillActivityList='default'):
    if DrillActivityList=='default':
        DrillActivityList = ["DRILLING FORMATION", 'CIRCULATE HOLE CLEANING','CONNECTION','DRILL OUT CEMENT',]


    RTSensor_df ['dt'] = pd.to_datetime(RTSensor_df ['dt'])
    RTSensor_df ["LABEL_All"] =RTSensor_df ['SubActivity'].astype(str)+'--'+RTSensor_df ['Activity'].astype(str)

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
        Date = DF_Temp['Date'].iloc[0]
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
        Duration = (StartDateTime - EndDateTime).total_seconds() / 60.0 


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
            'date':Date,
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
            "PIC":pic_data,
            "InSlip_Treshold":InSlip_Treshold_data,
            "Remarks":remarks_data,
            "Section":section_data,

            }
        )
    Duration_DB = pd.DataFrame.from_dict(list_dict_out,orient='columns')
    listSetDecimals = ['Duration','Hole_Depth_max','Bit_Depth_avg','DrillingMeterage',
                       'RotateDrillingDuration','SlideDrillingDuration','ReamingDuration',
                       'ConnectionDuration','InSlip_Treshold',]
    for ColumnName in listSetDecimals:
        Duration_DB[ColumnName] = np.round(Duration_DB[ColumnName],2)
    # TODO a function that validate the data type output
        # Duration_DB = Duration_DB.astype({'date': np.dtype('<M8[ns]'),
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
    return Duration_DB
    # RTSensor_df = Activity.GetActivity_DF(Activity_DF, Input_Temp)

    # Activity_DF = Activity.GetSubActivity_DF_v3(Activity_DF)
    
    # if RadioButton=='No/RAW':
    #     SummaryActivity_DF = Activity.labelStand_v2(Activity.GenerateDuration_DF_v4(Activity_DF))
    # else:
    #     SummaryActivity_DF = Activity.labelStand_v2(Activity.cleanFalseSensor((Activity.GenerateDuration_DF_v4(Activity_DF))))

def SubActivityMapping(RTSensor_df, TripActivityList='default', DrillActivityList='default', OverrideActivityList='default'):
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
def ActivityLogLabelling (RTSensor_df, InputActivity_DB):
    ii = 0
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