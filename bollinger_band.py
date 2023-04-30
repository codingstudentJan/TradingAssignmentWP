import numpy as np
import plotly.graph_objs as go



def draw_lines(df, fig, rolling_mean):
    fig.add_trace(go.Scatter(x=df['datetime'], y=df['close'], mode='lines', name='Close'))
    fig.add_trace(go.Scatter(x=df['datetime'], y=rolling_mean, mode='lines', name='Rolling Mean'))
    return fig


def draw_bollinger_bands(fig, df, upper_band, lower_band):
    fig.add_trace(go.Scatter(x=df['datetime'], y=upper_band, mode='lines', name='Upper Band'))
    fig.add_trace(go.Scatter(x=df['datetime'], y=lower_band, mode='lines', name='Lower Band'))
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
        x=df['datetime'],
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
        x=df['datetime'],
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