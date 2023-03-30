import streamlit as st
import requests
import pandas as pd
import datetime
from streamlit_option_menu import option_menu
import plotly.express as px
import numpy as np
import matplotlib.pyplot as plt


def fetch(session, url):
    try:
        result = session.get(url)
        return result.json()
    except Exception:
        print("Data Fetching failed")

session = requests.Session()
sample_data = fetch(session,"http://127.0.0.1:8084/investment")

def main():
    
    #Lists of defined variables
    session = requests.Session()


    # Navigation Bar
    with st.sidebar:
        choose = option_menu("Indicators", ["Support and Resistance", "Bowling","Categories","Balance"],
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

    
    elif choose == "Categories":
        st.title("Income")


    elif choose == "Balance":
        st.title("Transaction Details")


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