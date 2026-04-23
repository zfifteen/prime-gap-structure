#!/usr/bin/env python3
"""Probe the square-phase handoff structure of exact next-gap winners.

This probe measures one narrow question on the exact consecutive next-gap
surface:

- when a prime square enters the gap interior, does the winner offset lock to
  that square's offset;
- when no interior prime square is present, how often does the gap fall into
  the early d=4 regime and what carrier family wins there.

The script writes one compact JSON summary plus one figure. It does not create
alternate scan modes or heuristic fallbacks.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
from sympy import primerange

ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = ROOT / "src" / "python"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from z_band_prime_composite_field import divisor_counts_segment
from z_band_prime_predictor.gwr_boundary_walk import gwr_next_gap_profile
from z_band_prime_predictor.semiprime_factor_walk import carrier_family

DEFAULT_MAX_PRIME = 1_000_000
DEFAULT_OUTPUT_DIR = ROOT / "output"


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description="Probe the square-phase handoff structure on exact next-gap winners.",
    )
    parser.add_argument(
        "--max-prime",
        type=int,
        default=DEFAULT_MAX_PRIME,
        help="Scan every consecutive prime gap whose left prime q satisfies q <= max-prime.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for the summary JSON and figure.",
    )
    return parser


def quantiles(values: list[int]) -> dict[str, int | None]:
    """Return fixed summary quantiles for one integer sample."""
    if not values:
        return {
            "count": 0,
            "min": None,
            "median": None,
            "p90": None,
            "p99": None,
            "max": None,
        }

    ordered = sorted(values)

    def pick(fraction: float) -> int:
        index = int((len(ordered) - 1) * fraction)
        return int(ordered[index])

    return {
        "count": len(ordered),
        "min": int(ordered[0]),
        "median": pick(0.50),
        "p90": pick(0.90),
        "p99": pick(0.99),
        "max": int(ordered[-1]),
    }


def first_interior_prime_square_offset(left_prime: int, right_prime: int) -> int | None:
    """Return the offset of the first interior prime square, if one exists."""
    root_lo = math.isqrt(left_prime) + 1
    root_hi = math.isqrt(right_prime - 1)
    if root_hi < root_lo:
        return None

    for prime_root in primerange(root_lo, root_hi + 1):
        square = int(prime_root) * int(prime_root)
        if left_prime < square < right_prime:
            return square - left_prime
    return None


def winner_family(winner: int, winner_d: int) -> str:
    """Return the coarse carrier family for one winner."""
    exact_d = int(divisor_counts_segment(winner, winner + 1)[0])
    if exact_d != winner_d:
        raise AssertionError(f"winner_d mismatch at n={winner}: expected {winner_d}, got {exact_d}")
    return carrier_family(winner, exact_d)


def create_figure(
    plot_path: Path,
    *,
    d4_offsets: list[int],
    square_rows: list[dict[str, int]],
) -> None:
    """Render the handoff-offset figure."""
    square_offsets = [int(row["square_offset"]) for row in square_rows]
    if not d4_offsets:
        raise ValueError("d4_offsets must be non-empty")
    if not square_offsets:
        raise ValueError("square_rows must be non-empty")

    max_offset = max(max(d4_offsets), max(square_offsets))
    bins = list(range(1, max_offset + 2))

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

    axes[0].hist(
        d4_offsets,
        bins=bins,
        alpha=0.75,
        color="#0b6e4f",
        edgecolor="white",
        label="square-free d=4 winners",
    )
    axes[0].hist(
        square_offsets,
        bins=bins,
        alpha=0.75,
        color="#b63a2b",
        edgecolor="white",
        label="square-present gaps",
    )
    axes[0].set_xlabel("winner offset")
    axes[0].set_ylabel("gap count")
    axes[0].set_title("Winner-offset split")
    axes[0].legend(frameon=False)

    axes[1].scatter(
        square_offsets,
        [int(row["winner_offset"]) for row in square_rows],
        s=20,
        color="#b63a2b",
    )
    axes[1].plot([0, max_offset], [0, max_offset], color="#222222", linewidth=1)
    axes[1].set_xlim(0, max_offset + 1)
    axes[1].set_ylim(0, max_offset + 1)
    axes[1].set_xlabel("first interior prime-square offset")
    axes[1].set_ylabel("winner offset")
    axes[1].set_title("Square branch locking")

    fig.tight_layout()
    fig.savefig(plot_path, dpi=180)
    plt.close(fig)


def probe(max_prime: int) -> tuple[dict[str, object], list[int], list[dict[str, int]]]:
    """Return the handoff summary, square-free d=4 offsets, and square rows."""
    if max_prime < 2:
        raise ValueError("max_prime must be at least 2")

    total_gap_count = 0
    winner_d_counts: Counter[int] = Counter()
    square_free_non_d4_counts: Counter[int] = Counter()
    square_free_d4_family_counts: Counter[str] = Counter()
    square_free_d4_offsets: list[int] = []
    square_rows: list[dict[str, int]] = []
    all_winner_offsets: list[int] = []

    q = 2
    while q <= max_prime:
        profile = gwr_next_gap_profile(q)
        next_prime = int(profile["next_prime"])
        winner_d_raw = profile["winner_d"]
        winner_offset_raw = profile["winner_offset"]
        q = next_prime

        if winner_d_raw is None or winner_offset_raw is None:
            continue

        total_gap_count += 1
        winner_d = int(winner_d_raw)
        winner_offset = int(winner_offset_raw)
        winner = int(profile["current_prime"]) + winner_offset
        winner_d_counts[winner_d] += 1
        all_winner_offsets.append(winner_offset)

        square_offset = first_interior_prime_square_offset(int(profile["current_prime"]), next_prime)
        if square_offset is not None:
            square_rows.append(
                {
                    "left_prime": int(profile["current_prime"]),
                    "right_prime": next_prime,
                    "gap_width": int(profile["gap_boundary_offset"]),
                    "winner_d": winner_d,
                    "winner_offset": winner_offset,
                    "square_offset": square_offset,
                    "closure_after_square": int(profile["gap_boundary_offset"]) - square_offset,
                }
            )
            continue

        if winner_d == 4:
            square_free_d4_offsets.append(winner_offset)
            square_free_d4_family_counts[winner_family(winner, winner_d)] += 1
        else:
            square_free_non_d4_counts[winner_d] += 1

    if not square_rows:
        raise RuntimeError("probe produced no square-present gaps")
    if not square_free_d4_offsets:
        raise RuntimeError("probe produced no square-free d=4 gaps")

    exact_square_lock_count = sum(
        int(row["winner_d"] == 3 and row["winner_offset"] == row["square_offset"])
        for row in square_rows
    )
    if exact_square_lock_count != len(square_rows):
        raise RuntimeError("square branch did not lock exactly on the scanned surface")

    square_free_count = total_gap_count - len(square_rows)
    largest_square_rows = sorted(square_rows, key=lambda row: row["square_offset"], reverse=True)[:10]

    summary: dict[str, object] = {
        "max_prime": int(max_prime),
        "total_gap_count": total_gap_count,
        "winner_d_counts": {str(d): int(count) for d, count in sorted(winner_d_counts.items())},
        "all_winner_offset_quantiles": quantiles(all_winner_offsets),
        "square_present": {
            "gap_count": len(square_rows),
            "gap_share": len(square_rows) / total_gap_count,
            "exact_square_lock_count": exact_square_lock_count,
            "exact_square_lock_share": exact_square_lock_count / len(square_rows),
            "winner_offset_quantiles": quantiles([int(row["winner_offset"]) for row in square_rows]),
            "closure_after_square_quantiles": quantiles(
                [int(row["closure_after_square"]) for row in square_rows]
            ),
            "largest_rows": largest_square_rows,
        },
        "square_free": {
            "gap_count": square_free_count,
            "gap_share": square_free_count / total_gap_count,
            "d4_gap_count": len(square_free_d4_offsets),
            "d4_gap_share_within_square_free": len(square_free_d4_offsets) / square_free_count,
            "d4_winner_offset_quantiles": quantiles(square_free_d4_offsets),
            "d4_family_counts": {
                family: int(square_free_d4_family_counts[family])
                for family in sorted(square_free_d4_family_counts)
            },
            "non_d4_counts": {str(d): int(count) for d, count in sorted(square_free_non_d4_counts.items())},
        },
    }
    return summary, square_free_d4_offsets, square_rows


def main() -> int:
    """Run the handoff probe and write artifacts."""
    args = build_parser().parse_args()
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    summary, square_free_d4_offsets, square_rows = probe(args.max_prime)

    summary_path = output_dir / "gwr_square_phase_handoff_threshold_summary.json"
    plot_path = output_dir / "gwr_square_phase_handoff_threshold_offsets.png"

    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    create_figure(plot_path, d4_offsets=square_free_d4_offsets, square_rows=square_rows)

    print(
        "gwr-square-phase-handoff-threshold:"
        f" gaps={summary['total_gap_count']}"
        f" square_present={summary['square_present']['gap_count']}"
        f" square_free_d4={summary['square_free']['d4_gap_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
