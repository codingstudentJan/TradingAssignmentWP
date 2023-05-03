# Trading Assgiment - ProdigyTrade
Group 1 matriculation number:
Jan: 5155774
Laura: 7355671
Dennis: 7606443
Lyle: 2170275
Feni: 2222199


## Prerequisites
- You need to have python version 3.10
and all this dependencies installed:
```bash 
    pip install fastapi
    pip install uvicorn
    pip install sqlalchemy
    pip install streamlit
    pip install panda 
    pip install requests
    pip install streamlit-option-menu
    pip install plotly.express
    pip install NumPy
    pip install alpaca-py
    pip install streamlit-authenticator
    Pip install ta
    pip install openai
    pip install streamlit-chat
    pip install hydralit
```

## Streamlit Theme and paths

Please create in your user directory a .streamlit directory and then add a config.toml file.
In this config.toml add the follwoing code:
```bash
[theme]
primaryColor="#a2a2a2"
backgroundColor="#111f4d"
secondaryBackgroundColor="#020205"
textColor="#f3e99f"
```
Furthermore, you have to make sure that in line 40,75 and 200 of streamlit_app.py there are the right paths specified


## Login and Email-Account used for the app 
#### Login for the app: 
username: cPerrot, password: abc123

#### Email

Prodigy Trade Email Account
- ProdigyTradeDHBW@gmail.com
- abc123!*
- 01.01.2000

SMTP-Server: smtp.gmail.com

## Running the application
- To run the application, input following commands in separate terminals (both must be active):
```bash
    python main.py  
```
```bash
    streamlit run streamlit_app.py      
```

## Enduser Documentation
Hello together,
we are "ProdigyTrading", the newcomer for web application services in the money and stock trading sector.
As newcomers to this space, we are dedicated to bringing unique and user-friendly solutions to help businesses thrive in the digital age. Our team is passionate about trading and crypto, and we believe that our combined expertise will revolutionize the way businesses in this industry operate. We're thrilled to share our vision with you and showcase how our services can help take your business to the next level.
Exited for what is to come?
Stay tuned as we launch our next big project...

This documentation follows the purpose of informing and instructing the user of the main functionalities of our application. The guide will include instructions on the following use cases: 

- Login
- ChatBot
- Choosing a Strategy
- Buy & Sell Stocks
- Account & Order Information 

As any unanswered questions/queries arise, make sure to contact lauramakare00@gmail.com for further support.  

### 1. Login
A login option exists that enables the user to access “Prodigy Trade” and ist functionalities regarding stock trading. Upon login, users have the option to get information on different strategies, select various trading assets and look up performance of stocks.  
1. To open the browser, follow the instruction of the ReadMe file (deposited here: https://github.com/codingstudentJan/TraderJoe)  
2. Complete login with your credentials and select “login” at the bottom to submit 
3. You will be taken to the mane page overview with a navigation bar at the top 
4. Upon scrolling down, an overview of the possible strategies provided by Prodigy Trade will be displayed 

### 2. ChatBot
Our innovative ChatBot enables our users to access information and support 24/7. To access the chatbot, please follow these steps: 
1. select “ChatBot” at the top of the navigation bar 
2. To enter a question or statement, please do so by putting your input in the input field 

### 3. Choosing a Strategy
ProdigyTrade offers various strategy options with different plot visualizations and information.  
1. To select one, click the desired one in the navigation bar at the top. The possibilities are “Support and Resistance”, “Momentum”, “Bollinger” and “Paper  Trading”. In this example “Support and Resistance” will be showed. The procedure for the other options is the same.  
2. It is possible to enter a safe support/resistance number as well as various filter options on the left menu side. The filter options include the stock and trading type as well as the date and time of the visualized chart/plot. 
3. Upon scrolling down, you may find a wrap up and some basic tips when trading 

### 4. Buy/Sell Stocks
Our website offers the option to sell or buy your equities. To do so, follow these steps: 
1. Select “Paper Trading” in the navigation bar above 
2. Upon selecting different trading criteria such as symbol to trade or quantity, make sure to click “execute trade” to submit 

### 5. Account & Order Information
To see the overview of your closed or open orders, as well as other account details, please complete the following steps:  
1. Select “Account Details” from the navigation bar 
2. An overview of your account details will be displayed as below 
3. An overview display of your open orders is also possible, by clicking the according navigation register “Open Orders” 
4. An overview display of your closed orders is also possible, by clicking the according navigation register “Closed Orders” 
5. You may also see the positions, what the average starting price was and what the current price is. An overview is display upon clicking the register “Positions” 
