#!/usr/bin/env python3
"""Search prime squares for the first dynamic-cutoff counterexample.

This script attacks the square branch of the bounded DNI/GWR walker directly.
For each odd prime p, let q = prevprime(p^2). The square branch would refute
the current dynamic cutoff law as soon as

    p^2 - q > C(q),

where C(q) = max(64, ceil(0.5 * log(q)^2)).

The script stops on the first such contradiction by default. If no
counterexample is found on the requested finite range, it emits the finite
certificate for exactly that range together with the frontier rows where the
square-branch utilization sets a new maximum.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
import time
from pathlib import Path

import gmpy2
from sympy import nextprime, primerange


ROOT = Path(__file__).resolve().parents[3]
BENCHMARK_DIR = ROOT / "benchmarks" / "python" / "predictor"
if str(BENCHMARK_DIR) not in sys.path:
    sys.path.insert(0, str(BENCHMARK_DIR))

import gwr_dni_recursive_walk as walk


DEFAULT_MIN_PRIME = 3
DEFAULT_MAX_PRIME = 100_000
DEFAULT_OUTPUT_DIR = ROOT / "output" / "gwr_proof"
CSV_FIELDS = [
    "p",
    "square",
    "previous_prime",
    "offset",
    "o_q",
    "dynamic_cutoff",
    "dynamic_cutoff_utilization",
    "elapsed_seconds",
]


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description="Search prime squares for the first dynamic-cutoff counterexample.",
    )
    parser.add_argument(
        "--min-prime",
        type=int,
        default=DEFAULT_MIN_PRIME,
        help="Smallest odd prime p to test via p^2.",
    )
    parser.add_argument(
        "--max-prime",
        type=int,
        default=DEFAULT_MAX_PRIME,
        help="Largest odd prime p to test via p^2.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for JSON and CSV artifacts.",
    )
    return parser


def _first_tested_prime(min_prime: int) -> int:
    """Return the first odd prime at or above the requested lower bound."""
    if min_prime <= 3:
        return 3
    return int(nextprime(min_prime - 1))


def _previous_prime_before_square(square: int) -> int:
    """Return the prime immediately below one odd prime square."""
    candidate = square - 2
    while not gmpy2.is_prime(candidate):
        candidate -= 2
    return int(candidate)


def _branch_maxima_template() -> dict[str, dict[str, object] | None]:
    """Return the empty first-open-offset maxima table."""
    return {"2": None, "4": None, "6": None}


def _row_for_prime_square(p: int, started_at: float) -> dict[str, object]:
    """Return the square-branch comparison row for one prime p."""
    square = p * p
    previous_prime = _previous_prime_before_square(square)
    offset = square - previous_prime
    dynamic_cutoff = walk.dynamic_cutoff(previous_prime)
    utilization = float(offset) / float(dynamic_cutoff)
    return {
        "p": int(p),
        "square": int(square),
        "previous_prime": int(previous_prime),
        "offset": int(offset),
        "o_q": int(walk.first_open_offset(previous_prime % 30)),
        "dynamic_cutoff": int(dynamic_cutoff),
        "dynamic_cutoff_utilization": utilization,
        "elapsed_seconds": time.time() - started_at,
    }


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    """Write one LF-terminated CSV file."""
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def run_search(
    min_prime: int,
    max_prime: int,
) -> tuple[list[dict[str, object]], dict[str, object], dict[str, object] | None]:
    """Search prime squares for the first dynamic-cutoff counterexample."""
    if min_prime < 3:
        raise ValueError("min_prime must be at least 3")
    if max_prime < min_prime:
        raise ValueError("max_prime must be at least min_prime")

    started_at = time.time()
    frontier_rows: list[dict[str, object]] = []
    first_counterexample: dict[str, object] | None = None
    branch_maxima = _branch_maxima_template()
    first_tested_prime: int | None = None
    last_tested_prime: int | None = None
    tested_prime_count = 0
    max_utilization = 0.0
    max_row: dict[str, object] | None = None

    for prime_value in primerange(_first_tested_prime(min_prime), max_prime + 1):
        p = int(prime_value)
        row = _row_for_prime_square(p, started_at)
        tested_prime_count += 1
        if first_tested_prime is None:
            first_tested_prime = p
        last_tested_prime = p

        branch_key = str(row["o_q"])
        branch_max = branch_maxima[branch_key]
        if branch_max is None or float(row["dynamic_cutoff_utilization"]) > float(
            branch_max["dynamic_cutoff_utilization"],
        ):
            branch_maxima[branch_key] = row

        if float(row["dynamic_cutoff_utilization"]) > max_utilization:
            max_utilization = float(row["dynamic_cutoff_utilization"])
            max_row = row
            frontier_rows.append(row)

        if int(row["offset"]) > int(row["dynamic_cutoff"]):
            first_counterexample = row
            break

    if max_row is None:
        raise ValueError("search interval produced no prime-square rows")

    summary = {
        "min_prime": int(min_prime),
        "max_prime": int(max_prime),
        "tested_prime_count": tested_prime_count,
        "first_tested_prime": first_tested_prime,
        "last_tested_prime": last_tested_prime,
        "first_counterexample": first_counterexample,
        "max_dynamic_cutoff_utilization": max_utilization,
        "max_row": max_row,
        "max_row_by_o_q": branch_maxima,
        "elapsed_seconds": time.time() - started_at,
    }
    return frontier_rows, summary, first_counterexample


def main(argv: list[str] | None = None) -> int:
    """Run the square-branch dynamic-cutoff search and write artifacts."""
    args = build_parser().parse_args(argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    frontier_rows, summary, first_counterexample = run_search(
        args.min_prime,
        args.max_prime,
    )

    summary_path = args.output_dir / "square_branch_dynamic_cutoff_search_summary.json"
    frontier_path = args.output_dir / "square_branch_dynamic_cutoff_search_frontier.csv"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    _write_csv(frontier_path, frontier_rows)

    if first_counterexample is not None:
        counterexample_path = (
            args.output_dir / "square_branch_dynamic_cutoff_counterexample.json"
        )
        counterexample_path.write_text(
            json.dumps(first_counterexample, indent=2) + "\n",
            encoding="utf-8",
        )

    max_row = summary["max_row"]
    print(
        "square-branch-dynamic-cutoff-search:"
        f" primes={summary['tested_prime_count']}"
        f" first_counterexample={'none' if first_counterexample is None else first_counterexample['p']}"
        f" max_utilization={summary['max_dynamic_cutoff_utilization']}"
        f" max_p={max_row['p']}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
