#!/usr/bin/env python3
"""Thin benchmark-facing wrapper around the gap-ridge source module."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = ROOT / "src" / "python"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from geodesic_prime_gap_ridge import (  # noqa: F401
    DEFAULT_FULL_LIMITS,
    DEFAULT_RANDOM_SEED,
    DEFAULT_WINDOW_COUNT,
    DEFAULT_WINDOW_SCALES,
    DEFAULT_WINDOW_SIZE,
    GapEdgeRunSummary,
    build_even_window_starts,
    build_seeded_window_starts,
    run_exact_limit,
    run_window_sweep,
)


__all__ = [
    "DEFAULT_FULL_LIMITS",
    "DEFAULT_RANDOM_SEED",
    "DEFAULT_WINDOW_COUNT",
    "DEFAULT_WINDOW_SCALES",
    "DEFAULT_WINDOW_SIZE",
    "GapEdgeRunSummary",
    "build_even_window_starts",
    "build_seeded_window_starts",
    "run_exact_limit",
    "run_window_sweep",
]
