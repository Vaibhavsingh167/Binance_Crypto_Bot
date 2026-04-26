'''This python file is used to create a database along with its schema.'''
from binance.client import Client
import sqlite3

import os
from dotenv import load_dotenv

load_dotenv()

API_KEY=os.getenv("BINANCE_API_KEY")
API_SECRET=os.getenv("BINANCE_API_SECRET")

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