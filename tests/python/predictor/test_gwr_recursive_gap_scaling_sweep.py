"""Tests for the recursive GWR decade-scaling sweep."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SWEEP_MODULE_PATH = ROOT / "benchmarks" / "python" / "predictor" / "gwr_recursive_gap_scaling_sweep.py"
PLOT_MODULE_PATH = ROOT / "benchmarks" / "python" / "predictor" / "plot_gwr_recursive_gap_scaling_sweep.py"


def load_module(name: str, path: Path):
    """Load a benchmark helper from its file path."""
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module {name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_small_scaling_sweep_is_well_formed():
    """A small decade sweep should produce coherent regime-level metrics."""
    module = load_module("gwr_recursive_gap_scaling_sweep", SWEEP_MODULE_PATH)
    rows, summary = module.run_sweep(4)

    assert len(rows) == 3
    assert summary["power_start"] == 2
    assert summary["power_end"] == 4
    assert summary["count"] == 3
    assert summary["all_recovery_exact"] is True
    assert all(0.0 <= float(row["exact_immediate_hit_rate"]) <= 1.0 for row in rows)
    assert all(float(row["runtime_seconds"]) > 0.0 for row in rows)


def test_scaling_sweep_entry_point_writes_artifacts(tmp_path):
    """The scaling sweep CLI should emit JSON and CSV artifacts."""
    module = load_module("gwr_recursive_gap_scaling_sweep", SWEEP_MODULE_PATH)

    assert module.main(["--output-dir", str(tmp_path), "--max-power", "4"]) == 0

    summary_path = tmp_path / "gwr_recursive_gap_scaling_sweep_summary.json"
    detail_path = tmp_path / "gwr_recursive_gap_scaling_sweep_details.csv"
    assert summary_path.exists()
    assert detail_path.exists()

    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["power_start"] == 2
    assert payload["power_end"] == 4
    assert payload["count"] == 3


def test_scaling_plot_renderer_writes_png(tmp_path):
    """The scaling plot script should render one PNG from existing sweep artifacts."""
    sweep_module = load_module("gwr_recursive_gap_scaling_sweep", SWEEP_MODULE_PATH)
    plot_module = load_module("plot_gwr_recursive_gap_scaling_sweep", PLOT_MODULE_PATH)

    input_dir = tmp_path / "input"
    output_dir = tmp_path / "plots"
    assert sweep_module.main(["--output-dir", str(input_dir), "--max-power", "4"]) == 0

    output_path = plot_module.render_plot(input_dir, output_dir)
    assert output_path.exists()
    assert output_path.stat().st_size > 0
