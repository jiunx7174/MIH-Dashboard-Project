import streamlit as st
import pandas as pd
import numpy as np
from PDU_Func import Authentification, IO_Data, Table, ActivitySummary
from streamlit_toggle import st_toggle_switch
import time
from datetime import datetime
import base64
from importlib import reload
reload(IO_Data)
reload(Table)

def uploadActivityLog(ActivityLog_DF, WellInfoDict, UserDateRange):
    with st.spinner("Uploading your Activity Log Data"):
        for i,row in ActivityLog_DF.iterrows():
            
            input_dict_temp = {
                'wid':WellInfoDict['wid'],
                'dt':str(row['Date/Time']),
                'date':str(row['Date']),
                'time':str(row['Time']),
                'activity':row['Activity'],
                'in_slip_threshold':row['In-Slip Threshold'],
                'remarks' : row['Remarks'],
                'pic' : row['PIC'],
                'section':row['Section Size']
                
            }
            st.text(input_dict_temp)
            IO_Data.DomeInsertData(input_dict_temp)

        # print(IO_Data.DomeInsertData(input_dict_temp))
def getExampleExcelFileUrl():
    file_path = "Data\\Master_Report\\KS_ORKA\\AAE-05\\Upload_AAE-05_12.25in_Rev.1.3.xlsx"
    file_url = f"<a href='data:file/txt;base64,{base64.b64encode(open(file_path,'rb').read()).decode()}' download='example.xlsx'>Download Example file</a>"
    return file_url

@st.cache_data
def cache_DomeGetData_ActivityLog(WellInfoDict, UserDateRange):
    return (IO_Data.DomeGetData(WellInfoDict, (UserDateRange), table_type="ActivityLogTable"))



# @st.cache_data
def cache_DomeGetData_ActivitySummary(WellInfoDict, UserDateRange):
    print("Get ActSum Data")
    ActSumData= ActivitySummary.ActivitySummaryTable(WellInfoDict, UserDateRange)
        
            # generate both of FIRM and REVIEW ActSum
    ActSumData.getActivitySummary_Firm()
    return ActSumData.Data
def refreshAll():
    cache_DomeGetData_ActivityLog.clear()
    if 'ActSum_df_Database' not in st.session_state:
        del st.session_state['ActSum_df_Database'] 


def App(UserAuthDict, SelectComp, SelectWell):
    UserDateRange = {
        "StartDate":datetime.strptime('31-07-1990', '%d-%m-%Y').date(),

        "StartTime":datetime.strptime('00:00', '%H:%M').time(),

        "EndDate":datetime.strptime('01-08-2100', '%d-%m-%Y').date(),
        "EndTime":datetime.strptime('23:59', '%H:%M').time(),
        }
    # UserAuthDict = Authentification.getUserID()
    # "datetime.date(2021, 7, 31)"
    # WellInfoDict = st.session_state['WellInfoDict']
    WellInfoDict = IO_Data.getWellInfoDict(UserAuthDict, SelectComp, SelectWell)
    # st.write(WellInfoDict)
    ActivityLog_DF = cache_DomeGetData_ActivityLog(WellInfoDict,UserDateRange)

    st.markdown("# RTDC Database")
    st.markdown("## Activity Log")
    st.sidebar.button("Refresh Page", key="RefreshAll", on_click=refreshAll)
    Table.ActivityLogTableDatabase_Agrid(ActivityLog_DF, reload=True,)
    # st.dataframe(ActivityLog_DF)

    


    with st.expander("Activity Log Upload"):
        st.markdown(getExampleExcelFileUrl(), unsafe_allow_html=True)
        ActivityLogUploadContainer = st.container()
        ActivityLogTableContainer = st.container()

        file = ActivityLogUploadContainer.file_uploader("Upload Activity Log Excel here", key="ActivityLogUpload")
        if file is not None:
            try:
                ActivityLog_DF_Raw=pd.read_excel(file)
                ActivityLog_DF_Raw['Remarks'].fillna("", inplace=True)
                ActivityLog_DF_Raw = ActivityLog_DF_Raw.dropna(subset=['Date'])
                # SummaryActivity_DF['Date/Time_End'] = SummaryActivity_DF['Date/Time'].shift(periods=-1)
                ActivityLog_DF = ActivityLog_DF_Raw[ActivityLog_DF_Raw['Activity'] != ActivityLog_DF_Raw['Activity'].shift(periods=1)]
                ActivityLog_DF['Activity'] = ActivityLog_DF['Activity'].str.upper()
                # ActivityLog_DF['Date'] = ActivityLog_DF['Date'].date()
                ActivityLog_DF['Date'] = pd.to_datetime(ActivityLog_DF['Date']).dt.date
                ActivityLogTableContainer.markdown("### Activity Log Table")
                # st.text(UserAuthDict)
                if not "PIC" in ActivityLog_DF.columns:
                    ActivityLog_DF['PIC'] = UserAuthDict['data']["user_id"] 

                ActivityLogTableContainer.dataframe(
                    ActivityLog_DF[['Date', 'Time', 'Activity', 'Remarks', 'In-Slip Threshold', 'PIC', 'Section Size']].reset_index(), 
                    use_container_width =True)
                if ActivityLogTableContainer.button("Upload", key='uploadActivityLogButton'):
                    uploadActivityLog(ActivityLog_DF, WellInfoDict)
                    st.experimental_rerun()


            except Exception as error_msg:
                ActivityLogTableContainer.error(str(error_msg) + " | Please check your excel file")
    

    st.markdown("## Activity Summary")
    # Table.ActivityLogTableDatabase_Agrid(ActivityLog_DF, reload=True,)
    if 'ActSum_df_Database' not in st.session_state:
        st.session_state['ActSum_df_Database'] = cache_DomeGetData_ActivitySummary(WellInfoDict, UserDateRange)
        st.session_state['IsReloadActSumTable'] = True

    IsActSumDelete = st_toggle_switch(
        label="Delete Activity Summary",
        key="switch_1",
        default_value=False,
        label_after=False,
        # inactive_color="#D3D3D3",  # optional
        # active_color="#11567f",  # optional
        # track_color="#29B5E8",  # optional
    )
    if IsActSumDelete:
        with st.form("ActSum"):
            Out = Table.ActSumTableDatabase_Agrid(st.session_state['ActSum_df_Database'], reload=st.session_state['IsReloadActSumTable'],)
            IsActSumDeleteApply = st.form_submit_button("Delete Selected Rows")
        if st.session_state['IsReloadActSumTable']:
            st.session_state['IsReloadActSumTable'] = False
        if IsActSumDeleteApply:
            ActSumDeleteProgress = st.empty()
            # st.write(Out)
            # out_dict = {}
            ActSumDeleteProgress.progress(0.0)
            i_end = len(Out['selected_rows'])
            for i,dict_temp in enumerate(Out['selected_rows']):

                del dict_temp["_selectedRowNodeInfo"]
                # st.write(dict_temp['StartDateTime'])
                print(IO_Data.DomeDeleteData({
                        'wid':WellInfoDict['wid'],
                        'time_start':dict_temp['StartDateTime'],
                    },table_type="ActivitySummaryTable")
                )

                ActSumDeleteProgress.progress(i/i_end, text=f"Delete Activity, {np.round(i/i_end,2)} % complete")
                # time.sleep(0.5)
            ActSumDeleteProgress.progress(1.)
            ActSumDeleteProgress.warning("Activity Successfully deleted, please wait while the page is refreshes")
            del st.session_state['ActSum_df_Database']
            time.sleep(2)
            ActSumDeleteProgress.empty()

            st.experimental_rerun()

    else:
        Table.ActSumTableDatabase_Agrid(st.session_state['ActSum_df_Database'], reload=True,RowSelection=False)
