import pandas as pd
from typing import List

import pandas as pd
import plotly.express as px
import streamlit as st


def support_and_resistance_algorithm(option, sample_data):
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

        # print("Support Levels davor", support_levels)
        for i in range(0, len(support_levels)):
            if support_levels[i] != [0, 0, 0]:
                support_copy.append(support_levels[i])
        support_levels = []
        for i in range(0, len(support_copy)):
            if support_copy[i][2] >= safe_extrema_number:
                support_levels.append(support_copy[i])
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

        for i in range(0, len(resistance_levels)):
            if resistance_levels[i] != [0, 0, 0]:
                resistance_copy.append(resistance_levels[i])
        resistance_levels = []
        for i in range(0, len(resistance_copy)):
            if resistance_copy[i][2] >= safe_extrema_number:
                resistance_levels.append(resistance_copy[i])
        # print("Resistance Levels danach", resistance_levels)
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
    support_levels = []
    resistance_levels = []
    # Setting the boundaries (percentage of price found as support/resistance) for rectangle zones of supports
    # and resistances
    bottom_line = 0.99886
    up_line = 1.0007
    safe_extrema_number = st.number_input("Insert Safe Support/Resistance number", value=1, min_value=1,
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
        for i in range(1, new_df.shape[0]):
            if new_df['low'][i - 1] < (support[0] * bottom_line) and new_df['low'][i] > support[0] * bottom_line:
                sell_signal_supports = pd.concat([sell_signal_supports, new_df.iloc[[i]]])
    for support in support_levels:
        for i in range(1, new_df.shape[0]):
            if new_df['low'][i - 1] > (support[0] * up_line) and new_df['low'][i] < support[0] * up_line:
                buy_signal_supports = pd.concat([buy_signal_supports, new_df.iloc[[i - 1]]])
    for resistance in resistance_levels:
        for i in range(1, new_df.shape[0]):
            if new_df['high'][i - 1] < (resistance[0] * bottom_line) and new_df['high'][i] > resistance[
                0] * bottom_line:
                sell_signal_resistances = pd.concat([sell_signal_resistances, new_df.iloc[[i]]])
    for resistance in resistance_levels:
        for i in range(1, new_df.shape[0]):
            if new_df['high'][i - 1] > (resistance[0] * up_line) and new_df['high'][i] < resistance[0] * up_line:
                buy_signal_resistances = pd.concat([buy_signal_resistances, new_df.iloc[[i - 1]]])
    # Generating the chart based on the Arrays and the Dataframe
    chart = px.line()
    chart.update_layout(title=option, xaxis_title='Date', yaxis_title='Price')
    chart.add_scatter(x=new_df['datetime'], y=new_df['low'], mode='lines', line_color='blue',
                      name='Lowest Price')
    chart.add_scatter(x=new_df['datetime'], y=new_df['high'], mode='lines', line_color='violet',
                      name='Highest Price')
    # print(buy_signal_supports[1])
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
