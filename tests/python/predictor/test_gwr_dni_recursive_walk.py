"""Tests for the DNI-driven recursive gap walk."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "benchmarks" / "python" / "predictor" / "gwr_dni_recursive_walk.py"


def load_module():
    """Load the recursive walk script from its file path."""
    spec = importlib.util.spec_from_file_location("gwr_dni_recursive_walk", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load gwr_dni_recursive_walk module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_predict_next_gap_small_primes():
    """The bounded next-gap rule should recover the known small-gap lex-min."""
    module = load_module()
    # Gap (7, 11): interior = {8, 9, 10}, d = {4, 3, 4}, min = 3 at offset 2
    d, off = module.predict_next_gap(7)
    assert d == 3
    assert off == 2

    # Gap (11, 13): interior = {12}, d = {6}, min = 6 at offset 1
    d, off = module.predict_next_gap(11)
    assert d == 6
    assert off == 1

    # Gap (23, 29): interior = {24,25,26,27,28}, d = {8,3,4,4,6}
    # min = 3 at offset 2
    d, off = module.predict_next_gap(23)
    assert d == 3
    assert off == 2


def test_predict_next_gap_exact_small_primes():
    """The exact next-gap oracle should return the lex-min and boundary offset."""
    module = load_module()

    d, off, boundary = module.predict_next_gap_exact(7)
    assert d == 3
    assert off == 2
    assert boundary == 4

    d, off, boundary = module.predict_next_gap_exact(11)
    assert d == 6
    assert off == 1
    assert boundary == 2

    d, off, boundary = module.predict_next_gap_exact(23)
    assert d == 3
    assert off == 2
    assert boundary == 6


def test_compare_transition_rules_small_prime():
    """The bounded rule should match the exact oracle on a known small gap."""
    module = load_module()
    comparison = module.compare_transition_rules(23)

    assert comparison["first_open_offset"] == 6
    # dynamic_cutoff(23) == max(64, ceil(0.5 * log(23)^2)) == 64
    assert comparison["cutoff"] == 64
    assert comparison["bounded_next_dmin"] == 3
    assert comparison["bounded_next_peak_offset"] == 2
    assert comparison["exact_next_dmin"] == 3
    assert comparison["exact_next_peak_offset"] == 2
    assert comparison["exact_gap_boundary_offset"] == 6
    assert comparison["exact_next_prime"] == 29
    assert comparison["matches_cutoff_rule"] is True
    assert comparison["overshoot_margin"] == 0


def test_dynamic_cutoff_covers_known_counterexample():
    """dynamic_cutoff must cover the known falsification point q=24098209.

    The fixed map gave cutoff=60; E(q)=72 falsified it.
    dynamic_cutoff must return a value >= 72 at that prime.
    """
    module = load_module()
    cutoff = module.dynamic_cutoff(24098209)
    assert cutoff >= 72, f"dynamic_cutoff({24098209}) = {cutoff} does not cover E(q)=72"
    comparison = module.compare_transition_rules(24098209)
    assert comparison["matches_cutoff_rule"] is True
    assert comparison["overshoot_margin"] == 0


def test_walk_100_steps_exact():
    """A 100-step walk from gap index 4 should have zero skipped gaps."""
    module = load_module()
    rows, summary = module.run_walk(start_gap_index=4, steps=100)
    assert summary["exact_hit_rate"] == 1.0
    assert summary["total_skipped_gaps"] == 0
    assert summary["max_skipped_gaps"] == 0
    assert len(rows) == 100


def test_entry_point_writes_artifacts(tmp_path):
    """The CLI entry point should write summary JSON and detail CSV."""
    module = load_module()
    assert (
        module.main(
            [
                "--start-gap-index",
                "4",
                "--steps",
                "50",
                "--output-dir",
                str(tmp_path),
            ]
        )
        == 0
    )
    summary_path = tmp_path / "gwr_dni_recursive_walk_summary.json"
    detail_path = tmp_path / "gwr_dni_recursive_walk_details.csv"
    assert summary_path.exists()
    assert detail_path.exists()
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["exact_hit_rate"] == 1.0
    assert payload["total_skipped_gaps"] == 0
