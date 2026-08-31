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

    The function first looks for the specified column name. If not found,
    it tries to auto-detect a column containing 'url' or 'link' in its name.

    Args:
        file_path (str): Path to the CSV file.
        url_column (str): Name of the column containing URLs.
                          Default is 'url'.

    Returns:
        List of URL strings.

    Raises:
        ValueError: If no URL column can be found.
    """
    df = pd.read_csv(file_path)

    # Try the specified column name first
    if url_column in df.columns:
        return df[url_column].astype(str).tolist()

    # Auto-detect: look for columns with 'url' or 'link' in the name
    for col in df.columns:
        if "url" in col.lower() or "link" in col.lower():
            return df[col].astype(str).tolist()

    # If nothing found, raise an error with helpful message
    raise ValueError(
        f"Could not find a URL column in the CSV file.\n"
        f"Available columns: {list(df.columns)}\n"
        f"Please ensure your CSV has a column named 'url' or 'link'."
    )


def load_uploaded_csv(uploaded_file, url_column: str = "url") -> list:
    """
    Load URLs from a Streamlit UploadedFile object.

    Args:
        uploaded_file: Streamlit UploadedFile object.
        url_column: Name of the column containing URLs.

    Returns:
        List of URL strings.
    """
    df = pd.read_csv(uploaded_file)

    # Try specified column
    if url_column in df.columns:
        return df[url_column].astype(str).tolist()

    # Auto-detect
    for col in df.columns:
        if "url" in col.lower() or "link" in col.lower():
            return df[col].astype(str).tolist()

    raise ValueError(
        f"Could not find a URL column.\n"
        f"Available columns: {list(df.columns)}"
    )


def format_memory_size(bytes_size: float) -> str:
    """
    Format a byte count into a human-readable string.

    Args:
        bytes_size: Size in bytes.

    Returns:
        Formatted string like '1.23 KB', '4.56 MB', etc.

    Example:
        >>> format_memory_size(1536)
        '1.50 KB'
        >>> format_memory_size(1048576)
        '1.00 MB'
    """
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes_size < 1024:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.2f} TB"


def estimate_hashset_memory(urls: list) -> int:
    """
    Estimate the memory usage of storing URLs in a Python set (HashSet).

    This is used to compare against the Bloom Filter's memory usage,
    demonstrating the space efficiency advantage of Bloom Filters.

    A Python set stores:
        - The set object overhead (~216 bytes)
        - Each string object (~50 bytes overhead + length of string)
        - Hash table entries (~8 bytes per entry)

    Args:
        urls: List of URL strings.

    Returns:
        Estimated memory in bytes.
    """
    unique_urls = set(urls)
    # Base set overhead
    memory = sys.getsizeof(unique_urls)
    # Add the size of each string stored
    for url in unique_urls:
        memory += sys.getsizeof(url)
    return memory
