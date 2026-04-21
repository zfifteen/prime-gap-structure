"""Tests for the winner-parity next-opening probe."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "benchmarks" / "python" / "predictor" / "gwr_winner_parity_next_opening_probe.py"


def load_module():
    """Load the winner-parity probe script from its file path."""
    spec = importlib.util.spec_from_file_location("gwr_winner_parity_next_opening_probe", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load gwr_winner_parity_next_opening_probe module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_matched_lane_metrics_controls_for_stratum_mix():
    """Matched shares should ignore parity advantages caused only by stratum imbalance."""
    module = load_module()
    transitions = [
        {
            "current_winner_parity": "even",
            "current_gap_width": 12,
            "current_first_open_offset": 2,
            "next_lane": "o2_odd_semiprime|d<=4",
            "next_is_triad": 1,
        },
        {
            "current_winner_parity": "even",
            "current_gap_width": 12,
            "current_first_open_offset": 2,
            "next_lane": "o2_odd_semiprime|d<=4",
            "next_is_triad": 1,
        },
        {
            "current_winner_parity": "odd",
            "current_gap_width": 12,
            "current_first_open_offset": 2,
            "next_lane": "o4_odd_semiprime|d<=4",
            "next_is_triad": 1,
        },
        {
            "current_winner_parity": "even",
            "current_gap_width": 18,
            "current_first_open_offset": 4,
            "next_lane": "o2_odd_semiprime|d<=4",
            "next_is_triad": 1,
        },
        {
            "current_winner_parity": "odd",
            "current_gap_width": 18,
            "current_first_open_offset": 4,
            "next_lane": "o2_odd_semiprime|d<=4",
            "next_is_triad": 1,
        },
        {
            "current_winner_parity": "odd",
            "current_gap_width": 18,
            "current_first_open_offset": 4,
            "next_lane": "o2_odd_semiprime|d<=4",
            "next_is_triad": 1,
        },
        {
            "current_winner_parity": "even",
            "current_gap_width": 20,
            "current_first_open_offset": 2,
            "next_lane": "o6_odd_semiprime|d<=4",
            "next_is_triad": 1,
        },
    ]

    metrics = module.matched_lane_metrics(transitions)

    assert metrics["matched_strata_count"] == 2
    assert metrics["matched_total_weight_per_parity"] == 2
    assert metrics["matched_lane_shares"]["even"]["o2_odd_semiprime|d<=4"] == 1.0
    assert metrics["matched_lane_shares"]["odd"]["o2_odd_semiprime|d<=4"] == 0.5
    assert metrics["matched_lane_shares"]["odd"]["o4_odd_semiprime|d<=4"] == 0.5
    assert metrics["matched_lane_share_difference"]["o2_odd_semiprime|d<=4"] == 0.5
    assert metrics["matched_lane_share_difference"]["o4_odd_semiprime|d<=4"] == -0.5


def test_reduced_state_uses_open_offset_and_divisor_bucket():
    """Reduced state should keep the repo's open-family plus coarse divisor bucket."""
    module = load_module()
    row = {
        "first_open_offset": 6,
        "carrier_family": "higher_divisor_even",
        "next_dmin": 18,
    }

    assert module.reduced_state(row) == "o6_higher_divisor_even|17<=d<=64"
