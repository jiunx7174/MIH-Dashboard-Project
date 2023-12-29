import streamlit as st
from PDU_Func import Activity, Authentification, IO_Data
from importlib import reload
import pandas as pd
from datetime import datetime,timedelta
from streamlit_date_picker import date_range_picker, PickerType, Unit, date_picker
from stqdm import stqdm
from time import sleep
import streamlit_ext as ste
reload(IO_Data)
reload(Activity)
@st.cache_data(show_spinner="Retrieve Rig Activity")
def cache_getRigActivity(WellInfoDict, **kwargs):
    return IO_Data.getRigActivity(WellInfoDict, **kwargs)

# @st.cache_data(show_spinner="Retrieve Realtime Sensor Data")
def cache_DomeGetRealtimeSensorData(WellInfoDict,UserDateRange, **kwargs):
    return IO_Data.DomeGetRealtimeSensorData(WellInfoDict, UserDateRange, **kwargs)
def IsSubmitFormTrue(UserDateRange):
    # st.session_state['IsFormSubmit'] = CheckUserDateRange(UserDateRange)
    # if st.session_state['IsFormSubmit']:
    st.session_state['IsFormSubmit'] = True
    # cache_DomeGetRealtimeSensorData.clear()
def App():
    UserAuthDict = st.session_state['UserAuthDict']
    SelectComp = st.session_state['SelComp']
    SelectWell = st.session_state['SelWell']
    WellInfoDict = IO_Data.getWellInfoDict(UserAuthDict, SelectComp, SelectWell)
    SectionParams_DF = pd.read_excel('Data/SectionParams.xlsx')
    st.markdown("# ACTIVITY MAPPING")
    # UserAuthDict = st.session_state['UserAuthDict']
    RigName = WellInfoDict['RigName'].values.tolist()[0]
    # st.write()
    st.divider()
    # st.markdown(f"##### RIG ACTIVITY [*{RigName}*]")
    RigActivity_DF = (cache_getRigActivity(WellInfoDict, 
                   start_date="2000-01-01 00:00:01", 
                   end_date="2100-01-01 00:00:01"))
    if RigActivity_DF.empty:
        st.error("No Rig Activity")
        st.stop()
    # st.dataframe(SectionParams_DF)
    RigActivityCols = st.columns([7,3])
    RigActivityCols[0].markdown(f"##### Rig Status: *{RigName}*")
    RigActivityCols[0].dataframe(RigActivity_DF[['DateTime', 'Activity']].sort_values(by='DateTime', ascending=False),
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
    RigActivityCols[1].markdown(f"##### Well Parameters: *{SelectWell}*")
    RigActivityCols[1].dataframe(SectionParams_DF[['DateTime', 'Section Size', 'In-Slip Threshold']].sort_values(by='DateTime', ascending=False),
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
    # st.markdown("#### EPI-9")
    st.divider()
    # st.markdown("## WELL ACTIVITY")
    WellActivityHeaderCol = st.columns([6,5])
    DatetimeRangeCol = st.container()


    WellActivityHeaderCol[0].markdown("### WELL ACTIVITY")


    ActivateDate = datetime.strptime(WellInfoDict['ActiveDate'], '%Y-%m-%d').strftime('%d-%m-%Y')
    if datetime.strptime(WellInfoDict['EndDate'], '%Y-%m-%d') > datetime.today():
        EndDate = datetime.today().strftime('%d-%m-%Y')
    else:
        EndDate = datetime.strptime(WellInfoDict['EndDate'], '%Y-%m-%d').strftime('%d-%m-%Y')
        
    if 'IsFormSubmit' not in st.session_state:
        st.session_state['IsFormSubmit'] = False
    with DatetimeRangeCol.form(key='DateForm'):
        # StartHeaderCol, EndHeaderCol = st.columns([4,3])
        # StartHeaderCol.markdown("##### Start Datetime:")
        # EndHeaderCol.markdown("##### End Datetime:")
        StartDateCol,StartTimeCol, MiddleCol, EndDateCol, EndTimeCol = st.columns([2,1,1,2,1])
        RealtimeLoadingContainer = st.empty()
        # st.session_state['UserDateRange'] = {
        # MiddleCol.markdown('<h1 style="text-align: center; font-size: 40px; margin-top: 2px;">➡️</h1>', unsafe_allow_html=True)
        MiddleCol.markdown('<h2 style="text-align: center; font-size: 40px; margin-top: 2px;">--→</h2>', unsafe_allow_html=True)
        # MiddleCol.markdown("# ➡️")
        UserDateRange = {}
        with StartDateCol:
            UserDateRange['StartDate'] = ste.date_input(
                                        "**Start** Datetime",
                                        # "Start Date",
                                        value = datetime.strptime(ActivateDate, '%d-%m-%Y').date(),
                                        key="StrtDateRT"
                                        )
        with StartTimeCol:
            UserDateRange['StartTime'] = ste.time_input(
                                        "",
                                        # "Start Time",
                                        label_visibility='hidden',
                                        value = datetime.strptime('00:00', '%H:%M').time(),
                                        key="StrtTimeRT")
            
        with EndDateCol:
            UserDateRange['EndDate'] = ste.date_input(
                                        "**End** Datetime",
                                        # "End Date",
                                        value = datetime.strptime(EndDate, '%d-%m-%Y').date(),
                                        key="EndDateRT")
        with EndTimeCol:
            UserDateRange['EndTime'] = ste.time_input(
                                        "",
                                        label_visibility='hidden',
                                        # "End Time",
                                        value = datetime.strptime('23:59', '%H:%M').time(),
                                        key="EndTimeRT")

        st.form_submit_button(on_click=IsSubmitFormTrue, args=(UserDateRange,))

    if not st.session_state['IsFormSubmit']:
        st.warning("Please select a date range")
    else:
        RTSensor_DF = cache_DomeGetRealtimeSensorData(WellInfoDict,UserDateRange, hours=0.5, show_progress=True, container=RealtimeLoadingContainer)
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
        st.write("##### Realtime Activity Data")
        RealtimeActTabs = st.tabs(['Table', 'Visualization'])
        RealtimeActTabs[0].write(RTSensor_DF)
        RealtimeActTabs[1].image('Data\MockupRealtimeData.png', caption='Realtime')
        ActivitySummary_DF= Activity.groupActivity(RTSensor_DF , DrillActivityList='default')
        st.write("##### Activity Summary")
        st.write(ActivitySummary_DF)
        



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

        st.write(st.session_state)
        st.stop()