"""Tests for the exact GWR witness walk."""

from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "benchmarks" / "python" / "predictor" / "gwr_witness_walk.py"


def load_module():
    """Load the witness-walk script from its file path."""
    spec = importlib.util.spec_from_file_location("gwr_witness_walk", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load gwr_witness_walk module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_boundary_scan_and_witness_map_small_prime():
    """The witness path should match the direct boundary scan on a small gap."""
    module = load_module()

    assert module.boundary_scan_next_prime(23) == 29

    next_prime, profile = module.witness_map_next_prime(23)
    assert next_prime == 29
    assert profile["winner_d"] == 3
    assert profile["winner_offset"] == 2
    assert profile["winner_n"] == 25
    assert profile["witness"] == 25
    assert profile["witness_matches_winner"] is True
    assert profile["gap_width"] == 6
    assert profile["next_prime_boundary"] == 29
    assert profile["next_prime_via_witness"] == 29


def test_witness_map_handles_gap_after_two():
    """The empty gap after 2 should return the boundary with no witness."""
    module = load_module()

    next_prime, profile = module.witness_map_next_prime(2)
    assert next_prime == 3
    assert profile["winner_d"] is None
    assert profile["winner_offset"] is None
    assert profile["winner_n"] is None
    assert profile["witness"] is None
    assert profile["witness_matches_winner"] is True
    assert profile["gap_width"] == 1


def test_previous_prime_finds_exact_anchor():
    """The backward exact scan should recover the previous prime anchor."""
    module = load_module()

    assert module.previous_prime(29) == 29
    assert module.previous_prime(28) == 23


def test_next_prime_uses_previous_prime_anchor_and_witness_path():
    """The public next-prime helper should advance from the previous prime anchor."""
    module = load_module()

    assert module.next_prime(1) == 2
    assert module.next_prime(2) == 3
    assert module.next_prime(24) == 29
    assert module.next_prime(29) == 31


def test_lockstep_compare_has_no_divergence_on_short_run():
    """A short exact run from 11 should remain divergence-free."""
    module = load_module()

    rows, summary = module.lockstep_compare(start_prime=11, steps=100)

    assert len(rows) == 100
    assert summary["steps_completed"] == 100
    assert summary["matches"] == 100
    assert summary["divergences"] == 0
    assert summary["first_divergence"] is None
    assert summary["all_witnesses_match_winner"] is True
    assert all(bool(row["match"]) for row in rows)


def test_entry_point_writes_summary_and_detail_artifacts(tmp_path):
    """The CLI entry point should write the canonical witness-walk artifacts."""
    module = load_module()

    assert (
        module.main(
            [
                "--start-prime",
                "11",
                "--steps",
                "25",
                "--output-dir",
                str(tmp_path),
            ]
        )
        == 0
    )

    summary_path = tmp_path / "gwr_witness_walk_summary.json"
    detail_path = tmp_path / "gwr_witness_walk_details.csv"
    assert summary_path.exists()
    assert detail_path.exists()

    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["steps_requested"] == 25
    assert payload["steps_completed"] == 25
    assert payload["divergences"] == 0
    assert payload["all_witnesses_match_winner"] is True

    with detail_path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 25
    assert rows[0]["q"] == "11"
    assert rows[0]["path_a_next"] == "13"
    assert rows[0]["path_b_next"] == "13"
