import pandas as pd
import requests
import uvicorn
from fastapi import FastAPI


app = FastAPI(title="Finance Application",
              description="""Finance Tracker Application \n
    Made by: \n
    Lyle Braunbart \n
    Feni Yuliastutik \n
    Laura Makare \n
    Dennis Cassady \n
    Jan Berger
    """,
              version="1.0.0")


def get_historical_data(symbol, start_date):
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

    return apple_df

@app.get('/investment/{symbol}', status_code=200)
def get_all_transactions(symbol: str):

    print(symbol)
    symbol = symbol.replace("-", "/")
    print("ich hole Daten")
    return get_historical_data(symbol, '2022-01-01')


if __name__ == "__main__":
    uvicorn.run("main:app", port=8084, reload=True)
