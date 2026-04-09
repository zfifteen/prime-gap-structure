"""Tests for the DNI cutoff-law counterexample scan."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = (
    ROOT / "benchmarks" / "python" / "predictor" / "gwr_dni_cutoff_counterexample_scan.py"
)


def load_module():
    """Load the cutoff scan script from its file path."""
    spec = importlib.util.spec_from_file_location(
        "gwr_dni_cutoff_counterexample_scan",
        MODULE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load gwr_dni_cutoff_counterexample_scan module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_small_consecutive_surface_has_no_counterexample():
    """The bounded rule should agree with the exact oracle on a small exact surface."""
    module = load_module()
    frontier_rows, summary, first_counterexample = module.run_scan(11, 10_000)

    assert first_counterexample is None
    assert summary["first_counterexample"] is None
    assert summary["tested_gap_count"] > 0
    assert summary["first_tested_right_prime"] == 11
    assert summary["last_tested_right_prime"] is not None
    assert frontier_rows
    assert summary["max_exact_peak_offset_overall"] <= 60
    assert summary["max_cutoff_utilization_overall"] <= 1.0


def test_counterexample_scan_entry_point_writes_artifacts(tmp_path):
    """The cutoff scan CLI should emit summary JSON and frontier CSV."""
    module = load_module()

    assert (
        module.main(
            [
                "--min-right-prime",
                "11",
                "--max-right-prime",
                "10000",
                "--output-dir",
                str(tmp_path),
            ]
        )
        == 0
    )

    summary_path = tmp_path / "gwr_dni_cutoff_counterexample_scan_summary.json"
    frontier_path = tmp_path / "gwr_dni_cutoff_counterexample_scan_frontier.csv"
    counterexample_path = tmp_path / "gwr_dni_cutoff_counterexample.json"
    assert summary_path.exists()
    assert frontier_path.exists()
    assert not counterexample_path.exists()

    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["first_counterexample"] is None
    assert payload["tested_gap_count"] > 0
    assert payload["max_exact_peak_offset_overall"] <= 60


def test_scan_stops_at_first_counterexample(monkeypatch):
    """The scan should stop immediately when the bounded rule first fails."""
    module = load_module()
    original = module.walk.predict_next_gap_bounded

    def broken_predict_next_gap_bounded(current_right_prime: int):
        if current_right_prime == 11:
            predicted_dmin, predicted_peak_offset = original(current_right_prime)
            return predicted_dmin + 1, predicted_peak_offset
        return original(current_right_prime)

    monkeypatch.setattr(
        module.walk,
        "predict_next_gap_bounded",
        broken_predict_next_gap_bounded,
    )

    frontier_rows, summary, first_counterexample = module.run_scan(11, 1_000)

    assert summary["tested_gap_count"] == 1
    assert first_counterexample is not None
    assert summary["first_counterexample"] is not None
    assert first_counterexample["current_right_prime"] == 11
    assert frontier_rows


def test_exact_scan_through_one_million_has_no_counterexample():
    """The exact consecutive scan through 10^6 should stay inside the cutoff rule."""
    module = load_module()
    frontier_rows, summary, first_counterexample = module.run_scan(11, 1_000_000)

    assert first_counterexample is None
    assert summary["first_counterexample"] is None
    assert summary["tested_gap_count"] > 70_000
    assert frontier_rows
    assert summary["max_exact_peak_offset_overall"] <= 60
    assert summary["max_cutoff_utilization_overall"] <= 1.0
