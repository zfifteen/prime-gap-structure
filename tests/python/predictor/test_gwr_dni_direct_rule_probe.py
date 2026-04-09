"""Tests for the direct DNI next-gap rule probe."""

from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "benchmarks" / "python" / "predictor" / "gwr_dni_direct_rule_probe.py"


def load_module():
    """Load the direct-rule probe script from its file path."""
    spec = importlib.util.spec_from_file_location("gwr_dni_direct_rule_probe", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load gwr_dni_direct_rule_probe module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_detail_csv(path: Path, rows: list[dict[str, object]]) -> None:
    """Write one synthetic transition detail CSV."""
    fieldnames = [
        "current_right_prime",
        "current_gap_width",
        "current_dmin",
        "current_peak_offset",
        "first_open_offset",
        "next_dmin",
        "next_peak_offset",
    ]
    fieldnames.extend(f"prefix_d_{offset}" for offset in range(1, 13))
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def synthetic_rows() -> list[dict[str, object]]:
    """Return a tiny surface where min-first is exact and transfer is exact on coverage.

    Both gaps are narrow (width < 13) so the extended-rule scan never
    triggers.  Prefix entries beyond the gap interior are empty strings
    (read back as None), matching the real transition probe's behaviour.
    """
    return [
        {
            "current_right_prime": 5,
            "current_gap_width": 2,
            "current_dmin": 4,
            "current_peak_offset": 1,
            "first_open_offset": 2,
            "next_dmin": 4,
            "next_peak_offset": 2,
            "prefix_d_1": 8,
            "prefix_d_2": 4,
            **{f"prefix_d_{offset}": "" for offset in range(3, 13)},
        },
        {
            "current_right_prime": 11,
            "current_gap_width": 4,
            "current_dmin": 4,
            "current_peak_offset": 2,
            "first_open_offset": 2,
            "next_dmin": 6,
            "next_peak_offset": 1,
            "prefix_d_1": 6,
            **{f"prefix_d_{offset}": "" for offset in range(2, 13)},
        },
    ]


def test_rule_summary_reports_accuracy_and_transfer(tmp_path):
    """The summary should expose direct-rule accuracy and transfer metrics."""
    module = load_module()
    train_path = tmp_path / "train.csv"
    test_path = tmp_path / "test.csv"
    rows = synthetic_rows()
    write_detail_csv(train_path, rows)
    write_detail_csv(test_path, rows)

    summary = module.summarize(module.load_rows(train_path), module.load_rows(test_path))

    assert summary["combined_row_count"] == 4
    assert summary["direct_min_first_accuracy"]["exact_rate"] == 1.0
    assert summary["extended_min_accuracy"]["exact_rate"] == 1.0
    assert summary["prefix12_ambiguity"]["ambiguous_signature_count"] == 0
    assert summary["direct_rule_miss_surface"]["miss_count"] == 0
    assert summary["direct_rule_miss_surface"]["minimal_exact_miss_bundle"] is None
    assert summary["direct_rule_miss_surface"]["minimal_disjoint_miss_bundle"] is None
    assert summary["cutoff_rules"]["universal"]["max_cutoff"] == 2
    assert summary["cutoff_rules"]["universal"]["cutoff_map"] == {"global": 2}
    assert summary["cutoff_rules"]["first_open_piecewise"]["cutoff_map"] == {"2": 2}
    assert summary["low_divisor_first_position_family_exact"] is True
    assert summary["transfer"]["width_prefix12"]["coverage_share"] == 1.0
    assert summary["transfer"]["width_prefix12"]["exact_on_covered_share"] == 1.0


def test_entry_point_writes_summary_json(tmp_path):
    """The CLI entry point should emit the direct-rule summary JSON."""
    module = load_module()
    train_path = tmp_path / "train.csv"
    test_path = tmp_path / "test.csv"
    output_path = tmp_path / "summary.json"
    rows = synthetic_rows()
    write_detail_csv(train_path, rows)
    write_detail_csv(test_path, rows)

    assert (
        module.main(
            [
                "--train-detail-csv",
                str(train_path),
                "--test-detail-csv",
                str(test_path),
                "--output-json",
                str(output_path),
            ]
        )
        == 0
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["direct_min_first_accuracy"]["exact_rate"] == 1.0
    assert payload["extended_min_accuracy"]["exact_rate"] == 1.0
    assert payload["direct_rule_miss_surface"]["miss_count"] == 0
    assert payload["direct_rule_miss_surface"]["minimal_disjoint_miss_bundle"] is None
    assert payload["cutoff_rules"]["universal"]["cutoff_map"] == {"global": 2}
    assert payload["cutoff_rules"]["first_open_piecewise"]["cutoff_map"] == {"2": 2}
    assert payload["transfer"]["peak_prefix12"]["coverage_share"] == 1.0
