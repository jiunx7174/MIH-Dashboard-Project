import streamlit as st
import numpy as np 
import pandas as pd
from PDU_Func import Activity, Authentification, IO_Data
from datetime import datetime, timedelta
import time
from importlib import reload

reload(IO_Data)
@st.fragment
def App(WellInfoDict, RigName, RigActivity_DF_Display, is_editable=False):
    replacement_dict = {
        "Cementing":16,
        "Undefined Status":0,
        "Drilling":2,
        "Connection (drilling)":3,
        "Reaming":4,
        "Condition and/or Circulate mud":7,
        "Tripping In":8,
        "Tripping Out":9,
        "Lubricate Rig":10,
        "Rig Repair":11,
        "Cut/Slip Drilling Line":12,
        "Wireline Logs":14,
        "Run Casing":15,
        "Plug Back":17,
        "Squeeze Cementing":18,
        "Wait on Cement":19,
        "Drill Cement and/or Float Equipment":20,
        "Nipple Up /Nipple Down BOP Stack":21,
        "Test BOP":22,
        "Fishing":24,
        "Stuck Pipe":27,
        "Flow Check":30,
        "Pressure Integrity Test":31,
        "Lost Circulation":32,
        "Short Trip In":33,
        "Short Trip Out":34,
    }
    RigNameCols, IsRigEditCol = st.columns([7,3], vertical_alignment='center') 
    RigNameCols.markdown(f"##### Rig Name: *{RigName}*")

# IsRigEditCol.container(horizontal_alignment='right')
    if is_editable:
        is_edit = IsRigEditCol.container(horizontal_alignment='right').toggle("Edit Rig Activity", key="IsRigActivityEdit")
    else:
        is_edit = False

    # if is_edit = False:
    # else:
    #     is_edit = IsRigEditCol.toggle("Edit Rig Activity", key="IsRigActivityEdit")
    RigActivity_DF_Display = RigActivity_DF_Display[['DateTime', 'Detail Rig Activity', 'Simple Activity']].sort_values(by='DateTime', ascending=False)

    if is_edit:
        selection = st.segmented_control(
                "", ['Insert', 'Remove', 'Update'], selection_mode="single", width= 'stretch', label_visibility="collapsed", default=None,key="RigEditAction"
            )
        
        # st.write(selection)
        if selection == 'Remove':
            
            event = st.dataframe(
                RigActivity_DF_Display,
                # key="RigActivityTable",
                on_select="rerun",
                selection_mode="multi-row",
                column_config={
                    "DateTime": st.column_config.DatetimeColumn(
                        "DateTime",
                        format="YYYY-MM-DD | HH:mm:ss",
                        ),
                    
                    
                    "Detail Rig Activity": st.column_config.SelectboxColumn(
                        "Detail Rig Activity",
                        options = RigActivity_DF_Display['Detail Rig Activity'].unique().tolist(),
                        # max_chars=50,
                        # ed
                        ),
                    },   
                hide_index=True,
                height=150,
            )
            st.warning("Select rows to remove from the table above, then click the button below to confirm.")
            st.button("Remove Selected Rows", type="primary", disabled=True, width='stretch')
        elif selection == 'Insert':
            st.dataframe(
                RigActivity_DF_Display,
                hide_index=True,
                height=150,
            )
            RigEditDateCol, RigEditTimeCol, RigEditActivityCol = st.columns([2.5,2.5,5])
            RigEditDateCol.date_input("Select Date", key="RigEditDate")
            RigEditTimeCol.time_input("Select Time", key="RigEditTime")
            RigEditActivityCol.selectbox("Detail Rig Activity",list(replacement_dict.keys()),index=None, key="RigInsertActivityWidget")
            if st.session_state['RigInsertActivityWidget'] == None:
                st.warning("Fill in the details above, then click the button below to insert a new activity.")
            if st.button("Insert", type="primary",disabled=st.session_state['RigInsertActivityWidget'] == None, key="RigEditSubmit", width='stretch'):
                Date_str = str(st.session_state['RigEditDate'])
                Time_str = str(st.session_state['RigEditTime'])
                DateTime_str = Date_str + " " + Time_str
                ActCode_int = replacement_dict[st.session_state['RigInsertActivityWidget']]
                IO_Data.insertRigActivity(WellInfoDict, DateTime_str, ActCode_int)
                st.toast(f"{DateTime_str} with activity {st.session_state['RigInsertActivityWidget']} is inserted")
                time.sleep(2)
                st.rerun()

        elif selection == 'Update':
            result = st.data_editor(
                RigActivity_DF_Display,
                height=150,
                # key="RigActivityTable",
                num_rows="fixed",
                column_config={
                    "DateTime": st.column_config.DatetimeColumn(
                        "DateTime",
                        format="YYYY-MM-DD | HH:mm:ss",
                        ),
                    
                    
                    "Detail Rig Activity": st.column_config.SelectboxColumn(
                        "Detail Rig Activity",
                        options = list(replacement_dict.keys()),
                        # max_chars=50,
                        # ed
                        ),
                    },   
                hide_index=True,
                key='RigUpdateActivityWidget'
            )
            # st.write(st.session_state['RigUpdateActivityWidget']['edited_rows'].keys())
            # st.write(result)



            st.warning("Edit the details directly in the table above, then click the button below to confirm updates.")
            if st.button("Update", type="primary", disabled=True, width='stretch'):
                UpdatedResult_df = pd.DataFrame(result.iloc[list(st.session_state['RigUpdateActivityWidget']['edited_rows'].keys())])
                st.write(UpdatedResult_df)
                # st.write(result)
                for idx,row in UpdatedResult_df.iterrows():
                    DateTime_str = str(row['DateTime'])
                    ActCode_int = replacement_dict[row['Detail Rig Activity']]
                    IO_Data.updateRigActivity(WellInfoDict, DateTime_str, ActCode_int)
                    st.toast(f"{DateTime_str} is updated to {row['Detail Rig Activity']}")
                time.sleep(2)
                # st.rerun()
        else:
            st.dataframe(
                RigActivity_DF_Display,
                # key="RigActivityTable",
                height=150,
                # on_select="rerun",
                # selection_mode="multi-row",
                hide_index=True,
            )

        # st.write(event.selection)
        # if len(event.selection['rows'])>0 :
        #     # RigEditActivityCol, RigEditDeleteCol = st.columns([5,5])

        #     # st.selectbox("Select Action", ["Update Selected Rows","Remove Selected Rows"], key="RigEditAction")
        #     # RigEditDeleteCol.button("Update/Remove Selected Rows", type="primary", width='stretch')
        # else:

        #     RigEditDateCol, RigEditTimeCol, RigEditActivityCol = st.columns([2.5,2.5,5])
        #     RigEditDateCol.date_input("Select Date", key="RigEditDate")
        #     RigEditTimeCol.time_input("Select Time", key="RigEditTime")
        #     RigEditActivityCol.text_input("Detail Rig Activity", key="RigEditActivity")

        #     st.button("Submit", type="primary",disabled=False, key="RigEditSubmit", width='stretch')

        
        #     # st.write("tes")







    else:
        st.dataframe(
            RigActivity_DF_Display,
            # key="RigActivityTable",
            height=200,
            # on_select="rerun",
            # selection_mode="multi-row",
            hide_index=True,
        )
        st.session_state["RigEditAction"] = None
    # st.dataframe(df)
    
    # Add more functionality as needed