#!/usr/bin/env python3
"""Decode the reduced gap-type grammar into rules, stress metrics, and record-gap scores."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import multiprocessing as mp
import os
import time
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import gmpy2


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT_DIR = ROOT / "output"
DEFAULT_DETAIL_CSV = ROOT / "output" / "gwr_dni_gap_type_catalog_details.csv"
DEFAULT_RECORD_CSV = ROOT / "data" / "external" / "primegap_list_records_1e12_1e18.csv"
DEFAULT_TRAIN_MIN_POWER = 7
DEFAULT_TRAIN_MAX_POWER = 17
DEFAULT_REFERENCE_MIN_POWER = 12
DEFAULT_REFERENCE_MAX_POWER = 18
DEFAULT_SYNTHETIC_LENGTH = 1_000_000
DEFAULT_RECORD_WORKERS = max(1, min(8, os.cpu_count() or 1))
HORIZON_CHECKPOINTS = (256, 1024, 4096, 16384, 65536, 262144, 1_000_000)
GEN_PROBE_PATH = Path(__file__).with_name("gwr_dni_gap_type_generative_probe.py")
GAP_TYPE_PROBE_PATH = Path(__file__).with_name("gwr_dni_gap_type_probe.py")
MODEL_COLOR = "#4c72b0"

_WORKER_GAP_TYPE_PROBE = None


def load_module(module_path: Path, module_name: str):
    """Load one sibling Python module from file."""
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


GEN_PROBE = load_module(GEN_PROBE_PATH, "gwr_dni_gap_type_generative_probe_decode")


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Decode the reduced 14-state grammar into a compact rulebook, "
            "a 1,000,000-step stress walk, and record-gap rarity scores."
        ),
    )
    parser.add_argument(
        "--detail-csv",
        type=Path,
        default=DEFAULT_DETAIL_CSV,
        help="Catalog detail CSV emitted by gwr_dni_gap_type_catalog.py.",
    )
    parser.add_argument(
        "--record-csv",
        type=Path,
        default=DEFAULT_RECORD_CSV,
        help="Local extract of record gaps in the 10^12..10^18 range.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for JSON and PNG artifacts.",
    )
    parser.add_argument(
        "--train-min-power",
        type=int,
        default=DEFAULT_TRAIN_MIN_POWER,
        help="Smallest sampled decade power used to train the grammar.",
    )
    parser.add_argument(
        "--train-max-power",
        type=int,
        default=DEFAULT_TRAIN_MAX_POWER,
        help="Largest sampled decade power used to train the grammar.",
    )
    parser.add_argument(
        "--reference-min-power",
        type=int,
        default=DEFAULT_REFERENCE_MIN_POWER,
        help="Smallest sampled decade power used for extreme-scale comparisons.",
    )
    parser.add_argument(
        "--reference-max-power",
        type=int,
        default=DEFAULT_REFERENCE_MAX_POWER,
        help="Largest sampled decade power used for extreme-scale comparisons.",
    )
    parser.add_argument(
        "--synthetic-length",
        type=int,
        default=DEFAULT_SYNTHETIC_LENGTH,
        help="Length of the deterministic second-order stress walk.",
    )
    parser.add_argument(
        "--record-workers",
        type=int,
        default=DEFAULT_RECORD_WORKERS,
        help="Worker count for exact record-gap classification.",
    )
    return parser


def load_record_rows(record_csv: Path) -> list[dict[str, str]]:
    """Load the local record-gap extract."""
    if not record_csv.exists():
        raise FileNotFoundError(f"record CSV does not exist: {record_csv}")
    with record_csv.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError("record CSV must contain at least one row")
    return rows


def power_surface_label(power: int) -> str:
    """Return one sampled decade display label."""
    return f"10^{power}"


def higher_order_top_successor_share(sequence: list[str], order: int) -> float:
    """Return the weighted top-successor share for one fixed context depth."""
    if order < 1:
        raise ValueError("order must be at least 1")
    if len(sequence) <= order:
        raise ValueError("sequence must be longer than the context order")

    support: dict[tuple[str, ...], Counter[str]] = defaultdict(Counter)
    for index in range(len(sequence) - order):
        context = tuple(sequence[index:index + order])
        next_state = sequence[index + order]
        support[context][next_state] += 1
    return sum(max(counter.values()) for counter in support.values()) / (len(sequence) - order)


def pooled_real_concentrations(
    rows_by_surface: dict[str, list[dict[str, str]]],
    reference_surfaces: list[str],
    core_states: set[str],
) -> dict[str, float]:
    """Aggregate one-step, two-step, and three-step concentrations over real surfaces."""
    numerators = {1: 0, 2: 0, 3: 0}
    denominators = {1: 0, 2: 0, 3: 0}

    for surface_label in reference_surfaces:
        sequence = [
            GEN_PROBE.reduced_state(row)
            for row in rows_by_surface[surface_label]
            if GEN_PROBE.reduced_state(row) in core_states
        ]
        for order in (1, 2, 3):
            numerators[order] += higher_order_top_successor_share(sequence, order) * (len(sequence) - order)
            denominators[order] += len(sequence) - order

    return {
        "one_step": numerators[1] / denominators[1],
        "two_step": numerators[2] / denominators[2],
        "three_step": numerators[3] / denominators[3],
    }


def real_window_metric_bands(
    rows_by_surface: dict[str, list[dict[str, str]]],
    reference_surfaces: list[str],
    core_states: set[str],
) -> dict[str, dict[str, float]]:
    """Return min/max bands across extreme-scale real windows."""
    tracked: dict[str, list[float]] = defaultdict(list)
    for surface_label in reference_surfaces:
        surface_rows = [
            row for row in rows_by_surface[surface_label]
            if GEN_PROBE.reduced_state(row) in core_states
        ]
        states = [GEN_PROBE.reduced_state(row) for row in surface_rows]
        families = [row["carrier_family"] for row in surface_rows]
        peaks = [int(row["next_peak_offset"]) for row in surface_rows]

        tracked["higher_divisor_share"].append(
            sum(1 for family in families if "higher_divisor" in family) / len(families)
        )
        tracked["one_step_concentration"].append(higher_order_top_successor_share(states, 1))
        tracked["two_step_concentration"].append(higher_order_top_successor_share(states, 2))
        tracked["three_step_concentration"].append(higher_order_top_successor_share(states, 3))
        tracked["max_peak_offset"].append(float(max(peaks)))

    return {
        metric: {
            "min": min(values),
            "max": max(values),
        }
        for metric, values in tracked.items()
    }


def decode_rulebook(
    first_order_counter: dict[str, Counter[str]],
    second_order_counter: dict[tuple[str, str], Counter[str]],
) -> list[dict[str, float | int | str]]:
    """Return one compact twelve-rule reading of the trained grammar."""
    triad_set = set(GEN_PROBE.TRIAD_STATES)
    rulebook: list[dict[str, float | int | str]] = []

    aggregated_specs = [
        (
            "aggregate_non_triad_to_attractor",
            "current_state not in Semiprime Wheel Attractor",
            "next_state in Semiprime Wheel Attractor",
            lambda state: state not in triad_set,
        ),
        (
            "aggregate_higher_divisor_to_attractor",
            "current_state family = higher_divisor_*",
            "next_state in Semiprime Wheel Attractor",
            lambda state: "higher_divisor" in state,
        ),
        (
            "aggregate_even_semiprime_to_attractor",
            "current_state family = even_semiprime",
            "next_state in Semiprime Wheel Attractor",
            lambda state: "even_semiprime" in state,
        ),
        (
            "aggregate_attractor_retention",
            "current_state in Semiprime Wheel Attractor",
            "next_state in Semiprime Wheel Attractor",
            lambda state: state in triad_set,
        ),
    ]
    for rule_id, antecedent, consequent, predicate in aggregated_specs:
        hit_count = 0
        observation_count = 0
        for current_state, counter in first_order_counter.items():
            if not predicate(current_state):
                continue
            observation_count += sum(counter.values())
            hit_count += sum(
                count for next_state, count in counter.items()
                if next_state in triad_set
            )
        share = hit_count / observation_count if observation_count else 0.0
        rulebook.append(
            {
                "rule_id": rule_id,
                "formal_rule": f"{antecedent} => {consequent}",
                "natural_language": (
                    f"When {antecedent.replace('_', ' ')}, the next state lands in the "
                    f"Semiprime Wheel Attractor with share {share:.4f}."
                ),
                "share": share,
                "hit_count": hit_count,
                "observation_count": observation_count,
            }
        )

    pair_rules: list[dict[str, float | int | str]] = []
    for context, counter in second_order_counter.items():
        observation_count = sum(counter.values())
        if observation_count < 15:
            continue
        next_state, count = max(counter.items(), key=lambda item: (item[1], item[0]))
        share = count / observation_count
        pair_rules.append(
            {
                "rule_id": "pair_context_rule",
                "formal_rule": f"({context[0]}, {context[1]}) => {next_state}",
                "natural_language": (
                    f"After the pair ({context[0]}, {context[1]}), the next state is most often "
                    f"{next_state} with share {share:.4f}."
                ),
                "share": share,
                "hit_count": count,
                "observation_count": observation_count,
            }
        )
    pair_rules.sort(
        key=lambda row: (
            float(row["share"]),
            int(row["hit_count"]),
            int(row["observation_count"]),
            str(row["formal_rule"]),
        ),
        reverse=True,
    )
    rulebook.extend(pair_rules[:8])
    return rulebook[:12]


def build_rotors_from_support(
    support: dict[str, object],
) -> tuple[dict[tuple[str, str], GEN_PROBE.Rotor], dict[str, GEN_PROBE.Rotor]]:
    """Return deterministic transition and emission rotors for the stress walk."""
    transition_rotors = {
        context: GEN_PROBE.Rotor(GEN_PROBE.balanced_cycle(counter))
        for context, counter in support["second_order_counter"].items()
    }
    emission_rotors = {
        state: GEN_PROBE.Rotor(GEN_PROBE.balanced_cycle(counter))
        for state, counter in support["emission_counter"].items()
    }
    return transition_rotors, emission_rotors


def stream_stress_walk(
    support: dict[str, object],
    synthetic_length: int,
    real_family_distribution: dict[str, float],
    real_peak_distribution: dict[int, float],
    real_concentrations: dict[str, float],
    real_higher_divisor_share: float,
) -> dict[str, object]:
    """Run the 1,000,000-step stress walk and collect horizon metrics."""
    transition_rotors, emission_rotors = build_rotors_from_support(support)
    left_state, current_state = support["start_pair"]
    state_counter = Counter([left_state, current_state])
    family_counter = Counter()
    peak_counter = Counter()
    higher_divisor_count = 0
    one_step_counter: dict[str, Counter[str]] = defaultdict(Counter)
    two_step_counter: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    three_step_counter: dict[tuple[str, str, str], Counter[str]] = defaultdict(Counter)
    state_history: list[str] = [left_state, current_state]
    one_step_counter[left_state][current_state] += 1
    emitted_families: list[str] = []
    emitted_peaks: list[int] = []

    for state in (left_state, current_state):
        type_key, next_dmin, next_peak_offset, carrier_family = emission_rotors[state].next()
        emitted_families.append(carrier_family)
        emitted_peaks.append(next_peak_offset)
        family_counter[carrier_family] += 1
        peak_counter[next_peak_offset] += 1
        if "higher_divisor" in carrier_family:
            higher_divisor_count += 1

    checkpoints = set(HORIZON_CHECKPOINTS)
    if synthetic_length not in checkpoints:
        checkpoints.add(synthetic_length)
    horizon_rows: list[dict[str, float | int]] = []

    for step_index in range(3, synthetic_length + 1):
        next_state = transition_rotors[(left_state, current_state)].next()
        one_step_counter[current_state][next_state] += 1
        two_step_counter[(left_state, current_state)][next_state] += 1
        if len(state_history) >= 3:
            three_step_counter[
                (state_history[-3], state_history[-2], state_history[-1])
            ][next_state] += 1

        state_history.append(next_state)
        if len(state_history) > 3:
            state_history = state_history[-3:]
        state_counter[next_state] += 1
        type_key, next_dmin, next_peak_offset, carrier_family = emission_rotors[next_state].next()
        emitted_families.append(carrier_family)
        emitted_peaks.append(next_peak_offset)
        family_counter[carrier_family] += 1
        peak_counter[next_peak_offset] += 1
        if "higher_divisor" in carrier_family:
            higher_divisor_count += 1
        left_state, current_state = current_state, next_state

        if step_index not in checkpoints:
            continue

        prefix_length = step_index
        synthetic_family_distribution = {
            family: count / prefix_length
            for family, count in family_counter.items()
        }
        synthetic_peak_distribution = {
            offset: count / prefix_length
            for offset, count in peak_counter.items()
        }
        one_step_concentration = (
            sum(max(counter.values()) for counter in one_step_counter.values()) / (prefix_length - 1)
        )
        two_step_concentration = (
            sum(max(counter.values()) for counter in two_step_counter.values()) / (prefix_length - 2)
        )
        three_step_concentration = (
            sum(max(counter.values()) for counter in three_step_counter.values()) / (prefix_length - 3)
        )
        horizon_rows.append(
            {
                "prefix_length": prefix_length,
                "family_l1_to_real_pool": GEN_PROBE.l1_distance(
                    synthetic_family_distribution,
                    real_family_distribution,
                ),
                "peak_offset_l1_to_real_pool": GEN_PROBE.l1_distance(
                    synthetic_peak_distribution,
                    real_peak_distribution,
                ),
                "higher_divisor_share": higher_divisor_count / prefix_length,
                "higher_divisor_share_error": abs(
                    higher_divisor_count / prefix_length - real_higher_divisor_share
                ),
                "one_step_concentration": one_step_concentration,
                "one_step_concentration_error": abs(
                    one_step_concentration - real_concentrations["one_step"]
                ),
                "two_step_concentration": two_step_concentration,
                "two_step_concentration_error": abs(
                    two_step_concentration - real_concentrations["two_step"]
                ),
                "three_step_concentration": three_step_concentration,
                "three_step_concentration_error": abs(
                    three_step_concentration - real_concentrations["three_step"]
                ),
            }
        )

    final_row = horizon_rows[-1]
    return {
        "synthetic_length": synthetic_length,
        "horizon_metrics": horizon_rows,
        "final_metrics": final_row,
        "top_states": [
            {
                "reduced_state": state,
                "count": int(count),
                "share": count / synthetic_length,
            }
            for state, count in state_counter.most_common(12)
        ],
        "top_peak_offsets": [
            {
                "next_peak_offset": int(offset),
                "count": int(count),
                "share": count / synthetic_length,
            }
            for offset, count in peak_counter.most_common(12)
        ],
    }


def _worker_gap_type_probe():
    """Load the exact gap-type probe once per worker process."""
    global _WORKER_GAP_TYPE_PROBE
    if _WORKER_GAP_TYPE_PROBE is None:
        _WORKER_GAP_TYPE_PROBE = load_module(
            GAP_TYPE_PROBE_PATH,
            "gwr_dni_gap_type_probe_worker_decode",
        )
    return _WORKER_GAP_TYPE_PROBE


def classify_record_gap(gap_start: int) -> dict[str, object]:
    """Classify one record gap plus its two preceding contexts."""
    probe = _worker_gap_type_probe()
    previous_prime = int(gmpy2.prev_prime(gap_start))
    previous_previous_prime = int(gmpy2.prev_prime(previous_prime))
    previous_previous_row = probe.gap_type_row(previous_previous_prime)
    previous_row = probe.gap_type_row(previous_prime)
    current_row = probe.gap_type_row(gap_start)
    return {
        "gap_start": gap_start,
        "context_left_state": GEN_PROBE.reduced_state(
            {key: str(value) for key, value in previous_previous_row.items()}
        ),
        "context_right_state": GEN_PROBE.reduced_state(
            {key: str(value) for key, value in previous_row.items()}
        ),
        "current_state": GEN_PROBE.reduced_state(
            {key: str(value) for key, value in current_row.items()}
        ),
        "current_carrier_family": str(current_row["carrier_family"]),
        "current_peak_offset": int(current_row["next_peak_offset"]),
    }


def summarize_record_scores(
    record_rows: list[dict[str, str]],
    support: dict[str, object],
    rows_by_surface: dict[str, list[dict[str, str]]],
    reference_surfaces: list[str],
    record_workers: int,
) -> dict[str, object]:
    """Score actual record gaps by second-order grammar surprisal."""
    second_order_counter = support["second_order_counter"]
    row_probabilities = {
        context: {
            next_state: count / sum(counter.values())
            for next_state, count in counter.items()
        }
        for context, counter in second_order_counter.items()
    }
    core_states = set(support["state_counter"])

    control_surprisals: list[float] = []
    for surface_label in reference_surfaces:
        sequence = [
            GEN_PROBE.reduced_state(row)
            for row in rows_by_surface[surface_label]
            if GEN_PROBE.reduced_state(row) in core_states
        ]
        for left_state, current_state, next_state in zip(sequence, sequence[1:], sequence[2:]):
            context = (left_state, current_state)
            if context not in row_probabilities or next_state not in row_probabilities[context]:
                continue
            control_surprisals.append(-math.log2(row_probabilities[context][next_state]))
    control_mean_surprisal = sum(control_surprisals) / len(control_surprisals)

    gap_starts = [int(row["gap_start"]) for row in record_rows]
    if record_workers > 1:
        context = mp.get_context("fork")
        with ProcessPoolExecutor(
            max_workers=record_workers,
            mp_context=context,
        ) as executor:
            classified_rows = list(executor.map(classify_record_gap, gap_starts, chunksize=8))
    else:
        classified_rows = [classify_record_gap(gap_start) for gap_start in gap_starts]

    classified_by_start = {
        int(row["gap_start"]): row
        for row in classified_rows
    }

    scored_rows: list[dict[str, object]] = []
    for record_row in record_rows:
        gap_start = int(record_row["gap_start"])
        classified_row = classified_by_start[gap_start]
        context = (
            str(classified_row["context_left_state"]),
            str(classified_row["context_right_state"]),
        )
        current_state = str(classified_row["current_state"])
        payload = {
            "gap_start": gap_start,
            "gap_size": int(record_row["gap_size"]),
            "is_maximal": int(record_row["is_maximal"]),
            "is_first": int(record_row["is_first"]),
            "current_state": current_state,
            "current_carrier_family": str(classified_row["current_carrier_family"]),
            "current_peak_offset": int(classified_row["current_peak_offset"]),
        }
        if context in row_probabilities and current_state in row_probabilities[context]:
            successor_rows = sorted(
                row_probabilities[context].items(),
                key=lambda item: (-item[1], item[0]),
            )
            probability = row_probabilities[context][current_state]
            payload.update(
                {
                    "in_core": 1,
                    "context_left_state": context[0],
                    "context_right_state": context[1],
                    "transition_probability": probability,
                    "transition_surprisal_bits": -math.log2(probability),
                    "transition_rank": 1 + [state for state, _ in successor_rows].index(current_state),
                    "context_fanout": len(successor_rows),
                }
            )
        else:
            payload.update(
                {
                    "in_core": 0,
                    "context_left_state": context[0],
                    "context_right_state": context[1],
                }
            )
        scored_rows.append(payload)

    core_rows = [row for row in scored_rows if int(row["in_core"]) == 1]
    subsets = {
        "all_records": core_rows,
        "maximal_records": [row for row in core_rows if int(row["is_maximal"]) == 1],
        "nonmaximal_first_occurrences": [
            row for row in core_rows
            if int(row["is_first"]) == 1 and int(row["is_maximal"]) == 0
        ],
    }
    subset_summaries: dict[str, dict[str, float | int]] = {}
    for subset_name, subset_rows in subsets.items():
        subset_summaries[subset_name] = {
            "record_count": len(subset_rows),
            "mean_transition_probability": (
                sum(float(row["transition_probability"]) for row in subset_rows) / len(subset_rows)
            ),
            "mean_transition_surprisal_bits": (
                sum(float(row["transition_surprisal_bits"]) for row in subset_rows) / len(subset_rows)
            ),
            "mean_rank_fraction": (
                sum(
                    float(row["transition_rank"]) / float(row["context_fanout"])
                    for row in subset_rows
                ) / len(subset_rows)
            ),
            "share_above_control_mean_surprisal": (
                sum(
                    int(float(row["transition_surprisal_bits"]) >= control_mean_surprisal)
                    for row in subset_rows
                ) / len(subset_rows)
            ),
        }

    return {
        "control_mean_transition_surprisal_bits": control_mean_surprisal,
        "core_scored_record_count": len(core_rows),
        "noncore_record_count": len(scored_rows) - len(core_rows),
        "subset_summaries": subset_summaries,
        "most_surprising_records": sorted(
            core_rows,
            key=lambda row: (
                float(row["transition_surprisal_bits"]),
                int(row["gap_start"]),
            ),
            reverse=True,
        )[:20],
    }


def summarize(
    detail_rows: list[dict[str, str]],
    record_rows: list[dict[str, str]],
    train_surfaces: list[str],
    reference_surfaces: list[str],
    synthetic_length: int,
    record_workers: int,
) -> dict[str, object]:
    """Build the full engine-decode summary."""
    rows_by_surface = GEN_PROBE.surface_rows(detail_rows)
    core_states = GEN_PROBE.persistent_core_states(rows_by_surface, train_surfaces)
    segments = GEN_PROBE.contiguous_core_segments(rows_by_surface, train_surfaces, core_states)
    support = GEN_PROBE.build_training_support(segments)

    reference_rows = []
    for surface_label in reference_surfaces:
        reference_rows.extend(
            [
                row for row in rows_by_surface[surface_label]
                if GEN_PROBE.reduced_state(row) in core_states
            ]
        )
    real_family_distribution = GEN_PROBE.distribution(
        [row["carrier_family"] for row in reference_rows]
    )
    real_peak_distribution = GEN_PROBE.distribution(
        [int(row["next_peak_offset"]) for row in reference_rows]
    )
    real_higher_divisor_share = sum(
        1 for row in reference_rows if "higher_divisor" in row["carrier_family"]
    ) / len(reference_rows)
    real_concentrations = pooled_real_concentrations(
        rows_by_surface,
        reference_surfaces,
        core_states,
    )
    window_bands = real_window_metric_bands(
        rows_by_surface,
        reference_surfaces,
        core_states,
    )

    stress_summary = stream_stress_walk(
        support=support,
        synthetic_length=synthetic_length,
        real_family_distribution=real_family_distribution,
        real_peak_distribution=real_peak_distribution,
        real_concentrations=real_concentrations,
        real_higher_divisor_share=real_higher_divisor_share,
    )
    record_summary = summarize_record_scores(
        record_rows=record_rows,
        support=support,
        rows_by_surface=rows_by_surface,
        reference_surfaces=reference_surfaces,
        record_workers=record_workers,
    )

    return {
        "training_surfaces": train_surfaces,
        "reference_surfaces": reference_surfaces,
        "core_state_count": len(core_states),
        "core_states": sorted(core_states),
        "segment_count": len(segments),
        "Semiprime_Wheel_Attractor": list(GEN_PROBE.TRIAD_STATES),
        "rulebook": decode_rulebook(
            support["first_order_counter"],
            support["second_order_counter"],
        ),
        "real_extreme_scale_reference": {
            "row_count": len(reference_rows),
            "family_distribution": real_family_distribution,
            "peak_offset_distribution": real_peak_distribution,
            "higher_divisor_share": real_higher_divisor_share,
            "concentrations": real_concentrations,
            "window_bands": window_bands,
        },
        "stress_walk": stress_summary,
        "record_gap_probe": record_summary,
    }


def plot_summary(summary: dict[str, object], output_path: Path) -> None:
    """Render one overview figure for the decoded engine."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    horizon_rows = summary["stress_walk"]["horizon_metrics"]
    prefix_lengths = [int(row["prefix_length"]) for row in horizon_rows]
    x_positions = np.arange(len(prefix_lengths))

    fig, axes = plt.subplots(2, 2, figsize=(15, 10), constrained_layout=True)

    axes[0, 0].plot(
        x_positions,
        [float(row["family_l1_to_real_pool"]) for row in horizon_rows],
        marker="o",
        linewidth=2.0,
        color=MODEL_COLOR,
        label="family L1 to real pool",
    )
    axes[0, 0].plot(
        x_positions,
        [float(row["peak_offset_l1_to_real_pool"]) for row in horizon_rows],
        marker="o",
        linewidth=2.0,
        color="#dd8452",
        label="peak-offset L1 to real pool",
    )
    axes[0, 0].set_title("Long-horizon distribution drift")
    axes[0, 0].set_ylabel("L1 distance")
    axes[0, 0].set_xticks(x_positions)
    axes[0, 0].set_xticklabels([str(length) for length in prefix_lengths], rotation=35, ha="right")
    axes[0, 0].grid(axis="y", alpha=0.25)
    axes[0, 0].legend(loc="upper right")

    real_concentrations = summary["real_extreme_scale_reference"]["concentrations"]
    axes[0, 1].axhline(float(real_concentrations["one_step"]), color="#222222", linestyle="--", linewidth=1.4, label="real one-step")
    axes[0, 1].axhline(float(real_concentrations["two_step"]), color="#555555", linestyle=":", linewidth=1.4, label="real two-step")
    axes[0, 1].axhline(float(real_concentrations["three_step"]), color="#888888", linestyle="-.", linewidth=1.4, label="real three-step")
    axes[0, 1].plot(
        x_positions,
        [float(row["one_step_concentration"]) for row in horizon_rows],
        marker="o",
        linewidth=2.0,
        color="#4c72b0",
        label="synthetic one-step",
    )
    axes[0, 1].plot(
        x_positions,
        [float(row["two_step_concentration"]) for row in horizon_rows],
        marker="o",
        linewidth=2.0,
        color="#55a868",
        label="synthetic two-step",
    )
    axes[0, 1].plot(
        x_positions,
        [float(row["three_step_concentration"]) for row in horizon_rows],
        marker="o",
        linewidth=2.0,
        color="#c44e52",
        label="synthetic three-step",
    )
    axes[0, 1].set_title("Concentration across horizon length")
    axes[0, 1].set_ylabel("Weighted top-successor share")
    axes[0, 1].set_xticks(x_positions)
    axes[0, 1].set_xticklabels([str(length) for length in prefix_lengths], rotation=35, ha="right")
    axes[0, 1].grid(axis="y", alpha=0.25)
    axes[0, 1].legend(loc="upper right")

    real_higher_divisor_share = float(summary["real_extreme_scale_reference"]["higher_divisor_share"])
    axes[1, 0].axhline(real_higher_divisor_share, color="#222222", linestyle="--", linewidth=1.5, label="real higher-divisor share")
    axes[1, 0].plot(
        x_positions,
        [float(row["higher_divisor_share"]) for row in horizon_rows],
        marker="o",
        linewidth=2.0,
        color=MODEL_COLOR,
        label="synthetic higher-divisor share",
    )
    axes[1, 0].set_title("Higher-divisor intrusion rate")
    axes[1, 0].set_ylabel("Share")
    axes[1, 0].set_xticks(x_positions)
    axes[1, 0].set_xticklabels([str(length) for length in prefix_lengths], rotation=35, ha="right")
    axes[1, 0].grid(axis="y", alpha=0.25)
    axes[1, 0].legend(loc="upper right")

    subset_summaries = summary["record_gap_probe"]["subset_summaries"]
    subset_labels = list(subset_summaries)
    subset_positions = np.arange(len(subset_labels))
    axes[1, 1].bar(
        subset_positions - 0.18,
        [float(subset_summaries[label]["mean_transition_surprisal_bits"]) for label in subset_labels],
        width=0.36,
        color="#4c72b0",
        label="mean surprisal",
    )
    axes[1, 1].bar(
        subset_positions + 0.18,
        [float(subset_summaries[label]["share_above_control_mean_surprisal"]) for label in subset_labels],
        width=0.36,
        color="#dd8452",
        label="share above control mean",
    )
    axes[1, 1].axhline(
        float(summary["record_gap_probe"]["control_mean_transition_surprisal_bits"]),
        color="#222222",
        linestyle="--",
        linewidth=1.4,
        label="control mean surprisal",
    )
    axes[1, 1].set_title("Record-gap grammar rarity")
    axes[1, 1].set_ylabel("Bits / share")
    axes[1, 1].set_xticks(subset_positions)
    axes[1, 1].set_xticklabels([label.replace("_", " ") for label in subset_labels], rotation=20, ha="right")
    axes[1, 1].grid(axis="y", alpha=0.25)
    axes[1, 1].legend(loc="upper right")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=220)
    plt.close(fig)


def main(argv: list[str] | None = None) -> int:
    """Run the engine decode and write JSON plus PNG artifacts."""
    args = build_parser().parse_args(argv)
    if args.train_min_power > args.train_max_power:
        raise ValueError("train_min_power must be <= train_max_power")
    if args.reference_min_power > args.reference_max_power:
        raise ValueError("reference_min_power must be <= reference_max_power")
    if args.synthetic_length < 4:
        raise ValueError("synthetic_length must be at least 4")
    if args.record_workers < 1:
        raise ValueError("record_workers must be at least 1")

    detail_rows = GEN_PROBE.load_rows(args.detail_csv)
    record_rows = load_record_rows(args.record_csv)
    train_surfaces = [
        power_surface_label(power)
        for power in range(args.train_min_power, args.train_max_power + 1)
    ]
    reference_surfaces = [
        power_surface_label(power)
        for power in range(args.reference_min_power, args.reference_max_power + 1)
    ]

    started = time.perf_counter()
    summary = summarize(
        detail_rows=detail_rows,
        record_rows=record_rows,
        train_surfaces=train_surfaces,
        reference_surfaces=reference_surfaces,
        synthetic_length=args.synthetic_length,
        record_workers=args.record_workers,
    )
    summary["runtime_seconds"] = time.perf_counter() - started

    args.output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = args.output_dir / "gwr_dni_gap_type_engine_decode_summary.json"
    plot_path = args.output_dir / "gwr_dni_gap_type_engine_decode_overview.png"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    plot_summary(summary, plot_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
