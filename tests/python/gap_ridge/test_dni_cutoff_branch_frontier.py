"""Tests for the exact DNI cutoff branch frontier extractor."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = ROOT / "gwr" / "experiments" / "proof" / "dni_cutoff_branch_frontier.py"


def load_module():
    """Load the proof-pursuit script directly from its file path."""
    spec = importlib.util.spec_from_file_location(
        "dni_cutoff_branch_frontier",
        SCRIPT_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load dni_cutoff_branch_frontier")
    module = importlib.util.module_from_spec(spec)
    sys.modules["dni_cutoff_branch_frontier"] = module
    spec.loader.exec_module(module)
    return module


def test_dni_cutoff_branch_frontier_emits_branch_summary(tmp_path, capsys):
    """The branch frontier extractor should emit a ranked branch summary."""
    module = load_module()
    output_path = tmp_path / "proof" / "dni_cutoff_branch_frontier.json"

    assert (
        module.main(
            [
                "--min-right-prime",
                "11",
                "--max-right-prime",
                "10001",
                "--output",
                str(output_path),
            ]
        )
        == 0
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["interval"] == {"min_right_prime": 11, "max_right_prime": 10001}
    assert payload["tested_gap_count"] > 0
    assert payload["branch_count"] > 0
    assert payload["branch_summary"]
    top = payload["global_max_peak_branch"]
    assert top is not None
    assert top["max_exact_next_peak_offset"] <= top["cutoff"]

    frontier_path = output_path.with_name(output_path.stem + "_rows.csv")
    assert frontier_path.exists()

    stdout_payload = json.loads(capsys.readouterr().out)
    assert stdout_payload["interval"] == {"min_right_prime": 11, "max_right_prime": 10001}
