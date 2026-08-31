import React from 'react'
import { analyze } from '../services/api'

const FP_OPTIONS = [0.1, 0.05, 0.01, 0.005, 0.001, 0.0001]

export default function BloomConfig({
  data,
  fpRate,
  setFpRate,
  capacityPct,
  setCapacityPct,
  onAnalyze,
  setLoading,
  setError,
}) {
  const [localLoading, setLocalLoading] = React.useState(false)

  const handleAnalyze = async () => {
    if (!data?.dataPath) return
    setError(null)
    setLocalLoading(true)
    setLoading(true)
    try {
      const result = await analyze(data.dataPath, fpRate, capacityPct)
      onAnalyze(result)
    } catch (e) {
      setError(e.message)
    } finally {
      setLocalLoading(false)
      setLoading(false)
    }
  }

  const actualUnique = data?.summary.unique_urls_in_data ?? 0
  const expectedItems = Math.max(1, Math.round((actualUnique * capacityPct) / 100))
  const m = Math.round(-(expectedItems * Math.log(fpRate)) / Math.LN2 ** 2)
  const k = Math.round((m / expectedItems) * Math.LN2)

  return (
    <div className="bloom-config">
      <div className="config-grid">
        <div className="form-group">
          <label>Target false-positive rate</label>
          <select value={fpRate} onChange={(e) => setFpRate(Number(e.target.value))}>
            {FP_OPTIONS.map((opt) => (
              <option key={opt} value={opt}>
                {(opt * 100).toFixed(2)}%
              </option>
            ))}
          </select>
          <div className="form-hint">Lower rate = more memory</div>
        </div>

        <div className="form-group">
          <label>Filter capacity: {capacityPct}% of unique URLs</label>
          <input
            type="range"
            min="40"
            max="200"
            step="10"
            value={capacityPct}
            onChange={(e) => setCapacityPct(Number(e.target.value))}
          />
          <div className="form-hint">
            {capacityPct < 100
              ? 'Under-sized — expect visible false positives'
              : capacityPct === 100
              ? 'Optimal sizing — near-zero false positives'
              : 'Over-sized — more memory, fewer false positives'}
          </div>
        </div>
      </div>

      <div className="config-preview">
        <span title="Sized for this many items">Filter sized for <strong>{expectedItems.toLocaleString()}</strong> items</span>
        <span title="Approx. memory footprint">~{Math.round(m / 8 / 1024).toLocaleString()} KB</span>
        <span title="Number of hash functions">{k} hash functions</span>
      </div>

      <div style={{ maxWidth: '240px' }}>
        <button className="btn btn-primary" onClick={handleAnalyze} disabled={!data || localLoading}>
          {localLoading ? <><span className="loading" /> Analyzing...</> : 'Run analysis'}
        </button>
      </div>
      {!data && <div className="form-hint" style={{ marginTop: '0.5rem' }}>Load data above first.</div>}
    </div>
  )
}
