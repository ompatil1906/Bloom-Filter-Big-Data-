# 🔍 Detect Duplicate Web URLs Using Bloom Filters

> **Big Data Analytics — Mode Calculation**
> Detect duplicate URLs in browser history using a Bloom Filter, and find the most visited URL (mode).

---

## 📋 Table of Contents

- [Problem Statement](#-problem-statement)
- [What is a Bloom Filter?](#-what-is-a-bloom-filter)
- [What is Mode Calculation?](#-what-is-mode-calculation)
- [Project Architecture](#-project-architecture)
- [Installation & Setup](#-installation--setup)
- [How to Run](#-how-to-run)
- [Application Features](#-application-features)
- [API Endpoints](#-api-endpoints)
- [Technologies Used](#-technologies-used)
- [Key Observations & Results](#-key-observations--results)

---

## 🎯 Problem Statement

**Detect duplicate web URLs in a browser history using Bloom Filters.**

Modern browsers accumulate thousands of history entries. Many are repeat visits to the same pages. Detecting these duplicates efficiently — without storing every full URL string — is a classic **Big Data** problem. A **Bloom Filter** solves this with minimal memory at the cost of a tiny, controllable false-positive rate.

---

## 🔍 What is a Bloom Filter?

A **Bloom Filter** is a space-efficient probabilistic data structure used to test whether an element is a member of a set.

### Key Properties

- **FALSE NEGATIVES are IMPOSSIBLE**: If the filter says "not present", the element is *guaranteed* to not be in the set.
- **FALSE POSITIVES are POSSIBLE**: If the filter says "present", there is a small probability it could be wrong.

### How It Works

1. Maintain a bit array of size **m**, initialized to all 0s.
2. Use **k** independent hash functions.
3. **ADD** an item: hash it with all k functions, set bits at those indices to 1.
4. **CHECK** an item: hash it with all k functions, check if ALL bits are 1.
   - If any bit is 0 → **definitely not** in the set.
   - If all bits are 1 → **probably** in the set (could be a false positive).

### Optimal Parameters

```
Bit array size:  m = -(n * ln(p)) / (ln2)²
Hash functions:  k = (m / n) * ln2
```

Where `n` = expected number of items and `p` = desired false-positive rate.

---

## 📊 What is Mode Calculation?

The **MODE** is the value that appears most frequently in a dataset. For browser history, the mode is the URL visited most often. If multiple URLs share the highest frequency, the data is **multimodal**.

---

## 🏗️ Project Architecture

This project uses a modern **React + FastAPI** stack:

```
Bloom-Filter-Big-Data-/
├── backend/                        # FastAPI + Python backend
│   ├── main.py                     # FastAPI app with REST API endpoints
│   ├── bloom_filter.py             # Core Bloom Filter implementation
│   ├── data_generator.py           # Synthetic browser history generator
│   ├── mode_calculator.py          # Frequency & mode analysis
│   ├── utils.py                    # Helper utilities
│   ├── requirements.txt            # Backend dependencies
│   └── data/                       # Generated CSV data
│
└── frontend/                       # React frontend (white background theme)
    ├── src/
    │   ├── App.jsx                 # Main app with tabbed navigation
    │   ├── components/
    │   │   ├── DataInput.jsx       # Generate/upload browser history data
    │   │   ├── BloomConfig.jsx     # Bloom filter configuration + analyze
    │   │   ├── OverviewTab.jsx     # Project overview & loaded data
    │   │   ├── ResultsTab.jsx      # Metrics, confusion matrix, results table
    │   │   ├── ModeTab.jsx         # Mode analysis & top URLs chart
    │   │   ├── ChartsTab.jsx       # Visualizations (Chart.js)
    │   │   └── ConclusionTab.jsx   # Conclusion & export metrics
    │   ├── services/
    │   │   └── api.js              # API client
    │   ├── utils/
    │   │   └── formatters.js       # Formatting helpers
    │   └── styles/
    │       └── App.css             # White background theme
    ├── package.json
    └── vite.config.js
```

### How it works end-to-end

1. **React frontend** lets you generate synthetic browser history or upload a CSV.
2. Data is sent to the **FastAPI backend** via REST.
3. The backend streams URLs through the **Bloom filter**, comparing against an exact Python `set` as ground truth.
4. Metrics (accuracy, precision, recall, F1, memory savings) are computed and returned as JSON.
5. The frontend renders metrics, tables, and **Chart.js** visualizations.
6. Results can be **exported as JSON/CSV** for your report.

---

## 🛠️ Installation & Setup

### Prerequisites

- **Python 3.9+**
- **Node.js 16+** and **npm**

### 1. Backend Setup

```bash
# Navigate to the project root
cd "Bloom-Filter-Big-Data-"

# Create a virtual environment (or reuse the existing venv/)
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate

# Install backend dependencies
pip install -r backend/requirements.txt
```

If you reuse the existing `venv/`, just install the FastAPI-specific packages:

```bash
source venv/bin/activate
pip install fastapi uvicorn python-multipart
```

### 2. Frontend Setup

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install
```

---

## ▶️ How to Run

You need **two terminals**.

### Terminal 1 — Start the Backend

```bash
source venv/bin/activate
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`. Interactive API docs at
`http://localhost:8000/docs` (Swagger UI).

### Terminal 2 — Start the Frontend

```bash
cd frontend
npm run dev
```

Open your browser at **`http://localhost:3000`**. The Vite dev server proxies `/api`
requests to the backend on port 8000 automatically.

### Production Build (optional)

```bash
cd frontend
npm run build
npm run preview
```

---

## ✨ Application Features

### Data Input (Step 1)
- **Generate synthetic data** — tune total entries, unique URL pool size, and duplicate pressure (power-law popularity distribution).
- **Upload CSV** — load your own browser history with a `url`/`link` column.

### Bloom Filter Configuration (Steps 2–3)
- Select the **target false-positive rate** (0.1% to 10%).
- Lower rates cost more memory; 1% is a balanced default.
- Click **Run analysis** to process URLs and compute accuracy.

### Tabs

| Tab | What you see |
|-----|--------------|
| **Overview** | Project description, loaded data stats, sample rows |
| **Detection** | Confusion matrix counts (TP/TN/FP/FN), evaluation metrics (accuracy, precision, recall, F1, FPR, FNR), memory savings, filter parameters, filterable results table |
| **Mode** | Most visited URL, duplicate summary, top-10 URLs chart + table, multimodal detection |
| **Charts** | Bit array snapshot, prediction pie, confusion matrix, memory comparison bar, fill-ratio line, FPR curve, frequency distribution |
| **Conclusion** | Key insights & conclusion, **export metrics** as JSON/CSV for your report |

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/generate-data` | Generate synthetic browser history CSV |
| `POST` | `/api/upload-csv` | Upload a CSV file (multipart) |
| `POST` | `/api/analyze` | Run Bloom filter analysis on the loaded data |
| `GET` | `/api/download-metrics/{path}` | Fetch metrics directly |

---

## 🧰 Technologies Used

### Backend
- **FastAPI** — high-performance REST API framework
- **Uvicorn** — ASGI server
- **Pandas / NumPy** — data manipulation and analysis
- **mmh3** — MurmurHash3 for the Bloom filter's hash functions
- **bitarray** — memory-efficient bit array storage
- **python-multipart** — file upload handling

### Frontend
- **React 18** — UI framework
- **Vite** — fast build tool and dev server
- **Chart.js + react-chartjs-2** — interactive charts
- **Pure CSS** — clean white-background responsive theme

---

## 📈 Key Observations & Results

Running on a synthetic dataset of **10,000 visits** (500 unique URLs, ~60% duplicates) at a **1% target false-positive rate**:

- **~99% memory saved** vs a Python HashSet (Bloom filter stores bits, not full URL strings).
- **100% recall** — zero false negatives, confirming the Bloom filter guarantee.
- **Near 100% accuracy** — only a handful of false positives (~target FPR).
- **Mode**: the most-visited URL dominates, reflecting power-law browsing behavior.

The trade-off is clear: a small, tunable false-positive rate buys massive memory savings at Big Data scale.

---

## 📚 References

- Bloom, B. H. (1970). *Space/time trade-offs in hash coding with allowable errors.* Communications of the ACM, 13(7), 422–426.
- Wikipedia. *Bloom filter.*
