"""Tests for the DNI next-gap transition probe."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "benchmarks" / "python" / "predictor" / "gwr_dni_transition_probe.py"


def load_module():
    """Load the transition probe script from its file path."""
    spec = importlib.util.spec_from_file_location("gwr_dni_transition_probe", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load gwr_dni_transition_probe module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_transition_rows_keep_oracle_next_dmin_exact():
    """The oracle next-dmin witness should recover every nonempty next gap exactly."""
    module = load_module()
    rows = module.transition_rows(1_000)

    assert rows
    nonempty = [row for row in rows if not row["next_gap_empty"]]
    assert nonempty
    assert all(row["oracle_exact"] is True for row in nonempty)


def test_summary_reports_bundle_ambiguity_and_distributions():
    """The summary should expose next-dmin distributions and state-bundle ambiguity."""
    module = load_module()
    rows = module.transition_rows(1_000)
    summary = module.summarize_rows(rows)

    assert summary["transition_count"] == len(rows)
    assert summary["oracle_exact_rate_nonempty"] == 1.0
    assert summary["next_peak_offset_le_share"]["1"] > 0.0
    assert summary["prefix_min_match_share"]["1"] > 0.0
    assert summary["prefix_peak_exact_share"]["1"] > 0.0
    assert summary["next_peak_within_first_open_share"] > 0.0
    assert "4" in summary["next_dmin_distribution"]
    assert summary["bundle_ambiguity"]
    assert any(
        bundle["state_keys"] == ["residue_mod30", "current_gap_width", "current_dmin", "current_peak_offset"]
        for bundle in summary["bundle_ambiguity"]
    )
    assert any(
        bundle["state_keys"]
        == ["residue_mod30", "first_open_offset", "prefix_d_1", "prefix_d_2", "prefix_d_3", "prefix_d_4"]
        for bundle in summary["bundle_ambiguity"]
    )


def test_entry_point_writes_transition_artifacts(tmp_path):
    """The CLI entry point should emit JSON and CSV artifacts."""
    module = load_module()

    assert module.main(["--output-dir", str(tmp_path), "--max-right-prime", "1000"]) == 0

    summary_path = tmp_path / "gwr_dni_transition_probe_summary.json"
    detail_path = tmp_path / "gwr_dni_transition_probe_details.csv"
    assert summary_path.exists()
    assert detail_path.exists()

    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["oracle_exact_rate_nonempty"] == 1.0
    assert payload["prefix_min_match_share"]["1"] > 0.0
    assert payload["transition_count"] > 0
