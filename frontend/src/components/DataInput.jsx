import React, { useRef, useState } from 'react'
import { generateData, uploadCSV } from '../services/api'

export default function DataInput({ onDataLoaded, setLoading, setError }) {
  const [mode, setMode] = useState('generate')
  const [numEntries, setNumEntries] = useState(10000)
  const [numUnique, setNumUnique] = useState(500)
  const [dupRatio, setDupRatio] = useState(0.6)
  const [fileName, setFileName] = useState('')
  const [localLoading, setLocalLoading] = useState(false)
  const fileInputRef = useRef(null)

  const handleGenerate = async () => {
    setError(null)
    setLocalLoading(true)
    setLoading(true)
    try {
      const result = await generateData({
        num_entries: numEntries,
        num_unique_urls: numUnique,
        duplicate_ratio: dupRatio,
      })
      onDataLoaded(result)
    } catch (e) {
      setError(e.message)
    } finally {
      setLocalLoading(false)
      setLoading(false)
    }
  }

  const handleFileChange = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    setError(null)
    setLocalLoading(true)
    setLoading(true)
    setFileName(file.name)
    try {
      const result = await uploadCSV(file)
      onDataLoaded(result)
    } catch (err) {
      setError(err.message)
    } finally {
      setLocalLoading(false)
      setLoading(false)
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  return (
    <div style={{ marginBottom: '1.5rem' }}>
      <h3 style={{ fontSize: '1rem', marginBottom: '0.75rem' }}>
        Step 1 — Data source
      </h3>
      <div className="radio-group" style={{ marginBottom: '1rem' }}>
        <label className={`radio-option ${mode === 'generate' ? 'selected' : ''}`}>
          <input
            type="radio"
            name="source"
            checked={mode === 'generate'}
            onChange={() => setMode('generate')}
          />
          Generate synthetic data
        </label>
        <label className={`radio-option ${mode === 'upload' ? 'selected' : ''}`}>
          <input
            type="radio"
            name="source"
            checked={mode === 'upload'}
            onChange={() => setMode('upload')}
          />
          Upload CSV file
        </label>
      </div>

      {mode === 'generate' ? (
        <div>
          <p style={{ color: 'var(--muted)', fontSize: '0.85rem', marginBottom: '1rem' }}>
            Create a realistic browsing history with power-law popularity.
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1rem' }}>
            <div className="form-group">
              <label>Total entries</label>
              <input
                type="number"
                min="1000"
                max="50000"
                step="1000"
                value={numEntries}
                onChange={(e) => setNumEntries(Number(e.target.value))}
              />
              <div className="form-hint">Total browser history rows to generate</div>
            </div>
            <div className="form-group">
              <label>Unique URL pool</label>
              <input
                type="number"
                min="50"
                max="2000"
                step="50"
                value={numUnique}
                onChange={(e) => setNumUnique(Number(e.target.value))}
              />
              <div className="form-hint">Number of distinct URLs used by the generator</div>
            </div>
            <div className="form-group">
              <label>Duplicate pressure: {(dupRatio * 100).toFixed(0)}%</label>
              <input
                type="range"
                min="0.1"
                max="0.9"
                step="0.05"
                value={dupRatio}
                onChange={(e) => setDupRatio(Number(e.target.value))}
              />
              <div className="form-hint">Higher values create more repeated visits</div>
            </div>
          </div>
          <button
            className="btn btn-primary"
            onClick={handleGenerate}
            disabled={localLoading}
          >
            {localLoading ? <><span className="loading" /> Generating...</> : 'Generate data'}
          </button>
        </div>
      ) : (
        <div>
          <p style={{ color: 'var(--muted)', fontSize: '0.85rem', marginBottom: '1rem' }}>
            CSV must include a column named <code>url</code> or <code>link</code>.
          </p>
          <input
            type="file"
            accept=".csv"
            ref={fileInputRef}
            onChange={handleFileChange}
            style={{ width: '100%', padding: '0.5rem', border: '1px solid var(--line)', borderRadius: '6px' }}
          />
          {fileName && (
            <div className="alert alert-success" style={{ marginTop: '0.75rem' }}>
              File selected: <strong>{fileName}</strong>
            </div>
          )}
          {localLoading && (
            <div className="alert alert-info" style={{ marginTop: '0.75rem' }}>
              <span className="loading" style={{ borderColor: 'var(--accent)', borderTopColor: 'transparent' }} /> Uploading and processing...
            </div>
          )}
        </div>
      )}
    </div>
  )
}
