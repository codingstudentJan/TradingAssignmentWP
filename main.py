import json
import os.path

import pandas as pd
import requests
import uvicorn
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame
from fastapi import FastAPI

client = CryptoHistoricalDataClient()

API_KEY = "PK9M5LWB3QCIP3WQAYIS"
SECRET_KEY = "W59ISrRhIAwIG5Ib2k3cMASa0avwfUQxLoDFioqK"

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


@app.post('/investment/{symbol}', tags=["Transaction"], status_code=201)
async def create_transaction(symbol:str):
    """create transaction function
    * This function is used to create transactions and store them in the database

    param:
        * transaction_request(schemas.TransactionCreate): created transaction in schemas class
        * db(Session): acquired databank session

    Returns:
        * created Data of Transactions

    Test:
        * if data could be saved
        * if connection is available
        * if the datatype for each attributes is right
    """
    print(symbol)
    return get_asset_data()


def get_asset_data(symbol: str):
    request_params = CryptoBarsRequest(
        symbol_or_symbols=[symbol],
        timeframe=TimeFrame.Minute,
        start='2023-03-17 15:35:00',
        end='2023-03-17 17:00:00',
    )
    # Retrieve daily bars for Bitcoin in a DataFrame and printing it
    btc_bars = client.get_crypto_bars(request_params)
    print(type(btc_bars))
    print(str(btc_bars))
    # Convert to dataframe
    df = btc_bars.df
    asset_data = df.to_csv()
    print(asset_data)
    f = open("asset_info_file.csv", "w")
    f.write(asset_data)
    new_df = pd.read_csv("asset_info_file.csv")
    print(new_df)
    return new_df


def get_all_tradable_cryptos():
    # Setzen Sie den API-Endpunkt für die Krypto-Fiat-Paare
    url = "https://paper-api.alpaca.markets/v2/assets?asset_class=crypto"

    # Setzen Sie Ihre API-Schlüssel als Header-Parameter
    headers = {
        "Apca-Api-Key-Id": API_KEY,
        "Apca-Api-Secret-Key": SECRET_KEY
    }

    # Senden Sie die GET-Anfrage an die API und speichern Sie die Antwort
    response = requests.get(url, headers=headers)

    # Überprüfen Sie den Statuscode der Antwort
    if response.status_code == 200:
        # Wenn die Anfrage erfolgreich war, geben Sie die JSON-Antwort zurück
        print(type(response.text))
        dictonary = json.loads(response.text)
        print(type(dictonary))
        print(dictonary[0]['symbol'])
        return dictonary
    else:
        # Wenn die Anfrage nicht erfolgreich war, geben Sie eine Fehlermeldung zurück
        print(f"API-Anfrage fehlgeschlagen. Statuscode: {response.status_code}")
        return f"API-Anfrage fehlgeschlagen. Statuscode: {response.status_code}"


def get_historical_data(symbol, start_date):
    api_key = 'f8f59ed60c3743328f18e9aa36ac1048'
    api_url = f'https://api.twelvedata.com/time_series?symbol={symbol}&interval=1day&outputsize=5000&apikey={api_key}'
    raw_df = requests.get(api_url).json()
    print ("Raw Dataframe:",raw_df)
    df = pd.DataFrame(raw_df['values']).iloc[::-1].set_index('datetime').astype(float)
    df = df[df.index >= start_date]
    df.index = pd.to_datetime(df.index)

    # Convert to dataframe
    asset = df.to_csv()
    f = open("asset_apple.csv", "w")
    f.write(asset)
    apple_df = pd.read_csv("asset_apple.csv")

    return apple_df
"""def get_historical_data2(symbol, start_date):
    api_key = 'LJ43I6PJEPWAP513'
    api_url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={api_key}'
    raw_df = requests.get(api_url).json()
    print ("Raw Dataframe:",raw_df)
    df = pd.DataFrame(raw_df['values']).iloc[::-1].set_index('datetime').astype(float)
    df = df[df.index >= start_date]
    df.index = pd.to_datetime(df.index)

    # Convert to dataframe
    asset = df.to_csv()
    f = open("asset_apple.csv", "w")
    f.write(asset)
    apple_df = pd.read_csv("asset_apple.csv")

    return apple_df
"""
@app.get('/investment/{symbol}', status_code=200)
def get_all_transactions(symbol: str):
    """get all transaction function
    * This class is used to get transactions stored in the database

    param:
        * db(Session): acquired databank session

    Returns:
        * all list the transactions stored in the database

    Test:
        * if data can be fetched
        * if connection is available
    """
    print(symbol)
    print("Hallo")
    symbol = symbol.replace("-", "/")
    print(symbol)
    print("ich hole Daten")
    return get_historical_data(symbol, '2022-01-01')


@app.get('/cryptos', status_code=200)
def get_all_cryptos():
    return get_all_tradable_cryptos()


@app.get('/momentum', status_code=200)
def get_all_transactions():
    return get_historical_data('GOOGL', '2022-01-01')


if __name__ == "__main__":
    uvicorn.run("main:app", port=8084, reload=True)
