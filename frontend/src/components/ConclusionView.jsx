import React from 'react'

export default function ConclusionView({ data, results }) {
  if (!data) {
    return <div className="alert alert-info">Load data and run analysis to generate the conclusion.</div>
  }

  if (!results) {
    return <div className="alert alert-info">Click <strong>Run analysis</strong> in the sidebar to build the conclusion.</div>
  }

  const s = results.accuracy_stats
  const bf = results.bloom_filter
  const mode = results.mode
  const total = data.summary.total_entries
  const unique = data.summary.unique_urls_in_data

  const metricsRow = {
    total,
    unique,
    target_fpr: bf.false_positive_rate,
    bits_m: bf.size,
    hashes_k: bf.hash_count,
    bloom_bytes: results.memory.bloom_bytes,
    hashset_bytes: results.memory.hashset_bytes,
    savings_pct: results.memory.savings_percentage,
    ...s,
  }

  const downloadJSON = () => {
    const blob = new Blob([JSON.stringify(metricsRow, null, 2)], {
      type: 'application/json',
    })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'bloom_metrics.json'
    a.click()
    URL.revokeObjectURL(url)
  }

  const downloadCSV = () => {
    const headers = Object.keys(metricsRow)
    const line = headers.join(',')
    const values = headers.map((h) => metricsRow[h])
    const csv = `${line}\n${values.join(',')}`
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'bloom_metrics.csv'
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div>
      <div className="metrics-grid">
        <div className="metric">
          <div className="metric-label">Dataset</div>
          <div className="metric-value">{total.toLocaleString()} visits</div>
        </div>
        <div className="metric delta-positive">
          <div className="metric-label">Bloom memory</div>
          <div className="metric-value">{bf.memory_formatted}</div>
          <div className="metric-sub">-{results.memory.savings_percentage.toFixed(1)}% vs HashSet</div>
        </div>
        <div className="metric">
          <div className="metric-label">Accuracy / F1</div>
          <div className="metric-value">
            {s.accuracy.toFixed(1)}% / {s.f1_score.toFixed(1)}%
          </div>
        </div>
        <div className="metric">
          <div className="metric-label">Most visited</div>
          <div className="metric-value">{mode.mode_count.toLocaleString()}×</div>
          <div className="metric-sub" style={{ wordBreak: 'break-all' }}>{mode.mode_url}</div>
        </div>
      </div>

      <div className="panel" style={{ background: 'linear-gradient(135deg, #eff6ff 0%, #f0fdf4 100%)', borderColor: '#bfdbfe' }}>
        <h4 style={{ marginBottom: '0.5rem', color: '#1e40af' }}>What we made</h4>
        <p>
          A <strong>big-data efficient duplicate detector</strong> for browser history using a
          Bloom filter plus exact <strong>mode calculation</strong> (most visited URL). Pipeline:
          ingest CSV → stream through <code>m={bf.size.toLocaleString()}</code> /{' '}
          <code>k={bf.hash_count}</code> Bloom filter vs HashSet ground truth → evaluate.
        </p>
        <h4 style={{ margin: '0.75rem 0 0.5rem', color: '#1e40af' }}>Key conclusions</h4>
        <ul style={{ marginLeft: '1.2rem', color: '#334155' }}>
          <li>
            <strong>Memory wins at scale:</strong> {bf.memory_formatted} vs{' '}
            {results.memory.hashset_formatted} —{' '}
            <strong>{results.memory.savings_percentage.toFixed(1)}% saved</strong>. Storing
            hashes/bits beats storing full URL strings; gap widens with millions of URLs.
          </li>
          <li>
            <strong>Accuracy is usable:</strong> {s.accuracy.toFixed(2)}% accuracy,{' '}
            {s.precision.toFixed(2)}% precision, <strong>{s.recall.toFixed(2)}% recall</strong> —
            false negatives are <strong>{s.false_negatives}</strong> (guaranteed 0). Only price is{' '}
            {s.actual_fpr.toFixed(2)}% false positives (near target{' '}
            {(bf.false_positive_rate * 100).toFixed(2)}%).
          </li>
          <li>
            <strong>When to use:</strong> Best as a <em>first-pass filter</em> before expensive
            exact checks (DB / disk). Not suitable if any false positive is unacceptable.
          </li>
          <li>
            <strong>Mode insight:</strong> Top URL <code>{mode.mode_url}</code> (
            {mode.mode_count.toLocaleString()} visits) reflects power-law browsing — small pool
            drives most duplicates ({mode.duplicate_percentage.toFixed(1)}% duplicates).
          </li>
          <li>
            <strong>Tunable trade-off:</strong> Lower target FPR → larger <em>m</em> → more
            memory; higher fill ratio → FPR climbs. Current fill {(bf.fill_ratio * 100).toFixed(1)}% at{' '}
            {bf.items_added.toLocaleString()} inserts.
          </li>
        </ul>
        <p style={{ marginTop: '0.75rem', color: '#334155' }}>
          <strong>Bottom line:</strong> For big browser logs, Bloom filter gives ~
          <strong>{results.memory.savings_percentage.toFixed(0)}% memory cut</strong> for ~
          <strong>{s.actual_fpr.toFixed(1)}% extra checks</strong> — a practical Big Data trade-off.
        </p>
      </div>

      <h3>Export Metrics for Report</h3>
      <div className="export-row">
        <button className="btn btn-secondary" onClick={downloadJSON}>
          Download metrics JSON
        </button>
        <button className="btn btn-secondary" onClick={downloadCSV}>
          Download metrics CSV
        </button>
      </div>
      <div className="card-caption">
        Metrics include total/unique/target FPR, m bits, k hashes, memory savings, and all
        classification statistics.
      </div>
    </div>
  )
}
