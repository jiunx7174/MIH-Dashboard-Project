import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd 



def getDurationPieChart(ActSum_df, ColumnName, Title=None, DurationCol='Duration', hole=0.5, height=600, width=600, margin=dict(l=0, r=0, t=50, b=50)):
    ActSum_df[DurationCol] = ActSum_df[DurationCol].astype(float)
    SumDuration_DF = (ActSum_df.groupby([ColumnName])[DurationCol].sum().reset_index())

    # SumDuration_SubAct = (ActSum_df.groupby(['LABEL_SubActivity'])['Duration'].sum().reset_index())


    fig = go.Figure()
    fig.add_trace(go.Pie(labels=SumDuration_DF[ColumnName], hole=hole,
                        values=SumDuration_DF[DurationCol], ))

    LegendDict= {
            'legend':{
                'orientation':'h', 
                'xref':"paper",
                'yref':"container",
                'y':-0.4,
                'x':0.5,
                'xanchor':'center', 
                'yanchor':'bottom', 
                }
            }
    if Title is None:
        Title = ColumnName.split('_')[1]

    fig.update_layout(LegendDict)
    fig.update_layout(
            height=height,
            width=width,
            margin=dict(l=0, r=0, t=50, b=80),
            title={'text': Title, 'x': 0.5, 'xanchor': 'center'},
    )
    return fig

def getDrillingMeterageBarChart(ActSum_df):
    
    ActSum_df['DrillingMeterage'] = ActSum_df['DrillingMeterage'].astype(float)
    # Group by the new 'Date' column and sum the 'DrillingMeterage'
    ActSum_df['Date'] = pd.to_datetime(ActSum_df['Date']).dt.date
    DrilingMeterage_df = ActSum_df.groupby('Date')['DrillingMeterage'].sum().reset_index()
    DrilingMeterage_df

    # Create a bar chart using Plotly
    fig = px.bar(DrilingMeterage_df, x='Date', y='DrillingMeterage',
                labels={'Date': 'Date', 'DrillingMeterage': 'Total Drilling Meterage'},
                )
    fig.update_xaxes(
        dtick="D",)
    # Show the plot
    return fig