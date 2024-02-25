import streamlit as st 
from PDU_Func import Authentification, IO_Data, Table
from Page import ActivityMapping, ActivityDatabase, ActivityVisualization
from Page import Welcome, PageNotFound
from importlib import reload
import time
from datetime import datetime
reload(ActivityMapping)
reload(IO_Data)
reload(Table)
# reload(ActivityMapping)
@st.cache_data
def cache_DomeGetData_ActivityLog(WellInfoDict, UserDateRange):
    return (IO_Data.DomeGetData(WellInfoDict, (UserDateRange), table_type="ActivityLogTable"))

def updateActivityLog(WellInfoDict,UpdateActivityLog_DF,UserDateRange):
    try:
        UpdateActivityLog_DF['DateTime'] = UpdateActivityLog_DF['Date'] + " " + UpdateActivityLog_DF['Time']
    except:
        pass
    # st.write(UpdateActivityLog_DF)
    with st.spinner("Communicate with the server"):
        UpdateActivityLog_DF
        InputActivity_DB = (IO_Data.DomeGetData(WellInfoDict, UserDateRange,table_type="ActivityLogTable"))
        print(InputActivity_DB)
        ## Delete
        for i,row in InputActivity_DB.iterrows():
            dict_temp = {
            'wid':WellInfoDict['wid'],
            'id':str(row['id']),
            }
            # print(dict_temp)
            # st.write(row)
            print(IO_Data.DomeDeleteData(dict_temp, table_type="ActivityLogTable"))
            # time.sleep(2)

        ## Insert
        for  i,row in UpdateActivityLog_DF.iterrows():            
            dict_temp = {
                
                    'wid':WellInfoDict['wid'],
                    'dt':str(row['Date']) + " "+str(row['Time']),
                    'date':str(row['Date']),
                    'time':str(row['Time']),
                    'activity':row['Activity'],
                    'in_slip_threshold':row['In-Slip Threshold'],
                    'remarks' : row['Remarks'],
                    'pic' : row['PIC'],
                    'section':row['Section Size']
                    
                }
            # st.write("--")
            # st.write(dict_temp)
            print(IO_Data.DomeInsertData(dict_temp, table_type="ActivityLogTable"))
def App(UserAuthDict, SelectComp, SelectWell,ActivityList='default', SectionSizeList = 'default'):
    # if ActivityList  =='default':
    #     ActivityList = ["N/A",'CEMENTING JOB','CIRCULATE HOLE CLEANING','CONNECTION','DRILL OUT CEMENT','DRILLING FORMATION',
    #                     'LAY DOWN BHA','MAKE UP BHA','NPT','N/D BOP','N/U BOP','OTHER','RUNNING CASING IN','STATIONARY',
    #                     'STUCK PIPE','TRIP IN','TRIP OUT','WAIT ON CEMENT','CIRCULATION','RIG REPAIR','WIPER TRIP'
    #     ]
    # if SectionSizeList == 'default':
    #     SectionSizeList=['26"','17-1/2"','12-1/4"','9-7/8"', '7-7/8"', '8.5"','6-3/4"', '6-1/8"','6"', ]

    st.markdown(" Data Editor Test")
    UserDateRange = {
        "StartDate":datetime.strptime('31-07-1990', '%d-%m-%Y').date(),
      
        "StartTime":datetime.strptime('00:00', '%H:%M').time(),

        "EndDate":datetime.strptime('01-08-2100', '%d-%m-%Y').date(),
        "EndTime":datetime.strptime('23:59', '%H:%M').time(),
        }

    WellInfoDict = IO_Data.getWellInfoDict(UserAuthDict, SelectComp, SelectWell)

    ActivityLog_DF = cache_DomeGetData_ActivityLog(WellInfoDict,UserDateRange)
    ActivityLog_DF['DateTime'] = ActivityLog_DF['DateTime'].astype('datetime64[ns]') 
    ActivityLog_DF['Time'] = ActivityLog_DF['Time'].astype('datetime64[ns]') 
    ActivityLog_DF = ActivityLog_DF.reset_index()
    # column_config = {
    #     'DateTime':st.column_config.DatetimeColumn(
    #         "DateTime",
    #         format="D MMM YYYY, HH:mm:ss",
    #         # required =True,
    #         ),
    #     'In-Slip Threshold':st.column_config.NumberColumn(
    #         "In-Slip Threshold",
    #         # format="HH:mm:ss",
    #         # required =True,
    #         ),
    #     'Section Size':st.column_config.SelectboxColumn(
    #         "Section Size",
    #         # width='small',
    #         options =SectionSizeList,
    #         width='small',
    #         required =True,
    #         ),
    #     'Activity':st.column_config.SelectboxColumn(
    #         "Activity",
    #         # width='small',
    #         options =ActivityList,

    #         # required =True,
    #         ),
    #     'PIC':st.column_config.TextColumn(
    #         "PIC",
    #         width='small',
    #         disabled=True,
    #         default=UserAuthDict['data']['user_id'],
    #         # required =True,
    #         ),
    #     'Remarks':st.column_config.TextColumn(
    #         "Remarks",
    #         width='large',
    #         # required =True,
    #         ),

    # }
    with st.form('update'):
        # ActivityLog_DF_out = st.data_editor(
        #     ActivityLog_DF,
        #     num_rows ='dynamic',
        #     column_config=column_config,
        #     use_container_width=True,
        #     hide_index=True,
        #     column_order = ['DateTime', 'Activity', 'Section Size','In-Slip Threshold' ,  'Remarks', 'PIC'],
        #     key='ActivityLogTableDataEditor'
        # )
        ActivityLog_DF_out = Table.ActivityLogTable_DataEditor(ActivityLog_DF, UserAuthDict, ActivityList='default', SectionSizeList='default', key='ActLogInput')
        if st.form_submit_button():
            ActivityLog_DF_out['Date'] = ActivityLog_DF_out['DateTime'].dt.date
            ActivityLog_DF_out['Time'] = ActivityLog_DF_out['DateTime'].dt.time
            st.toast('Updating Activity Log', icon='🔄')
            updateActivityLog(WellInfoDict,ActivityLog_DF_out,UserDateRange)
            st.toast('Activity Log is updated!', icon='🟢')







