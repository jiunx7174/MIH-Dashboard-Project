import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import datetime
from PDU_Func import IO_Data, Activity, Viz_Data
from importlib import reload

reload(IO_Data)
reload(Activity)
reload(Viz_Data)

def SingleWellChart(ActSum_df, MainContainer=None):
    UserAuthDict = st.session_state['UserAuthDict']
    SelectComp = st.session_state['SelComp']
    SelectWell = st.session_state['SelWell']
    WellInfoDict = IO_Data.getWellInfoDict(UserAuthDict, SelectComp, SelectWell)

    if MainContainer is None:
        MainContainer = st.container(border=False)
    FirstRowContainer = MainContainer.columns([1, 1, 1], vertical_alignment="bottom")
    SecondRowContainer = MainContainer.columns([1, 1, 1], vertical_alignment="bottom")
    ThirdRowContainer = MainContainer.columns([1, 1, 1], vertical_alignment="bottom")
    for i, Container_temp in enumerate(FirstRowContainer):
        FirstRowContainer[i] = Container_temp.container(border=True, height=550)
    for i, Container_temp in enumerate(SecondRowContainer):
        SecondRowContainer[i] = Container_temp.container(border=True, height=550)
    for i, Container_temp in enumerate(ThirdRowContainer):
        ThirdRowContainer[i] = Container_temp.container(border=True, height=550)

    PieChartCol, DrillingMeterageCol, TimeVsDepthCol = FirstRowContainer
    ROP_PerStandCol, ConnectionTimeCol, StandTimeCol = SecondRowContainer
    BHA_TripBreakdownCol, CasingTripSpeedCol,CasingTripBreakdownCol = ThirdRowContainer


    SectionSize = "All"


    # PieChart Duration Chart
    PieChartCol.markdown(f"Pie Chart <b>{SelectWell}</b> in <b>{SectionSize}</b> hole section Section", unsafe_allow_html=True)
    PieChartActivityCol, PieChartSubActivityCol = PieChartCol.tabs(['Activity', 'SubActivity'])
    PieChartSubActivityCol.plotly_chart(
        Viz_Data.getDurationPieChart(
                            ActSum_df, 
                            'LABEL_Activity', 
                            Title='', 
                            DurationCol='Duration', 
                            height=400,
                            width=400,
                            hole=0.5),
                            use_container_width=True
    ) 
    PieChartActivityCol.plotly_chart(
        Viz_Data.getDurationPieChart(
                            ActSum_df, 
                            'LABEL_SubActivity', 
                            Title='', 
                            DurationCol='Duration', 
                            height=400,
                            width=400,
                            hole=0.5),
                            use_container_width=True
    ) 





    # Drilling Meterage Chart
    DrillingMeterageCol.markdown(f"Drilling Meterage <b>{SelectWell}</b> in <b>{SectionSize}</b> hole section Section", unsafe_allow_html=True)
    DrillingMeterageCol.plotly_chart(
        Viz_Data.getDrillingMeterageBarChart(ActSum_df),
        use_container_width=True
    )





    TimeVsDepthCol.markdown(f"Time vs Depth <b>{SelectWell}</b> in <b>{SectionSize}</b> hole section Section", unsafe_allow_html=True)
    TimeVsDepthCol.plotly_chart(
        Viz_Data.getTimeVsDepthChart(ActSum_df, height=400, width=800),
        use_container_width=True
    )

    ROP_PerStandCol.markdown(f"ROP On Bottom and Stand <b>{SelectWell}</b> in <b>{SectionSize}</b> hole section Section", unsafe_allow_html=True)
    ROP_PerStandCol.plotly_chart(
        Viz_Data.getROPchart(ActSum_df, height=400, width=800),
        use_container_width=True
    )
    ConnectionTimeCol.markdown(f"Connection time <b>{SelectWell}</b> in <b>{SectionSize}</b> hole section Section", unsafe_allow_html=True)
    # ConnectionTimeCol.plotly_chart(Viz_Data.getConnectionTimeChart(ActSum_df))
    ConnectionTimeCol.plotly_chart(
        Viz_Data.getConnectionTimeChart(ActSum_df, height=400, width=800),
        use_container_width=True
    )
    StandTimeCol.markdown(f"Time Stand Break Down <b>{SelectWell}</b> in <b>{SectionSize}</b> hole section Section", unsafe_allow_html=True)
    StandTimeCol.plotly_chart(
        Viz_Data.getStandTimeChart(ActSum_df, height=400, width=800),
        use_container_width=True
    )
    
    BHA_TripBreakdownCol.markdown(f"BHA Trip Breakdown <b>{SelectWell}</b> in <b>{SectionSize}</b> hole section Section", unsafe_allow_html=True)
    # BHA_TripBreakdownCol.write( Viz_Data.getBHA_TripBreakdownChart(ActSum_df, height=400, width=800))
    BHA_TripBreakdownCol.plotly_chart(
        Viz_Data.getBHA_TripBreakdownChart(ActSum_df, height=400, width=800),
        use_container_width=True
    )
    CasingTripSpeedCol.markdown(f"Casing Trip Speed <b>{SelectWell}</b> in <b>{SectionSize}</b> hole section Section", unsafe_allow_html=True)
    CasingTripBreakdownCol.markdown(f"Casing Trip Breakdown <b>{SelectWell}</b> in <b>{SectionSize}</b> hole section Section", unsafe_allow_html=True)
    st.write(ActSum_df)


