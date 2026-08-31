"""
data_generator.py — Synthetic Browser History Generator
========================================================

Generates realistic synthetic browser history data with controlled duplicates.

Why synthetic data?
    - Real browser history contains private/sensitive information.
    - Synthetic data lets us control the exact duplicate ratio for testing.
    - We know the "ground truth" — which URLs are duplicates — so we can
      measure the Bloom Filter's accuracy.

The generator creates a CSV with columns:
    - url: The visited URL
    - visit_time: Unix timestamp of the visit
    - visit_date: Human-readable date/time string

Duplicate distribution follows a power-law pattern:
    - A small set of "popular" URLs (top 10%) appear very frequently
    - The remaining URLs appear less often
    This mimics real browsing behavior where users revisit the same
    few sites (Google, YouTube, etc.) repeatedly.
"""

import csv
import os
import random
from datetime import datetime, timedelta


# Pool of realistic domains commonly found in browser history
DOMAINS = [
    "google.com", "youtube.com", "facebook.com", "twitter.com",
    "github.com", "stackoverflow.com", "reddit.com", "amazon.com",
    "wikipedia.org", "linkedin.com", "netflix.com", "medium.com",
    "instagram.com", "whatsapp.com", "zoom.us", "microsoft.com",
    "apple.com", "yahoo.com", "bing.com", "quora.com",
    "coursera.org", "udemy.com", "geeksforgeeks.org", "w3schools.com",
    "kaggle.com", "hackerrank.com", "leetcode.com", "codechef.com",
    "chatgpt.com", "notion.so", "figma.com", "canva.com",
    "spotify.com", "twitch.tv", "discord.com", "slack.com",
    "drive.google.com", "docs.google.com", "mail.google.com",
    "maps.google.com", "translate.google.com", "news.google.com",
]

# Realistic URL paths
PATHS = [
    "/", "/search", "/login", "/dashboard", "/profile",
    "/settings", "/about", "/contact", "/help", "/docs",
    "/api", "/blog", "/news", "/trending", "/explore",
    "/notifications", "/messages", "/feed", "/home", "/watch",
    "/results", "/video", "/channel", "/playlist", "/stories",
    "/post", "/article", "/question", "/answer", "/submit",
]

# Query parameters to add variety
QUERY_PARAMS = [
    "", "", "", "",  # Most URLs have no query params
    "?q=python", "?q=bloom+filter", "?q=big+data",
    "?page=1", "?page=2", "?ref=home", "?tab=trending",
    "?id=12345", "?v=dQw4w9WgXcQ", "?sort=newest",
]


def generate_unique_url_pool(num_urls: int) -> list:
    """
    Generate a pool of unique, realistic-looking URLs.

    Args:
        num_urls: Number of unique URLs to generate.

    Returns:
        List of unique URL strings.
    """
    unique_urls = set()
    while len(unique_urls) < num_urls:
        domain = random.choice(DOMAINS)
        path = random.choice(PATHS)
        query = random.choice(QUERY_PARAMS)
        url = f"https://www.{domain}{path}{query}"
        unique_urls.add(url)
    return list(unique_urls)


def generate_browser_history(
    num_entries: int = 10000,
    num_unique_urls: int = 500,
    duplicate_ratio: float = 0.6,
    output_path: str = "data/browser_history.csv",
) -> tuple:
    """
    Generate a synthetic browser history CSV file.

    The generated data mimics real browsing patterns:
    - A small number of "popular" sites are visited very frequently.
    - The remaining sites are visited less often.
    - Visits are spread over a 30-day period.

    The duplicate ratio is derived deterministically: every unique URL
    appears exactly once, and the remaining (num_entries - num_unique_urls)
    entries are repeats of popular URLs. The resulting duplicate rate equals
    (num_entries - num_unique_urls) / num_entries.

    Args:
        num_entries (int): Total number of history entries to generate.
        num_unique_urls (int): Number of distinct URLs that will appear in the
                                data (each appears at least once).
        duplicate_ratio (float): Kept for backward compatibility with the API
                                 but no longer controls generation directly;
                                 duplicates are derived from num_entries and
                                 num_unique_urls.
        output_path (str): Path to save the generated CSV file.

    Returns:
        Tuple of (output_path, summary_dict) where summary_dict contains
        statistics about the generated data.
    """
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".",
                exist_ok=True)

    # Guard against impossible inputs: we need at least as many entries as unique URLs
    # so that every unique URL can appear once.
    if num_entries < num_unique_urls:
        num_unique_urls = num_entries

    # Generate exactly `num_unique_urls` distinct URLs that WILL appear in the data.
    # This makes `unique_in_data` predictable and matching the user's input (not a
    # random subset of a larger pool). Every unique URL appears once as a "first seen".
    unique_urls = generate_unique_url_pool(num_unique_urls)

    # Designate "popular" URLs — top 10% get the bulk of the duplicate traffic.
    popular_count = max(1, int(num_unique_urls * 0.1))
    popular_urls = unique_urls[:popular_count]

    # Number of duplicate (repeat) visits: the remaining entries beyond the unique ones.
    num_duplicates = num_entries - num_unique_urls

    # History starts with every unique URL appearing exactly once (guaranteed "first seen").
    history = []
    for url in unique_urls:
        history.append({"url": url, "visit_time": 0, "visit_date": ""})

    # Generate the duplicate visits from the popular subset with power-law weighting.
    if popular_urls:
        weights = [2 ** (popular_count - j) for j in range(popular_count)]
    else:
        weights = [1] * num_unique_urls
        popular_urls = unique_urls

    for _ in range(num_duplicates):
        url = random.choices(popular_urls, weights=weights, k=1)[0]
        history.append({"url": url, "visit_time": 0, "visit_date": ""})

    # Sort into a random chronological order and stamp real timestamps over a 30-day window.
    random.shuffle(history)
    base_time = datetime.now() - timedelta(days=30)
    for row in history:
        seconds_offset = random.randint(0, 30 * 24 * 3600)
        visit_time = base_time + timedelta(seconds=seconds_offset)
        row["visit_time"] = int(visit_time.timestamp())
        row["visit_date"] = visit_time.strftime("%Y-%m-%d %H:%M:%S")

    # Sort by visit time (chronological order)
    history.sort(key=lambda x: x["visit_time"])

    # Write to CSV
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["url", "visit_time", "visit_date"])
        writer.writeheader()
        writer.writerows(history)

    # Calculate summary statistics — now consistent with the requested inputs.
    # Calculate summary statistics
    all_urls = [entry["url"] for entry in history]
    unique_in_data = len(set(all_urls))
    summary = {
        "total_entries": num_entries,
        "unique_urls_in_pool": num_unique_urls,
        "unique_urls_in_data": unique_in_data,
        "duplicate_entries": num_entries - unique_in_data,
        "actual_duplicate_ratio": (num_entries - unique_in_data) / num_entries,
        "output_path": output_path,
    }

    return output_path, summary


if __name__ == "__main__":
    # Quick test — generate a small dataset
    path, stats = generate_browser_history(
        num_entries=1000,
        num_unique_urls=100,
        duplicate_ratio=0.6,
        output_path="data/browser_history.csv",
    )
    print(f"Generated dataset at: {path}")
    print("Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
