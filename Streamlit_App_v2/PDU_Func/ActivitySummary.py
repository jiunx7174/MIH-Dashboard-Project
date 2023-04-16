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
        
    
    def getActivitySummary(self,):
        """
        download the activity summary table from existing server
        """
        UserDateRange = self.UserDateRange
        WellInfoDict = self.WellInfoDict

        StartDateTime = datetime.strptime(UserDateRange['StartDate'] + " " + UserDateRange['StartTime'], '%Y-%m-%d %H:%M:%S')
        EndDateTime = datetime.strptime(UserDateRange['EndDate'] + " " + UserDateRange['EndTime'], '%Y-%m-%d %H:%M:%S')
        
        temp_ActSum_df = IO_Data.DomeGetData(WellInfoDict, UserDateRange, table_type="Activity Summary")
        if list(temp_ActSum_df.columns) != []:
            self.Data[list(temp_ActSum_df.columns)] = temp_ActSum_df[list(temp_ActSum_df.columns)]
            self.Data['wid'] =  int(WellInfoDict['wid'])
            self.Data['status'] =  "FIRM"
            StartDateTime = self.Data['time_end'].max()

        if  StartDateTime <= EndDateTime:
            UserDateRangeUpdate = {
                    "StartDate": StartDateTime.strftime('%Y-%m-%d'),
                    "StartTime": StartDateTime.strftime('%H:%M:%S'),
                    "EndDate": EndDateTime.strftime('%Y-%m-%d'),
                    "EndTime": EndDateTime.strftime('%H:%M:%S'),
                    }
            # print(UserDateRangeUpdate)
            temp_RTSensor_df =IO_Data.DomeGetRealtimeSensorData(WellInfoDict, UserDateRangeUpdate)
            return temp_RTSensor_df, temp_ActSum_df


        pass
    def ApplyMappingFunction():
        pass
    def calculateDuration():
        pass
    def LabelStand():
        pass

    def Update():
        pass
    def Insert():
        pass
    def Delete():
        pass


