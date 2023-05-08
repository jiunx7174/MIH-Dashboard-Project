import streamlit as st
from PDU_Func import Authentification, IO_Data,Table, ActivitySummary
from PDU_Func.IO_Data import getAvailableCompanyDF
from datetime import datetime,timedelta
from importlib import reload
import pandas as pd 
from streamlit_modal import Modal
import time

# @st.cache_data(experimental_allow_widgets=True)
def DomeGetRealtimeSensorData(WellInfoDict, UserDateRange):
    # return IO_Data.DomeGetRealtimeSensorData(WellInfoDict, UserDateRange)
    return IO_Data.DomeGetRealtimeSensorData_v2(WellInfoDict, UserDateRange)


@st.cache_resource
def CheckCreateTable(WellInfoDict):
    if IO_Data.DomeCheckTable(WellInfoDict['wid'], table_type ="ActivityLogTable")['table']==0:
        IO_Data.DomeCreateTable(WellInfoDict['wid'], table_type ="ActivityLogTable")
    if IO_Data.DomeCheckTable(WellInfoDict['wid'], table_type ="ActivitySummaryTable")['table']==0:
        IO_Data.DomeCreateTable(WellInfoDict['wid'], table_type ="ActivitySummaryTable")

def AllDateTime():
    DateRange = {
                "StartDate": datetime.strptime('01-08-2000', '%d-%m-%Y').date(),
                "StartTime": datetime.strptime('00:00', '%H:%M').time(),
                "EndDate": datetime.strptime('01-08-2100', '%d-%m-%Y').date(),
                "EndTime": datetime.strptime('00:00', '%H:%M').time()
                    }
    return DateRange
def ExtendDateTime(DateRange):
    DateRange['StartDate'] = DateRange['StartDate'] - timedelta(days=1)
    # DateRange['EndDate'] = DateRange['EndDate'] - timedelta(days=1)

    return DateRange
def IsSubmitFormTrue():
    st.session_state['IsFormSubmit'] = True
    if ("ActSum" in st.session_state):
        del st.session_state["ActSum"]

    if ("RTSensor_df" in st.session_state):
        del st.session_state["RTSensor_df"]


def initiateSession(WellInfoDict):
    
    CheckCreateTable(WellInfoDict)
    if "IsFormSubmit" not in st.session_state:
        st.session_state['IsFormSubmit'] = False
    if 'UserDateRange' not in st.session_state:
        st.session_state['UserDateRange'] = {
            "StartDate":[],
            "StartTime":[],
            "EndDate":[],
            "EndTime":[]
        }


def updateActivityLog(WellInfoDict,UpdateActivityLog_DF,UserDateRange):
    with st.spinner("Communicate with the server"):
        InputActivity_DB = (IO_Data.DomeGetData(WellInfoDict, UserDateRange,table_type="ActivityLogTable"))

        ## Delete
        for i,row in InputActivity_DB.iterrows():
            dict_temp = {
            'wid':WellInfoDict['wid'],
            'id':str(row['id']),
            }
            # st.json(input_dict_temp)
            IO_Data.DomeDeleteData(dict_temp, table_type="ActivityLogTable")

        ## Insert
        for  i,row in UpdateActivityLog_DF.iterrows():            
            dict_temp = {
                    'wid':WellInfoDict['wid'],
                    'dt':str(row['DateTime']),
                    'date':str(row['Date']),
                    'time':str(row['Time']),
                    'activity':row['Activity'],
                    'in_slip_threshold':row['In-Slip Threshold'],
                    'remarks' : row['Remarks'],
                    'pic' : row['PIC'],
                    'section':row['Section Size']
                    
                }
            IO_Data.DomeInsertData(dict_temp, table_type="ActivityLogTable")


def checkActivityLog(ActivityLog_DF):
    # TODO
    # create an activity log input check
    # -Duplicate Date Time
    # -empty columns values

    return ActivityLog_DF
        

def checkActSum(ActSumData):
    # TODO
    # create an activity log input check
    # -Duplicate Date Time
    # -empty columns values

    return ActSumData
def ReCalculateDuration(ActSumData):
    # TODO
    # create an activity log input check
    # -Duplicate Date Time
    # -empty columns values

    return ActSumData

# TODO
# Build Case #1 ActivitySummary CRUD function
def updateActSum(ActivityLog_DF, UpdateActivityLog_DF, UpdateActivitysLog_DF):
    #The table should support the remove duplicate and any cleaning workflow
    pass

# def updateActivityLog(ActivityLog_DF, UpdateActivityLog_DF):
#     old = ActivityLog_DF.set_index('DateTime')
#     update = UpdateActivityLog_DF.set_index('DateTime')

#     changed = old[old.index.isin(update.index)].ne(update)

#     removed = old.index.difference(update.index)
#     added = update.index.difference(old.index)

#     st.text("Removed")
#     st.dataframe(old.loc[removed,:])
#     st.text("Added")
#     st.dataframe(update.loc[added,:])

#     old = old.drop(index=list(removed))
#     update = update.drop(index=list(added))
#     changed = old.ne(update)
#     rows_changed = changed.any(axis=1)
#     st.text("changed")
#     st.dataframe(changed)
#     st.text(rows_changed.values)



def App():

    UserAuthDict = st.session_state['UserAuthDict']
    WellInfoDict = st.session_state['WellInfoDict']
    st.json(UserAuthDict)
    st.json(WellInfoDict)
    initiateSession(WellInfoDict)

    SidebarContainer = st.sidebar.container()
    # with SidebarContainer:
    with SidebarContainer.form(key='DateForm'):
        DateCol,TimeCol = st.columns([1,1])
        st.session_state['UserDateRange'] = {
        "StartDate":(DateCol.date_input(
            "Start Date",
            value = datetime.strptime('31-07-2021', '%d-%m-%Y').date(),
            key="StartDateValues"
            )),

        "StartTime":(TimeCol.time_input(
            "Start Time",
            value = datetime.strptime('00:00', '%H:%M').time(),
            key="StartTimeValues")),
        "EndDate":(DateCol.date_input(
            "End Date",
            value = datetime.strptime('01-08-2021', '%d-%m-%Y').date(),
            key="EndDateValues")),
        "EndTime":(TimeCol.time_input(
            "End Time",
            value = datetime.strptime('23:59', '%H:%M').time(),
            key="EndTimeValues"))
        }


        st.form_submit_button(on_click=IsSubmitFormTrue)

    print(st.session_state['UserDateRange'])


    st.markdown('<h1 style="text-align: center; font-size: 50px; margin-top: 2px;"><span style="text-decoration: underline;">ACTIVITY MAPPING MODULE</span></h1>', unsafe_allow_html=True)
    
    st.button("Reset", key="ActLogReset")


    if st.session_state['IsFormSubmit']:

        if "ActvitiyLog_DF" not in st.session_state:
            st.session_state["ActivityLog_DF"] = (IO_Data.DomeGetData(WellInfoDict, ExtendDateTime(st.session_state['UserDateRange'].copy()), table_type="ActivityLogTable"))
        
        ActivityLog_DF = st.session_state["ActivityLog_DF"]
        # ActivityLog_DF = (IO_Data.DomeGetData(WellInfoDict, st.session_state['UserDateRange'], table_type="ActivityLogTable"))

        with st.form(key='ActivityLogTable_Agrid'):
            with st.container():
                ActLogAgridOut = Table.ActivityLogTable_Agrid(ActivityLog_DF, reload=True)


            isActLogApply = st.form_submit_button("apply")

        if isActLogApply:
            ActivityLog_DF_Upload = checkActivityLog(ActLogAgridOut['data'])

            updateActivityLog(WellInfoDict,ActivityLog_DF_Upload,st.session_state['UserDateRange'])
            st.session_state["ActivityLog_DF"] = (IO_Data.DomeGetData(WellInfoDict, st.session_state['UserDateRange'], table_type="ActivityLogTable"))
            st.success("Activity Log Update")
            st.experimental_rerun()
        
        # retrieve Realtime Sensor Data
        print("GetRealtimeData")
        print(st.session_state['UserDateRange'])
        if "RTSensor_df" not in st.session_state:
            st.session_state['RTSensor_df'] = IO_Data.DomeGetRealtimeSensorData_v2(WellInfoDict, st.session_state['UserDateRange'])
        RTSensor_df = st.session_state['RTSensor_df']
        # RTSensor_df = DomeGetRealtimeSensorData(WellInfoDict, st.session_state['UserDateRange'])

        # st.dataframe(RTSensor_df)
        ActSumButtonCol = st.columns(8)
        IsActSumReset = ActSumButtonCol[0].button("Reset", key="ActSumReset")
        IsActSumRefresh = ActSumButtonCol[1].button("Refresh", key="ActSumRefresh")
        #######
        ## ActSumTable
        #######
        if ("ActSum" not in st.session_state) or IsActSumReset:
            print("get activity summary")
            # Init ActSumTable
            st.session_state["ActSum"]= ActivitySummary.ActivitySummaryTable(WellInfoDict, st.session_state['UserDateRange'])
        
            # generate both of FIRM and REVIEW ActSum
            st.session_state["ActSum"].getActivitySummary(ActivityLog_DF, RTSensor_df, MinuteTolerances=1, CleaningIteration=1)
            if ("ActSum" not in st.session_state):
                st.session_state["ActSum_Preserve"] = st.session_state["ActSum"]
            # st.experimental_rerun()
        #if IsActSumReset:
        #    # Reset The ActSum
        #    st.session_state["ActSum"] = st.session_state["ActSum_Preserve"]
        #    # del st.session_state["ActSum"]
        #    st.experimental_rerun()

        ActSumData = st.session_state["ActSum"]

        # st.stop()
        PopUpWindow = Modal("Confirmation", key='modal_test')
        if not PopUpWindow.is_open():
            print("model is closed")
            st.session_state['ActSumDF_Upload'] = None
            if st.session_state.sidebar_state == 'collapsed': 
                st.session_state.sidebar_state = 'expanded'
                st.experimental_rerun()
            

        with st.form(key='ActSumTable_Agrid'):

            # TODO build a ActSum Agrid Table 
            with st.container():
                ActSumAgridOut = Table.ActSumTable_Agrid(ActSumData.Data, reload=IsActSumReset)

            isActSumApply = st.form_submit_button("apply")

        # print("modal")
        # print(isActSumApply and (ActSumAgridOut['selected_rows'] != []))
        if isActSumApply and (ActSumAgridOut['selected_rows'] != []):

            st.session_state['ActSumDF_Upload'] = pd.DataFrame.from_dict(ActSumAgridOut['selected_rows']).drop('_selectedRowNodeInfo', axis=1)
            st.session_state.sidebar_state = 'collapsed' if st.session_state.sidebar_state == 'expanded' else 'expanded'
            PopUpWindow.open()

        if PopUpWindow.is_open():
            
            with PopUpWindow.container():
                st.markdown("### Please make sure or double check the following table is already correct.")
                Table.ActSumTableConfirmation_Agrid(st.session_state['ActSumDF_Upload'])
                PopUpWindowCol = st.columns(15)
                isActSumUploadConfirm = PopUpWindowCol[14].button("Confirm", key="ActSumUploadConfirm")
                if isActSumUploadConfirm:
                    st.success("The Activity Summary Table has already update")
                    del st.session_state["ActSum"]
                    time.sleep(5)
                    PopUpWindow.close()




        if ("ActSum" not in st.session_state) or IsActSumReset:
            print("reset")
            st.experimental_rerun()
        # st.stop()
        # if isActSumApply:
        #     # TODO create a function to check the actsum data
        #     # - if there's a gap?
        #     # - if date error?
        #     # checkActSum(ActSumAgridOut['data'])

        #     # TODO build a recalculate duration
        #     # st.session_state["ActSum"] = ReCalculateDuration(ActSumAgridOut['data'])
        #     # st.session_state["ActSum"] = LabelStand(st.session_state["ActSum"])
        #     # ActSumData_Upload = checkActSum(ActSumAgridOut['data'])


        #     # updateActSum(WellInfoDict, ActSumData_Upload, st.session_state['UserDateRange'])
        #     # st.session_state["ActSum"].getActivitySummary(ActivityLog_DF, RTSensor_df, MinuteTolerances=1, CleaningIteration=1)
        #     if ActSumAgridOut['selected_rows'] != []:
        #         ActSumDF_Upload = pd.DataFrame.from_dict(ActSumAgridOut['selected_rows']).drop('_selectedRowNodeInfo', axis=1)
        #         # st.write(ActSumDF_Upload)
        #         # st.dataframe(ActSumDF_Upload)
        #         # st.dataframe(ActSumData.Data)
        #         Table.ActSumTableConfirmation_Agrid(ActSumDF_Upload)
        #     # selected_df = pd.DataFrame(selected).apply(pd.to_numeric, errors='coerce')
            
        #     # st.dataframe(ActSumData.Data)
        #     # st.dataframe(ActSumAgridOut['data'])
        #     # st.write(ActSumAgridOut['selected_rows'])
        #         st.success("ActSumUpdate")
        #     #if ActSumAgridOut['data'] is selected:
        #         # show the selected values
        #         # show button to reconfirm
        #         #if IsConfirmUpdate:
        #         #    upload ActSum
        #         #    st.experimental_rerun()

        #     # else:
        #     # st.experimental_rerun()
        # if ("ActSum" not in st.session_state) or IsActSumReset:
        #     print("reset")
        #     st.experimental_rerun()

        


    # TODO
    # create  