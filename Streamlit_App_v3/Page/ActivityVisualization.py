import streamlit as st
from PDU_Func import Activity, Authentification, IO_Data, Viz_Data
from Page.SubPage import Dashboard
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



@st.experimental_fragment
def ActSumColumnSelectionWidget(ActivitySummary_DF):
    
    TableContainer, ColumnSelectionContainer = st.columns([6, 1])
    ColumnRename_dict = {'Date':'Date',
    'StartDateTime':'Start Datetime',
    'EndDateTime':'End Datetime',
    'Duration':'Duration(s)',
    'Hole_Depth_max':'Hole Depth (Max)',
    'Bit_Depth_avg':'Bit Depth (Avg)',
    'DrillingMeterage':'Drilling Meterage (m)',
    'RotateDrillingDuration':'Rotate Drilling Duration (s)',
    'SlideDrillingDuration':'Slide Drilling Duration (s)',
    'ReamingDuration':'Reaming Duration(s)',
    'DrillingMeteragePerStand':'Total Drilling Meterage per. Stand',
    'OnBottomDurationPerStand':'Total On-Bottom Duration per. Stand',
    'StandDuration':'Total Duration per. Stand',
    'Stand Group_Pred':'Stand Group ID',
    'LABEL_ConnectionActivity':'Connection Group ID',
    'ConnectionDuration':'Connection Duration (s)',
    'LABEL_SubActivity':'Sub-Activity Group',
    'LABEL_Activity':'Activity Group',
    'InSlip_Treshold':'In-Slip Threshold',
    'stand_on_bottom':'?',
    'PIC':'PIC',
    'Section':'Section Size',
    'Remarks':'Remarks',}

    DatetimeColSelect_df = pd.DataFrame({
        'ColumnName': ['Date',
                        'StartDateTime',
                        'EndDateTime',
                        'Duration',
                        ],
        "Display": [False, True, True, True],
    })

    BitPosColSelect_df = pd.DataFrame({
        'ColumnName': [
            'Hole_Depth_max',
            'Bit_Depth_avg',
        ],
        "Display":[True, True]
    })



    DrillingOpsColSelect_df = pd.DataFrame({
        'ColumnName':['DrillingMeterage',
        'RotateDrillingDuration',
        'SlideDrillingDuration',
        'ReamingDuration',
        'DrillingMeteragePerStand',
        'OnBottomDurationPerStand',
        'StandDuration',
        'Stand Group_Pred',
        'LABEL_ConnectionActivity',
        'ConnectionDuration',],
        "Display":[False, False, False, False, False, False, False, False, False, False]
    })
    ActivityColSelect_df = pd.DataFrame({
        'ColumnName':['LABEL_SubActivity',
                        'LABEL_Activity'],
        "Display":[True, True]

    })
    AdditionalColSelect_df = pd.DataFrame({
        'ColumnName':['InSlip_Treshold',
                        'stand_on_bottom',
                        'PIC',
                        'Section',
                        'Remarks'],
        "Display":[True, True, True, True, True]
    })
    ColumnConfig = {
        'ColumnName': st.column_config.TextColumn(
            label="Column Name",
            disabled=True,
        ),
        'Display': st.column_config.CheckboxColumn(
            label="Display",
            disabled=False,
        ),
    }

    with ColumnSelectionContainer.popover("Datetime Columns", use_container_width=True):
        FinalDatetimeColSelect_df = st.data_editor(DatetimeColSelect_df, key='DatetimeColSelect', hide_index=True, column_config=ColumnConfig)
    with ColumnSelectionContainer.popover("Bit Position Columns", use_container_width=True):
        FinalBitPosColSelect_df = st.data_editor(BitPosColSelect_df, key='BitPosColSelect',hide_index=True, column_config=ColumnConfig)
    with ColumnSelectionContainer.popover("Drilling Operations Columns", use_container_width=True):
        FinalDrillingOpsColSelect_df = st.data_editor(DrillingOpsColSelect_df, key='DrillingOpsColSelect', hide_index=True,column_config=ColumnConfig)
    with ColumnSelectionContainer.popover("Activity Columns", use_container_width=True):
        FinalActivityColSelect_df = st.data_editor(ActivityColSelect_df, key='ActivityColSelect', hide_index=True,column_config=ColumnConfig)
    with ColumnSelectionContainer.popover("Additional Columns", use_container_width=True):
        FinalAdditionalColSelect_df = st.data_editor(AdditionalColSelect_df, key='AdditionalColSelect',hide_index=True, column_config=ColumnConfig)
    
    ColumnDisplaySelection_df= pd.concat([FinalDatetimeColSelect_df, FinalBitPosColSelect_df, FinalDrillingOpsColSelect_df, FinalActivityColSelect_df, FinalAdditionalColSelect_df])
    ColumnDisplaySelection_df = ColumnDisplaySelection_df[ColumnDisplaySelection_df['Display'] == True]
    ColumnDisplaySelection_list = ColumnDisplaySelection_df['ColumnName'].tolist()
    TableContainer.dataframe(ActivitySummary_DF[ColumnDisplaySelection_list], use_container_width=True)

def RecalculateActivitySummary():
    UserAuthDict = st.session_state['UserAuthDict']
    SelectComp = st.session_state['SelComp']
    SelectWell = st.session_state['SelWell']
    WellInfoDict = IO_Data.getWellInfoDict(UserAuthDict, SelectComp, SelectWell)

    st.toast("Recalculating Activity Summary")
    list_startdatetime = [datetime.combine(st.session_state['RecalculateStrtDateRT'], st.session_state['RecalculateStrtTimeRT']).strftime('%Y-%m-%d %H:%M:%S')]
    list_enddatetime = [datetime.combine(st.session_state['RecalculateEndDateRT'], st.session_state['RecalculateEndTimeRT']).strftime('%Y-%m-%d %H:%M:%S')]
    list_startdatetime, list_enddatetime = Override.SimplifyTimeRange(list_startdatetime, list_enddatetime)
    st.toast("Recalculating Activity Summary")
    Override.DomeUpdateRealtimeData(WellInfoDict, 
              list_startdatetime[0] ,
               list_enddatetime[0])
    st.toast("Complete!")

#     RecalculateStrtDateRT
# RecalculateStrtTimeRT
# RecalculateEndDateRT
# RecalculateEndTimeRT
    # st.toast(
    #     f"{st.session_state['RecalculateStrtDateRT']} - {st.session_state['RecalculateStrtTimeRT']} - {st.session_state['RecalculateEndDateRT']} - {st.session_state['RecalculateEndTimeRT']}"
    # )
# @st.cache_data
def cacheGetActivitySummaryData(*args, **kwargs):
    return IO_Data.DomeGetActivitySummaryData(*args, **kwargs)
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
    ActivateDate = datetime.strptime(WellInfoDict['ActiveDate'], '%Y-%m-%d').strftime('%d-%m-%Y')
    if datetime.strptime(WellInfoDict['EndDate'], '%Y-%m-%d') > datetime.today():
        EndDate = datetime.today().strftime('%d-%m-%Y')
    else:
        EndDate = datetime.strptime(WellInfoDict['EndDate'], '%Y-%m-%d').strftime('%d-%m-%Y')
    with DatetimeRangeCol.form(key='DateForm', border=False):

        TitleCol,NothingCol, StartDateCol,StartTimeCol, MiddleCol, EndDateCol, EndTimeCol, BtnSubmitCol = st.columns([1, 0.1, 1.4,1,0.1,1.4,1,0.7])
        TitleCol.markdown('## WELL ACTIVITY')
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
    if not st.session_state['IsFormSubmit']:
        st.warning("Please select a date range")
    else:
        validate_start_end_dates(UserDateRange)
        ActivitySummary_DF = cacheGetActivitySummaryData(WellInfoDict, UserDateRange)
        if ActivitySummary_DF.empty:
            st.warning("No data available for the selected date range.")
            st.stop()


        # DashboardButtonCol, TableButtonCol = st.columns(2)
        DashboardTab, TableTab = st.tabs(["Dashboard", "Table"])
        # with DashboardButtonCol:
        #     st.button("Dashboard", on_click=st.experimental_rerun, use_container_width=True)
        # with TableButtonCol:
        #     st.button("Table", on_click=st.experimental_rerun, use_container_width=True)

        # Dashboard.SingleWellChart(ActivitySummary_DF)
        with TableTab:
            ActSumColumnSelectionWidget(ActivitySummary_DF)


            with st.expander("Recalculate Activity Summary Form").form(key='RecalculateForm', border=False):
                RecalculateStartDateCol,RecalculateStartTimeCol, RecalculateMiddleCol, RecalculateEndDateCol, RecalculateEndTimeCol, RecalculateSubmitCol = st.columns([ 1.4,1,0.1,1.4,1, 1], vertical_alignment="bottom")
                
                RecalculateStartDateCol.markdown("**Start** Datetime")
                RecalculateStartTimeCol.markdown('<h7 style="text-align: center; font-size: 15px; margin-top: 0px;opacity: 0;">-</h7>', unsafe_allow_html=True)
                

                RecalculateEndDateCol.markdown("**End** Datetime:")
                RecalculateEndTimeCol.markdown('<h7 style="text-align: center; font-size: 15px; margin-top: 0px;opacity: 0;">-</h7>', unsafe_allow_html=True)
                with RecalculateStartDateCol:
                    UserDateRange['StartDate'] = st.date_input(
                                                "**Start** Datetime",
                                                label_visibility='collapsed',
                                                # "Start Date",
                                                value = datetime.strptime(EndDate, '%d-%m-%Y').date(),
                                                key="RecalculateStrtDateRT"
                                                )
                with RecalculateStartTimeCol:
                    UserDateRange['StartTime'] = st.time_input(
                                                "",
                                                # "Start Time",
                                                label_visibility='collapsed',
                                                value = datetime.strptime('00:00', '%H:%M').time(),
                                                key="RecalculateStrtTimeRT")
                    
                with RecalculateEndDateCol:
                    UserDateRange['EndDate'] = st.date_input(
                                                "**End** Datetime",
                                                label_visibility='collapsed',
                                                # "End Date",
                                                value = datetime.strptime(EndDate, '%d-%m-%Y').date(),
                                                key="RecalculateEndDateRT")
                with RecalculateEndTimeCol:
                    UserDateRange['EndTime'] = st.time_input(
                                                "",
                                                label_visibility='collapsed',
                                                # "End Time",
                                                value = datetime.strptime('23:59', '%H:%M').time(),
                                                key="RecalculateEndTimeRT")

                RecalculateSubmitCol.form_submit_button(on_click=RecalculateActivitySummary, 
                                                 
                                                use_container_width=True, 
                                                type="primary")

        with DashboardTab:
            Dashboard.SingleWellChart(ActivitySummary_DF)

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
