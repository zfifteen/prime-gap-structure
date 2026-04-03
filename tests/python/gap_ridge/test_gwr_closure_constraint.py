"""Smoke tests for the GWR closure-constraint validator."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BENCHMARKS_DIR = ROOT / "benchmarks" / "python" / "gap_ridge"


def load_module(name: str):
    """Load one benchmark module directly from its file path."""
    path = BENCHMARKS_DIR / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module {name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_validate_closure_constraint_on_small_exact_surface():
    """Small exact surfaces should show no closure-constraint violations."""
    module = load_module("gwr_closure_constraint")
    row = module.validate_closure_constraint_on_interval(
        2,
        10_001,
        10_000,
        "exact",
        prime_buffer=1_000,
    )

    assert row["gap_count"] > 0
    assert row["closure_violation_count"] == 0
    assert row["closure_match_rate"] == 1.0
    assert row["max_gap"] >= 4
    assert row["winner_d4_count"] > 0
    assert row["d4_threat_count"] == row["winner_d4_count"]
    assert row["d4_threat_distance_mean"] is not None
    assert row["d4_prime_arrival_margin_mean"] is not None


def test_closure_constraint_entry_point_emits_summary(tmp_path):
    """The CLI entry point should emit the summary artifact."""
    module = load_module("gwr_closure_constraint")

    assert (
        module.main(
            [
                "--output-dir",
                str(tmp_path),
                "--exact-limit",
                "100000",
                "--sampled-scales",
                "1000000",
                "--window-size",
                "10000",
                "--window-count",
                "2",
                "--seeds",
                "7",
                "11",
                "--max-examples",
                "3",
                "--prime-buffer",
                "1000",
            ]
        )
        == 0
    )

    summary_path = tmp_path / "gwr_closure_constraint_summary.json"
    sampled_csv_path = tmp_path / "gwr_closure_constraint_sampled.csv"
    assert summary_path.exists()
    assert sampled_csv_path.exists()

    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["exact"]["closure_violation_count"] == 0
    assert payload["exact"]["closure_match_rate"] == 1.0
    assert payload["exact"]["d4_threat_count"] == payload["exact"]["winner_d4_count"]
    assert len(payload["sampled"]) == 3
    assert all(row["closure_violation_count"] == 0 for row in payload["sampled"])
