"""Tests for the DNI-to-RH bridge helpers."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = ROOT / "src" / "python"

if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from geodesic_prime_rh_bridge import (
    build_bridge_rows,
    divisor_counts_up_to,
    evaluate_analytic_bridge,
    evaluate_partial_sum_bridge,
    mangoldt_values_up_to,
)


def test_small_divisor_counts_match_known_values():
    """The divisor-count table should agree with the exact small-n sequence."""
    counts = divisor_counts_up_to(10)

    assert counts == (0, 1, 2, 2, 3, 2, 4, 2, 4, 3, 4)


def test_small_mangoldt_values_match_prime_power_support():
    """Von Mangoldt should be nonzero exactly on prime powers in the small table."""
    values = mangoldt_values_up_to(10)

    assert values[1] == 0.0
    assert values[2] == pytest.approx(0.6931471805599453)
    assert values[3] == pytest.approx(1.0986122886681098)
    assert values[4] == pytest.approx(0.6931471805599453)
    assert values[5] == pytest.approx(1.6094379124341003)
    assert values[6] == 0.0
    assert values[8] == pytest.approx(0.6931471805599453)
    assert values[9] == pytest.approx(1.0986122886681098)
    assert values[10] == 0.0


def test_bridge_rows_recover_scaled_curvature_coefficients():
    """The coefficient bridge should match the scaled normalization-load layer term by term."""
    rows = build_bridge_rows(128)

    assert max(row.abs_error for row in rows) < 1e-12
    assert rows[0].scaled_bridge_coefficient == 0.0
    assert rows[1].mangoldt > 0.0
    assert rows[5].mangoldt == 0.0


def test_analytic_bridge_matches_negative_zeta_log_derivative():
    """The continued DNI ratio should equal `-zeta'/zeta` numerically."""
    evaluation = evaluate_analytic_bridge(2.0, dps=80)

    assert evaluation.abs_error < 1e-30


def test_partial_sum_bridge_tracks_the_analytic_detector():
    """Direct coefficient-side partial sums should approach the same analytic target."""
    evaluation = evaluate_partial_sum_bridge(2.0, terms=1000, dps=80)

    assert evaluation.normalized_ratio_error < 0.012
    assert evaluation.mangoldt_series_error < 0.002
