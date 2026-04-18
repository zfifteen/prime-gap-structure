"""Tests for the twin-prime outer gap-type probe."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "benchmarks" / "python" / "predictor" / "gwr_dni_twin_prime_gap_type_probe.py"


def load_module():
    """Load the twin-prime gap-type probe script from its file path."""
    spec = importlib.util.spec_from_file_location("gwr_dni_twin_prime_gap_type_probe", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load gwr_dni_twin_prime_gap_type_probe module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_exact_rows_capture_outer_types_of_small_twin_pairs():
    """Small twin pairs should expose their outer-gap types directly."""
    module = load_module()
    bundle = module.exact_type_rows(1_000)
    rows = bundle["twin_pair_rows"]
    pair_map = {(int(row["left_prime"]), int(row["right_prime"])): row for row in rows}

    assert len(rows) == 35
    assert pair_map[(3, 5)]["preceding_type_key"] is None
    assert pair_map[(3, 5)]["following_type_key"] == "o2_d4_a1_even_semiprime"
    assert pair_map[(11, 13)]["preceding_type_key"] == "o4_d3_a2_prime_square"
    assert pair_map[(11, 13)]["following_type_key"] == "o4_d4_a1_even_semiprime"
    assert pair_map[(569, 571)]["preceding_type_key"] == "o6_d4_a2_odd_semiprime"
    assert pair_map[(569, 571)]["following_type_key"] == "o6_d4_a2_odd_semiprime"
    assert pair_map[(569, 571)]["same_outer_family"] is True


def test_summary_uses_residue_conditioned_baselines():
    """The summary should compare twin-pair outer families to residue-conditioned baselines."""
    module = load_module()
    bundle = module.exact_type_rows(1_000)
    summary = module.summarize_rows(bundle, max_right_prime=1_000)

    assert summary["twin_pair_count"] == 35
    assert summary["defined_preceding_twin_pair_count"] == 34
    assert summary["left_twin_residues_mod30"] == [11, 17, 29]
    assert summary["right_twin_residues_mod30"] == [1, 13, 19]
    assert summary["distinct_outer_pair_signature_count"] > 1
    assert summary["same_outer_family_share"] > 0.0
    assert summary["preceding_family_vs_residue_baseline"]["odd_semiprime"]["twin_count"] > 0
    assert summary["following_family_vs_residue_baseline"]["even_semiprime"]["twin_count"] > 0
    assert summary["top_following_types"]


def test_entry_point_writes_twin_prime_artifacts(tmp_path):
    """The CLI entry point should emit JSON and CSV artifacts."""
    module = load_module()

    assert module.main(["--output-dir", str(tmp_path), "--max-right-prime", "1000"]) == 0

    summary_path = tmp_path / "gwr_dni_twin_prime_gap_type_probe_summary.json"
    detail_path = tmp_path / "gwr_dni_twin_prime_gap_type_probe_details.csv"
    assert summary_path.exists()
    assert detail_path.exists()

    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["twin_pair_count"] == 35
    assert payload["defined_preceding_twin_pair_count"] == 34
    assert payload["distinct_following_type_count"] > 1
