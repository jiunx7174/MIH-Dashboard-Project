from fastapi import FastAPI, HTTPException, Request,Query
from pydantic import BaseModel
from importlib import reload
import sys
import os

# Get the directory of the current file
current_dir = os.path.dirname(__file__)
# If you specifically want to use os.path.join() for clarity
up_one_folder = os.path.join(current_dir, '..')
# Normalize the path to resolve any '..'
library_path = os.path.normpath(up_one_folder)
# Add the path to sys.path
sys.path.append(library_path)

import pandas as pd
from fastapi.responses import HTMLResponse
from PDU_Func import Activity, Authentification, IO_Data
from importlib import reload
import datetime
reload(IO_Data)
reload(Activity)
app = FastAPI()

class SectionParamsDataModel(BaseModel):
    # Define the structure of your JSON data here
    # For example:
    wid: int
    DateTime : str
    SectionSize : str
    PIC : str


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

### Automatic API Update API
@app.get("/update-data/",response_class=HTMLResponse)
def UpdateRealtimeData(wid: int = Query(None, title="wid"), 
               cid: int = Query(None, title="cid"), 
               sync_datetime: str = Query(None, title="sync_datetime")):

    WellInfoDict = {
    "cid": cid,
    "wid": wid,
    }
    reload(Activity)
    # TODO change with the SectionParams Table
    SectionParams_DF = pd.read_excel('../Data/SectionParams.xlsx')
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
    df = pd.DataFrame({"Message": ["Hello World"]})
    
    # Convert the DataFrame to HTML
    html_content = df.to_html()
    
    return HTMLResponse(content=html_content)

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


@app.post("/override-activity-table/insert/")
def override_activity_insert(data: Insert_OverrideActivityDataModel):
    OverrideActivity_df = pd.read_parquet('../Data/OverrideActivity_TABLE.parquet')
    insert_df = pd.DataFrame.from_records([data.model_dump()])
    OverrideActivity_df = pd.concat([OverrideActivity_df,insert_df], ignore_index=True)
    OverrideActivity_df.to_parquet('../Data/OverrideActivity_TABLE.parquet', index=False)
    return {"message": "Data inserted successfully"}

@app.post("/override-activity-table/delete/")
def override_activity_delete(data: Delete_OverrideActivityDataModel):
    # Load the DataFrame
    DeleteDict = data.model_dump()
    try:
        OverrideActivity_df = pd.read_parquet('../Data/OverrideActivity_TABLE.parquet')
        # Filtering condition
        condition = (OverrideActivity_df['wid'] == DeleteDict['wid']) & \
                    (OverrideActivity_df['StartDateTime'] == DeleteDict['StartDateTime']) & \
                    (OverrideActivity_df['EndDateTime'] == DeleteDict['EndDateTime'])

        # Remove the row(s) by inverting the condition
        OverrideActivity_df = OverrideActivity_df[~condition]

        # Save the DataFrame back to parquet
        OverrideActivity_df.to_parquet('../Data/OverrideActivity_TABLE.parquet', index=False)
        return {"message": "Data deleted successfully"}
    except:
        raise HTTPException(status_code=404, detail="data not found")


@app.post("/override-activity-table/get/")
def override_activity_get(data: Get_OverrideActivityDataModel):
    list_col_str = 'StartDateTime'
    WellInfoDict = data.model_dump()
    OverrideActivity_df = pd.read_parquet('../Data/OverrideActivity_TABLE.parquet')
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
    SectionParams_df = pd.read_parquet('../Data/SectionParams_TABLE.parquet')
    insert_df = pd.DataFrame.from_records([data.model_dump()])
    SectionParams_df = pd.concat([SectionParams_df,insert_df], ignore_index=True)
    SectionParams_df.to_parquet('../Data/SectionParams_TABLE.parquet', index=False)
    return {"message": "Data inserted successfully"}

@app.post("/section-params-table/delete/")
def section_params_delete(data: Delete_SectionParamsDataModel):
    # Load the DataFrame
    DeleteDict = data.model_dump()
    try:
        SectionParams_df = pd.read_parquet('../Data/SectionParams_TABLE.parquet')
        # Filtering condition
        condition = (SectionParams_df['wid'] == DeleteDict['wid']) & \
                    (SectionParams_df['DateTime'] == DeleteDict['DateTime']) & \
                    (SectionParams_df['SectionSize'] == DeleteDict['SectionSize']) & \
                    (SectionParams_df['InSlipThreshold'] == DeleteDict['InSlipThreshold']) & \
                    (SectionParams_df['PIC'] == DeleteDict['PIC'])

        # Remove the row(s) by inverting the condition
        SectionParams_df = SectionParams_df[~condition]

        # Save the DataFrame back to parquet
        SectionParams_df.to_parquet('../Data/SectionParams_TABLE.parquet', index=False)
        return {"message": "Data deleted successfully"}
    except:
        raise HTTPException(status_code=404, detail="data not found")
@app.post("/section-params-table/get/")
def section_params_get(data: Get_SectionParamsDataModel):
    list_col_str = 'DateTime'
    WellInfoDict = data.model_dump()
    SectionParams_df = pd.read_parquet('../Data/SectionParams_TABLE.parquet')
    SectionParams_df = SectionParams_df[SectionParams_df['wid'] == WellInfoDict['wid']]
    if SectionParams_df.empty:
        empty_data = {col: [] for col in ['wid', 'DateTime', 'SectionSize', 'InSlipThreshold',  'PIC']}
        return empty_data
    return SectionParams_df.to_dict(orient='records')