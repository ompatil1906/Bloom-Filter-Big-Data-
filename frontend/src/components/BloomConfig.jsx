import React from 'react'
import { analyze } from '../services/api'
import { formatBytes } from '../utils/formatters'

const FP_OPTIONS = [0.1, 0.05, 0.01, 0.005, 0.001, 0.0001]

export default function BloomConfig({ data, fpRate, setFpRate, onAnalyze, setLoading, setError }) {
  const [localLoading, setLocalLoading] = React.useState(false)

  const handleAnalyze = async () => {
    if (!data?.dataPath) return
    setError(null)
    setLocalLoading(true)
    setLoading(true)
    try {
      const result = await analyze(data.dataPath, fpRate)
      onAnalyze(result)
    } catch (e) {
      setError(e.message)
    } finally {
      setLocalLoading(false)
      setLoading(false)
    }
  }

  const uniqueCount = data ? new Set(data.sampleData.map((r) => r.url)).size : 0

  return (
    <div style={{ marginBottom: '1.5rem' }}>
      <h3 style={{ fontSize: '1rem', marginBottom: '0.75rem' }}>
        Step 2 &amp; 3 — Bloom filter &amp; analyze
      </h3>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem', alignItems: 'end' }}>
        <div className="form-group">
          <label>Target false-positive rate</label>
          <select value={fpRate} onChange={(e) => setFpRate(Number(e.target.value))}>
            {FP_OPTIONS.map((opt) => (
              <option key={opt} value={opt}>
                {(opt * 100).toFixed(2)}%
              </option>
            ))}
          </select>
          <div className="form-hint">
            Lower false-positive rate uses more memory. Default 1% is balanced.
          </div>
          {data && data.summary && (
            <div className="form-hint" style={{ marginTop: '0.5rem' }}>
              Dataset: {data.summary.total_entries.toLocaleString()} visits
            </div>
          )}
        </div>
        <div>
          <button
            className="btn btn-primary"
            onClick={handleAnalyze}
            disabled={!data || localLoading}
          >
            {localLoading ? <><span className="loading" /> Analyzing...</> : 'Run analysis'}
          </button>
          {!data && (
            <div className="form-hint" style={{ marginTop: '0.5rem' }}>
              Load a dataset to enable analysis.
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
