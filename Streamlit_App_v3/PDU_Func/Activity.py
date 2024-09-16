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


def translateRigActivity2Activity(RigActivityDF):
    replacement_dict = {
        "Cementing":"Cementing Job",
        "Condition and/or Circulate mud":"Circulation",
        "Connection (drilling)":"Connection",
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