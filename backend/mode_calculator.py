"""
mode_calculator.py — Frequency Analysis & Mode Calculation
===========================================================

In statistics, the MODE is the value that appears most frequently in a dataset.

For browser history:
    - Each URL visit is a data point.
    - The MODE is the URL visited the most number of times.
    - If multiple URLs share the highest frequency, the data is "multimodal".

This module provides:
    1. Mode calculation — identify the most frequently visited URL(s).
    2. Frequency distribution — count visits per URL.
    3. Summary statistics — total entries, unique URLs, duplicate counts, etc.

Example:
    URLs = ["google.com", "youtube.com", "google.com", "google.com", "youtube.com"]
    Frequencies: google.com → 3, youtube.com → 2
    Mode: google.com (appears 3 times — the highest frequency)
"""

from collections import Counter


def calculate_mode(urls: list) -> dict:
    """
    Calculate the mode (most frequently visited URL) and full frequency analysis.

    The mode is the statistical measure of central tendency that identifies
    the most common value(s) in a dataset. In the context of browser history,
    it tells us which URL was visited most often.

    Args:
        urls (list): List of URL strings from browser history.
                     Can contain duplicates.

    Returns:
        dict: A dictionary containing:
            - mode_url (str): The single most frequently visited URL.
            - mode_count (int): How many times the mode URL was visited.
            - all_modes (list): All URLs tied for the highest frequency.
                                Each entry is a (url, count) tuple.
            - is_multimodal (bool): True if multiple URLs share the
                                     highest visit count.
            - frequency_distribution (Counter): Full frequency count for
                                                 every unique URL.
            - top_10 (list): Top 10 most visited URLs as (url, count) tuples.
            - total_urls (int): Total number of URL entries (including duplicates).
            - unique_urls (int): Count of distinct/unique URLs.
            - duplicate_count (int): Number of duplicate entries
                                      (total - unique).
            - duplicate_percentage (float): Percentage of entries that are
                                             duplicates.

    Example:
        >>> urls = ["a.com", "b.com", "a.com", "c.com", "a.com", "b.com"]
        >>> result = calculate_mode(urls)
        >>> result["mode_url"]
        'a.com'
        >>> result["mode_count"]
        3
        >>> result["unique_urls"]
        3
        >>> result["duplicate_count"]
        3
    """
    if not urls:
        return {
            "mode_url": "N/A",
            "mode_count": 0,
            "all_modes": [],
            "is_multimodal": False,
            "frequency_distribution": Counter(),
            "top_10": [],
            "total_urls": 0,
            "unique_urls": 0,
            "duplicate_count": 0,
            "duplicate_percentage": 0.0,
        }

    # Count the frequency of each URL
    # Counter is a dict subclass: {"url": count, ...}
    counter = Counter(urls)

    # most_common() returns a list sorted by frequency: [(url, count), ...]
    most_common = counter.most_common()

    # The mode is the first element (highest frequency)
    mode_url, mode_count = most_common[0]

    # Check for multiple modes (multimodal data)
    # Multiple URLs might have the same highest frequency
    all_modes = [(url, count) for url, count in most_common if count == mode_count]

    # Calculate duplicate statistics
    total = len(urls)
    unique = len(counter)
    duplicates = total - unique

    return {
        "mode_url": mode_url,
        "mode_count": mode_count,
        "all_modes": all_modes,
        "is_multimodal": len(all_modes) > 1,
        "frequency_distribution": counter,
        "top_10": most_common[:10],
        "total_urls": total,
        "unique_urls": unique,
        "duplicate_count": duplicates,
        "duplicate_percentage": (duplicates / total * 100) if total > 0 else 0.0,
    }


def get_frequency_dataframe(counter: Counter, top_n: int = 20):
    """
    Convert a Counter to a list of dicts suitable for creating a DataFrame.

    Args:
        counter: Counter object with URL frequencies.
        top_n: Number of top URLs to include.

    Returns:
        List of dicts with 'url' and 'visits' keys.
    """
    return [
        {"url": url, "visits": count}
        for url, count in counter.most_common(top_n)
    ]
