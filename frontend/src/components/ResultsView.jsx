import React, { useState } from 'react'

export default function ResultsView({ data, results, capacityPct }) {
  const [filter, setFilter] = useState('All')

  if (!data) {
    return (
      <div className="alert alert-info">
        Load a dataset from the <strong>Data</strong> page (sidebar) before running the analysis.
      </div>
    )
  }

  if (!results) {
    return (
      <div className="alert alert-info">
        Configure the false-positive rate and click <strong>Run analysis</strong> in the sidebar.
      </div>
    )
  }

  const s = results.accuracy_stats
  const bf = results.bloom_filter
  const total = data.summary.total_entries
  const unique = data.summary.unique_urls_in_data
  const cfg = results.config || {}

  const qualityLabel = (value, good, high) =>
    value >= good ? { text: 'Good', cls: 'q-good' } : value >= high ? { text: 'Acceptable', cls: 'q-accept' } : { text: 'Poor', cls: 'q-poor' }

  const accQ = qualityLabel(s.accuracy, 95, 80)
  const precQ = qualityLabel(s.precision, 90, 70)
  const recQ = qualityLabel(s.recall, 99, 90)

  const filteredResults = results.results.filter((r) => filter === 'All' || r.status === filter)

  const resolvedCap = cfg.capacity_pct ?? capacityPct ?? 100

  return (
    <div>
      <div className="config-strip">
        <div className="config-strip-title">Analysis context</div>
        <div className="config-strip-items">
          <span>Dataset: <strong>{data.summary.total_entries.toLocaleString()}</strong> visits / <strong>{unique.toLocaleString()}</strong> unique</span>
          <span>Target FPR: <strong>{(bf.false_positive_rate * 100).toFixed(2)}%</strong></span>
          <span>Capacity: <strong>{resolvedCap}%</strong></span>
          <span>Filter sized for <strong>{cfg.expected_items?.toLocaleString() ?? '—'}</strong> items</span>
          <span>Actual FPR: <strong>{s.actual_fpr.toFixed(3)}%</strong></span>
        </div>
      </div>

      <h3>Confusion Matrix Counts</h3>
      <div className="metrics-grid">
        <div className="metric">
          <div className="metric-label">True duplicates (TP)</div>
          <div className="metric-value">{s.true_positives.toLocaleString()}</div>
        </div>
        <div className="metric">
          <div className="metric-label">First seen (TN)</div>
          <div className="metric-value">{s.true_negatives.toLocaleString()}</div>
        </div>
        <div className="metric">
          <div className="metric-label">False positives (FP)</div>
          <div className="metric-value">{s.false_positives.toLocaleString()}</div>
          <div className="metric-sub">{s.actual_fpr.toFixed(2)}% FPR</div>
        </div>
        <div className="metric">
          <div className="metric-label">False negatives (FN)</div>
          <div className="metric-value">{s.false_negatives.toLocaleString()}</div>
          <div className="metric-sub">0 is ideal</div>
        </div>
      </div>

      <h3>Evaluation Metrics</h3>
      <div className="metrics-grid">
        <div className="metric">
          <div className="metric-label">Accuracy</div>
          <div className="metric-value">{s.accuracy.toFixed(2)}%</div>
          <div className="metric-sub"><span className={`q-badge ${accQ.cls}`}>{accQ.text}</span></div>
        </div>
        <div className="metric">
          <div className="metric-label">Precision</div>
          <div className="metric-value">{s.precision.toFixed(2)}%</div>
          <div className="metric-sub"><span className={`q-badge ${precQ.cls}`}>{precQ.text}</span></div>
        </div>
        <div className="metric">
          <div className="metric-label">Recall</div>
          <div className="metric-value">{s.recall.toFixed(2)}%</div>
          <div className="metric-sub"><span className={`q-badge ${recQ.cls}`}>{recQ.text}</span></div>
        </div>
        <div className="metric">
          <div className="metric-label">F1 Score</div>
          <div className="metric-value">{s.f1_score.toFixed(2)}%</div>
        </div>
      </div>

      <div className="card-caption" style={{ marginBottom: '1.5rem' }}>
        Non-zero false positives come from sizing the filter at <strong>{resolvedCap}%</strong> of the true unique count. Lower the capacity to make this effect (and the false-positive cost) more visible.
      </div>
      <div className="metrics-grid">
        <div className="metric">
          <div className="metric-label">Actual FPR</div>
          <div className="metric-value">{s.actual_fpr.toFixed(3)}%</div>
          <div className="metric-sub">target {(bf.false_positive_rate * 100).toFixed(2)}%</div>
        </div>
        <div className="metric">
          <div className="metric-label">Theoretical FPR</div>
          <div className="metric-value">{s.theoretical_fpr.toFixed(3)}%</div>
        </div>
        <div className="metric">
          <div className="metric-label">Specificity</div>
          <div className="metric-value">{s.specificity.toFixed(2)}%</div>
        </div>
        <div className="metric">
          <div className="metric-label">False Neg Rate</div>
          <div className="metric-value">{s.actual_fnr.toFixed(3)}%</div>
        </div>
      </div>

      {s.false_negatives === 0 ? (
        <div className="alert alert-success">
          Bloom guarantee holds — 0 false negatives. No duplicate was missed.
        </div>
      ) : (
        <div className="alert alert-error">
          Unexpected false negatives — Bloom filter guarantee violated (bug).
        </div>
      )}

      <h3>Memory Savings</h3>
      <div className="metrics-grid">
        <div className="metric">
          <div className="metric-label">Bloom filter</div>
          <div className="metric-value">{results.memory.bloom_formatted}</div>
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

      <h3>Filter Parameters</h3>
      <div className="table-wrapper" style={{ maxHeight: 'none', marginBottom: '1.5rem' }}>
        <table>
          <thead>
            <tr>
              <th>Parameter</th>
              <th>Value</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(bf.stats).map(([key, val]) => (
              <tr key={key}>
                <td>{key}</td>
                <td>{val}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <h3>Detection Results</h3>
      <div className="form-group" style={{ maxWidth: '300px' }}>
        <select value={filter} onChange={(e) => setFilter(e.target.value)}>
          <option value="All">All</option>
          <option value="True Duplicate">True Duplicate</option>
          <option value="First Seen">First Seen</option>
          <option value="False Positive">False Positive</option>
          <option value="False Negative">False Negative</option>
        </select>
      </div>
      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>URL</th>
              <th>Bloom filter result</th>
              <th>Ground truth</th>
              <th>Verdict</th>
            </tr>
          </thead>
          <tbody>
            {filteredResults.slice(0, 200).map((r, i) => (
              <tr key={i}>
                <td style={{ maxWidth: '380px', wordBreak: 'break-all' }}>{r.url}</td>
                <td>{r.bloom_filter_result}</td>
                <td>{r.actual}</td>
                <td>
                  <span
                    className={`status-badge ${
                      r.status === 'True Duplicate'
                        ? 'badge-tp'
                        : r.status === 'First Seen'
                        ? 'badge-tn'
                        : r.status === 'False Positive'
                        ? 'badge-fp'
                        : 'badge-fn'
                    }`}
                  >
                    {r.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="card-caption">
        Showing {Math.min(filteredResults.length, 200)} of {filteredResults.length} matching rows.
      </div>
    </div>
  )
}
