import panel as pn
import NotFound
from importlib import reload
import requests
from function import Auth, IO_Data
import pandas as pd
import param
reload(NotFound)
reload(IO_Data)
reload(Auth)

def getValue(widget):
    return widget
# @pn.cache
def getUserID(query_params):
    return Auth.getUserID(query_params)
def WidgetSelectCompany(AvailComp_DF):
    select = pn.widgets.Select(name='Select Company', options=['-'] + AvailComp_DF['company_name'].tolist())
    return select

    # SelectedModule = pn.bind(WidgetSelectModule, SelectedWell)
def WidgetSelectModule(UserLogin_dict, SelectWell):
    select = pn.widgets.Select(name='Select Module', options=['-'] + Auth.getAvailModule(UserLogin_dict, SelectWell))
    return select

def WidgetSelectWell(AvailWell_DF):
    # if AvailWell_DF != '-':
    #     return pn.widgets.Select(name='Select Well', options=['-'] + AvailWell_DF['well_name'].tolist())
    # else:
    #     return pn.widgets.Select(name='Select Well', options=['-'])
    try:
        select = pn.widgets.Select(name='Select Well', options=['-'] + AvailWell_DF['well_name'].tolist())
        return select
    except:
        select = pn.widgets.Select(name='Select Well', options=['-'])
        return select
    # WidgetSelectWell(AvailWell_DF)
    # return IO_Data.getAvailableWellDF(SelectComp, AvailComp_DF)

# class MainWidget(param.Parameterized):
#     param3 = param.ObjectSelector(default='D', objects=['A', 'B', 'C'])
#     def __init__(self, **params):
#         super().__init__(**params)
#         self.AvailComp_DF = None
#     def addAuth(self, UserAuthDict):
#         self.AvailComp_DF = IO_Data.getAvailableCompanyDF(UserAuthDict)
    
#     def CompanyWidget()



App = pn.template.BootstrapTemplate(
    title='RTDC Application',
    # site_url='/test/',
    sizing_mode="stretch_width",
    site='DOME'
)




# query_test = pn.state.location.query_params
UserAuthDict = getUserID(pn.state.location.query_params)
if UserAuthDict['verification'] != 'verified':
    App.main.append(
        pn.Row(
            pn.Column(
                "#  Not Found",
                NotFound.NotFoundPanes(),
                align="center",
                )
                )
    )
    App.servable()

else:
    AvailComp_DF = IO_Data.getAvailableCompanyDF(UserAuthDict)
    SelectComp = WidgetSelectCompany(AvailComp_DF)
    AvailWell_DF = pn.bind( IO_Data.getAvailableWellDF, SelectComp=SelectComp, AvailComp_DF=AvailComp_DF)

    SelectedWell = pn.bind(WidgetSelectWell, AvailWell_DF)
    selectedwell_value = pn.bind(getValue, SelectedWell().value)
    
    SelectedModule = pn.bind(WidgetSelectModule, UserLogin_dict=UserAuthDict, SelectWell=pn.bind(WidgetSelectWell, AvailWell_DF))

    App.sidebar.append(
        pn.Column(
            f"# Welcome {UserAuthDict['data']['user_name']}",
            f"### {UserAuthDict['data']['user_company_name']}\n{UserAuthDict['data']['user_id']}\n{UserAuthDict['data']['user_email']}",
            SelectComp,
            SelectedWell,
            SelectedModule,
            selectedwell_value,
        )
    )

    App.servable()
