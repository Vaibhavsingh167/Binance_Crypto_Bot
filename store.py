'''This python file is used to store data in trading_bot.db by fetching it from binance testnet.'''
from binance.client import Client
import pandas as pd
import sqlite3

API_KEY="Ox6hOQOFVylQZ11g7hAO0hnXlY6GwolE0Nejhr49UjvLyEc2iiImhRqWonlVrnya"
API_SECRET="jHy6hz9eSXvxQn5T4JhsQcjJWRyfGCeHqFd871Sp6ffpTt2jHFPskqOCUkCDTWH1"

client = Client(API_KEY, API_SECRET)
client.API_URL = 'https://testnet.binance.vision/api'


def fetch_and_store(symbol="BTCUSDT", interval="1m", limit=5000000000):
    klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)

    df = pd.DataFrame(klines, columns=[
        "timestamp", "open", "high", "low", "close", "volume",
        "close_time", "qav", "num_trades",
        "taker_base_vol", "taker_quote_vol", "ignore"
    ])

    df = df[["timestamp", "open", "high", "low", "close", "volume"]]
    df["symbol"] = symbol

    # Convert types
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit='ms')
    df = df.astype({
        "open": float,
        "high": float,
        "low": float,
        "close": float,
        "volume": float
    })

    conn = sqlite3.connect("trading_bot.db")
    df.to_sql("market_data", conn, if_exists="append", index=False)
    conn.close()


# Example usage
for _ in range(10):
    fetch_and_store("BTCUSDT")
for _ in range(10):
    fetch_and_store("ETHUSDT")
for _ in range(10):
    fetch_and_store("SOLUSDT")