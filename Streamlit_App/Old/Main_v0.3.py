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
import base64

import requests
import json
from datetime import datetime, timedelta
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
import plotly.express as px
import psycopg2
import plotly.io as pio
from fpdf import FPDF

################################################################################################################
########################################## Useful Function #####################################################
################################################################################################################

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

def oldIOdata():
    # @st.cache
    # def GetInputActivity_DB(Conn, Well, Comp):
    #     cursor = Conn.cursor()

    #     select_query = "select * from activitylog_db"
    #     select_query += " where (well = '%s' and comp = '%s')" % (Well, Comp)
    #     # select_query += "where  = %s" %Well
    #     Table_Column = ['input_id',
    #                         'dt',
    #                         'date',
    #                         'time',
    #                         'comp',
    #                         'well',
    #                         'activity',
    #                         'in_slip_treshold',
    #                         'remarks',
    #                         'pic',
    #                         'section'
    #                         ]
    #     try:
    #         cursor.execute(select_query)
    #     except (Exception, psycopg2.DatabaseError) as error:
    #         print("Error: %s" % error)
    #         cursor.close()
    #         return 1
        
    #     # Naturally we get a list of tupples
    #     tupples = cursor.fetchall()
    #     cursor.close()
    #     Conn.close()
    #     # We just need to turn it into a pandas dataframe
    #     df = pd.DataFrame(tupples, columns=Table_Column)
    #     return df
    # def GetSummaryActivity_DB(Conn, Well, Comp):
    #     cursor = Conn.cursor()

    #     select_query = "select * from summary_activity_db"
    #     select_query += " where (well = '%s' and comp = '%s')" % (Well, Comp)
    #     # select_query += "where  = %s" %Well
    #     listcolumn = ['comp',
    #         'well',
    #         'time_start',
    #         'time_end',
    #         'duration_minutes',
    #         'hole_depth',
    #         'bit_depth',
    #         'meterage_drilling',
    #         'rotate_drilling_time',
    #         'slide_drilling_time',
    #         'reaming_time',
    #         'connection_time',
    #         'on_bottom_hours',
    #         'stand_duration',
    #         'label_subactivity',
    #         'label_activity',
    #         'stand_meterage_drilling',
    #         'stand_durationx',
    #         'stand_on_bottom',
    #         'stand_group',
    #         'pic',
    #         'section',
    #         'remarks']
    #     try:
    #         cursor.execute(select_query)
    #     except (Exception, psycopg2.DatabaseError) as error:
    #         print("Error: %s" % error)
    #         cursor.close()
    #         return 1
        
    #     # Naturally we get a list of tupples
    #     tupples = cursor.fetchall()
    #     cursor.close()
    #     Conn.close()
    #     # We just need to turn it into a pandas dataframe
    #     df = pd.DataFrame(tupples, columns=Table_Column)
    #     return df

    # # @st.cache
    # def OpenConnection():
    #     param_dic = {
    #     "host"      : "localhost",
    #     "database"  : "PDU_AUTOMAPPING",
    #     "user"      : "postgres",
    #     "password"  : "Saber2496"
    #     }
    #     conn = None
    #     # import json


        
    #     # print(user_encode_data)
    #     # try:
    #         # connect to the PostgreSQL server
    #         # print('Connecting to the PostgreSQL database...')
    #     conn = psycopg2.connect(**param_dic)
    #     # except (Exception, psycopg2.DatabaseError) as error:
    #         # print(error)
    #         # sys.exit(1) 
    #     return conn

    # def DeleteInputActivity_DB(Conn, Well, Comp, InputID):
    #     SQL_Queries = "delete from activitylog_db"
    #     SQL_Queries += " where ((well = '%s' and comp = '%s') and input_id = %s)" % (Well, Comp, InputID)

        
    #     cursor = Conn.cursor()
    #     try:
    #         cursor.execute(SQL_Queries)
    #         Conn.commit()
    #     except(Exception, psycopg2.DatabaseError) as error:
    #         print("Error: %s" % error)
    #         Conn.rollback()
    #         cursor.close()
    #         return 1
    #     cursor.close()
    #     Conn.close() 

    #     # return None

    # def InsertInputActivity_DB(Conn, InputDict):
        
    #     SQL_Queries = """
    #     INSERT into activitylog_db(input_id, dt, date, time, comp, well, activity, in_slip_treshold, remarks, pic, section) values(%s,'%s','%s','%s','%s','%s','%s',%s,'%s','%s','%s');
    #     """ % tuple(InputDict.values())
        
    #     cursor = Conn.cursor()
    #     try:
    #         cursor.execute(SQL_Queries)
    #         Conn.commit()
    #     except(Exception, psycopg2.DatabaseError) as error:
    #         print("Error: %s" % error)
    #         Conn.rollback()
    #         cursor.close()
    #         return 1
    #     cursor.close()
    #     Conn.close() 
    #     # return None

    # def InsertSummaryActivity_DB(Conn, SummaryActivity_DF, WellName, CompName):
    #     SummaryActivity_DF = Activity.SummaryTranslator(SummaryActivity_DF, WellName, CompName, '-', '-', '-')
    #     for i in SummaryActivity_DF.index:
    #         SQL_Queries = """INSERT into summary_activity_db(comp, well, time_start, time_end, duration_minutes, hole_depth, bit_depth, meterage_drilling, rotate_drilling_time, slide_drilling_time, reaming_time, connection_time, on_bottom_hours, stand_duration, label_subactivity, label_activity, stand_meterage_drilling, stand_durationx, stand_on_bottom, stand_group, pic, section, remarks) values('%s', '%s', '%s', '%s', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '%s', '%s', '%s', %s, %s, '%s', '%s', '%s', '%s'"""
    #         SQL_Queries += ")" 

    #         # print()
    #         cursor = Conn.cursor()
    #         try:
    #             cursor.execute(SQL_Queries % tuple(SummaryActivity_DF.iloc[i,:].to_list()))
    #             Conn.commit()
    #         except(Exception, psycopg2.DatabaseError) as error:
    #             print("Error: %s" % error)
    #             Conn.rollback()
    #             cursor.close()
    #             return 1
    #         cursor.close()
    #     Conn.close() 
    return None

def InputTranslator(Input_DB):
    Input_DB['dt'] = (Input_DB['dt']).apply(lambda d: pd.to_datetime(str(d)))

    Input_DB.rename(columns = {'in_slip_treshold':'Hook Treshold', 'activity':'Activity'}, inplace = True)
    return Input_DB
    
def create_download_link(val, filename):
    b64 = base64.b64encode(val)  # val looks like b'...'
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}.pdf">Download file</a>'


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



################################################################################################################
######################################## App start from Here ###################################################
################################################################################################################


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

PageList = [
    "Activity Mapping Module",
    "Activity Summary Table",
    "Summary Dashboard",
]
NavBar = st.sidebar.selectbox("Select Module:",PageList)


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
    print(WellName_DF)
    WellName_DF['active_date'] = WellName_DF['active_date'].astype('datetime64').dt.date
    WellName_DF['end_date'] = WellName_DF['end_date'].astype('datetime64').dt.date

    WellList = WellName_DF['well_name'].to_list()



WellName_Select = st.sidebar.selectbox("Select Well",WellList, key='WellNameSelect')

CompWell_Name = CompName_Select + '-' + WellName_Select


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


if 'SelectDateLogic' not in st.session_state:
	st.session_state.SelectDateLogic = False
if 'FileUploadLogic' not in st.session_state:
	st.session_state.FileUploadLogic = False
if 'FileUploadLogic_SummaryReport' not in st.session_state:
	st.session_state.FileUploadLogic_SummaryReport = False

if 'UpdateRTData' not in st.session_state:
	st.session_state.UpdateRTData = False

if 'StartDateTime_select' not in st.session_state:
	st.session_state.StartDateTime_select = False
if 'EndDateTime_select' not in st.session_state:
	st.session_state.EndDateTime_select = True



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
if NavBar == "Activity Mapping Module" and (CompName_Select != '-') and ((st.session_state.SelectDateLogic == True)):
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
        # InputActivity_DB = GenerateInputActivity_DB(flag=True)
        
        InputActivity_DB = IO_Data.GetInputActivity_DB(IO_Data.OpenConnection(), WellName_Select, CompName_Select)
        # InputActivity_DB = pd.read_csv('RealTime_Test/Temp_InputActivity.csv', index_col = False)

            
        # Table_col = st.columns(1)
        with st.form(key='Activity Input:'):
            st.markdown('### Major Activity Input')
            cols = st.columns(7)
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
                        "In-Slip Treshold",
                        
                        key="InSlipTreshold"
                        )
            Remarks_Temp = cols[4].text_input(label='Additional Remarks',
                        key="Remarks"
                        )
            PIC_Temp = cols[5].text_input(label='PIC',
                        key="PIC"
                        )
            Section_Temp = cols[6].selectbox('Section',
                        [
                            '26"',
                            '17-1/2"',
                            '12-1/4"',
                            '9-3/4"'
                        ],
                        key="Section"
                        )

            

            
            if st.form_submit_button('Submit'):

                InputID_temp = InputActivity_DB['input_id'].max() + 1
                InputDict = {
                    'input_id':InputID_temp,
                        'dt':(datetime.combine(Date_Temp, Time_Temp)),
                        'date':str(Date_Temp),
                        'time':str(Time_Temp),
                        'comp':CompName_Select,
                        'well':WellName_Select,
                        'activity':Activity_Temp,
                        'in_slip_treshold':HookTreshold_Temp,
                        'remarks':Remarks_Temp,
                        'pic':PIC_Temp,
                        'section':Section_Temp
                }

                IO_Data.InsertInputActivity_DB(IO_Data.OpenConnection(), InputDict)
                





            
        Table_col = st.columns(1)
        Table_col[0].markdown('### Activity Log')
        Table_col[0].text('To Do')
        Table_col[0].text('- solve Aggrid reloading')

        # General = st.columns(1)
            
        # print('tes')
        # gb = GridOptionsBuilder.from_dataframe(InputActivity_DB[InputActivity_DB['Comp-Well']==CompWell_Name])
        # with st.form(key='Activity Edit:'):
        used_columns = {"date":"Date", "time":"Time", "well":"Well", "comp":"Company", "section":"Section", "activity":"Major Activity", "in_slip_treshold":"In-Slip Threshold", "remarks":"Additional Remarks", "pic":"PIC"
        }

        InputActivity_DB = IO_Data.GetInputActivity_DB(IO_Data.OpenConnection(), WellName_Select, CompName_Select)

        InputActivity_DB_temp = InputActivity_DB.copy()
        InputActivity_DB_temp.rename(columns=used_columns, inplace=True)

        gb = GridOptionsBuilder.from_dataframe(InputActivity_DB_temp[list(used_columns.values())])
        # gb = GridOptionsBuilder.from_dataframe((InputActivity_DB[used_columns.keys()]).rename(columns=used_columns, inplace=True))
        gb.configure_selection('multiple', use_checkbox=True)
        gridOptions = gb.build()


        InputActivityGrid_response = AgGrid(
                InputActivity_DB_temp, 
                gridOptions=gridOptions,
                data_return_mode=DataReturnMode.AS_INPUT, 
                update_mode=(GridUpdateMode.SELECTION_CHANGED),
        )


        Button_col_1 = st.columns(3)
        if Button_col_1[0].button('Clear Selected Row', key='refresh'):
            list_selected =[]
            for dt_temp in InputActivityGrid_response['selected_rows']:
                # IO_Data.DeleteInputActivity_DB(IO_Data.OpenConnection(), dt_temp['input_id'].values)
                print(dt_temp)
                # idx_delete = 
                # idx_delete = (InputActivity_DB['date'] == dt_temp ['Date']) & (InputActivity_DB['time'] == dt_temp ['Time'])
                # print("inilah yanganda cari")
                # print(idx_delete)
                IO_Data.DeleteInputActivity_DB(IO_Data.OpenConnection(), WellName_Select, CompName_Select, dt_temp['input_id'])
                # list_selected.append(dt_temp['input_id'])
                # print(list_selected)

            InputActivity_DB = IO_Data.GetInputActivity_DB(IO_Data.OpenConnection(), WellName_Select, CompName_Select)

        # Button_col_1 = st.columns(3)

            

        # if Button_col_1[1].button('LOAD AAE-08', key='AAE08'):


        #     InputActivity_DB = pd.read_csv('RealTime_Test/AAE-08_TEST_EDIT.csv', index_col = False)
        #     InputActivity_DB['dt'] = InputActivity_DB['dt'].astype('datetime64')
        #     InputActivity_DB.to_csv('RealTime_Test/Temp_InputActivity.csv', index = False)
        # if Button_col_1[2].button('clear All', key='AAE08'):

        #     InputActivity_DB = InputActivity_DB[1:1]

        #     InputActivity_DB.to_csv('RealTime_Test/Temp_InputActivity.csv', index = False)

        with st.expander("Download your Activity Log Table"):
            st.download_button(
                label="Download Activity Log Table as CSV",
                data=convert_df(InputActivity_DB),
                file_name=CompName_Select + "_"+ WellName_Select + '_ActivityLogTable.csv',
                mime='text/csv',
            )
        with st.expander("Upload Your Activity Log Table"):

            UploadUser = st.file_uploader('Override the Activity Log Table', type={'csv', 'txt'} , disabled=st.session_state.FileUploadLogic)
            st.markdown("""### Upload Guidelines:""")
            st.text("lorem ipsum")
            if UploadUser is not None:
                InputActivity_DB = pd.read_csv(UploadUser, index_col = False)
                InputActivity_DB['dt'] = InputActivity_DB['dt'].astype('datetime64')
                InputActivity_DB.to_csv('RealTime_Test/Temp_InputActivity.csv', index = False)
                print('uploaded')

            if st.button('submit', key='UserSubmit'):
                st.session_state.FileUploadLogic = True




        with st.spinner(text="Generate Activity Summary..."):
            Table_col_2 = st.columns(1)
            # InputActivity_DB['dt'] = InputActivity_DB['dt'].astype('datetime64')
            # print("--")
            # print(Activity_DF.head(10))
            # print(InputActivity_DB.dtypes)
            # print(Activity_DF.dtypes)
            # st.dataframe(Activity_DF)
            # st.dataframe(InputActivity_DB[InputActivity_DB['Comp-Well']==CompWell_Name])
            Input_Temp = InputTranslator(InputActivity_DB)
            print(Input_Temp.dtypes)

            Activity_DF = Activity.GetActivity_DF(Activity_DF, Input_Temp)
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

            
            Table_col_2[0].markdown('### Activity Summary Table')
            Table_col_2[0].text('To Do: ')
            Table_col_2[0].text('        -add aditional module/function to download the All Date summary Activity Table')
            Table_col_2[0].text('        -add aditional module/function edit the activity summary table')
            Table_col_2[0].text('        -user can only edit/create activity log for specific well only, not general wells')


            RadioButton = Table_col_2[0].radio("Apply FALSE Sensor Filter?",
                            ('Yes', 'No/RAW'), key='RadioButton'
                            )

            if RadioButton=='No/RAW':
                SummaryActivity_DF = Activity.GenerateDuration_DF_v3(Activity_DF)
            else:
                SummaryActivity_DF = Activity.labelStand(Activity.cleanFalseSensor((Activity.GenerateDuration_DF_v3(Activity_DF))))

                # Activity.GenerateDuration_DF_v3(Activity_DF)



            Summary_Used_Columns = {
                "date":"Date",
                "Time_start":"Start Time",
                "Time_end":"End Time",
                "LABEL_Activity":"ACTIVITY",
                "LABEL_SubActivity":"SUB-ACTIVITY",
                "Duration(minutes)": "Duration (Minutes)",
                "Hole Depth(max)":"Hole Depth (Max)",
                "Bit Depth(mean)":"Bit Depth(mean)",
                "Meterage(m)(Drilling)": "Drilling Meterage (m)",
                "RotateDrilling":"Rotate Drilling (minutes)",
                "Slide Drilling": "Slide Drilling (minutes)",
                "ReamingTime": "Reaming (minutes)",
                "ConnectionTime":"Connection (minutes)",
                "On Bottom Hours":"On Bottom state (Hours)",
                "Stand Group_Pred":"Stand Group",
                "Stand Meterage (m) (Drilling)":"Total Stand Drilling Meterage (m)",
                "Stand Stand Duration (hrs)":"Total Stand Duration (hrs)",
                "Stand On Bottom Hours": "Total On Bottom Duration (hrs)",
            }


            SummaryActivity_DF_temp = SummaryActivity_DF.copy()
            SummaryActivity_DF_temp.rename(columns=Summary_Used_Columns, inplace=True)

            gb_2 = GridOptionsBuilder.from_dataframe(SummaryActivity_DF_temp[list(Summary_Used_Columns.values())])
            # gb_2.configure_selection('multiple', use_checkbox=True)
            gb_2.configure_column("ACTIVITY", editable=True, cellEditor='agSelectCellEditor', cellEditorPopup=True, cellEditorParams={

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
                    SummaryActivity_DF_temp, 
                    gridOptions=gridOptions,
                    # data_return_mode=DataReturnMode.AS_INPUT, 
                    # update_mode=(GridUpdateMode.SELECTION_CHANGED),
                    
            )
            SummaryActivity_DF = SummaryActivityGrid_response['data']

            # SummaryActivity_DF.to_csv('RealTime_Test/Temp_SummaryActivity.csv', index = False)
            
            
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

        if st.button(label="Finalize"):
            IO_Data.InsertSummaryActivity_DB(IO_Data.OpenConnection(), SummaryActivity_DF, WellName_Select, CompName_Select)


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
    print("teeees")
    print(gridOptions)
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
    if not st.session_state.FileUploadLogic_SummaryReport:
        SummaryActivity_DF = pd.read_csv('RealTime_Test/Temp_SummaryActivity_tes1.csv', index_col = False)
    # st.dataframe(SummaryActivity_DF)
    PieChart_DF = SummaryActivity_DF.groupby(['LABEL_SubActivity', 'LABEL_Activity']).sum().reset_index()
    PieChart_DF = PieChart_DF[['LABEL_SubActivity', 'LABEL_Activity', 'Duration(minutes)']]
    
    # StandTimeBreakdown_DF = SummaryActivity_DF.copy()
    # StandTimeBreakdown_DF[]
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

    SummaryActivity_DF['Stand Group_Pred_Shift'] = SummaryActivity_DF['Stand Group_Pred'].shift(1)
    OBH_ROP_DF = SummaryActivity_DF.copy()

    OBH_ROP_DF = OBH_ROP_DF[OBH_ROP_DF['LABEL_SubActivity']=='Connection']
    OBH_ROP_DF = OBH_ROP_DF.dropna(subset=['Stand Group_Pred_Shift'])
    OBH_ROP_DF = OBH_ROP_DF[OBH_ROP_DF['Stand Meterage (m) (Drilling)']!=0]
    OBH_ROP_DF['ROP'] = OBH_ROP_DF['Stand Meterage (m) (Drilling)'] / (OBH_ROP_DF['Stand Stand Duration (hrs)']/60)
    OBH_ROP_DF['OBH'] = OBH_ROP_DF['Stand Meterage (m) (Drilling)'] / (OBH_ROP_DF['Stand On Bottom Hours']/60)


    MeterageDrillingDate_DF = SummaryActivity_DF.groupby(['date']).agg(
        {
            "Meterage(m)(Drilling)":"sum",
            "date":"first"
        }
    )
    st.dataframe(MeterageDrillingDate_DF)
    st.dataframe(SummaryActivity_DF)

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
            InputActivity_DB['dt'] = InputActivity_DB['date'].astype('datetime64')
            InputActivity_DB.to_csv('RealTime_Test/Temp_SummaryActivity_tes1.csv', index = False)
            print('uploaded')
        if st.button('submit', key='UserSubmit'):
            st.session_state.FileUploadLogic_SummaryReport = True

    # with st.sidebar():
    if st.sidebar.checkbox("Display Surrounding Well"):
        OffsetWells_Dict = st.multiselect(
    'Selected Surrounding Wells Statistics',
    [i for i in WellList if i != WellName_Select],
    [i for i in WellList if i != WellName_Select])
    SummaryActivity_DF['date_time'] = SummaryActivity_DF['date_time'].astype('datetime64')
    with st.expander('Activity Summary'):
        
        figPie_Activity = px.pie(PieChart_DF, 
                         values='Duration(minutes)',
                         names='LABEL_Activity',
                        #   title="Activity Pie Chart",
                          labels={"LABEL_Activity":"Activity", "Duration(minutes)":"Duration"}
                          
        )
        figPie_Activity.update_traces( textinfo='percent+label')
        st.plotly_chart(figPie_Activity)
    with st.expander('SubActivity Summary'):
        figPie_SubActivity = px.pie(PieChart_DF, 
                         values='Duration(minutes)',
                         names='LABEL_SubActivity',
                        #   title="Sub Activity Pie Chart",
                          labels={"LABEL_SubActivity":"Sub Activity", "Duration(minutes)":"Duration"}
                          
        )
        figPie_SubActivity.update_traces( textinfo='percent+label')
        # figPie_SubActivity = px.pie(PieChart_DF, values='Duration(minutes)', names='LABEL_SubActivity')
        st.plotly_chart(figPie_SubActivity)        
        # figSunBurst = px.sunburst(PieChart_DF, path=['LABEL_Activity', 'LABEL_SubActivity'], values='Duration(minutes)')
        # st.plotly_chart(figSunBurst)
        # st.markdown("<h1 style='text-align: center; font-size: 50px;margin-top: 300px;'>  Welcome !</h1>", unsafe_allow_html=True)

    with st.expander('Stand Time Breakdown'):
        # figStandTimeBreakdown = px.bar(StandTimeBreakdown_DF, x='date_time', y=['RotateDrilling', 'Slide Drilling','ReamingTime','ConnectionTime'], width=1000, height=1000)
        figStandTimeBreakdown = px.bar(SummaryActivity_DF.dropna(subset=['Stand Group_Pred', "Duration(minutes)"]), x='Stand Group_Pred', y="Duration(minutes)", color="LABEL_SubActivity", width=1000, height=1000)
        # figStandTimeBreakdown.update_xaxes(type='category')
        figStandTimeBreakdown.update_layout(
                        # title="Title",
                        xaxis=dict(
                            title="Stand Group"
                        ),
                        yaxis=dict(
                            title="Duration(Minutes)"
                        ) ) 
        st.plotly_chart(figStandTimeBreakdown)
        
    with st.expander("Time vs Depth"):
        figTimeDepth = px.scatter( x=SummaryActivity_DF["date_time"], 
                                   y=-SummaryActivity_DF["Hole Depth(max)"],
                                   color=SummaryActivity_DF['LABEL_SubActivity'])
        figTimeDepth.update_layout(
                        # title="Title",
                        xaxis=dict(
                            title="Date - Time"
                        ),
                        yaxis=dict(
                            title="Meterage Drilling(m)"
                        ) ) 
        st.plotly_chart(figTimeDepth)

        

    with st.expander("Meterage Drilling per Date"):
        layoutMeterageDrillingDate = go.Layout(
                        # title="Title",
                        xaxis=dict(
                            title="Date"
                        ),
                        yaxis=dict(
                            title="Meterage Drilling(m)"
                        ) ) 
        figMeterageDrillingDate = go.Figure(go.Waterfall(
            name = "20", 
            # orientation = "v",
            # measure = 'relative',
            x = MeterageDrillingDate_DF['date'],
            textposition = "outside",
            # text = ["+60", "+80", "", "-40", "-20", "Total"],
            y = -MeterageDrillingDate_DF['Meterage(m)(Drilling)'],
            connector = {"line":{"color":"rgb(63, 63, 63)"}},

        )
            ,layout = layoutMeterageDrillingDate
        )

        # figMeterageDrillingDate.update_layout(
        #         title = "Meterage Drilling By Date",
        #         showlegend = True,
        #         xaxis_label='depth'
        # )
        st.plotly_chart(figMeterageDrillingDate)

    with st.expander("ROP On Bottom and Stand"):
    

        figOBH_ROP = go.Figure(
            px.bar(OBH_ROP_DF, 
            x="date_time", 
            y=['OBH','ROP'] ,
            barmode='group',
            # width=1000,

            ),
                    # layout = layoutOBH_ROP
        )
        figOBH_ROP.update_layout(
                        # title="Title",
                        xaxis=dict(
                            title="Date - Time"
                        ),
                        yaxis=dict(
                            title="On Bottom Hours(m/hr)"
                        ) ) 
        st.plotly_chart(figOBH_ROP)
        
    if st.button('download as report'):

        figPie_Activity.write_image("RealTime_Test/Fig_temp/figPie_Activity.png")
        figPie_SubActivity.write_image("RealTime_Test/Fig_temp/figPie_SubActivity.png")
        figStandTimeBreakdown.write_image("RealTime_Test/Fig_temp/figStandTimeBreakdown.png")
        figTimeDepth.write_image("RealTime_Test/Fig_temp/figTimeDepth.png")
        figMeterageDrillingDate.write_image("RealTime_Test/Fig_temp/layoutMeterageDrillingDate.png")
        figOBH_ROP.write_image("RealTime_Test/Fig_temp/layoutOBH_ROP.png")
        pdf = FPDF()
        pdf.add_page()
        # pdf.cell(30, 10, 'Activity Mapping Report', 1, 0, 'C')
        pdf.image("RealTime_Test/Fig_temp/figPie_Activity.png",w = 170, h = 140)
        # pdf.add_page()
        pdf.image("RealTime_Test/Fig_temp/figPie_SubActivity.png",w = 170, h = 140)
        # pdf.add_page()
        pdf.image("RealTime_Test/Fig_temp/figStandTimeBreakdown.png",w = 170, h = 140)
        # pdf.add_page()
        pdf.image("RealTime_Test/Fig_temp/figTimeDepth.png",w = 170, h = 140)
        # pdf.add_page()
        pdf.image("RealTime_Test/Fig_temp/layoutMeterageDrillingDate.png",w = 170, h = 140)
        # pdf.add_page()
        pdf.image("RealTime_Test/Fig_temp/layoutOBH_ROP.png",w = 170, h = 140)

        # pdf.output('tuto2.pdf', 'F')
        html = create_download_link(pdf.output(dest="S").encode("latin-1"), "test")
        st.markdown(html, unsafe_allow_html=True)
        # with open("post1-compressed.pdf", "rb") as pdf_file:
        #     PDFbyte = pdf_file.read()
        # st.download_button('Download binary file', pdf)





        # for keys_fig in dict_list_fig.keys():
        #     plotly_write_image(dict_list_fig[keys_fig], (fig_folder_temp + keys_fig), format='png')
        #     png_renderer = pio.renderers["png"]
        #     png_renderer


    # with st.expander("Stand Time Breakdown"):
    #     # st.markdown("<h1 style='text-align: center; font-size: 5px;margin-top: 300px;'>  Welcome !</h1>", unsafe_allow_html=True)  
    #     st.plotly_chart(figConnectionTime)
else:
    st.markdown("<h1 style='text-align: center; font-size: 130px;margin-top: 300px;'>  Welcome !</h1>", unsafe_allow_html=True)