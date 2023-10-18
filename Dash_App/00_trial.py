import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import flask
import urllib.parse
app = dash.Dash(__name__)
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.H1(id='title-text')
])
@app.callback(
    Output('title-text', 'children'),
    Input('url', 'search')
)
def update_title(search):
    # Parse the URL query parameters
    query_params = urllib.parse.parse_qs(search[1:])
    
    # Get the 'ID' parameter value
    id_param = query_params.get('ID', [''])[0]
    
    return id_param
app.run_server(debug=True)