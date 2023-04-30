import numpy as np
import plotly.graph_objs as go

def calculate_stochastic(df, n=14):
    """
    Calculates the Stochastic Oscillator for a given DataFrame.

    Parameters:
    df (pandas.DataFrame): DataFrame with columns for 'high', 'low', and 'close' prices.
    n (int): The number of periods to use for calculating the Stochastic Oscillator. Default is 14.

    Returns:
    pandas.DataFrame: DataFrame with columns for '%K' and '%D' values.
    """
    # Calculate the lowest low and highest high over the past n periods
    lowest_low = df['low'].rolling(window=n, min_periods=0).min()
    highest_high = df['high'].rolling(window=n, min_periods=0).max()

    # Calculate the %K value
    k_percent = 100 * ((df['close'] - lowest_low) / (highest_high - lowest_low))

    # Calculate the %D value using a 3-period simple moving average
    d_percent = k_percent.rolling(window=3, min_periods=0).mean()

    # Add the %K and %D values to the DataFrame
    df['%K'] = k_percent
    df['%D'] = d_percent

    return df[['%K', '%D']]

def apply_momentum_strategy(df):
    # Calculate Stochastic Oscillator
    stochastic_df = calculate_stochastic(df, n=14)
    df['%K'] = stochastic_df['%K']
    df['%D'] = stochastic_df['%D']

    # Calculate MACD
    slow_window = 26
    fast_window = 12
    signal_window = 9
    exp1 = df['close'].ewm(span=fast_window, adjust=False).mean()
    exp2 = df['close'].ewm(span=slow_window, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=signal_window, adjust=False).mean()
    histogram = macd - signal
    df['MACD'] = macd
    df['Signal'] = signal
    df['Histogram'] = histogram

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

