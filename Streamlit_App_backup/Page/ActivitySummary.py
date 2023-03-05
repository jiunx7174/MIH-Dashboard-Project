import streamlit as st
from PDU_Func import IO_Data,Activity
import pandas as pd
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
from datetime import datetime, timedelta
# import 

# @st.cache
def getActivitySummary(Well_ID_API,starttime,endtime):
    return IO_Data.DomeGetData_v2(Well_ID_API, starttime,endtime, table_type="Activity Summary")


def App():
    if 'FileUploadLogic' not in st.session_state:
        st.session_state.FileUploadLogic = False

    WellName_DF = st.session_state.WellName_DF
    Well_ID_API = st.session_state.Well_ID_API
    WellName_Select = st.session_state.WellName_Select
    CompName_Select = st.session_state.CompName_Select
    # Well_ID_API = st.session_state.WellName_Select

    used_columns = {"date":"Date", "time":"Time", "well":"Well", "comp":"Company", "section":"Section", "activity":"Major Activity", "in_slip_threshold":"In-Slip Threshold", "remarks":"Additional Remarks", "pic":"PIC"
        }
      # st.markdown('<h1 style="text-align: center; font-size: 50px; margin-top: 2px;"><span style="text-decoration: underline;">ACTIVITY MAPPING MODULE</span></h1>', unsafe_allow_html=True)
    st.markdown('<h1 style="text-align: center; font-size: 50px; margin-top: 2px;"><span style="text-decoration: underline;">ACTIVITY TABLE VIEWER MODULE</span></h1>', unsafe_allow_html=True)
    # try:
    InputActivity_DB = IO_Data.dict2DF(IO_Data.DomeGetData(Well_ID_API, 
                                        str((WellName_DF.loc[WellName_DF['well_name']==WellName_Select, 'active_date']).to_list()[0]), 
                                        str((WellName_DF.loc[WellName_DF['well_name']==WellName_Select, 'end_date']).to_list()[0])))

    if(InputActivity_DB.empty):
        InputActivity_DB = pd.DataFrame(columns=['input_id'] + list(used_columns.values()))
        st.warning("Activity Log Table are not found please submit new data and/or resubmit it")
    InputActivity_DB['well'] = WellName_Select
    InputActivity_DB['comp'] = CompName_Select




    InputActivity_DB_temp = InputActivity_DB.copy()
    InputActivity_DB_temp.rename(columns=used_columns, inplace=True)
    st.markdown('### Activity Log Table')
    gb = GridOptionsBuilder.from_dataframe(InputActivity_DB_temp[list(used_columns.values())])
    gb.configure_selection('multiple')
    gridOptions = gb.build()


    InputActivityGrid_response = AgGrid(
            InputActivity_DB_temp, 
            gridOptions=gridOptions,
            data_return_mode=DataReturnMode.AS_INPUT, 
            update_mode=(GridUpdateMode.SELECTION_CHANGED),
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

    st.markdown('### Activity Summary Table')
    ActivitySummary_DF_Dome = IO_Data.DomeGetData(Well_ID_API, 
                                                str((WellName_DF.loc[WellName_DF['well_name']==WellName_Select, 'active_date']).to_list()[0]), 
                                                str((WellName_DF.loc[WellName_DF['well_name']==WellName_Select, 'end_date']).to_list()[0]),
                                                table_type="Activity Summary")
    SectionList =['All'] + list(ActivitySummary_DF_Dome['Section'].unique())
 
    ActivitySummary_DF_Dome['STATUS'] = 'FIRM'


    
    SectionSelect = st.sidebar.selectbox("Select Section:",SectionList)
    
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
    
    if SectionSelect is not 'All':
        ActivitySummary_DF_Dome = ActivitySummary_DF_Dome[ActivitySummary_DF_Dome['Section']==SectionSelect]

    gb_3 = GridOptionsBuilder.from_dataframe(ActivitySummary_DF_Dome[Summary_Used_Columns.values()])





    gb_3.configure_column("ACTIVITY", cellStyle=JsCode("""
                            function(params) {
                            return {
                                        'color': 'black',
                                        'backgroundColor': 'peachpuff'
                                    }
                            };
                            """)
                            )
    gb_3.configure_column("SUB-ACTIVITY", cellStyle=JsCode("""
                            function(params) {
                            return {
                                        'color': 'black',
                                        'backgroundColor': 'azure'
                                    }
                            };
                            """)
                            )

    gridOptions = gb_3.build()


    SummaryActivityGrid_response = AgGrid(
            ActivitySummary_DF_Dome, 
            gridOptions=gridOptions,
            allow_unsafe_jscode=True,
            height=1000, 

            
    )
    st.download_button(
                        label="Download Activity Summary",
                        data=IO_Data.to_excel(ActivitySummary_DF_Dome),
                        file_name=CompName_Select + "_"+ WellName_Select + '_All_ActivitySummary.xlsx',
                        # mime='text/csv',
                    )
def App_v02():
    # if 'ActivitySummary' not in st.session_state:
    #     st.session_state.ActivitySummary = False
    if 'FileUploadLogic' not in st.session_state:
        st.session_state.FileUploadLogic = False

    WellName_DF = st.session_state.WellName_DF
    Well_ID_API = st.session_state.Well_ID_API
    WellName_Select = st.session_state.WellName_Select
    CompName_Select = st.session_state.CompName_Select
    # Well_ID_API = st.session_state.WellName_Select

    used_columns = {"date":"Date", "time":"Time", "well":"Well", "comp":"Company", "section":"Section", "activity":"Major Activity", "in_slip_threshold":"In-Slip Threshold", "remarks":"Additional Remarks", "pic":"PIC"
        }
      # st.markdown('<h1 style="text-align: center; font-size: 50px; margin-top: 2px;"><span style="text-decoration: underline;">ACTIVITY MAPPING MODULE</span></h1>', unsafe_allow_html=True)
    st.markdown('<h1 style="text-align: center; font-size: 50px; margin-top: 2px;"><span style="text-decoration: underline;">ACTIVITY TABLE VIEWER MODULE</span></h1>', unsafe_allow_html=True)
    try:
        InputActivity_DB = IO_Data.dict2DF(IO_Data.DomeGetData(Well_ID_API, 
                                        str((WellName_DF.loc[WellName_DF['well_name']==WellName_Select, 'active_date']).to_list()[0]), 
                                        str((WellName_DF.loc[WellName_DF['well_name']==WellName_Select, 'end_date']).to_list()[0])))
        error_stop = True
    except:
        IO_Data.DomeCreateTable(Well_ID_API, table_type="Activity Log")
        InputActivity_DB = IO_Data.dict2DF(IO_Data.DomeGetData(Well_ID_API, 
                                        str((WellName_DF.loc[WellName_DF['well_name']==WellName_Select, 'active_date']).to_list()[0]), 
                                        str((WellName_DF.loc[WellName_DF['well_name']==WellName_Select, 'end_date']).to_list()[0])))
        # st.warning("Well Summary are not found in server")
        error_stop = True
    if error_stop:
        if(InputActivity_DB.empty):
            InputActivity_DB = pd.DataFrame(columns=['input_id'] + list(used_columns.values()))
            st.warning("Activity Log Table are not found please submit new data and/or resubmit it")
        InputActivity_DB['well'] = WellName_Select
        InputActivity_DB['comp'] = CompName_Select




        InputActivity_DB_temp = InputActivity_DB.copy()
        InputActivity_DB_temp.rename(columns=used_columns, inplace=True)
        st.markdown('### Activity Log Table')
        gb = GridOptionsBuilder.from_dataframe(InputActivity_DB_temp[list(used_columns.values())])
        gb.configure_selection('multiple')
        gridOptions = gb.build()

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

        InputActivityGrid_response = AgGrid(
                InputActivity_DB_temp, 
                gridOptions=gridOptions,
                data_return_mode=DataReturnMode.AS_INPUT, 
                update_mode=(GridUpdateMode.SELECTION_CHANGED),
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

        st.markdown('### Activity Summary Table')
        try:
            ActivitySummary_DF_Dome = getActivitySummary(Well_ID_API, 
                                                        str((WellName_DF.loc[WellName_DF['well_name']==WellName_Select, 'active_date']).to_list()[0]), 
                                                        str((WellName_DF.loc[WellName_DF['well_name']==WellName_Select, 'end_date']).to_list()[0])
                                                        )
        except:
            st.warning("Well Summary are not found in server")
            ActivitySummary_DF_Dome = pd.DataFrame(columns=Summary_Used_Columns.values())



        SectionList =['All'] + list(ActivitySummary_DF_Dome['Section'].unique())
    
        ActivitySummary_DF_Dome['STATUS'] = 'FIRM'


        
        SectionSelect = st.sidebar.selectbox("Select Section:",SectionList)
        

        
        if SectionSelect is not 'All':
            ActivitySummary_DF_Dome = ActivitySummary_DF_Dome[ActivitySummary_DF_Dome['Section']==SectionSelect]
        ActivitySummary_DF_Dome = Activity.labelStand_v3(ActivitySummary_DF_Dome)

        # gb_3 = GridOptionsBuilder.from_dataframe(ActivitySummary_DF_Dome[Summary_Used_Columns.values()])
        gb_3 = GridOptionsBuilder.from_dataframe(ActivitySummary_DF_Dome)





        gb_3.configure_column("ACTIVITY", cellStyle=JsCode("""
                                function(params) {
                                return {
                                            'color': 'black',
                                            'backgroundColor': 'peachpuff'
                                        }
                                };
                                """)
                                )
        gb_3.configure_column("SUB-ACTIVITY", cellStyle=JsCode("""
                                function(params) {
                                return {
                                            'color': 'black',
                                            'backgroundColor': 'azure'
                                        }
                                };
                                """)
                                )

        gridOptions = gb_3.build()


        SummaryActivityGrid_response = AgGrid(
                ActivitySummary_DF_Dome, 
                gridOptions=gridOptions,
                allow_unsafe_jscode=True,
                height=1000, 

                
        )
        st.download_button(
                            label="Download Activity Summary",
                            data=IO_Data.to_excel(ActivitySummary_DF_Dome),
                            file_name=CompName_Select + "_"+ WellName_Select + '_All_ActivitySummary.xlsx',
                            # mime='text/csv',
                        )
    

