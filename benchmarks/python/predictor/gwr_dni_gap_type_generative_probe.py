#!/usr/bin/env python3
"""Test whether the reduced gap-type grammar can generate a held-out high-scale window."""

from __future__ import annotations

import argparse
import csv
import json
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Hashable, TypeVar


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT_DIR = ROOT / "output"
DEFAULT_DETAIL_CSV = ROOT / "output" / "gwr_dni_gap_type_catalog_details.csv"
DEFAULT_TRAIN_MIN_POWER = 7
DEFAULT_TRAIN_MAX_POWER = 17
DEFAULT_HELD_POWER = 18
DEFAULT_SYNTHETIC_LENGTH = 10_000
D_BUCKET_LABELS = (
    "d<=4",
    "5<=d<=16",
    "17<=d<=64",
    "d>64",
)
TRIAD_STATES = (
    "o2_odd_semiprime|d<=4",
    "o4_odd_semiprime|d<=4",
    "o6_odd_semiprime|d<=4",
)
MODEL_COLORS = {
    "iid_balanced_cycle": "#8172b2",
    "first_order_rotor": "#dd8452",
    "second_order_rotor": "#4c72b0",
}

KeyT = TypeVar("KeyT", bound=Hashable)


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Train a deterministic reduced-state grammar and compare its "
            "synthetic held-out window against 10^18."
        ),
    )
    parser.add_argument(
        "--detail-csv",
        type=Path,
        default=DEFAULT_DETAIL_CSV,
        help="Catalog detail CSV emitted by gwr_dni_gap_type_catalog.py.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for JSON, CSV, and PNG artifacts.",
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
        "--held-power",
        type=int,
        default=DEFAULT_HELD_POWER,
        help="Sampled decade power reserved for held-out evaluation.",
    )
    parser.add_argument(
        "--synthetic-length",
        type=int,
        default=DEFAULT_SYNTHETIC_LENGTH,
        help="Number of synthetic reduced-state rows emitted by the main generator.",
    )
    return parser


def load_rows(detail_csv: Path) -> list[dict[str, str]]:
    """Load catalog detail rows."""
    if not detail_csv.exists():
        raise FileNotFoundError(f"detail CSV does not exist: {detail_csv}")
    with detail_csv.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError("detail CSV must contain at least one row")
    return rows


def open_family_state(row: dict[str, str]) -> str:
    """Return the open-family state for one row."""
    return f"o{row['first_open_offset']}_{row['carrier_family']}"


def d_bucket(next_dmin: str) -> str:
    """Bucket the winning divisor class into one coarse band."""
    value = int(next_dmin)
    if value <= 4:
        return D_BUCKET_LABELS[0]
    if value <= 16:
        return D_BUCKET_LABELS[1]
    if value <= 64:
        return D_BUCKET_LABELS[2]
    return D_BUCKET_LABELS[3]


def reduced_state(row: dict[str, str]) -> str:
    """Return the reduced state used by the generative grammar."""
    return f"{open_family_state(row)}|{d_bucket(row['next_dmin'])}"


def surface_rows(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    """Group rows by their display label."""
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["surface_display_label"]].append(row)
    return dict(grouped)


def power_surface_label(power: int) -> str:
    """Return the display label for one sampled decade power."""
    return f"10^{power}"


def persistent_core_states(
    rows_by_surface: dict[str, list[dict[str, str]]],
    train_surfaces: list[str],
) -> set[str]:
    """Return reduced states present on every training surface."""
    if not train_surfaces:
        raise ValueError("train_surfaces must not be empty")
    core_states = {
        reduced_state(row)
        for row in rows_by_surface[train_surfaces[0]]
    }
    for surface_label in train_surfaces[1:]:
        core_states &= {
            reduced_state(row)
            for row in rows_by_surface[surface_label]
        }
    return core_states


def contiguous_core_segments(
    rows_by_surface: dict[str, list[dict[str, str]]],
    train_surfaces: list[str],
    core_states: set[str],
) -> list[list[dict[str, str]]]:
    """Return contiguous row segments that stay inside the persistent core."""
    segments: list[list[dict[str, str]]] = []
    for surface_label in train_surfaces:
        current_segment: list[dict[str, str]] = []
        for row in rows_by_surface[surface_label]:
            state = reduced_state(row)
            if state in core_states:
                current_segment.append(row)
                continue
            if current_segment:
                segments.append(current_segment)
                current_segment = []
        if current_segment:
            segments.append(current_segment)
    return segments


def balanced_cycle(counter: Counter[KeyT]) -> list[KeyT]:
    """Spread one weighted multiset across a deterministic low-discrepancy cycle."""
    if not counter:
        raise ValueError("counter must not be empty")

    items = sorted(counter.items(), key=lambda item: (-item[1], item[0]))
    total = sum(counter.values())
    emitted = {key: 0 for key, _ in items}
    cycle: list[KeyT] = []

    for step in range(total):
        best_key: KeyT | None = None
        best_score: tuple[float, int, KeyT] | None = None
        for key, count in items:
            if emitted[key] >= count:
                continue
            score = (step + 1) * count / total - emitted[key]
            payload = (score, count, key)
            if (
                best_score is None
                or score > best_score[0] + 1e-12
                or (
                    abs(score - best_score[0]) <= 1e-12
                    and (
                        count > best_score[1]
                        or (count == best_score[1] and key < best_score[2])
                    )
                )
            ):
                best_key = key
                best_score = payload
        if best_key is None:
            raise RuntimeError("balanced cycle failed to choose a key")
        emitted[best_key] += 1
        cycle.append(best_key)

    return cycle


class Rotor:
    """Deterministic cyclic emitter over one weighted support."""

    def __init__(self, cycle: list[KeyT]) -> None:
        if not cycle:
            raise ValueError("cycle must not be empty")
        self._cycle = cycle
        self._index = 0

    def next(self) -> KeyT:
        """Return the next emitted key and advance the rotor."""
        value = self._cycle[self._index]
        self._index = (self._index + 1) % len(self._cycle)
        return value


def distribution(values: list[Hashable]) -> dict[Hashable, float]:
    """Return the empirical distribution of one list."""
    counter = Counter(values)
    total = len(values)
    return {
        key: count / total
        for key, count in counter.items()
    }


def l1_distance(
    left_distribution: dict[Hashable, float],
    right_distribution: dict[Hashable, float],
) -> float:
    """Return the L1 distance between two empirical distributions."""
    return sum(
        abs(left_distribution.get(key, 0.0) - right_distribution.get(key, 0.0))
        for key in (set(left_distribution) | set(right_distribution))
    )


def pair_distribution(sequence: list[str]) -> dict[tuple[str, str], float]:
    """Return the empirical distribution of adjacent state pairs."""
    return distribution(list(zip(sequence, sequence[1:])))


def pair_top_successor_share(sequence: list[str]) -> float:
    """Return the weighted top-successor share of a one-step state sequence."""
    if len(sequence) < 2:
        raise ValueError("sequence must contain at least 2 states")
    support: dict[str, Counter[str]] = defaultdict(Counter)
    for current_state, next_state in zip(sequence, sequence[1:]):
        support[current_state][next_state] += 1
    return sum(max(counter.values()) for counter in support.values()) / (len(sequence) - 1)


def family_from_reduced_state(state: str) -> str:
    """Extract the carrier family from one reduced state key."""
    open_family = state.split("|", 1)[0]
    return open_family.split("_", 1)[1]


def build_emission_payload(row: dict[str, str]) -> tuple[str, int, int, str]:
    """Return the emitted exact payload attached to one reduced state visit."""
    return (
        row["type_key"],
        int(row["next_dmin"]),
        int(row["next_peak_offset"]),
        row["carrier_family"],
    )


def build_training_support(
    segments: list[list[dict[str, str]]],
) -> dict[str, object]:
    """Build deterministic training supports from contiguous core segments."""
    if not segments:
        raise ValueError("segments must not be empty")

    state_counter: Counter[str] = Counter()
    first_order_counter: dict[str, Counter[str]] = defaultdict(Counter)
    second_order_counter: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    emission_counter: dict[str, Counter[tuple[str, int, int, str]]] = defaultdict(Counter)

    for segment in segments:
        sequence = [reduced_state(row) for row in segment]
        for row, state in zip(segment, sequence):
            state_counter[state] += 1
            emission_counter[state][build_emission_payload(row)] += 1
        for current_state, next_state in zip(sequence, sequence[1:]):
            first_order_counter[current_state][next_state] += 1
        for left_state, current_state, next_state in zip(sequence, sequence[1:], sequence[2:]):
            second_order_counter[(left_state, current_state)][next_state] += 1

    if not second_order_counter:
        raise ValueError("second-order support must not be empty")

    start_state = max(state_counter.items(), key=lambda item: (item[1], item[0]))[0]
    start_pair = max(
        second_order_counter.items(),
        key=lambda item: (sum(item[1].values()), item[0]),
    )[0]

    return {
        "state_counter": state_counter,
        "first_order_counter": first_order_counter,
        "second_order_counter": second_order_counter,
        "emission_counter": emission_counter,
        "start_state": start_state,
        "start_pair": start_pair,
    }


def synthetic_row(
    step_index: int,
    state: str,
    emission: tuple[str, int, int, str],
) -> dict[str, object]:
    """Return one synthetic row payload."""
    open_family, d_bucket_label = state.split("|", 1)
    type_key, next_dmin, next_peak_offset, carrier_family = emission
    return {
        "step_index": step_index,
        "reduced_state": state,
        "open_family": open_family,
        "carrier_family": carrier_family,
        "d_bucket": d_bucket_label,
        "emitted_type_key": type_key,
        "emitted_next_dmin": next_dmin,
        "emitted_next_peak_offset": next_peak_offset,
    }


def emit_iid_sequence(
    state_counter: Counter[str],
    emission_counter: dict[str, Counter[tuple[str, int, int, str]]],
    synthetic_length: int,
) -> list[dict[str, object]]:
    """Emit a deterministic i.i.d. reduced-state surrogate."""
    state_rotor = Rotor(balanced_cycle(state_counter))
    emission_rotors = {
        state: Rotor(balanced_cycle(counter))
        for state, counter in emission_counter.items()
    }
    return [
        synthetic_row(
            step_index=step_index + 1,
            state=(state := state_rotor.next()),
            emission=emission_rotors[state].next(),
        )
        for step_index in range(synthetic_length)
    ]


def emit_first_order_sequence(
    first_order_counter: dict[str, Counter[str]],
    emission_counter: dict[str, Counter[tuple[str, int, int, str]]],
    synthetic_length: int,
    start_state: str,
) -> list[dict[str, object]]:
    """Emit a deterministic first-order rotor sequence."""
    if synthetic_length < 1:
        raise ValueError("synthetic_length must be at least 1")

    transition_rotors = {
        state: Rotor(balanced_cycle(counter))
        for state, counter in first_order_counter.items()
    }
    emission_rotors = {
        state: Rotor(balanced_cycle(counter))
        for state, counter in emission_counter.items()
    }

    current_state = start_state
    rows = [
        synthetic_row(
            step_index=1,
            state=current_state,
            emission=emission_rotors[current_state].next(),
        )
    ]
    while len(rows) < synthetic_length:
        current_state = transition_rotors[current_state].next()
        rows.append(
            synthetic_row(
                step_index=len(rows) + 1,
                state=current_state,
                emission=emission_rotors[current_state].next(),
            )
        )
    return rows


def emit_second_order_sequence(
    second_order_counter: dict[tuple[str, str], Counter[str]],
    emission_counter: dict[str, Counter[tuple[str, int, int, str]]],
    synthetic_length: int,
    start_pair: tuple[str, str],
) -> list[dict[str, object]]:
    """Emit a deterministic second-order rotor sequence."""
    if synthetic_length < 2:
        raise ValueError("synthetic_length must be at least 2")

    transition_rotors = {
        context: Rotor(balanced_cycle(counter))
        for context, counter in second_order_counter.items()
    }
    emission_rotors = {
        state: Rotor(balanced_cycle(counter))
        for state, counter in emission_counter.items()
    }

    left_state, current_state = start_pair
    rows = [
        synthetic_row(
            step_index=1,
            state=left_state,
            emission=emission_rotors[left_state].next(),
        ),
        synthetic_row(
            step_index=2,
            state=current_state,
            emission=emission_rotors[current_state].next(),
        ),
    ]

    while len(rows) < synthetic_length:
        next_state = transition_rotors[(left_state, current_state)].next()
        rows.append(
            synthetic_row(
                step_index=len(rows) + 1,
                state=next_state,
                emission=emission_rotors[next_state].next(),
            )
        )
        left_state, current_state = current_state, next_state

    return rows


def held_out_metrics(
    synthetic_rows: list[dict[str, object]],
    held_out_rows: list[dict[str, str]],
) -> dict[str, float | int]:
    """Compare one synthetic prefix against the held-out real window."""
    prefix_length = len(held_out_rows)
    prefix = synthetic_rows[:prefix_length]
    synthetic_states = [str(row["reduced_state"]) for row in prefix]
    held_states = [reduced_state(row) for row in held_out_rows]
    synthetic_families = [str(row["carrier_family"]) for row in prefix]
    held_families = [row["carrier_family"] for row in held_out_rows]
    synthetic_peaks = [int(row["emitted_next_peak_offset"]) for row in prefix]
    held_peaks = [int(row["next_peak_offset"]) for row in held_out_rows]
    triad_set = set(TRIAD_STATES)
    synthetic_triad_share = sum(
        1 for state in synthetic_states if state in triad_set
    ) / prefix_length
    held_triad_share = sum(
        1 for state in held_states if state in triad_set
    ) / prefix_length

    return {
        "prefix_length": prefix_length,
        "state_count": len(set(synthetic_states)),
        "reduced_state_l1": l1_distance(
            distribution(synthetic_states),
            distribution(held_states),
        ),
        "reduced_state_pair_l1": l1_distance(
            pair_distribution(synthetic_states),
            pair_distribution(held_states),
        ),
        "family_l1": l1_distance(
            distribution(synthetic_families),
            distribution(held_families),
        ),
        "peak_offset_l1": l1_distance(
            distribution(synthetic_peaks),
            distribution(held_peaks),
        ),
        "triad_share": synthetic_triad_share,
        "held_triad_share": held_triad_share,
        "triad_share_error": abs(synthetic_triad_share - held_triad_share),
        "pair_top_successor_share": pair_top_successor_share(synthetic_states),
        "held_pair_top_successor_share": pair_top_successor_share(held_states),
        "pair_top_successor_share_error": abs(
            pair_top_successor_share(synthetic_states)
            - pair_top_successor_share(held_states)
        ),
        "max_peak_offset": max(synthetic_peaks),
        "held_max_peak_offset": max(held_peaks),
        "max_peak_offset_error": abs(max(synthetic_peaks) - max(held_peaks)),
    }


def top_states(rows: list[dict[str, object]], limit: int = 10) -> list[dict[str, object]]:
    """Return the leading reduced states in one synthetic sequence."""
    counter = Counter(str(row["reduced_state"]) for row in rows)
    total = len(rows)
    return [
        {
            "reduced_state": state,
            "count": int(count),
            "share": count / total,
        }
        for state, count in counter.most_common(limit)
    ]


def top_peak_offsets(rows: list[dict[str, object]], limit: int = 10) -> list[dict[str, object]]:
    """Return the leading emitted peak offsets in one synthetic sequence."""
    counter = Counter(int(row["emitted_next_peak_offset"]) for row in rows)
    total = len(rows)
    return [
        {
            "next_peak_offset": int(offset),
            "count": int(count),
            "share": count / total,
        }
        for offset, count in counter.most_common(limit)
    ]


def aggregated_rules(
    first_order_counter: dict[str, Counter[str]],
) -> list[dict[str, float | int | str]]:
    """Return a short human-readable rule list from the trained grammar."""
    triad_set = set(TRIAD_STATES)
    grouped_counts = {
        "higher_divisor_to_triad": [0, 0],
        "even_semiprime_to_triad": [0, 0],
        "non_triad_to_triad": [0, 0],
        "triad_to_triad": [0, 0],
    }

    for current_state, counter in first_order_counter.items():
        total = sum(counter.values())
        triad_hits = sum(count for next_state, count in counter.items() if next_state in triad_set)
        if "higher_divisor" in current_state:
            grouped_counts["higher_divisor_to_triad"][0] += triad_hits
            grouped_counts["higher_divisor_to_triad"][1] += total
        if "even_semiprime" in current_state:
            grouped_counts["even_semiprime_to_triad"][0] += triad_hits
            grouped_counts["even_semiprime_to_triad"][1] += total
        if current_state in triad_set:
            grouped_counts["triad_to_triad"][0] += triad_hits
            grouped_counts["triad_to_triad"][1] += total
        else:
            grouped_counts["non_triad_to_triad"][0] += triad_hits
            grouped_counts["non_triad_to_triad"][1] += total

    rules: list[dict[str, float | int | str]] = []
    for rule_name, (hits, total) in grouped_counts.items():
        rules.append(
            {
                "rule": rule_name,
                "share": hits / total if total else 0.0,
                "hit_count": hits,
                "observation_count": total,
            }
        )

    dominant_rows: list[dict[str, float | int | str]] = []
    for current_state, counter in first_order_counter.items():
        observation_count = sum(counter.values())
        next_state, next_count = max(counter.items(), key=lambda item: (item[1], item[0]))
        dominant_rows.append(
            {
                "current_state": current_state,
                "next_state": next_state,
                "share": next_count / observation_count,
                "count": next_count,
                "observation_count": observation_count,
            }
        )

    dominant_rows.sort(
        key=lambda row: (
            float(row["share"]),
            int(row["count"]),
            str(row["current_state"]),
        ),
        reverse=True,
    )
    rules.extend(dominant_rows[:6])
    return rules


def summarize(
    rows: list[dict[str, str]],
    train_surfaces: list[str],
    held_surface: str,
    synthetic_length: int,
) -> tuple[dict[str, object], list[dict[str, object]]]:
    """Build the generative summary plus the main synthetic CSV rows."""
    rows_by_surface = surface_rows(rows)
    if held_surface not in rows_by_surface:
        raise ValueError(f"held-out surface {held_surface} is not present in detail CSV")
    for surface_label in train_surfaces:
        if surface_label not in rows_by_surface:
            raise ValueError(f"training surface {surface_label} is not present in detail CSV")

    core_states = persistent_core_states(rows_by_surface, train_surfaces)
    segments = contiguous_core_segments(rows_by_surface, train_surfaces, core_states)
    support = build_training_support(segments)
    held_rows = rows_by_surface[held_surface]

    iid_rows = emit_iid_sequence(
        state_counter=support["state_counter"],
        emission_counter=support["emission_counter"],
        synthetic_length=synthetic_length,
    )
    first_order_rows = emit_first_order_sequence(
        first_order_counter=support["first_order_counter"],
        emission_counter=support["emission_counter"],
        synthetic_length=synthetic_length,
        start_state=support["start_state"],
    )
    second_order_rows = emit_second_order_sequence(
        second_order_counter=support["second_order_counter"],
        emission_counter=support["emission_counter"],
        synthetic_length=synthetic_length,
        start_pair=support["start_pair"],
    )

    held_states = [reduced_state(row) for row in held_rows]
    held_families = [row["carrier_family"] for row in held_rows]
    held_peaks = [int(row["next_peak_offset"]) for row in held_rows]

    summary = {
        "training_surfaces": train_surfaces,
        "held_out_surface": held_surface,
        "reduced_state_definition": {
            "state_form": "open_family|d_bucket",
            "d_bucket_labels": list(D_BUCKET_LABELS),
        },
        "core_state_count": len(core_states),
        "core_states": sorted(core_states),
        "segment_count": len(segments),
        "training_start_state": support["start_state"],
        "training_start_pair": list(support["start_pair"]),
        "held_out_window": {
            "gap_count": len(held_rows),
            "state_count": len(set(held_states)),
            "triad_share": sum(1 for state in held_states if state in TRIAD_STATES) / len(held_states),
            "pair_top_successor_share": pair_top_successor_share(held_states),
            "max_peak_offset": max(held_peaks),
            "family_distribution": distribution(held_families),
        },
        "aggregated_rules": aggregated_rules(support["first_order_counter"]),
        "model_comparisons": {
            "iid_balanced_cycle": held_out_metrics(iid_rows, held_rows),
            "first_order_rotor": held_out_metrics(first_order_rows, held_rows),
            "second_order_rotor": held_out_metrics(second_order_rows, held_rows),
        },
        "second_order_synthetic_summary": {
            "synthetic_length": synthetic_length,
            "state_count": len({str(row["reduced_state"]) for row in second_order_rows}),
            "triad_share": sum(
                1 for row in second_order_rows if str(row["reduced_state"]) in TRIAD_STATES
            ) / synthetic_length,
            "pair_top_successor_share": pair_top_successor_share(
                [str(row["reduced_state"]) for row in second_order_rows]
            ),
            "max_peak_offset": max(int(row["emitted_next_peak_offset"]) for row in second_order_rows),
            "top_states": top_states(second_order_rows),
            "top_peak_offsets": top_peak_offsets(second_order_rows),
        },
    }
    return summary, second_order_rows


def plot_overview(summary: dict[str, object], output_path: Path) -> None:
    """Render one overview figure for the generative probe."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    model_comparisons = summary["model_comparisons"]
    model_labels = list(model_comparisons)
    model_positions = np.arange(len(model_labels))

    fig, axes = plt.subplots(2, 2, figsize=(15, 10), constrained_layout=True)

    error_metrics = (
        "reduced_state_l1",
        "reduced_state_pair_l1",
        "family_l1",
        "peak_offset_l1",
    )
    width = 0.18
    metric_positions = np.arange(len(error_metrics))
    for model_index, model_label in enumerate(model_labels):
        axes[0, 0].bar(
            metric_positions + (model_index - 1) * width,
            [float(model_comparisons[model_label][metric]) for metric in error_metrics],
            width=width,
            color=MODEL_COLORS[model_label],
            label=model_label.replace("_", " "),
        )
    axes[0, 0].set_title("Held-out 10^18 error metrics")
    axes[0, 0].set_ylabel("L1 distance")
    axes[0, 0].set_xticks(metric_positions)
    axes[0, 0].set_xticklabels(
        [metric.replace("_", " ") for metric in error_metrics],
        rotation=25,
        ha="right",
    )
    axes[0, 0].grid(axis="y", alpha=0.25)
    axes[0, 0].legend(loc="upper right")

    held_triad_share = float(summary["held_out_window"]["triad_share"])
    held_pair_top = float(summary["held_out_window"]["pair_top_successor_share"])
    held_max_peak = int(summary["held_out_window"]["max_peak_offset"])
    axes[0, 1].axhline(held_triad_share, color="#222222", linestyle="--", linewidth=1.6, label="held triad share")
    axes[0, 1].axhline(held_pair_top, color="#555555", linestyle=":", linewidth=1.6, label="held pair-top share")
    axes[0, 1].axhline(held_max_peak / 100.0, color="#888888", linestyle="-.", linewidth=1.4, label="held max peak / 100")
    axes[0, 1].bar(
        model_positions - 0.2,
        [float(model_comparisons[label]["triad_share"]) for label in model_labels],
        width=0.18,
        color="#4c72b0",
        label="triad share",
    )
    axes[0, 1].bar(
        model_positions,
        [float(model_comparisons[label]["pair_top_successor_share"]) for label in model_labels],
        width=0.18,
        color="#dd8452",
        label="pair-top share",
    )
    axes[0, 1].bar(
        model_positions + 0.2,
        [int(model_comparisons[label]["max_peak_offset"]) / 100.0 for label in model_labels],
        width=0.18,
        color="#55a868",
        label="max peak / 100",
    )
    axes[0, 1].set_title("Held-out structure targets")
    axes[0, 1].set_ylabel("Share / scaled peak")
    axes[0, 1].set_xticks(model_positions)
    axes[0, 1].set_xticklabels([label.replace("_", " ") for label in model_labels], rotation=15, ha="right")
    axes[0, 1].grid(axis="y", alpha=0.25)
    axes[0, 1].legend(loc="upper right")

    second_order_top_states = summary["second_order_synthetic_summary"]["top_states"]
    state_labels = [row["reduced_state"] for row in second_order_top_states[:8]]
    synthetic_distribution = {
        row["reduced_state"]: row["share"]
        for row in second_order_top_states
    }
    held_state_distribution = distribution_cache(summary, "held_states")
    axes[1, 0].bar(
        np.arange(len(state_labels)) - 0.18,
        [held_state_distribution.get(label, 0.0) for label in state_labels],
        width=0.36,
        color="#999999",
        label="held 10^18",
    )
    axes[1, 0].bar(
        np.arange(len(state_labels)) + 0.18,
        [synthetic_distribution.get(label, 0.0) for label in state_labels],
        width=0.36,
        color=MODEL_COLORS["second_order_rotor"],
        label="second-order 10k",
    )
    axes[1, 0].set_title("Leading reduced states in the synthetic grammar walk")
    axes[1, 0].set_ylabel("Share")
    axes[1, 0].set_xticks(np.arange(len(state_labels)))
    axes[1, 0].set_xticklabels(state_labels, rotation=40, ha="right")
    axes[1, 0].grid(axis="y", alpha=0.25)
    axes[1, 0].legend(loc="upper right")

    peak_labels = [row["next_peak_offset"] for row in summary["second_order_synthetic_summary"]["top_peak_offsets"][:10]]
    held_peak_distribution = distribution_cache(summary, "held_peaks")
    second_peak_distribution = distribution_cache(summary, "second_order_peaks")
    axes[1, 1].bar(
        np.arange(len(peak_labels)) - 0.18,
        [held_peak_distribution.get(offset, 0.0) for offset in peak_labels],
        width=0.36,
        color="#999999",
        label="held 10^18",
    )
    axes[1, 1].bar(
        np.arange(len(peak_labels)) + 0.18,
        [second_peak_distribution.get(offset, 0.0) for offset in peak_labels],
        width=0.36,
        color=MODEL_COLORS["second_order_rotor"],
        label="second-order 10k",
    )
    axes[1, 1].set_title("Peak-offset distribution: held-out vs second-order synthetic")
    axes[1, 1].set_ylabel("Share")
    axes[1, 1].set_xticks(np.arange(len(peak_labels)))
    axes[1, 1].set_xticklabels([str(offset) for offset in peak_labels])
    axes[1, 1].grid(axis="y", alpha=0.25)
    axes[1, 1].legend(loc="upper right")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=220)
    plt.close(fig)


def distribution_cache(summary: dict[str, object], key: str) -> dict[Hashable, float]:
    """Read one cached distribution from the JSON summary."""
    payload = summary["plot_cache"][key]
    return {
        int(item["key"]) if item["kind"] == "int" else item["key"]: item["share"]
        for item in payload
    }


def cache_distribution(values: list[Hashable]) -> list[dict[str, object]]:
    """Serialize one empirical distribution for the JSON summary plot cache."""
    serialized: list[dict[str, object]] = []
    for key, share in sorted(distribution(values).items(), key=lambda item: item[0]):
        serialized.append(
            {
                "kind": "int" if isinstance(key, int) else "str",
                "key": key,
                "share": share,
            }
        )
    return serialized


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    """Write one synthetic sequence CSV with LF endings."""
    fieldnames = [
        "step_index",
        "reduced_state",
        "open_family",
        "carrier_family",
        "d_bucket",
        "emitted_type_key",
        "emitted_next_dmin",
        "emitted_next_peak_offset",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main(argv: list[str] | None = None) -> int:
    """Run the deterministic generative grammar probe."""
    args = build_parser().parse_args(argv)
    if args.train_min_power > args.train_max_power:
        raise ValueError("train_min_power must be <= train_max_power")
    if args.held_power <= args.train_max_power:
        raise ValueError("held_power must be larger than the training powers")
    if args.synthetic_length < 2:
        raise ValueError("synthetic_length must be at least 2")

    rows = load_rows(args.detail_csv)
    train_surfaces = [
        power_surface_label(power)
        for power in range(args.train_min_power, args.train_max_power + 1)
    ]
    held_surface = power_surface_label(args.held_power)

    started = time.perf_counter()
    summary, synthetic_rows = summarize(
        rows=rows,
        train_surfaces=train_surfaces,
        held_surface=held_surface,
        synthetic_length=args.synthetic_length,
    )
    held_rows = [row for row in rows if row["surface_display_label"] == held_surface]
    summary["plot_cache"] = {
        "held_states": cache_distribution([reduced_state(row) for row in held_rows]),
        "held_peaks": cache_distribution([int(row["next_peak_offset"]) for row in held_rows]),
        "second_order_peaks": cache_distribution(
            [int(row["emitted_next_peak_offset"]) for row in synthetic_rows]
        ),
    }
    summary["runtime_seconds"] = time.perf_counter() - started

    args.output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = args.output_dir / "gwr_dni_gap_type_generative_probe_summary.json"
    csv_path = args.output_dir / "gwr_dni_gap_type_generative_probe_synthetic.csv"
    plot_path = args.output_dir / "gwr_dni_gap_type_generative_probe_overview.png"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    write_csv(csv_path, synthetic_rows)
    plot_overview(summary, plot_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
