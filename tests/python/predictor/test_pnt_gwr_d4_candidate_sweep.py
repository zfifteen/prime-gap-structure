"""Tests for the dominant d=4 candidate sweep."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "benchmarks" / "python" / "predictor" / "pnt_gwr_d4_candidate_sweep.py"


def load_module():
    """Load the sweep runner from its file path."""
    spec = importlib.util.spec_from_file_location("pnt_gwr_d4_candidate_sweep", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load pnt_gwr_d4_candidate_sweep module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_small_sweep_exposes_nonzero_error_surface():
    """A small sweep should already show that the dominant path is approximate."""
    module = load_module()
    rows, summary = module.run_sweep(10, 25)

    assert len(rows) == 16
    assert summary["count"] == 16
    assert summary["exact_hit_rate"] < 1.0
    assert summary["mean_abs_prime_offset"] > 0.0
    assert summary["mean_abs_rank_offset"] > 0.0
    assert summary["exact_hits_equal_witness_hits"] is True


def test_admissible_rate_dominates_seed_in_gap_rate_on_small_surface():
    """The seed can still be before an admissible target-gap d=4 carrier."""
    module = load_module()
    _, summary = module.run_sweep(10, 100)

    assert summary["admissible_d4_from_seed_rate"] >= summary["seed_in_target_gap_rate"]
    assert summary["witness_in_target_gap_rate"] <= summary["admissible_d4_from_seed_rate"]


def test_entry_point_writes_summary_and_detail_artifacts(tmp_path):
    """The CLI entry point should emit JSON and CSV artifacts."""
    module = load_module()

    assert module.main(["--output-dir", str(tmp_path), "--n-start", "10", "--n-end", "25"]) == 0

    summary_path = tmp_path / "pnt_gwr_d4_candidate_sweep_summary.json"
    detail_path = tmp_path / "pnt_gwr_d4_candidate_sweep_details.csv"
    assert summary_path.exists()
    assert detail_path.exists()

    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["n_start"] == 10
    assert payload["n_end"] == 25
    assert payload["count"] == 16
