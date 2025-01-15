import pandas as pd
import numpy as np  
from datetime import datetime,timedelta, timezone
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


def getStandLabel(ActSum_df, DrillActivityList='default',stand_num=None):
    # if ActSum_df[ActSum_df['status']=='REVIEW'].empty:
    #     return ActSum_df
    # else:
    # ActSum_df = ActSum_df[ActSum_df['status']=='REVIEW']

    ActSum_df['DrillingMeteragePerStand'] = np.NaN
    ActSum_df['StandDuration'] = np.NaN
    ActSum_df['OnBottomDurationPerStand'] = np.NaN
    ActSum_df['Stand Group_Pred'] = ""
    ActSum_df['LABEL_ConnectionActivity'] = ""
    ActSum_df['RotateDrillingDuration'] = ActSum_df['RotateDrillingDuration'].astype('float')
    ActSum_df['SlideDrillingDuration']= ActSum_df['SlideDrillingDuration'].astype('float')
    ActSum_df['DrillingMeterage']= ActSum_df['DrillingMeterage'].astype('float')
    ActSum_df['Duration']= ActSum_df['Duration'].astype('float')

    # ActSum_df['ConnectionDurationPerStand'] = np.NaN

    ActSum_df = ActSum_df.reset_index(drop=True).fillna(0)
    if DrillActivityList=='default':
        DrillActivityList = ["DRILLING FORMATION", 'DRILL OUT CEMENT','CONNECTION']


    ActSum_df['LABEL_Activity'] = ActSum_df['LABEL_Activity'].astype(str)
    # ActSum_df['LABEL_Activity'] = ActSum_df['LABEL_Activity'].replace({"CONNECTION":"DRILLING FORMATION"})
    ActSum_df = replace_connection_with_nearest_activity(ActSum_df)
    

    if stand_num is None:
        stand_num = 0
    stand_num = stand_num+1

    # st.write(ActSum_df_Drilling.index[0])
    for k,ActSum_df_Temp in ActSum_df.groupby((ActSum_df['LABEL_Activity'].shift() != ActSum_df ['LABEL_Activity']).cumsum()):
        if ActSum_df_Temp['LABEL_Activity'].tolist()[0] in (DrillActivityList):
            ii = 1
            idx_start = ActSum_df_Temp.index[0]



            len_connection = len(ActSum_df_Temp[(ActSum_df_Temp['LABEL_SubActivity']=='Connection')])
            # First, define the stand first
            for idx,row in ActSum_df_Temp[(ActSum_df_Temp['LABEL_SubActivity']=='Connection')].iterrows():
                idx_end=idx-1
                ActSum_df_Stand = ActSum_df[idx_start:idx_end+1]

                if 'Reaming' in ActSum_df_Stand['LABEL_SubActivity'].tolist():
                    OnBottomDurationPerStand =  ActSum_df.loc[idx_start:idx_end, 'RotateDrillingDuration'].sum() + ActSum_df.loc[idx_start:idx_end, 'SlideDrillingDuration'].sum()
                    StandDuration =  ActSum_df.loc[idx_start:idx_end+1, 'Duration'].sum()
                    DrillingMeteragePerStand = ActSum_df.loc[idx_start:idx_end, 'DrillingMeterage'].sum()
                    stand_num = int(ActSum_df.loc[idx, 'StartDateTime'].replace(tzinfo=timezone.utc).timestamp())

                    ActSum_df.loc[idx, 'OnBottomDurationPerStand'] = OnBottomDurationPerStand
                    ActSum_df.loc[idx, 'StandDuration'] = StandDuration
                    ActSum_df.loc[idx, "DrillingMeteragePerStand"] = DrillingMeteragePerStand
                    ActSum_df.loc[idx_start:idx_end, 'Stand Group_Pred'] = 'Drilling Stand-' + str(stand_num)
                    if ii==1:
                        PreCon_Start_idx = ActSum_df_Stand[ActSum_df_Stand['LABEL_SubActivity']=='Reaming'].index[-1]
                        
                        PreCon_End_idx = (idx-1)
                        ActSum_df.loc[PreCon_Start_idx:PreCon_End_idx,'LABEL_ConnectionActivity'] = 'Pre Connection-'+str(stand_num)
                        ActSum_df.loc[idx,'LABEL_ConnectionActivity'] = 'Connection-'+str(stand_num)
                        # stand_num = stand_num-1
                        ii = ii +1
                        # st.write(PreCon_Start_idx)
                        before_stand_num = stand_num
                    else:
                        
                        # try:
                        PostCon_Start_idx = idx_start
                        PostCon_End_idx = ActSum_df_Stand[ActSum_df_Stand['LABEL_SubActivity']=='Reaming'].index[0]
                        ActSum_df.loc[PostCon_Start_idx:PostCon_End_idx,'LABEL_ConnectionActivity'] = 'Post Connection-'+str(before_stand_num)
                        # print(PostCon_Start_idx)
                        # print('PostCon')
                        # print(PostCon_End_idx)
                        # if ii < len_connection:
                        ActSum_df.loc[idx,'LABEL_ConnectionActivity'] = 'Connection-'+str(stand_num)
                        before_stand_num = stand_num
                        PreCon_Start_idx = ActSum_df_Stand[ActSum_df_Stand['LABEL_SubActivity']=='Reaming'].index[-1]
                        PreCon_End_idx = (idx-1)
                        ActSum_df.loc[PreCon_Start_idx:PreCon_End_idx,'LABEL_ConnectionActivity'] = 'Pre Connection-'+str(stand_num)
                        # st.write(f"PreConIdx {PreCon_Start_idx} - {PreCon_End_idx}")

                        # except:
                        #     pass
                        ii = ii+1
                    # st.write()
                    stand_num = stand_num+1
                
                idx_start = idx+1
            
            #################################################################################
            ###### uncomment this code if you want to remove the latest post connection
            #################################################################################
            try:
                ActSum_df_PostCon = ActSum_df_Temp[idx_start-2:]
                # st.write(ActSum_df_PostCon)

                PostCon_Start_idx = idx_start
                PostCon_End_idx = ActSum_df_PostCon[ActSum_df_PostCon['LABEL_SubActivity']=='Reaming'].index[0]
                ActSum_df.loc[PostCon_Start_idx:PostCon_End_idx,'LABEL_ConnectionActivity'] = 'Post Connection-'+str(before_stand_num)
            except:
                # st.write(ii)
                try:
                    ActSum_df.loc[PreCon_Start_idx:PreCon_End_idx,'LABEL_ConnectionActivity'] = ''
                except:
                    pass
                pass

    return ActSum_df
def replace_connection_with_nearest_activity(ActSum_df):
    connection_indices = ActSum_df.index[ActSum_df['LABEL_Activity'] == 'CONNECTION'].tolist()
    for conn_idx in connection_indices:
        prev_activities = ActSum_df['LABEL_Activity'].iloc[:conn_idx]
        next_activities = ActSum_df['LABEL_Activity'].iloc[conn_idx+1:]

        prev_nearest = prev_activities[prev_activities.isin(['DRILLING FORMATION', 'DRILL OUT CEMENT'])].last_valid_index()
        next_nearest = next_activities[next_activities.isin(['DRILLING FORMATION', 'DRILL OUT CEMENT'])].first_valid_index()

        dist_prev = np.inf if prev_nearest is None else conn_idx - prev_nearest
        dist_next = np.inf if next_nearest is None else next_nearest - conn_idx

        if dist_prev <= dist_next and prev_nearest is not None:
            replace_with = ActSum_df.at[prev_nearest, 'LABEL_Activity']
        elif next_nearest is not None:
            replace_with = ActSum_df.at[next_nearest, 'LABEL_Activity']
        else:
            replace_with = 'DRILLING FORMATION'

        ActSum_df.at[conn_idx, 'LABEL_Activity'] = replace_with
    return ActSum_df
def cleanFalseSensor(ActSum_df, MinuteTolerances=1, CleaningIteration=10, includeStatus=False):
    def _first_non_empty(x):
        non_empty_values = x[x != ''].tolist()
        return non_empty_values[0] if non_empty_values else ''
    # st.write('clean')
    if 'LABEL_ConnectionActivity' not in ActSum_df.columns:
        ActSum_df['LABEL_ConnectionActivity']  = ''
    # ActSum_df['LABEL_ConnectionActivity'] = ActSum_df['LABEL_ConnectionActivity'].fillna('-')

    # Set the Duration==0 to FALSE/Check
    # ActSum_df.loc[, 'LABEL_SubActivity'] = "Look and define"

    ActSum_df['Duration'] = ActSum_df['Duration'].astype('float')
    for iter in range(CleaningIteration):
        ActSum_df = ActSum_df.reset_index(drop=True)
        # while ("FALSE/Check" in ActSum_df['LABEL_SubActivity'].values) or ("Look and define" in ActSum_df['LABEL_SubActivity'].values):
        lookdefine_logic = ActSum_df['LABEL_SubActivity']=="Look and define"
        falsecheck_logic = ActSum_df['LABEL_SubActivity']=="FALSE/Check"
        duration_logic = (ActSum_df['Duration'] <= float(MinuteTolerances))

        
        idx_same = ActSum_df.index[
            (lookdefine_logic | falsecheck_logic) #& duration_logic
            ]
        idx_before = idx_same - 1

        idx_same = idx_same[idx_before>=0]
        idx_before = idx_before[idx_before>=0]
        
        ActSum_df.loc[idx_same, 'LABEL_SubActivity'] = ActSum_df.loc[idx_before, 'LABEL_SubActivity'].values
        ActSum_df.loc[idx_same, 'LABEL_All'] = ActSum_df.loc[idx_before, 'LABEL_All'].values
        AggDict = {'Date': 'max',
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
                    'LABEL_ConnectionActivity': _first_non_empty,
                    # 'PIC': 'first',
                    'InSlip_Treshold': 'first',
                    # 'Remarks': 'first',
                    'Section': 'first'
                    }
        # if includeStatus:
        #     AggDict['status'] = 'first'
        ActSum_df = ActSum_df.groupby((ActSum_df['LABEL_All'].shift() != ActSum_df['LABEL_All']).cumsum(), as_index=False).agg(AggDict)

    return ActSum_df

def groupActivity(RTSensor_df , DrillActivityList='default'):
    if DrillActivityList=='default':
        DrillActivityList = ["DRILLING FORMATION", 'CIRCULATE HOLE CLEANING','CONNECTION','DRILL OUT CEMENT',]


    RTSensor_df ['dt'] = pd.to_datetime(RTSensor_df ['dt'])
    RTSensor_df ["LABEL_All"] =RTSensor_df ['Section Size'].astype(str)+'--'+RTSensor_df ['SubActivity'].astype(str)+'--'+RTSensor_df['Activity'].astype(str)
    RTSensor_df ['Activity'] = RTSensor_df ['Activity'].fillna("N/A").astype(str)
    RTSensor_df ['SubActivity'] = RTSensor_df ['SubActivity'].fillna("N/A").astype(str)
    # TODO , a funtion that check the latest hole depth
    Hole_Depth_max = 0
    list_dict_out = []
    # st.write(RTSensor_df)
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
        # pic_data = DF_Temp['PIC'].iloc[0]
        InSlip_Treshold_data = DF_Temp['In-Slip Threshold'].iloc[0]
        # remarks_data = DF_Temp['remarks'].iloc[0]
        # status_data = DF_Temp['status'].iloc[0]

        # Duration(minutes)
        # the duration should add 5 second to compensate the delta 5s
        Duration = (((EndDateTime-StartDateTime).total_seconds()+5) / 60.0 )


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
            "LABEL_All": section_data+"--"+LABEL_SubActivity+'--'+LABEL_Activity,
            # "PIC":pic_data,
            "InSlip_Treshold":InSlip_Treshold_data,
            # "Remarks":remarks_data,
            "Section":section_data,
            # "status":status_data,

            }
        )

    ActSum_df = pd.DataFrame.from_dict(list_dict_out,orient='columns')
    
    # st.write(ActSum_df)

    
    listSetDecimals = ['Duration','Hole_Depth_max','Bit_Depth_avg','DrillingMeterage',
                       'RotateDrillingDuration','SlideDrillingDuration','ReamingDuration',
                       'ConnectionDuration','InSlip_Treshold',]
    for ColumnName in listSetDecimals:
        ActSum_df[ColumnName] = np.round(ActSum_df[ColumnName].astype('float'),2)
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
    ActSum_df['LABEL_SubActivity'] = ActSum_df['LABEL_SubActivity'].replace('CONNECTION', 'Connection')
    return ActSum_df
def predictSubActivityLabel(RTSensor_df, TripActivityList='default', DrillActivityList='default', OverrideActivityList='default'):
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
            # "PIC":'str',
            # "remarks":'str',
            "Section Size":'str',
            # "SubActivity":"object",
            # "logic_status":"int64",
            # "isBitDepthMoving":"bool",
            # "LABEL_All":"object",
        },
    # errors='coerce'
    )
    if TripActivityList=='default':
        TripActivityList = ['TRIP IN', 'TRIP OUT', 'WIPER TRIP']

        # TripActivityList = ['NPT', 'N/D BOP', 'N/U BOP', 'OTHER', 'RUNNING CASING IN', 'STATIONARY', 'STUCK PIPE', 
        #                     'TRIP IN', 'TRIP OUT', 'WAIT ON CEMENT', 'LAY DOWN BHA', 'MAKE UP BHA', 'WIPER TRIP']
        
    if DrillActivityList=='default':
        DrillActivityList = ["DRILLING FORMATION", 'CIRCULATE HOLE CLEANING','CONNECTION','DRILL OUT CEMENT',]

    if OverrideActivityList=='default':
        OverrideActivityList = ['CEMENTING JOB', 'CONNECTION', 'LAY DOWN BHA', 'MAKE UP BHA', 'NPT', 'N/D BOP', 
                                'N/U BOP', 'RUNNING CASING IN', 'STATIONARY', 'STUCK PIPE', 'WAIT ON CEMENT', 'RIG REPAIR','N/A', 'OTHER']

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
    SubActivity_Label = "Reaming"
    # SubActivity_Label = "Wash Up/Down"
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
    SubActivity_Label = "Reaming"
    # SubActivity_Label = "Wash Up/Down"
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
    list_columns = ["dt", 'date', 'time', "bitdepth", "md", "blockpos", "rop", "hklda", "woba", "torqa", 
                    "rpm", "stppress", "mudflowin", "In-Slip Threshold", "Section Size" ,'Activity', 'SubActivity']
    return RTSensor_df[list_columns]
def addRigActivityLabel (RTSensor_df, InputActivity_DB, UserDateRange="All"):
    
    ii = 0
    if UserDateRange != "All":
        StartDateTime = datetime.combine(UserDateRange['StartDate'], UserDateRange['StartTime'])
        EndDateTime = datetime.combine(UserDateRange['EndDate'], UserDateRange['EndTime'])
        RTSensor_df = RTSensor_df[(RTSensor_df['dt'] >= StartDateTime) & (RTSensor_df['dt'] < EndDateTime)]

    InputActivity_DB = InputActivity_DB.reset_index()

    for i,row in InputActivity_DB.iterrows():


        try:
            start_time_temp = InputActivity_DB.loc[ii, 'DateTime']
            end_time_temp = InputActivity_DB.loc[ii+1, 'DateTime']

            idx_logic = (RTSensor_df['dt'] >= start_time_temp) & (RTSensor_df['dt'] < end_time_temp)
        except:
            start_time_temp = InputActivity_DB.loc[ii, 'DateTime']

            idx_logic = (RTSensor_df['dt'] >= start_time_temp)

        activity_label_temp = InputActivity_DB.loc[ii, 'Activity']
        # pic_label_temp = InputActivity_DB.loc[ii, 'PIC']
        # section_label_temp = InputActivity_DB.loc[ii, 'Section Size']
        # remarks_label_temp = InputActivity_DB.loc[ii, 'Remarks']
        # activity_label_temp = InputActivity_DB.loc[ii, 'In-Slip Threshold']

        RTSensor_df.loc[idx_logic, ("Activity")] = activity_label_temp
        # RTSensor_df.loc[idx_logic, ("PIC")] = pic_label_temp
        # RTSensor_df.loc[idx_logic, ("Section Size")] = section_label_temp
        # RTSensor_df.loc[idx_logic, ("remarks")] = remarks_label_temp
        # RTSensor_df.loc[idx_logic, ("In-Slip Threshold")] = activity_label_temp
        ii = ii+1
    return RTSensor_df
def addSectionParams (RTSensor_df, InputActivity_DB, UserDateRange="All"):
    ii = 0
    if UserDateRange != "All":
        StartDateTime = datetime.combine(UserDateRange['StartDate'], UserDateRange['StartTime'])
        EndDateTime = datetime.combine(UserDateRange['EndDate'], UserDateRange['EndTime'])
        RTSensor_df = RTSensor_df[(RTSensor_df['dt'] >= StartDateTime) & (RTSensor_df['dt'] < EndDateTime)]

    InputActivity_DB = InputActivity_DB.reset_index()


    for i,row in InputActivity_DB.iterrows():


        try:
            start_time_temp = InputActivity_DB.loc[ii, 'DateTime']
            end_time_temp = InputActivity_DB.loc[ii+1, 'DateTime']

            idx_logic = (RTSensor_df['dt'] >= start_time_temp) & (RTSensor_df['dt'] < end_time_temp)
        except:
            start_time_temp = InputActivity_DB.loc[ii, 'DateTime']

            idx_logic = (RTSensor_df['dt'] >= start_time_temp)

        # activity_label_temp = InputActivity_DB.loc[ii, 'Activity']
        # pic_label_temp = InputActivity_DB.loc[ii, 'PIC']
        section_label_temp = InputActivity_DB.loc[ii, 'Section Size']
        # remarks_label_temp = InputActivity_DB.loc[ii, 'Remarks']
        activity_label_temp = InputActivity_DB.loc[ii, 'In-Slip Threshold']

        # RTSensor_df.loc[idx_logic, ("Activity")] = activity_label_temp
        # RTSensor_df.loc[idx_logic, ("PIC")] = pic_label_temp
        RTSensor_df.loc[idx_logic, ("Section Size")] = section_label_temp
        # RTSensor_df.loc[idx_logic, ("remarks")] = remarks_label_temp
        RTSensor_df.loc[idx_logic, ("In-Slip Threshold")] = activity_label_temp
        ii = ii+1
    return RTSensor_df

def Override(RTSensor_df, Override_df, ):
    if Override_df.empty:
        return RTSensor_df
    ii = 0
 
    Override_df = Override_df.reset_index()
    # print("Override Table")
    # print(Override_df)


    for i,row in Override_df.iterrows():


        start_time_temp = row['StartDateTime']
        end_time_temp = row['EndDateTime']

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



def getROP_df(ActSum_df):
    ROP_df = ActSum_df.copy()
    ROP_df['StartDateTime'] = pd.to_datetime(ROP_df['StartDateTime'])
    ROP_df['EndDateTime'] = pd.to_datetime(ROP_df['EndDateTime'])
    ROP_df[['DrillingMeteragePerStand', 'OnBottomDurationPerStand', 'StandDuration']] = ROP_df[['DrillingMeteragePerStand', 'OnBottomDurationPerStand', 'StandDuration']].astype(float)

    # Calculate MidDateTime as the average of StartDateTime and EndDateTime
    ROP_df['MidDateTime'] = ROP_df['StartDateTime'] + (ROP_df['EndDateTime'] - ROP_df['StartDateTime']) / 2

    idx_logic = (ROP_df['LABEL_Activity'].isin(["DRILLING FORMATION", 'CIRCULATE HOLE CLEANING','DRILL OUT CEMENT',])) & (ROP_df['LABEL_SubActivity'] == 'Connection')


    ROP_df = ROP_df[idx_logic]

    ROP_df['ROP_OnBottom'] = ROP_df['DrillingMeteragePerStand'] / (ROP_df['OnBottomDurationPerStand']/60) 
    ROP_df['ROP_Stand'] = ROP_df['DrillingMeteragePerStand'] / (ROP_df['StandDuration']/60)
    ROP_df['ROP_Percentage'] = ROP_df['ROP_Stand']/ROP_df['ROP_OnBottom']  * 100
    ROP_df['Stand Group_Pred'] = ROP_df['LABEL_ConnectionActivity'].str.replace('Connection-', 'Drilling Stand-')
    return ROP_df[['StartDateTime','EndDateTime', 'DrillingMeteragePerStand', 'OnBottomDurationPerStand', 'StandDuration', 'ROP_OnBottom', 'ROP_Stand', 'ROP_Percentage', 'Stand Group_Pred']]

def getConnectionTime_df(ActSum_df):
    ConnectionTime_df = ActSum_df.copy()

    if ConnectionTime_df['LABEL_ConnectionActivity'].str.contains("-", na=False).any():
        ConnectionTime_df[['ConnectionCategory', 'ConnectionID']] = ConnectionTime_df['LABEL_ConnectionActivity'].str.split('-', expand=True)

        ConnectionTime_df['StartDateTime'] = pd.to_datetime(ConnectionTime_df['StartDateTime'])
        ConnectionTime_df['EndDateTime'] = pd.to_datetime(ConnectionTime_df['EndDateTime'])
        # Calculate MidDateTime as the average of StartDateTime and EndDateTime
        # ConnectionTime_df['MidDateTime'] = ConnectionTime_df['StartDateTime'] + (ConnectionTime_df['EndDateTime'] - ConnectionTime_df['StartDateTime']) / 2

        ConnectionTime_agg_df = ConnectionTime_df.groupby(['ConnectionID', 'ConnectionCategory']).agg(
            Total_Duration=('Duration', 'sum'),
            First_StartDatetime=('StartDateTime', 'min'),
            Latest_EndDatetime=('EndDateTime', 'max')
        ).reset_index()
        # Pivot the data to match the requested output format
        ConnectionTime_pivot_df = ConnectionTime_agg_df.pivot(index='ConnectionID', columns='ConnectionCategory', values='Total_Duration').reset_index()

        # Renaming columns to match the desired output
        # ConnectionTime_pivot_df.columns = ['ConnectionID', 'ConnectionDuration', 'PostConnectionDuration', 'PreConnectionDuration']
        ConnectionTime_pivot_df = ConnectionTime_pivot_df.rename(columns={
            'Connection': 'ConnectionDuration', 
            'Post Connection': 'PostConnectionDuration', 
            'Pre Connection': 'PreConnectionDuration'
        })
        # Merge with the original DataFrame to get the StartDatetime and EndDatetime
        start_end_times = ConnectionTime_df.groupby('ConnectionID').agg(
            StartDatetime=('StartDateTime', 'min'),
            EndDatetime=('EndDateTime', 'max')
        ).reset_index()

        # Merging the pivoted DataFrame with the start and end times
        ConnectionTime_pivot_df = pd.merge(ConnectionTime_pivot_df, start_end_times, on='ConnectionID')
        ConnectionTime_pivot_df[['PreConnectionDuration', 'ConnectionDuration', 'PostConnectionDuration']] = ConnectionTime_pivot_df[['PreConnectionDuration', 'ConnectionDuration', 'PostConnectionDuration']].fillna(0)
        return ConnectionTime_pivot_df[[ 'StartDatetime', 'EndDatetime', 'PreConnectionDuration', 'ConnectionDuration', 'PostConnectionDuration', 'ConnectionID']]
    else:
        return pd.DataFrame(columns=['StartDatetime', 'EndDatetime', 'PreConnectionDuration', 'ConnectionDuration', 'PostConnectionDuration', 'ConnectionID'])

def getStandTime_df(ActSum_df):
    StandTime_df = ActSum_df.copy()
    if StandTime_df['Stand Group_Pred'].str.contains("Drilling", na=False).any():
        StandTime_df = StandTime_df[ StandTime_df['Stand Group_Pred'].str.contains(r'Drilling', case=False, na=False)]

        last_indices = StandTime_df.groupby("Stand Group_Pred").apply(lambda x: x.index[-1]).values
        StandTime_df = ActSum_df.copy()
        StandTime_df.loc[last_indices[:-1] + 1, 'Stand Group_Pred'] = StandTime_df.loc[last_indices[:-1], 'Stand Group_Pred'].values
        StandTime_df = StandTime_df[ StandTime_df['Stand Group_Pred'].str.contains(r'Drilling', case=False, na=False)]
        StandTime_df[['RotateDrillingDuration', 'SlideDrillingDuration', 'ReamingDuration', 'ConnectionDuration']] = StandTime_df[['RotateDrillingDuration', 'SlideDrillingDuration', 'ReamingDuration', 'ConnectionDuration']].astype(float)
        
        StandTime_df = StandTime_df.groupby('Stand Group_Pred').agg({
            'RotateDrillingDuration': 'sum',
            'SlideDrillingDuration': 'sum',
            'ReamingDuration': 'sum',
            'ConnectionDuration': 'sum',
            'EndDateTime': 'max',
            'StartDateTime': 'min',
        }).reset_index()
        StandTime_df[['RotateDrillingDuration', 'SlideDrillingDuration', 'ReamingDuration', 'ConnectionDuration']].fillna(0, inplace=True)

        
        return StandTime_df
    else:
        return pd.DataFrame(columns=['RotateDrillingDuration', 'SlideDrillingDuration', 'ReamingDuration', 'ConnectionDuration', 'EndDateTime', 'StartDateTime', 'Stand Group_Pred'])

def getBHA_TripBreakdown_df(ActSum_df):
    BHA_Trip_df = ActSum_df.copy()
    BHA_Trip_df = BHA_Trip_df[BHA_Trip_df['LABEL_SubActivity'].str.contains(r'BHA|N/D|N/U BOP|POOH', case=False, na=False)]
    BHA_Trip_df['StartDateTime'] = pd.to_datetime(BHA_Trip_df['StartDateTime'])
    BHA_Trip_df['EndDateTime'] = pd.to_datetime(BHA_Trip_df['EndDateTime'])
    BHA_Trip_df['Duration'] = BHA_Trip_df['Duration'].astype(float)
    


    return BHA_Trip_df[['StartDateTime', 'EndDateTime', 'Duration', 'LABEL_SubActivity', 'LABEL_Activity']]

def GroupCasingJoint(ActSum_df):
    CasingTrip_df = ActSum_df.copy()
    CasingTrip_df['Stand Group_Pred_TRIP'] = ""
    
    if ("TRIP IN" in CasingTrip_df['LABEL_Activity'].unique()) or ("TRIP OUT" in CasingTrip_df['LABEL_Activity'].unique()):
            CasingTrip_df['GroupChange'] = (CasingTrip_df['LABEL_Activity'] != CasingTrip_df['LABEL_Activity'].shift()).cumsum()
            CasingTripGroup = CasingTrip_df.groupby('GroupChange').apply(
                lambda x: {
                    "Group": x['LABEL_Activity'].iloc[0],
                    "StartIndex": x.index[0],
                    "EndIndex": x.index[-1],
                }
            )
            CasingTripGroup = pd.DataFrame(CasingTripGroup.tolist())
            CasingTripGroup = CasingTripGroup[CasingTripGroup['Group'].isin(['TRIP IN', 'TRIP OUT'])]
            for idx, row in CasingTripGroup.iterrows():
                CasingTrip_df_temp = CasingTrip_df.loc[row['StartIndex']:row['EndIndex']]

            # CasingTrip_df_temp = CasingTrip_df[CasingTrip_df['LABEL_Activity'].isin(['TRIP IN', 'TRIP OUT'])]
                CasingTrip_df_temp['StartDateTime'] = pd.to_datetime((CasingTrip_df_temp['StartDateTime']))
                CasingTrip_df_temp['EndDateTime'] = pd.to_datetime((CasingTrip_df_temp['EndDateTime']))
            # CasingTrip_df = CasingTrip_df.reset_index(drop=True)

                # Step 2: Find indices where the activity is 'Connection'
                if 'Connection' in CasingTrip_df_temp['LABEL_SubActivity'].unique():
                    connection_indices = CasingTrip_df_temp[CasingTrip_df_temp['LABEL_SubActivity'] == 'Connection'].index.tolist()
                    segments_start_list = []
                    segments_end_list = []

                    for i,indices in enumerate(connection_indices):
                        if i == 0:
                            segments_start_list.append(CasingTrip_df_temp.index[0])
                            segments_end_list.append(indices)
                        else:
                            segments_start_list.append(connection_indices[i-1]+1)
                            segments_end_list.append(indices)

                    for segments_start,segments_end, connection_idx in zip(segments_start_list, segments_end_list, connection_indices):

                        CasingTrip_df.loc[segments_start:segments_end, 'Stand Group_Pred_TRIP'] = int(CasingTrip_df_temp.loc[connection_idx,'StartDateTime'].timestamp())
                        CasingTrip_df.loc[segments_start:segments_end, 'Stand Group_Pred_TRIP'] = "Casing Joint-" + CasingTrip_df.loc[segments_start:segments_end, 'Stand Group_Pred_TRIP'].astype(str)
    return CasingTrip_df

def getCasingTrip_df(ActSum_df):
    CasingTrip_df = ActSum_df.copy()


    CasingTrip_df = CasingTrip_df[CasingTrip_df['Stand Group_Pred_TRIP'].str.contains(r'Casing Joint-', case=False, na=False)]
    CasingTrip_df['Duration'] = CasingTrip_df['Duration'].astype(float)

    if CasingTrip_df.empty:
        return pd.DataFrame(columns=['Stand Group_Pred_TRIP',  'Duration', 'StartDateTime', 'EndDateTime', 'Duration_Hours', 'Joint Per Hour'])
    FinalCasingTrip_df = CasingTrip_df[["Stand Group_Pred_TRIP", "LABEL_SubActivity", "Duration", "StartDateTime", "EndDateTime"]]
    FinalCasingTrip_df = FinalCasingTrip_df.groupby("Stand Group_Pred_TRIP", as_index=False).agg(
            Duration=("Duration", "sum"),
            StartDateTime=("StartDateTime", "min"),
            EndDateTime=("EndDateTime", "max"),
        )

    FinalCasingTrip_df.drop_duplicates(subset=['StartDateTime'], keep='first', inplace=True)
    # FinalCasingTrip_df['StartDateTime'] = pd.to_datetime(FinalCasingTrip_df['StartDateTime'])
    FinalCasingTrip_df['Duration_Hours'] = FinalCasingTrip_df['Duration'] / 60
    FinalCasingTrip_df['Joint Per Hour'] = 1/FinalCasingTrip_df['Duration_Hours']
    return FinalCasingTrip_df

def getCasingTripBreakdown_df(ActSum_df):
    CasingTripBreakdown_df = ActSum_df.copy()

    CasingTripBreakdown_df = CasingTripBreakdown_df[CasingTripBreakdown_df['Stand Group_Pred_TRIP'].str.contains(r'Casing Joint-', case=False, na=False)]
    if CasingTripBreakdown_df.empty:
        return pd.DataFrame(columns=['Stand Group_Pred_TRIP', 'LABEL_SubActivity', 'Duration', 'StartDateTime', 'EndDateTime', 'Duration_Hours'])
    FinalCasingTripBreakdown_df = CasingTripBreakdown_df[["Stand Group_Pred_TRIP", "LABEL_SubActivity", "Duration", "StartDateTime", "EndDateTime"]]
    FinalCasingTripBreakdown_df['Duration'] = FinalCasingTripBreakdown_df['Duration'].astype(float)
    FinalCasingTripPerJoint_df = FinalCasingTripBreakdown_df.groupby("Stand Group_Pred_TRIP", as_index=False).agg(
                        # Duration=("Duration", "sum"),
                        StartDateTime=("StartDateTime", "min"),
                        EndDateTime=("EndDateTime", "max"),
                    ) 

    FinalCasingTripBreakdown_df = FinalCasingTripBreakdown_df.groupby(["Stand Group_Pred_TRIP", "LABEL_SubActivity"], as_index=False).agg(
                        Duration=("Duration", "sum"),
                        # StartDateTime=("StartDateTime", "first")
                    )

    FinalCasingTripBreakdown_df = FinalCasingTripBreakdown_df.merge(
                    FinalCasingTripPerJoint_df[['Stand Group_Pred_TRIP', 'StartDateTime','EndDateTime']],
                    on='Stand Group_Pred_TRIP',
                    how='left'
                )
    FinalCasingTripBreakdown_df['StartDateTime'] = pd.to_datetime(FinalCasingTripBreakdown_df['StartDateTime'])
    FinalCasingTripBreakdown_df['Duration_Hours'] = FinalCasingTripBreakdown_df['Duration'] / 60
    # FinalCasingTripBreakdown_df['Joint Per Hour'] = 1/FinalCasingTripBreakdown_df['Duration_Hours']
    return FinalCasingTripBreakdown_df

                # FinalCasingTrip_df.drop_duplicates(subset=['StartDateTime'], keep='first', inplace=True)
                # FinalCasingTrip_df['StartDateTime'] = pd.to_datetime(FinalCasingTrip_df['StartDateTime'])
                # FinalCasingTrip_df['Duration_Hours'] = FinalCasingTrip_df['Duration'] / 60
                # FinalCasingTrip_df['Joint Per Hour'] = 1/FinalCasingTrip_df['Duration_Hours']
                # return FinalCasingTrip_df

def getRemarks(ActSum_df):
    Remarks_df = ActSum_df.copy()
    Remarks_df = Remarks_df[Remarks_df['Remarks'].notna()]
    Remarks_df = Remarks_df[Remarks_df['Remarks'] != '']
    return Remarks_df[['StartDateTime', 'EndDateTime','LABEL_SubActivity', 'LABEL_Activity', 'PIC', 'Remarks']]

def translateRigActivity2Activity(RigActivityDF):
    replacement_dict = {
        "Cementing":"Cementing Job",
        "Condition and/or Circulate mud":"Circulation",
        "Connection (drilling)":"Drilling Formation",
        "Cut/Slip Drilling Line":"Other",
        "Drill Cement and/or Float Equipment":"Drill Out Cement",
        "Drilling":"Drilling Formation",
        "Fishing":"Other",
        "Flow Check":"Other",
        "Lost Circulation":"Other",
        "Lubricate Rig":"Rig Repair",
        "Nipple Up /Nipple Down BOP Stack":"Make up BHA",
        "Plug Back":"Other",
        "Pressure Integrity Test":"Other",
        "Reaming":"Stationary",
        "Rig Repair":"Rig Repair",
        "Run Casing":"Running Casing In",
        "Short Trip In":"Trip In",
        "Short Trip Out":"Trip Out",
        "Squeeze Cementing":"Cementing Job",
        "Stuck Pipe":"Stuck Pipe",
        "Test BOP":"Make up BHA",
        "Tripping In":"Trip In",
        "Tripping Out":"Trip Out",
        "Undefined Status":"Other",
        "Wait on Cement":"Wait on Cement",
        "Wireline Logs":"Other",
    }
    RigActivityDF['Activity'] = RigActivityDF['Activity'].replace(replacement_dict)
    RigActivityDF['Activity'] = RigActivityDF['Activity'].str.upper()

    
    return RigActivityDF