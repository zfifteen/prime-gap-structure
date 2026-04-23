"""Tests for the missed-entry miner and tighter entry law search."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MINER_PATH = (
    ROOT
    / "benchmarks"
    / "python"
    / "predictor"
    / "pgs_semiprime_backward_missed_entry_pattern_miner.py"
)
TIGHTER_PATH = (
    ROOT
    / "benchmarks"
    / "python"
    / "predictor"
    / "pgs_semiprime_backward_tighter_entry_law_search.py"
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


def test_missed_entry_miner_pins_current_bottleneck():
    """The missed-entry miner should pin the exact current opportunity and miss surface."""
    module = load_module("pgs_semiprime_backward_missed_entry_pattern_miner", MINER_PATH)
    summary = module.mine_missed_patterns(max_n=5000)

    assert summary["immediate_good_entry_count"] == 153
    assert summary["missed_good_entry_count"] == 82
    assert summary["top_switch_rows"][0]["selected_shape"] == ["previous", True, True, 8, 2]
    assert summary["top_switch_rows"][0]["alternative_shape"] == ["previous", False, False, 8, 4]
    assert summary["top_switch_rows"][0]["alt_lane_success_count"] == 5


def test_tighter_harness_is_deterministic_on_reduced_surface():
    """The tighter reduced summary should be deterministic."""
    module = load_module("pgs_semiprime_backward_tighter_entry_law_search", TIGHTER_PATH)
    trace_a, summary_a = module.run_search(max_n=500, max_steps=24)
    trace_b, summary_b = module.run_search(max_n=500, max_steps=24)

    assert trace_a == trace_b
    assert summary_a == summary_b


def test_tighter_harness_beats_refined_baseline_on_full_surface():
    """The exact-shape tighter family should improve over the pushed 71/980 refined baseline."""
    module = load_module("pgs_semiprime_backward_tighter_entry_law_search", TIGHTER_PATH)
    _trace, summary = module.run_search(max_n=5000, max_steps=24)

    assert summary["best_law"] == "exact_shape_entry_switch"
    assert summary["best_lane_success_count"] == 84
    assert summary["best_factor_reach_count"] == 0
    assert summary["baseline_best_lane_success_count"] == 71
    assert summary["improvement_over_baseline"] == 13
    assert summary["searched_family_falsified"] is False


def test_cli_writes_lf_terminated_tighter_summary(tmp_path: Path):
    """The tighter CLI should emit LF-terminated summary JSON only."""
    module = load_module("pgs_semiprime_backward_tighter_entry_law_search", TIGHTER_PATH)
    exit_code = module.main(["--max-n", "500", "--max-steps", "24", "--output-dir", str(tmp_path)])

    assert exit_code == 0

    summary_path = tmp_path / module.SUMMARY_FILENAME
    assert summary_path.exists()
    raw = summary_path.read_bytes()
    assert raw.endswith(b"\n")
    assert b"\r\n" not in raw

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["best_lane_success_count"] == 10
    assert summary["baseline_best_lane_success_count"] == 71
    assert summary["searched_family_falsified"] is False
