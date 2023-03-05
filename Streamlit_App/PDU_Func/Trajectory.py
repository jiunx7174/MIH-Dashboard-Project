import pandas as pd 
import welleng as we
import plotly.graph_objects as go
import numpy as np


def convertDF2Survey(TrajectoryDF):
    TrajectoryDF = TrajectoryDF.copy()
    ColumnUnitDict = {}
    ColumnRenameDict = {}

    for ColName in list(TrajectoryDF.columns):
        ColKeys=ColName.split(" (")[0]
        ColValues=ColName.split(" (")[1].split(")")[0]
        ColumnRenameDict[ColName] = ColKeys
        ColumnUnitDict[ColKeys] = ColValues
    TrajectoryDF.rename(columns = ColumnRenameDict, inplace = True)
    # TrajectoryDF[]
    # TrajectoryDF[]
    # TrajectoryDF[]
    surveyObj=we.survey.Survey(TrajectoryDF['MD'].tolist(),
            TrajectoryDF['Inc'].tolist(),
            TrajectoryDF['Azi'].tolist(),
            start_xyz=[0., 0., 0.],
            deg=True,
            unit="meters",
        )


    return surveyObj

def loadSurvey(Filename):
    TrajectoryRaw_DF = pd.read_excel(Filename, sheet_name="Data")
    TrajectorySurvey = convertDF2Survey(TrajectoryRaw_DF)
    return TrajectorySurvey

def emptyTargetPoint():
    TargetDF = pd.DataFrame(columns=[
        "X",
        "Y",
        "Z",
        "DLS"
    ])
    return TargetDF

def generateSurvey(TargetDF, interpolation_step = 30, datum=15, init_inc=0, init_azi=0):
    # node_list = []
    connector_list = []
    i = 0
    for idx,row in TargetDF.iterrows():
        print([row['X'], row['Y'], row['Z'], row['DLS']])
        if i==0:

            node0 = (we.node.Node(pos=[row['X'], row['Y'], row['Z']], md=-datum, inc=init_inc, azi=init_azi))
        elif i==1:
            node = (we.node.Node(pos=[row['X'], row['Y'], row['Z']]))
            connector_list.append(
                we.connector.Connector(node0, node, dls_design=row['DLS'])
            )
            
        elif i>1:
            node = (we.node.Node(pos=[row['X'], row['Y'], row['Z']]))
            connector_list.append(
                we.connector.Connector(connector_list[-1].node_end, node,dls_design=row['DLS'])
            )
        i = i+1
    survey_example_2 = we.survey.from_connections(
        connector_list
        ).interpolate_survey(step=interpolation_step)
    return survey_example_2


def add3DTrajectoryLines(SurveyList):
    pass

    # for idx,row in TargetDF.iterrows():
    #     if idx==1:

    #         node_list.append(we.node.Node(pos=[row['X'], row['Y'], row['Z']], md=-datum, inc=init_inc, azi=init_azi))
    #     else:
    #         node_list.append(we.node.Node(pos=[row['X'], row['Y'], row['Z']]))


    # for i in range(len(node_list)-1):
    #     connector_list.append(
    #     we.connector.Connector(node_list[i], node_list[i+1])
    #     )
def _update_fig(fig, kwargs):
    """
    Update the fig axis along with any user defined kwargs.
    """
    fig.update_scenes(
        zaxis_autorange="reversed",
        aspectmode='data',
        xaxis=dict(
            title='East (m)'
        ),
        yaxis=dict(
            title='North (m)',
        ),
        zaxis=dict(
            title="TVD (m)"
        )
    )
    for k, v in kwargs.items():
        if k == "layout":
            fig.update_layout(v)
        elif k == "traces":
            fig.update_traces(v)
        else:
            continue

    return fig
def _scatter3d(survey, **kwargs):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter3d(
            x=survey.e,
            y=survey.n,
            z=survey.tvd,
            name='survey',
            mode='lines',
            hoverinfo='skip'
        )
    )
    if not hasattr(survey, "interpolated"):
        survey.interpolated = [False] * len(survey.md)
    if survey.interpolated is None:
        survey.interpolated = [False] * len(survey.md)
    try:
        n, e, v, md, inc, azi = np.array([
            [n, e, v, md, inc, azi]
            for n, e, v, i, md, inc, azi in zip(
                survey.n, survey.e, survey.tvd, survey.interpolated,
                survey.md, survey.inc_deg, survey.azi_grid_deg
            )
            if bool(i) is True
        ]).T
        if n.size:
            text = [
                f"N: {n:.2f}m<br>E: {e:.2f}m<br>TVD: {v:.2f}m<br>"
                + f"MD: {md:.2f}m<br>INC: {inc:.2f}\xb0<br>AZI: {azi:.2f}\xb0"
                for n, e, v, md, inc, azi in zip(n, e, v, md, inc, azi)
            ]
            fig.add_trace(
                go.Scatter3d(
                    x=e,
                    y=n,
                    z=v,
                    name='interpolated',
                    mode='markers',
                    marker=dict(
                        size=5,
                        color='blue',
                    ),
                    text=text,
                    hoverinfo='text'
                )
            )
    except ValueError:
        pass

    try:
        n, e, v, md, inc, azi = np.array([
            [n, e, v, md, inc, azi]
            for n, e, v, i, md, inc, azi in zip(
                survey.n, survey.e, survey.tvd, survey.interpolated,
                survey.md, survey.inc_deg, survey.azi_grid_deg
            )
            if bool(i) is False
        ]).T
        text = [
            f"N: {n:.2f}m<br>E: {e:.2f}m<br>TVD: {v:.2f}m<br>"
            + f"MD: {md:.2f}m<br>INC: {inc:.2f}\xb0<br>AZI: {azi:.2f}\xb0"
            for n, e, v, md, inc, azi in zip(n, e, v, md, inc, azi)
        ]
        fig.add_trace(
            go.Scatter3d(
                x=e,
                y=n,
                z=v,
                name='survey_point',
                mode='markers',
                marker=dict(
                    size=5,
                    color='red',
                ),
                text=text,
                hoverinfo='text'
            )
        )
    except ValueError:
        pass

    fig = _update_fig(fig, kwargs)

    return fig