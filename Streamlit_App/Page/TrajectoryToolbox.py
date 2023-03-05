import streamlit as st
import pandas as pd 
import welleng as we
from PDU_Func import Trajectory
from st_aggrid import AgGrid, DataReturnMode, GridUpdateMode, GridOptionsBuilder
from importlib import reload
import plotly.graph_objects as go
# from streamlit.ScriptRunner import RerunException

reload(Trajectory)

@st.cache(allow_output_mutation=True)
def CreateTargetDF():
    return Trajectory.emptyTargetPoint().astype('float64')

@st.cache(allow_output_mutation=True)
def generateTrajectorySurvey(TargetDF,**kwargs):
    return Trajectory.generateSurvey(TargetDF, **kwargs)
    

@st.cache(allow_output_mutation=True)
def CreateTrajectoryDF():
    return Trajectory.emptyTargetPoint()
def addEmptyTargetDFRow(TargetDF):
    TargetDF = TargetDF.append(pd.Series(), ignore_index = True)
    # emptyDF = pd.DataFrame(

    
    return TargetDF
def App():
    SubToolList = [
        "Trajectory Visualization",
        "Trajectory Design",
        'Trajectory Update'
    ]

    ToolNavBar = st.sidebar.selectbox("Select Tools:",["-"] + SubToolList)

    if ToolNavBar == "Trajectory Visualization":
        TrajectoryViewer()
    elif ToolNavBar == "Trajectory Design":
        TrajectoryDesign()
    elif ToolNavBar == "Trajectory Update":
        TrajectoryDesignUpdate()
    else:
        st.text(ToolNavBar)


    # st.text(ToolNavBar)


def TrajectoryViewer():
    st.markdown('<h1 style="text-align: center; font-size: 50px; margin-top: 2px;"><span ;">TRAJECTORY VIEWER</span></h1>', unsafe_allow_html=True)
    PlotContainer = st.container()
    TableContainer = st.container()
    UploadContainer= st.container()

    with UploadContainer.expander("Upload your Trajectory File"):
        TrajectoryRaw = st.file_uploader("",type="xlsx")
        with open('Streamlit_App\\Data\\WellTrajectoryFormat.xlsx', 'rb') as f:
            st.download_button('Download Example Format', f, file_name='WellTrajectoryFormat.xlsx')
    if TrajectoryRaw is not None:
        
        TrajectorySurvey = Trajectory.loadSurvey(TrajectoryRaw)
        fig2DPanelTrajectory = TrajectorySurvey.figure(type='panel')
        # fig2DPanelTrajectory 
        fig3DTrajectory = TrajectorySurvey.interpolate_survey(step=30).figure(type='scatter3d')
        PlotColumns = PlotContainer.columns(2)

        PlotColumns[0].plotly_chart(fig3DTrajectory)
        PlotColumns[1].plotly_chart(fig2DPanelTrajectory)

        TableContainer.dataframe(we.survey.export_csv(TrajectorySurvey, None), use_container_width =True)


def TrajectoryDesign():
    if 'counter' not in st.session_state:
        st.session_state.counter = 0
    if 'TargetDF' not in st.session_state:
        st.session_state.TargetDF = CreateTargetDF()
        st.session_state.TargetDF = addEmptyTargetDFRow(st.session_state.TargetDF)
        st.session_state.TargetDF = addEmptyTargetDFRow(st.session_state.TargetDF)
        st.session_state.TargetDF = addEmptyTargetDFRow(st.session_state.TargetDF)

    if 'TrajectoryDF' not in st.session_state:
        st.session_state.TrajectoryDF = CreateTrajectoryDF()

    st.markdown('<h1 style="text-align: center; font-size: 50px; margin-top: 2px;"><span ;">TRAJECTORY DESIGNS</span></h1>', unsafe_allow_html=True)
    # InputContainer = st.container()
    # PlotColumns = st.columns(1)
    TableColumns,PlotColumns= st.columns([1, 2])
    PlotColumns.markdown("## Trajectory Visualization")
    Tab3DView,Tab2DView=PlotColumns.tabs(['3D View','2D View'])
    AddRowColumn, ClearColumn,_,_= st.columns([1,1,1,3])
    TrajectorySurveyColumn = st.columns(1)[0]



    # st.text(st.session_state.counter)
    # st.session_state.counter = st.session_state.counter+1
    # Xcols, Ycols, Zcols, DLScols,_ = st.columns([1,1,1,1,4])
    # FormColumns,_ = st.columns(2)

    # TableInputContainer = TableColumns
    # TableInputContainer.text("Table")


    # FormInputContainer = FormColumns.container()
    

    # Tab3DView, Tab2DView = PlotColumns.tabs(["3D View", "2D View"])

    # with TableColumns:
    TableColumns.markdown("## Target Tables")
    with TableColumns.form(key="TargetForm"):
        submitted = st.form_submit_button('Calculate Trajectory')
        response = AgGrid(st.session_state.TargetDF , key='TargetDFInputForm', editable=True, reload_data=True, fit_columns_on_grid_load=True)
    # FormButton = FormColumn.button('CalculateTrajectory', key='CalculateTrajectory')
    # if FormButton:
        if submitted:
            st.session_state.counter = st.session_state.counter+1
            st.session_state.TargetDF = response['data'].astype('float64')
            st.text("response")
            st.dataframe(response['data'])
            st.session_state.TrajectorySurvey = generateTrajectorySurvey(st.session_state.TargetDF, interpolation_step = 30, datum=15, init_inc=0, init_azi=0)
            # tes = we.survey.export_csv(we.survey.from_connections(we.connector.survey_to_plan(st.session_state.TrajectorySurvey)))
            # st.dataframe(tes)
            st.session_state.TrajectoryDF = (we.survey.export_csv(st.session_state.TrajectorySurvey, None))
            st.session_state.FigEmpty = False
            st.experimental_rerun()
            

    ClearButton = ClearColumn.button('Clear Table', key='TargetDF_TableRefresh')
    if ClearButton:
        st.session_state.TargetDF = Trajectory.emptyTargetPoint().astype('float64')
        st.session_state.TargetDF = addEmptyTargetDFRow(st.session_state.TargetDF)
        st.session_state.TargetDF = addEmptyTargetDFRow(st.session_state.TargetDF)
        st.session_state.TargetDF = addEmptyTargetDFRow(st.session_state.TargetDF)
        st.session_state.FigEmpty = True
        st.experimental_rerun()
    AddRowButton = AddRowColumn.button('Add Row', key='TargetDF_AddRow')
    if AddRowButton:
        st.session_state.TargetDF = addEmptyTargetDFRow(st.session_state.TargetDF)
        st.experimental_rerun()
        # 


        
    
        ##### Trajectory Display

    if  ('FigEmpty' not in st.session_state) :
        st.session_state.FigEmpty = True
    # elif submitted:
        


    if st.session_state.FigEmpty == False:
    # if (len(st.session_state.TargetDF) > 1) and submitted:

        fig2DPanelTrajectory = st.session_state.TrajectorySurvey.figure(type='panel')
        fig3DTrajectory = st.session_state.TrajectorySurvey.figure(type='scatter3d')
        fig2DPanelTrajectory = fig2DPanelTrajectory.update_layout(
            # title="Wind Frequencies",
            # xaxis_title="Direction",
            # yaxis_title="Frequency",
            # autosize=False,
            width=100,
            height=1000,
        )

        # tes_survey  
        # st.experimental_rerun()
        


    # elif st.session_state.FigEmpty == True:
    else:
        fig3DTrajectory = go.Figure().add_annotation(x=2, y=2,text="No Data to Display",font=dict(family="sans serif",size=25,color="crimson"),showarrow=False,yshift=10)
        fig2DPanelTrajectory = go.Figure().add_annotation(x=2, y=2,text="No Data to Display",font=dict(family="sans serif",size=25,color="crimson"),showarrow=False,yshift=10)
        # return fig3DTrajectory,fig2DPanelTrajectory

    # if ((not st.session_state.TargetDF.empty) and (len(st.session_state.TargetDF) > 1)) and submitted:
        # TrajectorySurvey
        # fig2DPanelTrajectory 
    # TableColumns.markdown("## Target Tables")
    
    Tab3DView.plotly_chart(fig3DTrajectory, use_container_width=True)
    Tab2DView.plotly_chart(fig2DPanelTrajectory, use_container_width=True)
    TrajectorySurveyColumn.markdown("### Trajectory Survey Table")
    TrajectorySurveyColumn.dataframe(st.session_state.TrajectoryDF,use_container_width=True)
    #  = CreateTrajectoryDF()
    
    st.text(st.session_state.TargetDF.empty)


def TrajectoryDesignUpdate():
    st.markdown('<h1 style="text-align: center; font-size: 50px; margin-top: 2px;"><span ;">TRAJECTORY UPDATE</span></h1>', unsafe_allow_html=True)
    UploadContainer= st.container()

    with UploadContainer.expander("Upload your Trajectory File"):
        PlanSurveyUpload, ActualSurveyUpload = st.columns(2)

        PlanSurveyUpload.markdown("### Upload Plan Survey")
        PlanSurveyUpload_Raw = PlanSurveyUpload.file_uploader("",key='PlanSurveyUpload', type="xlsx")
        ActualSurveyUpload.markdown("### Upload Actual Survey")
        ActualSurveyUpload_Raw = ActualSurveyUpload.file_uploader("",key='ActualSurveyUpload',type="xlsx")

        if PlanSurveyUpload_Raw is not None:
            PlanSurveyUpload_DF = pd.read_excel(PlanSurveyUpload_Raw, sheet_name="Data")
            PlanSurveyUpload.dataframe(PlanSurveyUpload_DF)
        if ActualSurveyUpload_Raw is not None:
            ActualSurveyUpload_DF = pd.read_excel(ActualSurveyUpload_Raw, sheet_name="Data")
            ActualSurveyUpload.dataframe(ActualSurveyUpload_DF)


        with open('Streamlit_App\\Data\\WellTrajectoryFormat.xlsx', 'rb') as f:
            st.download_button('Download Example Format', f, file_name='WellTrajectoryFormat.xlsx')
    if PlanSurveyUpload_Raw is not None:
        PlanSurvey = Trajectory.loadSurvey(PlanSurveyUpload_Raw).interpolate_survey_tvd(step=10)
        # st.dataframe(PlanSurvey)
        fig2DPanelTrajectory = PlanSurvey.figure(type='scatter3d')
        st.plotly_chart(fig2DPanelTrajectory)
        
        # PlotColumns[0]
        # PlotColumns[1]
        # st.number_input(label, min_value=None, max_value=None, value=, step=None, format=None, key=None
    # OutputContainer= st.container()


    




