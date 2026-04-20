"""Tests for the long-horizon controller probe."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = (
    ROOT
    / "benchmarks"
    / "python"
    / "predictor"
    / "gwr_dni_gap_type_long_horizon_controller_probe.py"
)


def load_module():
    """Load the long-horizon controller probe module from its file path."""
    spec = importlib.util.spec_from_file_location(
        "gwr_dni_gap_type_long_horizon_controller_probe",
        MODULE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load gwr_dni_gap_type_long_horizon_controller_probe module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_controller_summary_exposes_tradeoff_frontier():
    """The long-horizon controllers should improve different sides of the frontier."""
    module = load_module()
    rows = module.GEN_PROBE.load_rows(ROOT / "output" / "gwr_dni_gap_type_catalog_details.csv")
    record_rows = module.load_record_rows(ROOT / "data" / "external" / "primegap_list_records_1e12_1e18.csv")

    summary = module.summarize(
        rows=rows,
        record_rows=record_rows,
        synthetic_length=4096,
        window_length=256,
        mod_cycle_length=8,
        event_lock_min=2,
        event_lock_max=4,
        debt_threshold_min=5,
        debt_threshold_max=7,
    )

    assert summary["best_event_lock_by_pooled"]["pooled_window_concentration_l1"] < (
        summary["hybrid_baseline"]["pooled_window_concentration_l1"]
    )
    assert summary["best_event_lock_by_full_walk"]["full_walk_concentrations"]["three_step"] > (
        summary["hybrid_baseline"]["full_walk_concentrations"]["three_step"]
    )
    assert summary["best_fatigue_by_full_walk"]["full_walk_concentrations"]["three_step"] > (
        summary["hybrid_baseline"]["full_walk_concentrations"]["three_step"]
    )
    assert "event_lock_best_full_walk" in summary["recent_higher_divisor_signature"]


def test_entry_point_writes_long_horizon_controller_artifacts(tmp_path):
    """The CLI entry point should emit JSON and PNG artifacts."""
    module = load_module()

    assert module.main(
        [
            "--detail-csv",
            str(ROOT / "output" / "gwr_dni_gap_type_catalog_details.csv"),
            "--record-csv",
            str(ROOT / "data" / "external" / "primegap_list_records_1e12_1e18.csv"),
            "--output-dir",
            str(tmp_path),
            "--synthetic-length",
            "4096",
            "--window-length",
            "256",
            "--mod-cycle-length",
            "8",
            "--event-lock-min",
            "2",
            "--event-lock-max",
            "4",
            "--debt-threshold-min",
            "5",
            "--debt-threshold-max",
            "7",
        ]
    ) == 0

    summary_path = tmp_path / "gwr_dni_gap_type_long_horizon_controller_probe_summary.json"
    plot_path = tmp_path / "gwr_dni_gap_type_long_horizon_controller_probe_overview.png"
    assert summary_path.exists()
    assert plot_path.exists()

    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert "event_lock_sweep" in payload
    assert "fatigue_debt_sweep" in payload
