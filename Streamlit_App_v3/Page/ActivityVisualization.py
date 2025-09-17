import streamlit as st
from PDU_Func import Activity, Authentification, IO_Data, Viz_Data
from Page.SubPage import Dashboard, ActSumTableViz
from Page import  Override
from datetime import datetime,timedelta
import streamlit_ext as ste
import pandas as pd
from importlib import reload
reload(IO_Data)
reload(Activity)
reload(Viz_Data)
reload(Dashboard)
# from streamlit_elements import elements, mui, html
# reload(RealtimeDataViz)
def IsSubmitFormTrue(UserDateRange):
    # st.session_state['IsFormSubmit'] = CheckUserDateRange(UserDateRange)
    # if st.session_state['IsFormSubmit']:
    st.session_state['IsFormSubmit'] = True


    
def RecalculateActivitySummary():
    UserAuthDict = st.session_state['UserAuthDict']
    SelectComp = st.session_state['SelComp']
    SelectWell = st.session_state['SelWell']
    WellInfoDict = IO_Data.getWellInfoDict(UserAuthDict, SelectComp, SelectWell)

    st.toast("Recalculating Activity Summary")
    list_startdatetime = [datetime.combine(st.session_state['RecalculateStrtDateRT'], st.session_state['RecalculateStrtTimeRT']).strftime('%Y-%m-%d %H:%M:%S')]
    list_enddatetime = [datetime.combine(st.session_state['RecalculateEndDateRT'], st.session_state['RecalculateEndTimeRT']).strftime('%Y-%m-%d %H:%M:%S')]
    list_startdatetime, list_enddatetime = Override.SimplifyTimeRange(list_startdatetime, list_enddatetime)
    UserDateRange = {
        'StartDate': list_startdatetime[0].split(' ')[0],
        'StartTime': list_startdatetime[0].split(' ')[1],
        'EndDate': list_enddatetime[0].split(' ')[0],
        'EndTime': list_enddatetime[0].split(' ')[1]
    }

    Final_list_startdatetime, Final_list_enddatetime = IO_Data.splitDateTime(UserDateRange, hours=24)
    print(Final_list_startdatetime, Final_list_enddatetime)
    for Final_startdatetime, Final_enddatetime in zip(Final_list_startdatetime, Final_list_enddatetime):

        # st.write(st.session_state['RecalculateStrtDateRT'], st.session_state['RecalculateStrtTimeRT'], st.session_state['RecalculateEndDateRT'], st.session_state['RecalculateEndTimeRT'])
        Override.DomeUpdateRealtimeData(WellInfoDict, 
                Final_startdatetime.strftime('%Y-%m-%d %H:%M:%S') ,
                Final_enddatetime.strftime('%Y-%m-%d %H:%M:%S'), runOnStreamlit=True)
        st.toast(f"{Final_startdatetime.strftime('%Y-%m-%d %H:%M:%S')} - {Final_enddatetime.strftime('%Y-%m-%d %H:%M:%S')} Complete!")

#     RecalculateStrtDateRT
# RecalculateStrtTimeRT
# RecalculateEndDateRT
# RecalculateEndTimeRT
    # st.toast(
    #     f"{st.session_state['RecalculateStrtDateRT']} - {st.session_state['RecalculateStrtTimeRT']} - {st.session_state['RecalculateEndDateRT']} - {st.session_state['RecalculateEndTimeRT']}"
    # )
# @st.cache_data
def cacheGetActivitySummaryData(*args, **kwargs):
    return Activity.GroupCasingJoint(IO_Data.DomeGetActivitySummaryData(*args, **kwargs))
    # return 
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
def App():
    if 'IsFormSubmit' not in st.session_state:
        st.session_state['IsFormSubmit'] = False
    UserAuthDict = st.session_state['UserAuthDict']

    SelectComp = st.session_state['SelComp']
    SelectWell = st.session_state['SelWell']
    WellInfoDict = IO_Data.getWellInfoDict(UserAuthDict, SelectComp, SelectWell)
    st.markdown('<h1 style="text-align: center; font-size: 40px; margin-top: 0px;">ACTIVITY DASHBOARD</h1>', unsafe_allow_html=True)
    WellActivityContainer = st.container(border=True)
    DatetimeRangeCol = WellActivityContainer.container()

    SectionFilter_col, DrillingCheckbox_col, TripCheckbox_col, TableCheckbox_col = WellActivityContainer.columns([3, 2.2,2.2,2.2], vertical_alignment="bottom")
    with DrillingCheckbox_col:
        st.checkbox("Display Drilling Chart", key="DrillingCheckbox", value=True)
    with TripCheckbox_col:
        st.checkbox("Display Trip Chart", key="TripCheckbox", value=True)
    with TableCheckbox_col:
        st.checkbox("Activity Summary Table", key="TableCheckbox", value=True)

    ActivateDate = datetime.strptime(WellInfoDict['ActiveDate'], '%Y-%m-%d').strftime('%d-%m-%Y')
    if datetime.strptime(WellInfoDict['EndDate'], '%Y-%m-%d') > datetime.today():
        EndDate = datetime.today().strftime('%d-%m-%Y')
    else:
        EndDate = datetime.strptime(WellInfoDict['EndDate'], '%Y-%m-%d').strftime('%d-%m-%Y')
    with DatetimeRangeCol.form(key='DateForm', border=False):

        TitleCol, StartDateCol,StartTimeCol, MiddleCol, EndDateCol, EndTimeCol, BtnSubmitCol = st.columns([1.2, 1.4,1,0.1,1.4,1,0.7])
        TitleCol.markdown('## WELL ACTIVITY')
        # TitleCol.markdown('<h3 style="text-align: left; font-size: 40px; margin-top: -10px;">WELL ACTIVITY</h3>', unsafe_allow_html=True)
        RealtimeLoadingContainer = st.empty()

        UserDateRange = {}
        StartDateCol.markdown("**Start** Datetime")
        StartTimeCol.markdown('<h7 style="text-align: center; font-size: 15px; margin-top: 0px;opacity: 0;">-</h7>', unsafe_allow_html=True)
        

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
                                        "",
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
                                        "",
                                        label_visibility='collapsed',
                                        # "End Time",
                                        value = datetime.strptime('23:59', '%H:%M').time(),
                                        key="EndTimeRT")

        BtnSubmitCol.form_submit_button(on_click=IsSubmitFormTrue, 
                                           args=(UserDateRange,), 
                                           use_container_width=True, 
                                           type="secondary" if st.session_state['IsFormSubmit'] else "primary")
        st.session_state['StrtDateRT'] = st.session_state['SYNC_StrtDateRT']
        st.session_state['StrtTimeRT'] = st.session_state['SYNC_StrtTimeRT']
        st.session_state['EndDateRT'] = st.session_state['SYNC_EndDateRT']
        st.session_state['EndTimeRT'] = st.session_state['SYNC_EndTimeRT']
    if not st.session_state['IsFormSubmit']:
        st.warning("Please select a date range")
    else:
        validate_start_end_dates(UserDateRange)
        ActivitySummary_DF = cacheGetActivitySummaryData(WellInfoDict, UserDateRange)
        if ActivitySummary_DF.empty:
            st.warning("No data available for the selected date range.")
            st.stop()
        SectionFilter_col.selectbox("Section Filter", options=['All'] + ActivitySummary_DF['Section'].unique().tolist(), key="SectionFilter", index=0)
        if st.session_state['SectionFilter'] is not 'All':
            ActivitySummary_DF = ActivitySummary_DF[ActivitySummary_DF['Section'] == st.session_state['SectionFilter']]


        # DashboardButtonCol, TableButtonCol = st.columns(2)
        # DashboardTab, TableTab = st.tabs(["Dashboard", "Table"])
        DashboardTab = st.container()
        TableTab = st.container()
        # with DashboardButtonCol:
        #     st.button("Dashboard", on_click=st.experimental_rerun, use_container_width=True)
        # with TableButtonCol:
        #     st.button("Table", on_click=st.experimental_rerun, use_container_width=True)

        # Dashboard.SingleWellChart(ActivitySummary_DF)
        with TableTab:
            ActSumTableViz.App(ActivitySummary_DF, WellInfoDict, UserAuthDict)


            with st.expander("Recalculate Activity Summary Form").form(key='RecalculateForm', border=False):
                RecalculateUserDateRange = {}
                RecalculateStartDateCol,RecalculateStartTimeCol, RecalculateMiddleCol, RecalculateEndDateCol, RecalculateEndTimeCol, RecalculateSubmitCol = st.columns([ 1.4,1,0.1,1.4,1, 1], vertical_alignment="bottom")
                
                RecalculateStartDateCol.markdown("**Start** Datetime")
                RecalculateStartTimeCol.markdown('<h7 style="text-align: center; font-size: 15px; margin-top: 0px;opacity: 0;">-</h7>', unsafe_allow_html=True)
                

                RecalculateEndDateCol.markdown("**End** Datetime:")
                RecalculateEndTimeCol.markdown('<h7 style="text-align: center; font-size: 15px; margin-top: 0px;opacity: 0;">-</h7>', unsafe_allow_html=True)
                with RecalculateStartDateCol:
                    RecalculateUserDateRange['StartDate'] = st.date_input(
                                                "**Start** Datetime",
                                                label_visibility='collapsed',
                                                # "Start Date",
                                                value = datetime.strptime(EndDate, '%d-%m-%Y').date(),
                                                key="RecalculateStrtDateRT"
                                                )
                with RecalculateStartTimeCol:
                    RecalculateUserDateRange['StartTime'] = st.time_input(
                                                "",
                                                # "Start Time",
                                                label_visibility='collapsed',
                                                value = datetime.strptime('00:00', '%H:%M').time(),
                                                key="RecalculateStrtTimeRT")
                    
                with RecalculateEndDateCol:
                    RecalculateUserDateRange['EndDate'] = st.date_input(
                                                "**End** Datetime",
                                                label_visibility='collapsed',
                                                # "End Date",
                                                value = datetime.strptime(EndDate, '%d-%m-%Y').date(),
                                                key="RecalculateEndDateRT")
                with RecalculateEndTimeCol:
                    RecalculateUserDateRange['EndTime'] = st.time_input(
                                                "",
                                                label_visibility='collapsed',
                                                # "End Time",
                                                value = datetime.strptime('23:59', '%H:%M').time(),
                                                key="RecalculateEndTimeRT")

                RecalculateSubmitCol.form_submit_button(on_click=RecalculateActivitySummary, 
                                                 
                                                use_container_width=True, 
                                                type="primary")

        with DashboardTab:
            Dashboard.SingleWellChart(ActivitySummary_DF, 
                                      UserDateRange, 
                                      DisplayDrillingChart=st.session_state['DrillingCheckbox'], 
                                      DisplayTripChart=st.session_state['TripCheckbox'])

        # st.write(ActivitySummary_DF)
        # st.plotly_chart(
        #     Viz_Data.getDurationPieChart(
        #                     ActivitySummary_DF, 
        #                     'LABEL_Activity', 
        #                     Title='', 
        #                     DurationCol='Duration', 
        #                     height=400,
        #                     width=400,
        #                     hole=0.5),
        #                     use_container_width=True
        # )
        # st.plotly_chart(
        #     Viz_Data.getDurationPieChart(
        #                     ActivitySummary_DF, 
        #                     'LABEL_SubActivity', 
        #                     Title='', 
        #                     DurationCol='Duration', 
        #                     height=400,
        #                     width=400,
        #                     hole=0.5),
        #                     use_container_width=True
        # )
        # First, import the elements you need
