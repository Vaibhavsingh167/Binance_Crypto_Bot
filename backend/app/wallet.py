"""
wallet.py — Simulated trading wallet backed by SQLite.

Manages buy/sell execution, portfolio valuation, and PnL calculation.
"""

import logging
from datetime import datetime, timezone

from . import database as db

logger = logging.getLogger(__name__)


class SimulatedWallet:
    """
    Simulated trading wallet that executes paper trades
    based on ML model signals.

    Rules:
    - Buy: Convert 100% of available USDT → BTC at current price.
    - Sell: Convert 100% of available BTC → USDT at current price.
    - Cannot buy if USDT balance < $1.
    - Cannot sell if BTC balance ≈ 0.
    """

    def __init__(self) -> None:
        self._ensure_initialized()

    @staticmethod
    def _ensure_initialized() -> None:
        """Make sure the wallet table exists and is seeded."""
        db.init_wallet_table()

    # ------------------------------------------------------------------
    # Trade execution
    # ------------------------------------------------------------------

    def execute_buy(self, price: float) -> dict | None:
        """
        Buy BTC with all available USDT.

        Returns trade details dict, or None if insufficient funds.
        """
        state = db.get_wallet_state()
        usdt = state.get("usdt_balance", 0.0)

        if usdt < 1.0:
            logger.info("Buy skipped — insufficient USDT (%.2f)", usdt)
            return None

        # Calculate quantity (simple: no fees in simulation)
        quantity = usdt / price
        now = datetime.now(timezone.utc).isoformat()

        # Update wallet
        db.update_wallet(
            usdt_balance=0.0,
            btc_balance=state.get("btc_balance", 0.0) + quantity,
            last_buy_price=price,
            last_buy_time=now,
        )

        # Log the trade
        db.log_trade(symbol="BTCUSDT", action="BUY", price=price, quantity=quantity)

        trade = {
            "action": "BUY",
            "price": price,
            "quantity": round(quantity, 8),
            "timestamp": now,
        }
        logger.info("BUY executed: %.8f BTC @ $%.2f", quantity, price)
        return trade

    def execute_sell(self, price: float) -> dict | None:
        """
        Sell all available BTC for USDT.

        Returns trade details dict, or None if no BTC held.
        """
        state = db.get_wallet_state()
        btc = state.get("btc_balance", 0.0)

        if btc < 1e-8:
            logger.info("Sell skipped — no BTC to sell (%.10f)", btc)
            return None

        # Calculate USDT received (no fees)
        usdt_received = btc * price
        now = datetime.now(timezone.utc).isoformat()

        # Update wallet
        db.update_wallet(
            usdt_balance=state.get("usdt_balance", 0.0) + usdt_received,
            btc_balance=0.0,
            last_sell_price=price,
            last_sell_time=now,
        )

        # Log the trade
        db.log_trade(symbol="BTCUSDT", action="SELL", price=price, quantity=btc)

        trade = {
            "action": "SELL",
            "price": price,
            "quantity": round(btc, 8),
            "usdt_received": round(usdt_received, 2),
            "timestamp": now,
        }
        logger.info("SELL executed: %.8f BTC @ $%.2f → $%.2f", btc, price, usdt_received)
        return trade

    # ------------------------------------------------------------------
    # Portfolio state
    # ------------------------------------------------------------------

    def get_portfolio(self, current_price: float) -> dict:
        """
        Calculate the full portfolio state at the given BTC price.

        Returns:
            {
                "total_portfolio_value": float,
                "current_pnl": float,
                "pnl_percentage": float,
                "usdt_balance": float,
                "btc_balance": float,
                "most_recent_buy_price": float | None,
                "most_recent_buy_time": str | None,
                "most_recent_sell_price": float | None,
                "most_recent_sell_time": str | None,
            }
        """
        state = db.get_wallet_state()

        usdt = state.get("usdt_balance", 0.0)
        btc = state.get("btc_balance", 0.0)
        initial = state.get("initial_balance", 10000.0)

        # Total value = USDT held + BTC valued at current price
        total_value = usdt + (btc * current_price)
        pnl = total_value - initial
        pnl_pct = (pnl / initial) * 100 if initial > 0 else 0.0

        return {
            "total_portfolio_value": round(total_value, 2),
            "current_pnl": round(pnl, 2),
            "pnl_percentage": round(pnl_pct, 2),
            "usdt_balance": round(usdt, 2),
            "btc_balance": round(btc, 8),
            "most_recent_buy_price": state.get("last_buy_price"),
            "most_recent_buy_time": state.get("last_buy_time"),
            "most_recent_sell_price": state.get("last_sell_price"),
            "most_recent_sell_time": state.get("last_sell_time"),
        }

    def process_signal(self, signal: str, current_price: float) -> dict | None:
        """
        Execute a trade based on the ML signal if applicable.

        Returns the trade dict if a trade was executed, else None.
        """
        if signal == "Buy":
            return self.execute_buy(current_price)
        elif signal == "Sell":
            return self.execute_sell(current_price)
        return None
