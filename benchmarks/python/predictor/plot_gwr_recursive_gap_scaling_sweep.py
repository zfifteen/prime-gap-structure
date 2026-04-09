#!/usr/bin/env python3
"""Render plots for the forward recursive GWR decade-scaling sweep."""

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
DETAIL_FILENAME = "gwr_recursive_gap_scaling_sweep_details.csv"
SUMMARY_FILENAME = "gwr_recursive_gap_scaling_sweep_summary.json"


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description="Render plots for the recursive GWR decade-scaling sweep.",
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=DEFAULT_INPUT_DIR,
        help="Directory containing scaling sweep CSV and JSON artifacts.",
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
                    "exact_immediate_hit_rate": float(row["exact_immediate_hit_rate"]),
                    "mean_skipped_gap_count": float(row["mean_skipped_gap_count"]),
                    "runtime_seconds": float(row["runtime_seconds"]),
                }
            )
    if not rows:
        raise ValueError("detail CSV must contain at least one row")
    return rows


def _read_summary(summary_path: Path) -> dict[str, object]:
    """Read the JSON summary."""
    return json.loads(summary_path.read_text(encoding="utf-8"))


def plot_scaling(rows: list[dict[str, object]], summary: dict[str, object], output_path: Path) -> None:
    """Plot hit rate, skipped-gap count, and runtime by decade."""
    powers = [row["power"] for row in rows]
    decade_labels = [f"10^{power}" for power in powers]
    hit_rates = [row["exact_immediate_hit_rate"] for row in rows]
    skipped = [row["mean_skipped_gap_count"] for row in rows]
    runtimes = [row["runtime_seconds"] for row in rows]

    fig, axes = plt.subplots(2, 1, figsize=(11, 8.5), height_ratios=[1.1, 1.0])

    axes[0].plot(decade_labels, hit_rates, marker="o", color="#2f7d32", linewidth=2.0, label="Immediate-hit rate")
    axes[0].plot(decade_labels, skipped, marker="o", color="#b23a48", linewidth=2.0, label="Mean skipped gaps")
    axes[0].set_title("Forward GWR Scaling by Start Decade")
    axes[0].set_ylabel("Rate / mean skipped gaps")
    axes[0].grid(alpha=0.2)
    axes[0].legend(loc="upper right")

    summary_text = (
        f"powers = {summary['power_start']}..{summary['power_end']}\n"
        f"mean hit rate = {summary['mean_exact_immediate_hit_rate']:.4f}\n"
        f"mean skipped gaps = {summary['mean_mean_skipped_gap_count']:.4f}\n"
        f"all recovery exact = {summary['all_recovery_exact']}"
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

    bars = axes[1].bar(decade_labels, runtimes, color="#28536b", width=0.7)
    axes[1].set_title("Runtime by Start Decade")
    axes[1].set_ylabel("Seconds")
    axes[1].set_xlabel("Start regime")
    axes[1].grid(axis="y", alpha=0.2)
    for bar, row in zip(bars, rows, strict=True):
        axes[1].text(
            bar.get_x() + bar.get_width() / 2.0,
            bar.get_height(),
            f"{row['steps']}",
            ha="center",
            va="bottom",
            fontsize=8,
        )

    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


def render_plot(input_dir: Path, output_dir: Path) -> Path:
    """Render the scaling sweep plot."""
    detail_path = input_dir / DETAIL_FILENAME
    summary_path = input_dir / SUMMARY_FILENAME
    if not detail_path.exists():
        raise FileNotFoundError(f"missing detail CSV: {detail_path}")
    if not summary_path.exists():
        raise FileNotFoundError(f"missing summary JSON: {summary_path}")

    output_dir.mkdir(parents=True, exist_ok=True)
    rows = _read_rows(detail_path)
    summary = _read_summary(summary_path)
    output_path = output_dir / "gwr_recursive_gap_scaling_sweep.png"
    plot_scaling(rows, summary, output_path)
    return output_path


def main(argv: list[str] | None = None) -> int:
    """Render the scaling sweep plot."""
    args = build_parser().parse_args(argv)
    render_plot(args.input_dir, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
