import numpy as np
from ta.momentum import StochasticOscillator
from ta.trend import MACD
import plotly.graph_objs as go

# Define function to get data and apply momentum strategy
def apply_momentum_strategy(df):
    # Calculate Stochastic Oscillator
    stoch = StochasticOscillator(high=df['high'], low=df['low'], close=df['close'], window=14, smooth_window=3)
    df['%K'] = stoch.stoch()
    df['%D'] = stoch.stoch_signal()

     # Calculate MACD
    macd = MACD(df['close'], window_slow=26, window_fast=12, window_sign=9)
    df['MACD'] = macd.macd()
    df['Signal'] = macd.macd_signal()
    df['Histogram'] = macd.macd_diff()

    # Buy when %K is above %D and both are below 20
    df['Signal'] = np.where((df['%K'] > df['%D']) & (df['%K'] < 20) & (df['%D'] < 20), 1, 0)

    # Sell when %K is below %D and both are above 80
    df['Signal'] = np.where((df['%K'] < df['%D']) & (df['%K'] > 80) & (df['%D'] > 80), -1, df['Signal'])

    # Calculate daily returns
    df['Returns'] = df['close'].pct_change()

    # Calculate strategy returns
    df['Strategy Returns'] = df['Signal'].shift(1) * df['Returns']

    # Calculate cumulative returns
    df['Cumulative Returns'] = (1 + df['Strategy Returns']).cumprod() - 1

    return df
            
def add_signals_to_chart(chart_data, df, datetime_col='datetime'):
    # Create separate dataframes for buy and sell signals
    buy_signals = df[df['Signal'] == 1]
    sell_signals = df[df['Signal'] == -1]

    # Create scatter plot with different marker symbols for buy and sell signals
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=buy_signals[datetime_col], y=buy_signals['Cumulative Returns'],
                            mode='markers', marker=dict(symbol='triangle-up', size=10, color='green'), name='Buy'))
    fig.add_trace(go.Scatter(x=sell_signals[datetime_col], y=sell_signals['Cumulative Returns'],
                            mode='markers', marker=dict(symbol='triangle-down', size=10, color='red'), name='Sell'))
                
    # Add a line trace for cumulative returns
    fig.add_trace(go.Scatter(x=df[datetime_col], y=df['Cumulative Returns'], name='Cumulative Returns', line=dict(color='blue')))
                
    # Add title and axis labels
    fig.update_layout(title='Cumulative Returns with Buy and Sell Signals', xaxis_title='Date', yaxis_title='Cumulative Returns')
                
    # Show plot in Streamlit
    chart_data.plotly_chart(fig)
                
    return chart_data

