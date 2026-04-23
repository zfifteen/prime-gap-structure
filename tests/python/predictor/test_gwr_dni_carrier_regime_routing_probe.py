"""Tests for the carrier-regime routing probe."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "benchmarks" / "python" / "predictor" / "gwr_dni_carrier_regime_routing_probe.py"


def load_module():
    """Load the carrier-regime routing probe module from its file path."""
    spec = importlib.util.spec_from_file_location(
        "gwr_dni_carrier_regime_routing_probe",
        MODULE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load gwr_dni_carrier_regime_routing_probe module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_carrier_regime_probe_emits_partition_scores():
    """The held-out probe should score partitions and routing policies."""
    module = load_module()
    rows = module.load_rows(ROOT / "output" / "gwr_dni_gap_type_catalog_details.csv")

    summary, detail_rows = module.evaluate(
        rows,
        train_min_power=7,
        train_max_power=17,
        held_power=18,
        pressure_quantile=0.8,
        recent_window=6,
    )

    assert summary["row_count"] == len(detail_rows)
    assert summary["row_count"] > 0
    assert summary["carrier_regime_gate_count"] > 0
    assert set(summary["policy_scores"]) == {
        "short_only",
        "long_only",
        "carrier_regime_gated",
    }
    assert "hard_case_capture" in summary
    assert "pollution_rate" in summary
    assert summary["sweep_count"] == len(summary["sweep_rows"])
    assert summary["sweep_count"] > 0
    assert "best_sweep_candidate" in summary
    assert "best_low_pollution_candidate" in summary
    assert "partition_table" in summary
    assert "four_way_partition" in summary
    assert len(summary["four_way_partition"]) == 4
    assert "decision" in summary


def test_carrier_regime_probe_cli_writes_artifacts(tmp_path):
    """The CLI entry point should write the summary JSON and row CSV."""
    module = load_module()

    assert module.main(
        [
            "--detail-csv",
            str(ROOT / "output" / "gwr_dni_gap_type_catalog_details.csv"),
            "--output-dir",
            str(tmp_path),
            "--held-power",
            "18",
            "--recent-window",
            "6",
        ]
    ) == 0

    summary_path = tmp_path / "gwr_dni_carrier_regime_routing_summary.json"
    rows_path = tmp_path / "gwr_dni_carrier_regime_routing_rows.csv"
    sweep_path = tmp_path / "gwr_dni_carrier_regime_routing_sweep.csv"
    assert summary_path.exists()
    assert rows_path.exists()
    assert sweep_path.exists()

    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["held_surface"] == "10^18"
    assert payload["recent_window"] == 6
    assert payload["row_count"] > 0
    assert payload["sweep_count"] > 0
    assert "partition_table" in payload
