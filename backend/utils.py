"""
utils.py — Helper Utilities
=============================

Shared utility functions used across the project:
    - CSV data loading with auto-detection of URL columns.
    - Memory size formatting for display.
    - HashSet memory estimation for comparison with Bloom Filter.
"""

import sys
import pandas as pd


def load_csv_data(file_path: str, url_column: str = "url") -> list:
    """
    Load URLs from a CSV file, with auto-detection of the URL column.
    """
    df = pd.read_csv(file_path)

    if url_column in df.columns:
        return df[url_column].astype(str).tolist()

    for col in df.columns:
        if "url" in col.lower() or "link" in col.lower():
            return df[col].astype(str).tolist()

    raise ValueError(
        f"Could not find a URL column in the CSV file.\n"
        f"Available columns: {list(df.columns)}\n"
        f"Please ensure your CSV has a column named 'url' or 'link'."
    )


def load_uploaded_csv_file(file_content: bytes, url_column: str = "url") -> list:
    """
    Load URLs from uploaded file content (bytes).
    """
    import io
    df = pd.read_csv(io.BytesIO(file_content))

    if url_column in df.columns:
        return df[url_column].astype(str).tolist()

    for col in df.columns:
        if "url" in col.lower() or "link" in col.lower():
            return df[col].astype(str).tolist()

    raise ValueError(
        f"Could not find a URL column.\n"
        f"Available columns: {list(df.columns)}"
    )


def load_uploaded_csv_to_df(file_content: bytes, url_column: str = "url"):
    """
    Load uploaded CSV content as a DataFrame and return it along with URLs.
    """
    import io
    df = pd.read_csv(io.BytesIO(file_content))

    urls = None
    if url_column in df.columns:
        urls = df[url_column].astype(str).tolist()
    else:
        for col in df.columns:
            if "url" in col.lower() or "link" in col.lower():
                urls = df[col].astype(str).tolist()
                break

    if urls is None:
        raise ValueError(
            f"Could not find a URL column.\n"
            f"Available columns: {list(df.columns)}"
        )

    return urls, df


def format_memory_size(bytes_size: float) -> str:
    """
    Format a byte count into a human-readable string.
    """
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes_size < 1024:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.2f} TB"


def estimate_hashset_memory(urls: list) -> int:
    """
    Estimate the memory usage of storing URLs in a Python set (HashSet).
    """
    unique_urls = set(urls)
    memory = sys.getsizeof(unique_urls)
    for url in unique_urls:
        memory += sys.getsizeof(url)
    return memory
