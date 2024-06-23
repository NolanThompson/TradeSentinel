import pandas as pd
from schwabdev.api import Client

def get_account_info(client):
    response = client.account_details_all()
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching account info: {response.status_code}")
        return {}

def get_stocks(client):
    response = client.instruments("AAPL", "symbol-search")  # Example; adjust based on actual needs
    if response.status_code == 200:
        return response.json()
    else:
        return []

def filter_stocks(stocks):
    filtered = [stock for stock in stocks if stock.get('marketCap', 0) > 1e10 and stock.get('volume', 0) > 1e6]
    return filtered

def fetch_stock_data(client, symbols):
    data = {}
    for symbol in symbols:
        response = client.quote(symbol)
        if response.status_code == 200:
            data[symbol] = response.json()
    return data

