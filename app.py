from dash import Dash, dcc, html, callback
from dash.dependencies import Input, Output
from pages import main_page, hw3_1_page

app = Dash(__name__, suppress_callback_exceptions=True)
server = app.server
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@callback(Output('page-content', 'children'),
          Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/':
        return main_page.layout
    elif pathname == '/homework_3.1':
        return hw3_1_page.layout
    else:
        return '404'


if __name__ == '__main__':
    app.run_server(debug=True)
