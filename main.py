import pandas as pd
import requests
import uvicorn
from alpaca_trade_api.rest import TimeFrame
from fastapi import FastAPI
import alpaca_trade_api as tradeapi



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


def get_historical_data(symbol, start_date_time, end_date_time):
    """
    api_key = 'f8f59ed60c3743328f18e9aa36ac1048'
    api_url = f'https://api.twelvedata.com/time_series?symbol={symbol}&interval=1day&outputsize=5000&apikey={api_key}'
    raw_df = requests.get(api_url).json()
    df = pd.DataFrame(raw_df['values']).iloc[::-1].set_index('datetime').astype(float)
    df = df[df.index >= start_date]
    df.index = pd.to_datetime(df.index)

    # Convert to dataframe
    asset = df.to_csv()
    f = open("asset_apple.csv", "w")
    f.write(asset)
    apple_df = pd.read_csv("asset_apple.csv")

    return apple_df"""
    api_key = 'PK7QBPXIS9I119J8USMT'
    api_secret = 'FeDY72hqrSGKyySG56faJvLaqWiKymn0yLxcBMAY'
    base_url = 'https://paper-api.alpaca.markets'

    # instantiate REST API
    api = tradeapi.REST(api_key, api_secret, base_url, api_version='v2')

    # obtain account information
    account = api.get_account()
    print(account)

    aapl = api.get_bars(symbol,TimeFrame.Minute, start= start_date_time, end=end_date_time).df
    df = aapl.to_csv()
    f = open('asset_apple.csv','w')
    f.write(df)
    new_df = pd.read_csv('asset_apple.csv')
    print()
    new_df.rename(columns={'timestamp': 'datetime'}, inplace=True)
    print(new_df.to_string())
    return new_df


@app.get('/investment/{symbol}/{start_date_time}/{end_date_time}', status_code=200)
def get_all_transactions(symbol: str, start_date_time:str, end_date_time: str):

    print(symbol)
    symbol = symbol.replace("-", "/")
    print("ich hole Daten")
    print(end_date_time)
    return get_historical_data(symbol, start_date_time, end_date_time).to_json()

# authentication and connection details

if __name__ == "__main__":
    uvicorn.run("main:app", port=8084, reload=True)

