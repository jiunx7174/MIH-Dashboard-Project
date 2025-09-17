
import streamlit as st
import pandas as pd
from Page import Override
import numpy as np

def is_empty_dict(d):
    """
    Checks if a dictionary contains only empty dictionaries or lists.
    """
    if isinstance(d, dict):
        return all(is_empty_dict(v) for v in d.values())
    elif isinstance(d, list):
        return len(d) == 0  # Empty list
    else:
        return False  # Non-empty value

    # Recursively check all values in the dictionary
    return all(is_nested_dict_empty(v) for v in d.values())
@st.fragment
def App(ActivitySummary_DF, WellInfoDict, UserAuthDict, RemarksEdit=True):
    if "PIC" not in ActivitySummary_DF.columns:
        ActivitySummary_DF['PIC'] = ""
    if "Remarks" not in ActivitySummary_DF.columns:
        ActivitySummary_DF['Remarks'] = ""
    TableContainer, ColumnSelectionContainer = st.columns([6, 1])
    ColumnRename_dict = {'Date':'Date',
    'StartDateTime':'Start Datetime',
    'EndDateTime':'End Datetime',
    'Duration':'Duration(min)',
    'Hole_Depth_max':'Hole Depth (Max)',
    'Bit_Depth_avg':'Bit Depth (Avg)',
    'DrillingMeterage':'Drilling Meterage (m)',
    'RotateDrillingDuration':'Rotate Drilling Duration (min)',
    'SlideDrillingDuration':'Slide Drilling Duration (min)',
    'ReamingDuration':'Reaming Duration(min)',
    'DrillingMeteragePerStand':'Total Drilling Meterage per. Stand',
    'OnBottomDurationPerStand':'Total On-Bottom Duration per. Stand',
    'StandDuration':'Total Duration per. Stand',
    'Stand Group_Pred':'Stand Group ID',
    'Stand Group_Pred_TRIP':'Casing Joint Group ID',
    'LABEL_ConnectionActivity':'Connection Group ID',
    'ConnectionDuration':'Connection Duration (min)',
    'LABEL_SubActivity':'Sub-Activity Group',
    'LABEL_Activity':'Activity Group',
    'InSlip_Treshold':'In-Slip Threshold',
    'stand_on_bottom':'?',
    'PIC':'PIC',
    'Section':'Section Size',
    'Remarks':'Remarks',}
    ColumnRename_r_dict = {v: k for k, v in ColumnRename_dict.items()}

    DatetimeColSelect_df = pd.DataFrame({
        'ColumnName': ['Date',
                        'StartDateTime',
                        'EndDateTime',
                        'Duration',
                        ],
        "Display": [False, True, True, True],
    })

    BitPosColSelect_df = pd.DataFrame({
        'ColumnName': [
            'Hole_Depth_max',
            'Bit_Depth_avg',
        ],
        "Display":[True, True]
    })



    DrillingOpsColSelect_df = pd.DataFrame({
        'ColumnName':['DrillingMeterage',
        'RotateDrillingDuration',
        'SlideDrillingDuration',
        'ReamingDuration',
        'DrillingMeteragePerStand',
        'OnBottomDurationPerStand',
        'StandDuration',
        'Stand Group_Pred',
        'Stand Group_Pred_TRIP',
        'LABEL_ConnectionActivity',
        'ConnectionDuration',],
        "Display":[False, False, False, False, False, False, False,False, False, False, False]
    })
    ActivityColSelect_df = pd.DataFrame({
        'ColumnName':['LABEL_SubActivity',
                        'LABEL_Activity'],
        "Display":[True, True]

    })
    AdditionalColSelect_df = pd.DataFrame({
        'ColumnName':['InSlip_Treshold',
                        'stand_on_bottom',
                        'PIC',
                        'Section',
                        'Remarks'],
        "Display":[True, False, True, True, True]
    })
    ColumnConfigColSel = {
        'ColumnName': st.column_config.TextColumn(
            label="Column Name",
            disabled=True,
        ),
        'Display': st.column_config.CheckboxColumn(
            label="Display",
            disabled=False,
        ),
    }
    ActSumColumnConfig = {
    "Date": st.column_config.DatetimeColumn(
        "Date",
        disabled=True
    ),
    "StartDateTime": st.column_config.DatetimeColumn(
        "Start Datetime",
        disabled=True
    ),
    "EndDateTime": st.column_config.DatetimeColumn(
        "End Datetime",
        disabled=True
    ),
    "Duration": st.column_config.TextColumn(
        "Duration(min)",
        disabled=True
    ),
    "Hole_Depth_max": st.column_config.TextColumn(
        "Hole Depth (Max)",
        disabled=True
    ),
    "Bit_Depth_avg": st.column_config.TextColumn(
        "Bit Depth (Avg)",
        disabled=True
    ),
    "DrillingMeterage": st.column_config.TextColumn(
        "Drilling Meterage (m)",
        disabled=True
    ),
    "RotateDrillingDuration": st.column_config.TextColumn(
        "Rotate Drilling Duration (min)",
        disabled=True
    ),
    "SlideDrillingDuration": st.column_config.TextColumn(
        "Slide Drilling Duration (min)",
        disabled=True
    ),
    "ReamingDuration": st.column_config.TextColumn(
        "Reaming Duration(min)",
        disabled=True
    ),
    "DrillingMeteragePerStand": st.column_config.TextColumn(
        "Total Drilling Meterage per. Stand",
        disabled=True
    ),
    "OnBottomDurationPerStand": st.column_config.TextColumn(
        "Total On-Bottom Duration per. Stand",
        disabled=True
    ),
    "StandDuration": st.column_config.TextColumn(
        "Total Duration per. Stand",
        disabled=True
    ),
    "Stand Group_Pred": st.column_config.TextColumn(
        "Stand Group ID",
        disabled=True
    ),
    "Stand Group_Pred_TRIP": st.column_config.TextColumn(
        "Casing Joint Group ID",
        disabled=True
    ),
    "LABEL_ConnectionActivity": st.column_config.TextColumn(
        "Connection Group ID",
        disabled=True
    ),
    "ConnectionDuration": st.column_config.TextColumn(
        "Connection Duration (min)",
        disabled=True
    ),
    "LABEL_SubActivity": st.column_config.TextColumn(
        "Sub-Activity Group",
        disabled=True
    ),
    "LABEL_Activity": st.column_config.TextColumn(
        "Activity Group",
        disabled=True
    ),
    "InSlip_Treshold": st.column_config.TextColumn(
        "In-Slip Threshold",
        disabled=True
    ),
    "stand_on_bottom": st.column_config.TextColumn(
        "?",
        disabled=True
    ),
    "PIC": st.column_config.TextColumn(
        "PIC",
        disabled=True
    ),
    "Section": st.column_config.TextColumn(
        "Section Size",
        disabled=True
    ),
    "Remarks": st.column_config.TextColumn(
        "Remarks",
        disabled=False
    )
}


    DatetimeColSelect_df['ColumnName'] = DatetimeColSelect_df['ColumnName'].map(ColumnRename_dict)
    BitPosColSelect_df['ColumnName'] = BitPosColSelect_df['ColumnName'].map(ColumnRename_dict)
    DrillingOpsColSelect_df['ColumnName'] = DrillingOpsColSelect_df['ColumnName'].map(ColumnRename_dict)
    ActivityColSelect_df['ColumnName'] = ActivityColSelect_df['ColumnName'].map(ColumnRename_dict)
    AdditionalColSelect_df['ColumnName'] = AdditionalColSelect_df['ColumnName'].map(ColumnRename_dict)


    with ColumnSelectionContainer.popover("Datetime Columns", width="content"):
        FinalDatetimeColSelect_df = st.data_editor(DatetimeColSelect_df, key='DatetimeColSelect', hide_index=True, column_config=ColumnConfigColSel)
    with ColumnSelectionContainer.popover("Bit Position Columns", width="content"):
        FinalBitPosColSelect_df = st.data_editor(BitPosColSelect_df, key='BitPosColSelect',hide_index=True, column_config=ColumnConfigColSel)
    with ColumnSelectionContainer.popover("Drilling Operations Columns", width="content"):
        FinalDrillingOpsColSelect_df = st.data_editor(DrillingOpsColSelect_df, key='DrillingOpsColSelect', hide_index=True,column_config=ColumnConfigColSel)
    with ColumnSelectionContainer.popover("Activity Columns", width="content"):
        FinalActivityColSelect_df = st.data_editor(ActivityColSelect_df, key='ActivityColSelect', hide_index=True,column_config=ColumnConfigColSel)
    with ColumnSelectionContainer.popover("Additional Columns", width="content"):
        FinalAdditionalColSelect_df = st.data_editor(AdditionalColSelect_df, key='AdditionalColSelect',hide_index=True, column_config=ColumnConfigColSel)
    
    ColumnDisplaySelection_df= pd.concat([FinalDatetimeColSelect_df, FinalBitPosColSelect_df, FinalDrillingOpsColSelect_df, FinalActivityColSelect_df, FinalAdditionalColSelect_df])
    ColumnDisplaySelection_df['ColumnName'] = ColumnDisplaySelection_df['ColumnName'].map(ColumnRename_r_dict)
    ColumnDisplaySelection_df = ColumnDisplaySelection_df[ColumnDisplaySelection_df['Display'] == True]
    ColumnDisplaySelection_list = ColumnDisplaySelection_df['ColumnName'].tolist()
    FinalActSumColumnConfig = {}
    for ColumnName in ColumnDisplaySelection_list:
        FinalActSumColumnConfig[ColumnName] = ActSumColumnConfig[ColumnName]
    # if "Remarks" in ColumnDisplaySelection_list:
    #     # TableContainer.dataframe(ActivitySummary_DF[ColumnDisplaySelection_list], use_container_width=True)
    #     TableContainer.write(st.write(st.session_state['RemarksActSumTable']))
    # else:
    #     TableContainer.dataframe(ActivitySummary_DF[ColumnDisplaySelection_list], use_container_width=True)
    
    if RemarksEdit :
        OverrideRemark_df = TableContainer.data_editor(ActivitySummary_DF[ColumnDisplaySelection_list], key='RemarksActSumTable_DataEditor', hide_index=True,  use_container_width=True, column_config=FinalActSumColumnConfig)
        isRemarksActSumUpdateEmpty = True
        for RemarksActSumKey in ['edited_rows', 'added_rows', 'deleted_rows']:
            if is_empty_dict(st.session_state['RemarksActSumTable_DataEditor']):
            # if st.session_state['RemarksActSumTable'][RemarksActSumKey] != []:
                isRemarksActSumUpdateEmpty = True
            else:
                isRemarksActSumUpdateEmpty = False
        if not isRemarksActSumUpdateEmpty:

            FinalOverrideRemark_df = pd.DataFrame(st.session_state['RemarksActSumTable_DataEditor']['edited_rows']).T.reset_index(names="Idx")

            FinalOverrideRemark_df['StartDateTime'] = OverrideRemark_df.loc[FinalOverrideRemark_df['Idx'].tolist(), 'StartDateTime'].tolist()
            FinalOverrideRemark_df['EndDateTime'] = OverrideRemark_df.loc[FinalOverrideRemark_df['Idx'].tolist(), 'EndDateTime'].tolist()

            # Split the 'datetime' column into 'Date' and 'Time'

            FinalOverrideRemark_df[['StartDate', 'StartTime']] = FinalOverrideRemark_df['StartDateTime'].astype(str).str.split(' ', expand=True)
            FinalOverrideRemark_df[['EndDate', 'EndTime']] = FinalOverrideRemark_df['EndDateTime'].astype(str).str.split(' ', expand=True)

            # Drop the 'datetime' column
            FinalOverrideRemark_df = FinalOverrideRemark_df.drop(columns=['StartDateTime'])
            FinalOverrideRemark_df = FinalOverrideRemark_df.drop(columns=['EndDateTime'])
            

            # st.write(FinalOverrideRemark_df)
            # st.write(FinalOverrideRemark_df)
            if st.button("Update Remarks", type="primary", use_container_width=True):

                Override.UpdateRemarksActSumTable(FinalOverrideRemark_df, WellInfoDict,UserAuthDict, 'RemarksActSumTable',)
                st.success("Remarks Updated!")
    else:
        TableContainer.dataframe(ActivitySummary_DF[ColumnDisplaySelection_list], use_container_width=True, hide_index=True, column_config=FinalActSumColumnConfig)