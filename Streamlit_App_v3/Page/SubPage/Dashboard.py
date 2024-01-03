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
        MainContainer = st.container()
    FirstRowContainer = MainContainer.columns([1, 1, 1])
    SecondRowContainer = MainContainer.columns([1, 1, 1])

    PieChartCol, DrillingMeterageCol, TimeVsDepthCol = FirstRowContainer
    ROP_PerStandCol, ConnectionTimeCol, StandTimeCol = SecondRowContainer


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
    
    ROP_PerStandCol.markdown(f"ROP On Bottom and Stand <b>{SelectWell}</b> in <b>{SectionSize}</b> hole section Section", unsafe_allow_html=True)
    ConnectionTimeCol.markdown(f"Connection time <b>{SelectWell}</b> in <b>{SectionSize}</b> hole section Section", unsafe_allow_html=True)
    StandTimeCol.markdown(f"Time Stand Break Down <b>{SelectWell}</b> in <b>{SectionSize}</b> hole section Section", unsafe_allow_html=True)


    st.write(ActSum_df)


