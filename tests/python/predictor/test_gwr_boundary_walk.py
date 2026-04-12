"""Tests for the exact divisor-field boundary walk shell."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from sympy import nextprime


ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = ROOT / "src" / "python"
RECURSIVE_WALK_PATH = ROOT / "benchmarks" / "python" / "predictor" / "gwr_dni_recursive_walk.py"

if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from z_band_prime_predictor import gwr_next_gap_profile, gwr_next_prime, next_prime_after


def load_recursive_walk_module():
    """Load the recursive walk script from its file path."""
    spec = importlib.util.spec_from_file_location("gwr_dni_recursive_walk", RECURSIVE_WALK_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load gwr_dni_recursive_walk module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_gwr_next_gap_profile_matches_exact_recursive_walk_samples():
    """The standalone profile should match the existing exact unbounded oracle."""
    module = load_recursive_walk_module()

    for q in (7, 11, 23, 29, 101, 229433):
        expected = module.exact_next_gap_profile(q)
        observed = gwr_next_gap_profile(q)

        assert observed["current_prime"] == q
        assert observed["next_prime"] == expected["next_prime"]
        assert observed["gap_boundary_offset"] == expected["gap_boundary_offset"]
        assert observed["winner_d"] == expected["next_dmin"]
        assert observed["winner_offset"] == expected["next_peak_offset"]


def test_gwr_next_gap_profile_handles_empty_gap_after_two():
    """The gap after 2 should return the boundary with no interior winner."""
    profile = gwr_next_gap_profile(2)

    assert profile["current_prime"] == 2
    assert profile["next_prime"] == 3
    assert profile["gap_boundary_offset"] == 1
    assert profile["winner_d"] is None
    assert profile["winner_offset"] is None


def test_gwr_next_prime_matches_true_successor_on_small_prime_anchors():
    """Prime-anchor scans should recover the immediate next prime exactly."""
    for q in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 97):
        assert gwr_next_prime(q) == int(nextprime(q))


def test_next_prime_after_returns_first_prime_after_composite_input():
    """Composite anchors should return the first prime after n without skipping one."""
    cases = {
        14: 17,
        15: 17,
        16: 17,
        18: 19,
        20: 23,
        24: 29,
    }

    for n, expected in cases.items():
        assert next_prime_after(n) == expected

    assert next_prime_after(17) == 19
    assert next_prime_after(19) == 23
