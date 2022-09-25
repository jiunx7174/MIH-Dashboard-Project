import streamlit as st
from datetime import datetime, timedelta
# import 
from PDU_Func import IO_Data,Activity
import time
import pandas as pd
import numpy as np
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
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


def to_excel(df, sheet_name="Sheet1"):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name=sheet_name)
    # workbook = writer.book
    # worksheet = writer.sheets[sheet_name]
    # format1 = workbook.add_format({'num_format': '0.00'}) 
    # worksheet.set_column('A:A', None, format1)  
    writer.save()
    processed_data = output.getvalue()
    return processed_data


def InputTranslator(Input_DB):
    Input_DB['dt'] = (Input_DB['dt']).apply(lambda d: pd.to_datetime(str(d)))

    Input_DB.rename(columns = {'in_slip_threshold':'Hook Treshold', 'activity':'Activity'}, inplace = True)
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
    Activity_DF = IO_Data.getActivityData_v2(well_id, StartDateTime_select, EndDateTime_select)
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


def App_v05():
    if 'SelectDateLogic' not in st.session_state:
        st.session_state.SelectDateLogic = False

    if 'FileUploadLogic_SummaryReport' not in st.session_state:
        st.session_state.FileUploadLogic_SummaryReport = False

    if 'UpdateRTData' not in st.session_state:
        st.session_state.UpdateRTData = False

    if 'StartDateTime_select' not in st.session_state:
        st.session_state.StartDateTime_select = False
    if 'EndDateTime_select' not in st.session_state:
        st.session_state.EndDateTime_select = True


    # App started from here
    st.markdown('<h1 style="text-align: center; font-size: 50px; margin-top: 2px;"><span style="text-decoration: underline;">ACTIVITY MAPPING MODULE</span></h1>', unsafe_allow_html=True)
    try:
        # select date
        st.session_state.Datetime_start = (st.session_state.WellName_DF.loc[st.session_state.WellName_DF['well_name']==st.session_state.WellName_Select, 'active_date']).to_list()[0]
        st.session_state.Datetime_end = (st.session_state.WellName_DF.loc[st.session_state.WellName_DF['well_name']==st.session_state.WellName_Select, 'end_date']).to_list()[0]

        # if selected date are newer than current date
        if st.session_state.Datetime_end > datetime.now().date():
            st.session_state.Datetime_end = datetime.now().date()
    except Exception as error_msg:
    
        st.session_state.Datetime_start = datetime.now().date()
        st.session_state.Datetime_end = datetime.now().date()

        print(error_msg)
        # None

    # Sidebar date input form button 
    with st.sidebar.form(key='DateInput'):
        sideStart_col1,sideStart_col2 = st.columns(2)

        StartDate = sideStart_col1.date_input('Start Date-Time',value=(st.session_state.Datetime_end - timedelta(days=2)), key='StartDate')
        StartTime = sideStart_col2.time_input('',value=datetime.strptime('00:00:00', '%H:%M:%S'), key='StartTime')

        InputActivityLog_date_start = datetime.combine(st.session_state.Datetime_start - timedelta(days=1), datetime.strptime('00:00:00', '%H:%M:%S').time())
        InputActivityLog_date_end =  datetime.combine(st.session_state.Datetime_end + timedelta(days=1), datetime.strptime('00:00:00', '%H:%M:%S').time())

        st.session_state.StartDateTime_select = datetime.combine(StartDate, StartTime)


        sideEnd_col1,sideEnd_col2 = st.columns(2)


        EndDate = sideEnd_col1.date_input('End Date-Time',value=st.session_state.Datetime_end, key='EndDate')
        EndTime = sideEnd_col2.time_input('',value=datetime.strptime('00:00:00', '%H:%M:%S'), key='EndTime')
        st.session_state.EndDateTime_select = datetime.combine(EndDate, EndTime)
        if st.form_submit_button('Select Date'):
            st.session_state.SelectDateLogic = True
            st.session_state.UpdateRTData = True

    # 
    if (st.session_state.SelectDateLogic == True):
        print(st.session_state.StartDateTime_select)
        print(st.session_state.EndDateTime_select)
        print(st.session_state.Well_ID_API)

        ActivitySummary_TimeStart = str(st.session_state.StartDateTime_select - timedelta(hours=3))
        ActivitySummary_TimeEnd = str(st.session_state.EndDateTime_select +timedelta(hours=3))

        ActivitySummary_DF_Dome = IO_Data.DomeGetData(st.session_state.Well_ID_API, ActivitySummary_TimeStart, ActivitySummary_TimeEnd, table_type="Activity Summary")
        ActivitySummary_DF_Dome['STATUS'] = 'FIRM'
        # st.text(ActivitySummary_TimeStart)
        # st.text(ActivitySummary_TimeEnd)
        try:
            RT_5second_TimeStart = pd.to_datetime(ActivitySummary_DF_Dome['End Time'].tail(5).to_list()[0])
        except:
            RT_5second_TimeStart = pd.to_datetime(ActivitySummary_TimeStart)

        RT_5second_TimeEnd = pd.to_datetime(ActivitySummary_TimeEnd)

        # st.text((RT_5second_TimeStart).strftime("%Y-%m-%d %H:%M:%S"))
        # st.text(RT_5second_TimeEnd.strftime("%Y-%m-%d %H:%M:%S"))

        # st.title("Activity Mapping Module")
        
        try:
            if st.session_state.UpdateRTData:
                st.session_state.UpdateRTData = None
                st.session_state.Activity_DF = cache_RealTime_Data(st.session_state.Well_ID, 
                                                                    RT_5second_TimeStart.strftime("%Y-%m-%d %H:%M:%S"),
                                                                    RT_5second_TimeEnd.strftime("%Y-%m-%d %H:%M:%S"))
                st.session_state.UpdateRTData = False
            error_stop = True
        except:
            st.markdown('<h2 style="text-align: center; font-size: 30px; margin-top: 300px;"><span style="color: #000000;"><em>Inputed Date is Incorrect</em></span></h2>', unsafe_allow_html=True)
            error_stop = False
        if error_stop:
            # Well_ID = st.session_state.WellName_DF.loc[st.session_state.WellName_DF['well_name'] == st.session_state.WellName_Select, 'wid']
            # time_date_start = st.session_state.WellName_DF.loc[st.session_state.WellName_DF['well_name'] == st.session_state.WellName_Select, 'wid']
            # time_date_end = st.session_state.WellName_DF.loc[st.session_state.WellName_DF['well_name'] == st.session_state.WellName_Select, 'wid']
            # Well_ID =int(Well_ID.values)
            print("desire WellID = ")
            print(st.session_state.Well_ID_API)
            
            if IO_Data.DomeCekTable(st.session_state.Well_ID_API)['table']==0:
                IO_Data.DomeCreateTable(st.session_state.Well_ID_API)
            print("tes")
            print(str(InputActivityLog_date_start))
            print(str(InputActivityLog_date_end))
            # Table_col = st.columns(1)
            Activity_DF = st.session_state.Activity_DF
            # InputActivity_DB = GenerateInputActivity_DB(flag=True)
            InputActivity_DB = IO_Data.dict2DF(IO_Data.DomeGetData(st.session_state.Well_ID_API, str(InputActivityLog_date_start), str(InputActivityLog_date_end)))
            print("test")

            # InputActivity_DB = IO_Data.GetInputActivity_DB(IO_Data.OpenConnection(), st.session_state.WellName_Select, CompName_Select)
            # InputActivity_DB = pd.read_csv('RealTime_Test/Temp_InputActivity.csv', index_col = False)

            with st.form(key='Activity Input:'):
                st.markdown('### Major Activity Input')
                cols = st.columns(7)
                Date_Temp = cols[0].date_input(
                            "Date", value= st.session_state.Datetime_end, key='InputDate'
                            )
                Time_Temp = cols[1].time_input(
                            "Time",value=datetime.strptime('00:00:00', '%H:%M:%S'),  key='InputTime'
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

                    # InputID_temp = InputActivity_DB['input_id'].max() + 1
                    InputDict = {
                        # 'input_id':InputID_temp,
                            'wid':st.session_state.Well_ID_API,
                            'dt':str(datetime.combine(Date_Temp, Time_Temp)),
                            'date':str(Date_Temp),
                            'time':str(Time_Temp),
                            # 'comp':CompName_Select,
                            # 'well':st.session_state.WellName_Select,
                            'activity':Activity_Temp,
                            'in_slip_threshold':HookTreshold_Temp,
                            'remarks':Remarks_Temp,
                            'pic':PIC_Temp,
                            'section':Section_Temp
                    }
                    print("test input")
                    print(InputDict)
                    IO_Data.DomeAddData(InputDict)
                    st.success("activity input success")
                    





                
            Table_col = st.columns(1)
            Table_col[0].markdown('### Activity Log')
            Table_col[0].text('To Do')
            Table_col[0].text('- solve Aggrid reloading')

            # General = st.columns(1)
                
            # print('tes')
            # gb = GridOptionsBuilder.from_dataframe(InputActivity_DB[InputActivity_DB['Comp-Well']==CompWell_Name])
            # with st.form(key='Activity Edit:'):
            used_columns = {"date":"Date", "time":"Time", "well":"Well", "comp":"Company", "section":"Section", "activity":"Major Activity", "in_slip_threshold":"In-Slip Threshold", "remarks":"Additional Remarks", "pic":"PIC"
            }

            # InputActivity_DB = IO_Data.GetInputActivity_DB(IO_Data.OpenConnection(), st.session_state.WellName_Select, CompName_Select)
            InputActivity_DB = IO_Data.dict2DF(IO_Data.DomeGetData(st.session_state.Well_ID_API, str(InputActivityLog_date_start), str(InputActivityLog_date_end)))
            if(InputActivity_DB.empty):
                InputActivity_DB = pd.DataFrame(columns=['input_id'] + list(used_columns.values()))
                st.warning("Activity Log Table are not found please submit new data and/or resubmit it")

            InputActivity_DB['well'] = st.session_state.WellName_Select
            InputActivity_DB['comp'] = st.session_state.CompName_Select

            print(InputActivity_DB.columns)
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

                    IO_Data.DomeDelete(st.session_state.Well_ID_API,dt_temp['input_id'])
                InputActivity_DB = IO_Data.dict2DF(IO_Data.DomeGetData(st.session_state.Well_ID_API, str(InputActivityLog_date_start), str(InputActivityLog_date_end)))

                st.success("activity deleted")
            


            with st.expander("Download your Activity Log Table"):
                st.download_button(
                    label="Download Activity Log Table as CSV",
                    data=convert_df(InputActivity_DB),
                    file_name=st.session_state.CompName_Select + "_"+ st.session_state.WellName_Select + '_ActivityLogTable.csv',
                    mime='text/csv',
                )


            
            



            # ######## below are Activity Summary Table #########################

            if not (InputActivity_DB.empty):
                # elif(InputActivityLog_date_start)
                with st.spinner(text="Generate Activity Summary..."):
                    Table_col_2 = st.columns(1)

                    Input_Temp = InputTranslator(InputActivity_DB)

                    Activity_DF = Activity.GetActivity_DF(Activity_DF, Input_Temp)

                    Activity_DF = Activity.GetSubActivity_DF_v3(Activity_DF)

                    



                    Table_col_2[0].markdown('### Activity Summary Table')
                    Table_col_2[0].text('To Do: ')


                    RadioButton = Table_col_2[0].radio("Apply FALSE Sensor Filter?",
                                    ('Yes', 'No/RAW'), key='RadioButton'
                                    )

                    if RadioButton=='No/RAW':
                        SummaryActivity_DF = Activity.labelStand_v2(Activity.GenerateDuration_DF_v4(Activity_DF))
                    else:
                        SummaryActivity_DF = Activity.labelStand_v2(Activity.cleanFalseSensor((Activity.GenerateDuration_DF_v4(Activity_DF))))

                        # Activity.GenerateDuration_DF_v4(Activity_DF)
                    SummaryActivity_DF['Stand Group_Pred'] = 0
                    # print(SummaryActivity_DF.columns)
                    Summary_Used_Columns = {
                        "STATUS":"STATUS",
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
                        "Stand Group_Pred":"Stand Group_Pred", #to be check
                        "Stand Duration":"Stand Duration",
                        "Stand Meterage (m) (Drilling)":"Total Stand Drilling Meterage (m)",
                        "Stand Stand Duration (hrs)":"Total Stand Duration (hrs)",
                        "Stand On Bottom Hours": "Total On Bottom Duration (hrs)",
                        "pic":"PIC",
                        "remarks":"Remarks",
                        "section":"Section",
                    }



                    if ActivitySummary_DF_Dome.empty:
                        SummaryActivity_DF_temp = SummaryActivity_DF.copy()
                    else:
                        SummaryActivity_DF_temp = SummaryActivity_DF.loc[SummaryActivity_DF['Time_start'] >= ActivitySummary_DF_Dome['End Time'].max(),:].copy()
                    SummaryActivity_DF_temp['STATUS'] = 'ON REVIEW'

                    SummaryActivity_DF_temp.rename(columns=Summary_Used_Columns, inplace=True)



                    ActivitySummary_AgGrid = pd.concat([ActivitySummary_DF_Dome[list(Summary_Used_Columns.values())],
                                                                        SummaryActivity_DF_temp[list(Summary_Used_Columns.values())]],
                                                                        ignore_index=True
                                                                        )

                    # totrows = df.shape[0])
                    # gb. Configure your aggrid initially with
                    
                    gb_2 = GridOptionsBuilder.from_dataframe(ActivitySummary_AgGrid)
                    gb_2.configure_selection('multiple', use_checkbox=True)
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
                    gb_2.configure_column("SUB-ACTIVITY", editable=True, cellEditor='agSelectCellEditor', cellEditorPopup=True, cellEditorParams={

                            'values': ["Wash Up/Down",
                                        "Reaming",
                                        "Moving",
                                        "Circulation",
                                        "Connection",
                                        "Stationary",
                                        "Rotary Drilling",
                                        "Slide Drilling",
                                        "Look and define",
                                        "CEMENTING JOB",
                                        "CONNECTION",
                                        "LAY DOWN BHA",
                                        "MAKE UP BHA",
                                        "NPT",
                                        "N/D BOP",
                                        "N/U BOP",
                                        "RUNNING CASING IN",
                                        "STATIONARY",
                                        "STUCK PIPE",
                                        "WAIT ON CEMENT",
                                        "RIG REPAIR",
                                        "nan"
                                            ],
                                        }
                                    )


                    gb_2.configure_column("STATUS", cellStyle=JsCode("""
                                            function(params) {
                                                if (params.value == 'FIRM') {
                                                    return {
                                                        'color': 'white',
                                                        'backgroundColor': 'seagreen'
                                                    }
                                                } else {
                                                    return {
                                                        'color': 'white',
                                                        'backgroundColor': 'darkorange'
                                                    }
                                                }
                                            };
                                            """))
                    gb_2.configure_column("ACTIVITY", cellStyle=JsCode("""
                                            function(params) {
                                            return {
                                                        'color': 'black',
                                                        'backgroundColor': 'peachpuff'
                                                    }
                                            };
                                            """)
                                            )
                    gb_2.configure_column("SUB-ACTIVITY", cellStyle=JsCode("""
                                            function(params) {
                                            return {
                                                        'color': 'black',
                                                        'backgroundColor': 'azure'
                                                    }
                                            };
                                            """)
                                            )

                # if FormButton_a:


                    gridOptions = gb_2.build()


                    SummaryActivityGrid_response = AgGrid(
                            ActivitySummary_AgGrid, 
                            gridOptions=gridOptions,
                            allow_unsafe_jscode=True,
                            height=1000, 
                            # width='100%',
                            data_return_mode=DataReturnMode.AS_INPUT, 
                            update_mode=(GridUpdateMode.SELECTION_CHANGED | GridUpdateMode.MODEL_CHANGED),
                            
                    )
                    SummaryDF_Finalize = SummaryActivityGrid_response['data']

                    # SummaryActivity_DF.to_csv('RealTime_Test/Temp_SummaryActivity.csv', index = False)
                    
                    
                    # st.table(Activity_DF.head(20))

                    # csv = convert_df(my_large_df)
                    st.download_button(
                        label="Download Summary data as CSV",
                        data=convert_df(ActivitySummary_AgGrid),
                        file_name=st.session_state.CompName_Select + "_"+ st.session_state.WellName_Select + '_ActivitySummary.csv',
                        mime='text/csv',
                    )
                    st.download_button(
                        label="Download Realtime(5second) data as CSV",
                        data=convert_df(Activity_DF),
                        file_name=st.session_state.CompName_Select + "_"+ st.session_state.WellName_Select + '_RT_5second_Data.csv',
                        mime='text/csv',
                    )

                    if st.button(label="Finalize"):
                        SummaryDF_Finalize.to_excel('finalize.xlsx')
                        print('TEST')
                        print(SummaryActivityGrid_response['selected_rows'])
                        # st.dataframe(pd.DataFrame(SummaryActivityGrid_response['selected_rows']))
                        with st.spinner("Finalizing Activity Summary...."):

                            IO_Data.UploadActivitySummary(pd.DataFrame(SummaryActivityGrid_response['selected_rows']), st.session_state.Well_ID_API)
                        st.success("Success!")
                        # InputActivityGrid_response
                        # IO_Data.InsertSummaryActivity_DB(IO_Data.OpenConnection(), SummaryActivity_DF, st.session_state.WellName_Select, st.session_state.CompName_Select)
            else:
                st.warning("Please Input Activity Log Table first before generate Activity Summary Table")
    else:
        st.markdown("<h1 style='text-align: center; font-size: 50px;margin-top: 300px;'>  Welcome !</h1>", unsafe_allow_html=True)



# before Summary editor
def App_v06():
    if 'SelectDateLogic' not in st.session_state:
        st.session_state.SelectDateLogic = False

    if 'FileUploadLogic_SummaryReport' not in st.session_state:
        st.session_state.FileUploadLogic_SummaryReport = False

    if 'UpdateRTData' not in st.session_state:
        st.session_state.UpdateRTData = False

    if 'StartDateTime_select' not in st.session_state:
        st.session_state.StartDateTime_select = False
    if 'EndDateTime_select' not in st.session_state:
        st.session_state.EndDateTime_select = True


    # App started from here
    st.markdown('<h1 style="text-align: center; font-size: 50px; margin-top: 2px;"><span style="text-decoration: underline;">ACTIVITY MAPPING MODULE</span></h1>', unsafe_allow_html=True)
    try:
        # select date
        st.session_state.Datetime_start = (st.session_state.WellName_DF.loc[st.session_state.WellName_DF['well_name']==st.session_state.WellName_Select, 'active_date']).to_list()[0]
        st.session_state.Datetime_end = (st.session_state.WellName_DF.loc[st.session_state.WellName_DF['well_name']==st.session_state.WellName_Select, 'end_date']).to_list()[0]

        # if selected date are newer than current date
        if st.session_state.Datetime_end > datetime.now().date():
            st.session_state.Datetime_end = datetime.now().date()
    except Exception as error_msg:
    
        st.session_state.Datetime_start = datetime.now().date()
        st.session_state.Datetime_end = datetime.now().date()

        print(error_msg)
        # None

    # Sidebar date input form button 
    with st.sidebar.form(key='DateInput'):
        sideStart_col1,sideStart_col2 = st.columns(2)

        StartDate = sideStart_col1.date_input('Start Date-Time',value=(st.session_state.Datetime_end - timedelta(days=2)), key='StartDate')
        StartTime = sideStart_col2.time_input('',value=datetime.strptime('00:00:00', '%H:%M:%S'), key='StartTime')

        InputActivityLog_date_start = datetime.combine(st.session_state.Datetime_start - timedelta(days=1), datetime.strptime('00:00:00', '%H:%M:%S').time())
        InputActivityLog_date_end =  datetime.combine(st.session_state.Datetime_end + timedelta(days=1), datetime.strptime('00:00:00', '%H:%M:%S').time())

        st.session_state.StartDateTime_select = datetime.combine(StartDate, StartTime)


        sideEnd_col1,sideEnd_col2 = st.columns(2)


        EndDate = sideEnd_col1.date_input('End Date-Time',value=st.session_state.Datetime_end, key='EndDate')
        EndTime = sideEnd_col2.time_input('',value=datetime.strptime('00:00:00', '%H:%M:%S'), key='EndTime')
        st.session_state.EndDateTime_select = datetime.combine(EndDate, EndTime)
        if st.form_submit_button('Select Date'):
            st.session_state.SelectDateLogic = True
            st.session_state.UpdateRTData = True

    # 
    if (st.session_state.SelectDateLogic == True):
        # print(st.session_state.StartDateTime_select)
        # print(st.session_state.EndDateTime_select)
        # print(st.session_state.Well_ID_API)


        ActivitySummary_TimeStart = str(st.session_state.StartDateTime_select - timedelta(hours=3))
        ActivitySummary_TimeEnd = str(st.session_state.EndDateTime_select +timedelta(hours=3))
        if IO_Data.DomeCekTable(st.session_state.Well_ID_API, table_type="Activity Summary")['table']==0:
            IO_Data.DomeCreateTable(st.session_state.Well_ID_API, table_type="Activity Summary")
        
        # print(IO_Data.DomeCekTable(st.session_state.Well_ID_API, table_type="Activity Summary"))
        # print(IO_Data.DomeCekTable(st.session_state.Well_ID_API, table_type="Activity Summary"))
        ActivitySummary_DF_Dome = IO_Data.DomeGetData(st.session_state.Well_ID_API, ActivitySummary_TimeStart, ActivitySummary_TimeEnd, table_type="Activity Summary")
        ActivitySummary_DF_Dome['STATUS'] = 'FIRM'

        # st.text(ActivitySummary_TimeStart)
        # st.text(ActivitySummary_TimeEnd)
        try:
            RT_5second_TimeStart = pd.to_datetime(ActivitySummary_DF_Dome['End Time'].tail(5).to_list()[0])
        except:
            RT_5second_TimeStart = pd.to_datetime(ActivitySummary_TimeStart)

        RT_5second_TimeEnd = pd.to_datetime(ActivitySummary_TimeEnd)

        # st.text((RT_5second_TimeStart).strftime("%Y-%m-%d %H:%M:%S"))
        # st.text(RT_5second_TimeEnd.strftime("%Y-%m-%d %H:%M:%S"))

        # st.title("Activity Mapping Module")
        
        try:
            if st.session_state.UpdateRTData:
                st.session_state.UpdateRTData = None
                st.session_state.Activity_DF = cache_RealTime_Data(st.session_state.Well_ID, 
                                                                    RT_5second_TimeStart.strftime("%Y-%m-%d %H:%M:%S"),
                                                                    RT_5second_TimeEnd.strftime("%Y-%m-%d %H:%M:%S"))
                st.session_state.UpdateRTData = False
            error_stop = True
        except:
            st.markdown('<h2 style="text-align: center; font-size: 30px; margin-top: 300px;"><span style="color: #000000;"><em>Inputed Date is Incorrect</em></span></h2>', unsafe_allow_html=True)
            error_stop = False
        if error_stop:
            # Well_ID = st.session_state.WellName_DF.loc[st.session_state.WellName_DF['well_name'] == st.session_state.WellName_Select, 'wid']
            # time_date_start = st.session_state.WellName_DF.loc[st.session_state.WellName_DF['well_name'] == st.session_state.WellName_Select, 'wid']
            # time_date_end = st.session_state.WellName_DF.loc[st.session_state.WellName_DF['well_name'] == st.session_state.WellName_Select, 'wid']
            # Well_ID =int(Well_ID.values)
            # print("desire WellID = ")
            # print(st.session_state.Well_ID_API)
            
            if IO_Data.DomeCekTable(st.session_state.Well_ID_API)['table']==0:
                IO_Data.DomeCreateTable(st.session_state.Well_ID_API)
            # print("tes")
            # print(str(InputActivityLog_date_start))
            # print(str(InputActivityLog_date_end))
            # Table_col = st.columns(1)
            Activity_DF = st.session_state.Activity_DF
            # InputActivity_DB = GenerateInputActivity_DB(flag=True)
            InputActivity_DB = (IO_Data.DomeGetData(st.session_state.Well_ID_API, str(InputActivityLog_date_start), str(InputActivityLog_date_end)))
            # print("test")

            # InputActivity_DB = IO_Data.GetInputActivity_DB(IO_Data.OpenConnection(), st.session_state.WellName_Select, CompName_Select)
            # InputActivity_DB = pd.read_csv('RealTime_Test/Temp_InputActivity.csv', index_col = False)

            with st.form(key='Activity Input:'):
                st.markdown('### Major Activity Input')
                cols = st.columns(7)
                Date_Temp = cols[0].date_input(
                            "Date", value= st.session_state.Datetime_end, key='InputDate'
                            )
                Time_Temp = cols[1].time_input(
                            "Time",value=datetime.strptime('00:00:00', '%H:%M:%S'),  key='InputTime'
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

                    # InputID_temp = InputActivity_DB['input_id'].max() + 1
                    InputDict = {
                        # 'input_id':InputID_temp,
                            'wid':st.session_state.Well_ID_API,
                            'dt':str(datetime.combine(Date_Temp, Time_Temp)),
                            'date':str(Date_Temp),
                            'time':str(Time_Temp),
                            # 'comp':CompName_Select,
                            # 'well':st.session_state.WellName_Select,
                            'activity':Activity_Temp,
                            'in_slip_threshold':HookTreshold_Temp,
                            'remarks':Remarks_Temp,
                            'pic':PIC_Temp,
                            'section':Section_Temp
                    }
                    # print("test input")
                    # print(InputDict)
                    IO_Data.DomeAddData(InputDict)
                    st.success("activity input success")
                    





                
            Table_col = st.columns(1)
            Table_col[0].markdown('### Activity Log')
            Table_col[0].text('To Do')
            Table_col[0].text('- solve Aggrid reloading')
            Table_col[0].text('- add row color on different section, and date')

            # General = st.columns(1)
                
            # print('tes')
            # gb = GridOptionsBuilder.from_dataframe(InputActivity_DB[InputActivity_DB['Comp-Well']==CompWell_Name])
            # with st.form(key='Activity Edit:'):
            used_columns = {"date":"Date", "time":"Time", "well":"Well", "comp":"Company", "section":"Section", "activity":"Major Activity", "in_slip_threshold":"In-Slip Threshold", "remarks":"Additional Remarks", "pic":"PIC"
            }

            # InputActivity_DB = IO_Data.GetInputActivity_DB(IO_Data.OpenConnection(), st.session_state.WellName_Select, CompName_Select)
            InputActivity_DB = (IO_Data.DomeGetData(st.session_state.Well_ID_API, str(InputActivityLog_date_start), str(InputActivityLog_date_end)))
            if(InputActivity_DB.empty):
                InputActivity_DB = pd.DataFrame(columns=['input_id'] + list(used_columns.values()))
                st.warning("Activity Log Table are not found please submit new data and/or resubmit it")

            InputActivity_DB['well'] = st.session_state.WellName_Select
            InputActivity_DB['comp'] = st.session_state.CompName_Select

            # print(InputActivity_DB.columns)
            InputActivity_DB_temp = InputActivity_DB.copy()
            InputActivity_DB_temp.rename(columns=used_columns, inplace=True)

            gb = GridOptionsBuilder.from_dataframe(InputActivity_DB_temp[list(used_columns.values())])
            # gb = GridOptionsBuilder.from_dataframe((InputActivity_DB[used_columns.keys()]).rename(columns=used_columns, inplace=True))
            

            gb.configure_selection('multiple', use_checkbox=True)
            Button_col_1 = st.columns(3)
            if Button_col_1[1].button(label="Select all row"):
                gb.configure_selection("multiple",use_checkbox=True, pre_selected_rows=np.arange(0,InputActivity_DB_temp.shape[0]).tolist())
            
            
            # gb_reload_Data = False

            gridOptions = gb.build()

            InputActivityGrid_response = AgGrid(
                    InputActivity_DB_temp, 
                    gridOptions=gridOptions,
                    data_return_mode=DataReturnMode.AS_INPUT, 
                    update_mode=(GridUpdateMode.MANUAL),
                    # reload_data = True
            )
            st.dataframe(pd.DataFrame(InputActivityGrid_response['selected_rows']))



            
            # Button_col_1 = st.columns(3)
            if Button_col_1[0].button('Clear Selected Row', key='refresh'):
                list_selected =[]
                for dt_temp in InputActivityGrid_response['selected_rows']:

                    IO_Data.DomeDelete(st.session_state.Well_ID_API,dt_temp['input_id'])
                InputActivity_DB = (IO_Data.DomeGetData(st.session_state.Well_ID_API, str(InputActivityLog_date_start), str(InputActivityLog_date_end)))

                st.success("activity deleted")
            # else:



            with st.expander("Download your Activity Log Table"):
                st.download_button(
                    label="Download Activity Log Table as CSV",
                    data=convert_df(InputActivity_DB),
                    file_name=st.session_state.CompName_Select + "_"+ st.session_state.WellName_Select + '_ActivityLogTable.csv',
                    mime='text/csv',
                )


            
            



            # ######## below are Activity Summary Table #########################

            Table_col_2 = st.columns(1)
            Table_col_2[0].markdown('### Activity Summary Table')
            if not (InputActivity_DB.empty):
                # elif(InputActivityLog_date_start)
                with st.spinner(text="Generate Activity Summary..."):

                    Input_Temp = InputTranslator(InputActivity_DB)

                    Activity_DF = Activity.GetActivity_DF(Activity_DF, Input_Temp)

                    Activity_DF = Activity.GetSubActivity_DF_v3(Activity_DF)

                    



                    Table_col_2[0].text('To Do: ')


                    RadioButton = Table_col_2[0].radio("Apply FALSE Sensor Filter?",
                                    ('Yes', 'No/RAW'), key='RadioButton'
                                    )

                    if RadioButton=='No/RAW':
                        SummaryActivity_DF = Activity.labelStand_v2(Activity.GenerateDuration_DF_v4(Activity_DF))
                    else:
                        SummaryActivity_DF = Activity.labelStand_v2(Activity.cleanFalseSensor((Activity.GenerateDuration_DF_v4(Activity_DF))))

                        # Activity.GenerateDuration_DF_v4(Activity_DF)
                    SummaryActivity_DF['Stand Group_Pred'] = 0
                    # print(SummaryActivity_DF.columns)
                    Summary_Used_Columns = {
                        "STATUS":"STATUS",
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
                        "Stand Group_Pred":"Stand Group_Pred", #to be check
                        "Stand Duration":"Stand Duration",
                        "Stand Meterage (m) (Drilling)":"Total Stand Drilling Meterage (m)",
                        "Stand Stand Duration (hrs)":"Total Stand Duration (hrs)",
                        "Stand On Bottom Hours": "Total On Bottom Duration (hrs)",
                        "pic":"PIC",
                        "remarks":"Remarks",
                        "section":"Section",
                    }



                    if ActivitySummary_DF_Dome.empty:
                        SummaryActivity_DF_temp = SummaryActivity_DF.copy()
                    else:
                        SummaryActivity_DF_temp = SummaryActivity_DF.loc[SummaryActivity_DF['Time_start'] >= ActivitySummary_DF_Dome['End Time'].max(),:].copy()
                    SummaryActivity_DF_temp['STATUS'] = 'ON REVIEW'

                    SummaryActivity_DF_temp.rename(columns=Summary_Used_Columns, inplace=True)



                    ActivitySummary_AgGrid = pd.concat([ActivitySummary_DF_Dome[list(Summary_Used_Columns.values())],
                                                                        SummaryActivity_DF_temp[list(Summary_Used_Columns.values())]],
                                                                        ignore_index=True
                                                                        )


                    gb_2 = GridOptionsBuilder.from_dataframe(ActivitySummary_AgGrid)
                    gb_2.configure_selection('multiple', use_checkbox=True)
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
                    gb_2.configure_column("SUB-ACTIVITY", editable=True, cellEditor='agSelectCellEditor', cellEditorPopup=True, cellEditorParams={

                            'values': ["Wash Up/Down",
                                        "Reaming",
                                        "Moving",
                                        "Circulation",
                                        "Connection",
                                        "Stationary",
                                        "Rotary Drilling",
                                        "Slide Drilling",
                                        "Look and define",
                                        "CEMENTING JOB",
                                        "CONNECTION",
                                        "LAY DOWN BHA",
                                        "MAKE UP BHA",
                                        "NPT",
                                        "N/D BOP",
                                        "N/U BOP",
                                        "RUNNING CASING IN",
                                        "STATIONARY",
                                        "STUCK PIPE",
                                        "WAIT ON CEMENT",
                                        "RIG REPAIR",
                                        "nan"
                                            ],
                                        }
                                    )


                    gb_2.configure_column("STATUS", cellStyle=JsCode("""
                                            function(params) {
                                                if (params.value == 'FIRM') {
                                                    return {
                                                        'color': 'white',
                                                        'backgroundColor': 'seagreen'
                                                    }
                                                } else {
                                                    return {
                                                        'color': 'white',
                                                        'backgroundColor': 'darkorange'
                                                    }
                                                }
                                            };
                                            """))
                    gb_2.configure_column("ACTIVITY", cellStyle=JsCode("""
                                            function(params) {
                                            return {
                                                        'color': 'black',
                                                        'backgroundColor': 'peachpuff'
                                                    }
                                            };
                                            """)
                                            )
                    gb_2.configure_column("SUB-ACTIVITY", cellStyle=JsCode("""
                                            function(params) {
                                            return {
                                                        'color': 'black',
                                                        'backgroundColor': 'azure'
                                                    }
                                            };
                                            """)
                                            )

                    gridOptions = gb_2.build()


                    SummaryActivityGrid_response = AgGrid(
                            ActivitySummary_AgGrid, 
                            gridOptions=gridOptions,
                            allow_unsafe_jscode=True,
                            height=1000, 
                            # width='100%',
                            data_return_mode=DataReturnMode.AS_INPUT, 
                            update_mode=(GridUpdateMode.SELECTION_CHANGED | GridUpdateMode.MODEL_CHANGED),
                            
                    )
                    SummaryDF_Finalize = SummaryActivityGrid_response['data']

                    # SummaryActivity_DF.to_csv('RealTime_Test/Temp_SummaryActivity.csv', index = False)
                    
                    
                    # st.table(Activity_DF.head(20))

                    # csv = convert_df(my_large_df)
                # if FormButton_a:
                    st.download_button(
                        label="Download Summary data as CSV",
                        data=convert_df(ActivitySummary_AgGrid),
                        file_name=st.session_state.CompName_Select + "_"+ st.session_state.WellName_Select + '_ActivitySummary.csv',
                        mime='text/csv',
                    )
                    st.download_button(
                        label="Download Realtime(5second) data as CSV",
                        data=convert_df(Activity_DF),
                        file_name=st.session_state.CompName_Select + "_"+ st.session_state.WellName_Select + '_RT_5second_Data.csv',
                        mime='text/csv',
                    )

                    if st.button(label="Finalize"):
                        SummaryDF_Finalize.to_excel('finalize.xlsx')
                        # print('TEST')
                        # print(SummaryActivityGrid_response['selected_rows'])
                        # st.dataframe(pd.DataFrame(SummaryActivityGrid_response['selected_rows']))
                        with st.spinner("Finalizing Activity Summary...."):

                            IO_Data.UploadActivitySummary(pd.DataFrame(SummaryActivityGrid_response['selected_rows']), st.session_state.Well_ID_API)
                        st.success("Success!")
                        # InputActivityGrid_response
                        # IO_Data.InsertSummaryActivity_DB(IO_Data.OpenConnection(), SummaryActivity_DF, st.session_state.WellName_Select, st.session_state.CompName_Select)
            else:
                st.warning("Please Input Activity Log Table first before generate Activity Summary Table")
    else:
        st.markdown("<h1 style='text-align: center; font-size: 50px;margin-top: 300px;'>  Welcome !</h1>", unsafe_allow_html=True)

@st.experimental_memo
def getActivityLogTable(Well_ID_API, InputActivityLog_date_start, InputActivityLog_date_end):
    return (IO_Data.DomeGetData_v2(Well_ID_API, (InputActivityLog_date_start), (InputActivityLog_date_end)))

@st.experimental_memo
def getActivitySummaryTable(Well_ID_API, ActivitySummary_TimeStart, ActivitySummary_TimeEnd):
    ActivitySummary_DF_Dome = IO_Data.DomeGetData_v2(Well_ID_API, ActivitySummary_TimeStart, ActivitySummary_TimeEnd, table_type="Activity Summary")
    # ActivitySummary_DF_Dome.rename(columns=Summary_Used_Columns, inplace=True)
    # psrint("test")
    print(ActivitySummary_DF_Dome)
    return ActivitySummary_DF_Dome
    
@st.experimental_memo
def GetRealTimeData(well_id, StartDateTime_select, EndDateTime_select):
    Activity_DF = IO_Data.getActivityData_v2(well_id, StartDateTime_select, EndDateTime_select)
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

@st.experimental_memo
def GenerateSummaryActivity_DB(Activity_DF, Input_Temp, cleanFalseSensor=True):
    Input_Temp = InputTranslator(Input_Temp)

    Activity_DF = Activity.GetActivity_DF(Activity_DF, Input_Temp)

    Activity_DF = Activity.GetSubActivity_DF_v3(Activity_DF)
    # SummaryActivity_DF = 
    if cleanFalseSensor:
        return Activity.labelStand_v3(Activity.cleanFalseSensor_v3(Activity.cleanFalseSensor_v3(Activity.GenerateDuration_DF_v7(Activity_DF))))
    else:
        return Activity.labelStand_v3(Activity.GenerateDuration_DF_v7(Activity_DF))

# @st.cache(allow_output_mutation=True)
@st.experimental_memo
def MergedSummaryActivity_DB(ActivitySummary_DF_Dome, SummaryActivity_DF,InputActivityLog_date_start,InputActivityLog_date_end):
    print("run Merged Summary")
    Summary_Used_Columns = [
        "STATUS",
        "Date",
        "Start Time",
        "End Time",
        # "date_time",
        "ACTIVITY",
        "SUB-ACTIVITY",
        "CONNECTION-ACTIVITY",
        "Section",
        "Duration (Minutes)",
        "Hole Depth (Max)",
        "Bit Depth(mean)",
        "Drilling Meterage (m)",
        "MERGE_SubActivity-Activity",
        "Rotate Drilling Time (Minutes)",
        "Slide Drilling Time (Minutes)",
        "Reaming Time (Minutes)",
        "Connection Time (Minutes)",
        "Total Stand Drilling Meterage (m)",
        "Total Stand Duration (hrs)",
        "On Bottom state (hrs)",
        "Stand Group",
        "PIC",
        "Remarks",
    ]

    ActivitySummary_DF_Dome['STATUS'] = 'FIRM'
    if ActivitySummary_DF_Dome.empty:
        SummaryActivity_DF_temp = SummaryActivity_DF.copy()
    else:
        SummaryActivity_DF_temp = SummaryActivity_DF.loc[SummaryActivity_DF['Start Time'] >= ActivitySummary_DF_Dome['End Time'].max(),:].copy()
    SummaryActivity_DF_temp['STATUS'] = 'ON REVIEW'

    # print(list(SummaryActivity_DF_temp.columns))
    # SummaryActivity_DF_temp.rename(columns=Summary_Used_Columns, inplace=True)
    # ActivitySummary_DF_Dome.rename(columns=Summary_Used_Columns, inplace=True)

    Out_DF = pd.concat([ActivitySummary_DF_Dome,SummaryActivity_DF_temp],ignore_index=True)
    Out_DF = Out_DF[Summary_Used_Columns]
    return Out_DF


def MergedSummaryActivity_DB_update(ActivitySummary_DF_Dome, SummaryActivity_DF,InputActivityLog_date_start,InputActivityLog_date_end):
    print("run Merged Summary")
    Summary_Used_Columns = [
        "STATUS",
        "Date",
        "Start Time",
        "End Time",
        # "date_time",
        "ACTIVITY",
        "SUB-ACTIVITY",
        "CONNECTION-ACTIVITY",
        "Section",
        "Duration (Minutes)",
        "Hole Depth (Max)",
        "Bit Depth(mean)",
        "Drilling Meterage (m)",
        "MERGE_SubActivity-Activity",
        "Rotate Drilling Time (Minutes)",
        "Slide Drilling Time (Minutes)",
        "Reaming Time (Minutes)",
        "Connection Time (Minutes)",
        "Total Stand Drilling Meterage (m)",
        "Total Stand Duration (hrs)",
        "On Bottom state (hrs)",
        "Stand Group",
        "PIC",
        "Remarks",
    ]

    ActivitySummary_DF_Dome['STATUS'] = 'FIRM'
    if ActivitySummary_DF_Dome.empty:
        SummaryActivity_DF_temp = SummaryActivity_DF.copy()
    else:
        SummaryActivity_DF_temp = SummaryActivity_DF.loc[SummaryActivity_DF['Start Time'] >= ActivitySummary_DF_Dome['End Time'].max(),:].copy()
    SummaryActivity_DF_temp['STATUS'] = 'ON REVIEW'

    # print(list(SummaryActivity_DF_temp.columns))
    # SummaryActivity_DF_temp.rename(columns=Summary_Used_Columns, inplace=True)
    # ActivitySummary_DF_Dome.rename(columns=Summary_Used_Columns, inplace=True)

    Out_DF = pd.concat([ActivitySummary_DF_Dome,SummaryActivity_DF_temp],ignore_index=True)
    Out_DF = Out_DF[Summary_Used_Columns]
    return Out_DF




def App_v07():
    if 'SelectDateLogic' not in st.session_state:
        st.session_state.SelectDateLogic = False

    if 'FileUploadLogic_SummaryReport' not in st.session_state:
        st.session_state.FileUploadLogic_SummaryReport = False

    if 'UpdateRTData' not in st.session_state:
        st.session_state.UpdateRTData = False

    if 'StartDateTime_select' not in st.session_state:
        st.session_state.StartDateTime_select = False
    if 'EndDateTime_select' not in st.session_state:
        st.session_state.EndDateTime_select = True
    if 'CalculateDuration' not in st.session_state:
        st.session_state.CalculateDuration = False


    # App started from here
    st.markdown('<h1 style="text-align: center; font-size: 50px; margin-top: 2px;"><span style="text-decoration: underline;">ACTIVITY MAPPING MODULE</span></h1>', unsafe_allow_html=True)
    try:
        # select date
        st.session_state.Datetime_start = (st.session_state.WellName_DF.loc[st.session_state.WellName_DF['well_name']==st.session_state.WellName_Select, 'active_date']).to_list()[0]
        st.session_state.Datetime_end = (st.session_state.WellName_DF.loc[st.session_state.WellName_DF['well_name']==st.session_state.WellName_Select, 'end_date']).to_list()[0]

        # if selected date are newer than current date
        if st.session_state.Datetime_end > datetime.now().date():
            st.session_state.Datetime_end = datetime.now().date()
    except Exception as error_msg:
    
        st.session_state.Datetime_start = datetime.now().date()
        st.session_state.Datetime_end = datetime.now().date()

        print(error_msg)
        # None

    # Sidebar date input form button 
    with st.sidebar.form(key='DateInput'):
        sideStart_col1,sideStart_col2 = st.columns(2)

        StartDate = sideStart_col1.date_input('Start Date-Time',value=(st.session_state.Datetime_end - timedelta(days=2)), key='StartDate')
        StartTime = sideStart_col2.time_input('',value=datetime.strptime('00:00:00', '%H:%M:%S'), key='StartTime')

        InputActivityLog_date_start = datetime.combine(st.session_state.Datetime_start - timedelta(days=1), datetime.strptime('00:00:00', '%H:%M:%S').time())
        InputActivityLog_date_end =  datetime.combine(st.session_state.Datetime_end + timedelta(days=1), datetime.strptime('00:00:00', '%H:%M:%S').time())

        st.session_state.StartDateTime_select = datetime.combine(StartDate, StartTime)


        sideEnd_col1,sideEnd_col2 = st.columns(2)


        EndDate = sideEnd_col1.date_input('End Date-Time',value=st.session_state.Datetime_end, key='EndDate')
        EndTime = sideEnd_col2.time_input('',value=datetime.strptime('00:00:00', '%H:%M:%S'), key='EndTime')
        st.session_state.EndDateTime_select = datetime.combine(EndDate, EndTime)
        if st.form_submit_button('Select Date'):
            st.session_state.SelectDateLogic = True
            st.session_state.UpdateRTData = True
            try:
                GenerateSummaryActivity_DB.clear()
                # st.session_state.ActivitySummary_AgGrid.loc[:] = None
            except:
                None


    # 
    if (st.session_state.SelectDateLogic == True):


        ActivitySummary_TimeStart = str(st.session_state.StartDateTime_select - timedelta(hours=1))
        ActivitySummary_TimeEnd = str(st.session_state.EndDateTime_select)
        # st.text(ActivitySummary_TimeStart)
        # st.text(ActivitySummary_TimeEnd)
        
        try:
            ActivitySummary_DF_Dome = getActivitySummaryTable(st.session_state.Well_ID_API, ActivitySummary_TimeStart, ActivitySummary_TimeEnd)
        except:
            if IO_Data.DomeCekTable(st.session_state.Well_ID_API, table_type="Activity Summary")['table']==0:
                print('create table of ' + str(st.session_state.Well_ID_API))
                IO_Data.DomeCreateTable(st.session_state.Well_ID_API, table_type="Activity Summary")
            ActivitySummary_DF_Dome = getActivitySummaryTable(st.session_state.Well_ID_API, ActivitySummary_TimeStart, ActivitySummary_TimeEnd)



        try:
            RT_5second_TimeStart = pd.to_datetime(ActivitySummary_DF_Dome['End Time'].tail(5).to_list()[0])
        except:
            RT_5second_TimeStart = pd.to_datetime(ActivitySummary_TimeStart)

        RT_5second_TimeEnd = pd.to_datetime(ActivitySummary_TimeEnd)
        print(" - ")
        print("RT data ")
        print(RT_5second_TimeStart)
        print(RT_5second_TimeEnd)
        print(" - ")


        
        try:

            Activity_DF = GetRealTimeData(st.session_state.Well_ID,
                                                                RT_5second_TimeStart.strftime("%Y-%m-%d %H:%M:%S"),
                                                                RT_5second_TimeEnd.strftime("%Y-%m-%d %H:%M:%S"))

            error_stop = True
        except:
            st.markdown('<h2 style="text-align: center; font-size: 30px; margin-top: 300px;"><em>Inputed Date is Incorrect</em></h2>', unsafe_allow_html=True)
            error_stop = False
        if error_stop:

            

            try:
                InputActivity_DB = getActivityLogTable(st.session_state.Well_ID_API, str(InputActivityLog_date_start), str(InputActivityLog_date_end))
            except:
                if DomeCekTable(st.session_state.Well_ID_API)['table']==0:
                   DomeCreateTable(st.session_state.Well_ID_API)
                InputActivity_DB = getActivityLogTable(st.session_state.Well_ID_API, str(InputActivityLog_date_start), str(InputActivityLog_date_end))

            with st.form(key='Activity Input:'):
                st.markdown('### Major Activity Input')
                cols = st.columns(7)
                Date_Temp = cols[0].date_input(
                            "Date", value= st.session_state.Datetime_end, key='InputDate'
                            )
                Time_Temp = cols[1].time_input(
                            "Time",value=datetime.strptime('00:00:00', '%H:%M:%S'),  key='InputTime'
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

                    # InputID_temp = InputActivity_DB['input_id'].max() + 1
                    InputDict = {
                        # 'input_id':InputID_temp,
                            'wid':st.session_state.Well_ID_API,
                            'dt':str(datetime.combine(Date_Temp, Time_Temp)),
                            'date':str(Date_Temp),
                            'time':str(Time_Temp),
                            # 'comp':CompName_Select,
                            # 'well':st.session_state.WellName_Select,
                            'activity':Activity_Temp,
                            'in_slip_threshold':HookTreshold_Temp,
                            'remarks':Remarks_Temp,
                            'pic':PIC_Temp,
                            'section':Section_Temp
                    }
                    # print("test input")
                    # print(InputDict)
                    IO_Data.DomeAddData(InputDict)
                    getActivityLogTable.clear()
                    st.success("activity input success")
                    # getActivityLogTable.clear()
                    # InputActivity_DB.clear()
                    





                
            # Table_col = st.columns(1)
            # Table_col[0].markdown('### Activity Log')
            # Table_col[0].text('To Do')
            # Table_col[0].text('- solve Aggrid reloading')
            # Table_col[0].text('- add row color on different section, and date')


            used_columns = {"date":"Date", "time":"Time", "well":"Well", "comp":"Company", "section":"Section", "activity":"Major Activity", "in_slip_threshold":"In-Slip Threshold", "remarks":"Additional Remarks", "pic":"PIC"
            }


            if(InputActivity_DB.empty):
                InputActivity_DB = pd.DataFrame(columns=['input_id'] + list(used_columns.values()))
                st.warning("Activity Log Table are not found please submit new data and/or resubmit it")

            InputActivity_DB['well'] = st.session_state.WellName_Select
            InputActivity_DB['comp'] = st.session_state.CompName_Select

            # print(InputActivity_DB.columns)
            InputActivity_DB_temp = InputActivity_DB.copy()
            InputActivity_DB_temp.rename(columns=used_columns, inplace=True)

            gb = GridOptionsBuilder.from_dataframe(InputActivity_DB_temp[list(used_columns.values())])
            # gb = GridOptionsBuilder.from_dataframe((InputActivity_DB[used_columns.keys()]).rename(columns=used_columns, inplace=True))
            

            gb.configure_selection('multiple', use_checkbox=True)
            # gb_reload_Data = False

            gridOptions = gb.build()

            InputActivityGrid_response = AgGrid(
                    InputActivity_DB_temp, 
                    gridOptions=gridOptions,
                    data_return_mode=DataReturnMode.FILTERED_AND_SORTED, 
                    update_mode=(GridUpdateMode.SELECTION_CHANGED),
                    # reload_data = True
            )
            # st.dataframe(pd.DataFrame(InputActivityGrid_response['selected_rows']))

            # Button_col_1 = st.columns(3)
            # if Button_col_1[1].button(label="Select all row"):
            #     gb.configure_selection("multiple",use_checkbox=True, pre_selected_rows=np.arange(0,InputActivity_DB_temp.shape[0]).tolist())
            
            


            
            # Button_col_1 = st.columns(3)
            # else:



            if st.button('Clear Selected Row', key='refresh'):
                list_selected =[]
                for dt_temp in InputActivityGrid_response['selected_rows']:

                    IO_Data.DomeDelete(st.session_state.Well_ID_API,dt_temp['input_id'])
                InputActivity_DB = (IO_Data.DomeGetData(st.session_state.Well_ID_API, str(InputActivityLog_date_start), str(InputActivityLog_date_end)))
                getActivityLogTable.clear()

                st.success("activity deleted")
            with st.expander("Download your Activity Log Table"):
                st.download_button(
                    label="Download Activity Log Table as CSV",
                    data=convert_df(InputActivity_DB),
                    file_name=st.session_state.CompName_Select + "_"+ st.session_state.WellName_Select + '_ActivityLogTable.csv',
                    mime='text/csv',
                )


            
            



            # ######## below are Activity Summary Table #########################
            # ######## below are Activity Summary Table #########################
            # ######## below are Activity Summary Table #########################
            # ######## below are Activity Summary Table #########################
            # ######## below are Activity Summary Table #########################
            # ######## below are Activity Summary Table #########################
            # ######## below are Activity Summary Table #########################
            # ######## below are Activity Summary Table #########################
            # ######## below are Activity Summary Table #########################
            # ######## below are Activity Summary Table #########################

            Table_col_2 = st.columns(1)
            Table_col_2[0].markdown('### Activity Summary Table')
            if not (InputActivity_DB.empty):
                # elif(InputActivityLog_date_start)
                with st.spinner(text="Generate Activity Summary..."):


                    # Table_col_2[0].text('To Do: ')


                    RadioButton = Table_col_2[0].radio("Apply FALSE Sensor Filter?",
                                    ('Yes', 'No/RAW'), key='RadioButton'
                                    )


                    if RadioButton=='No/RAW':
                        SummaryActivity_DF = GenerateSummaryActivity_DB(Activity_DF, InputActivity_DB, cleanFalseSensor=False)
                    else:
                        SummaryActivity_DF = GenerateSummaryActivity_DB(Activity_DF, InputActivity_DB, cleanFalseSensor=True)

                    if 'ActivitySummary_AgGrid' not in st.session_state:
	                    st.session_state.ActivitySummary_AgGrid = MergedSummaryActivity_DB(ActivitySummary_DF_Dome, SummaryActivity_DF,InputActivityLog_date_start,InputActivityLog_date_end)
                    # st.dataframe(ActivitySummary_DF_Dome)
                    # st.dataframe(SummaryActivity_DF)
                    # st.dataframe(ActivitySummary_DF_Dome)

                    ActivitySummary_AgGrid = st.session_state.ActivitySummary_AgGrid
                    gb_2 = GridOptionsBuilder.from_dataframe(ActivitySummary_AgGrid)
                    gb_2.configure_selection('multiple', use_checkbox=True)

                    gb_2.configure_column("SUB-ACTIVITY", editable=True, cellEditor='agSelectCellEditor', cellEditorPopup=True, cellEditorParams={

                            'values': ["Wash Up/Down",
                                        "Reaming",
                                        "Moving",
                                        "Circulation",
                                        "Connection",
                                        "Stationary",
                                        "Rotary Drilling",
                                        "Slide Drilling",
                                        "Look and define",
                                        "CEMENTING JOB",
                                        "LAY DOWN BHA",
                                        "MAKE UP BHA",
                                        "NPT",
                                        "N/D BOP",
                                        "N/U BOP",
                                        "RUNNING CASING IN",
                                        "STUCK PIPE",
                                        "WAIT ON CEMENT",
                                        "RIG REPAIR",
                                        "nan"
                                            ],
                                        }
                                    )


                    gb_2.configure_column("STATUS", cellStyle=JsCode("""
                                            function(params) {
                                                if (params.value == 'FIRM') {
                                                    return {
                                                        'color': 'white',
                                                        'backgroundColor': 'seagreen'
                                                    }
                                                } else {
                                                    return {
                                                        'color': 'white',
                                                        'backgroundColor': 'darkorange'
                                                    }
                                                }
                                            };
                                            """))
                    gb_2.configure_column("ACTIVITY", cellStyle=JsCode("""
                                            function(params) {
                                            return {
                                                        'color': 'black',
                                                        'backgroundColor': 'peachpuff'
                                                    }
                                            };
                                            """)
                                            )
                    gb_2.configure_column("SUB-ACTIVITY", cellStyle=JsCode("""
                                            function(params) {
                                            return {
                                                        'color': 'black',
                                                        'backgroundColor': 'azure'
                                                    }
                                            };
                                            """)
                                            )

                    gridOptions = gb_2.build()
                    # if 'ActivitySummaryReloadData' not in st.session_state:
                    #     st.session_state.ActivitySummaryReloadData = False

                    SummaryActivityGrid_response = AgGrid(
                            ActivitySummary_AgGrid, 
                            gridOptions=gridOptions,
                            allow_unsafe_jscode=True,
                            # reload_data = st.session_state.ActivitySummaryReloadData,
                            height=500, 
                            # width='100%',
                            data_return_mode=DataReturnMode.AS_INPUT, 
                            update_mode=(GridUpdateMode.SELECTION_CHANGED),
                            
                    )
                    st.session_state.ActivitySummaryReloadData = False
                    
                    # ActivitySummary_AgGrid = SummaryActivityGrid_response['data']
                    last_col = st.columns(4)
                    if last_col[0].button("Regenerate Activity Summary Table"):
                        GenerateSummaryActivity_DB.clear()
                        MergedSummaryActivity_DB.clear()
                        st.session_state.ActivitySummary_AgGrid = Activity.cleanRepeatedActivity(SummaryActivityGrid_response['data'])
                        st.session_state.ActivitySummary_AgGrid = MergedSummaryActivity_DB(ActivitySummary_DF_Dome, SummaryActivity_DF,InputActivityLog_date_start,InputActivityLog_date_end)

                    last_col[1].download_button(
                        label="Download Summary data as CSV",
                        data=convert_df(ActivitySummary_AgGrid),
                        file_name=st.session_state.CompName_Select + "_"+ st.session_state.WellName_Select + '_ActivitySummary.csv',
                        mime='text/csv',
                        
                    )
                    last_col[2].download_button(
                        label="Download Realtime(5second) data as CSV",
                        data=convert_df(Activity_DF),
                        file_name=st.session_state.CompName_Select + "_"+ st.session_state.WellName_Select + '_RT_5second_Data.csv',
                        mime='text/csv',
                    )

                    if last_col[3].button(label="Finalize"):
                        ActivitySummary_AgGrid.to_excel('finalize_new.xlsx')
                        with st.spinner("Finalizing Activity Summary...."):
                            time.sleep(1)

                            IO_Data.UploadActivitySummary(pd.DataFrame(SummaryActivityGrid_response['selected_rows']), st.session_state.Well_ID_API)
                            IO_Data.UploadActivitySummary_v2(pd.DataFrame(SummaryActivityGrid_response['selected_rows']), st.session_state.Well_ID_API)
                        st.success("Success!")
                        # InputActivityGrid_response
                        # IO_Data.InsertSummaryActivity_DB(IO_Data.OpenConnection(), SummaryActivity_DF, st.session_state.WellName_Select, st.session_state.CompName_Select)
            else:
                st.warning("Please Input Activity Log Table first before generate Activity Summary Table")
    else:
        st.markdown("<h1 style='text-align: center; font-size: 50px;margin-top: 300px;'>  Welcome !</h1>", unsafe_allow_html=True)


