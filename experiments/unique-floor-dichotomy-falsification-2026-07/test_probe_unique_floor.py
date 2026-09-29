#!/usr/bin/env python3
"""Local unit checks for unique-floor dichotomy probe."""

from __future__ import annotations

from probe_unique_floor import analyze_gap, divisor_counts, run_probe, u1_ceiling


def test_u1_ceiling_schedule():
    assert u1_ceiling(2_000_000, 100) == 40
    assert u1_ceiling(5_000_000, 100) == 40
    assert u1_ceiling(10_000_000, 10**6) >= 48


def test_analyze_gap_fields():
    tau = divisor_counts(100)
    row = analyze_gap(23, 29, tau)
    assert row is not None
    assert row["g"] == 6
    assert row["L_size"] >= 1
    assert row["unique"] == (row["L_size"] == 1)


def test_run_probe_smoke():
    result = run_probe(p_max=800, p_min=11)
    assert result["counts"]["gaps_nonempty"] > 0
    assert result["status_language"] == "measured_on_regime_only"
    blob = str(result).lower()
    assert "validated" not in blob
    assert "verified" not in blob


def test_outcomes_keys():
    result = run_probe(p_max=500, p_min=11)
    for k in (
        "U1_unique_m4_short_gap",
        "U2_long_m4_multi_rate",
        "U3_unique_high_floor_short",
        "U4_square_long_unique_contrast",
    ):
        assert k in result["outcomes"]


def test_decade_ladder_helpers_smoke():
    """Local smoke: one tiny ladder decade uses high-scale field path."""
    from probe_unique_floor_decade_ladder import (
        analyze_gap_from_primes,
        u1_ceiling_high,
        walk_decade,
    )

    assert u1_ceiling_high(10**6) >= 48
    # Tiny decade near 10^6 with only 4 primes (3 gaps)
    block = walk_decade(1_000_000, primes_per_decade=4)
    assert block["n_gaps"] == 3
    assert block["first_p"] >= 1_000_000
    row = analyze_gap_from_primes(block["gaps"][0]["p"], block["gaps"][0]["q"])
    assert row["g"] == block["gaps"][0]["g"]
    assert row["L_size"] >= 1
