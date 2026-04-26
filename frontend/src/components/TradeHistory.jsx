/**
 * TradeHistory.jsx — Recent trades table.
 *
 * Props:
 *   trades — Array of { action, price, quantity, timestamp }
 */

export default function TradeHistory({ trades = [] }) {
  const formatTime = (ts) => {
    if (!ts) return '—';
    const d = new Date(ts);
    return d.toLocaleString([], {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  const formatPrice = (p) => {
    if (p == null) return '—';
    return '$' + Number(p).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  };

  const formatQty = (q) => {
    if (q == null) return '—';
    return Number(q).toFixed(8);
  };

  return (
    <div className="trade-table-wrap" id="trade-history">
      {trades.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)', fontSize: '0.82rem' }}>
          <i className="bi bi-clock-history" style={{ fontSize: '1.5rem', display: 'block', marginBottom: '0.5rem' }}></i>
          No trades executed yet. Waiting for signals...
        </div>
      ) : (
        <table className="trade-table">
          <thead>
            <tr>
              <th>Time</th>
              <th>Action</th>
              <th>Price</th>
              <th>Quantity (BTC)</th>
            </tr>
          </thead>
          <tbody>
            {trades.map((trade, idx) => (
              <tr key={idx} style={{ animation: idx === 0 ? 'fadeInUp 0.4s ease' : 'none' }}>
                <td>{formatTime(trade.timestamp)}</td>
                <td className={trade.action === 'BUY' ? 'action-buy' : 'action-sell'}>
                  <i className={`bi ${trade.action === 'BUY' ? 'bi-arrow-up-short' : 'bi-arrow-down-short'}`}></i>
                  {trade.action}
                </td>
                <td>{formatPrice(trade.price)}</td>
                <td style={{ fontFamily: 'var(--font-mono)' }}>{formatQty(trade.quantity)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
