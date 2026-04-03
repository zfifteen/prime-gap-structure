"""Exact raw-Z gap-ridge analysis helpers."""

from .runs import (
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
