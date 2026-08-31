"""
main.py — FastAPI Backend for URL Duplicate Analyzer
=====================================================

Provides REST API endpoints for:
    - Generating synthetic browser history data
    - Uploading CSV files
    - Running Bloom Filter analysis
    - Getting analysis results
"""

import math
import os
from typing import Optional

import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from bloom_filter import BloomFilter
from data_generator import generate_browser_history
from mode_calculator import calculate_mode, get_frequency_dataframe
from utils import (
    estimate_hashset_memory,
    format_memory_size,
    load_csv_data,
    load_uploaded_csv_to_df,
)

app = FastAPI(
    title="URL Duplicate Analyzer API",
    description="Bloom Filter duplicate detection with mode analysis for browser history",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)


class GenerateDataRequest(BaseModel):
    num_entries: int = 10000
    num_unique_urls: int = 500
    duplicate_ratio: float = 0.6


class AnalyzeRequest(BaseModel):
    data_path: str
    fp_rate: float = 0.01


class DataSummary(BaseModel):
    total_entries: int
    unique_urls_in_pool: int
    unique_urls_in_data: int
    duplicate_entries: int
    actual_duplicate_ratio: float
    output_path: str


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "URL Duplicate Analyzer API is running"}


@app.post("/api/generate-data")
async def generate_data(request: GenerateDataRequest):
    try:
        output_path = os.path.join(DATA_DIR, "browser_history.csv")
        path, summary = generate_browser_history(
            num_entries=request.num_entries,
            num_unique_urls=request.num_unique_urls,
            duplicate_ratio=request.duplicate_ratio,
            output_path=output_path,
        )

        df = pd.read_csv(path)
        urls = df["url"].astype(str).tolist()

        return {
            "success": True,
            "data_path": path,
            "summary": summary,
            "sample_data": df.head(10).to_dict(orient="records"),
            "total_urls": len(urls),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    try:
        content = await file.read()
        urls, df = load_uploaded_csv_to_df(content)

        output_path = os.path.join(DATA_DIR, "uploaded_history.csv")
        df.to_csv(output_path, index=False)

        unique_count = len(set(urls))
        duplicate_count = len(urls) - unique_count

        return {
            "success": True,
            "data_path": output_path,
            "summary": {
                "total_entries": len(urls),
                "unique_urls_in_data": unique_count,
                "duplicate_entries": duplicate_count,
                "actual_duplicate_ratio": duplicate_count / len(urls) if urls else 0,
            },
            "sample_data": df.head(10).to_dict(orient="records"),
            "total_urls": len(urls),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze")
async def analyze(request: AnalyzeRequest):
    try:
        if not os.path.exists(request.data_path):
            raise HTTPException(status_code=404, detail="Data file not found")

        urls = load_csv_data(request.data_path)

        unique_count = max(len(set(urls)), 1)
        bf = BloomFilter(expected_items=unique_count, false_positive_rate=request.fp_rate)

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

            results.append({
                "url": url,
                "bloom_filter_result": "Duplicate" if bf_says_duplicate else "First Seen",
                "actual": "Duplicate" if actually_duplicate else "First Seen",
                "status": status,
            })

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

        bloom_mem = bf.memory_usage_bytes()
        hash_mem = estimate_hashset_memory(urls)
        savings = (1 - bloom_mem / hash_mem) * 100 if hash_mem else 0

        mode_result = calculate_mode(urls)
        freq_data = get_frequency_dataframe(mode_result["frequency_distribution"], top_n=20)

        mode_result_serializable = {
            "mode_url": mode_result["mode_url"],
            "mode_count": mode_result["mode_count"],
            "all_modes": mode_result["all_modes"],
            "is_multimodal": mode_result["is_multimodal"],
            "top_10": mode_result["top_10"],
            "total_urls": mode_result["total_urls"],
            "unique_urls": mode_result["unique_urls"],
            "duplicate_count": mode_result["duplicate_count"],
            "duplicate_percentage": mode_result["duplicate_percentage"],
        }

        bit_snapshot = bf.get_bit_array_snapshot(max_length=500)

        m = bf.size
        k = bf.hash_count
        n_values = list(range(1, bf.expected_items * 2, max(1, bf.expected_items // 50)))
        fp_rates_curve = [(1 - math.exp(-k * n / m)) ** k for n in n_values]

        return {
            "success": True,
            "accuracy_stats": {
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
            },
            "bloom_filter": {
                "size": bf.size,
                "hash_count": bf.hash_count,
                "items_added": bf.items_added,
                "expected_items": bf.expected_items,
                "false_positive_rate": bf.false_positive_rate,
                "current_fpr": bf.current_false_positive_rate(),
                "fill_ratio": bf.fill_ratio(),
                "memory_bytes": bloom_mem,
                "memory_formatted": format_memory_size(bloom_mem),
                "stats": bf.get_stats(),
            },
            "memory": {
                "bloom_bytes": bloom_mem,
                "bloom_formatted": format_memory_size(bloom_mem),
                "hashset_bytes": hash_mem,
                "hashset_formatted": format_memory_size(hash_mem),
                "savings_percentage": savings,
            },
            "mode": mode_result_serializable,
            "frequency_data": freq_data,
            "bit_snapshot": bit_snapshot,
            "fp_rate_curve": {
                "n_values": n_values,
                "fp_rates": fp_rates_curve,
                "expected_items": bf.expected_items,
                "target_fpr": bf.false_positive_rate,
            },
            "fill_history": bf.fill_history,
            "results": results[:1000],
            "total_results": len(results),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/download-metrics/{data_path:path}")
async def download_metrics(data_path: str, fp_rate: float = 0.01):
    try:
        if not os.path.exists(data_path):
            raise HTTPException(status_code=404, detail="Data file not found")

        urls = load_csv_data(data_path)
        unique_count = max(len(set(urls)), 1)
        bf = BloomFilter(expected_items=unique_count, false_positive_rate=fp_rate)

        ground_truth_set = set()
        true_positives = false_positives = true_negatives = false_negatives = 0

        for url in urls:
            bf_says_duplicate = bf.check(url)
            actually_duplicate = url in ground_truth_set

            if bf_says_duplicate and actually_duplicate:
                true_positives += 1
            elif bf_says_duplicate and not actually_duplicate:
                false_positives += 1
            elif not bf_says_duplicate and not actually_duplicate:
                true_negatives += 1
            else:
                false_negatives += 1

            if not actually_duplicate:
                bf.add(url)
            ground_truth_set.add(url)

        total = len(urls)
        bloom_mem = bf.memory_usage_bytes()
        hash_mem = estimate_hashset_memory(urls)
        savings = (1 - bloom_mem / hash_mem) * 100 if hash_mem else 0

        metrics = {
            "total": total,
            "unique": len(set(urls)),
            "target_fpr": fp_rate,
            "bits_m": bf.size,
            "hashes_k": bf.hash_count,
            "bloom_bytes": bloom_mem,
            "hashset_bytes": hash_mem,
            "savings_pct": savings,
            "true_positives": true_positives,
            "false_positives": false_positives,
            "true_negatives": true_negatives,
            "false_negatives": false_negatives,
            "accuracy": (true_positives + true_negatives) / total * 100 if total else 0,
            "precision": true_positives / (true_positives + false_positives) * 100 if (true_positives + false_positives) > 0 else 100,
            "recall": true_positives / (true_positives + false_negatives) * 100 if (true_positives + false_negatives) > 0 else 100,
            "f1_score": 0,
            "actual_fpr": false_positives / (false_positives + true_negatives) * 100 if (false_positives + true_negatives) > 0 else 0,
        }

        return metrics
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
