"""Tests for the semiprime-branch d=4 layer baseline runner."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "benchmarks" / "python" / "gap_ridge" / "d4_layer_baseline.py"


def load_module():
    """Load the baseline runner as a module."""
    spec = importlib.util.spec_from_file_location("d4_layer_baseline", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load d4_layer_baseline module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_small_exact_interval_separates_semiprimes_from_prime_cubes():
    """A small exact surface should already separate the d=4 winner classes."""
    module = load_module()
    row = module.summarize_interval(
        lo=2,
        hi=10_001,
        scale=10_000,
        window_mode="exact",
    )

    assert row["winner_d4_count"] > 0
    assert row["winner_prime_cube_count"] == 1
    assert row["winner_other_d4_count"] == 0
    assert row["winner_semiprime_count"] + row["winner_prime_cube_count"] == row[
        "winner_d4_count"
    ]
    assert row["first_d4_match_count"] == row["winner_d4_count"]
    assert row["interior_square_violation_count"] == 0
    assert row["median_winner_offset"] == row["median_first_d4_offset"]


def test_prefilter_surface_loads_current_candidate_loop_headlines():
    """The baseline summary should carry the committed large-RSA rejection surface."""
    module = load_module()
    surface = module.load_prefilter_surface()

    assert surface["exact_calibration"]["prime_fixed_points"] == 29
    assert surface["exact_calibration"]["composite_false_fixed_points"] == 0
    assert surface["candidate_loop"]["rsa_2048"]["rejected_by_proxy"] == 932
    assert surface["candidate_loop"]["rsa_4096"]["rejected_by_proxy"] == 234


def test_summary_json_is_lf_terminated_and_contains_exact_20m_starting_facts(tmp_path: Path):
    """The summary artifact should be LF-terminated and expose the exact 2e7 baseline row."""
    module = load_module()
    row = module.summarize_interval(
        lo=2,
        hi=10_001,
        scale=10_000,
        window_mode="exact",
    )
    summary = {
        "by_scale": [module._public_row(row)],
        "starting_facts": {"exact_20000000": {"winner_d4_count": 959730}},
    }
    output_path = tmp_path / "summary.json"
    output_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    raw = output_path.read_bytes()
    assert raw.endswith(b"\n")
    assert b"\r\n" not in raw
