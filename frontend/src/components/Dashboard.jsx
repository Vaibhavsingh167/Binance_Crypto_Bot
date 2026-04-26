/**
 * Dashboard.jsx — Main trading dashboard layout.
 *
 * Assembles all components into a responsive grid:
 * - Top: Live price + connection status
 * - Metric cards row: Portfolio Value, PnL, Last Buy, Last Sell
 * - Middle: Live Chart (8-col) + Signal Panel (4-col)
 * - Bottom: Trade History
 */

import { useState, useEffect, useRef } from 'react';
import useWebSocket from '../hooks/useWebSocket';
import LiveChart from './LiveChart';
import WalletCard from './WalletCard';
import SignalBadge from './SignalBadge';
import TradeHistory from './TradeHistory';

const MAX_PRICE_HISTORY = 100;

export default function Dashboard() {
  const { data, connectionStatus } = useWebSocket();

  // Price history for the chart — rolling window
  const [priceHistory, setPriceHistory] = useState([]);
  // Trade history for the table
  const [trades, setTrades] = useState([]);
  // Latest data snapshot
  const [latest, setLatest] = useState(null);

  // Track the previous data reference to avoid duplicate processing
  const prevDataRef = useRef(null);

  // Process incoming WebSocket data
  useEffect(() => {
    if (!data || data === prevDataRef.current) return;
    prevDataRef.current = data;

    setLatest(data);

    // Add to price history
    setPriceHistory((prev) => {
      const next = [...prev, { price: data.current_price, timestamp: data.timestamp }];
      if (next.length > MAX_PRICE_HISTORY) {
        return next.slice(next.length - MAX_PRICE_HISTORY);
      }
      return next;
    });

    // Track executed trades
    if (data.trade_executed) {
      setTrades((prev) => [data.trade_executed, ...prev].slice(0, 50));
    }
  }, [data]);

  // ---- Formatting helpers ----
  const formatUsd = (val) => {
    if (val == null) return '—';
    return '$' + Number(val).toLocaleString(undefined, {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
  };

  const formatPnl = (val, pct) => {
    if (val == null) return '—';
    const sign = val >= 0 ? '+' : '';
    return `${sign}${formatUsd(val)} (${sign}${pct}%)`;
  };

  const formatTime = (ts) => {
    if (!ts) return '—';
    const d = new Date(ts);
    return d.toLocaleString([], {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // ---- Derive display values ----
  const wallet = latest?.wallet || {};
  const currentPrice = latest?.current_price;
  const signal = latest?.model_signal || 'Warming Up';
  const confidence = latest?.confidence || 0;
  const pnl = wallet.current_pnl ?? 0;
  const pnlPct = wallet.pnl_percentage ?? 0;

  // Connection status display
  const statusMap = {
    OPEN: { dotClass: 'connected', text: 'Live' },
    CONNECTING: { dotClass: 'connecting', text: 'Connecting' },
    CLOSED: { dotClass: 'disconnected', text: 'Disconnected' },
  };
  const status = statusMap[connectionStatus] || statusMap.CLOSED;

  return (
    <div className="container-fluid px-3 px-md-4 py-3">
      {/* ---- Header Row ---- */}
      <div className="row align-items-center dashboard-header">
        <div className="col">
          <h1 className="dashboard-title">BTCUSDT Trading Terminal</h1>
          <p className="dashboard-subtitle">AI-Powered Real-Time Trading Signals</p>
        </div>
        <div className="col-auto text-end">
          <div className="d-flex align-items-center gap-3">
            {/* Live Price */}
            {currentPrice != null && (
              <div>
                <div className="live-price-label">BTC/USDT</div>
                <div className="live-price">{formatUsd(currentPrice)}</div>
              </div>
            )}
            {/* Connection Status */}
            <div className="d-flex align-items-center">
              <span className={`connection-dot ${status.dotClass}`}></span>
              <span className="status-text">{status.text}</span>
            </div>
          </div>
        </div>
      </div>

      {/* ---- Metric Cards Row ---- */}
      <div className="row g-3 mb-3">
        <div className="col-6 col-lg-3">
          <WalletCard
            label="Portfolio Value"
            value={formatUsd(wallet.total_portfolio_value)}
            subValue={`USDT: ${formatUsd(wallet.usdt_balance)} · BTC: ${wallet.btc_balance ?? 0}`}
            icon="bi-wallet2"
            accent="cyan"
          />
        </div>
        <div className="col-6 col-lg-3">
          <WalletCard
            label="Profit / Loss"
            value={formatPnl(pnl, pnlPct)}
            icon="bi-graph-up-arrow"
            accent={pnl >= 0 ? 'green' : 'red'}
            isPnl={true}
            rawValue={pnl}
          />
        </div>
        <div className="col-6 col-lg-3">
          <WalletCard
            label="Last Buy"
            value={formatUsd(wallet.most_recent_buy_price)}
            subValue={formatTime(wallet.most_recent_buy_time)}
            icon="bi-bag-plus-fill"
            accent="green"
          />
        </div>
        <div className="col-6 col-lg-3">
          <WalletCard
            label="Last Sell"
            value={formatUsd(wallet.most_recent_sell_price)}
            subValue={formatTime(wallet.most_recent_sell_time)}
            icon="bi-bag-dash-fill"
            accent="red"
          />
        </div>
      </div>

      {/* ---- Chart + Signal Row ---- */}
      <div className="row g-3 mb-3">
        {/* Live Chart */}
        <div className="col-12 col-lg-8">
          <div className="glass-card">
            <div className="section-title">
              <i className="bi bi-graph-up"></i>
              Live Price Chart
            </div>
            <LiveChart priceHistory={priceHistory} />
          </div>
        </div>

        {/* Signal Panel */}
        <div className="col-12 col-lg-4">
          <div className="glass-card h-100">
            <SignalBadge signal={signal} confidence={confidence} />
          </div>
        </div>
      </div>

      {/* ---- Trade History Row ---- */}
      <div className="row g-3">
        <div className="col-12">
          <div className="glass-card">
            <div className="section-title">
              <i className="bi bi-clock-history"></i>
              Recent Trades
            </div>
            <TradeHistory trades={trades} />
          </div>
        </div>
      </div>
    </div>
  );
}
