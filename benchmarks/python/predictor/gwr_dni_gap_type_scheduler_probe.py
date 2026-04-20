#!/usr/bin/env python3
"""Test finite scheduler candidates against the extreme-scale gap-type windows."""

from __future__ import annotations

import argparse
import importlib.util
import json
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Callable, Hashable


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT_DIR = ROOT / "output"
DEFAULT_DETAIL_CSV = ROOT / "output" / "gwr_dni_gap_type_catalog_details.csv"
DEFAULT_TRAIN_MIN_POWER = 7
DEFAULT_TRAIN_MAX_POWER = 17
DEFAULT_REFERENCE_MIN_POWER = 12
DEFAULT_REFERENCE_MAX_POWER = 18
DEFAULT_SYNTHETIC_LENGTH = 1_000_000
DEFAULT_WINDOW_LENGTH = 256
DEFAULT_MOD_CYCLE_LENGTH = 8
GEN_PROBE_PATH = Path(__file__).with_name("gwr_dni_gap_type_generative_probe.py")
ENGINE_DECODE_PATH = Path(__file__).with_name("gwr_dni_gap_type_engine_decode.py")
MODEL_COLORS = {
    "second_order_rotor": "#dd8452",
    "mod_cycle_scheduler": "#8172b2",
    "lag2_state_scheduler": "#4c72b0",
}


def load_module(module_path: Path, module_name: str):
    """Load one sibling Python module from file."""
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


GEN_PROBE = load_module(GEN_PROBE_PATH, "gwr_dni_gap_type_generative_probe_scheduler")
ENGINE_DECODE = load_module(
    ENGINE_DECODE_PATH,
    "gwr_dni_gap_type_engine_decode_scheduler",
)


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Probe finite scheduler candidates for the reduced gap-type grammar "
            "against the sampled 10^12..10^18 window surface."
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
        help="Smallest sampled decade power used for the real comparison pool.",
    )
    parser.add_argument(
        "--reference-max-power",
        type=int,
        default=DEFAULT_REFERENCE_MAX_POWER,
        help="Largest sampled decade power used for the real comparison pool.",
    )
    parser.add_argument(
        "--synthetic-length",
        type=int,
        default=DEFAULT_SYNTHETIC_LENGTH,
        help="Length of each deterministic synthetic walk.",
    )
    parser.add_argument(
        "--window-length",
        type=int,
        default=DEFAULT_WINDOW_LENGTH,
        help="Local window length used for pooled concentration comparisons.",
    )
    parser.add_argument(
        "--mod-cycle-length",
        type=int,
        default=DEFAULT_MOD_CYCLE_LENGTH,
        help="Cycle length for the simple modulo scheduler candidate.",
    )
    return parser


def power_surface_label(power: int) -> str:
    """Return one sampled decade display label."""
    return f"10^{power}"


def state_family(state: str) -> str:
    """Extract the carrier family from one reduced-state key."""
    return state.split("|", 1)[0].split("_", 1)[1]


def windowed_concentrations(states: list[str], window_length: int) -> dict[str, float]:
    """Return pooled concentration metrics over fixed non-overlapping windows."""
    numerators = {1: 0.0, 2: 0.0, 3: 0.0}
    denominators = {1: 0, 2: 0, 3: 0}

    for start in range(0, len(states) - window_length + 1, window_length):
        window = states[start:start + window_length]
        for order in (1, 2, 3):
            share = ENGINE_DECODE.higher_order_top_successor_share(window, order)
            numerators[order] += share * (len(window) - order)
            denominators[order] += len(window) - order

    return {
        "one_step": numerators[1] / denominators[1],
        "two_step": numerators[2] / denominators[2],
        "three_step": numerators[3] / denominators[3],
    }


def concentration_l1(
    left: dict[str, float],
    right: dict[str, float],
) -> float:
    """Return the L1 gap across one-step, two-step, and three-step concentrations."""
    return sum(abs(left[key] - right[key]) for key in ("one_step", "two_step", "three_step"))


def pruned_transition_counter(
    counter: dict[Hashable, Counter[str]],
    successor_context: Callable[[Hashable, str], Hashable],
) -> dict[Hashable, Counter[str]]:
    """Prune one transition surface to the largest forward-staying context set."""
    active = set(counter)
    while True:
        next_active = {
            context
            for context in active
            if any(successor_context(context, next_state) in active for next_state in counter[context])
        }
        if next_active == active:
            break
        active = next_active

    pruned: dict[Hashable, Counter[str]] = {}
    for context in sorted(active):
        kept = Counter()
        for next_state, count in counter[context].items():
            if successor_context(context, next_state) in active:
                kept[next_state] += count
        if kept:
            pruned[context] = kept
    return pruned


def emit_distribution_metrics(
    states: list[str],
    emission_counter: dict[str, Counter[tuple[str, int, int, str]]],
    real_family_distribution: dict[str, float],
    real_peak_distribution: dict[int, float],
    real_higher_divisor_share: float,
) -> dict[str, float]:
    """Emit state payloads deterministically and compare their distributions."""
    emission_rotors = {
        state: GEN_PROBE.Rotor(GEN_PROBE.balanced_cycle(counter))
        for state, counter in emission_counter.items()
    }
    family_counter: Counter[str] = Counter()
    peak_counter: Counter[int] = Counter()
    higher_divisor_count = 0

    for state in states:
        _, _, peak_offset, carrier_family = emission_rotors[state].next()
        family_counter[carrier_family] += 1
        peak_counter[peak_offset] += 1
        if "higher_divisor" in carrier_family:
            higher_divisor_count += 1

    total = len(states)
    family_distribution = {
        family: count / total
        for family, count in family_counter.items()
    }
    peak_distribution = {
        peak: count / total
        for peak, count in peak_counter.items()
    }
    higher_divisor_share = higher_divisor_count / total

    return {
        "family_l1_to_real_pool": GEN_PROBE.l1_distance(
            family_distribution,
            real_family_distribution,
        ),
        "peak_offset_l1_to_real_pool": GEN_PROBE.l1_distance(
            peak_distribution,
            real_peak_distribution,
        ),
        "higher_divisor_share": higher_divisor_share,
        "higher_divisor_share_error": abs(higher_divisor_share - real_higher_divisor_share),
    }


def evaluate_state_sequence(
    states: list[str],
    emission_counter: dict[str, Counter[tuple[str, int, int, str]]],
    real_window_concentrations: dict[str, float],
    real_family_distribution: dict[str, float],
    real_peak_distribution: dict[int, float],
    real_higher_divisor_share: float,
    window_length: int,
) -> dict[str, object]:
    """Evaluate one synthetic state stream against the real reference surface."""
    full_walk_concentrations = {
        "one_step": ENGINE_DECODE.higher_order_top_successor_share(states, 1),
        "two_step": ENGINE_DECODE.higher_order_top_successor_share(states, 2),
        "three_step": ENGINE_DECODE.higher_order_top_successor_share(states, 3),
    }
    pooled_window = windowed_concentrations(states, window_length)
    metrics = emit_distribution_metrics(
        states=states,
        emission_counter=emission_counter,
        real_family_distribution=real_family_distribution,
        real_peak_distribution=real_peak_distribution,
        real_higher_divisor_share=real_higher_divisor_share,
    )
    metrics.update(
        {
            "full_walk_concentrations": full_walk_concentrations,
            "pooled_window_concentrations": pooled_window,
            "pooled_window_concentration_l1": concentration_l1(
                pooled_window,
                real_window_concentrations,
            ),
        }
    )
    return metrics


def build_third_order_support(
    segments: list[list[dict[str, str]]],
) -> tuple[dict[tuple[str, str, str], Counter[str]], tuple[str, str, str]]:
    """Build the third-order scheduler support keyed by the lag-2 reduced state."""
    counter: dict[tuple[str, str, str], Counter[str]] = defaultdict(Counter)
    start_counter: Counter[tuple[str, str, str]] = Counter()

    for segment in segments:
        states = [GEN_PROBE.reduced_state(row) for row in segment]
        if len(states) < 4:
            continue
        start_counter[(states[0], states[1], states[2])] += 1
        for left2, left1, current, next_state in zip(
            states,
            states[1:],
            states[2:],
            states[3:],
        ):
            counter[(left2, left1, current)][next_state] += 1

    pruned = pruned_transition_counter(
        counter=counter,
        successor_context=lambda context, next_state: (context[1], context[2], next_state),
    )
    if not pruned:
        raise ValueError("third-order scheduler support is empty after pruning")

    start_context = max(
        (
            (context, count)
            for context, count in start_counter.items()
            if context in pruned
        ),
        key=lambda item: (item[1], item[0]),
        default=(max(pruned, key=lambda context: (sum(pruned[context].values()), context)), 0),
    )[0]
    return pruned, start_context


def build_mod_cycle_support(
    segments: list[list[dict[str, str]]],
    mod_cycle_length: int,
) -> tuple[dict[tuple[int, str, str], Counter[str]], tuple[int, str, str]]:
    """Build the simple modulo scheduler support."""
    counter: dict[tuple[int, str, str], Counter[str]] = defaultdict(Counter)
    start_counter: Counter[tuple[int, str, str]] = Counter()

    for segment in segments:
        states = [GEN_PROBE.reduced_state(row) for row in segment]
        if len(states) < 3:
            continue
        start_counter[(0, states[0], states[1])] += 1
        for index, (left_state, current_state, next_state) in enumerate(
            zip(states, states[1:], states[2:]),
            start=0,
        ):
            counter[(index % mod_cycle_length, left_state, current_state)][next_state] += 1

    pruned = pruned_transition_counter(
        counter=counter,
        successor_context=lambda context, next_state: (
            (context[0] + 1) % mod_cycle_length,
            context[2],
            next_state,
        ),
    )
    if not pruned:
        raise ValueError("mod-cycle scheduler support is empty after pruning")

    start_context = max(
        (
            (context, count)
            for context, count in start_counter.items()
            if context in pruned
        ),
        key=lambda item: (item[1], item[0]),
        default=(max(pruned, key=lambda context: (sum(pruned[context].values()), context)), 0),
    )[0]
    return pruned, start_context


def simulate_second_order(
    support: dict[str, object],
    synthetic_length: int,
) -> list[str]:
    """Emit one deterministic second-order state sequence."""
    left_state, current_state = support["start_pair"]
    transition_rotors = {
        context: GEN_PROBE.Rotor(GEN_PROBE.balanced_cycle(counter))
        for context, counter in support["second_order_counter"].items()
    }
    states = [left_state, current_state]
    while len(states) < synthetic_length:
        next_state = transition_rotors[(left_state, current_state)].next()
        states.append(next_state)
        left_state, current_state = current_state, next_state
    return states


def simulate_third_order(
    transition_counter: dict[tuple[str, str, str], Counter[str]],
    start_context: tuple[str, str, str],
    synthetic_length: int,
) -> list[str]:
    """Emit one deterministic third-order state sequence."""
    transition_rotors = {
        context: GEN_PROBE.Rotor(GEN_PROBE.balanced_cycle(counter))
        for context, counter in transition_counter.items()
    }
    states = [start_context[0], start_context[1], start_context[2]]
    while len(states) < synthetic_length:
        next_state = transition_rotors[(states[-3], states[-2], states[-1])].next()
        states.append(next_state)
    return states


def simulate_mod_cycle(
    transition_counter: dict[tuple[int, str, str], Counter[str]],
    start_context: tuple[int, str, str],
    synthetic_length: int,
    mod_cycle_length: int,
) -> list[str]:
    """Emit one deterministic modulo-scheduler state sequence."""
    phase, left_state, current_state = start_context
    transition_rotors = {
        context: GEN_PROBE.Rotor(GEN_PROBE.balanced_cycle(counter))
        for context, counter in transition_counter.items()
    }
    states = [left_state, current_state]
    while len(states) < synthetic_length:
        next_state = transition_rotors[(phase, left_state, current_state)].next()
        states.append(next_state)
        phase = (phase + 1) % mod_cycle_length
        left_state, current_state = current_state, next_state
    return states


def summarize(
    rows: list[dict[str, str]],
    train_surfaces: list[str],
    reference_surfaces: list[str],
    synthetic_length: int,
    window_length: int,
    mod_cycle_length: int,
) -> dict[str, object]:
    """Build the scheduler-probe summary."""
    rows_by_surface = GEN_PROBE.surface_rows(rows)
    core_states = GEN_PROBE.persistent_core_states(rows_by_surface, train_surfaces)
    segments = GEN_PROBE.contiguous_core_segments(rows_by_surface, train_surfaces, core_states)
    support = GEN_PROBE.build_training_support(segments)

    real_rows = []
    for surface_label in reference_surfaces:
        real_rows.extend(
            row
            for row in rows_by_surface[surface_label]
            if GEN_PROBE.reduced_state(row) in core_states
        )
    real_family_distribution = GEN_PROBE.distribution(
        [row["carrier_family"] for row in real_rows]
    )
    real_peak_distribution = GEN_PROBE.distribution(
        [int(row["next_peak_offset"]) for row in real_rows]
    )
    real_higher_divisor_share = (
        sum(1 for row in real_rows if "higher_divisor" in row["carrier_family"])
        / len(real_rows)
    )
    real_window_concentrations = ENGINE_DECODE.pooled_real_concentrations(
        rows_by_surface,
        reference_surfaces,
        core_states,
    )

    third_order_counter, third_order_start = build_third_order_support(segments)
    mod_cycle_counter, mod_cycle_start = build_mod_cycle_support(
        segments,
        mod_cycle_length=mod_cycle_length,
    )

    model_rows = [
        {
            "model_id": "second_order_rotor",
            "description": "Baseline persistent 14-state second-order rotor.",
            "scheduler_phase_count": 0,
            "transition_context_count": len(support["second_order_counter"]),
            "states": simulate_second_order(support, synthetic_length),
        },
        {
            "model_id": "mod_cycle_scheduler",
            "description": (
                f"Simple {mod_cycle_length}-phase modulo scheduler over the second-order core."
            ),
            "scheduler_phase_count": mod_cycle_length,
            "transition_context_count": len(mod_cycle_counter),
            "states": simulate_mod_cycle(
                transition_counter=mod_cycle_counter,
                start_context=mod_cycle_start,
                synthetic_length=synthetic_length,
                mod_cycle_length=mod_cycle_length,
            ),
        },
        {
            "model_id": "lag2_state_scheduler",
            "description": (
                "Finite scheduler whose phase is the reduced state two steps back; "
                "equivalently, a third-order walk on the persistent core."
            ),
            "scheduler_phase_count": len({context[0] for context in third_order_counter}),
            "transition_context_count": len(third_order_counter),
            "states": simulate_third_order(
                transition_counter=third_order_counter,
                start_context=third_order_start,
                synthetic_length=synthetic_length,
            ),
        },
    ]

    models: dict[str, object] = {}
    ranking_payload: list[tuple[float, str]] = []
    for row in model_rows:
        metrics = evaluate_state_sequence(
            states=row["states"],
            emission_counter=support["emission_counter"],
            real_window_concentrations=real_window_concentrations,
            real_family_distribution=real_family_distribution,
            real_peak_distribution=real_peak_distribution,
            real_higher_divisor_share=real_higher_divisor_share,
            window_length=window_length,
        )
        models[row["model_id"]] = {
            "description": row["description"],
            "scheduler_phase_count": row["scheduler_phase_count"],
            "transition_context_count": row["transition_context_count"],
            **metrics,
        }
        ranking_payload.append((metrics["pooled_window_concentration_l1"], row["model_id"]))

    ranking = [
        {
            "model_id": model_id,
            "pooled_window_concentration_l1": error_value,
        }
        for error_value, model_id in sorted(ranking_payload)
    ]

    return {
        "synthetic_length": synthetic_length,
        "reference_window_length": window_length,
        "real_reference_window_concentrations": real_window_concentrations,
        "real_reference_higher_divisor_share": real_higher_divisor_share,
        "core_state_count": len(core_states),
        "core_states": sorted(core_states),
        "models": models,
        "ranking_by_pooled_window_concentration_l1": ranking,
        "best_model_id": ranking[0]["model_id"],
    }


def plot_summary(summary: dict[str, object], output_path: Path) -> None:
    """Render one compact overview plot."""
    import matplotlib.pyplot as plt

    model_ids = list(summary["models"])
    labels = ["1-step", "2-step", "3-step"]
    x_positions = range(len(labels))
    real_window = summary["real_reference_window_concentrations"]
    real_values = [
        real_window["one_step"],
        real_window["two_step"],
        real_window["three_step"],
    ]

    fig, axes = plt.subplots(2, 2, figsize=(15, 10), constrained_layout=True)

    pooled_ax = axes[0][0]
    width = 0.22
    offsets = {
        "second_order_rotor": -width,
        "mod_cycle_scheduler": 0.0,
        "lag2_state_scheduler": width,
    }
    for model_id in model_ids:
        pooled = summary["models"][model_id]["pooled_window_concentrations"]
        values = [pooled["one_step"], pooled["two_step"], pooled["three_step"]]
        pooled_ax.bar(
            [index + offsets[model_id] for index in x_positions],
            values,
            width=width,
            label=model_id,
            color=MODEL_COLORS[model_id],
        )
    pooled_ax.plot(
        list(x_positions),
        real_values,
        color="#000000",
        marker="o",
        linewidth=2,
        label="real pooled 256-window",
    )
    pooled_ax.set_title("Pooled Window Concentrations")
    pooled_ax.set_xticks(list(x_positions), labels)
    pooled_ax.set_ylim(0.25, 0.9)
    pooled_ax.legend(fontsize=8)

    full_ax = axes[0][1]
    for model_id in model_ids:
        full_walk = summary["models"][model_id]["full_walk_concentrations"]
        values = [full_walk["one_step"], full_walk["two_step"], full_walk["three_step"]]
        full_ax.bar(
            [index + offsets[model_id] for index in x_positions],
            values,
            width=width,
            label=model_id,
            color=MODEL_COLORS[model_id],
        )
    full_ax.plot(
        list(x_positions),
        real_values,
        color="#000000",
        marker="o",
        linewidth=2,
        label="real pooled 256-window",
    )
    full_ax.set_title("Full-Walk Concentrations vs Real Window Target")
    full_ax.set_xticks(list(x_positions), labels)
    full_ax.set_ylim(0.25, 0.9)
    full_ax.legend(fontsize=8)

    error_ax = axes[1][0]
    distribution_labels = ["family L1", "peak L1", "higher-divisor error"]
    for model_id in model_ids:
        model_summary = summary["models"][model_id]
        values = [
            model_summary["family_l1_to_real_pool"],
            model_summary["peak_offset_l1_to_real_pool"],
            model_summary["higher_divisor_share_error"],
        ]
        error_ax.bar(
            [index + offsets[model_id] for index in range(len(distribution_labels))],
            values,
            width=width,
            label=model_id,
            color=MODEL_COLORS[model_id],
        )
    error_ax.set_title("Distribution Errors")
    error_ax.set_xticks(range(len(distribution_labels)), distribution_labels)
    error_ax.legend(fontsize=8)

    ranking_ax = axes[1][1]
    ranking_ax.bar(
        model_ids,
        [
            summary["models"][model_id]["pooled_window_concentration_l1"]
            for model_id in model_ids
        ],
        color=[MODEL_COLORS[model_id] for model_id in model_ids],
    )
    ranking_ax.set_title("Pooled Window Concentration L1")
    ranking_ax.set_ylabel("L1 error")
    ranking_ax.tick_params(axis="x", labelrotation=15)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=220)
    plt.close(fig)


def main(argv: list[str] | None = None) -> int:
    """Run the scheduler probe and write its artifacts."""
    parser = build_parser()
    args = parser.parse_args(argv)

    start_time = time.perf_counter()
    rows = GEN_PROBE.load_rows(args.detail_csv)
    summary = summarize(
        rows=rows,
        train_surfaces=[
            power_surface_label(power)
            for power in range(args.train_min_power, args.train_max_power + 1)
        ],
        reference_surfaces=[
            power_surface_label(power)
            for power in range(args.reference_min_power, args.reference_max_power + 1)
        ],
        synthetic_length=args.synthetic_length,
        window_length=args.window_length,
        mod_cycle_length=args.mod_cycle_length,
    )
    summary["runtime_seconds"] = time.perf_counter() - start_time

    args.output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = args.output_dir / "gwr_dni_gap_type_scheduler_probe_summary.json"
    plot_path = args.output_dir / "gwr_dni_gap_type_scheduler_probe_overview.png"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    plot_summary(summary, plot_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
