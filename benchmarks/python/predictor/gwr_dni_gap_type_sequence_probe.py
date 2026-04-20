#!/usr/bin/env python3
"""Probe transition structure in the exact GWR/DNI gap-type sequence."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT_DIR = ROOT / "output"
DEFAULT_DETAIL_CSV = ROOT / "output" / "gwr_dni_gap_type_catalog_details.csv"
SELECTED_SURFACES = ("<=10^6", "10^12", "10^15", "10^18")
REDUCED_ALPHABET = "open_family_d_bucket"
ALPHABETS = ("exact_type", "family", "open_family", REDUCED_ALPHABET)
ALPHABET_COLORS = {
    "exact_type": "#4c72b0",
    "family": "#dd8452",
    "open_family": "#55a868",
    REDUCED_ALPHABET: "#c44e52",
}
D_BUCKET_LABELS = (
    "d<=4",
    "5<=d<=16",
    "17<=d<=64",
    "d>64",
)


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description="Probe transition structure in the exact GWR/DNI gap-type sequence.",
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
        help="Directory for JSON and PNG artifacts.",
    )
    return parser


def load_rows(detail_csv: Path) -> list[dict[str, str]]:
    """Load the catalog detail rows."""
    if not detail_csv.exists():
        raise FileNotFoundError(
            f"detail CSV does not exist: {detail_csv}"
        )
    with detail_csv.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError("detail CSV must contain at least one data row")
    return rows


def surface_order(rows: list[dict[str, str]]) -> list[str]:
    """Return the stable surface order preserved in the detail CSV."""
    order: list[str] = []
    seen: set[str] = set()
    for row in rows:
        label = row["surface_display_label"]
        if label in seen:
            continue
        seen.add(label)
        order.append(label)
    return order


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


def state_value(row: dict[str, str], alphabet: str) -> str:
    """Return the selected sequence state for one row."""
    if alphabet == "exact_type":
        return row["type_key"]
    if alphabet == "family":
        return row["carrier_family"]
    if alphabet == "open_family":
        return open_family_state(row)
    if alphabet == REDUCED_ALPHABET:
        return f"{open_family_state(row)}|{d_bucket(row['next_dmin'])}"
    raise ValueError(f"unsupported alphabet {alphabet}")


def sequence_metrics(sequence: list[str]) -> dict[str, float | int]:
    """Return transition concentration metrics for one sequence."""
    if len(sequence) < 3:
        raise ValueError("sequence must contain at least 3 states")

    support: dict[str, Counter[str]] = defaultdict(Counter)
    for current_state, next_state in zip(sequence, sequence[1:]):
        support[current_state][next_state] += 1

    observation_count = len(sequence) - 1
    unique_successor_state_count = sum(1 for counter in support.values() if len(counter) == 1)
    unique_successor_observation_count = sum(
        sum(counter.values()) for counter in support.values() if len(counter) == 1
    )

    pair_support: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    for left_state, current_state, next_state in zip(sequence, sequence[1:], sequence[2:]):
        pair_support[(left_state, current_state)][next_state] += 1

    pair_observation_count = len(sequence) - 2
    unique_pair_state_count = sum(1 for counter in pair_support.values() if len(counter) == 1)
    unique_pair_observation_count = sum(
        sum(counter.values()) for counter in pair_support.values() if len(counter) == 1
    )

    return {
        "state_count": len(set(sequence)),
        "observation_count": observation_count,
        "unique_successor_state_rate": unique_successor_state_count / len(support),
        "unique_successor_observation_share": (
            unique_successor_observation_count / observation_count
        ),
        "weighted_top_successor_share": (
            sum(max(counter.values()) for counter in support.values()) / observation_count
        ),
        "mean_successor_fanout": (
            sum(len(counter) for counter in support.values()) / len(support)
        ),
        "pair_unique_successor_state_rate": (
            unique_pair_state_count / len(pair_support)
        ),
        "pair_unique_successor_observation_share": (
            unique_pair_observation_count / pair_observation_count
        ),
        "pair_weighted_top_successor_share": (
            sum(max(counter.values()) for counter in pair_support.values())
            / pair_observation_count
        ),
    }


def row_normalized_transition_matrix(
    sequence: list[str],
    state_order: list[str] | None = None,
) -> tuple[list[str], list[list[float]], dict[str, Counter[str]]]:
    """Return the row-normalized transition matrix for one sequence."""
    if len(sequence) < 2:
        raise ValueError("sequence must contain at least 2 states")

    support: dict[str, Counter[str]] = defaultdict(Counter)
    for current_state, next_state in zip(sequence, sequence[1:]):
        support[current_state][next_state] += 1

    if state_order is None:
        state_order = sorted(support)

    matrix: list[list[float]] = []
    for current_state in state_order:
        row_total = sum(support[current_state].values())
        if row_total == 0:
            matrix.append([0.0 for _ in state_order])
            continue
        matrix.append(
            [support[current_state][next_state] / row_total for next_state in state_order]
        )
    return state_order, matrix, support


def top_lift_transitions(
    sequence: list[str],
    limit: int = 12,
    min_count: int = 3,
) -> list[dict[str, float | int | str]]:
    """Return the strongest current-to-next lifts relative to the surface marginal."""
    if len(sequence) < 2:
        raise ValueError("sequence must contain at least 2 states")

    support: dict[str, Counter[str]] = defaultdict(Counter)
    for current_state, next_state in zip(sequence, sequence[1:]):
        support[current_state][next_state] += 1

    totals = Counter(sequence)
    total_count = len(sequence)
    lifts: list[dict[str, float | int | str]] = []
    for current_state, counter in support.items():
        row_total = sum(counter.values())
        for next_state, count in counter.items():
            if count < min_count:
                continue
            transition_probability = count / row_total
            marginal_probability = totals[next_state] / total_count
            lifts.append(
                {
                    "current_state": current_state,
                    "next_state": next_state,
                    "count": int(count),
                    "transition_probability": transition_probability,
                    "marginal_probability": marginal_probability,
                    "lift": transition_probability / marginal_probability,
                }
            )

    lifts.sort(
        key=lambda row: (
            float(row["lift"]),
            float(row["transition_probability"]),
            int(row["count"]),
        ),
        reverse=True,
    )
    return lifts[:limit]


def closure_metrics(sequence: list[str], core_states: set[str]) -> dict[str, float | int]:
    """Measure how completely a sequence lives inside a fixed core state set."""
    if len(sequence) < 2:
        raise ValueError("sequence must contain at least 2 states")

    observation_count = len(sequence) - 1
    state_set = set(sequence)
    next_core_observation_count = sum(
        1 for next_state in sequence[1:] if next_state in core_states
    )
    transition_core_observation_count = sum(
        1
        for current_state, next_state in zip(sequence, sequence[1:])
        if current_state in core_states and next_state in core_states
    )

    return {
        "state_count": len(state_set),
        "core_state_count": len(state_set & core_states),
        "core_state_share": len(state_set & core_states) / len(state_set),
        "next_core_observation_share": next_core_observation_count / observation_count,
        "transition_core_observation_share": (
            transition_core_observation_count / observation_count
        ),
    }


def l1_distance(matrix_a: list[list[float]], matrix_b: list[list[float]]) -> float:
    """Return the entrywise L1 distance between two equal-shaped matrices."""
    if len(matrix_a) != len(matrix_b):
        raise ValueError("matrix row counts must match")
    distance = 0.0
    for row_a, row_b in zip(matrix_a, matrix_b):
        if len(row_a) != len(row_b):
            raise ValueError("matrix column counts must match")
        for value_a, value_b in zip(row_a, row_b):
            distance += abs(value_a - value_b)
    return distance


def high_scale_core_states(
    rows_by_surface: dict[str, list[dict[str, str]]],
    alphabet: str,
    baseline_surface: str = "<=10^6",
) -> set[str]:
    """Return states that persist across every post-baseline sampled surface."""
    surface_labels = [
        label for label in rows_by_surface
        if label != baseline_surface
    ]
    if not surface_labels:
        raise ValueError("need at least one post-baseline surface")

    core_states = {
        state_value(row, alphabet)
        for row in rows_by_surface[surface_labels[0]]
    }
    for surface_label in surface_labels[1:]:
        core_states &= {
            state_value(row, alphabet)
            for row in rows_by_surface[surface_label]
        }
    return core_states


def transition_l1_summary(
    rows_by_surface: dict[str, list[dict[str, str]]],
    alphabet: str,
) -> list[dict[str, float | str]]:
    """Return selected-surface transition distances for one alphabet."""
    distances: list[dict[str, float | str]] = []
    for left_surface in SELECTED_SURFACES:
        if left_surface not in rows_by_surface:
            continue
        left_sequence = [
            state_value(row, alphabet)
            for row in rows_by_surface[left_surface]
        ]
        left_states = set(left_sequence)
        for right_surface in SELECTED_SURFACES:
            if right_surface <= left_surface:
                continue
            if right_surface not in rows_by_surface:
                continue
            right_sequence = [
                state_value(row, alphabet)
                for row in rows_by_surface[right_surface]
            ]
            union_order = sorted(left_states | set(right_sequence))
            _, left_matrix, _ = row_normalized_transition_matrix(left_sequence, union_order)
            _, right_matrix, _ = row_normalized_transition_matrix(right_sequence, union_order)
            distances.append(
                {
                    "left_surface": left_surface,
                    "right_surface": right_surface,
                    "l1_distance": l1_distance(left_matrix, right_matrix),
                }
            )
    return distances


def summarize(rows: list[dict[str, str]]) -> dict[str, object]:
    """Aggregate the sequence probe into a JSON-ready summary."""
    order = surface_order(rows)
    rows_by_surface: dict[str, list[dict[str, str]]] = {
        label: [row for row in rows if row["surface_display_label"] == label]
        for label in order
    }

    sequence_summaries: dict[str, dict[str, dict[str, float | int]]] = {}
    closure_summaries: dict[str, dict[str, dict[str, float | int]]] = {}
    selected_open_family_heatmaps: dict[str, dict[str, object]] = {}
    selected_open_family_lifts: dict[str, list[dict[str, float | int | str]]] = {}
    selected_reduced_state_heatmaps: dict[str, dict[str, object]] = {}
    selected_reduced_state_lifts: dict[str, list[dict[str, float | int | str]]] = {}
    open_family_core = high_scale_core_states(rows_by_surface, "open_family")
    reduced_state_core = high_scale_core_states(rows_by_surface, REDUCED_ALPHABET)

    for surface_label in order:
        surface_rows = rows_by_surface[surface_label]
        alphabet_payload: dict[str, dict[str, float | int]] = {}
        for alphabet in ALPHABETS:
            sequence = [state_value(row, alphabet) for row in surface_rows]
            alphabet_payload[alphabet] = sequence_metrics(sequence)

        sequence_summaries[surface_label] = alphabet_payload
        closure_summaries[surface_label] = {
            "open_family": closure_metrics(
                [state_value(row, "open_family") for row in surface_rows],
                open_family_core,
            ),
            REDUCED_ALPHABET: closure_metrics(
                [state_value(row, REDUCED_ALPHABET) for row in surface_rows],
                reduced_state_core,
            ),
        }

        if surface_label in SELECTED_SURFACES:
            open_family_sequence = [state_value(row, "open_family") for row in surface_rows]
            state_order, matrix, _ = row_normalized_transition_matrix(open_family_sequence)
            selected_open_family_heatmaps[surface_label] = {
                "state_order": state_order,
                "matrix": matrix,
            }
            selected_open_family_lifts[surface_label] = top_lift_transitions(open_family_sequence)
            reduced_sequence = [state_value(row, REDUCED_ALPHABET) for row in surface_rows]
            reduced_state_order, reduced_matrix, _ = row_normalized_transition_matrix(reduced_sequence)
            selected_reduced_state_heatmaps[surface_label] = {
                "state_order": reduced_state_order,
                "matrix": reduced_matrix,
            }
            selected_reduced_state_lifts[surface_label] = top_lift_transitions(reduced_sequence)

    return {
        "input_surface_order": order,
        "selected_surfaces": list(SELECTED_SURFACES),
        "reduced_state_definition": {
            "alphabet": REDUCED_ALPHABET,
            "state_form": "open_family|d_bucket",
            "d_bucket_labels": list(D_BUCKET_LABELS),
        },
        "sequence_summaries": sequence_summaries,
        "high_scale_open_family_core": sorted(open_family_core),
        "high_scale_reduced_state_core": sorted(reduced_state_core),
        "closure_summaries": closure_summaries,
        "selected_open_family_heatmaps": selected_open_family_heatmaps,
        "selected_open_family_lifts": selected_open_family_lifts,
        "selected_reduced_state_heatmaps": selected_reduced_state_heatmaps,
        "selected_reduced_state_lifts": selected_reduced_state_lifts,
        "open_family_transition_l1": transition_l1_summary(rows_by_surface, "open_family"),
        "reduced_state_transition_l1": transition_l1_summary(rows_by_surface, REDUCED_ALPHABET),
    }


def plot_summary(summary: dict[str, object], output_path: Path) -> None:
    """Render one compact plot for the sequence probe."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    surface_order_labels = summary["input_surface_order"]
    surface_positions = np.arange(len(surface_order_labels))
    sequence_summaries = summary["sequence_summaries"]
    closure_summaries = summary["closure_summaries"]

    fig, axes = plt.subplots(3, 2, figsize=(16, 15), constrained_layout=True)

    for alphabet in ALPHABETS:
        values = [
            float(sequence_summaries[surface][alphabet]["weighted_top_successor_share"])
            for surface in surface_order_labels
        ]
        axes[0, 0].plot(
            surface_positions,
            values,
            marker="o",
            linewidth=2.0,
            color=ALPHABET_COLORS[alphabet],
            label=alphabet.replace("_", " "),
        )
    axes[0, 0].set_title("One-step transition concentration by state alphabet")
    axes[0, 0].set_ylabel("Weighted top-successor share")
    axes[0, 0].set_xticks(surface_positions)
    axes[0, 0].set_xticklabels(surface_order_labels, rotation=35, ha="right")
    axes[0, 0].grid(axis="y", alpha=0.25)
    axes[0, 0].legend(loc="lower right")

    for alphabet in ALPHABETS:
        values = [
            float(sequence_summaries[surface][alphabet]["pair_weighted_top_successor_share"])
            for surface in surface_order_labels
        ]
        axes[0, 1].plot(
            surface_positions,
            values,
            marker="o",
            linewidth=2.0,
            color=ALPHABET_COLORS[alphabet],
            label=alphabet.replace("_", " "),
        )
    axes[0, 1].set_title("Two-step transition concentration by state alphabet")
    axes[0, 1].set_ylabel("Pair weighted top-successor share")
    axes[0, 1].set_xticks(surface_positions)
    axes[0, 1].set_xticklabels(surface_order_labels, rotation=35, ha="right")
    axes[0, 1].grid(axis="y", alpha=0.25)
    axes[0, 1].legend(loc="lower right")

    for alphabet in ("open_family", REDUCED_ALPHABET):
        values = [
            int(sequence_summaries[surface][alphabet]["state_count"])
            for surface in surface_order_labels
        ]
        axes[1, 0].plot(
            surface_positions,
            values,
            marker="o",
            linewidth=2.0,
            color=ALPHABET_COLORS[alphabet],
            label=alphabet.replace("_", " "),
        )
    axes[1, 0].set_title("Compressed-state counts by surface")
    axes[1, 0].set_ylabel("State count")
    axes[1, 0].set_xticks(surface_positions)
    axes[1, 0].set_xticklabels(surface_order_labels, rotation=35, ha="right")
    axes[1, 0].grid(axis="y", alpha=0.25)
    axes[1, 0].legend(loc="upper right")

    for alphabet in ("open_family", REDUCED_ALPHABET):
        values = [
            float(closure_summaries[surface][alphabet]["transition_core_observation_share"])
            for surface in surface_order_labels
        ]
        axes[1, 1].plot(
            surface_positions,
            values,
            marker="o",
            linewidth=2.0,
            color=ALPHABET_COLORS[alphabet],
            label=alphabet.replace("_", " "),
        )
    axes[1, 1].set_title("High-scale core closure by surface")
    axes[1, 1].set_ylabel("Core transition share")
    axes[1, 1].set_xticks(surface_positions)
    axes[1, 1].set_xticklabels(surface_order_labels, rotation=35, ha="right")
    axes[1, 1].set_ylim(0.94, 1.005)
    axes[1, 1].grid(axis="y", alpha=0.25)
    axes[1, 1].legend(loc="lower right")

    for axis_index, surface_label in enumerate(("<=10^6", "10^18")):
        axis = axes[2, axis_index]
        heatmap = summary["selected_reduced_state_heatmaps"][surface_label]
        state_order = heatmap["state_order"]
        matrix = np.array(heatmap["matrix"])
        image = axis.imshow(matrix, cmap="magma", aspect="auto", vmin=0.0, vmax=max(matrix.max(), 0.35))
        axis.set_title(f"Reduced-state transition grammar: {surface_label}")
        axis.set_xticks(np.arange(len(state_order)))
        axis.set_xticklabels(state_order, rotation=90, fontsize=7)
        axis.set_yticks(np.arange(len(state_order)))
        axis.set_yticklabels(state_order, fontsize=7)
        axis.set_xlabel("Next state")
        axis.set_ylabel("Current state")
        fig.colorbar(image, ax=axis, fraction=0.046, pad=0.04)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=220)
    plt.close(fig)


def main(argv: list[str] | None = None) -> int:
    """Run the gap-type sequence probe and write JSON plus PNG artifacts."""
    args = build_parser().parse_args(argv)
    rows = load_rows(args.detail_csv)
    summary = summarize(rows)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    summary_path = args.output_dir / "gwr_dni_gap_type_sequence_probe_summary.json"
    plot_path = args.output_dir / "gwr_dni_gap_type_sequence_probe_overview.png"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    plot_summary(summary, plot_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
