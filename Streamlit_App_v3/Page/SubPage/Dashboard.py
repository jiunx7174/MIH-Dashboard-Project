import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime
from PDU_Func import IO_Data, Activity, Viz_Data
from importlib import reload

reload(IO_Data)
reload(Activity)
reload(Viz_Data)

def SingleWellChart(ActSum_df,UserDateRange,  MainContainer=None):
    UserAuthDict = st.session_state['UserAuthDict']
    SelectComp = st.session_state['SelComp']
    SelectWell = st.session_state['SelWell']
    WellInfoDict = IO_Data.getWellInfoDict(UserAuthDict, SelectComp, SelectWell)

    RangeDateTime = [
                        datetime.combine(UserDateRange["StartDate"], UserDateRange["StartTime"]), 
                        datetime.combine(UserDateRange["EndDate"], UserDateRange["EndTime"])
                        ]
    RangeDateTime[0] = RangeDateTime[0] - pd.Timedelta(hours=3)
    RangeDateTime[1] = RangeDateTime[1] + pd.Timedelta(hours=3)
    st.write(UserDateRange)

    if MainContainer is None:
        MainContainer = st.container(border=False)
    # FirstRowContainer = MainContainer.columns([1, 2], vertical_alignment="bottom")
    PercentageActivityCol,  DrillingMeterageCol, TimeVsDepthCol = MainContainer.container(border=True).tabs(['Pie Chart Activity-Sub Activity', 'Drilling Meterage', 'Time vs Depth'])
    # MainContainer.divider()
    SecondRowContainer = MainContainer.container(border=True).tabs(['ROP on Bottom', 'Connection Time', 'Stand Time Breakdown'])
    # MainContainer.divider()
    ThirdRowContainer = MainContainer.container(border=True).tabs(['Casing Trip Duration', 'Casing Trip Duration Breakdown', 'BHA Trip Breakdown'])

    PieChartActivityCol, PieChartSubActivityCol = PercentageActivityCol.columns([1, 1])
    # SecondRowContainer = MainContainer.columns([1, 1, 1], vertical_alignment="bottom")
    # ThirdRowContainer = MainContainer.columns([1, 1, 1], vertical_alignment="bottom")
    # for i, Container_temp in enumerate(FirstRowContainer):
    #     FirstRowContainer[i] = Container_temp.container(border=False, height=400)

    # for i, Container_temp in enumerate(ThirdRowContainer):
    #     ThirdRowContainer[i] = Container_temp.container(border=True, height=550)

    # PieChartCol, DrillingTimeDepthCol = FirstRowContainer
    # PieChartCol, DrillingMeterageCol, TimeVsDepthCol = FirstRowContainer
    ROP_PerStandCol, ConnectionTimeCol, StandTimeCol = SecondRowContainer
    CasingTripSpeedCol,CasingTripBreakdownCol, BHA_TripBreakdownCol = ThirdRowContainer


    SectionSize = "All"


    # PieChart Duration Chart
    # PieChartActivityCol, PieChartSubActivityCol = PieChartCol.tabs(['Activity', 'SubActivity'])
    # DrillingMeterageCol, TimeVsDepthCol = DrillingTimeDepthCol.tabs(['Drilling Meterage', 'Time vs Depth'])

    PieChartActivityCol.markdown(f"<b>Sub-Activity</b> Pie Chart <b>{SelectWell}</b> in <b>{SectionSize}</b> hole section", unsafe_allow_html=True)
    PieChartActivityCol.plotly_chart(
        Viz_Data.getDurationPieChart(
                            ActSum_df, 
                            'LABEL_Activity', 
                            Title='', 
                            DurationCol='Duration', 
                            height=300,
                            width=250,
                            hole=0.5),
                            use_container_width=True
    ) 
    PieChartSubActivityCol.markdown(f"<b>Activity</b> Pie Chart <b>{SelectWell}</b> in <b>{SectionSize}</b> hole section", unsafe_allow_html=True)
    PieChartSubActivityCol.plotly_chart(
        Viz_Data.getDurationPieChart(
                            ActSum_df, 
                            'LABEL_SubActivity', 
                            Title='', 
                            DurationCol='Duration', 
                            height=300,
                            width=250,
                            hole=0.5),
                            use_container_width=True
    ) 




    

    # Drilling Meterage Chart
    DrillingMeterageCol.markdown(f"Drilling Meterage <b>{SelectWell}</b> in <b>{SectionSize}</b> hole section Section", unsafe_allow_html=True)
    DrillingMeterageCol.plotly_chart(
        Viz_Data.getDrillingMeterageBarChart(ActSum_df, height=300, width=800),
        use_container_width=True
    )





    TimeVsDepthCol.markdown(f"Time vs Depth <b>{SelectWell}</b> in <b>{SectionSize}</b> hole section Section", unsafe_allow_html=True)
    # TimeVsDepthCol = TimeVsDepthCol.container(height=900)
    TimeVsDepthCol.plotly_chart(
        Viz_Data.getTimeVsDepthChart(ActSum_df, height=300, width=800),
        use_container_width=True,
        Theme=None
    )

    ROP_PerStandCol.markdown(f"ROP On Bottom and Stand <b>{SelectWell}</b> in <b>{SectionSize}</b> hole section Section", unsafe_allow_html=True)
    ROP_df = Activity.getROP_df(ActSum_df)
    ROP_df['OnBottomDurationPerStand'] = ROP_df['OnBottomDurationPerStand']/60
    ROP_df['StandDuration'] = ROP_df['StandDuration']/60
    ROP_PerStandCol.plotly_chart(
        Viz_Data.getROPchart(ROP_df, height=300, width=800,  RangeDateTime=RangeDateTime),
        use_container_width=True
    )
    if ROP_df.empty:
        ROP_PerStandCol.warning("No Drilling Data")
    else:
        with ROP_PerStandCol.expander("Drilling Resume Table"):
            st.dataframe(ROP_df[['StartDateTime','EndDateTime', 'DrillingMeteragePerStand', 'OnBottomDurationPerStand', 'StandDuration', 'ROP_OnBottom', 'ROP_Stand', 'ROP_Percentage', 'Stand Group_Pred']], 
                        column_config={
                            'StartDatetime':st.column_config.DatetimeColumn("Start Datetime"),
                            'EndDatetime':st.column_config.DatetimeColumn("End Datetime"),
                            'DrillingMeteragePerStand':st.column_config.NumberColumn("Drilling meterage (m)", width=None),
                            'OnBottomDurationPerStand':st.column_config.NumberColumn("On Bottom duration (hrs)"),
                            'StandDuration':st.column_config.NumberColumn("Stand Duration (hrs)"),
                            'ROP_OnBottom':st.column_config.NumberColumn("On Bottom ROP/stand (m/hrs)"),
                            'ROP_Stand':st.column_config.NumberColumn("ROP/stand (m/hrs)"),
                            'ROP_Percentage':st.column_config.NumberColumn("Percentage", format="%.1f %%"),
                            'Stand Group_Pred':st.column_config.TextColumn("Drilling Stand Group ID"),
                            },
                        use_container_width=True, hide_index=True, height=200)

########################################## CONNECTION TIME ##############################
    ConnectionTimeCol.markdown(f"Connection time <b>{SelectWell}</b> in <b>{SectionSize}</b> hole section Section", unsafe_allow_html=True)
    ConnectionTime_df = Activity.getConnectionTime_df(ActSum_df)
    ConnectionTime_df['ConnectionID'] = "Connection-" + ConnectionTime_df['ConnectionID'].astype(str)

    ConnectionTimeCol.plotly_chart(
            Viz_Data.getConnectionTimeChart(ConnectionTime_df, height=300, width=800,  RangeDateTime=RangeDateTime),
            use_container_width=True
        )
    if ConnectionTime_df.empty:
        ConnectionTimeCol.warning("No Connection Data")
    else:
        with ConnectionTimeCol.expander("Connection Time Table"):
            st.dataframe(ConnectionTime_df[[ 'StartDatetime', 'EndDatetime', 'PreConnectionDuration', 'ConnectionDuration', 'PostConnectionDuration', 'ConnectionID']], 
                        column_config={
                            'StartDatetime':st.column_config.DatetimeColumn("Start Datetime"),
                            'EndDatetime':st.column_config.DatetimeColumn("End Datetime"),
                            # 'EndDatetime':st.column_config.TextColumn("End Datetime"),
                            'PreConnectionDuration':st.column_config.NumberColumn("Pre Connection Duration (min)"),
                            'ConnectionDuration':st.column_config.NumberColumn("Connection Duration (min)"),
                            'PostConnectionDuration':st.column_config.NumberColumn("Post Connection Duration (min)"),
                            'ConnectionID':st.column_config.TextColumn("Connection ID"),
                        },
                        use_container_width=True, hide_index=True, height=200)



########################################## STAND TIME ##############################

    StandTimeCol.markdown(f"Time Stand Break Down <b>{SelectWell}</b> in <b>{SectionSize}</b> hole section Section", unsafe_allow_html=True)
    StandTime_df = Activity.getStandTime_df(ActSum_df)
    StandTimeCol.plotly_chart(
        Viz_Data.getStandTimeChart(StandTime_df, height=300, width=800, RangeDateTime=RangeDateTime),
        use_container_width=True
    )

    if StandTime_df.empty:
        StandTimeCol.warning("No Connection Data")
    else:
        with StandTimeCol.expander("Stand Time Table"):
            st.dataframe(StandTime_df[
                                ['StartDateTime','EndDateTime',
                                  'RotateDrillingDuration', 'SlideDrillingDuration',
                                    'ReamingDuration', 'ConnectionDuration', 'Stand Group_Pred']], 
                        column_config={
                            'StartDateTime':st.column_config.DatetimeColumn("Start Datetime"),
                            'EndDateTime':st.column_config.DatetimeColumn("End Datetime"),
                            'RotateDrillingDuration':st.column_config.NumberColumn("Rotate Drilling Duration (min)"),
                            'SlideDrillingDuration':st.column_config.NumberColumn("Slide Drilling Duration (min)"),
                            'ReamingDuration':st.column_config.NumberColumn("Reaming Duration (min)"),
                            'ConnectionDuration':st.column_config.NumberColumn("Connection Duration (min)"),
                            'Stand Group_Pred':st.column_config.TextColumn("Drilling Stand Group ID"),
                        },
                        use_container_width=True, hide_index=True, height=200)
########################################## BHA TRIP ##############################

    BHA_TripBreakdownCol.markdown(f"BHA Trip Breakdown <b>{SelectWell}</b> in <b>{SectionSize}</b> hole section Section", unsafe_allow_html=True)
    # BHA_TripBreakdownCol.write( Viz_Data.getBHA_TripBreakdownChart(ActSum_df, height=400, width=800))

    BHA_TripBreakdown_df = Activity.getBHA_TripBreakdown_df(ActSum_df)
    BHA_TripBreakdownCol.plotly_chart(
        Viz_Data.getBHA_TripBreakdownChart(BHA_TripBreakdown_df, height=300, width=800,RangeDateTime=RangeDateTime),
        use_container_width=True,
    )
    if BHA_TripBreakdown_df.empty:
        BHA_TripBreakdownCol.warning("No BHA Trip Data")
    else:
        with BHA_TripBreakdownCol.expander("BHA Trip Table"):
            st.dataframe(BHA_TripBreakdown_df[
                                ['StartDateTime', 'EndDateTime', 'Duration', 
                                 'LABEL_SubActivity', 'LABEL_Activity']], 
                        column_config={
                            'StartDateTime':st.column_config.DatetimeColumn("Start Datetime"),
                            'EndDateTime':st.column_config.DatetimeColumn("End Datetime"),
                            'Duration':st.column_config.NumberColumn("Duration (min)"),
                            'LABEL_SubActivity':st.column_config.TextColumn("Sub Activity"),
                            'LABEL_Activity':st.column_config.TextColumn("Activity"),
                        },
                        use_container_width=True, hide_index=True, height=200)


########################################## CASING TRIP ##############################

    CasingTripSpeedCol.markdown(f"Casing Trip Speed <b>{SelectWell}</b> in <b>{SectionSize}</b> hole section Section", unsafe_allow_html=True)
    CasingTrip_df = Activity.getCasingTrip_df(ActSum_df)
    CasingTripSpeedCol.plotly_chart(
            Viz_Data.getCasingTripChart(CasingTrip_df, height=300, width=800,RangeDateTime=RangeDateTime),
            use_container_width=True
        )
    CasingTripSpeedCol.write(CasingTrip_df)
        # CasingTripSpeedCol.warning("No Casing Trip Data")



########################################## CASING TRIP BREAKDOWN ##############################
    CasingTripBreakdownCol.markdown(f"Casing Trip Breakdown <b>{SelectWell}</b> in <b>{SectionSize}</b> hole section Section", unsafe_allow_html=True)
    # st.write(Activity.getCasingTripBreakdown_df(ActSum_df))
    CasingTrip_df = Activity.getCasingTripBreakdown_df(ActSum_df)











    try:
        CasingTripBreakdownCol.plotly_chart(
            Viz_Data.getCasingTripBreakdownChart(ActSum_df, height=300, width=800, RangeDateTime=RangeDateTime),
            use_container_width=True
        )
    except:
        CasingTripBreakdownCol.warning("No Casing Trip Data")
    # st.write(ActSum_df)


