import React, { useState } from 'react'
import DataAnalysisView from './components/DataAnalysisView'
import DashboardView from './components/DashboardView'
import ResultsView from './components/ResultsView'
import ChartsView from './components/ChartsView'
import ModeView from './components/ModeView'
import ConclusionView from './components/ConclusionView'

const NAV_ITEMS = [
  { id: 'dashboard', label: 'Dashboard', icon: '🏠' },
  { id: 'data', label: 'Data & Analysis', icon: '⚙️' },
  { id: 'detection', label: 'Detection', icon: '🎯' },
  { id: 'mode', label: 'Mode', icon: '📊' },
  { id: 'charts', label: 'Charts', icon: '📈' },
  { id: 'conclusion', label: 'Conclusion', icon: '✅' },
]

export default function App() {
  const [activeNav, setActiveNav] = useState('dashboard')
  const [data, setData] = useState(null)
  const [results, setResults] = useState(null)
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
    setActiveNav('data')
  }

  const handleAnalyzed = (result) => {
    setResults(result)
    setActiveNav('detection')
  }

  const handleClear = () => {
    setData(null)
    setResults(null)
    setError(null)
    setActiveNav('dashboard')
  }

  const duplicateCount = data
    ? data.summary.total_entries - data.summary.unique_urls_in_data
    : 0

  const renderView = () => {
    switch (activeNav) {
      case 'dashboard':
        return <DashboardView data={data} onNavigate={setActiveNav} />
      case 'data':
        return (
          <DataAnalysisView
            data={data}
            results={results}
            fpRate={fpRate}
            setFpRate={setFpRate}
            onDataLoaded={handleDataLoaded}
            onAnalyze={handleAnalyzed}
            setLoading={setLoading}
            setError={setError}
            onNavigate={setActiveNav}
          />
        )
      case 'detection':
        return <ResultsView data={data} results={results} />
      case 'mode':
        return <ModeView data={data} results={results} />
      case 'charts':
        return <ChartsView data={data} results={results} />
      case 'conclusion':
        return <ConclusionView data={data} results={results} />
      default:
        return <DashboardView data={data} onNavigate={setActiveNav} />
    }
  }

  return (
    <div className="app">
      <nav className="navbar">
        <div className="navbar-brand">
          <div className="navbar-logo">🔍</div>
          <div>
            <div className="navbar-title">URL Duplicate Analyzer</div>
            <div className="navbar-sub">Bloom Filter · Big Data</div>
          </div>
        </div>
        <div className="navbar-status">
          <span className={`pill ${data ? 'pill-green' : 'pill-gray'}`}>
            {data ? `${data.summary.total_entries.toLocaleString()} visits loaded` : 'No dataset'}
          </span>
        </div>
      </nav>

      <div className="layout">
        <aside className="sidebar">
          <div className="sidebar-heading">Navigation</div>
          <nav className="sidebar-nav">
            {NAV_ITEMS.map((item) => (
              <button
                key={item.id}
                className={`nav-item ${activeNav === item.id ? 'active' : ''}`}
                onClick={() => setActiveNav(item.id)}
              >
                <span className="nav-item-icon">{item.icon}</span>
                <span className="nav-item-label">{item.label}</span>
                {item.id === 'detection' && results && <span className="nav-item-check">✓</span>}
              </button>
            ))}
          </nav>

          {data && results && (
            <>
              <div className="sidebar-divider" />
              <div className="sidebar-stats">
                <div className="stat-row">
                  <span>Accuracy</span>
                  <strong>{results.accuracy_stats.accuracy.toFixed(2)}%</strong>
                </div>
                <div className="stat-row">
                  <span>Memory saved</span>
                  <strong>{results.memory.savings_percentage.toFixed(1)}%</strong>
                </div>
              </div>
            </>
          )}

          {data && (
            <>
              <div className="sidebar-divider" />
              <button className="btn btn-secondary" onClick={handleClear}>
                Clear dataset
              </button>
            </>
          )}
        </aside>

        <main className="content">
          {error && <div className="alert alert-error">{error}</div>}

          {loading ? (
            <div className="spinner-container">
              <div className="spinner" />
              <span>Processing...</span>
            </div>
          ) : (
            renderView()
          )}
        </main>
      </div>

      <footer className="footer">
        Duplicate URL detection with Bloom filters &amp; mode analysis — Big Data Analytics
      </footer>
    </div>
  )
}
