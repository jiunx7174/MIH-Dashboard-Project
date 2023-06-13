import streamlit as st 

from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
import streamlit.components.v1 as components


def add_row_func():
    return """function(e) 
            { let api = e.api; 
            let rowIndex = e.rowIndex + 1; 
            
            let vnme = e.data.Name;
            let vage = e.data.Age;

            api.applyTransaction({addIndex: rowIndex, add: [{'Name': vnme, 'Age': vage}]}); 

            };"""


# def ActivityLogTable_Agrid(ActivityLog_DF):
#     gridOptions  = GridOptionsBuilder.from_dataframe(ActivityLog_DF)
#     gridOptions .configure_selection('multiple', use_checkbox=True)
#     ShowAddBtn = ('function addBtn(params) { return "<button style=background-color:green;>+</button>"; }')
#     gridOptions.configure_column('+', headerTooltip='Add new row', editable=False, filter=False, 
#                     onCellClicked=JsCode(add_row_func()), cellRenderer=JsCode(ShowAddBtn),
#                     autoHeight=True, wrapText=False, lockPosition='left', pinned='left', 
#                     sorteable=False, suppressMenu=True, maxWidth = 150)
#     gridOptions.configure_default_column(editable=True)
#     gb = gridOptions.build()
    
#     InputActivityGrid_response = AgGrid(
#         ActivityLog_DF, 
#         gridOptions=gb,
#         data_return_mode=DataReturnMode.FILTERED_AND_SORTED, 
#         update_mode=(GridUpdateMode.VALUE_CHANGED),
#         allow_unsafe_jscode=True,
#         reload_data =False)
#     return InputActivityGrid_response



def ActivityLogTable_Agrid(ActivityLog_DF, reload=False, ActivityList='default', SectionSizeList='default'):
    css = """
    .custom-rich-select-editor {
    display: inline-block;
    width: 100%;
    }

    .custom-rich-select-wrapper {
    position: relative;
    }

    .custom-rich-select {
    width: 100%;
    padding: 8px 16px;
    font-family: Arial;
    font-size: 14px;
    border: 1px solid #bdbdbd;
    border-radius: 4px;
    background-color: #fff;
    color: #333;
    }

    .custom-rich-select:focus {
    outline: none;
    border-color: #1976d2;
    }


    """
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

    # st.markdown(html_import, unsafe_allow_html=True)
    string_to_add_row = "\n\n function(e) { \n \
        let api = e.api; \n \
        let rowIndex = e.rowIndex + 1; \n \
        api.applyTransaction({addIndex: rowIndex, add: [{}]}); \n \
            }; \n \n"
    cell_button_add = JsCode('''
        class BtnAddCellRenderer {
            init(params) {
                this.params = params;
                this.eGui = document.createElement('div');
                this.eGui.innerHTML = `
                <span>
                    <style>
                    .btn_add {
                    background-color: limegreen;
                    border: none;
                    color: white;
                    text-align: center;
                    text-decoration: none;
                    display: inline-block;
                    font-size: 10px;
                    font-weight: bold;
                    height: 2.5em;
                    width: 8em;
                    cursor: pointer;
                    }

                    .btn_add :hover {
                    background-color: #05d588;
                    }
                    </style>
                    <button id='click-button' 
                        class="btn_add" 
                        >&CirclePlus; Add</button>
                </span>
            `;
            }

            getGui() {
                return this.eGui;
            }

        };
        ''')
    string_to_delete = "\n\n function(e) { \n \
        let api = e.api; \n \
        let sel = api.getSelectedRows(); \n \
        api.applyTransaction({remove: sel});\n\
    }; \n"
    
    cell_button_delete = ('''
        class BtnCellRenderer {
            init(params) {
                console.log(params.api.getSelectedRows());
                this.params = params;
                this.eGui = document.createElement('div');
                this.eGui.innerHTML = `
                <span>
                    <style>
                    .btn {
                    background-color: #F94721;
                    border: none;
                    color: white;
                    font-size: 10px;
                    font-weight: bold;
                    height: 2.5em;
                    width: 8em;
                    cursor: pointer;
                    }

                    .btn:hover {
                    background-color: #FB6747;
                    }
                    </style>
                    <button id='click-button'
                        class="btn"
                        >&#128465; Delete</button>
                </span>
            `;
            }

            getGui() {
                return this.eGui;
            }

        };
        ''')
    customCellEditor = JsCode(
        """
            class CustomRichSelectEditor {
            init(params) {
                this.params = params;
                this.options = params.values;
                this.eGui = document.createElement('div');
                this.eGui.className = 'custom-rich-select-editor';
                this.populateOptions();
                this.addClickHandler();
            }

            populateOptions() {
                const selectWrapper = document.createElement('div');
                selectWrapper.className = 'custom-rich-select-wrapper';

                const selectElement = document.createElement('select');
                selectElement.className = 'custom-rich-select';

                this.options.forEach((option) => {
                const optionElement = document.createElement('option');
                optionElement.value = option;
                optionElement.text = option;
                selectElement.appendChild(optionElement);
                });

                selectWrapper.appendChild(selectElement);
                this.eGui.appendChild(selectWrapper);
            }

            addClickHandler() {
                const selectElement = this.eGui.querySelector('.custom-rich-select');
                selectElement.addEventListener('change', () => {
                this.params.stopEditing();
                });
            }

            getGui() {
                return this.eGui;
            }

            afterGuiAttached() {
                const selectElement = this.eGui.querySelector('.custom-rich-select');
                selectElement.focus();
            }

            getValue() {
                const selectElement = this.eGui.querySelector('.custom-rich-select');
                return selectElement.value;
            }

            isPopup() {
                return true;
            }
            }
        """
    )

    if ActivityList  =='default':
        ActivityList = ["N/A",'CEMENTING JOB','CIRCULATE HOLE CLEANING','CONNECTION','DRILL OUT CEMENT','DRILLING FORMATION',
                        'LAY DOWN BHA','MAKE UP BHA','NPT','N/D BOP','N/U BOP','OTHER','RUNNING CASING IN','STATIONARY',
                        'STUCK PIPE','TRIP IN','TRIP OUT','WAIT ON CEMENT','CIRCULATION','RIG REPAIR','WIPER TRIP'
        ]
    if SectionSizeList == 'default':
        SectionSizeList=['26"','17-1/2"','12-1/4"','9-7/8"', '7-7/8"', '8.5"','6-3/4"', '6-1/8"','6"', ]
    gridOptions  = GridOptionsBuilder.from_dataframe(ActivityLog_DF.drop(columns=['id','DateTime']))
    # gridOptions  = GridOptionsBuilder.from_dataframe(ActivityLog_DF.drop(['DateTime'], 1))
    gridOptions.configure_selection('single')

    gridOptions.configure_column('Insert', headerTooltip='Click on Button to add new row', editable=False, filter=False,width=105,
                            onCellClicked=JsCode(string_to_add_row), cellRenderer=cell_button_add,
                            autoHeight=True, wrapText=True, suppressMovable='true')
    gridOptions.configure_column('Delete', headerTooltip='Click on Button to remove row',width=105,
                                    editable=False, filter=False, onCellClicked=JsCode(string_to_delete),
                                    cellRenderer=JsCode(cell_button_delete),
                                    autoHeight=True, suppressMovable='true',
                                    # checkboxSelection=True,
                                    )
    gridOptions.configure_column('Date', width=100, autoHeight=True, editable=True,
                                #  cellEditor=customDateEditor,
                                #  cellEditorPopup=True
                             )
    gridOptions.configure_column('Time', width=90, autoHeight=True, )
    gridOptions.configure_column('Activity', width=175, autoHeight=True, 
                                cellEditor=customCellEditor,
                                cellEditorPopup=True,
                                cellEditorParams={'values': ActivityList}
                                 )
    gridOptions.configure_column('Section Size', width=175, autoHeight=True, 
                                cellEditor=customCellEditor,
                                cellEditorPopup=True,
                                cellEditorParams={'values': SectionSizeList}
                                 )
    gridOptions.configure_column('In-Slip Threshold', width=120, autoHeaderHeight=True, wrapHeaderText=True,)
    gridOptions.configure_column('Remarks', width=200, autoHeight=True,cellEditorPopup=True, cellEditor='agLargeTextCellEditor',)
    gridOptions.configure_column('PIC', width=80, autoHeight=True, )


    gridOptions.configure_default_column(editable=True)
    gb = gridOptions.build()
    gb['pagination']=True
    # gb['autoSizeColumns ']=True
    InputActivityGrid_response = AgGrid(
        ActivityLog_DF, 
        height=450,
        gridOptions=gb,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED, 
        # update_mode=(GridUpdateMode.NO_UPDATE),
        update_mode=(GridUpdateMode.VALUE_CHANGED) | (GridUpdateMode.SELECTION_CHANGED) ,
        allow_unsafe_jscode=True,
        enable_enterprise_modules=False,
        reload_data =reload)
    return InputActivityGrid_response


def ActivityLogTableDatabase_Agrid(ActivityLog_DF, reload=False,):
    css = """
    .custom-rich-select-editor {
    display: inline-block;
    width: 100%;
    }

    .custom-rich-select-wrapper {
    position: relative;
    }

    .custom-rich-select {
    width: 100%;
    padding: 8px 16px;
    font-family: Arial;
    font-size: 14px;
    border: 1px solid #bdbdbd;
    border-radius: 4px;
    background-color: #fff;
    color: #333;
    }

    .custom-rich-select:focus {
    outline: none;
    border-color: #1976d2;
    }


    """
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)


    gridOptions  = GridOptionsBuilder.from_dataframe(ActivityLog_DF.drop(columns=['id','DateTime']))
    # gridOptions  = GridOptionsBuilder.from_dataframe(ActivityLog_DF.drop(['DateTime'], 1))
    # gridOptions.configure_selection('single')


    gridOptions.configure_column('Date', width=100, autoHeight=True,
                                #  cellEditor=customDateEditor,
                                #  cellEditorPopup=True
                             )
    gridOptions.configure_column('Time', width=90, autoHeight=True, )
    gridOptions.configure_column('Activity', width=175, autoHeight=True, 
                                 )
    gridOptions.configure_column('Section Size', width=175, autoHeight=True, 
                                 )
    gridOptions.configure_column('In-Slip Threshold', width=120, autoHeaderHeight=True, wrapHeaderText=True,)
    gridOptions.configure_column('Remarks', width=200, autoHeight=True,cellEditorPopup=True, cellEditor='agLargeTextCellEditor',)
    gridOptions.configure_column('PIC', width=80, autoHeight=True, )


    gridOptions.configure_default_column(editable=False)
    gb = gridOptions.build()
    gb['pagination']=True
    # gb['autoSizeColumns ']=True
    InputActivityGrid_response = AgGrid(
        ActivityLog_DF, 
        height=450,
        gridOptions=gb,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED, 
        update_mode=(GridUpdateMode.NO_UPDATE),
        # update_mode=(GridUpdateMode.VALUE_CHANGED) | (GridUpdateMode.SELECTION_CHANGED) ,
        allow_unsafe_jscode=True,
        enable_enterprise_modules=False,
        reload_data =reload)
    return InputActivityGrid_response

def datetime_renderer(params):
    value = params.value
    date_str = value.strftime("%Y-%m-%d")
    time_str = value.strftime("%H:%M:%S")
    formatted_value = f"<span style='font-style: italic;'>{date_str}</span><br><span style='font-weight: bold; font-size: 16px;'>{time_str}</span>"
    return formatted_value

def ActSumTable_Agrid(ActSum_DF, reload=False):
    # ActSum_DF = ActSumData.Data
    css = """
    .custom-rich-select-editor {
    display: inline-block;
    width: 100%;
    }

    .custom-rich-select-wrapper {
    position: relative;
    }

    .custom-rich-select {
    width: 100%;
    padding: 8px 16px;
    font-family: Arial;
    font-size: 14px;
    border: 1px solid #bdbdbd;
    border-radius: 4px;
    background-color: #fff;
    color: #333;
    }

    .custom-rich-select:focus {
    outline: none;
    border-color: #1976d2;
    }

    """
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)
    datetime_renderer = JsCode('''
    class DatetimeCellRenderer {
        init(params) {
            this.params = params;
            this.eGui = document.createElement('div');
            this.eGui.innerHTML = `
                <span>
                    <style>
                    .date {
                        font-style: oblique;
                        font-weight: lighter;
                        color: #696969;
                    //    font-size: larger;
                    }

                    .time {
                        font-weight: bolder;
                        color: #696969;
                    //    font-style: oblique;
                    }
                    </style>
                    <span class="date">${params.value.split(' ')[0]}</span>
                    <span class="time">${params.value.split(' ')[1]}</span>
                </span>
            `;
        }

        getGui() {
            return this.eGui;
        }
    }
    ''')
                               
    is_row_selectable = JsCode("function isRowSelectable(params) {\
                            if (params.data.status === 'FIRM') {\
                                return false;\
                            } else {\
                                return true;\
                            }\
                            }\
                        ")
    string_to_add_rowx = ("\n\n function(e) { \n \
    let api = e.api; \n \
    let rowIndex = e.rowIndex + 1; \n \
    let previousRowData = api.getDisplayedRowAtIndex(rowIndex - 1).data; \n \
    let newRowData = Object.assign({}, previousRowData); \n \
    api.applyTransaction({addIndex: rowIndex, add: [newRowData]}); \n \
        }; \n \n")
    string_to_add_row = ("\n\n function(e) { \n \
    let api = e.api; \n \
    let currentData = api.getDisplayedRowAtIndex(e.rowIndex).data; \n \
    if (currentData.status ==='REVIEW') {\
    let rowIndex = e.rowIndex + 1; \n \
    let previousRowData = api.getDisplayedRowAtIndex(rowIndex - 1).data; \n \
    let newRowData = Object.assign({}, previousRowData); \n \
    api.applyTransaction({addIndex: rowIndex, add: [newRowData]}); \n \
        };}; \n \n")

    cell_button_add = JsCode('''
    class BtnAddCellRenderer {
        init(params) {
            this.params = params;
            this.eGui = document.createElement('div');
            this.eGui.innerHTML = `
             <span>
                <style>
                .btn_add {
                  background-color: limegreen;
                  border: none;
                  color: white;
                  text-align: center;
                  text-decoration: none;
                  display: inline-block;
                  font-size: 10px;
                  height: 2.5em;
                  width: 8em;
                  cursor: pointer;
                }

                .btn_add :hover {
                  background-color: #05d588;
                }
                </style>
                <button id='click-button' 
                    class="btn_add" 
                    >&CirclePlus; Insert Row</button>
             </span>
          `;
        }

        getGui() {
            return this.eGui;
        }

    };
    ''')

    string_to_delete = "\n\n function(e) { \n \
        let api = e.api; \n \
        let sel = api.getSelectedRows(); \n \
        api.applyTransaction({remove: sel});\n\
    }; \n"
    
    status_style_code = JsCode("""
    function(params) {
        if (params.value === 'REVIEW') {
            return {
                'background-color': '#E9967A',
                'color': '#F8F8FF',

            };
        } else {
            return {
                'background-color': '#2E8B57',
                'color': '#F8F8FF',

            };
        }
    }
    """)
    highlight_style_code = JsCode("""
    function(params) {
        let api = params.api;
        let currentData = api.getDisplayedRowAtIndex(params.rowIndex).data;
        if (['FALSE/Check', 'Look and define'].includes(currentData.LABEL_SubActivity)) {
            return {
                'background-color': '#F0E68C',

            };
        } ;
    }
    """)
    customCellEditor = JsCode(
        """
            class CustomRichSelectEditor {
            init(params) {
                this.params = params;
                this.options = params.values;
                this.eGui = document.createElement('div');
                this.eGui.className = 'custom-rich-select-editor';
                this.populateOptions();
                this.addClickHandler();
            }

            populateOptions() {
                const selectWrapper = document.createElement('div');
                selectWrapper.className = 'custom-rich-select-wrapper';

                const selectElement = document.createElement('select');
                selectElement.className = 'custom-rich-select';

                this.options.forEach((option) => {
                const optionElement = document.createElement('option');
                optionElement.value = option;
                optionElement.text = option;
                selectElement.appendChild(optionElement);
                });

                selectWrapper.appendChild(selectElement);
                this.eGui.appendChild(selectWrapper);
            }

            addClickHandler() {
                const selectElement = this.eGui.querySelector('.custom-rich-select');
                selectElement.addEventListener('change', () => {
                this.params.stopEditing();
                });
            }

            getGui() {
                return this.eGui;
            }

            afterGuiAttached() {
                const selectElement = this.eGui.querySelector('.custom-rich-select');
                selectElement.focus();
            }

            getValue() {
                const selectElement = this.eGui.querySelector('.custom-rich-select');
                return selectElement.value;
            }

            isPopup() {
                return true;
            }
            }
        """
    )

    TripActivityList = [   'TRIP IN', 'TRIP OUT',   'WIPER TRIP']

    DrillActivityList = ["DRILLING FORMATION", 'CIRCULATE HOLE CLEANING','DRILL OUT CEMENT',]

    OverrideActivityList = ['CEMENTING JOB', 'CONNECTION', 'LAY DOWN BHA', 'MAKE UP BHA', 'NPT', 'N/D BOP', 
                                'N/U BOP', 'RUNNING CASING IN', 'STATIONARY', 'STUCK PIPE', 'WAIT ON CEMENT', 'RIG REPAIR',]
    
    DrillSubActivityList = ['Rotary Drilling','Slide Drilling','Reaming','Wash Up/Down','Connection']
    TripSubActivityList = ['Wash Up/Down','Reaming','Moving','Circulation','Connection','Stationary']

    customCellEditorParams = JsCode(
        f"""
        function(params) {{
        let api = params.api;
        let currentActivity = api.getDisplayedRowAtIndex(params.rowIndex).data.LABEL_Activity;
        if ({TripActivityList}.includes(currentActivity)) {{
            // Logic for List_A
            console.log('Current Activity is in List_A');
            // ... Additional code for List_A
            return {{values: {TripSubActivityList}}};
        }} else if ({DrillActivityList}.includes(currentActivity)) {{
            return {{values: {DrillSubActivityList}}};
        }} else {{
            return {{values: [currentActivity]}};
        }}


        }}
        """
    )

    cell_button_delete = JsCode('''
        class BtnCellRenderer {
            init(params) {
                console.log(params.api.getSelectedRows());
                this.params = params;
                this.eGui = document.createElement('div');
                this.eGui.innerHTML = `
                <span>
                    <style>
                    .btn {
                    background-color: #F94721;
                    border: none;
                    color: white;
                    font-size: 10px;
                    font-weight: bold;
                    height: 2.5em;
                    width: 8em;
                    cursor: pointer;
                    }

                    .btn:hover {
                    background-color: #FB6747;
                    }
                    </style>
                    <button id='click-button'
                        class="btn"
                        >&#128465; Delete</button>
                </span>
            `;
            }

            getGui() {
                return this.eGui;
            }

        };
        ''')

    gridOptions  = GridOptionsBuilder.from_dataframe(ActSum_DF)


    
    gridOptions.configure_default_column(editable=False, autoHeaderHeight=True, wrapHeaderText=True)

    gb = gridOptions.build()

    gb["columnDefs"] =([
        {"field":'status',                      "headerName":"Status", "width":80,'editable':False,"filter":True,"headerTooltip":"Activity Finalization Status",
                                                # 'headerCheckboxSelection': True,
                                                # 'checkboxSelection': True,
                                                # 'showDisabledCheckboxes':False,
                                                'cellStyle':status_style_code,
                                                },
        {"field":'StartDateTime',               "headerName":"Start", "width":160,'editable':True,"filter":True,"headerTooltip":"Date Time when the activity start \n(YYYY:MM:DD hh:mm:ss)",
                                                    "cellRenderer": datetime_renderer,'cellStyle':highlight_style_code,
                                                },
        {"field":'EndDateTime',                 "headerName":"End", "width":160,'editable':True,"filter":True,"headerTooltip":"Date Time when the activity end \n(YYYY:MM:DD hh:mm:ss)" ,
                                                "cellRenderer": datetime_renderer,'cellStyle':highlight_style_code,
                                                },
        {"field":'LABEL_Activity',              "headerName":"Activity", "width":180,'editable':False,"filter":True,"headerTooltip":"Major Activity",
                                                'cellStyle':highlight_style_code,
                                                },
        {"field":'LABEL_SubActivity',           "headerName":"SubActivity", "width":140,'editable':'(params) => params.data.status == "REVIEW"',"filter":True,
                                                'editable':True,
                                                "headerTooltip":"SubActivity",
                                                'cellStyle':highlight_style_code,
                                                'cellEditor':customCellEditor,
                                                'cellEditorPopup':True,
                                                'cellEditorParams':customCellEditorParams
                                                # 'cellEditorParams':{'values': DrillSubActivityList}

                                                },
        {"field":'LABEL_ConnectionActivity',    "headerName":"Connection Activity", "width":90,'editable':True,"filter":True,"headerTooltip":"Date Time when the activity start"},
        {"headerName": "Activity Duration","width":200,
         "children":[
            {"field":'Duration',                    "headerName":"Duration (Minutes)","width":170, 'editable':False,"filter":True,"headerTooltip":"Minutes",'columnGroupShow': 'closed',},
            {"field":'Duration',                    "headerName":"Duration (Minutes)","width":100, 'editable':False,"filter":True,"headerTooltip":"Minutes",'columnGroupShow': 'open',},
            {"field":'RotateDrillingDuration',  "headerName":"Rotate Drilling Duration","width":95,'editable':False,"filter":False,"headerTooltip":"Minutes",'columnGroupShow': 'open',},
            {"field":'SlideDrillingDuration',   "headerName":"Slide Drilling Duration","width":95,'editable':False,"filter":False,"headerTooltip":"Minutes",'columnGroupShow': 'open',},
            {"field":'ReamingDuration',         "headerName":"Reaming Duration","width":95,'editable':False,"filter":False,"headerTooltip":"Minutes",'columnGroupShow': 'open',},
            {"field":'ConnectionDuration',      "headerName":"Connection Duration","width":105,'editable':False,"filter":False,"headerTooltip":"Minutes",'columnGroupShow': 'open',},
         ]},
        {"headerName": "Activity Meterage",
         "children":[
            {'field':'DrillingMeterage',        "headerName":"Drilling Meterage","width":170,'editable':False,"filter":True,"headerTooltip":"(Meter)",'columnGroupShow': 'closed',},
            {'field':'DrillingMeterage',        "headerName":"Drilling Meterage","width":95,'editable':False,"filter":True,"headerTooltip":"(Meter)",'columnGroupShow': 'open',},
            {'field':'Hole_Depth_max',          "headerName":"Hole Depth","width":90,'editable':False,"filter":True,"headerTooltip":"Max. (Meter)",'columnGroupShow': 'open',},
            {'field':'Bit_Depth_avg',           "headerName":"Bit Depth","width":90,'editable':False,"filter":True,"headerTooltip":"Avg. (Meter)",'columnGroupShow': 'open',},
         ]},

        {"headerName": "Stand Duration & Meterage",'columnGroupShow': 'closed',
         "children":[
            {"field":'Stand Group_Pred',            "headerName":"Stand Number","width":150,'editable':False,"filter":True,'columnGroupShow': 'closed',},
            {"field":'Stand Group_Pred',            "headerName":"Stand Number","width":100,'editable':False,"filter":True,'columnGroupShow': 'open',},
            {"field":'OnBottomDurationPerStand',    "headerName":"On Bottom Duration (Minutes)","width":100,'editable':False,"filter":True,"headerTooltip":"Minutes",'columnGroupShow': 'open',},
            {"field":'StandDuration',               "headerName":"Stand Duration (Minutes)","width":100,'editable':False,"filter":True,"headerTooltip":"Minutes",'columnGroupShow': 'open',},
            {"field":'DrillingMeteragePerStand',    "headerName":"Drilling Meterage per stand (Minutes)",'editable':False,"filter":False,"headerTooltip":"Minutes",'columnGroupShow': 'open',},
         ]},

        {"field":'Insert', 
            "headerTooltip":'Click on Button to add new row',
            'editable':False,
            "filter":False,
            "onCellClicked":JsCode(string_to_add_row), 
            "cellRenderer":cell_button_add,
            "autoHeight":True, 
            "wrapText":True, 
            "suppressMovable":True,
            "width":110,
            'pinned': 'right',
        },
        {"field":'Delete',
            "headerTooltip":'Click on Button to remove row',
            "editable":False, 
            "filter":False, 
            "onCellClicked":JsCode(string_to_delete),
            "cellRenderer":cell_button_delete,
            "autoHeight":True, 
            "width":110,
            'pinned': 'right',
        }
    ]
        
        )
    gb['rowSelection']='single'
    gb['isRowSelectable']=is_row_selectable
    gb['tooltipShowDelay']=800
    gb['enableRangeSelection']= True
    # gb['rowStyle']=row_style_code
    gb['alwaysShowHorizontalScroll']=True
    gb['alwaysShowVerticalScroll']=True
    gb['pagination']=True
    gb['paginationPageSize']=20
    # gb['rowClassRules']=row_style_code_2

    # gb['getRowId'] ='StartDateTime'
    # gridOptions_dict = {
    # 'alwaysShowHorizontalScroll': True,
    # 'alwaysShowVerticalScroll': True,
    # # 'pagination': True,
    # # 'paginationPageSize': 15,
    # }
    # for keys in gridOptions_dict.keys():
    #     gb[keys] = gridOptions_dict[keys]

    InputActSumGrid_response = AgGrid(
        ActSum_DF, 
        gridOptions=gb,
        # height="100%",
        fit_columns_on_grid_load =True,
        # width=1300,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED, 
        # update_mode=(GridUpdateMode.NO_UPDATE),
        update_mode=(GridUpdateMode.VALUE_CHANGED) | (GridUpdateMode.SELECTION_CHANGED) ,
        allow_unsafe_jscode=True,
        enable_enterprise_modules=False,
        # on_ready=preselect_rows,
        # preselected_rows=[24,25],
        # on_edit_done=disable_checkboxes,
        reload_data =reload)
    return InputActSumGrid_response

def ActSumTableDatabase_Agrid(ActSum_DF, reload=False):
    # ActSum_DF = ActSumData.Data
    css = """
    .custom-rich-select-editor {
    display: inline-block;
    width: 100%;
    }

    .custom-rich-select-wrapper {
    position: relative;
    }

    .custom-rich-select {
    width: 100%;
    padding: 8px 16px;
    font-family: Arial;
    font-size: 14px;
    border: 1px solid #bdbdbd;
    border-radius: 4px;
    background-color: #fff;
    color: #333;
    }

    .custom-rich-select:focus {
    outline: none;
    border-color: #1976d2;
    }

    """
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)
    datetime_renderer = JsCode('''
    class DatetimeCellRenderer {
        init(params) {
            this.params = params;
            this.eGui = document.createElement('div');
            this.eGui.innerHTML = `
                <span>
                    <style>
                    .date {
                        font-style: oblique;
                        font-weight: lighter;
                        color: #696969;
                    //    font-size: larger;
                    }

                    .time {
                        font-weight: bolder;
                        color: #696969;
                    //    font-style: oblique;
                    }
                    </style>
                    <span class="date">${params.value.split(' ')[0]}</span>
                    <span class="time">${params.value.split(' ')[1]}</span>
                </span>
            `;
        }

        getGui() {
            return this.eGui;
        }
    }
    ''')

    status_style_code = JsCode("""
    function(params) {
        if (params.value === 'REVIEW') {
            return {
                'background-color': '#E9967A',
                'color': '#F8F8FF',

            };
        } else {
            return {
                'background-color': '#2E8B57',
                'color': '#F8F8FF',

            };
        }
    }
    """)
    highlight_style_code = JsCode("""
    function(params) {
        let api = params.api;
        let currentData = api.getDisplayedRowAtIndex(params.rowIndex).data;
        if (['FALSE/Check', 'Look and define'].includes(currentData.LABEL_SubActivity)) {
            return {
                'background-color': '#F0E68C',

            };
        } ;
    }
    """)

    gridOptions  = GridOptionsBuilder.from_dataframe(ActSum_DF)


    
    gridOptions.configure_default_column(editable=False, autoHeaderHeight=True, wrapHeaderText=True)

    gb = gridOptions.build()

    gb["columnDefs"] =([
        {"field":'status',                      "headerName":"Status", "width":160,'editable':False,"filter":True,"headerTooltip":"Activity Finalization Status",
                                                'headerCheckboxSelection': True,
                                                'checkboxSelection': True,
                                                # 'showDisabledCheckboxes':False,
                                                'cellStyle':status_style_code,
                                                },
        {"field":'StartDateTime',               "headerName":"Start", "width":160,'editable':False,"filter":True,"headerTooltip":"Date Time when the activity start \n(YYYY:MM:DD hh:mm:ss)",
                                                    "cellRenderer": datetime_renderer,'cellStyle':highlight_style_code,
                                                },
        {"field":'EndDateTime',                 "headerName":"End", "width":160,'editable':False,"filter":True,"headerTooltip":"Date Time when the activity end \n(YYYY:MM:DD hh:mm:ss)" ,
                                                "cellRenderer": datetime_renderer,'cellStyle':highlight_style_code,
                                                },
        {"field":'LABEL_Activity',              "headerName":"Activity", "width":180,'editable':False,"filter":True,"headerTooltip":"Major Activity",
                                                'cellStyle':highlight_style_code,
                                                },
        {"field":'LABEL_SubActivity',           "headerName":"SubActivity", "width":140,'editable':False,"filter":True,
                                                'editable':True,
                                                "headerTooltip":"SubActivity",
                                                'cellStyle':highlight_style_code,
                                                # 'cellEditor':customCellEditor,
                                                # 'cellEditorPopup':True,
                                                # 'cellEditorParams':customCellEditorParams
                                                # 'cellEditorParams':{'values': DrillSubActivityList}

                                                },
        {"field":'LABEL_ConnectionActivity',    "headerName":"Connection Activity", "width":140,'editable':False,"filter":True,"headerTooltip":"Date Time when the activity start"},
        {"headerName": "Activity Duration","width":200,
         "children":[
            {"field":'Duration',                    "headerName":"Duration (Minutes)","width":170, 'editable':False,"filter":True,"headerTooltip":"Minutes",'columnGroupShow': 'closed',},
            {"field":'Duration',                    "headerName":"Duration (Minutes)","width":100, 'editable':False,"filter":True,"headerTooltip":"Minutes",'columnGroupShow': 'open',},
            {"field":'RotateDrillingDuration',  "headerName":"Rotate Drilling Duration","width":95,'editable':False,"filter":False,"headerTooltip":"Minutes",'columnGroupShow': 'open',},
            {"field":'SlideDrillingDuration',   "headerName":"Slide Drilling Duration","width":95,'editable':False,"filter":False,"headerTooltip":"Minutes",'columnGroupShow': 'open',},
            {"field":'ReamingDuration',         "headerName":"Reaming Duration","width":95,'editable':False,"filter":False,"headerTooltip":"Minutes",'columnGroupShow': 'open',},
            {"field":'ConnectionDuration',      "headerName":"Connection Duration","width":105,'editable':False,"filter":False,"headerTooltip":"Minutes",'columnGroupShow': 'open',},
         ]},
        {"headerName": "Activity Meterage",
         "children":[
            {'field':'DrillingMeterage',        "headerName":"Drilling Meterage","width":170,'editable':False,"filter":True,"headerTooltip":"(Meter)",'columnGroupShow': 'closed',},
            {'field':'DrillingMeterage',        "headerName":"Drilling Meterage","width":95,'editable':False,"filter":True,"headerTooltip":"(Meter)",'columnGroupShow': 'open',},
            {'field':'Hole_Depth_max',          "headerName":"Hole Depth","width":90,'editable':False,"filter":True,"headerTooltip":"Max. (Meter)",'columnGroupShow': 'open',},
            {'field':'Bit_Depth_avg',           "headerName":"Bit Depth","width":90,'editable':False,"filter":True,"headerTooltip":"Avg. (Meter)",'columnGroupShow': 'open',},
         ]},

        {"headerName": "Stand Duration & Meterage",'columnGroupShow': 'closed',
         "children":[
            {"field":'Stand Group_Pred',            "headerName":"Stand Number","width":150,'editable':False,"filter":True,'columnGroupShow': 'closed',},
            {"field":'Stand Group_Pred',            "headerName":"Stand Number","width":100,'editable':False,"filter":True,'columnGroupShow': 'open',},
            {"field":'OnBottomDurationPerStand',    "headerName":"On Bottom Duration (Minutes)","width":100,'editable':False,"filter":True,"headerTooltip":"Minutes",'columnGroupShow': 'open',},
            {"field":'StandDuration',               "headerName":"Stand Duration (Minutes)","width":100,'editable':False,"filter":True,"headerTooltip":"Minutes",'columnGroupShow': 'open',},
            {"field":'DrillingMeteragePerStand',    "headerName":"Drilling Meterage per stand (Minutes)",'editable':False,"filter":False,"headerTooltip":"Minutes",'columnGroupShow': 'open',},
         ]},

    ]
        
        )
    gb['rowSelection']='multiple'
    # gb['isRowSelectable']=is_row_selectable
    gb['tooltipShowDelay']=800
    gb['enableRangeSelection']= True
    # gb['rowStyle']=row_style_code
    gb['alwaysShowHorizontalScroll']=True
    gb['alwaysShowVerticalScroll']=True
    gb['pagination']=True
    gb['paginationPageSize']=20
    # gb['rowClassRules']=row_style_code_2

    # gb['getRowId'] ='StartDateTime'
    # gridOptions_dict = {
    # 'alwaysShowHorizontalScroll': True,
    # 'alwaysShowVerticalScroll': True,
    # # 'pagination': True,
    # # 'paginationPageSize': 15,
    # }
    # for keys in gridOptions_dict.keys():
    #     gb[keys] = gridOptions_dict[keys]

    InputActSumGrid_response = AgGrid(
        ActSum_DF, 
        gridOptions=gb,
        # height="100%",
        fit_columns_on_grid_load =True,
        # width=1300,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED, 
        # update_mode=(GridUpdateMode.NO_UPDATE),
        update_mode=(GridUpdateMode.SELECTION_CHANGED) ,
        allow_unsafe_jscode=True,
        enable_enterprise_modules=False,
        # on_ready=preselect_rows,
        # preselected_rows=[24,25],
        # on_edit_done=disable_checkboxes,
        reload_data =reload)
    return InputActSumGrid_response


def ActSumTableConfirmation_Agrid(ActSum_DF, reload=False, showWarning=False):
    # ActSum_DF = ActSumData.Data
    datetime_renderer = JsCode('''
    class DatetimeCellRenderer {
        init(params) {
            this.params = params;
            this.eGui = document.createElement('div');
            this.eGui.innerHTML = `
                <span>
                    <style>
                    .date {
                        font-style: oblique;
                        font-weight: lighter;
                        color: #696969;
                    //    font-size: larger;
                    }

                    .time {
                        font-weight: bolder;
                        color: #696969;
                    //    font-style: oblique;
                    }
                    </style>
                    <span class="date">${params.value.split(' ')[0]}</span>
                    <span class="time">${params.value.split(' ')[1]}</span>
                </span>
            `;
        }

        getGui() {
            return this.eGui;
        }
    }
    ''')
    
    gridOptions  = GridOptionsBuilder.from_dataframe(ActSum_DF)

    gridOptions.configure_default_column(editable=False, autoHeaderHeight=True, autoHeight=True, wrapHeaderText=True)
    gb = gridOptions.build()

    
    ColumnDefs = ([
        {"field":'status',                      "headerName":"Status", "width":130,'editable':False,"filter":True,"headerTooltip":"Activity Finalization Status",                                                
                                                },
        {"field":'StartDateTime',               "headerName":"Start", "width":140,'editable':False,"filter":True,"headerTooltip":"Date Time when the activity start \n(YYYY:MM:DD hh:mm:ss)","cellRenderer": datetime_renderer},
        {"field":'EndDateTime',                 "headerName":"End", "width":140,'editable':False,"filter":True,"headerTooltip":"Date Time when the activity end \n(YYYY:MM:DD hh:mm:ss)" ,"cellRenderer": datetime_renderer},
        {"field":'LABEL_Activity',              "headerName":"Activity", "width":160,'editable':False,"filter":True,"headerTooltip":"Major Activity"},
        {"field":'LABEL_SubActivity',           "headerName":"SubActivity", "width":140,'editable':False,"filter":True,"headerTooltip":"SubActivity"},
        {"field":'LABEL_ConnectionActivity',    "headerName":"Connection Activity", "width":90,'editable':False,"filter":True,"headerTooltip":"Date Time when the activity start"},
        {"headerName": "Activity Duration","width":200,
         "children":[
            {"field":'Duration',                    "headerName":"Duration (Minutes)","width":170, 'editable':False,"filter":True,"headerTooltip":"Minutes",'columnGroupShow': 'closed',},
            {"field":'Duration',                    "headerName":"Duration (Minutes)","width":100, 'editable':False,"filter":True,"headerTooltip":"Minutes",'columnGroupShow': 'open',},
            {"field":'RotateDrillingDuration',  "headerName":"Rotate Drilling Duration","width":95,'editable':False,"filter":False,"headerTooltip":"Minutes",'columnGroupShow': 'open',},
            {"field":'SlideDrillingDuration',   "headerName":"Slide Drilling Duration","width":95,'editable':False,"filter":False,"headerTooltip":"Minutes",'columnGroupShow': 'open',},
            {"field":'ReamingDuration',         "headerName":"Reaming Duration","width":95,'editable':False,"filter":False,"headerTooltip":"Minutes",'columnGroupShow': 'open',},
            {"field":'ConnectionDuration',      "headerName":"Connection Duration","width":105,'editable':False,"filter":False,"headerTooltip":"Minutes",'columnGroupShow': 'open',},
         ]},
        {"headerName": "Activity Meterage",
         "children":[
            {'field':'DrillingMeterage',        "headerName":"Drilling Meterage","width":170,'editable':False,"filter":True,"headerTooltip":"(Meter)",'columnGroupShow': 'closed',},
            {'field':'DrillingMeterage',        "headerName":"Drilling Meterage","width":95,'editable':False,"filter":True,"headerTooltip":"(Meter)",'columnGroupShow': 'open',},
            {'field':'Hole_Depth_max',          "headerName":"Hole Depth","width":90,'editable':False,"filter":True,"headerTooltip":"Max. (Meter)",'columnGroupShow': 'open',},
            {'field':'Bit_Depth_avg',           "headerName":"Bit Depth","width":90,'editable':False,"filter":True,"headerTooltip":"Avg. (Meter)",'columnGroupShow': 'open',},
         ]},

        {"headerName": "Stand Duration & Meterage",'columnGroupShow': 'closed',
         "children":[
            {"field":'Stand Group_Pred',            "headerName":"Stand Number","width":150,'editable':False,"filter":True,'columnGroupShow': 'closed',},
            {"field":'Stand Group_Pred',            "headerName":"Stand Number","width":100,'editable':False,"filter":True,'columnGroupShow': 'open',},
            {"field":'OnBottomDurationPerStand',    "headerName":"On Bottom Duration (Minutes)","width":100,'editable':False,"filter":True,"headerTooltip":"Minutes",'columnGroupShow': 'open',},
            {"field":'StandDuration',               "headerName":"Stand Duration (Minutes)","width":100,'editable':False,"filter":True,"headerTooltip":"Minutes",'columnGroupShow': 'open',},
            {"field":'DrillingMeteragePerStand',    "headerName":"Drilling Meterage per stand (Minutes)",'editable':False,"filter":False,"headerTooltip":"Minutes",'columnGroupShow': 'open',},
         ]},

        # {"field":'Insert', 
        #     "headerTooltip":'Click on Button to add new row',
        #     'editable':False,
        #     "filter":False,
        #     "onCellClicked":JsCode(string_to_add_row), 
        #     "cellRenderer":cell_button_add,
        #     "autoHeight":True, 
        #     "wrapText":True, 
        #     "suppressMovable":True,
        #     "width":110,
        #     'pinned': 'right',
        # },
        # {"field":'Delete',
        #     "headerTooltip":'Click on Button to remove row',
        #     "editable":False, 
        #     "filter":False, 
        #     "onCellClicked":JsCode(string_to_delete),
        #     "cellRenderer":cell_button_delete,
        #     "autoHeight":True, 
        #     "width":110,
        #     'pinned': 'right',
        # }
    ]
        
        )
    if showWarning:
        highlight_style_code = JsCode("""
        function(params) {
            let api = params.api;
            let currentData = api.getDisplayedRowAtIndex(params.rowIndex).data;
            if (null !== (currentData.ErrorWarning)) {
                return {
                    'background-color': '#F0E68C',
                };
            } ;
        }
        """)
        ColumnDefsWarning = [{"field":'ErrorWarning',"headerName":"Error Warning", "width":100,'editable':False,"filter":True,
          "headerTooltip":"Please revise the inputed row",'cellStyle':highlight_style_code,}]
    else:
        ColumnDefsWarning = []
    gb["columnDefs"] = ColumnDefsWarning + ColumnDefs
    gb['tooltipShowDelay']=100
    # gb['alwaysShowHorizontalScroll']=False
    # gb['alwaysShowVerticalScroll']=True
    gb['pagination']=True
    # gb['paginationPageSize']=15
    # gridOptions_dict = {
    # 'alwaysShowHorizontalScroll': True,
    # 'alwaysShowVerticalScroll': True,
    # # 'pagination': True,
    # # 'paginationPageSize': 15,
    # }
    # for keys in gridOptions_dict.keys():
    #     gb[keys] = gridOptions_dict[keys]

    InputActSumGrid_response = AgGrid(
        ActSum_DF, 
        gridOptions=gb,
        height=400,
        fit_columns_on_grid_load =True,
        width=1300,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED, 
        # update_mode=(GridUpdateMode.NO_UPDATE),
        update_mode=(GridUpdateMode.VALUE_CHANGED) | (GridUpdateMode.SELECTION_CHANGED) ,
        allow_unsafe_jscode=True,
        # on_ready=preselect_rows,
        # preselected_rows=[24,25],
        # on_edit_done=disable_checkboxes,
        reload_data =reload)
    return InputActSumGrid_response

# df=pd.DataFrame({ "Name": ['Erica', 'Rogers', 'Malcolm', 'Barrett'], "Age": [43, 35, 57, 29]})


#     gridOptions = GridOptionsBuilder.from_dataframe(df)
#     gb = gridOptions.build()

#     dta = AgGrid(df, gridOptions=gb, height=350, allow_unsafe_jscode=True, theme="blue",
#                 update_mode=GridUpdateMode.VALUE_CHANGED | GridUpdateMode.SELECTION_CHANGED | GridUpdateMode.FILTERING_CHANGED | GridUpdateMode.SORTING_CHANGED)
#     st.text(dta)