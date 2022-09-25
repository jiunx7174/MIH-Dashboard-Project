import requests
import json
import pandas as pd
# import psycopg2
from io import BytesIO
import streamlit as st
import time

def getActivityData(wid, start_dt, end_dt):
    Data_params ={
        "wid" : int(wid),
        "start" : start_dt.strftime("%Y-%m-%d %H:%M:%S"),
        "end" : end_dt.strftime("%Y-%m-%d %H:%M:%S")
    }
    # now.strftime("%Y-%m-%d, %H:%M:%S")
    # print(Data_params)
    column_list = ["dt", "date", "time", "bitdepth", "md", "blockpos", "rop", "hklda", "woba", "torqa", "rpm", "stppress", "mudflowin",]
    # return None
    WellData = (
        (
            requests.get("http://khansadev.xyz/dome_api/rtdc/get_data", data=json.dumps(Data_params))
        ).text
    )

    Data_DF = pd.json_normalize(json.loads(WellData), record_path='result')
    # print(Data_DF.head(5))
    return Data_DF[column_list]


def getActivityData_v2(wid, start_dt, end_dt):
    Data_params ={
        "wid" : int(wid),
        "start" : start_dt,
        "end" : end_dt
    }
    # now.strftime("%Y-%m-%d, %H:%M:%S")
    # print(Data_params)
    column_list = ["dt", "date", "time", "bitdepth", "md", "blockpos", "rop", "hklda", "woba", "torqa", "rpm", "stppress", "mudflowin",]
    # return None
    WellData = (
        (
            requests.get("http://khansadev.xyz/dome_api/rtdc/get_data", data=json.dumps(Data_params))
        ).text
    )

    Data_DF = pd.json_normalize(json.loads(WellData), record_path='result')
    # print(Data_DF.head(5))
    return Data_DF[column_list]



def get_session_id():
    # Hack to get the session object from Streamlit.

    ctx = ReportThread.get_report_ctx()

    this_session = None
    
    current_server = Server.get_current()
    if hasattr(current_server, '_session_infos'):
        # Streamlit < 0.56        
        session_infos = Server.get_current()._session_infos.values()
    else:
        session_infos = Server.get_current()._session_info_by_id.values()

    for session_info in session_infos:
        s = session_info.session
        if (
            # Streamlit < 0.54.0
            (hasattr(s, '_main_dg') and s._main_dg == ctx.main_dg)
            or
            # Streamlit >= 0.54.0
            (not hasattr(s, '_main_dg') and s.enqueue == ctx.enqueue)
        ):
            this_session = s

    if this_session is None:
        raise RuntimeError(
            "Oh noes. Couldn't get your Streamlit Session object"
            'Are you doing something fancy with threads?')

    return id(this_session)

def GetInputActivity_DB(Conn, Well, Comp):
    cursor = Conn.cursor()

    select_query = "select * from activitylog_db"
    select_query += " where (well = '%s' and comp = '%s')" % (Well, Comp)
    # select_query += "where  = %s" %Well
    Table_Column = ['input_id',
                        'dt',
                        'date',
                        'time',
                        'comp',
                        'well',
                        'activity',
                        'in_slip_treshold',
                        'remarks',
                        'pic',
                        'section'
                        ]
    try:
        cursor.execute(select_query)
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        cursor.close()
        return 1
    
    # Naturally we get a list of tupples
    tupples = cursor.fetchall()
    cursor.close()
    Conn.close()
    # We just need to turn it into a pandas dataframe
    df = pd.DataFrame(tupples, columns=Table_Column)
    return df
def GetSummaryActivity_DB(Conn, Well, Comp):
    cursor = Conn.cursor()

    select_query = "select * from summary_activity_db"
    select_query += " where (well = '%s' and comp = '%s')" % (Well, Comp)
    # select_query += "where  = %s" %Well
    listcolumn = ['comp',
        'well',
        'time_start',
        'time_end',
        'duration_minutes',
        'hole_depth',
        'bit_depth',
        'meterage_drilling',
        'rotate_drilling_time',
        'slide_drilling_time',
        'reaming_time',
        'connection_time',
        'on_bottom_hours',
        'stand_duration',
        'label_subactivity',
        'label_activity',
        'stand_meterage_drilling',
        'stand_durationx',
        'stand_on_bottom',
        'stand_group',
        'pic',
        'section',
        'remarks']
    try:
        cursor.execute(select_query)
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        cursor.close()
        return 1
    
    # Naturally we get a list of tupples
    tupples = cursor.fetchall()
    cursor.close()
    Conn.close()
    # We just need to turn it into a pandas dataframe
    df = pd.DataFrame(tupples, columns=Table_Column)
    return df

# @st.cache
def OpenConnection():
    param_dic = {
    "host"      : "localhost",
    "database"  : "PDU_AUTOMAPPING",
    "user"      : "postgres",
    "password"  : "Saber2496"
    }
    conn = None
    # import json


    
    # print(user_encode_data)
    # try:
        # connect to the PostgreSQL server
        # print('Connecting to the PostgreSQL database...')
    conn = psycopg2.connect(**param_dic)
    # except (Exception, psycopg2.DatabaseError) as error:
        # print(error)
        # sys.exit(1) 
    return conn

def DeleteInputActivity_DB(Conn, Well, Comp, InputID):
    SQL_Queries = "delete from activitylog_db"
    SQL_Queries += " where ((well = '%s' and comp = '%s') and input_id = %s)" % (Well, Comp, InputID)

    
    cursor = Conn.cursor()
    try:
        cursor.execute(SQL_Queries)
        Conn.commit()
    except(Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        Conn.rollback()
        cursor.close()
        return 1
    cursor.close()
    Conn.close() 

    # return None

def InsertInputActivity_DB(Conn, InputDict):
    
    SQL_Queries = """
    INSERT into activitylog_db(input_id, dt, date, time, comp, well, activity, in_slip_treshold, remarks, pic, section) values(%s,'%s','%s','%s','%s','%s','%s',%s,'%s','%s','%s');
    """ % tuple(InputDict.values())
    
    cursor = Conn.cursor()
    try:
        cursor.execute(SQL_Queries)
        Conn.commit()
    except(Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        Conn.rollback()
        cursor.close()
        return 1
    cursor.close()
    Conn.close() 
    # return None

def InsertSummaryActivity_DB(Conn, SummaryActivity_DF, WellName, CompName):
    SummaryActivity_DF = Activity.SummaryTranslator(SummaryActivity_DF, WellName, CompName, '-', '-', '-')
    for i in SummaryActivity_DF.index:
        SQL_Queries = """INSERT into summary_activity_db(comp, well, time_start, time_end, duration_minutes, hole_depth, bit_depth, meterage_drilling, rotate_drilling_time, slide_drilling_time, reaming_time, connection_time, on_bottom_hours, stand_duration, label_subactivity, label_activity, stand_meterage_drilling, stand_durationx, stand_on_bottom, stand_group, pic, section, remarks) values('%s', '%s', '%s', '%s', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '%s', '%s', '%s', %s, %s, '%s', '%s', '%s', '%s'"""
        SQL_Queries += ")" 

        # print()
        cursor = Conn.cursor()
        try:
            cursor.execute(SQL_Queries % tuple(SummaryActivity_DF.iloc[i,:].to_list()))
            Conn.commit()
        except(Exception, psycopg2.DatabaseError) as error:
            print("Error: %s" % error)
            Conn.rollback()
            cursor.close()
            return 1
        cursor.close()
    Conn.close() 


# http://khansadev.xyz/dome_api/rtdc/Activitylog/cek_table
# http://khansadev.xyz/dome_api/rtdc/Activitylog/create_table
# http://khansadev.xyz/dome_api/rtdc/Activitylog/create
# http://khansadev.xyz/dome_api/rtdc/Activitylog/update
# http://khansadev.xyz/dome_api/rtdc/Activitylog/delete
# http://khansadev.xyz/dome_api/rtdc/Activitylog/get_data

def DomeCekTable(wid, table_type="Activity Log"):
    if table_type=="Activity Log":    
        WellAPI = "http://khansadev.xyz/dome_api/rtdc/Activitylog/cek_table"
        json_queries = {
        "wid": wid
        }

        response = (
            requests.post(
                WellAPI, data=json.dumps(json_queries, indent = 4) 
            )
        )
        return dict(response.json())
    
    elif table_type=="Activity Summary":
        WellAPI = "http://khansadev.xyz/dome_api/rtdc/ActivitySummary/cek_table"
        json_queries = {
        "wid": wid
        }

        response = (
            requests.post(
                WellAPI, data=json.dumps(json_queries, indent = 4) 
            )
        )
        return dict(response.json())


def DomeCreateTable(wid, table_type="Activity Log"):
    if table_type=="Activity Log":    
        WellAPI = "http://khansadev.xyz/dome_api/rtdc/Activitylog/create_table"
        json_queries = {
        "wid": wid
        }

        response = (
            requests.post(
                WellAPI, data=json.dumps(json_queries, indent = 4) 
            )
        )

        return dict(response.json())
    elif table_type=="Activity Summary":    
        WellAPI = "http://khansadev.xyz/dome_api/rtdc/ActivitySummary/create_table"
        json_queries = {
        "wid": wid
        }

        response = (
            requests.post(
                WellAPI, data=json.dumps(json_queries, indent = 4) 
            )
        )

        return dict(response.json())
    

def DomeAddData(dict_row, table_type="Activity Log"):
    time.sleep(0.1)
    print("add new data to " + table_type)
    if table_type=="Activity Log":
        AddRowAPI = "http://khansadev.xyz/dome_api/rtdc/Activitylog/create"
        error_msg = ""
        keys_list = ["wid", "dt", "date", "time", "activity",
                            "in_slip_threshold", "remarks", "pic", "section"]
        
        for keys_name in keys_list:
            if keys_name not in dict_row.keys():
                error_msg = error_msg + keys_name + ", "
        if error_msg == "":
            json_queries = json.dumps(
                dict_row,
                indent = 4
            )
            response = (
                requests.post(
                    AddRowAPI, data=json_queries 
                )
            )
            
            return dict(response.json())
        else:
            return error_msg
    elif table_type=="Activity Summary":
        AddRowAPI = "http://khansadev.xyz/dome_api/rtdc/ActivitySummary/create"
        error_msg = ""
        keys_list = ['wid', 'date', 'time_start', 'time_end', 'duration_minutes', 'hole_depth', 
                        'bit_depth', 'meterage_drilling', 'rotate_drilling_time', 'slide_drilling_time', 
                        'reaming_time', 'connection_time', 'on_bottom_hours', 'stand_duration', 'label_subactivity', 
                        'label_activity', 'stand_meterage_drilling', 'stand_durationx', 'stand_on_bottom', 'pic', 
                        'section', 'remark', 'stand_group']
        
        for keys_name in keys_list:
            if keys_name not in dict_row.keys():
                error_msg = error_msg + keys_name + ", "
        print(dict_row)
        if error_msg == "":
            json_queries = json.dumps(
                dict_row,
                indent = 4
            )
            response = (
                requests.post(
                    AddRowAPI, data=json_queries 
                )
            )
            # print(response)
            return dict(response.json())
        else:
            return error_msg

     
def DomeGetData(wid, start_date_time, end_date_time, table_type="Activity Log"):
    
    ColumnRenameDict = {'wid': 'wid',
                        'date': 'Date',
                        'time_start': 'Start Time',
                        'time_end': 'End Time',
                        'duration_minutes': 'Duration (Minutes)',
                        'hole_depth': 'Hole Depth (Max)',
                        'bit_depth': 'Bit Depth(mean)',
                        'meterage_drilling': 'Drilling Meterage (m)',
                        'rotate_drilling_time': 'Rotate Drilling (minutes)',
                        'slide_drilling_time': 'Slide Drilling (minutes)',
                        'reaming_time': 'Reaming (minutes)',
                        'connection_time': 'Connection (minutes)',
                        'on_bottom_hours': 'On Bottom state (Hours)',
                        'stand_duration': 'Stand Duration',
                        'label_subactivity': 'SUB-ACTIVITY',
                        'label_activity': 'ACTIVITY',
                        'stand_meterage_drilling': 'Total Stand Drilling Meterage (m)',
                        'stand_durationx': 'Total Stand Duration (hrs)',
                        'stand_on_bottom': 'Total On Bottom Duration (hrs)',
                        'pic': 'PIC',
                        'section': 'Section',
                        'remark': 'Remarks',
                        'stand_group': 'Stand Group_Pred'}
    ActivityLogColumnRenameDict = {
                            'id': 'id',
                            'dt': 'dt',
                            'date': 'date',
                            'time': 'time',
                            'activity': 'activity',
                            'in_slip_threshold': 'in_slip_threshold', 
                            'remarks': 'remarks',
                            'pic': 'pic',
                            'section': 'section'
                            }
    print("get " + table_type + " data/table from DOME")
    if table_type=="Activity Log":
        TableAPI = "http://khansadev.xyz/dome_api/rtdc/Activitylog/get_data"
        json_queries = json.dumps(
            {
            "wid": wid,
            "start" : '2000-10-17 00:00:00',
            "end" : '2050-10-17 00:00:00',
            # "start" : start_date_time,
            # "end" : end_date_time
            },
            indent = 4
        )
        response = (
            requests.get(
                TableAPI, data=json_queries
            )
        )
        if (dict(response.json())['result']) == []:
            # print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
            # print(dict(response.json())['result'])
            out_DF = pd.DataFrame(columns=ActivityLogColumnRenameDict.values())
            # print(ActivityLog_DF)
            # return ActivityLog_DF.to_dict()
        else:
            out_DF = pd.DataFrame(dict(response.json())['result'])
    
            out_DF['date_time'] = pd.to_datetime(out_DF['date'] + " " + out_DF['time'])
            out_DF = out_DF.sort_values(by='date_time')
            out_DF = out_DF.drop('date_time', 1)
        out_DF.rename(columns = {'id':'input_id'}, inplace = True)
        return out_DF
            # return dict(response.json())['result']

    elif table_type=="Activity Summary":
        TableAPI = "http://khansadev.xyz/dome_api/rtdc/ActivitySummary/get_data"
        json_queries = json.dumps(
            {
            "wid": wid,
            "start" : start_date_time,
            "end" : end_date_time
            },
            indent = 4
        )
        response = (
            requests.get(
                TableAPI, data=json_queries
            )
        )
        # print((response.json()))

        ActivitySummary_DF = pd.DataFrame(dict(response.json())['result'])
        # print("TESSSSSSSSSS")
        # print(ActivitySummary_DF.empty)
        # print(list(ActivitySummary_DF.columns))
        if list(ActivitySummary_DF.columns) == []:
            ActivitySummary_DF = pd.DataFrame(columns=ColumnRenameDict.values())
        else:
            ActivitySummary_DF.rename(columns = ColumnRenameDict, inplace = True)
        ActivitySummary_DF[['Date', 'Start Time', 'End Time']] = ActivitySummary_DF[['Date', 'Start Time', 'End Time']].astype('datetime64') 
        list_float = ['Duration (Minutes)', 'Hole Depth (Max)', 'Bit Depth(mean)', 'Drilling Meterage (m)', 'Rotate Drilling (minutes)',
                     'Slide Drilling (minutes)', 'Reaming (minutes)', 'Connection (minutes)', 'On Bottom state (Hours)', 'Stand Duration',
                     'Total Stand Drilling Meterage (m)', 'Total Stand Duration (hrs)', 'Total On Bottom Duration (hrs)']

        ActivitySummary_DF[list_float] = ActivitySummary_DF[list_float].astype('float64') 

        # print(ActivitySummary_DF)
        return ActivitySummary_DF



     
def DomeGetData_v2(wid, start_date_time, end_date_time, table_type="Activity Log"):
    
    ColumnRenameDict = {'wid': 'wid',
                        'date': 'Date',
                        'time_start': 'Start Time',
                        'time_end': 'End Time',
                        'duration_minutes': 'Duration (Minutes)',
                        'label_subactivity': 'SUB-ACTIVITY',
                        'label_activity': 'ACTIVITY',
                        'stand_durationx': 'CONNECTION-ACTIVITY',
                        'hole_depth': 'Hole Depth (Max)',
                        'bit_depth': 'Bit Depth(mean)',
                        'meterage_drilling': 'Drilling Meterage (m)',
                        'rotate_drilling_time': 'Rotate Drilling Time (Minutes)',
                        'slide_drilling_time': 'Slide Drilling Time (Minutes)',
                        'reaming_time': 'Reaming Time (Minutes)',
                        'connection_time': 'Connection Time (Minutes)',
                        'on_bottom_hours': 'On Bottom state (hrs)',
                        'stand_duration': 'Total Stand Duration (hrs)',
                        'stand_meterage_drilling': 'Total Stand Drilling Meterage (m)',
                        'stand_group': 'Stand Group',
                        'pic': 'PIC',
                        'section': 'Section',
                        'remark': 'Remarks',
                        'stand_on_bottom': 'zeros'}
    ActivityLogColumnRenameDict = {
                            'id': 'id',
                            'dt': 'dt',
                            'date': 'date',
                            'time': 'time',
                            'activity': 'activity',
                            'in_slip_threshold': 'in_slip_threshold', 
                            'remarks': 'remarks',
                            'pic': 'pic',
                            'section': 'section'
                            }
    print("get " + table_type + " data/table from DOME")
    if table_type=="Activity Log":
        TableAPI = "http://khansadev.xyz/dome_api/rtdc/Activitylog/get_data"
        print(wid)
        json_queries = json.dumps(
            {
            "wid": wid,
            "start" : '2000-10-17 00:00:00',
            "end" : '2050-10-17 00:00:00',
            # "start" : start_date_time,
            # "end" : end_date_time
            },
            indent = 4
        )
        response = (
            requests.get(
                TableAPI, data=json_queries
            )
        )
        if (dict(response.json())['result']) == []:
            # print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
            # print(dict(response.json())['result'])
            out_DF = pd.DataFrame(columns=ActivityLogColumnRenameDict.values())
            # print(ActivityLog_DF)
            # return ActivityLog_DF.to_dict()
        else:
            out_DF = pd.DataFrame(dict(response.json())['result'])
    
            out_DF['date_time'] = pd.to_datetime(out_DF['date'] + " " + out_DF['time'])
            out_DF = out_DF.sort_values(by='date_time')
            out_DF = out_DF.drop('date_time', 1)
        out_DF.rename(columns = {'id':'input_id'}, inplace = True)
        return out_DF
            # return dict(response.json())['result']

    elif table_type=="Activity Summary":
        TableAPI = "http://khansadev.xyz/dome_api/rtdc/ActivitySummary/get_data"
        print(wid)
        json_queries = json.dumps(
            {
            "wid": wid,
            "start" : start_date_time,
            "end" : end_date_time
            },
            indent = 4
        )
        response = (
            requests.get(
                TableAPI, data=json_queries
            )
        )
        # print((response.json()))

        ActivitySummary_DF = pd.DataFrame(dict(response.json())['result'])
        # print("TESSSSSSSSSS")
        # print(ActivitySummary_DF.empty)
        if list(ActivitySummary_DF.columns) == []:
            ActivitySummary_DF['wid'] = wid
            ActivitySummary_DF = pd.DataFrame(columns=ColumnRenameDict.values())
        else:
            # ActivitySummary_DF.drop('on_bottom_hours', axis=1, inplace=True)
            ActivitySummary_DF['wid'] = wid
            ActivitySummary_DF.rename(columns = ColumnRenameDict, inplace = True)
            ActivitySummary_DF = ActivitySummary_DF[ColumnRenameDict.values()]
        # ActivitySummary_DF.drop('wid', axis=1, inplace=True)
        # st.dataframe(ActivitySummary_DF)
        ActivitySummary_DF[['Date', 'Start Time', 'End Time']] = ActivitySummary_DF[['Date', 'Start Time', 'End Time']].astype('datetime64') 
        
        list_float = ['Duration (Minutes)', 'Hole Depth (Max)', 'Bit Depth(mean)', 'Drilling Meterage (m)', 'Rotate Drilling Time (Minutes)',
                     'Slide Drilling Time (Minutes)', 'Reaming Time (Minutes)', 'Connection Time (Minutes)', 'On Bottom state (hrs)', 'Total Stand Duration (hrs)',
                     'Total Stand Drilling Meterage (m)']

        ActivitySummary_DF[list_float] = ActivitySummary_DF[list_float].astype('float64') 
        list_string = ["SUB-ACTIVITY","ACTIVITY","CONNECTION-ACTIVITY","PIC",
                        "Section","Remarks","Stand Group"]
        ActivitySummary_DF[list_string] = ActivitySummary_DF[list_string].astype('string') 
        # ActivitySummary_DF
        

        # print(ActivitySummary_DF)
        return ActivitySummary_DF



def DomeUpdateData(wid, dict_row):
    AddRowAPI = "http://khansadev.xyz/dome_api/rtdc/Activitylog/update"
    error_msg = ""
    keys_list = ["wid", "dt", "date", "time", "activity",
                        "in_slip_threshold", "remarks", "pic", "section", "id"]
    
    for keys_name in keys_list:
        if keys_name not in dict_row.keys():
            error_msg = error_msg + keys_name + ", "
    if error_msg == "":
        json_queries = json.dumps(
            dict_row,
            indent = 4
        )
        response = (
            requests.post(
                AddRowAPI, data=json_queries 
            )
        )
        
        return dict(response.json())
    else:
        return error_msg


def DomeDelete(wid, ID_or_timestart, table_type="Activity Log"):
    time.sleep(0.1)
    print("delete dome of " + table_type + " data/table from DOME")
    if table_type=="Activity Log":
        TableAPI = "http://khansadev.xyz/dome_api/rtdc/Activitylog/delete"

        json_queries = json.dumps(
            {
            "wid": wid,
            "id":ID_or_timestart
            },
            indent = 4
        )
        response = (
            requests.post(
                TableAPI, data=json_queries 
            )
        )
        # print("delete Activity Log data success")
    elif table_type=="Activity Summary":
        TableAPI = "http://khansadev.xyz/dome_api/rtdc/ActivitySummary/delete"

        json_queries = json.dumps(
            {
            "wid": wid,
            "time_start":ID_or_timestart
            },
            indent = 4
        )
        response = (
            requests.post(
                TableAPI, data=json_queries 
            )
        )
        # print(TableAPI)
        # print("delete Activity Summary data success")


def dict2DF(input_Dict):
    out_DF = pd.DataFrame(input_Dict)
    out_DF.rename(columns = {'id':'input_id'}, inplace = True)
    out_DF['date_time'] = pd.to_datetime(out_DF['date'] + " " + out_DF['time'])
    out_DF = out_DF.sort_values(by='date_time')
    out_DF = out_DF.drop('date_time', 1)
    # 'id':'input_id',
    return out_DF


def DF2list_dict(DF):
    DF.rename(columns = {'input_id':'id'}, inplace = True)
    out_dict = DF.to_dict("index")
    return list(out_dict.values())

def UploadActivitySummary(ActivitySummary_DF, wid):
    list_rename_column = {
    'wid':'wid',
    'Date':'date',
    'Start Time':'time_start',
    'End Time':'time_end',
    'Duration (Minutes)':'duration_minutes',
    'Hole Depth (Max)':'hole_depth',
    'Bit Depth(mean)':'bit_depth',
    'Drilling Meterage (m)':'meterage_drilling',
    'Rotate Drilling (minutes)':'rotate_drilling_time',
    'Slide Drilling (minutes)':'slide_drilling_time',
    'Reaming (minutes)':'reaming_time',
    'Connection (minutes)':'connection_time',
    'On Bottom state (Hours)':'on_bottom_hours',
    'Stand Duration':'stand_duration',
    'SUB-ACTIVITY':'label_subactivity',
    'ACTIVITY':'label_activity',
    'Total Stand Drilling Meterage (m)':'stand_meterage_drilling',
    'Total Stand Duration (hrs)':'stand_durationx',
    'Total On Bottom Duration (hrs)':'stand_on_bottom',
    "PIC":"pic",
    "Section":"section",
    "Remarks":"remark",
    'Stand Group_Pred':'stand_group',
    }

    ActivitySummary_DF.rename(columns = list_rename_column, inplace = True)
    ActivitySummary_DF['wid'] = wid



    # ActivitySummary_DF['time_start'] = pd.to_datetime(ActivitySummary_DF['date'].str.split(' ', expand=True)[0] + ' ' + ActivitySummary_DF['time_start']).dt.strftime('%Y-%m-%d %H:%M:%S')
    # ActivitySummary_DF['time_end'] = pd.to_datetime(ActivitySummary_DF['date'].str.split(' ', expand=True)[0] + ' ' + ActivitySummary_DF['time_end']).dt.strftime('%Y-%m-%d %H:%M:%S')

    ActivitySummary_DF['date'] = ActivitySummary_DF['date'].astype('datetime64').dt.strftime('%Y-%m-%d')


    list_float64_col = ["duration_minutes",
    "hole_depth",
    "bit_depth",
    "meterage_drilling",
    "rotate_drilling_time",
    "slide_drilling_time",
    "reaming_time",
    "connection_time",
    "on_bottom_hours",
    "stand_duration",
    "stand_durationx",

    ]

    list_string_col = ["label_subactivity",
    "label_activity",
    # "MERGE_SubActivity-Activity",
    "pic",
    "remark",
    "section",
    ]


    for string_col in list_string_col:
        ActivitySummary_DF[string_col] = ActivitySummary_DF[string_col].astype('string')

    for float64_col in list_float64_col:
        ActivitySummary_DF[float64_col] = ActivitySummary_DF[float64_col].astype('float64')

    ActivitySummary_DF[['label_subactivity','label_activity']] = ActivitySummary_DF[['label_subactivity','label_activity']].fillna('NaN')
    ActivitySummary_DF['stand_group'] = ActivitySummary_DF['stand_group'].fillna(999)

    list_dict_out = []
    # total_data = ActivitySummary_DF[list_rename_column.values()].shape[0]
    # i = 0
    for idx,row in ActivitySummary_DF[list_rename_column.values()].iterrows():
        # i = i + 1
        # st.progress(i/total_data)
        DomeAddData(row.to_dict(), table_type="Activity Summary")
        # list_dict_out.append(row.to_dict())

    # return list_dict_out
# def label2


def UploadActivitySummary_v2(ActivitySummary_DF, wid):
    list_rename_column = {
        'wid':'wid',
        'Date':'date',
        'Start Time':'time_start',
        'End Time':'time_end',
        'Duration (Minutes)':'duration_minutes',
        'Hole Depth (Max)':'hole_depth',
        'Bit Depth(mean)':'bit_depth',
        'Drilling Meterage (m)':'meterage_drilling',
        'Rotate Drilling Time (Minutes)':'rotate_drilling_time',
        'Slide Drilling Time (Minutes)':'slide_drilling_time',
        'Reaming Time (Minutes)':'reaming_time',
        'Connection Time (Minutes)':'connection_time',
        'On Bottom state (hrs)':'on_bottom_hours',
        'Total Stand Duration (hrs)':'stand_duration',
        'SUB-ACTIVITY':'label_subactivity',
        'ACTIVITY':'label_activity',
        'Total Stand Drilling Meterage (m)':'stand_meterage_drilling',
        'CONNECTION-ACTIVITY':'stand_durationx',
        "PIC":"pic",
        "Section":"section",
        "Remarks":"remark",
        'Stand Group':'stand_group',
        'zeros':'stand_on_bottom',
        }
    ActivitySummary_DF['zeros'] = 0


    ActivitySummary_DF.rename(columns = list_rename_column, inplace = True)
    ActivitySummary_DF['wid'] = wid



    # ActivitySummary_DF['time_start'] = pd.to_datetime(ActivitySummary_DF['date'].str.split(' ', expand=True)[0] + ' ' + ActivitySummary_DF['time_start']).dt.strftime('%Y-%m-%d %H:%M:%S')
    # ActivitySummary_DF['time_end'] = pd.to_datetime(ActivitySummary_DF['date'].str.split(' ', expand=True)[0] + ' ' + ActivitySummary_DF['time_end']).dt.strftime('%Y-%m-%d %H:%M:%S')

    ActivitySummary_DF['date'] = ActivitySummary_DF['date'].astype('datetime64').dt.strftime('%Y-%m-%d')
    ActivitySummary_DF['time_start'] = ActivitySummary_DF['time_start'].astype('string')
    ActivitySummary_DF['time_end'] = ActivitySummary_DF['time_end'].astype('string')


    list_float64_col = ["duration_minutes",
    "hole_depth",
    "bit_depth",
    "meterage_drilling",
    "rotate_drilling_time",
    "slide_drilling_time",
    "reaming_time",
    "connection_time",
    "on_bottom_hours",
    "stand_duration",

    ]

    list_string_col = ["label_subactivity",
    "label_activity",
    "stand_group",
    # "MERGE_SubActivity-Activity",
    "stand_durationx",
    "pic",
    "remark",
    "section",
    ]


    for string_col in list_string_col:
        ActivitySummary_DF.loc[:, string_col] = ActivitySummary_DF.loc[:, string_col].astype('string')

    for float64_col in list_float64_col:
        ActivitySummary_DF.loc[:, float64_col] = ActivitySummary_DF[float64_col].astype('float64')

    ActivitySummary_DF[['label_subactivity','label_activity']] = ActivitySummary_DF[['label_subactivity','label_activity']].fillna('NaN')
    ActivitySummary_DF['stand_group'] = ActivitySummary_DF['stand_group'].fillna("")

    list_dict_out = []
    # total_data = ActivitySummary_DF[list_rename_column.values()].shape[0]
    # i = 0
    for idx,row in ActivitySummary_DF[list_rename_column.values()].iterrows():
        time.sleep(0.1)
        # i = i + 1
        # st.progress(i/total_data)
        try:
            DomeAddData(row.to_dict(), table_type="Activity Summary")
        except:
            
            time.sleep(30)
            DomeAddData(row.to_dict(), table_type="Activity Summary")
        # list_dict_out.append(row.to_dict())

    # return list_dict_out
#



def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    # workbook = writer.book
    # worksheet = writer.sheets['ActivitySummary']
    # format1 = workbook.add_format({'num_format': '0.00'}) 
    # worksheet.set_column('A:A', None, format1)  
    writer.save()
    processed_data = output.getvalue()
    return processed_data




