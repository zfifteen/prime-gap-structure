#!/usr/bin/env python3
"""Measure the residue-locked dead zone below the d=4 square ceiling."""

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


ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = ROOT / "src" / "python"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from z_band_prime_composite_field import divisor_counts_segment


DEFAULT_OUTPUT_DIR = ROOT / "output"
DEFAULT_MAX_N = 10_000_000
DEFAULT_CHUNK_SIZE = 1_000_000
DEFAULT_BUFFER = 10_000
DEFAULT_FRONTIER_SIZE = 12
DEFAULT_PRIME_BUFFER = 5_000
RESIDUE_ORDER = (1, 19)
CSV_FIELDS = [
    "square_residue_mod30",
    "predicted_first_nonfloor_margin",
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
]


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description="Measure the residue-locked dead zone below the d=4 square ceiling.",
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
        help="Number of smallest-margin rows to retain per residue class.",
    )
    parser.add_argument(
        "--prime-buffer",
        type=int,
        default=DEFAULT_PRIME_BUFFER,
        help="Prime lookup buffer above sqrt(max scanned value).",
    )
    return parser


def build_prime_lookup(max_n: int, prime_buffer: int) -> np.ndarray:
    """Build a prime table large enough for every square query."""
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
        raise RuntimeError("prime lookup buffer too small for square scan")
    prime_value = int(prime_lookup[prime_index])
    return prime_value, prime_value * prime_value


def is_prime_cube(n: int) -> bool:
    """Return whether n is a prime cube."""
    root, exact = gmpy2.iroot(n, 3)
    return bool(exact and gmpy2.is_prime(root))


def predicted_first_nonfloor_margin(square_residue_mod30: int) -> int:
    """Return the first wheel-open margin after floor failure for one square residue."""
    if square_residue_mod30 == 1:
        return 8
    if square_residue_mod30 == 19:
        return 6
    raise ValueError(f"unsupported square residue mod 30: {square_residue_mod30}")


def _row_sort_key(row: dict[str, object]) -> tuple[int, int, int]:
    """Return the frontier ordering key."""
    return (
        int(row["margin"]),
        int(row["p"]),
        int(row["w"]),
    )


def retain_frontier(
    frontier_rows: list[dict[str, object]],
    candidate_row: dict[str, object],
    frontier_size: int,
) -> None:
    """Retain the smallest-margin rows only."""
    frontier_rows.append(candidate_row)
    frontier_rows.sort(key=_row_sort_key)
    if len(frontier_rows) > frontier_size:
        del frontier_rows[frontier_size:]


def _empty_residue_bucket() -> dict[str, object]:
    """Return one empty residue summary bucket."""
    return {
        "count": 0,
        "min_margin": None,
        "margin_counts": {},
        "predicted_first_nonfloor_margin": None,
    }


def scan_residue_dead_zone(
    *,
    max_n: int,
    chunk_size: int,
    buffer: int,
    frontier_size: int,
    prime_buffer: int,
) -> tuple[dict[str, object], list[dict[str, object]]]:
    """Run the exact segmented residue-split scan."""
    started = time.perf_counter()
    prime_lookup = build_prime_lookup(max_n=max_n, prime_buffer=prime_buffer)
    residue_summary = {residue: _empty_residue_bucket() for residue in RESIDUE_ORDER}
    frontier_by_residue = {residue: [] for residue in RESIDUE_ORDER}

    scanned_gap_count = 0
    d4_gap_count = 0
    earliest_d4_semiprime_gap_count = 0
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
            if gmpy2.is_prime(s_plus_w - 2):
                continue

            square_residue = int(s_plus_w % 30)
            if square_residue not in residue_summary:
                raise AssertionError(
                    f"unexpected non-floor square residue {square_residue} for r={r}, s={s_plus_w}"
                )

            nonfloor_count += 1
            margin = int(s_plus_w - int(right_prime))
            winner_offset = int(winner_n - left_prime)
            q_offset = int(right_prime - left_prime)
            closure_utilization = float(q_offset - winner_offset) / float(s_plus_w - winner_n)
            predicted_margin = predicted_first_nonfloor_margin(square_residue)
            row = {
                "square_residue_mod30": square_residue,
                "predicted_first_nonfloor_margin": predicted_margin,
                "p": int(left_prime),
                "w": winner_n,
                "q": int(right_prime),
                "r": int(r),
                "S_plus_w": int(s_plus_w),
                "margin": margin,
                "gap_size": q_offset,
                "winner_offset": winner_offset,
                "q_offset": q_offset,
                "closure_utilization": closure_utilization,
            }

            bucket = residue_summary[square_residue]
            bucket["count"] = int(bucket["count"]) + 1
            bucket["predicted_first_nonfloor_margin"] = predicted_margin
            margin_counts = bucket["margin_counts"]
            margin_key = str(margin)
            margin_counts[margin_key] = int(margin_counts.get(margin_key, 0)) + 1
            min_margin = bucket["min_margin"]
            if min_margin is None or margin < min_margin:
                bucket["min_margin"] = margin

            retain_frontier(frontier_by_residue[square_residue], row, frontier_size)

        chunk_lo = chunk_hi_exclusive

    if nonfloor_count == 0:
        raise RuntimeError("residue dead-zone scan produced no non-floor rows")

    residue_checks: dict[str, object] = {}
    for residue in RESIDUE_ORDER:
        bucket = residue_summary[residue]
        margin_counts = bucket["margin_counts"]
        residue_checks[str(residue)] = {
            "predicted_first_nonfloor_margin": bucket["predicted_first_nonfloor_margin"],
            "observed_min_margin_matches_prediction": (
                bucket["min_margin"] == bucket["predicted_first_nonfloor_margin"]
            ),
            "margin_6_count": int(margin_counts.get("6", 0)),
            "margin_8_count": int(margin_counts.get("8", 0)),
        }

    frontier_rows: list[dict[str, object]] = []
    for residue in RESIDUE_ORDER:
        frontier_rows.extend(frontier_by_residue[residue])

    frontier_rows.sort(key=lambda row: (int(row["square_residue_mod30"]), int(row["margin"]), int(row["p"])))
    summary = {
        "parameters": {
            "max_n": max_n,
            "chunk_size": chunk_size,
            "buffer": buffer,
            "frontier_size": frontier_size,
            "prime_buffer": prime_buffer,
        },
        "scanned_gap_count": scanned_gap_count,
        "d4_gap_count": d4_gap_count,
        "earliest_d4_semiprime_gap_count": earliest_d4_semiprime_gap_count,
        "nonfloor_count": nonfloor_count,
        "residue_summary": {str(key): value for key, value in residue_summary.items()},
        "checks": {
            "nonfloor_residue_classes_mod30": list(RESIDUE_ORDER),
            "all_margin_6_rows_live_in_residue_19": residue_checks["1"]["margin_6_count"] == 0,
            "residue_1_branch_starts_at_margin_8": (
                residue_summary[1]["min_margin"] == predicted_first_nonfloor_margin(1)
            ),
            "residue_19_branch_starts_at_margin_6": (
                residue_summary[19]["min_margin"] == predicted_first_nonfloor_margin(19)
            ),
            "residue_checks": residue_checks,
        },
        "frontier": frontier_rows,
        "runtime_seconds": time.perf_counter() - started,
    }
    return summary, frontier_rows


def main(argv: list[str] | None = None) -> int:
    """Run the residue-split scan and write artifacts."""
    parser = build_parser()
    args = parser.parse_args(argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    summary, frontier_rows = scan_residue_dead_zone(
        max_n=args.max_n,
        chunk_size=args.chunk_size,
        buffer=args.buffer,
        frontier_size=args.frontier_size,
        prime_buffer=args.prime_buffer,
    )

    summary_path = args.output_dir / "d4_square_residue_dead_zone_summary.json"
    frontier_path = args.output_dir / "d4_square_residue_dead_zone.csv"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    with frontier_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(frontier_rows)

    print(
        "d4-square-residue-dead-zone:"
        f" nonfloor_count={summary['nonfloor_count']}"
        f" residue_1_min_margin={summary['residue_summary']['1']['min_margin']}"
        f" residue_19_min_margin={summary['residue_summary']['19']['min_margin']}"
        f" runtime={summary['runtime_seconds']:.3f}s"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
