"""Tests for the compression shock probe."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "benchmarks" / "python" / "predictor" / "gwr_compression_shock_probe.py"


def load_module():
    """Load the compression shock probe module from disk."""
    spec = importlib.util.spec_from_file_location("gwr_compression_shock_probe", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load gwr_compression_shock_probe module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_pareto_frontier_keeps_nondominated_rows():
    """The Pareto frontier should keep only rows that are not jointly dominated."""
    module = load_module()
    rows = [
        {
            "model_id": "a",
            "effective_state_count": 5,
            "pooled_window_concentration_l1": 0.10,
            "three_step_concentration": 0.40,
        },
        {
            "model_id": "b",
            "effective_state_count": 5,
            "pooled_window_concentration_l1": 0.12,
            "three_step_concentration": 0.35,
        },
        {
            "model_id": "c",
            "effective_state_count": 7,
            "pooled_window_concentration_l1": 0.08,
            "three_step_concentration": 0.44,
        },
    ]

    frontier = module.pareto_frontier(rows)

    assert [row["model_id"] for row in frontier] == ["a", "c"]


def test_select_shock_winner_prefers_smallest_strict_improver():
    """The shock winner should be the smallest model that clears both strict improvements."""
    module = load_module()
    rows = [
        {
            "model_id": "second_order_rotor",
            "effective_state_count": 13,
            "pooled_window_concentration_l1": 0.10,
            "three_step_concentration": 0.30,
        },
        {
            "model_id": "hidden_state_augmented_rotor",
            "effective_state_count": 20,
            "pooled_window_concentration_l1": 0.09,
            "three_step_concentration": 0.32,
        },
        {
            "model_id": "hidden_state_phase_scheduler",
            "effective_state_count": 18,
            "pooled_window_concentration_l1": 0.09,
            "three_step_concentration": 0.31,
        },
    ]

    winner, negative_result = module.select_shock_winner(rows)

    assert winner["model_id"] == "hidden_state_phase_scheduler"
    assert negative_result is None


def test_select_shock_winner_records_negative_result_when_only_three_step_improves():
    """A three-step-only improvement should return the best small improver plus a negative note."""
    module = load_module()
    rows = [
        {
            "model_id": "second_order_rotor",
            "effective_state_count": 13,
            "pooled_window_concentration_l1": 0.10,
            "three_step_concentration": 0.30,
        },
        {
            "model_id": "hidden_state_augmented_rotor",
            "effective_state_count": 17,
            "pooled_window_concentration_l1": 0.11,
            "three_step_concentration": 0.31,
        },
    ]

    winner, negative_result = module.select_shock_winner(rows)

    assert winner["model_id"] == "hidden_state_augmented_rotor"
    assert "no model improved both" in negative_result
