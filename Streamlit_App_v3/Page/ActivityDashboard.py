import streamlit as st 
from PDU_Func import IO_Data,Activity
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly
import plotly.io as pio
from fpdf import FPDF
import plotly.express as px

# @st.cache
def getActivitySummary(Well_ID_API,starttime,endtime):
    return IO_Data.DomeGetData_v2(Well_ID_API, starttime,endtime, table_type="Activity Summary")
# @st.cache
def getOffsetWellActivitySummary(WellList, WellName_DF, Section,starttime,endtime):
    # st.dataframe(WellName_DF)
    OffsetWell_id = (WellName_DF.loc[WellName_DF['well_name'].isin(WellList), ['wid','well_name']])
    OffsetWell_DF_list = []
    # st.dataframe(OffsetWell_id)
    for idx,row in OffsetWell_id.iterrows():
        wid_temp = int(row['wid'])
        # st.text(starttime)
        # st.text(endtime)

        # st.dataframe(IO_Data.DomeGetData_v2(wid_temp, "2001-10-07 21:00:00","2100-10-10 03:00:00", table_type="Activity Summary"))
        OffsetWell_DF_temp =Activity.labelStand_v3(IO_Data.DomeGetData_v2(wid_temp, "2001-10-07 21:00:00","2100-10-10 03:00:00", table_type="Activity Summary"))
        OffsetWell_DF_temp = OffsetWell_DF_temp[OffsetWell_DF_temp['Section'] == Section]
        OffsetWell_DF_temp['WELLNAME'] = row['well_name']
        OffsetWell_DF_list.append(OffsetWell_DF_temp)
    return pd.concat(OffsetWell_DF_list, ignore_index=True)

    # for wid_temp,wellname in zip(well_id_list,well_name_list):
    # # ActivitySummary_DF_Dome = 
    #     welltemp = Activity.labelStand_v3(IO_Data.DomeGetData_v2(wid_temp, StartDateTime_select,EndDateTime_select, table_type="Activity Summary"))
    #     welltemp['WELLNAME'] = wellname
    #     Table_list.append(welltemp)

    # return IO_Data.DomeGetData_v2(Well_ID_API, starttime,endtime, table_type="Activity Summary")


def App():
    if not st.session_state.FileUploadLogic_SummaryReport:
        SummaryActivity_DF = pd.read_csv('RealTime_Test/Temp_SummaryActivity_tes1.csv', index_col = False)
        OffsetWell_DF = pd.read_excel('RealTime_Test/OnBottom_OffsetWell_Test.xlsx', index_col = False)
    ActivitySummary_DF_Dome = IO_Data.DomeGetData(Well_ID_API, 
                                                str((WellName_DF.loc[WellName_DF['well_name']==WellName_Select, 'active_date']).to_list()[0]), 
                                                str((WellName_DF.loc[WellName_DF['well_name']==WellName_Select, 'end_date']).to_list()[0]),
                                                table_type="Activity Summary")
    SectionList =['All'] + list(ActivitySummary_DF_Dome['Section'].unique())

    SectionSelect = st.sidebar.selectbox("Select Section:",SectionList)
    # except Exception as error_msg:
    #     st.text(error_msg)
    if SectionSelect is not 'All':
        # ActivitySummary_DF_Dome = ActivitySummary_DF_Dome[ActivitySummary_DF_Dome['Section']==SectionSelect]
        OffsetWell_DF = OffsetWell_DF[OffsetWell_DF['Section']==SectionSelect]




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
    # st.dataframe(MeterageDrillingDate_DF)
    # st.dataframe(SummaryActivity_DF)

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
    OffsetWellPlot_Logic = False
    if st.sidebar.checkbox("Display Surrounding Well"):
        OffsetWells_Dict = st.multiselect(
            'Selected Surrounding Wells Statistics',
            [i for i in WellList if i != WellName_Select],
            [i for i in WellList if i != WellName_Select])
        OffsetWellPlot_Logic = True
        OffsetWell_DF = OffsetWell_DF[OffsetWell_DF['well'].isin(OffsetWells_Dict)]


    # print(WellList)

    SummaryActivity_DF['date_time'] = SummaryActivity_DF['date_time'].astype('datetime64')
    with st.expander('Activity Summary'):
        
        figPie_Activity = px.pie(PieChart_DF, 
                         values='Duration(minutes)',
                         names='LABEL_Activity',
                        #   title="Activity Pie Chart",
                          labels={"LABEL_Activity":"Activity", "Duration(minutes)":"Duration"}
                          
        )
        figPie_Activity.update_traces( textinfo='percent+label')
        st.markdown("#### Activity Pie Chart by " + WellName_Select + " " + SectionSelect+ " in Hole Section")
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
        st.markdown("#### Sub-Activity Pie Chart by " + WellName_Select + " " + SectionSelect+ " in Hole Section")
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
        st.markdown("#### Stand Break Down by " + WellName_Select + " " + SectionSelect+ " in Hole Section")
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
        st.markdown("#### Time Vs Depth " + WellName_Select + " " + SectionSelect+ " in Hole Section")
        st.plotly_chart(figTimeDepth)




        fi0_date_Time = plotly.graph_objs.Figure()

        # a dict which maps your categorical values to colors
        colors_subActivity = {
                'Wash Up/Down': 'darkkhaki',
                'Reaming': 'darkmagenta',
                'Moving': 'darkolivegreen',
                'Circulation': 'darkorange',
                'Connection': 'darkorchid',
                'Stationary': 'darkred',
                'Rotary Drilling': 'darksalmon',
                'Slide Drilling': 'darkseagreen',
                'Look and define': 'darkslateblue',
                'CEMENTING JOB': 'darkslategray',
                'CONNECTION': 'darkturquoise',
                'LAY DOWN BHA': 'darkviolet',
                'MAKE UP BHA': 'deeppink',
                'NPT': 'deepskyblue',
                'N/D BOP': 'darkcyan',
                'N/U BOP': 'hotpink',
                'RUNNING CASING IN': 'lightblue',
                'STATIONARY': 'lightred',
                'STUCK PIPE': 'lightgreen',
                'WAIT ON CEMENT': 'lightseagreen',
                'RIG REPAIR': 'mediumpurple',
                'FALSE/Check': 'mediumpurple',
                'nan': 'orange'
            }



        # the list which stores categories which were already plotted
        already_plotted = []
        df = SummaryActivity_DF.copy()
        for i in range(df.shape[0] + 1):
            # create a new trace if the category changes or at the end of the data frame
            if i in (0, df.shape[0]) or cat != df.iloc[i, ]['LABEL_SubActivity']:
                if i != 0:
                    if i != df.shape[0]:
                        x.append(df.iloc[i,]['date_time'])
                        y.append(df.iloc[i,]['Hole Depth(max)'])
                    trace = plotly.graph_objs.Scatter(x=x, y=y, 
                                                    legendgroup=cat,  # group identical categories
                                                    showlegend=cat not in already_plotted,  # hide legend if already plotted
                                                    name=cat,
                                                    marker={'color': colors_subActivity[df.iloc[i - 1, ]['LABEL_SubActivity']]})
                    fi0_date_Time.add_trace(trace)
                    already_plotted.append(cat)

                if i == df.shape[0]:
                    continue
                cat = df.iloc[i, ]['LABEL_SubActivity']
                x = []
                y = []    

            x.append(df.iloc[i,].name)
            y.append(df.iloc[i,]["Hole Depth(max)"])
        st.plotly_chart(fi0_date_Time)
        
        

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
        st.markdown("#### Drilling Meterage " + WellName_Select + " " + SectionSelect+ " in Hole Section")
        st.plotly_chart(figMeterageDrillingDate)

    with st.expander("ROP On Bottom and Stand"):
        if OffsetWellPlot_Logic:
            ROP_Layout = st.columns(2)
            figOBH_ROP_OffsetWell = go.Figure(
                px.bar(OffsetWell_DF, 
                x="well", 
                y=['On Bottom Hours','Rate Of Penetration'] ,
                barmode='group',
                # width=1000,

                ),
                        # layout = layoutOBH_ROP
            )

            figOBH_ROP_OffsetWell.update_layout(
                            # title="Title",
                            xaxis=dict(
                                title="Well"
                            ),
                            # yaxis=dict(
                            #     title="On Bottom Hours(m/hr)"
                            # ) 
                            ) 

            ROP_Layout[1].markdown("#### Average On Bottom and Stand by" + " " + SectionSelect+ " Hole Section")
            ROP_Layout[1].plotly_chart(figOBH_ROP_OffsetWell)
        else:
            ROP_Layout = st.columns(1)
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
                        
        ROP_Layout[0].markdown("#### ROP On Bottom and Stand " + WellName_Select + " " + SectionSelect+ " Hole Section")
        ROP_Layout[0].plotly_chart(figOBH_ROP)
        
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


def App_v02():
    WellName_DF = st.session_state.WellName_DF
    # st.dataframe(WellName_DF)
    Well_ID_API = st.session_state.Well_ID_API
    WellName_Select = st.session_state.WellName_Select
    CompName_Select = st.session_state.CompName_Select
    combine_text = CompName_Select + '-' + WellName_Select
    st.markdown('<h1 style="text-align: center; font-size: 50px; margin-top: 2px;"><span style="text-decoration: underline;">Summary Report</span></h1>', unsafe_allow_html=True)
    st.markdown('<h1 style="text-align: center; font-size: 40px; margin-top: 2px;">%s</h1>' % CompName_Select, unsafe_allow_html=True)
    st.markdown('<h1 style="text-align: center; font-size: 30px; margin-top: 2px;">%s</h1>' % WellName_Select, unsafe_allow_html=True)

    try:
        SummaryActivity_DF_RAW = getActivitySummary(Well_ID_API, 
                                                    str((WellName_DF.loc[WellName_DF['well_name']==WellName_Select, 'active_date']).to_list()[0]), 
                                                    str((WellName_DF.loc[WellName_DF['well_name']==WellName_Select, 'end_date']).to_list()[0]),
                                                    )
        if SummaryActivity_DF_RAW.empty:
            error_stop=False
        else:
            error_stop=True 
    except:
        # st.warning("Well Summary are not found in server")
        error_stop = False
    
    if error_stop: 
        SectionList =['All'] + list(SummaryActivity_DF_RAW['Section'].unique())

        SectionSelect = st.sidebar.selectbox("Select Section:",SectionList)
        # except Exception as error_msg:
        #     st.text(error_msg)
        OffsetWellPlot_Logic = False
        if SectionSelect is not 'All':
            SummaryActivity_DF = SummaryActivity_DF_RAW[SummaryActivity_DF_RAW['Section']==SectionSelect]
            # ActivitySummary_DF_Dome = ActivitySummary_DF_Dome[ActivitySummary_DF_Dome['Section']==SectionSelect]
            WellList = WellName_DF['well_name'].tolist()
            if st.sidebar.checkbox("Display Surrounding Well"):
                OffsetWells_List = st.sidebar.multiselect(
                    'Selected Surrounding Wells Statistics',
                    [i for i in WellList if i != WellName_Select],
                    [])
                OffsetWellPlot_Logic = True

                OffsetWell_DF_RAW = getOffsetWellActivitySummary(
                    OffsetWells_List + [WellName_Select], 
                    WellName_DF, 
                    SectionSelect,
                    str((WellName_DF.loc[WellName_DF['well_name']==WellName_Select, 'active_date']).to_list()[0]), 
                    str((WellName_DF.loc[WellName_DF['well_name']==WellName_Select, 'end_date']).to_list()[0]),
                    )

                # st.text(OffsetWells_Dict)
        else:
            SummaryActivity_DF = SummaryActivity_DF_RAW.copy()



        
    #######################################################################################################################################
    #############################################               Heading            #############################################
    #######################################################################################################################################


        #######################################################################################################################################
        #############################################               Chart 1 : Piechart            #############################################
        #######################################################################################################################################
        # To Do:
        # 1. merge subactivity and activity in single expander(sebelah2an)
        
        PieChart_DF = SummaryActivity_DF.groupby(['SUB-ACTIVITY', 'ACTIVITY']).sum().reset_index()
        PieChart_DF = PieChart_DF[['SUB-ACTIVITY', 'ACTIVITY', 'Duration (Minutes)']]
        with st.expander('Activity & Sub-Activity Summary'):
            
            figPie_Activity = px.pie(PieChart_DF, 
                            values='Duration (Minutes)',
                            names='ACTIVITY',
                            #   title="Activity Pie Chart",
                            labels={"ACTIVITY":"Activity", "Duration (Minutes)":"Duration"}
                            
                            )
            figPie_Activity.update_layout(
                                autosize=False,
                                width=700,
                                height=700,
                                )
            figPie_Activity.update_traces( textinfo='percent+label')
        # with st.expander('SubActivity Summary'):

            figPie_SubActivity = px.pie(PieChart_DF, 
                            values='Duration (Minutes)',
                            names='SUB-ACTIVITY',
                            #   title="Activity Pie Chart",
                            labels={"SUB-ACTIVITY":"Activity", "Duration (Minutes)":"Duration"}
                            
            )
            figPie_SubActivity.update_layout(
                                autosize=False,
                                width=700,
                                height=700,
                                )
            figPie_SubActivity.update_traces( textinfo='percent+label')

            Pie_Layout = st.columns(2)
            Pie_Layout[0].markdown("#### Activity Pie Chart by " + WellName_Select + " " + SectionSelect+ " in Hole Section")
            Pie_Layout[0].plotly_chart(figPie_Activity)
            Pie_Layout[1].markdown("#### Sub-Activity Pie Chart by " + WellName_Select + " " + SectionSelect+ " in Hole Section")
            Pie_Layout[1].plotly_chart(figPie_SubActivity)    
    
        #######################################################################################################################################
        #############################################           Chart 2 : Time vs Depth           #############################################
        #######################################################################################################################################
        with st.expander("Time vs Depth"):
            TimeDepth_DF_1 = SummaryActivity_DF.reset_index()
            TimeDepth_DF_2 = SummaryActivity_DF.reset_index()
            TimeDepth_DF_3 = SummaryActivity_DF.reset_index()

            TimeDepth_DF_2['Start Time'] = TimeDepth_DF_2['End Time']
            TimeDepth_DF_3['Start Time'] = TimeDepth_DF_3['End Time']
            TimeDepth_DF_3['Bit Depth(mean)'] = TimeDepth_DF_3['Bit Depth(mean)'].shift(-1)

            TimeDepth_DF = pd.concat([TimeDepth_DF_1, TimeDepth_DF_2, TimeDepth_DF_3], ignore_index=True)

            TimeDepth_DF = TimeDepth_DF.sort_values(by=['index', 'Start Time'])
            # display(Data_test[['Start Time','Bit Depth(mean)','SUB-ACTIVITY']])

            list_subactivity_unique = list(TimeDepth_DF['SUB-ACTIVITY'].unique())
            figTimeDepth = go.Figure()



            for subactivity_unique in list_subactivity_unique:
                TimeDepth_DF_temp = TimeDepth_DF.copy()
                # if subactivity_unique == "Rotary Drilling":
                TimeDepth_DF_temp[TimeDepth_DF_temp["SUB-ACTIVITY"] != subactivity_unique] = None
                figTimeDepth.add_trace(
                    go.Scatter(
                        x=TimeDepth_DF_temp['Start Time'], 
                        y=TimeDepth_DF_temp["Bit Depth(mean)"],
                        mode='lines',
                        name=subactivity_unique,
                        hovertemplate='Date: %{x} <br>Bit Depth: %{y}'
                        )
                    )
            figTimeDepth.update_layout(
                xaxis_title="Date/Time",
                yaxis_title="Bit Depth(mean)",
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=16,
                    font_family="Rockwell"
                ))
            figTimeDepth['layout']['yaxis']['autorange'] = "reversed"
            st.plotly_chart(figTimeDepth) 
            # figTimeDepth.show()
            

        #######################################################################################################################################
        #############################################           Chart 3 : Drilling Meterage     #############################################
        #######################################################################################################################################
        MeterageDrillingDate_DF = SummaryActivity_DF.groupby(['Date']).agg(
            {
                "Drilling Meterage (m)":"sum",
                "Start Time":"first"
            }
        ).reset_index()
        # st.dataframe(MeterageDrillingDate_DF)

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
                x = MeterageDrillingDate_DF['Start Time'],
                textposition = "outside",
                # text = ["+60", "+80", "", "-40", "-20", "Total"],
                y = -MeterageDrillingDate_DF['Drilling Meterage (m)'],
                connector = {"line":{"color":"rgb(63, 63, 63)"}},

            )
                ,layout = layoutMeterageDrillingDate
            )

            # figMeterageDrillingDate.update_layout(
            #         title = "Meterage Drilling By Date",
            #         showlegend = True,
            #         xaxis_label='depth'
            # )
            MeterageDrilling_Layout = st.columns(2)
            MeterageDrilling_Layout[0].markdown("#### Drilling Meterage " + WellName_Select + " " + SectionSelect+ " in Hole Section")
            MeterageDrilling_Layout[0].plotly_chart(figMeterageDrillingDate)

            # data_canada = px.data.gapminder().query("country == 'Canada'")
            figMeterageDrillingDate_v2 = px.bar(MeterageDrillingDate_DF, x='Date', y='Drilling Meterage (m)')
            
            MeterageDrilling_Layout[1].markdown("#### Drilling Meterage " + WellName_Select + " " + SectionSelect+ " in Hole Section")
            MeterageDrilling_Layout[1].plotly_chart(figMeterageDrillingDate_v2)
            # fig.show()
            


        #######################################################################################################################################
        #############################################           Chart 4 : Connection Time     #############################################
        #######################################################################################################################################





        #######################################################################################################################################
        #############################################           Chart 5 : ROP On Bottom     #############################################
        #######################################################################################################################################
        OBH_ROP_DF = SummaryActivity_DF.copy()

        OBH_ROP_DF = OBH_ROP_DF[OBH_ROP_DF['SUB-ACTIVITY']=='Connection']

        OBH_ROP_DF = OBH_ROP_DF[OBH_ROP_DF['Total Stand Drilling Meterage (m)']!=0]
        OBH_ROP_DF['On Bottom ROP (m/hr)'] = OBH_ROP_DF['Total Stand Drilling Meterage (m)'] / (OBH_ROP_DF['On Bottom state (hrs)'])
        OBH_ROP_DF['Avg. ROP Per Stand'] = OBH_ROP_DF['Total Stand Drilling Meterage (m)'] / (OBH_ROP_DF['Total Stand Duration (hrs)'])
        # OBH_ROP_DF
        # import plotly.express as px

        figOBH_ROP = go.Figure(
            px.bar(OBH_ROP_DF, x="Start Time", y=['On Bottom ROP (m/hr)','Avg. ROP Per Stand'],
                        barmode='group',
                        height=400),
                    # layout = layoutOBH_ROP
        )
        figOBH_ROP.update_layout(
                        # title="Title",
                        xaxis=dict(
                            title="Date - Time"
                        ),
                        yaxis=dict(
                            title="(m/hr)"
                        ) ) 

        with st.expander("ROP On Bottom and Stand"):
            if OffsetWellPlot_Logic:
                # OffsetWell_DF_RAW
                OffsetWell_OBH_ROP_DF = OffsetWell_DF_RAW.groupby('WELLNAME').agg(
                    {
                        "Total Stand Drilling Meterage (m)":'mean',
                        'On Bottom state (hrs)':'mean',
                        'Total Stand Duration (hrs)':'mean'
                    }
                ).reset_index()

                OffsetWell_OBH_ROP_DF['On Bottom ROP (m/hr)'] = OffsetWell_OBH_ROP_DF['Total Stand Drilling Meterage (m)'] / (OffsetWell_OBH_ROP_DF['On Bottom state (hrs)'])
                OffsetWell_OBH_ROP_DF['Avg. ROP Per Stand'] = OffsetWell_OBH_ROP_DF['Total Stand Drilling Meterage (m)'] / (OffsetWell_OBH_ROP_DF['Total Stand Duration (hrs)'])


                figOBH_ROP_OffsetWell = go.Figure(
                    px.bar(
                        OffsetWell_OBH_ROP_DF, 
                        x="WELLNAME", 
                        y=['On Bottom ROP (m/hr)','Avg. ROP Per Stand'],
                        barmode='group',
                        height=400
                        ),
                            # layout = layoutOBH_ROP
                )

                figOBH_ROP_OffsetWell.update_layout(
                                # title="Title",
                                xaxis=dict(
                                    title="Well"
                                ),
                                # yaxis=dict(
                                #     title="On Bottom Hours(m/hr)"
                                # ) 
                                ) 

                Chart_05_Layout = st.columns(2)
                Chart_05_Layout[0].markdown("#### ROP On Bottom and Stand " + WellName_Select + " " + SectionSelect+ " Hole Section")
                Chart_05_Layout[0].plotly_chart(figOBH_ROP)
                Chart_05_Layout[1].markdown("#### Average On Bottom and Stand by Well" + " " + SectionSelect+ " Hole Section")
                Chart_05_Layout[1].plotly_chart(figOBH_ROP_OffsetWell)
                
                
            else:

                Chart_05_Layout = st.columns(1)
                            
                Chart_05_Layout[0].markdown("#### ROP On Bottom and Stand " + WellName_Select + " " + SectionSelect+ " Hole Section")
                Chart_05_Layout[0].plotly_chart(figOBH_ROP)



        #######################################################################################################################################
        #############################################           Chart 6 : StandTime Breakdown     #############################################
        #######################################################################################################################################

        StandTimeBreakdown_DF = SummaryActivity_DF.copy()
        StandTimeBreakdown_DF = StandTimeBreakdown_DF.groupby(['Stand Group','SUB-ACTIVITY']).agg({
                    'Start Time':'first', 
                    'ACTIVITY':'first', 
                    'Duration (Minutes)':'sum',
                    'Rotate Drilling Time (Minutes)':'sum', 
                    'Slide Drilling Time (Minutes)':'sum',
                    'Reaming Time (Minutes)':'sum',
                    'Connection Time (Minutes)':'sum',
                    }
                ).reset_index()
        # StandTimeBreakdown_DF = StandTimeBreakdown_DF.loc[~(StandTimeBreakdown_DF[['Rotate Drilling Time (Minutes)','Slide Drilling Time (Minutes)','Reaming Time (Minutes)']]==0).all(axis=1)]
        # StandTimeBreakdown_DF

        idx_logic_activity = StandTimeBreakdown_DF["ACTIVITY"].isin(["DRILLING FORMATION", 
                                                    'CIRCULATE HOLE CLEANING',
                                                    'CONNECTION',
                                                    'DRILL OUT CEMENT',
                                                ])
        StandTimeBreakdown_DF= StandTimeBreakdown_DF[idx_logic_activity]
        # tes = 
        StandTimeBreakdown_DF = StandTimeBreakdown_DF.join(StandTimeBreakdown_DF.groupby(['Stand Group']).agg({'Start Time':'first'}), on='Stand Group', rsuffix='_used')
        # display(tes)
        # display(StandTimeBreakdown_DF)



        figStandTimeBreakdown = px.bar(StandTimeBreakdown_DF, x='Start Time_used', y=['Duration (Minutes)'],color='SUB-ACTIVITY', width=500, height=500)
        # figStandTimeBreakdown = px.bar(SummaryActivity_DF.dropna(subset=['Stand Group_Pred', "Duration(minutes)"]), x='Stand Group_Pred', y="Duration(minutes)", color="LABEL_SubActivity", width=1000, height=1000)
        figStandTimeBreakdown.update_xaxes(type='category')
        figStandTimeBreakdown.update_layout(
                        # title="Title",
                        xaxis=dict(
                            title="Stand Group"
                        ),
                        yaxis=dict(
                            title="Duration(Minutes)"
                        ) ) 
        with st.expander('Stand Time Breakdown'):
            if OffsetWellPlot_Logic:
                OffsetWell_StandTimeBreakdown_DF = OffsetWell_DF_RAW.copy()
                idx_logic_activity = OffsetWell_StandTimeBreakdown_DF["ACTIVITY"].isin(["DRILLING FORMATION", 
                                                                'CIRCULATE HOLE CLEANING',
                                                                'CONNECTION',
                                                                'DRILL OUT CEMENT',
                                                            ])
                OffsetWell_StandTimeBreakdown_DF= OffsetWell_StandTimeBreakdown_DF[idx_logic_activity]

                OffsetWell_StandTimeBreakdown_DF = OffsetWell_StandTimeBreakdown_DF.groupby(['WELLNAME','SUB-ACTIVITY']).agg(
                    {
                        "Duration (Minutes)":'mean',
                    }
                ).reset_index()
                
                figOffsetWell_StandTimeBreakdown = px.bar(OffsetWell_StandTimeBreakdown_DF, x='WELLNAME', y=['Duration (Minutes)'],color='SUB-ACTIVITY', width=500, height=500)

                figOffsetWell_StandTimeBreakdown.update_xaxes(type='category')
                figOffsetWell_StandTimeBreakdown.update_layout(
                                # title="Title",
                                xaxis=dict(
                                    title="Offset Well"
                                ),
                                yaxis=dict(
                                    title="Duration(Minutes)"
                                ) ) 
                Chart_06_Layout = st.columns(2)
                Chart_06_Layout[0].markdown("#### Stand Break Down by " + WellName_Select + " " + SectionSelect+ " in Hole Section")
                Chart_06_Layout[0].plotly_chart(figStandTimeBreakdown)

                Chart_06_Layout[1].markdown("#### Stand Break Down by Well" + " " + SectionSelect+ " Hole Section")
                Chart_06_Layout[1].plotly_chart(figOffsetWell_StandTimeBreakdown)
                
                # figOffsetWell_StandTimeBreakdown.show()
            else:
                Chart_06_Layout = st.columns(1)
                Chart_06_Layout[0].markdown("#### Stand Break Down by " + WellName_Select + " " + SectionSelect+ " in Hole Section")
                Chart_06_Layout[0].plotly_chart(figStandTimeBreakdown)



        # st.dataframe(MeterageDrillingDate_DF)
        # st.dataframe(SummaryActivity_DF)


        # with st.expander("Upload Your Summary Activity Table"):

        #     UploadUser = st.file_uploader('Override the Summary Activity Table', type={'csv', 'txt'} , disabled=st.session_state.FileUploadLogic_SummaryReport)
        #     st.markdown("""### Upload Guidelines:""")
        #     st.text("lorem ipsum")
        #     if UploadUser is not None:
        #         InputActivity_DB = pd.read_csv(UploadUser, index_col = False)
        #         InputActivity_DB['dt'] = InputActivity_DB['date'].astype('datetime64')
        #         InputActivity_DB.to_csv('RealTime_Test/Temp_SummaryActivity_tes1.csv', index = False)
        #         print('uploaded')
        #     if st.button('submit', key='UserSubmit'):
        #         st.session_state.FileUploadLogic_SummaryReport = True

        # with st.sidebar():
        



        # print(WellList)

        # SummaryActivity_DF['date_time'] = SummaryActivity_DF['date_time'].astype('datetime64')
        


            
            

            
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
        st.warning("Well Summary are not found in server")