const API_BASE = '/api'

async function handleResponse(res) {
  if (!res.ok) {
    const error = await res.json().catch(() => ({}))
    throw new Error(error.detail || `Request failed with status ${res.status}`)
  }
  return res.json()
}

export async function healthCheck() {
  const res = await fetch(`${API_BASE}/health`)
  return handleResponse(res)
}

export async function generateData(params) {
  const res = await fetch(`${API_BASE}/generate-data`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  })
  return handleResponse(res)
}

export async function uploadCSV(file) {
  const formData = new FormData()
  formData.append('file', file)
  const res = await fetch(`${API_BASE}/upload-csv`, {
    method: 'POST',
    body: formData,
  })
  return handleResponse(res)
}

export async function analyze(dataPath, fpRate, capacityPct) {
  const res = await fetch(`${API_BASE}/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ data_path: dataPath, fp_rate: fpRate, capacity_pct: capacityPct }),
  })
  return handleResponse(res)
}
