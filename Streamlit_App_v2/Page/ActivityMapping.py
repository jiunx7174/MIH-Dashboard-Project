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
reload(Table)
reload(ActivitySummary)
# @st.cache_data(experimental_allow_widgets=True)
def DomeGetRealtimeSensorData(WellInfoDict, UserDateRange):
    # return IO_Data.DomeGetRealtimeSensorData(WellInfoDict, UserDateRange)
    return IO_Data.DomeGetRealtimeSensorData_v2(WellInfoDict, UserDateRange)
def ActivitySummaryColumnRenameDict():
    ActivitySummaryColumnRenameDict = {"wid":"wid",
                            "date":"Date",
                            "time_start":"StartDateTime",
                            "time_end":"EndDateTime",
                            "duration_minutes":"Duration",
                            "hole_depth":"Hole_Depth_max",
                            "bit_depth":"Bit_Depth_avg",
                            "meterage_drilling":"DrillingMeterage",
                            "rotate_drilling_time":"RotateDrillingDuration",
                            "slide_drilling_time":"SlideDrillingDuration",
                            "reaming_time":"ReamingDuration",
                            "connection_time":"ConnectionDuration",
                            "on_bottom_hours":"OnBottomDurationPerStand",
                            "stand_duration":"StandDuration",
                            "label_subactivity":"LABEL_SubActivity",
                            "label_activity":"LABEL_Activity",
                            "stand_meterage_drilling":"DrillingMeteragePerStand",
                            "stand_durationx":"InSlip_Treshold",
                            # "stand_on_bottom":"OnBottomDurationPerStand",
                            "pic":"PIC",
                            "section":"Section",
                            "remark":"Remarks",
                            "stand_group":"Stand Group_Pred",
                            }
    out= {
        "ColumnName":{"wid":"wid",
                            "date":"Date",
                            "time_start":"StartDateTime",
                            "time_end":"EndDateTime",
                            "duration_minutes":"Duration",
                            "hole_depth":"Hole_Depth_max",
                            "bit_depth":"Bit_Depth_avg",
                            "meterage_drilling":"DrillingMeterage",
                            "rotate_drilling_time":"RotateDrillingDuration",
                            "slide_drilling_time":"SlideDrillingDuration",
                            "reaming_time":"ReamingDuration",
                            "connection_time":"ConnectionDuration",
                            "on_bottom_hours":"OnBottomDurationPerStand",
                            "stand_duration":"StandDuration",
                            "label_subactivity":"LABEL_SubActivity",
                            "label_activity":"LABEL_Activity",
                            "stand_meterage_drilling":"DrillingMeteragePerStand",
                            "stand_durationx":"InSlip_Treshold",
                            # "stand_on_bottom":"OnBottomDurationPerStand",
                            "stand_on_bottom":"LABEL_ConnectionActivity",
                            "pic":"PIC",
                            "section":"Section",
                            "remark":"Remarks",
                            "stand_group":"Stand Group_Pred",
                            },
        "DataTypeDict":{
                    "wid": 'int',
                    "Date": "datetime64",
                    "StartDateTime": "datetime64",
                    "EndDateTime": "datetime64",
                    "Duration": "float",
                    "Hole_Depth_max": "float",
                    "Bit_Depth_avg": "float",
                    "DrillingMeterage": "float",
                    "RotateDrillingDuration": "float",
                    "SlideDrillingDuration": "float",
                    "ReamingDuration": "float",
                    "ConnectionDuration": "float",
                    "OnBottomDurationPerStand": "float",
                    "StandDuration": "float",
                    "LABEL_SubActivity": "string",
                    "LABEL_Activity": "string",
                    "DrillingMeteragePerStand": "float",
                    "InSlip_Treshold": "float",
                    "PIC": "string",
                    "Section": "string",
                    "Remarks": "string",
                    "Stand Group_Pred": "string",
                    "LABEL_ConnectionActivity":"string",
                    # stand_on_bottom:
                    },

    }
    return out


def UploadActivitySummary(ActSumDF):
    ConversionDict = ActivitySummaryColumnRenameDict()
    swapped_dict = {value: key for key, value in ConversionDict['ColumnName'].items()}
    ActSumDF = ActSumDF.astype(ConversionDict['DataTypeDict'])
    ActSumDF = ActSumDF.astype('str')
    # ActSumDF.fillna(0)
    ActSumDF = ActSumDF[ConversionDict['DataTypeDict'].keys()]
    tes_df = ActSumDF.rename(columns=swapped_dict).iloc[40,:]
    # st.write(ActSumDF.rename(columns=swapped_dict))
    tobeupload_testa = tes_df.to_dict()


    return tobeupload_testa
@st.cache_resource
def CheckCreateTable(WellInfoDict):
    if IO_Data.DomeCheckTable(WellInfoDict['wid'], table_type ="ActivityLogTable")['table']==0:
        IO_Data.DomeCreateTable(WellInfoDict['wid'], table_type ="ActivityLogTable")
    if IO_Data.DomeCheckTable(WellInfoDict['wid'], table_type ="ActivitySummaryTable")['table']==0:
        IO_Data.DomeCreateTable(WellInfoDict['wid'], table_type ="ActivitySummaryTable")

# @st.cache_data(ttl=timedelta(hours=1))
def cache_DomeGetData_ActivityLog(WellInfoDict, UserDateRange):
    UserDateRange_Ext = ExtendDateTime(UserDateRange.copy())
    # st.write(UserDateRange_Ext)
    return (IO_Data.DomeGetData(WellInfoDict, UserDateRange_Ext, table_type="ActivityLogTable"))

@st.cache_data(show_spinner=False, ttl=timedelta(hours=2))
def cache_DomeGetRealtimeSensorData_v2(WellInfoDict, UserDateRange):
    return IO_Data.DomeGetRealtimeSensorData_v2(WellInfoDict, UserDateRange)
# @st.cache_data
def cache_DomeGetData_ActivitySummary(WellInfoDict, UserDateRange,ActivityLog_DF, RTSensor_df):
    print("Get ActSum Data")
    ActivityLog_DF['DateTime'] = ActivityLog_DF['Date'] + " " + ActivityLog_DF['Time']
    
    ActSumData= ActivitySummary.ActivitySummaryTable(WellInfoDict, UserDateRange)
        
            # generate both of FIRM and REVIEW ActSum
    # ActSumData.getActivitySummary(ActivityLog_DF, RTSensor_df, MinuteTolerances=1, CleaningIteration=1)
    ActSumData.getActivitySummary_v2(ActivityLog_DF, RTSensor_df, MinuteTolerances=0.5, CleaningIteration=1)
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
    DateRange['EndDate'] = DateRange['EndDate'] + timedelta(days=14)
    # DateRange['EndDate'] = DateRange['EndDate'] - timedelta(days=1)

    return DateRange
def IsSubmitFormTrue():
    st.session_state['IsFormSubmit'] = True
    ActSumClear()
    ActLogClear()

def ActSumClear():
    if ("ActSum" in st.session_state):
        del st.session_state["ActSum"]
    if ("actsumtable_v2" in st.session_state):
        del st.session_state["actsumtable_v2"]
def ActLogClear():
    if ("ActLogDF" in st.session_state):
        del st.session_state["ActLogDF"]
    
    # if ("RTSensor_df" in st.session_state):
    #     del st.session_state["RTSensor_df"]


def initiateSession(WellInfoDict):
    CheckCreateTable(WellInfoDict)
    if "IsFormSubmit" not in st.session_state:
        st.session_state['IsFormSubmit'] = False
    if 'PopUpWindow' not in st.session_state:
        st.session_state['PopUpWindow'] = Modal("Confirmation", key='modal_test')
    if 'IsActSumNoError' not in st.session_state:
        st.session_state['IsActSumNoError'] = False
        
    # if 'UserDateRange' not in st.session_state:
    #     st.session_state['UserDateRange'] = {
    #         "StartDate":[],
    #         "StartTime":[],
    #         "EndDate":[],
    #         "EndTime":[]
    #     }


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

def ConfirmToSave():
    with st.session_state['PopUpWindow'].container():
        with st.empty():
            ActivitySummary.UploadActivitySummary(st.session_state['ActSum'].Data)
            
            ActSumClear()
            st.success("Actitivity Summary Update successfully, please wait while the page is refreshes")
            time.sleep(5)
            st.session_state['PopUpWindow'].close()


def ActLogApply(ActLogAgridOut,WellInfoDict,UserDateRange):
    ActLogApplyButtonSontainer = st.empty()
    # ActivityLog_DF_Upload = checkActivityLog(ActLogAgridOut['data'])

    updateActivityLog(WellInfoDict,ActLogAgridOut['data'],UserDateRange)
    del st.session_state['ActLog']
    ActLogApplyButtonSontainer.success("Activity Log Updated")
    ActSumClear()
    time.sleep(2)
    ActLogApplyButtonSontainer.empty()


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
    
    # ActivateDate = (WellInfoDict['ActiveDate'])
    # ActivateDate =
    ActivateDate = datetime.strptime(WellInfoDict['ActiveDate'], '%Y-%m-%d').strftime('%d-%m-%Y')

    if datetime.strptime(WellInfoDict['EndDate'], '%Y-%m-%d') > datetime.today():
        EndDate = datetime.today().strftime('%d-%m-%Y')
    else:
        EndDate = datetime.strptime(WellInfoDict['EndDate'], '%Y-%m-%d').strftime('%d-%m-%Y')
        


# Compare the dates
# if EndDate_datetime < datetime.today():
#     if datetime.today().strftime('%Y-%m-%d')
    # 'ActiveDate':WellActiveDate,
    # 'EndDate':WellEndDate
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
            value = datetime.strptime(ActivateDate, '%d-%m-%Y').date(),
            key="StartDateValues"
            )),

        "StartTime":(TimeCol.time_input(
            "Start Time",
            value = datetime.strptime('00:00', '%H:%M').time(),
            key="StartTimeValues")),
        "EndDate":(DateCol.date_input(
            "End Date",
            value = datetime.strptime(EndDate, '%d-%m-%Y').date(),
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
        if 'ActLogDF' not in st.session_state:
            st.session_state['ActLogDF'] = cache_DomeGetData_ActivityLog(WellInfoDict, UserDateRange)
            st.session_state['ActLogDF']['DateTime'] = st.session_state['ActLogDF']['Date'] + " " + st.session_state['ActLogDF']['Time']
            st.session_state['IsActLogTableReload'] = True


        with ActLogContainer:
            RTSensor_df = cache_DomeGetRealtimeSensorData_v2(WellInfoDict, UserDateRange)

        # st.write()

        # st.write(UserDateRangeJSON)
        # st.write(st.session_state['ActLogDF'])
        ActLogDF = st.session_state['ActLogDF']
        with ActLogContainer.form(key='ActivityLogTable_Agrid'):
            st.markdown('<h1 style="text-align: center; font-size: 40px; margin-top: 2px;">Major Activity Log Table</h1>', unsafe_allow_html=True)
            ActivityLog_DF = Table.ActivityLogTable_Agrid(ActLogDF, reload=st.session_state['IsActLogTableReload'])['data']
            # ActivityLog_DF = ActivityLog_DF
            # if ActivityLog_DF.empty:
            #     ActivityLog_DF = ActLogDF

  
            
            isActLogApply = st.form_submit_button("apply")
        
        # st.stop()
        if isActLogApply:
            # st.write(ActivityLog_DF)
            # st.stop()
            updateActivityLog(WellInfoDict,ActivityLog_DF,ExtendDateTime(UserDateRange.copy()))
            # cache_DomeGetData_ActivityLog.clear()
            del st.session_state['ActLogDF']
            ActLogContainer.success("Activity Log successfully updated. Please wait for the page to refresh.")
            time.sleep(1)
            ActSumClear()
            st.experimental_rerun()
        if ActivityLog_DF.empty:
            st.error("Please input the Activity Log")
            st.stop()
        st.session_state['IsActLogTableReload'] = False
        # if 
        # retrieve Realtime Sensor Data
        print("GetRealtimeData")
        print(UserDateRange)
        print("-----")
        
        # st.write(cache_DomeGetData_ActivityLog(WellInfoDict, UserDateRange))

        #######
        ## ActSumTable
        #######
        if 'ActSum' not in st.session_state:
            st.success('Calculate Activity Summary Successr')
            st.session_state['ActSum'] = cache_DomeGetData_ActivitySummary(WellInfoDict, UserDateRange,ActivityLog_DF, RTSensor_df)
            st.session_state['IsActSumReload'] = True
            st.session_state['isActSumApply'] = False
        
        # else:
        #     st.session_state['IsActSumReload'] = False

        ActSumData = st.session_state['ActSum']
        # st.write('ActSumData.Data')
        # st.write(ActSumData.Data)

        
        if not st.session_state['PopUpWindow'].is_open():
            print("model is closed")
            # st.session_state['ActSumDF_Upload'] = None
            if st.session_state.sidebar_state == 'collapsed': 
                st.session_state.sidebar_state = 'expanded'
                st.experimental_rerun()
            
        ActSumContainer.markdown('<h1 style="text-align: center; font-size: 40px; margin-top: 2px;">Activity Summary Table</h1>', unsafe_allow_html=True)
        ActSumButtonCol = ActSumContainer.columns(3)
        ActSumForm = ActSumContainer.container()

        ActSumButtonCol[0].button("Refresh", key="Refresh")
        

        with ActSumForm.form(key='ActSumTable_Agrid'):
            # ActSumAgridOut = pd.DataFrame(Table.ActSumTable_Agrid(ActSumData.Data, reload=st.session_state['IsActSumReload'])['data'])
            # ActSumAgridOut = pd.DataFrame(Table.ActSumTable_Agrid(ActSumData.getActivitySummary_v2(ActivityLog_DF, RTSensor_df), reload=st.session_state['IsActSumReload'], key='actsumtable_v2')['data'])
            ActSumAgridOut = pd.DataFrame(Table.ActSumTable_Agrid(ActSumData.Data, reload=st.session_state['IsActSumReload'], key='actsumtable_v2')['data'])
            # st.write('ActSumAgridOut')
            # st.write(ActSumAgridOut)
            ActSumAgridOut = ActivitySummary.RecalculateActSum(ActSumAgridOut, IsStatusOverride=False,MinuteTolerances=0.5, CleaningIteration=1, includeStatus=False)
            # st.write('ActSumAgridOutRecalculate')
            # st.write(ActSumAgridOut)
            st.session_state['ActSum'].Data = ActSumAgridOut
            # st.write("---")
            isActSumApply = st.form_submit_button("apply")
        # tes_df = ActSumAgridOut.
        # ActivitySummary.UploadActivitySummary(st.session_state['ActSum'].Data)

        if isActSumApply :
            st.session_state['IsActSumReload'] = True
            st.session_state['isActSumApply'] = True
            st.experimental_rerun()


        # st.stop()
        if st.session_state['isActSumApply']:
            st.session_state['IsActSumReload'] = False
            st.session_state['isActSumApply'] = False
            # ActSumAgridOut_Firm = ActSumAgridOut[ActSumAgridOut['status'] == "FIRM"]
            ActSumAgridOut =(ActivitySummary.checkActSumDF(ActSumAgridOut))
            # ActSumAgridOut =(ActivitySummary.checkActSumDF(ActSumAgridOut[ActSumAgridOut['status'] != "FIRM"]))
            print(ActSumAgridOut.columns)
            if "ErrorWarning" in (ActSumAgridOut.columns):
                st.warning("Found some Error")
                with st.expander("Please Update the following row first"):
                    # st.markdown("Please Update the following row first")
                    Table.ActSumTableConfirmation_Agrid(ActSumAgridOut[ActSumAgridOut['ErrorWarning'].notna()], showWarning=True)
            else:
                
                # st.session_state['ActSum'].Data = pd.concat([ActSumAgridOut_Firm,ActivitySummary.RecalculateActSum(ActSumAgridOut)])
                st.session_state['IsActSumNoError'] = True
                # st.stop()
        ActSumButtonColumn = st.columns(8)

        ActSumButtonColumn[0].button("save the Activity Summary", 
                                key="saveActSum", 
                                on_click=showPopupWindow, 
                                disabled=(not st.session_state['IsActSumNoError']), 
                                type='primary',
                                help= ( 'click to save' if st.session_state['IsActSumNoError'] else 'please apply change first')
                                )
        ActSumButtonColumn[1].download_button(
                                label="Download Activity Summary as CSV",
                                data=convert_df(st.session_state['ActSum'].Data),
                                file_name=SelectComp + "_"+ SelectWell + '_ActivitySummary.csv',
                                mime='text/csv',
                            )
        ActSumButtonColumn[2].download_button(
                                label="Download Raw Realtime 5s as CSV",
                                data=convert_df(RTSensor_df),
                                file_name=SelectComp + "_"+ SelectWell + '_RawREaltime5s.csv',
                                mime='text/csv',
                            )
        if st.session_state['IsActSumNoError']:
            st.success("No Error Found, Great Job!")
            # st.download_button(
            #     label="Download Activity Summary as CSV",
            #     data=convert_df(st.session_state['ActSum'].Data),
            #     file_name=SelectComp + "_"+ SelectWell + '_ActivitySummary.csv',
            #     mime='text/csv',
            # )
            st.session_state['IsActSumNoError'] = False
            
                # if not PopUpWindow.is_open():
                #     PopUpWindow.open()

        if st.session_state['PopUpWindow'].is_open():
            # st.text('tes')
            # st.stop
            ActSumAgridOut = st.session_state['ActSum'].Data
            with st.session_state['PopUpWindow'].container():
                st.markdown("### Please make sure or double check the following table is already correct.")
                # print("ErrorWarning" in (ActSumAgridOut.columns))
                # if "ErrorWarning" in (ActSumAgridOut.columns):
                #     print('ErrorWarning')
                #     Table.ActSumTableConfirmation_Agrid(ActSumAgridOut[ActSumAgridOut['status'] != "FIRM"], showWarning=True)
                # else:
                Table.ActSumTableConfirmation_Agrid(ActSumAgridOut[ActSumAgridOut['status'] != "FIRM"])
                PopUpWindowCol = st.columns(15)
                isActSumUploadConfirm = PopUpWindowCol[14].button("Confirm", key="ActSumUploadConfirm", on_click=ConfirmToSave)

                # // Table.ActSumTableConfirmation_Agrid(st.session_state['ActSumDF_Upload'])
                    # if isActSumUploadConfirm:
                    #     st.success("The Activity Summary Table has already update")
                    #     # cache_DomeGetData_ActivitySummary.clear()
                    #     del st.session_state['ActSum']
                    #     time.sleep(5)
                    #     st.session_state['PopUpWindow'].close()




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