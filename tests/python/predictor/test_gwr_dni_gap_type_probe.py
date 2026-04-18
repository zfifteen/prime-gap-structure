"""Tests for the exact DNI gap-type probe."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "benchmarks" / "python" / "predictor" / "gwr_dni_gap_type_probe.py"


def load_module():
    """Load the gap-type probe script from its file path."""
    spec = importlib.util.spec_from_file_location("gwr_dni_gap_type_probe", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load gwr_dni_gap_type_probe module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_gap_type_row_splits_width_six_into_distinct_families():
    """Width six should realize distinct exact winner families."""
    module = load_module()

    square = module.gap_type_row(23)
    odd_semiprime = module.gap_type_row(31)
    even_semiprime = module.gap_type_row(61)

    assert square["next_gap_width"] == 6
    assert square["winner"] == 25
    assert square["next_dmin"] == 3
    assert square["carrier_family"] == "prime_square"
    assert square["type_key"] == "o6_d3_a2_prime_square"

    assert odd_semiprime["next_gap_width"] == 6
    assert odd_semiprime["winner"] == 33
    assert odd_semiprime["next_dmin"] == 4
    assert odd_semiprime["carrier_family"] == "odd_semiprime"
    assert odd_semiprime["type_key"] == "o6_d4_a2_odd_semiprime"

    assert even_semiprime["next_gap_width"] == 6
    assert even_semiprime["winner"] == 62
    assert even_semiprime["next_dmin"] == 4
    assert even_semiprime["carrier_family"] == "even_semiprime"
    assert even_semiprime["type_key"] == "o6_d4_a1_even_semiprime"


def test_summary_reports_multifamily_gap_width_examples():
    """The summary should record widths that split across carrier families."""
    module = load_module()
    rows = module.type_rows(70)
    summary = module.summarize_rows(rows)

    assert summary["gap_count"] == len(rows)
    assert summary["winner_offset_le_share"]["12"] == 1.0
    assert summary["carrier_family_distribution"]["prime_square"]["count"] > 0
    assert summary["carrier_family_distribution"]["odd_semiprime"]["count"] > 0
    assert summary["carrier_family_distribution"]["even_semiprime"]["count"] > 0
    assert summary["distinct_exact_type_count"] > 1
    assert summary["multifamily_gap_width_count"] > 0

    width_six = next(
        example
        for example in summary["multifamily_gap_width_examples"]
        if example["gap_width"] == 6
    )
    assert width_six["carrier_family_count"] >= 3
    assert "prime_square" in width_six["carrier_families"]
    assert "odd_semiprime" in width_six["carrier_families"]
    assert "even_semiprime" in width_six["carrier_families"]


def test_entry_point_writes_gap_type_artifacts(tmp_path):
    """The CLI entry point should emit JSON and CSV artifacts."""
    module = load_module()

    assert module.main(["--output-dir", str(tmp_path), "--max-right-prime", "1000"]) == 0

    summary_path = tmp_path / "gwr_dni_gap_type_probe_summary.json"
    detail_path = tmp_path / "gwr_dni_gap_type_probe_details.csv"
    assert summary_path.exists()
    assert detail_path.exists()

    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["gap_count"] > 0
    assert payload["carrier_family_distribution"]["odd_semiprime"]["count"] > 0
    assert payload["distinct_exact_type_count"] > 0
    assert payload["multifamily_gap_width_count"] > 0
