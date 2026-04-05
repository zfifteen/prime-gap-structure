"""Tests for the exact no-early-spoiler ratio frontier extractor."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = ROOT / "gwr" / "experiments" / "proof" / "no_early_spoiler_ratio_frontier.py"


def load_module():
    """Load the proof-pursuit script directly from its file path."""
    spec = importlib.util.spec_from_file_location(
        "no_early_spoiler_ratio_frontier",
        SCRIPT_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load no_early_spoiler_ratio_frontier")
    module = importlib.util.module_from_spec(spec)
    sys.modules["no_early_spoiler_ratio_frontier"] = module
    spec.loader.exec_module(module)
    return module


def test_no_early_spoiler_ratio_frontier_emits_ranked_pairs(tmp_path, capsys):
    """The frontier extractor should emit a ranked pair surface on a small interval."""
    module = load_module()
    output_path = tmp_path / "proof" / "no_early_spoiler_ratio_frontier.json"

    assert (
        module.main(
            [
                "--lo",
                "2",
                "--hi",
                "10001",
                "--output",
                str(output_path),
            ]
        )
        == 0
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["interval"] == {"lo": 2, "hi": 10001}
    assert payload["pair_count"] > 0
    assert payload["top_ratio_frontier_pairs"]
    assert payload["winner_class_frontier"]
    tightest = payload["top_ratio_frontier_pairs"][0]
    assert tightest["critical_ratio_margin"] > 0.0

    stdout_payload = json.loads(capsys.readouterr().out)
    assert stdout_payload["interval"] == {"lo": 2, "hi": 10001}
