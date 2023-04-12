import streamlit as st
import pandas as pd
from PDU_Func import Authentification, IO_Data
import time
import base64
def uploadActivityLog(ActivityLog_DF, WellInfoDict):
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
def App():
    UserAuthDict = st.session_state['UserAuthDict']
    WellInfoDict = st.session_state['WellInfoDict']


    st.text("Activity Database")

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