import pandas as pd
from ibapi.client import EClient
from ibapi.common import OrderId
from ibapi.wrapper import EWrapper
import threading
import time

default_hostname = '127.0.0.1'
default_port = 7497
default_client_id = 10645
DEFAULT_ERROR_CODE = -999
SHORT_SLEEP_SECONDS = 0.1
MEDIUM_SLEEP_SECONDS = 0.5
LONG_SLEEP_SECONDS = 5
WARNING_ERROR_CODES = [399, 504, 2104, 2168, 2169]


class ibkr_app(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.error_messages = pd.DataFrame(columns=[
            'reqId', 'errorCode', 'errorString'
        ])
        self.next_valid_id = None
        self.historical_data_end = ''
        self.contract_details = None
        self.contract_details_end = None
        self.contract_details_reqId = None
        self.order_reqId_end = None
        self.order_reqId = None

        self.historical_data = pd.DataFrame(columns=['date', 'open', 'close', 'high', 'low'])
        self.managed_accounts = ''

    def error(self, reqId, errorCode, errorString):
        if reqId == self.contract_details_reqId:
            print(f'Error from contract details api: errorCode={errorCode} errorMessage={errorString}')
            self.contract_details_end = DEFAULT_ERROR_CODE
        elif reqId == self.order_reqId_end:
            print(f'Error from place order api: errorCode={errorCode} errorMessage={errorString}')
            self.order_reqId_end = DEFAULT_ERROR_CODE

        if (reqId != -1) and errorCode not in WARNING_ERROR_CODES:
            print("Error: ", reqId, " ", errorCode, " ", errorString)
            print("Closing connection!")
            self.disconnect()
        self.error_messages = pd.concat(
            [self.error_messages, pd.DataFrame({
                "reqId": [reqId],
                "errorCode": [errorCode],
                "errorString": [errorString]
            })])

    def managedAccounts(self, accountsList):
        self.managed_accounts = [i for i in accountsList.split(",") if i]

    def nextValidId(self, orderId: int):
        self.next_valid_id = orderId

    def historicalData(self, reqId, bar):
        record = pd.DataFrame(
            {'date': [bar.date],
             'open': [bar.open],
             'high': [bar.high],
             'low': [bar.low],
             'close': [bar.close]
             })
        record['date'] = pd.to_datetime(record['date'])
        self.historical_data = pd.concat([self.historical_data, record], ignore_index=True)

    def historicalDataEnd(self, reqId: int, start: str, end: str):
        print("HistoricalDataEnd. ReqId:", reqId, "from", start, "to", end)
        self.historical_data_end = reqId

    def contractDetails(self, reqId: int, contractDetails):
        self.contract_details = contractDetails

    def contractDetailsEnd(self, reqId: int):
        self.contract_details_end = reqId

    def orderStatus(self, orderId: OrderId, status: str, filled: float,
                    remaining: float, avgFillPrice: float, permId: int,
                    parentId: int, lastFillPrice: float, clientId: int,
                    whyHeld: str, mktCapPrice: float):
        print(f'Order {orderId} status is {status}')
        self.order_reqId_end = orderId


def fetch_managed_accounts(hostname=default_hostname, port=default_port,
                           client_id=default_client_id):
    app = ibkr_app()
    app.connect(hostname, port, client_id)
    while not app.isConnected():
        time.sleep(SHORT_SLEEP_SECONDS)

    def run_loop():
        app.run()

    api_thread = threading.Thread(target=run_loop, daemon=True)
    api_thread.start()
    while isinstance(app.next_valid_id, type(None)):
        time.sleep(SHORT_SLEEP_SECONDS)
    app.disconnect()
    return app.managed_accounts


def fetch_historical_data(contract, endDateTime='', durationStr='30 D',
                          barSizeSetting='1 hour', whatToShow='MIDPOINT',
                          useRTH=True, hostname=default_hostname,
                          port=default_port, client_id=default_client_id):
    app = ibkr_app()
    app.connect(hostname, port, client_id)
    while not app.isConnected():
        time.sleep(SHORT_SLEEP_SECONDS)

    def run_loop():
        app.run()

    api_thread = threading.Thread(target=run_loop, daemon=True)
    api_thread.start()
    while isinstance(app.next_valid_id, type(None)):
        time.sleep(SHORT_SLEEP_SECONDS)
    tickerId = app.next_valid_id
    app.reqHistoricalData(
        tickerId, contract, endDateTime, durationStr, barSizeSetting,
        whatToShow, useRTH, formatDate=1, keepUpToDate=False, chartOptions=[])
    while app.historical_data_end != tickerId:
        time.sleep(MEDIUM_SLEEP_SECONDS)
        if not app.isConnected():
            break
    app.disconnect()
    return app.historical_data


def fetch_contract_details(contract, hostname=default_hostname,
                           port=default_port, client_id=default_client_id):
    app = ibkr_app()
    app.connect(hostname, port, client_id)
    while not app.isConnected():
        time.sleep(SHORT_SLEEP_SECONDS)

    def run_loop():
        app.run()

    api_thread = threading.Thread(target=run_loop, daemon=True)
    api_thread.start()
    while isinstance(app.next_valid_id, type(None)):
        time.sleep(SHORT_SLEEP_SECONDS)
    app.contract_details_reqId = app.next_valid_id
    app.reqContractDetails(app.contract_details_reqId, contract)
    while (app.contract_details_end != app.contract_details_reqId) and (app.contract_details_end != DEFAULT_ERROR_CODE):
        time.sleep(MEDIUM_SLEEP_SECONDS)
        if not app.isConnected():
            break
    app.disconnect()
    return app.contract_details


def submit_order(contract, order, hostname=default_hostname,
                 port=default_port, client_id=default_client_id):
    app = ibkr_app()
    app.connect(hostname, port, client_id)
    while not app.isConnected():
        time.sleep(SHORT_SLEEP_SECONDS)

    def run_loop():
        app.run()

    api_thread = threading.Thread(target=run_loop, daemon=True)
    api_thread.start()
    while isinstance(app.next_valid_id, type(None)):
        time.sleep(SHORT_SLEEP_SECONDS)

    app.order_reqId = app.next_valid_id
    app.placeOrder(app.order_reqId, contract, order)

    while (app.order_reqId_end != app.order_reqId) and (app.order_reqId_end != DEFAULT_ERROR_CODE):
        time.sleep(MEDIUM_SLEEP_SECONDS)
        if not app.isConnected():
            break
    app.disconnect()

    msg = f'Order {app.order_reqId} successfully submitted'
    print(msg)
    return msg
