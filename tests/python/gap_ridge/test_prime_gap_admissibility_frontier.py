"""Tests for the prime-gap admissibility frontier extractor."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
FRONTIER_SCRIPT_PATH = ROOT / "gwr" / "experiments" / "proof" / "prime_gap_admissibility_frontier.py"
PARALLEL_SCRIPT_PATH = ROOT / "gwr" / "experiments" / "proof" / "parallel_no_early_spoiler_scan.py"


def load_module(module_name: str, script_path: Path):
    """Load one proof helper directly from its file path."""
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {script_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_prime_gap_admissibility_frontier_exact_interval(tmp_path, capsys):
    """The frontier extractor should emit the exact interval summary and CSV rows."""
    module = load_module("prime_gap_admissibility_frontier_interval", FRONTIER_SCRIPT_PATH)
    output_path = tmp_path / "proof" / "prime_gap_admissibility_frontier_interval.json"

    assert (
        module.main(
            [
                "--interval-hi",
                "10001",
                "--top-cases",
                "10",
                "--top-states",
                "10",
                "--output",
                str(output_path),
            ]
        )
        == 0
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["source_summary"]["mode"] == "exact_interval"
    assert payload["source_summary"]["interval"] == {"lo": 2, "hi": 10001}
    assert payload["hard_case_count"] > 0
    assert payload["square_branch_case_count"] > 0
    assert payload["non_square_case_count"] > 0
    assert payload["exact_case_rows"]
    assert payload["exact_state_summary"]
    assert payload["chamber_state_summary"]
    assert payload["winner_class_summary"]
    assert payload["automatic_window_elimination_summary"]["checked_divisor_classes"]

    rows_path = output_path.with_name(output_path.stem + "_rows.csv")
    assert rows_path.exists()

    stdout_payload = json.loads(capsys.readouterr().out)
    assert stdout_payload["source_summary"]["interval"] == {"lo": 2, "hi": 10001}


def test_prime_gap_admissibility_frontier_checkpoint_mode(tmp_path, capsys):
    """The frontier extractor should reconstruct hard cases from segment checkpoints."""
    parallel_module = load_module("parallel_no_early_spoiler_scan_frontier_fixture", PARALLEL_SCRIPT_PATH)
    frontier_module = load_module("prime_gap_admissibility_frontier_checkpoint", FRONTIER_SCRIPT_PATH)

    segment_output_dir = tmp_path / "segments"
    aggregate_output = tmp_path / "aggregate.json"
    assert (
        parallel_module.main(
            [
                "--lo",
                "2",
                "--hi",
                "10001",
                "--segment-size",
                "1000",
                "--jobs",
                "1",
                "--segment-output-dir",
                str(segment_output_dir),
                "--aggregate-output",
                str(aggregate_output),
            ]
        )
        == 0
    )
    capsys.readouterr()

    output_path = tmp_path / "proof" / "prime_gap_admissibility_frontier_checkpoints.json"
    assert (
        frontier_module.main(
            [
                "--checkpoint-dir",
                str(segment_output_dir),
                "--top-cases",
                "10",
                "--top-states",
                "10",
                "--output",
                str(output_path),
            ]
        )
        == 0
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["source_summary"]["mode"] == "checkpoint_frontier"
    assert payload["source_summary"]["checkpoint_dir"] == str(segment_output_dir)
    assert payload["source_summary"]["checkpoint_case_count"] > 0
    assert payload["source_summary"]["gap_count"] > 0
    assert payload["hard_case_count"] == payload["source_summary"]["retained_case_count"]
    assert payload["exact_case_rows"]
    assert payload["winner_class_summary"]

    stdout_payload = json.loads(capsys.readouterr().out)
    assert stdout_payload["source_summary"]["mode"] == "checkpoint_frontier"
