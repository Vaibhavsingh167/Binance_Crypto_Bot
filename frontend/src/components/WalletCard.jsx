/**
 * WalletCard.jsx — Single metric display card with dynamic styling.
 *
 * Props:
 *   label    — Card label (e.g., "Portfolio Value")
 *   value    — Formatted display value (e.g., "$10,234.50")
 *   subValue — Optional secondary text (e.g., timestamp)
 *   icon     — Bootstrap icon class (e.g., "bi-wallet2")
 *   accent   — "cyan" | "green" | "red" | "amber" — top bar color
 *   isPnl    — If true, dynamically colors based on positive/negative value
 *   rawValue — Raw numeric for PnL coloring decisions
 */

export default function WalletCard({
  label,
  value,
  subValue,
  icon,
  accent = 'cyan',
  isPnl = false,
  rawValue = 0,
}) {
  // Determine dynamic class for PnL values
  let valueClass = 'metric-value';
  if (isPnl) {
    if (rawValue > 0) valueClass += ' profit';
    else if (rawValue < 0) valueClass += ' loss';
  }

  return (
    <div className={`glass-card metric-card ${accent}`} id={`metric-${label.replace(/\s+/g, '-').toLowerCase()}`}>
      <div className="metric-label">
        {icon && <i className={`bi ${icon}`}></i>}
        {label}
      </div>
      <div className={valueClass}>{value}</div>
      {subValue && <div className="metric-sub">{subValue}</div>}
    </div>
  );
}
