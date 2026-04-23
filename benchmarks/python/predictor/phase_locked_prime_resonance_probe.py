#!/usr/bin/env python3
"""Measure exact neighborhood structure around record prime gaps."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sympy import primerange


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT_DIR = ROOT / "benchmarks" / "output" / "python" / "predictor" / "phase_locked_prime_resonance"
DEFAULT_MAX_N = 20_000_000
DEFAULT_WINDOW_RADIUS = 8
DEFAULT_RING_INNER = 9
DEFAULT_RING_OUTER = 64
DEFAULT_LATE_CUTOFF = 100_000


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description="Measure exact record-gap neighborhood profiles on a finite prime surface.",
    )
    parser.add_argument(
        "--max-n",
        type=int,
        default=DEFAULT_MAX_N,
        help="Largest integer included in the exact prime surface.",
    )
    parser.add_argument(
        "--window-radius",
        type=int,
        default=DEFAULT_WINDOW_RADIUS,
        help="Number of neighboring gaps kept on each side of the record gap.",
    )
    parser.add_argument(
        "--ring-inner",
        type=int,
        default=DEFAULT_RING_INNER,
        help="Inner exclusion radius for the uncontaminated local baseline ring.",
    )
    parser.add_argument(
        "--ring-outer",
        type=int,
        default=DEFAULT_RING_OUTER,
        help="Outer radius for the uncontaminated local baseline ring.",
    )
    parser.add_argument(
        "--late-cutoff",
        type=int,
        default=DEFAULT_LATE_CUTOFF,
        help="Smallest record-gap start included in the late-record subset.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for JSON and plot artifacts.",
    )
    return parser


def record_gap_indices(gaps: list[int]) -> list[int]:
    """Return the indices of new record gaps."""
    indices: list[int] = []
    largest_gap = -1
    for index, gap in enumerate(gaps):
        if gap > largest_gap:
            indices.append(index)
            largest_gap = gap
    return indices


def ring_baseline(
    gaps: list[int],
    index: int,
    ring_inner: int,
    ring_outer: int,
) -> float:
    """Return the uncontaminated local baseline around one gap."""
    left_ring = gaps[index - ring_outer:index - ring_inner + 1]
    right_ring = gaps[index + ring_inner:index + ring_outer + 1]
    ring = left_ring + right_ring
    return sum(ring) / len(ring)


def neighborhood_profile(
    gaps: list[int],
    indices: list[int],
    window_radius: int,
    ring_inner: int,
    ring_outer: int,
) -> list[float]:
    """Return the mean normalized neighborhood profile for one index set."""
    rows: list[list[float]] = []
    for index in indices:
        baseline = ring_baseline(gaps, index, ring_inner, ring_outer)
        rows.append(
            [gaps[index + offset] / baseline for offset in range(-window_radius, window_radius + 1)]
        )
    return [sum(column) / len(column) for column in zip(*rows)]


def profile_summary(profile: list[float], window_radius: int) -> dict[str, float]:
    """Return compact summary ratios for one neighborhood profile."""
    center = window_radius
    adjacent_mean = (profile[center - 1] + profile[center + 1]) / 2.0
    four_step_mean = (profile[center - 4] + profile[center + 4]) / 2.0
    return {
        "adjacent_mean": adjacent_mean,
        "four_step_mean": four_step_mean,
        "four_step_to_adjacent_ratio": four_step_mean / adjacent_mean,
        "pre_five_mean": sum(profile[center - 5:center]) / 5.0,
        "post_five_mean": sum(profile[center + 1:center + 6]) / 5.0,
    }


def event_rows(
    primes: list[int],
    gaps: list[int],
    indices: list[int],
    ring_inner: int,
    ring_outer: int,
) -> list[dict[str, float | int]]:
    """Return per-record event measurements."""
    rows: list[dict[str, float | int]] = []
    for index in indices:
        baseline = ring_baseline(gaps, index, ring_inner, ring_outer)
        pre_five_mean = sum(gaps[index + offset] / baseline for offset in range(-5, 0)) / 5.0
        post_five_mean = sum(gaps[index + offset] / baseline for offset in range(1, 6)) / 5.0
        adjacent_mean = ((gaps[index - 1] / baseline) + (gaps[index + 1] / baseline)) / 2.0
        four_step_mean = ((gaps[index - 4] / baseline) + (gaps[index + 4] / baseline)) / 2.0
        rows.append(
            {
                "gap_start": primes[index],
                "gap_end": primes[index + 1],
                "record_gap": gaps[index],
                "ring_baseline": baseline,
                "pre_five_mean": pre_five_mean,
                "post_five_mean": post_five_mean,
                "adjacent_mean": adjacent_mean,
                "four_step_mean": four_step_mean,
                "four_step_to_adjacent_ratio": four_step_mean / adjacent_mean,
            }
        )
    return rows


def plot_profiles(
    control_profile: list[float],
    all_record_profile: list[float],
    late_record_profile: list[float],
    output_path: Path,
) -> None:
    """Render the normalized neighborhood comparison plot."""
    window_radius = (len(control_profile) - 1) // 2
    offsets = list(range(-window_radius, window_radius + 1))
    figure, axis = plt.subplots(figsize=(10.5, 6.0))
    axis.plot(
        offsets,
        control_profile,
        color="#1d4ed8",
        linewidth=1.8,
        alpha=0.85,
        label="All non-record windows",
    )
    axis.plot(
        offsets,
        all_record_profile,
        color="#c2410c",
        linewidth=2.2,
        marker="o",
        label="All record gaps",
    )
    axis.plot(
        offsets,
        late_record_profile,
        color="#047857",
        linewidth=2.4,
        marker="o",
        label="Late record gaps",
    )
    axis.axhline(1.0, color="#334155", linewidth=1.0, linestyle="--")
    axis.axvline(0, color="#7c2d12", linewidth=1.0, linestyle=":")
    axis.set_xlabel("Gap offset relative to the record gap")
    axis.set_ylabel("Gap size / surrounding-ring baseline")
    axis.set_title("Record-gap neighborhood profiles on an exact finite surface")
    axis.grid(alpha=0.18)
    axis.legend(frameon=False)
    figure.tight_layout()
    figure.savefig(output_path, dpi=170)


def main(argv: list[str] | None = None) -> int:
    """Run the probe and write the artifact set."""
    args = build_parser().parse_args(argv)
    if args.window_radius < 5:
        raise ValueError("window_radius must be at least 5")
    if args.ring_inner <= args.window_radius:
        raise ValueError("ring_inner must exceed window_radius")
    if args.ring_outer < args.ring_inner:
        raise ValueError("ring_outer must be at least ring_inner")

    args.output_dir.mkdir(parents=True, exist_ok=True)

    primes = list(primerange(2, args.max_n + 1))
    gaps = [right - left for left, right in zip(primes, primes[1:])]
    record_indices_all = record_gap_indices(gaps)
    eligible_record_indices = [
        index
        for index in record_indices_all
        if index >= args.ring_outer and index + args.ring_outer < len(gaps)
    ]
    late_record_indices = [
        index for index in eligible_record_indices if primes[index] >= args.late_cutoff
    ]
    record_index_set = set(record_indices_all)
    control_indices = [
        index
        for index in range(args.ring_outer, len(gaps) - args.ring_outer)
        if index not in record_index_set
    ]

    control_profile = neighborhood_profile(
        gaps,
        control_indices,
        args.window_radius,
        args.ring_inner,
        args.ring_outer,
    )
    all_record_profile = neighborhood_profile(
        gaps,
        eligible_record_indices,
        args.window_radius,
        args.ring_inner,
        args.ring_outer,
    )
    late_record_profile = neighborhood_profile(
        gaps,
        late_record_indices,
        args.window_radius,
        args.ring_inner,
        args.ring_outer,
    )

    summary = {
        "max_n": args.max_n,
        "prime_count": len(primes),
        "gap_count": len(gaps),
        "window_radius": args.window_radius,
        "ring_inner": args.ring_inner,
        "ring_outer": args.ring_outer,
        "late_cutoff": args.late_cutoff,
        "record_count_total": len(record_indices_all),
        "record_count_used": len(eligible_record_indices),
        "late_record_count_used": len(late_record_indices),
        "profiles": {
            "control": control_profile,
            "all_records": all_record_profile,
            "late_records": late_record_profile,
        },
        "profile_summary": {
            "control": profile_summary(control_profile, args.window_radius),
            "all_records": profile_summary(all_record_profile, args.window_radius),
            "late_records": profile_summary(late_record_profile, args.window_radius),
        },
        "late_record_events": event_rows(
            primes,
            gaps,
            late_record_indices,
            args.ring_inner,
            args.ring_outer,
        ),
    }

    summary_path = args.output_dir / "phase_locked_prime_resonance_summary.json"
    plot_path = args.output_dir / "phase_locked_prime_resonance_profile.png"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    plot_profiles(control_profile, all_record_profile, late_record_profile, plot_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
