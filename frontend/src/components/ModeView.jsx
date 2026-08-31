import React from 'react'
import { Bar } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

export default function ModeView({ data, results }) {
  if (!data) {
    return (
      <div className="alert alert-info">Load data to calculate the most visited URL.</div>
    )
  }

  const mode = results?.mode

  if (!mode) {
    return (
      <div className="alert alert-info">
        Run the analysis to generate mode results.
      </div>
    )
  }

  const top10 = mode.top_10 || []
  const chartLabels = top10.map(([, url]) => (url.length > 25 ? url.slice(0, 24) + '…' : url))
  const chartValues = top10.map(([, count]) => count)

  const barData = {
    labels: chartLabels,
    datasets: [
      {
        label: 'Visit count',
        data: chartValues,
        backgroundColor: '#2563eb',
        borderRadius: 4,
      },
    ],
  }

  const barOptions = {
    indexAxis: 'y',
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      title: { display: true, text: 'Top 10 URLs by visits' },
    },
  }

  return (
    <div>
      {mode.is_multimodal && (
        <div className="alert alert-warning">
          {mode.all_modes.length} URLs are tied for the highest visit count.
        </div>
      )}

      <div className="mode-card">
        <div className="label">Most visited URL</div>
        <div className="url">{mode.mode_url}</div>
        <div className="count">
          Visited <strong>{mode.mode_count.toLocaleString()}</strong> times
        </div>
      </div>

      <h3>Summary</h3>
      <div className="metrics-grid">
        <div className="metric">
          <div className="metric-label">Total entries</div>
          <div className="metric-value">{mode.total_urls.toLocaleString()}</div>
        </div>
        <div className="metric">
          <div className="metric-label">Unique URLs</div>
          <div className="metric-value">{mode.unique_urls.toLocaleString()}</div>
        </div>
        <div className="metric">
          <div className="metric-label">Duplicate entries</div>
          <div className="metric-value">{mode.duplicate_count.toLocaleString()}</div>
        </div>
        <div className="metric">
          <div className="metric-label">Duplicate rate</div>
          <div className="metric-value">{mode.duplicate_percentage.toFixed(1)}%</div>
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-box">
          <div style={{ height: '380px' }}>
            <Bar data={barData} options={barOptions} />
          </div>
        </div>
        <div className="chart-box">
          <h3 style={{ marginBottom: '0.75rem' }}>Top URLs Table</h3>
          <div className="table-wrapper" style={{ maxHeight: '380px' }}>
            <table>
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>URL</th>
                  <th>Visit Count</th>
                </tr>
              </thead>
              <tbody>
                {top10.map(([url, count], i) => (
                  <tr key={i}>
                    <td>{i + 1}</td>
                    <td style={{ maxWidth: '280px', wordBreak: 'break-all' }}>{url}</td>
                    <td>{count.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {mode.is_multimodal && (
        <>
          <h3>URLs Tied For Mode</h3>
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>URL</th>
                  <th>Visit Count</th>
                </tr>
              </thead>
              <tbody>
                {mode.all_modes.map(([url, count], i) => (
                  <tr key={i}>
                    <td style={{ wordBreak: 'break-all' }}>{url}</td>
                    <td>{count.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  )
}
