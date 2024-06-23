import pandas as pd
import ta

def add_technical_indicators(df):
    df['MA10'] = ta.trend.sma_indicator(df['close'], window=10)
    df['MA50'] = ta.trend.sma_indicator(df['close'], window=50)
    df['RSI'] = ta.momentum.rsi(df['close'], window=14)
    df['MACD'] = ta.trend.macd_diff(df['close'])
    df['BB_high'] = ta.volatility.bollinger_hband(df['close'])
    df['BB_low'] = ta.volatility.bollinger_lband(df['close'])
    return df

def process_data(stock_data):
    processed_data = {}
    for symbol, data in stock_data.items():
        df = pd.DataFrame(data)
        df = add_technical_indicators(df)
        processed_data[symbol] = df
    return processed_data
