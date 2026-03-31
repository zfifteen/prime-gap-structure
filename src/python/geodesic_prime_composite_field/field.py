"""Exact composite-field helpers used by prime-gap studies."""

from __future__ import annotations

import math

import numpy as np


def _small_primes(limit: int) -> np.ndarray:
    """Return every prime up to one small sieve limit."""
    sieve = np.ones(limit + 1, dtype=bool)
    sieve[:2] = False
    root = int(limit ** 0.5)
    for prime in range(2, root + 1):
        if sieve[prime]:
            sieve[prime * prime : limit + 1 : prime] = False
    return np.flatnonzero(sieve)


def divisor_counts_segment(lo: int, hi: int) -> np.ndarray:
    """Compute exact divisor counts on one contiguous natural-number interval."""
    if lo < 1:
        raise ValueError("lo must be at least 1")
    if hi <= lo:
        raise ValueError("hi must be larger than lo")

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
