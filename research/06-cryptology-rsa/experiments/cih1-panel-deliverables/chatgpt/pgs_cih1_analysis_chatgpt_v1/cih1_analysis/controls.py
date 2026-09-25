"""Deterministic uniform-band controls."""
from __future__ import annotations
import random
import statistics

def sample_uniform_distances(lo, hi, p, q, k, rng):
    if lo > hi:
        raise ValueError("invalid_band")
    vals = []
    for _ in range(k):
        u = rng.randint(lo, hi)
        vals.append(min(abs(u-p), abs(u-q)))
    return vals

def summarize_control(distances):
    return {
        "median": statistics.median(distances),
        "mean": statistics.fmean(distances),
    }
