"""
database.py — SQLite helpers for the trading bot.

Manages connections, trade logging, and the simulated wallet table.
"""

import sqlite3
import os
from datetime import datetime, timezone

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "trading_bot.db")


def get_connection() -> sqlite3.Connection:
    """Return a new SQLite connection with row_factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_wallet_table(initial_balance: float = 10000.0) -> None:
    """
    Create the wallet table if it doesn't exist and seed it with initial balance.
    Preserves existing wallet state on restart.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wallet (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            usdt_balance REAL NOT NULL DEFAULT 10000.0,
            btc_balance REAL NOT NULL DEFAULT 0.0,
            initial_balance REAL NOT NULL DEFAULT 10000.0,
            last_buy_price REAL DEFAULT NULL,
            last_buy_time TEXT DEFAULT NULL,
            last_sell_price REAL DEFAULT NULL,
            last_sell_time TEXT DEFAULT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    # Only seed if no wallet row exists
    cursor.execute("SELECT COUNT(*) FROM wallet")
    count = cursor.fetchone()[0]
    if count == 0:
        now = datetime.now(timezone.utc).isoformat()
        cursor.execute("""
            INSERT INTO wallet (id, usdt_balance, btc_balance, initial_balance, updated_at)
            VALUES (1, ?, 0.0, ?, ?)
        """, (initial_balance, initial_balance, now))

    conn.commit()
    conn.close()


def log_trade(symbol: str, action: str, price: float, quantity: float) -> None:
    """Insert a trade record into the trades table."""
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    cursor.execute("""
        INSERT INTO trades (symbol, timestamp, action, price, quantity)
        VALUES (?, ?, ?, ?, ?)
    """, (symbol, now, action, price, quantity))
    conn.commit()
    conn.close()


def log_prediction(symbol: str, prediction: str, confidence: float) -> None:
    """Insert a prediction record into the predictions table."""
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    cursor.execute("""
        INSERT INTO predictions (symbol, timestamp, prediction, confidence)
        VALUES (?, ?, ?, ?)
    """, (symbol, now, prediction, confidence))
    conn.commit()
    conn.close()


def get_recent_trades(limit: int = 20) -> list[dict]:
    """Return the most recent trades as a list of dicts."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT symbol, timestamp, action, price, quantity
        FROM trades
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_wallet_state() -> dict:
    """Return the current wallet state as a dict."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM wallet WHERE id = 1")
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return {}


def update_wallet(
    usdt_balance: float,
    btc_balance: float,
    last_buy_price: float | None = None,
    last_buy_time: str | None = None,
    last_sell_price: float | None = None,
    last_sell_time: str | None = None,
) -> None:
    """Update the wallet row in-place."""
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()

    # Build dynamic SET clause — only update buy/sell fields when provided
    fields = ["usdt_balance = ?", "btc_balance = ?", "updated_at = ?"]
    values: list = [usdt_balance, btc_balance, now]

    if last_buy_price is not None:
        fields.append("last_buy_price = ?")
        values.append(last_buy_price)
    if last_buy_time is not None:
        fields.append("last_buy_time = ?")
        values.append(last_buy_time)
    if last_sell_price is not None:
        fields.append("last_sell_price = ?")
        values.append(last_sell_price)
    if last_sell_time is not None:
        fields.append("last_sell_time = ?")
        values.append(last_sell_time)

    sql = f"UPDATE wallet SET {', '.join(fields)} WHERE id = 1"
    cursor.execute(sql, values)
    conn.commit()
    conn.close()
