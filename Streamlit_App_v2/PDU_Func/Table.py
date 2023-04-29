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
def ActivityLogTable_Agrid(ActivityLog_DF, reload=False):
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

    gridOptions  = GridOptionsBuilder.from_dataframe(ActivityLog_DF.drop(['id','DateTime'], 1))
    # gridOptions  = GridOptionsBuilder.from_dataframe(ActivityLog_DF.drop(['DateTime'], 1))
    gridOptions.configure_selection('single')

    gridOptions.configure_column('Insert', headerTooltip='Click on Button to add new row', editable=False, filter=False,
                            onCellClicked=JsCode(string_to_add_row), cellRenderer=cell_button_add,
                            autoHeight=True, wrapText=True, suppressMovable='true')
    gridOptions.configure_column('Delete', headerTooltip='Click on Button to remove row',
                                    editable=False, filter=False, onCellClicked=JsCode(string_to_delete),
                                    cellRenderer=cell_button_delete,
                                    autoHeight=True, )
    gridOptions.configure_default_column(editable=True)
    gb = gridOptions.build()
    gb['autoSizeColumns ']=True
    InputActivityGrid_response = AgGrid(
        ActivityLog_DF, 
        gridOptions=gb,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED, 
        # update_mode=(GridUpdateMode.NO_UPDATE),
        update_mode=(GridUpdateMode.VALUE_CHANGED) | (GridUpdateMode.SELECTION_CHANGED) ,
        allow_unsafe_jscode=True,
        reload_data =reload)
    return InputActivityGrid_response

def ActSumTable_Agrid(ActSumData, reload=False):
    ActSum_DF = ActSumData.Data
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
    gridOptions.configure_selection('single')

    #TODO
    # column edit on SubActivity
    # column edit on datetime end
    # column edit on remarks
    # gridOptions.configure_column('SubActivity',editable=True)
    # gridOptions.configure_column('End DateTime',editable=True)
    # gridOptions.configure_column('remarks',editable=True)



    gridOptions.configure_column('Insert', headerTooltip='Click on Button to add new row', editable=False, filter=False,
                            onCellClicked=JsCode(string_to_add_row), cellRenderer=cell_button_add,
                            autoHeight=True, wrapText=True, suppressMovable='true')
    gridOptions.configure_column('Delete', headerTooltip='Click on Button to remove row',
                                    editable=False, filter=False, onCellClicked=JsCode(string_to_delete),
                                    cellRenderer=cell_button_delete,
                                    autoHeight=True, )
    gridOptions.configure_default_column(editable=False)
    gb = gridOptions.build()
    gridOptions_dict = {
    'alwaysShowHorizontalScroll': True,
    'alwaysShowVerticalScroll': True,
    'pagination': True,
    'paginationPageSize': 15,
    }
    for keys in gridOptions_dict.keys():
        gb[keys] = gridOptions_dict[keys]
    
    InputActSumGrid_response = AgGrid(
        ActSum_DF, 
        gridOptions=gb,
        # height=500,
        # width=700,

        data_return_mode=DataReturnMode.FILTERED_AND_SORTED, 
        # update_mode=(GridUpdateMode.NO_UPDATE),
        update_mode=(GridUpdateMode.VALUE_CHANGED) | (GridUpdateMode.SELECTION_CHANGED) ,
        allow_unsafe_jscode=True,
        reload_data =reload)
    return InputActSumGrid_response
# df=pd.DataFrame({ "Name": ['Erica', 'Rogers', 'Malcolm', 'Barrett'], "Age": [43, 35, 57, 29]})


#     gridOptions = GridOptionsBuilder.from_dataframe(df)
#     gb = gridOptions.build()

#     dta = AgGrid(df, gridOptions=gb, height=350, allow_unsafe_jscode=True, theme="blue",
#                 update_mode=GridUpdateMode.VALUE_CHANGED | GridUpdateMode.SELECTION_CHANGED | GridUpdateMode.FILTERING_CHANGED | GridUpdateMode.SORTING_CHANGED)
#     st.text(dta)