import React from 'react'
import DataInput from './DataInput'
import BloomConfig from './BloomConfig'

export default function DataAnalysisView({
  data,
  results,
  fpRate,
  setFpRate,
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

      <div className="panel">
        <div className="panel-heading">2 · Run Bloom analysis</div>
        <BloomConfig
          data={data}
          fpRate={fpRate}
          setFpRate={setFpRate}
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
