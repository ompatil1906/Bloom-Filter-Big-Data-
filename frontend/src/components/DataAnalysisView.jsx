import React from 'react'
import DataInput from './DataInput'
import BloomConfig from './BloomConfig'

export default function DataAnalysisView({
  data,
  results,
  fpRate,
  setFpRate,
  capacityPct,
  setCapacityPct,
  onDataLoaded,
  onAnalyze,
  setLoading,
  setError,
  onNavigate,
}) {
  return (
    <div>
      <h3>Data &amp; Analysis</h3>
      <p className="view-intro" style={{ color: 'var(--muted)', marginBottom: '1.25rem' }}>
        Load your browser history, then configure and run the Bloom filter analysis in one place.
      </p>

      <div className="panel" style={{ marginBottom: '1.25rem' }}>
        <div className="panel-heading">1 · Load data</div>
        <DataInput
          data={data}
          onDataLoaded={onDataLoaded}
          setLoading={setLoading}
          setError={setError}
        />
      </div>

      {data && (
        <div className="config-strip">
          <div className="config-strip-title">Dataset config</div>
          <div className="config-strip-items">
            <span>Total entries: <strong>{data.summary.total_entries.toLocaleString()}</strong></span>
            <span>Unique URLs: <strong>{data.summary.unique_urls_in_data.toLocaleString()}</strong></span>
            <span>Duplicates: <strong>{data.summary.duplicate_entries.toLocaleString()}</strong></span>
            <span>Duplicate rate: <strong>{(data.summary.actual_duplicate_ratio * 100).toFixed(1)}%</strong></span>
          </div>
        </div>
      )}

      <div className="panel">
        <div className="panel-heading">2 · Run Bloom analysis</div>
        <BloomConfig
          data={data}
          fpRate={fpRate}
          setFpRate={setFpRate}
          capacityPct={capacityPct}
          setCapacityPct={setCapacityPct}
          onAnalyze={onAnalyze}
          setLoading={setLoading}
          setError={setError}
        />

        {data && results && (
          <div className="analysis-summary">
            <div className="panel-heading" style={{ marginTop: '1rem' }}>Analysis complete</div>
            <div className="metrics-grid">
              <div className="metric">
                <div className="metric-label">Accuracy</div>
                <div className="metric-value">{results.accuracy_stats.accuracy.toFixed(2)}%</div>
              </div>
              <div className="metric">
                <div className="metric-label">Precision</div>
                <div className="metric-value">{results.accuracy_stats.precision.toFixed(2)}%</div>
              </div>
              <div className="metric">
                <div className="metric-label">False positives</div>
                <div className="metric-value">{results.accuracy_stats.false_positives.toLocaleString()}</div>
              </div>
              <div className="metric">
                <div className="metric-label">Memory saved</div>
                <div className="metric-value">{results.memory.savings_percentage.toFixed(1)}%</div>
              </div>
            </div>
            <button className="btn btn-primary" style={{ width: 'auto' }} onClick={() => onNavigate('detection')}>
              View full detection results →
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
