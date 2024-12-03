import streamlit as st
import plotly.graph_objects as go

def getDefaultPlotParamDict():
    return {
        'bitdepth': {'color': '#b0f26b', 'width': 1, 'min': 0, 'max': 100},
        'md': {'color': '#e88c09', 'width': 1, 'min': 0, 'max': 100},
        'blockpos': {'color': '#6b1b1c', 'width': 1, 'min': 0, 'max': 100},
        'rop': {'color': '#852754', 'width': 1, 'min': 0, 'max': 100},
        'hklda': {'color': '#09e624', 'width': 1, 'min': 0, 'max': 100},
        'woba': {'color': '#407eb6', 'width': 1, 'min': 0, 'max': 100},
        'torqa': {'color': '#a8c0c0', 'width': 1, 'min': 0, 'max': 100},
        'rpm': {'color': '#fdf8e9', 'width': 1, 'min': 0, 'max': 100},
        'stppress': {'color': '#6eab3c', 'width': 1, 'min': 0, 'max': 100},
        'mudflowin': {'color': '#de2c91', 'width': 1, 'min': 0, 'max': 100}
    }

import plotly.graph_objects as go
from plotly.subplots import make_subplots

def getRealtimeVisualization(df, plot_params):

    # Determine the number of subplots from the plot_params
    num_subplots = len(plot_params)

    # Create a subplot figure with 1 row and n columns, and shared y-axes
    fig = make_subplots(rows=1, cols=num_subplots, shared_yaxes=True, horizontal_spacing=0.01)

    legectDict = {}
    # Loop over each grid in plot_params
    for i, (grid_key, grid_data) in enumerate(plot_params.items()):

        # Each item in grid_data is a trace to be plotted in the subplot
        legendname = f"legend{i+1}"
        xaxisname = f"x{i+1}"
        for trace_key, trace_params in grid_data.items():
            # Check if the trace_key exists in the dataframe
            if trace_key in df.columns:
                # Add a trace with a legend group corresponding to the grid
                fig.add_trace(
                    go.Scatter(
                        x=df[trace_key],
                        y=df['dt'], 
                        mode='lines',
                        name=trace_key,
                        # line=dict(
                        #     color=trace_params['color'],
                        #     width=trace_params['width']
                        # ),
                        legend=legendname,  # Group legend by grid key
                        xaxis=xaxisname
                    ),
                    row=1, col=i+1
                )

        # Reverse the y-axis and move x-axis to top
        fig.update_yaxes(autorange='reversed', row=1, col=i+1,gridcolor='rgb(80,80,80)' ,tickfont=dict(color='lightgrey'))
        fig.update_xaxes(side='top', row=1, col=i+1, gridcolor='rgb(80,80,80)' ,tickfont=dict(color='lightgrey'))
        legectDict[legendname] = {
            # 'title':i*(1/num_subplots),
            'orientation':'h', 
            'xref':"paper",
            'yref':"container",
            'y':0.1,
            'x':i / num_subplots + 1 / (2 * num_subplots),
            'xanchor':'center', 
            'yanchor':'bottom', 
            'font':dict(color='lightgrey')
            # 'orientation':'h', 'yanchor':'bottom', 'y':0, 'xanchor':'center', 'x':i*(1/num_subplots)
        }

    # Update layout
    fig.update_layout(
        height=500,
        width=1000,
        margin=dict(l=100, r=100, t=50, b=50),
        hovermode='y unified',
        # paper_bgcolor='grey',
            paper_bgcolor='rgb(10,10,10)',  # Dark background for the entire figure area
    plot_bgcolor='rgb(30,30,30)',  # Dark background for the plot area
    # xaxis=dict(
    #     gridcolor='rgb(80,80,80)'  # Dark grid lines
    # ),
    # yaxis=dict(
    #     gridcolor='rgb(80,80,80)'  # Dark grid lines
    # ),

    )
    fig.update_layout(legectDict)

    return fig
# @st.experimental_fragment
def App(container, RTSensor_DF):
    TitleContainer, NumberContainer, EmptyRightCol_title = container.columns([3,2,4])
    TitleContainer.markdown("### Realtime Data Visualization")
    EmptyLeftCol, PlotParamContainer, EmptyRightCol = container.columns([0.075,1,0.075])

    if "NumPlot" not in st.session_state:
        st.session_state["NumPlot"] = 3
    try:
        with NumberContainer.popover(f"Number of Plot: {st.session_state['NumPlot']}", use_container_width=True ):
            NumPlot = st.number_input("Number of Plot", min_value=1, max_value=5,  step=1, key="NumPlot")
    except:
        with NumberContainer.popover(f"Number of Plot: 3", use_container_width=True ):
            NumPlot = st.number_input("Number of Plot", min_value=1, max_value=5, value=3,  step=1, key="NumPlot")

        # st.markdown("Hello World 👋")
        # name = st.text_input("What's your name?")

    PlotParamCol_list = PlotParamContainer.columns(NumPlot)
    DefaultPlotDict = {
        'PlotRT_0': [ "hklda", "woba", "blockpos"],   
        'PlotRT_1': [ "torqa", "woba", "stppress"],   
        'PlotRT_2': [ "hklda", "rop", "mudflowin"],   
    }

    ListData = [
        'bitdepth', 'md', 'blockpos', 'rop', 'hklda', 'woba', 'torqa', 'rpm', 'stppress', 'mudflowin'
    ]
    FinalPlotParamDict = {}
    for i, PlotParamCol in enumerate(PlotParamCol_list):
        if f"PlotRT_{i}" in DefaultPlotDict.keys():
            DefaultPlotList = DefaultPlotDict[f"PlotRT_{i}"]
        else:
            DefaultPlotList=None
        PlotParamList = PlotParamCol.multiselect("Select Data", ListData,default=DefaultPlotList, key=f"PlotRT_{i}")
        PlotParamDict = {}
        for Param in PlotParamList:
            PlotParamDict[Param] = getDefaultPlotParamDict()[Param]

        FinalPlotParamDict[f"PlotRT_{i}"] = PlotParamDict
    container.plotly_chart(getRealtimeVisualization(RTSensor_DF, FinalPlotParamDict), use_container_width=True, theme=None)



    # st.write(st.session_state['PlotRT_0'])
    # st.write(st.session_state['PlotRT_1'])
    # st.write(st.session_state['PlotRT_2'])