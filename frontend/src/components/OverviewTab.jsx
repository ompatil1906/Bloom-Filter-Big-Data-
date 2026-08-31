import React from 'react'
import { formatBytes } from '../utils/formatters'

export default function OverviewTab({ data, results }) {
  if (!data) {
    return (
      <div className="panel">
        <p>
          <strong>What this project does:</strong> it reads browser-history URLs, detects
          repeat visits with a Bloom filter, and calculates the mode: the URL visited most often.
        </p>
        <p style={{ marginTop: '0.75rem' }}>
          <strong>Why Bloom filters matter:</strong> they use far less memory than storing every
          full URL, but they are probabilistic. A duplicate result can occasionally be a false
          positive. A first-seen result should not be a false negative.
        </p>
      </div>
    )
  }

  const total = data.summary.total_entries
  const unique = data.summary.unique_urls_in_data
  const duplicates = total - unique
  const duplicatePct = total > 0 ? (duplicates / total) * 100 : 0

  return (
    <div>
      <h3>Loaded Data</h3>
      <div className="metrics-grid">
        <div className="metric">
          <div className="metric-label">Total entries</div>
          <div className="metric-value">{total.toLocaleString()}</div>
        </div>
        <div className="metric">
          <div className="metric-label">Unique URLs</div>
          <div className="metric-value">{unique.toLocaleString()}</div>
        </div>
        <div className="metric">
          <div className="metric-label">Duplicate entries</div>
          <div className="metric-value">{duplicates.toLocaleString()}</div>
        </div>
        <div className="metric">
          <div className="metric-label">Duplicate rate</div>
          <div className="metric-value">{duplicatePct.toFixed(1)}%</div>
        </div>
      </div>

      {results && (
        <>
          <h3>Bloom Filter Summary</h3>
          <div className="metrics-grid">
            <div className="metric">
              <div className="metric-label">Bit array size</div>
              <div className="metric-value">{results.bloom_filter.size.toLocaleString()}</div>
            </div>
            <div className="metric">
              <div className="metric-label">Hash functions</div>
              <div className="metric-value">{results.bloom_filter.hash_count}</div>
            </div>
            <div className="metric">
              <div className="metric-label">Bloom memory</div>
              <div className="metric-value">{results.bloom_filter.memory_formatted}</div>
            </div>
            <div className="metric">
              <div className="metric-label">HashSet memory</div>
              <div className="metric-value">{results.memory.hashset_formatted}</div>
            </div>
          </div>
        </>
      )}

      <h3>Sample Rows</h3>
      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              {data.sampleData.length > 0 &&
                Object.keys(data.sampleData[0]).map((key) => <th key={key}>{key}</th>)}
            </tr>
          </thead>
          <tbody>
            {data.sampleData.map((row, i) => (
              <tr key={i}>
                {Object.values(row).map((val, j) => (
                  <td key={j} style={{ maxWidth: '300px', wordBreak: 'break-all' }}>{String(val)}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
