"""
main.py — FastAPI application with WebSocket streaming.

Connects to the Binance WebSocket for live BTCUSDT kline data,
runs ML inference, executes simulated trades, and broadcasts
real-time updates to connected frontend clients.
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from .ml_engine import engine as ml_engine
from .wallet import SimulatedWallet
from . import database as db

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Crypto Trading Bot API",
    description="Real-time BTCUSDT trading signals powered by LSTM",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Global state
# ---------------------------------------------------------------------------
wallet = SimulatedWallet()
connected_clients: list[WebSocket] = []

# Binance WebSocket URL — public mainnet, no API key required
BINANCE_WS_URL = "wss://stream.binance.com:9443/ws/btcusdt@kline_1m"


# ---------------------------------------------------------------------------
# Startup / Shutdown
# ---------------------------------------------------------------------------
@app.on_event("startup")
async def startup_event():
    """Load ML model and initialize database on startup."""
    logger.info("=" * 60)
    logger.info("Starting Crypto Trading Bot Backend")
    logger.info("=" * 60)

    # Initialize database tables
    db.init_wallet_table(
        initial_balance=float(os.getenv("INITIAL_WALLET_BALANCE", "10000"))
    )
    logger.info("Database initialized.")

    # Load ML model
    ml_engine.load()
    logger.info("ML engine loaded and ready.")

    # Start the Binance stream in the background
    asyncio.create_task(binance_stream_loop())
    logger.info("Binance stream task started.")


# ---------------------------------------------------------------------------
# REST endpoints
# ---------------------------------------------------------------------------
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "model_ready": ml_engine.is_ready,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/trades")
async def get_trades():
    """Return the 20 most recent trades."""
    trades = db.get_recent_trades(limit=20)
    return {"trades": trades}


@app.get("/api/wallet")
async def get_wallet():
    """Return current wallet state (needs a price for valuation)."""
    state = db.get_wallet_state()
    return {"wallet": state}


# ---------------------------------------------------------------------------
# WebSocket — Client connections
# ---------------------------------------------------------------------------
@app.websocket("/ws/stream")
async def websocket_endpoint(ws: WebSocket):
    """
    Accept a frontend WebSocket connection.
    The client doesn't send data — it only receives broadcasts.
    """
    await ws.accept()
    connected_clients.append(ws)
    logger.info("Client connected. Total clients: %d", len(connected_clients))

    try:
        # Keep the connection alive — just wait for disconnect
        while True:
            # We read to detect disconnection; clients don't send meaningful data
            await ws.receive_text()
    except WebSocketDisconnect:
        connected_clients.remove(ws)
        logger.info("Client disconnected. Total clients: %d", len(connected_clients))
    except Exception:
        if ws in connected_clients:
            connected_clients.remove(ws)


async def broadcast(payload: dict) -> None:
    """Send a JSON payload to all connected WebSocket clients."""
    if not connected_clients:
        return

    message = json.dumps(payload)
    stale: list[WebSocket] = []

    for client in connected_clients:
        try:
            await client.send_text(message)
        except Exception:
            stale.append(client)

    # Clean up disconnected clients
    for client in stale:
        if client in connected_clients:
            connected_clients.remove(client)


# ---------------------------------------------------------------------------
# Binance WebSocket stream (background task)
# ---------------------------------------------------------------------------
async def binance_stream_loop() -> None:
    """
    Connect to the Binance WebSocket and stream kline data.
    Automatically reconnects on failure.
    """
    import websockets  # type: ignore

    while True:
        try:
            logger.info("Connecting to Binance WebSocket: %s", BINANCE_WS_URL)
            async with websockets.connect(BINANCE_WS_URL) as ws_binance:
                logger.info("Connected to Binance WebSocket.")
                async for raw_msg in ws_binance:
                    try:
                        data = json.loads(raw_msg)
                        await process_kline(data)
                    except json.JSONDecodeError:
                        logger.warning("Received non-JSON message from Binance.")
                    except Exception as e:
                        logger.error("Error processing kline: %s", e, exc_info=True)

        except Exception as e:
            logger.error("Binance WebSocket error: %s. Reconnecting in 5s...", e)
            await asyncio.sleep(5)


async def process_kline(data: dict) -> None:
    """
    Process a single kline event from Binance.

    Binance kline payload structure:
    {
        "e": "kline",
        "k": {
            "t": 1234567890000,  // kline start time
            "o": "67000.00",     // open
            "h": "67100.00",     // high
            "l": "66900.00",     // low
            "c": "67050.00",     // close
            "v": "123.456",     // volume
            "x": true/false     // is this kline closed?
        }
    }
    """
    kline = data.get("k", {})
    if not kline:
        return

    current_price = float(kline.get("c", 0))
    is_closed = kline.get("x", False)

    if current_price <= 0:
        return

    timestamp = datetime.now(timezone.utc).isoformat()

    # Feed closed candles to the ML engine for indicator computation
    if is_closed:
        candle = {
            "open": kline.get("o", 0),
            "high": kline.get("h", 0),
            "low": kline.get("l", 0),
            "close": kline.get("c", 0),
            "volume": kline.get("v", 0),
        }
        ml_engine.add_candle(candle)

    # Run prediction (will return "Warming Up" if buffer not full)
    prediction = ml_engine.predict()
    signal = prediction["signal"]
    confidence = prediction["confidence"]

    # Execute trade on closed candles only (avoid partial candle trading)
    trade_executed = None
    if is_closed and signal in ("Buy", "Sell"):
        trade_executed = wallet.process_signal(signal, current_price)

    # Log prediction on closed candles
    if is_closed:
        db.log_prediction("BTCUSDT", signal, confidence)

    # Get portfolio state
    portfolio = wallet.get_portfolio(current_price)

    # Build payload
    payload = {
        "current_price": current_price,
        "timestamp": timestamp,
        "model_signal": signal,
        "confidence": confidence,
        "candle_closed": is_closed,
        "trade_executed": trade_executed,
        "wallet": {
            "total_portfolio_value": portfolio["total_portfolio_value"],
            "current_pnl": portfolio["current_pnl"],
            "pnl_percentage": portfolio["pnl_percentage"],
            "usdt_balance": portfolio["usdt_balance"],
            "btc_balance": portfolio["btc_balance"],
            "most_recent_buy_price": portfolio["most_recent_buy_price"],
            "most_recent_buy_time": portfolio["most_recent_buy_time"],
            "most_recent_sell_price": portfolio["most_recent_sell_price"],
            "most_recent_sell_time": portfolio["most_recent_sell_time"],
        },
    }

    # Broadcast to all connected frontend clients
    await broadcast(payload)


# ---------------------------------------------------------------------------
# Entry point (for `python -m app.main`)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
