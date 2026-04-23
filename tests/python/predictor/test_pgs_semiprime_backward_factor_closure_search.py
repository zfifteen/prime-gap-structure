"""Tests for the factor-closure search harness."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HARNESS_PATH = (
    ROOT
    / "benchmarks"
    / "python"
    / "predictor"
    / "pgs_semiprime_backward_factor_closure_search.py"
)


def load_module(name: str, path: Path):
    """Load one local benchmark module by path."""
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module {name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_factor_closure_harness_is_deterministic_on_reduced_surface():
    """The reduced factor-closure summary should be deterministic."""
    module = load_module("pgs_semiprime_backward_factor_closure_search", HARNESS_PATH)
    summary_a = module.run_search(max_n=500, max_steps=24)
    summary_b = module.run_search(max_n=500, max_steps=24)

    assert summary_a == summary_b


def test_factor_closure_harness_pins_zero_floor_on_full_surface():
    """The factor-closure family should honestly remain at the 0/980 floor."""
    module = load_module("pgs_semiprime_backward_factor_closure_search", HARNESS_PATH)
    summary = module.run_search(max_n=5000, max_steps=24)

    assert summary["fixed_entry_law"] == "layered_hybrid_exact_shape_entry_switch"
    assert summary["entry_lane_count"] == 89
    assert summary["best_factor_reach_count"] == 0
    assert summary["searched_family_falsified"] is True
    assert summary["best_law"] == "prime_left_boundary_control"
    assert all(
        law_summary["factor_reach_count"] == 0
        for law_summary in summary["closure_law_summaries"].values()
    )


def test_cli_writes_lf_terminated_factor_closure_summary(tmp_path: Path):
    """The factor-closure CLI should emit LF-terminated summary JSON only."""
    module = load_module("pgs_semiprime_backward_factor_closure_search", HARNESS_PATH)
    exit_code = module.main(["--max-n", "500", "--max-steps", "24", "--output-dir", str(tmp_path)])

    assert exit_code == 0

    summary_path = tmp_path / module.SUMMARY_FILENAME
    assert summary_path.exists()
    raw = summary_path.read_bytes()
    assert raw.endswith(b"\n")
    assert b"\r\n" not in raw

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["entry_lane_count"] == 10
    assert summary["best_factor_reach_count"] == 0
    assert summary["searched_family_falsified"] is True
