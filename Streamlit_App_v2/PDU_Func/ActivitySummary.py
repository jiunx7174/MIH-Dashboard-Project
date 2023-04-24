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
        
    
    def getActivitySummary(self,InputActivity_DB):
        """
        download the activity summary table from existing server
        """
        UserDateRange = self.UserDateRange
        WellInfoDict = self.WellInfoDict

        StartDateTime = datetime.strptime(UserDateRange['StartDate'] + " " + UserDateRange['StartTime'], '%Y-%m-%d %H:%M:%S')
        EndDateTime = datetime.strptime(UserDateRange['EndDate'] + " " + UserDateRange['EndTime'], '%Y-%m-%d %H:%M:%S')
        
        # get the ActivitySummaryTable data between the UserDateRange
        temp_ActSum_df = IO_Data.DomeGetData(WellInfoDict, UserDateRange, table_type="Activity Summary")
        
        # If the ActivitySummaryTable between the UserDateRange is exist or partially exist
        # TODO, if we want to fill out a "Gap" ActSumTable case

        if list(temp_ActSum_df.columns) != []:
            self.Data[list(temp_ActSum_df.columns)] = temp_ActSum_df[list(temp_ActSum_df.columns)]
            self.Data['wid'] =  int(WellInfoDict['wid'])
            self.Data['status'] =  "FIRM"
            StartDateTime = self.Data['time_end'].max()

        # if the ActSumTable max end time is outside the UserDateRange, 
        # then ActivityMapping is no longer needed
        if  StartDateTime >= EndDateTime:
            return self.Data

        # TODO the strftime should be done in IO_Data.DomeGetRealtimeSensorData function
        UserDateRangeUpdate = {
                    "StartDate": StartDateTime.strftime('%Y-%m-%d'),
                    "StartTime": StartDateTime.strftime('%H:%M:%S'),
                    "EndDate": EndDateTime.strftime('%Y-%m-%d'),
                    "EndTime": EndDateTime.strftime('%H:%M:%S'),
                    }
        

        # get the realtime data
        RTSensor_df =IO_Data.DomeGetRealtimeSensorData(WellInfoDict, UserDateRangeUpdate)
        # labelling the activity data with the ActLogData
        RTSensor_df = ActivityLogLabelling (RTSensor_df, ActivityLog_DF)
        # apply the PDU mapping logic function
        RTSensor_df = SubActivityMapping(RTSensor_df)
        # group and aggregate the Realtime data into ActitivtySummaryTable
        
        #TODO 
        # -create the GroupActivity function
        # -create the false sensor cleaning, should be different function(?)

        tail_ActSum_df = GroupSubActivity(RTSensor_df)


        return tail_ActSum_df


        

    def GroupSubActivity(RTSensor_df):
        return RTSensor_df
    def LabelStand():
        pass

    def Update():
        pass
    def Insert():
        pass
    def Delete():
        pass


    # Activity_DF = Activity.GetActivity_DF(Activity_DF, Input_Temp)

    # Activity_DF = Activity.GetSubActivity_DF_v3(Activity_DF)
    
    # if RadioButton=='No/RAW':
    #     SummaryActivity_DF = Activity.labelStand_v2(Activity.GenerateDuration_DF_v4(Activity_DF))
    # else:
    #     SummaryActivity_DF = Activity.labelStand_v2(Activity.cleanFalseSensor((Activity.GenerateDuration_DF_v4(Activity_DF))))

def SubActivityMapping(RTSensor_df):
    #TODO makesure the column name and data type is match
    Activity_DF = Activity_DF.astype(
        {
            "dt":"datetime64",
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
            "Hookload Treshold":"float64",
            "pic":'str',
            "remarks":'str',
            "section":'str',
            # "SubActivity":"object",
            # "logic_status":"int64",
            # "isBitDepthMoving":"bool",
            # "LABEL_All":"object",
        }
    )
    
    logic_status = 0
    Activity_DF["SubActivity"] = "FALSE/Check"
    Activity_DF["logic_status"] = logic_status



    # TODO use drilling activity as list input 
    idx_logic_activity = Activity_DF["Activity"].isin(["DRILLING FORMATION", 
                                            'CIRCULATE HOLE CLEANING',
                                            'CONNECTION',
                                            'DRILL OUT CEMENT',
                                        ])
    # print((Activity_DF.dtypes))

    idx_logic = idx_logic_activity & ((Activity_DF['woba']>0) & (Activity_DF['rpm']>10) & (Activity_DF['stppress']>100) & (Activity_DF['hklda']>Activity_DF['Hookload Treshold']))
    SubActivity_Label = "Rotary Drilling"
    Activity_DF.loc[idx_logic, "SubActivity"] = SubActivity_Label
    #

    logic_status = logic_status + 1
    Activity_DF.loc[idx_logic, "logic_status"] = logic_status
    # 1

    logic_status = logic_status + 1
    Activity_DF.loc[idx_logic, "logic_status"] = logic_status

    idx_logic = idx_logic_activity &(Activity_DF["SubActivity"] == "FALSE/Check") & ((Activity_DF['woba']>0) & (Activity_DF['rpm']<10) & (Activity_DF['stppress']>100) & (Activity_DF['hklda']>Activity_DF['Hookload Treshold']))
    SubActivity_Label = "Slide Drilling"
    Activity_DF.loc[idx_logic, "SubActivity"] = SubActivity_Label
    # 2

    logic_status = logic_status + 1
    Activity_DF.loc[idx_logic, "logic_status"] = logic_status
    
    idx_logic = idx_logic_activity &(Activity_DF["SubActivity"] == "FALSE/Check") & ((Activity_DF['woba']==0) & (Activity_DF['rpm']>10) & (Activity_DF['stppress']>100) & (Activity_DF['hklda']>Activity_DF['Hookload Treshold']))
    SubActivity_Label = "Reaming"
    Activity_DF.loc[idx_logic, "SubActivity"] = SubActivity_Label
    #3

    logic_status = logic_status + 1
    Activity_DF.loc[idx_logic, "logic_status"] = logic_status

    idx_logic = idx_logic_activity &(Activity_DF["SubActivity"] == "FALSE/Check") & ((Activity_DF['woba']==0) & (Activity_DF['rpm']==0) & (Activity_DF['stppress']>100) & (Activity_DF['hklda']>Activity_DF['Hookload Treshold']))
    SubActivity_Label = "Wash Up/Down"
    Activity_DF.loc[idx_logic, "SubActivity"] = SubActivity_Label
    #4

    logic_status = logic_status + 1
    Activity_DF.loc[idx_logic, "logic_status"] = logic_status


    idx_logic = idx_logic_activity &(Activity_DF["SubActivity"] == "FALSE/Check") & ((Activity_DF['woba']==0) & (Activity_DF['rpm']==0) & (Activity_DF['stppress']<50))
    SubActivity_Label = "Connection"
    Activity_DF.loc[idx_logic, "SubActivity"] = SubActivity_Label
    #5

    logic_status = logic_status + 1
    Activity_DF.loc[idx_logic, "logic_status"] = logic_status

    # idx_logic = idx_logic_activity & ((Activity_DF["SubActivity"] == "FALSE/Check") & (Activity_DF['hklda']>Activity_DF['Hookload Treshold']))
    idx_logic = idx_logic & (Activity_DF['hklda']>Activity_DF['Hookload Treshold'])
    SubActivity_Label="Look and define"
    Activity_DF.loc[idx_logic, "SubActivity"] = SubActivity_Label
    #6

    logic_status = logic_status + 1
    Activity_DF.loc[idx_logic, "logic_status"] = logic_status
    #7

    # TODO use tripping activity as list input
    # ############################
    idx_logic_activity_2 = Activity_DF["Activity"].isin([
                                            'NPT',
                                            'N/D BOP',
                                            'N/U BOP',
                                            'OTHER',
                                            'RUNNING CASING IN',
                                            'STATIONARY',
                                            'STUCK PIPE',
                                            'TRIP IN',
                                            'TRIP OUT',
                                            'WAIT ON CEMENT',
                                            'LAY DOWN BHA',
                                            'MAKE UP BHA',
                                            'WIPER TRIP'
                                        ]
                                        )
    Activity_DF['isBitDepthMoving'] = Activity_DF['bitdepth'].shift(periods=-1) != Activity_DF['bitdepth']

    # Activity_DF["LABEL_SubActivity"] = "Check"
    idx_logic_2 = idx_logic_activity_2 & ((Activity_DF['isBitDepthMoving']) & (Activity_DF['hklda']>Activity_DF['Hookload Treshold']) & (Activity_DF['rpm']==0) & (Activity_DF['mudflowin']>10))
    SubActivity_Label = "Wash Up/Down"
    Activity_DF.loc[idx_logic_2, "SubActivity"] = SubActivity_Label
    # DisplayDF(Activity_DF.loc[idx_logic_2, :])
    #

    logic_status = logic_status + 1
    Activity_DF.loc[idx_logic_2, "logic_status"] = logic_status
    #8
    
    idx_logic_2 = idx_logic_activity_2 &(Activity_DF["SubActivity"] == "FALSE/Check") & ((Activity_DF['isBitDepthMoving']) & (Activity_DF['hklda']>Activity_DF['Hookload Treshold']) & (Activity_DF['rpm']>10) & (Activity_DF['stppress']>100) & (Activity_DF['mudflowin']>10))
    SubActivity_Label = "Reaming"
    Activity_DF.loc[idx_logic_2, "SubActivity"] = SubActivity_Label
    

    logic_status = logic_status + 1
    Activity_DF.loc[idx_logic_2, "logic_status"] = logic_status
    #9

    idx_logic_2 = idx_logic_activity_2 &(Activity_DF["SubActivity"] == "FALSE/Check") & ((Activity_DF['isBitDepthMoving']) & (Activity_DF['hklda']>Activity_DF['Hookload Treshold']) & (Activity_DF['rpm']<10) & (Activity_DF['stppress']<100) & (Activity_DF['mudflowin']<50))
    SubActivity_Label = "Moving"
    Activity_DF.loc[idx_logic_2, "SubActivity"] = SubActivity_Label

    logic_status = logic_status + 1
    Activity_DF.loc[idx_logic_2, "logic_status"] = logic_status
    #10

    idx_logic_2 = idx_logic_activity_2 &(Activity_DF["SubActivity"] == "FALSE/Check") & (~(Activity_DF['isBitDepthMoving']) & (Activity_DF['hklda']>Activity_DF['Hookload Treshold']) & (Activity_DF['mudflowin']>10))
    SubActivity_Label = "Circulation"
    Activity_DF.loc[idx_logic_2, "SubActivity"] = SubActivity_Label
    #

    logic_status = logic_status + 1
    Activity_DF.loc[idx_logic_2, "logic_status"] = logic_status
    #11

    idx_logic_2 = idx_logic_activity_2 &(Activity_DF["SubActivity"] == "FALSE/Check") & ((Activity_DF['mudflowin']<10) & (Activity_DF['rpm']<10) & (Activity_DF['hklda']<Activity_DF['Hookload Treshold']))
    SubActivity_Label = "Connection"
    Activity_DF.loc[idx_logic_2, "SubActivity"] = SubActivity_Label
    #

    logic_status = logic_status + 1
    Activity_DF.loc[idx_logic_2, "logic_status"] = logic_status
    #12

    idx_logic_2 = idx_logic_activity_2 &(Activity_DF["SubActivity"] == "FALSE/Check") & ((~Activity_DF['isBitDepthMoving']) & (Activity_DF['mudflowin']<10) & (Activity_DF['rpm']<10) & (Activity_DF['hklda']>Activity_DF['Hookload Treshold']))
    SubActivity_Label = "Stationary"
    Activity_DF.loc[idx_logic_2, "SubActivity"] = SubActivity_Label
    #

    logic_status = logic_status + 1
    Activity_DF.loc[idx_logic_2, "logic_status"] = logic_status
    #13
    # TODO use user same/override activity as list input
    ## force to be same as activity
    idx_logic_3 = Activity_DF["Activity"].isin([
                            'CEMENTING JOB',
                            'CONNECTION',
                            'LAY DOWN BHA',
                            'MAKE UP BHA',
                            'NPT',
                            'N/D BOP',
                            'N/U BOP',
                            'RUNNING CASING IN',
                            'STATIONARY',
                            'STUCK PIPE',
                            'WAIT ON CEMENT',
                            'RIG REPAIR',
    ])
    Activity_DF.loc[idx_logic_3, "SubActivity"] = Activity_DF.loc[idx_logic_3, "Activity"]
    #

    logic_status = logic_status + 1
    Activity_DF.loc[idx_logic_3, "logic_status"] = logic_status
    #14

    # print(Activity_DF.columns)

    return Activity_DF

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
            start_time_temp = InputActivity_DB.loc[ii, 'dt']
            end_time_temp = InputActivity_DB.loc[ii+1, 'dt']
            # print(InputActivity_DB.iloc[ii+1, 0])
            idx_logic = (RTSensor_df['dt'] >= start_time_temp) & (RTSensor_df['dt'] < end_time_temp)
        except:
            start_time_temp = InputActivity_DB.loc[ii, 'dt']
            # print(InputActivity_DB.iloc[ii, 0])
            # print('test')
            # end_time_temp = InputActivity_DB.loc[ii+1, 'dt']
            # print((RTSensor_df['dt'].dtypes))
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
        RTSensor_df.loc[idx_logic, ("Hookload Treshold")] = activity_label_temp
        ii = ii+1
    
    return RTSensor_df