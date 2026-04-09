#!/usr/bin/env python3
"""Render plots for the exact DNI recursive-walk decade sweep."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_INPUT_DIR = ROOT / "output"
DEFAULT_OUTPUT_DIR = ROOT / "output"
DETAIL_FILENAME = "gwr_dni_recursive_gap_scaling_sweep_details.csv"
SUMMARY_FILENAME = "gwr_dni_recursive_gap_scaling_sweep_summary.json"


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description="Render plots for the exact DNI recursive-walk decade sweep.",
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=DEFAULT_INPUT_DIR,
        help="Directory containing sweep CSV and JSON artifacts.",
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
                    "power": int(row["power"]),
                    "steps": int(row["steps"]),
                    "start_right_prime": int(row["start_right_prime"]),
                    "final_predicted_next_prime": int(row["final_predicted_next_prime"]),
                    "exact_hit_rate": float(row["exact_hit_rate"]),
                    "mean_skipped_gap_count": float(row["mean_skipped_gap_count"]),
                    "mean_predicted_peak_offset": float(row["mean_predicted_peak_offset"]),
                    "max_predicted_peak_offset": int(row["max_predicted_peak_offset"]),
                    "mean_cutoff_utilization": float(row["mean_cutoff_utilization"]),
                    "max_cutoff_utilization": float(row["max_cutoff_utilization"]),
                    "runtime_seconds": float(row["runtime_seconds"]),
                    "runtime_seconds_per_step": float(row["runtime_seconds_per_step"]),
                    "first_open_2_share": float(row["first_open_2_share"]),
                    "first_open_4_share": float(row["first_open_4_share"]),
                    "first_open_6_share": float(row["first_open_6_share"]),
                }
            )
    if not rows:
        raise ValueError("detail CSV must contain at least one row")
    return rows


def _read_summary(summary_path: Path) -> dict[str, object]:
    """Read the JSON summary."""
    return json.loads(summary_path.read_text(encoding="utf-8"))


def plot_performance(rows: list[dict[str, object]], summary: dict[str, object], output_path: Path) -> None:
    """Plot exactness and runtime by decade."""
    labels = [f"10^{row['power']}" for row in rows]
    hit_rates = [row["exact_hit_rate"] for row in rows]
    skipped = [row["mean_skipped_gap_count"] for row in rows]
    per_step = [row["runtime_seconds_per_step"] for row in rows]
    steps = [row["steps"] for row in rows]

    fig, axes = plt.subplots(2, 1, figsize=(11, 8.5), height_ratios=[1.0, 1.0])

    axes[0].plot(labels, hit_rates, marker="o", color="#2f7d32", linewidth=2.0, label="Exact hit rate")
    axes[0].plot(labels, skipped, marker="o", color="#b23a48", linewidth=2.0, label="Mean skipped gaps")
    axes[0].set_title("Exact DNI Recursive Walk by Start Decade")
    axes[0].set_ylabel("Rate / mean skipped gaps")
    axes[0].set_ylim(-0.05, 1.05)
    axes[0].grid(alpha=0.2)
    axes[0].legend(loc="lower left")

    summary_text = (
        f"powers = {summary['power_start']}..{summary['power_end']}\n"
        f"all exact hits = {summary['all_exact_hits']}\n"
        f"all zero skips = {summary['all_zero_skips']}\n"
        f"max start prime >= {summary['max_start_right_prime']}"
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

    bars = axes[1].bar(labels, per_step, color="#28536b", width=0.7)
    axes[1].set_title("Runtime Per Step by Start Decade")
    axes[1].set_ylabel("Seconds")
    axes[1].set_xlabel("Start regime")
    axes[1].grid(axis="y", alpha=0.2)
    for bar, step_budget in zip(bars, steps, strict=True):
        axes[1].text(
            bar.get_x() + bar.get_width() / 2.0,
            bar.get_height(),
            f"{step_budget}",
            ha="center",
            va="bottom",
            fontsize=8,
        )

    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


def plot_offsets(rows: list[dict[str, object]], summary: dict[str, object], output_path: Path) -> None:
    """Plot observed peak offsets and cutoff utilization by decade."""
    labels = [f"10^{row['power']}" for row in rows]
    mean_offsets = [row["mean_predicted_peak_offset"] for row in rows]
    max_offsets = [row["max_predicted_peak_offset"] for row in rows]
    mean_util = [row["mean_cutoff_utilization"] for row in rows]
    max_util = [row["max_cutoff_utilization"] for row in rows]
    first_open_2 = [row["first_open_2_share"] for row in rows]
    first_open_4 = [row["first_open_4_share"] for row in rows]
    first_open_6 = [row["first_open_6_share"] for row in rows]

    fig, axes = plt.subplots(2, 1, figsize=(11, 8.8), height_ratios=[1.1, 1.0])

    axes[0].plot(labels, mean_offsets, marker="o", color="#28536b", linewidth=2.0, label="Mean peak offset")
    axes[0].plot(labels, max_offsets, marker="o", color="#b23a48", linewidth=2.0, label="Max peak offset")
    axes[0].axhline(60, color="#6c757d", linestyle="--", linewidth=1.5, label="Universal tested cutoff 60")
    axes[0].set_title("Observed DNI Peak Offsets by Start Decade")
    axes[0].set_ylabel("Offset from current right prime")
    axes[0].grid(alpha=0.2)
    axes[0].legend(loc="upper left")

    axes[1].plot(labels, mean_util, marker="o", color="#2f7d32", linewidth=2.0, label="Mean cutoff utilization")
    axes[1].plot(labels, max_util, marker="o", color="#c77dff", linewidth=2.0, label="Max cutoff utilization")
    axes[1].bar(labels, first_open_2, color="#8ecae6", alpha=0.35, label="first_open = 2 share")
    axes[1].bar(labels, first_open_4, bottom=first_open_2, color="#ffb703", alpha=0.35, label="first_open = 4 share")
    stacked_46 = [a + b for a, b in zip(first_open_2, first_open_4, strict=True)]
    axes[1].bar(labels, first_open_6, bottom=stacked_46, color="#fb8500", alpha=0.35, label="first_open = 6 share")
    axes[1].set_title("Cutoff Utilization and First-Open Mix")
    axes[1].set_ylabel("Utilization / share")
    axes[1].set_xlabel("Start regime")
    axes[1].set_ylim(0.0, 1.05)
    axes[1].grid(alpha=0.2)
    axes[1].legend(loc="upper left", ncol=2, fontsize=8)

    summary_text = (
        f"max observed peak offset = {summary['max_observed_peak_offset']}\n"
        f"max cutoff utilization = {summary['max_observed_cutoff_utilization']:.4f}\n"
        f"max final prime >= {summary['max_final_predicted_next_prime']}"
    )
    axes[0].text(
        0.985,
        0.97,
        summary_text,
        transform=axes[0].transAxes,
        va="top",
        ha="right",
        fontsize=9,
        bbox={"facecolor": "white", "edgecolor": "#d8dee9", "boxstyle": "round,pad=0.3"},
    )

    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


def render_plots(input_dir: Path, output_dir: Path) -> dict[str, Path]:
    """Render both exact DNI scaling plots."""
    detail_path = input_dir / DETAIL_FILENAME
    summary_path = input_dir / SUMMARY_FILENAME
    if not detail_path.exists():
        raise FileNotFoundError(f"missing detail CSV: {detail_path}")
    if not summary_path.exists():
        raise FileNotFoundError(f"missing summary JSON: {summary_path}")

    output_dir.mkdir(parents=True, exist_ok=True)
    rows = _read_rows(detail_path)
    summary = _read_summary(summary_path)

    performance_path = output_dir / "gwr_dni_recursive_gap_scaling_performance.png"
    offsets_path = output_dir / "gwr_dni_recursive_gap_scaling_offsets.png"
    plot_performance(rows, summary, performance_path)
    plot_offsets(rows, summary, offsets_path)
    return {
        "performance": performance_path,
        "offsets": offsets_path,
    }


def main(argv: list[str] | None = None) -> int:
    """Render the exact DNI scaling plots."""
    args = build_parser().parse_args(argv)
    render_plots(args.input_dir, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
