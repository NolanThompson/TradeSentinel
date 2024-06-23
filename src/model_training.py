from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
import pandas as pd

def prepare_data(df):
    feature_columns = ['MA10', 'MA50', 'RSI', 'MACD', 'BB_high', 'BB_low']
    X = df[feature_columns]
    y = (df['close'].shift(-1) > df['close']).astype(int)
    X, y = X[:-1], y[:-1]
    return X, y

def train_model(stock_data):
    X, y = pd.DataFrame(), pd.Series(dtype='int')
    for df in stock_data.values():
        X_single, y_single = prepare_data(df)
        X = pd.concat([X, X_single], axis=0)
        y = pd.concat([y, y_single], axis=0)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = XGBClassifier(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy: {accuracy * 100:.2f}%")
    joblib.dump(model, 'trading_model.pkl')
