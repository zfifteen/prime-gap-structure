#!/usr/bin/env python3
"""Measure whether the best hidden state creates real compression in the reduced gap engine."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Callable, Hashable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from hourly_research_relay_common import (
    ROOT,
    append_jsonl_row,
    prepare_task_branch,
    read_last_jsonl_row,
    remote_json,
    run_git,
    stage_commit_push,
    utc_timestamp_compact,
    utc_timestamp_iso,
    write_json,
)


DEFAULT_OUTPUT_DIR = ROOT / "output"
DEFAULT_DETAIL_CSV = ROOT / "output" / "gwr_dni_gap_type_catalog_details.csv"
DEFAULT_TRAIN_MIN_POWER = 7
DEFAULT_TRAIN_MAX_POWER = 17
DEFAULT_REFERENCE_MIN_POWER = 12
DEFAULT_REFERENCE_MAX_POWER = 18
DEFAULT_SYNTHETIC_LENGTH = 1_000_000
DEFAULT_WINDOW_LENGTH = 256
DEFAULT_MOD_CYCLE_LENGTH = 8
TASK_BRANCH = "codex/research-compression-shock-probe"
FIRST_LAUNCH_BASE_BRANCH = "origin/codex/even-winner-next-opening-probe"
HIDDEN_STATE_REMOTE_BRANCH = "origin/codex/research-hidden-state-miner"
HIDDEN_STATE_SUMMARY_REMOTE_PATH = "output/gwr_hidden_state_miner_summary.json"
SUMMARY_PATH = ROOT / "output" / "gwr_compression_shock_probe_summary.json"
MODELS_CSV_PATH = ROOT / "output" / "gwr_compression_shock_probe_models.csv"
HISTORY_PATH = ROOT / "output" / "gwr_compression_shock_probe_history.jsonl"
PLOT_PATH = ROOT / "output" / "gwr_compression_shock_probe_overview.png"
FINDINGS_PATH = ROOT / "gwr" / "findings" / "compression_shock_probe_findings.md"
TEST_PATH = ROOT / "tests" / "python" / "predictor" / "test_gwr_compression_shock_probe.py"
GEN_PROBE_PATH = Path(__file__).with_name("gwr_dni_gap_type_generative_probe.py")
SCHED_PROBE_PATH = Path(__file__).with_name("gwr_dni_gap_type_scheduler_probe.py")
HYBRID_PROBE_PATH = Path(__file__).with_name("gwr_dni_gap_type_hybrid_scheduler_probe.py")
HIDDEN_STATE_MINER_PATH = Path(__file__).with_name("gwr_hidden_state_miner.py")


def load_module(module_path: Path, module_name: str):
    """Load one sibling module from its file path."""
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


GEN_PROBE = load_module(GEN_PROBE_PATH, "gwr_dni_gap_type_generative_probe_compression")
SCHED_PROBE = load_module(SCHED_PROBE_PATH, "gwr_dni_gap_type_scheduler_probe_compression")
HYBRID_PROBE = load_module(HYBRID_PROBE_PATH, "gwr_dni_gap_type_hybrid_scheduler_probe_compression")
HIDDEN_STATE_MINER = load_module(HIDDEN_STATE_MINER_PATH, "gwr_hidden_state_miner_compression")
TRIAD_SET = set(GEN_PROBE.TRIAD_STATES)
MODEL_ORDER = (
    "first_order_rotor",
    "second_order_rotor",
    "lag2_state_scheduler",
    "mod_cycle_scheduler",
    "hybrid_lag2_mod8_scheduler",
    "hybrid_lag2_mod8_reset_hdiv_scheduler",
    "hybrid_lag2_mod8_reset_nontriad_scheduler",
    "hidden_state_augmented_rotor",
    "hidden_state_phase_scheduler",
    "hidden_state_reset_scheduler",
)
MODEL_COLORS = {
    "first_order_rotor": "#8c8c8c",
    "second_order_rotor": "#dd8452",
    "lag2_state_scheduler": "#4c72b0",
    "mod_cycle_scheduler": "#8172b2",
    "hybrid_lag2_mod8_scheduler": "#55a868",
    "hybrid_lag2_mod8_reset_hdiv_scheduler": "#c44e52",
    "hybrid_lag2_mod8_reset_nontriad_scheduler": "#937860",
    "hidden_state_augmented_rotor": "#2a9d8f",
    "hidden_state_phase_scheduler": "#264653",
    "hidden_state_reset_scheduler": "#e76f51",
}


Payload = tuple[str, str, int, str, str]


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Compare standard and hidden-state-augmented deterministic machines "
            "on the repo's current reduced gap-type concentration surface."
        ),
    )
    parser.add_argument("--detail-csv", type=Path, default=DEFAULT_DETAIL_CSV)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--train-min-power", type=int, default=DEFAULT_TRAIN_MIN_POWER)
    parser.add_argument("--train-max-power", type=int, default=DEFAULT_TRAIN_MAX_POWER)
    parser.add_argument("--reference-min-power", type=int, default=DEFAULT_REFERENCE_MIN_POWER)
    parser.add_argument("--reference-max-power", type=int, default=DEFAULT_REFERENCE_MAX_POWER)
    parser.add_argument("--synthetic-length", type=int, default=DEFAULT_SYNTHETIC_LENGTH)
    parser.add_argument("--window-length", type=int, default=DEFAULT_WINDOW_LENGTH)
    parser.add_argument("--mod-cycle-length", type=int, default=DEFAULT_MOD_CYCLE_LENGTH)
    return parser


def power_surface_label(power: int) -> str:
    """Return the sampled decade display label."""
    return f"10^{power}"


def payload_state(payload: Payload) -> str:
    """Return the reduced state from one payload."""
    return payload[0]


def payload_peak_offset(payload: Payload) -> int:
    """Return the winning peak offset from one payload."""
    return int(payload[2])


def payload_family(payload: Payload) -> str:
    """Return the carrier family from one payload."""
    return payload[3]


def payload_winner_parity(payload: Payload) -> str:
    """Return the winner parity from one payload."""
    return payload[4]


def winner_parity_from_row(row: dict[str, str]) -> str:
    """Return the parity of the winning simplest number."""
    return "even" if int(row["winner"]) % 2 == 0 else "odd"


def extended_payload(row: dict[str, str]) -> Payload:
    """Return one payload key that preserves the emitted row features used downstream."""
    return (
        GEN_PROBE.reduced_state(row),
        str(row["type_key"]),
        int(row["next_peak_offset"]),
        str(row["carrier_family"]),
        winner_parity_from_row(row),
    )


def synthetic_row(step_index: int, payload: Payload) -> dict[str, object]:
    """Return one synthetic row payload."""
    return {
        "step_index": step_index,
        "state": payload_state(payload),
        "type_key": payload[1],
        "next_peak_offset": payload_peak_offset(payload),
        "carrier_family": payload_family(payload),
        "winner_parity": payload_winner_parity(payload),
    }


def row_d_bucket(row: dict[str, object]) -> str:
    """Return the d-bucket label embedded inside one reduced state."""
    return str(row["state"]).split("|", 1)[1]


def row_feature_record(
    previous_row: dict[str, object] | None,
    current_row: dict[str, object],
) -> dict[str, object]:
    """Return the hidden-state feature record for one current row."""
    return {
        "current_winner_parity": str(current_row["winner_parity"]),
        "current_winner_offset": int(current_row["next_peak_offset"]),
        "current_carrier_family": str(current_row["carrier_family"]),
        "current_d_bucket": row_d_bucket(current_row),
        "previous_reduced_state": "START" if previous_row is None else str(previous_row["state"]),
        "previous_winner_parity": "START" if previous_row is None else str(previous_row["winner_parity"]),
        "previous_carrier_family": "START" if previous_row is None else str(previous_row["carrier_family"]),
    }


def candidate_fields(candidate_id: str) -> tuple[str, ...]:
    """Return the primitive field tuple for one candidate id."""
    return dict(HIDDEN_STATE_MINER.CANDIDATE_SPECS)[candidate_id]


def candidate_uses_previous_winner_parity(candidate_id: str) -> bool:
    """Return whether the candidate needs previous-row winner parity."""
    return "previous_winner_parity" in candidate_fields(candidate_id)


def candidate_label(
    previous_row: dict[str, object] | None,
    current_row: dict[str, object],
    candidate_id: str,
) -> str:
    """Return the candidate label for one previous/current row pair."""
    return HIDDEN_STATE_MINER.candidate_value(
        row_feature_record(previous_row, current_row),
        candidate_id,
    )


def load_hidden_state_summary() -> tuple[dict[str, object] | None, str | None, str | None]:
    """Return the upstream hidden-state summary and commit, or the explicit blocker."""
    try:
        summary = remote_json(HIDDEN_STATE_REMOTE_BRANCH, HIDDEN_STATE_SUMMARY_REMOTE_PATH)
        source_commit = run_git("rev-parse", HIDDEN_STATE_REMOTE_BRANCH)
    except subprocess.CalledProcessError:
        return None, None, "missing upstream hidden-state summary"
    best_candidate = summary.get("best_candidate")
    if not isinstance(best_candidate, dict) or "candidate_id" not in best_candidate:
        return None, source_commit, "hidden-state summary does not name a best candidate"
    return summary, source_commit, None


def pruned_payload_counter(
    counter: dict[Hashable, Counter[Payload]],
    successor_context: Callable[[Hashable, Payload], Hashable],
) -> dict[Hashable, Counter[Payload]]:
    """Prune one payload-transition surface to the forward-staying context set."""
    active = set(counter)
    while True:
        next_active = {
            context
            for context in active
            if any(successor_context(context, payload) in active for payload in counter[context])
        }
        if next_active == active:
            break
        active = next_active

    pruned: dict[Hashable, Counter[Payload]] = {}
    for context in sorted(active):
        kept = Counter()
        for payload, count in counter[context].items():
            if successor_context(context, payload) in active:
                kept[payload] += count
        if kept:
            pruned[context] = kept
    return pruned


def choose_start_context(
    start_counter: Counter[Hashable],
    pruned_counter: dict[Hashable, Counter[Payload]],
) -> Hashable:
    """Choose the dominant valid start context."""
    candidates = [
        (context, count)
        for context, count in start_counter.items()
        if context in pruned_counter
    ]
    if candidates:
        return max(candidates, key=lambda item: (item[1], item[0]))[0]
    return max(pruned_counter, key=lambda context: (sum(pruned_counter[context].values()), context))


def choose_start_value(
    start_counter: Counter[Hashable],
    is_valid: Callable[[Hashable], bool],
) -> Hashable:
    """Choose the dominant valid start payload tuple."""
    valid_rows = [(value, count) for value, count in start_counter.items() if is_valid(value)]
    if not valid_rows:
        raise ValueError("no valid start value remains after pruning")
    return max(valid_rows, key=lambda item: (item[1], item[0]))[0]


def build_training_frame(
    detail_csv: Path,
    train_surfaces: list[str],
    reference_surfaces: list[str],
) -> dict[str, object]:
    """Build the shared training/reference frame used by all compression models."""
    rows = GEN_PROBE.load_rows(detail_csv)
    rows_by_surface = GEN_PROBE.surface_rows(rows)
    core_states = GEN_PROBE.persistent_core_states(rows_by_surface, train_surfaces)
    segments = GEN_PROBE.contiguous_core_segments(rows_by_surface, train_surfaces, core_states)
    state_counter: Counter[str] = Counter()
    emission_counter_extended: dict[str, Counter[Payload]] = defaultdict(Counter)
    for segment in segments:
        for row in segment:
            state = GEN_PROBE.reduced_state(row)
            state_counter[state] += 1
            emission_counter_extended[state][extended_payload(row)] += 1

    real_rows: list[dict[str, str]] = []
    for surface_label in reference_surfaces:
        real_rows.extend(
            row
            for row in rows_by_surface[surface_label]
            if GEN_PROBE.reduced_state(row) in core_states
        )
    real_family_distribution = GEN_PROBE.distribution([row["carrier_family"] for row in real_rows])
    real_peak_distribution = GEN_PROBE.distribution([int(row["next_peak_offset"]) for row in real_rows])
    real_higher_divisor_share = (
        sum(1 for row in real_rows if "higher_divisor" in row["carrier_family"]) / len(real_rows)
    )
    real_window_concentrations = SCHED_PROBE.ENGINE_DECODE.pooled_real_concentrations(
        rows_by_surface,
        reference_surfaces,
        core_states,
    )
    return {
        "rows_by_surface": rows_by_surface,
        "core_states": core_states,
        "segments": segments,
        "state_counter": state_counter,
        "emission_counter_extended": emission_counter_extended,
        "real_family_distribution": real_family_distribution,
        "real_peak_distribution": real_peak_distribution,
        "real_higher_divisor_share": real_higher_divisor_share,
        "real_window_concentrations": real_window_concentrations,
    }


def evaluate_synthetic_rows(
    synthetic_rows: list[dict[str, object]],
    real_window_concentrations: dict[str, float],
    real_family_distribution: dict[str, float],
    real_peak_distribution: dict[int, float],
    real_higher_divisor_share: float,
    window_length: int,
) -> dict[str, object]:
    """Evaluate one synthetic emitted row stream against the real reference surface."""
    states = [str(row["state"]) for row in synthetic_rows]
    full_walk_concentrations = {
        "one_step": SCHED_PROBE.ENGINE_DECODE.higher_order_top_successor_share(states, 1),
        "two_step": SCHED_PROBE.ENGINE_DECODE.higher_order_top_successor_share(states, 2),
        "three_step": SCHED_PROBE.ENGINE_DECODE.higher_order_top_successor_share(states, 3),
    }
    pooled_window_concentrations = SCHED_PROBE.windowed_concentrations(states, window_length)
    family_distribution = GEN_PROBE.distribution([str(row["carrier_family"]) for row in synthetic_rows])
    peak_distribution = GEN_PROBE.distribution([int(row["next_peak_offset"]) for row in synthetic_rows])
    higher_divisor_share = (
        sum(1 for row in synthetic_rows if "higher_divisor" in str(row["carrier_family"]))
        / len(synthetic_rows)
    )
    return {
        "pooled_window_concentrations": pooled_window_concentrations,
        "pooled_window_concentration_l1": SCHED_PROBE.concentration_l1(
            pooled_window_concentrations,
            real_window_concentrations,
        ),
        "full_walk_concentrations": full_walk_concentrations,
        "family_l1_to_real_pool": GEN_PROBE.l1_distance(family_distribution, real_family_distribution),
        "peak_offset_l1_to_real_pool": GEN_PROBE.l1_distance(peak_distribution, real_peak_distribution),
        "higher_divisor_share": higher_divisor_share,
        "higher_divisor_share_error": abs(higher_divisor_share - real_higher_divisor_share),
    }


def emit_standard_rows(states: list[str], emission_counter_extended: dict[str, Counter[Payload]]) -> list[dict[str, object]]:
    """Emit one deterministic row stream from a state sequence."""
    rotors = {
        state: GEN_PROBE.Rotor(GEN_PROBE.balanced_cycle(counter))
        for state, counter in emission_counter_extended.items()
    }
    return [
        synthetic_row(index + 1, rotors[state].next())
        for index, state in enumerate(states)
    ]


def simulate_first_order_payloads(
    first_order_counter: dict[str, Counter[Payload]],
    start_payload: Payload,
    synthetic_length: int,
) -> list[dict[str, object]]:
    """Emit one deterministic first-order payload stream."""
    transition_rotors = {
        state: GEN_PROBE.Rotor(GEN_PROBE.balanced_cycle(counter))
        for state, counter in first_order_counter.items()
    }
    rows = [synthetic_row(1, start_payload)]
    current_state = payload_state(start_payload)
    while len(rows) < synthetic_length:
        next_payload = transition_rotors[current_state].next()
        rows.append(synthetic_row(len(rows) + 1, next_payload))
        current_state = payload_state(next_payload)
    return rows


def build_first_order_model(
    segments: list[list[dict[str, str]]],
    synthetic_length: int,
) -> tuple[list[dict[str, object]], int]:
    """Build and simulate the first-order rotor."""
    counter: dict[str, Counter[Payload]] = defaultdict(Counter)
    start_counter: Counter[Payload] = Counter()
    for segment in segments:
        payloads = [extended_payload(row) for row in segment]
        if not payloads:
            continue
        start_counter[payloads[0]] += 1
        for current_payload, next_payload in zip(payloads, payloads[1:]):
            counter[payload_state(current_payload)][next_payload] += 1
    pruned = pruned_payload_counter(counter, lambda _context, payload: payload_state(payload))
    start_payload = choose_start_value(start_counter, lambda payload: payload_state(payload) in pruned)
    return simulate_first_order_payloads(pruned, start_payload, synthetic_length), len(pruned)


def build_second_order_model(
    segments: list[list[dict[str, str]]],
    synthetic_length: int,
) -> tuple[list[dict[str, object]], int]:
    """Build and simulate the second-order rotor."""
    support = GEN_PROBE.build_training_support(segments)
    states = SCHED_PROBE.simulate_second_order(support, synthetic_length)
    emission_counter_extended: dict[str, Counter[Payload]] = defaultdict(Counter)
    for segment in segments:
        for row in segment:
            emission_counter_extended[GEN_PROBE.reduced_state(row)][extended_payload(row)] += 1
    return emit_standard_rows(states, emission_counter_extended), len(support["second_order_counter"])


def build_lag2_state_model(
    segments: list[list[dict[str, str]]],
    synthetic_length: int,
    emission_counter_extended: dict[str, Counter[Payload]],
) -> tuple[list[dict[str, object]], int]:
    """Build and simulate the lag-2 scheduler."""
    counter, start_context = SCHED_PROBE.build_third_order_support(segments)
    states = SCHED_PROBE.simulate_third_order(counter, start_context, synthetic_length)
    return emit_standard_rows(states, emission_counter_extended), len(counter)


def build_mod_cycle_model(
    segments: list[list[dict[str, str]]],
    synthetic_length: int,
    mod_cycle_length: int,
    emission_counter_extended: dict[str, Counter[Payload]],
) -> tuple[list[dict[str, object]], int]:
    """Build and simulate the simple modulo scheduler."""
    counter, start_context = SCHED_PROBE.build_mod_cycle_support(segments, mod_cycle_length)
    states = SCHED_PROBE.simulate_mod_cycle(counter, start_context, synthetic_length, mod_cycle_length)
    return emit_standard_rows(states, emission_counter_extended), len(counter)


def build_hybrid_model(
    segments: list[list[dict[str, str]]],
    synthetic_length: int,
    mod_cycle_length: int,
    reset_mode: str,
    emission_counter_extended: dict[str, Counter[Payload]],
) -> tuple[list[dict[str, object]], int]:
    """Build and simulate one existing hybrid scheduler."""
    counter, start_context = HYBRID_PROBE.build_hybrid_support(
        segments,
        mod_cycle_length=mod_cycle_length,
        reset_mode=reset_mode,
    )
    states = HYBRID_PROBE.simulate_hybrid(
        transition_counter=counter,
        start_context=start_context,
        synthetic_length=synthetic_length,
        mod_cycle_length=mod_cycle_length,
        reset_mode=reset_mode,
    )
    return emit_standard_rows(states, emission_counter_extended), len(counter)


def hidden_context_suffix(
    previous_row: dict[str, object] | None,
    current_row: dict[str, object],
    candidate_id: str,
) -> tuple[object, ...]:
    """Return the extra hidden carry needed to advance the chosen candidate deterministically."""
    if not candidate_uses_previous_winner_parity(candidate_id):
        return ()
    return (
        "START" if previous_row is None else str(previous_row["winner_parity"]),
        str(current_row["winner_parity"]),
    )


def hidden_current_label(
    previous_row: dict[str, object] | None,
    current_row: dict[str, object],
    candidate_id: str,
) -> str:
    """Return the hidden-state label on the current row."""
    return candidate_label(previous_row, current_row, candidate_id)


def build_hidden_augmented_support(
    segments: list[list[dict[str, str]]],
    candidate_id: str,
) -> tuple[dict[Hashable, Counter[Payload]], Hashable]:
    """Build the hidden-state augmented second-order support."""
    counter: dict[Hashable, Counter[Payload]] = defaultdict(Counter)
    start_counter: Counter[Hashable] = Counter()
    for segment in segments:
        rows = [synthetic_row(index + 1, extended_payload(row)) for index, row in enumerate(segment)]
        if len(rows) < 3:
            continue
        start_context = (
            str(rows[0]["state"]),
            str(rows[1]["state"]),
            hidden_current_label(rows[0], rows[1], candidate_id),
            *hidden_context_suffix(rows[0], rows[1], candidate_id),
        )
        start_counter[start_context] += 1
        for left_row, current_row, next_row in zip(rows, rows[1:], rows[2:]):
            context = (
                str(left_row["state"]),
                str(current_row["state"]),
                hidden_current_label(left_row, current_row, candidate_id),
                *hidden_context_suffix(left_row, current_row, candidate_id),
            )
            counter[context][(
                str(next_row["state"]),
                str(next_row["type_key"]),
                int(next_row["next_peak_offset"]),
                str(next_row["carrier_family"]),
                str(next_row["winner_parity"]),
            )] += 1
    def successor(context: Hashable, payload: Payload) -> Hashable:
        left_state, current_state, _label, *suffix = context
        current_row = {
            "state": current_state,
            "next_peak_offset": payload_peak_offset(
                (
                    current_state,
                    "synthetic",
                    0,
                    current_state.split("|", 1)[0].split("_", 1)[1],
                    suffix[-1] if suffix else "odd",
                )
            ),
        }
        _ = left_state
        left_row = {
            "state": current_state,
        }
        previous_row = {
            "state": current_state,
            "winner_parity": suffix[-1] if suffix else "odd",
            "carrier_family": current_state.split("|", 1)[0].split("_", 1)[1],
        }
        next_row = synthetic_row(0, payload)
        next_label = candidate_label(previous_row, next_row, candidate_id)
        if candidate_uses_previous_winner_parity(candidate_id):
            return (
                current_state,
                payload_state(payload),
                next_label,
                suffix[-1],
                payload_winner_parity(payload),
            )
        return (
            current_state,
            payload_state(payload),
            next_label,
        )
    pruned = pruned_payload_counter(counter, successor)
    start_context = choose_start_context(start_counter, pruned)
    return pruned, start_context


def simulate_hidden_augmented(
    transition_counter: dict[Hashable, Counter[Payload]],
    start_context: Hashable,
    synthetic_length: int,
    candidate_id: str,
) -> list[dict[str, object]]:
    """Emit the hidden-state augmented rotor."""
    transition_rotors = {
        context: GEN_PROBE.Rotor(GEN_PROBE.balanced_cycle(counter))
        for context, counter in transition_counter.items()
    }
    left_state, current_state, current_label, *suffix = start_context
    if candidate_uses_previous_winner_parity(candidate_id):
        left_winner_parity, current_winner_parity = suffix
    else:
        left_winner_parity = "START"
        current_winner_parity = "odd"
    left_row = {
        "state": left_state,
        "next_peak_offset": 0,
        "carrier_family": left_state.split("|", 1)[0].split("_", 1)[1],
        "winner_parity": left_winner_parity,
    }
    current_row = {
        "state": current_state,
        "next_peak_offset": 0,
        "carrier_family": current_state.split("|", 1)[0].split("_", 1)[1],
        "winner_parity": current_winner_parity,
    }
    rows = [left_row, current_row]
    _ = current_label
    while len(rows) < synthetic_length:
        context = (
            str(rows[-2]["state"]),
            str(rows[-1]["state"]),
            candidate_label(rows[-2], rows[-1], candidate_id),
            *hidden_context_suffix(rows[-2], rows[-1], candidate_id),
        )
        next_payload = transition_rotors[context].next()
        rows.append(synthetic_row(len(rows) + 1, next_payload))
    return rows


def build_hidden_phase_support(
    segments: list[list[dict[str, str]]],
    candidate_id: str,
) -> tuple[dict[Hashable, Counter[Payload]], Hashable]:
    """Build the hidden-label phase scheduler support."""
    counter: dict[Hashable, Counter[Payload]] = defaultdict(Counter)
    start_counter: Counter[Hashable] = Counter()
    for segment in segments:
        rows = [synthetic_row(index + 1, extended_payload(row)) for index, row in enumerate(segment)]
        if len(rows) < 3:
            continue
        start_context = (
            "START",
            str(rows[0]["state"]),
            str(rows[1]["state"]),
            *hidden_context_suffix(rows[0], rows[1], candidate_id),
        )
        start_counter[start_context] += 1
        for left_row, current_row, next_row in zip(rows, rows[1:], rows[2:]):
            previous_row = None if left_row["step_index"] == 1 else rows[int(left_row["step_index"]) - 2]
            phase_label = "START" if previous_row is None else candidate_label(previous_row, left_row, candidate_id)
            context = (
                phase_label,
                str(left_row["state"]),
                str(current_row["state"]),
                *hidden_context_suffix(left_row, current_row, candidate_id),
            )
            counter[context][(
                str(next_row["state"]),
                str(next_row["type_key"]),
                int(next_row["next_peak_offset"]),
                str(next_row["carrier_family"]),
                str(next_row["winner_parity"]),
            )] += 1
    def successor(context: Hashable, payload: Payload) -> Hashable:
        _phase_label, left_state, current_state, *suffix = context
        current_row = {
            "state": current_state,
            "next_peak_offset": 0,
            "carrier_family": current_state.split("|", 1)[0].split("_", 1)[1],
            "winner_parity": suffix[-1] if suffix else "odd",
        }
        left_row = {
            "state": left_state,
            "next_peak_offset": 0,
            "carrier_family": left_state.split("|", 1)[0].split("_", 1)[1],
            "winner_parity": suffix[0] if len(suffix) == 2 else "START",
        }
        current_label = candidate_label(left_row, current_row, candidate_id)
        if candidate_uses_previous_winner_parity(candidate_id):
            return (
                current_label,
                current_state,
                payload_state(payload),
                suffix[-1],
                payload_winner_parity(payload),
            )
        return (
            current_label,
            current_state,
            payload_state(payload),
        )
    pruned = pruned_payload_counter(counter, successor)
    start_context = choose_start_context(start_counter, pruned)
    return pruned, start_context


def simulate_hidden_phase(
    transition_counter: dict[Hashable, Counter[Payload]],
    start_context: Hashable,
    synthetic_length: int,
    candidate_id: str,
) -> list[dict[str, object]]:
    """Emit the hidden-label phase scheduler."""
    transition_rotors = {
        context: GEN_PROBE.Rotor(GEN_PROBE.balanced_cycle(counter))
        for context, counter in transition_counter.items()
    }
    _phase_label, left_state, current_state, *suffix = start_context
    left_winner_parity = suffix[0] if len(suffix) == 2 else "START"
    current_winner_parity = suffix[-1] if suffix else "odd"
    rows = [
        {
            "step_index": 1,
            "state": left_state,
            "type_key": "synthetic_start",
            "next_peak_offset": 0,
            "carrier_family": left_state.split("|", 1)[0].split("_", 1)[1],
            "winner_parity": left_winner_parity,
        },
        {
            "step_index": 2,
            "state": current_state,
            "type_key": "synthetic_start",
            "next_peak_offset": 0,
            "carrier_family": current_state.split("|", 1)[0].split("_", 1)[1],
            "winner_parity": current_winner_parity,
        },
    ]
    while len(rows) < synthetic_length:
        previous_row = None if len(rows) < 3 else rows[-3]
        phase_label = "START" if previous_row is None else candidate_label(previous_row, rows[-2], candidate_id)
        context = (
            phase_label,
            str(rows[-2]["state"]),
            str(rows[-1]["state"]),
            *hidden_context_suffix(rows[-2], rows[-1], candidate_id),
        )
        next_payload = transition_rotors[context].next()
        rows.append(synthetic_row(len(rows) + 1, next_payload))
    return rows


def hidden_reset_phase(
    phase: int,
    current_label: str,
    reset_label: str,
    mod_cycle_length: int,
) -> int:
    """Advance the hidden reset scheduler phase."""
    if current_label == reset_label:
        return 0
    return (phase + 1) % mod_cycle_length


def build_hidden_reset_support(
    segments: list[list[dict[str, str]]],
    candidate_id: str,
    reset_label: str,
    mod_cycle_length: int,
) -> tuple[dict[Hashable, Counter[Payload]], Hashable]:
    """Build the hidden-label reset scheduler support."""
    counter: dict[Hashable, Counter[Payload]] = defaultdict(Counter)
    start_counter: Counter[Hashable] = Counter()
    for segment in segments:
        rows = [synthetic_row(index + 1, extended_payload(row)) for index, row in enumerate(segment)]
        if len(rows) < 3:
            continue
        phase = 0
        start_context = (
            phase,
            str(rows[0]["state"]),
            str(rows[1]["state"]),
            *hidden_context_suffix(rows[0], rows[1], candidate_id),
        )
        start_counter[start_context] += 1
        for left_row, current_row, next_row in zip(rows, rows[1:], rows[2:]):
            context = (
                phase,
                str(left_row["state"]),
                str(current_row["state"]),
                *hidden_context_suffix(left_row, current_row, candidate_id),
            )
            next_payload = (
                str(next_row["state"]),
                str(next_row["type_key"]),
                int(next_row["next_peak_offset"]),
                str(next_row["carrier_family"]),
                str(next_row["winner_parity"]),
            )
            counter[context][next_payload] += 1
            phase = hidden_reset_phase(
                phase=phase,
                current_label=candidate_label(left_row, current_row, candidate_id),
                reset_label=reset_label,
                mod_cycle_length=mod_cycle_length,
            )
    def successor(context: Hashable, payload: Payload) -> Hashable:
        phase, left_state, current_state, *suffix = context
        left_row = {
            "state": left_state,
            "next_peak_offset": 0,
            "carrier_family": left_state.split("|", 1)[0].split("_", 1)[1],
            "winner_parity": suffix[0] if len(suffix) == 2 else "START",
        }
        current_row = {
            "state": current_state,
            "next_peak_offset": 0,
            "carrier_family": current_state.split("|", 1)[0].split("_", 1)[1],
            "winner_parity": suffix[-1] if suffix else "odd",
        }
        current_label = candidate_label(left_row, current_row, candidate_id)
        next_phase = hidden_reset_phase(phase, current_label, reset_label, mod_cycle_length)
        if candidate_uses_previous_winner_parity(candidate_id):
            return (
                next_phase,
                current_state,
                payload_state(payload),
                suffix[-1],
                payload_winner_parity(payload),
            )
        return (
            next_phase,
            current_state,
            payload_state(payload),
        )
    pruned = pruned_payload_counter(counter, successor)
    start_context = choose_start_context(start_counter, pruned)
    return pruned, start_context


def simulate_hidden_reset(
    transition_counter: dict[Hashable, Counter[Payload]],
    start_context: Hashable,
    synthetic_length: int,
    candidate_id: str,
    reset_label: str,
    mod_cycle_length: int,
) -> list[dict[str, object]]:
    """Emit the hidden reset scheduler."""
    transition_rotors = {
        context: GEN_PROBE.Rotor(GEN_PROBE.balanced_cycle(counter))
        for context, counter in transition_counter.items()
    }
    phase, left_state, current_state, *suffix = start_context
    left_winner_parity = suffix[0] if len(suffix) == 2 else "START"
    current_winner_parity = suffix[-1] if suffix else "odd"
    rows = [
        {
            "step_index": 1,
            "state": left_state,
            "type_key": "synthetic_start",
            "next_peak_offset": 0,
            "carrier_family": left_state.split("|", 1)[0].split("_", 1)[1],
            "winner_parity": left_winner_parity,
        },
        {
            "step_index": 2,
            "state": current_state,
            "type_key": "synthetic_start",
            "next_peak_offset": 0,
            "carrier_family": current_state.split("|", 1)[0].split("_", 1)[1],
            "winner_parity": current_winner_parity,
        },
    ]
    while len(rows) < synthetic_length:
        context = (
            phase,
            str(rows[-2]["state"]),
            str(rows[-1]["state"]),
            *hidden_context_suffix(rows[-2], rows[-1], candidate_id),
        )
        next_payload = transition_rotors[context].next()
        current_label = candidate_label(rows[-2], rows[-1], candidate_id)
        rows.append(synthetic_row(len(rows) + 1, next_payload))
        phase = hidden_reset_phase(phase, current_label, reset_label, mod_cycle_length)
    return rows


def model_rows(
    frame: dict[str, object],
    hidden_state_summary: dict[str, object],
    synthetic_length: int,
    window_length: int,
    mod_cycle_length: int,
) -> list[dict[str, object]]:
    """Evaluate all standard and hidden-state-augmented models."""
    segments = frame["segments"]
    emission_counter_extended = frame["emission_counter_extended"]
    candidate_id = str(hidden_state_summary["best_candidate"]["candidate_id"])
    reset_label = str(hidden_state_summary["best_candidate"]["best_label"])
    builders: list[tuple[str, str, Callable[[], tuple[list[dict[str, object]], int]]]] = [
        (
            "first_order_rotor",
            "Baseline first-order rotor over reduced states.",
            lambda: build_first_order_model(segments, synthetic_length),
        ),
        (
            "second_order_rotor",
            "Baseline persistent second-order rotor.",
            lambda: build_second_order_model(segments, synthetic_length),
        ),
        (
            "lag2_state_scheduler",
            "Finite scheduler whose phase is the reduced state two steps back.",
            lambda: build_lag2_state_model(segments, synthetic_length, emission_counter_extended),
        ),
        (
            "mod_cycle_scheduler",
            f"Simple {mod_cycle_length}-phase modulo scheduler over the second-order core.",
            lambda: build_mod_cycle_model(
                segments,
                synthetic_length,
                mod_cycle_length,
                emission_counter_extended,
            ),
        ),
        (
            "hybrid_lag2_mod8_scheduler",
            f"Hybrid lag-2 plus {mod_cycle_length}-phase modulo scheduler with no explicit reset.",
            lambda: build_hybrid_model(
                segments,
                synthetic_length,
                mod_cycle_length,
                "none",
                emission_counter_extended,
            ),
        ),
        (
            "hybrid_lag2_mod8_reset_hdiv_scheduler",
            f"Hybrid lag-2 plus {mod_cycle_length}-phase modulo scheduler with higher-divisor resets.",
            lambda: build_hybrid_model(
                segments,
                synthetic_length,
                mod_cycle_length,
                "higher_divisor",
                emission_counter_extended,
            ),
        ),
        (
            "hybrid_lag2_mod8_reset_nontriad_scheduler",
            f"Hybrid lag-2 plus {mod_cycle_length}-phase modulo scheduler with non-triad resets.",
            lambda: build_hybrid_model(
                segments,
                synthetic_length,
                mod_cycle_length,
                "nontriad",
                emission_counter_extended,
            ),
        ),
        (
            "hidden_state_augmented_rotor",
            f"Second-order rotor with `{candidate_id}` as an extra hidden-state label.",
            lambda: (
                lambda counter, start: (
                    simulate_hidden_augmented(counter, start, synthetic_length, candidate_id),
                    len(counter),
                )
            )(*build_hidden_augmented_support(segments, candidate_id)),
        ),
        (
            "hidden_state_phase_scheduler",
            f"Lag-2 style scheduler whose phase is the previous `{candidate_id}` label.",
            lambda: (
                lambda counter, start: (
                    simulate_hidden_phase(counter, start, synthetic_length, candidate_id),
                    len(counter),
                )
            )(*build_hidden_phase_support(segments, candidate_id)),
        ),
        (
            "hidden_state_reset_scheduler",
            f"Hybrid reset scheduler whose reset trigger is the best `{candidate_id}` label `{reset_label}`.",
            lambda: (
                lambda counter, start: (
                    simulate_hidden_reset(
                        counter,
                        start,
                        synthetic_length,
                        candidate_id,
                        reset_label,
                        mod_cycle_length,
                    ),
                    len(counter),
                )
            )(*build_hidden_reset_support(segments, candidate_id, reset_label, mod_cycle_length)),
        ),
    ]
    rows: list[dict[str, object]] = []
    for model_id, description, builder in builders:
        synthetic_rows, effective_state_count = builder()
        metrics = evaluate_synthetic_rows(
            synthetic_rows=synthetic_rows,
            real_window_concentrations=frame["real_window_concentrations"],
            real_family_distribution=frame["real_family_distribution"],
            real_peak_distribution=frame["real_peak_distribution"],
            real_higher_divisor_share=frame["real_higher_divisor_share"],
            window_length=window_length,
        )
        rows.append(
            {
                "model_id": model_id,
                "description": description,
                "effective_state_count": int(effective_state_count),
                "pooled_window_concentration_l1": float(metrics["pooled_window_concentration_l1"]),
                "one_step_concentration": float(metrics["full_walk_concentrations"]["one_step"]),
                "two_step_concentration": float(metrics["full_walk_concentrations"]["two_step"]),
                "three_step_concentration": float(metrics["full_walk_concentrations"]["three_step"]),
                "family_l1_to_real_pool": float(metrics["family_l1_to_real_pool"]),
                "peak_offset_l1_to_real_pool": float(metrics["peak_offset_l1_to_real_pool"]),
                "higher_divisor_share_error": float(metrics["higher_divisor_share_error"]),
            }
        )
    return rows


def pareto_frontier(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    """Return the nondominated model frontier."""
    frontier: list[dict[str, object]] = []
    for row in rows:
        dominated = False
        for other in rows:
            if other["model_id"] == row["model_id"]:
                continue
            not_worse = (
                int(other["effective_state_count"]) <= int(row["effective_state_count"])
                and float(other["pooled_window_concentration_l1"]) <= float(row["pooled_window_concentration_l1"])
                and float(other["three_step_concentration"]) >= float(row["three_step_concentration"])
            )
            strictly_better = (
                int(other["effective_state_count"]) < int(row["effective_state_count"])
                or float(other["pooled_window_concentration_l1"]) < float(row["pooled_window_concentration_l1"])
                or float(other["three_step_concentration"]) > float(row["three_step_concentration"])
            )
            if not_worse and strictly_better:
                dominated = True
                break
        if not dominated:
            frontier.append(row)
    return sorted(
        frontier,
        key=lambda row: (
            int(row["effective_state_count"]),
            float(row["pooled_window_concentration_l1"]),
            -float(row["three_step_concentration"]),
            str(row["model_id"]),
        ),
    )


def select_shock_winner(rows: list[dict[str, object]]) -> tuple[dict[str, object] | None, str | None]:
    """Return the shock winner under the relay's explicit ranking rule."""
    by_id = {str(row["model_id"]): row for row in rows}
    baseline = by_id["second_order_rotor"]
    strict_improvers = [
        row
        for row in rows
        if float(row["pooled_window_concentration_l1"]) < float(baseline["pooled_window_concentration_l1"]) - 1e-12
        and float(row["three_step_concentration"]) > float(baseline["three_step_concentration"]) + 1e-12
    ]
    if strict_improvers:
        return min(
            strict_improvers,
            key=lambda row: (
                int(row["effective_state_count"]),
                float(row["pooled_window_concentration_l1"]),
                -float(row["three_step_concentration"]),
                str(row["model_id"]),
            ),
        ), None

    three_step_only = [
        row
        for row in rows
        if float(row["three_step_concentration"]) > float(baseline["three_step_concentration"]) + 1e-12
    ]
    if three_step_only:
        return min(
            three_step_only,
            key=lambda row: (
                int(row["effective_state_count"]),
                float(row["pooled_window_concentration_l1"]),
                -float(row["three_step_concentration"]),
                str(row["model_id"]),
            ),
        ), "no model improved both pooled L1 and three-step concentration over second_order_rotor"

    return None, "no model improved three-step concentration over second_order_rotor"


def write_models_csv(rows: list[dict[str, object]], csv_path: Path) -> None:
    """Write the model comparison table."""
    fieldnames = [
        "model_id",
        "effective_state_count",
        "pooled_window_concentration_l1",
        "one_step_concentration",
        "two_step_concentration",
        "three_step_concentration",
        "family_l1_to_real_pool",
        "peak_offset_l1_to_real_pool",
        "higher_divisor_share_error",
        "description",
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def build_overview_plot(summary: dict[str, object], plot_path: Path) -> None:
    """Render one compact compression overview plot."""
    rows = summary["models"]
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))

    axes[0].scatter(
        [int(row["effective_state_count"]) for row in rows],
        [float(row["pooled_window_concentration_l1"]) for row in rows],
        s=[70 + 180 * float(row["three_step_concentration"]) for row in rows],
        c=[MODEL_COLORS.get(str(row["model_id"]), "#4c72b0") for row in rows],
    )
    for row in rows:
        axes[0].annotate(
            str(row["model_id"]).replace("_scheduler", "").replace("_rotor", ""),
            (
                int(row["effective_state_count"]),
                float(row["pooled_window_concentration_l1"]),
            ),
            fontsize=8,
        )
    axes[0].set_xlabel("Effective state count")
    axes[0].set_ylabel("Pooled-window concentration L1")
    axes[0].set_title("Compression vs Fit")

    ordered = sorted(rows, key=lambda row: MODEL_ORDER.index(str(row["model_id"])))
    axes[1].bar(
        [str(row["model_id"]) for row in ordered],
        [float(row["three_step_concentration"]) for row in ordered],
        color=[MODEL_COLORS.get(str(row["model_id"]), "#4c72b0") for row in ordered],
    )
    axes[1].tick_params(axis="x", rotation=70)
    axes[1].set_ylabel("Three-step concentration")
    axes[1].set_title("Three-Step Concentration")
    fig.tight_layout()
    fig.savefig(plot_path, dpi=220)
    plt.close(fig)


def findings_markdown(summary: dict[str, object]) -> str:
    """Render the findings note."""
    if summary.get("blocked_reason") is not None:
        return "\n".join(
            [
                "# Compression Shock Probe Findings",
                "",
                f"This run blocked because `{summary['blocked_reason']}`.",
                "",
                "## Artifacts",
                "",
                "- [compression shock probe script](../../benchmarks/python/predictor/gwr_compression_shock_probe.py)",
                "- [summary JSON](../../output/gwr_compression_shock_probe_summary.json)",
                "- [history JSONL](../../output/gwr_compression_shock_probe_history.jsonl)",
            ]
        ) + "\n"

    shock_winner = summary.get("shock_winner")
    if shock_winner is None:
        opening = (
            "The best hidden-state candidate does not create extra three-step compression over "
            "the current second-order rotor on this surface."
        )
        interpretation = "The hidden state bloats the machine instead of compressing it."
    else:
        opening = (
            f"The smallest model that clears the compression rule is `{shock_winner['model_id']}` "
            f"with pooled-window concentration L1 `{shock_winner['pooled_window_concentration_l1']:.4f}` "
            f"and three-step concentration `{shock_winner['three_step_concentration']:.4f}`."
        )
        interpretation = (
            "This is real compression, not just machine bloat."
            if str(shock_winner["model_id"]).startswith("hidden_state_")
            else "The extra hidden state does not win; existing scheduler structure still dominates."
        )
    lines = [
        "# Compression Shock Probe Findings",
        "",
        opening,
        "",
        interpretation,
        "",
        "## Upstream Hidden State",
        "",
        f"- candidate id: `{summary['hidden_state_candidate_id']}`",
        f"- source commit: `{summary['hidden_state_source_commit']}`",
        "",
        "## Frontier",
        "",
    ]
    for row in summary["pareto_frontier"]:
        lines.append(
            f"- `{row['model_id']}`: states `{row['effective_state_count']}`, pooled L1 `{row['pooled_window_concentration_l1']:.4f}`, three-step `{row['three_step_concentration']:.4f}`"
        )
    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            "- [compression shock probe script](../../benchmarks/python/predictor/gwr_compression_shock_probe.py)",
            "- [summary JSON](../../output/gwr_compression_shock_probe_summary.json)",
            "- [model CSV](../../output/gwr_compression_shock_probe_models.csv)",
            "- [history JSONL](../../output/gwr_compression_shock_probe_history.jsonl)",
            "- ![Compression shock overview](../../output/gwr_compression_shock_probe_overview.png)",
        ]
    )
    return "\n".join(lines) + "\n"


def summarize(
    frame: dict[str, object],
    hidden_state_summary: dict[str, object],
    hidden_state_source_commit: str,
    synthetic_length: int,
    window_length: int,
    mod_cycle_length: int,
) -> dict[str, object]:
    """Build the compression shock summary."""
    rows = model_rows(
        frame=frame,
        hidden_state_summary=hidden_state_summary,
        synthetic_length=synthetic_length,
        window_length=window_length,
        mod_cycle_length=mod_cycle_length,
    )
    rows = sorted(rows, key=lambda row: MODEL_ORDER.index(str(row["model_id"])))
    shock_winner, negative_result = select_shock_winner(rows)
    return {
        "hidden_state_source_commit": hidden_state_source_commit,
        "hidden_state_candidate_id": str(hidden_state_summary["best_candidate"]["candidate_id"]),
        "synthetic_length": synthetic_length,
        "reference_window_length": window_length,
        "models": rows,
        "model_count": len(rows),
        "pareto_frontier": pareto_frontier(rows),
        "shock_winner": shock_winner,
        "shock_winner_model_id": None if shock_winner is None else shock_winner["model_id"],
        "negative_result": negative_result,
    }


def run_targeted_pytest() -> None:
    """Run the targeted compression shock tests."""
    subprocess.run(
        ["python3", "-m", "pytest", "-q", str(TEST_PATH.relative_to(ROOT))],
        check=True,
        cwd=ROOT,
        text=True,
    )


def write_blocked_outputs(
    blocked_reason: str,
    hidden_state_source_commit: str | None,
) -> dict[str, object]:
    """Write a blocked summary and findings note."""
    summary = {
        "hidden_state_source_commit": hidden_state_source_commit,
        "blocked_reason": blocked_reason,
        "models": [],
        "model_count": 0,
        "pareto_frontier": [],
        "shock_winner": None,
        "shock_winner_model_id": None,
    }
    write_json(SUMMARY_PATH, summary)
    write_models_csv([], MODELS_CSV_PATH)
    FINDINGS_PATH.write_text(findings_markdown(summary), encoding="utf-8")
    return summary


def main(argv: list[str] | None = None) -> int:
    """Run one full compression shock task."""
    args = build_parser().parse_args(argv)
    started = time.perf_counter()
    compact_timestamp = utc_timestamp_compact()
    previous_history_row = read_last_jsonl_row(HISTORY_PATH)
    starting_head, _current_head = prepare_task_branch(
        branch_name=TASK_BRANCH,
        first_launch_base_branch=FIRST_LAUNCH_BASE_BRANCH,
    )
    hidden_state_summary, hidden_state_source_commit, blocked_reason = load_hidden_state_summary()
    if blocked_reason is not None:
        summary = write_blocked_outputs(blocked_reason, hidden_state_source_commit)
        history_row = {
            "run_timestamp_utc": utc_timestamp_iso(),
            "branch": TASK_BRANCH,
            "head_commit": starting_head,
            "hidden_state_source_commit": hidden_state_source_commit,
            "hidden_state_candidate_id": None,
            "model_count": 0,
            "shock_winner_model_id": None,
            "shock_winner_state_count": None,
            "shock_winner_pooled_l1": None,
            "shock_winner_three_step": None,
            "blocked_reason": blocked_reason,
        }
        append_jsonl_row(HISTORY_PATH, history_row)
        run_targeted_pytest()
        stage_commit_push(
            branch_name=TASK_BRANCH,
            artifact_paths=[Path(__file__), TEST_PATH, SUMMARY_PATH, MODELS_CSV_PATH, HISTORY_PATH, FINDINGS_PATH],
            commit_message=f"compression-shock-probe: {compact_timestamp}",
        )
        _ = summary
        return 0

    train_surfaces = [power_surface_label(power) for power in range(args.train_min_power, args.train_max_power + 1)]
    reference_surfaces = [
        power_surface_label(power)
        for power in range(args.reference_min_power, args.reference_max_power + 1)
    ]
    frame = build_training_frame(args.detail_csv, train_surfaces, reference_surfaces)
    summary = summarize(
        frame=frame,
        hidden_state_summary=hidden_state_summary,
        hidden_state_source_commit=str(hidden_state_source_commit),
        synthetic_length=int(args.synthetic_length),
        window_length=int(args.window_length),
        mod_cycle_length=int(args.mod_cycle_length),
    )
    summary["history_seed_present"] = previous_history_row is not None
    summary["runtime_seconds"] = time.perf_counter() - started
    write_json(SUMMARY_PATH, summary)
    write_models_csv(summary["models"], MODELS_CSV_PATH)
    build_overview_plot(summary, PLOT_PATH)
    FINDINGS_PATH.write_text(findings_markdown(summary), encoding="utf-8")

    shock_winner = summary["shock_winner"]
    history_row = {
        "run_timestamp_utc": utc_timestamp_iso(),
        "branch": TASK_BRANCH,
        "head_commit": starting_head,
        "hidden_state_source_commit": hidden_state_source_commit,
        "hidden_state_candidate_id": summary["hidden_state_candidate_id"],
        "model_count": int(summary["model_count"]),
        "shock_winner_model_id": None if shock_winner is None else shock_winner["model_id"],
        "shock_winner_state_count": None if shock_winner is None else int(shock_winner["effective_state_count"]),
        "shock_winner_pooled_l1": None if shock_winner is None else float(shock_winner["pooled_window_concentration_l1"]),
        "shock_winner_three_step": None if shock_winner is None else float(shock_winner["three_step_concentration"]),
        "blocked_reason": None,
    }
    append_jsonl_row(HISTORY_PATH, history_row)
    run_targeted_pytest()
    stage_commit_push(
        branch_name=TASK_BRANCH,
        artifact_paths=[
            Path(__file__),
            TEST_PATH,
            SUMMARY_PATH,
            MODELS_CSV_PATH,
            HISTORY_PATH,
            PLOT_PATH,
            FINDINGS_PATH,
        ],
        commit_message=f"compression-shock-probe: {compact_timestamp}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
