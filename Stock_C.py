import streamlit as st
import pandas as pd
import requests
from io import BytesIO
github_url = 'https://raw.githubusercontent.com/tomzcn123/china_stock/main/A.xlsx'
response = requests.get(github_url)
excel_data = BytesIO(response.content)
sheet_name = 'Sheet'
data = pd.read_excel(excel_data, sheet_name=sheet_name, engine='openpyxl')
tickers = data[['tickers', 'sector','name']].to_dict('records')


import yfinance as yf
from ta.trend import MACD
import lxml
from collections import defaultdict
import plotly.graph_objects as go
from plotly.subplots import make_subplots

@st.cache
def fetch_stock_data(stock_ticker, period='100d', interval='1d'):
    data = yf.download(tickers=stock_ticker, period=period, interval=interval)
    return data

@st.cache
def calculate_macd(data, window_fast=12, window_slow=26, window_sign=9, macd_ma_window=5):
    data = data.copy()  # Create a copy of the data
    macd_indicator = MACD(data['Close'], window_slow=window_slow, window_fast=window_fast, window_sign=window_sign)
    data[f'MACD_{window_fast}_{window_slow}_{window_sign}'] = macd_indicator.macd()
    data[f'MACD_{window_fast}_{window_slow}_{window_sign}_MA_{macd_ma_window}'] = data[f'MACD_{window_fast}_{window_slow}_{window_sign}'].rolling(window=macd_ma_window).mean()
    return data

@st.cache
def calculate_moving_average(data, window=20):
    data = data.copy()  # Create a copy of the data
    data[f'MovingAverage_{window}'] = data['Close'].rolling(window=window).mean()
    return data


@st.cache(suppress_st_warning=True)
def find_stocks_above_conditions(stock_list):
    stocks_above_conditions = defaultdict(list)
    error_messages = []
    for stock_info in stock_list:
        stock = stock_info['tickers']
        sector = stock_info['sector']
        name = stock_info['name']
        try:
            data = fetch_stock_data(stock)
            data = calculate_moving_average(data)
            data = calculate_macd(data, window_fast=5, macd_ma_window=5)
            data = calculate_macd(data)
            if (not data.empty and
                data.iloc[-1]['Close'] > data.iloc[-1]['MovingAverage_20'] and
                data.iloc[-1][f'MACD_5_26_9_MA_5'] > data.iloc[-1]['MACD_5_26_9']
            ):
                stocks_above_conditions[sector].append((stock, name))
        except Exception as e:
            error_messages.append(f"Error processing stock {stock}: {e}")

    return stocks_above_conditions, error_messages



def plot_candlestick_chart(stock_ticker, period='3mo', interval='1d'):
    data = yf.download(tickers=stock_ticker, period=period, interval=interval)
    data = calculate_moving_average(data, window=20)
    data = calculate_moving_average(data, window=5)

    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=data.index,
                                  open=data['Open'],
                                  high=data['High'],
                                  low=data['Low'],
                                  close=data['Close'],
                                  name='Candlestick'))
    fig.add_trace(go.Scatter(x=data.index,
                             y=data['MovingAverage_20'],
                             mode='lines',
                             line=dict(color='green', width=1),
                             name='20-day Moving Average'))
    fig.add_trace(go.Scatter(x=data.index,
                             y=data['MovingAverage_5'],
                             mode='lines',
                             line=dict(color='blue', width=1),
                             name='5-day Moving Average'))
    fig.update_layout(title=f'{stock_ticker} Candlestick Chart with 20-day and 5-day Moving Averages',
                      xaxis_title='Date',
                      yaxis_title='Price',
                      xaxis_rangeslider_visible=False)
    return fig

st.title("Stock Opportunity")
st.write("Analyzing stocks...")
stocks_above_conditions, errors = find_stocks_above_conditions(tickers)
for error in errors:
    st.warning(error)  # Display the error messages outside the cached function

st.header("Stocks with the current price above the 20-day moving average and 5-day MACD line:")
for sector, stocks in stocks_above_conditions.items():
    st.subheader(sector)
    selected_stock = st.selectbox(f"Select a stock from {sector}", stocks, format_func=lambda x: f"{x[1]} ({x[0]})")
    st.write(f"Selected stock: {selected_stock[1]} ({selected_stock[0]})")
    candlestick_chart = plot_candlestick_chart(selected_stock[0])
    st.plotly_chart(candlestick_chart)

