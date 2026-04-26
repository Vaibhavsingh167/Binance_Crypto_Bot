"""
ml_engine.py — ML inference engine for the trading bot.

Loads the pre-trained Keras model and scikit-learn scaler,
maintains a rolling buffer, and generates Buy/Sell/Hold signals.
"""

import os
import pickle
import logging
from collections import deque

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
MODEL_PATH = os.path.join(MODELS_DIR, "model_BTCUSDT.h5")
SCALER_PATH = os.path.join(MODELS_DIR, "scaler_BTCUSDT.pkl")

# ---------------------------------------------------------------------------
# Feature config — must match train.py exactly
# ---------------------------------------------------------------------------
FEATURES = ["open", "high", "low", "close", "volume", "ema_10", "ema_20", "rsi"]
WINDOW_SIZE = 50

# Signal thresholds on the sigmoid output
BUY_THRESHOLD = 0.6
SELL_THRESHOLD = 0.4


class MLEngine:
    """
    Singleton-style ML engine that:
    1. Loads model + scaler once at startup.
    2. Maintains a rolling deque of raw OHLCV candles.
    3. Computes technical indicators (EMA-10, EMA-20, RSI-14).
    4. Scales features and runs inference.
    """

    def __init__(self) -> None:
        self._model = None
        self._scaler = None
        # Raw candle buffer — we need extra rows for indicator warm-up
        # RSI needs 14 periods, EMA-20 needs ~40 periods for convergence,
        # plus 50 for the sequence window. 120 is a safe buffer.
        self._raw_buffer: deque[dict] = deque(maxlen=120)
        self._ready = False

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def load(self) -> None:
        """Load the Keras model and scaler from disk."""
        try:
            # Lazy import tensorflow — heavy dependency
            from tensorflow.keras.models import load_model  # type: ignore

            logger.info("Loading model from %s", MODEL_PATH)
            self._model = load_model(MODEL_PATH)
            logger.info("Model loaded successfully. Input shape: %s", self._model.input_shape)

            logger.info("Loading scaler from %s", SCALER_PATH)
            with open(SCALER_PATH, "rb") as f:
                self._scaler = pickle.load(f)
            logger.info("Scaler loaded successfully.")

        except Exception as e:
            logger.error("Failed to load ML assets: %s", e)
            raise

    @property
    def is_ready(self) -> bool:
        """True once we have enough data points for a full prediction."""
        return self._ready

    # ------------------------------------------------------------------
    # Data ingestion
    # ------------------------------------------------------------------

    def add_candle(self, candle: dict) -> None:
        """
        Add a raw OHLCV candle to the buffer.

        Expected keys: open, high, low, close, volume
        All values should be floats.
        """
        self._raw_buffer.append({
            "open": float(candle["open"]),
            "high": float(candle["high"]),
            "low": float(candle["low"]),
            "close": float(candle["close"]),
            "volume": float(candle["volume"]),
        })

        # We need at least WINDOW_SIZE + enough rows for indicator convergence
        # RSI-14 drops 14 NaN rows, EMA needs ~20 for convergence
        # So we need WINDOW_SIZE + 20 raw candles minimum
        min_required = WINDOW_SIZE + 20
        if len(self._raw_buffer) >= min_required:
            self._ready = True

    # ------------------------------------------------------------------
    # Technical indicators — mirrors train.py exactly
    # ------------------------------------------------------------------

    @staticmethod
    def _add_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Compute EMA-10, EMA-20, and RSI-14. Drops NaN rows."""
        # EMA
        df["ema_10"] = df["close"].ewm(span=10).mean()
        df["ema_20"] = df["close"].ewm(span=20).mean()

        # RSI-14
        delta = df["close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df["rsi"] = 100 - (100 / (1 + rs))

        df.dropna(inplace=True)
        df.reset_index(drop=True, inplace=True)
        return df

    # ------------------------------------------------------------------
    # Inference
    # ------------------------------------------------------------------

    def predict(self) -> dict:
        """
        Run inference on the current buffer.

        Returns:
            {
                "signal": "Buy" | "Sell" | "Hold" | "Warming Up",
                "confidence": float (0-1),
                "raw_score": float (sigmoid output),
            }
        """
        if not self._ready:
            return {"signal": "Warming Up", "confidence": 0.0, "raw_score": 0.5}

        if self._model is None or self._scaler is None:
            return {"signal": "Error", "confidence": 0.0, "raw_score": 0.5}

        try:
            # Build DataFrame from raw buffer
            df = pd.DataFrame(list(self._raw_buffer))

            # Add technical indicators (this drops some initial rows)
            df = self._add_indicators(df)

            if len(df) < WINDOW_SIZE:
                return {"signal": "Warming Up", "confidence": 0.0, "raw_score": 0.5}

            # Take the last WINDOW_SIZE rows
            window_df = df.tail(WINDOW_SIZE).copy()

            # Scale features using the loaded scaler
            scaled_data = self._scaler.transform(window_df[FEATURES].values)

            # Reshape for LSTM: (1, WINDOW_SIZE, num_features)
            X = np.array([scaled_data])

            # Predict
            raw_score = float(self._model.predict(X, verbose=0)[0][0])

            # Determine signal
            if raw_score > BUY_THRESHOLD:
                signal = "Buy"
                confidence = raw_score
            elif raw_score < SELL_THRESHOLD:
                signal = "Sell"
                confidence = 1.0 - raw_score
            else:
                signal = "Hold"
                confidence = 1.0 - abs(raw_score - 0.5) * 2  # higher near 0.5 edges

            return {
                "signal": signal,
                "confidence": round(confidence, 4),
                "raw_score": round(raw_score, 4),
            }

        except Exception as e:
            logger.error("Prediction error: %s", e, exc_info=True)
            return {"signal": "Error", "confidence": 0.0, "raw_score": 0.5}


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------
engine = MLEngine()
