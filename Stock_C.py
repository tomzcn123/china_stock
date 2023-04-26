import streamlit as st
import yfinance as yf
import pandas as pd
from ta.trend import MACD
import lxml
from collections import defaultdict
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import requests
import tempfile

github_url = 'https://raw.githubusercontent.com/tomzcn123/china_stock/main/A.xlsx'

# Download the Excel file
response = requests.get(github_url)

# Check if the download was successful
if response.status_code == 200:
    # Save the downloaded file as a temporary file
    with tempfile.NamedTemporaryFile(suffix=".xlsx") as temp_file:
        temp_file.write(response.content)
        temp_file.flush()

        # Read the Excel file
        sheet_name = 'Sheet'  # Replace 'Sheet' with the name of the sheet containing the data
        data = pd.read_excel(temp_file.name, sheet_name=sheet_name, engine='openpyxl')

        # Process the data
        tickers = data[['tickers', 'sector']].to_dict('records')
else:
    print("Error: Unable to download the Excel file.")
