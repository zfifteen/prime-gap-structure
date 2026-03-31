#!/usr/bin/env python3
"""Shared helpers for exact raw composite Z gap-edge reproduction runs."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Sequence

import numpy as np


DEFAULT_FULL_LIMITS = (1_000_000, 10_000_000)
DEFAULT_WINDOW_SCALES = (100_000_000, 1_000_000_000, 10_000_000_000)
DEFAULT_WINDOW_SIZE = 10_000_000
DEFAULT_WINDOW_COUNT = 10
DEFAULT_RANDOM_SEED = 20260331


@dataclass(frozen=True)
class GapEdgeRunSummary:
    """One exact raw-Z gap-edge run summary."""

    scale: int
    gap_count: int
    observed_edge2_share: float
    baseline_edge2_share: float
    edge2_enrichment: float
    observed_d4_share: float
    baseline_d4_share: float
    d4_enrichment: float
    left_share: float
    right_share: float
    center_share: float
    window_mode: str
    window_size: int | None = None
    sampled_gap_count: int | None = None
    approximate_gap_count: int | None = None
    seed: int | None = None

    def to_dict(self) -> dict[str, int | float | str | None]:
        """Return a JSON-ready mapping."""
        return asdict(self)


def run_exact_limit(limit: int) -> GapEdgeRunSummary:
    """Run the full exact raw-Z gap-edge study up to one natural-number limit."""
    if limit < 5:
        raise ValueError("limit must be at least 5")

    return _analyze_interval(
        lo=2,
        hi=limit + 1,
        scale=limit,
        window_mode="exact",
    )


def build_even_window_starts(
    scale: int,
    window_size: int,
    window_count: int,
) -> list[int]:
    """Return evenly spaced deterministic segment starts."""
    if scale < window_size:
        raise ValueError("scale must be at least as large as window_size")
    if window_size < 5:
        raise ValueError("window_size must be at least 5")
    if window_count < 1:
        raise ValueError("window_count must be at least 1")

    if window_count == 1:
        return [2]

    max_start_offset = scale - window_size
    return [
        2 + round(index * max_start_offset / (window_count - 1))
        for index in range(window_count)
    ]


def build_seeded_window_starts(
    scale: int,
    window_size: int,
    window_count: int,
    seed: int,
) -> list[int]:
    """Return deterministic fixed-seed segment starts."""
    if scale < window_size:
        raise ValueError("scale must be at least as large as window_size")
    if window_size < 5:
        raise ValueError("window_size must be at least 5")
    if window_count < 1:
        raise ValueError("window_count must be at least 1")

    if window_count == 1:
        return [2]

    rng = np.random.default_rng(seed)
    max_start = scale - window_size
    starts = rng.integers(2, max_start + 1, size=window_count, endpoint=False)
    return sorted(int(start) for start in starts)


def run_window_sweep(
    scales: Sequence[int],
    window_size: int,
    starts_by_scale: dict[int, Sequence[int]],
    window_mode: str,
    seed: int | None = None,
) -> list[GapEdgeRunSummary]:
    """Run the exact raw-Z gap-edge study over preselected natural-number windows."""
    rows: list[GapEdgeRunSummary] = []
    for scale in scales:
        starts = list(starts_by_scale[scale])
        interval_rows = [
            _analyze_interval(
                lo=start,
                hi=start + window_size,
                scale=scale,
                window_mode=window_mode,
                window_size=window_size,
                seed=seed,
            )
            for start in starts
        ]

        sampled_gap_count = sum(row.gap_count for row in interval_rows)
        coverage = len(starts) * window_size / scale
        approximate_gap_count = round(sampled_gap_count / coverage)

        observed_edge2_share = (
            sum(row.observed_edge2_share * row.gap_count for row in interval_rows)
            / sampled_gap_count
        )
        baseline_edge2_share = (
            sum(row.baseline_edge2_share * row.gap_count for row in interval_rows)
            / sampled_gap_count
        )
        observed_d4_share = (
            sum(row.observed_d4_share * row.gap_count for row in interval_rows)
            / sampled_gap_count
        )
        baseline_d4_share = (
            sum(row.baseline_d4_share * row.gap_count for row in interval_rows)
            / sampled_gap_count
        )
        left_share = (
            sum(row.left_share * row.gap_count for row in interval_rows)
            / sampled_gap_count
        )
        right_share = (
            sum(row.right_share * row.gap_count for row in interval_rows)
            / sampled_gap_count
        )
        center_share = (
            sum(row.center_share * row.gap_count for row in interval_rows)
            / sampled_gap_count
        )

        rows.append(
            GapEdgeRunSummary(
                scale=scale,
                gap_count=sampled_gap_count,
                observed_edge2_share=observed_edge2_share,
                baseline_edge2_share=baseline_edge2_share,
                edge2_enrichment=observed_edge2_share / baseline_edge2_share,
                observed_d4_share=observed_d4_share,
                baseline_d4_share=baseline_d4_share,
                d4_enrichment=observed_d4_share / baseline_d4_share,
                left_share=left_share,
                right_share=right_share,
                center_share=center_share,
                window_mode=window_mode,
                window_size=window_size,
                sampled_gap_count=sampled_gap_count,
                approximate_gap_count=approximate_gap_count,
                seed=seed,
            )
        )

    return rows


def _small_primes(limit: int) -> np.ndarray:
    """Return every prime up to one small sieve limit."""
    sieve = np.ones(limit + 1, dtype=bool)
    sieve[:2] = False
    root = int(limit ** 0.5)
    for prime in range(2, root + 1):
        if sieve[prime]:
            sieve[prime * prime : limit + 1 : prime] = False
    return np.flatnonzero(sieve)


def _divisor_counts_segment(lo: int, hi: int) -> np.ndarray:
    """Compute exact divisor counts on one contiguous natural-number interval."""
    size = hi - lo
    values = np.arange(lo, hi, dtype=np.int64)
    residual = values.copy()
    divisor_count = np.ones(size, dtype=np.uint16)
    small_primes = _small_primes(int(math.isqrt(hi - 1)))

    for prime in small_primes:
        start = ((lo + prime - 1) // prime) * prime
        indices = np.arange(start - lo, size, prime, dtype=np.int64)
        if indices.size == 0:
            continue

        subvalues = residual[indices].copy()
        exponent = np.zeros(indices.size, dtype=np.uint8)
        while True:
            mask = (subvalues % prime) == 0
            if not mask.any():
                break
            subvalues[mask] //= prime
            exponent[mask] += 1

        residual[indices] = subvalues
        nonzero = exponent != 0
        if nonzero.any():
            divisor_count[indices[nonzero]] *= (exponent[nonzero] + 1).astype(np.uint16)

    divisor_count[residual > 1] *= 2
    if lo <= 1 < hi:
        divisor_count[1 - lo] = 1
    return divisor_count


def _analyze_interval(
    lo: int,
    hi: int,
    scale: int,
    window_mode: str,
    window_size: int | None = None,
    seed: int | None = None,
) -> GapEdgeRunSummary:
    """Analyze one exact natural-number interval under the raw-Z gap-edge metric."""
    divisor_count = _divisor_counts_segment(lo, hi)
    values = np.arange(lo, hi, dtype=np.int64)
    primes = values[divisor_count == 2]
    log_values = np.log(values.astype(np.float64))

    gap_count = 0
    observed_edge2 = 0
    baseline_edge2_sum = 0.0
    observed_d4 = 0
    baseline_d4_sum = 0.0
    observed_left = 0
    observed_right = 0
    observed_center = 0

    for left_prime, right_prime in zip(primes[:-1], primes[1:]):
        gap = int(right_prime - left_prime)
        if gap < 4:
            continue

        left_index = int(left_prime - lo + 1)
        right_index = int(right_prime - lo)
        gap_divisors = divisor_count[left_index:right_index]
        scores = (1.0 - gap_divisors.astype(np.float64) / 2.0) * log_values[left_index:right_index]
        best_offset = int(np.argmax(scores)) + 1
        edge_distance = min(best_offset, gap - best_offset)

        gap_count += 1
        observed_edge2 += int(edge_distance == 2)
        observed_d4 += int(gap_divisors[best_offset - 1] == 4)
        if best_offset < gap / 2:
            observed_left += 1
        elif best_offset > gap / 2:
            observed_right += 1
        else:
            observed_center += 1

        edge2_positions = 1 if gap == 4 else 2
        baseline_edge2_sum += edge2_positions / (gap - 1)
        baseline_d4_sum += float(np.count_nonzero(gap_divisors == 4)) / float(gap - 1)

    observed_edge2_share = observed_edge2 / gap_count
    baseline_edge2_share = baseline_edge2_sum / gap_count
    observed_d4_share = observed_d4 / gap_count
    baseline_d4_share = baseline_d4_sum / gap_count

    interval_size = hi - lo
    approximate_gap_count = gap_count if lo == 2 and hi == scale + 1 else None

    return GapEdgeRunSummary(
        scale=scale,
        gap_count=gap_count,
        observed_edge2_share=observed_edge2_share,
        baseline_edge2_share=baseline_edge2_share,
        edge2_enrichment=observed_edge2_share / baseline_edge2_share,
        observed_d4_share=observed_d4_share,
        baseline_d4_share=baseline_d4_share,
        d4_enrichment=observed_d4_share / baseline_d4_share,
        left_share=observed_left / gap_count,
        right_share=observed_right / gap_count,
        center_share=observed_center / gap_count,
        window_mode=window_mode,
        window_size=window_size or interval_size,
        sampled_gap_count=gap_count,
        approximate_gap_count=approximate_gap_count,
        seed=seed,
    )
