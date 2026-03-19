'''This python file is used to create a database along with its schema.'''
from binance.client import Client
import sqlite3

API_KEY="Ox6hOQOFVylQZ11g7hAO0hnXlY6GwolE0Nejhr49UjvLyEc2iiImhRqWonlVrnya"
API_SECRET="jHy6hz9eSXvxQn5T4JhsQcjJWRyfGCeHqFd871Sp6ffpTt2jHFPskqOCUkCDTWH1"

client = Client(API_KEY, API_SECRET)
client.API_URL = 'https://testnet.binance.vision/api'

def connect_db():
    return sqlite3.connect("trading_bot.db")

def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS market_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT,
        timestamp DATETIME,
        open REAL,
        high REAL,
        low REAL,
        close REAL,
        volume REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT,
        timestamp DATETIME,
        prediction TEXT,
        confidence REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT,
        timestamp DATETIME,
        action TEXT,
        price REAL,
        quantity REAL
    )
    """)

    conn.commit()
    conn.close()

create_tables()