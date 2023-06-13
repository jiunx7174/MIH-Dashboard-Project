import streamlit as st
from PDU_Func import Authentification, IO_Data,Table, ActivitySummary
from PDU_Func.IO_Data import getAvailableCompanyDF
from datetime import datetime,timedelta
from importlib import reload
import pandas as pd 
from streamlit_modal import Modal
import time
import numpy as np
reload(IO_Data)
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

@st.cache_data
def cache_DomeGetData_ActivityLog(WellInfoDict, UserDateRange):
    return (IO_Data.DomeGetData(WellInfoDict, ExtendDateTime(UserDateRange.copy()), table_type="ActivityLogTable"))

@st.cache_data
def cache_DomeGetRealtimeSensorData_v2(WellInfoDict, UserDateRange):
    return IO_Data.DomeGetRealtimeSensorData_v2(WellInfoDict, UserDateRange)
# @st.cache_data
def cache_DomeGetData_ActivitySummary(WellInfoDict, UserDateRange,ActivityLog_DF, RTSensor_df):
    print("Get ActSum Data")
    ActSumData= ActivitySummary.ActivitySummaryTable(WellInfoDict, UserDateRange)
        
            # generate both of FIRM and REVIEW ActSum
    ActSumData.getActivitySummary(ActivityLog_DF, RTSensor_df, MinuteTolerances=1, CleaningIteration=1)
    return ActSumData

def AllDateTime():
    DateRange = {
                "StartDate": datetime.strptime('01-08-2000', '%d-%m-%Y').date(),
                "StartTime": datetime.strptime('00:00', '%H:%M').time(),
                "EndDate": datetime.strptime('01-08-2100', '%d-%m-%Y').date(),
                "EndTime": datetime.strptime('00:00', '%H:%M').time()
                    }
    return DateRange
def ExtendDateTime(DateRange):
    """
    Extend the date time by backdate by 1 day in the StartDate
    """
    DateRange['StartDate'] = DateRange['StartDate'] - timedelta(days=14)
    # DateRange['EndDate'] = DateRange['EndDate'] - timedelta(days=1)

    return DateRange
def IsSubmitFormTrue():
    st.session_state['IsFormSubmit'] = True
    if ("ActSum" in st.session_state):
        del st.session_state["ActSum"]

    # if ("RTSensor_df" in st.session_state):
    #     del st.session_state["RTSensor_df"]


def initiateSession(WellInfoDict):
    CheckCreateTable(WellInfoDict)
    if "IsFormSubmit" not in st.session_state:
        st.session_state['IsFormSubmit'] = False
    if 'PopUpWindow' not in st.session_state:
        st.session_state['PopUpWindow'] = Modal("Confirmation", key='modal_test')
    if 'IsRecalculate' not in st.session_state:
        st.session_state['IsRecalculate'] = False
        
    # if 'UserDateRange' not in st.session_state:
    #     st.session_state['UserDateRange'] = {
    #         "StartDate":[],
    #         "StartTime":[],
    #         "EndDate":[],
    #         "EndTime":[]
    #     }


def updateActivityLog(WellInfoDict,UpdateActivityLog_DF,UserDateRange):
    with st.spinner("Communicate with the server"):
        InputActivity_DB = (IO_Data.DomeGetData(WellInfoDict, ExtendDateTime(UserDateRange.copy()),table_type="ActivityLogTable"))
        print(InputActivity_DB)
        ## Delete
        for i,row in InputActivity_DB.iterrows():
            dict_temp = {
            'wid':WellInfoDict['wid'],
            'id':str(row['id']),
            }
            print(dict_temp)
            # st.json(input_dict_temp)
            print(IO_Data.DomeDeleteData(dict_temp, table_type="ActivityLogTable"))

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
            print(IO_Data.DomeInsertData(dict_temp, table_type="ActivityLogTable"))


def checkActivityLog(ActivityLog_DF):
    # TODO
    # create an activity log input check
    # -Duplicate Date Time
    # -empty columns values

    return ActivityLog_DF
        

def checkActSum(df):

    df['StartDateTime'] = df['StartDateTime'].astype('datetime64[ns]')
    df['EndDateTime'] = df['EndDateTime'].astype('datetime64[ns]')
    df['Duration'] = df['Duration'].astype('float')
    # df['Duration'] = pd.to_timedelta(df['Duration'], unit='minutes')
    df = df.sort_values('StartDateTime')
    df = df.reset_index(drop=True)

    df['Diff'] = df['StartDateTime'].shift(-1) - df['EndDateTime']
    # case if Diff > 0
    # df_out = pd.DataFrame(df)
    idx_start = 0
    df_concat_list = []
    

    for idx,row in df[(df['Diff'] > pd.Timedelta(0))].iterrows():

        df_concat_list.append(df.loc[idx_start:idx])
        new_row = {
            "StartDateTime":row["EndDateTime"],
            "EndDateTime":df.loc[idx+1, 'StartDateTime'],
            "LABEL_SubActivity":"Look and Define",
        }
        # st.write(new_row)
        df_concat_list.append(pd.DataFrame([new_row]))
        idx_start = idx
    df_concat_list.append(df.loc[idx:])

        

    df_out = pd.concat(df_concat_list, ignore_index=True,axis=0).drop('Duration', axis=1)
    print(df_out)
    print(df_out.columns)
    # st.write(df_out)

    # if negative-> overlap antara start dengan end 
    #     2 baris tersebut SubActivitynya jadi DateError-look and define
    # if positive-> ada gap antara start dengan end 
    #     create new row to fill the gap, dan isi sub activitynya jadi look and define
    

    # TODO
    #     # if date error?
    #     # - if there's a gap?
    #           - should fill the gap by Look and define values
    #       - if there's date overlapping. End overlap with Start, Start overlap with End, 
    #           - should be filled by "Overlap with previous/next activity"
        # if False/Check
        # if Look and Define
    
    # create an activity log input check
    # -Duplicate Date Time
    # -empty columns values

    return df_out
def ReCalculateDuration(ActSumData):
    # TODO
    # create an activity log input check
    # -Duplicate Date Time
    # -empty columns values

    return ActSumData

# TODO
# Build Case #1 ActivitySummary CRUD function
def UploadActSum(WellInfoDict,UpdateActivityLog_DF,UserDateRange):
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
            print(IO_Data.DomeInsertData(dict_temp, table_type="ActivityLogTable"))
def convert_df(df):
     # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(index = False).encode('utf-8')
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
def showPopupWindow():
    print("Clicked")
    if st.session_state.sidebar_state == 'expanded':
        st.session_state.sidebar_state = 'collapsed' 
    if not st.session_state['PopUpWindow'].is_open():
        st.session_state['PopUpWindow'].open()



def App(UserAuthDict, SelectComp, SelectWell):
    st.markdown(
    """
    <style>
        [data-testid="stForm"] {border: 0px}
    </style>
    """,
    unsafe_allow_html=True
    )
    # st.session_state['WellInfoDict'] = IO_Data.getWellInfoDict(UserAuthDict, SelectComp, SelectWell)
    WellInfoDict = IO_Data.getWellInfoDict(UserAuthDict, SelectComp, SelectWell)

    # UserAuthDict = st.session_state['UserAuthDict']
    # WellInfoDict = st.session_state['WellInfoDict']
    # st.json(UserAuthDict)
    # st.json(WellInfoDict)
    initiateSession(WellInfoDict)

    SidebarContainer = st.sidebar.container()
    st.markdown('<h1 style="text-align: center; font-size: 50px; margin-top: 2px;"><span style="text-decoration: underline;">ACTIVITY MAPPING MODULE</span></h1>', unsafe_allow_html=True)
    # st.divider()
    # st.markdown('<h1 style="text-align: center; font-size: 40px; margin-top: 2px;">Major Activity Log Table</h1>', unsafe_allow_html=True)
    ActLogContainer = st.container()
    st.divider()
    
    ActSumContainer = st.container()
    if not st.session_state['IsFormSubmit']:
        SidebarContainer.warning("Select Datetime Range first")

    SidebarContainer = st.sidebar.container()
    # with SidebarContainer:
    with SidebarContainer.form(key='DateForm'):
        DateCol,TimeCol = st.columns([1,1])
        # st.session_state['UserDateRange'] = {
        UserDateRange = {
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
        # st.json(UserDateRange)


        st.form_submit_button(on_click=IsSubmitFormTrue)

    # print(st.session_state['UserDateRange'])

    # st.json(UserDateRange)
    



    if st.session_state['IsFormSubmit']:

        with ActLogContainer:
            RTSensor_df = cache_DomeGetRealtimeSensorData_v2(WellInfoDict, UserDateRange)
        ActivityLog_DF = cache_DomeGetData_ActivityLog(WellInfoDict, UserDateRange)

        with ActLogContainer.form(key='ActivityLogTable_Agrid'):
            st.markdown('<h1 style="text-align: center; font-size: 40px; margin-top: 2px;">Major Activity Log Table</h1>', unsafe_allow_html=True)
            with st.container():

                ActLogAgridOut = Table.ActivityLogTable_Agrid(ActivityLog_DF, reload=True)


            isActLogApply = st.form_submit_button("apply")

        if isActLogApply:
            ActivityLog_DF_Upload = checkActivityLog(ActLogAgridOut['data'])

            updateActivityLog(WellInfoDict,ActivityLog_DF_Upload,UserDateRange)
            # st.session_state["ActivityLog_DF"] = (IO_Data.DomeGetData(WellInfoDict, UserDateRange, table_type="ActivityLogTable"))
            cache_DomeGetData_ActivityLog.clear()
            # ActivityLog_DF = cache_DomeGetData_AcctivityLog(WellInfoDict, UserDateRange)
            st.success("Activity Log Updated")
            if isActLogApply:
                st.experimental_rerun()
            
        
        # retrieve Realtime Sensor Data
        print("GetRealtimeData")
        print(UserDateRange)
        print("-----")


        #######
        ## ActSumTable
        #######
        if 'ActSum' not in st.session_state:
            st.session_state['ActSum'] = cache_DomeGetData_ActivitySummary(WellInfoDict, UserDateRange,ActivityLog_DF, RTSensor_df)
            IsActSumReload = True
        else:
            IsActSumReload = False

        ActSumData = st.session_state['ActSum']

        
        if not st.session_state['PopUpWindow'].is_open():
            print("model is closed")
            # st.session_state['ActSumDF_Upload'] = None
            if st.session_state.sidebar_state == 'collapsed': 
                st.session_state.sidebar_state = 'expanded'
                st.experimental_rerun()
            
        ActSumContainer.markdown('<h1 style="text-align: center; font-size: 40px; margin-top: 2px;">Activity Summary Table</h1>', unsafe_allow_html=True)
        ActSumButtonCol = ActSumContainer.columns(3)
        ActSumForm = ActSumContainer.container()

        IsActSumReset = ActSumButtonCol[0].button("Reset Activity Summary Table", key="ActSumReset")
        # IsActSumRecalculate = ActSumButtonCol[0].button("Recalculate Activity Summary Table", key="IsActSumRecalculate")
        if IsActSumReset:
            print("reset")
            del st.session_state['ActSum']
            # cache_DomeGetData_ActivitySummary.clear()
            st.experimental_rerun()
        # IsActSumReload = IsActSumReset
        # IsActSumRefresh = ActSumButtonCol[-1].button("Refresh", key="ActSumRefresh")
        with ActSumForm.form(key='ActSumTable_Agrid'):
            ActSumAgridOut = pd.DataFrame(Table.ActSumTable_Agrid(ActSumData.Data, reload=IsActSumReload)['data'])
            isActSumApply = st.form_submit_button("apply")


        if isActSumApply :
            ActSumAgridOut_Firm = ActSumAgridOut[ActSumAgridOut['status'] == "FIRM"]
            ActSumAgridOut =(ActivitySummary.checkActSumDF(ActSumAgridOut[ActSumAgridOut['status'] != "FIRM"]))
            print(ActSumAgridOut.columns)
            if "ErrorWarning" in (ActSumAgridOut.columns):
                with st.expander("Activity Summary Table Error"):
                    st.markdown("Please Update the following row first")
                    Table.ActSumTableConfirmation_Agrid(ActSumAgridOut[ActSumAgridOut['ErrorWarning'].notna()], showWarning=True)
            else:
                
                st.session_state['ActSum'].Data = pd.concat([ActSumAgridOut_Firm,ActivitySummary.RecalculateActSum(ActSumAgridOut)])
                st.session_state['IsRecalculate'] = True
                # st.stop()
        if st.session_state['IsRecalculate']:
            st.success("No Error Found")
            st.button("save the Activity Summary", key="saveActSum", on_click=showPopupWindow)
            st.download_button(
                label="Download Activity Summary as CSV",
                data=convert_df(st.session_state['ActSum'].Data),
                file_name=SelectComp + "_"+ SelectWell + '_ActivitySummary.csv',
                mime='text/csv',
            )



            st.session_state['IsRecalculate'] = False
            
                # if not PopUpWindow.is_open():
                #     PopUpWindow.open()

        if st.session_state['PopUpWindow'].is_open():
            # st.text('tes')
            # st.stop
            ActSumAgridOut = st.session_state['ActSum'].Data
            with st.session_state['PopUpWindow'].container():
                st.markdown("### Please make sure or double check the following table is already correct.")
                print("ErrorWarning" in (ActSumAgridOut.columns))
                if "ErrorWarning" in (ActSumAgridOut.columns):
                    print('ErrorWarning')
                    Table.ActSumTableConfirmation_Agrid(ActSumAgridOut[ActSumAgridOut['status'] != "FIRM"], showWarning=True)
                else:
                    Table.ActSumTableConfirmation_Agrid(ActSumAgridOut[ActSumAgridOut['status'] != "FIRM"])
                    PopUpWindowCol = st.columns(15)
                    isActSumUploadConfirm = PopUpWindowCol[14].button("Confirm", key="ActSumUploadConfirm")

                # // Table.ActSumTableConfirmation_Agrid(st.session_state['ActSumDF_Upload'])
                    if isActSumUploadConfirm:
                        st.success("The Activity Summary Table has already update")
                        # cache_DomeGetData_ActivitySummary.clear()
                        del st.session_state['ActSum']
                        time.sleep(5)
                        st.session_state['PopUpWindow'].close()




        # st.stop()
        # if isActSumApply:
        #     # IDEA if the user click the recalculate duration, the QC Actsum run first, 
        #                   if fail it'll raise an error and highlight the actsum 
        #                   if QC pass, it'll recalculate the duration.
        #     # TODO create a function to check the actsum data
        #     # if date error?
            #     # - if there's a gap?
            #           - should fill the gap by Look and define values
            #       - if there's date overlapping. End overlap with Start, Start overlap with End, 
            #           - should be filled by "Overlap with previous/next activity"
              # if False/Check
              # if Look and Define

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

        
    # else:
        

    # TODO
    # create  