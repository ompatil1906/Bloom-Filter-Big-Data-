import React from 'react'

export default function DashboardView({ data, onNavigate }) {
  return (
    <div>
      <h3>Welcome</h3>
      <div className="panel">
        <p>
          <strong>What this project does:</strong> it reads browser-history URLs, detects repeat
          visits with a <strong>Bloom filter</strong>, and calculates the <strong>mode</strong>:
          the URL visited most often.
        </p>
        <p style={{ marginTop: '0.75rem' }}>
          <strong>Why Bloom filters matter:</strong> they use far less memory than storing every
          full URL, but they are probabilistic. A duplicate result can occasionally be a false
          positive. A first-seen result should not be a false negative.
        </p>
      </div>

      <h3>Workflow</h3>
      <div className="workflow-grid">
        <div className="wf-card">
          <div className="wf-step">1</div>
          <div className="wf-title">Load browser history</div>
          <div className="wf-desc">Generate realistic synthetic data or upload your own CSV.</div>
        </div>
        <div className="wf-card">
          <div className="wf-step">2</div>
          <div className="wf-title">Configure Bloom filter</div>
          <div className="wf-desc">Pick a target false-positive rate (default 1%).</div>
        </div>
        <div className="wf-card">
          <div className="wf-step">3</div>
          <div className="wf-title">Run analysis</div>
          <div className="wf-desc">Stream URLs through the filter and compare to ground truth.</div>
        </div>
        <div className="wf-card">
          <div className="wf-step">4</div>
          <div className="wf-title">Explore results</div>
          <div className="wf-desc">Review detection metrics, mode, charts, and export the report.</div>
        </div>
      </div>

      <div className="get-started">
        <button className="btn btn-primary" onClick={() => onNavigate('data')}>
          Get started → Go to Data
        </button>
      </div>

      <h3>About Bloom Filters</h3>
      <div className="panel">
        <p>
          A <strong>Bloom filter</strong> is a space-efficient probabilistic data structure that
          tests membership in a set. It uses a bit array and <code>k</code> hash functions. Adding
          an item sets several bits; checking an item verifies if all its bits are set.
        </p>
        <ul className="workflow-steps" style={{ marginTop: '0.5rem' }}>
          <li><strong>No false negatives:</strong> a "not found" answer is always correct.</li>
          <li><strong>Possible false positives:</strong> a "found" answer may be wrong, at a tunable rate.</li>
          <li><strong>Huge memory win:</strong> stores only bits, not full strings.</li>
        </ul>
      </div>
    </div>
  )
}
