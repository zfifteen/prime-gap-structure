"""Tests for the self-contained recursive GWR decade-scaling sweep."""

from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULAR_MODULE_PATH = ROOT / "benchmarks" / "python" / "predictor" / "gwr_recursive_gap_scaling_sweep.py"
SELF_CONTAINED_MODULE_PATH = (
    ROOT / "benchmarks" / "python" / "predictor" / "gwr_recursive_gap_scaling_sweep_self_contained.py"
)


def load_module(name: str, path: Path):
    """Load one benchmark helper from its file path."""
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module {name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_self_contained_small_sweep_matches_modular_surface():
    """The single-file sweep should match the modular sweep on a small range."""
    modular = load_module("gwr_recursive_gap_scaling_sweep_modular", MODULAR_MODULE_PATH)
    self_contained = load_module(
        "gwr_recursive_gap_scaling_sweep_self_contained",
        SELF_CONTAINED_MODULE_PATH,
    )

    modular_rows, modular_summary = modular.run_sweep(4)
    self_rows, self_summary = self_contained.run_sweep(4)

    assert len(modular_rows) == len(self_rows) == 3
    comparable_keys = [
        "power",
        "decade_start",
        "steps",
        "start_gap_index",
        "start_left_prime",
        "start_right_prime",
        "exact_immediate_hit_rate",
        "mean_skipped_gap_count",
        "max_skipped_gap_count",
        "recovery_exact_rate",
        "mean_next_gap_width",
    ]
    for modular_row, self_row in zip(modular_rows, self_rows, strict=True):
        assert {key: modular_row[key] for key in comparable_keys} == {
            key: self_row[key] for key in comparable_keys
        }

    summary_keys = [
        "power_start",
        "power_end",
        "count",
        "mean_exact_immediate_hit_rate",
        "mean_mean_skipped_gap_count",
        "max_start_right_prime",
        "all_recovery_exact",
    ]
    assert {key: modular_summary[key] for key in summary_keys} == {
        key: self_summary[key] for key in summary_keys
    }


def test_self_contained_entry_point_writes_artifacts(tmp_path):
    """The self-contained sweep CLI should emit JSON and CSV artifacts."""
    module = load_module(
        "gwr_recursive_gap_scaling_sweep_self_contained",
        SELF_CONTAINED_MODULE_PATH,
    )

    assert module.main(["--output-dir", str(tmp_path), "--max-power", "4"]) == 0

    summary_path = tmp_path / "gwr_recursive_gap_scaling_sweep_summary.json"
    detail_path = tmp_path / "gwr_recursive_gap_scaling_sweep_details.csv"
    assert summary_path.exists()
    assert detail_path.exists()

    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["power_start"] == 2
    assert payload["power_end"] == 4
    assert payload["count"] == 3

    with detail_path.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 3
