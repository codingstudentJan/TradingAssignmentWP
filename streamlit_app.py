import datetime
import os
import toml
import openai
from math import floor
from typing import List

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import requests
import streamlit as st
import yaml
from streamlit_authenticator import Authenticate
from streamlit_option_menu import option_menu
from yaml.loader import SafeLoader
from streamlit_chat import message

from main import get_account_details
from momentum_strategy import apply_momentum_strategy, add_signals_to_chart
from support_and_resistance_file import support_and_resistance_algorithm
from trading_platform_component import trading_platform
from SessionState import SessionState

st.set_page_config(page_title="Prodigy Trade", page_icon="random")


def fetch(session, url):
    try:
        result = session.get(url)
        return result.json()
    except Exception:
        print("Data Fetching failed")


# hashed_passwords = stauth.Hasher(['abc123','def']).generate()

with open(os.getcwd() + "\config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

    authenticator = Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
    )
    name, authentication_status, username = authenticator.login('Login', 'main')
    print(username)

session = requests.Session()

stocks_list = fetch(session, f"http://127.0.0.1:8084/investment/assets")
# print(stocks_list)
# dictionary for the categories
stocks_category = stocks_list
if authentication_status:
    def main():
        authenticator.logout('Logout', 'sidebar')
        # with open(r"C:\Users\User\Desktop\4.Semester\Web_Programming\TraderJoe\style.css") as f:
        #   st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        st.title("Welcome to Prodigy Trade!")
        # create a session state object to store sample_data
        state = SessionState.get(sample_data=None)
        filter_expander = st.sidebar.expander(label="Click to filter")
        with filter_expander:
            with st.container():
                option = st.selectbox(
                    'Which Stock, Forex, Crypto, ETF, or indices would you like to trade?',
                    stocks_category.keys())
                option = option.replace("/", "-")
            with st.container():
                trading_options = ["Minute Trading", "Hour Trading", "Day Trading"]
                trading_option = st.selectbox(label="Select Trading Type", options=trading_options)
            with st.container():
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input(
                        "At which date should the chart start?",
                        datetime.date(2023, 4, 27))
                with col2:
                    end_date = st.date_input(
                        "At which date should the chart end?",
                        datetime.date(2023, 4, 28), max_value=datetime.date.today())
            with st.container():
                col1, col2 = st.columns(2)
                with col1:
                    start_time = st.time_input("At which time should the chart start?", datetime.time(00, 00, 00))
                with col2:
                    end_time = st.time_input("at which time should the chart end?", datetime.time(15, 00, 00))

        if st.sidebar.button("Submit"):
            temp_start_date_time = datetime.datetime.combine(start_date, start_time)
            start_date_time = str(temp_start_date_time).replace(" ", "T") + "+00:00"
            temp_end_date_time = datetime.datetime.combine(end_date, end_time)
            new_temp_end_date_time = temp_end_date_time
            end_date_time = str(new_temp_end_date_time).replace(" ", "T") + "+00:00"
            print(start_date_time)
            print(end_date_time)

            sample = fetch(session,
                           f"http://127.0.0.1:8084/investment/{stocks_category[option]}/{start_date_time}/{end_date_time}/{trading_option}")
            try:
                sample_data = pd.read_json(sample, orient="columns")
                state.sample_data = sample_data
                sample_data = state.sample_data
            except:
                st.error("Sorry, no data available. We are working on it")

            # update the session state with new sample_data

        # use the session state to access sample_data

        # Navigation Bar
        with st.sidebar:
            choose = option_menu("Trading Strategy",
                                 ["Home", "Chat Bot", "Support and Resistance", "Momentum", "Bollinger", "Paper Trading",
                                  "Account Details"])

        if choose == "Home":
            st.header("Hallo")

        elif choose == "Chat Bot":
            st.header("Chat-Bot")
            with open(".secrets.toml", "r") as f:
                config = toml.load(f)
            openai.api_key = config["OPENAI_KEY"]

            def generate_response(prompt):
                completions = openai.Completion.create(
                    engine="text-davinci-003",
                    prompt=prompt,
                    max_tokens=1024,
                    n=1,
                    stop=None,
                    temperature=0.5,
                )
                message = completions.choices[0].text
                return message

            # Creating the chatbot interface
            st.title("chatBot : Streamlit + openAI")

            # Storing the chat
            if 'generated' not in st.session_state:
                st.session_state['generated'] = []

            if 'past' not in st.session_state:
                st.session_state['past'] = []

            # We will get the user's input by calling the get_text function
            def get_text():
                input_text = st.text_input("You: ", "Hello, how are you?", key="input")
                return input_text

            user_input = get_text()

            if user_input:
                output = generate_response(user_input)
                # store the output
                st.session_state.past.append(user_input)
                st.session_state.generated.append(output)

            if st.session_state['generated']:

                for i in range(len(st.session_state['generated']) - 1, -1, -1):
                    message(st.session_state["generated"][i], key=str(i))
                    message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')


        elif choose == "Support and Resistance":
            try:

                support_and_resistance_algorithm(option, sample_data)
            except:
                st.warning("Please submit the form to see the results")



        elif choose == "Momentum":
            st.title('Momentum')
            try:
                # Calling the momentum method
                sample_data = apply_momentum_strategy(sample_data)
                st.write(sample_data)

                # Create chart data from sample data

                chart_data = st.line_chart(sample_data['Cumulative Returns'])

                # Add buy and sell signals to chart data
                chart_data = add_signals_to_chart(chart_data, sample_data)
            except Exception:
                st.warning("Please submit the form to see the results")

        elif choose == "Paper Trading":
            st.write('Paper Trading')
            st.write("Enter your Alpaca API and secret keys to get started.")
            st.write("After authentication, you can enter your trading information and execute trades.")

            # Create input fields for the user to enter their API and secret keys
            trading_platform()

        elif choose == "Bollinger":
            try:
                st.title("Bollinger Bands Breakout")
                # sample_data = fetch(session, f"http://127.0.0.1:8084/investment/ETH-USD")
                df = pd.DataFrame(sample_data)
                rolling_mean, upper_band, lower_band = calc_bollinger_bands(df)

                buy_signal, sell_signal = bollinger_strategy_signals(upper_band, lower_band, df)
                buy_markers, sell_markers = bollinger_marker_return(df, buy_signal, sell_signal)

                fig = go.Figure()
                draw_lines(df, fig, rolling_mean)
                draw_bollinger_bands(fig, df, upper_band, lower_band)
                draw_signals(fig, buy_markers, sell_markers)
                fig.update_layout(title=option, xaxis_title='Timestamp', yaxis_title='Price')
                st.plotly_chart(fig)
            except:
                st.warning("Please submit the form to see the results")


        elif choose == "Account Details":
            tab1, tab2, tab3 = st.tabs(["Account Details", "Open Orders", "Closed Orders"])
            with tab1:
                st.subheader("Account Details")
                sample: dict = fetch(session,
                                     f"http://127.0.0.1:8084/investment/account")
                sample = sample.get('_raw')
                col1, col2 = st.columns(2)
                with col1:
                    st.write('Account Number: ')
                with col2:
                    st.write(sample.get('account_number'))
                col1, col2 = st.columns(2)
                with col1:
                    st.write('Cash: ')
                with col2:
                    st.write(sample.get('cash'))
                col1, col2 = st.columns(2)
                with col1:
                    st.write('Daytrade count: ')
                with col2:
                    day_trade_count: int = sample.get('daytrade_count')
                    st.write(str(day_trade_count))
                col1, col2 = st.columns(2)
                with col1:
                    st.write('Status: ')
                with col2:
                    st.write(sample.get('status'))
                col1, col2 = st.columns(2)
                with col1:
                    st.write("Portfolio development: ")

                with col2:
                    new_equity: float = float(sample.get('equity')) - float(sample.get('last_equity'))
                    st.write(str(new_equity))
            with tab2:
                st.subheader("Open Orders")
                open_order = "open"
                sample: dict = fetch(session,
                                     f"http://127.0.0.1:8084/investment/orders/{open_order}")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write("Symbol")
                with col2:
                    st.write("Quantity")
                with col3:
                    st.write("Executed at (UTC Time)")

                if sample == []:
                    st.warning("No open orders")
                for row in sample:
                    open_order: dict = row.get('_raw')

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(open_order.get('symbol'))
                    with col2:
                        st.write(open_order.get('qty'))
                    with col3:
                        date: str = open_order.get('submitted_at')
                        date = date.replace("T", " ")
                        date = date.removesuffix("Z")
                        date = date.split(".")[0]
                        st.write(date)

            with tab3:
                st.subheader("Closed Orders")
                closed = 'closed'
                sample: dict = fetch(session,
                                     f"http://127.0.0.1:8084/investment/orders/{closed}")

                col1, col2 = st.columns(2)
                with col1:
                    st.write("Symbol")
                with col2:
                    st.write("Executed at (UTC Time)")
                if sample == []:
                    st.warning("No closed orders")
                else:
                    for row in sample:
                        open_order: dict = row.get('_raw')

                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(open_order.get('symbol'))
                    with col2:
                        date: str = open_order.get('submitted_at')
                        date = date.replace("T", " ")
                        date = date.removesuffix("Z")
                        date = date.split(".")[0]
                        st.write(date)

    # ------METHODS--------------------

    # ------------------------------------------------------------------------------

    # Resistance and Support Indicator

    # -------------------------------------------------------------------
    # Bollinger Bands
    # -------------------------------------------------------------------
    def draw_lines(df, fig, rolling_mean):
        fig.add_trace(go.Scatter(x=df.index, y=df['close'], mode='lines', name='Close'))
        fig.add_trace(go.Scatter(x=df.index, y=rolling_mean, mode='lines', name='Rolling Mean'))
        return fig


    def draw_bollinger_bands(fig, df, upper_band, lower_band):
        fig.add_trace(go.Scatter(x=df.index, y=upper_band, mode='lines', name='Upper Band'))
        fig.add_trace(go.Scatter(x=df.index, y=lower_band, mode='lines', name='Lower Band'))
        return fig


    def draw_signals(fig, buy_markers, sell_markers):
        fig.add_trace(buy_markers)
        fig.add_trace(sell_markers)
        return fig


    def calc_bollinger_bands(df, window_size=20, num_std=2):
        rolling_mean = df["close"].rolling(window=window_size).mean()
        rolling_std = df["close"].rolling(window=window_size).std()
        upper_band = rolling_mean + (rolling_std * num_std)
        lower_band = rolling_mean - (rolling_std * num_std)

        return rolling_mean, upper_band, lower_band


    def bollinger_marker_return(df, buy_signal, sell_signal):
        buy_markers = go.Scatter(
            x=df.index,
            y=buy_signal,
            mode='markers',
            name='Buy Signals',
            marker=dict(
                symbol='triangle-up',
                size=10,
                color='green'
            )
        )

        sell_markers = go.Scatter(
            x=df.index,
            y=sell_signal,
            mode='markers',
            name='Sell Signals',
            marker=dict(
                symbol='triangle-down',
                size=10,
                color='red'
            )
        )

        return buy_markers, sell_markers


    def bollinger_strategy_signals(upper_band, lower_band, df):
        buy_signal = []
        sell_signal = []
        for i in range(len(df)):
            if df['close'][i] > upper_band[i]:
                sell_signal.append(np.nan)
                if i > 0 and df['close'][i - 1] <= upper_band[i - 1]:
                    buy_signal.append(df['close'][i])
                else:
                    buy_signal.append(np.nan)
            elif df['close'][i] < lower_band[i]:
                buy_signal.append(np.nan)
                if i > 0 and df['close'][i - 1] >= lower_band[i - 1]:
                    sell_signal.append(df['close'][i])
                else:
                    sell_signal.append(np.nan)
            else:
                buy_signal.append(np.nan)
                sell_signal.append(np.nan)
        return buy_signal, sell_signal


    if __name__ == '__main__':
        main()

elif authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')
