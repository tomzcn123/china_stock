import streamlit as st
import pandas as pd
import requests
from io import BytesIO



github_url = 'https://raw.githubusercontent.com/tomzcn123/china_stock/main/A.xlsx'
response = requests.get(github_url)
excel_data = BytesIO(response.content)
sheet_name = 'Sheet'
data = pd.read_excel(excel_data, sheet_name=sheet_name, engine='openpyxl')
tickers = data[['tickers', 'sector']].to_dict('records')

st.write(tickers)
