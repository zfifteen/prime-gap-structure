"""Tests for the GWR/DNI gap-type sequence probe."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "benchmarks" / "python" / "predictor" / "gwr_dni_gap_type_sequence_probe.py"


def load_module():
    """Load the gap-type sequence probe script from its file path."""
    spec = importlib.util.spec_from_file_location("gwr_dni_gap_type_sequence_probe", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load gwr_dni_gap_type_sequence_probe module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_sequence_metrics_detects_deterministic_shift():
    """A short repeating grammar should show full one-step concentration."""
    module = load_module()
    metrics = module.sequence_metrics(["A", "B", "A", "B", "A", "B"])

    assert metrics["state_count"] == 2
    assert metrics["weighted_top_successor_share"] == 1.0
    assert metrics["unique_successor_state_rate"] == 1.0
    assert metrics["pair_weighted_top_successor_share"] == 1.0


def test_top_lift_transitions_ranks_state_conditioning():
    """Lift ranking should preserve the strongest current-to-next preferences."""
    module = load_module()
    lifts = module.top_lift_transitions(
        ["A", "B", "A", "B", "A", "C", "A", "B", "A", "C"],
        limit=4,
        min_count=1,
    )

    assert lifts[0]["next_state"] == "A"
    assert lifts[0]["lift"] > 1.0
    assert any(
        row["current_state"] == "C"
        and row["next_state"] == "A"
        and row["lift"] > 1.0
        for row in lifts
    )


def test_closure_metrics_detects_core_settlement():
    """Closure metrics should separate the stable core from excursions."""
    module = load_module()
    metrics = module.closure_metrics(
        ["A", "B", "A", "C", "A"],
        {"A", "B"},
    )

    assert metrics["state_count"] == 3
    assert metrics["core_state_count"] == 2
    assert metrics["next_core_observation_share"] == 0.75
    assert metrics["transition_core_observation_share"] == 0.5


def test_state_value_reduced_alphabet_uses_divisor_bucket():
    """The reduced alphabet should join open-family with the coarse d bucket."""
    module = load_module()
    row = {
        "first_open_offset": "4",
        "carrier_family": "higher_divisor_even",
        "next_dmin": "48",
        "type_key": "unused",
    }

    assert module.state_value(row, module.REDUCED_ALPHABET) == (
        "o4_higher_divisor_even|17<=d<=64"
    )


def test_entry_point_writes_sequence_probe_artifacts(tmp_path):
    """The CLI entry point should emit JSON and PNG artifacts."""
    module = load_module()

    assert module.main(
        [
            "--detail-csv",
            str(ROOT / "output" / "gwr_dni_gap_type_catalog_details.csv"),
            "--output-dir",
            str(tmp_path),
        ]
    ) == 0

    summary_path = tmp_path / "gwr_dni_gap_type_sequence_probe_summary.json"
    plot_path = tmp_path / "gwr_dni_gap_type_sequence_probe_overview.png"
    assert summary_path.exists()
    assert plot_path.exists()

    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert "sequence_summaries" in payload
    assert "<=10^6" in payload["sequence_summaries"]
    assert "10^18" in payload["selected_open_family_heatmaps"]
    assert payload["reduced_state_definition"]["alphabet"] == module.REDUCED_ALPHABET
    assert "10^18" in payload["selected_reduced_state_heatmaps"]
    assert "closure_summaries" in payload
