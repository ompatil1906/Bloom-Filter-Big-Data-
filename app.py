"""
Streamlit application for URL Duplicate Analyzer.

Detect duplicate web URLs in browser history with a Bloom filter and calculate
the most frequently visited URL.
"""

import math
import os

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from bloom_filter import BloomFilter
from data_generator import generate_browser_history
from mode_calculator import calculate_mode, get_frequency_dataframe
from utils import estimate_hashset_memory, format_memory_size, load_uploaded_csv


st.set_page_config(
    page_title="URL Duplicate Analyzer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
    <style>
        :root {
            --bg: #f8fafc;
            --panel: #ffffff;
            --text: #111827;
            --muted: #64748b;
            --line: #e2e8f0;
            --accent: #2563eb;
            --accent-soft: #dbeafe;
            --success: #15803d;
            --warning: #b45309;
            --danger: #b91c1c;
        }

        .stApp {
            background: var(--bg);
            color: var(--text);
        }

        header[data-testid="stHeader"] {
            background: rgba(248, 250, 252, 0.96);
            border-bottom: 1px solid var(--line);
            color: var(--text);
        }

        header[data-testid="stHeader"] *,
        [data-testid="stToolbar"] *,
        [data-testid="stDecoration"] *,
        [data-testid="stStatusWidget"] * {
            color: var(--text);
        }

        #MainMenu,
        footer,
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        [data-testid="stStatusWidget"] {
            visibility: hidden;
            height: 0;
        }

        .stApp,
        .stApp p,
        .stApp li,
        .stApp label,
        .stApp span,
        .stApp small,
        .stApp div[data-testid="stMarkdownContainer"],
        .stApp div[data-testid="stWidgetLabel"],
        .stApp div[data-testid="stCaptionContainer"] {
            color: var(--text);
        }

        [data-testid="stSidebar"] {
            background: var(--panel);
            border-right: 1px solid var(--line);
        }

        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
            gap: 0.9rem;
        }

        .sidebar-brand {
            padding: 0.2rem 0 0.35rem;
        }
        .sidebar-brand-title {
            font-size: 1.32rem;
            font-weight: 800;
            color: var(--text);
            line-height: 1.2;
            letter-spacing: -0.01em;
        }
        .sidebar-brand-subtitle {
            font-size: 0.82rem;
            color: var(--muted);
            margin-top: 0.18rem;
            line-height: 1.35;
        }
        .sidebar-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            background: var(--accent-soft);
            color: var(--accent);
            border: 1px solid #bfdbfe;
            border-radius: 999px;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.02em;
            padding: 0.18rem 0.55rem;
            margin-bottom: 0.35rem;
        }
        .sidebar-status {
            background: #f1f5f9;
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 0.65rem 0.75rem;
            font-size: 0.84rem;
            line-height: 1.4;
        }
        .sidebar-status.loaded {
            background: #f0fdf4;
            border-color: #bbf7d0;
        }
        .sidebar-step {
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            color: var(--muted);
            margin-bottom: 0.15rem;
        }
        .sidebar-hint {
            font-size: 0.8rem;
            color: #64748b;
            line-height: 1.4;
        }

        [data-testid="stSidebar"],
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            color: var(--text);
        }

        h1, h2, h3 {
            color: var(--text);
            letter-spacing: 0;
        }

        h1 {
            font-size: clamp(1.75rem, 2.4vw, 2.25rem);
            line-height: 1.25;
            margin-bottom: 0.45rem;
            overflow-wrap: anywhere;
        }

        h2 {
            font-size: 1.35rem;
        }

        h3 {
            font-size: 1.05rem;
        }

        .block-container {
            padding-top: 2.75rem;
            padding-bottom: 2rem;
            max-width: 1280px;
        }

        .app-kicker {
            color: var(--accent);
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0;
            text-transform: uppercase;
            margin-bottom: 0.45rem;
        }

        .app-subtitle {
            color: var(--muted);
            font-size: 1rem;
            margin-top: 0;
            margin-bottom: 1.25rem;
        }

        .summary-strip {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 8px;
            color: var(--text);
            padding: 1rem 1.1rem;
            margin: 0.5rem 0 1.25rem;
        }

        .mode-card {
            background: var(--panel);
            border: 1px solid var(--line);
            border-left: 4px solid var(--accent);
            border-radius: 8px;
            padding: 1rem 1.1rem;
            margin: 0.75rem 0 1rem;
        }

        .mode-card .label {
            color: var(--muted);
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0;
            text-transform: uppercase;
            margin-bottom: 0.35rem;
        }

        .mode-card .url {
            color: var(--text);
            font-size: 1.25rem;
            font-weight: 700;
            line-height: 1.35;
            overflow-wrap: anywhere;
        }

        .mode-card .count {
            color: var(--muted);
            margin-top: 0.35rem;
        }

        .help-panel {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 1.1rem;
        }

        .help-panel p,
        .help-panel li {
            color: #334155;
        }

        .conclusion-panel {
            background: linear-gradient(135deg, #eff6ff 0%, #f0fdf4 100%);
            border: 1px solid #bfdbfe;
            border-radius: 10px;
            padding: 1.1rem 1.2rem;
        }
        .conclusion-panel h4 {
            margin: 0 0 0.5rem;
            color: #1e40af;
            font-size: 0.95rem;
        }
        .conclusion-panel ul {
            margin: 0.35rem 0 0 1.1rem;
        }
        .metric-delta-good {
            color: var(--success);
            font-size: 0.8rem;
        }
        .metric-delta-warn {
            color: var(--warning);
            font-size: 0.8rem;
        }

        div[data-testid="stMetric"] {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 0.8rem 0.9rem;
        }

        div[data-testid="stMetric"] label {
            color: var(--muted);
        }

        div[data-testid="stMetric"] [data-testid="stMetricValue"],
        div[data-testid="stMetric"] [data-testid="stMetricValue"] *,
        div[data-testid="stMetric"] [data-testid="stMetricDelta"],
        div[data-testid="stMetric"] [data-testid="stMetricDelta"] * {
            color: var(--text);
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 0.25rem;
            border-bottom: 1px solid var(--line);
        }

        .stTabs [data-baseweb="tab"] {
            height: 2.75rem;
            padding: 0 1rem;
            color: var(--muted);
            background: transparent;
            border-radius: 6px 6px 0 0;
        }

        .stTabs [data-baseweb="tab"] p,
        .stTabs [data-baseweb="tab"] span {
            color: var(--muted);
        }

        .stTabs [aria-selected="true"] {
            color: var(--accent);
            background: var(--panel);
            border: 1px solid var(--line);
            border-bottom-color: var(--panel);
        }

        .stTabs [aria-selected="true"] p,
        .stTabs [aria-selected="true"] span {
            color: var(--accent);
        }

        .stButton > button {
            border-radius: 6px;
            font-weight: 700;
        }

        .stButton > button[kind="primary"],
        .stButton > button[kind="primary"] * {
            background: var(--accent);
            border-color: var(--accent);
            color: #ffffff;
        }

        .stButton > button[kind="secondary"],
        .stButton > button[kind="secondary"] * {
            color: var(--text);
        }

        [data-baseweb="radio"] *,
        [data-baseweb="select"] *,
        [data-baseweb="slider"] *,
        [data-baseweb="input"] *,
        [data-baseweb="textarea"] * {
            color: var(--text);
        }

        [data-testid="stAlert"] *,
        [data-testid="stFileUploader"] *,
        [data-testid="stExpander"] * {
            color: var(--text);
        }

        input,
        textarea {
            color: var(--text);
            background: #ffffff;
        }

        .stDataFrame,
        [data-testid="stTable"] {
            border: 1px solid var(--line);
            border-radius: 8px;
            overflow: hidden;
        }

        hr {
            border-color: var(--line);
        }
    </style>
    """,
    unsafe_allow_html=True,
)


PLOTLY_TEMPLATE = "plotly_white"
PRIMARY_BLUE = "#2563eb"
GREEN = "#16a34a"
AMBER = "#d97706"
RED = "#dc2626"
SLATE = "#475569"


def apply_chart_style(fig, height=400):
    """Apply common chart styling for the white dashboard."""
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        height=height,
        margin=dict(l=20, r=20, t=55, b=35),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(color="#111827"),
        title_font=dict(size=16, color="#111827"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(gridcolor="#e2e8f0", zerolinecolor="#e2e8f0")
    fig.update_yaxes(gridcolor="#e2e8f0", zerolinecolor="#e2e8f0")
    return fig


def has_loaded_data():
    return bool(st.session_state.get("urls"))


def reset_analysis_state():
    st.session_state["processed"] = False
    for key in ["bf", "results", "accuracy_stats", "mode_result"]:
        st.session_state.pop(key, None)


def run_bloom_filter_analysis(urls, fp_rate):
    """
    Process URLs in chronological order and compare Bloom filter predictions with
    exact ground truth from a Python set.
    """
    unique_count = max(len(set(urls)), 1)
    bf = BloomFilter(expected_items=unique_count, false_positive_rate=fp_rate)

    results = []
    ground_truth_set = set()
    true_positives = 0
    false_positives = 0
    true_negatives = 0
    false_negatives = 0

    for url in urls:
        bf_says_duplicate = bf.check(url)
        actually_duplicate = url in ground_truth_set

        if bf_says_duplicate and actually_duplicate:
            status = "True Duplicate"
            true_positives += 1
        elif bf_says_duplicate and not actually_duplicate:
            status = "False Positive"
            false_positives += 1
        elif not bf_says_duplicate and not actually_duplicate:
            status = "First Seen"
            true_negatives += 1
        else:
            status = "False Negative"
            false_negatives += 1

        results.append(
            {
                "url": url,
                "bloom_filter_result": "Duplicate" if bf_says_duplicate else "First Seen",
                "actual": "Duplicate" if actually_duplicate else "First Seen",
                "status": status,
            }
        )

        if not actually_duplicate:
            bf.add(url)
        ground_truth_set.add(url)

    total = len(urls) if urls else 0
    accuracy = (true_positives + true_negatives) / total * 100 if total else 0
    precision = (
        true_positives / (true_positives + false_positives) * 100
        if (true_positives + false_positives) > 0
        else 100.0
    )
    recall = (
        true_positives / (true_positives + false_negatives) * 100
        if (true_positives + false_negatives) > 0
        else 100.0
    )
    specificity = (
        true_negatives / (true_negatives + false_positives) * 100
        if (true_negatives + false_positives) > 0
        else 100.0
    )
    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) > 0
        else 0.0
    )
    actual_fpr = (
        false_positives / (false_positives + true_negatives) * 100
        if (false_positives + true_negatives) > 0
        else 0.0
    )
    actual_fnr = (
        false_negatives / (false_negatives + true_positives) * 100
        if (false_negatives + true_positives) > 0
        else 0.0
    )
    theoretical_fpr = bf.current_false_positive_rate() * 100 if total else 0.0

    accuracy_stats = {
        "true_positives": true_positives,
        "false_positives": false_positives,
        "true_negatives": true_negatives,
        "false_negatives": false_negatives,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "specificity": specificity,
        "f1_score": f1,
        "actual_fpr": actual_fpr,
        "actual_fnr": actual_fnr,
        "theoretical_fpr": theoretical_fpr,
    }

    return bf, results, accuracy_stats


def render_data_metrics(urls):
    duplicate_count = len(urls) - len(set(urls))
    duplicate_pct = duplicate_count / len(urls) * 100 if urls else 0

    col_a, col_b, col_c, col_d = st.columns(4)
    col_a.metric("Total entries", f"{len(urls):,}")
    col_b.metric("Unique URLs", f"{len(set(urls)):,}")
    col_c.metric("Duplicate entries", f"{duplicate_count:,}")
    col_d.metric("Duplicate rate", f"{duplicate_pct:.1f}%")


def render_empty_state(message):
    st.info(message)


def render_overview():
    st.header("Project Overview")

    st.markdown(
        """
        <div class="help-panel">
            <p><strong>What this project does:</strong> it reads browser-history URLs,
            detects repeat visits with a Bloom filter, and calculates the mode: the URL
            visited most often.</p>
            <p><strong>Why Bloom filters matter:</strong> they use far less memory than
            storing every full URL, but they are probabilistic. A duplicate result can
            occasionally be a false positive. A first-seen result should not be a false
            negative.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("Workflow")
    st.markdown(
        """
        1. Generate synthetic browser history or upload a CSV.
        2. Pick the target false positive rate.
        3. Run the Bloom filter analysis.
        4. Review duplicate detection, mode results, and memory savings.
        """
    )

    if not has_loaded_data():
        render_empty_state("Load data from the sidebar to preview dataset and Bloom filter settings.")
        return

    urls = st.session_state["urls"]
    st.subheader("Loaded Data")
    render_data_metrics(urls)

    unique_count = max(len(set(urls)), 1)
    fp_rate = st.session_state.get("fp_rate", 0.01)
    bit_array_size = BloomFilter._optimal_size(unique_count, fp_rate)
    hash_count = BloomFilter._optimal_hash_count(bit_array_size, unique_count)
    hashset_mem = estimate_hashset_memory(urls)

    st.subheader("Bloom Filter Preview")
    col_e, col_f, col_g, col_h = st.columns(4)
    col_e.metric("Bit array size", f"{bit_array_size:,}")
    col_f.metric("Hash functions", f"{hash_count}")
    col_g.metric("Bloom memory", format_memory_size(math.ceil(bit_array_size / 8)))
    col_h.metric("HashSet memory", format_memory_size(hashset_mem))

    if "df" in st.session_state:
        st.subheader("Sample Rows")
        st.dataframe(st.session_state["df"].head(10), use_container_width=True)


def render_detection():
    st.header("Duplicate Detection")

    if not has_loaded_data():
        render_empty_state("Load data from the sidebar before running the analysis.")
        return

    if not st.session_state.get("processed", False):
        render_empty_state("Click Run analysis in the sidebar to process the loaded URLs.")
        return

    urls = st.session_state["urls"]
    fp_rate = st.session_state.get("fp_rate", 0.01)

    if (
        "results" not in st.session_state
        or "bf" not in st.session_state
        or st.session_state.get("processed_fp_rate") != fp_rate
    ):
        with st.spinner("Processing URLs through the Bloom filter..."):
            bf, results, accuracy_stats = run_bloom_filter_analysis(urls, fp_rate)
        st.session_state["bf"] = bf
        st.session_state["results"] = results
        st.session_state["accuracy_stats"] = accuracy_stats
        st.session_state["processed_fp_rate"] = fp_rate

    bf = st.session_state["bf"]
    results = st.session_state["results"]
    accuracy_stats = st.session_state["accuracy_stats"]

    # --- Confusion counts ---
    st.subheader("Confusion Matrix Counts")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("True duplicates (TP)", f"{accuracy_stats['true_positives']:,}")
    col2.metric("First seen (TN)", f"{accuracy_stats['true_negatives']:,}")
    col3.metric("False positives (FP)", f"{accuracy_stats['false_positives']:,}", delta=f"{accuracy_stats['actual_fpr']:.2f}% FPR", delta_color="inverse")
    col4.metric("False negatives (FN)", f"{accuracy_stats['false_negatives']:,}", delta="0 is ideal", delta_color="off")

    # --- Core classification metrics ---
    st.subheader("Evaluation Metrics")
    st.caption("Metrics computed against exact HashSet ground truth. Higher is better except FPR/FNR.")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Accuracy", f"{accuracy_stats['accuracy']:.2f}%", help="(TP+TN)/Total")
    m2.metric("Precision", f"{accuracy_stats['precision']:.2f}%", help="TP/(TP+FP) — when filter says duplicate, how often is it right")
    m3.metric("Recall", f"{accuracy_stats['recall']:.2f}%", help="TP/(TP+FN) — of actual duplicates, how many were caught. Should be 100%")
    m4.metric("F1 Score", f"{accuracy_stats['f1_score']:.2f}%", help="Harmonic mean of precision & recall")

    m5, m6, m7, m8 = st.columns(4)
    m5.metric(
        "Actual FPR",
        f"{accuracy_stats['actual_fpr']:.3f}%",
        delta=f"target {bf.false_positive_rate:.2%}",
        delta_color="off",
        help="FP/(FP+TN) — observed false positive rate",
    )
    m6.metric(
        "Theoretical FPR",
        f"{accuracy_stats['theoretical_fpr']:.3f}%",
        help="(1 - e^(-k·n/m))^k — expected from Bloom formula",
    )
    m7.metric("Specificity", f"{accuracy_stats['specificity']:.2f}%", help="TN/(TN+FP) — true negative rate")
    m8.metric("False Neg Rate", f"{accuracy_stats['actual_fnr']:.3f}%", help="FN/(FN+TP) — must be 0% for Bloom filter guarantee")

    # Quick verdict badge
    if accuracy_stats["false_negatives"] == 0:
        st.success("✓ Bloom guarantee holds — **0 false negatives**. No duplicate was missed.")
    else:
        st.error("✗ Unexpected false negatives — Bloom filter guarantee violated (bug).")

    if accuracy_stats["actual_fpr"] <= bf.false_positive_rate * 100 * 1.5 + 0.1:
        st.caption(f"✓ Observed FPR ({accuracy_stats['actual_fpr']:.3f}%) is within tolerance of target ({bf.false_positive_rate:.2%}).")
    else:
        st.caption(f"⚠ Observed FPR ({accuracy_stats['actual_fpr']:.3f}%) exceeds target ({bf.false_positive_rate:.2%}) — filter is more full than designed.")

    # --- What we built ---
    bloom_mem = bf.memory_usage_bytes()
    hash_mem = estimate_hashset_memory(urls)
    savings = (1 - bloom_mem / hash_mem) * 100 if hash_mem else 0
    st.markdown(
        f"""
        <div class="conclusion-panel">
            <h4>What we built &amp; what it proves</h4>
            <ul>
                <li><strong>System:</strong> Streaming duplicate detection on <strong>{len(urls):,}</strong> visits ({len(set(urls)):,} unique) without storing full URLs.</li>
                <li><strong>Method:</strong> Bloom filter <code>m={bf.size:,}</code> bits, <code>k={bf.hash_count}</code> hashes @ target FPR <strong>{bf.false_positive_rate:.2%}</strong>.</li>
                <li><strong>Efficiency:</strong> <strong>{format_memory_size(bloom_mem)}</strong> vs HashSet <strong>{format_memory_size(hash_mem)}</strong> → <strong>{savings:.1f}% memory saved</strong>.</li>
                <li><strong>Accuracy:</strong> {accuracy_stats['accuracy']:.2f}% accuracy, {accuracy_stats['precision']:.2f}% precision, {accuracy_stats['recall']:.2f}% recall, F1 {accuracy_stats['f1_score']:.2f}%.</li>
                <li><strong>Conclusion:</strong> Probabilistic structure achieves near-exact accuracy with ~{savings:.0f}% less memory; only cost is <strong>{accuracy_stats['actual_fpr']:.2f}% false positives</strong> and zero false negatives — ideal for Big Data pre-filtering at scale.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Downloadable metrics for report
    with st.expander("Export metrics for report"):
        metrics_row = {
            "total": len(urls),
            "unique": len(set(urls)),
            "target_fpr": bf.false_positive_rate,
            "bits_m": bf.size,
            "hashes_k": bf.hash_count,
            "bloom_bytes": bloom_mem,
            "hashset_bytes": hash_mem,
            "savings_pct": savings,
            **accuracy_stats,
        }
        st.json(metrics_row, expanded=False)
        st.download_button(
            "Download metrics JSON",
            data=pd.Series(metrics_row).to_json(indent=2),
            file_name="bloom_metrics.json",
            mime="application/json",
        )
        st.download_button(
            "Download metrics CSV",
            data=pd.DataFrame([metrics_row]).to_csv(index=False),
            file_name="bloom_metrics.csv",
            mime="text/csv",
        )

    st.subheader("Filter Parameters")
    stats_df = pd.DataFrame(list(bf.get_stats().items()), columns=["Parameter", "Value"])
    st.table(stats_df)

    st.subheader("Detection Results")
    filter_option = st.selectbox(
        "Result type",
        ["All", "True Duplicate", "First Seen", "False Positive", "False Negative"],
    )

    results_df = pd.DataFrame(results)
    if filter_option != "All":
        results_df = results_df[results_df["status"] == filter_option]

    st.caption(f"Showing {min(len(results_df), 500):,} of {len(results_df):,} matching rows.")
    st.dataframe(
        results_df.head(500),
        use_container_width=True,
        column_config={
            "url": st.column_config.TextColumn("URL", width="large"),
            "bloom_filter_result": st.column_config.TextColumn("Bloom filter result"),
            "actual": st.column_config.TextColumn("Ground truth"),
            "status": st.column_config.TextColumn("Verdict"),
        },
    )


def render_mode_analysis():
    st.header("Mode Analysis")

    if not has_loaded_data():
        render_empty_state("Load data from the sidebar to calculate the most visited URL.")
        return

    urls = st.session_state["urls"]
    mode_result = calculate_mode(urls)
    st.session_state["mode_result"] = mode_result

    if mode_result["is_multimodal"]:
        st.warning(
            f"{len(mode_result['all_modes'])} URLs are tied for the highest visit count."
        )

    st.markdown(
        f"""
        <div class="mode-card">
            <div class="label">Most visited URL</div>
            <div class="url">{mode_result["mode_url"]}</div>
            <div class="count">Visited <strong>{mode_result["mode_count"]:,}</strong> times</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("Summary")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total entries", f"{mode_result['total_urls']:,}")
    col2.metric("Unique URLs", f"{mode_result['unique_urls']:,}")
    col3.metric("Duplicate entries", f"{mode_result['duplicate_count']:,}")
    col4.metric("Duplicate rate", f"{mode_result['duplicate_percentage']:.1f}%")

    if mode_result["is_multimodal"]:
        st.subheader("URLs Tied For Mode")
        modes_df = pd.DataFrame(mode_result["all_modes"], columns=["URL", "Visit Count"])
        st.dataframe(modes_df, use_container_width=True)

    st.subheader("Top URLs")
    top10_df = pd.DataFrame(mode_result["top_10"], columns=["URL", "Visit Count"])
    top10_df.index = range(1, len(top10_df) + 1)
    top10_df.index.name = "Rank"

    col_table, col_chart = st.columns([1, 1])
    with col_table:
        st.dataframe(top10_df, use_container_width=True)
    with col_chart:
        fig = px.bar(
            top10_df.reset_index(),
            x="Visit Count",
            y="URL",
            orientation="h",
            title="Top 10 URLs by visits",
            color_discrete_sequence=[PRIMARY_BLUE],
        )
        fig.update_layout(yaxis=dict(autorange="reversed"), showlegend=False)
        st.plotly_chart(apply_chart_style(fig, height=420), use_container_width=True)

    st.subheader("Frequency Distribution")
    freq_data = get_frequency_dataframe(mode_result["frequency_distribution"], top_n=20)
    freq_df = pd.DataFrame(freq_data)

    fig_dist = px.bar(
        freq_df,
        x="url",
        y="visits",
        title="Top 20 URLs by visit count",
        labels={"url": "URL", "visits": "Visits"},
        color_discrete_sequence=[SLATE],
    )
    fig_dist.update_layout(xaxis_tickangle=-35)
    st.plotly_chart(apply_chart_style(fig_dist, height=500), use_container_width=True)


def render_conclusion():
    st.header("Conclusion & Insights")
    if not has_loaded_data():
        render_empty_state("Load data and run analysis to generate the conclusion.")
        return
    if not st.session_state.get("processed") or "bf" not in st.session_state:
        render_empty_state("Run the analysis from the sidebar to build the conclusion.")
        return

    bf = st.session_state["bf"]
    urls = st.session_state["urls"]
    s = st.session_state["accuracy_stats"]
    mode_result = st.session_state.get("mode_result") or calculate_mode(urls)
    bloom_mem = bf.memory_usage_bytes()
    hash_mem = estimate_hashset_memory(urls)
    savings = (1 - bloom_mem / hash_mem) * 100 if hash_mem else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Dataset", f"{len(urls):,} visits")
    c2.metric("Bloom memory", format_memory_size(bloom_mem), delta=f"-{savings:.1f}% vs HashSet", delta_color="normal")
    c3.metric("Accuracy / F1", f"{s['accuracy']:.1f}% / {s['f1_score']:.1f}%")
    c4.metric("Most visited", f"{mode_result['mode_count']:,}×", help=mode_result["mode_url"])

    st.markdown(
        f"""
        <div class="conclusion-panel">
            <h4>What we made</h4>
            <p>A <strong>big-data efficient duplicate detector</strong> for browser history using a Bloom filter
            plus exact <strong>mode calculation</strong> (most visited URL). Pipeline: ingest CSV → stream through
            <code>m={bf.size:,}</code> / <code>k={bf.hash_count}</code> Bloom filter vs HashSet ground truth → evaluate.</p>
            <h4>Key conclusions</h4>
            <ul>
                <li><strong>Memory wins at scale:</strong> {format_memory_size(bloom_mem)} vs {format_memory_size(hash_mem)} — <strong>{savings:.1f}% saved</strong>. Storing hashes/bits beats storing full URL strings; gap widens with millions of URLs.</li>
                <li><strong>Accuracy is usable:</strong> {s['accuracy']:.2f}% accuracy, {s['precision']:.2f}% precision, <strong>{s['recall']:.2f}% recall</strong> — false negatives are <strong>{s['false_negatives']}</strong> (guaranteed 0). Only price is {s['actual_fpr']:.2f}% false positives (near target {bf.false_positive_rate:.2%}).</li>
                <li><strong>When to use:</strong> Best as a <em>first-pass filter</em> before expensive exact checks (DB / disk). Not suitable if any false positive is unacceptable.</li>
                <li><strong>Mode insight:</strong> Top URL <code>{mode_result['mode_url']}</code> ({mode_result['mode_count']:,} visits) reflects power-law browsing — small pool drives most duplicates ({mode_result['duplicate_percentage']:.1f}% duplicates).</li>
                <li><strong>Tunable trade-off:</strong> Lower target FPR → larger <em>m</em> → more memory; higher fill ratio → FPR climbs. Current fill {bf.fill_ratio():.1%} at {bf.items_added:,} inserts.</li>
            </ul>
            <p style="margin-top:0.6rem;color:#334155"><strong>Bottom line:</strong> For big browser logs, Bloom filter gives ~<strong>{savings:.0f}% memory cut</strong> for ~<strong>{s['actual_fpr']:.1f}% extra checks</strong> — a practical Big Data trade-off.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_visualizations():
    st.header("Visualizations")

    if not st.session_state.get("processed", False):
        render_empty_state("Run the Bloom filter analysis to unlock charts.")
        return

    if "bf" not in st.session_state or "accuracy_stats" not in st.session_state:
        render_empty_state("Open the Detection tab once to calculate the analysis results.")
        return

    bf = st.session_state["bf"]
    urls = st.session_state["urls"]
    accuracy_stats = st.session_state["accuracy_stats"]

    st.subheader("Bit Array Snapshot")
    st.caption("Each cell represents a sampled bit. Light cells are empty; blue cells are set.")

    bit_snapshot = bf.get_bit_array_snapshot(max_length=500)
    num_cols = 50
    num_rows = len(bit_snapshot) // num_cols

    if num_rows > 0:
        bit_matrix = np.array(bit_snapshot[: num_rows * num_cols]).reshape(num_rows, num_cols)
        fig_heatmap = go.Figure(
            data=go.Heatmap(
                z=bit_matrix,
                colorscale=[[0, "#eff6ff"], [1, PRIMARY_BLUE]],
                showscale=True,
                colorbar=dict(title="Bit", tickvals=[0, 1], ticktext=["0", "1"]),
            )
        )
        fig_heatmap.update_layout(
            title=f"Bloom filter bit array sample ({bf.size:,} total bits)",
            xaxis_title="Column",
            yaxis_title="Row",
        )
        st.plotly_chart(apply_chart_style(fig_heatmap, height=390), use_container_width=True)

    st.subheader("Detection Breakdown")
    col1, col2 = st.columns(2)

    with col1:
        labels = ["True Duplicate", "First Seen", "False Positive", "False Negative"]
        values = [
            accuracy_stats["true_positives"],
            accuracy_stats["true_negatives"],
            accuracy_stats["false_positives"],
            accuracy_stats["false_negatives"],
        ]
        fig_pie = go.Figure(
            data=[
                go.Pie(
                    labels=labels,
                    values=values,
                    marker=dict(colors=[GREEN, PRIMARY_BLUE, AMBER, RED]),
                    hole=0.45,
                    textinfo="label+percent",
                )
            ]
        )
        fig_pie.update_layout(title="Prediction outcomes")
        st.plotly_chart(apply_chart_style(fig_pie, height=390), use_container_width=True)

    with col2:
        cm_data = [
            [accuracy_stats["true_positives"], accuracy_stats["false_negatives"]],
            [accuracy_stats["false_positives"], accuracy_stats["true_negatives"]],
        ]
        fig_cm = go.Figure(
            data=go.Heatmap(
                z=cm_data,
                x=["Predicted duplicate", "Predicted first seen"],
                y=["Actually duplicate", "Actually first seen"],
                text=[[str(v) for v in row] for row in cm_data],
                texttemplate="%{text}",
                textfont={"size": 18},
                colorscale="Blues",
                showscale=False,
            )
        )
        fig_cm.update_layout(
            title="Confusion matrix",
            xaxis_title="Bloom filter prediction",
            yaxis_title="Ground truth",
        )
        st.plotly_chart(apply_chart_style(fig_cm, height=390), use_container_width=True)

    st.subheader("Memory Comparison")
    bloom_memory = bf.memory_usage_bytes()
    hashset_memory = estimate_hashset_memory(urls)
    savings_pct = (1 - bloom_memory / hashset_memory) * 100 if hashset_memory > 0 else 0

    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Bloom filter", format_memory_size(bloom_memory))
    col_m2.metric("Python HashSet", format_memory_size(hashset_memory))
    col_m3.metric("Memory saved", f"{savings_pct:.1f}%")

    fig_mem = go.Figure(
        data=[
            go.Bar(
                name="Bloom filter",
                x=["Memory usage"],
                y=[bloom_memory],
                marker_color=GREEN,
                text=[format_memory_size(bloom_memory)],
                textposition="auto",
            ),
            go.Bar(
                name="Python HashSet",
                x=["Memory usage"],
                y=[hashset_memory],
                marker_color=RED,
                text=[format_memory_size(hashset_memory)],
                textposition="auto",
            ),
        ]
    )
    fig_mem.update_layout(
        title=f"Bloom filter saves {savings_pct:.1f}% memory",
        yaxis_title="Bytes",
        barmode="group",
    )
    st.plotly_chart(apply_chart_style(fig_mem, height=390), use_container_width=True)

    st.subheader("Fill Ratio Over Time")
    st.caption("A higher fill ratio means more bit collisions and higher false-positive risk.")

    if bf.fill_history:
        fill_df = pd.DataFrame(bf.fill_history)
        fig_fill = px.line(
            fill_df,
            x="items",
            y="fill_ratio",
            title="Bit array fill ratio",
            labels={"items": "Unique URLs inserted", "fill_ratio": "Fill ratio"},
            markers=True,
            color_discrete_sequence=[PRIMARY_BLUE],
        )
        fig_fill.add_hline(
            y=0.5,
            line_dash="dash",
            line_color=AMBER,
            annotation_text="50% fill",
        )
        st.plotly_chart(apply_chart_style(fig_fill, height=390), use_container_width=True)
    else:
        st.info("Fill history is not available for this dataset.")

    st.subheader("False Positive Rate Curve")
    m = bf.size
    k = bf.hash_count
    n_values = list(range(1, bf.expected_items * 2, max(1, bf.expected_items // 50)))
    fp_rates = [(1 - math.exp(-k * n / m)) ** k for n in n_values]

    fig_fp = px.line(
        x=n_values,
        y=fp_rates,
        title="Theoretical false-positive rate as the filter fills",
        labels={"x": "Unique URLs inserted", "y": "False-positive rate"},
        color_discrete_sequence=[PRIMARY_BLUE],
    )
    fig_fp.add_vline(
        x=bf.expected_items,
        line_dash="dash",
        line_color=GREEN,
        annotation_text=f"Expected capacity ({bf.expected_items:,})",
    )
    fig_fp.add_hline(
        y=bf.false_positive_rate,
        line_dash="dash",
        line_color=RED,
        annotation_text=f"Target rate ({bf.false_positive_rate:.2%})",
    )
    st.plotly_chart(apply_chart_style(fig_fp, height=390), use_container_width=True)


if "processed" not in st.session_state:
    st.session_state["processed"] = False
if "fp_rate" not in st.session_state:
    st.session_state["fp_rate"] = 0.01


with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-badge">● Big Data Analytics</div>
            <div class="sidebar-brand-title">URL Duplicate Analyzer</div>
            <div class="sidebar-brand-subtitle">Bloom filter &amp; mode detection for browser history</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Status — compact, presentation-ready
    if has_loaded_data():
        _urls = st.session_state["urls"]
        _unique = len(set(_urls))
        _dups = len(_urls) - _unique
        st.markdown(
            f"""
            <div class="sidebar-status loaded">
                <strong>✓ Dataset ready</strong><br>
                {len(_urls):,} visits · {_unique:,} unique · {_dups:,} duplicates
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.session_state.get("processed"):
            st.caption("Analysis completed — see Detection / Charts tabs.")
        else:
            st.caption("Press **Run analysis** to process with the current filter settings.")
    else:
        st.markdown(
            """
            <div class="sidebar-status">
                <strong>No dataset loaded</strong><br>
                Generate synthetic data or upload a CSV to begin.
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    st.markdown('<div class="sidebar-step">Step 1 — Data source</div>', unsafe_allow_html=True)
    data_source = st.radio(
        "Choose data source",
        ["Generate synthetic data", "Upload CSV file"],
        label_visibility="collapsed",
        help="Synthetic data is great for demos. CSV files should contain a column named url, link, or similar.",
    )

    if data_source == "Generate synthetic data":
        st.caption("Create a realistic browsing history with power-law popularity.")
        num_entries = st.slider(
            "Total entries",
            min_value=1000,
            max_value=50000,
            value=10000,
            step=1000,
            help="Total browser history rows to generate.",
        )
        num_unique = st.slider(
            "Unique URL pool",
            min_value=50,
            max_value=2000,
            value=500,
            step=50,
            help="Number of distinct URLs used by the generator.",
        )
        dup_ratio = st.slider(
            "Duplicate pressure",
            min_value=0.1,
            max_value=0.9,
            value=0.6,
            step=0.05,
            help="Higher values create more repeated visits.",
        )

        if st.button("Generate data", use_container_width=True, type="primary"):
            with st.spinner("Generating browser history..."):
                output_path = os.path.join("data", "browser_history.csv")
                path, summary = generate_browser_history(
                    num_entries=num_entries,
                    num_unique_urls=num_unique,
                    duplicate_ratio=dup_ratio,
                    output_path=output_path,
                )
                df = pd.read_csv(path)
                st.session_state["data_path"] = path
                st.session_state["data_summary"] = summary
                st.session_state["urls"] = df["url"].astype(str).tolist()
                st.session_state["df"] = df
                reset_analysis_state()
            st.success(f"Generated {num_entries:,} rows.")
            st.rerun()

    else:
        st.caption("CSV must include a column named `url` or `link`.")
        uploaded_file = st.file_uploader(
            "Browser history CSV",
            type=["csv"],
            label_visibility="collapsed",
            help="The CSV must include a column named url, link, or similar.",
        )
        if uploaded_file is not None:
            try:
                urls_loaded = load_uploaded_csv(uploaded_file)
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file)
                st.session_state["urls"] = urls_loaded
                st.session_state["df"] = df
                reset_analysis_state()
                st.success(f"Loaded {len(urls_loaded):,} URLs.")
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))

    # Quick clear action when data is loaded
    if has_loaded_data():
        if st.button("Clear dataset", use_container_width=True):
            for key in ["urls", "df", "data_path", "data_summary"]:
                st.session_state.pop(key, None)
            reset_analysis_state()
            st.rerun()

    st.divider()

    st.markdown('<div class="sidebar-step">Step 2 — Bloom filter</div>', unsafe_allow_html=True)
    st.caption("Lower false-positive rate uses more memory. Default 1% is balanced.")
    previous_fp_rate = st.session_state.get("fp_rate", 0.01)
    fp_rate = st.select_slider(
        "Target false-positive rate",
        options=[0.1, 0.05, 0.01, 0.005, 0.001, 0.0001],
        value=previous_fp_rate,
        format_func=lambda x: f"{x:.2%}",
        help="Lower rates use more memory.",
    )
    if fp_rate != previous_fp_rate:
        st.session_state["fp_rate"] = fp_rate
        reset_analysis_state()

    # Live preview of memory / parameters
    if has_loaded_data():
        _n = max(len(set(st.session_state["urls"])), 1)
        _m = BloomFilter._optimal_size(_n, fp_rate)
        _k = BloomFilter._optimal_hash_count(_m, _n)
        st.caption(f"Preview: **{_m:,} bits · {_k} hashes · {format_memory_size(math.ceil(_m / 8))}**")

    st.divider()

    st.markdown('<div class="sidebar-step">Step 3 — Analyze</div>', unsafe_allow_html=True)
    run_disabled = not has_loaded_data()
    if st.button(
        "Run analysis",
        use_container_width=True,
        type="primary",
        disabled=run_disabled,
        help="Load data first" if run_disabled else "Process URLs and compute accuracy + mode",
    ):
        st.session_state["processed"] = True
        st.rerun()

    if run_disabled:
        st.caption("Load a dataset to enable analysis.")
    elif not st.session_state.get("processed"):
        st.caption("Ready to run with the current settings.")

    st.divider()
    st.markdown(
        '<div class="sidebar-hint">Tip: try synthetic data first, then upload your own history to compare memory savings.</div>',
        unsafe_allow_html=True,
    )


st.markdown("<div class='app-kicker'>Big Data Analytics</div>", unsafe_allow_html=True)
st.title("URL Duplicate Analyzer")
st.markdown(
    "<div class='app-subtitle'>Bloom filter duplicate detection with mode analysis for browser history.</div>",
    unsafe_allow_html=True,
)

if has_loaded_data():
    urls = st.session_state["urls"]
    duplicate_count = len(urls) - len(set(urls))
    st.markdown(
        f"""
        <div class="summary-strip">
            Loaded <strong>{len(urls):,}</strong> URL visits with
            <strong>{len(set(urls)):,}</strong> unique URLs and
            <strong>{duplicate_count:,}</strong> duplicate entries.
        </div>
        """,
        unsafe_allow_html=True,
    )


tab_overview, tab_detection, tab_mode, tab_charts, tab_conclusion = st.tabs(
    ["Overview", "Detection", "Mode", "Charts", "Conclusion"]
)

with tab_overview:
    render_overview()

with tab_detection:
    render_detection()

with tab_mode:
    render_mode_analysis()

with tab_charts:
    render_visualizations()

with tab_conclusion:
    render_conclusion()


st.divider()
st.caption("Duplicate URL detection with Bloom filters & mode analysis — Big Data Analytics")
