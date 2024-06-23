from data_collection import get_account_info, get_stocks, fetch_stock_data, filter_stocks
from feature_engineering import process_data
from model_training import train_model
from trade_execution import execute_trades
from schwabdev.api import Client
import joblib
import os

def fetch_and_process_data(client):
    stocks = get_stocks(client)
    filtered_stocks = filter_stocks(stocks)
    stock_data = fetch_stock_data(client, filtered_stocks)
    processed_data = process_data(stock_data)
    return processed_data

def main():
    app_key = os.getenv("app_key")
    app_secret = os.getenv("app_secret")
    callback_url = os.getenv("callback_url")
    tokens_file = "tokens.json"

    client = Client(app_key, app_secret, callback_url, tokens_file)
    
    # Step 1: Get Account Info (Optional)
    account_info = get_account_info(client)
    
    # Step 2: Fetch and Process Stock Data
    processed_data = fetch_and_process_data(client)
    
    # Step 3: Train Model (Initially)
    train_model(processed_data)
    
    # Step 4: Load Model and Execute Trades
    model = joblib.load('trading_model.pkl')
    execute_trades(client, model, processed_data)

if __name__ == "__main__":
    main()
