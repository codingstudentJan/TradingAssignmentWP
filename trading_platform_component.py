import smtplib
from email.mime.text import MIMEText
from email.message import EmailMessage
import ssl

import alpaca_trade_api as tradeapi
import streamlit as st


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
        symbols_to_names = {asset.symbol: asset.name for asset in assets if asset.tradable and asset.fractionable}

        # Create a dropdown menu of symbols with names as labels
        symbol = st.selectbox("Select a symbol to trade", list(symbols_to_names.values()))

        # Get the symbol corresponding to the selected name
        selected_symbol = [k for k, v in symbols_to_names.items() if v == symbol][0]
        side = st.selectbox("Select the side", ("Buy", "Sell"))
        qty = st.number_input("Quantity", value=1.00, min_value=1.00, step=0.01)

        # Execute the trade when the "Execute Trade" button is clicked
        if st.button("Execute Trade"):
            if side == "Buy":
                order = api.submit_order(symbol=selected_symbol, qty=qty, side='buy', type='market',
                                         time_in_force='day', order_class='simple')
            else:
                order = api.submit_order(symbol=selected_symbol, qty=qty, side='sell', type='market',
                                         time_in_force='day', order_class='simple')

            # Show the order details and current unrealized profit or loss
            text = f"Your order of {symbol} was a success. \n" \
                   f"Order ID: {order.id} \n" \
                   f"Symbol: {order.symbol}\n" \
                   f"Quantity: {order.qty}\n" \
                   f"Status: {order.status}\n" \
                   f"Thank you for choosing ProdigyTrade!"
            mailsender = 'ProdigyTradeDHBW@gmail.com'
            password = 'zhkmuvnaykjhrhqd'
            mail_receiver = 'cedric.perrot@gmail.com'

            em = EmailMessage()
            em['From'] = mailsender
            em['To'] = mail_receiver
            em['Subject'] = f"Your order of {selected_symbol}"
            context = em.set_content(text)

            ssl.create_default_context()
            with smtplib.SMTP_SSL('smtp.gmail.com',465,context= context) as smtp:
                smtp.login(mailsender,password)
                smtp.sendmail(mailsender,mail_receiver,em.as_string())

            st.success(f"Your order of{selected_symbol} was a success")
            st.write("Order ID:", order.id)
            st.write("Symbol:", order.symbol)
            st.write("Quantity:", order.qty)
            st.write("Status:", order.status)
