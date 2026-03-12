import streamlit as st
from PDU_Func import Activity, Authentification, IO_Data
from Page import  Override
from Page.SubPage import RealtimeDataViz, ActSumTableViz, RigActivityTable
from importlib import reload
import pandas as pd
from datetime import datetime,timedelta
# from streamlit_date_picker import date_range_picker, PickerType, Unit, date_picker
from stqdm import stqdm
from time import sleep
import streamlit_ext as ste
reload(IO_Data)
reload(Activity)
reload(Override)
reload(RealtimeDataViz)
# @st.cache_data(show_spinner="Retrieve Rig Activity")
def cache_getRigActivity(WellInfoDict, **kwargs):
    return IO_Data.getRigActivity(WellInfoDict, **kwargs)

@st.cache_data(show_spinner="Retrieve Well Parameters")
def cache_getWellParams(WellInfoDict, **kwargs):
    return IO_Data.DomeGetActivityLogData(WellInfoDict, **kwargs)

# @st.cache_data(show_spinner="Retrieve Realtime Sensor Data")
def cache_DomeGetRealtimeSensorData(WellInfoDict,UserDateRange, **kwargs):
    return IO_Data.DomeGetRealtimeSensorData(WellInfoDict, UserDateRange, **kwargs)

# @st.cache_data(show_spinner="Retrieve Override Activity Data")
def cache_DomeOverrideActivity_Get(WellInfoDict, **kwargs):
    return IO_Data.DomeOverrideActivity_Get(WellInfoDict, **kwargs)
def IsSubmitFormTrue(UserDateRange):
    # st.session_state['IsFormSubmit'] = CheckUserDateRange(UserDateRange)
    # if st.session_state['IsFormSubmit']:
    st.session_state['IsFormSubmit'] = True
    # cache_DomeGetRealtimeSensorData.clear()
def validate_start_end_dates(UserDateRange):
    """
    Check if StartDateTime is less than EndDateTime.

    Parameters:
    UserDateRange (dict): A dictionary containing the start and end dates and times.

    Returns:
    bool: True if StartDateTime < EndDateTime, False otherwise.
    """

    # Combine date and time for start and end to form complete datetime objects
    startDateTime = datetime.combine(UserDateRange['StartDate'], UserDateRange['StartTime'])
    endDateTime = datetime.combine(UserDateRange['EndDate'], UserDateRange['EndTime'])

    # Check if startDateTime is less than endDateTime
    if startDateTime >= endDateTime:
        st.error("***Start*** *Datetime* must be less than ***End*** *Datetime*. Please adjust the dates/times.")
        st.stop()
    # Check if the range is more than 2 days
    if (endDateTime - startDateTime) > timedelta(days=2):
        st.error("Date range cannot be more than ***48 hours***. Please adjust the dates/times.")
        st.stop()
        # return False

def resetDataEditorKey(WellInfoDict, InitialKey = 'SectionParamsEdit', PrefixKey = 'OverrideActivityTable'):
        # st.session_state["SectionParams_DF"] = cache_getWellParams(WellInfoDict, start_date="2000-01-01 00:00:01", end_date="2100-01-01 00:00:01")
        # cache_getWellParams.clear()
        # cache_DomeGetRealtimeSensorData.clear()
        # cache_getRigActivity.clear()
        try:
            num = int(st.session_state['DataEditorKey'].split('_')[1]) + 1
        except:
            st.write(st.session_state['DataEditorKey'])
            st.stop()
        st.session_state['DataEditorKey'] = InitialKey + f"_{num}"
        if f"{PrefixKey}_DataEditor" in st.session_state:
            del st.session_state[f"{PrefixKey}_DataEditor"]

        if f"{PrefixKey}_df" in st.session_state:
            del st.session_state[f"{PrefixKey}_df"]
        if 'OverrideActivityTable_df' in st.session_state:
            del st.session_state['OverrideActivityTable_df']

def initiateDataEditorKey(InitialKey = 'SectionParamsEdit'):
    if 'DataEditorKey' not in st.session_state:
        st.session_state['DataEditorKey'] = InitialKey + f"_{0}"
def getDataEditorKey():
    return st.session_state['DataEditorKey']


def DomeUpdateSectionParamsDF(WellInfoDict, SectionParams_DF, updateDict):
    SectionParams_DF = SectionParams_DF.copy()
    # st.write(SectionParams_DF)
    # delete row 
    for i in updateDict['deleted_rows']:
        row_id = SectionParams_DF.loc[i]['id']
        IO_Data.DomeDeleteActivityLogData(WellInfoDict, row_id)
    # updated row
    for row_index in updateDict['edited_rows'].keys():
        for column in updateDict['edited_rows'][row_index].keys():
            SectionParams_DF.at[int(row_index), column] = updateDict['edited_rows'][row_index][column]
        row_id = SectionParams_DF.loc[row_index]['id']
        IO_Data.DomeDeleteActivityLogData(WellInfoDict, row_id)
    # st.stop()
    # add row 
    # st.write(updateDict)
    editedSectionParams_DF = SectionParams_DF.loc[updateDict['edited_rows'].keys()]
    addSectionParams_DF = pd.DataFrame(updateDict['added_rows'], columns=SectionParams_DF.columns)
    # st.write(editedSectionParams_DF)
    # st.write(editedSectionParams_DF.empty)
    if not editedSectionParams_DF.empty:
        IO_Data.DomeInsertActivityLogData(WellInfoDict, editedSectionParams_DF)
    if not addSectionParams_DF.empty:
        IO_Data.DomeInsertActivityLogData(WellInfoDict, addSectionParams_DF)
    # st.stop()

def SectionParamsDataEditor(WellInfoDict, SectionParams_DF):
    SectionSizeList=['36"', '26"','17-1/2"','12-1/4"','9-7/8"', '7-7/8"', '8.5"','6-3/4"', '6-1/8"','6"', ]
    column_config={
        "DateTime": st.column_config.DatetimeColumn(
            "Datetime",
            # min_value=datetime(2023, 6, 1),
            # max_value=datetime(2025, 1, 1),
            format="D MMM YYYY, hh:mm a",
            step=5,
             required=True,
        ),
        "Section Size": st.column_config.TextColumn(
            "Section Size",
            help="Select the well section size",
            width="medium",
            validate='*"',
            # options=SectionSizeList,
            required=True,
        ),
        "In-Slip Threshold": st.column_config.NumberColumn(
            "In-Slip Threshold",
            help="In-Slip Threshold",
            min_value=0,
            max_value=1000,
            step=1,
             required=True,
        )
    }
   
    with st.form(key='SectionParamsFormKey', border=False):
        
        SectionParamsEdit = st.data_editor(SectionParams_DF[['DateTime', 'Section Size', 'In-Slip Threshold', 'In-Slip Run Casing Threshold']].sort_values(by='DateTime', ascending=False),
                                           hide_index=True,
                                         num_rows='dynamic', key=getDataEditorKey(),
                                        column_config=column_config,
                                        height=200,
                                        use_container_width=True,
                                        )
        if st.form_submit_button(label='Submit'):
            DomeUpdateSectionParamsDF(WellInfoDict, SectionParams_DF, st.session_state[getDataEditorKey()])
            
            resetDataEditorKey(WellInfoDict,)
            st.rerun()



def App():
    initiateDataEditorKey()

    UserAuthDict = st.session_state['UserAuthDict']
    SelectComp = st.session_state['SelComp']
    SelectWell = st.session_state['SelWell']
    WellInfoDict = IO_Data.getWellInfoDict(UserAuthDict, SelectComp, SelectWell)
    # IO_Data.initiateTable(WellInfoDict)
    # st.write(WellInfoDict)
    # st.write(IO_Data.DomeCheckTable(WellInfoDict['wid'], table_type="ActivityLogTable"))
    # st.stop()
    # SectionParams_DF = pd.read_excel('Data/SectionParams.xlsx')

    # SectionParams_DF = cache_getWellParams(WellInfoDict, start_date="2000-01-01 00:00:01", end_date="2100-01-01 00:00:01")
    # if "SectionParams_DF" not in st.session_state:
    #     st.session_state["SectionParams_DF"] = cache_getWellParams(WellInfoDict, start_date="2000-01-01 00:00:01", end_date="2100-01-01 00:00:01")
    # SectionParams_DF = cache_getWellParams(WellInfoDict, start_date="2000-01-01 00:00:01", end_date="2100-01-01 00:00:01")
    # SectionParams_DF = cache_getWellParams(WellInfoDict, start_date="2000-01-01 00:00:01", end_date="2100-01-01 00:00:01")
    # if "SectionParamsTable_df" not in st.session_state:
    #     st.session_state["SectionParamsTable_df"] =  IO_Data.DomeSectionParamsTable_Get(WellInfoDict)
    SectionParams_DF = IO_Data.DomeSectionParamsTable_Get(WellInfoDict)
    if st.sidebar.button("🔄 Refresh Data", key="RefreshSectionParamsTable", on_click=resetDataEditorKey, args=(WellInfoDict,)):
        st.rerun()
    

    # st.stop()
    # st.markdown("# ACTIVITY MAPPING")
    st.markdown('<h1 style="text-align: center; font-size: 40px; margin-top: 0px;">ACTIVITY MAPPING</h1>', unsafe_allow_html=True)
    # UserAuthDict = st.session_state['UserAuthDict']
    RigName = WellInfoDict['RigName'].values.tolist()[0]

    RigActivity_DF = (cache_getRigActivity(WellInfoDict, 
                   start_date="2000-01-01 00:00:01", 
                   end_date="2100-01-01 00:00:01"))
    # st.dataframe(SectionParams_DF)

    RigActivityCols = st.container(border=False).columns([5,5],)
    if RigActivity_DF.empty:
        RigActivityCols[0].error("No Rig Activity")
    RigActivityCols[1].markdown(f"##### Well Name: *{SelectWell}*")
    # RigNameCols, IsRigEditCol = RigActivityCols[0].columns([7,3], vertical_alignment='center') 
    # RigNameCols.markdown(f"##### Rig Name: *{RigName}*")
    # if RigActivity_DF.empty:
    #     RigNameCols.error("No Rig Activity")

    # RigActivityCols[1].markdown(f"##### Well Name: *{SelectWell}*")

    RigActivity_DF_Display = RigActivity_DF.copy()
    RigActivity_DF_Display['Detail Rig Activity'] = RigActivity_DF_Display['Activity']
    RigActivity_DF_Display['Simple Activity'] = Activity.translateRigActivity2Activity(RigActivity_DF_Display)['Activity']
    # st.write()
    # RigActivity_DF_Display['Simple Activity'] = RigActivity_DFg
    # RigActivityCols[0].dataframe(RigActivity_DF_Display[['DateTime', 'Detail Rig Activity', 'Simple Activity']].sort_values(by='DateTime', ascending=False),
    #                 use_container_width=True,
    #                 hide_index=True,
    #                 height=200,
    #                 column_config={
    #                     "DateTime": st.column_config.DatetimeColumn(
    #                         "DateTime",
    #                         format="YYYY-MM-DD | HH:mm:ss",
    #                         )
    #                     }
                    
    #                )
    # with IsRigEditCol.container(horizontal_alignment='right'):
    #     IsRigActivityEdit = st.toggle("Edit Rig Activity", key="IsRigActivityEdit")
    with RigActivityCols[0]:
        # IsRigActivityEdit = st.toggle("Edit Rig Activity", key="IsRigActivityEdit")
        RigActivityTable.App(WellInfoDict,
                             RigName, 
                             RigActivity_DF_Display, 
                             is_editable = True
                             )

    # st.stop()
    Override.SectionParamsTableWidget(WellInfoDict, RigActivityCols[1], 
                          PrefixKey = 'SectionParamsTable' , 
                          SectionSizeList='default',)
    if RigActivity_DF.empty or SectionParams_DF.empty:
        st.stop()

    WellActivityContainer = st.container(border=True)
    DatetimeRangeCol = WellActivityContainer.container()


    # WellActivityHeaderCol[0].markdown("### WELL ACTIVITY")


    ActivateDate = datetime.strptime(WellInfoDict['ActiveDate'], '%Y-%m-%d').strftime('%d-%m-%Y')
    if datetime.strptime(WellInfoDict['EndDate'], '%Y-%m-%d') > datetime.today():
        EndDate = datetime.today().strftime('%d-%m-%Y')
    else:
        EndDate = datetime.strptime(WellInfoDict['EndDate'], '%Y-%m-%d').strftime('%d-%m-%Y')
        
    if 'IsFormSubmit' not in st.session_state:
        st.session_state['IsFormSubmit'] = False
    with DatetimeRangeCol.form(key='DateForm', border=False):

        TitleCol, StartDateCol,StartTimeCol, MiddleCol, EndDateCol, EndTimeCol, BtnSubmitCol = st.columns([1.5,  1.4,1,0.1,1.4,1,0.7],vertical_alignment='center' )
        TitleCol.markdown('### DATETIME SELECTION')
        # TitleCol.markdown('<h3 style="text-align: left; font-size: 40px; margin-top: -10px;">WELL ACTIVITY</h3>', unsafe_allow_html=True)
        RealtimeLoadingContainer = st.empty()

        UserDateRange = {}
        StartDateCol.markdown("**Start** Datetime")
        StartTimeCol.markdown('<h7 style="text-align: center; font-size: 15px; margin-top: 0px;opacity: 0;">-</h7>', unsafe_allow_html=True)
        
        # MiddleCol.markdown('<h7 style="text-align: center; font-size: 15px; margin-top: 0px;opacity: 0;">-</h7>', unsafe_allow_html=True)
        # # MiddleCol.markdown('<h7 style="text-align: center; font-size: 20px; margin-top: 0px;">-----→</h7>', unsafe_allow_html=True)
        # MiddleCol.markdown('### --→')

        EndDateCol.markdown("**End** Datetime:")
        EndTimeCol.markdown('<h7 style="text-align: center; font-size: 15px; margin-top: 0px;opacity: 0;">-</h7>', unsafe_allow_html=True)

        BtnSubmitCol.markdown('<h7 style="text-align: center; font-size: 15px; margin-top: 0px;opacity: 0;">-</h7>', unsafe_allow_html=True)
        with StartDateCol:
            UserDateRange['StartDate'] = ste.date_input(
                                        "**Start** Datetime",
                                        label_visibility='collapsed',
                                        # "Start Date",
                                        value = datetime.strptime(ActivateDate, '%d-%m-%Y').date(),
                                        key="StrtDateRT"
                                        )
        with StartTimeCol:
            UserDateRange['StartTime'] = ste.time_input(
                                        "-",
                                        # "Start Time",
                                        label_visibility='collapsed',
                                        value = datetime.strptime('00:00', '%H:%M').time(),
                                        key="StrtTimeRT")
            
        with EndDateCol:
            UserDateRange['EndDate'] = ste.date_input(
                                        "**End** Datetime",
                                        label_visibility='collapsed',
                                        # "End Date",
                                        value = datetime.strptime(EndDate, '%d-%m-%Y').date(),
                                        key="EndDateRT")
        with EndTimeCol:
            UserDateRange['EndTime'] = ste.time_input(
                                        "--",
                                        label_visibility='collapsed',
                                        # "End Time",
                                        value = datetime.strptime('23:59', '%H:%M').time(),
                                        key="EndTimeRT")

        BtnSubmitCol.form_submit_button(on_click=IsSubmitFormTrue, 
                                           args=(UserDateRange,), 
                                           use_container_width=True, 
                                           type="secondary" if st.session_state['IsFormSubmit'] else "primary")
        # st.write(st.session_state)
        st.session_state['StrtDateRT'] = st.session_state['SYNC_StrtDateRT']
        st.session_state['StrtTimeRT'] = st.session_state['SYNC_StrtTimeRT']
        st.session_state['EndDateRT'] = st.session_state['SYNC_EndDateRT']
        st.session_state['EndTimeRT'] = st.session_state['SYNC_EndTimeRT']
    if not st.session_state['IsFormSubmit']:
        st.warning("Please select a date range")
    else:
        validate_start_end_dates(UserDateRange)
        RTSensor_DF = IO_Data.DomeGetRealtimeSensorData(WellInfoDict,
                                                      UserDateRange, 
                                                      hours=0.5, 
                                                      show_progress=False, 
                                                      runOnStreamlit=True,
                                                      _container=RealtimeLoadingContainer
                                                      )

        RealtimeLoadingContainer.empty()
        # InputActivity_DB = ActivityMapping.translateRigActivity2Activity(RigActivity_DF)
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
        # WellActivityContainer.divider()
        # WellActivityContainer.write("#### Realtime Activity Data")
        # RTDataContainer,RTVizContainer = WellActivityContainer.tabs(['Table', 'Visualization'])
        RTVizContainer = st.container().expander("📊 Realtime Drilling Data Visualization", expanded=False)
        RTDataContainer = st.container().expander("📅 Realtime Drilling Data Table ", expanded=False)

        with RTDataContainer: 
            st.dataframe(RTSensor_DF, height = 300,)
        with RTVizContainer:
            RealtimeDataViz.App(st, RTSensor_DF)
        # RealtimeActTabs[1].RealtimeDataViz

        
        # st.write(OverridedActivity_df)
        # st.write(st.session_state['OverridedActivity_df'])
        # st.stop()
        if 'OverrideActivityTable_df' not in st.session_state:
            st.session_state['OverrideActivityTable_df'] = IO_Data.DomeOverrideActivity_Get(WellInfoDict)
        Override_df = st.session_state['OverrideActivityTable_df']
        RTSensor_DF = Activity.Override(RTSensor_DF, Override_df)
        ActivitySummary_DF= Activity.groupActivity(RTSensor_DF , DrillActivityList='default')
        ActivitySummary_DF = Activity.cleanFalseSensor(ActivitySummary_DF)
        ActivitySummary_DF = Activity.getStandLabel(ActivitySummary_DF)
        ActivitySummary_DF = Activity.GroupCasingJoint(ActivitySummary_DF)
        # GroupCasingJoint(ActSum_df)
        st.write("##### Activity Summary")
        ActivitySummaryTable, ActivitySummaryOverrideTable = st.tabs(['Table','Override Table'])
        with ActivitySummaryTable:
            with st.container(border=None):
                ActSumTableViz.App(ActivitySummary_DF, WellInfoDict, UserAuthDict, RemarksEdit=False)
        with ActivitySummaryOverrideTable:
            with st.container(border=None):
                Override.OverrideActivityTableWidget(WellInfoDict, st.container(), 
                            PrefixKey = 'OverrideActivityTable' , 
                            TripActivityList='default', DrillActivityList='default', OverrideActivityList='default')
            # OverridedActivity_df = pd.DataFrame(columns=['StartDateTime','EndDateTime','Activity','SubActivity'], )
            # with st.form(key='OverridedActivityForm'):
            #     OverrideActivityForm_ColumnConfig = {
            #                                             "StartDateTime": st.column_config.DatetimeColumn(
            #                                                 "StartDateTime",
            #                                                 format="D MMM YYYY, h:mm:ss",
            #                                                 step=60,
            #                                             ),
            #                                         }
            #     OverridedActivity_df = st.data_editor(OverridedActivity_df,column_config=OverrideActivityForm_ColumnConfig,  key="OverridedActivity_df", num_rows='dynamic')
            #     st.form_submit_button(label='Submit')
        # ActivitySummary_DFColumnShow = [
        #     "StartDateTime","EndDateTime", "Duration", 'Hole_Depth_max', "Bit_Depth_avg", "DrillingMeterage"
        # ]
        # StartDateTime
        # EndDateTime
        # Duration
        # Hole_Depth_max
        # Bit_Depth_avg
        # DrillingMeterage
        # RotateDrillingDuration
        # SlideDrillingDuration
        # ReamingDuration
        # ConnectionDuration
        # LABEL_SubActivity
        # LABEL_Activity
        # LABEL_ConnectionActivity
        # InSlip_Treshold
        # DrillingMeteragePerStand
        # StandDuration
        # OnBottomDurationPerStand
        # Stand Group_Pred
        # st.write(ActivitySummary_DF.columns)
        
        # st.button("Upload Activity Summary", on_click=IO_Data.DomeInsertActivitySummaryData, args=(WellInfoDict, ActivitySummary_DF ))







        st.stop()
        # RealtimeDF = IO_Data.DomeGetRealtimeSensorData(WellInfoDict, UserDateRange, hours=1)
        # RealtimeDF


            # for _ in stqdm(range(15)):
        st.markdown("#### Activity Summary Table")
        st.dataframe(RigActivity_DF[['DateTime', 'Activity']].sort_values(by='DateTime', ascending=False),
                    use_container_width=True,
                    hide_index=True,
                    height=200,
                    column_config={
                        "DateTime": st.column_config.DatetimeColumn(
                            "DateTime",
                            format="D MMM YYYY, h:mm a",
                            )
                        }
                    
                    )
        with st.expander("Override Activity Data"):
            # st.image('Data\MockupActivityMapping.png', caption='Activity Mapping')
            st.dataframe(RigActivity_DF[['DateTime', 'Activity']].sort_values(by='DateTime', ascending=False),
                        use_container_width=True,
                        hide_index=True,
                        height=200,
                        column_config={
                            "DateTime": st.column_config.DatetimeColumn(
                                "DateTime",
                                format="D MMM YYYY, h:mm a",
                                )
                            }
                        
                        )
        # if 'IsFormSubmit' not in st.session_state:
        #     st.session_state['IsFormSubmit'] = False

        # st.write(st.session_state)
        st.stop()