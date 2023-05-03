import alpaca_trade_api
import alpaca_trade_api as tradeapi
import pandas as pd
import uvicorn
from alpaca_trade_api.rest import TimeFrame
from fastapi import FastAPI

app = FastAPI(title="Finance Application",
              description="""Trading App \n
    Made by: \n
    Lyle Braunbart \n
    Feni Yuliastutik \n
    Laura Makare \n
    Dennis Cassady \n
    Jan Berger
    """,
              version="1.0.0")

api_key = 'PK7QBPXIS9I119J8USMT'
api_secret = 'FeDY72hqrSGKyySG56faJvLaqWiKymn0yLxcBMAY'

base_url = 'https://paper-api.alpaca.markets'
def get_historical_data(symbol, start_date_time, end_date_time, trading_option):

    # instantiate REST API
    api = tradeapi.REST(api_key, api_secret, base_url, api_version='v2')

    strategy = TimeFrame.Minute
    if trading_option == "Hour Trading":
        strategy = TimeFrame.Hour
    elif trading_option == "Day Trading":
        strategy = TimeFrame.Day

    aapl = api.get_bars(symbol, strategy, start=start_date_time, end=end_date_time).df
    df = aapl.to_csv()
    f = open('asset_apple.csv', 'w')
    f.write(df)
    try:
        new_df = pd.read_csv('asset_apple.csv')
        print()
        new_df.rename(columns={'timestamp': 'datetime'}, inplace=True)
        print(new_df.to_string())
        return new_df
    except:
        new_df = pd.DataFrame()
        return new_df


def get_account_details():

    # instantiate REST API
    api = tradeapi.REST(api_key, api_secret, base_url, api_version='v2')

    # obtain account information
    account = api.get_account()
    return account


def get_orders(status: str):

    # instantiate REST API
    api = tradeapi.REST(api_key, api_secret, base_url, api_version='v2')
    orders_list = api.list_orders(
        status=status,
        limit=100,
        nested=True  # show nested multi-leg orders
    )
    # print(orders_list)
    return orders_list


def get_asset_list():
    endpoint = 'https://paper-api.alpaca.markets'
    api_version = 'v2'
    api_key = 'PK7QBPXIS9I119J8USMT'
    secret_key = 'FeDY72hqrSGKyySG56faJvLaqWiKymn0yLxcBMAY'
    # Authenticate the user's API keys using the paper trading endpoint
    if api_key and secret_key:
        api = tradeapi.REST(api_key, secret_key, base_url=endpoint, api_version=api_version)

        # Get a list of available assets from Alpaca
        assets = api.list_assets()
        asset_dict: dict = {}
        for asset in assets:
            if asset.tradable:
                asset_dict[f'{asset.name}'] = asset.symbol
        return asset_dict


def portfolio_history():

    # instantiate REST API
    api = tradeapi.REST(api_key, api_secret, base_url, api_version='v2')
    portfolio_history: alpaca_trade_api.entity.PortfolioHistory = api.get_portfolio_history(date_start="2023-03-14")
    return portfolio_history
def get_position():
    api = tradeapi.REST(api_key, api_secret, base_url, api_version='v2')
    positions = api.list_positions()
    return positions

@app.get('/investment/{symbol}/{start_date_time}/{end_date_time}/{trading_option}', status_code=200)
def get_all_transactions(symbol: str, start_date_time: str, end_date_time: str, trading_option: str):
    print(trading_option)
    print(symbol)
    # symbol = symbol.replace("-", "/")
    print("ich hole Daten")
    print(end_date_time)
    get_asset_list()
    return get_historical_data(symbol, start_date_time, end_date_time, trading_option).to_json()


@app.get('/investment/account')
def get_details():
    # portfolio_history()
    return get_account_details()


@app.get('/investment/orders/{status}')
def get_order_by_status(status: str):
    return get_orders(status)


@app.get('/investment/assets')
def get_all_assets():
    return get_asset_list()


@app.get('/investment/portfolio_history')
def get_portfolio_history():
    return portfolio_history()

@app.get('/investment/positions')
def get_positions():
    return get_position()

# authentication and connection details

if __name__ == "__main__":
    uvicorn.run("main:app", port=8084, reload=True)
