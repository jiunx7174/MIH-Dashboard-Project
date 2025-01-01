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
def ActSumColumnSelectionWidget(ActivitySummary_DF, WellInfoDict):
    
    TableContainer, ColumnSelectionContainer = st.columns([6, 1])
    ColumnRename_dict = {'Date':'Date',
    'StartDateTime':'Start Datetime',
    'EndDateTime':'End Datetime',
    'Duration':'Duration(min)',
    'Hole_Depth_max':'Hole Depth (Max)',
    'Bit_Depth_avg':'Bit Depth (Avg)',
    'DrillingMeterage':'Drilling Meterage (m)',
    'RotateDrillingDuration':'Rotate Drilling Duration (min)',
    'SlideDrillingDuration':'Slide Drilling Duration (min)',
    'ReamingDuration':'Reaming Duration(min)',
    'DrillingMeteragePerStand':'Total Drilling Meterage per. Stand',
    'OnBottomDurationPerStand':'Total On-Bottom Duration per. Stand',
    'StandDuration':'Total Duration per. Stand',
    'Stand Group_Pred':'Stand Group ID',
    'LABEL_ConnectionActivity':'Connection Group ID',
    'ConnectionDuration':'Connection Duration (min)',
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
    ColumnConfigColSel = {
        'ColumnName': st.column_config.TextColumn(
            label="Column Name",
            disabled=True,
        ),
        'Display': st.column_config.CheckboxColumn(
            label="Display",
            disabled=False,
        ),
    }
    ActSumColumnConfig = {
    "Date": st.column_config.TextColumn(
        "Date",
        disabled=True
    ),
    "StartDateTime": st.column_config.TextColumn(
        "Start Datetime",
        disabled=True
    ),
    "EndDateTime": st.column_config.TextColumn(
        "End Datetime",
        disabled=True
    ),
    "Duration": st.column_config.TextColumn(
        "Duration(min)",
        disabled=True
    ),
    "Hole_Depth_max": st.column_config.TextColumn(
        "Hole Depth (Max)",
        disabled=True
    ),
    "Bit_Depth_avg": st.column_config.TextColumn(
        "Bit Depth (Avg)",
        disabled=True
    ),
    "DrillingMeterage": st.column_config.TextColumn(
        "Drilling Meterage (m)",
        disabled=True
    ),
    "RotateDrillingDuration": st.column_config.TextColumn(
        "Rotate Drilling Duration (min)",
        disabled=True
    ),
    "SlideDrillingDuration": st.column_config.TextColumn(
        "Slide Drilling Duration (min)",
        disabled=True
    ),
    "ReamingDuration": st.column_config.TextColumn(
        "Reaming Duration(min)",
        disabled=True
    ),
    "DrillingMeteragePerStand": st.column_config.TextColumn(
        "Total Drilling Meterage per. Stand",
        disabled=True
    ),
    "OnBottomDurationPerStand": st.column_config.TextColumn(
        "Total On-Bottom Duration per. Stand",
        disabled=True
    ),
    "StandDuration": st.column_config.TextColumn(
        "Total Duration per. Stand",
        disabled=True
    ),
    "Stand Group_Pred": st.column_config.TextColumn(
        "Stand Group ID",
        disabled=True
    ),
    "LABEL_ConnectionActivity": st.column_config.TextColumn(
        "Connection Group ID",
        disabled=True
    ),
    "ConnectionDuration": st.column_config.TextColumn(
        "Connection Duration (min)",
        disabled=True
    ),
    "LABEL_SubActivity": st.column_config.TextColumn(
        "Sub-Activity Group",
        disabled=True
    ),
    "LABEL_Activity": st.column_config.TextColumn(
        "Activity Group",
        disabled=True
    ),
    "InSlip_Treshold": st.column_config.TextColumn(
        "In-Slip Threshold",
        disabled=True
    ),
    "stand_on_bottom": st.column_config.TextColumn(
        "?",
        disabled=True
    ),
    "PIC": st.column_config.TextColumn(
        "PIC",
        disabled=True
    ),
    "Section": st.column_config.TextColumn(
        "Section Size",
        disabled=True
    ),
    "Remarks": st.column_config.TextColumn(
        "Remarks",
        disabled=False
    )
}

    with ColumnSelectionContainer.popover("Datetime Columns", use_container_width=True):
        FinalDatetimeColSelect_df = st.data_editor(DatetimeColSelect_df, key='DatetimeColSelect', hide_index=True, column_config=ColumnConfigColSel)
    with ColumnSelectionContainer.popover("Bit Position Columns", use_container_width=True):
        FinalBitPosColSelect_df = st.data_editor(BitPosColSelect_df, key='BitPosColSelect',hide_index=True, column_config=ColumnConfigColSel)
    with ColumnSelectionContainer.popover("Drilling Operations Columns", use_container_width=True):
        FinalDrillingOpsColSelect_df = st.data_editor(DrillingOpsColSelect_df, key='DrillingOpsColSelect', hide_index=True,column_config=ColumnConfigColSel)
    with ColumnSelectionContainer.popover("Activity Columns", use_container_width=True):
        FinalActivityColSelect_df = st.data_editor(ActivityColSelect_df, key='ActivityColSelect', hide_index=True,column_config=ColumnConfigColSel)
    with ColumnSelectionContainer.popover("Additional Columns", use_container_width=True):
        FinalAdditionalColSelect_df = st.data_editor(AdditionalColSelect_df, key='AdditionalColSelect',hide_index=True, column_config=ColumnConfigColSel)
    
    ColumnDisplaySelection_df= pd.concat([FinalDatetimeColSelect_df, FinalBitPosColSelect_df, FinalDrillingOpsColSelect_df, FinalActivityColSelect_df, FinalAdditionalColSelect_df])
    ColumnDisplaySelection_df = ColumnDisplaySelection_df[ColumnDisplaySelection_df['Display'] == True]
    ColumnDisplaySelection_list = ColumnDisplaySelection_df['ColumnName'].tolist()
    FinalActSumColumnConfig = {}
    for ColumnName in ColumnDisplaySelection_list:
        FinalActSumColumnConfig[ColumnName] = ActSumColumnConfig[ColumnName]
    # if "Remarks" in ColumnDisplaySelection_list:
    #     # TableContainer.dataframe(ActivitySummary_DF[ColumnDisplaySelection_list], use_container_width=True)
    #     TableContainer.write(st.write(st.session_state['RemarksActSumTable']))
    # else:
    #     TableContainer.dataframe(ActivitySummary_DF[ColumnDisplaySelection_list], use_container_width=True)
    OverrideRemark_df = TableContainer.data_editor(ActivitySummary_DF[ColumnDisplaySelection_list], key='RemarksActSumTable_DataEditor', hide_index=True,  use_container_width=True, column_config=FinalActSumColumnConfig)
    isRemarksActSumUpdateEmpty = True
    for RemarksActSumKey in ['edited_rows', 'added_rows', 'deleted_rows']:
        if is_empty_dict(st.session_state['RemarksActSumTable_DataEditor']):
        # if st.session_state['RemarksActSumTable'][RemarksActSumKey] != []:
            isRemarksActSumUpdateEmpty = True
        else:
            isRemarksActSumUpdateEmpty = False
    if not isRemarksActSumUpdateEmpty:

        FinalOverrideRemark_df = pd.DataFrame(st.session_state['RemarksActSumTable_DataEditor']['edited_rows']).T.reset_index(names="Idx")

        FinalOverrideRemark_df['StartDateTime'] = OverrideRemark_df.loc[FinalOverrideRemark_df['Idx'].tolist(), 'StartDateTime'].tolist()
        FinalOverrideRemark_df['EndDateTime'] = OverrideRemark_df.loc[FinalOverrideRemark_df['Idx'].tolist(), 'EndDateTime'].tolist()

        # Split the 'datetime' column into 'Date' and 'Time'

        FinalOverrideRemark_df[['StartDate', 'StartTime']] = FinalOverrideRemark_df['StartDateTime'].astype(str).str.split(' ', expand=True)
        FinalOverrideRemark_df[['EndDate', 'EndTime']] = FinalOverrideRemark_df['EndDateTime'].astype(str).str.split(' ', expand=True)

        # Drop the 'datetime' column
        FinalOverrideRemark_df = FinalOverrideRemark_df.drop(columns=['StartDateTime'])
        FinalOverrideRemark_df = FinalOverrideRemark_df.drop(columns=['EndDateTime'])


        # st.write(FinalOverrideRemark_df)
        # st.write(FinalOverrideRemark_df)
        if st.button("Update Remarks", type="primary", use_container_width=True):

            Override.UpdateRemarksActSumTable(FinalOverrideRemark_df, WellInfoDict, 'RemarksActSumTable',)
            st.success("Remarks Updated!")


    
    # st.write(st.session_state['RemarksActSumTable_DataEditor'])
def is_empty_dict(d):
    """
    Checks if a dictionary contains only empty dictionaries or lists.
    """
    if isinstance(d, dict):
        return all(is_empty_dict(v) for v in d.values())
    elif isinstance(d, list):
        return len(d) == 0  # Empty list
    else:
        return False  # Non-empty value

    # Recursively check all values in the dictionary
    return all(is_nested_dict_empty(v) for v in d.values())
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
            ActSumColumnSelectionWidget(ActivitySummary_DF, WellInfoDict)


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
            Dashboard.SingleWellChart(ActivitySummary_DF, UserDateRange)

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
