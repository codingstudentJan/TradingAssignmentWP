import streamlit as st
import alpaca_trade_api as tradeapi
import time

def trading_platform():
    # Set the API endpoint to the Alpaca paper trading endpoint
    endpoint = 'https://paper-api.alpaca.markets'
    api_version = 'v2'
    api_key = 'PK7QBPXIS9I119J8USMT'
    secret_key = 'FeDY72hqrSGKyySG56faJvLaqWiKymn0yLxcBMAY'
    # Authenticate the user's API keys using the paper trading endpoint
    if api_key and secret_key:
        api = tradeapi.REST(api_key, secret_key, base_url=endpoint, api_version=api_version)

        # Get a list of available assets from Alpaca
        assets = api.list_assets()

        # Create a dictionary mapping symbols to asset names
        symbols_to_names = {asset.symbol: asset.name for asset in assets if asset.tradable}

        # Create a dropdown menu of symbols with names as labels
        symbol = st.selectbox("Select a symbol to trade", list(symbols_to_names.values()))

        # Get the symbol corresponding to the selected name
        selected_symbol = [k for k, v in symbols_to_names.items() if v == symbol][0]
        side = st.selectbox("Select the side", ("Buy", "Sell"))
        qty = st.number_input("Quantity", value=1, min_value=1)

        # Execute the trade when the "Execute Trade" button is clicked
        if st.button("Execute Trade"):
            if side == "Buy":
                order = api.submit_order(symbol=selected_symbol, qty=qty, side='buy', type='market', time_in_force='day', order_class='simple')
            else:
                order = api.submit_order(symbol=selected_symbol, qty=qty, side='sell', type='market', time_in_force='day', order_class='simple')

            # Show the order details and current unrealized profit or loss
            st.write("Order ID:", order.id)
            st.write("Symbol:", order.symbol)
            st.write("Quantity:", order.qty)
            st.write("Status:", order.status)