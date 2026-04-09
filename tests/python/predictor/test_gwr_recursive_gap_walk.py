"""Tests for the recursive GWR gap-walk prototype."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "benchmarks" / "python" / "predictor" / "gwr_recursive_gap_walk.py"


def load_module():
    """Load the recursive gap-walk script from its file path."""
    spec = importlib.util.spec_from_file_location("gwr_recursive_gap_walk", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load gwr_recursive_gap_walk module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_gap_state_extracts_exact_d4_corridor():
    """A fixed gap should expose its exact d=4 corridor geometry."""
    module = load_module()
    state = module.gap_state(13, 17)

    assert state["gap_width"] == 4
    assert state["interior_count"] == 3
    assert state["dmin"] == 4
    assert state["gap_has_d4"] is True
    assert state["last_pre_gap_d4"] == 10
    assert state["first_in_gap_d4"] == 14
    assert state["last_in_gap_d4"] == 15
    assert state["d4_corridor_start"] == 11
    assert state["d4_corridor_end"] == 15
    assert state["d4_corridor_width"] == 5


def test_exact_recursive_gap_step_hands_off_one_known_gap_to_the_next():
    """One recursive step should predict a next prime and derive the next gap from it."""
    module = load_module()
    row = module.gwr_recursive_gap_step(6, 13, 17)

    assert row["current_gap_index"] == 6
    assert row["next_gap_index"] == 8
    assert row["current_left_prime"] == 13
    assert row["current_right_prime"] == 17
    assert row["localizer_seed"] == 17
    assert row["localizer_divisor_target"] == 4
    assert row["localizer_witness"] == 21
    assert row["next_left_prime"] == 19
    assert row["next_right_prime"] == 23
    assert row["next_gap_width"] == 4
    assert row["next_gap_has_d4"] is True
    assert row["next_d4_corridor_start"] == 16
    assert row["recovery_mode"] == "witness"
    assert row["recovered_next_prime"] == 23
    assert row["recovery_divisor_target"] == 4
    assert row["recovery_seed"] == 16
    assert row["recovery_witness"] == 21
    assert row["recovery_exact"] is True
    assert row["exact_immediate_next_right_prime"] == 19
    assert row["exact_immediate_hit"] is False
    assert row["skipped_gap_count"] == 1
    assert row["next_gap_right_offset_from_current_right"] == 6


def test_forward_localizer_hits_the_immediate_next_gap_when_d4_is_present():
    """The dominant d=4 localizer can land on the true adjacent next gap."""
    module = load_module()
    row = module.gwr_recursive_gap_step(10, 29, 31)

    assert row["current_gap_index"] == 10
    assert row["next_gap_index"] == 11
    assert row["next_left_prime"] == 31
    assert row["next_right_prime"] == 37
    assert row["exact_immediate_next_right_prime"] == 37
    assert row["exact_immediate_hit"] is True
    assert row["skipped_gap_count"] == 0


def test_recursive_walk_builds_one_contiguous_gap_chain():
    """Each row should hand its predicted next gap directly to the next row as current state."""
    module = load_module()
    rows, summary = module.run_recursive_walk(6, 4)

    assert len(rows) == 4
    assert summary["predicted_chain_is_self_feeding"] is True
    assert len(rows[1:]) == len(rows) - 1
    for left_row, right_row in zip(rows, rows[1:]):
        assert left_row["next_gap_index"] == right_row["current_gap_index"]
        assert left_row["next_left_prime"] == right_row["current_left_prime"]
        assert left_row["next_right_prime"] == right_row["current_right_prime"]
        assert left_row["recovered_next_prime"] == right_row["current_right_prime"]


def test_recover_prime_from_exact_gap_uses_witness_on_nonempty_gap():
    """A nonempty gap should recover its right endpoint from the leftmost exact corridor seed."""
    module = load_module()
    recovery = module.recover_prime_from_exact_gap(13, 17)

    assert recovery["recovery_mode"] == "witness"
    assert recovery["recovered_prime"] == 17
    assert recovery["recovery_divisor_target"] == 4
    assert recovery["recovery_seed"] == 11
    assert recovery["recovery_witness"] == 14
    assert recovery["recovery_corridor_start"] == 11
    assert recovery["recovery_corridor_end"] == 15
    assert recovery["recovery_corridor_width"] == 5
    assert recovery["recovery_exact"] is True


def test_recover_prime_from_exact_gap_uses_witness_for_width_two_gap():
    """A width-two gap still has one interior carrier and recovers by witness."""
    module = load_module()
    recovery = module.recover_prime_from_exact_gap(17, 19)

    assert recovery["recovery_mode"] == "witness"
    assert recovery["recovered_prime"] == 19
    assert recovery["recovery_divisor_target"] == 6
    assert recovery["recovery_seed"] == 13
    assert recovery["recovery_witness"] == 18
    assert recovery["recovery_corridor_start"] == 13
    assert recovery["recovery_corridor_end"] == 18
    assert recovery["recovery_corridor_width"] == 6
    assert recovery["recovery_exact"] is True


def test_recover_prime_from_exact_gap_uses_endpoint_only_for_two_three():
    """The special gap (2, 3) is the endpoint-only recovery case."""
    module = load_module()
    recovery = module.recover_prime_from_exact_gap(2, 3)

    assert recovery["recovery_mode"] == "empty_gap_endpoint"
    assert recovery["recovered_prime"] == 3
    assert recovery["recovery_divisor_target"] is None
    assert recovery["recovery_seed"] is None
    assert recovery["recovery_witness"] is None
    assert recovery["recovery_exact"] is True


def test_entry_point_writes_summary_and_detail_artifacts(tmp_path):
    """The CLI entry point should emit JSON and CSV artifacts."""
    module = load_module()

    assert module.main(["--output-dir", str(tmp_path), "--start-gap-index", "6", "--steps", "4"]) == 0

    summary_path = tmp_path / "gwr_recursive_gap_walk_summary.json"
    detail_path = tmp_path / "gwr_recursive_gap_walk_details.csv"
    assert summary_path.exists()
    assert detail_path.exists()

    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["start_gap_index"] == 6
    assert payload["steps"] == 4
    assert payload["predicted_chain_is_self_feeding"] is True
    assert payload["recovery_exact_rate"] == 1.0
