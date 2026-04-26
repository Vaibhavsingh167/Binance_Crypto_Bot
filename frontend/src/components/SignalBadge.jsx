/**
 * SignalBadge.jsx — Buy / Sell / Hold signal indicator.
 *
 * Props:
 *   signal     — "Buy" | "Sell" | "Hold" | "Warming Up" | "Error"
 *   confidence — float 0–1
 */

export default function SignalBadge({ signal, confidence = 0 }) {
  const signalLower = (signal || 'hold').toLowerCase().replace(/\s+/g, '');
  let badgeClass = 'signal-badge ';
  let icon = '';
  let fillColor = '';

  switch (signalLower) {
    case 'buy':
      badgeClass += 'buy';
      icon = 'bi-arrow-up-circle-fill';
      fillColor = 'var(--green)';
      break;
    case 'sell':
      badgeClass += 'sell';
      icon = 'bi-arrow-down-circle-fill';
      fillColor = 'var(--red)';
      break;
    case 'hold':
      badgeClass += 'hold';
      icon = 'bi-pause-circle-fill';
      fillColor = 'var(--amber)';
      break;
    case 'warmingup':
      badgeClass += 'warming';
      icon = 'bi-hourglass-split';
      fillColor = 'var(--text-secondary)';
      break;
    default:
      badgeClass += 'warming';
      icon = 'bi-exclamation-circle';
      fillColor = 'var(--text-secondary)';
  }

  const confidencePct = Math.round(confidence * 100);

  return (
    <div className="signal-panel" id="signal-panel">
      <div className="signal-label">Model Signal</div>
      <div className={badgeClass}>
        <i className={`bi ${icon}`}></i>
        {signal || 'N/A'}
      </div>
      <div className="confidence-bar">
        <div
          className="confidence-fill"
          style={{
            width: `${confidencePct}%`,
            background: fillColor,
            boxShadow: `0 0 8px ${fillColor}`,
          }}
        />
      </div>
      <div className="confidence-text">
        Confidence: {confidencePct}%
      </div>
    </div>
  );
}
