"""Tests for the backward pattern miner and refined transition harness."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MINER_PATH = ROOT / "benchmarks" / "python" / "predictor" / "pgs_semiprime_backward_pattern_miner.py"
REFINED_PATH = (
    ROOT
    / "benchmarks"
    / "python"
    / "predictor"
    / "pgs_semiprime_backward_refined_transition_law_search.py"
)


def load_module(name: str, path: Path):
    """Load one local benchmark module by path."""
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module {name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_pattern_miner_pins_immediate_good_entry_count():
    """The miner should pin the measured immediate entry opportunity surface."""
    module = load_module("pgs_semiprime_backward_pattern_miner", MINER_PATH)
    summary = module.mine_patterns(max_n=5000)

    assert summary["immediate_good_entry_case_count"] == 153
    assert summary["one_step_best_law"] == "small_gap_d4_large_offset__same_role_same_offset_winner__same_role_p_left"
    assert summary["two_step_best_law"] == "small_gap_d4_large_offset__repeat_role_repeat_offset__same_role_p_left"


def test_refined_harness_is_deterministic_on_reduced_surface():
    """The refined reduced summary should be deterministic."""
    module = load_module("pgs_semiprime_backward_refined_transition_law_search", REFINED_PATH)
    trace_a, summary_a = module.run_search(max_n=500, max_steps=24)
    trace_b, summary_b = module.run_search(max_n=500, max_steps=24)

    assert trace_a == trace_b
    assert summary_a == summary_b


def test_refined_harness_beats_baseline_on_full_surface():
    """The refined family should improve over the pushed 70/980 one-step baseline."""
    module = load_module("pgs_semiprime_backward_refined_transition_law_search", REFINED_PATH)
    _trace, summary = module.run_search(max_n=5000, max_steps=24)

    assert summary["best_law"] == "containing_if_prev_early_largegap_14"
    assert summary["best_lane_success_count"] == 71
    assert summary["best_factor_reach_count"] == 0
    assert summary["baseline_best_lane_success_count"] == 70
    assert summary["improvement_over_baseline"] == 1
    assert summary["searched_family_falsified"] is False


def test_cli_writes_lf_terminated_refined_summary(tmp_path: Path):
    """The refined CLI should emit LF-terminated summary JSON only."""
    module = load_module("pgs_semiprime_backward_refined_transition_law_search", REFINED_PATH)
    exit_code = module.main(["--max-n", "500", "--max-steps", "24", "--output-dir", str(tmp_path)])

    assert exit_code == 0

    summary_path = tmp_path / module.SUMMARY_FILENAME
    assert summary_path.exists()
    raw = summary_path.read_bytes()
    assert raw.endswith(b"\n")
    assert b"\r\n" not in raw

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["best_lane_success_count"] == 8
    assert summary["baseline_best_lane_success_count"] == 70
    assert summary["searched_family_falsified"] is False
