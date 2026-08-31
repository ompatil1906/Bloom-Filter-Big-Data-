import React from 'react'
import { analyze } from '../services/api'

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

  return (
    <div className="bloom-config">
      <div className="form-group" style={{ maxWidth: '320px' }}>
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

      <div style={{ maxWidth: '240px' }}>
        <button className="btn btn-primary" onClick={handleAnalyze} disabled={!data || localLoading}>
          {localLoading ? <><span className="loading" /> Analyzing...</> : 'Run analysis'}
        </button>
      </div>
      {!data && <div className="form-hint" style={{ marginTop: '0.5rem' }}>Load data above first.</div>}
    </div>
  )
}
