#!/usr/bin/env python3
"""Probe deterministic long-horizon controllers for the gap-type engine."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import time
from collections import Counter
from functools import lru_cache
from pathlib import Path

import gmpy2


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT_DIR = ROOT / "output"
DEFAULT_DETAIL_CSV = ROOT / "output" / "gwr_dni_gap_type_catalog_details.csv"
DEFAULT_RECORD_CSV = ROOT / "data" / "external" / "primegap_list_records_1e12_1e18.csv"
DEFAULT_SYNTHETIC_LENGTH = 1_000_000
DEFAULT_WINDOW_LENGTH = 256
DEFAULT_MOD_CYCLE_LENGTH = 8
DEFAULT_EVENT_LOCK_MIN = 2
DEFAULT_EVENT_LOCK_MAX = 6
DEFAULT_DEBT_THRESHOLD_MIN = 5
DEFAULT_DEBT_THRESHOLD_MAX = 8
HYBRID_PROBE_PATH = Path(__file__).with_name("gwr_dni_gap_type_hybrid_scheduler_probe.py")
GAP_TYPE_PROBE_PATH = Path(__file__).with_name("gwr_dni_gap_type_probe.py")
MODEL_COLORS = {
    "hybrid_baseline": "#55a868",
    "event_lock": "#c44e52",
    "fatigue_debt": "#4c72b0",
}


def load_module(module_path: Path, module_name: str):
    """Load one sibling Python module from file."""
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


HYBRID_PROBE = load_module(HYBRID_PROBE_PATH, "gwr_dni_gap_type_hybrid_scheduler_probe_long_horizon")
GAP_TYPE_PROBE = load_module(GAP_TYPE_PROBE_PATH, "gwr_dni_gap_type_probe_long_horizon")
GEN_PROBE = HYBRID_PROBE.GEN_PROBE
SCHED_PROBE = HYBRID_PROBE.SCHED_PROBE
ENGINE_DECODE = HYBRID_PROBE.ENGINE_DECODE


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Probe deterministic long-horizon reset controllers layered on the "
            "best current hybrid gap-type engine."
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
        help="Record-gap extract used for the reset-window signature summary.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for JSON and PNG artifacts.",
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
        help="Cycle length for the hybrid base scheduler.",
    )
    parser.add_argument(
        "--event-lock-min",
        type=int,
        default=DEFAULT_EVENT_LOCK_MIN,
        help="Smallest event-lock horizon included in the sweep.",
    )
    parser.add_argument(
        "--event-lock-max",
        type=int,
        default=DEFAULT_EVENT_LOCK_MAX,
        help="Largest event-lock horizon included in the sweep.",
    )
    parser.add_argument(
        "--debt-threshold-min",
        type=int,
        default=DEFAULT_DEBT_THRESHOLD_MIN,
        help="Smallest fatigue threshold included in the sweep.",
    )
    parser.add_argument(
        "--debt-threshold-max",
        type=int,
        default=DEFAULT_DEBT_THRESHOLD_MAX,
        help="Largest fatigue threshold included in the sweep.",
    )
    return parser


def state_family(state: str) -> str:
    """Extract the carrier family from one reduced-state key."""
    return state.split("|", 1)[0].split("_", 1)[1]


def load_record_rows(record_csv: Path) -> list[dict[str, str]]:
    """Load the local record-gap extract."""
    if not record_csv.exists():
        raise FileNotFoundError(f"record CSV does not exist: {record_csv}")
    with record_csv.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError("record CSV must contain at least one row")
    return rows


def base_support(
    rows: list[dict[str, str]],
    mod_cycle_length: int,
) -> dict[str, object]:
    """Build the base hybrid support and the real comparison surface."""
    train_surfaces = [f"10^{power}" for power in range(7, 18)]
    reference_surfaces = [f"10^{power}" for power in range(12, 19)]
    rows_by_surface = GEN_PROBE.surface_rows(rows)
    core_states = GEN_PROBE.persistent_core_states(rows_by_surface, train_surfaces)
    segments = GEN_PROBE.contiguous_core_segments(rows_by_surface, train_surfaces, core_states)
    support = GEN_PROBE.build_training_support(segments)
    hybrid_counter, hybrid_start = HYBRID_PROBE.build_hybrid_support(
        segments,
        mod_cycle_length=mod_cycle_length,
        reset_mode="none",
    )

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
    top_successor = {
        context: max(counter.items(), key=lambda item: (item[1], item[0]))[0]
        for context, counter in hybrid_counter.items()
    }

    return {
        "support": support,
        "hybrid_counter": hybrid_counter,
        "hybrid_start": hybrid_start,
        "top_successor": top_successor,
        "real_family_distribution": real_family_distribution,
        "real_peak_distribution": real_peak_distribution,
        "real_higher_divisor_share": real_higher_divisor_share,
        "real_window_concentrations": real_window_concentrations,
    }


def evaluate_states(
    states: list[str],
    support: dict[str, object],
    window_length: int,
) -> dict[str, object]:
    """Score one visible state stream against the real comparison surface."""
    return SCHED_PROBE.evaluate_state_sequence(
        states=states,
        emission_counter=support["support"]["emission_counter"],
        real_window_concentrations=support["real_window_concentrations"],
        real_family_distribution=support["real_family_distribution"],
        real_peak_distribution=support["real_peak_distribution"],
        real_higher_divisor_share=support["real_higher_divisor_share"],
        window_length=window_length,
    )


def simulate_hybrid_baseline(
    support: dict[str, object],
    synthetic_length: int,
    mod_cycle_length: int,
) -> list[str]:
    """Emit the best current hybrid baseline with no explicit controller."""
    return HYBRID_PROBE.simulate_hybrid(
        transition_counter=support["hybrid_counter"],
        start_context=support["hybrid_start"],
        synthetic_length=synthetic_length,
        mod_cycle_length=mod_cycle_length,
        reset_mode="none",
    )


def simulate_event_lock(
    support: dict[str, object],
    synthetic_length: int,
    mod_cycle_length: int,
    lock_length: int,
) -> list[str]:
    """Emit the event-triggered top-successor lock controller."""
    phase, left2, left1, current = support["hybrid_start"]
    states = [left2, left1, current]
    lock_remaining = 0
    transition_rotors = {
        context: GEN_PROBE.Rotor(GEN_PROBE.balanced_cycle(counter))
        for context, counter in support["hybrid_counter"].items()
    }

    while len(states) < synthetic_length:
        context = (phase, left2, left1, current)
        if lock_remaining > 0:
            next_state = support["top_successor"][context]
        else:
            next_state = transition_rotors[context].next()
        states.append(next_state)
        if "higher_divisor" in state_family(next_state):
            lock_remaining = lock_length
        else:
            lock_remaining = max(0, lock_remaining - 1)
        phase = HYBRID_PROBE.next_phase(
            phase=phase,
            next_state=next_state,
            mod_cycle_length=mod_cycle_length,
            reset_mode="none",
        )
        left2, left1, current = left1, current, next_state
    return states


def simulate_fatigue_debt(
    support: dict[str, object],
    synthetic_length: int,
    mod_cycle_length: int,
    threshold: int,
) -> list[str]:
    """Emit the deterministic fatigue controller."""
    phase, left2, left1, current = support["hybrid_start"]
    states = [left2, left1, current]
    debt = 0
    transition_rotors = {
        context: GEN_PROBE.Rotor(GEN_PROBE.balanced_cycle(counter))
        for context, counter in support["hybrid_counter"].items()
    }

    while len(states) < synthetic_length:
        context = (phase, left2, left1, current)
        if debt >= threshold:
            next_state = support["top_successor"][context]
        else:
            next_state = transition_rotors[context].next()
        states.append(next_state)
        if "higher_divisor" in state_family(next_state):
            debt = 0
        else:
            debt = min(threshold + 2, debt + 1)
        phase = HYBRID_PROBE.next_phase(
            phase=phase,
            next_state=next_state,
            mod_cycle_length=mod_cycle_length,
            reset_mode="none",
        )
        left2, left1, current = left1, current, next_state
    return states


@lru_cache(maxsize=None)
def carrier_family_for_gap_start(gap_start: int) -> str:
    """Return the exact carrier family for one gap start."""
    row = GAP_TYPE_PROBE.gap_type_row(gap_start)
    return str(row["carrier_family"])


def recent_higher_divisor_signature(
    record_rows: list[dict[str, str]],
    history_depth: int,
) -> dict[str, dict[str, float | int]]:
    """Return the record-gap share with a higher-divisor event in the recent window."""
    summaries = {
        "all_records": {
            "record_count": 0,
            "recent_higher_divisor_hits": 0,
        },
        "maximal_records": {
            "record_count": 0,
            "recent_higher_divisor_hits": 0,
        },
    }

    for record_row in record_rows:
        current_start = int(record_row["gap_start"])
        probe_start = current_start
        hit = 0
        for _ in range(history_depth):
            probe_start = int(gmpy2.prev_prime(probe_start))
            if "higher_divisor" in carrier_family_for_gap_start(probe_start):
                hit = 1
                break
        summaries["all_records"]["record_count"] += 1
        summaries["all_records"]["recent_higher_divisor_hits"] += hit
        if int(record_row["is_maximal"]) == 1:
            summaries["maximal_records"]["record_count"] += 1
            summaries["maximal_records"]["recent_higher_divisor_hits"] += hit

    return {
        subset_name: {
            "record_count": payload["record_count"],
            "recent_higher_divisor_share": (
                payload["recent_higher_divisor_hits"] / payload["record_count"]
            ),
            "history_depth": history_depth,
        }
        for subset_name, payload in summaries.items()
    }


def summarize(
    rows: list[dict[str, str]],
    record_rows: list[dict[str, str]],
    synthetic_length: int,
    window_length: int,
    mod_cycle_length: int,
    event_lock_min: int,
    event_lock_max: int,
    debt_threshold_min: int,
    debt_threshold_max: int,
) -> dict[str, object]:
    """Build the long-horizon controller summary."""
    support = base_support(rows, mod_cycle_length=mod_cycle_length)

    baseline_states = simulate_hybrid_baseline(
        support=support,
        synthetic_length=synthetic_length,
        mod_cycle_length=mod_cycle_length,
    )
    baseline_metrics = evaluate_states(
        states=baseline_states,
        support=support,
        window_length=window_length,
    )

    event_lock_rows = []
    for lock_length in range(event_lock_min, event_lock_max + 1):
        states = simulate_event_lock(
            support=support,
            synthetic_length=synthetic_length,
            mod_cycle_length=mod_cycle_length,
            lock_length=lock_length,
        )
        metrics = evaluate_states(
            states=states,
            support=support,
            window_length=window_length,
        )
        event_lock_rows.append(
            {
                "lock_length": lock_length,
                **metrics,
            }
        )

    fatigue_rows = []
    for threshold in range(debt_threshold_min, debt_threshold_max + 1):
        states = simulate_fatigue_debt(
            support=support,
            synthetic_length=synthetic_length,
            mod_cycle_length=mod_cycle_length,
            threshold=threshold,
        )
        metrics = evaluate_states(
            states=states,
            support=support,
            window_length=window_length,
        )
        fatigue_rows.append(
            {
                "debt_threshold": threshold,
                **metrics,
            }
        )

    best_event_by_pooled = min(
        event_lock_rows,
        key=lambda row: (
            row["pooled_window_concentration_l1"],
            -row["full_walk_concentrations"]["three_step"],
            row["lock_length"],
        ),
    )
    best_event_by_full = max(
        event_lock_rows,
        key=lambda row: (
            row["full_walk_concentrations"]["three_step"],
            -row["pooled_window_concentration_l1"],
            -row["lock_length"],
        ),
    )
    best_fatigue_by_pooled = min(
        fatigue_rows,
        key=lambda row: (
            row["pooled_window_concentration_l1"],
            -row["full_walk_concentrations"]["three_step"],
            row["debt_threshold"],
        ),
    )
    best_fatigue_by_full = max(
        fatigue_rows,
        key=lambda row: (
            row["full_walk_concentrations"]["three_step"],
            -row["pooled_window_concentration_l1"],
            -row["debt_threshold"],
        ),
    )

    summary = {
        "synthetic_length": synthetic_length,
        "reference_window_length": window_length,
        "hybrid_baseline": baseline_metrics,
        "event_lock_sweep": event_lock_rows,
        "fatigue_debt_sweep": fatigue_rows,
        "best_event_lock_by_pooled": best_event_by_pooled,
        "best_event_lock_by_full_walk": best_event_by_full,
        "best_fatigue_by_pooled": best_fatigue_by_pooled,
        "best_fatigue_by_full_walk": best_fatigue_by_full,
        "recent_higher_divisor_signature": {
            "event_lock_best_pooled": recent_higher_divisor_signature(
                record_rows=record_rows,
                history_depth=int(best_event_by_pooled["lock_length"]),
            ),
            "event_lock_best_full_walk": recent_higher_divisor_signature(
                record_rows=record_rows,
                history_depth=int(best_event_by_full["lock_length"]),
            ),
        },
    }
    return summary


def plot_summary(summary: dict[str, object], output_path: Path) -> None:
    """Render one compact long-horizon controller overview plot."""
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 2, figsize=(16, 10), constrained_layout=True)

    pooled_ax = axes[0][0]
    pooled_ax.axhline(
        summary["hybrid_baseline"]["pooled_window_concentration_l1"],
        color=MODEL_COLORS["hybrid_baseline"],
        linewidth=2,
        label="hybrid baseline",
    )
    pooled_ax.plot(
        [row["lock_length"] for row in summary["event_lock_sweep"]],
        [row["pooled_window_concentration_l1"] for row in summary["event_lock_sweep"]],
        marker="o",
        linewidth=2,
        color=MODEL_COLORS["event_lock"],
        label="event lock",
    )
    pooled_ax.plot(
        [row["debt_threshold"] for row in summary["fatigue_debt_sweep"]],
        [row["pooled_window_concentration_l1"] for row in summary["fatigue_debt_sweep"]],
        marker="o",
        linewidth=2,
        color=MODEL_COLORS["fatigue_debt"],
        label="fatigue debt",
    )
    pooled_ax.axhline(0.015, color="#000000", linestyle="--", linewidth=1.5, label="target")
    pooled_ax.set_title("Pooled Window Concentration L1")
    pooled_ax.legend(fontsize=8)

    full_ax = axes[0][1]
    full_ax.axhline(
        summary["hybrid_baseline"]["full_walk_concentrations"]["three_step"],
        color=MODEL_COLORS["hybrid_baseline"],
        linewidth=2,
        label="hybrid baseline",
    )
    full_ax.plot(
        [row["lock_length"] for row in summary["event_lock_sweep"]],
        [row["full_walk_concentrations"]["three_step"] for row in summary["event_lock_sweep"]],
        marker="o",
        linewidth=2,
        color=MODEL_COLORS["event_lock"],
        label="event lock",
    )
    full_ax.plot(
        [row["debt_threshold"] for row in summary["fatigue_debt_sweep"]],
        [row["full_walk_concentrations"]["three_step"] for row in summary["fatigue_debt_sweep"]],
        marker="o",
        linewidth=2,
        color=MODEL_COLORS["fatigue_debt"],
        label="fatigue debt",
    )
    full_ax.axhline(0.62, color="#000000", linestyle="--", linewidth=1.5, label="target")
    full_ax.set_title("Full-Walk Three-Step Concentration")
    full_ax.legend(fontsize=8)

    frontier_ax = axes[1][0]
    frontier_ax.scatter(
        summary["hybrid_baseline"]["pooled_window_concentration_l1"],
        summary["hybrid_baseline"]["full_walk_concentrations"]["three_step"],
        color=MODEL_COLORS["hybrid_baseline"],
        s=80,
        label="hybrid baseline",
    )
    frontier_ax.scatter(
        [row["pooled_window_concentration_l1"] for row in summary["event_lock_sweep"]],
        [row["full_walk_concentrations"]["three_step"] for row in summary["event_lock_sweep"]],
        color=MODEL_COLORS["event_lock"],
        s=60,
        label="event lock",
    )
    frontier_ax.scatter(
        [row["pooled_window_concentration_l1"] for row in summary["fatigue_debt_sweep"]],
        [row["full_walk_concentrations"]["three_step"] for row in summary["fatigue_debt_sweep"]],
        color=MODEL_COLORS["fatigue_debt"],
        s=60,
        label="fatigue debt",
    )
    frontier_ax.axvline(0.015, color="#000000", linestyle="--", linewidth=1.5)
    frontier_ax.axhline(0.62, color="#000000", linestyle="--", linewidth=1.5)
    frontier_ax.set_xlabel("Pooled window L1")
    frontier_ax.set_ylabel("Full-walk three-step")
    frontier_ax.set_title("Tradeoff Frontier")
    frontier_ax.legend(fontsize=8)

    record_ax = axes[1][1]
    record_labels = ["all", "maximal"]
    pooled_signature = summary["recent_higher_divisor_signature"]["event_lock_best_pooled"]
    full_signature = summary["recent_higher_divisor_signature"]["event_lock_best_full_walk"]
    x_positions = [0, 1]
    width = 0.35
    record_ax.bar(
        [index - width / 2 for index in x_positions],
        [
            pooled_signature["all_records"]["recent_higher_divisor_share"],
            pooled_signature["maximal_records"]["recent_higher_divisor_share"],
        ],
        width=width,
        color=MODEL_COLORS["event_lock"],
        label=f"best pooled lock L={summary['best_event_lock_by_pooled']['lock_length']}",
    )
    record_ax.bar(
        [index + width / 2 for index in x_positions],
        [
            full_signature["all_records"]["recent_higher_divisor_share"],
            full_signature["maximal_records"]["recent_higher_divisor_share"],
        ],
        width=width,
        color=MODEL_COLORS["fatigue_debt"],
        label=f"best full lock L={summary['best_event_lock_by_full_walk']['lock_length']}",
    )
    record_ax.set_xticks(x_positions, record_labels)
    record_ax.set_title("Recent Higher-Divisor Signature")
    record_ax.legend(fontsize=8)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=220)
    plt.close(fig)


def main(argv: list[str] | None = None) -> int:
    """Run the long-horizon controller probe and write its artifacts."""
    parser = build_parser()
    args = parser.parse_args(argv)

    start_time = time.perf_counter()
    rows = GEN_PROBE.load_rows(args.detail_csv)
    record_rows = load_record_rows(args.record_csv)
    summary = summarize(
        rows=rows,
        record_rows=record_rows,
        synthetic_length=args.synthetic_length,
        window_length=args.window_length,
        mod_cycle_length=args.mod_cycle_length,
        event_lock_min=args.event_lock_min,
        event_lock_max=args.event_lock_max,
        debt_threshold_min=args.debt_threshold_min,
        debt_threshold_max=args.debt_threshold_max,
    )
    summary["runtime_seconds"] = time.perf_counter() - start_time

    args.output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = args.output_dir / "gwr_dni_gap_type_long_horizon_controller_probe_summary.json"
    plot_path = args.output_dir / "gwr_dni_gap_type_long_horizon_controller_probe_overview.png"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    plot_summary(summary, plot_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
