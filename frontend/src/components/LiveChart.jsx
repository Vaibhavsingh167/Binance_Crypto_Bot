/**
 * LiveChart.jsx — Real-time BTCUSDT price chart with Chart.js.
 *
 * - Rolling window of 100 data points
 * - Gradient fill under the line
 * - Animated transitions
 * - Responsive container
 */

import { useRef, useEffect, useMemo } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
);

const MAX_POINTS = 100;

export default function LiveChart({ priceHistory }) {
  const chartRef = useRef(null);

  // Derive labels and data from priceHistory array
  const labels = useMemo(
    () =>
      priceHistory.map((p) => {
        const d = new Date(p.timestamp);
        return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
      }),
    [priceHistory]
  );

  const prices = useMemo(() => priceHistory.map((p) => p.price), [priceHistory]);

  const data = useMemo(() => {
    return {
      labels,
      datasets: [
        {
          label: 'BTCUSDT',
          data: prices,
          borderColor: '#00d4ff',
          borderWidth: 2,
          pointRadius: 0,
          pointHoverRadius: 4,
          pointHoverBackgroundColor: '#00d4ff',
          pointHoverBorderColor: '#fff',
          fill: true,
          backgroundColor: (ctx) => {
            const chart = ctx.chart;
            const { ctx: context, chartArea } = chart;
            if (!chartArea) return 'rgba(0,212,255,0.05)';
            const gradient = context.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);
            gradient.addColorStop(0, 'rgba(0, 212, 255, 0.15)');
            gradient.addColorStop(0.5, 'rgba(0, 212, 255, 0.05)');
            gradient.addColorStop(1, 'rgba(0, 212, 255, 0)');
            return gradient;
          },
          tension: 0.35,
        },
      ],
    };
  }, [labels, prices]);

  const options = useMemo(
    () => ({
      responsive: true,
      maintainAspectRatio: false,
      animation: {
        duration: 300,
        easing: 'easeOutQuart',
      },
      interaction: {
        mode: 'index',
        intersect: false,
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: 'rgba(12, 17, 32, 0.95)',
          borderColor: 'rgba(0, 212, 255, 0.2)',
          borderWidth: 1,
          titleColor: '#8b95a8',
          bodyColor: '#e8edf5',
          bodyFont: { family: "'JetBrains Mono', monospace", size: 13, weight: '600' },
          titleFont: { family: "'Inter', sans-serif", size: 11 },
          padding: 12,
          cornerRadius: 10,
          displayColors: false,
          callbacks: {
            label: (ctx) => `$${ctx.parsed.y.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
          },
        },
      },
      scales: {
        x: {
          display: true,
          grid: {
            color: 'rgba(100, 160, 255, 0.04)',
            drawBorder: false,
          },
          ticks: {
            color: '#4a5568',
            font: { family: "'JetBrains Mono', monospace", size: 10 },
            maxTicksLimit: 8,
            maxRotation: 0,
          },
        },
        y: {
          display: true,
          position: 'right',
          grid: {
            color: 'rgba(100, 160, 255, 0.04)',
            drawBorder: false,
          },
          ticks: {
            color: '#4a5568',
            font: { family: "'JetBrains Mono', monospace", size: 11 },
            callback: (value) => '$' + value.toLocaleString(),
          },
        },
      },
    }),
    []
  );

  return (
    <div className="chart-container">
      <Line ref={chartRef} data={data} options={options} />
    </div>
  );
}
