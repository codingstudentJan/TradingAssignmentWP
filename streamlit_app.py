import streamlit as st
import requests
import pandas as pd
import datetime
from streamlit_option_menu import option_menu
import plotly.express as px
import numpy as np


def fetch(session, url):
    try:
        result = session.get(url)
        return result.json()
    except Exception:
        print("Data Fetching failed")

def main():
    
    #Lists of defined variables
    session = requests.Session()


    # Navigation Bar
    with st.sidebar:
        choose = option_menu("Trading Strategy", ["Momentum", "Bowling","Categories","Balance"],
                             icons=['pencil-fill', 'bar-chart-fill','bookmarks-fill', 'piggy-bank-fill'],
                             menu_icon="coin", default_index=0,
                             styles={
            "container": {"padding": "5!important", "background-color": "#bfcce3"},
            "icon": {"color": "black", "font-size": "25px"}, 
            "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "#7596bd"},
      }
     )

    if choose == "Momentum":
        st.title("Momentum")


    elif choose == "Bowling":
        st.title("Expenses")

    
    elif choose == "Categories":
        st.title("Income")


    elif choose == "Balance":
        st.title("Transaction Details")


if __name__ == '__main__':
    main()