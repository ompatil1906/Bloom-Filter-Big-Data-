 # 🔍 Detect Duplicate Web URLs Using Bloom Filters

> **Big Data Analytics — Mode Calculation**
> Detect duplicate URLs in browser history using a Bloom Filter, and find the most visited URL (mode).

---

## 📋 Table of Contents

- [Problem Statement](#-problem-statement)
- [What is a Bloom Filter?](#-what-is-a-bloom-filter)
  - [How It Works](#how-it-works)
  - [Key Properties](#key-properties)
  - [Mathematical Formulas](#mathematical-formulas)
  - [Step-by-Step Example](#step-by-step-example)
- [What is Mode Calculation?](#-what-is-mode-calculation)
- [Project Architecture](#-project-architecture)
- [Installation & Setup](#-installation--setup)
- [How to Run](#-how-to-run)
- [Application Features](#-application-features)
- [Code Walkthrough](#-code-walkthrough)
  - [bloom_filter.py](#1-bloom_filterpy--core-bloom-filter)
  - [data_generator.py](#2-data_generatorpy--synthetic-data-generator)
  - [mode_calculator.py](#3-mode_calculatorpy--mode-calculation)
  - [utils.py](#4-utilspy--utility-functions)
  - [app.py](#5-apppy--streamlit-gui)
- [Key Observations & Results](#-key-observations--results)
- [Technologies Used](#-technologies-used)
- [References](#-references)

---

## 📝 Problem Statement

Detect duplicate web URLs in a browser history using Bloom Filters — Mode Calculation.

### Objective

1. **Duplicate Detection**: Use a Bloom Filter to efficiently identify which URLs in a browsing history have been visited before (duplicates).
2. **Mode Calculation**: Find the most frequently visited URL(s) in the browser history — the statistical **mode**.

### Why Bloom Filters?

In Big Data scenarios, storing every URL in a hash set becomes memory-expensive. For example:
- **10 million URLs** in a Python set ≈ **~1 GB** of RAM
- **10 million URLs** in a Bloom Filter ≈ **~12 MB** of RAM (with 1% false positive rate)

That's a **~98.8% memory reduction!**

---

## 🌸 What is a Bloom Filter?

A **Bloom Filter** is a space-efficient **probabilistic data structure** invented by Burton Howard Bloom in 1970. It is used to test whether an element is a member of a set.

### How It Works

A Bloom Filter consists of:
- A **bit array** of `m` bits, all initialized to `0`
- `k` independent **hash functions**, each mapping an element to one of the `m` bit positions

#### Adding an Element

When adding a URL (e.g., `"https://google.com"`):

```
URL: "https://google.com"
    │
    ├──► Hash₁("https://google.com") → index 3
    ├──► Hash₂("https://google.com") → index 7
    └──► Hash₃("https://google.com") → index 12

Bit Array (before): [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                                ↑              ↑              ↑
                             idx=3          idx=7          idx=12

Bit Array (after):  [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0]
```

#### Checking an Element

When checking if a URL exists:

```
URL: "https://google.com"
    │
    ├──► Hash₁ → index 3  → bit[3]  = 1 ✅
    ├──► Hash₂ → index 7  → bit[7]  = 1 ✅
    └──► Hash₃ → index 12 → bit[12] = 1 ✅

Result: ALL bits are 1 → "PROBABLY in the set" ✅
```

```
URL: "https://example.com"  (never added)
    │
    ├──► Hash₁ → index 1  → bit[1]  = 0 ❌
    ├──► Hash₂ → index 5  → bit[5]  = 0 ❌
    └──► Hash₃ → index 9  → bit[9]  = 0 ❌

Result: Some bits are 0 → "DEFINITELY NOT in the set" ❌
```

### Key Properties

| Property | Description |
|----------|-------------|
| **No False Negatives** | If the filter says "not present", the URL is **guaranteed** to not have been seen before. This is **100% reliable**. |
| **Possible False Positives** | If the filter says "present", there is a small probability (`p`) that this is a mistake — the URL was never actually added, but its hash indices happen to overlap with other URLs' indices. |
| **No Deletion** | Standard Bloom Filters don't support removing elements. Once a bit is set to `1`, it stays `1`. |
| **Space Efficient** | Uses only `m` bits regardless of the size of the stored elements. A URL string can be 100+ bytes, but the Bloom Filter only needs ~10 bits per element. |

### Mathematical Formulas

#### 1. Optimal Bit Array Size (`m`)

Given:
- `n` = expected number of unique elements
- `p` = desired false positive probability

```
m = -(n × ln(p)) / (ln 2)²
```

**Example**: For `n = 1000` URLs and `p = 0.01` (1% false positive rate):
```
m = -(1000 × ln(0.01)) / (ln 2)²
m = -(1000 × (-4.605)) / (0.693)²
m = 4605 / 0.480
m ≈ 9,585 bits ≈ 1.17 KB
```

#### 2. Optimal Number of Hash Functions (`k`)

```
k = (m / n) × ln 2
```

**Example**: With `m = 9585` and `n = 1000`:
```
k = (9585 / 1000) × 0.693
k ≈ 6.64 → 7 hash functions
```

#### 3. Actual False Positive Rate

After inserting `n` elements:
```
P ≈ (1 - e^(-k × n / m))^k
```

### Step-by-Step Example

Let's trace through a small example with `m = 10` bits and `k = 2` hash functions:

```
Initial state:  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

Step 1: Add "google.com"
  Hash₁("google.com") % 10 = 2
  Hash₂("google.com") % 10 = 5
  Bit array:    [0, 0, 1, 0, 0, 1, 0, 0, 0, 0]

Step 2: Add "youtube.com"
  Hash₁("youtube.com") % 10 = 1
  Hash₂("youtube.com") % 10 = 8
  Bit array:    [0, 1, 1, 0, 0, 1, 0, 0, 1, 0]

Step 3: Check "google.com"
  Hash₁("google.com") % 10 = 2  → bit[2] = 1 ✅
  Hash₂("google.com") % 10 = 5  → bit[5] = 1 ✅
  Result: PROBABLY IN THE SET → DUPLICATE! ✅

Step 4: Check "facebook.com" (never added)
  Hash₁("facebook.com") % 10 = 5  → bit[5] = 1 ✅
  Hash₂("facebook.com") % 10 = 8  → bit[8] = 1 ✅
  Result: PROBABLY IN THE SET → FALSE POSITIVE! ⚠️
  (Both indices happen to be set by other URLs)

Step 5: Check "reddit.com" (never added)
  Hash₁("reddit.com") % 10 = 3  → bit[3] = 0 ❌
  Result: DEFINITELY NOT IN THE SET ✅
  (At least one bit is 0, so it was never added)
```

---

## 📊 What is Mode Calculation?

In statistics, the **mode** is the value that appears **most frequently** in a dataset.

### In the Context of Browser History:

```
Browser History URLs:
  1. google.com       ← visit
  2. youtube.com      ← visit
  3. google.com       ← visit (duplicate!)
  4. github.com       ← visit
  5. google.com       ← visit (duplicate!)
  6. youtube.com      ← visit (duplicate!)

Frequency Count:
  google.com  → 3 visits
  youtube.com → 2 visits
  github.com  → 1 visit

MODE = google.com (highest frequency = 3)
```

### Key Concepts:

| Term | Definition |
|------|------------|
| **Mode** | The URL with the highest visit count |
| **Multimodal** | When multiple URLs share the same highest frequency |
| **Frequency Distribution** | A table showing how many times each URL was visited |
| **Unimodal** | Only one URL has the highest frequency |

---

## 🏗 Project Architecture

```
BDA/
├── app.py                 # Main Streamlit GUI application
├── bloom_filter.py        # Core Bloom Filter implementation
├── data_generator.py      # Synthetic browser history generator
├── mode_calculator.py     # Frequency analysis & mode calculation
├── utils.py               # Helper utility functions
├── requirements.txt       # Python dependencies
├── README.md              # This file
└── data/
    └── browser_history.csv  # Generated/uploaded dataset
```

### Module Dependency Diagram:

```
                    ┌─────────────┐
                    │   app.py    │  ← Streamlit GUI (entry point)
                    │  (main app) │
                    └──────┬──────┘
                           │
            ┌──────────────┼──────────────┐
            │              │              │
    ┌───────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐
    │ bloom_filter │ │   data_    │ │   mode_    │
    │    .py       │ │ generator  │ │ calculator │
    │              │ │   .py      │ │    .py     │
    └──────────────┘ └────────────┘ └────────────┘
            │                              │
            └──────────┐  ┌────────────────┘
                       │  │
                  ┌────▼──▼────┐
                  │  utils.py  │
                  └────────────┘
```

---

## ⚡ Installation & Setup

### Prerequisites

- **Python 3.8+** installed on your system
- **pip** (Python package manager)

### Step 1: Navigate to the Project Directory

```bash
cd D:\college\project\BDA
```

### Step 2: (Optional) Create a Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
| Package | Purpose |
|---------|---------|
| `streamlit` | Web-based GUI framework |
| `mmh3` | MurmurHash3 — fast, non-cryptographic hash function |
| `bitarray` | Memory-efficient bit array implementation |
| `pandas` | Data manipulation and CSV handling |
| `plotly` | Interactive charts and visualizations |
| `numpy` | Numerical operations for array manipulation |

---

## 🚀 How to Run

### Start the Application

```bash
streamlit run app.py
```

This will open the application in your default web browser at `http://localhost:8501`.

### Quick Test (Without GUI)

You can also test the Bloom Filter directly from the command line:

```bash
python -c "
from bloom_filter import BloomFilter

# Create a Bloom Filter expecting 1000 items with 1% false positive rate
bf = BloomFilter(expected_items=1000, false_positive_rate=0.01)

# Add some URLs
bf.add('https://google.com')
bf.add('https://youtube.com')
bf.add('https://github.com')

# Check URLs
print('google.com in filter?', bf.check('https://google.com'))       # True
print('youtube.com in filter?', bf.check('https://youtube.com'))     # True
print('facebook.com in filter?', bf.check('https://facebook.com'))   # False (probably)

# Print stats
for key, value in bf.get_stats().items():
    print(f'{key}: {value}')
"
```

---

## 🎨 Application Features

### Tab 1: 🏠 Overview
- Explains how Bloom Filters work with mathematical formulas
- Shows current dataset statistics (total entries, unique URLs, duplicates)
- Previews Bloom Filter parameters (bit array size, hash functions, memory usage)
- Displays sample data from the loaded/generated CSV

### Tab 2: 🔍 Duplicate Detection
- Processes every URL through the Bloom Filter
- Classifies each result as:
  - ✅ **True Duplicate** — correctly identified duplicate
  - 🆕 **First Seen** — correctly identified new URL
  - ⚠️ **False Positive** — incorrectly flagged as duplicate (expected with Bloom Filters)
  - ❌ **False Negative** — should NEVER happen (Bloom Filter guarantee)
- Shows accuracy metrics, precision, and a detailed results table
- Compares Bloom Filter results against ground truth (Python set)

### Tab 3: 📊 Mode Analysis
- Calculates and displays the **mode** (most visited URL)
- Detects **multimodal** data (multiple URLs with same top frequency)
- Shows summary statistics (total, unique, duplicate count, percentage)
- Displays Top 10 most visited URLs in a table and horizontal bar chart
- Full frequency distribution chart (Top 20)

### Tab 4: 📈 Visualizations
- **Bit Array Heatmap**: Visual representation of the Bloom Filter's bit array
- **Accuracy Breakdown**: Pie chart + Confusion Matrix of detection results
- **Memory Comparison**: Bar chart comparing Bloom Filter vs HashSet memory usage
- **Fill Ratio Over Time**: Line chart showing how the bit array fills up
- **False Positive Rate Curve**: Theoretical FP rate as more elements are added

---

## 📖 Code Walkthrough

### 1. `bloom_filter.py` — Core Bloom Filter

This is the heart of the project. It implements a Bloom Filter from scratch.

**Key Methods:**

| Method | What It Does |
|--------|-------------|
| `__init__(expected_items, fp_rate)` | Calculates optimal `m` (bit array size) and `k` (hash count), initializes the bit array |
| `add(item)` | Hashes the item `k` times, sets those bit positions to `1` |
| `check(item)` | Hashes the item `k` times, returns `True` if ALL bits at those positions are `1` |
| `current_false_positive_rate()` | Calculates the theoretical FP rate based on current state |
| `fill_ratio()` | Returns the percentage of bits that are set to `1` |
| `get_stats()` | Returns a dictionary with all filter parameters and metrics |

**Hash Function**: We use **MurmurHash3** (`mmh3`) — a fast, non-cryptographic hash function widely used in Big Data applications (Hadoop, Spark, Cassandra all use it). Each hash function uses a different **seed** value (0, 1, 2, ..., k-1) to produce independent hash values.

### 2. `data_generator.py` — Synthetic Data Generator

Generates realistic browser history data with:
- **40+ real-world domains** (Google, YouTube, GitHub, etc.)
- **30 realistic URL paths** (/search, /login, /dashboard, etc.)
- **Power-law distribution**: Top 10% of URLs ("popular sites") get ~60% of the traffic, mimicking real browsing behavior
- Entries span a **30-day time window** with random timestamps
- Output is a **sorted CSV** (chronological order)

### 3. `mode_calculator.py` — Mode Calculation

Uses Python's `collections.Counter` to:
- Count the frequency of each URL
- Find the mode (most common URL)
- Detect multimodal data
- Generate Top-N frequency tables

### 4. `utils.py` — Utility Functions

- **CSV loading** with auto-detection of URL columns (handles 'url', 'link', 'URL', etc.)
- **Memory estimation** for HashSet comparison
- **Size formatting** (bytes → KB → MB → GB)

### 5. `app.py` — Streamlit GUI

The main application that ties everything together. Key implementation details:
- Uses `st.session_state` to persist data across Streamlit re-runs
- Processes URLs sequentially: for each URL, CHECK first, then ADD if new
- Maintains a parallel Python `set` as ground truth for accuracy comparison
- All charts use **Plotly** for interactivity (zoom, hover, pan)

---

## 📊 Key Observations & Results

### Expected Behavior:

1. **False Positive Rate**: With the default setting of 1%, you should see roughly 1% of first-seen URLs incorrectly flagged as duplicates.

2. **False Negatives**: Should ALWAYS be 0. This is the fundamental guarantee of Bloom Filters. If you see any false negatives, there's a bug.

3. **Memory Savings**: The Bloom Filter typically uses **95-99% less memory** than a Python set for the same data.

4. **Fill Ratio**: As more elements are added, the bit array fills up. Once the fill ratio exceeds ~50%, the false positive rate increases rapidly.

5. **Mode**: With the synthetic data generator's power-law distribution, the mode will typically be one of the "popular" URLs (top 10% of the URL pool).

---

## 🛠 Technologies Used

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.8+ | Core programming language |
| Streamlit | ≥1.28.0 | Web-based GUI framework |
| mmh3 | ≥4.0.0 | MurmurHash3 hash function |
| bitarray | ≥2.8.0 | Memory-efficient bit array |
| Pandas | ≥2.0.0 | Data manipulation & CSV handling |
| Plotly | ≥5.18.0 | Interactive visualizations |
| NumPy | ≥1.24.0 | Numerical operations |

---

## 📚 References

1. **Bloom, B. H. (1970)**. "Space/time trade-offs in hash coding with allowable errors". *Communications of the ACM*, 13(7), 422–426.
2. **MurmurHash3**: [https://github.com/aappleby/smhasher](https://github.com/aappleby/smhasher)
3. **Bloom Filter Calculator**: [https://hur.st/bloomfilter/](https://hur.st/bloomfilter/)
4. **Streamlit Documentation**: [https://docs.streamlit.io/](https://docs.streamlit.io/)
5. **Big Data Analytics** — Course material on probabilistic data structures.

---

<p align="center">
  Built with ❤️ for Big Data Analytics<br>
  Bloom Filter + Mode Calculation
</p>
