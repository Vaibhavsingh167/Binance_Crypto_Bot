'''This python file is used to train model asset by asset.'''
import sqlite3
import pandas as pd

def load_data(symbol="BTCUSDT"):
    conn = sqlite3.connect("trading_bot.db")
    
    query = f"""
    SELECT * FROM market_data
    WHERE symbol = '{symbol}'
    ORDER BY timestamp
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    
    return df
import numpy as np

def add_indicators(df):
    # EMA
    df['ema_10'] = df['close'].ewm(span=10).mean()
    df['ema_20'] = df['close'].ewm(span=20).mean()

    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))

    df.dropna(inplace=True)
    
    return df
from sklearn.preprocessing import MinMaxScaler

def normalize_data(df):
    scaler = MinMaxScaler()
    
    features = ['open', 'high', 'low', 'close', 'volume', 'ema_10', 'ema_20', 'rsi']
    
    df[features] = scaler.fit_transform(df[features])
    
    return df, scaler
def create_sequences(df, window_size=50):
    features = ['open', 'high', 'low', 'close', 'volume', 'ema_10', 'ema_20', 'rsi']
    
    X = []
    y = []

    future_window = 10
    threshold = 0.002  # 0.2%

    for i in range(window_size, len(df) - future_window):

        current_price = df['close'].iloc[i]

        # Avoid division issues
        if current_price == 0 or np.isnan(current_price):
            continue

        future_prices = df['close'].iloc[i:i+future_window]

        future_max = future_prices.max()
        future_min = future_prices.min()

        # Label decision
        if (future_max - current_price) / current_price > threshold:
            label = 1  # Buy
        elif (current_price - future_min) / current_price > threshold:
            label = 0  # Sell
        else:
            continue  # Skip unclear → skip BOTH X and y

        # Append ONLY when label exists
        X.append(df[features].iloc[i-window_size:i].values)
        y.append(label)
    X, y = create_sequences(df)
    print("X shape:", X.shape)
    print("y shape:", y.shape)

    return np.array(X), np.array(y)


from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

def build_model(input_shape):
    model = Sequential()

    model.add(LSTM(50, return_sequences=True, input_shape=input_shape))
    model.add(Dropout(0.2))

    model.add(LSTM(50))
    model.add(Dropout(0.2))

    model.add(Dense(1, activation='sigmoid'))

    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy']
    )

    return model
def train_model(symbol="BTCUSDT"):
    df = load_data(symbol)
    df = add_indicators(df)
    df, scaler = normalize_data(df)

    X, y = create_sequences(df)

    model = build_model((X.shape[1], X.shape[2]))

    model.fit(X, y, epochs=5, batch_size=32)

    return model, scaler
model, scaler= train_model("BTCUSDT")


