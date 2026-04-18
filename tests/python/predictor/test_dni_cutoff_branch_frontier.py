"""Tests for the dynamic bounded branch-frontier extractor."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "gwr" / "experiments" / "proof" / "dni_cutoff_branch_frontier.py"


def load_module():
    """Load the branch-frontier script from its file path."""
    spec = importlib.util.spec_from_file_location(
        "dni_cutoff_branch_frontier",
        MODULE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load dni_cutoff_branch_frontier module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_small_dynamic_branch_frontier_is_well_formed():
    """A small branch frontier should record both cutoff and boundary extrema."""
    module = load_module()
    summary, frontier_rows = module.run_frontier(11, 10_000)

    assert summary["tested_gap_count"] > 0
    assert summary["branch_count"] > 0
    assert frontier_rows

    for row in summary["branch_summary"]:
        assert "argmax_cutoff_utilization" in row
        assert "argmax_boundary_utilization" in row
        assert float(row["max_cutoff_utilization"]) <= 1.0
        assert float(row["max_boundary_utilization"]) <= 1.0

        cutoff_argmax = row["argmax_cutoff_utilization"]
        boundary_argmax = row["argmax_boundary_utilization"]
        assert cutoff_argmax["metric_value"] == float(row["max_cutoff_utilization"])
        assert boundary_argmax["metric_value"] == float(row["max_boundary_utilization"])
