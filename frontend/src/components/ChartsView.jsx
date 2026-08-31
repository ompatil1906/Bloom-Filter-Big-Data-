import React, { useMemo } from 'react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  RadialLinearScale,
} from 'chart.js'
import { Bar, Pie, Line } from 'react-chartjs-2'
import { formatBytes } from '../utils/formatters'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  RadialLinearScale
)

export default function ChartsView({ data, results }) {
  const charts = useMemo(() => {
    if (!results) return null
    const s = results.accuracy_stats
    const bf = results.bloom_filter

    const pieData = {
      labels: ['True Duplicate', 'First Seen', 'False Positive', 'False Negative'],
      datasets: [
        {
          data: [s.true_positives, s.true_negatives, s.false_positives, s.false_negatives],
          backgroundColor: ['#16a34a', '#2563eb', '#d97706', '#dc2626'],
          borderWidth: 1,
        },
      ],
    }

    const pieOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'bottom' },
        title: { display: true, text: 'Prediction outcomes' },
      },
    }

    const freqData = {
      labels: results.frequency_data.map((d) =>
        d.url.length > 20 ? d.url.slice(0, 19) + '…' : d.url
      ),
      datasets: [
        {
          label: 'Visits',
          data: results.frequency_data.map((d) => d.visits),
          backgroundColor: '#475569',
          borderRadius: 3,
        },
      ],
    }

    const freqOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        title: { display: true, text: 'Top 20 URLs by visit count' },
      },
      scales: {
        x: { ticks: { maxRotation: 45, minRotation: 45, callback: (v) => String(v).slice(0, 12) } },
      },
    }

    const memoryData = {
      labels: ['Bloom filter', 'Python HashSet'],
      datasets: [
        {
          label: 'Memory usage (bytes)',
          data: [results.memory.bloom_bytes, results.memory.hashset_bytes],
          backgroundColor: ['#16a34a', '#dc2626'],
          borderRadius: 4,
        },
      ],
    }

    const memoryOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        title: {
          display: true,
          text: `Bloom filter saves ${results.memory.savings_percentage.toFixed(1)}% memory`,
        },
        tooltip: {
          callbacks: {
            label: (ctx) => formatBytes(ctx.parsed.y),
          },
        },
      },
    }

    const fillHistory = results.fill_history || []

    const fillData = {
      labels: fillHistory.map((h) => h.items),
      datasets: [
        {
          label: 'Fill ratio',
          data: fillHistory.map((h) => h.fill_ratio),
          borderColor: '#2563eb',
          backgroundColor: '#2563eb',
          tension: 0.3,
          pointRadius: 3,
        },
      ],
    }

    const fillOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        title: { display: true, text: 'Bit array fill ratio' },
      },
      scales: {
        y: {
          min: 0,
          max: 1,
          ticks: { callback: (v) => `${(v * 100).toFixed(0)}%` },
        },
      },
    }

    const fpCurve = results.fp_rate_curve
    const fpData = {
      labels: fpCurve.n_values,
      datasets: [
        {
          label: 'False-positive rate',
          data: fpCurve.fp_rates,
          borderColor: '#2563eb',
          backgroundColor: '#2563eb',
          tension: 0.3,
          pointRadius: 0,
          fill: false,
        },
        {
          label: `Target (${(fpCurve.target_fpr * 100).toFixed(2)}%)`,
          data: fpCurve.n_values.map(() => fpCurve.target_fpr),
          borderColor: '#dc2626',
          borderDash: [6, 6],
          pointRadius: 0,
          fill: false,
        },
      ],
    }

    const fpOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: { display: true, text: 'Theoretical false-positive rate as the filter fills' },
      },
      scales: {
        y: {
          ticks: { callback: (v) => `${(v * 100).toFixed(2)}%` },
        },
      },
    }

    return { pieData, pieOptions, freqData, freqOptions, memoryData, memoryOptions, fillData, fillOptions, fpData, fpOptions, bf, s, hasFillHistory: fillHistory.length > 0 }
  }, [results])

  if (!data) {
    return <div className="alert alert-info">Load data to view charts.</div>
  }

  if (!results || !charts) {
    return <div className="alert alert-info">Run the analysis to unlock charts.</div>
  }

  const confusionData = {
    labels: ['Predicted first seen', 'Predicted duplicate'],
    datasets: [
      {
        label: 'Actually first seen',
        data: [charts.s.true_negatives, charts.s.false_positives],
        backgroundColor: ['#93c5fd', '#93c5fd'],
      },
      {
        label: 'Actually duplicate',
        data: [charts.s.false_negatives, charts.s.true_positives],
        backgroundColor: ['#60a5fa', '#3b82f6'],
      },
    ],
  }

  const confusionOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: { x: { stacked: true }, y: { stacked: true } },
    plugins: {
      title: { display: true, text: 'Confusion matrix (counts)' },
    },
  }

  const bitSnapshot = results.bit_snapshot
  const setBits = bitSnapshot.filter((b) => b === 1).length

  return (
    <div>
      <h3>Bit Array Snapshot</h3>
      <div className="card-caption">
        {setBits} of {bitSnapshot.length} sampled bits are set (fill ~
        {((setBits / bitSnapshot.length) * 100).toFixed(1)}% of sampled region).
      </div>
      <div className="chart-box" style={{ margin: '0.75rem 0 1.5rem' }}>
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: `repeat(50, 1fr)`,
            gap: '1px',
            background: '#e5e7eb',
            padding: '1px',
          }}
        >
          {bitSnapshot.map((bit, i) => (
            <div
              key={i}
              style={{
                height: '8px',
                background: bit === 1 ? '#2563eb' : '#eff6ff',
              }}
            />
          ))}
        </div>
        <div className="card-caption">
          Bloom filter bit array sample ({charts.bf.size.toLocaleString()} total bits)
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-box">
          <div style={{ height: '320px' }}>
            <Pie data={charts.pieData} options={charts.pieOptions} />
          </div>
        </div>
        <div className="chart-box">
          <div style={{ height: '320px' }}>
            <Bar data={confusionData} options={confusionOptions} />
          </div>
        </div>
      </div>

      <h3>Memory Comparison</h3>
      <div className="metrics-grid">
        <div className="metric">
          <div className="metric-label">Bloom filter</div>
          <div className="metric-value">{charts.bf.memory_formatted}</div>
        </div>
        <div className="metric">
          <div className="metric-label">Python HashSet</div>
          <div className="metric-value">{results.memory.hashset_formatted}</div>
        </div>
        <div className="metric delta-positive">
          <div className="metric-label">Memory saved</div>
          <div className="metric-value">{results.memory.savings_percentage.toFixed(1)}%</div>
        </div>
      </div>
      <div className="chart-box" style={{ marginBottom: '1rem' }}>
        <div style={{ height: '320px' }}>
          <Bar data={charts.memoryData} options={charts.memoryOptions} />
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-box">
          <div style={{ height: '320px' }}>
            {charts.hasFillHistory ? (
              <Line data={charts.fillData} options={charts.fillOptions} />
            ) : (
              <div className="alert alert-info">Fill history is not available for this dataset.</div>
            )}
          </div>
        </div>
        <div className="chart-box">
          <div style={{ height: '320px' }}>
            <Line data={charts.fpData} options={charts.fpOptions} />
          </div>
        </div>
      </div>

      <h3>Frequency Distribution</h3>
      <div className="chart-box">
        <div style={{ height: '380px' }}>
          <Bar data={charts.freqData} options={charts.freqOptions} />
        </div>
      </div>
    </div>
  )
}
