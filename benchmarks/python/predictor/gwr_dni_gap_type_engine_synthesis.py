#!/usr/bin/env python3
"""Assemble the frozen gap-type engine synthesis artifacts from probe summaries."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

from matplotlib import pyplot as plt
from matplotlib.patches import FancyBboxPatch


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT_DIR = ROOT / "output"
DEFAULT_GENERATIVE_SUMMARY = ROOT / "output" / "gwr_dni_gap_type_generative_probe_summary.json"
DEFAULT_DECODE_SUMMARY = ROOT / "output" / "gwr_dni_gap_type_engine_decode_summary.json"
DEFAULT_SCHEDULER_SUMMARY = ROOT / "output" / "gwr_dni_gap_type_scheduler_probe_summary.json"
DEFAULT_HYBRID_SUMMARY = ROOT / "output" / "gwr_dni_gap_type_hybrid_scheduler_probe_summary.json"
DEFAULT_LONG_HORIZON_SUMMARY = ROOT / "output" / "gwr_dni_gap_type_long_horizon_controller_probe_summary.json"
SUMMARY_FILENAME = "gwr_dni_gap_type_engine_v1_summary.json"
PLOT_FILENAME = "gwr_dni_gap_type_engine_v1_overview.png"
TRIAD_STATES = [
    "o2_odd_semiprime|d<=4",
    "o4_odd_semiprime|d<=4",
    "o6_odd_semiprime|d<=4",
]
MODEL_COLORS = {
    "real": "#222222",
    "second_order_rotor": "#dd8452",
    "lag2_state_scheduler": "#4c72b0",
    "hybrid_lag2_mod8_scheduler": "#55a868",
    "hybrid_lag2_mod8_reset_nontriad_scheduler": "#937860",
    "event_lock_l3": "#c44e52",
    "event_lock_l6": "#8172b2",
    "fatigue_t5": "#64b5cd",
}


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Freeze the current Prime Gap Generative Engine surface into a "
            "single summary JSON and overview figure."
        ),
    )
    parser.add_argument(
        "--generative-summary",
        type=Path,
        default=DEFAULT_GENERATIVE_SUMMARY,
        help="JSON summary emitted by gwr_dni_gap_type_generative_probe.py.",
    )
    parser.add_argument(
        "--decode-summary",
        type=Path,
        default=DEFAULT_DECODE_SUMMARY,
        help="JSON summary emitted by gwr_dni_gap_type_engine_decode.py.",
    )
    parser.add_argument(
        "--scheduler-summary",
        type=Path,
        default=DEFAULT_SCHEDULER_SUMMARY,
        help="JSON summary emitted by gwr_dni_gap_type_scheduler_probe.py.",
    )
    parser.add_argument(
        "--hybrid-summary",
        type=Path,
        default=DEFAULT_HYBRID_SUMMARY,
        help="JSON summary emitted by gwr_dni_gap_type_hybrid_scheduler_probe.py.",
    )
    parser.add_argument(
        "--long-horizon-summary",
        type=Path,
        default=DEFAULT_LONG_HORIZON_SUMMARY,
        help="JSON summary emitted by gwr_dni_gap_type_long_horizon_controller_probe.py.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for the synthesized JSON and PNG artifacts.",
    )
    return parser


def load_json(path: Path) -> dict[str, object]:
    """Load one JSON artifact."""
    if not path.exists():
        raise FileNotFoundError(f"summary JSON does not exist: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def state_family(state: str) -> str:
    """Extract the carrier family from one reduced-state key."""
    return state.split("|", 1)[0].split("_", 1)[1]


def rounded(value: float) -> float:
    """Round one float to four decimals for stable reporting."""
    return round(float(value), 4)


def build_summary(
    generative: dict[str, object],
    decode: dict[str, object],
    scheduler: dict[str, object],
    hybrid: dict[str, object],
    long_horizon: dict[str, object],
) -> dict[str, object]:
    """Assemble the frozen engine summary from existing probe artifacts."""
    core_states = list(scheduler["core_states"])
    family_counts = Counter(state_family(state) for state in core_states)
    generative_second_order = generative["model_comparisons"]["second_order_rotor"]
    scheduler_best_id = scheduler["best_model_id"]
    scheduler_best = scheduler["models"][scheduler_best_id]
    hybrid_best_local_id = hybrid["best_pooled_model_id"]
    hybrid_best_local = hybrid["models"][hybrid_best_local_id]
    hybrid_best_full_id = hybrid["best_full_walk_three_step_model_id"]
    hybrid_best_full = hybrid["models"][hybrid_best_full_id]
    local_controller = long_horizon["best_event_lock_by_pooled"]
    long_horizon_controller = long_horizon["best_event_lock_by_full_walk"]
    best_fatigue = long_horizon["best_fatigue_by_full_walk"]
    mod_cycle_best = min(
        hybrid["cycle_sweeps"]["mod_cycle_scheduler"],
        key=lambda row: (row["pooled_window_concentration_l1"], row["cycle_length"]),
    )
    reset_cycle_best = min(
        hybrid["cycle_sweeps"]["hybrid_reset_hdiv_scheduler"],
        key=lambda row: (row["pooled_window_concentration_l1"], row["cycle_length"]),
    )

    return {
        "engine_name": "Prime Gap Generative Engine",
        "version": "v1.0",
        "surface": "persistent 14-state reduced gap-type surface",
        "core_grammar": {
            "state_count": int(scheduler["core_state_count"]),
            "core_states": core_states,
            "family_state_counts": dict(sorted(family_counts.items())),
            "attractor_name": "Semiprime Wheel Attractor",
            "attractor_states": TRIAD_STATES,
        },
        "frozen_profiles": {
            "local_fidelity": {
                "model_id": hybrid_best_local_id,
                "description": hybrid_best_local["description"],
                "pooled_window_concentration_l1": rounded(
                    hybrid_best_local["pooled_window_concentration_l1"]
                ),
                "pooled_window_concentrations": {
                    step: rounded(value)
                    for step, value in hybrid_best_local["pooled_window_concentrations"].items()
                },
                "full_walk_three_step": rounded(
                    hybrid_best_local["full_walk_concentrations"]["three_step"]
                ),
            },
            "balanced_frontier": {
                "controller_family": "event_lock",
                "lock_length": int(local_controller["lock_length"]),
                "pooled_window_concentration_l1": rounded(
                    local_controller["pooled_window_concentration_l1"]
                ),
                "pooled_window_concentrations": {
                    step: rounded(value)
                    for step, value in local_controller["pooled_window_concentrations"].items()
                },
                "full_walk_three_step": rounded(
                    local_controller["full_walk_concentrations"]["three_step"]
                ),
            },
            "long_horizon_study": {
                "controller_family": "event_lock",
                "lock_length": int(long_horizon_controller["lock_length"]),
                "pooled_window_concentration_l1": rounded(
                    long_horizon_controller["pooled_window_concentration_l1"]
                ),
                "full_walk_three_step": rounded(
                    long_horizon_controller["full_walk_concentrations"]["three_step"]
                ),
            },
        },
        "milestones": {
            "held_out_second_order_rotor": {
                "surface": generative["held_out_surface"],
                "triad_share_error": rounded(generative_second_order["triad_share_error"]),
                "reduced_state_pair_l1": rounded(generative_second_order["reduced_state_pair_l1"]),
                "pair_top_successor_share_error": rounded(
                    generative_second_order["pair_top_successor_share_error"]
                ),
            },
            "best_scheduler": {
                "model_id": scheduler_best_id,
                "pooled_window_concentration_l1": rounded(
                    scheduler_best["pooled_window_concentration_l1"]
                ),
            },
            "hybrid_local_best": {
                "model_id": hybrid_best_local_id,
                "pooled_window_concentration_l1": rounded(
                    hybrid_best_local["pooled_window_concentration_l1"]
                ),
            },
            "hybrid_stationary_best": {
                "model_id": hybrid_best_full_id,
                "full_walk_three_step": rounded(
                    hybrid_best_full["full_walk_concentrations"]["three_step"]
                ),
            },
            "long_horizon_frontier": {
                "best_event_lock_by_pooled": {
                    "lock_length": int(local_controller["lock_length"]),
                    "pooled_window_concentration_l1": rounded(
                        local_controller["pooled_window_concentration_l1"]
                    ),
                    "full_walk_three_step": rounded(
                        local_controller["full_walk_concentrations"]["three_step"]
                    ),
                },
                "best_event_lock_by_full_walk": {
                    "lock_length": int(long_horizon_controller["lock_length"]),
                    "pooled_window_concentration_l1": rounded(
                        long_horizon_controller["pooled_window_concentration_l1"]
                    ),
                    "full_walk_three_step": rounded(
                        long_horizon_controller["full_walk_concentrations"]["three_step"]
                    ),
                },
                "best_fatigue_by_full_walk": {
                    "debt_threshold": int(best_fatigue["debt_threshold"]),
                    "pooled_window_concentration_l1": rounded(
                        best_fatigue["pooled_window_concentration_l1"]
                    ),
                    "full_walk_three_step": rounded(
                        best_fatigue["full_walk_concentrations"]["three_step"]
                    ),
                },
            },
        },
        "periodic_reset_signals": {
            "operating_hybrid_cycle_length": 8,
            "best_plain_cycle_length_by_pooled_window_l1": int(mod_cycle_best["cycle_length"]),
            "best_plain_cycle_pooled_window_l1": rounded(
                mod_cycle_best["pooled_window_concentration_l1"]
            ),
            "best_reset_higher_divisor_cycle_length_by_pooled_window_l1": int(
                reset_cycle_best["cycle_length"]
            ),
            "best_reset_higher_divisor_cycle_pooled_window_l1": rounded(
                reset_cycle_best["pooled_window_concentration_l1"]
            ),
        },
        "record_reset_signature": {
            "event_lock_l3": {
                "all_records_recent_higher_divisor_share": rounded(
                    long_horizon["recent_higher_divisor_signature"]["event_lock_best_pooled"][
                        "all_records"
                    ]["recent_higher_divisor_share"]
                ),
                "maximal_records_recent_higher_divisor_share": rounded(
                    long_horizon["recent_higher_divisor_signature"]["event_lock_best_pooled"][
                        "maximal_records"
                    ]["recent_higher_divisor_share"]
                ),
            },
            "event_lock_l6": {
                "all_records_recent_higher_divisor_share": rounded(
                    long_horizon["recent_higher_divisor_signature"]["event_lock_best_full_walk"][
                        "all_records"
                    ]["recent_higher_divisor_share"]
                ),
                "maximal_records_recent_higher_divisor_share": rounded(
                    long_horizon["recent_higher_divisor_signature"]["event_lock_best_full_walk"][
                        "maximal_records"
                    ]["recent_higher_divisor_share"]
                ),
            },
        },
        "rulebook_anchor": {
            "rule_count": len(decode["rulebook"]),
            "first_rule": decode["rulebook"][0],
        },
        "current_claim": (
            "The gap-type stream on the persistent reduced surface is generated "
            "by a hierarchical finite-state engine with a 14-state core "
            "grammar, a scheduler layer, and a higher-divisor-triggered "
            "long-horizon controller frontier."
        ),
        "current_boundary": (
            "No single deterministic controller on the present surface "
            "simultaneously reaches pooled-window concentration L1 below 0.015 "
            "and full-walk three-step concentration above 0.62."
        ),
    }


def add_box(ax, xy, width, height, label, facecolor):
    """Draw one rounded annotation box."""
    patch = FancyBboxPatch(
        xy,
        width,
        height,
        boxstyle="round,pad=0.02,rounding_size=0.03",
        linewidth=1.2,
        edgecolor="#333333",
        facecolor=facecolor,
    )
    ax.add_patch(patch)
    ax.text(
        xy[0] + width / 2,
        xy[1] + height / 2,
        label,
        ha="center",
        va="center",
        fontsize=10,
    )


def plot_core_inventory(ax, summary: dict[str, object]):
    """Render the 14-state core inventory and attractor annotation."""
    family_counts = summary["core_grammar"]["family_state_counts"]
    labels = list(family_counts.keys())
    values = [family_counts[label] for label in labels]
    colors = ["#c44e52" if label == "odd_semiprime" else "#8da0cb" for label in labels]
    ax.bar(labels, values, color=colors, edgecolor="#333333")
    ax.set_title("A. 14-State Core Grammar")
    ax.set_ylabel("Core states")
    ax.set_ylim(0, max(values) + 3)
    ax.tick_params(axis="x", rotation=20)
    for index, value in enumerate(values):
        ax.text(index, value + 0.15, str(value), ha="center", va="bottom", fontsize=9)
    triad_text = "Semiprime Wheel Attractor\n" + "\n".join(summary["core_grammar"]["attractor_states"])
    ax.text(
        0.98,
        0.96,
        triad_text,
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=9,
        bbox={"boxstyle": "round,pad=0.3", "facecolor": "#fff7f3", "edgecolor": "#c44e52"},
    )


def plot_architecture(ax, summary: dict[str, object]):
    """Render the layered engine diagram."""
    ax.set_title("B. Frozen Engine v1.0")
    ax.set_axis_off()
    add_box(ax, (0.06, 0.62), 0.24, 0.2, "14-state\ncore grammar", "#f7f7f7")
    add_box(ax, (0.38, 0.62), 0.24, 0.2, "lag2 scheduler\n+ periodic phase", "#eef3fb")
    add_box(ax, (0.70, 0.62), 0.24, 0.2, "higher-divisor\nreset controller", "#fff3ee")
    add_box(ax, (0.38, 0.20), 0.24, 0.18, "gap-type stream", "#f2f8ec")
    ax.annotate("", xy=(0.38, 0.72), xytext=(0.30, 0.72), arrowprops={"arrowstyle": "->", "lw": 1.5})
    ax.annotate("", xy=(0.70, 0.72), xytext=(0.62, 0.72), arrowprops={"arrowstyle": "->", "lw": 1.5})
    ax.annotate("", xy=(0.50, 0.38), xytext=(0.50, 0.62), arrowprops={"arrowstyle": "->", "lw": 1.5})
    local_profile = summary["frozen_profiles"]["local_fidelity"]
    balanced = summary["frozen_profiles"]["balanced_frontier"]
    long_profile = summary["frozen_profiles"]["long_horizon_study"]
    notes = [
        f"local: nontriad-reset hybrid | L1 {local_profile['pooled_window_concentration_l1']:.4f}",
        f"balanced: event-lock L={balanced['lock_length']} | 3-step {balanced['full_walk_three_step']:.4f}",
        f"long horizon: event-lock L={long_profile['lock_length']} | 3-step {long_profile['full_walk_three_step']:.4f}",
    ]
    ax.text(
        0.02,
        0.02,
        "\n".join(notes),
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=9,
        bbox={"boxstyle": "round,pad=0.3", "facecolor": "#fafafa", "edgecolor": "#bbbbbb"},
    )


def plot_grouped_bars(ax, title, real, models, colors):
    """Render one grouped concentration comparison chart."""
    steps = ["one_step", "two_step", "three_step"]
    step_labels = ["1-step", "2-step", "3-step"]
    width = 0.18
    x_positions = list(range(len(steps)))
    offsets = [index - (len(models)) / 2 for index in range(len(models) + 1)]

    ax.bar(
        [x + offsets[0] * width for x in x_positions],
        [real[step] for step in steps],
        width,
        label="real",
        color=colors["real"],
    )
    for model_index, (label, values) in enumerate(models.items(), start=1):
        ax.bar(
            [x + offsets[model_index] * width for x in x_positions],
            [values[step] for step in steps],
            width,
            label=label,
            color=colors[label],
        )
    ax.set_xticks(x_positions, step_labels)
    ax.set_ylim(0.0, 0.85)
    ax.set_title(title)
    ax.set_ylabel("Concentration")
    ax.legend(fontsize=8, frameon=False, ncol=2, loc="upper left")


def plot_frontier(ax, scheduler, hybrid, long_horizon):
    """Render the pooled-vs-stationary tradeoff frontier."""
    ax.set_title("E. Local vs Long-Horizon Frontier")
    points = [
        (
            "second_order_rotor",
            scheduler["models"]["second_order_rotor"]["pooled_window_concentration_l1"],
            scheduler["models"]["second_order_rotor"]["full_walk_concentrations"]["three_step"],
            "2nd order",
        ),
        (
            "lag2_state_scheduler",
            scheduler["models"]["lag2_state_scheduler"]["pooled_window_concentration_l1"],
            scheduler["models"]["lag2_state_scheduler"]["full_walk_concentrations"]["three_step"],
            "lag2",
        ),
        (
            "hybrid_lag2_mod8_scheduler",
            long_horizon["hybrid_baseline"]["pooled_window_concentration_l1"],
            long_horizon["hybrid_baseline"]["full_walk_concentrations"]["three_step"],
            "hybrid",
        ),
        (
            "hybrid_lag2_mod8_reset_nontriad_scheduler",
            hybrid["models"]["hybrid_lag2_mod8_reset_nontriad_scheduler"]["pooled_window_concentration_l1"],
            hybrid["models"]["hybrid_lag2_mod8_reset_nontriad_scheduler"]["full_walk_concentrations"][
                "three_step"
            ],
            "hybrid+nontriad",
        ),
        (
            "event_lock_l3",
            long_horizon["best_event_lock_by_pooled"]["pooled_window_concentration_l1"],
            long_horizon["best_event_lock_by_pooled"]["full_walk_concentrations"]["three_step"],
            "event L3",
        ),
        (
            "event_lock_l6",
            long_horizon["best_event_lock_by_full_walk"]["pooled_window_concentration_l1"],
            long_horizon["best_event_lock_by_full_walk"]["full_walk_concentrations"]["three_step"],
            "event L6",
        ),
        (
            "fatigue_t5",
            long_horizon["best_fatigue_by_full_walk"]["pooled_window_concentration_l1"],
            long_horizon["best_fatigue_by_full_walk"]["full_walk_concentrations"]["three_step"],
            "fatigue T5",
        ),
    ]
    label_offsets = {
        "2nd order": (0.003, -0.012),
        "lag2": (0.003, 0.006),
        "hybrid": (0.003, 0.002),
        "hybrid+nontriad": (0.003, -0.008),
        "event L3": (0.003, 0.006),
        "event L6": (0.003, 0.006),
        "fatigue T5": (0.003, 0.006),
    }
    for model_id, pooled_l1, full_three_step, label in points:
        ax.scatter(
            pooled_l1,
            full_three_step,
            s=80,
            color=MODEL_COLORS[model_id],
            edgecolor="#333333",
        )
        x_offset, y_offset = label_offsets[label]
        ax.text(pooled_l1 + x_offset, full_three_step + y_offset, label, fontsize=8)
    ax.axvline(0.015, color="#999999", linestyle="--", linewidth=1.0)
    ax.axhline(0.62, color="#999999", linestyle="--", linewidth=1.0)
    ax.set_xlabel("Pooled-window concentration L1")
    ax.set_ylabel("Full-walk 3-step concentration")
    ax.set_xlim(0.0, 0.16)
    ax.set_ylim(0.30, 0.72)


def plot_periodic_sweeps(ax, hybrid):
    """Render the cycle-length sweep evidence."""
    ax.set_title("F. Periodic Reset Signals")
    mod_rows = hybrid["cycle_sweeps"]["mod_cycle_scheduler"]
    hdiv_rows = hybrid["cycle_sweeps"]["hybrid_reset_hdiv_scheduler"]
    mod_x = [row["cycle_length"] for row in mod_rows]
    mod_y = [row["pooled_window_concentration_l1"] for row in mod_rows]
    hdiv_x = [row["cycle_length"] for row in hdiv_rows]
    hdiv_y = [row["pooled_window_concentration_l1"] for row in hdiv_rows]
    ax.plot(mod_x, mod_y, marker="o", color="#8172b2", label="plain modulo")
    ax.plot(hdiv_x, hdiv_y, marker="o", color="#c44e52", label="reset on h-div")
    best_mod = min(mod_rows, key=lambda row: (row["pooled_window_concentration_l1"], row["cycle_length"]))
    best_hdiv = min(hdiv_rows, key=lambda row: (row["pooled_window_concentration_l1"], row["cycle_length"]))
    ax.scatter(best_mod["cycle_length"], best_mod["pooled_window_concentration_l1"], s=90, color="#8172b2")
    ax.scatter(best_hdiv["cycle_length"], best_hdiv["pooled_window_concentration_l1"], s=90, color="#c44e52")
    ax.text(best_mod["cycle_length"] + 0.2, best_mod["pooled_window_concentration_l1"] + 0.001, "best plain = 11", fontsize=8)
    ax.text(best_hdiv["cycle_length"] + 0.2, best_hdiv["pooled_window_concentration_l1"] + 0.001, "best reset = 2", fontsize=8)
    ax.set_xlabel("Cycle length")
    ax.set_ylabel("Pooled-window concentration L1")
    ax.legend(frameon=False, fontsize=8)


def plot_summary(
    summary: dict[str, object],
    scheduler: dict[str, object],
    hybrid: dict[str, object],
    long_horizon: dict[str, object],
    output_path: Path,
) -> None:
    """Render the definitive multi-panel synthesis figure."""
    figure = plt.figure(figsize=(18, 11))
    grid = figure.add_gridspec(2, 3, hspace=0.32, wspace=0.28)

    axis_a = figure.add_subplot(grid[0, 0])
    axis_b = figure.add_subplot(grid[0, 1])
    axis_c = figure.add_subplot(grid[0, 2])
    axis_d = figure.add_subplot(grid[1, 0])
    axis_e = figure.add_subplot(grid[1, 1])
    axis_f = figure.add_subplot(grid[1, 2])

    plot_core_inventory(axis_a, summary)
    plot_architecture(axis_b, summary)
    plot_grouped_bars(
        axis_c,
        "C. Pooled 256-Window Concentration",
        scheduler["real_reference_window_concentrations"],
        {
            "lag2_state_scheduler": scheduler["models"]["lag2_state_scheduler"][
                "pooled_window_concentrations"
            ],
            "hybrid_lag2_mod8_reset_nontriad_scheduler": hybrid["models"][
                "hybrid_lag2_mod8_reset_nontriad_scheduler"
            ]["pooled_window_concentrations"],
            "event_lock_l3": long_horizon["best_event_lock_by_pooled"][
                "pooled_window_concentrations"
            ],
        },
        MODEL_COLORS,
    )
    plot_grouped_bars(
        axis_d,
        "D. Stationary Walk Concentration",
        scheduler["real_reference_window_concentrations"],
        {
            "second_order_rotor": scheduler["models"]["second_order_rotor"][
                "full_walk_concentrations"
            ],
            "hybrid_lag2_mod8_scheduler": long_horizon["hybrid_baseline"][
                "full_walk_concentrations"
            ],
            "event_lock_l3": long_horizon["best_event_lock_by_pooled"][
                "full_walk_concentrations"
            ],
            "event_lock_l6": long_horizon["best_event_lock_by_full_walk"][
                "full_walk_concentrations"
            ],
        },
        MODEL_COLORS,
    )
    plot_frontier(axis_e, scheduler, hybrid, long_horizon)
    plot_periodic_sweeps(axis_f, hybrid)

    figure.suptitle(
        "Prime Gap Generative Engine v1.0",
        fontsize=16,
        y=0.98,
    )
    figure.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(figure)


def main(argv: list[str] | None = None) -> int:
    """Run the synthesis entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)

    generative = load_json(args.generative_summary)
    decode = load_json(args.decode_summary)
    scheduler = load_json(args.scheduler_summary)
    hybrid = load_json(args.hybrid_summary)
    long_horizon = load_json(args.long_horizon_summary)

    summary = build_summary(
        generative=generative,
        decode=decode,
        scheduler=scheduler,
        hybrid=hybrid,
        long_horizon=long_horizon,
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = args.output_dir / SUMMARY_FILENAME
    plot_path = args.output_dir / PLOT_FILENAME
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    plot_summary(
        summary=summary,
        scheduler=scheduler,
        hybrid=hybrid,
        long_horizon=long_horizon,
        output_path=plot_path,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
