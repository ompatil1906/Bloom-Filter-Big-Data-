"""
bloom_filter.py — Core Bloom Filter Implementation
====================================================

A Bloom Filter is a space-efficient probabilistic data structure used to
test whether an element is a member of a set.

Key Properties:
    - FALSE NEGATIVES are IMPOSSIBLE: If the filter says "not present",
      the element is GUARANTEED to not be in the set.
    - FALSE POSITIVES are POSSIBLE: If the filter says "present",
      there is a small probability it could be wrong.

How it works:
    1. Maintain a bit array of size 'm', initialized to all 0s.
    2. Use 'k' independent hash functions.
    3. To ADD an item: hash it with all k functions, set bits at those indices to 1.
    4. To CHECK an item: hash it with all k functions, check if ALL bits are 1.
       - If any bit is 0 → DEFINITELY NOT in the set.
       - If all bits are 1 → PROBABLY in the set (could be a false positive).

Optimal Parameters:
    - Bit array size:    m = -(n * ln(p)) / (ln2)²
    - Hash functions:    k = (m / n) * ln2
    where n = expected number of items, p = desired false positive rate.
"""

import math
import mmh3
from bitarray import bitarray


class BloomFilter:
    """
    A space-efficient probabilistic data structure for membership testing.
    Used to detect duplicate URLs in browser history.
    """

    def __init__(self, expected_items: int, false_positive_rate: float = 0.01):
        """
        Initialize the Bloom Filter with optimal parameters.

        Args:
            expected_items (int): Expected number of unique items to be inserted (n).
            false_positive_rate (float): Desired false positive probability (p).
                                         Default is 0.01 (1%).

        Example:
            >>> bf = BloomFilter(expected_items=1000, false_positive_rate=0.01)
            >>> bf.add("https://google.com")
            >>> bf.check("https://google.com")
            True
            >>> bf.check("https://never-added.com")
            False
        """
        if expected_items <= 0:
            raise ValueError("expected_items must be a positive integer.")
        if not (0 < false_positive_rate < 1):
            raise ValueError("false_positive_rate must be between 0 and 1 (exclusive).")

        self.expected_items = expected_items
        self.false_positive_rate = false_positive_rate
        self.items_added = 0

        # Calculate optimal bit array size: m = -(n * ln(p)) / (ln2)^2
        self.size = self._optimal_size(expected_items, false_positive_rate)

        # Calculate optimal number of hash functions: k = (m / n) * ln2
        self.hash_count = self._optimal_hash_count(self.size, expected_items)

        # Initialize bit array — all bits set to 0
        self.bit_array = bitarray(self.size)
        self.bit_array.setall(0)

        # Track fill ratio history for visualization
        self.fill_history = []

    @staticmethod
    def _optimal_size(n: int, p: float) -> int:
        """
        Calculate the optimal bit array size.

        Formula: m = -(n * ln(p)) / (ln2)²

        Args:
            n: Expected number of elements.
            p: Desired false positive rate.

        Returns:
            Optimal bit array size (m).
        """
        m = -(n * math.log(p)) / (math.log(2) ** 2)
        return max(int(m), 1)  # Ensure at least 1 bit

    @staticmethod
    def _optimal_hash_count(m: int, n: int) -> int:
        """
        Calculate the optimal number of hash functions.

        Formula: k = (m / n) * ln2

        Args:
            m: Bit array size.
            n: Expected number of elements.

        Returns:
            Optimal number of hash functions (k).
        """
        k = (m / n) * math.log(2)
        return max(int(k), 1)  # Ensure at least 1 hash function

    def _get_hash_indices(self, item: str) -> list:
        """
        Generate k hash indices for the given item using MurmurHash3.

        Each hash function uses a different seed to produce independent indices.
        The result is taken modulo the bit array size to get valid indices.

        Args:
            item: The string item to hash (e.g., a URL).

        Returns:
            List of k indices into the bit array.
        """
        indices = []
        for seed in range(self.hash_count):
            # mmh3.hash() returns a 32-bit signed integer
            # We use different seeds (0, 1, 2, ..., k-1) for independent hashes
            hash_value = mmh3.hash(item, seed)
            index = hash_value % self.size
            indices.append(index)
        return indices

    def add(self, item: str) -> list:
        """
        Add an item to the Bloom Filter.

        Sets the bits at all k hash positions to 1.

        Args:
            item: The string item to add (e.g., a URL).

        Returns:
            List of bit indices that were set to 1.
        """
        indices = self._get_hash_indices(item)
        for idx in indices:
            self.bit_array[idx] = 1
        self.items_added += 1

        # Record fill ratio for visualization
        if self.items_added % max(1, self.expected_items // 100) == 0:
            self.fill_history.append({
                "items": self.items_added,
                "fill_ratio": self.fill_ratio(),
            })

        return indices

    def check(self, item: str) -> bool:
        """
        Check if an item might be in the set.

        Checks if ALL bits at the k hash positions are 1.

        Args:
            item: The string item to check.

        Returns:
            False → The item is DEFINITELY NOT in the set.
            True  → The item is PROBABLY in the set (may be a false positive).
        """
        indices = self._get_hash_indices(item)
        return all(self.bit_array[idx] for idx in indices)

    def current_false_positive_rate(self) -> float:
        """
        Calculate the current estimated false positive rate.

        Formula: P ≈ (1 - e^(-k*n/m))^k

        Returns:
            Estimated false positive probability based on current state.
        """
        n = self.items_added
        m = self.size
        k = self.hash_count
        if n == 0:
            return 0.0
        return (1 - math.exp(-k * n / m)) ** k

    def fill_ratio(self) -> float:
        """
        Return the fraction of bits set to 1 in the bit array.

        A higher fill ratio means more collisions and higher false positive rate.

        Returns:
            Float between 0.0 and 1.0.
        """
        return self.bit_array.count(1) / self.size if self.size > 0 else 0.0

    def memory_usage_bytes(self) -> int:
        """
        Return the memory usage of the bit array in bytes.

        Returns:
            Number of bytes used by the bit array.
        """
        return math.ceil(self.size / 8)

    def get_stats(self) -> dict:
        """
        Return a comprehensive dictionary of Bloom Filter statistics.

        Useful for displaying in the GUI and for debugging.

        Returns:
            Dictionary with all key metrics.
        """
        return {
            "Bit Array Size (m)": f"{self.size:,}",
            "Hash Functions (k)": self.hash_count,
            "Items Added (n)": f"{self.items_added:,}",
            "Expected Items": f"{self.expected_items:,}",
            "Target FP Rate": f"{self.false_positive_rate:.4%}",
            "Current FP Rate": f"{self.current_false_positive_rate():.4%}",
            "Fill Ratio": f"{self.fill_ratio():.2%}",
            "Memory Usage": f"{self.memory_usage_bytes() / 1024:.2f} KB",
        }

    def get_bit_array_snapshot(self, max_length: int = 500) -> list:
        """
        Get a snapshot of the bit array for visualization.

        If the array is larger than max_length, returns a downsampled version.

        Args:
            max_length: Maximum number of bits to return.

        Returns:
            List of 0s and 1s representing the bit array state.
        """
        if self.size <= max_length:
            return self.bit_array.tolist()

        # Downsample: take evenly spaced samples
        step = self.size / max_length
        return [self.bit_array[int(i * step)] for i in range(max_length)]
