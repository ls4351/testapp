import plotly.graph_objects as go
import dash
from dash import dcc, html, callback, dash_table
from dash.dependencies import Input, Output, State
from ibapi.contract import Contract
from ibapi.order import Order
from fintech_ibkr import *
import pandas as pd

APP_DATA_PATH = f"{os.getenv('TESTAPP_DATA_PATH')}\submitted_orders.csv"
order_data = pd.read_csv(APP_DATA_PATH)

layout = html.Div([

    # Section title
    html.H3("Section 1: Fetch & Display exchange rate historical data"),
    html.H4("Select value for whatToShow:"),
    html.Div(
        dcc.Dropdown(
            ["TRADES", "MIDPOINT", "BID", "ASK", "BID_ASK", "ADJUSTED_LAST",
             "HISTORICAL_VOLATILITY", "OPTION_IMPLIED_VOLATILITY", 'REBATE_RATE',
             'FEE_RATE', "YIELD_BID", "YIELD_ASK", 'YIELD_BID_ASK', 'YIELD_LAST',
             "SCHEDULE"],
            "MIDPOINT",
            id='what-to-show'
        ),
        style={'width': '15%'}
    ),
    html.H4("Select value for endDateTime:"),
    html.Div(
        children=[
            html.P("You may select a specific endDateTime for the call to " + \
                   "fetch_historical_data. If any of the below is left empty, " + \
                   "the current present moment will be used.")
        ],
        style={'width': '15%'}
    ),
    html.Div(
        children=[
            html.Div(
                children=[
                    html.Label('Date:'),
                    dcc.DatePickerSingle(id='edt-date')
                ],
                style={
                    'display': 'inline-block',
                    'margin-right': '0.5%',
                }
            ),
            html.Div(
                children=[
                    html.Label('Hour:'),
                    dcc.Dropdown(list(range(24)), id='edt-hour'),
                ],
                style={
                    'display': 'inline-block',
                    'padding-right': '0.5%'
                }
            ),
            html.Div(
                children=[
                    html.Label('Minute:'),
                    dcc.Dropdown(list(range(60)), id='edt-minute'),
                ],
                style={
                    'display': 'inline-block',
                    'padding-right': '0.5%'
                }
            ),
            html.Div(
                children=[
                    html.Label('Second:'),
                    dcc.Dropdown(list(range(60)), id='edt-second'),
                ],
                style={'display': 'inline-block'}
            )
        ]
    ),
    html.H4("Select the duration:"),
    html.Div(
        children=[
            html.Div(
                children=[
                    html.Label('Duration: '),
                    dcc.Input(id='duration-value', value='30', type='number')
                ],
                style={
                    'display': 'inline-block',
                    'margin-right': '1%',
                }
            ),
            html.Div(
                dcc.Dropdown(
                    options=[
                        {'label': 'SECONDS', 'value': 'S'},
                        {'label': 'DAYS', 'value': 'D'},
                        {'label': 'WEEKS', 'value': 'W'},
                        {'label': 'MONTHS', 'value': 'M'},
                        {'label': 'YEARS', 'value': 'Y'},
                    ],
                    value="D",
                    id='duration-category'
                ),
                style={
                    'display': 'inline-block',
                    'width': '10%'}
            )
        ]
    ),
    html.H4("Select the bar size:"),
    html.Div(
        children=[
            html.Div(
                children=[
                    html.Label('Bar Size: '),
                ],
                style={
                    'display': 'inline-block',
                    'margin-right': '0.5%',
                }
            ),
            html.Div(
                dcc.Dropdown(
                    ["1 sec", "5 secs", "15 secs", "30 secs", "1 min", "2 mins", "3 mins", "5 mins", "15 mins",
                     "30 mins", "1 hour", "1 day"],
                    "1 hour",
                    id='bar-size'
                ),
                style={
                    'display': 'inline-block',
                    'width': '5%'}
            )
        ]
    ),
    html.H4("Use Regular Trading Hours:"),
    html.Div(
        children=[
            html.Div(
                children=[
                    html.Label('Use RTH: '),
                ],
                style={
                    'display': 'inline-block',
                    'margin-right': '0.5%',
                }
            ),
            html.Div(
                dcc.RadioItems(
                    id='rth-choice',
                    options=[
                        {'label': 'TRUE', 'value': 'True'},
                        {'label': 'FALSE', 'value': 'False'}
                    ],
                    value='True'
                ),
                style={
                    'display': 'inline-block',
                    'width': '10%'}
            )
        ]
    ),
    html.H4("Enter a currency pair:"),
    html.P(
        children=[
            "See the various currency pairs here: ",
            html.A(
                "currency pairs",
                href='https://www.interactivebrokers.com/en/index.php?f=2222&exch=ibfxpro&showcategories=FX'
            )
        ]
    ),
    # Currency pair text input, within its own div.
    html.Div(
        # The input object itself
        ["Input Currency: ", dcc.Input(
            id='currency-input', value='AUD.CAD', type='text'
        )],
        # Style it so that the submit button appears beside the input.
        style={'display': 'inline-block', 'padding-top': '5px'}
    ),
    # Submit button
    html.Button('Submit', id='submit-button', n_clicks=0, disabled=False),
    # Divs that only serve as a state holder
    html.Div(id='submit-button-disabled', children=0, style=dict(display='none')),
    html.Div(id='submit-button-enabled', children=0, style=dict(display='none')),
    # Line break
    html.Br(),
    # Div to hold the initial instructions and the updated info once submit is pressed
    html.Div(id='currency-output', children='Enter a currency code and press submit'),
    # Div to hold the candlestick graph
    # Loading spinner for graph
    dcc.Loading(
        id="loading-1",
        type="default",
        children=html.Div([dcc.Graph(id='candlestick-graph')]),
    ),
    # Another line break
    html.H3("Section 2: Place Orders"),
    html.H4("Make a Trade"),
    # Radio items to select buy or sell
    dcc.RadioItems(
        id='buy-or-sell',
        options=[
            {'label': 'BUY', 'value': 'BUY'},
            {'label': 'SELL', 'value': 'SELL'}
        ],
        value='BUY'
    ),
    dcc.RadioItems(
        id='market-or-limit',
        options=[
            {'label': 'MARKET', 'value': 'MKT'},
            {'label': 'LIMIT', 'value': 'LMT'}
        ],
        value='MKT'
    ),
    html.Div(
        id='limit-price-div',
        # The input object itself
        children=[html.Label("Limit Price: "), dcc.Input(id='limit-price', value='0', type='number')],
        # Style it so that the submit button appears beside the input.
        style={'display': 'inline-block', 'padding-top': '5px'}
    ),
    html.Br(),
    html.Div(
        children=[html.Label("Currency: "), dcc.Input(id='currency', value='USD', type='text')],
        # Style it so that the submit button appears beside the input.
        style={'display': 'inline-block', 'padding-top': '5px'}
    ),
    html.Br(),
    html.Div(
        children=[
            html.Label("Security Type: "),
            dcc.Dropdown(
                options=[
                    {'label': 'STOCK', 'value': 'STK'},
                    {'label': 'CASH', 'value': 'CASH'},
                    {'label': 'CRYPTO', 'value': 'CRYPTO'},
                ],
                value='STK',
                id='security-type'
            ),
            html.Br(),
            dcc.Input(id='security-symbol', value='AAPL', type='text'),
            dcc.Input(id='trade-amt', value='0', type='number'),
            html.Button('Trade', id='trade-button', n_clicks=0)
        ],
        style={'display': 'inline-block', 'padding-top': '5px'}
    ),
    html.Div(id='trade-button-disabled', children=0, style=dict(display='none')),
    html.Div(id='trade-button-enabled', children=0, style=dict(display='none')),

    # Div to confirm what trade was made
    html.Div(id='trade-output'),
    html.Br(),
    html.H3("Section 3: Display Order History"),
    html.Div(
        children=[
            dash_table.DataTable(
                order_data.to_dict('records'),
                [{"name": i, "id": i} for i in order_data.columns],
                id='order-history-tbl'
            )],
        style={'width': '50%', 'margin': '0 auto'}
    )
])


# This callback only cares about the input event, not its value
# This is called if both events happen together or if only one happens
@callback(
    Output(component_id='submit-button', component_property='disabled'),
    Input('submit-button-disabled', 'children'),
    Input('submit-button-enabled', 'children'),
)
def should_disable_submit_button(should_disable, should_enable):
    if len(dash.callback_context.triggered) == 1:
        context = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
        return context == 'submit-button-disabled'


@callback(
    Output(component_id='trade-button', component_property='disabled'),
    Input('trade-button-disabled', 'children'),
    Input('trade-button-enabled', 'children'),
)
def should_disable_trade_button(should_disable, should_enable):
    if len(dash.callback_context.triggered) == 1:
        context = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
        return context == 'trade-button-disabled'


# Breaking the process into 2 separate triggers.
# Rationale: If 'should_disable_button' waits for either 'submit-button' or 'candlestick-graph' directly,
# Dash only delivers those events together to 'should_disable_button'
@callback(
    Output(component_id='submit-button-disabled', component_property='children'),
    Input('submit-button', 'n_clicks'),
)
def trigger_disable_submit_button(n_click):
    return 1


@callback(
    Output(component_id='trade-button-disabled', component_property='children'),
    Input('trade-button', 'n_clicks'),
)
def trigger_disable_trade_button(n_click):
    return 1


@callback(
    Output(component_id='submit-button-enabled', component_property='children'),
    Input('candlestick-graph', 'figure'),
)
def trigger_enable_submit_button(n_click):
    return 1


@callback(
    Output(component_id='trade-button-enabled', component_property='children'),
    Input('order-history-tbl', 'data'),
)
def trigger_enable_trade_button(n_click):
    return 1


@callback(
    [  # there's more than one output here, so you have to use square brackets to pass it in as an array.
        Output(component_id='currency-output', component_property='children'),
        Output(component_id='candlestick-graph', component_property='figure')
    ],
    Input('submit-button', 'n_clicks'),
    # The callback function will
    # fire when the submit button's n_clicks changes
    # The currency input's value is passed in as a "State" because if the user is typing and the value changes, then
    #   the callback function won't run. But the callback does run because the submit button was pressed, then the value
    #   of 'currency-input' at the time the button was pressed DOES get passed in.
    [State('currency-input', 'value'), State('what-to-show', 'value'),
     State('edt-date', 'date'), State('edt-hour', 'value'),
     State('edt-minute', 'value'), State('edt-second', 'value'),
     State('duration-value', 'value'), State('duration-category', 'value'),
     State('bar-size', 'value'), State('rth-choice', 'value')]
)
def update_candlestick_graph(n_clicks, currency_string, what_to_show,
                             edt_date, edt_hour, edt_minute, edt_second,
                             duration_value, duration_category, bar_size, rth_choice):
    # n_clicks doesn't get used, we only include it for the dependency.
    if any([i is None for i in [edt_date, edt_hour, edt_minute, edt_second]]):
        end_date_time = ''
    else:
        end_date_time = f'{edt_date.replace("-", "")} {edt_hour}:{edt_minute}:{edt_second}'

    # First things first -- what currency pair history do you want to fetch?
    # Define it as a contract object!
    contract = Contract()
    contract.symbol = currency_string.split(".")[0]
    contract.secType = 'CASH'
    contract.exchange = 'IDEALPRO'  # 'IDEALPRO' is the currency exchange.
    contract.currency = currency_string.split(".")[1]

    print("Graph Input:"
          f"\n\t contract.symbol: {contract.symbol}"
          f"\n\t contract.currency: {contract.currency}"
          f"\n\t end_date_time: {end_date_time}"
          f"\n\t duration: {duration_value} {duration_category}"
          f"\n\t bar_size:  {bar_size}"
          f"\n\t what_to_show:  {what_to_show}"
          f"\n\t rth:  {bool(rth_choice)}"
          )
    print("Checking if contract is valid...")
    contract_details = fetch_contract_details(contract)
    if isinstance(contract_details, type(None)):
        return ('Currency pair ' + currency_string + ' is not valid'), {}

    cph = fetch_historical_data(
        contract=contract,
        endDateTime=end_date_time,
        durationStr=f"{duration_value} {duration_category}",  # <-- make a reactive input
        barSizeSetting=bar_size,  # <-- make a reactive input
        whatToShow=what_to_show,
        useRTH=bool(rth_choice)  # <-- make a reactive input
    )
    # # # Make the candlestick figure
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=cph['date'],
                open=cph['open'],
                high=cph['high'],
                low=cph['low'],
                close=cph['close']
            )
        ]
    )
    fig.update_layout(title=('Exchange Rate: ' + currency_string))

    return ('Submitted query for ' + currency_string), fig


@callback(
    Output('limit-price-div', 'style'),
    Input('market-or-limit', 'value')
)
def display_limit_price(order_type):
    if order_type == 'LMT':
        return {'display': 'inline-block'}
    else:
        return {'display': 'none'}


# Callback for what to do when trade-button is pressed
@callback(
    [
        Output(component_id='trade-output', component_property='children'),
        Output(component_id='order-history-tbl', component_property='data')
    ],
    # We only want to run this callback function when the trade-button is pressed
    Input('trade-button', 'n_clicks'),
    # We DON'T want to run this function whenever buy-or-sell, trade-currency, or trade-amt is updated, so we pass those
    #   in as States, not Inputs:
    [State('security-type', 'value'), State('buy-or-sell', 'value'), State('security-symbol', 'value'),
     State('trade-amt', 'value'), State('currency', 'value'),
     State('market-or-limit', 'value'), State('limit-price', 'value'),
     State('order-history-tbl', 'data')
     ],
    # We DON'T want to start executing trades just because n_clicks was initialized to 0!!!
    prevent_initial_call=True
)
def trade(n_clicks, sec_type, action, security_symbol, trade_amt, currency, order_type, limit_price,
          order_history_data):
    contract = Contract()

    if sec_type == 'STK':
        contract.symbol = security_symbol
        contract.secType = 'STK'
        contract.exchange = 'SMART'
        contract.primaryExchange = 'ARCA'
        contract.currency = currency
    elif sec_type == 'CASH':
        contract.symbol = security_symbol.split(".")[0]
        contract.secType = 'CASH'
        contract.exchange = 'IDEALPRO'
        contract.currency = security_symbol.split(".")[1]
    elif sec_type == 'CRYPTO':
        contract.symbol = security_symbol
        contract.secType = 'CRYPTO'
        contract.currency = currency
        contract.exchange = 'PAXOS'

    print("Order Input:"
          f"\n\t sec_type: {sec_type}"
          f"\n\t action: {action}"
          f"\n\t contract.symbol: {contract.symbol}"
          f"\n\t contract.currency: {contract.currency}"
          f"\n\t currency: {currency}"
          f"\n\t trade_amt: {trade_amt}"
          f"\n\t order_type: {order_type}"
          f"\n\t limit_price: {limit_price}"
          )

    print("Checking if contract is valid...")
    contract_details = fetch_contract_details(contract)
    if isinstance(contract_details, type(None)):
        return ('Contract for ' + security_symbol + ' is not valid'), order_history_data

    order = Order()
    order.action = action
    order.totalQuantity = trade_amt
    order.orderType = order_type
    if order_type == 'LMT':
        order.lmtPrice = limit_price
    if sec_type == 'CRYPTO':
        order.tif = 'IOC'  # tif = TimeInForce  IOC = Immediate or Cancel
        if action == 'BUY' and order_type == 'MKT':
            order.cashQty = trade_amt
            order.totalQuantity = ''

    msg = submit_order(contract, order)

    order_history_data = pd.read_csv(APP_DATA_PATH)
    return msg, order_history_data.to_dict('records')
