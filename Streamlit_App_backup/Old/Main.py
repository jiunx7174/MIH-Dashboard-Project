import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import LogsDisp
import AppPage
import Activity
import time
import datetime
import numpy as np
# from st_aggrid import AgGrid
# image_PDU = Image.open('PDU_Logo.jpg')

# st.image(image, caption='Sunrise by the mountains')
@st.cache(persist=True, allow_output_mutation=True)
def GenerateInputActivity_DB():
    InputActivity_DB = pd.DataFrame(
        columns=[
            'Date',
            'Time',
            'ConnectionActivity',
            # 'SubActivity',
            "Activity",
            "MajorActivity",
            "Remarks",
            "PIC"
            ]
        )
    return InputActivity_DB


st.set_page_config(page_title="Realtime Drilling Operation", page_icon=None, layout="wide",)
PageList = [
    "Realtime Viewer",
    "Activity Table",
    "Activity Summary"
]
st.sidebar.image('PDU_Logo.jpg')
NavBar = st.sidebar.selectbox("Select Module:",PageList)



InputActivity_DB = GenerateInputActivity_DB()

if NavBar=="Realtime Viewer":
    st.markdown(
        """
        # Realtime Operation Viewer
        """
    )
    iiii = 0
    if st.button("Time 1"):
        iiii = 1
    if st.button("Time 2"):
        iiii = 2
    if st.button("Time 3"):
        iiii = 3
    if st.button("Time 4"):
        iiii = 4
    # with st.empty():
    TestRadioButton = st.radio(
        "Show Result?",
        (
            'Yes', 'No'
        )
    )
    
    HeaderColumn = st.columns((0.9,2,2,2,9))
    with HeaderColumn[1]:
        option_a = st.selectbox(
            'sensor:',
            ("bitdepth",
            "md",
            "blockpos",
            "rop",
            "hklda",
            "woba",
            "torqa",
            "rpm",
            "stppress",
            "mudflowin"),
            7,
            key='plot_a'
            )

        # st.write('You selected:', option_a)
    with HeaderColumn[2]:
        option_b = st.selectbox(
            'sensor:',
            ("bitdepth",
            "md",
            "blockpos",
            "rop",
            "hklda",
            "woba",
            "torqa",
            "rpm",
            "stppress",
            "mudflowin"),
            4,
            key='plot_b'
            )
        # st.write('You selected:', option_b)
    with HeaderColumn[3]:
        option_c = st.selectbox(
            'sensor:',
            ("bitdepth",
            "md",
            "blockpos",
            "rop",
            "hklda",
            "woba",
            "torqa",
            "rpm",
            "stppress",
            "mudflowin"),
            5,
            key='plot_c'
            )
        # st.write('You selected:', option_c)


    RealTime_DB_Real = pd.read_csv("RealTime_Test/AAE-03_RAW.csv")
    idx_end = (np.round(np.linspace(1,len(RealTime_DB_Real),20)))
    idx_end = idx_end[1:].astype(int)
    
    
    print(idx_end)
    print(idx_end[iiii])

        
    RealTime_DB = RealTime_DB_Real.iloc[1:idx_end[iiii], :]
    if TestRadioButton== 'No':
        RealTime_DB.loc[(idx_end[iiii]-np.round(idx_end[iiii]*(0.15)).astype(int)):(idx_end[iiii]), ["LABEL_ConnectionActivity","LABEL_Activity","LABEL_SubActivity","LABEL_MajorActivity"]] = "N/A"
    


    VizColumn = st.columns((12,3))

    # Initialize figure with subplots
    fig = make_subplots(
        rows=1, cols=8,
        column_widths=[0.2, 0.2,0.2, 0.1, 0.1, 0.1, 0.1, 0.1],
        # row_heights=[0.4, 0.6],
        specs=[
                [{"type": "scatter"}, 
                {"type": "scatter"}, 
                {"type": "scatter"},
                {"type": "bar"},
                {"type": "bar"},
                {"type": "bar"},
                {"type": "bar"},
                {"type": "bar"},
                ]
            ],
        shared_yaxes=True,
        horizontal_spacing=0.01,
        # subplot_titles = ['gadfdfs1','asd2','asd3'],
        row_titles = ["Date - Time"],
        column_titles =[option_a,option_b,option_c,'ConnectionActivity', 'SubActivity', 'Activity', 'MajorActivity' ]
        )


    fig.update_layout(

        showlegend=False,

        
        width=500,
        height=1000,
        hovermode="y unified",

        yaxis=dict(
            autorange='reversed'
        )
    )

    fig = LogsDisp.addWellLogs(fig,RealTime_DB,option_a,row=1,col=1)
    fig = LogsDisp.addWellLogs(fig,RealTime_DB,option_b,row=1,col=2)
    fig = LogsDisp.addWellLogs(fig,RealTime_DB,option_c,row=1,col=3)


    #% display Activity label
    fig = LogsDisp.addWellClass(fig,RealTime_DB,"LABEL_ConnectionActivity",row=1,col=4)
    fig = LogsDisp.addWellClass(fig,RealTime_DB,"LABEL_SubActivity",row=1,col=5)
    fig = LogsDisp.addWellClass(fig,RealTime_DB,"LABEL_Activity",row=1,col=6)
    fig = LogsDisp.addWellClass(fig,RealTime_DB,"LABEL_MajorActivity",row=1,col=7)
    with VizColumn[0]:
        st.plotly_chart(fig,use_container_width=True)

    
        # RealTime_DB = get_RealTime_DB("RealTime_Test/AAE-03_RealtimeSimulation.csv")


    # with st.empty():

    with st.form(key='Activity Input:'):
        cols = st.columns(7)
        Date_Temp = cols[0].date_input(
                    "Date",
                    # datetime.date(2019, 7, 6)
                    )
        Time_Temp = cols[1].time_input(
                    "Time",
                    # datetime.date(2019, 7, 6)
                    )
        Connection_Temp = cols[2].selectbox(
                    'Connection Activity',
                    ["N/A", 'PRE CONNECTION', 'CONNECTION', 'POST CONNECTION'],
                    key='connection'
                    )
        
        Activity_Temp = cols[3].selectbox(
                    "Activity",
                    ["N/A",
                         'CEMENTING JOB',
                            'CIRCULATE HOLE CLEANING',
                            'CONNECTION',
                            'DRILL OUT CEMENT',
                            'DRILLING FORMATION',
                            'LAY DOWN BHA',
                            'MAKE UP BHA',
                            'NPT',
                            'OTHER',
                            'RUNNING CASING IN',
                            'STATIONARY',
                            'STUCK PIPE',
                            'TRIP IN',
                            'TRIP OUT',
                            'WAIT ON CEMENT',
                            'CIRCULATION',
                            'RIG REPAIR'
                    ],
                    key='Activity'
                    )
        
        MajorActivity_Temp = cols[4].selectbox(
                    "MajorActivity",
                    ['Drilling', 'Tripping'],
                    key="MajorActivity"
                    )
        Remarks_Temp = cols[5].text_input(label='Additional Remarks',
                    key="Remarks"
                    )
        PIC_Temp = cols[6].text_input(label='PIC',
                    key="PIC"
                    )

        submitted = st.form_submit_button('Submit')
        print(submitted)
        
        if submitted:
            InputActivity_DB.loc[len(InputActivity_DB.index)] = [
                str(Date_Temp),
                str(Time_Temp),
                Connection_Temp,
                # SubActivity_Temp,
                Activity_Temp,
                MajorActivity_Temp,
                Remarks_Temp,
                PIC_Temp
            ]
            # Table.add_rows([
            #     Date_Temp,
            #     Time_Temp,
            #     Connection_Temp,
            #     SubActivity_Temp,
            #     Activity_Temp,
            #     MajorActivity_Temp,
            #     Remarks_Temp,
            #     PIC_Temp
            # ],
            # columns = InputActivity_DB.columns
            # )
            print([
                Date_Temp,
                Time_Temp,
                Connection_Temp,
                # SubActivity_Temp,
                Activity_Temp,
                MajorActivity_Temp,
                Remarks_Temp,
                PIC_Temp
            ])
            print(len(InputActivity_DB))
        Table = st.dataframe(InputActivity_DB)

elif NavBar=="Activity Table":
    st.markdown(
        """
        # PDU Activity Table
        """
    )
    RealTime_DB = pd.read_csv("RealTime_Test/AAE-03_RealtimeSimulation.csv")
    Activity_DB = Activity.GenerateDuration_DF(RealTime_DB)
    Activity_DB.to_csv("RealTime_Test/AAE-03_Activity_DB.csv")
    TableColumnList = st.multiselect(
        'Choose Data',
        [           
            'Duration(minutes)',
            'Hole Depth(max)',
            'Bit Depth(mean)',
            "Meterage(m)(Drilling)",
            'RotateDrilling',
            'Slide Drilling',
            'ReamingTime',
            'ConnectionTime',
            'On Bottom Hours',
            'Stand Duration',
            "LABEL_StandGroup",
            "LABEL_ConnectionActivity", 'LABEL_SubActivity', "LABEL_Activity", "LABEL_MajorActivity"
        ],
        ["LABEL_ConnectionActivity", 'LABEL_SubActivity', "LABEL_Activity", "LABEL_MajorActivity"])
    with st.empty():
        # st.title("Activity Table")
        st.dataframe(Activity_DB[['date','Time_start','Time_end']+TableColumnList])
        # print(Activity_DB.dtypes)

    if st.button("Refresh"):
        RealTime_DB = pd.read_csv("RealTime_Test/AAE-03_RealtimeSimulation.csv")
        Activity_DB = Activity.GenerateDuration_DF(RealTime_DB)
        Activity_DB.to_csv("RealTime_Test/AAE-03_Activity_DB.csv")

elif NavBar=="Activity Summary":
    ChartColumn = st.columns((5,5))
    with ChartColumn[0]:
        Activity_DB = pd.read_csv("RealTime_Test/AAE-03_Activity_DB.csv")
        PieChart_DF = Activity_DB.groupby('LABEL_SubActivity')['Duration(minutes)'].sum()

    # Initialize figure with subplots
        figchart = make_subplots(
            rows=2, cols=2,
            # column_widths=[0.2, 0.2,0.2, 0.1, 0.1, 0.1, 0.1],
            # row_heights=[0.4, 0.6],
            specs=[
                    [{"type": "pie"}, 
                    {"type": "scatter"},
                    ],

                    [ 
                    {"type": "bar"},
                    {"type": "bar"},
                    ]
                ],
            # shared_yaxes=True,
            # horizontal_spacing=0.01,
            # subplot_titles = ['gadfdfs1','asd2','asd3'],
            )

        figchart.add_trace(
                go.Pie(
                labels = PieChart_DF.index,
                values = PieChart_DF.values/60,
                hoverinfo = "label+percent",
                textinfo = "value+label"
                ),
                row=1, col=1
        
            )
        # figchart.add_trace(
        # fig = go.Figure(data=[
        #     go.Bar(name='SF Zoo', x=Activity_DB.groupby('LABEL_StandGroup')['date_time'].median(), y=Activity_DB.groupby('LABEL_StandGroup')['date_time'].median()),
        #     go.Bar(name='LA Zoo', x=Activity_DB, y=[12, 18, 29])
        # ])
# Change the bar mode
        
            # )
        # fig.update_layout(barmode='group')
        st.plotly_chart(figchart,use_container_width=True)