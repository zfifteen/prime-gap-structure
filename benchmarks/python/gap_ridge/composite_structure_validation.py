#!/usr/bin/env python3
"""Validate or falsify composite-structure organization inside prime gaps."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/z-band-prime-prefilter-mpl")

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter

ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = ROOT / "src" / "python"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from geodesic_prime_composite_field import divisor_counts_segment
from geodesic_prime_gap_ridge.runs import build_even_window_starts


DEFAULT_OUTPUT_DIR = Path("benchmarks/output/python/gap_ridge/composite_structure_validation")
DEFAULT_FULL_LIMITS = (1_000_000, 10_000_000)
DEFAULT_WINDOW_SCALES = (100_000_000, 1_000_000_000, 10_000_000_000)
DEFAULT_WINDOW_SIZE = 2_000_000
DEFAULT_WINDOW_COUNT = 4
NORMALIZED_BIN_COUNT = 12
EDGE_ZONE_BIN_COUNT = 3
HIGH_DIVISOR_THRESHOLD = 12
DIVISOR_BUCKET_LABELS = ["4", "6", "8", "10", "12", "14", "16+"]
GAP_SIZE_BINS = (
    ("6-10", 6, 10),
    ("12-20", 12, 20),
    ("22+", 22, None),
)


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description="Validate or falsify composite-structure organization inside prime gaps.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for JSON and plot artifacts.",
    )
    parser.add_argument(
        "--full-limits",
        type=int,
        nargs="+",
        default=list(DEFAULT_FULL_LIMITS),
        help="Exact full natural-number ceilings to analyze.",
    )
    parser.add_argument(
        "--window-scales",
        type=int,
        nargs="+",
        default=list(DEFAULT_WINDOW_SCALES),
        help="Larger scales analyzed through evenly spaced windows.",
    )
    parser.add_argument(
        "--window-size",
        type=int,
        default=DEFAULT_WINDOW_SIZE,
        help="Width of each exact sampled window.",
    )
    parser.add_argument(
        "--window-count",
        type=int,
        default=DEFAULT_WINDOW_COUNT,
        help="Number of evenly spaced windows per larger scale.",
    )
    parser.add_argument(
        "--detail-scale",
        type=int,
        default=10_000_000,
        help="Exact full scale used for detailed normalized-position plots.",
    )
    return parser


def empty_scope_stats() -> dict[str, np.ndarray]:
    """Return one zeroed statistics payload."""
    return {
        "normalized_count": np.zeros(NORMALIZED_BIN_COUNT, dtype=np.int64),
        "normalized_divisor_sum": np.zeros(NORMALIZED_BIN_COUNT, dtype=np.float64),
        "normalized_d4_count": np.zeros(NORMALIZED_BIN_COUNT, dtype=np.int64),
        "normalized_high_count": np.zeros(NORMALIZED_BIN_COUNT, dtype=np.int64),
        "normalized_bucket_count": np.zeros(
            (len(DIVISOR_BUCKET_LABELS), NORMALIZED_BIN_COUNT),
            dtype=np.int64,
        ),
        "edge_zone_count": np.array(0, dtype=np.int64),
        "edge_zone_divisor_sum": np.array(0.0, dtype=np.float64),
        "edge_zone_d4_count": np.array(0, dtype=np.int64),
        "edge_zone_high_count": np.array(0, dtype=np.int64),
        "center_zone_count": np.array(0, dtype=np.int64),
        "center_zone_divisor_sum": np.array(0.0, dtype=np.float64),
        "center_zone_d4_count": np.array(0, dtype=np.int64),
        "center_zone_high_count": np.array(0, dtype=np.int64),
    }


def empty_accumulator() -> dict[str, object]:
    """Return one zeroed accumulator for one regime or gap-size bin."""
    return {
        "gap_count": 0,
        "all": empty_scope_stats(),
        "odd": empty_scope_stats(),
    }


def divisor_bucket_index(divisor_count: int) -> int:
    """Map one divisor count to one compact visualization bucket."""
    if divisor_count <= 4:
        return 0
    if divisor_count >= 16:
        return len(DIVISOR_BUCKET_LABELS) - 1
    if divisor_count <= 6:
        return 1
    if divisor_count <= 8:
        return 2
    if divisor_count <= 10:
        return 3
    if divisor_count <= 12:
        return 4
    if divisor_count <= 14:
        return 5
    return len(DIVISOR_BUCKET_LABELS) - 1


def gap_size_label(gap: int) -> str | None:
    """Return the configured gap-size label for one gap."""
    for label, lo, hi in GAP_SIZE_BINS:
        if gap < lo:
            continue
        if hi is None or gap <= hi:
            return label
    return None


def update_scope_stats(scope: dict[str, np.ndarray], bin_index: int, divisor_count: int) -> None:
    """Update one scope payload with one interior composite observation."""
    scope["normalized_count"][bin_index] += 1
    scope["normalized_divisor_sum"][bin_index] += float(divisor_count)
    scope["normalized_d4_count"][bin_index] += int(divisor_count == 4)
    scope["normalized_high_count"][bin_index] += int(divisor_count >= HIGH_DIVISOR_THRESHOLD)
    scope["normalized_bucket_count"][divisor_bucket_index(divisor_count), bin_index] += 1

    if bin_index < EDGE_ZONE_BIN_COUNT:
        scope["edge_zone_count"] += 1
        scope["edge_zone_divisor_sum"] += float(divisor_count)
        scope["edge_zone_d4_count"] += int(divisor_count == 4)
        scope["edge_zone_high_count"] += int(divisor_count >= HIGH_DIVISOR_THRESHOLD)

    if bin_index >= NORMALIZED_BIN_COUNT - EDGE_ZONE_BIN_COUNT:
        scope["center_zone_count"] += 1
        scope["center_zone_divisor_sum"] += float(divisor_count)
        scope["center_zone_d4_count"] += int(divisor_count == 4)
        scope["center_zone_high_count"] += int(divisor_count >= HIGH_DIVISOR_THRESHOLD)


def analyze_interval(lo: int, hi: int) -> dict[str, dict[str, object]]:
    """Analyze one exact interval."""
    divisor_count = divisor_counts_segment(lo, hi)
    values = np.arange(lo, hi, dtype=np.int64)
    primes = values[divisor_count == 2]

    accumulators: dict[str, dict[str, object]] = {"overall": empty_accumulator()}
    for label, _, _ in GAP_SIZE_BINS:
        accumulators[label] = empty_accumulator()

    for left_prime, right_prime in zip(primes[:-1], primes[1:]):
        gap = int(right_prime - left_prime)
        if gap < 6:
            continue

        label = gap_size_label(gap)
        targets = [accumulators["overall"]]
        if label is not None:
            targets.append(accumulators[label])

        for target in targets:
            target["gap_count"] = int(target["gap_count"]) + 1

        left_index = int(left_prime - lo + 1)
        right_index = int(right_prime - lo)
        gap_values = values[left_index:right_index]
        gap_divisors = divisor_count[left_index:right_index]
        max_edge_distance = gap // 2

        for offset, candidate_n in enumerate(gap_values, start=1):
            edge_distance = min(offset, gap - offset)
            if max_edge_distance > 1:
                normalized_position = (edge_distance - 1) / (max_edge_distance - 1)
            else:
                normalized_position = 1.0
            bin_index = min(
                int(normalized_position * NORMALIZED_BIN_COUNT),
                NORMALIZED_BIN_COUNT - 1,
            )
            d_value = int(gap_divisors[offset - 1])

            for target in targets:
                update_scope_stats(target["all"], bin_index, d_value)  # type: ignore[arg-type]
                if candidate_n % 2 == 1:
                    update_scope_stats(target["odd"], bin_index, d_value)  # type: ignore[arg-type]

    return accumulators


def merge_accumulators(target: dict[str, dict[str, object]], source: dict[str, dict[str, object]]) -> None:
    """Merge one interval accumulator into a regime accumulator."""
    for label, source_entry in source.items():
        target_entry = target[label]
        target_entry["gap_count"] = int(target_entry["gap_count"]) + int(source_entry["gap_count"])
        for scope_name in ("all", "odd"):
            target_scope = target_entry[scope_name]
            source_scope = source_entry[scope_name]
            for key in target_scope:
                target_scope[key] += source_scope[key]


def build_regime_accumulator() -> dict[str, dict[str, object]]:
    """Return one empty regime accumulator."""
    regime = {"overall": empty_accumulator()}
    for label, _, _ in GAP_SIZE_BINS:
        regime[label] = empty_accumulator()
    return regime


def summarize_scope(scope: dict[str, np.ndarray]) -> dict[str, object]:
    """Convert one scope accumulator into JSON-ready metrics."""
    normalized_count = scope["normalized_count"]
    normalized_divisor_sum = scope["normalized_divisor_sum"]
    normalized_d4_count = scope["normalized_d4_count"]
    normalized_high_count = scope["normalized_high_count"]
    normalized_bucket_count = scope["normalized_bucket_count"]

    normalized_mean_divisors = np.divide(
        normalized_divisor_sum,
        normalized_count,
        out=np.zeros(NORMALIZED_BIN_COUNT, dtype=np.float64),
        where=normalized_count > 0,
    )
    normalized_d4_share = np.divide(
        normalized_d4_count,
        normalized_count,
        out=np.zeros(NORMALIZED_BIN_COUNT, dtype=np.float64),
        where=normalized_count > 0,
    )
    normalized_high_share = np.divide(
        normalized_high_count,
        normalized_count,
        out=np.zeros(NORMALIZED_BIN_COUNT, dtype=np.float64),
        where=normalized_count > 0,
    )
    normalized_bucket_share = np.divide(
        normalized_bucket_count,
        normalized_count[np.newaxis, :],
        out=np.zeros_like(normalized_bucket_count, dtype=np.float64),
        where=normalized_count[np.newaxis, :] > 0,
    )

    edge_count = int(scope["edge_zone_count"])
    center_count = int(scope["center_zone_count"])
    edge_mean_divisors = (
        float(scope["edge_zone_divisor_sum"] / edge_count) if edge_count > 0 else None
    )
    center_mean_divisors = (
        float(scope["center_zone_divisor_sum"] / center_count) if center_count > 0 else None
    )
    edge_d4_share = (
        float(scope["edge_zone_d4_count"] / edge_count) if edge_count > 0 else None
    )
    center_d4_share = (
        float(scope["center_zone_d4_count"] / center_count) if center_count > 0 else None
    )
    edge_high_share = (
        float(scope["edge_zone_high_count"] / edge_count) if edge_count > 0 else None
    )
    center_high_share = (
        float(scope["center_zone_high_count"] / center_count) if center_count > 0 else None
    )

    return {
        "normalized_position_bin_centers": (
            (np.arange(NORMALIZED_BIN_COUNT, dtype=np.float64) + 0.5) / NORMALIZED_BIN_COUNT
        ).tolist(),
        "normalized_mean_divisors": normalized_mean_divisors.tolist(),
        "normalized_d4_share": normalized_d4_share.tolist(),
        "normalized_high_divisor_share": normalized_high_share.tolist(),
        "normalized_bucket_share": normalized_bucket_share.tolist(),
        "edge_zone_count": edge_count,
        "center_zone_count": center_count,
        "edge_mean_divisors": edge_mean_divisors,
        "center_mean_divisors": center_mean_divisors,
        "edge_d4_share": edge_d4_share,
        "center_d4_share": center_d4_share,
        "edge_high_divisor_share": edge_high_share,
        "center_high_divisor_share": center_high_share,
    }


def summarize_regime(
    scale: int,
    regime_type: str,
    accumulator: dict[str, dict[str, object]],
    window_size: int | None = None,
    window_count: int | None = None,
) -> dict[str, object]:
    """Convert one regime accumulator into JSON-ready metrics."""
    result: dict[str, object] = {
        "scale": scale,
        "regime_type": regime_type,
        "window_size": window_size,
        "window_count": window_count,
        "gap_bins": {},
    }
    overall_entry = accumulator["overall"]
    result["gap_count"] = int(overall_entry["gap_count"])
    result["all"] = summarize_scope(overall_entry["all"])  # type: ignore[arg-type]
    result["odd"] = summarize_scope(overall_entry["odd"])  # type: ignore[arg-type]
    for label, _, _ in GAP_SIZE_BINS:
        gap_entry = accumulator[label]
        result["gap_bins"][label] = {
            "gap_count": int(gap_entry["gap_count"]),
            "all": summarize_scope(gap_entry["all"]),  # type: ignore[arg-type]
            "odd": summarize_scope(gap_entry["odd"]),  # type: ignore[arg-type]
        }
    return result


def validate_regime(regime: dict[str, object]) -> tuple[bool, list[str]]:
    """Evaluate the validation conditions for one regime."""
    failures: list[str] = []
    scale = int(regime["scale"])
    regime_type = str(regime["regime_type"])

    for scope_name in ("all", "odd"):
        scope = regime[scope_name]
        if scope["edge_mean_divisors"] is None or scope["center_mean_divisors"] is None:
            failures.append(f"{scale} {regime_type} {scope_name} missing edge/center support")
            continue
        if not scope["edge_mean_divisors"] < scope["center_mean_divisors"]:
            failures.append(f"{scale} {regime_type} {scope_name} mean divisor slope failed")
        if not scope["edge_d4_share"] > scope["center_d4_share"]:
            failures.append(f"{scale} {regime_type} {scope_name} d4 edge concentration failed")
        if not scope["edge_high_divisor_share"] < scope["center_high_divisor_share"]:
            failures.append(f"{scale} {regime_type} {scope_name} high-divisor center concentration failed")

    if regime_type == "exact":
        gap_bins = regime["gap_bins"]
        for label, gap_entry in gap_bins.items():
            if int(gap_entry["gap_count"]) < 200:
                continue
            for scope_name in ("all", "odd"):
                scope = gap_entry[scope_name]
                if scope["edge_mean_divisors"] is None or scope["center_mean_divisors"] is None:
                    failures.append(f"{scale} {label} {scope_name} missing edge/center support")
                    continue
                if not scope["edge_mean_divisors"] < scope["center_mean_divisors"]:
                    failures.append(f"{scale} {label} {scope_name} mean divisor slope failed")
                if not scope["edge_d4_share"] > scope["center_d4_share"]:
                    failures.append(f"{scale} {label} {scope_name} d4 edge concentration failed")
                if not scope["edge_high_divisor_share"] < scope["center_high_divisor_share"]:
                    failures.append(f"{scale} {label} {scope_name} high-divisor center concentration failed")

    return (len(failures) == 0, failures)


def render_summary_panel(regimes: list[dict[str, object]], output_path: Path) -> None:
    """Render one scale summary panel."""
    scales = np.array([int(row["scale"]) for row in regimes], dtype=np.int64)
    all_edge_mean = np.array([row["all"]["edge_mean_divisors"] for row in regimes], dtype=np.float64)
    all_center_mean = np.array([row["all"]["center_mean_divisors"] for row in regimes], dtype=np.float64)
    odd_edge_mean = np.array([row["odd"]["edge_mean_divisors"] for row in regimes], dtype=np.float64)
    odd_center_mean = np.array([row["odd"]["center_mean_divisors"] for row in regimes], dtype=np.float64)
    all_edge_d4 = np.array([row["all"]["edge_d4_share"] for row in regimes], dtype=np.float64)
    all_center_d4 = np.array([row["all"]["center_d4_share"] for row in regimes], dtype=np.float64)
    odd_edge_d4 = np.array([row["odd"]["edge_d4_share"] for row in regimes], dtype=np.float64)
    odd_center_d4 = np.array([row["odd"]["center_d4_share"] for row in regimes], dtype=np.float64)

    fig, axes = plt.subplots(2, 2, figsize=(12.0, 9.2), sharex=True)
    axes[0, 0].plot(scales, all_edge_mean, marker="o", linewidth=2.3, color="#1f4e79", label="Edge zone")
    axes[0, 0].plot(scales, all_center_mean, marker="o", linewidth=2.3, color="#c05621", label="Center zone")
    axes[0, 0].set_title("All composites: mean divisor count")
    axes[0, 0].set_ylabel("Mean d(n)")
    axes[0, 0].grid(True, alpha=0.25)
    axes[0, 0].legend(frameon=False)

    axes[0, 1].plot(scales, odd_edge_mean, marker="o", linewidth=2.3, color="#1f4e79", label="Edge zone")
    axes[0, 1].plot(scales, odd_center_mean, marker="o", linewidth=2.3, color="#c05621", label="Center zone")
    axes[0, 1].set_title("Odd composites only: mean divisor count")
    axes[0, 1].grid(True, alpha=0.25)
    axes[0, 1].legend(frameon=False)

    axes[1, 0].plot(scales, all_edge_d4, marker="o", linewidth=2.3, color="#0f8b8d", label="Edge zone")
    axes[1, 0].plot(scales, all_center_d4, marker="o", linewidth=2.3, color="#7b341e", label="Center zone")
    axes[1, 0].set_title("All composites: d(n)=4 share")
    axes[1, 0].set_ylabel("Share")
    axes[1, 0].grid(True, alpha=0.25)
    axes[1, 0].legend(frameon=False)

    axes[1, 1].plot(scales, odd_edge_d4, marker="o", linewidth=2.3, color="#0f8b8d", label="Edge zone")
    axes[1, 1].plot(scales, odd_center_d4, marker="o", linewidth=2.3, color="#7b341e", label="Center zone")
    axes[1, 1].set_title("Odd composites only: d(n)=4 share")
    axes[1, 1].grid(True, alpha=0.25)
    axes[1, 1].legend(frameon=False)

    for ax in axes.flat:
        ax.set_xscale("log")
        ax.xaxis.set_major_formatter(
            FuncFormatter(lambda value, _: rf"$10^{{{int(np.log10(value))}}}$")
        )
    axes[1, 0].yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value * 100.0:.0f}%"))
    axes[1, 1].yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value * 100.0:.0f}%"))
    axes[1, 0].set_xlabel("Scale")
    axes[1, 1].set_xlabel("Scale")
    fig.suptitle("Prime-gap edges stay simpler than centers across tested scales", y=0.99)
    fig.tight_layout()
    fig.savefig(output_path, format="svg")
    plt.close(fig)


def render_detail_panel(regime: dict[str, object], output_path: Path) -> None:
    """Render one detailed normalized-position panel."""
    x_values = np.array(regime["all"]["normalized_position_bin_centers"], dtype=np.float64)

    fig, axes = plt.subplots(2, 2, figsize=(12.0, 9.0), sharex=True)

    axes[0, 0].plot(
        x_values,
        np.array(regime["all"]["normalized_mean_divisors"], dtype=np.float64),
        marker="o",
        linewidth=2.3,
        color="#1f4e79",
    )
    axes[0, 0].set_title("All composites: mean divisor count")
    axes[0, 0].set_ylabel("Mean d(n)")
    axes[0, 0].grid(True, alpha=0.25)

    axes[0, 1].plot(
        x_values,
        np.array(regime["odd"]["normalized_mean_divisors"], dtype=np.float64),
        marker="o",
        linewidth=2.3,
        color="#1f4e79",
    )
    axes[0, 1].set_title("Odd composites only: mean divisor count")
    axes[0, 1].grid(True, alpha=0.25)

    axes[1, 0].plot(
        x_values,
        np.array(regime["all"]["normalized_d4_share"], dtype=np.float64),
        marker="o",
        linewidth=2.1,
        color="#0f8b8d",
        label="d(n)=4 share",
    )
    axes[1, 0].plot(
        x_values,
        np.array(regime["all"]["normalized_high_divisor_share"], dtype=np.float64),
        marker="o",
        linewidth=2.1,
        color="#c05621",
        label=f"d(n)>={HIGH_DIVISOR_THRESHOLD} share",
    )
    axes[1, 0].set_title("All composites: low-divisor edge, high-divisor center")
    axes[1, 0].set_xlabel("Normalized position from edge to center")
    axes[1, 0].set_ylabel("Share")
    axes[1, 0].grid(True, alpha=0.25)
    axes[1, 0].legend(frameon=False)

    axes[1, 1].plot(
        x_values,
        np.array(regime["odd"]["normalized_d4_share"], dtype=np.float64),
        marker="o",
        linewidth=2.1,
        color="#0f8b8d",
        label="d(n)=4 share",
    )
    axes[1, 1].plot(
        x_values,
        np.array(regime["odd"]["normalized_high_divisor_share"], dtype=np.float64),
        marker="o",
        linewidth=2.1,
        color="#c05621",
        label=f"d(n)>={HIGH_DIVISOR_THRESHOLD} share",
    )
    axes[1, 1].set_title("Odd composites only: the same gradient survives")
    axes[1, 1].set_xlabel("Normalized position from edge to center")
    axes[1, 1].grid(True, alpha=0.25)
    axes[1, 1].legend(frameon=False)

    axes[1, 0].yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value * 100.0:.0f}%"))
    axes[1, 1].yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value * 100.0:.0f}%"))
    fig.suptitle(
        f"Detailed exact profile at scale {int(regime['scale']):,}",
        y=0.99,
    )
    fig.tight_layout()
    fig.savefig(output_path, format="svg")
    plt.close(fig)


def render_gap_bin_heatmaps(regime: dict[str, object], output_path: Path) -> None:
    """Render gap-size-conditioned heatmaps for the detailed exact regime."""
    fig, axes = plt.subplots(len(GAP_SIZE_BINS), 2, figsize=(12.0, 10.5), sharex=True)

    for row_index, (label, _, _) in enumerate(GAP_SIZE_BINS):
        gap_entry = regime["gap_bins"][label]
        all_bucket_share = np.array(
            gap_entry["all"]["normalized_bucket_share"],
            dtype=np.float64,
        )
        odd_bucket_share = np.array(
            gap_entry["odd"]["normalized_bucket_share"],
            dtype=np.float64,
        )
        images = [
            axes[row_index, 0].imshow(all_bucket_share, aspect="auto", cmap="YlOrRd", origin="lower"),
            axes[row_index, 1].imshow(odd_bucket_share, aspect="auto", cmap="YlGnBu", origin="lower"),
        ]
        axes[row_index, 0].set_ylabel(f"Gap {label}\nDivisor bucket")
        axes[row_index, 0].set_yticks(np.arange(len(DIVISOR_BUCKET_LABELS)))
        axes[row_index, 0].set_yticklabels([f"d={value}" for value in DIVISOR_BUCKET_LABELS])
        axes[row_index, 1].set_yticks(np.arange(len(DIVISOR_BUCKET_LABELS)))
        axes[row_index, 1].set_yticklabels([f"d={value}" for value in DIVISOR_BUCKET_LABELS])
        for column_index, ax in enumerate(axes[row_index]):
            ax.set_xticks(np.arange(NORMALIZED_BIN_COUNT))
            ax.set_xticklabels(
                [f"{value:.2f}" for value in regime["all"]["normalized_position_bin_centers"]],
                rotation=45,
                ha="right",
            )
            if row_index == 0:
                ax.set_title("All composites" if column_index == 0 else "Odd composites only")
        for image, ax in zip(images, axes[row_index]):
            colorbar = fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
            colorbar.ax.yaxis.set_major_formatter(
                FuncFormatter(lambda value, _: f"{value * 100.0:.0f}%")
            )
            colorbar.set_label("Share")

    axes[-1, 0].set_xlabel("Normalized position from edge to center")
    axes[-1, 1].set_xlabel("Normalized position from edge to center")
    fig.suptitle("Gap-size-conditioned divisor structure at the detailed exact scale", y=0.995)
    fig.tight_layout()
    fig.savefig(output_path, format="svg")
    plt.close(fig)


def main(argv: list[str] | None = None) -> int:
    """Run the validation campaign."""
    args = build_parser().parse_args(argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    regimes: list[dict[str, object]] = []

    for limit in args.full_limits:
        accumulator = analyze_interval(2, limit + 1)
        regimes.append(summarize_regime(limit, "exact", accumulator))

    for scale in args.window_scales:
        accumulator = build_regime_accumulator()
        starts = build_even_window_starts(scale, args.window_size, args.window_count)
        for start in starts:
            merge_accumulators(
                accumulator,
                analyze_interval(start, start + args.window_size),
            )
        regimes.append(
            summarize_regime(
                scale,
                "even-window",
                accumulator,
                window_size=args.window_size,
                window_count=args.window_count,
            )
        )

    regimes.sort(key=lambda row: int(row["scale"]))
    decisions: list[dict[str, object]] = []
    failure_messages: list[str] = []
    for regime in regimes:
        passed, failures = validate_regime(regime)
        decisions.append(
            {
                "scale": regime["scale"],
                "regime_type": regime["regime_type"],
                "passed": passed,
                "failures": failures,
            }
        )
        failure_messages.extend(failures)

    validation_status = "validated" if not failure_messages else "falsified"

    detail_regime = next(
        (row for row in regimes if int(row["scale"]) == args.detail_scale and str(row["regime_type"]) == "exact"),
        None,
    )
    if detail_regime is None:
        raise ValueError(f"detail scale {args.detail_scale} is not present in the exact regime set")

    render_summary_panel(regimes, args.output_dir / "validation_summary_panel.svg")
    render_detail_panel(detail_regime, args.output_dir / "validation_detail_panel.svg")
    render_gap_bin_heatmaps(detail_regime, args.output_dir / "validation_gap_bin_heatmaps.svg")

    payload = {
        "validation_status": validation_status,
        "decision_rule": (
            "validated only if edge zones remain simpler than center zones in all tested regimes, "
            "in odd-only controls, and in every exact gap-size bin with at least 200 gaps"
        ),
        "regimes": regimes,
        "decisions": decisions,
    }
    (args.output_dir / "validation_results.json").write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
