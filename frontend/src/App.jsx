import React, { useState } from 'react'
import DataInput from './components/DataInput'
import BloomConfig from './components/BloomConfig'
import OverviewTab from './components/OverviewTab'
import ResultsTab from './components/ResultsTab'
import ChartsTab from './components/ChartsTab'
import ModeTab from './components/ModeTab'
import ConclusionTab from './components/ConclusionTab'

const TABS = [
  { id: 'overview', label: 'Overview' },
  { id: 'detection', label: 'Detection' },
  { id: 'mode', label: 'Mode' },
  { id: 'charts', label: 'Charts' },
  { id: 'conclusion', label: 'Conclusion' },
]

export default function App() {
  const [activeTab, setActiveTab] = useState('overview')
  const [data, setData] = useState(null)          // { urls, dataPath, summary, sampleData }
  const [results, setResults] = useState(null)    // Full analysis results
  const [fpRate, setFpRate] = useState(0.01)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleDataLoaded = (payload) => {
    setData({
      dataPath: payload.data_path,
      sampleData: payload.sample_data || [],
      summary: payload.summary,
    })
    setResults(null)
    setActiveTab('overview')
  }

  const handleAnalyzed = (result) => {
    setResults(result)
    setActiveTab('detection')
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="app-kicker">Big Data Analytics</div>
        <h1 className="app-title">URL Duplicate Analyzer</h1>
        <p className="app-subtitle">
          Bloom filter duplicate detection with mode analysis for browser history
        </p>
      </header>

      {data && (
        <div className="status-banner">
          Loaded <strong>{data.summary.total_entries.toLocaleString()}</strong> URL
          visits with <strong>{data.summary.unique_urls_in_data.toLocaleString()}</strong>{' '}
          unique URLs and{' '}
          <strong>{(data.summary.total_entries - data.summary.unique_urls_in_data).toLocaleString()}</strong>{' '}
          duplicate entries.
        </div>
      )}

      <div className="card">
        <div className="tabs" role="tablist">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              className={`tab ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
              role="tab"
            >
              {tab.label}
            </button>
          ))}
        </div>

        <DataInput onDataLoaded={handleDataLoaded} setLoading={setLoading} setError={setError} />
        <BloomConfig
          data={data}
          fpRate={fpRate}
          setFpRate={setFpRate}
          onAnalyze={handleAnalyzed}
          setLoading={setLoading}
          setError={setError}
        />

        <hr className="divider" />

        {error && <div className="alert alert-error">{error}</div>}

        {loading ? (
          <div className="spinner-container">
            <div className="spinner" />
            <span>Processing...</span>
          </div>
        ) : (
          <>
            {activeTab === 'overview' && <OverviewTab data={data} results={results} />}
            {activeTab === 'detection' && <ResultsTab data={data} results={results} fpRate={fpRate} />}
            {activeTab === 'mode' && <ModeTab data={data} results={results} />}
            {activeTab === 'charts' && <ChartsTab data={data} results={results} />}
            {activeTab === 'conclusion' && <ConclusionTab data={data} results={results} />}
          </>
        )}
      </div>

      <footer className="footer">
        Duplicate URL detection with Bloom filters &amp; mode analysis — Big Data Analytics
      </footer>
    </div>
  )
}
