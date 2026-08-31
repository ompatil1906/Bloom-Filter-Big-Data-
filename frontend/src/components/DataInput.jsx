import React, { useRef, useState } from 'react'
import { generateData, uploadCSV } from '../services/api'

export default function DataInput({ data, onDataLoaded, setLoading, setError }) {
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
    <div>
      <div className="mini-tabs wide">
        <button
          className={`mini-tab ${mode === 'generate' ? 'active' : ''}`}
          onClick={() => setMode('generate')}
        >
          Generate synthetic data
        </button>
        <button
          className={`mini-tab ${mode === 'upload' ? 'active' : ''}`}
          onClick={() => setMode('upload')}
        >
          Upload CSV
        </button>
      </div>

      {mode === 'generate' ? (
        <div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem', marginBottom: '1rem' }}>
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
              <div className="form-hint">Total browser history rows</div>
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
              <div className="form-hint">Distinct URLs used by the generator</div>
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
              <div className="form-hint">Higher = more repeated visits</div>
            </div>
          </div>
          <div style={{ maxWidth: '240px' }}>
            <button className="btn btn-primary" onClick={handleGenerate} disabled={localLoading}>
              {localLoading ? <><span className="loading" /> Generating...</> : 'Generate data'}
            </button>
          </div>
        </div>
      ) : (
        <div>
          <div className="form-group" style={{ maxWidth: '400px' }}>
            <label>Browser history CSV file</label>
            <input type="file" accept=".csv" ref={fileInputRef} onChange={handleFileChange} />
            <div className="form-hint">Column must be named url or link</div>
          </div>
          {fileName && <div className="alert alert-success file-alert">{fileName}</div>}
          {localLoading && (
            <div className="alert alert-info">
              <span className="loading" style={{ borderColor: 'var(--accent)', borderTopColor: 'transparent' }} />
              Uploading...
            </div>
          )}
        </div>
      )}
    </div>
  )
}
