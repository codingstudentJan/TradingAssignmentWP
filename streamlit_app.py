import streamlit as st
import requests
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from streamlit_option_menu import option_menu
import plotly.express as px
import numpy as np
import matplotlib.pyplot as plt
from math import floor


def fetch(session, url):
    try:
        result = session.get(url)
        return result.json()
    except Exception:
        print("Data Fetching failed")

session = requests.Session()
sample_data = fetch(session,"http://127.0.0.1:8084/investment")
momentum_data = fetch(session, "http://127.0.0.1:8084/momentum")
aapl = pd.DataFrame(momentum_data)

def main():
    # Navigation Bar
    with st.sidebar:
        choose = option_menu("Indicators", ["Support and Resistance", "Bowling","Momentum","Balance"],
                             icons=['pencil-fill', 'bar-chart-fill','bookmarks-fill', 'piggy-bank-fill'],
                             menu_icon="coin", default_index=0,
                             styles={
            "container": {"padding": "5!important", "background-color": "#bfcce3"},
            "icon": {"color": "black", "font-size": "25px"}, 
            "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "#7596bd"},
      }
     )

    if choose == "Support and Resistance":
        st.title("Support and Resistance")
        new_df = pd.DataFrame(sample_data)
        support_levels = []
        resistance_levels = []
        filling_support_resistance_array_with_data(new_df, resistance_levels, support_levels)

        print(new_df)
        new_df.plot(x='timestamp', y='low', kind='line')
        chart = px.line()
        chart.add_scatter(x=new_df['timestamp'], y=new_df['low'], mode='lines', line_color = 'blue', name = 'Lowest Price')
        chart.add_scatter(x=new_df['timestamp'], y=new_df['high'], mode='lines', line_color = 'violet', name = 'Highest Price')
        adding_support_resistance_lines(chart, new_df, resistance_levels, support_levels)
        st.write(chart)


    elif choose == "Bowling":
        st.title("Expenses")

    
    elif choose == "Momentum":
        st.title("Momentum")
        aapl_ret = pd.DataFrame(np.diff(aapl['close'])).rename(columns = {0:'returns'})
        stoch_macd_strategy_ret = []
        

        plot_data = aapl[aapl.index >= '2020-01-01']
        plot_data.rename(columns={'datetime':'timestamp'}, inplace=True)
        st.write(plot_data)

        st.write('AAPL STOCK PRICES')
        chart4 = px.line()
        chart4.add_scatter(x=plot_data['timestamp'], y=plot_data['close'], mode='lines', line_color = 'blue', name = 'Close')
        st.write(chart4)

        st.write(f'AAPL STOCH 14,3')
        chart5 = px.line()
        chart5.add_scatter(x=plot_data['timestamp'], y=plot_data['%k'], mode='lines', line_color = 'blue', name = '%K')
        chart5.add_scatter(x=plot_data['timestamp'], y=plot_data[f"%d"], mode='lines', line_color = 'orange', name = "%D")
        st.write(chart5)

        st.write('AAPL MACD 26,12,9')
        chart = px.line()
        chart.add_scatter(x=plot_data['timestamp'], y=plot_data['macd'], mode='lines', line_color = 'blue', name = 'macd')
        chart.add_scatter(x=plot_data['timestamp'], y=plot_data['macd_signal'], mode='lines', line_color = 'orange', name = "signal")
        chart.add_scatter(x=plot_data['timestamp'], y=plot_data['macd_hist'], mode='lines', line_color = 'violet', name = "hist")
        st.write(chart)

        st.write("Momentum Strategy")
        strategy.head()
        strategy[-75:-70]
        
        for i in range(len(aapl_ret)):
            try:
                returns = aapl_ret['returns'][i] * strategy['stoch_macd_position'][i]
                stoch_macd_strategy_ret.append(returns)
            except:
                pass

        stoch_macd_strategy_ret_df = pd.DataFrame(stoch_macd_strategy_ret).rename(columns = {0:'stoch_macd_returns'})
        investment_value = 100000
        number_of_stocks = floor(investment_value / aapl['close'][0])
        stoch_macd_investment_ret = []

        for i in range(len(stoch_macd_strategy_ret_df['stoch_macd_returns'])):
            returns = number_of_stocks * stoch_macd_strategy_ret_df['stoch_macd_returns'][i]
            stoch_macd_investment_ret.append(returns)

        stoch_macd_investment_ret_df = pd.DataFrame(stoch_macd_investment_ret).rename(columns = {0:'investment_returns'})
        total_investment_ret = round(sum(stoch_macd_investment_ret_df['investment_returns']), 2)
        profit_percentage = floor((total_investment_ret / investment_value) * 100)
        st.write('Profit gained from the STOCH MACD strategy by investing $100k in AAPL : {}'.format(total_investment_ret))
        st.write('Profit percentage of the STOCH MACD strategy : {}%'.format(profit_percentage))

    elif choose == "Balance":
        st.title("Transaction Details")

# ------METHODS--------------------


# Momentum Strategy

# 1. STOCHASTIC OSCILLATOR CALCULATION

def get_stoch_osc(high, low, close, k_lookback, d_lookback):
    lowest_low = low.rolling(k_lookback).min()
    highest_high = high.rolling(k_lookback).max()
    k_line = ((close - lowest_low) / (highest_high - lowest_low)) * 100
    d_line = k_line.rolling(d_lookback).mean()
    return k_line, d_line

aapl['%k'], aapl['%d'] = get_stoch_osc(aapl['high'], aapl['low'], aapl['close'], 14, 3)


# 2. MACD CALCULATION

def get_macd(price, slow, fast, smooth):
    exp1 = price.ewm(span = fast, adjust = False).mean()
    exp2 = price.ewm(span = slow, adjust = False).mean()
    macd = pd.DataFrame(exp1 - exp2).rename(columns = {'close':'macd'})
    signal = pd.DataFrame(macd.ewm(span = smooth, adjust = False).mean()).rename(columns = {'macd':'signal'})
    hist = pd.DataFrame(macd['macd'] - signal['signal']).rename(columns = {0:'hist'})
    return macd, signal, hist

aapl['macd'] = get_macd(aapl['close'], 26, 12, 9)[0]
aapl['macd_signal'] = get_macd(aapl['close'], 26, 12, 9)[1]
aapl['macd_hist'] = get_macd(aapl['close'], 26, 12, 9)[2]
aapl = aapl.dropna()

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
            
buy_price, sell_price, stoch_macd_signal = implement_stoch_macd_strategy(aapl['close'], aapl['%k'], aapl['%d'], aapl['macd'], aapl['macd_signal'])

# 4. POSITION

position = []
for i in range(len(stoch_macd_signal)):
    if stoch_macd_signal[i] > 1:
        position.append(0)
    else:
        position.append(1)
        
for i in range(len(aapl['close'])):
    if stoch_macd_signal[i] == 1:
        position[i] = 1
    elif stoch_macd_signal[i] == -1:
        position[i] = 0
    else:
        position[i] = position[i-1]
        
close_price = aapl['close']
k_line = aapl['%k']
d_line = aapl['%d']
macd_line = aapl['macd']
signal_line = aapl['macd_signal']
stoch_macd_signal = pd.DataFrame(stoch_macd_signal).rename(columns = {0:'stoch_macd_signal'}).set_index(aapl.index)
position = pd.DataFrame(position).rename(columns = {0:'stoch_macd_position'}).set_index(aapl.index)

frames = [close_price, k_line, d_line, macd_line, signal_line, stoch_macd_signal, position]
strategy = pd.concat(frames, join = 'inner', axis = 1)


# ------------------------------------------------------------------------------

# Resistance and Support Strategy
def adding_support_resistance_lines(chart, new_df, resistance_levels, support_levels):
    for level in support_levels:
        print(new_df['timestamp'][level[1]])
        print(new_df['timestamp'][-1])
        chart.add_shape(type="line", y0=level[0], y1=level[0], x0=pd.to_datetime(new_df['timestamp'][level[1]]),
                        x1=pd.to_datetime(new_df['timestamp'][-1]), line_dash="dash", line_color="green")
    for level in resistance_levels:
        chart.add_shape(type="line", y0=level[0], y1=level[0], x0=pd.to_datetime(new_df['timestamp'][level[1]]),
                        x1=pd.to_datetime(new_df['timestamp'][-1]), line_dash="dash", line_color="red")


def filling_support_resistance_array_with_data(new_df, resistance_levels, support_levels):
    for i in range(2, new_df.shape[0] - 2):
        if is_support(new_df, i):
            low = new_df['low'][i]
            row_number = i
            support_levels.append([low, i])
        elif is_resistance(new_df, i):
            high = new_df['high'][i]
            row_number = i
            resistance_levels.append([high, i])


def is_support(new_df, i: int):
    # get bullish fractal
    candle1 = new_df['low'][i] < new_df['low'][i+1]
    candle2 = new_df['low'][i] < new_df['low'][i-1]
    candle3 = new_df['low'][i+1] < new_df['low'][i+2]
    candle4 = new_df['low'][i-1] < new_df['low'][i-2]
    return (candle1 and candle2 and candle3 and candle4)

def is_resistance(new_df, i: int):
    candle1 = new_df['high'][i] > new_df['high'][i+1]
    candle2 = new_df['high'][i] > new_df['high'][i-1]
    candle3 = new_df['high'][i+1] > new_df['high'][i+2]
    candle4 = new_df['high'][i-1] > new_df['high'][i-2]
    return (candle1 and candle2 and candle3 and candle4)

if __name__ == '__main__':
    main()