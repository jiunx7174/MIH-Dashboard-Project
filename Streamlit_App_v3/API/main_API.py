from fastapi import FastAPI, HTTPException, Request,Query
from pydantic import BaseModel, constr
from fastapi.responses import JSONResponse
from typing import List, Dict , Literal
from importlib import reload
import sys
import os
import time
import numpy as np
import json
import requests
# Get the directory of the current file
current_dir = os.path.dirname(__file__)
# If you specifically want to use os.path.join() for clarity
up_one_folder = os.path.join(current_dir, '..')
# Normalize the path to resolve any '..'
library_path = os.path.normpath(up_one_folder)
# Add the path to sys.path
sys.path.append(library_path)
def getURLAPI_pdu():
    return "http://pdumitradome.id/dome_api/"
def getURLAPI_FastAPI():
    return "http://pdumitradome.id:8090/"

import pandas as pd
from fastapi.responses import HTMLResponse
from PDU_Func import Activity, Authentification, IO_Data
from Page import Override
from importlib import reload
import datetime
reload(Activity)
reload(IO_Data)
# reload(IO_Data)
# reload(Activity)
app = FastAPI()

class SectionParamsDataModel(BaseModel):
    # Define the structure of your JSON data here
    # For example:
    wid: int
    DateTime : str
    SectionSize : str
    PIC : str
class updateDataRequest(BaseModel):
    wid: int
    cid: int

def getHTML_Table(df_list):
    html_content = f"""
    <html>
    <head>
    <title>Multiple DataFrames</title>
    <style>
    table, th, td {{
      border: 1px solid black;
      border-collapse: collapse;
      padding: 5px;
      text-align: left;
    }}
    </style>
    </head>
    <body>"""
        # Concatenate the HTML strings with some formatting
    for i,df in enumerate(df_list):
        html_content += f"<h2>DataFrame {i+1}</h2>"
        html_content += df.to_html()
        html_content += "<br><hr><br>"
    html_content += "</body></html>"

    return html_content
class UpdateDataRequest(BaseModel):
    wid: int
    cid: int
    sync_datetime: str
@app.post("/update-data-multiuser/")
def update_data_multiuser(data: updateDataRequest):
    wid = data.wid
    cid = data.cid

    for i in range(20):
        if i==0:
            new_wid = wid
            new_cid = cid
        else:
            new_wid = new_wid+wid
            new_cid = new_cid+cid
        print({"new_wid":new_wid, "new_cid":new_cid})
        time.sleep(3)


    return {"new_wid":new_wid, "new_cid":new_cid}

@app.post("/update-activity-summary-data/")
def update_realtime_data(data: UpdateDataRequest):
    wid = data.wid
    cid = data.cid
    sync_datetime = data.sync_datetime
    WellInfoDict = IO_Data.getWellInfoDict_byID(cid, wid)

    SectionParams_DF = IO_Data.DomeSectionParamsTable_Get(WellInfoDict)
    if SectionParams_DF.empty:
        return JSONResponse(
            status_code=404,
            content={"detail": "inslip threshold not set"}
        )
    df_list = []
    try:
        LastDateTime_obj = datetime.datetime.strptime(sync_datetime, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid sync_datetime format. Please use 'YYYY-MM-DD HH:MM:SS'.")
    UserDateRange_Sync = {
    "StartDate": datetime.date(2000, 4, 9),
    "StartTime": datetime.time(00, 00),
    "EndDate": LastDateTime_obj.date(),
    "EndTime": LastDateTime_obj.time()
    }

    df_list.append(pd.DataFrame.from_records([UserDateRange_Sync]))
    StartDateTime = IO_Data.getLastActSum(WellInfoDict, UserDateRange_Sync, DrillActivityList='default')['StartDateTime']
    StartDateTime_obj = datetime.datetime.strptime(StartDateTime.values[0], '%Y-%m-%d %H:%M:%S')

    UserDateRange_Sync = {
    "StartDate": StartDateTime_obj.date(),
    "StartTime": StartDateTime_obj.time(),
    "EndDate": LastDateTime_obj.date(),
    "EndTime": LastDateTime_obj.time()
    }

    print(f"request realtime data {UserDateRange_Sync}")
    df_list.append(pd.DataFrame.from_records([UserDateRange_Sync]))
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
    ActivitySummary_DF= Activity.groupActivity(RTSensor_DF , DrillActivityList='default')
    ActivitySummary_DF = Activity.cleanFalseSensor(ActivitySummary_DF)
    ActivitySummary_DF = Activity.getStandLabel(ActivitySummary_DF)
    df_list.append(ActivitySummary_DF)

    IO_Data.DomeDeleteActivitySummaryData(UserDateRange_Sync, WellInfoDict)
    IO_Data.DomeInsertActivitySummaryData(WellInfoDict, ActivitySummary_DF )
    output_dict = {"Last Data":ActivitySummary_DF.tail(1).astype(str).to_dict()}
    

    return JSONResponse(status_code=200, content=output_dict)




    # Your logic here
    return WellInfoDict

class RecalculateDataRequest(BaseModel):
    wid: int
    cid: int
    startdatetime: str
    enddatetime: str
@app.post("/recalculate-activity-summary-data/")
def recalculate_data(data: RecalculateDataRequest):
    wid = data.wid
    cid = data.cid
    startdatetime = data.startdatetime
    enddatetime = data.enddatetime
    WellInfoDict = IO_Data.getWellInfoDict_byID(cid, wid)

    # TODO redefine the startdatetime and enddatetime readjustment
    Override.DomeUpdateRealtimeData(WellInfoDict, startdatetime, enddatetime) 


### Visualization API
class VisualDataModel(BaseModel):
    wid: int
    cid: int
    start_time: str
    end_time: str

@app.get("/get-activity-duration/")
def get_activity_duration(wid: int = Query(None, title="wid"), 
               cid: int = Query(None, title="cid"), 
               StartDateTime: str = Query(None, title="StartDateTime"),
               EndDateTime: str = Query(None, title="EndDateTime"),
               ActivityType: Literal["activity", "subactivity"] = Query(None, title="type"),
               ):

    if ActivityType == "activity":
        ColumnName = 'LABEL_Activity'
    elif ActivityType == "subactivity":
        ColumnName = 'LABEL_SubActivity'
    UserDateRange = {
    "StartDateTime": datetime.datetime.strptime(StartDateTime, '%Y-%m-%d %H:%M:%S'),
    "EndDateTime": datetime.datetime.strptime(EndDateTime, '%Y-%m-%d %H:%M:%S')
    }
    UserDateRange['StartDate'] = UserDateRange['StartDateTime'].date()
    UserDateRange['StartTime'] = UserDateRange['StartDateTime'].time()
    UserDateRange['EndDate'] = UserDateRange['EndDateTime'].date()
    UserDateRange['EndTime'] = UserDateRange['EndDateTime'].time()


    WellInfoDict = IO_Data.getWellInfoDict_byID(cid, wid)
    ActSum_df = IO_Data.DomeGetActivitySummaryData(WellInfoDict, UserDateRange)
    DurationCol = 'Duration'

    ActSum_df[DurationCol] = ActSum_df[DurationCol].astype(float)
    SumDuration_DF = (ActSum_df.groupby([ColumnName])[DurationCol].sum().reset_index())
    return SumDuration_DF.to_dict(orient='records')



@app.get("/get-activity-drilling-meterage/")
def get_activity_drilling_meterage(wid: int = Query(None, title="wid"), 
               cid: int = Query(None, title="cid"), 
               StartDateTime: str = Query(None, title="StartDateTime"),
               EndDateTime: str = Query(None, title="EndDateTime"),
               ):
    UserDateRange = {
    "StartDateTime": datetime.datetime.strptime(StartDateTime, '%Y-%m-%d %H:%M:%S'),
    "EndDateTime": datetime.datetime.strptime(EndDateTime, '%Y-%m-%d %H:%M:%S')
    }
    UserDateRange['StartDate'] = UserDateRange['StartDateTime'].date()
    UserDateRange['StartTime'] = UserDateRange['StartDateTime'].time()
    UserDateRange['EndDate'] = UserDateRange['EndDateTime'].date()
    UserDateRange['EndTime'] = UserDateRange['EndDateTime'].time()
    WellInfoDict = IO_Data.getWellInfoDict_byID(cid, wid)
    ActSum_df = IO_Data.DomeGetActivitySummaryData(WellInfoDict, UserDateRange)
    ActSum_df['DrillingMeterage'] = ActSum_df['DrillingMeterage'].astype(float)
    # Group by the new 'Date' column and sum the 'DrillingMeterage'
    ActSum_df['Date'] = pd.to_datetime(ActSum_df['Date']).dt.date
    DrilingMeterage_df = ActSum_df.groupby('Date')['DrillingMeterage'].sum().reset_index()
    return DrilingMeterage_df.to_dict(orient='records')

@app.get("/get-activity-rop-per-stand/")
def get_activity_rop_per_stand(wid: int = Query(None, title="wid"), 
               cid: int = Query(None, title="cid"), 
               StartDateTime: str = Query(None, title="StartDateTime"),
               EndDateTime: str = Query(None, title="EndDateTime"),
               ):
    UserDateRange = {
    "StartDateTime": datetime.datetime.strptime(StartDateTime, '%Y-%m-%d %H:%M:%S'),
    "EndDateTime": datetime.datetime.strptime(EndDateTime, '%Y-%m-%d %H:%M:%S')
    }
    UserDateRange['StartDate'] = UserDateRange['StartDateTime'].date()
    UserDateRange['StartTime'] = UserDateRange['StartDateTime'].time()
    UserDateRange['EndDate'] = UserDateRange['EndDateTime'].date()
    UserDateRange['EndTime'] = UserDateRange['EndDateTime'].time()
    WellInfoDict = IO_Data.getWellInfoDict_byID(cid, wid)
    ROP_df = IO_Data.DomeGetActivitySummaryData(WellInfoDict, UserDateRange)
    ROP_df['StartDateTime'] = pd.to_datetime(ROP_df['StartDateTime'])
    ROP_df['EndDateTime'] = pd.to_datetime(ROP_df['EndDateTime'])
    ROP_df[['DrillingMeteragePerStand', 'OnBottomDurationPerStand', 'StandDuration']] = ROP_df[['DrillingMeteragePerStand', 'OnBottomDurationPerStand', 'StandDuration']].astype(float)
    # Calculate MidDateTime as the average of StartDateTime and EndDateTime
    ROP_df['MidDateTime'] = ROP_df['StartDateTime'] + (ROP_df['EndDateTime'] - ROP_df['StartDateTime']) / 2

    idx_logic = (ROP_df['LABEL_Activity'].isin(["DRILLING FORMATION", 'CIRCULATE HOLE CLEANING','DRILL OUT CEMENT',])) & (ROP_df['LABEL_SubActivity'] == 'Connection')


    ROP_df = ROP_df[idx_logic]

    ROP_df['ROP_OnBottom'] = ROP_df['DrillingMeteragePerStand'] / (ROP_df['OnBottomDurationPerStand']/60)
    ROP_df['ROP_Stand'] = ROP_df['DrillingMeteragePerStand'] / (ROP_df['StandDuration']/60)
    ROP_df.replace([np.inf, -np.inf], np.nan, inplace=True)
    ROP_df['ROP_OnBottom'].fillna(0, inplace=True)
    ROP_df['ROP_Stand'].fillna(0, inplace=True)
    # ROP_df.fillna('', inplace=True)

    # display(ROP_df[['MidDateTime', 'LABEL_SubActivity', 'LABEL_Activity', 'DrillingMeteragePerStand', 'OnBottomDurationPerStand', 'StandDuration', 'ROP_OnBottom', 'ROP_Stand']])
    # ROP stand m/hr 



    # Assuming your DataFrame is named df and contains columns 'ROP_OnBottom', 'ROP_Stand', and 'DateTime'
    # First, convert your 'DateTime' column to a datetime type if it's not already
    # df = pd.DataFrame(ROP_df[['MidDateTime', 'LABEL_SubActivity', 'LABEL_Activity', 'DrillingMeteragePerStand', 'OnBottomDurationPerStand', 'StandDuration', 'ROP_OnBottom', 'ROP_Stand']])
    df = pd.DataFrame(ROP_df)
    if df.empty:
        raise HTTPException(
            status_code=404,
            detail={"error": "No Drilling available", "item_id": {'wid':wid, 'cid':cid}}
        )
    else:
        return df.to_dict(orient='records')


@app.get("/get-activity-stand-time/")
def get_activity_stand_time(wid: int = Query(None, title="wid"), 
               cid: int = Query(None, title="cid"), 
               StartDateTime: str = Query(None, title="StartDateTime"),
               EndDateTime: str = Query(None, title="EndDateTime"),
               ):
    UserDateRange = {
    "StartDateTime": datetime.datetime.strptime(StartDateTime, '%Y-%m-%d %H:%M:%S'),
    "EndDateTime": datetime.datetime.strptime(EndDateTime, '%Y-%m-%d %H:%M:%S')
    }
    UserDateRange['StartDate'] = UserDateRange['StartDateTime'].date()
    UserDateRange['StartTime'] = UserDateRange['StartDateTime'].time()
    UserDateRange['EndDate'] = UserDateRange['EndDateTime'].date()
    UserDateRange['EndTime'] = UserDateRange['EndDateTime'].time()
    WellInfoDict = IO_Data.getWellInfoDict_byID(cid, wid)
    StandTime_df = IO_Data.DomeGetActivitySummaryData(WellInfoDict, UserDateRange)
    StandTime_df[['RotateDrillingDuration', 'SlideDrillingDuration', 'ReamingDuration', 'ConnectionDuration']] = StandTime_df[['RotateDrillingDuration', 'SlideDrillingDuration', 'ReamingDuration', 'ConnectionDuration']].astype(float)
    StandTime_df = StandTime_df[ StandTime_df['Stand Group_Pred'].str.contains(r'Drilling', case=False, na=False)]
    StandTime_df = StandTime_df.groupby('Stand Group_Pred').agg({
        'RotateDrillingDuration': 'sum',
        'SlideDrillingDuration': 'sum',
        'ReamingDuration': 'sum',
        'ConnectionDuration': 'sum',
        'EndDateTime': 'max'
    })
    return StandTime_df.to_dict(orient='records')



@app.get("/get-casing-trip-time/")
def get_casing_trip_time(wid: int = Query(None, title="wid"), 
               cid: int = Query(None, title="cid"), 
               StartDateTime: str = Query(None, title="StartDateTime"),
               EndDateTime: str = Query(None, title="EndDateTime"),
               ):
    UserDateRange = {
    "StartDateTime": datetime.datetime.strptime(StartDateTime, '%Y-%m-%d %H:%M:%S'),
    "EndDateTime": datetime.datetime.strptime(EndDateTime, '%Y-%m-%d %H:%M:%S')
    }
    UserDateRange['StartDate'] = UserDateRange['StartDateTime'].date()
    UserDateRange['StartTime'] = UserDateRange['StartDateTime'].time()
    UserDateRange['EndDate'] = UserDateRange['EndDateTime'].date()
    UserDateRange['EndTime'] = UserDateRange['EndDateTime'].time()
    WellInfoDict = IO_Data.getWellInfoDict_byID(cid, wid)
    CasingTrip_df = IO_Data.DomeGetActivitySummaryData(WellInfoDict, UserDateRange)

    if ("TRIP IN" in CasingTrip_df['LABEL_Activity'].unique()) or ("TRIP OUT" in CasingTrip_df['LABEL_Activity'].unique()):
        CasingTrip_df = CasingTrip_df[CasingTrip_df['LABEL_Activity'].isin(['TRIP IN', 'TRIP OUT'])]
        CasingTrip_df = CasingTrip_df.reset_index(drop=True)
        CasingTrip_df['Stand Group_Pred_TRIP'] = None

        # Step 2: Find indices where the activity is 'Connection'
        if 'Connection' in CasingTrip_df['LABEL_SubActivity'].unique():
            connection_indices = CasingTrip_df[CasingTrip_df['LABEL_SubActivity'] == 'Connection'].index.tolist()
            CasingTrip_df['StartDateTime'] = pd.to_datetime((CasingTrip_df['StartDateTime']))
            CasingTrip_df['EndDateTime'] = pd.to_datetime((CasingTrip_df['EndDateTime']))
            segments_start_list = []
            segments_end_list = []

            for i,indices in enumerate(connection_indices):
                if i == 0:
                    segments_start_list.append(0)
                    segments_end_list.append(indices)
                else:
                    segments_start_list.append(connection_indices[i-1]+1)
                    segments_end_list.append(indices)

            for segments_start,segments_end, connection_idx in zip(segments_start_list, segments_end_list, connection_indices):
                ReferenceTime = CasingTrip_df.loc[connection_idx, 'StartDateTime']
                CasingTrip_df.loc[segments_start:segments_end, 'Stand Group_Pred_TRIP'] = int(CasingTrip_df.loc[connection_idx,'StartDateTime'].timestamp())
                CasingTrip_df.loc[segments_start:segments_end, 'Stand Group_Pred_TRIP'] = "Joint-" + CasingTrip_df.loc[segments_start:segments_end, 'Stand Group_Pred_TRIP'].astype(str)

            CasingTrip_df = CasingTrip_df.dropna(subset = ['Stand Group_Pred_TRIP'])
            FinalCasingTrip_df = CasingTrip_df[["Stand Group_Pred_TRIP", "LABEL_SubActivity", "Duration", "StartDateTime"]]
            FinalCasingTrip_df = FinalCasingTrip_df.groupby("Stand Group_Pred_TRIP", as_index=False).agg(
                    Duration=("Duration", "sum"),
                    StartDateTime=("StartDateTime", "first")
                )

            FinalCasingTrip_df.drop_duplicates(subset=['StartDateTime'], keep='first', inplace=True)
            FinalCasingTrip_df['StartDateTime'] = pd.to_datetime(FinalCasingTrip_df['StartDateTime'])
            FinalCasingTrip_df['Duration_Hours'] = FinalCasingTrip_df['Duration'] / 60
            FinalCasingTrip_df['Joint Per Hour'] = 1/FinalCasingTrip_df['Duration_Hours']
            return FinalCasingTrip_df.to_dict(orient='records')
        else:
            raise HTTPException(
                status_code=404,
                detail={"error": "No Detail Casing Trip were defined, please check the Activity Summary Table Definition", "item_id": {'wid':wid, 'cid':cid}}
            )
    else:
        raise HTTPException(
            status_code=404,
            detail={"error": "No Trip Activity in this time range ", "item_id": {'wid':wid, 'cid':cid}}
        )


@app.get("/get-bitdepth-vs-time")
def get_bitdepth_vs_time(wid: int = Query(None, title="wid"), 
               cid: int = Query(None, title="cid"), 
               StartDateTime: str = Query(None, title="StartDateTime"),
               EndDateTime: str = Query(None, title="EndDateTime"),
               ):
    UserDateRange = {
    "StartDateTime": datetime.datetime.strptime(StartDateTime, '%Y-%m-%d %H:%M:%S'),
    "EndDateTime": datetime.datetime.strptime(EndDateTime, '%Y-%m-%d %H:%M:%S')
    }
    UserDateRange['StartDate'] = UserDateRange['StartDateTime'].date()
    UserDateRange['StartTime'] = UserDateRange['StartDateTime'].time()
    UserDateRange['EndDate'] = UserDateRange['EndDateTime'].date()
    UserDateRange['EndTime'] = UserDateRange['EndDateTime'].time()
    WellInfoDict = IO_Data.getWellInfoDict_byID(cid, wid)
    BitDepthTime_df = IO_Data.DomeGetActivitySummaryData(WellInfoDict, UserDateRange)
    BitDepthTime_df = BitDepthTime_df[['StartDateTime', 'EndDateTime', 'Bit_Depth_avg', 'LABEL_Activity', 'LABEL_SubActivity', ]]
    return BitDepthTime_df.to_dict(orient='records')

@app.get("/get-casing-trip-breakdown-time/")
def get_casing_trip_breakdown_time(wid: int = Query(None, title="wid"), 
               cid: int = Query(None, title="cid"), 
               StartDateTime: str = Query(None, title="StartDateTime"),
               EndDateTime: str = Query(None, title="EndDateTime"),
               ):
    UserDateRange = {
    "StartDateTime": datetime.datetime.strptime(StartDateTime, '%Y-%m-%d %H:%M:%S'),
    "EndDateTime": datetime.datetime.strptime(EndDateTime, '%Y-%m-%d %H:%M:%S')
    }
    UserDateRange['StartDate'] = UserDateRange['StartDateTime'].date()
    UserDateRange['StartTime'] = UserDateRange['StartDateTime'].time()
    UserDateRange['EndDate'] = UserDateRange['EndDateTime'].date()
    UserDateRange['EndTime'] = UserDateRange['EndDateTime'].time()
    WellInfoDict = IO_Data.getWellInfoDict_byID(cid, wid)
    CasingTrip_df = IO_Data.DomeGetActivitySummaryData(WellInfoDict, UserDateRange)
    CasingTrip_df = CasingTrip_df[CasingTrip_df['LABEL_Activity'].isin(['TRIP IN', 'TRIP OUT'])]
    CasingTrip_df = CasingTrip_df.reset_index(drop=True)
    CasingTrip_df['Stand Group_Pred_TRIP'] = None
    # Step 2: Find indices where the activity is 'Connection'
    connection_indices = CasingTrip_df[CasingTrip_df['LABEL_SubActivity'] == 'Connection'].index.tolist()
    CasingTrip_df['StartDateTime'] = pd.to_datetime((CasingTrip_df['StartDateTime']))
    CasingTrip_df['EndDateTime'] = pd.to_datetime((CasingTrip_df['EndDateTime']))
    segments_start_list = []
    segments_end_list = []

    for i,indices in enumerate(connection_indices):
        if i == 0:
            segments_start_list.append(0)
            segments_end_list.append(indices)
        else:
            segments_start_list.append(connection_indices[i-1]+1)
            segments_end_list.append(indices)

    for segments_start,segments_end, connection_idx in zip(segments_start_list, segments_end_list, connection_indices):
        ReferenceTime = CasingTrip_df.loc[connection_idx, 'StartDateTime']
        CasingTrip_df.loc[segments_start:segments_end, 'Stand Group_Pred_TRIP'] = int(CasingTrip_df.loc[connection_idx,'StartDateTime'].timestamp())
        CasingTrip_df.loc[segments_start:segments_end, 'Stand Group_Pred_TRIP'] = "Joint-" + CasingTrip_df.loc[segments_start:segments_end, 'Stand Group_Pred_TRIP'].astype(str)

    CasingTrip_df = CasingTrip_df.dropna(subset = ['Stand Group_Pred_TRIP'])
    FinalCasingTripBreakdown_df = CasingTrip_df[["Stand Group_Pred_TRIP", "LABEL_SubActivity", "Duration", "StartDateTime"]]
    FinalCasingTripBreakdown_df = FinalCasingTripBreakdown_df.groupby(["Stand Group_Pred_TRIP", "LABEL_SubActivity"], as_index=False).agg(
            Duration=("Duration", "sum"),
            StartDateTime=("StartDateTime", "first")
        )
    # FinalCasingTripBreakdown_df
    return FinalCasingTripBreakdown_df.to_dict(orient='records')

@app.get("/get-activity-bha-trip-breakdown/")
def get_BHA_trip_breakdown(wid: int = Query(None, title="wid"), 
               cid: int = Query(None, title="cid"), 
               StartDateTime: str = Query(None, title="StartDateTime"),
               EndDateTime: str = Query(None, title="EndDateTime"),
               ):
    UserDateRange = {
    "StartDateTime": datetime.datetime.strptime(StartDateTime, '%Y-%m-%d %H:%M:%S'),
    "EndDateTime": datetime.datetime.strptime(EndDateTime, '%Y-%m-%d %H:%M:%S')
    }
    UserDateRange['StartDate'] = UserDateRange['StartDateTime'].date()
    UserDateRange['StartTime'] = UserDateRange['StartDateTime'].time()
    UserDateRange['EndDate'] = UserDateRange['EndDateTime'].date()
    UserDateRange['EndTime'] = UserDateRange['EndDateTime'].time()
    WellInfoDict = IO_Data.getWellInfoDict_byID(cid, wid)
    BHA_Trip_df = IO_Data.DomeGetActivitySummaryData(WellInfoDict, UserDateRange)
    BHA_Trip_df = BHA_Trip_df[BHA_Trip_df['LABEL_SubActivity'].str.contains(r'BHA|N/D|N/U BOP', case=False, na=False)]
    BHA_Trip_df['StartDateTime'] = pd.to_datetime(BHA_Trip_df['StartDateTime'])
    BHA_Trip_df['EndDateTime'] = pd.to_datetime(BHA_Trip_df['EndDateTime'])
    BHA_Trip_df['Duration'] = BHA_Trip_df['Duration'].astype(float)
    return BHA_Trip_df.to_dict(orient='records')

@app.get("/get_connection_time/")
def get_connection_time(wid: int = Query(None, title="wid"), 
               cid: int = Query(None, title="cid"), 
               StartDateTime: str = Query(None, title="StartDateTime"),
               EndDateTime: str = Query(None, title="EndDateTime"),
               ):
    UserDateRange = {
    "StartDateTime": datetime.datetime.strptime(StartDateTime, '%Y-%m-%d %H:%M:%S'),
    "EndDateTime": datetime.datetime.strptime(EndDateTime, '%Y-%m-%d %H:%M:%S')
    }
    UserDateRange['StartDate'] = UserDateRange['StartDateTime'].date()
    UserDateRange['StartTime'] = UserDateRange['StartDateTime'].time()
    UserDateRange['EndDate'] = UserDateRange['EndDateTime'].date()
    UserDateRange['EndTime'] = UserDateRange['EndDateTime'].time()
    WellInfoDict = IO_Data.getWellInfoDict_byID(cid, wid)
    ConnectionTime_df = IO_Data.DomeGetActivitySummaryData(WellInfoDict, UserDateRange)
    # print(ConnectionTime_df['LABEL_ConnectionActivity'].to_csv("Connection.csv"))
    if ConnectionTime_df['LABEL_ConnectionActivity'].isnull().any():
        raise HTTPException(
            status_code=404,
            detail={"error": "No data available", "item_id": {'wid':wid, 'cid':cid}}
        )
    if ConnectionTime_df['LABEL_ConnectionActivity'] is None:
        raise HTTPException(
            status_code=404,
            detail={"error": "No data available", "item_id": {'wid':wid, 'cid':cid}}
        )

    if (ConnectionTime_df['LABEL_ConnectionActivity'] == '').all():
        raise HTTPException(
            status_code=404,
            detail={"error": "No data available", "item_id": {'wid':wid, 'cid':cid}}
        )

    ConnectionTime_df[['ConnectionCategory', 'ConnectionID']] = ConnectionTime_df['LABEL_ConnectionActivity'].str.split('-', expand=True)
    ConnectionTime_df['StartDateTime'] = pd.to_datetime(ConnectionTime_df['StartDateTime'])
    ConnectionTime_df['EndDateTime'] = pd.to_datetime(ConnectionTime_df['EndDateTime'])
    ConnectionTime_df['Duration'] =ConnectionTime_df['Duration'].astype(float)

    ConnectionTime_agg_df = ConnectionTime_df.groupby(['ConnectionID', 'ConnectionCategory']).agg(
        Total_Duration=('Duration', 'sum'),
        First_StartDatetime=('StartDateTime', 'min'),
        Latest_EndDatetime=('EndDateTime', 'max')
    ).reset_index()
    # Pivot the data to match the requested output format
    ConnectionTime_pivot_df = ConnectionTime_agg_df.pivot(index='ConnectionID', columns='ConnectionCategory', values='Total_Duration').reset_index()
    
    # Renaming columns to match the desired output
    ConnectionTime_pivot_df = ConnectionTime_pivot_df.rename(columns={
        'Connection': 'ConnectionDuration', 
        'Post Connection': 'PostConnectionDuration', 
        'Pre Connection': 'PreConnectionDuration'
    })
    ConnectionTime_pivot_df = ConnectionTime_pivot_df.fillna(0)
    # Merge with the original DataFrame to get the StartDatetime and EndDatetime
    start_end_times = ConnectionTime_df.groupby('ConnectionID').agg(
        StartDatetime=('StartDateTime', 'min'),
        EndDatetime=('EndDateTime', 'max')
    ).reset_index()

    # Merging the pivoted DataFrame with the start and end times
    # print(ConnectionTime_pivot_df)
    for col in ['ConnectionDuration', 'PostConnectionDuration', 'PreConnectionDuration']:
        ConnectionTime_pivot_df[col] = ConnectionTime_pivot_df[col].astype(float)
    ConnectionTime_pivot_df = pd.merge(ConnectionTime_pivot_df, start_end_times, on='ConnectionID')
    # for col in ['StartDateTime', 'EndDateTime']:
    #     ConnectionTime_pivot_df[col] = pd.to_datetime(ConnectionTime_pivot_df[col])
    ConnectionTime_pivot_df['ConnectionID'] = ConnectionTime_pivot_df['ConnectionID'].astype(int)


    return ConnectionTime_pivot_df.to_dict(orient='records')

### Automatic API Update API
@app.get("/update-data/",response_class=HTMLResponse)
def UpdateRealtimeData(wid: int = Query(None, title="wid"), 
               cid: int = Query(None, title="cid"), 
               sync_datetime: str = Query(None, title="sync_datetime")):

    # WellInfoDict = {
    # "cid": cid,
    # "wid": wid,
    # }
    WellInfoDict = IO_Data.getWellInfoDict_byID(cid, wid)
    reload(Activity)

    # SectionParams_DF = pd.read_excel('Data/SectionParams.xlsx')
    SectionParams_DF = IO_Data.DomeSectionParamsTable_Get(WellInfoDict)
    if SectionParams_DF.empty:
        return JSONResponse(
            status_code=404,
            content={"detail": "inslip threshold not set"}
        )
    df_list = []
    # LastDateTime_obj = datetime.datetime.strptime(sync_datetime, '%Y-%m-%d %H:%M:%S')
    try:
        LastDateTime_obj = datetime.datetime.strptime(sync_datetime, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid sync_datetime format. Please use 'YYYY-MM-DD HH:MM:SS'.")
    UserDateRange_Sync = {
    "StartDate": datetime.date(2000, 4, 9),
    "StartTime": datetime.time(00, 00),
    "EndDate": LastDateTime_obj.date(),
    "EndTime": LastDateTime_obj.time()
    }

    df_list.append(pd.DataFrame.from_records([UserDateRange_Sync]))
    # display(UserDateRange_Sync)
    StartDateTime = IO_Data.getLastActSum(WellInfoDict, UserDateRange_Sync, DrillActivityList='default')['StartDateTime']
    StartDateTime_obj = datetime.datetime.strptime(StartDateTime.values[0], '%Y-%m-%d %H:%M:%S')

    UserDateRange_Sync = {
    "StartDate": StartDateTime_obj.date(),
    "StartTime": StartDateTime_obj.time(),
    "EndDate": LastDateTime_obj.date(),
    "EndTime": LastDateTime_obj.time()
    }
    print(f"request realtime data {UserDateRange_Sync}")
    df_list.append(pd.DataFrame.from_records([UserDateRange_Sync]))
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
    ActivitySummary_DF= Activity.groupActivity(RTSensor_DF , DrillActivityList='default')
    ActivitySummary_DF = Activity.cleanFalseSensor(ActivitySummary_DF)
    ActivitySummary_DF = Activity.getStandLabel(ActivitySummary_DF)
    df_list.append(ActivitySummary_DF)

    IO_Data.DomeDeleteActivitySummaryData(UserDateRange_Sync, WellInfoDict)
    IO_Data.DomeInsertActivitySummaryData(WellInfoDict, ActivitySummary_DF )
    

    # Convert the DataFrame to HTML
    html_content = getHTML_Table(df_list)
    
    return HTMLResponse(content=html_content)

@app.get("/hello/",response_class=HTMLResponse)
def hello_func():
    return "Hello"



### Override Activity Table API

class Insert_OverrideActivityDataModel(BaseModel):
    # Define the structure of your JSON data here
    # For example:
    wid: int
    StartDateTime: str
    EndDateTime : str
    LABEL_ACTIVITY : str
    LABEL_SUBACTIVITY : str
    PIC : str
class Get_OverrideActivityDataModel(BaseModel):
    wid:int
    cid:int

class Delete_OverrideActivityDataModel(BaseModel):
    wid:int
    StartDateTime: str
    EndDateTime : str



def convert_datetime_column(df, column_list, datetime_format = "%Y-%m-%dT%H:%M:%S.%f"):
    for column_name in column_list:
        try:
            # Convert the column to datetime using the provided format
            df[column_name] = pd.to_datetime(df[column_name], format=datetime_format)
            # Reformat the datetime to the desired string format
            df[column_name] = df[column_name].dt.strftime("%Y-%m-%d %H:%M:%S")
            
        except:
            pass
    return df
        # print(f"An error occurred: {e}")


@app.post("/override-activity-table/insert/")
def override_activity_insert(data: Insert_OverrideActivityDataModel):
    OverrideActivity_df = pd.read_parquet('Data/OverrideActivity_TABLE.parquet')
    OverrideActivity_df = convert_datetime_column(OverrideActivity_df, ['StartDateTime', 'EndDateTime'])
    insert_df = pd.DataFrame.from_records([data.model_dump()])
    insert_df = convert_datetime_column(insert_df, ['StartDateTime', 'EndDateTime'])

    OverrideActivity_df = pd.concat([OverrideActivity_df,insert_df], ignore_index=True)

    OverrideActivity_df.to_parquet('Data/OverrideActivity_TABLE.parquet', index=False)
    return {"message": "Data inserted successfully"}

@app.post("/override-activity-table/delete/")
def override_activity_delete(data: Delete_OverrideActivityDataModel):
    # Load the DataFrame
    DeleteDict = data.model_dump()
    try:
        OverrideActivity_df = pd.read_parquet('Data/OverrideActivity_TABLE.parquet')
        # Filtering condition
        condition = (OverrideActivity_df['wid'] == DeleteDict['wid']) & \
                    (OverrideActivity_df['StartDateTime'] == DeleteDict['StartDateTime']) & \
                    (OverrideActivity_df['EndDateTime'] == DeleteDict['EndDateTime'])

        # Remove the row(s) by inverting the condition
        OverrideActivity_df = OverrideActivity_df[~condition]

        # Save the DataFrame back to parquet
        OverrideActivity_df.to_parquet('Data/OverrideActivity_TABLE.parquet', index=False)
        return {"message": "Data deleted successfully"}
    except:
        raise HTTPException(status_code=404, detail="data not found")


@app.post("/override-activity-table/get/")
def override_activity_get(data: Get_OverrideActivityDataModel):
    list_col_str = 'StartDateTime'
    WellInfoDict = data.model_dump()
    OverrideActivity_df = pd.read_parquet('Data/OverrideActivity_TABLE.parquet')
    OverrideActivity_df = OverrideActivity_df[OverrideActivity_df['wid'] == WellInfoDict['wid']]
    if OverrideActivity_df.empty:
        empty_data = {col: [] for col in ['wid', 'StartDateTime', 'EndDateTime', 'LABEL_ACTIVITY', 'LABEL_SUBACTIVITY', 'PIC']}
        return empty_data
    return OverrideActivity_df.to_dict(orient='records')



### Section Params Table API
class Insert_SectionParamsDataModel(BaseModel):
    # Define the structure of your JSON data here
    # For example:
    wid: int
    DateTime : str
    SectionSize : str
    InSlipThreshold : float
    PIC : str
class Get_SectionParamsDataModel(BaseModel):
    wid:int
    cid:int
class Delete_SectionParamsDataModel(BaseModel):
    wid: int
    DateTime : str
    SectionSize : str
    InSlipThreshold : float
    PIC : str

@app.post("/section-params-table/insert/")
def section_params_insert(data: Insert_SectionParamsDataModel):
    SectionParams_df = pd.read_parquet('Data/SectionParams_TABLE.parquet')
    SectionParams_df = convert_datetime_column(SectionParams_df, ['StartDateTime', 'EndDateTime'])
    insert_df = pd.DataFrame.from_records([data.model_dump()])
    insert_df = convert_datetime_column(insert_df, ['StartDateTime', 'EndDateTime'])
    
    SectionParams_df = pd.concat([SectionParams_df,insert_df], ignore_index=True)
    SectionParams_df.to_parquet('Data/SectionParams_TABLE.parquet', index=False)
    return {"message": "Data inserted successfully"}

@app.post("/section-params-table/delete/")
def section_params_delete(data: Delete_SectionParamsDataModel):
    # Load the DataFrame
    DeleteDict = data.model_dump()
    try:
        SectionParams_df = pd.read_parquet('Data/SectionParams_TABLE.parquet')
        # Filtering condition
        condition = (SectionParams_df['wid'] == DeleteDict['wid']) & \
                    (SectionParams_df['DateTime'] == DeleteDict['DateTime']) & \
                    (SectionParams_df['SectionSize'] == DeleteDict['SectionSize']) & \
                    (SectionParams_df['InSlipThreshold'] == DeleteDict['InSlipThreshold']) & \
                    (SectionParams_df['PIC'] == DeleteDict['PIC'])

        # Remove the row(s) by inverting the condition
        SectionParams_df = SectionParams_df[~condition]

        # Save the DataFrame back to parquet
        SectionParams_df.to_parquet('Data/SectionParams_TABLE.parquet', index=False)
        return {"message": "Data deleted successfully"}
    except:
        raise HTTPException(status_code=404, detail="data not found")
@app.post("/section-params-table/get/")
def section_params_get(data: Get_SectionParamsDataModel):
    list_col_str = 'DateTime'
    WellInfoDict = data.model_dump()
    SectionParams_df = pd.read_parquet('Data/SectionParams_TABLE.parquet')
    SectionParams_df = SectionParams_df[SectionParams_df['wid'] == WellInfoDict['wid']]
    if SectionParams_df.empty:
        empty_data = {col: [] for col in ['wid', 'DateTime', 'SectionSize', 'InSlipThreshold',  'PIC']}
        return empty_data
    return SectionParams_df.to_dict(orient='records')

@app.get("/get_company/")
def getAvailableCompanyDF():
    url_pdu_api = getURLAPI_pdu()
    GetCompAPI = f"{url_pdu_api}rtdc/get_company/" 
    CompName_JSON = requests.get(GetCompAPI).json()  
    return CompName_JSON


@app.get("/get_well/")
def getAvailableWellDF(cid: int):
    url_pdu_api = getURLAPI_pdu()
    GetAvailableWellAPI =  f"{url_pdu_api}rtdc/get_well?cid=" + str(cid)
    AvailableWell_JSON = requests.get(GetAvailableWellAPI).json()
    return AvailableWell_JSON

@app.post("/ActivitySummary/delete/")
def deleteActivitySummary(wid: int, ID_or_timestart:str):
    print(ID_or_timestart)
    url_pdu_api = getURLAPI_pdu()
    TableAPI = f"{url_pdu_api}rtdc/ActivitySummary/delete"
    response = (
        requests.post(
            TableAPI, 
            data=json.dumps(
                            {
                                "wid": wid,
                                "time_start":str(ID_or_timestart)
                            },
                            indent = 4
                        ) 
            )
    )
    return response
#########################################################################################
################################ Version 2 ##############################################
#########################################################################################

@app.get("/v2/get-remarks/")
def v2_get_remarks(wid: int = Query(None, title="wid"), 
               cid: int = Query(None, title="cid"), 
               StartDateTime: str = Query(None, title="StartDateTime"),
               EndDateTime: str = Query(None, title="EndDateTime"),
               ):
    UserDateRange = {
    "StartDateTime": datetime.datetime.strptime(StartDateTime, '%Y-%m-%d %H:%M:%S'),
    "EndDateTime": datetime.datetime.strptime(EndDateTime, '%Y-%m-%d %H:%M:%S')
    }
    UserDateRange['StartDate'] = UserDateRange['StartDateTime'].date()
    UserDateRange['StartTime'] = UserDateRange['StartDateTime'].time()
    UserDateRange['EndDate'] = UserDateRange['EndDateTime'].date()
    UserDateRange['EndTime'] = UserDateRange['EndDateTime'].time()
    WellInfoDict = IO_Data.getWellInfoDict_byID(cid, wid)
    Remarks_df = IO_Data.DomeGetActivitySummaryData(WellInfoDict, UserDateRange)
    Remarks_df = Activity.getRemarks(Remarks_df)
    if Remarks_df.empty:
        raise HTTPException(
            status_code=404,
            detail={"error": "No Remarks available", "item_id": {'wid':wid, 'cid':cid}}
        )
    return Remarks_df.astype(str).to_dict(orient='records')


@app.get("/v2/get-activity-duration/")
def v2_get_activity_duration(wid: int = Query(None, title="wid"), 
               cid: int = Query(None, title="cid"), 
               StartDateTime: str = Query(None, title="StartDateTime"),
               EndDateTime: str = Query(None, title="EndDateTime"),
               ActivityType: Literal["activity", "subactivity"] = Query(None, title="type"),
               ):

    if ActivityType == "activity":
        ColumnName = 'LABEL_Activity'
    elif ActivityType == "subactivity":
        ColumnName = 'LABEL_SubActivity'
    UserDateRange = {
    "StartDateTime": datetime.datetime.strptime(StartDateTime, '%Y-%m-%d %H:%M:%S'),
    "EndDateTime": datetime.datetime.strptime(EndDateTime, '%Y-%m-%d %H:%M:%S')
    }
    UserDateRange['StartDate'] = UserDateRange['StartDateTime'].date()
    UserDateRange['StartTime'] = UserDateRange['StartDateTime'].time()
    UserDateRange['EndDate'] = UserDateRange['EndDateTime'].date()
    UserDateRange['EndTime'] = UserDateRange['EndDateTime'].time()


    WellInfoDict = IO_Data.getWellInfoDict_byID(cid, wid)
    ActSum_df = IO_Data.DomeGetActivitySummaryData(WellInfoDict, UserDateRange)
    DurationCol = 'Duration'

    ActSum_df[DurationCol] = ActSum_df[DurationCol].astype(float)
    SumDuration_DF = (ActSum_df.groupby([ColumnName])[DurationCol].sum().reset_index())
    if SumDuration_DF.empty:
        raise HTTPException(
            status_code=404,
            detail={"error": "No Activity available", "item_id": {'wid':wid, 'cid':cid}}
        )
    return SumDuration_DF.astype(str).to_dict(orient='records')


@app.get("/v2/get-activity-drilling-meterage/")
def v2_get_activity_drilling_meterage(wid: int = Query(None, title="wid"), 
               cid: int = Query(None, title="cid"), 
               StartDateTime: str = Query(None, title="StartDateTime"),
               EndDateTime: str = Query(None, title="EndDateTime"),
               ):
    UserDateRange = {
    "StartDateTime": datetime.datetime.strptime(StartDateTime, '%Y-%m-%d %H:%M:%S'),
    "EndDateTime": datetime.datetime.strptime(EndDateTime, '%Y-%m-%d %H:%M:%S')
    }
    UserDateRange['StartDate'] = UserDateRange['StartDateTime'].date()
    UserDateRange['StartTime'] = UserDateRange['StartDateTime'].time()
    UserDateRange['EndDate'] = UserDateRange['EndDateTime'].date()
    UserDateRange['EndTime'] = UserDateRange['EndDateTime'].time()
    WellInfoDict = IO_Data.getWellInfoDict_byID(cid, wid)
    ActSum_df = IO_Data.DomeGetActivitySummaryData(WellInfoDict, UserDateRange)
    ActSum_df['DrillingMeterage'] = ActSum_df['DrillingMeterage'].astype(float)
    # Group by the new 'Date' column and sum the 'DrillingMeterage'
    ActSum_df['Date'] = pd.to_datetime(ActSum_df['Date']).dt.date
    DrilingMeterage_df = ActSum_df.groupby('Date')['DrillingMeterage'].sum().reset_index()
    return DrilingMeterage_df.astype(str).to_dict(orient='records')

@app.get("/v2/get-bitdepth-vs-time")
def v2_get_bitdepth_vs_time(wid: int = Query(None, title="wid"), 
               cid: int = Query(None, title="cid"), 
               StartDateTime: str = Query(None, title="StartDateTime"),
               EndDateTime: str = Query(None, title="EndDateTime"),
               ):
    UserDateRange = {
    "StartDateTime": datetime.datetime.strptime(StartDateTime, '%Y-%m-%d %H:%M:%S'),
    "EndDateTime": datetime.datetime.strptime(EndDateTime, '%Y-%m-%d %H:%M:%S')
    }
    UserDateRange['StartDate'] = UserDateRange['StartDateTime'].date()
    UserDateRange['StartTime'] = UserDateRange['StartDateTime'].time()
    UserDateRange['EndDate'] = UserDateRange['EndDateTime'].date()
    UserDateRange['EndTime'] = UserDateRange['EndDateTime'].time()
    WellInfoDict = IO_Data.getWellInfoDict_byID(cid, wid)
    BitDepthTime_df = IO_Data.DomeGetActivitySummaryData(WellInfoDict, UserDateRange)
    BitDepthTime_df = BitDepthTime_df[['StartDateTime', 'EndDateTime', 'Bit_Depth_avg', 'LABEL_Activity', 'LABEL_SubActivity', ]]
    return BitDepthTime_df.to_dict(orient='records')
@app.get("/v2/get-flattime")
def v2_get_flattime(wid: int = Query(None, title="wid"), 
               cid: int = Query(None, title="cid"), 
               StartDateTime: str = Query(None, title="StartDateTime"),
               EndDateTime: str = Query(None, title="EndDateTime"),
               ):
    UserDateRange = {
    "StartDateTime": datetime.datetime.strptime(StartDateTime, '%Y-%m-%d %H:%M:%S'),
    "EndDateTime": datetime.datetime.strptime(EndDateTime, '%Y-%m-%d %H:%M:%S')
    }
    UserDateRange['StartDate'] = UserDateRange['StartDateTime'].date()
    UserDateRange['StartTime'] = UserDateRange['StartDateTime'].time()
    UserDateRange['EndDate'] = UserDateRange['EndDateTime'].date()
    UserDateRange['EndTime'] = UserDateRange['EndDateTime'].time()
    WellInfoDict = IO_Data.getWellInfoDict_byID(cid, wid)
    FlatTime_df = IO_Data.DomeGetActivitySummaryData(WellInfoDict, UserDateRange)
    FlatTime_df = FlatTime_df[['StartDateTime', 'EndDateTime', 'Duration', 'LABEL_Activity', 'LABEL_SubActivity', ]]
    return FlatTime_df.to_dict(orient='records')


@app.get("/v2/get-activity-rop-per-stand/")
def v2_get_activity_rop_per_stand(wid: int = Query(None, title="wid"), 
               cid: int = Query(None, title="cid"), 
               StartDateTime: str = Query(None, title="StartDateTime"),
               EndDateTime: str = Query(None, title="EndDateTime"),
               ):
    UserDateRange = {
    "StartDateTime": datetime.datetime.strptime(StartDateTime, '%Y-%m-%d %H:%M:%S'),
    "EndDateTime": datetime.datetime.strptime(EndDateTime, '%Y-%m-%d %H:%M:%S')
    }
    UserDateRange['StartDate'] = UserDateRange['StartDateTime'].date()
    UserDateRange['StartTime'] = UserDateRange['StartDateTime'].time()
    UserDateRange['EndDate'] = UserDateRange['EndDateTime'].date()
    UserDateRange['EndTime'] = UserDateRange['EndDateTime'].time()
    WellInfoDict = IO_Data.getWellInfoDict_byID(cid, wid)
    ROP_df = IO_Data.DomeGetActivitySummaryData(WellInfoDict, UserDateRange)
    ROP_df = Activity.getROP_df(ROP_df)
    ROP_df.replace([np.inf, -np.inf], np.nan, inplace=True)
    ROP_df['ROP_OnBottom'].fillna(0, inplace=True)
    ROP_df['ROP_Stand'].fillna(0, inplace=True)

    df = pd.DataFrame(ROP_df)
    if df.empty:
        raise HTTPException(
            status_code=404,
            detail={"error": "No Drilling available", "item_id": {'wid':wid, 'cid':cid}}
        )
    else:
        return df.astype(str).to_dict(orient='records')

@app.get("/v2/get_connection_time/")
def v2_get_connection_time(wid: int = Query(None, title="wid"), 
               cid: int = Query(None, title="cid"), 
               StartDateTime: str = Query(None, title="StartDateTime"),
               EndDateTime: str = Query(None, title="EndDateTime"),
               ):
    UserDateRange = {
    "StartDateTime": datetime.datetime.strptime(StartDateTime, '%Y-%m-%d %H:%M:%S'),
    "EndDateTime": datetime.datetime.strptime(EndDateTime, '%Y-%m-%d %H:%M:%S')
    }
    UserDateRange['StartDate'] = UserDateRange['StartDateTime'].date()
    UserDateRange['StartTime'] = UserDateRange['StartDateTime'].time()
    UserDateRange['EndDate'] = UserDateRange['EndDateTime'].date()
    UserDateRange['EndTime'] = UserDateRange['EndDateTime'].time()
    WellInfoDict = IO_Data.getWellInfoDict_byID(cid, wid)
    ConnectionTime_df = IO_Data.DomeGetActivitySummaryData(WellInfoDict, UserDateRange)
    # print(ConnectionTime_df['LABEL_ConnectionActivity'].to_csv("Connection.csv"))
    ConnectionTime_df = Activity.getConnectionTime_df(ConnectionTime_df)
    if ConnectionTime_df.empty:
        raise HTTPException(
            status_code=404,
            detail={"error": "No Connection Time available", "item_id": {'wid':wid, 'cid':cid}})

    return ConnectionTime_df.astype(str).to_dict(orient='records')

@app.get("/v2/get-activity-stand-time/")
def v2_get_activity_stand_time(wid: int = Query(None, title="wid"), 
               cid: int = Query(None, title="cid"), 
               StartDateTime: str = Query(None, title="StartDateTime"),
               EndDateTime: str = Query(None, title="EndDateTime"),
               ):
    UserDateRange = {
    "StartDateTime": datetime.datetime.strptime(StartDateTime, '%Y-%m-%d %H:%M:%S'),
    "EndDateTime": datetime.datetime.strptime(EndDateTime, '%Y-%m-%d %H:%M:%S')
    }
    UserDateRange['StartDate'] = UserDateRange['StartDateTime'].date()
    UserDateRange['StartTime'] = UserDateRange['StartDateTime'].time()
    UserDateRange['EndDate'] = UserDateRange['EndDateTime'].date()
    UserDateRange['EndTime'] = UserDateRange['EndDateTime'].time()
    WellInfoDict = IO_Data.getWellInfoDict_byID(cid, wid)
    StandTime_df = IO_Data.DomeGetActivitySummaryData(WellInfoDict, UserDateRange)
    StandTime_df = Activity.getStandTime_df(StandTime_df)
    if StandTime_df.empty:
        raise HTTPException(
            status_code=404,
            detail={"error": "No Stand Time available", "item_id": {'wid':wid, 'cid':cid}}
        )
    return StandTime_df.astype(str).to_dict(orient='records')

@app.get("/v2/get-activity-bha-trip-breakdown/")
def v2_get_BHA_trip_breakdown(wid: int = Query(None, title="wid"), 
               cid: int = Query(None, title="cid"), 
               StartDateTime: str = Query(None, title="StartDateTime"),
               EndDateTime: str = Query(None, title="EndDateTime"),
               ):
    UserDateRange = {
    "StartDateTime": datetime.datetime.strptime(StartDateTime, '%Y-%m-%d %H:%M:%S'),
    "EndDateTime": datetime.datetime.strptime(EndDateTime, '%Y-%m-%d %H:%M:%S')
    }
    UserDateRange['StartDate'] = UserDateRange['StartDateTime'].date()
    UserDateRange['StartTime'] = UserDateRange['StartDateTime'].time()
    UserDateRange['EndDate'] = UserDateRange['EndDateTime'].date()
    UserDateRange['EndTime'] = UserDateRange['EndDateTime'].time()
    WellInfoDict = IO_Data.getWellInfoDict_byID(cid, wid)
    BHA_Trip_df = IO_Data.DomeGetActivitySummaryData(WellInfoDict, UserDateRange)
    BHA_Trip_df = Activity.getBHA_TripBreakdown_df(BHA_Trip_df)
    if BHA_Trip_df.empty:
        raise HTTPException(
            status_code=404,
            detail={"error": "No BHA Trip available", "item_id": {'wid':wid, 'cid':cid}}
        )
    return BHA_Trip_df.astype(str).to_dict(orient='records')

@app.get("/v2/get-casing-trip-time/")
def v2_get_casing_trip_time(wid: int = Query(None, title="wid"), 
               cid: int = Query(None, title="cid"), 
               StartDateTime: str = Query(None, title="StartDateTime"),
               EndDateTime: str = Query(None, title="EndDateTime"),
               ):
    UserDateRange = {
    "StartDateTime": datetime.datetime.strptime(StartDateTime, '%Y-%m-%d %H:%M:%S'),
    "EndDateTime": datetime.datetime.strptime(EndDateTime, '%Y-%m-%d %H:%M:%S')
    }
    UserDateRange['StartDate'] = UserDateRange['StartDateTime'].date()
    UserDateRange['StartTime'] = UserDateRange['StartDateTime'].time()
    UserDateRange['EndDate'] = UserDateRange['EndDateTime'].date()
    UserDateRange['EndTime'] = UserDateRange['EndDateTime'].time()
    WellInfoDict = IO_Data.getWellInfoDict_byID(cid, wid)
    CasingTrip_df = IO_Data.DomeGetActivitySummaryData(WellInfoDict, UserDateRange)
    CasingTrip_df = Activity.GroupCasingJoint(CasingTrip_df)
    CasingTrip_df = Activity.getCasingTrip_df(CasingTrip_df)
    if CasingTrip_df.empty:
        raise HTTPException(
            status_code=404,
            detail={"error": "No Casing Trip available", "item_id": {'wid':wid, 'cid':cid}}
        )
    return CasingTrip_df.astype(str).to_dict(orient='records')

@app.get("/v2/get-casing-trip-breakdown-time/")
def v2_get_casing_trip_breakdown_time(wid: int = Query(None, title="wid"), 
               cid: int = Query(None, title="cid"), 
               StartDateTime: str = Query(None, title="StartDateTime"),
               EndDateTime: str = Query(None, title="EndDateTime"),
               ):
    UserDateRange = {
    "StartDateTime": datetime.datetime.strptime(StartDateTime, '%Y-%m-%d %H:%M:%S'),
    "EndDateTime": datetime.datetime.strptime(EndDateTime, '%Y-%m-%d %H:%M:%S')
    }
    UserDateRange['StartDate'] = UserDateRange['StartDateTime'].date()
    UserDateRange['StartTime'] = UserDateRange['StartDateTime'].time()
    UserDateRange['EndDate'] = UserDateRange['EndDateTime'].date()
    UserDateRange['EndTime'] = UserDateRange['EndDateTime'].time()
    WellInfoDict = IO_Data.getWellInfoDict_byID(cid, wid)
    CasingTripBreakdown_df = IO_Data.DomeGetActivitySummaryData(WellInfoDict, UserDateRange)
    CasingTripBreakdown_df = Activity.GroupCasingJoint(CasingTripBreakdown_df)
    CasingTripBreakdown_df = Activity.getCasingTripBreakdown_df(CasingTripBreakdown_df)
    if CasingTripBreakdown_df.empty:
        raise HTTPException(
            status_code=404,
            detail={"error": "No Casing Trip Breakdown available", "item_id": {'wid':wid, 'cid':cid}}
        )


    return CasingTripBreakdown_df.astype(str).to_dict(orient='records')





