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
            margin=dict(l=0, r=0, t=20, b=100),
            title={'text': Title, 'x': 0.5, 'xanchor': 'center'},
    )
    return fig

def getDrillingMeterageBarChart(ActSum_df, height=600,width=1200):
    
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
    fig.update_layout(
        height=height,
        width=width,
        # margin=dict(l=50, r=0, t=50, b=50),
    )
    # Show the plot
    return fig



from matplotlib.colors import to_hex
import matplotlib.pyplot as plt
def getColorList():
    # from matplotlib.colors import to_hex
    tab10_colors = [to_hex(plt.cm.tab10(i)) for i in range(plt.cm.tab10.N)]
    set3_colors = [to_hex(plt.cm.Set3(i)) for i in range(plt.cm.Set3.N)]
    set2_colors = [to_hex(plt.cm.Set2(i)) for i in range(plt.cm.Set2.N)]
    set1_colors = [to_hex(plt.cm.Set1(i)) for i in range(plt.cm.Set1.N)]
    FinalColors = tab10_colors + set3_colors + set2_colors + set1_colors
    return FinalColors
def getTimeVsDepthChart(ActSum_df, height=600,width=1200, ActivityType="LABEL_Activity"):
    df = ActSum_df.copy()
    df['Activity'] = df[ActivityType]
    df['BitDepth'] = df['Bit_Depth_avg']

    # Convert the 'StartDateTime' and 'EndDateTime' columns to datetime type
    df['StartDateTime'] = pd.to_datetime(df['StartDateTime'])
    df['EndDateTime'] = pd.to_datetime(df['EndDateTime'])

    # Sort the DataFrame by 'StartDateTime' for chronological plotting
    df = df.sort_values('StartDateTime').reset_index(drop=True)

    # Create a new Plotly figure
    fig = go.Figure()

    # Define custom colors for each activity type
    activity_colors = {}
    ColorList = getColorList()
    for i in range(len(df[ActivityType].unique())):
        activity_colors[df[ActivityType].unique()[i]] = ColorList[i]


    # activity_colors = {'TRIP IN': 'red',
    # 'TRIP OUT': 'orange',
    # 'WIPER TRIP': '#00CC96',
    # 'DRILLING FORMATION': '#AB63FA',
    # 'CIRCULATE HOLE CLEANING': '#FFA15A',
    # 'CONNECTION': '#19D3F3',
    # 'DRILL OUT CEMENT': '#FF6692',
    # 'CEMENTING JOB': '#B6E880',
    # 'LAY DOWN BHA': '#FF97FF',
    # 'MAKE UP BHA': '#FECB52',
    # 'NPT': '#4D8BFA',
    # 'N/D BOP': '#F5663B',
    # 'N/U BOP': '#00D596',
    # 'RUNNING CASING IN': '#9B63FA',
    # 'STATIONARY': '#FFB85A',
    # 'STUCK PIPE': '#39D4F3',
    # 'WAIT ON CEMENT': '#FF3388',
    # 'RIG REPAIR': '#C6F980',
    # 'N/A': '#FFC0FF',
    # 'nan':'#FFC0FF',
    # 'OTHER': '#FED752'}

    # Temporary list to track activities for legend display
    temp_activity_list = []

    # Iterate over each row in the DataFrame to plot the activities
    for idx, row in df.iterrows():
        # Show legend only for the first instance of each activity
        legend_show = row['Activity'] not in temp_activity_list
        if legend_show:
            temp_activity_list.append(row['Activity'])

        # Create a date range with 15-minute intervals, ensuring to include the end time
        time_range = pd.date_range(start=row['StartDateTime'], end=row['EndDateTime'], freq='15T')
        if time_range[-1] != row['EndDateTime']:
            time_range = time_range.union(pd.DatetimeIndex([row['EndDateTime']]))

        # Assume BitDepth is constant for simplicity
        bit_depth_values = [row['BitDepth']] * len(time_range)

        # Create and add a trace to the figure for each activity
        if idx == 0:
            df_plot = pd.DataFrame({'Datetime': time_range.values.tolist(), 'bit_depth': bit_depth_values})
            df_plot['Datetime'] = pd.to_datetime(df_plot['Datetime'])
            fig.add_trace(
                go.Scatter(
                    x=df_plot['Datetime'],
                    y=df_plot['bit_depth'],
                    mode='lines',
                    name=row['Activity'],
                    line=dict(color=activity_colors[row['Activity']], width=4),
                    legendgroup=row['Activity'],
                    showlegend=legend_show  # Show legend only for the first instance of each activity
                )
            )
            before_bit_depth = [bit_depth_values[-1]]
        else:
            df_plot = pd.DataFrame({'Datetime': [time_range.values.tolist()[0]] + time_range.values.tolist(), 'bit_depth': before_bit_depth + bit_depth_values})
            df_plot['Datetime'] = pd.to_datetime(df_plot['Datetime'])
            fig.add_trace(
                go.Scatter(
                    x=df_plot['Datetime'],
                    y=df_plot['bit_depth'],
                    mode='lines',
                    name=row['Activity'],
                    line=dict(color=activity_colors[row['Activity']], width=4),
                    legendgroup=row['Activity'],
                    showlegend=legend_show  # Show legend only for the first instance of each activity
                )
            )
            before_bit_depth = [bit_depth_values[-1]]

    # Update layout for the legend
    legend_layout = {
        'orientation': 'v',
        # 'xref': "paper",
        # 'yref': "container",
        # 'y': -0.3,
        # 'x': 0.5,
        # 'xanchor': 'center',
        # 'yanchor': 'bottom'
    }
    fig.update_layout(legend=legend_layout)

    # Set the plot titles and labels
    fig.update_layout(
        height=height,
        width=width,
        margin=dict(l=0, r=20, t=0, b=50),
        xaxis_title='Datetime',
        yaxis_title='Avg. Bit Depth (m)',
        yaxis_autorange='reversed',  # Reverse the y-axis to show deeper depths at the top
        legend_title='Activity'
    )
    return fig

def getConnectionTimeChart(ActSum_df, height=400, width=800):
    ConnectionTime_df = ActSum_df.copy()
    ConnectionTime_df[['ConnectionCategory', 'ConnectionID']] = ConnectionTime_df['LABEL_ConnectionActivity'].str.split('-', expand=True)

    ConnectionTime_df['StartDateTime'] = pd.to_datetime(ConnectionTime_df['StartDateTime'])
    ConnectionTime_df['EndDateTime'] = pd.to_datetime(ConnectionTime_df['EndDateTime'])
    # Calculate MidDateTime as the average of StartDateTime and EndDateTime
    # ConnectionTime_df['MidDateTime'] = ConnectionTime_df['StartDateTime'] + (ConnectionTime_df['EndDateTime'] - ConnectionTime_df['StartDateTime']) / 2

    ConnectionTime_agg_df = ConnectionTime_df.groupby(['ConnectionID', 'ConnectionCategory']).agg(
        Total_Duration=('Duration', 'sum'),
        First_StartDatetime=('StartDateTime', 'min'),
        Latest_EndDatetime=('EndDateTime', 'max')
    ).reset_index()
    # Pivot the data to match the requested output format
    ConnectionTime_pivot_df = ConnectionTime_agg_df.pivot(index='ConnectionID', columns='ConnectionCategory', values='Total_Duration').reset_index()

    # Renaming columns to match the desired output
    # ConnectionTime_pivot_df.columns = ['ConnectionID', 'ConnectionDuration', 'PostConnectionDuration', 'PreConnectionDuration']
    ConnectionTime_pivot_df = ConnectionTime_pivot_df.rename(columns={
        'Connection': 'ConnectionDuration', 
        'Post Connection': 'PostConnectionDuration', 
        'Pre Connection': 'PreConnectionDuration'
    })
    # Merge with the original DataFrame to get the StartDatetime and EndDatetime
    start_end_times = ConnectionTime_df.groupby('ConnectionID').agg(
        StartDatetime=('StartDateTime', 'min'),
        EndDatetime=('EndDateTime', 'max')
    ).reset_index()

    # Merging the pivoted DataFrame with the start and end times
    ConnectionTime_pivot_df = pd.merge(ConnectionTime_pivot_df, start_end_times, on='ConnectionID')


    ConnectionTime_fig = go.Figure()
    ConnectionTime_fig.add_trace(go.Bar(
        x=ConnectionTime_pivot_df['StartDatetime'],
        y=ConnectionTime_pivot_df['PreConnectionDuration'],
        name='PreConnection Duration',
        marker_color='blue'
    ))
    ConnectionTime_fig.add_trace(go.Bar(
        x=ConnectionTime_pivot_df['StartDatetime'],
        y=ConnectionTime_pivot_df['ConnectionDuration'],
        name='Connection Duration',
        # marker_color='red'
    ))
    ConnectionTime_fig.add_trace(go.Bar(
        x=ConnectionTime_pivot_df['StartDatetime'],
        y=ConnectionTime_pivot_df['PostConnectionDuration'],
        name='PostConnection Duration',
        # marker_color='blue'
    ))

    ConnectionTime_fig.update_layout(
        height=height,
        width=width,
        barmode='stack',  # This will group the bars side by side at each x-value (datetime)
        xaxis_title='Datetime',
        yaxis_title='Duration',
        xaxis=dict(type='date')  # Ensuring x-axis is treated as date
    )


    return ConnectionTime_fig

def getBHA_TripBreakdownChart(ActSum_df, height=400, width=800):
    BHA_Trip_df = ActSum_df.copy()
   
    BHA_Trip_df = BHA_Trip_df[BHA_Trip_df['LABEL_SubActivity'].str.contains(r'BHA|N/D|N/U BOP', case=False, na=False)]
    BHA_Trip_df['StartDateTime'] = pd.to_datetime(BHA_Trip_df['StartDateTime'])
    BHA_Trip_df['EndDateTime'] = pd.to_datetime(BHA_Trip_df['EndDateTime'])
    BHA_Trip_df['Duration'] = BHA_Trip_df['Duration'].astype(float)


    BHA_TripBreakdown_fig = go.Figure()
    for BHAActivity in BHA_Trip_df['LABEL_SubActivity'].unique():
        BHA_Trip_df_filter = BHA_Trip_df[BHA_Trip_df['LABEL_SubActivity'] == BHAActivity]
        
        BHA_TripBreakdown_fig.add_trace(go.Bar(
            x=BHA_Trip_df_filter['StartDateTime'],
            y=BHA_Trip_df_filter['Duration'],
            name=BHAActivity,
            # marker_color='blue'
        ))
    #     BHA_Trip_df_filter = BHA_Trip_df[BHA_Trip_df['LABEL_Activity'] == BHAActivity]
        
    #     BHA_TripBreakdown_fig.add_trace(go.Bar(
    #         x=BHA_Trip_df_filter['StartDateTime'],
    #         y=BHA_Trip_df_filter['Duration'],
    #         name=BHAActivity,
    #         # marker_color='blue'
    #     ))
    BHA_TripBreakdown_fig.update_layout(
        height=height,
        width=width,
        # barmode='stack',  # This will group the bars side by side at each x-value (datetime)
        xaxis_title='Datetime',
        yaxis_title='Duration',
        xaxis=dict(type='date')  # Ensuring x-axis is treated as date
    )
    return BHA_TripBreakdown_fig

def getROPchart(ActSum_df, height=400, width=800):
    ROP_df = ActSum_df.copy()
    ROP_df['StartDateTime'] = pd.to_datetime(ROP_df['StartDateTime'])
    ROP_df['EndDateTime'] = pd.to_datetime(ROP_df['EndDateTime'])
    ROP_df[['DrillingMeteragePerStand', 'OnBottomDurationPerStand', 'StandDuration']] = ROP_df[['DrillingMeteragePerStand', 'OnBottomDurationPerStand', 'StandDuration']].astype(float)

    # Calculate MidDateTime as the average of StartDateTime and EndDateTime
    ROP_df['MidDateTime'] = ROP_df['StartDateTime'] + (ROP_df['EndDateTime'] - ROP_df['StartDateTime']) / 2

    idx_logic = (ROP_df['LABEL_Activity'].isin(["DRILLING FORMATION", 'CIRCULATE HOLE CLEANING','DRILL OUT CEMENT',])) & (ROP_df['LABEL_SubActivity'] == 'Connection')


    ROP_df = ROP_df[idx_logic]

    ROP_df['ROP_OnBottom'] = ROP_df['DrillingMeteragePerStand'] / (ROP_df['OnBottomDurationPerStand']/60) 
    ROP_df['ROP_Stand'] = ROP_df['DrillingMeteragePerStand'] / (ROP_df['StandDuration']/60)
    # display(ROP_df[['MidDateTime', 'LABEL_SubActivity', 'LABEL_Activity', 'DrillingMeteragePerStand', 'OnBottomDurationPerStand', 'StandDuration', 'ROP_OnBottom', 'ROP_Stand']])
    # ROP stand m/hr 



    # Assuming your DataFrame is named df and contains columns 'ROP_OnBottom', 'ROP_Stand', and 'DateTime'
    # First, convert your 'DateTime' column to a datetime type if it's not already
    df = pd.DataFrame(ROP_df)
    # df['DateTime'] = pd.to_datetime(df['DateTime'])

    # Create a new Plotly figure
    fig = go.Figure()
    bar_width = 60*60*60*10
    # Add ROP_OnBottom as one set of bars
    fig.add_trace(go.Bar(
        x=df['MidDateTime'],
        y=df['ROP_OnBottom'],
        name='ROP On Bottom',
        marker_color='blue',  # You can choose a color
        #  width=bar_width 
    ))

    # Add ROP_Stand as another set of bars
    fig.add_trace(go.Bar(
        x=df['MidDateTime'],
        y=df['ROP_Stand'],
        name='ROP Stand',
        marker_color='red',  # You can choose a different color
        #  width=bar_width 
    ))

    # Update the layout
    fig.update_layout(
        barmode='group',  # This will group the bars side by side at each x-value (datetime)
            bargap=0, # gap between bars of adjacent location coordinates.
        bargroupgap=0, # gap between bars of the same location coordinate.
        # title='ROP On Bottom vs ROP Stand Over Time',
        xaxis_title='Datetime',
        yaxis_title='ROP(m/hr)', # Ensuring x-axis is treated as date
        height=height,
        width=width,
        margin=dict(l=0, r=50, t=50, b=50),
    )
    return fig



def getStandTimeChart(ActSum_df, height=400, width=800):
    StandTime_df = ActSum_df.copy()
    StandTime_df[['RotateDrillingDuration', 'SlideDrillingDuration', 'ReamingDuration', 'ConnectionDuration']] = StandTime_df[['RotateDrillingDuration', 'SlideDrillingDuration', 'ReamingDuration', 'ConnectionDuration']].astype(float)
    StandTime_df = StandTime_df[ StandTime_df['Stand Group_Pred'].str.contains(r'Drilling', case=False, na=False)]
    StandTime_df = StandTime_df.groupby('Stand Group_Pred').agg({
        'RotateDrillingDuration': 'sum',
        'SlideDrillingDuration': 'sum',
        'ReamingDuration': 'sum',
        'ConnectionDuration': 'sum',
        'EndDateTime': 'max'
    })
    fig = go.Figure()

    for DurationCols in [ 'Rotate Drilling', 'Slide Drilling', 'Reaming', 'Connection']:
        # DurationCols = DurationCols.replace(' ', '').replace('Duration', '')
        
        fig.add_trace(go.Bar(
            x=StandTime_df['EndDateTime'],
            y=StandTime_df[DurationCols.replace(' ', '') + "Duration"],
            name=DurationCols,
            # marker_color='blue',  # You can choose a color
            #  width=bar_width 
        ))


    # Update the layout
    fig.update_layout(
        height=height,
        width=width,
        barmode='stack',  # This will group the bars side by side at each x-value (datetime)
        xaxis_title='Datetime',
        yaxis_title='Duration',
        xaxis=dict(type='date')  # Ensuring x-axis is treated as date
    )
    return fig

