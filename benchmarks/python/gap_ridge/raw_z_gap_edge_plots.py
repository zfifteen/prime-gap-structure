#!/usr/bin/env python3
"""Render 2D and 3D plots for the exact raw composite Z gap-edge ridge."""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/geodesic-prime-prefilter-mpl")

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


DEFAULT_SUITE_JSON = (
    Path("benchmarks/output/python/gap_ridge/raw_z_gap_edge/raw_z_gap_edge_run_all.json")
)
DEFAULT_OUTPUT_DIR = Path("benchmarks/output/python/gap_ridge/raw_z_gap_edge")
EDGE_DISTANCE_CUTOFF = 8
CARRIER_CATEGORY_COUNT = 6
GAP_SIZE_COUNT_THRESHOLD = 100


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser for gap-edge plot rendering."""
    parser = argparse.ArgumentParser(
        description="Render 2D and 3D plots for the raw composite Z gap-edge ridge.",
    )
    parser.add_argument(
        "--suite-json",
        type=Path,
        default=DEFAULT_SUITE_JSON,
        help="JSON file emitted by raw_z_gap_edge_run_all.py.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for plot artifacts.",
    )
    parser.add_argument(
        "--detail-limit",
        type=int,
        default=1_000_000,
        help="Exact limit used for detailed million-scale plot data.",
    )
    parser.add_argument(
        "--gap-size-threshold",
        type=int,
        default=GAP_SIZE_COUNT_THRESHOLD,
        help="Minimum number of gaps for a gap size to appear in 3D plots.",
    )
    return parser


def load_suite_rows(path: Path) -> list[dict[str, object]]:
    """Load the consolidated regime JSON and flatten the row groups."""
    data = json.loads(path.read_text(encoding="utf-8"))
    return (
        list(data["exact_full_runs"])
        + list(data["even_window_runs"])
        + list(data["seeded_window_runs"])
    )


def collect_detail(limit: int) -> dict[str, object]:
    """Collect exact million-scale detail for local and aggregated ridge plots."""
    if limit < 5:
        raise ValueError("detail limit must be at least 5")

    lo = 2
    hi = limit + 1
    divisor_count = divisor_counts_segment(lo, hi)
    values = np.arange(lo, hi, dtype=np.int64)
    primes = values[divisor_count == 2]
    log_values = np.log(values.astype(np.float64))

    gap_count = 0
    edge_observed = Counter()
    edge_baseline = Counter()
    carrier_observed = Counter()
    carrier_baseline = Counter()
    gap_size_counts = Counter()
    gap_size_edge_observed: dict[int, Counter[int]] = defaultdict(Counter)
    gap_size_edge_baseline: dict[int, Counter[int]] = defaultdict(Counter)
    gap_size_carrier_observed: dict[int, Counter[int]] = defaultdict(Counter)
    gap_size_carrier_baseline: dict[int, Counter[int]] = defaultdict(Counter)

    representative: dict[str, object] | None = None

    for left_prime, right_prime in zip(primes[:-1], primes[1:]):
        gap = int(right_prime - left_prime)
        if gap < 4:
            continue

        left_index = int(left_prime - lo + 1)
        right_index = int(right_prime - lo)
        gap_values = values[left_index:right_index]
        gap_divisors = divisor_count[left_index:right_index]
        scores = (
            1.0 - gap_divisors.astype(np.float64) / 2.0
        ) * log_values[left_index:right_index]
        best_index = int(np.argmax(scores))
        best_offset = best_index + 1
        best_edge_distance = min(best_offset, gap - best_offset)
        best_divisors = int(gap_divisors[best_index])

        gap_count += 1
        gap_size_counts[gap] += 1
        edge_observed[best_edge_distance] += 1
        carrier_observed[best_divisors] += 1
        gap_size_edge_observed[gap][best_edge_distance] += 1
        gap_size_carrier_observed[gap][best_divisors] += 1

        position_count = gap - 1
        for offset, d_value in enumerate(gap_divisors, start=1):
            edge_distance = min(offset, gap - offset)
            share_increment = 1.0 / position_count
            edge_baseline[edge_distance] += share_increment
            carrier_baseline[int(d_value)] += share_increment
            gap_size_edge_baseline[gap][edge_distance] += share_increment
            gap_size_carrier_baseline[gap][int(d_value)] += share_increment

        if best_edge_distance == 2 and best_divisors == 4:
            candidate = {
                "left_prime": int(left_prime),
                "right_prime": int(right_prime),
                "gap": gap,
                "peak_n": int(gap_values[best_index]),
                "peak_offset": best_offset,
                "peak_edge_distance": best_edge_distance,
                "peak_divisors": best_divisors,
                "positions": list(range(1, gap)),
                "log_raw_z": scores.tolist(),
                "divisors": gap_divisors.astype(int).tolist(),
            }
            if representative is None or gap > int(representative["gap"]):
                representative = candidate

    if representative is None:
        raise RuntimeError("no representative edge-distance-2, d(n)=4 gap found")

    return {
        "gap_count": gap_count,
        "edge_observed": edge_observed,
        "edge_baseline": edge_baseline,
        "carrier_observed": carrier_observed,
        "carrier_baseline": carrier_baseline,
        "gap_size_counts": gap_size_counts,
        "gap_size_edge_observed": gap_size_edge_observed,
        "gap_size_edge_baseline": gap_size_edge_baseline,
        "gap_size_carrier_observed": gap_size_carrier_observed,
        "gap_size_carrier_baseline": gap_size_carrier_baseline,
        "representative": representative,
    }


def render_regime_enrichment(rows: list[dict[str, object]], output_path: Path) -> None:
    """Render the scale-by-regime enrichment confirmation plot."""
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["window_mode"])].append(row)

    for mode_rows in grouped.values():
        mode_rows.sort(key=lambda row: int(row["scale"]))

    fig, axes = plt.subplots(2, 1, figsize=(10.5, 10.5), sharex=True)
    colors = {"exact": "#1f4e79", "even": "#0f8b8d", "seeded-random": "#c05621"}
    labels = {"exact": "Exact full runs", "even": "Even windows", "seeded-random": "Seeded windows"}

    for mode in ("exact", "even", "seeded-random"):
        mode_rows = grouped.get(mode, [])
        if not mode_rows:
            continue
        x_values = [int(row["scale"]) for row in mode_rows]
        axes[0].plot(
            x_values,
            [float(row["edge2_enrichment"]) for row in mode_rows],
            marker="o",
            linewidth=2.5,
            markersize=7,
            color=colors[mode],
            label=labels[mode],
        )
        axes[1].plot(
            x_values,
            [float(row["d4_enrichment"]) for row in mode_rows],
            marker="o",
            linewidth=2.5,
            markersize=7,
            color=colors[mode],
            label=labels[mode],
        )

    axes[0].set_title("Near-edge and d(n)=4 ridge enrichment across tested scales", pad=16)
    axes[0].set_ylabel("Edge-distance-2 enrichment")
    axes[1].set_ylabel("d(n)=4 carrier enrichment")
    axes[1].set_xlabel("Natural-number scale")

    for ax in axes:
        ax.set_xscale("log")
        ax.grid(True, alpha=0.25)
        ax.legend(frameon=False)

    axes[1].xaxis.set_major_formatter(
        FuncFormatter(lambda value, _: rf"$10^{{{int(np.log10(value))}}}$")
    )
    fig.tight_layout()
    fig.savefig(output_path, format="svg")
    plt.close(fig)


def render_edge_distribution(detail: dict[str, object], output_path: Path) -> None:
    """Render observed versus baseline peak positions by edge distance."""
    gap_count = int(detail["gap_count"])
    observed: Counter[int] = detail["edge_observed"]  # type: ignore[assignment]
    baseline: Counter[int] = detail["edge_baseline"]  # type: ignore[assignment]

    categories = list(range(1, EDGE_DISTANCE_CUTOFF + 1))
    labels = [str(value) for value in categories] + [f">{EDGE_DISTANCE_CUTOFF}"]

    observed_values = [
        observed.get(value, 0) / gap_count for value in categories
    ] + [
        sum(count for value, count in observed.items() if value > EDGE_DISTANCE_CUTOFF)
        / gap_count
    ]
    baseline_values = [
        baseline.get(value, 0.0) / gap_count for value in categories
    ] + [
        sum(
            count for value, count in baseline.items() if value > EDGE_DISTANCE_CUTOFF
        )
        / gap_count
    ]

    x = np.arange(len(labels), dtype=np.float64)
    width = 0.38

    fig, ax = plt.subplots(figsize=(11.0, 6.4))
    ax.bar(x - width / 2.0, observed_values, width, color="#1f4e79", label="Observed peak share")
    ax.bar(x + width / 2.0, baseline_values, width, color="#d9e2ec", label="Within-gap baseline")
    ax.set_title("Gap-local raw-Z maxima cluster near the edge", pad=14)
    ax.set_xlabel("Edge distance from nearest prime boundary")
    ax.set_ylabel("Share of tested prime gaps")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value * 100.0:.0f}%"))
    ax.grid(True, axis="y", alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(output_path, format="svg")
    plt.close(fig)


def render_carrier_distribution(detail: dict[str, object], output_path: Path) -> None:
    """Render observed versus baseline carrier divisor counts."""
    gap_count = int(detail["gap_count"])
    observed: Counter[int] = detail["carrier_observed"]  # type: ignore[assignment]
    baseline: Counter[int] = detail["carrier_baseline"]  # type: ignore[assignment]

    top_divisors = [
        divisor
        for divisor, _ in sorted(
            observed.items(),
            key=lambda item: (-item[1], item[0]),
        )[:CARRIER_CATEGORY_COUNT]
    ]
    labels = [f"d={value}" for value in top_divisors] + ["other"]
    observed_values = [observed.get(value, 0) / gap_count for value in top_divisors]
    baseline_values = [baseline.get(value, 0.0) / gap_count for value in top_divisors]
    observed_values.append(
        sum(count for value, count in observed.items() if value not in top_divisors)
        / gap_count
    )
    baseline_values.append(
        sum(count for value, count in baseline.items() if value not in top_divisors)
        / gap_count
    )

    x = np.arange(len(labels), dtype=np.float64)
    width = 0.38

    fig, ax = plt.subplots(figsize=(10.2, 6.4))
    ax.bar(x - width / 2.0, observed_values, width, color="#0f8b8d", label="Observed carrier share")
    ax.bar(x + width / 2.0, baseline_values, width, color="#d9e2ec", label="Within-gap baseline")
    ax.set_title("The ridge is carried mainly by d(n)=4 composites", pad=14)
    ax.set_xlabel("Carrier divisor count")
    ax.set_ylabel("Share of tested prime gaps")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value * 100.0:.0f}%"))
    ax.grid(True, axis="y", alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(output_path, format="svg")
    plt.close(fig)


def render_representative_gap(detail: dict[str, object], output_path: Path) -> None:
    """Render one representative prime-gap raw-Z profile."""
    representative = detail["representative"]
    if not isinstance(representative, dict):
        raise TypeError("representative gap payload must be a mapping")

    positions = np.array(representative["positions"], dtype=np.int64)
    scores = np.array(representative["log_raw_z"], dtype=np.float64)
    peak_offset = int(representative["peak_offset"])

    fig, ax = plt.subplots(figsize=(11.0, 6.6))
    ax.plot(positions, scores, color="#c05621", linewidth=2.5)
    ax.scatter(
        [peak_offset],
        [scores[peak_offset - 1]],
        color="#1f4e79",
        s=80,
        zorder=3,
    )
    ax.axvline(1, color="#243b53", linestyle="--", linewidth=1.2, alpha=0.5)
    ax.axvline(int(representative["gap"]) - 1, color="#243b53", linestyle="--", linewidth=1.2, alpha=0.5)
    ax.set_title(
        "Representative prime-gap slice: the raw-Z ridge rises near the boundary",
        pad=14,
    )
    ax.set_xlabel(
        f"Offset inside gap [{representative['left_prime']}, {representative['right_prime']}]"
    )
    ax.set_ylabel("log raw Z")
    ax.grid(True, alpha=0.25)
    ax.annotate(
        (
            f"peak at n={representative['peak_n']}\n"
            f"edge distance={representative['peak_edge_distance']}, d(n)={representative['peak_divisors']}"
        ),
        xy=(peak_offset, scores[peak_offset - 1]),
        xytext=(peak_offset + 3, scores[peak_offset - 1] + 0.12),
        arrowprops={"arrowstyle": "->", "color": "#1f4e79"},
        fontsize=10,
        color="#102a43",
    )
    fig.tight_layout()
    fig.savefig(output_path, format="svg")
    plt.close(fig)


def render_edge_surface(detail: dict[str, object], output_path: Path, threshold: int) -> None:
    """Render a 3D enrichment plot over gap size and edge distance."""
    gap_size_counts: Counter[int] = detail["gap_size_counts"]  # type: ignore[assignment]
    observed: dict[int, Counter[int]] = detail["gap_size_edge_observed"]  # type: ignore[assignment]
    baseline: dict[int, Counter[int]] = detail["gap_size_edge_baseline"]  # type: ignore[assignment]

    gap_sizes = sorted(
        gap_size
        for gap_size, count in gap_size_counts.items()
        if count >= threshold and gap_size <= 40
    )
    edge_distances = list(range(1, EDGE_DISTANCE_CUTOFF + 1))
    xpos: list[float] = []
    ypos: list[float] = []
    zpos: list[float] = []
    dx: list[float] = []
    dy: list[float] = []
    dz: list[float] = []
    colors: list[tuple[float, float, float, float]] = []
    cmap = plt.get_cmap("viridis")

    for x_index, gap_size in enumerate(gap_sizes):
        gap_count = gap_size_counts[gap_size]
        for y_index, edge_distance in enumerate(edge_distances):
            observed_share = observed[gap_size].get(edge_distance, 0) / gap_count
            baseline_share = baseline[gap_size].get(edge_distance, 0.0) / gap_count
            enrichment = observed_share / baseline_share if baseline_share > 0.0 else 0.0
            xpos.append(x_index)
            ypos.append(y_index)
            zpos.append(0.0)
            dx.append(0.72)
            dy.append(0.72)
            dz.append(enrichment)
            colors.append(cmap(min(enrichment / 2.5, 1.0)))

    fig = plt.figure(figsize=(12.8, 8.4))
    ax = fig.add_subplot(111, projection="3d")
    ax.bar3d(xpos, ypos, zpos, dx, dy, dz, color=colors, shade=True)
    ax.set_title("Gap-size by edge-distance enrichment", pad=18)
    ax.set_xlabel("Gap size")
    ax.set_ylabel("Edge distance")
    ax.set_zlabel("Observed / baseline")
    ax.set_xticks(np.arange(len(gap_sizes)) + 0.36)
    ax.set_xticklabels([str(gap_size) for gap_size in gap_sizes], rotation=45, ha="right")
    ax.set_yticks(np.arange(len(edge_distances)) + 0.36)
    ax.set_yticklabels([str(value) for value in edge_distances])
    ax.view_init(elev=28, azim=-58)
    fig.subplots_adjust(left=0.03, right=0.97, bottom=0.06, top=0.92)
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


def render_carrier_surface(detail: dict[str, object], output_path: Path, threshold: int) -> None:
    """Render a 3D enrichment plot over gap size and carrier divisor count."""
    gap_size_counts: Counter[int] = detail["gap_size_counts"]  # type: ignore[assignment]
    observed: dict[int, Counter[int]] = detail["gap_size_carrier_observed"]  # type: ignore[assignment]
    baseline: dict[int, Counter[int]] = detail["gap_size_carrier_baseline"]  # type: ignore[assignment]
    global_observed: Counter[int] = detail["carrier_observed"]  # type: ignore[assignment]

    gap_sizes = sorted(
        gap_size
        for gap_size, count in gap_size_counts.items()
        if count >= threshold and gap_size <= 40
    )
    divisor_counts = [
        divisor
        for divisor, _ in sorted(
            global_observed.items(),
            key=lambda item: (-item[1], item[0]),
        )[:CARRIER_CATEGORY_COUNT]
    ]

    xpos: list[float] = []
    ypos: list[float] = []
    zpos: list[float] = []
    dx: list[float] = []
    dy: list[float] = []
    dz: list[float] = []
    colors: list[tuple[float, float, float, float]] = []
    cmap = plt.get_cmap("plasma")

    for x_index, gap_size in enumerate(gap_sizes):
        gap_count = gap_size_counts[gap_size]
        for y_index, divisor in enumerate(divisor_counts):
            observed_share = observed[gap_size].get(divisor, 0) / gap_count
            baseline_share = baseline[gap_size].get(divisor, 0.0) / gap_count
            enrichment = observed_share / baseline_share if baseline_share > 0.0 else 0.0
            xpos.append(x_index)
            ypos.append(y_index)
            zpos.append(0.0)
            dx.append(0.72)
            dy.append(0.72)
            dz.append(enrichment)
            colors.append(cmap(min(enrichment / 6.0, 1.0)))

    fig = plt.figure(figsize=(12.8, 8.4))
    ax = fig.add_subplot(111, projection="3d")
    ax.bar3d(xpos, ypos, zpos, dx, dy, dz, color=colors, shade=True)
    ax.set_title("Gap-size by carrier-divisor enrichment", pad=18)
    ax.set_xlabel("Gap size")
    ax.set_ylabel("Carrier divisor count")
    ax.set_zlabel("Observed / baseline")
    ax.set_xticks(np.arange(len(gap_sizes)) + 0.36)
    ax.set_xticklabels([str(gap_size) for gap_size in gap_sizes], rotation=45, ha="right")
    ax.set_yticks(np.arange(len(divisor_counts)) + 0.36)
    ax.set_yticklabels([f"d={value}" for value in divisor_counts])
    ax.view_init(elev=28, azim=-54)
    fig.subplots_adjust(left=0.03, right=0.97, bottom=0.06, top=0.92)
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


def main(argv: list[str] | None = None) -> int:
    """Render the full raw-Z gap-edge plot set."""
    args = build_parser().parse_args(argv)
    if not args.suite_json.exists():
        raise FileNotFoundError(f"suite JSON not found: {args.suite_json}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows = load_suite_rows(args.suite_json)
    detail = collect_detail(args.detail_limit)

    render_regime_enrichment(rows, args.output_dir / "regime_enrichment_2d.svg")
    render_edge_distribution(detail, args.output_dir / "edge_distance_distribution_2d.svg")
    render_carrier_distribution(detail, args.output_dir / "carrier_divisor_distribution_2d.svg")
    render_representative_gap(detail, args.output_dir / "representative_gap_profile_2d.svg")
    render_edge_surface(
        detail,
        args.output_dir / "gap_size_edge_distance_enrichment_3d.png",
        args.gap_size_threshold,
    )
    render_carrier_surface(
        detail,
        args.output_dir / "gap_size_carrier_enrichment_3d.png",
        args.gap_size_threshold,
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
