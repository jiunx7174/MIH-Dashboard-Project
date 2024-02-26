import pandas as pd 
from datetime import datetime
import plotly.express as px
import requests
# from PDU_Func.IO_Data import DomeGetRealtimeRange
from PDU_Func import IO_Data
from datetime import datetime,timedelta
from importlib import reload
import pandas as pd 
from streamlit_modal import Modal
import time
import numpy as np
reload(IO_Data)
def getTimelinePlot(ActSumDF, wid,  LabelColumn = 'LABEL_SubActivity', TimelineRange='All'):
    def _checkActSum(df, Label="Label"):
        df = df.copy()

        df['StartDateTime'] = df['StartDateTime'].astype('datetime64[ns]')
        df['EndDateTime'] = df['EndDateTime'].astype('datetime64[ns]')
        # df['Duration'] = df['Duration'].astype('float')
        # df['Duration'] = pd.to_timedelta(df['Duration'], unit='minutes')
        df = df.sort_values('StartDateTime')
        df = df.reset_index(drop=True)

        df['Diff'] = df['StartDateTime'].shift(-1) - df['EndDateTime']
        # print(df)
        # case if Diff > 0
        # df_out = pd.DataFrame(df)
        idx_start = 0
        df_concat_list = []
        df['LABEL_IsVoid'] = False
        i = 0
        for idx,row in df[(df['Diff'] > pd.Timedelta(0))].iterrows():
            # print(i)
            if i == 0:
                df_concat_list.append(df.loc[idx_start:idx])
                i = i+1
            else:
                df_concat_list.append(df.loc[idx_start+1:idx])
            new_row = {
                "StartDateTime":row["EndDateTime"],
                "EndDateTime":df.loc[idx+1, 'StartDateTime'],
                Label:"Look and Define",
                "LABEL_IsVoid":True,
            }
            # st.write(new_row)
            df_concat_list.append(pd.DataFrame([new_row]))
            idx_start = idx
        df_concat_list.append(df.loc[idx+1:])

            

        df_out = pd.concat(df_concat_list, ignore_index=True,axis=0)
        return df_out
    
    # LabelColumn
    AllRealtime_DF = IO_Data.DomeGetRealtimeRange(wid)
    
    Timeline_DF = ActSumDF[['StartDateTime', 'EndDateTime']]
    Timeline_DF['Y-Axis'] = ActSumDF['Section']
    Timeline_DF['Label'] = ActSumDF[LabelColumn]


    Realtime_DF = _checkActSum(Timeline_DF)


    Realtime_DF['LABEL_IsVoid'] = ~Realtime_DF['LABEL_IsVoid']

    # df_fin = pd.concat([Timeline_DF.head(1), Timeline_DF, Timeline_DF.tail(1)])
    Realtime_DF.loc[(~Realtime_DF['LABEL_IsVoid']).tolist(), 'Label'] = 'VOID'
    Realtime_DF.loc[Realtime_DF['LABEL_IsVoid'].tolist(), 'Label'] = 'DONE'
    Realtime_DF['Y-Axis'] = 'REALTIME'
    Realtime_DF.drop(['Diff','LABEL_IsVoid'], axis=1, inplace=True)
    if  TimelineRange=='All':
        if AllRealtime_DF['StartDateTime'][0] < Realtime_DF['StartDateTime'].min():
            PreRealtime_DF = pd.DataFrame.from_dict([{
            'StartDateTime':AllRealtime_DF['StartDateTime'][0],
            'EndDateTime':Realtime_DF.head(1)['StartDateTime'][0],
            'Y-Axis':'REALTIME',
            'Label':'VOID',
                }]
                )
            Realtime_DF = pd.concat([PreRealtime_DF, Realtime_DF], ignore_index=True,axis=0)
        if AllRealtime_DF['EndDateTime'][0] > Realtime_DF['EndDateTime'].max():
            PostRealtime_DF = pd.DataFrame.from_dict([{
            'StartDateTime':Realtime_DF.head(1)['EndDateTime'][0],
            'EndDateTime':AllRealtime_DF['EndDateTime'][0],
            'Y-Axis':'REALTIME',
            'Label':'VOID',
                }]
                )
            Realtime_DF = pd.concat([ Realtime_DF, PostRealtime_DF], ignore_index=True,axis=0)
        

    
    fig = px.timeline(pd.concat([ Realtime_DF,Timeline_DF,]), 
                x_start="StartDateTime", 
                x_end="EndDateTime", 
                y="Y-Axis",
                hover_data=['Label'],
                color='Label'
                )
    for i in fig.data:
        i.marker.line.width = 0
    fig.update_layout(
        title = 'Progress Activity Mapping',
                      legend=dict(
                            orientation="h",
                            # itemwidth=70,
                            yanchor="bottom",
                            y=-0.8,
                            xanchor="right",
                            x=1
                        ),
        template='ggplot2'
        )
    fig.update_yaxes(title='Section')
    fig.update_xaxes(title='Timeline')
    return fig