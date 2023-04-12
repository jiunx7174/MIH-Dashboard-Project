import streamlit as st
from PDU_Func import Authentification, IO_Data,Table
from PDU_Func.IO_Data import getAvailableCompanyDF
from datetime import datetime


@st.cache_resource
def CheckCreateTable(WellInfoDict):
    if IO_Data.DomeCheckTable(WellInfoDict['wid'], table_type ="ActivityLogTable")['table']==0:
        IO_Data.DomeCreateTable(WellInfoDict['wid'], table_type ="ActivityLogTable")
    if IO_Data.DomeCheckTable(WellInfoDict['wid'], table_type ="ActivitySummaryTable")['table']==0:
        IO_Data.DomeCreateTable(WellInfoDict['wid'], table_type ="ActivitySummaryTable")


def IsSubmitFormTrue():
    st.session_state['IsFormSubmit'] = True


def initiateSession(WellInfoDict):
    
    CheckCreateTable(WellInfoDict)
    if "IsFormSubmit" not in st.session_state:
        st.session_state['IsFormSubmit'] = False
    if 'UserDateRange' not in st.session_state:
        st.session_state['UserDateRange'] = {
            "StartDate":[],
            "StartTime":[],
            "EndDate":[],
            "EndTime":[]
        }

def updateActivityLog(WellInfoDict,UpdateActivityLog_DF,UserDateRange):
    with st.spinner("Communicate with the server"):
        InputActivity_DB = (IO_Data.DomeGetData(WellInfoDict, UserDateRange,table_type="ActivityLogTable"))

        ## Delete
        for i,row in InputActivity_DB.iterrows():
            dict_temp = {
            'wid':WellInfoDict['wid'],
            'id':str(row['id']),
            }
            # st.json(input_dict_temp)
            IO_Data.DomeDeleteData(dict_temp, table_type="ActivityLogTable")

        ## Insert
        for  i,row in UpdateActivityLog_DF.iterrows():            
            dict_temp = {
                    'wid':WellInfoDict['wid'],
                    'dt':str(row['DateTime']),
                    'date':str(row['Date']),
                    'time':str(row['Time']),
                    'activity':row['Activity'],
                    'in_slip_threshold':row['In-Slip Threshold'],
                    'remarks' : row['Remarks'],
                    'pic' : row['PIC'],
                    'section':row['Section Size']
                    
                }
            IO_Data.DomeInsertData(dict_temp, table_type="ActivityLogTable")


def checkActivityLog(ActivityLog_DF):
    # TODO
    # create an activity log input check
    # -Duplicate Date Time
    # -empty columns values

    return ActivityLog_DF
        





# def updateActivityLog(ActivityLog_DF, UpdateActivityLog_DF):
#     old = ActivityLog_DF.set_index('DateTime')
#     update = UpdateActivityLog_DF.set_index('DateTime')

#     changed = old[old.index.isin(update.index)].ne(update)

#     removed = old.index.difference(update.index)
#     added = update.index.difference(old.index)

#     st.text("Removed")
#     st.dataframe(old.loc[removed,:])
#     st.text("Added")
#     st.dataframe(update.loc[added,:])

#     old = old.drop(index=list(removed))
#     update = update.drop(index=list(added))
#     changed = old.ne(update)
#     rows_changed = changed.any(axis=1)
#     st.text("changed")
#     st.dataframe(changed)
#     st.text(rows_changed.values)



def App():
    UserAuthDict = st.session_state['UserAuthDict']
    WellInfoDict = st.session_state['WellInfoDict']
    st.json(UserAuthDict)
    st.json(WellInfoDict)
    initiateSession(WellInfoDict)

    SidebarContainer = st.sidebar.container()
    # with SidebarContainer:
    with SidebarContainer.form(key='DateForm'):
        DateCol,TimeCol = st.columns([1,1])
        st.session_state['UserDateRange'] = {
        "StartDate":DateCol.date_input(
            "Start Date",
            value = datetime.strptime('31-07-2021', '%d-%m-%Y').date(),
            key="StartDateValues"
            ),

        "StartTime":TimeCol.time_input(
            "Start Time",
            value = datetime.strptime('00:00', '%H:%M').time(),
            key="StartTimeValues"),
        "EndDate":DateCol.date_input(
            "End Date",
            value = datetime.strptime('01-08-2021', '%d-%m-%Y').date(),
            key="EndDateValues"),
        "EndTime":TimeCol.time_input(
            "End Time",
            value = datetime.strptime('23:59', '%H:%M').time(),
            key="EndTimeValues")
        }


        st.form_submit_button(on_click=IsSubmitFormTrue)



    st.markdown('<h1 style="text-align: center; font-size: 50px; margin-top: 2px;"><span style="text-decoration: underline;">ACTIVITY MAPPING MODULE</span></h1>', unsafe_allow_html=True)
    
    st.button("Refresh", key="RefreshButton")


    if st.session_state['IsFormSubmit']:

        if "ActvitiyLog_DF" not in st.session_state:
            st.session_state["ActivityLog_DF"] = (IO_Data.DomeGetData(WellInfoDict, st.session_state['UserDateRange'], table_type="ActivityLogTable"))
        
        ActivityLog_DF = st.session_state["ActivityLog_DF"]
        # ActivityLog_DF = (IO_Data.DomeGetData(WellInfoDict, st.session_state['UserDateRange'], table_type="ActivityLogTable"))
        st.json(st.session_state['UserDateRange'])
        with st.form(key='aggrid_update'):
            out = Table.ActivityLogTable_Agrid(ActivityLog_DF, reload=True)


            isApply = st.form_submit_button("apply")


        if isApply:
            ActivityLog_DF_Upload = checkActivityLog(out['data'])

            updateActivityLog(WellInfoDict,ActivityLog_DF_Upload,st.session_state['UserDateRange'])
            st.session_state["ActivityLog_DF"] = (IO_Data.DomeGetData(WellInfoDict, st.session_state['UserDateRange'], table_type="ActivityLogTable"))
            st.success("Activity Log Update")
            st.experimental_rerun()


