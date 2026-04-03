#!/usr/bin/env python3
"""Validate the dominant d=4 arrival reduction behind GWR."""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path
from typing import Sequence

import gmpy2
import numpy as np


ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = ROOT / "src" / "python"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from z_band_prime_composite_field import divisor_counts_segment
from z_band_prime_gap_ridge.runs import build_even_window_starts


DEFAULT_OUTPUT_DIR = ROOT / "output"
DEFAULT_EXACT_LIMITS = (1_000_000, 20_000_000)
DEFAULT_SCALES = (
    100_000_000,
    1_000_000_000,
    10_000_000_000,
    100_000_000_000,
    1_000_000_000_000,
    10_000_000_000_000,
    100_000_000_000_000,
    1_000_000_000_000_000,
    10_000_000_000_000_000,
    100_000_000_000_000_000,
    1_000_000_000_000_000_000,
)
DEFAULT_WINDOW_SIZE = 2_000_000
DEFAULT_WINDOW_COUNT = 2
DEFAULT_MAX_EXAMPLES = 10


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description="Validate the dominant d=4 arrival reduction behind GWR.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for JSON and CSV artifacts.",
    )
    parser.add_argument(
        "--exact-limits",
        type=int,
        nargs="+",
        default=list(DEFAULT_EXACT_LIMITS),
        help="Exact natural-number limits for full-range scans.",
    )
    parser.add_argument(
        "--scales",
        type=int,
        nargs="+",
        default=list(DEFAULT_SCALES),
        help="Deterministic even-band scales to test.",
    )
    parser.add_argument(
        "--window-size",
        type=int,
        default=DEFAULT_WINDOW_SIZE,
        help="Window size for deterministic even-band sweeps.",
    )
    parser.add_argument(
        "--window-count",
        type=int,
        default=DEFAULT_WINDOW_COUNT,
        help="Number of even windows per scale.",
    )
    parser.add_argument(
        "--max-examples",
        type=int,
        default=DEFAULT_MAX_EXAMPLES,
        help="Maximum number of examples to retain per example bucket.",
    )
    return parser


def is_prime_cube(n: int) -> bool:
    """Return whether n is a prime cube."""
    root, exact = gmpy2.iroot(n, 3)
    return bool(exact and gmpy2.is_prime(root))


def _empty_row(
    scale: int,
    window_mode: str,
    lo: int,
    hi: int,
    window_size: int | None,
) -> dict[str, object]:
    """Create one mutable result row."""
    return {
        "scale": scale,
        "window_mode": window_mode,
        "lo": lo,
        "hi": hi,
        "window_size": window_size,
        "gap_count": 0,
        "winner_d3_count": 0,
        "winner_d4_count": 0,
        "d4_winner_gap_count": 0,
        "d4_winner_with_interior_square_count": 0,
        "d4_winner_equals_first_d4_count": 0,
        "d4_winner_semiprime_count": 0,
        "d4_winner_prime_cube_count": 0,
        "no_square_has_d4_gap_count": 0,
        "no_square_has_d4_first_d4_winner_count": 0,
        "max_gap": 0,
        "d4_winner_with_interior_square_examples": [],
        "no_square_has_d4_not_first_d4_examples": [],
        "d4_winner_prime_cube_examples": [],
        "interval_count": 0,
        "runtime_seconds": 0.0,
    }


def _append_example(
    bucket: object,
    example: dict[str, object],
    max_examples: int,
) -> None:
    """Append one example to a bounded list."""
    if not isinstance(bucket, list):
        raise RuntimeError("example bucket must remain a list")
    if len(bucket) < max_examples:
        bucket.append(example)


def _finalize_row(row: dict[str, object]) -> dict[str, object]:
    """Fill derived shares and rates."""
    gap_count = int(row["gap_count"])
    d4_winner_gap_count = int(row["d4_winner_gap_count"])
    no_square_has_d4_gap_count = int(row["no_square_has_d4_gap_count"])
    row["winner_d3_share"] = int(row["winner_d3_count"]) / gap_count
    row["winner_d4_share"] = int(row["winner_d4_count"]) / gap_count
    row["d4_winner_share"] = d4_winner_gap_count / gap_count
    row["d4_winner_with_interior_square_rate"] = (
        int(row["d4_winner_with_interior_square_count"]) / d4_winner_gap_count
        if d4_winner_gap_count > 0
        else None
    )
    row["d4_winner_equals_first_d4_rate"] = (
        int(row["d4_winner_equals_first_d4_count"]) / d4_winner_gap_count
        if d4_winner_gap_count > 0
        else None
    )
    row["d4_winner_semiprime_share"] = (
        int(row["d4_winner_semiprime_count"]) / d4_winner_gap_count
        if d4_winner_gap_count > 0
        else None
    )
    row["d4_winner_prime_cube_share"] = (
        int(row["d4_winner_prime_cube_count"]) / d4_winner_gap_count
        if d4_winner_gap_count > 0
        else None
    )
    row["no_square_has_d4_first_d4_winner_rate"] = (
        int(row["no_square_has_d4_first_d4_winner_count"]) / no_square_has_d4_gap_count
        if no_square_has_d4_gap_count > 0
        else None
    )
    return row


def validate_d4_arrival_on_interval(
    lo: int,
    hi: int,
    scale: int,
    window_mode: str,
    *,
    max_examples: int,
) -> dict[str, object]:
    """Validate the local d=4 arrival reduction on one exact interval."""
    started = time.perf_counter()
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

        row["gap_count"] = int(row["gap_count"]) + 1
        row["max_gap"] = max(int(row["max_gap"]), gap)
        row["winner_d3_count"] = int(row["winner_d3_count"]) + int(winner_d == 3)
        row["winner_d4_count"] = int(row["winner_d4_count"]) + int(winner_d == 4)

        d3_indices = np.flatnonzero(gap_divisors == 3)
        d4_indices = np.flatnonzero(gap_divisors == 4)
        has_interior_square = d3_indices.size > 0
        has_interior_d4 = d4_indices.size > 0
        first_d4_n = int(gap_values[int(d4_indices[0])]) if has_interior_d4 else None

        if (not has_interior_square) and has_interior_d4:
            row["no_square_has_d4_gap_count"] = int(row["no_square_has_d4_gap_count"]) + 1
            if winner_n == first_d4_n:
                row["no_square_has_d4_first_d4_winner_count"] = (
                    int(row["no_square_has_d4_first_d4_winner_count"]) + 1
                )
            else:
                _append_example(
                    row["no_square_has_d4_not_first_d4_examples"],
                    {
                        "left_prime": int(left_prime),
                        "right_prime": int(right_prime),
                        "gap": gap,
                        "winner_n": winner_n,
                        "winner_d": winner_d,
                        "first_d4_n": first_d4_n,
                        "first_d4_offset": int(first_d4_n - left_prime),
                        "winner_offset": int(winner_n - left_prime),
                    },
                    max_examples,
                )

        if winner_d != 4:
            continue

        row["d4_winner_gap_count"] = int(row["d4_winner_gap_count"]) + 1
        if has_interior_square:
            row["d4_winner_with_interior_square_count"] = (
                int(row["d4_winner_with_interior_square_count"]) + 1
            )
            first_square_n = int(gap_values[int(d3_indices[0])])
            _append_example(
                row["d4_winner_with_interior_square_examples"],
                {
                    "left_prime": int(left_prime),
                    "right_prime": int(right_prime),
                    "gap": gap,
                    "winner_n": winner_n,
                    "winner_offset": int(winner_n - left_prime),
                    "first_square_n": first_square_n,
                    "first_square_offset": int(first_square_n - left_prime),
                },
                max_examples,
            )

        if first_d4_n == winner_n:
            row["d4_winner_equals_first_d4_count"] = (
                int(row["d4_winner_equals_first_d4_count"]) + 1
            )

        if is_prime_cube(winner_n):
            row["d4_winner_prime_cube_count"] = int(row["d4_winner_prime_cube_count"]) + 1
            _append_example(
                row["d4_winner_prime_cube_examples"],
                {
                    "left_prime": int(left_prime),
                    "right_prime": int(right_prime),
                    "gap": gap,
                    "winner_n": winner_n,
                    "winner_offset": int(winner_n - left_prime),
                },
                max_examples,
            )
        else:
            row["d4_winner_semiprime_count"] = int(row["d4_winner_semiprime_count"]) + 1

    row["interval_count"] = 1
    row["runtime_seconds"] = time.perf_counter() - started
    return _finalize_row(row)


def aggregate_rows(
    rows: Sequence[dict[str, object]],
    *,
    scale: int,
    window_mode: str,
    window_size: int,
    max_examples: int,
) -> dict[str, object]:
    """Aggregate multiple interval rows for one even-band regime."""
    aggregate = _empty_row(
        scale=scale,
        window_mode=window_mode,
        lo=min(int(row["lo"]) for row in rows),
        hi=max(int(row["hi"]) for row in rows),
        window_size=window_size,
    )
    for row in rows:
        for key in (
            "gap_count",
            "winner_d3_count",
            "winner_d4_count",
            "d4_winner_gap_count",
            "d4_winner_with_interior_square_count",
            "d4_winner_equals_first_d4_count",
            "d4_winner_semiprime_count",
            "d4_winner_prime_cube_count",
            "no_square_has_d4_gap_count",
            "no_square_has_d4_first_d4_winner_count",
        ):
            aggregate[key] = int(aggregate[key]) + int(row[key])

        aggregate["max_gap"] = max(int(aggregate["max_gap"]), int(row["max_gap"]))
        aggregate["interval_count"] = int(aggregate["interval_count"]) + 1
        aggregate["runtime_seconds"] = float(aggregate["runtime_seconds"]) + float(
            row["runtime_seconds"]
        )

        for key in (
            "d4_winner_with_interior_square_examples",
            "no_square_has_d4_not_first_d4_examples",
            "d4_winner_prime_cube_examples",
        ):
            target = aggregate[key]
            source = row[key]
            if not isinstance(target, list) or not isinstance(source, list):
                raise RuntimeError("example buckets must remain lists")
            remaining = max_examples - len(target)
            if remaining > 0:
                target.extend(source[:remaining])

    return _finalize_row(aggregate)


def run_even_band_sweeps(
    *,
    scales: Sequence[int],
    window_size: int,
    window_count: int,
    max_examples: int,
) -> list[dict[str, object]]:
    """Run deterministic even-band sweeps."""
    rows: list[dict[str, object]] = []
    for scale in scales:
        starts = build_even_window_starts(scale, window_size, window_count)
        interval_rows = [
            validate_d4_arrival_on_interval(
                lo=start,
                hi=start + window_size,
                scale=scale,
                window_mode="even",
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
                max_examples=max_examples,
            )
        )
    return rows


def write_even_csv(output_path: Path, rows: Sequence[dict[str, object]]) -> None:
    """Write the deterministic even-band summary as CSV."""
    fieldnames = [
        "scale",
        "window_mode",
        "window_size",
        "interval_count",
        "gap_count",
        "winner_d3_count",
        "winner_d3_share",
        "winner_d4_count",
        "winner_d4_share",
        "d4_winner_gap_count",
        "d4_winner_with_interior_square_count",
        "d4_winner_with_interior_square_rate",
        "d4_winner_equals_first_d4_count",
        "d4_winner_equals_first_d4_rate",
        "d4_winner_semiprime_count",
        "d4_winner_semiprime_share",
        "d4_winner_prime_cube_count",
        "d4_winner_prime_cube_share",
        "no_square_has_d4_gap_count",
        "no_square_has_d4_first_d4_winner_count",
        "no_square_has_d4_first_d4_winner_rate",
        "max_gap",
        "runtime_seconds",
    ]
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name) for name in fieldnames})


def write_exact_csv(output_path: Path, rows: Sequence[dict[str, object]]) -> None:
    """Write the exact-surface summary as CSV."""
    fieldnames = [
        "scale",
        "window_mode",
        "window_size",
        "interval_count",
        "gap_count",
        "winner_d3_count",
        "winner_d3_share",
        "winner_d4_count",
        "winner_d4_share",
        "d4_winner_gap_count",
        "d4_winner_with_interior_square_count",
        "d4_winner_with_interior_square_rate",
        "d4_winner_equals_first_d4_count",
        "d4_winner_equals_first_d4_rate",
        "d4_winner_semiprime_count",
        "d4_winner_semiprime_share",
        "d4_winner_prime_cube_count",
        "d4_winner_prime_cube_share",
        "no_square_has_d4_gap_count",
        "no_square_has_d4_first_d4_winner_count",
        "no_square_has_d4_first_d4_winner_rate",
        "max_gap",
        "runtime_seconds",
    ]
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name) for name in fieldnames})


def main(argv: list[str] | None = None) -> int:
    """Run the dominant-case d=4 arrival validation and emit artifacts."""
    parser = build_parser()
    args = parser.parse_args(argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    exact_runs = [
        validate_d4_arrival_on_interval(
            lo=2,
            hi=exact_limit + 1,
            scale=exact_limit,
            window_mode="exact",
            max_examples=args.max_examples,
        )
        for exact_limit in args.exact_limits
    ]
    even = run_even_band_sweeps(
        scales=args.scales,
        window_size=args.window_size,
        window_count=args.window_count,
        max_examples=args.max_examples,
    )

    summary = {
        "parameters": {
            "exact_limits": list(args.exact_limits),
            "scales": list(args.scales),
            "window_size": args.window_size,
            "window_count": args.window_count,
            "max_examples": args.max_examples,
        },
        "exact_runs": exact_runs,
        "exact": exact_runs[0],
        "even_bands": even,
    }

    summary_path = args.output_dir / "gwr_d4_arrival_validation_summary.json"
    even_csv_path = args.output_dir / "gwr_d4_arrival_validation_even_bands.csv"
    exact_csv_path = args.output_dir / "gwr_d4_arrival_validation_exact.csv"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    write_even_csv(even_csv_path, even)
    write_exact_csv(exact_csv_path, exact_runs)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
