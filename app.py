from dash import *
from testapp import *
from dash import dcc
from dash.dependencies import Input, Output

app = Dash(__name__)
server = app.server
app.layout = html.Div([
    github_info_header(),
    html.Div([
        "Input: ",
        dcc.Input(id='ticker-input', value='Enter stock ticker', type='text')
    ]),
    html.Br(),
    html.Div(id='ticker-output'),
    html.Img(src="assets/bear_statue.jpg")
])


@app.callback(
    Output(component_id='ticker-output', component_property='children'),
    Input(component_id='ticker-input', component_property='value')
)
def display_output(input_value):
    return 'You chose: {}'.format(input_value)


if __name__ == '__main__':
    app.run_server(debug=True)
