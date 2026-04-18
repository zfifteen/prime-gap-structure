"""Tests for the tractable Mersenne gap-type probe."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "benchmarks" / "python" / "predictor" / "gwr_dni_mersenne_gap_type_probe.py"


def load_module():
    """Load the Mersenne gap-type probe script from its file path."""
    spec = importlib.util.spec_from_file_location("gwr_dni_mersenne_gap_type_probe", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load gwr_dni_mersenne_gap_type_probe module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_rows_show_one_sided_following_pattern():
    """For tractable Mersenne primes with p >= 5, the following family collapses."""
    module = load_module()
    rows = module.mersenne_rows(window_radius=2)

    row_by_exponent = {int(row["exponent"]): row for row in rows}
    assert row_by_exponent[2]["preceding_type_key"] is None
    assert row_by_exponent[2]["following_type_key"] == "o4_d3_a1_prime_square"
    assert row_by_exponent[31]["preceding_type_key"] == "o4_d4_a4_odd_semiprime"
    assert row_by_exponent[31]["following_type_key"] == "o4_d4_a2_odd_semiprime"
    assert row_by_exponent[61]["following_type_key"] == "o6_d4_a2_odd_semiprime"
    assert all(
        str(row["following_family"]) == "odd_semiprime"
        for row in rows
        if int(row["exponent"]) >= 5
    )


def test_summary_reports_following_collapse_without_full_preceding_collapse():
    """The summary should separate the rigid following side from the varied preceding side."""
    module = load_module()
    rows = module.mersenne_rows(window_radius=2)
    summary = module.summarize_rows(rows, window_radius=2)

    assert summary["mersenne_prime_count"] == 9
    assert summary["preceding_gap_count"] == 8
    assert summary["following_gap_count"] == 9
    assert summary["p_ge_5_following_all_odd_semiprime"] is True
    assert summary["distinct_preceding_type_count"] > summary["distinct_following_type_count"]
    assert summary["p_ge_5_following_exact_type_distribution"] == {
        "o6_d4_a2_odd_semiprime": 4,
        "o4_d4_a2_odd_semiprime": 3,
    }


def test_entry_point_writes_mersenne_artifacts(tmp_path):
    """The CLI entry point should emit JSON and CSV artifacts."""
    module = load_module()

    assert module.main(["--output-dir", str(tmp_path), "--window-radius", "2"]) == 0

    summary_path = tmp_path / "gwr_dni_mersenne_gap_type_probe_summary.json"
    detail_path = tmp_path / "gwr_dni_mersenne_gap_type_probe_details.csv"
    assert summary_path.exists()
    assert detail_path.exists()

    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["mersenne_prime_count"] == 9
    assert payload["p_ge_5_following_all_odd_semiprime"] is True
    assert payload["distinct_following_type_count"] == 4
