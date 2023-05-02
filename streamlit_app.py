import datetime

import hydralit_components as hc
import openai
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import requests
import streamlit as st
import toml
import yaml
from streamlit_authenticator import Authenticate
from streamlit_chat import message
from yaml.loader import SafeLoader

from SessionState import SessionState
from bollinger_band import draw_lines, draw_bollinger_bands, draw_signals, calc_bollinger_bands, \
    bollinger_marker_return, bollinger_strategy_signals
from momentum_strategy import apply_momentum_strategy, add_signals_to_chart
from support_and_resistance_file import support_and_resistance_algorithm
from trading_platform_component import trading_platform
from PIL import Image

st.set_page_config(page_title="Prodigy Trade", page_icon="random", layout='wide', initial_sidebar_state='collapsed')

random_stock_pick_array = []


@st.cache_data
def fetch(_session, url):
    try:
        result = session.get(url)
        return result.json()
    except Exception:
        print("Data Fetching failed")


# hashed_passwords = stauth.Hasher(['abc123','def']).generate()

with open(r"D:\New folder\TraderJoe\config.yaml") as file:
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

stocks_list = fetch(session, f"http://127.0.0.1:8084/investment/assets")

# dictionary for the categories
stocks_category = stocks_list

# Define the menu items and their labels
menu_items = [
    {"id": "home", "label": "Home"},
    {"id": "chatbot", "label": "Chat Bot"},
    {"id": "support", "label": "Support and Resistance"},
    {"id": "momentum", "label": "Momentum"},
    {"id": "bolinger", "label": "Bolinger"},
    {"id": "papertrading", "label": "Paper Trading"},
    {"id": "accountdetails", "label": "Account Details"},
]

# Define the override theme to set the background color of the navigation bar
over_theme = {"txc_navbar": "#808080", "txc_navbar_st": "#808080"}


# Load the image file
image = Image.open(r'D:\New folder\TraderJoe\logo.png')

if authentication_status:
    def main():
        authenticator.logout('Logout', 'sidebar')

        # Display the image in the sidebar
        st.sidebar.image(image, use_column_width=True)

        state = SessionState.get(sample_data=None)
        filter_expander = st.sidebar.expander(label="Click to filter")
        with filter_expander:
            with st.container():
                option = st.selectbox(
                    'Which Stock, Forex, Crypto, ETF, or indices would you like to trade?',
                    stocks_category.keys())
                option = option.replace("/", "-")
            with st.container():
                trading_options = ["Minute Trading", "Hour Trading", "Day Trading"]
                trading_option = st.selectbox(label="Select Trading Type", options=trading_options)
                st.markdown("<span style='font-size:10pt; font-style:italic;'>"
                            "<strong>Note:</strong></span>", unsafe_allow_html=True)
                st.markdown("<span style='font-size:10pt; font-style:italic;'>"
                            "- Minute Trading, please ensure you choose at least 5 hours timespan.<br>"
                            "- Hour Trading, please ensure you choose at least 8 days timespan.<br>"
                            "- Day Trading, please ensure you choose at least 5 months timespan.</span>", 
            unsafe_allow_html=True)
            with st.container():
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input(
                        "At which date should the chart start?",
                        datetime.date(2023, 4, 27))
                with col2:
                    end_date = st.date_input(
                        "At which date should the chart end?",
                        datetime.date(2023, 4, 28), max_value=datetime.date.today())
            with st.container():
                col1, col2 = st.columns(2)
                with col1:
                    start_time = st.time_input("At which time should the chart start?", datetime.time(00, 00, 00))
                with col2:
                    end_time = st.time_input("at which time should the chart end?", datetime.time(15, 00, 00))

            temp_start_date_time = datetime.datetime.combine(start_date, start_time)
            start_date_time = str(temp_start_date_time).replace(" ", "T") + "+00:00"
            temp_end_date_time = datetime.datetime.combine(end_date, end_time)
            new_temp_end_date_time = temp_end_date_time
            end_date_time = str(new_temp_end_date_time).replace(" ", "T") + "+00:00"
            print(start_date_time)
            print(end_date_time)

            sample = fetch(session,
                           f"http://127.0.0.1:8084/investment/{stocks_category[option]}/{start_date_time}/{end_date_time}/{trading_option}")
            try:
                sample_data = pd.read_json(sample, orient="columns")
                state.sample_data = sample_data
                sample_data = state.sample_data
            except:
                # st.error("Sorry, no data available. We are working on it")
                print('Error')

        # Display the image in the sidebar
        st.sidebar.image(image, use_column_width=True)

        # Create the navigation bar using the `hc.nav_bar` function
        menu_id = hc.nav_bar(
            menu_definition=menu_items,
            override_theme=over_theme,
            hide_streamlit_markers=False,  # will show the st hamburger as well as the navbar now!
            sticky_nav=True,  # at the top or not
            sticky_mode='pinned',  # jumpy or not-jumpy, but sticky or pinned
        )

        # Set the session state variable `nav` whenever a menu item is clicked
        if menu_id != "home":
            st.session_state.nav = menu_id
        else:
            st.session_state.nav = "home"

        # Render content based on selected navigation link
        if st.session_state.nav == "home":

            st.title("Welcome to Prodigy Trade!")
            st.header("Crack the Market with Prodigy Trade")
            st.write(
                "Prodigy Trade is a cutting-edge web application designed for traders who want to stay ahead of the game. It offers real-time trading data and advanced charting tools to help traders make informed decisions. With Prodigy Trade, users can access a wide range of markets, including stocks, futures, forex, and more. The platform also features customizable watchlists, alerts, and a social trading community where users can share ideas and strategies with other traders. Prodigy Trade is user-friendly and accessible on desktop and mobile devices, making it a convenient and powerful tool for traders of all levels.")

            stock_symbol_rdm = "AAPL"

            end_dt_rdm = datetime.datetime.today() - datetime.timedelta(hours=10)
            end_date_time_rdm = str(end_dt_rdm).replace(" ", "T") + "+00:00"
            st.write(end_date_time_rdm)

            start_dt_rdm = end_dt_rdm - datetime.timedelta(hours=80)
            start_date_time_rdm = str(start_dt_rdm).replace(" ", "T") + "+00:00"
            st.write(start_date_time_rdm)

            sample = fetch(session,
                           f"http://127.0.0.1:8084/investment/{stock_symbol_rdm}/{start_date_time_rdm}/{end_date_time_rdm}/Minute Trading")
            rdm_df = pd.read_json(sample, orient="columns")
            state.rdm_df = rdm_df
            rdm_df = state.rdm_df
            print(rdm_df)

            fig = px.line(rdm_df, x=rdm_df["datetime"], y=rdm_df['vwap'], title=f"{stock_symbol_rdm}")
            fig.update_layout(
                xaxis_title="Date", yaxis_title="Price"
            )
            st.write(fig)

            st.header("Strategies we use in our web-application: ")
            st.subheader("Support and Resistance")
            st.write(
                "Breakouts in trading occur when a stock, commodity, or currency moves beyond a previously established range. This indicates a shift in market sentiment and can lead to sustained trends in the direction of the breakout. Traders can use breakouts as a signal to enter a trade, but must exercise caution as false breakouts can lead to losses. If the price breaks through a resistance level, buyers have gained control and an uptrend may occur, while breaking through a support level suggests sellers have gained control and a downtrend may occur.")

            st.subheader("Bollinger Bands")
            st.write(
                "Bollinger Bands use a simple moving average and two standard deviations to identify overbought and oversold assets, and can be adjusted to user preferences. They expand and contract with volatility, indicating relative volatility and potential trend reversals. When the price moves outside the upper or lower band, it signals a potential trend reversal or continuation. If the price moves above the upper band, it's overbought, prompting a short position or sell, while a move below the lower band indicates oversold, prompting a long position or buy.")

            st.subheader("Momentum (Stochastic and MACD)")
            st.write(
                "The Stochastic oscillator identifies overbought and oversold market conditions to predict price reversals, often used with the MACD to confirm trends. The %K and D% lines make up the Stochastic oscillator, with values above 80 indicating overbought and below 20 indicating oversold conditions. The MACD and signal lines indicate trend direction, with an upward trend suggested by a crossing of the MACD above the signal line and a downward trend suggested by the opposite.")

        elif st.session_state.nav == "chatbot":

            st.title("Chat-Bot")
            with open(r"D:\New folder\TraderJoe\.secrets.toml", "r") as f:
                config = toml.load(f)
            openai.api_key = config["OPENAI_KEY"]

            def generate_response(prompt):
                completions = openai.Completion.create(
                    engine="text-davinci-003",
                    prompt=prompt,
                    max_tokens=1024,
                    n=1,
                    stop=None,
                    temperature=0.5,
                )
                message = completions.choices[0].text
                return message

            # Creating the chatbot interface
            st.header("Ask your questions regarding trading")
            st.markdown("Powered by ChatGPT and Streamlit")

            # Storing the chat
            if 'generated' not in st.session_state:
                st.session_state['generated'] = []

            if 'past' not in st.session_state:
                st.session_state['past'] = []

            # We will get the user's input by calling the get_text function
            def get_text():
                input_text = st.text_input("Your input ", "Hello, how are you?", key="input")
                return input_text

            user_input = get_text()

            if user_input:
                output = generate_response(user_input)
                # store the output
                st.session_state.past.append(user_input)
                st.session_state.generated.append(output)

            if st.session_state['generated']:

                for i in range(len(st.session_state['generated']) - 1, -1, -1):
                    message(st.session_state["generated"][i], key=str(i))
                    message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')

        elif st.session_state.nav == "support":

            st.title("Support and Ressistance")
            try:

                support_and_resistance_algorithm(option, sample_data)
            except:
                st.warning("No data available. We are working on it.")

            st.subheader("Keep in mind!")
            st.markdown(
                "No breakout strategy is fool-proof and requires risk management techniques and discipline. It's essential to adapt your strategy to changing market conditions, to always do your own research before entering any trade and use a combination of tools & techniques to make informed trading decisions. Possible strategies include: Support/Resistance Breakout: identify key levels and look for breakout above/below Trendline Breakout: look for price patterns, such as triangles or rectangles, to identify the potential direction of the trend Volatility Breakout: identify narrow price ranges and catch the shift when volatility increases ")

        elif st.session_state.nav == "momentum":

            st.title('Momentum')
            try:
                # Calling the momentum method
                sample_data = apply_momentum_strategy(sample_data)

                # Create chart data from sample data

                chart_data = st.line_chart(sample_data['Cumulative Returns'])

                # Add buy and sell signals to chart data
                chart_data = add_signals_to_chart(chart_data, sample_data)
            except Exception:
                st.warning("No data available. We are working on it.")

            st.subheader("Keep in mind!")
            st.markdown(
                "No breakout strategy is fool-proof and requires risk management techniques and discipline. It's essential to adapt your strategy to changing market conditions, to always do your own research before entering any trade and use a combination of tools & techniques to make informed trading decisions. Possible strategies include: The crossover: identify the Stochastic line to be below 20 in combination with the MACD line being above the signal line to indicate oversold conditions The divergence: look for divergencies between the MACD and the prices of asset which indicate the up-/downside and confirm divergences with the Stochastic oscillator values ")

        elif st.session_state.nav == "bolinger":

            st.title("Bollinger Bands Breakout")
            try:
                df = pd.DataFrame(sample_data)
                rolling_mean, upper_band, lower_band = calc_bollinger_bands(df)

                buy_signal, sell_signal = bollinger_strategy_signals(upper_band, lower_band, df)
                buy_markers, sell_markers = bollinger_marker_return(df, buy_signal, sell_signal)

                fig = go.Figure()
                draw_lines(df, fig, rolling_mean)
                draw_bollinger_bands(fig, df, upper_band, lower_band)
                draw_signals(fig, buy_markers, sell_markers)
                fig.update_layout(title=option, xaxis_title='Date', yaxis_title='Price')
                st.plotly_chart(fig)
            except:
                st.warning("No data available. We are working on it.")

            st.subheader("Keep in mind!")
            st.markdown(
                "No breakout strategy is fool-proof and requires risk management techniques and discipline. It's essential to adapt your strategy to changing market conditions, to always do your own research before entering any trade and use a combination of tools & techniques to make informed trading decisions. Possible strategies include: The Bollinger squeeze: bands squeezing together indicate an imminent price move, choose long/short position accordingly The Bollinger breakout: wait for price breaks outside of the upper/lower bands to determine the potential up-/downtrend The Bollinger reversal: look for divergences between price action and the Bollinger Bands, which indicate potential trend reversals ")


        elif st.session_state.nav == "papertrading":
            st.write("Welcome to the Paper Trading page!")

            st.title('Paper Trading')
            st.write('In this section you can buy or sell your equities')

            trading_platform()

        elif st.session_state.nav == "accountdetails":
            st.write("Welcome to the Account Details page!")

            st.cache_data.clear()
            tab1, tab2, tab3 = st.tabs(["Account Details", "Open Orders", "Closed Orders"])
            with tab1:
                st.subheader("Account Details")
                sample: dict = fetch(session,
                                     f"http://127.0.0.1:8084/investment/account")
                portfolio_history: dict = fetch(session, f"http://127.0.0.1:8084/investment/portfolio_history")
                print(portfolio_history)
                history: dict = portfolio_history.get('_raw')
                chart = px.line()
                chart.add_scatter(x=history.get('timestamp'), y=history.get('equity'), mode='lines', line_color='green',
                                  name='Lowest Price')
                sample = sample.get('_raw')
                col1, col2 = st.columns(2)
                with col1:
                    st.write('Account Number: ')
                with col2:
                    st.write(sample.get('account_number'))
                col1, col2 = st.columns(2)
                with col1:
                    st.write('Cash: ')
                with col2:
                    st.write(sample.get('cash'))
                col1, col2 = st.columns(2)
                with col1:
                    st.write('Daytrade count: ')
                with col2:
                    day_trade_count: int = sample.get('daytrade_count')
                    st.write(str(day_trade_count))
                col1, col2 = st.columns(2)
                with col1:
                    st.write('Status: ')
                with col2:
                    st.write(sample.get('status'))
                col1, col2 = st.columns(2)
                with col1:
                    st.write("Portfolio development: ")

                with col2:
                    new_equity: float = float(sample.get('equity')) - float(sample.get('last_equity'))
                    st.write(str(new_equity))
                with st.container():
                    st.subheader('Portfolio Development')
                    st.write(chart)
            with tab2:
                st.subheader("Open Orders")
                open_order = "open"
                sample: dict = fetch(session,
                                     f"http://127.0.0.1:8084/investment/orders/{open_order}")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write("Symbol")
                with col2:
                    st.write("Quantity")
                with col3:
                    st.write("Executed at (UTC Time)")

                if sample == []:
                    st.warning("No open orders")
                for row in sample:
                    open_order: dict = row.get('_raw')

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(open_order.get('symbol'))
                    with col2:
                        st.write(open_order.get('qty'))
                    with col3:
                        date: str = open_order.get('submitted_at')
                        date = date.replace("T", " ")
                        date = date.removesuffix("Z")
                        date = date.split(".")[0]
                        st.write(date)

            with tab3:
                st.subheader("Closed Orders")
                closed = 'closed'
                sample: dict = fetch(session,
                                     f"http://127.0.0.1:8084/investment/orders/{closed}")

                col1, col2 = st.columns(2)
                with col1:
                    st.write("Symbol")
                with col2:
                    st.write("Executed at (UTC Time)")
                if sample == []:
                    st.warning("No closed orders")
                else:
                    for row in sample:
                        open_order: dict = row.get('_raw')

                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(open_order.get('symbol'))
                    with col2:
                        date: str = open_order.get('submitted_at')
                        date = date.replace("T", " ")
                        date = date.removesuffix("Z")
                        date = date.split(".")[0]
                        st.write(date)
        else:
            st.write("Please select a page from the navigation menu.")


    if __name__ == '__main__':
        main()

elif authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')
