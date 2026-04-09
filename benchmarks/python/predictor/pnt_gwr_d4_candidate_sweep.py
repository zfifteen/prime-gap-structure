#!/usr/bin/env python3
"""Sweep the current PNT-seeded dominant d=4 candidate surface."""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path

from sympy import prime, primepi, prevprime


ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = ROOT / "src" / "python"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from z_band_prime_predictor import (
    d4_gap_profile,
    pnt_gwr_d4_candidate,
)

DEFAULT_OUTPUT_DIR = ROOT / "output"
DEFAULT_N_START = 10
DEFAULT_N_END = 1000


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description="Sweep the current PNT-seeded dominant d=4 candidate surface.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for JSON and CSV artifacts.",
    )
    parser.add_argument(
        "--n-start",
        type=int,
        default=DEFAULT_N_START,
        help="First prime index to include.",
    )
    parser.add_argument(
        "--n-end",
        type=int,
        default=DEFAULT_N_END,
        help="Last prime index to include.",
    )
    return parser


def analyze_index(n: int) -> dict[str, object]:
    """Analyze one index on the current dominant-regime candidate path."""
    if n < 2:
        raise ValueError("n must be at least 2")

    actual_prime = int(prime(n))
    left_prime = int(prevprime(actual_prime))
    candidate_prime, witness, seed = pnt_gwr_d4_candidate(n)
    rank_offset = int(primepi(candidate_prime) - n)
    prime_offset = int(candidate_prime - actual_prime)
    gap_profile = d4_gap_profile(left_prime, actual_prime)
    gap_has_d4 = bool(gap_profile["gap_has_d4"])
    last_pre_gap_d4 = gap_profile["last_pre_gap_d4"]
    first_in_gap_d4 = gap_profile["first_in_gap_d4"]
    last_in_gap_d4 = gap_profile["last_in_gap_d4"]
    seed_in_d4_corridor = bool(
        last_in_gap_d4 is not None
        and (last_pre_gap_d4 is None or seed > last_pre_gap_d4)
        and seed <= last_in_gap_d4
    )
    witness_in_target_gap = left_prime < witness < actual_prime
    seed_in_target_gap = left_prime < seed < actual_prime
    blocked_by_pre_gap_d4 = bool(
        gap_has_d4 and last_pre_gap_d4 is not None and seed <= last_pre_gap_d4
    )
    past_last_gap_d4 = bool(
        gap_has_d4 and last_in_gap_d4 is not None and seed > last_in_gap_d4
    )
    gap_lacks_d4 = not gap_has_d4
    seed_corridor_left_deficit = (
        max(0, int(last_pre_gap_d4) + 1 - seed) if last_pre_gap_d4 is not None else 0
    )
    corridor_width = (
        int(last_in_gap_d4) - int(last_pre_gap_d4)
        if last_pre_gap_d4 is not None and last_in_gap_d4 is not None
        else None
    )

    return {
        "n": n,
        "left_prime": left_prime,
        "actual_prime": actual_prime,
        "candidate_prime": int(candidate_prime),
        "seed": int(seed),
        "witness": int(witness),
        "prime_offset": prime_offset,
        "abs_prime_offset": abs(prime_offset),
        "rank_offset": rank_offset,
        "abs_rank_offset": abs(rank_offset),
        "exact_hit": candidate_prime == actual_prime,
        "seed_in_target_gap": seed_in_target_gap,
        "gap_has_d4": gap_has_d4,
        "last_pre_gap_d4": last_pre_gap_d4,
        "first_in_gap_d4": first_in_gap_d4,
        "last_in_gap_d4": last_in_gap_d4,
        "seed_in_d4_corridor": seed_in_d4_corridor,
        "blocked_by_pre_gap_d4": blocked_by_pre_gap_d4,
        "past_last_gap_d4": past_last_gap_d4,
        "gap_lacks_d4": gap_lacks_d4,
        "seed_corridor_left_deficit": seed_corridor_left_deficit,
        "corridor_width": corridor_width,
        "witness_in_target_gap": witness_in_target_gap,
    }


def summarize_rows(rows: list[dict[str, object]]) -> dict[str, object]:
    """Aggregate one deterministic sweep surface."""
    if not rows:
        raise ValueError("rows must not be empty")

    count = len(rows)
    exact_hit_count = sum(int(row["exact_hit"]) for row in rows)
    seed_in_target_gap_count = sum(int(row["seed_in_target_gap"]) for row in rows)
    gap_has_d4_count = sum(int(row["gap_has_d4"]) for row in rows)
    seed_in_d4_corridor_count = sum(int(row["seed_in_d4_corridor"]) for row in rows)
    blocked_by_pre_gap_d4_count = sum(int(row["blocked_by_pre_gap_d4"]) for row in rows)
    past_last_gap_d4_count = sum(int(row["past_last_gap_d4"]) for row in rows)
    gap_lacks_d4_count = sum(int(row["gap_lacks_d4"]) for row in rows)
    witness_in_target_gap_count = sum(int(row["witness_in_target_gap"]) for row in rows)
    prime_offset_sum = sum(int(row["prime_offset"]) for row in rows)
    abs_prime_offset_sum = sum(int(row["abs_prime_offset"]) for row in rows)
    abs_rank_offset_sum = sum(int(row["abs_rank_offset"]) for row in rows)
    seed_corridor_left_deficit_sum = sum(int(row["seed_corridor_left_deficit"]) for row in rows)
    corridor_width_values = [
        int(row["corridor_width"]) for row in rows if row["corridor_width"] is not None
    ]

    return {
        "n_start": int(rows[0]["n"]),
        "n_end": int(rows[-1]["n"]),
        "count": count,
        "exact_hit_count": exact_hit_count,
        "exact_hit_rate": exact_hit_count / count,
        "seed_in_target_gap_count": seed_in_target_gap_count,
        "seed_in_target_gap_rate": seed_in_target_gap_count / count,
        "gap_has_d4_count": gap_has_d4_count,
        "gap_has_d4_rate": gap_has_d4_count / count,
        "seed_in_d4_corridor_count": seed_in_d4_corridor_count,
        "seed_in_d4_corridor_rate": seed_in_d4_corridor_count / count,
        "blocked_by_pre_gap_d4_count": blocked_by_pre_gap_d4_count,
        "blocked_by_pre_gap_d4_rate": blocked_by_pre_gap_d4_count / count,
        "past_last_gap_d4_count": past_last_gap_d4_count,
        "past_last_gap_d4_rate": past_last_gap_d4_count / count,
        "gap_lacks_d4_count": gap_lacks_d4_count,
        "gap_lacks_d4_rate": gap_lacks_d4_count / count,
        "witness_in_target_gap_count": witness_in_target_gap_count,
        "witness_in_target_gap_rate": witness_in_target_gap_count / count,
        "mean_seed_corridor_left_deficit": seed_corridor_left_deficit_sum / count,
        "mean_corridor_width": (
            sum(corridor_width_values) / len(corridor_width_values)
            if corridor_width_values
            else None
        ),
        "max_corridor_width": max(corridor_width_values) if corridor_width_values else None,
        "mean_prime_offset": prime_offset_sum / count,
        "mean_abs_prime_offset": abs_prime_offset_sum / count,
        "max_abs_prime_offset": max(int(row["abs_prime_offset"]) for row in rows),
        "mean_abs_rank_offset": abs_rank_offset_sum / count,
        "max_abs_rank_offset": max(int(row["abs_rank_offset"]) for row in rows),
        "exact_hits_equal_witness_hits": exact_hit_count == witness_in_target_gap_count,
        "exact_hits_equal_corridor_hits": exact_hit_count == seed_in_d4_corridor_count,
    }


def run_sweep(n_start: int, n_end: int) -> tuple[list[dict[str, object]], dict[str, object]]:
    """Run the deterministic sweep and return detail rows plus summary."""
    if n_start < 2:
        raise ValueError("n_start must be at least 2")
    if n_end < n_start:
        raise ValueError("n_end must be at least n_start")

    rows = [analyze_index(n) for n in range(n_start, n_end + 1)]
    return rows, summarize_rows(rows)


def main(argv: list[str] | None = None) -> int:
    """Run the sweep and write JSON and CSV artifacts."""
    args = build_parser().parse_args(argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    started = time.perf_counter()
    rows, summary = run_sweep(args.n_start, args.n_end)
    summary["runtime_seconds"] = time.perf_counter() - started

    summary_path = args.output_dir / "pnt_gwr_d4_candidate_sweep_summary.json"
    detail_path = args.output_dir / "pnt_gwr_d4_candidate_sweep_details.csv"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    fieldnames = [
        "n",
        "left_prime",
        "actual_prime",
        "candidate_prime",
        "seed",
        "witness",
        "prime_offset",
        "abs_prime_offset",
        "rank_offset",
        "abs_rank_offset",
        "exact_hit",
        "seed_in_target_gap",
        "gap_has_d4",
        "last_pre_gap_d4",
        "first_in_gap_d4",
        "last_in_gap_d4",
        "seed_in_d4_corridor",
        "blocked_by_pre_gap_d4",
        "past_last_gap_d4",
        "gap_lacks_d4",
        "seed_corridor_left_deficit",
        "corridor_width",
        "witness_in_target_gap",
    ]
    with detail_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
