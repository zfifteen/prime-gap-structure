"""Tests for the hybrid gap-type scheduler probe."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "benchmarks" / "python" / "predictor" / "gwr_dni_gap_type_hybrid_scheduler_probe.py"


def load_module():
    """Load the hybrid scheduler probe module from its file path."""
    spec = importlib.util.spec_from_file_location(
        "gwr_dni_gap_type_hybrid_scheduler_probe",
        MODULE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load gwr_dni_gap_type_hybrid_scheduler_probe module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_hybrid_summary_improves_pooled_window_fit_but_not_stationary_gap():
    """Hybrid schedulers should improve the pooled fit while staying below the 0.60 full-walk target."""
    module = load_module()
    rows = module.GEN_PROBE.load_rows(ROOT / "output" / "gwr_dni_gap_type_catalog_details.csv")

    summary = module.summarize(
        rows=rows,
        train_surfaces=[f"10^{power}" for power in range(7, 18)],
        reference_surfaces=[f"10^{power}" for power in range(12, 19)],
        synthetic_length=4096,
        window_length=256,
        mod_cycle_length=8,
        sweep_min_cycle=2,
        sweep_max_cycle=8,
        record_csv=None,
        skip_record_analysis=True,
        record_workers=1,
    )

    models = summary["models"]
    assert models["hybrid_lag2_mod8_reset_hdiv_scheduler"]["pooled_window_concentration_l1"] < (
        models["lag2_state_scheduler"]["pooled_window_concentration_l1"]
    )
    assert (
        summary["ranking_by_full_walk_three_step"][0]["full_walk_three_step"] < 0.60
    )
    assert summary["best_full_walk_three_step_model_id"] == "hybrid_lag2_mod8_scheduler"


def test_entry_point_writes_hybrid_scheduler_artifacts(tmp_path):
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
            "--sweep-min-cycle",
            "2",
            "--sweep-max-cycle",
            "8",
            "--skip-record-analysis",
        ]
    ) == 0

    summary_path = tmp_path / "gwr_dni_gap_type_hybrid_scheduler_probe_summary.json"
    plot_path = tmp_path / "gwr_dni_gap_type_hybrid_scheduler_probe_overview.png"
    assert summary_path.exists()
    assert plot_path.exists()

    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["best_pooled_model_id"] == "hybrid_lag2_mod8_reset_nontriad_scheduler"
    assert "hybrid_reset_hdiv_scheduler" in payload["cycle_sweeps"]
