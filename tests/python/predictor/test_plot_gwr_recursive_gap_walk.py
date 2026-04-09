"""Tests for recursive GWR gap-walk plotting."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
WALK_MODULE_PATH = ROOT / "benchmarks" / "python" / "predictor" / "gwr_recursive_gap_walk.py"
PLOT_MODULE_PATH = ROOT / "benchmarks" / "python" / "predictor" / "plot_gwr_recursive_gap_walk.py"


def load_module(name: str, path: Path):
    """Load a benchmark helper from its file path."""
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module {name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_render_plots_writes_three_png_artifacts(tmp_path):
    """The plotting script should render the recursive walk into three PNG plots."""
    walk_module = load_module("gwr_recursive_gap_walk", WALK_MODULE_PATH)
    plot_module = load_module("plot_gwr_recursive_gap_walk", PLOT_MODULE_PATH)

    input_dir = tmp_path / "input"
    output_dir = tmp_path / "plots"
    assert walk_module.main(["--output-dir", str(input_dir), "--start-gap-index", "10", "--steps", "12"]) == 0

    outputs = plot_module.render_plots(input_dir, output_dir)

    numberline_path = outputs["numberline"]
    dashboard_path = outputs["dashboard"]
    jump_path = outputs["jump_behavior"]
    assert numberline_path.exists()
    assert dashboard_path.exists()
    assert jump_path.exists()
    assert numberline_path.stat().st_size > 0
    assert dashboard_path.stat().st_size > 0
    assert jump_path.stat().st_size > 0


def test_plot_entry_point_runs_from_cli(tmp_path):
    """The CLI entry point should render plots from an existing walk artifact directory."""
    walk_module = load_module("gwr_recursive_gap_walk", WALK_MODULE_PATH)
    plot_module = load_module("plot_gwr_recursive_gap_walk", PLOT_MODULE_PATH)

    input_dir = tmp_path / "input"
    output_dir = tmp_path / "plots"
    assert walk_module.main(["--output-dir", str(input_dir), "--start-gap-index", "10", "--steps", "8"]) == 0
    assert plot_module.main(["--input-dir", str(input_dir), "--output-dir", str(output_dir)]) == 0

    assert (output_dir / "gwr_recursive_gap_walk_numberline.png").exists()
    assert (output_dir / "gwr_recursive_gap_walk_dashboard.png").exists()
    assert (output_dir / "gwr_recursive_gap_walk_jump_behavior.png").exists()
