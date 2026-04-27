# 📈 Real-Time AI Crypto Trading Bot Dashboard

> **🚧 Work In Progress:** This project is currently in active development. Features and documentation are being updated continuously.

Welcome to the **Real-Time Crypto Trading Bot Dashboard**! This project is a full-stack monorepo featuring a powerful machine learning-driven trading bot and a sleek, real-time React dashboard. 

The bot is connecting to the Binance WebSocket API, streaming live BTCUSDT data, feeding it into an LSTM model to predict market movements, and executing simulated trades in a local SQLite-backed wallet. The entire operation is being visualized live on a high-performance React dashboard.

---

## ✨ Features

- **Live Market Data:** Streaming real-time `BTCUSDT` klines directly from Binance via WebSockets.
- **AI-Driven Trading:** Utilizing an LSTM (Long Short-Term Memory) model trained on historical market data to predict "Buy" and "Sell" signals with associated confidence levels.
- **Simulated Wallet:** Managing a virtual portfolio (USDT/BTC) using SQLite to track performance, calculating PnL, and recording all executed trades without risking real money.
- **Real-Time Dashboard:** A responsive, modern React dashboard that is visualizing price action (Chart.js), portfolio value, PnL, and live trade executions seamlessly using WebSocket broadcasting.
- **Asynchronous Backend:** Built with FastAPI, handling concurrent WebSocket connections and background tasks efficiently.

---

## 🛠️ Technology Stack

### Backend
- **Python 3.10+**
- **FastAPI** (REST API & WebSockets)
- **Uvicorn** (ASGI server)
- **TensorFlow / Keras** (LSTM Machine Learning Model)
- **Scikit-Learn** (Data Normalization)
- **SQLite / aiosqlite** (Simulated Wallet & Trade Database)
- **python-binance** & **websockets** (Data streaming)

### Frontend
- **React 19**
- **Vite** (Build tool)
- **Chart.js & react-chartjs-2** (Live data visualization)
- **Bootstrap 5 & Bootstrap Icons** (Styling & Icons)
- **reconnecting-websocket** (Resilient real-time communication)

---

## 🚀 Getting Started

Follow these steps to run the application locally.

### 1. Clone the Repository

```bash
git clone https://github.com/Vaibhavsingh167/Binance_Crypto_Bot.git
cd Binance_Crypto_Bot
```

### 2. Backend Setup

Open a terminal and navigate to the `backend` directory (or run from root).

1. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
2. **Install dependencies:**
   ```bash
   pip install -r backend/requirements.txt
   ```
3. **Environment Variables:**
   Create a `.env` file in the root of the backend directory (or project root depending on your path setup). 
   ```env
   BINANCE_API_KEY=your_api_key_here
   BINANCE_API_SECRET=your_api_secret_here
   INITIAL_WALLET_BALANCE=10000
   ```
4. **Run the FastAPI server:**
   ```bash
   cd backend
   uvicorn app.main:app --reload --port 8000
   ```
   The backend API will be available at `http://localhost:8000` and the WebSocket at `ws://localhost:8000/ws/stream`.

### 3. Frontend Setup

Open a new terminal and navigate to the `frontend` directory.

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```
2. **Start the development server:**
   ```bash
   npm run dev
   ```
3. **View the Dashboard:**
   Open your browser and navigate to the URL provided by Vite (usually `http://localhost:5173`).

---

## 🧠 Machine Learning Model Pipeline

The machine learning pipeline is housed in the root python scripts (`train.py`, `dataset.py`, etc.). 

1. **Data Collection:** Historical data is being collected and stored in `trading_bot.db`.
2. **Indicators:** Technical indicators like EMA (10, 20) and RSI (14) are being calculated.
3. **Sequence Creation:** The data is being windowed (e.g., 50 previous periods) to create sequences for the LSTM.
4. **Model Architecture:** The model is using stacked LSTM layers with Dropout for regularization, followed by a Dense sigmoid output layer.
5. **Inference:** The backend is loading this pre-trained `.h5` model and a `.pkl` scaler to normalize live incoming data and emit predictions.

---

## 🔒 Disclaimer

This software is for **educational and research purposes only**. Do not use this bot to trade with real money. Cryptocurrency trading is highly volatile and risky. The developers assume no liability for financial losses incurred.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/Vaibhavsingh167/Binance_Crypto_Bot/issues).

---

<div align="center">
  <b>Being built with ❤️ by Vaibhav Singh</b>
</div>
