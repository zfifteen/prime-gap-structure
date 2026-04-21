"""Tests for the phase-reset hunter."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "benchmarks" / "python" / "predictor" / "gwr_phase_reset_hunter.py"


def load_module():
    """Load the phase-reset hunter module from disk."""
    spec = importlib.util.spec_from_file_location("gwr_phase_reset_hunter", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load gwr_phase_reset_hunter module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_advance_phase_resets_on_matching_hidden_label():
    """A matching hidden-label trigger should zero the phase immediately."""
    module = load_module()
    previous_row = {
        "state": "o2_odd_semiprime|d<=4",
        "next_peak_offset": 4,
        "carrier_family": "odd_semiprime",
        "winner_parity": "odd",
    }
    current_row = {
        "state": "o4_odd_semiprime|d<=4",
        "next_peak_offset": 6,
        "carrier_family": "odd_semiprime",
        "winner_parity": "even",
    }

    next_phase = module.advance_phase(
        phase=5,
        rule_id="reset_on_best_hidden_state_label",
        previous_row=previous_row,
        current_row=current_row,
        candidate_id="current_winner_parity+current_winner_offset",
        best_hidden_label="even|6",
        mod_cycle_length=8,
    )

    assert next_phase == 0


def test_rank_reset_rules_uses_fit_then_three_step_then_signature():
    """Reset-rule ranking should follow the declared ordering."""
    module = load_module()
    ranked = module.rank_reset_rules(
        [
            {
                "rule_id": "b",
                "pooled_window_concentration_l1": 0.10,
                "three_step_concentration": 0.31,
                "reset_signature_gain": 0.04,
                "distinct_reset_phases": 2,
            },
            {
                "rule_id": "a",
                "pooled_window_concentration_l1": 0.10,
                "three_step_concentration": 0.32,
                "reset_signature_gain": 0.03,
                "distinct_reset_phases": 2,
            },
            {
                "rule_id": "c",
                "pooled_window_concentration_l1": 0.11,
                "three_step_concentration": 0.40,
                "reset_signature_gain": 0.50,
                "distinct_reset_phases": 1,
            },
        ]
    )

    assert [row["rule_id"] for row in ranked] == ["a", "b", "c"]
