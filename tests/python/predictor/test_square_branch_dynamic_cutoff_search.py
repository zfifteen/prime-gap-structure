"""Tests for the square-branch dynamic-cutoff search."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = (
    ROOT
    / "benchmarks"
    / "python"
    / "predictor"
    / "square_branch_dynamic_cutoff_search.py"
)
ARTIFACT_SUMMARY_PATH = (
    ROOT
    / "output"
    / "gwr_proof"
    / "square_branch_dynamic_cutoff_search_1e8"
    / "square_branch_dynamic_cutoff_search_summary.json"
)


def load_module():
    """Load the square-branch search script from its file path."""
    spec = importlib.util.spec_from_file_location(
        "square_branch_dynamic_cutoff_search",
        MODULE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load square_branch_dynamic_cutoff_search module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_small_range_has_no_counterexample_and_known_frontier():
    """A small square range should stay inside the current dynamic cutoff."""
    module = load_module()
    frontier_rows, summary, first_counterexample = module.run_search(3, 10_000)

    assert first_counterexample is None
    assert summary["first_counterexample"] is None
    assert summary["tested_prime_count"] > 0
    assert summary["first_tested_prime"] == 3
    assert summary["last_tested_prime"] is not None
    assert frontier_rows
    assert summary["max_row"]["p"] == 3929
    assert summary["max_row"]["square"] == 15437041
    assert summary["max_row"]["previous_prime"] == 15436943
    assert summary["max_row"]["offset"] == 98
    assert summary["max_row"]["o_q"] == 6
    assert summary["max_row"]["dynamic_cutoff"] == 137
    assert summary["max_dynamic_cutoff_utilization"] == 98 / 137
    assert summary["max_row_by_o_q"]["6"]["p"] == 3929


def test_search_stops_at_first_counterexample(monkeypatch):
    """The search should stop immediately when one square branch breaks the cutoff."""
    module = load_module()
    original = module.walk.dynamic_cutoff

    def broken_dynamic_cutoff(current_right_prime: int) -> int:
        if current_right_prime == 7:
            return 1
        return original(current_right_prime)

    monkeypatch.setattr(module.walk, "dynamic_cutoff", broken_dynamic_cutoff)

    frontier_rows, summary, first_counterexample = module.run_search(3, 100)

    assert summary["tested_prime_count"] == 1
    assert first_counterexample is not None
    assert summary["first_counterexample"] is not None
    assert first_counterexample["p"] == 3
    assert frontier_rows


def test_cli_writes_artifacts(tmp_path):
    """The CLI entry point should emit summary JSON and frontier CSV."""
    module = load_module()

    assert (
        module.main(
            [
                "--min-prime",
                "3",
                "--max-prime",
                "10000",
                "--output-dir",
                str(tmp_path),
            ]
        )
        == 0
    )

    summary_path = tmp_path / "square_branch_dynamic_cutoff_search_summary.json"
    frontier_path = tmp_path / "square_branch_dynamic_cutoff_search_frontier.csv"
    counterexample_path = tmp_path / "square_branch_dynamic_cutoff_counterexample.json"
    assert summary_path.exists()
    assert frontier_path.exists()
    assert not counterexample_path.exists()

    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["first_counterexample"] is None
    assert payload["max_row"]["p"] == 3929
    assert payload["max_dynamic_cutoff_utilization"] == 98 / 137


def test_recorded_1e8_frontier_row_reproduces_exact_transition():
    """The retained 1e8 square frontier row should still match the exact oracle."""
    module = load_module()
    payload = json.loads(ARTIFACT_SUMMARY_PATH.read_text(encoding="utf-8"))
    row = payload["max_row"]

    comparison = module.walk.compare_transition_rules(int(row["previous_prime"]))

    assert payload["first_counterexample"] is None
    assert comparison["matches_cutoff_rule"] is True
    assert comparison["exact_next_dmin"] == 3
    assert comparison["exact_next_peak_offset"] == int(row["offset"])
    assert comparison["cutoff"] == int(row["dynamic_cutoff"])
