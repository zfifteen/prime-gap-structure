"""Tests for the dominant d=4 arrival validation runner."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "benchmarks" / "python" / "gap_ridge" / "gwr_d4_arrival_validation.py"


def load_module():
    """Load the benchmark runner as a module."""
    spec = importlib.util.spec_from_file_location("gwr_d4_arrival_validation", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load gwr_d4_arrival_validation module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_small_exact_interval_supports_the_broad_first_d4_reduction():
    """A small exact surface should already satisfy the broad d=4 reduction."""
    module = load_module()
    row = module.validate_d4_arrival_on_interval(
        lo=2,
        hi=10_001,
        scale=10_000,
        window_mode="exact",
        max_examples=5,
    )

    assert row["d4_winner_gap_count"] > 0
    assert row["d4_winner_with_interior_square_count"] == 0
    assert row["d4_winner_equals_first_d4_count"] == row["d4_winner_gap_count"]
    assert (
        row["no_square_has_d4_first_d4_winner_count"]
        == row["no_square_has_d4_gap_count"]
    )


def test_small_exact_interval_already_falsifies_the_semiprime_only_version():
    """The stricter semiprime-only version already fails on a small exact range."""
    module = load_module()
    row = module.validate_d4_arrival_on_interval(
        lo=2,
        hi=10_001,
        scale=10_000,
        window_mode="exact",
        max_examples=5,
    )

    assert row["d4_winner_prime_cube_count"] == 1
    assert row["d4_winner_semiprime_count"] + row["d4_winner_prime_cube_count"] == row[
        "d4_winner_gap_count"
    ]
    examples = row["d4_winner_prime_cube_examples"]
    assert isinstance(examples, list)
    assert examples[0]["winner_n"] == 6859
