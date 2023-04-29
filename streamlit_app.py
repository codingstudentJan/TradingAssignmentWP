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
                        datetime.date(2023,4,28))
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
            def filling_support_levels(new_df, support_levels, bottom_factor, up_factor, safe_extrema_number):
                support_copy: List = []
                for i in range(2, new_df.shape[0] - 2):
                    if is_support(new_df, i):
                        low = new_df['low'][i]
                        support_levels.append([low, i, 1])
                for i in range(0, len(support_levels)):
                    item = support_levels[i][0]
                    for j in range(i + 1, len(support_levels)):
                        if (support_levels[j][0] * bottom_factor <= item * bottom_factor <= support_levels[j][
                            0] * up_factor or \
                            support_levels[j][0] * bottom_factor <= item * up_factor <= support_levels[j][
                                0] * up_factor) and \
                                support_levels[i] != [0, 0, 0]:
                            support_levels[i][2] = support_levels[i][2] + 1
                            support_levels[j] = [0, 0, 0]

                print("Support Levels davor", support_levels)
                for i in range(0, len(support_levels)):
                    if support_levels[i] != [0, 0, 0]:
                        support_copy.append(support_levels[i])
                support_levels = []
                print("Leere Support Levels", support_levels)
                for i in range(0, len(support_copy)):
                    if support_copy[i][2] >= safe_extrema_number:
                        support_levels.append(support_copy[i])
                print("Support Levels danach", support_levels)
                return support_levels

            def filling_resistance_levels(new_df, resistance_levels, bottom_factor, up_factor, safe_extrema_number):
                resistance_copy: List = []
                for i in range(2, new_df.shape[0] - 2):
                    if is_resistance(new_df, i):
                        high = new_df['high'][i]
                        resistance_levels.append([high, i, 1])
                for i in range(0, len(resistance_levels)):
                    item = resistance_levels[i][0]
                    for j in range(i + 1, len(resistance_levels)):
                        if (resistance_levels[j][0] * bottom_factor <= item * bottom_factor <= resistance_levels[j][
                            0] * up_factor or \
                            resistance_levels[j][0] * bottom_factor <= item * up_factor <= resistance_levels[j][
                                0] * up_factor) and \
                                resistance_levels[i] != [0, 0, 0]:
                            resistance_levels[i][2] = resistance_levels[i][2] + 1
                            resistance_levels[j] = [0, 0, 0]

                print("Resistance Levels davor", resistance_levels)
                for i in range(0, len(resistance_levels)):
                    if resistance_levels[i] != [0, 0, 0]:
                        resistance_copy.append(resistance_levels[i])
                resistance_levels = []
                print("Leere Support Levels", resistance_levels)
                for i in range(0, len(resistance_copy)):
                    if resistance_copy[i][2] >= safe_extrema_number:
                        resistance_levels.append(resistance_copy[i])
                print("Resistance Levels danach", resistance_levels)
                return resistance_levels

            def is_support(new_df, i: int):
                # get bullish fractal
                candle1 = new_df['low'][i] < new_df['low'][i + 1]
                candle2 = new_df['low'][i] < new_df['low'][i - 1]
                candle3 = new_df['low'][i + 1] < new_df['low'][i + 2]
                candle4 = new_df['low'][i - 1] < new_df['low'][i - 2]
                return candle1 and candle2 and candle3 and candle4

            def is_resistance(new_df, i: int):
                candle1 = new_df['high'][i] > new_df['high'][i + 1]
                candle2 = new_df['high'][i] > new_df['high'][i - 1]
                candle3 = new_df['high'][i + 1] > new_df['high'][i + 2]
                candle4 = new_df['high'][i - 1] > new_df['high'][i - 2]
                return candle1 and candle2 and candle3 and candle4

            def remove_duplicate_supports(bottom_line, resistance_levels, support_levels, supports_to_remove, up_line):
                for resistance in resistance_levels:
                    for support in support_levels:
                        if (resistance[0] * bottom_line <= support[0] * bottom_line <= resistance[0] * up_line or
                            resistance[0] * bottom_line <= support[0] * up_line <= resistance[0] * up_line) and support[
                            1] > \
                                resistance[1]:
                            supports_to_remove.append(support)
                for support in supports_to_remove:
                    if support in support_levels:
                        support_levels.remove(support)

            def remove_duplicate_resistances(bottom_line, resistance_levels, resistances_to_remove, support_levels,
                                             up_line):
                for support in support_levels:
                    for resistance in resistance_levels:
                        if (support[0] * bottom_line <= resistance[0] * bottom_line <= support[0] * up_line or
                            support[0] * bottom_line <= resistance[0] * up_line <= support[0] * up_line) and resistance[
                            1] > \
                                support[1]:
                            resistances_to_remove.append(resistance)
                for resistance in resistances_to_remove:
                    if resistance in resistance_levels:
                        resistance_levels.remove(resistance)

            def adding_support_resistance_lines(chart, new_df, resistance_levels, support_levels, bottom_factor,
                                                up_factor):
                last_entry = new_df.shape[0] - 1
                for level in support_levels:
                    print(new_df['datetime'][level[1]])
                    print(new_df['datetime'][last_entry])
                    bottom_factor = bottom_factor
                    up_factor = up_factor
                    chart.add_shape(type="line", y0=level[0], y1=level[0],
                                    x0=pd.to_datetime(new_df['datetime'][level[1]]),
                                    x1=pd.to_datetime(new_df['datetime'][last_entry]), line_dash="dash",
                                    line_color="green")
                    chart.add_shape(type="rect", y0=level[0] * bottom_factor, y1=level[0] * up_factor,
                                    x0=pd.to_datetime(new_df['datetime'][level[1]]),
                                    x1=pd.to_datetime(new_df['datetime'][last_entry]),
                                    line=dict(color="#90EE90", width=2),
                                    fillcolor="rgba(144,238,144,0.2)")
                for level in resistance_levels:
                    chart.add_shape(type="line", y0=level[0], y1=level[0],
                                    x0=pd.to_datetime(new_df['datetime'][level[1]]),
                                    x1=pd.to_datetime(new_df['datetime'][last_entry]), line_dash="dash",
                                    line_color="red")
                    chart.add_shape(type="rect", y0=level[0] * bottom_factor, y1=level[0] * up_factor,
                                    x0=pd.to_datetime(new_df['datetime'][level[1]]),
                                    x1=pd.to_datetime(new_df['datetime'][last_entry]), line=dict(color="red", width=2),
                                    fillcolor="rgba(255, 0, 0, 0.2)")

            # Setup of the page and for computation with algorithm
            new_df = pd.DataFrame(sample_data)
            print(new_df)
            support_levels = []
            resistance_levels = []

            # Setting the boundaries (percentage of price found as support/resistance) for rectangle zones of supports
            # and resistances

            bottom_line = 0.99886
            up_line = 1.0007

            safe_extrema_number = st.number_input("Insert Safe Support/Resistance number", value=3, min_value=3,
                                                  max_value=10, step=1,
                                                  help="This number should help you add or remove supports and "
                                                       "resistances, based on how many times they are found in the "
                                                       "datasaet. This number represents how many times they should be "
                                                       "found to be sure it is a resistance or a support.")

            # Filling the Arrays with data
            support_levels = filling_support_levels(new_df, support_levels, bottom_line, up_line, safe_extrema_number)
            resistance_levels = filling_resistance_levels(new_df, resistance_levels, bottom_line, up_line,
                                                          safe_extrema_number)
            resistances_to_remove: List = []
            supports_to_remove: List = []

            # Remove duplicates from both Arrays (filtering)
            remove_duplicate_resistances(bottom_line, resistance_levels, resistances_to_remove, support_levels, up_line)
            remove_duplicate_supports(bottom_line, resistance_levels, support_levels, supports_to_remove, up_line)

            sell_signal_supports = pd.DataFrame()
            buy_signal_supports = pd.DataFrame()
            sell_signal_resistances = pd.DataFrame()
            buy_signal_resistances = pd.DataFrame()

            for support in support_levels:
                for i in range(1,new_df.shape[0]):
                    if new_df['low'][i-1] < (support[0] * bottom_line) and new_df['low'][i] > support[0] * bottom_line:
                        sell_signal_supports = pd.concat([sell_signal_supports, new_df.iloc[[i]]])

            for support in support_levels:
                for i in range(1,new_df.shape[0]):
                    if new_df['low'][i-1] > (support[0] * up_line) and new_df['low'][i] < support[0] * up_line:
                        buy_signal_supports= pd.concat([buy_signal_supports, new_df.iloc[[i-1]]])

            for resistance in resistance_levels:
                for i in range(1,new_df.shape[0]):
                    if new_df['high'][i-1] < (resistance[0] * bottom_line) and new_df['high'][i] > resistance[0] * bottom_line:
                        sell_signal_resistances = pd.concat([sell_signal_resistances, new_df.iloc[[i]]])

            for resistance in resistance_levels:
                for i in range(1,new_df.shape[0]):
                    if new_df['high'][i-1] > (resistance[0] * up_line) and new_df['high'][i] < resistance[0] * up_line:
                        buy_signal_resistances= pd.concat([buy_signal_resistances, new_df.iloc[[i-1]]])


            # Generating the chart based on the Arrays and the Dataframe
            chart = px.line()
            chart.update_layout(title=option, xaxis_title='Date', yaxis_title='Price')
            chart.add_scatter(x=new_df['datetime'], y=new_df['low'], mode='lines', line_color='blue',
                              name='Lowest Price')
            chart.add_scatter(x=new_df['datetime'], y=new_df['high'], mode='lines', line_color='violet',
                              name='Highest Price')
            #print(buy_signal_supports[1])
            print(buy_signal_supports)
            if buy_signal_supports.shape[0] > 0:
                chart.add_scatter(x=buy_signal_supports['datetime'], y=buy_signal_supports['low'],
                                    mode='markers', name='Buy Signals',
                marker=dict(
                    symbol='triangle-up',
                    size=8,
                    color='green'
                ))
            if sell_signal_supports.shape[0] > 0:
                chart.add_scatter(x=sell_signal_supports['datetime'], y=sell_signal_supports['low'],
                                  mode='markers', name='Sell Signals',
                                  marker=dict(
                                      symbol='triangle-down',
                                      size=8,
                                      color='red'
                                  ))
            if buy_signal_resistances.shape[0] > 0:
                chart.add_scatter(x=buy_signal_resistances['datetime'], y=buy_signal_resistances['high'],
                                  mode='markers', name='Buy Signals',
                                  marker=dict(
                                      symbol='triangle-up',
                                      size=8,
                                      color='green'
                                  ))
            if sell_signal_resistances.shape[0] > 0:
                chart.add_scatter(x=sell_signal_resistances['datetime'], y=sell_signal_resistances['high'],
                                  mode='markers', name='Sell Signals',
                                  marker=dict(
                                      symbol='triangle-down',
                                      size=8,
                                      color='red'
                                  ))
            adding_support_resistance_lines(chart, new_df, resistance_levels, support_levels, bottom_line, up_line)
            st.write(chart)



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
