#!/usr/bin/env python3
"""Scan the non-floor d=4 square-threat closure frontier exactly."""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
import time
from pathlib import Path

import gmpy2
import numpy as np
from sympy import factorint


ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = ROOT / "src" / "python"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from z_band_prime_composite_field import divisor_counts_segment


DEFAULT_OUTPUT_DIR = ROOT / "output"
DEFAULT_MAX_N = 1_000_000_000
DEFAULT_CHUNK_SIZE = 2_000_000
DEFAULT_BUFFER = 10_000
DEFAULT_FRONTIER_SIZE = 50
DEFAULT_PRIME_BUFFER = 100_000
CSV_FIELDS = [
    "p",
    "w",
    "q",
    "r",
    "S_plus_w",
    "margin",
    "gap_size",
    "winner_offset",
    "q_offset",
    "closure_utilization",
    "log_score_w",
    "r2_minus_2",
    "r2_minus_2_factors",
]


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description="Scan the non-floor d=4 square-threat closure frontier exactly.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for JSON and CSV artifacts.",
    )
    parser.add_argument(
        "--max-n",
        type=int,
        default=DEFAULT_MAX_N,
        help="Exact natural-number ceiling for the segmented scan.",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=DEFAULT_CHUNK_SIZE,
        help="Segment size for the exact scan.",
    )
    parser.add_argument(
        "--buffer",
        type=int,
        default=DEFAULT_BUFFER,
        help="Right overlap buffer used to finish gaps crossing one chunk edge.",
    )
    parser.add_argument(
        "--frontier-size",
        type=int,
        default=DEFAULT_FRONTIER_SIZE,
        help="Number of smallest non-floor rows to retain.",
    )
    parser.add_argument(
        "--prime-buffer",
        type=int,
        default=DEFAULT_PRIME_BUFFER,
        help="Prime lookup buffer above sqrt(max scanned value).",
    )
    return parser


def build_prime_lookup(max_n: int, prime_buffer: int) -> np.ndarray:
    """Build a prime table large enough for every square-threat query."""
    root_hi = math.isqrt(max_n + prime_buffer) + prime_buffer
    divisor_count = divisor_counts_segment(2, root_hi + 1)
    values = np.arange(2, root_hi + 1, dtype=np.int64)
    primes = values[divisor_count == 2]
    if primes.size == 0:
        raise RuntimeError("prime lookup construction failed")
    return primes


def next_prime_square_after(n: int, prime_lookup: np.ndarray) -> tuple[int, int]:
    """Return the first prime root r above sqrt(n) and its square."""
    root_floor = math.isqrt(n)
    prime_index = int(np.searchsorted(prime_lookup, root_floor, side="right"))
    if prime_index >= prime_lookup.size:
        raise RuntimeError("prime lookup buffer too small for square-threat scan")
    prime_value = int(prime_lookup[prime_index])
    return prime_value, prime_value * prime_value


def log_score(value: int, divisor_count: int) -> float:
    """Return the implemented raw-Z log-score."""
    return (1.0 - divisor_count / 2.0) * math.log(value)


def is_prime_cube(n: int) -> bool:
    """Return whether n is a prime cube."""
    root, exact = gmpy2.iroot(n, 3)
    return bool(exact and gmpy2.is_prime(root))


def factor_string(n: int) -> str:
    """Return one stable factorization string."""
    pieces: list[str] = []
    for prime_value, exponent in sorted(factorint(n).items()):
        if exponent == 1:
            pieces.append(str(prime_value))
        else:
            pieces.append(f"{prime_value}^{exponent}")
    return " * ".join(pieces)


def _row_sort_key(row: dict[str, object]) -> tuple[int, float, int]:
    """Return the frontier ordering key."""
    return (
        int(row["margin"]),
        -float(row["closure_utilization"]),
        int(row["p"]),
    )


def retain_frontier(
    frontier_rows: list[dict[str, object]],
    candidate_row: dict[str, object],
    frontier_size: int,
) -> None:
    """Retain only the smallest non-floor rows."""
    frontier_rows.append(candidate_row)
    frontier_rows.sort(key=_row_sort_key)
    if len(frontier_rows) > frontier_size:
        del frontier_rows[frontier_size:]


def scan_nonfloor_frontier(
    *,
    max_n: int,
    chunk_size: int,
    buffer: int,
    frontier_size: int,
    prime_buffer: int,
) -> tuple[dict[str, object], list[dict[str, object]]]:
    """Run the exact segmented non-floor scan."""
    started = time.perf_counter()
    prime_lookup = build_prime_lookup(max_n=max_n, prime_buffer=prime_buffer)
    frontier_rows: list[dict[str, object]] = []
    scanned_gap_count = 0
    d4_gap_count = 0
    earliest_d4_semiprime_gap_count = 0
    filtered_r2_minus_2_composite_count = 0
    nonfloor_count = 0

    chunk_lo = 2
    while chunk_lo <= max_n:
        chunk_hi_exclusive = min(max_n + 1, chunk_lo + chunk_size)
        scan_hi_exclusive = min(max_n + 1, chunk_hi_exclusive + buffer)
        divisor_count = divisor_counts_segment(chunk_lo, scan_hi_exclusive)
        values = np.arange(chunk_lo, scan_hi_exclusive, dtype=np.int64)
        primes = values[divisor_count == 2]
        log_values = np.log(values.astype(np.float64))

        for left_prime, right_prime in zip(primes[:-1], primes[1:]):
            if left_prime < chunk_lo or left_prime >= chunk_hi_exclusive:
                continue
            if right_prime > max_n:
                continue

            gap = int(right_prime - left_prime)
            if gap < 4:
                continue

            scanned_gap_count += 1
            left_index = int(left_prime - chunk_lo + 1)
            right_index = int(right_prime - chunk_lo)
            gap_values = values[left_index:right_index]
            gap_divisors = divisor_count[left_index:right_index]
            scores = (
                (1.0 - gap_divisors.astype(np.float64) / 2.0)
                * log_values[left_index:right_index]
            )
            winner_index = int(np.argmax(scores))
            winner_n = int(gap_values[winner_index])
            winner_d = int(gap_divisors[winner_index])
            if winner_d != 4:
                continue

            d4_gap_count += 1
            if is_prime_cube(winner_n):
                continue

            d4_indices = np.flatnonzero(gap_divisors == 4)
            first_d4_semiprime_index: int | None = None
            for raw_index in d4_indices:
                candidate = int(gap_values[int(raw_index)])
                if not is_prime_cube(candidate):
                    first_d4_semiprime_index = int(raw_index)
                    break
            if first_d4_semiprime_index is None or first_d4_semiprime_index != winner_index:
                continue

            earliest_d4_semiprime_gap_count += 1
            r, s_plus_w = next_prime_square_after(winner_n, prime_lookup)
            r2_minus_2 = s_plus_w - 2
            if gmpy2.is_prime(r2_minus_2):
                continue

            filtered_r2_minus_2_composite_count += 1
            margin = int(s_plus_w - int(right_prime))
            if margin <= 2:
                continue

            nonfloor_count += 1
            winner_offset = int(winner_n - left_prime)
            q_offset = int(right_prime - left_prime)
            square_threat_distance = int(s_plus_w - winner_n)
            row = {
                "p": int(left_prime),
                "w": winner_n,
                "q": int(right_prime),
                "r": int(r),
                "S_plus_w": int(s_plus_w),
                "margin": margin,
                "gap_size": q_offset,
                "winner_offset": winner_offset,
                "q_offset": q_offset,
                "closure_utilization": float(q_offset - winner_offset) / float(square_threat_distance),
                "log_score_w": float(log_score(winner_n, 4)),
                "r2_minus_2": int(r2_minus_2),
                "r2_minus_2_factors": "",
            }
            retain_frontier(frontier_rows, row, frontier_size)

        chunk_lo = chunk_hi_exclusive

    if not frontier_rows:
        raise RuntimeError("non-floor scan produced no rows")

    for row in frontier_rows:
        row["r2_minus_2_factors"] = factor_string(int(row["r2_minus_2"]))

    summary = {
        "parameters": {
            "max_n": int(max_n),
            "chunk_size": int(chunk_size),
            "buffer": int(buffer),
            "frontier_size": int(frontier_size),
            "prime_buffer": int(prime_buffer),
        },
        "scanned_gap_count": scanned_gap_count,
        "d4_gap_count": d4_gap_count,
        "earliest_d4_semiprime_gap_count": earliest_d4_semiprime_gap_count,
        "filtered_r2_minus_2_composite_count": filtered_r2_minus_2_composite_count,
        "nonfloor_count": nonfloor_count,
        "global_min_margin": int(frontier_rows[0]["margin"]),
        "global_min_margin_row": frontier_rows[0],
        "frontier": frontier_rows,
        "runtime_seconds": time.perf_counter() - started,
    }
    return summary, frontier_rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    """Write one LF-terminated CSV file."""
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main(argv: list[str] | None = None) -> int:
    """Run the non-floor scan and write artifacts."""
    args = build_parser().parse_args(argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    summary, frontier_rows = scan_nonfloor_frontier(
        max_n=args.max_n,
        chunk_size=args.chunk_size,
        buffer=args.buffer,
        frontier_size=args.frontier_size,
        prime_buffer=args.prime_buffer,
    )

    summary_path = args.output_dir / "d4_square_threat_nonfloor_frontier_summary.json"
    frontier_path = args.output_dir / "d4_square_threat_nonfloor_frontier.csv"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    write_csv(frontier_path, frontier_rows)

    print(
        "d4-square-threat-nonfloor-frontier:"
        f" rows={len(frontier_rows)}"
        f" global_min_margin={summary['global_min_margin']}"
        f" runtime_seconds={summary['runtime_seconds']:.3f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
