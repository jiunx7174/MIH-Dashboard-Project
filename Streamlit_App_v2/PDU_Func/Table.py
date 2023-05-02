import streamlit as st 

from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode



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
    st.markdown("""
    <style>
    /* Make agRichSelectCellEditor popup opaque */
    .ag-rich-select-value.ag-cell-edit-input.ag-input-field-focus {
        background-color: white;
        opacity: 1 !important;
        box-shadow: 0 2px 5px rgba(0,0,0,.26),0 2px 10px rgba(0,0,0,.16);
    }
    </style>
    """, unsafe_allow_html=True)
    string_to_add_row = ("\n\n function(e) { \n \
    let api = e.api; \n \
    let rowIndex = e.rowIndex + 1; \n \
    let previousRowData = api.getDisplayedRowAtIndex(rowIndex - 1).data; \n \
    let newRowData = Object.assign({}, previousRowData); \n \
    api.applyTransaction({addIndex: rowIndex, add: [newRowData]}); \n \
        }; \n \n")
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
    string_to_delete =('''\n\n function(e) { \n \
        let api = e.api; \n \
        let sel = api.getSelectedRows(); \n \
        api.applyTransaction({remove: sel}); \n \
        };''')
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

    if ActivityList  =='default':
        ActivityList = ["N/A",'CEMENTING JOB','CIRCULATE HOLE CLEANING','CONNECTION','DRILL OUT CEMENT','DRILLING FORMATION',
                        'LAY DOWN BHA','MAKE UP BHA','NPT','N/D BOP','N/U BOP','OTHER','RUNNING CASING IN','STATIONARY',
                        'STUCK PIPE','TRIP IN','TRIP OUT','WAIT ON CEMENT','CIRCULATION','RIG REPAIR','WIPER TRIP'
        ]
    if SectionSizeList == 'default':
        SectionSizeList=['26"','17-1/2"','12-1/4"','9-3/4"']
    gridOptions  = GridOptionsBuilder.from_dataframe(ActivityLog_DF.drop(columns=['id','DateTime']))
    # gridOptions  = GridOptionsBuilder.from_dataframe(ActivityLog_DF.drop(['DateTime'], 1))
    gridOptions.configure_selection('multi')

    gridOptions.configure_column('Insert', headerTooltip='Click on Button to add new row', editable=False, filter=False,width=105,
                            onCellClicked=JsCode(string_to_add_row), cellRenderer=cell_button_add,
                            autoHeight=True, wrapText=True, suppressMovable='true')
    gridOptions.configure_column('Delete', headerTooltip='Click on Button to remove row',width=105,
                                    editable=False, filter=False, onCellClicked=JsCode(string_to_delete),
                                    cellRenderer=cell_button_delete,
                                    autoHeight=True, )
    gridOptions.configure_column('Date', width=100, autoHeight=True, editable=True,
                             )
    gridOptions.configure_column('Time', width=90, autoHeight=True, )
    gridOptions.configure_column('Activity', width=175, autoHeight=True, 
                                cellEditor='agRichSelectCellEditor',
                                cellEditorPopup=True,
                                cellEditorParams={'values': ActivityList}
                                 )
    gridOptions.configure_column('Section Size', width=175, autoHeight=True, 
                                cellEditor='agRichSelectCellEditor',
                                cellEditorPopup=True,
                                cellEditorParams={'values': SectionSizeList}
                                 )
    gridOptions.configure_column('In-Slip Threshold', width=120, autoHeaderHeight=True, wrapHeaderText=True,)
    gridOptions.configure_column('Remarks', width=200, autoHeight=True,cellEditorPopup=True, cellEditor='agLargeTextCellEditor',)
    gridOptions.configure_column('PIC', width=80, autoHeight=True, )


    gridOptions.configure_default_column(editable=True)
    gb = gridOptions.build()
    gb['autoSizeColumns ']=True
    InputActivityGrid_response = AgGrid(
        ActivityLog_DF, 
        height=450,
        gridOptions=gb,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED, 
        # update_mode=(GridUpdateMode.NO_UPDATE),
        update_mode=(GridUpdateMode.VALUE_CHANGED) | (GridUpdateMode.SELECTION_CHANGED) ,
        allow_unsafe_jscode=True,
        reload_data =reload)
    return InputActivityGrid_response


# def is_row_selectable(params):
#     if params['data']['Status'] == 'FIRM':
#         return False
#     else:
#         return True
def ActSumTable_Agrid(ActSumData, reload=False):
    ActSum_DF = ActSumData.Data
    is_row_selectable = JsCode("function isRowSelectable(params) {\
                            if (params.data.status === 'FIRM') {\
                                return false;\
                            } else {\
                                return true;\
                            }\
                            }\
                        ")
    string_to_add_row = ("\n\n function(e) { \n \
    let api = e.api; \n \
    let rowIndex = e.rowIndex + 1; \n \
    let previousRowData = api.getDisplayedRowAtIndex(rowIndex - 1).data; \n \
    let newRowData = Object.assign({}, previousRowData); \n \
    api.applyTransaction({addIndex: rowIndex, add: [newRowData]}); \n \
        }; \n \n")

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
    string_to_delete =('''\n\n function(e) { \n \
        let api = e.api; \n \
        let sel = api.getSelectedRows(); \n \
        api.applyTransaction({remove: sel}); \n \
        };''')
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
    # gridOptions  = GridOptionsBuilder.from_dataframe(ActivityLog_DF.drop(['DateTime'], 1))
    gridOptions.configure_selection('multiple')


    # gridOptions.configure_column('Insert', headerTooltip='Click on Button to add new row', editable=False, filter=False,
    #                         onCellClicked=JsCode(string_to_add_row), cellRenderer=cell_button_add,
    #                         autoHeight=True, wrapText=True, suppressMovable='true')
    # gridOptions.configure_column('Delete', headerTooltip='Click on Button to remove row',
    #                                 editable=False, filter=False, onCellClicked=JsCode(string_to_delete),
    #                                 cellRenderer=cell_button_delete,
    #                                 autoHeight=True, )
    # gridOptions.configure_column('Delete', headerTooltip='Click on Button to remove row',
    #                                 editable=False, filter=False, onCellClicked=JsCode(string_to_delete),
    #                                 cellRenderer=cell_button_delete,
    #                                 autoHeight=True, )
    
    gridOptions.configure_default_column(editable=False, autoHeaderHeight=True, autoHeight=True, wrapHeaderText=True)
    gb = gridOptions.build()
    gb["columnDefs"] =([
        {"field":'status',                      "headerName":"Status", "width":120,'editable':False,"filter":True,"headerTooltip":"Activity Finalization Status",
                                                'headerCheckboxSelection': True,
                                                'checkboxSelection': True,
                                                'showDisabledCheckboxes':False,
                                                },
        {"field":'StartDateTime',               "headerName":"Start", "width":140,'editable':True,"filter":True,"headerTooltip":"Date Time when the activity start",},
        {"field":'EndDateTime',                 "headerName":"End", "width":140,'editable':True,"filter":True,"headerTooltip":"Date Time when the activity start"},
        {"field":'LABEL_Activity',              "headerName":"Activity", "width":160,'editable':False,"filter":True,"headerTooltip":"Major Activity"},
        {"field":'LABEL_SubActivity',           "headerName":"SubActivity", "width":140,'editable':True,"filter":True,"headerTooltip":"SubActivity"},
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
        },
        {"field":'Delete',
            "headerTooltip":'Click on Button to remove row',
            "editable":False, 
            "filter":False, 
            "onCellClicked":JsCode(string_to_delete),
            "cellRenderer":cell_button_delete,
            "autoHeight":True, 
            "width":110,
        }
    ]
        
        )
    gb['isRowSelectable']=is_row_selectable
    gb['tooltipShowDelay']=100
    gridOptions_dict = {
    'alwaysShowHorizontalScroll': True,
    'alwaysShowVerticalScroll': True,
    # 'pagination': True,
    # 'paginationPageSize': 15,
    }
    for keys in gridOptions_dict.keys():
        gb[keys] = gridOptions_dict[keys]
    
    InputActSumGrid_response = AgGrid(
        ActSum_DF, 
        gridOptions=gb,
        height=800,
        # width=700,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED, 
        # update_mode=(GridUpdateMode.NO_UPDATE),
        update_mode=(GridUpdateMode.VALUE_CHANGED) | (GridUpdateMode.SELECTION_CHANGED) ,
        allow_unsafe_jscode=True,
        # on_edit_done=disable_checkboxes,
        reload_data =reload)
    return InputActSumGrid_response
# df=pd.DataFrame({ "Name": ['Erica', 'Rogers', 'Malcolm', 'Barrett'], "Age": [43, 35, 57, 29]})


#     gridOptions = GridOptionsBuilder.from_dataframe(df)
#     gb = gridOptions.build()

#     dta = AgGrid(df, gridOptions=gb, height=350, allow_unsafe_jscode=True, theme="blue",
#                 update_mode=GridUpdateMode.VALUE_CHANGED | GridUpdateMode.SELECTION_CHANGED | GridUpdateMode.FILTERING_CHANGED | GridUpdateMode.SORTING_CHANGED)
#     st.text(dta)