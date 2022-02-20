from dash import dcc
from dash import html
from dash import callback
from dash.dependencies import Input, Output
from testapp import *

layout = html.Div([
    html.H1('You Passed'),
    github_info_header(),
    html.Div([
        "Input: ",
        dcc.Input(id='ticker-input', value='Enter stock ticker', type='text')
    ]),
    html.Br(),
    html.Div(id='ticker-output'),
    html.Img(src="assets/charging_bull.jpg")
])


@callback(
    Output(component_id='ticker-output', component_property='children'),
    Input(component_id='ticker-input', component_property='value')
)
def display_output(input_value):
    return 'You chose: {}'.format(input_value)
