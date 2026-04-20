"""Tests for the gap-type scheduler probe."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "benchmarks" / "python" / "predictor" / "gwr_dni_gap_type_scheduler_probe.py"


def load_module():
    """Load the scheduler probe module from its file path."""
    spec = importlib.util.spec_from_file_location(
        "gwr_dni_gap_type_scheduler_probe",
        MODULE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load gwr_dni_gap_type_scheduler_probe module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_windowed_scheduler_summary_prefers_lag2_state_model():
    """The lag-2 state scheduler should be the best pooled-window fit."""
    module = load_module()
    rows = module.GEN_PROBE.load_rows(ROOT / "output" / "gwr_dni_gap_type_catalog_details.csv")

    summary = module.summarize(
        rows=rows,
        train_surfaces=[f"10^{power}" for power in range(7, 18)],
        reference_surfaces=[f"10^{power}" for power in range(12, 19)],
        synthetic_length=4096,
        window_length=256,
        mod_cycle_length=8,
    )

    models = summary["models"]
    assert summary["best_model_id"] == "lag2_state_scheduler"
    assert models["lag2_state_scheduler"]["scheduler_phase_count"] == 14
    assert models["lag2_state_scheduler"]["pooled_window_concentration_l1"] < (
        models["second_order_rotor"]["pooled_window_concentration_l1"]
    )
    assert models["lag2_state_scheduler"]["pooled_window_concentration_l1"] < (
        models["mod_cycle_scheduler"]["pooled_window_concentration_l1"]
    )


def test_entry_point_writes_scheduler_artifacts(tmp_path):
    """The CLI entry point should emit JSON and PNG artifacts."""
    module = load_module()

    assert module.main(
        [
            "--detail-csv",
            str(ROOT / "output" / "gwr_dni_gap_type_catalog_details.csv"),
            "--output-dir",
            str(tmp_path),
            "--synthetic-length",
            "4096",
            "--window-length",
            "256",
            "--mod-cycle-length",
            "8",
        ]
    ) == 0

    summary_path = tmp_path / "gwr_dni_gap_type_scheduler_probe_summary.json"
    plot_path = tmp_path / "gwr_dni_gap_type_scheduler_probe_overview.png"
    assert summary_path.exists()
    assert plot_path.exists()

    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["best_model_id"] == "lag2_state_scheduler"
    assert "mod_cycle_scheduler" in payload["models"]
