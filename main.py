from fastapi import FastAPI
from sqlalchemy.orm import Session
import uvicorn
from typing import List
import datetime

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.data.historical import CryptoHistoricalDataClient
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import date2num
client = CryptoHistoricalDataClient()


API_KEY = "PK9M5LWB3QCIP3WQAYIS"
SECRET_KEY = "W59ISrRhIAwIG5Ib2k3cMASa0avwfUQxLoDFioqK"


app = FastAPI(title="Finance Application",
              description="""Finance Tracker Application \n
    Made by: \n
    Alina Günther \n
    Feni Yuliastutik \n
    Laura Makare \n
    """,
              version="1.0.0")




@app.post('/investment', tags=["Transaction"], status_code=201)
async def create_transaction():
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

def get_asset_data():
    request_params = CryptoBarsRequest(
        symbol_or_symbols=["ETH/USD"],
        timeframe=TimeFrame.Minute,
        start='2023-03-17 15:35:00',
        end='2023-03-17 17:00:00',
    )
    # Retrieve daily bars for Bitcoin in a DataFrame and printing it
    btc_bars = client.get_crypto_bars(request_params)
    print(type(btc_bars))

    # Convert to dataframe
    df = btc_bars.df
    asset_data = df.to_csv()
    f = open("asset_info_file.csv", "w")
    f.write(asset_data)
    new_df = pd.read_csv("asset_info_file.csv")
    return new_df
@app.get('/investment', status_code=200)
def get_all_transactions():
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
    return get_asset_data()

if __name__ == "__main__":
    uvicorn.run("main:app", port=8084, reload=True)