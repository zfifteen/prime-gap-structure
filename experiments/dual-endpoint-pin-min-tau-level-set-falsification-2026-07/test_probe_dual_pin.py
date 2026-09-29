#!/usr/bin/env python3
"""Local unit checks for dual right-pin probe."""

from __future__ import annotations

from probe_dual_pin import analyze_gap, divisor_counts, p2_bound, run_probe


def test_p2_bound_floor():
    assert p2_bound(11) == 32
    assert p2_bound(10**6) >= 32


def test_analyze_gap_level_set():
    tau = divisor_counts(100)
    row = analyze_gap(23, 29, tau)
    assert row is not None
    assert row["w"] <= row["w_R"]
    assert row["clearance"] == 29 - row["w_R"]
    assert row["L_size"] >= 1


def test_run_probe_smoke():
    result = run_probe(p_max=500, p_min=11)
    assert result["counts"]["gaps_nonempty"] > 0
    assert result["status_language"] == "measured_on_regime_only"
    blob = str(result).lower()
    assert "validated" not in blob
    assert "verified" not in blob


def test_pinned_ce_structure_if_present():
    """Structural check for the known P2 counter-example integers (if in range)."""
    # p=9725087 is above smoke regime; only check analyze_gap math on a synthetic.
    tau = divisor_counts(200)
    row = analyze_gap(113, 127, tau)
    assert row is not None
    assert row["g"] == 14
    assert row["clearance"] >= 1
