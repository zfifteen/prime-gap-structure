"""Smoke tests for the non-floor d=4 square-threat frontier scan."""

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


def test_nonfloor_scan_returns_rows_on_small_exact_surface():
    """A small exact surface should produce non-floor d=4 rows."""
    module = load_module("d4_square_threat_nonfloor_frontier")
    summary, frontier = module.scan_nonfloor_frontier(
        max_n=1_000_000,
        chunk_size=200_000,
        buffer=10_000,
        frontier_size=10,
        prime_buffer=1_000,
    )

    assert summary["scanned_gap_count"] > 0
    assert summary["nonfloor_count"] > 0
    assert frontier
    assert all(int(row["margin"]) > 2 for row in frontier)
    assert all(not row["r2_minus_2_factors"] == "" for row in frontier)


def test_entry_point_emits_nonfloor_artifacts(tmp_path):
    """The CLI entry point should emit summary and frontier artifacts."""
    module = load_module("d4_square_threat_nonfloor_frontier")

    assert (
        module.main(
            [
                "--output-dir",
                str(tmp_path),
                "--max-n",
                "1000000",
                "--chunk-size",
                "200000",
                "--buffer",
                "10000",
                "--frontier-size",
                "5",
                "--prime-buffer",
                "1000",
            ]
        )
        == 0
    )

    summary_path = tmp_path / "d4_square_threat_nonfloor_frontier_summary.json"
    frontier_path = tmp_path / "d4_square_threat_nonfloor_frontier.csv"
    assert summary_path.exists()
    assert frontier_path.exists()

    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert int(payload["global_min_margin"]) > 2
    assert len(payload["frontier"]) == 5
