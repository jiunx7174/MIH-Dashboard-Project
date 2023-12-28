import streamlit as st
from PDU_Func import Authentification, IO_Data
from importlib import reload
import pandas as pd
from streamlit_date_picker import date_range_picker, PickerType, Unit, date_picker
reload(IO_Data)
# @st.cache_data(show_spinner="Retrieve Rig Activity")
def cache_getRigActivity(WellInfoDict, **kwargs):
    return IO_Data.getRigActivity(WellInfoDict, **kwargs)
def App():
    UserAuthDict = st.session_state['UserAuthDict']
    SelectComp = st.session_state['SelComp']
    SelectWell = st.session_state['SelWell']
    WellInfoDict = IO_Data.getWellInfoDict(UserAuthDict, SelectComp, SelectWell)
    st.markdown("# ACTIVITY MAPPING")
    # UserAuthDict = st.session_state['UserAuthDict']
    RigName = WellInfoDict['RigName'].values.tolist()[0]
    # st.write()
    st.markdown(f"## RIG ACTIVITY [*{RigName}*]")
    st.divider()
    RigActivity_DF = (cache_getRigActivity(WellInfoDict, 
                   start_date="2000-01-01 00:00:01", 
                   end_date="2100-01-01 00:00:01"))
    if RigActivity_DF.empty:
        st.error("No Rig Activity")
        st.stop()   
    st.dataframe(RigActivity_DF[['DateTime', 'Activity']].sort_values(by='DateTime', ascending=False),
                    use_container_width=True,
                    hide_index=True,
                    height=200,
                    column_config={
                        "DateTime": st.column_config.DatetimeColumn(
                            "DateTime",
                            format="D MMM YYYY, h:mm a",
                            )
                        }
                    
                   )
    # st.markdown("#### EPI-9")
    st.divider()
    st.markdown("## WELL ACTIVITY")
    WellActivityHeaderCol = st.columns([6,5])

    WellActivityHeaderCol[0].caption("#### Select Datetime Range:")
    # WellActivityHeaderCol[0].caption("Select Datetime Range")
    with WellActivityHeaderCol[0]:
        date_range_string = date_range_picker(picker_type=PickerType.time.string_value,
                                            start=-30, end=0, unit=Unit.minutes.string_value,
                                            key='range_picker',
                                            # refresh_button={'is_show': True, 'button_name': 'Refresh last 30min',
                                            #                 'refresh_date': -30,
                                            #                 'unit': Unit.minutes.string_value}
                                                            )
    st.divider()
    st.image('Data\MockupRealtimeData.png', caption='Realtime')
    st.markdown("#### Activity Summary Table")
    st.dataframe(RigActivity_DF[['DateTime', 'Activity']].sort_values(by='DateTime', ascending=False),
                use_container_width=True,
                hide_index=True,
                height=200,
                column_config={
                    "DateTime": st.column_config.DatetimeColumn(
                        "DateTime",
                        format="D MMM YYYY, h:mm a",
                        )
                    }
                
                )
    with st.expander("Override Activity Data"):
        # st.image('Data\MockupActivityMapping.png', caption='Activity Mapping')
        st.dataframe(RigActivity_DF[['DateTime', 'Activity']].sort_values(by='DateTime', ascending=False),
                    use_container_width=True,
                    hide_index=True,
                    height=200,
                    column_config={
                        "DateTime": st.column_config.DatetimeColumn(
                            "DateTime",
                            format="D MMM YYYY, h:mm a",
                            )
                        }
                    
                    )
    st.write(date_range_string)
    st.write(st.session_state)
    st.stop()