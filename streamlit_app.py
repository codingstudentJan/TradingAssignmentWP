import datetime
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
from momentum_strategy import apply_momentum_strategy, add_signals_to_chart
from support_and_resistance_file import support_and_resistance_algorithm
st.set_page_config(page_title="Prodigy Trade", page_icon="random")


def fetch(session, url):
    try:
        result = session.get(url)
        return result.json()
    except Exception:
        print("Data Fetching failed")


# hashed_passwords = stauth.Hasher(['abc123','def']).generate()

with open(r'C:\Users\User\Desktop\4.Semester\Web_Programming\TraderJoe\config.yaml') as file:
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

# dictionary for the categories
stocks_category = {
    'Stocks Apple': 'AAPL',
    'Stocks Amazon': 'AMZN',
    'Stocks META': 'META',
    'Stocks Microsoft': 'MSFT',
    'Stocks Tesla': 'TSLA',
    'ETF SPDR S&P 500 ETF Trust': 'SPY',
}
if authentication_status:
    def main():
        authenticator.logout('Logout', 'sidebar')
        # with open(r"C:\Users\User\Desktop\4.Semester\Web_Programming\TraderJoe\style.css") as f:
        #   st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        st.title("Welcome to Prodigy Trade!")
        filter_expander = st.expander(label="Click to filter")
        with filter_expander:

            with st.container():
                col1 = st.columns(1)
                option = st.selectbox(
                    'Which Stock, Forex, Crypto, ETF, or indices would you like to trade?',
                    stocks_category.keys())
                option = option.replace("/", "-")
            with st.container():
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input(
                        "At which date should the chart start?",
                        datetime.date(2023, 4, 1))
                with col2:
                    end_date = st.date_input(
                        "At whicht date should the chart end?",
                        datetime.date(2023,4,28), max_value=datetime.date.today())
            with st.container():
                col1, col2 = st.columns(2)
                with col1:
                    start_time = st.time_input("At which time should the chart start?", datetime.time(00, 00, 00))
                with col2:
                    end_time = st.time_input("at which time should the chart end?", datetime.time(15,00,00))
        temp_start_date_time = datetime.datetime.combine(start_date, start_time)
        start_date_time = str(temp_start_date_time).replace(" ", "T") + "+00:00"
        temp_end_date_time = datetime.datetime.combine(end_date, end_time)
        new_temp_end_date_time = temp_end_date_time
        end_date_time = str(new_temp_end_date_time).replace(" ", "T") + "+00:00"
        print(start_date_time)
        print(end_date_time)
        sample = fetch(session,
                       f"http://127.0.0.1:8084/investment/{stocks_category[option]}/{start_date_time}/{end_date_time}")
        sample_data = pd.read_json(sample, orient="columns")
        if not sample_data.shape[0] > 0:
            st.error("No Data, did you choose a too short timeframe?")
        # st.write('You selected:', option)

        # Navigation Bar
        with st.sidebar:
            choose = option_menu("Trading Strategy", ["Support and Resistance", "Momentum", "Bollinger"],
                                 icons=['pencil-fill', 'bar-chart-fill', 'bookmarks-fill',
                                        'pencil-fill'],
                                 menu_icon="coin", default_index=0,
                                 )

        if choose == "Support and Resistance":
            support_and_resistance_algorithm(option, sample_data)



        elif choose == "Momentum":
            st.title('Momentum')

            #Calling the momentum method
            sample_data = apply_momentum_strategy(sample_data)
            st.write(sample_data)

            # Create chart data from sample data
            chart_data = st.line_chart(sample_data['Cumulative Returns'])

            # Add buy and sell signals to chart data
            chart_data = add_signals_to_chart(chart_data, sample_data)




        elif choose == "Bollinger":
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
