import pandas as pd
import numpy as np  
from datetime import datetime,timedelta
# import streamlit as st


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