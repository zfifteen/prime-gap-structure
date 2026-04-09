#!/usr/bin/env python3
"""Render meaningful plots for one recursive GWR gap-walk run."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_INPUT_DIR = ROOT / "output"
DEFAULT_OUTPUT_DIR = ROOT / "output"
DETAIL_FILENAME = "gwr_recursive_gap_walk_details.csv"
SUMMARY_FILENAME = "gwr_recursive_gap_walk_summary.json"


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description="Render number-line and dashboard plots for one recursive GWR gap walk.",
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=DEFAULT_INPUT_DIR,
        help="Directory containing recursive gap-walk CSV and JSON artifacts.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory to receive PNG plots.",
    )
    return parser


def _read_rows(detail_path: Path) -> list[dict[str, object]]:
    """Read the detail CSV into typed rows."""
    with detail_path.open(encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = []
        for row in reader:
            rows.append(
                {
                    "step": int(row["step"]),
                    "current_gap_index": int(row["current_gap_index"]),
                    "next_gap_index": int(row["next_gap_index"]),
                    "exact_immediate_hit": row["exact_immediate_hit"] == "True",
                    "skipped_gap_count": int(row["skipped_gap_count"]),
                    "current_right_prime": int(row["current_right_prime"]),
                    "next_right_prime": int(row["next_right_prime"]),
                    "next_gap_width": int(row["next_gap_width"]),
                    "next_gap_has_d4": row["next_gap_has_d4"] == "True",
                    "next_d4_corridor_width": (
                        int(row["next_d4_corridor_width"])
                        if row["next_d4_corridor_width"]
                        else None
                    ),
                    "next_d4_corridor_start_offset_from_current_right": (
                        int(row["next_d4_corridor_start_offset_from_current_right"])
                        if row["next_d4_corridor_start_offset_from_current_right"]
                        else None
                    ),
                    "next_d4_corridor_end_offset_from_current_right": (
                        int(row["next_d4_corridor_end_offset_from_current_right"])
                        if row["next_d4_corridor_end_offset_from_current_right"]
                        else None
                    ),
                }
            )
    if not rows:
        raise ValueError("detail CSV must contain at least one row")
    return rows


def _read_summary(summary_path: Path) -> dict[str, object]:
    """Read the JSON summary."""
    return json.loads(summary_path.read_text(encoding="utf-8"))


def plot_numberline(rows: list[dict[str, object]], output_path: Path) -> None:
    """Plot each recursive step as a number line from the current right prime."""
    figure_height = max(4.5, 0.24 * len(rows) + 1.5)
    fig, ax = plt.subplots(figsize=(11, figure_height))

    for row in rows:
        step = int(row["step"])
        gap_end = int(row["next_gap_width"])
        corridor_start = row["next_d4_corridor_start_offset_from_current_right"]
        corridor_end = row["next_d4_corridor_end_offset_from_current_right"]

        ax.hlines(step, 0, gap_end, color="#4c566a", linewidth=2.0, zorder=1)
        ax.scatter([0, gap_end], [step, step], color="#4c566a", s=14, zorder=2)

        if corridor_start is not None and corridor_end is not None:
            ax.hlines(step, corridor_start, corridor_end, color="#2f7d32", linewidth=5.5, zorder=3)
            ax.scatter(
                [corridor_start, corridor_end],
                [step, step],
                color="#2f7d32",
                s=18,
                zorder=4,
            )

    ax.axvline(0, color="#b23a48", linewidth=1.2, linestyle="--")
    ax.set_title("Recursive GWR Step Map")
    ax.set_xlabel("Offset from current right prime")
    ax.set_ylabel("Step")
    ax.set_yticks([row["step"] for row in rows])
    ax.invert_yaxis()
    ax.grid(axis="x", alpha=0.2)

    legend_handles = [
        Line2D([0], [0], color="#b23a48", linestyle="--", label="Current right prime"),
        Line2D([0], [0], color="#4c566a", linewidth=2.0, label="Next gap span"),
        Line2D([0], [0], color="#2f7d32", linewidth=5.5, label="Next d=4 corridor"),
    ]
    ax.legend(handles=legend_handles, loc="upper right")
    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


def plot_dashboard(
    rows: list[dict[str, object]],
    summary: dict[str, object],
    output_path: Path,
) -> None:
    """Plot width traces and offset distributions for one recursive walk."""
    steps = [int(row["step"]) for row in rows]
    gap_widths = [int(row["next_gap_width"]) for row in rows]
    corridor_widths = [
        row["next_d4_corridor_width"] if row["next_d4_corridor_width"] is not None else float("nan")
        for row in rows
    ]
    start_offsets = [
        int(row["next_d4_corridor_start_offset_from_current_right"])
        for row in rows
        if row["next_d4_corridor_start_offset_from_current_right"] is not None
    ]
    end_offsets = [
        int(row["next_d4_corridor_end_offset_from_current_right"])
        for row in rows
        if row["next_d4_corridor_end_offset_from_current_right"] is not None
    ]

    fig, axes = plt.subplots(2, 1, figsize=(11, 8), height_ratios=[1.2, 1.0])

    axes[0].plot(steps, gap_widths, color="#28536b", linewidth=2.0, label="Next gap width")
    axes[0].plot(
        steps,
        corridor_widths,
        color="#2f7d32",
        linewidth=2.0,
        label="Next d=4 corridor width",
    )
    axes[0].set_title("Gap Width and Corridor Width by Step")
    axes[0].set_xlabel("Step")
    axes[0].set_ylabel("Integers")
    axes[0].grid(alpha=0.2)
    axes[0].legend(loc="upper right")

    summary_text = (
        f"steps = {summary['steps']}\n"
        f"next-gap d=4 rate = {summary['next_gap_has_d4_rate']:.4f}\n"
        f"mean next gap width = {summary['mean_next_gap_width']:.2f}\n"
        f"mean corridor start offset = {summary['mean_next_d4_corridor_start_offset']:.2f}\n"
        f"mean corridor end offset = {summary['mean_next_d4_corridor_end_offset']:.2f}"
    )
    axes[0].text(
        0.015,
        0.97,
        summary_text,
        transform=axes[0].transAxes,
        va="top",
        ha="left",
        fontsize=9,
        bbox={"facecolor": "white", "edgecolor": "#d8dee9", "boxstyle": "round,pad=0.3"},
    )

    bins = min(16, max(6, len(start_offsets) // 6)) if start_offsets else 6
    axes[1].hist(start_offsets, bins=bins, color="#b23a48", alpha=0.75, label="Corridor start offset")
    axes[1].hist(end_offsets, bins=bins, color="#d9923b", alpha=0.65, label="Corridor end offset")
    axes[1].axvline(0, color="#4c566a", linestyle="--", linewidth=1.0)
    axes[1].set_title("Offset Distribution from the Current Right Prime")
    axes[1].set_xlabel("Offset")
    axes[1].set_ylabel("Count")
    axes[1].grid(alpha=0.2)
    axes[1].legend(loc="upper right")

    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


def plot_jump_behavior(
    rows: list[dict[str, object]],
    summary: dict[str, object],
    output_path: Path,
) -> None:
    """Plot predicted next-gap jumps against the exact adjacent next gap."""
    steps = [int(row["step"]) for row in rows]
    current_gap_indices = [int(row["current_gap_index"]) for row in rows]
    exact_next_gap_indices = [index + 1 for index in current_gap_indices]
    predicted_next_gap_indices = [int(row["next_gap_index"]) for row in rows]
    skipped_gap_counts = [int(row["skipped_gap_count"]) for row in rows]
    hit_colors = [
        "#2f7d32" if row["exact_immediate_hit"] else "#b23a48"
        for row in rows
    ]

    fig, axes = plt.subplots(2, 1, figsize=(11, 8.5), height_ratios=[1.4, 0.9])

    axes[0].plot(steps, current_gap_indices, color="#4c566a", linewidth=1.6, label="Current gap index")
    axes[0].plot(
        steps,
        exact_next_gap_indices,
        color="#28536b",
        linewidth=2.0,
        linestyle="--",
        label="Exact adjacent next gap index",
    )
    axes[0].scatter(
        steps,
        predicted_next_gap_indices,
        c=hit_colors,
        s=42,
        zorder=3,
        label="Predicted next gap index",
    )
    for step, exact_index, predicted_index, color in zip(
        steps,
        exact_next_gap_indices,
        predicted_next_gap_indices,
        hit_colors,
    ):
        axes[0].vlines(
            step,
            exact_index,
            predicted_index,
            color=color,
            linewidth=1.6,
            alpha=0.8,
            zorder=2,
        )

    axes[0].set_title("Forward GWR Jump Behavior")
    axes[0].set_xlabel("Step")
    axes[0].set_ylabel("Gap index")
    axes[0].grid(alpha=0.2)

    summary_text = (
        f"steps = {summary['steps']}\n"
        f"immediate-hit rate = {summary['exact_immediate_hit_rate']:.4f}\n"
        f"mean skipped gaps = {summary['mean_skipped_gap_count']:.2f}\n"
        f"max skipped gaps = {summary['max_skipped_gap_count']}"
    )
    axes[0].text(
        0.015,
        0.97,
        summary_text,
        transform=axes[0].transAxes,
        va="top",
        ha="left",
        fontsize=9,
        bbox={"facecolor": "white", "edgecolor": "#d8dee9", "boxstyle": "round,pad=0.3"},
    )

    legend_handles = [
        Line2D([0], [0], color="#4c566a", linewidth=1.6, label="Current gap index"),
        Line2D([0], [0], color="#28536b", linewidth=2.0, linestyle="--", label="Exact adjacent next gap"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#2f7d32", markersize=7, label="Immediate hit"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#b23a48", markersize=7, label="Jumped ahead"),
    ]
    axes[0].legend(handles=legend_handles, loc="upper right")

    axes[1].bar(steps, skipped_gap_counts, color=hit_colors, width=0.8)
    axes[1].set_title("Skipped-gap count by step")
    axes[1].set_xlabel("Step")
    axes[1].set_ylabel("Skipped gaps")
    axes[1].grid(axis="y", alpha=0.2)

    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


def render_plots(input_dir: Path, output_dir: Path) -> dict[str, Path]:
    """Render all recursive-walk plots from one artifact directory."""
    detail_path = input_dir / DETAIL_FILENAME
    summary_path = input_dir / SUMMARY_FILENAME
    if not detail_path.exists():
        raise FileNotFoundError(f"missing detail CSV: {detail_path}")
    if not summary_path.exists():
        raise FileNotFoundError(f"missing summary JSON: {summary_path}")

    output_dir.mkdir(parents=True, exist_ok=True)
    rows = _read_rows(detail_path)
    summary = _read_summary(summary_path)

    numberline_path = output_dir / "gwr_recursive_gap_walk_numberline.png"
    dashboard_path = output_dir / "gwr_recursive_gap_walk_dashboard.png"
    jump_path = output_dir / "gwr_recursive_gap_walk_jump_behavior.png"
    plot_numberline(rows, numberline_path)
    plot_dashboard(rows, summary, dashboard_path)
    plot_jump_behavior(rows, summary, jump_path)
    return {"numberline": numberline_path, "dashboard": dashboard_path, "jump_behavior": jump_path}


def main(argv: list[str] | None = None) -> int:
    """Render plot artifacts from one recursive gap-walk run."""
    args = build_parser().parse_args(argv)
    render_plots(args.input_dir, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
