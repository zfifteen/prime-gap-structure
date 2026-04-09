"""Tests for the exact DNI recursive-walk decade sweep and plots."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SWEEP_MODULE_PATH = (
    ROOT / "benchmarks" / "python" / "predictor" / "gwr_dni_recursive_gap_scaling_sweep.py"
)
PLOT_MODULE_PATH = (
    ROOT / "benchmarks" / "python" / "predictor" / "plot_gwr_dni_recursive_gap_scaling_sweep.py"
)


def load_module(name: str, path: Path):
    """Load a benchmark helper from its file path."""
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module {name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_small_scaling_sweep_is_well_formed():
    """A small exact DNI decade sweep should produce coherent metrics."""
    module = load_module("gwr_dni_recursive_gap_scaling_sweep", SWEEP_MODULE_PATH)
    rows, summary = module.run_sweep(2, 3)

    assert len(rows) == 2
    assert summary["power_start"] == 2
    assert summary["power_end"] == 3
    assert summary["count"] == 2
    assert summary["all_exact_hits"] is True
    assert summary["all_zero_skips"] is True
    assert all(float(row["exact_hit_rate"]) == 1.0 for row in rows)
    assert all(int(row["total_skipped_gaps"]) == 0 for row in rows)
    assert all(0.0 <= float(row["max_cutoff_utilization"]) <= 1.0 for row in rows)


def test_scaling_sweep_entry_point_writes_artifacts(tmp_path):
    """The sweep CLI should emit JSON and CSV artifacts."""
    module = load_module("gwr_dni_recursive_gap_scaling_sweep", SWEEP_MODULE_PATH)

    assert module.main(["--output-dir", str(tmp_path), "--min-power", "2", "--max-power", "3"]) == 0

    summary_path = tmp_path / "gwr_dni_recursive_gap_scaling_sweep_summary.json"
    detail_path = tmp_path / "gwr_dni_recursive_gap_scaling_sweep_details.csv"
    assert summary_path.exists()
    assert detail_path.exists()

    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["power_start"] == 2
    assert payload["power_end"] == 3
    assert payload["count"] == 2
    assert payload["all_exact_hits"] is True


def test_scaling_plot_renderer_writes_pngs(tmp_path):
    """The scaling plot script should render both PNGs from existing sweep artifacts."""
    sweep_module = load_module("gwr_dni_recursive_gap_scaling_sweep", SWEEP_MODULE_PATH)
    plot_module = load_module("plot_gwr_dni_recursive_gap_scaling_sweep", PLOT_MODULE_PATH)

    input_dir = tmp_path / "input"
    output_dir = tmp_path / "plots"
    assert sweep_module.main(["--output-dir", str(input_dir), "--min-power", "2", "--max-power", "3"]) == 0

    outputs = plot_module.render_plots(input_dir, output_dir)
    assert outputs["performance"].exists()
    assert outputs["performance"].stat().st_size > 0
    assert outputs["offsets"].exists()
    assert outputs["offsets"].stat().st_size > 0
