"""Tests for the hidden-state miner."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "benchmarks" / "python" / "predictor" / "gwr_hidden_state_miner.py"


def load_module():
    """Load the hidden-state miner module from its file path."""
    spec = importlib.util.spec_from_file_location("gwr_hidden_state_miner", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load gwr_hidden_state_miner module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_candidate_value_builds_pairwise_labels():
    """Candidate values should compose the requested fields in order."""
    module = load_module()
    row = {
        "current_winner_parity": "even",
        "current_winner_offset": 6,
        "current_carrier_family": "even_semiprime",
        "previous_reduced_state": "o4_odd_semiprime|d<=4",
    }

    assert module.candidate_value(row, "current_winner_parity+current_winner_offset") == "even|6"
    assert (
        module.candidate_value(row, "current_winner_parity+previous_reduced_state")
        == "even|o4_odd_semiprime|d<=4"
    )


def test_rank_candidates_uses_gain_then_simplicity_tie_breaks():
    """Candidate ranking should prefer fewer primitives and lower cardinality on ties."""
    module = load_module()
    ranked = module.rank_candidates(
        [
            {
                "candidate_id": "b",
                "log_loss_gain": 0.1,
                "primitive_count": 2,
                "candidate_cardinality": 2,
                "row_count": 10,
            },
            {
                "candidate_id": "a",
                "log_loss_gain": 0.1,
                "primitive_count": 1,
                "candidate_cardinality": 3,
                "row_count": 10,
            },
            {
                "candidate_id": "c",
                "log_loss_gain": 0.1,
                "primitive_count": 1,
                "candidate_cardinality": 2,
                "row_count": 10,
            },
        ]
    )

    assert [row["candidate_id"] for row in ranked] == ["c", "a", "b"]


def test_evaluate_candidate_reports_positive_gain_for_informative_label():
    """A label that separates triad from non-triad outcomes should improve log loss."""
    module = load_module()
    rows = [
        {
            "power": 12,
            "current_gap_width": 12,
            "current_first_open_offset": 2,
            "current_winner_parity": "even",
            "current_winner_offset": 4,
            "current_carrier_family": "even_semiprime",
            "current_d_bucket": "d<=4",
            "previous_reduced_state": "o2_odd_semiprime|d<=4",
            "previous_winner_parity": "odd",
            "previous_carrier_family": "odd_semiprime",
            "next_state": "o2_odd_semiprime|d<=4",
            "next_is_triad": 1,
        },
        {
            "power": 12,
            "current_gap_width": 12,
            "current_first_open_offset": 2,
            "current_winner_parity": "even",
            "current_winner_offset": 4,
            "current_carrier_family": "even_semiprime",
            "current_d_bucket": "d<=4",
            "previous_reduced_state": "o2_odd_semiprime|d<=4",
            "previous_winner_parity": "odd",
            "previous_carrier_family": "odd_semiprime",
            "next_state": "o4_odd_semiprime|d<=4",
            "next_is_triad": 1,
        },
        {
            "power": 12,
            "current_gap_width": 12,
            "current_first_open_offset": 2,
            "current_winner_parity": "odd",
            "current_winner_offset": 4,
            "current_carrier_family": "odd_semiprime",
            "current_d_bucket": "d<=4",
            "previous_reduced_state": "o2_odd_semiprime|d<=4",
            "previous_winner_parity": "even",
            "previous_carrier_family": "even_semiprime",
            "next_state": "non_triad",
            "next_is_triad": 0,
        },
        {
            "power": 12,
            "current_gap_width": 12,
            "current_first_open_offset": 2,
            "current_winner_parity": "odd",
            "current_winner_offset": 4,
            "current_carrier_family": "odd_semiprime",
            "current_d_bucket": "d<=4",
            "previous_reduced_state": "o2_odd_semiprime|d<=4",
            "previous_winner_parity": "even",
            "previous_carrier_family": "even_semiprime",
            "next_state": "non_triad",
            "next_is_triad": 0,
        },
    ]

    result = module.evaluate_candidate(rows, "current_winner_parity")

    assert result["log_loss_gain"] > 0.0
    assert result["matched_next_triad_lift"] == 1.0
