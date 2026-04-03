#!/usr/bin/env python3
"""Validate the lexicographic raw-Z peak rule on tested prime-gap regimes."""

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
SCRIPT_DIR = Path(__file__).resolve().parent
for entry in (SOURCE_DIR, SCRIPT_DIR):
    if str(entry) not in sys.path:
        sys.path.insert(0, str(entry))

from geodesic_prime_composite_field import divisor_counts_segment
from raw_z_gap_edge_runs import build_even_window_starts


DEFAULT_OUTPUT_DIR = Path("benchmarks/output/python/gap_ridge/lexicographic_peak_validation")
DEFAULT_FULL_LIMITS = (1_000_000, 10_000_000)
DEFAULT_WINDOW_SCALES = (100_000_000, 1_000_000_000, 10_000_000_000)
DEFAULT_WINDOW_SIZE = 2_000_000
DEFAULT_WINDOW_COUNT = 4


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description="Validate the lexicographic raw-Z peak rule on tested prime-gap regimes.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for JSON and SVG artifacts.",
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
        help="Number of windows per sampled scale.",
    )
    return parser


def analyze_interval(lo: int, hi: int) -> dict[str, object]:
    """Analyze one exact interval for counterexamples to the lexicographic rule."""
    divisor_count = divisor_counts_segment(lo, hi)
    values = np.arange(lo, hi, dtype=np.int64)
    primes = values[divisor_count == 2]
    log_values = np.log(values.astype(np.float64))

    gap_count = 0
    counterexample_count = 0
    min_margin: float | None = None
    min_margin_gap: dict[str, int | float] | None = None
    max_gap = 0
    examples: list[dict[str, int | float]] = []

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
        best_n = int(gap_values[best_index])
        best_d = int(gap_divisors[best_index])
        best_score = float(scores[best_index])

        min_d = int(np.min(gap_divisors))
        lex_index = int(np.flatnonzero(gap_divisors == min_d)[0])
        lex_n = int(gap_values[lex_index])
        lex_d = int(gap_divisors[lex_index])
        lex_score = float(scores[lex_index])

        gap_count += 1
        max_gap = max(max_gap, gap)

        positive_scores = np.sort(scores)[::-1]
        if positive_scores.size >= 2:
            margin = float(positive_scores[0] - positive_scores[1])
        else:
            margin = 0.0
        if min_margin is None or margin < min_margin:
            min_margin = margin
            min_margin_gap = {
                "left_prime": int(left_prime),
                "right_prime": int(right_prime),
                "gap": gap,
                "best_n": best_n,
                "best_d": best_d,
                "lex_n": lex_n,
                "lex_d": lex_d,
                "log_score_margin": margin,
            }

        if best_index != lex_index:
            counterexample_count += 1
            if len(examples) < 20:
                examples.append(
                    {
                        "left_prime": int(left_prime),
                        "right_prime": int(right_prime),
                        "gap": gap,
                        "best_n": best_n,
                        "best_d": best_d,
                        "lex_n": lex_n,
                        "lex_d": lex_d,
                        "best_log_score": best_score,
                        "lex_log_score": lex_score,
                    }
                )

    if min_margin is None or min_margin_gap is None:
        raise RuntimeError("no prime gaps with interior composites were analyzed")

    return {
        "gap_count": gap_count,
        "counterexample_count": counterexample_count,
        "match_count": gap_count - counterexample_count,
        "match_rate": (gap_count - counterexample_count) / gap_count,
        "counterexample_rate": counterexample_count / gap_count,
        "max_gap": max_gap,
        "min_log_score_margin": min_margin,
        "min_margin_gap": min_margin_gap,
        "counterexample_examples": examples,
    }


def render_summary(rows: list[dict[str, object]], output_path: Path) -> None:
    """Render the match-rate summary plot across tested regimes."""
    scales = [int(row["scale"]) for row in rows]
    match_rates = [float(row["match_rate"]) for row in rows]
    gaps = [int(row["gap_count"]) for row in rows]

    fig, ax = plt.subplots(figsize=(9.2, 5.0))
    ax.plot(scales, match_rates, marker="o", linewidth=2.5, color="#1f4e79")
    ax.set_xscale("log")
    ax.set_ylim(0.95, 1.005)
    ax.set_title(
        "Lexicographic winner-take-all rule versus exact raw-Z peak",
        pad=14,
    )
    ax.set_xlabel("Scale")
    ax.set_ylabel("Match rate")
    ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value * 100.0:.1f}%"))
    ax.xaxis.set_major_formatter(
        FuncFormatter(lambda value, _: rf"$10^{{{int(np.log10(value))}}}$")
    )
    ax.grid(True, alpha=0.25)
    for scale, rate, gap_count in zip(scales, match_rates, gaps):
        ax.annotate(
            f"{gap_count:,} gaps",
            (scale, rate),
            textcoords="offset points",
            xytext=(0, 8),
            ha="center",
            fontsize=9,
            color="#243b53",
        )
    fig.tight_layout()
    fig.savefig(output_path, format="svg")
    plt.close(fig)


def main(argv: list[str] | None = None) -> int:
    """Run the lexicographic peak validation campaign."""
    args = build_parser().parse_args(argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, object]] = []
    for limit in args.full_limits:
        result = analyze_interval(2, limit + 1)
        result["scale"] = limit
        result["mode"] = "exact"
        rows.append(result)

    for scale in args.window_scales:
        starts = build_even_window_starts(scale, args.window_size, args.window_count)
        parts = [analyze_interval(start, start + args.window_size) for start in starts]
        total_gaps = sum(int(part["gap_count"]) for part in parts)
        total_counterexamples = sum(int(part["counterexample_count"]) for part in parts)
        min_margin_part = min(parts, key=lambda part: float(part["min_log_score_margin"]))
        rows.append(
            {
                "scale": scale,
                "mode": "even-window",
                "window_size": args.window_size,
                "window_count": args.window_count,
                "gap_count": total_gaps,
                "counterexample_count": total_counterexamples,
                "match_count": total_gaps - total_counterexamples,
                "match_rate": (total_gaps - total_counterexamples) / total_gaps,
                "counterexample_rate": total_counterexamples / total_gaps,
                "max_gap": max(int(part["max_gap"]) for part in parts),
                "min_log_score_margin": float(min_margin_part["min_log_score_margin"]),
                "min_margin_gap": min_margin_part["min_margin_gap"],
                "counterexample_examples": [],
            }
        )

    rows.sort(key=lambda row: int(row["scale"]))
    validation_status = (
        "validated_on_tested_surface"
        if all(int(row["counterexample_count"]) == 0 for row in rows)
        else "falsified_on_tested_surface"
    )

    payload = {
        "decision_rule": (
            "validated on the tested surface if and only if every tested regime "
            "contains zero counterexample gaps where the exact raw-Z peak differs "
            "from the lexicographic winner: smallest d(n), then leftmost"
        ),
        "validation_status": validation_status,
        "rows": rows,
    }

    render_summary(rows, args.output_dir / "lexicographic_peak_validation_summary.svg")
    (args.output_dir / "lexicographic_peak_validation.json").write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
