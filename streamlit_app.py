from math import floor
from typing import List

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import requests
import streamlit as st
from streamlit_option_menu import option_menu


def fetch(session, url):
    try:
        result = session.get(url)
        return result.json()
    except Exception:
        print("Data Fetching failed")


session = requests.Session()

# dictionary for the categories
stocks_category = {
    'Stocks Apple': 'AAPL',
    'Stocks Amazon': 'AMZN',
    'Stocks Google': 'GOOGL',
    'Stocks Goldman Sachs': 'GS',
    'Stocks META': 'META',
    'Stocks Microsoft': 'MSFT',
    'Stocks Nike': 'NKE',
    'Stocks Pfizer': 'PFE',
    'Stocks Procter and Gamble': 'PG',
    'Stocks Tesla': 'TSLA',
    'Stocks Walmart': 'WMT',
    'Forex Euro/USD': 'EUR-USD',
    'Forex  Gold Spot': 'XAU-USD',
    'Crypto Bitcoin/USD': 'BTC-USD',
    'Crypto Ethereum/Bitcoin': 'ETH-BTC',
    'ETF SPDR S&P 500 ETF Trust': 'SPY',
    'ETF Vanguard Total Stock Market Index Fund ETF Shares': 'VTI',
    'Indices NASDAQ Composite': 'IXIC',
    'Indices S&P 500': 'SPX'
}


def main():
    with open(r"C:\Users\User\Desktop\4.Semester\Web_Programming\TraderJoe\style.css") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    option = st.selectbox(
        'Which Stock, Forex, Crypto, ETF, or indices would you like to trade?',
        stocks_category.keys())
    option = option.replace("/", "-")
    sample_data = fetch(session, f"http://127.0.0.1:8084/investment/{stocks_category[option]}")
    st.write('You selected:', option)

    # Navigation Bar
    with st.sidebar:
        choose = option_menu("Trading Strategy", ["Support and Resistance", "Momentum", "Bollinger"],
                             icons=['pencil-fill', 'bar-chart-fill', 'bookmarks-fill', 'piggy-bank-fill',
                                    'pencil-fill'],
                             menu_icon="coin", default_index=0,
                             styles={
                                 "container": {"padding": "5!important", "background-color": "#007bff"},
                                 "icon": {"color": "black", "font-size": "25px"},
                                 "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px",
                                              "--hover-color": "#eee"},
                                 "nav-link-selected": {"background-color": "#7596bd"},
                             }
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
                        resistance[0] * bottom_line <= support[0] * up_line <= resistance[0] * up_line) and support[1] > \
                            resistance[1]:
                        supports_to_remove.append(support)
            for support in supports_to_remove:
                support_levels.remove(support)

        def remove_duplicate_resistances(bottom_line, resistance_levels, resistances_to_remove, support_levels,
                                         up_line):
            for support in support_levels:
                for resistance in resistance_levels:
                    if (support[0] * bottom_line <= resistance[0] * bottom_line <= support[0] * up_line or
                        support[0] * bottom_line <= resistance[0] * up_line <= support[0] * up_line) and resistance[1] > \
                            support[1]:
                        resistances_to_remove.append(resistance)
            for resistance in resistances_to_remove:
                resistance_levels.remove(resistance)

        def adding_support_resistance_lines(chart, new_df, resistance_levels, support_levels, bottom_factor, up_factor):
            for level in support_levels:
                print(new_df['datetime'][level[1]])
                print(new_df['datetime'][-1])
                bottom_factor = bottom_factor
                up_factor = up_factor
                chart.add_shape(type="line", y0=level[0], y1=level[0], x0=pd.to_datetime(new_df['datetime'][level[1]]),
                                x1=pd.to_datetime(new_df['datetime'][-1]), line_dash="dash", line_color="green")
                chart.add_shape(type="rect", y0=level[0] * bottom_factor, y1=level[0] * up_factor,
                                x0=pd.to_datetime(new_df['datetime'][level[1]]),
                                x1=pd.to_datetime(new_df['datetime'][-1]), line=dict(color="#90EE90", width=2),
                                fillcolor="rgba(144,238,144,0.2)")
            for level in resistance_levels:
                chart.add_shape(type="line", y0=level[0], y1=level[0], x0=pd.to_datetime(new_df['datetime'][level[1]]),
                                x1=pd.to_datetime(new_df['datetime'][-1]), line_dash="dash", line_color="red")
                chart.add_shape(type="rect", y0=level[0] * bottom_factor, y1=level[0] * up_factor,
                                x0=pd.to_datetime(new_df['datetime'][level[1]]),
                                x1=pd.to_datetime(new_df['datetime'][-1]), line=dict(color="red", width=2),
                                fillcolor="rgba(255, 0, 0, 0.2)")

        # Setup of the page and for computation with algorithm
        st.title("Support and Resistance")
        new_df = pd.DataFrame(sample_data)
        support_levels = []
        resistance_levels = []

        # Setting the boundaries (percentage of price found as support/resistance) for rectangle zones of supports
        # and resistances

        bottom_line = 0.9886
        up_line = 1.007

        safe_extrema_number = st.number_input("Insert Safe Support/Resistance number", value=3, min_value=3,
                                              max_value=5, step=1,
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

        # Generating the chart based on the Arrays and the Dataframe
        chart = px.line()
        chart.update_layout(title=option, xaxis_title='Date', yaxis_title='Price')
        chart.add_scatter(x=new_df['datetime'], y=new_df['low'], mode='lines', line_color='blue', name='Lowest Price')
        chart.add_scatter(x=new_df['datetime'], y=new_df['high'], mode='lines', line_color='violet',
                          name='Highest Price')
        adding_support_resistance_lines(chart, new_df, resistance_levels, support_levels, bottom_line, up_line)
        st.write(chart)





    elif choose == "Momentum":
        # Momentum Strategy Methods

        # specific data frame for momentum strategy
        momentum_data = pd.DataFrame(sample_data)

        # 1. STOCHASTIC OSCILLATOR CALCULATION

        def get_stoch_osc(high, low, close, k_lookback, d_lookback):
            lowest_low = low.rolling(k_lookback).min()
            highest_high = high.rolling(k_lookback).max()
            k_line = ((close - lowest_low) / (highest_high - lowest_low)) * 100
            d_line = k_line.rolling(d_lookback).mean()
            return k_line, d_line

        momentum_data['%k'], momentum_data['%d'] = get_stoch_osc(momentum_data['high'], momentum_data['low'],
                                                                 momentum_data['close'], 14, 3)

        # 2. MACD CALCULATION

        def get_macd(price, slow, fast, smooth):
            exp1 = price.ewm(span=fast, adjust=False).mean()
            exp2 = price.ewm(span=slow, adjust=False).mean()
            macd = pd.DataFrame(exp1 - exp2).rename(columns={'close': 'macd'})
            signal = pd.DataFrame(macd.ewm(span=smooth, adjust=False).mean()).rename(columns={'macd': 'signal'})
            hist = pd.DataFrame(macd['macd'] - signal['signal']).rename(columns={0: 'hist'})
            return macd, signal, hist

        momentum_data['macd'] = get_macd(momentum_data['close'], 26, 12, 9)[0]
        momentum_data['macd_signal'] = get_macd(momentum_data['close'], 26, 12, 9)[1]
        momentum_data['macd_hist'] = get_macd(momentum_data['close'], 26, 12, 9)[2]
        momentum_data = momentum_data.dropna()

        # 3. TRADING STRATEGY

        def implement_stoch_macd_strategy(prices, k, d, macd, macd_signal):
            buy_price = []
            sell_price = []
            stoch_macd_signal = []
            signal = 0

            for i in range(len(prices)):
                if k[i] < 30 and d[i] < 30 and macd[i] < -2 and macd_signal[i] < -2:
                    if signal != 1:
                        buy_price.append(prices[i])
                        sell_price.append(np.nan)
                        signal = 1
                        stoch_macd_signal.append(signal)
                    else:
                        buy_price.append(np.nan)
                        sell_price.append(np.nan)
                        stoch_macd_signal.append(0)

                elif k[i] > 70 and d[i] > 70 and macd[i] > 2 and macd_signal[i] > 2:
                    if signal != -1 and signal != 0:
                        buy_price.append(np.nan)
                        sell_price.append(prices[i])
                        signal = -1
                        stoch_macd_signal.append(signal)
                    else:
                        buy_price.append(np.nan)
                        sell_price.append(np.nan)
                        stoch_macd_signal.append(0)

                else:
                    buy_price.append(np.nan)
                    sell_price.append(np.nan)
                    stoch_macd_signal.append(0)

            return buy_price, sell_price, stoch_macd_signal

        buy_price, sell_price, stoch_macd_signal = implement_stoch_macd_strategy(momentum_data['close'],
                                                                                 momentum_data['%k'],
                                                                                 momentum_data['%d'],
                                                                                 momentum_data['macd'],
                                                                                 momentum_data['macd_signal'])

        # 4. POSITION

        position = []
        for i in range(len(stoch_macd_signal)):
            if stoch_macd_signal[i] > 1:
                position.append(0)
            else:
                position.append(1)

        for i in range(len(momentum_data['close'])):
            if stoch_macd_signal[i] == 1:
                position[i] = 1
            elif stoch_macd_signal[i] == -1:
                position[i] = 0
            else:
                position[i] = position[i - 1]

        close_price = momentum_data['close']
        k_line = momentum_data['%k']
        d_line = momentum_data['%d']
        macd_line = momentum_data['macd']
        signal_line = momentum_data['macd_signal']
        stoch_macd_signal = pd.DataFrame(stoch_macd_signal).rename(columns={0: 'stoch_macd_signal'}).set_index(
            momentum_data.index)
        position = pd.DataFrame(position).rename(columns={0: 'stoch_macd_position'}).set_index(momentum_data.index)

        frames = [close_price, k_line, d_line, macd_line, signal_line, stoch_macd_signal, position]
        strategy = pd.concat(frames, join='inner', axis=1)

        # -----------Momentum Output--------

        st.title("Momentum")
        momentum_ret = pd.DataFrame(np.diff(momentum_data['close'])).rename(columns={0: 'returns'})
        stoch_macd_strategy_ret = []

        plot_data = momentum_data[momentum_data.index >= '2020-01-01']

        st.write(option, ' PRICES')
        price_chart = px.line()
        price_chart.update_layout(title=option, xaxis_title='Date', yaxis_title='Price')
        price_chart.add_scatter(x=plot_data['datetime'], y=plot_data['close'], mode='lines', line_color='blue',
                                name='Close')
        st.write(price_chart)

        st.write(option, f' STOCH 14,3')
        stoch_chart = px.line()
        stoch_chart.update_layout(title=option, xaxis_title='Date', yaxis_title='stoch')
        stoch_chart.add_scatter(x=plot_data['datetime'], y=plot_data[f"%k"], mode='lines', line_color='blue', name='%K')
        stoch_chart.add_hline(y=70, line_dash="dot",
                              annotation_text="Jan 1, 2018 baseline",
                              annotation_position="bottom right",
                              annotation_font_size=20,
                              annotation_font_color="blue"
                              )
        stoch_chart.add_scatter(x=plot_data['datetime'], y=plot_data[f"%d"], mode='lines', line_color='orange',
                                name="%D")
        st.write(stoch_chart)

        st.write(option, ' MACD 26,12,9')
        macd_chart = px.line()
        macd_chart.update_layout(title=option, xaxis_title='Date', yaxis_title='macd')
        macd_chart.add_scatter(x=plot_data['datetime'], y=plot_data['macd'], mode='lines', line_color='blue',
                               name='macd')
        macd_chart.add_scatter(x=plot_data['datetime'], y=plot_data['macd_signal'], mode='lines', line_color='orange',
                               name="signal")
        macd_chart.add_scatter(x=plot_data['datetime'], y=plot_data['macd_hist'], mode='lines', line_color='violet',
                               name="hist")
        st.write(macd_chart)

        st.write("Back Testing Momentum Strategy")
        for i in range(len(momentum_ret)):
            try:
                returns = momentum_ret['returns'][i] * strategy['stoch_macd_position'][i]
                stoch_macd_strategy_ret.append(returns)
            except:
                pass

        stoch_macd_strategy_ret_df = pd.DataFrame(stoch_macd_strategy_ret).rename(columns={0: 'stoch_macd_returns'})
        investment_value = 100000
        number_of_stocks = floor(investment_value / momentum_data['close'][0])
        stoch_macd_investment_ret = []

        for i in range(len(stoch_macd_strategy_ret_df['stoch_macd_returns'])):
            returns = number_of_stocks * stoch_macd_strategy_ret_df['stoch_macd_returns'][i]
            stoch_macd_investment_ret.append(returns)

        stoch_macd_investment_ret_df = pd.DataFrame(stoch_macd_investment_ret).rename(columns={0: 'investment_returns'})
        total_investment_ret = round(sum(stoch_macd_investment_ret_df['investment_returns']), 2)
        profit_percentage = floor((total_investment_ret / investment_value) * 100)
        st.write(
            'Profit gained from the STOCH MACD strategy by investing $100k in', option,
            ': {}'.format(total_investment_ret))
        st.write('Profit percentage of the STOCH MACD strategy : {}%'.format(profit_percentage))


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
