#!/usr/bin/env python3
"""Validate the GWR closure constraint on exact and sampled surfaces."""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
import time
from pathlib import Path
from typing import Sequence

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = ROOT / "src" / "python"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from z_band_prime_composite_field import divisor_counts_segment
from z_band_prime_gap_ridge.runs import build_even_window_starts, build_seeded_window_starts


DEFAULT_OUTPUT_DIR = ROOT / "output"
DEFAULT_EXACT_LIMIT = 1_000_000
DEFAULT_SAMPLED_SCALES = (
    100_000_000,
    1_000_000_000,
    10_000_000_000,
    100_000_000_000,
    1_000_000_000_000,
)
DEFAULT_WINDOW_SIZE = 2_000_000
DEFAULT_WINDOW_COUNT = 4
DEFAULT_SEEDS = (20260331, 20260401)
DEFAULT_MAX_EXAMPLES = 10
DEFAULT_PRIME_BUFFER = 100_000


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description="Validate the GWR closure constraint on exact and sampled surfaces.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for JSON and CSV artifacts.",
    )
    parser.add_argument(
        "--exact-limit",
        type=int,
        default=DEFAULT_EXACT_LIMIT,
        help="Exact natural-number limit for the full-range scan.",
    )
    parser.add_argument(
        "--sampled-scales",
        type=int,
        nargs="+",
        default=list(DEFAULT_SAMPLED_SCALES),
        help="Sampled scales for closure-constraint sweeps.",
    )
    parser.add_argument(
        "--window-size",
        type=int,
        default=DEFAULT_WINDOW_SIZE,
        help="Window size for sampled sweeps.",
    )
    parser.add_argument(
        "--window-count",
        type=int,
        default=DEFAULT_WINDOW_COUNT,
        help="Number of windows per sampled regime.",
    )
    parser.add_argument(
        "--seeds",
        type=int,
        nargs="+",
        default=list(DEFAULT_SEEDS),
        help="Seeds for sampled seeded-window regimes.",
    )
    parser.add_argument(
        "--max-examples",
        type=int,
        default=DEFAULT_MAX_EXAMPLES,
        help="Maximum number of example violations to retain.",
    )
    parser.add_argument(
        "--prime-buffer",
        type=int,
        default=DEFAULT_PRIME_BUFFER,
        help="Prime lookup buffer above sqrt(max scanned value) for d=4 threat summaries.",
    )
    return parser


def build_prime_lookup(lo: int, hi: int, prime_buffer: int) -> np.ndarray:
    """Build a local prime table for one interval's d=4 threat summaries."""
    root_lo = max(2, math.isqrt(max(lo, 2)) - 1)
    root_hi = math.isqrt(hi) + prime_buffer
    divisor_count = divisor_counts_segment(root_lo, root_hi + 1)
    values = np.arange(root_lo, root_hi + 1, dtype=np.int64)
    primes = values[divisor_count == 2]
    if primes.size == 0:
        raise RuntimeError("prime lookup construction failed")
    return primes


def _empty_row(
    scale: int,
    window_mode: str,
    lo: int,
    hi: int,
    window_size: int | None,
    seed: int | None,
) -> dict[str, object]:
    """Create one mutable aggregate row."""
    return {
        "scale": scale,
        "window_mode": window_mode,
        "lo": lo,
        "hi": hi,
        "window_size": window_size,
        "seed": seed,
        "gap_count": 0,
        "closure_pass_count": 0,
        "closure_violation_count": 0,
        "closure_match_rate": 0.0,
        "max_gap": 0,
        "winner_d3_count": 0,
        "winner_d4_count": 0,
        "d4_threat_count": 0,
        "d4_threat_distance_sum": 0,
        "d4_threat_distance_min": None,
        "d4_threat_distance_max": None,
        "d4_prime_arrival_margin_sum": 0,
        "d4_prime_arrival_margin_min": None,
        "d4_prime_arrival_margin_max": None,
        "violation_examples": [],
        "interval_count": 0,
        "runtime_seconds": 0.0,
    }


def _update_min_or_max(
    current: int | None,
    candidate: int,
    *,
    mode: str,
) -> int:
    """Update one integer min or max accumulator."""
    if current is None:
        return candidate
    if mode == "min":
        return min(current, candidate)
    if mode == "max":
        return max(current, candidate)
    raise RuntimeError(f"unsupported mode {mode}")


def _finalize_row(row: dict[str, object]) -> dict[str, object]:
    """Fill derived rates and means for one row."""
    gap_count = int(row["gap_count"])
    if gap_count == 0:
        raise RuntimeError("no prime gaps with composite interior were analyzed")

    row["closure_match_rate"] = int(row["closure_pass_count"]) / gap_count
    row["winner_d3_share"] = int(row["winner_d3_count"]) / gap_count
    row["winner_d4_share"] = int(row["winner_d4_count"]) / gap_count

    d4_threat_count = int(row["d4_threat_count"])
    if d4_threat_count > 0:
        row["d4_threat_distance_mean"] = int(row["d4_threat_distance_sum"]) / d4_threat_count
        row["d4_prime_arrival_margin_mean"] = (
            int(row["d4_prime_arrival_margin_sum"]) / d4_threat_count
        )
    else:
        row["d4_threat_distance_mean"] = None
        row["d4_prime_arrival_margin_mean"] = None
    return row


def _first_prime_square_after(n: int, prime_lookup: np.ndarray) -> int:
    """Return the first prime square strictly larger than n."""
    root_floor = math.isqrt(n)
    prime_index = int(np.searchsorted(prime_lookup, root_floor, side="right"))
    if prime_index >= prime_lookup.size:
        raise RuntimeError("prime lookup buffer too small for d=4 threat summary")
    prime_value = int(prime_lookup[prime_index])
    return prime_value * prime_value


def validate_closure_constraint_on_interval(
    lo: int,
    hi: int,
    scale: int,
    window_mode: str,
    *,
    prime_buffer: int,
    seed: int | None = None,
    max_examples: int = DEFAULT_MAX_EXAMPLES,
) -> dict[str, object]:
    """Check that no later interior composite is strictly simpler than the score winner."""
    started = time.perf_counter()
    prime_lookup = build_prime_lookup(lo=lo, hi=hi, prime_buffer=prime_buffer)
    divisor_count = divisor_counts_segment(lo, hi)
    values = np.arange(lo, hi, dtype=np.int64)
    primes = values[divisor_count == 2]
    log_values = np.log(values.astype(np.float64))

    row = _empty_row(
        scale=scale,
        window_mode=window_mode,
        lo=lo,
        hi=hi,
        window_size=hi - lo,
        seed=seed,
    )

    for left_prime, right_prime in zip(primes[:-1], primes[1:]):
        gap = int(right_prime - left_prime)
        if gap < 4:
            continue

        left_index = int(left_prime - lo + 1)
        right_index = int(right_prime - lo)
        gap_values = values[left_index:right_index]
        gap_divisors = divisor_count[left_index:right_index]
        scores = (
            (1.0 - gap_divisors.astype(np.float64) / 2.0)
            * log_values[left_index:right_index]
        )

        winner_index = int(np.argmax(scores))
        winner_n = int(gap_values[winner_index])
        winner_d = int(gap_divisors[winner_index])
        later_values = gap_values[winner_index + 1 :]
        later_divisors = gap_divisors[winner_index + 1 :]
        later_strictly_simpler = np.flatnonzero(later_divisors < winner_d)

        row["gap_count"] = int(row["gap_count"]) + 1
        row["max_gap"] = max(int(row["max_gap"]), gap)
        row["winner_d3_count"] = int(row["winner_d3_count"]) + int(winner_d == 3)
        row["winner_d4_count"] = int(row["winner_d4_count"]) + int(winner_d == 4)

        if winner_d == 4:
            threat_n = _first_prime_square_after(winner_n, prime_lookup)
            threat_distance = threat_n - winner_n
            prime_arrival_margin = threat_n - int(right_prime)
            row["d4_threat_count"] = int(row["d4_threat_count"]) + 1
            row["d4_threat_distance_sum"] = int(row["d4_threat_distance_sum"]) + threat_distance
            row["d4_threat_distance_min"] = _update_min_or_max(
                row["d4_threat_distance_min"],
                threat_distance,
                mode="min",
            )
            row["d4_threat_distance_max"] = _update_min_or_max(
                row["d4_threat_distance_max"],
                threat_distance,
                mode="max",
            )
            row["d4_prime_arrival_margin_sum"] = (
                int(row["d4_prime_arrival_margin_sum"]) + prime_arrival_margin
            )
            row["d4_prime_arrival_margin_min"] = _update_min_or_max(
                row["d4_prime_arrival_margin_min"],
                prime_arrival_margin,
                mode="min",
            )
            row["d4_prime_arrival_margin_max"] = _update_min_or_max(
                row["d4_prime_arrival_margin_max"],
                prime_arrival_margin,
                mode="max",
            )

        if later_strictly_simpler.size == 0:
            row["closure_pass_count"] = int(row["closure_pass_count"]) + 1
            continue

        threat_index = int(later_strictly_simpler[0])
        threat_n = int(later_values[threat_index])
        threat_d = int(later_divisors[threat_index])
        row["closure_violation_count"] = int(row["closure_violation_count"]) + 1

        examples = row["violation_examples"]
        if not isinstance(examples, list):
            raise RuntimeError("violation_examples must remain a list")
        if len(examples) < max_examples:
            examples.append(
                {
                    "left_prime": int(left_prime),
                    "right_prime": int(right_prime),
                    "gap": gap,
                    "winner_n": winner_n,
                    "winner_d": winner_d,
                    "first_later_strictly_simpler_n": threat_n,
                    "first_later_strictly_simpler_d": threat_d,
                    "winner_offset": int(winner_n - left_prime),
                    "threat_offset": int(threat_n - left_prime),
                }
            )

    row["interval_count"] = 1
    row["runtime_seconds"] = time.perf_counter() - started
    return _finalize_row(row)


def aggregate_rows(
    rows: Sequence[dict[str, object]],
    *,
    scale: int,
    window_mode: str,
    window_size: int,
    seed: int | None,
    max_examples: int,
) -> dict[str, object]:
    """Aggregate multiple interval rows for one sampled regime."""
    aggregate = _empty_row(
        scale=scale,
        window_mode=window_mode,
        lo=min(int(row["lo"]) for row in rows),
        hi=max(int(row["hi"]) for row in rows),
        window_size=window_size,
        seed=seed,
    )
    for row in rows:
        for key in (
            "gap_count",
            "closure_pass_count",
            "closure_violation_count",
            "winner_d3_count",
            "winner_d4_count",
            "d4_threat_count",
            "d4_threat_distance_sum",
            "d4_prime_arrival_margin_sum",
        ):
            aggregate[key] = int(aggregate[key]) + int(row[key])
        aggregate["max_gap"] = max(int(aggregate["max_gap"]), int(row["max_gap"]))
        aggregate["interval_count"] = int(aggregate["interval_count"]) + 1
        aggregate["runtime_seconds"] = float(aggregate["runtime_seconds"]) + float(
            row["runtime_seconds"]
        )

        for min_key, max_key in (
            ("d4_threat_distance_min", "d4_threat_distance_max"),
            ("d4_prime_arrival_margin_min", "d4_prime_arrival_margin_max"),
        ):
            current_min = aggregate[min_key]
            current_max = aggregate[max_key]
            candidate_min = row[min_key]
            candidate_max = row[max_key]
            if candidate_min is not None:
                aggregate[min_key] = _update_min_or_max(
                    current_min,
                    int(candidate_min),
                    mode="min",
                )
            if candidate_max is not None:
                aggregate[max_key] = _update_min_or_max(
                    current_max,
                    int(candidate_max),
                    mode="max",
                )

        examples = aggregate["violation_examples"]
        if not isinstance(examples, list):
            raise RuntimeError("aggregate violation_examples must remain a list")
        source_examples = row["violation_examples"]
        if not isinstance(source_examples, list):
            raise RuntimeError("row violation_examples must remain a list")
        remaining = max_examples - len(examples)
        if remaining > 0:
            examples.extend(source_examples[:remaining])

    return _finalize_row(aggregate)


def run_sampled_sweeps(
    *,
    scales: Sequence[int],
    window_size: int,
    window_count: int,
    seeds: Sequence[int],
    prime_buffer: int,
    max_examples: int,
) -> list[dict[str, object]]:
    """Run even and seeded sampled closure-constraint sweeps."""
    rows: list[dict[str, object]] = []

    for scale in scales:
        starts = build_even_window_starts(scale, window_size, window_count)
        interval_rows = [
            validate_closure_constraint_on_interval(
                lo=start,
                    hi=start + window_size,
                    scale=scale,
                    window_mode="even",
                    prime_buffer=prime_buffer,
                    max_examples=max_examples,
                )
            for start in starts
        ]
        rows.append(
            aggregate_rows(
                interval_rows,
                scale=scale,
                window_mode="even",
                window_size=window_size,
                seed=None,
                max_examples=max_examples,
            )
        )

    for seed in seeds:
        for scale in scales:
            starts = build_seeded_window_starts(scale, window_size, window_count, seed)
            interval_rows = [
                validate_closure_constraint_on_interval(
                    lo=start,
                    hi=start + window_size,
                    scale=scale,
                    window_mode="seeded",
                    seed=seed,
                    prime_buffer=prime_buffer,
                    max_examples=max_examples,
                )
                for start in starts
            ]
            rows.append(
                aggregate_rows(
                    interval_rows,
                    scale=scale,
                    window_mode="seeded",
                    window_size=window_size,
                    seed=seed,
                    max_examples=max_examples,
                )
            )

    return rows


def write_sampled_csv(output_path: Path, rows: Sequence[dict[str, object]]) -> None:
    """Write the sampled sweep summary as CSV."""
    fieldnames = [
        "scale",
        "window_mode",
        "seed",
        "window_size",
        "interval_count",
        "gap_count",
        "closure_violation_count",
        "closure_match_rate",
        "max_gap",
        "winner_d3_count",
        "winner_d4_count",
        "winner_d4_share",
        "d4_threat_count",
        "d4_threat_distance_min",
        "d4_threat_distance_mean",
        "d4_threat_distance_max",
        "d4_prime_arrival_margin_min",
        "d4_prime_arrival_margin_mean",
        "d4_prime_arrival_margin_max",
        "runtime_seconds",
    ]
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name) for name in fieldnames})


def main(argv: list[str] | None = None) -> int:
    """Run the exact and sampled closure-constraint scans and emit artifacts."""
    parser = build_parser()
    args = parser.parse_args(argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    exact = validate_closure_constraint_on_interval(
        lo=2,
        hi=args.exact_limit + 1,
        scale=args.exact_limit,
        window_mode="exact",
        prime_buffer=args.prime_buffer,
        max_examples=args.max_examples,
    )
    sampled = run_sampled_sweeps(
        scales=args.sampled_scales,
        window_size=args.window_size,
        window_count=args.window_count,
        seeds=args.seeds,
        prime_buffer=args.prime_buffer,
        max_examples=args.max_examples,
    )

    summary = {
        "parameters": {
            "exact_limit": args.exact_limit,
            "sampled_scales": list(args.sampled_scales),
            "window_size": args.window_size,
            "window_count": args.window_count,
            "seeds": list(args.seeds),
            "prime_buffer": args.prime_buffer,
            "max_examples": args.max_examples,
        },
        "exact": exact,
        "sampled": sampled,
    }

    summary_path = args.output_dir / "gwr_closure_constraint_summary.json"
    sampled_csv_path = args.output_dir / "gwr_closure_constraint_sampled.csv"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    write_sampled_csv(sampled_csv_path, sampled)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
