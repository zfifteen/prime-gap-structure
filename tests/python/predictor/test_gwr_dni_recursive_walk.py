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
    d, off = module.predict_next_gap(7)
    assert d == 3
    assert off == 2

    d, off = module.predict_next_gap(11)
    assert d == 6
    assert off == 1

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


def test_exact_next_gap_profile_small_primes():
    """The next-gap profiles should recover the known small-gap boundary."""
    module = load_module()

    profile = module.exact_next_gap_profile(7)
    assert profile["next_dmin"] == 3
    assert profile["next_peak_offset"] == 2
    assert profile["gap_boundary_offset"] == 4
    assert profile["next_prime"] == 11

    profile = module.bounded_next_gap_profile(23)
    assert profile["next_dmin"] == 3
    assert profile["next_peak_offset"] == 2
    assert profile["gap_boundary_offset"] == 6
    assert profile["next_prime"] == 29


def test_bounded_profile_uses_prefix_lock_witness_without_extended_scan(monkeypatch):
    """Locked delta<=3 prefixes should recover the boundary from the prefix alone."""
    module = load_module()
    original = module.divisor_counts_segment

    cases = [
        (229433, 3, 8, 26, 229459, [(229434, 229446)]),
        (1026167, 3, 2, 30, 1026197, [(1026168, 1026180)]),
    ]

    for q, expected_d, expected_peak, expected_boundary, expected_next_prime, expected_calls in cases:
        calls: list[tuple[int, int]] = []

        def tracked_divisor_counts_segment(start: int, stop: int):
            calls.append((start, stop))
            return original(start, stop)

        monkeypatch.setattr(module, "divisor_counts_segment", tracked_divisor_counts_segment)
        profile = module.bounded_next_gap_profile(q)

        assert profile["next_dmin"] == expected_d
        assert profile["next_peak_offset"] == expected_peak
        assert profile["gap_boundary_offset"] == expected_boundary
        assert profile["next_prime"] == expected_next_prime
        assert calls == expected_calls


def test_compare_transition_rules_small_prime():
    """The bounded rule should match the exact oracle on a known small gap."""
    module = load_module()
    comparison = module.compare_transition_rules(23)

    assert comparison["first_open_offset"] == 6
    assert comparison["cutoff"] == 64
    assert comparison["bounded_next_dmin"] == 3
    assert comparison["bounded_next_peak_offset"] == 2
    assert comparison["bounded_gap_boundary_offset"] == 6
    assert comparison["bounded_next_prime"] == 29
    assert comparison["exact_next_dmin"] == 3
    assert comparison["exact_next_peak_offset"] == 2
    assert comparison["exact_gap_boundary_offset"] == 6
    assert comparison["exact_next_prime"] == 29
    assert comparison["matches_cutoff_rule"] is True
    assert comparison["boundary_utilization"] == 6 / 64
    assert comparison["overshoot_margin"] == 0


def test_unbounded_runtime_path_uses_prefix_then_clipped_tail(monkeypatch):
    """The live unbounded path should stop segment reads after the 12-offset prefix."""
    module = load_module()
    original = module.divisor_counts_segment
    calls: list[tuple[int, int]] = []

    def tracked_divisor_counts_segment(start: int, stop: int):
        calls.append((start, stop))
        return original(start, stop)

    monkeypatch.setattr(module, "divisor_counts_segment", tracked_divisor_counts_segment)
    fast = module.next_gap_profile(24098209, "unbounded")
    fast_calls = list(calls)
    calls.clear()
    exact = module.exact_next_gap_profile(24098209)

    assert fast["next_prime"] == exact["next_prime"]
    assert fast["gap_boundary_offset"] == exact["gap_boundary_offset"]
    assert fast["next_dmin"] == exact["next_dmin"]
    assert fast["next_peak_offset"] == exact["next_peak_offset"]
    assert fast_calls == [(24098210, 24098222)]


def test_dynamic_cutoff_covers_known_counterexample():
    """dynamic_cutoff must cover the known falsification point q=24098209."""
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


def test_compare_mode_100_steps_exact():
    """Compare mode should show no bounded misses on the 100-step probe."""
    module = load_module()
    rows, summary = module.run_walk(start_gap_index=4, steps=100, mode="compare")
    assert summary["exact_hit_rate"] == 1.0
    assert summary["bounded_miss_count"] == 0
    assert summary["bounded_conjecture_held"] is True
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


def test_compare_entry_point_writes_artifacts(tmp_path):
    """Compare-mode CLI should write the canonical artifact names."""
    module = load_module()
    assert (
        module.main(
            [
                "--start-gap-index",
                "4",
                "--steps",
                "50",
                "--mode",
                "compare",
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
    assert payload["bounded_miss_count"] == 0
    assert payload["bounded_conjecture_held"] is True
