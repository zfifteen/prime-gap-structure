#!/usr/bin/env python3
"""Probe hybrid finite schedulers for the reduced gap-type engine."""

from __future__ import annotations

import argparse
import importlib.util
import json
import time
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT_DIR = ROOT / "output"
DEFAULT_DETAIL_CSV = ROOT / "output" / "gwr_dni_gap_type_catalog_details.csv"
DEFAULT_RECORD_CSV = ROOT / "data" / "external" / "primegap_list_records_1e12_1e18.csv"
DEFAULT_TRAIN_MIN_POWER = 7
DEFAULT_TRAIN_MAX_POWER = 17
DEFAULT_REFERENCE_MIN_POWER = 12
DEFAULT_REFERENCE_MAX_POWER = 18
DEFAULT_SYNTHETIC_LENGTH = 1_000_000
DEFAULT_WINDOW_LENGTH = 256
DEFAULT_MOD_CYCLE_LENGTH = 8
DEFAULT_SWEEP_MIN_CYCLE = 2
DEFAULT_SWEEP_MAX_CYCLE = 12
SCHED_PROBE_PATH = Path(__file__).with_name("gwr_dni_gap_type_scheduler_probe.py")
MODEL_COLORS = {
    "second_order_rotor": "#dd8452",
    "lag2_state_scheduler": "#4c72b0",
    "mod_cycle_scheduler": "#8172b2",
    "hybrid_lag2_mod8_scheduler": "#55a868",
    "hybrid_lag2_mod8_reset_hdiv_scheduler": "#c44e52",
    "hybrid_lag2_mod8_reset_nontriad_scheduler": "#937860",
}


def load_module(module_path: Path, module_name: str):
    """Load one sibling Python module from file."""
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SCHED_PROBE = load_module(SCHED_PROBE_PATH, "gwr_dni_gap_type_scheduler_probe_hybrid")
GEN_PROBE = SCHED_PROBE.GEN_PROBE
ENGINE_DECODE = SCHED_PROBE.ENGINE_DECODE


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Test hybrid lag-2 and modulo schedulers for the reduced gap-type "
            "engine on both pooled-window and stationary-walk metrics."
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
        "--record-csv",
        type=Path,
        default=DEFAULT_RECORD_CSV,
        help="Record-gap extract used for the reset-signature summary.",
    )
    parser.add_argument(
        "--skip-record-analysis",
        action="store_true",
        help="Skip the exact record-gap reset-signature summary.",
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
        help="Cycle length for the explicit modulo scheduler and hybrid.",
    )
    parser.add_argument(
        "--sweep-min-cycle",
        type=int,
        default=DEFAULT_SWEEP_MIN_CYCLE,
        help="Smallest cycle length included in the cycle sweep.",
    )
    parser.add_argument(
        "--sweep-max-cycle",
        type=int,
        default=DEFAULT_SWEEP_MAX_CYCLE,
        help="Largest cycle length included in the cycle sweep.",
    )
    parser.add_argument(
        "--record-workers",
        type=int,
        default=ENGINE_DECODE.DEFAULT_RECORD_WORKERS,
        help="Worker count for the exact record-gap reset-signature summary.",
    )
    return parser


def state_family(state: str) -> str:
    """Extract the carrier family from one reduced-state key."""
    return state.split("|", 1)[0].split("_", 1)[1]


def next_phase(
    phase: int,
    next_state: str,
    mod_cycle_length: int,
    reset_mode: str,
) -> int:
    """Advance the finite scheduler phase under the requested reset law."""
    if reset_mode == "none":
        return (phase + 1) % mod_cycle_length
    if reset_mode == "higher_divisor":
        if "higher_divisor" in state_family(next_state):
            return 0
        return (phase + 1) % mod_cycle_length
    if reset_mode == "nontriad":
        if next_state not in set(GEN_PROBE.TRIAD_STATES):
            return 0
        return (phase + 1) % mod_cycle_length
    raise ValueError(f"unsupported reset mode: {reset_mode}")


def build_hybrid_support(
    segments: list[list[dict[str, str]]],
    mod_cycle_length: int,
    reset_mode: str,
) -> tuple[dict[tuple[int, str, str, str], Counter[str]], tuple[int, str, str, str]]:
    """Build the hybrid lag-2 plus modulo scheduler support."""
    counter: dict[tuple[int, str, str, str], Counter[str]] = defaultdict(Counter)
    start_counter: Counter[tuple[int, str, str, str]] = Counter()

    for segment in segments:
        states = [GEN_PROBE.reduced_state(row) for row in segment]
        if len(states) < 4:
            continue
        phase = 0
        start_counter[(phase, states[0], states[1], states[2])] += 1
        for left2, left1, current, next_state in zip(
            states,
            states[1:],
            states[2:],
            states[3:],
        ):
            counter[(phase, left2, left1, current)][next_state] += 1
            phase = next_phase(
                phase=phase,
                next_state=next_state,
                mod_cycle_length=mod_cycle_length,
                reset_mode=reset_mode,
            )

    pruned = SCHED_PROBE.pruned_transition_counter(
        counter=counter,
        successor_context=lambda context, next_state: (
            next_phase(
                phase=context[0],
                next_state=next_state,
                mod_cycle_length=mod_cycle_length,
                reset_mode=reset_mode,
            ),
            context[2],
            context[3],
            next_state,
        ),
    )
    if not pruned:
        raise ValueError("hybrid scheduler support is empty after pruning")

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


def simulate_hybrid(
    transition_counter: dict[tuple[int, str, str, str], Counter[str]],
    start_context: tuple[int, str, str, str],
    synthetic_length: int,
    mod_cycle_length: int,
    reset_mode: str,
) -> list[str]:
    """Emit one deterministic hybrid scheduler sequence."""
    phase, left2, left1, current = start_context
    transition_rotors = {
        context: GEN_PROBE.Rotor(GEN_PROBE.balanced_cycle(counter))
        for context, counter in transition_counter.items()
    }
    states = [left2, left1, current]
    while len(states) < synthetic_length:
        next_state = transition_rotors[(phase, left2, left1, current)].next()
        states.append(next_state)
        phase = next_phase(
            phase=phase,
            next_state=next_state,
            mod_cycle_length=mod_cycle_length,
            reset_mode=reset_mode,
        )
        left2, left1, current = left1, current, next_state
    return states


def cycle_sweep(
    segments: list[list[dict[str, str]]],
    synthetic_length: int,
    emission_counter: dict[str, Counter[tuple[str, int, int, str]]],
    real_window_concentrations: dict[str, float],
    real_family_distribution: dict[str, float],
    real_peak_distribution: dict[int, float],
    real_higher_divisor_share: float,
    window_length: int,
    sweep_min_cycle: int,
    sweep_max_cycle: int,
    model_kind: str,
    reset_mode: str,
) -> list[dict[str, float | int]]:
    """Sweep one family of cycle lengths and record its main scores."""
    rows: list[dict[str, float | int]] = []
    for cycle_length in range(sweep_min_cycle, sweep_max_cycle + 1):
        if model_kind == "mod_cycle":
            counter, start_context = SCHED_PROBE.build_mod_cycle_support(
                segments,
                mod_cycle_length=cycle_length,
            )
            states = SCHED_PROBE.simulate_mod_cycle(
                transition_counter=counter,
                start_context=start_context,
                synthetic_length=synthetic_length,
                mod_cycle_length=cycle_length,
            )
        elif model_kind == "hybrid":
            counter, start_context = build_hybrid_support(
                segments,
                mod_cycle_length=cycle_length,
                reset_mode=reset_mode,
            )
            states = simulate_hybrid(
                transition_counter=counter,
                start_context=start_context,
                synthetic_length=synthetic_length,
                mod_cycle_length=cycle_length,
                reset_mode=reset_mode,
            )
        else:
            raise ValueError(f"unsupported model_kind: {model_kind}")

        metrics = SCHED_PROBE.evaluate_state_sequence(
            states=states,
            emission_counter=emission_counter,
            real_window_concentrations=real_window_concentrations,
            real_family_distribution=real_family_distribution,
            real_peak_distribution=real_peak_distribution,
            real_higher_divisor_share=real_higher_divisor_share,
            window_length=window_length,
        )
        rows.append(
            {
                "cycle_length": cycle_length,
                "pooled_window_concentration_l1": metrics["pooled_window_concentration_l1"],
                "full_walk_three_step": metrics["full_walk_concentrations"]["three_step"],
            }
        )
    return rows


def record_reset_signature(
    record_csv: Path,
    record_workers: int,
) -> dict[str, object]:
    """Summarize whether records cluster near reset-trigger states."""
    record_rows = ENGINE_DECODE.load_record_rows(record_csv)
    gap_starts = [int(row["gap_start"]) for row in record_rows]
    _ = record_workers
    classified_rows = [ENGINE_DECODE.classify_record_gap(gap_start) for gap_start in gap_starts]

    classified_by_start = {
        int(row["gap_start"]): row
        for row in classified_rows
    }
    triad_set = set(GEN_PROBE.TRIAD_STATES)
    subset_rows = {
        "all_records": [],
        "maximal_records": [],
    }
    for record_row in record_rows:
        gap_start = int(record_row["gap_start"])
        classified_row = classified_by_start[gap_start]
        previous_state = str(classified_row["context_right_state"])
        previous_family = state_family(previous_state)
        current_state = str(classified_row["current_state"])
        current_family = str(classified_row["current_carrier_family"])
        payload = {
            "previous_higher_divisor": int("higher_divisor" in previous_family),
            "previous_nontriad": int(previous_state not in triad_set),
            "current_higher_divisor": int("higher_divisor" in current_family),
            "current_nontriad": int(current_state not in triad_set),
        }
        subset_rows["all_records"].append(payload)
        if int(record_row["is_maximal"]) == 1:
            subset_rows["maximal_records"].append(payload)

    summaries: dict[str, dict[str, float | int]] = {}
    for subset_name, rows in subset_rows.items():
        summaries[subset_name] = {
            "record_count": len(rows),
            "previous_higher_divisor_share": (
                sum(int(row["previous_higher_divisor"]) for row in rows) / len(rows)
            ),
            "previous_nontriad_share": (
                sum(int(row["previous_nontriad"]) for row in rows) / len(rows)
            ),
            "current_higher_divisor_share": (
                sum(int(row["current_higher_divisor"]) for row in rows) / len(rows)
            ),
            "current_nontriad_share": (
                sum(int(row["current_nontriad"]) for row in rows) / len(rows)
            ),
        }
    return summaries


def summarize(
    rows: list[dict[str, str]],
    train_surfaces: list[str],
    reference_surfaces: list[str],
    synthetic_length: int,
    window_length: int,
    mod_cycle_length: int,
    sweep_min_cycle: int,
    sweep_max_cycle: int,
    record_csv: Path | None,
    skip_record_analysis: bool,
    record_workers: int,
) -> dict[str, object]:
    """Build the hybrid scheduler summary."""
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

    third_order_counter, third_order_start = SCHED_PROBE.build_third_order_support(segments)
    mod_cycle_counter, mod_cycle_start = SCHED_PROBE.build_mod_cycle_support(
        segments,
        mod_cycle_length=mod_cycle_length,
    )
    hybrid_mod8_counter, hybrid_mod8_start = build_hybrid_support(
        segments,
        mod_cycle_length=mod_cycle_length,
        reset_mode="none",
    )
    hybrid_mod8_hdiv_counter, hybrid_mod8_hdiv_start = build_hybrid_support(
        segments,
        mod_cycle_length=mod_cycle_length,
        reset_mode="higher_divisor",
    )
    hybrid_mod8_nontriad_counter, hybrid_mod8_nontriad_start = build_hybrid_support(
        segments,
        mod_cycle_length=mod_cycle_length,
        reset_mode="nontriad",
    )

    model_rows = [
        {
            "model_id": "second_order_rotor",
            "description": "Baseline persistent 14-state second-order rotor.",
            "scheduler_phase_count": 0,
            "transition_context_count": len(support["second_order_counter"]),
            "states": SCHED_PROBE.simulate_second_order(support, synthetic_length),
        },
        {
            "model_id": "lag2_state_scheduler",
            "description": (
                "Finite scheduler whose phase is the reduced state two steps back; "
                "equivalently, a third-order walk on the persistent core."
            ),
            "scheduler_phase_count": len({context[0] for context in third_order_counter}),
            "transition_context_count": len(third_order_counter),
            "states": SCHED_PROBE.simulate_third_order(
                transition_counter=third_order_counter,
                start_context=third_order_start,
                synthetic_length=synthetic_length,
            ),
        },
        {
            "model_id": "mod_cycle_scheduler",
            "description": (
                f"Simple {mod_cycle_length}-phase modulo scheduler over the second-order core."
            ),
            "scheduler_phase_count": mod_cycle_length,
            "transition_context_count": len(mod_cycle_counter),
            "states": SCHED_PROBE.simulate_mod_cycle(
                transition_counter=mod_cycle_counter,
                start_context=mod_cycle_start,
                synthetic_length=synthetic_length,
                mod_cycle_length=mod_cycle_length,
            ),
        },
        {
            "model_id": "hybrid_lag2_mod8_scheduler",
            "description": (
                f"Hybrid lag-2 plus {mod_cycle_length}-phase modulo scheduler "
                "with no explicit reset trigger."
            ),
            "scheduler_phase_count": mod_cycle_length * len(core_states),
            "transition_context_count": len(hybrid_mod8_counter),
            "states": simulate_hybrid(
                transition_counter=hybrid_mod8_counter,
                start_context=hybrid_mod8_start,
                synthetic_length=synthetic_length,
                mod_cycle_length=mod_cycle_length,
                reset_mode="none",
            ),
        },
        {
            "model_id": "hybrid_lag2_mod8_reset_hdiv_scheduler",
            "description": (
                f"Hybrid lag-2 plus {mod_cycle_length}-phase modulo scheduler "
                "with phase reset when a higher-divisor state arrives."
            ),
            "scheduler_phase_count": mod_cycle_length * len(core_states),
            "transition_context_count": len(hybrid_mod8_hdiv_counter),
            "states": simulate_hybrid(
                transition_counter=hybrid_mod8_hdiv_counter,
                start_context=hybrid_mod8_hdiv_start,
                synthetic_length=synthetic_length,
                mod_cycle_length=mod_cycle_length,
                reset_mode="higher_divisor",
            ),
        },
        {
            "model_id": "hybrid_lag2_mod8_reset_nontriad_scheduler",
            "description": (
                f"Hybrid lag-2 plus {mod_cycle_length}-phase modulo scheduler "
                "with phase reset when the walk leaves the Semiprime Wheel Attractor."
            ),
            "scheduler_phase_count": mod_cycle_length * len(core_states),
            "transition_context_count": len(hybrid_mod8_nontriad_counter),
            "states": simulate_hybrid(
                transition_counter=hybrid_mod8_nontriad_counter,
                start_context=hybrid_mod8_nontriad_start,
                synthetic_length=synthetic_length,
                mod_cycle_length=mod_cycle_length,
                reset_mode="nontriad",
            ),
        },
    ]

    models: dict[str, object] = {}
    ranking_by_pooled: list[tuple[float, str]] = []
    ranking_by_full_three: list[tuple[float, str]] = []
    for row in model_rows:
        metrics = SCHED_PROBE.evaluate_state_sequence(
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
        ranking_by_pooled.append((metrics["pooled_window_concentration_l1"], row["model_id"]))
        ranking_by_full_three.append(
            (metrics["full_walk_concentrations"]["three_step"], row["model_id"])
        )

    cycle_sweeps = {
        "mod_cycle_scheduler": cycle_sweep(
            segments=segments,
            synthetic_length=synthetic_length,
            emission_counter=support["emission_counter"],
            real_window_concentrations=real_window_concentrations,
            real_family_distribution=real_family_distribution,
            real_peak_distribution=real_peak_distribution,
            real_higher_divisor_share=real_higher_divisor_share,
            window_length=window_length,
            sweep_min_cycle=sweep_min_cycle,
            sweep_max_cycle=sweep_max_cycle,
            model_kind="mod_cycle",
            reset_mode="none",
        ),
        "hybrid_reset_hdiv_scheduler": cycle_sweep(
            segments=segments,
            synthetic_length=synthetic_length,
            emission_counter=support["emission_counter"],
            real_window_concentrations=real_window_concentrations,
            real_family_distribution=real_family_distribution,
            real_peak_distribution=real_peak_distribution,
            real_higher_divisor_share=real_higher_divisor_share,
            window_length=window_length,
            sweep_min_cycle=sweep_min_cycle,
            sweep_max_cycle=sweep_max_cycle,
            model_kind="hybrid",
            reset_mode="higher_divisor",
        ),
    }

    summary: dict[str, object] = {
        "synthetic_length": synthetic_length,
        "reference_window_length": window_length,
        "real_reference_window_concentrations": real_window_concentrations,
        "real_reference_higher_divisor_share": real_higher_divisor_share,
        "core_state_count": len(core_states),
        "core_states": sorted(core_states),
        "models": models,
        "ranking_by_pooled_window_concentration_l1": [
            {
                "model_id": model_id,
                "pooled_window_concentration_l1": error_value,
            }
            for error_value, model_id in sorted(ranking_by_pooled)
        ],
        "ranking_by_full_walk_three_step": [
            {
                "model_id": model_id,
                "full_walk_three_step": share_value,
            }
            for share_value, model_id in sorted(ranking_by_full_three, reverse=True)
        ],
        "best_pooled_model_id": min(ranking_by_pooled)[1],
        "best_full_walk_three_step_model_id": max(ranking_by_full_three)[1],
        "cycle_sweeps": cycle_sweeps,
    }

    if not skip_record_analysis and record_csv is not None and record_csv.exists():
        summary["record_reset_signature"] = record_reset_signature(
            record_csv=record_csv,
            record_workers=record_workers,
        )

    return summary


def plot_summary(summary: dict[str, object], output_path: Path) -> None:
    """Render one compact hybrid-scheduler overview plot."""
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

    fig, axes = plt.subplots(2, 2, figsize=(16, 10), constrained_layout=True)

    pooled_ax = axes[0][0]
    width = 0.12
    centered_offsets = [
        (index - (len(model_ids) - 1) / 2.0) * width
        for index in range(len(model_ids))
    ]
    for offset, model_id in zip(centered_offsets, model_ids):
        pooled = summary["models"][model_id]["pooled_window_concentrations"]
        values = [pooled["one_step"], pooled["two_step"], pooled["three_step"]]
        pooled_ax.bar(
            [index + offset for index in x_positions],
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
    pooled_ax.legend(fontsize=7)

    full_ax = axes[0][1]
    for offset, model_id in zip(centered_offsets, model_ids):
        full_walk = summary["models"][model_id]["full_walk_concentrations"]
        values = [full_walk["one_step"], full_walk["two_step"], full_walk["three_step"]]
        full_ax.bar(
            [index + offset for index in x_positions],
            values,
            width=width,
            label=model_id,
            color=MODEL_COLORS[model_id],
        )
    full_ax.set_title("Full-Walk Concentrations")
    full_ax.set_xticks(list(x_positions), labels)
    full_ax.set_ylim(0.25, 0.9)
    full_ax.legend(fontsize=7)

    pooled_error_ax = axes[1][0]
    pooled_error_ax.bar(
        model_ids,
        [
            summary["models"][model_id]["pooled_window_concentration_l1"]
            for model_id in model_ids
        ],
        color=[MODEL_COLORS[model_id] for model_id in model_ids],
    )
    pooled_error_ax.set_title("Pooled Window Concentration L1")
    pooled_error_ax.tick_params(axis="x", labelrotation=20)

    sweep_ax = axes[1][1]
    for sweep_name, rows in summary["cycle_sweeps"].items():
        sweep_ax.plot(
            [row["cycle_length"] for row in rows],
            [row["pooled_window_concentration_l1"] for row in rows],
            marker="o",
            linewidth=2,
            label=sweep_name,
        )
    sweep_ax.set_title("Cycle Sweep on Pooled Window L1")
    sweep_ax.set_xlabel("Cycle length")
    sweep_ax.set_ylabel("L1 error")
    sweep_ax.legend(fontsize=8)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=220)
    plt.close(fig)


def main(argv: list[str] | None = None) -> int:
    """Run the hybrid scheduler probe and write its artifacts."""
    parser = build_parser()
    args = parser.parse_args(argv)

    start_time = time.perf_counter()
    rows = GEN_PROBE.load_rows(args.detail_csv)
    summary = summarize(
        rows=rows,
        train_surfaces=[
            SCHED_PROBE.power_surface_label(power)
            for power in range(args.train_min_power, args.train_max_power + 1)
        ],
        reference_surfaces=[
            SCHED_PROBE.power_surface_label(power)
            for power in range(args.reference_min_power, args.reference_max_power + 1)
        ],
        synthetic_length=args.synthetic_length,
        window_length=args.window_length,
        mod_cycle_length=args.mod_cycle_length,
        sweep_min_cycle=args.sweep_min_cycle,
        sweep_max_cycle=args.sweep_max_cycle,
        record_csv=args.record_csv,
        skip_record_analysis=args.skip_record_analysis,
        record_workers=args.record_workers,
    )
    summary["runtime_seconds"] = time.perf_counter() - start_time

    args.output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = args.output_dir / "gwr_dni_gap_type_hybrid_scheduler_probe_summary.json"
    plot_path = args.output_dir / "gwr_dni_gap_type_hybrid_scheduler_probe_overview.png"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    plot_summary(summary, plot_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
