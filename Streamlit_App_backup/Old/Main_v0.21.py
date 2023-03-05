import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import LogsDisp
import AppPage
import Activity
import IO_Data
import time
# import datetime
import numpy as np

import requests
import json
from datetime import datetime, timedelta
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
import plotly.express as px



st.set_page_config(page_title="Realtime Activity Mapping", page_icon=None, layout="wide",)
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
# st.markdown(hide_st_style, unsafe_allow_html=True)

st.sidebar.image('PDU_Logo.jpg',use_column_width ='never', width=300)

def GenerateInputActivity_DB(flag=False):
    if flag:
        # print(CompWell_Name)
        InputActivity_DB = pd.read_csv('RealTime_Test/Temp_InputActivity.csv', index_col = False)
        InputActivity_DB['dt'] = InputActivity_DB['dt'].astype('datetime64')
        # print(InputActivity_DB)
        # InputActivity_DB = InputActivity_DB.loc[InputActivity_DB['Comp-Well']==CompWell_Name,:]
    else:
        InputActivity_DB = pd.DataFrame(
            columns=[
                'dt',
                'Date',
                'Time',
                'Comp-Well',
                "Activity",
                "Hook Treshold",
                "Remarks",
                "PIC"
                ]
            )

    return InputActivity_DB


@st.cache
def convert_df(df):
     # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(index = False).encode('utf-8')

@st.cache(allow_output_mutation=True)
def cache_RealTime_Data(well_id, StartDateTime_select, EndDateTime_select):
    Activity_DF = IO_Data.getActivityData(well_id, StartDateTime_select, EndDateTime_select)
    Activity_DF['dt'] = Activity_DF['dt'].astype('datetime64')
    Activity_DF['bitdepth'] = Activity_DF['bitdepth'].astype('float64')
    Activity_DF['blockpos'] = Activity_DF['blockpos'].astype('float64')
    Activity_DF['rop'] = Activity_DF['rop'].astype('float64')
    Activity_DF['hklda'] = Activity_DF['hklda'].astype('float64')
    Activity_DF['woba'] = Activity_DF['woba'].astype('float64')
    Activity_DF['torqa'] = Activity_DF['torqa'].astype('float64')
    Activity_DF['rpm'] = Activity_DF['rpm'].astype('float64')
    Activity_DF['stppress'] = Activity_DF['stppress'].astype('float64')
    Activity_DF['mudflowin'] = Activity_DF['mudflowin'].astype('float64')

    return Activity_DF

def UpdateWellData():
    st.session_state.SelectDateLogic = True
    # return
PageList = [
    "Activity Mapping",
    "Activity Summary Table",
    "Summary Dashboard",
]
NavBar = st.sidebar.selectbox("Select Module:",PageList)

# InputActivity_DB = GenerateInputActivity_DB()
InputActivity_DB = pd.read_csv('RealTime_Test/Temp_InputActivity.csv', index_col = False)
# print(InputActivity_DB)
CompName_JSON = requests.get(
        "https://pdumitradome.id/dome_api/rtdc/get_company/"
    ).json()
CompName_DF = pd.json_normalize(CompName_JSON, record_path = 'result')

CompName_Select = st.sidebar.selectbox("Select Company:",["-"] + CompName_DF['company_name'].to_list())

if CompName_Select == "-":
    WellList =["-"]
    Datetime_min = ['-']
    Datetime_max = ['-']
else:
    # print(CompName_DF.loc[CompName_DF['company_name']==CompName_Select, 'cid'].values)
    getWellAPI = "https://pdumitradome.id/dome_api/rtdc/get_well?cid=" + (CompName_DF.loc[CompName_DF['company_name']==CompName_Select, 'cid'].values)

    WellName_JSON = requests.get(
            getWellAPI[0]
        ).json()

    WellName_DF = pd.json_normalize(WellName_JSON, record_path = 'result')
    WellName_DF['active_date'] = WellName_DF['active_date'].astype('datetime64').dt.date
    WellName_DF['end_date'] = WellName_DF['end_date'].astype('datetime64').dt.date

    WellList = WellName_DF['well_name'].to_list()


# temp_wellname = st.session_state.WellNameSelect
WellName_Select = st.sidebar.selectbox("Select Well",WellList, key='WellNameSelect')

CompWell_Name = CompName_Select + '-' + WellName_Select
# print(CompWell_Name)
# twoday_dt_temp = 
try:
    Datetime_start = (WellName_DF.loc[WellName_DF['well_name']==WellName_Select, 'active_date']).to_list()[0]
    Datetime_end = (WellName_DF.loc[WellName_DF['well_name']==WellName_Select, 'end_date']).to_list()[0]
    well_id = (WellName_DF.loc[WellName_DF['well_name']==WellName_Select, 'wid'])

    # st.sidebar.table(WellName_DF.loc[WellName_DF['well_name']==WellName_Select, ['active_date', 'end_date']])
    if Datetime_end > datetime.now().date():
        Datetime_end = datetime.now().date()
except Exception as error_msg:
    Datetime_start = datetime.now().date()
    Datetime_end = datetime.now().date()

    print(error_msg)
    # None

# PageList = [
#     "Activity Mapping",
#     "Summary Dashboard",
# ]
# NavBar = st.sidebar.selectbox("Select Module:",PageList)
if 'SelectDateLogic' not in st.session_state:
	st.session_state.SelectDateLogic = False
if 'FileUploadLogic' not in st.session_state:
	st.session_state.FileUploadLogic = False

if 'UpdateRTData' not in st.session_state:
	st.session_state.UpdateRTData = False

if 'StartDateTime_select' not in st.session_state:
	st.session_state.StartDateTime_select = False
if 'EndDateTime_select' not in st.session_state:
	st.session_state.EndDateTime_select = True
if 'FileUploadLogic_SummaryReport' not in st.session_state:
	st.session_state.FileUploadLogic_SummaryReport = False


with st.sidebar.form(key='DateInput'):
    sideStart_col1,sideStart_col2 = st.columns(2)

    StartDate = sideStart_col1.date_input('Start Date-Time',value=(Datetime_end - timedelta(days=2)), key='StartDate')
    StartTime = sideStart_col2.time_input('',value=datetime.strptime('00:00:00', '%H:%M:%S'), key='StartTime')

    st.session_state.StartDateTime_select = datetime.combine(StartDate, StartTime)


    sideEnd_col1,sideEnd_col2 = st.columns(2)


    EndDate = sideEnd_col1.date_input('End Date-Time',value=Datetime_end, key='EndDate')
    EndTime = sideEnd_col2.time_input('',value=datetime.strptime('00:00:00', '%H:%M:%S'), key='EndTime')
    st.session_state.EndDateTime_select = datetime.combine(EndDate, EndTime)

    if st.form_submit_button('Select Date'):
        st.session_state.SelectDateLogic = True
        st.session_state.UpdateRTData = True

print(st.session_state.SelectDateLogic)
if NavBar == "Activity Mapping" and (CompName_Select != '-') and ((st.session_state.SelectDateLogic == True)):
    # st.title("Activity Mapping Module")
    st.markdown('<h1 style="text-align: center; font-size: 50px; margin-top: 2px;"><span style="text-decoration: underline;">ACTIVITY MAPPING MODULE</span></h1>', unsafe_allow_html=True)
    try:
        if st.session_state.UpdateRTData:
            st.session_state.UpdateRTData = None
            st.session_state.Activity_DF = cache_RealTime_Data(well_id, st.session_state.StartDateTime_select, st.session_state.EndDateTime_select)
            st.session_state.UpdateRTData = False
        error_stop = True
    except:
        st.markdown('<h2 style="text-align: center; font-size: 30px; margin-top: 300px;"><span style="color: #000000;"><em>Inputed Date is Incorrect</em></span></h2>', unsafe_allow_html=True)
        error_stop = False
    if error_stop:
        Activity_DF = st.session_state.Activity_DF
        InputActivity_DB = GenerateInputActivity_DB(flag=True)
        # InputActivity_DB = pd.read_csv('RealTime_Test/Temp_InputActivity.csv', index_col = False)

        with st.form(key='Activity Input:'):
            cols = st.columns(6)
            Date_Temp = cols[0].date_input(
                        "Date", value= Datetime_end, key='InputDate'
                        )
            Time_Temp = cols[1].time_input(
                        "Time",  key='InputTime'
                        )

            
            Activity_Temp = cols[2].selectbox(
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
                                'N/D BOP',
                                'N/U BOP',
                                'OTHER',
                                'RUNNING CASING IN',
                                'STATIONARY',
                                'STUCK PIPE',
                                'TRIP IN',
                                'TRIP OUT',
                                'WAIT ON CEMENT',
                                'CIRCULATION',
                                'RIG REPAIR',
                                'WIPER TRIP'
                        ],
                        key='Activity'
                        )
            
            HookTreshold_Temp = cols[3].number_input(
                        "HookTreshold",
                        
                        key="HookTreshold"
                        )
            Remarks_Temp = cols[4].text_input(label='Additional Remarks',
                        key="Remarks"
                        )
            PIC_Temp = cols[5].text_input(label='PIC',
                        key="PIC"
                        )

            
            # submitted = st.form_submit_button('Submit')
            # print(submitted)
            
            if st.form_submit_button('Submit'):

                # print(InputActivity_DB)
                InputActivity_DB['dt'] = InputActivity_DB['dt'].astype('datetime64')
                # columns=[
                # 'dt',
                # 'Date',
                # 'Time',
                # 'Comp-Well',
                # "Activity",
                # "Hook Treshold",
                # "Remarks",
                # "PIC"
                # ]
                # InputActivity_DB.loc[len(InputActivity_DB.index), 'dt'] = (datetime.combine(Date_Temp, Time_Temp))
                # InputActivity_DB.loc[len(InputActivity_DB.index), 'Date'] = str(Date_Temp)
                # InputActivity_DB.loc[len(InputActivity_DB.index), 'Time'] = str(Time_Temp)
                # InputActivity_DB.loc[len(InputActivity_DB.index), 'Comp-Well'] = CompWell_Name
                # InputActivity_DB.loc[len(InputActivity_DB.index), 'Activity'] = Activity_Temp
                # InputActivity_DB.loc[len(InputActivity_DB.index), 'Hook Treshold'] = HookTreshold_Temp
                # InputActivity_DB.loc[len(InputActivity_DB.index), 'Remarks'] = Remarks_Temp
                # InputActivity_DB.loc[len(InputActivity_DB.index), 'PIC'] = PIC_Temp

                InputActivity_DB.loc[len(InputActivity_DB.index)] = [
                    (datetime.combine(Date_Temp, Time_Temp)),
                    str(Date_Temp),
                    str(Time_Temp),
                    CompWell_Name,
                    Activity_Temp,
                    HookTreshold_Temp,
                    Remarks_Temp,
                    PIC_Temp
                ]

                InputActivity_DB = InputActivity_DB.sort_values(by='dt', ascending=True)    
                InputActivity_DB.sort_values(by='dt', ascending=True).to_csv('RealTime_Test/Temp_InputActivity.csv', index = False)


            
            Table_col = st.columns(1)
            Table_col[0].markdown('### Activity Log')
            Table_col[0].text('To Do')
            Table_col[0].text('- solve Aggrid reloading')

        # General = st.columns(1)
            
        # print('tes')
        gb = GridOptionsBuilder.from_dataframe(InputActivity_DB[InputActivity_DB['Comp-Well']==CompWell_Name])
        gb.configure_selection('multiple', use_checkbox=True)
        gridOptions = gb.build()


        InputActivityGrid_response = AgGrid(
                InputActivity_DB[InputActivity_DB['Comp-Well']==CompWell_Name], 
                gridOptions=gridOptions,
                data_return_mode=DataReturnMode.AS_INPUT, 
                update_mode=(GridUpdateMode.SELECTION_CHANGED),
                
        )

        Button_col_1 = st.columns(3)
        if Button_col_1[0].button('Clear Selected Row', key='refresh'):
            list_selected =[]
            for dt_temp in InputActivityGrid_response['selected_rows']:
                list_selected.append(dt_temp['dt'])
                # print(list_selected)


            InputActivity_DB = InputActivity_DB.drop(InputActivity_DB.index[(InputActivity_DB['dt'].isin(list_selected)) & (InputActivity_DB['Comp-Well']==CompWell_Name)])
            InputActivity_DB['dt'] = InputActivity_DB['dt'].astype('datetime64')
            InputActivity_DB.sort_values(by='dt', ascending=True).to_csv('RealTime_Test/Temp_InputActivity.csv', index = False)
            InputActivity_DB = GenerateInputActivity_DB(flag=True)


            

        if Button_col_1[1].button('LOAD AAE-08', key='AAE08'):

            
            InputActivity_DB = pd.read_csv('RealTime_Test/AAE-08_TEST_EDIT.csv', index_col = False)
            InputActivity_DB['dt'] = InputActivity_DB['dt'].astype('datetime64')
            InputActivity_DB.to_csv('RealTime_Test/Temp_InputActivity.csv', index = False)
        if Button_col_1[2].button('clear All', key='AAE08'):

            InputActivity_DB = InputActivity_DB[1:1]

            InputActivity_DB.to_csv('RealTime_Test/Temp_InputActivity.csv', index = False)

        with st.expander("Upload Your Data"):
            UploadUser = st.file_uploader('ManualUpload', type={'csv', 'txt'} , disabled=st.session_state.FileUploadLogic)
            if UploadUser is not None:
                InputActivity_DB = pd.read_csv(UploadUser, index_col = False)
                InputActivity_DB['dt'] = InputActivity_DB['dt'].astype('datetime64')
                InputActivity_DB.to_csv('RealTime_Test/Temp_InputActivity.csv', index = False)
                print('uploaded')
            # else:
            #     st.text('File Uploaded have incorrect format')
            if st.button('submit', key='UserSubmit'):
                st.session_state.FileUploadLogic = True


            # InputActivity_DB = pd.read_csv('RealTime_Test/AAE-08_TEST_EDIT.csv', index_col = False)
            # spectra = st.file_uploader("upload file", type={"csv", "txt"})

        # st.dataframe(InputActivity_DB)
        # st.text(InputActivity_DB.columns)
        # st.text(InputActivity_DB.dtypes)
        # try:
        with st.spinner(text="Generate Activity Summary..."):
            Table_col_2 = st.columns(1)
            InputActivity_DB['dt'] = InputActivity_DB['dt'].astype('datetime64')
            # print("--")
            # print(Activity_DF.head(10))
            # print(InputActivity_DB.dtypes)
            # print(Activity_DF.dtypes)
            # st.dataframe(Activity_DF)
            # st.dataframe(InputActivity_DB[InputActivity_DB['Comp-Well']==CompWell_Name])
            Activity_DF = Activity.GetActivity_DF(Activity_DF, InputActivity_DB[InputActivity_DB['Comp-Well']==CompWell_Name])
            # st.dataframe(Activity_DF)
            # st.dataframe(InputActivity_DB[InputActivity_DB['Comp-Well']==CompWell_Name])
            # print(Activity_DF.columns)
            # print("-GetActivity")
            # print(Activity_DF.dtypes)
            # print(Activity_DF.head(10))
            # print('activity')
            # st.dataframe(Activity_DF)
            Activity_DF = Activity.GetSubActivity_DF_v3(Activity_DF)
            # print(Activity_DF.dtypes)
            # print(Activity_DF.head(10))
            # print("-GetSubActivity")
            # print('Subactivity')
            RadioButton = Table_col_2[0].radio("RAW Data?",
                            ('Cleaned', 'Raw'), key='RadioButton'
                            )

            if RadioButton=='Raw':
                SummaryActivity_DF = Activity.GenerateDuration_DF_v3(Activity_DF)
            else:
                SummaryActivity_DF = Activity.labelStand(Activity.cleanFalseSensor((Activity.GenerateDuration_DF_v3(Activity_DF))))
                # Activity.GenerateDuration_DF_v3(Activity_DF)



            
            Table_col_2[0].markdown('### Activity Summary Table')
            Table_col_2[0].text('To Do: ')
            Table_col_2[0].text('        -add aditional module/function to download the All Date summary Activity Table')
            Table_col_2[0].text('        -add aditional module/function edit the activity summary table')
            Table_col_2[0].text('        -user can only edit/create activity log for specific well only, not general wells')

            # Table_2 = Table_col_2[0].dataframe(SummaryActivity_DF)

            gb_2 = GridOptionsBuilder.from_dataframe(SummaryActivity_DF)
            # gb_2.configure_selection('multiple', use_checkbox=True)
            gb_2.configure_column("LABEL_Activity", editable=True, cellEditor='agSelectCellEditor', cellEditorPopup=True, cellEditorParams={

                'values': ['CEMENTING JOB',
                                'CIRCULATE HOLE CLEANING',
                                'CONNECTION',
                                'DRILL OUT CEMENT',
                                'DRILLING FORMATION',
                                'LAY DOWN BHA',
                                'MAKE UP BHA',
                                'NPT',
                                'N/D BOP',
                                'N/U BOP',
                                'OTHER',
                                'RUNNING CASING IN',
                                'STATIONARY',
                                'STUCK PIPE',
                                'TRIP IN',
                                'TRIP OUT',
                                'WAIT ON CEMENT',
                                'CIRCULATION',
                                'RIG REPAIR',
                                'WIPER TRIP'
                                ],
                                }
                            )

            gridOptions = gb_2.build()


            SummaryActivityGrid_response = AgGrid(
                    SummaryActivity_DF, 
                    gridOptions=gridOptions,
                    # data_return_mode=DataReturnMode.AS_INPUT, 
                    # update_mode=(GridUpdateMode.SELECTION_CHANGED),
                    
            )
            SummaryActivity_DF = SummaryActivityGrid_response['data']

            SummaryActivity_DF.to_csv('RealTime_Test/Temp_SummaryActivity.csv', index = False)
            

            # st.table(Activity_DF.head(20))

            # csv = convert_df(my_large_df)
        # if FormButton_a:
        st.download_button(
            label="Download Summary data as CSV",
            data=convert_df(SummaryActivity_DF),
            file_name=CompName_Select + "_"+ WellName_Select + '_ActivitySummary.csv',
            mime='text/csv',
        )
        st.download_button(
            label="Download Realtime(5second) data as CSV",
            data=convert_df(Activity_DF),
            file_name=CompName_Select + "_"+ WellName_Select + '_RT_5second_Data.csv',
            mime='text/csv',
        )
        st.download_button(
            label="Download ActivityLog data as CSV",
            data=convert_df(InputActivity_DB),
            file_name=CompName_Select + "_"+ WellName_Select + '_InputActivityDB.csv',
            mime='text/csv',
        )

        # except Exception as error_msg:
        #     st.text(error_msg)

        #     st.markdown("<h1 style='text-align: center; font-size: 50px;margin-top: 300px;'>  Select Date First </h1>", unsafe_allow_html=True)

    # st.table(SummaryActivity_DF)


        # figchart.add_trace(
        #         go.Pie(
        #         labels = PieChart_DF.index,
        #         values = PieChart_DF.values/60,
        #         hoverinfo = "label+percent",
        #         textinfo = "value+label"
        #         ),
        #         row=1, col=1
        
        #     )
        # st.plotly_chart(figchart,use_container_width=True)
elif NavBar =="Activity Summary Table":
    # try:

    InputActivity_DB = GenerateInputActivity_DB(flag=True)
    ActivitySum_Table = st.dataframe(InputActivity_DB)

    # Cell_dict_test = {
    #     'field':'Activity',

    #     'editable': True,
    #     # cellRenderer: GenderRenderer,
    #     'cellEditor': 'agRichSelectCellEditor',
    #     'cellEditorPopup': True,
    #     cellEditorParams: {
    #     #   cellRenderer: GenderRenderer,
    #     values: ['Male', 'Female'],
    #     },
    # }
    gb = GridOptionsBuilder.from_dataframe(InputActivity_DB)
    gb.configure_selection('multiple', use_checkbox=True)
    gb.configure_column("Activity", editable=True, cellEditor='agSelectCellEditor', cellEditorPopup=True, cellEditorParams={
        #   cellRenderer: GenderRenderer,
        'values': ["DRILLING FORMATION", 
                                'CIRCULATE HOLE CLEANING',
                                'CONNECTION',
                                'DRILL OUT CEMENT'],
        })
    gridOptions = gb.build()
    grid_response = AgGrid(
        InputActivity_DB, 
        gridOptions=gridOptions,
        data_return_mode=DataReturnMode.AS_INPUT, 
        update_mode=(GridUpdateMode.SELECTION_CHANGED),
    )

    if st.button('print result'):
        list_selected =[]
        for dt_temp in grid_response['selected_rows']:
            list_selected.append(dt_temp['dt'])
        st.dataframe(InputActivity_DB[~InputActivity_DB['dt'].isin(list_selected)])


    # except Exception as error_msg:
    #     st.text(error_msg)
elif NavBar == 'Summary Dashboard':
    # st.dataframe(MeterageDrillingDate_DF)

    combine_text = CompName_Select + '-' + WellName_Select
    st.markdown('<h1 style="text-align: center; font-size: 50px; margin-top: 2px;"><span style="text-decoration: underline;">Summary Report</span></h1>', unsafe_allow_html=True)
    st.markdown('<h1 style="text-align: center; font-size: 40px; margin-top: 2px;">%s</h1>' % CompName_Select, unsafe_allow_html=True)
    st.markdown('<h1 style="text-align: center; font-size: 30px; margin-top: 2px;">%s</h1>' % WellName_Select, unsafe_allow_html=True)
    with st.expander("Upload Your Summary Activity Table"):

        UploadUser = st.file_uploader('Override the Summary Activity Table', type={'csv', 'txt'} , disabled=st.session_state.FileUploadLogic_SummaryReport)
        st.markdown("""### Upload Guidelines:""")
        st.text("lorem ipsum")
        if UploadUser is not None:
            InputActivity_DB = pd.read_csv(UploadUser, index_col = False)
            # InputActivity_DB['dt'] = InputActivity_DB['dt'].astype('datetime64')
            InputActivity_DB.to_csv('RealTime_Test/Temp_SummaryActivity_tes1.csv', index = False)
            print('uploaded')
        if st.button('submit', key='UserSubmit'):
            st.session_state.FileUploadLogic_SummaryReport = True
    if not st.session_state.FileUploadLogic_SummaryReport:
        SummaryActivity_DF = pd.read_csv('RealTime_Test/Temp_SummaryActivity_tes1.csv', index_col = False)
    # st.dataframe(SummaryActivity_DF)
    PieChart_DF = SummaryActivity_DF.groupby(['LABEL_SubActivity', 'LABEL_Activity']).sum().reset_index()
    PieChart_DF = PieChart_DF[['LABEL_SubActivity', 'LABEL_Activity', 'Duration(minutes)']]
    
    
    StandTimeBreakdown_DF = SummaryActivity_DF.groupby(['Stand Group_Pred']).agg({
            'date_time':'first', 
            'RotateDrilling':'sum', 
            'Slide Drilling':'sum',
            'ReamingTime':'sum',
            'ConnectionTime':'sum',
            }
        ).reset_index()
    # StandTimeBreakdown_DF = StandTimeBreakdown_DF[ConnectionTime_DF['RotateDrilling'] != 0]
    # StandTimeBreakdown_DF = StandTimeBreakdown_DF[ConnectionTime_DF['RotateDrilling'] != 0]
    StandTimeBreakdown_DF = StandTimeBreakdown_DF.loc[~(StandTimeBreakdown_DF[['RotateDrilling', 'Slide Drilling', 'ReamingTime', 'ConnectionTime']]==0).all(axis=1)]
    # st.dataframe(StandTimeBreakdown_DF)

    OBH_ROP_DF = SummaryActivity_DF.copy()

    OBH_ROP_DF['Stand Group_Pred_Shift'] = SummaryActivity_DF['Stand Group_Pred'].shift(1)
    OBH_ROP_DF = OBH_ROP_DF[OBH_ROP_DF['LABEL_SubActivity']=='Connection']
    OBH_ROP_DF = OBH_ROP_DF.dropna(subset=['Stand Group_Pred_Shift'])
    OBH_ROP_DF = OBH_ROP_DF[OBH_ROP_DF['Stand Meterage (m) (Drilling)']!=0]
    OBH_ROP_DF['ROP'] = OBH_ROP_DF['Stand Meterage (m) (Drilling)'] / (OBH_ROP_DF['Stand On Bottom Hours']/60)
    OBH_ROP_DF['OBH'] = OBH_ROP_DF['Stand Meterage (m) (Drilling)'] / (OBH_ROP_DF['Stand Stand Duration (hrs)']/60)


    MeterageDrillingDate_DF = SummaryActivity_DF.groupby(['date']).agg(
        {
            "Meterage(m)(Drilling)":"sum",
            "date":"first"
        }
    )

    # with st.sidebar():
    if st.sidebar.checkbox("Display Surrounding Well"):
        OffsetWells_Dict = st.multiselect(
    'Selected Surrounding Wells Statistics',
    [i for i in WellList if i != WellName_Select],
    [i for i in WellList if i != WellName_Select])

    with st.expander('Activity Summary'):
        
        figPie_Activity = px.pie(PieChart_DF, values='Duration(minutes)', names='LABEL_Activity')
        st.plotly_chart(figPie_Activity)
    with st.expander('SubActivity Summary'):
        figPie_SubActivity = px.pie(PieChart_DF, values='Duration(minutes)', names='LABEL_SubActivity')
        st.plotly_chart(figPie_SubActivity)        
        # figSunBurst = px.sunburst(PieChart_DF, path=['LABEL_Activity', 'LABEL_SubActivity'], values='Duration(minutes)')
        # st.plotly_chart(figSunBurst)
        # st.markdown("<h1 style='text-align: center; font-size: 50px;margin-top: 300px;'>  Welcome !</h1>", unsafe_allow_html=True)

    with st.expander('Stand Time Breakdown'):
        figStandTimeBreakdown = px.bar(StandTimeBreakdown_DF, x='date_time', y=['RotateDrilling', 'Slide Drilling','ReamingTime','ConnectionTime'], width=1000, height=1000)
        st.plotly_chart(figStandTimeBreakdown)
        
    with st.expander("Time vs Depth"):
        figTimeDepth = px.scatter(SummaryActivity_DF, x="date_time", y="Bit Depth(mean)", color='LABEL_SubActivity')
        st.plotly_chart(figTimeDepth)

        

    with st.expander("Meterage Drilling per Date"):
        figMeterageDrillingDate = go.Figure(go.Waterfall(
            name = "20", 
            orientation = "v",
            # measure = 'relative',
            x = MeterageDrillingDate_DF['date'],
            textposition = "outside",
            # text = ["+60", "+80", "", "-40", "-20", "Total"],
            y = -MeterageDrillingDate_DF['Meterage(m)(Drilling)'],
            connector = {"line":{"color":"rgb(63, 63, 63)"}},
        ))

        figMeterageDrillingDate.update_layout(
                title = "Meterage Drilling By Date",
                showlegend = True
        )
        st.plotly_chart(figMeterageDrillingDate)

    with st.expander("ROP On Bottom and Stand"):
    
        figOBH_ROP = px.bar(OBH_ROP_DF, x="date_time", y=['ROP','OBH'] ,
                    barmode='group',
                    # height=600,
                    width=1000
                    )

        st.plotly_chart(figOBH_ROP)
        

    # with st.expander("Stand Time Breakdown"):
    #     # st.markdown("<h1 style='text-align: center; font-size: 5px;margin-top: 300px;'>  Welcome !</h1>", unsafe_allow_html=True)  
    #     st.plotly_chart(figConnectionTime)
else:
    st.markdown("<h1 style='text-align: center; font-size: 130px;margin-top: 300px;'>  Welcome !</h1>", unsafe_allow_html=True)