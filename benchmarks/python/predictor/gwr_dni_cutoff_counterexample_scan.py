#!/usr/bin/env python3
"""Scan consecutive prime gaps for a dynamic-cutoff counterexample."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

from sympy import nextprime


ROOT = Path(__file__).resolve().parents[3]
BENCHMARK_DIR = ROOT / "benchmarks" / "python" / "predictor"
if str(BENCHMARK_DIR) not in sys.path:
    sys.path.insert(0, str(BENCHMARK_DIR))

import gwr_dni_recursive_walk as walk


DEFAULT_OUTPUT_DIR = ROOT / "output"
DEFAULT_MIN_RIGHT_PRIME = 11
DEFAULT_MAX_RIGHT_PRIME = 10**6


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description="Scan consecutive prime gaps for the first DNI cutoff-law counterexample.",
    )
    parser.add_argument(
        "--min-right-prime",
        type=int,
        default=DEFAULT_MIN_RIGHT_PRIME,
        help="Smallest current right prime q to test.",
    )
    parser.add_argument(
        "--max-right-prime",
        type=int,
        default=DEFAULT_MAX_RIGHT_PRIME,
        help="Largest current right prime q to test.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for JSON and CSV artifacts.",
    )
    parser.add_argument(
        "--keep-going",
        action="store_true",
        help="Continue scanning after the first counterexample.",
    )
    return parser


def _empty_offset_dict_int() -> dict[str, int]:
    """Return the zeroed first-open-offset integer map."""
    return {"2": 0, "4": 0, "6": 0}


def _empty_offset_dict_float() -> dict[str, float]:
    """Return the zeroed first-open-offset float map."""
    return {"2": 0.0, "4": 0.0, "6": 0.0}


def _first_tested_prime(min_right_prime: int) -> int:
    """Return the first odd prime at or above the requested lower bound."""
    if min_right_prime <= 3:
        return 3
    return int(nextprime(min_right_prime - 1))


def _frontier_row(comparison: dict[str, object]) -> dict[str, object]:
    """Return one proof-facing frontier certificate row."""
    exact_peak_offset = int(comparison["exact_next_peak_offset"])
    ladder = list(comparison["exact_divisor_ladder"])[:exact_peak_offset]
    return {
        "current_right_prime": int(comparison["current_right_prime"]),
        "next_prime": int(comparison["exact_next_prime"]),
        "gap_width": int(comparison["exact_gap_width"]),
        "first_open_offset": int(comparison["first_open_offset"]),
        "exact_next_dmin": int(comparison["exact_next_dmin"]),
        "exact_next_peak_offset": exact_peak_offset,
        "exact_gap_boundary_offset": int(comparison["exact_gap_boundary_offset"]),
        "cutoff": int(comparison["cutoff"]),
        "cutoff_utilization": float(comparison["cutoff_utilization"]),
        "boundary_utilization": float(comparison["boundary_utilization"]),
        "divisor_ladder": " ".join(str(value) for value in ladder),
    }


def run_scan(
    min_right_prime: int,
    max_right_prime: int,
    keep_going: bool = False,
) -> tuple[list[dict[str, object]], dict[str, object], dict[str, object] | None]:
    """Scan consecutive prime gaps for the first bounded-vs-exact mismatch."""
    if min_right_prime < 3:
        raise ValueError("min_right_prime must be at least 3")
    if max_right_prime < min_right_prime:
        raise ValueError("max_right_prime must be at least min_right_prime")

    current_right_prime = _first_tested_prime(min_right_prime)
    frontier_rows: list[dict[str, object]] = []
    first_counterexample: dict[str, object] | None = None
    tested_gap_count = 0
    first_tested_right_prime: int | None = None
    last_tested_right_prime: int | None = None
    max_exact_peak_offset_overall = 0
    max_cutoff_utilization_overall = 0.0
    max_exact_peak_offset_by_first_open_offset = _empty_offset_dict_int()
    max_cutoff_utilization_by_first_open_offset = _empty_offset_dict_float()
    max_boundary_utilization_overall = 0.0
    max_boundary_utilization_by_first_open_offset = _empty_offset_dict_float()

    while current_right_prime <= max_right_prime:
        comparison = walk.compare_transition_rules(current_right_prime)
        tested_gap_count += 1
        if first_tested_right_prime is None:
            first_tested_right_prime = current_right_prime
        last_tested_right_prime = current_right_prime

        first_open_key = str(int(comparison["first_open_offset"]))
        exact_peak_offset = int(comparison["exact_next_peak_offset"])
        cutoff_utilization = float(comparison["cutoff_utilization"])

        if exact_peak_offset > max_exact_peak_offset_overall:
            max_exact_peak_offset_overall = exact_peak_offset
            frontier_rows.append(_frontier_row(comparison))

        if exact_peak_offset > max_exact_peak_offset_by_first_open_offset[first_open_key]:
            max_exact_peak_offset_by_first_open_offset[first_open_key] = exact_peak_offset
        if cutoff_utilization > max_cutoff_utilization_overall:
            max_cutoff_utilization_overall = cutoff_utilization
        if cutoff_utilization > max_cutoff_utilization_by_first_open_offset[first_open_key]:
            max_cutoff_utilization_by_first_open_offset[first_open_key] = cutoff_utilization
        boundary_utilization = float(comparison["boundary_utilization"])
        if boundary_utilization > max_boundary_utilization_overall:
            max_boundary_utilization_overall = boundary_utilization
        if boundary_utilization > max_boundary_utilization_by_first_open_offset[first_open_key]:
            max_boundary_utilization_by_first_open_offset[first_open_key] = boundary_utilization

        if not bool(comparison["matches_cutoff_rule"]) and first_counterexample is None:
            first_counterexample = comparison
            if not keep_going:
                break

        current_right_prime = int(nextprime(current_right_prime))

    summary = {
        "min_right_prime": min_right_prime,
        "max_right_prime": max_right_prime,
        "tested_gap_count": tested_gap_count,
        "first_tested_right_prime": first_tested_right_prime,
        "last_tested_right_prime": last_tested_right_prime,
        "first_counterexample": first_counterexample,
        "max_exact_peak_offset_overall": max_exact_peak_offset_overall,
        "max_exact_peak_offset_by_first_open_offset": max_exact_peak_offset_by_first_open_offset,
        "max_cutoff_utilization_overall": max_cutoff_utilization_overall,
        "max_cutoff_utilization_by_first_open_offset": max_cutoff_utilization_by_first_open_offset,
        "max_boundary_utilization_overall": max_boundary_utilization_overall,
        "max_boundary_utilization_by_first_open_offset": max_boundary_utilization_by_first_open_offset,
    }
    return frontier_rows, summary, first_counterexample


def main(argv: list[str] | None = None) -> int:
    """Run the cutoff-law scan and write the artifact set."""
    args = build_parser().parse_args(argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    frontier_rows, summary, first_counterexample = run_scan(
        args.min_right_prime,
        args.max_right_prime,
        keep_going=args.keep_going,
    )

    summary_path = args.output_dir / "gwr_dni_cutoff_counterexample_scan_summary.json"
    frontier_path = args.output_dir / "gwr_dni_cutoff_counterexample_scan_frontier.csv"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    fieldnames = [
        "current_right_prime",
        "next_prime",
        "gap_width",
        "first_open_offset",
        "exact_next_dmin",
        "exact_next_peak_offset",
        "exact_gap_boundary_offset",
        "cutoff",
        "cutoff_utilization",
        "boundary_utilization",
        "divisor_ladder",
    ]
    with frontier_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(frontier_rows)

    if first_counterexample is not None:
        counterexample_path = args.output_dir / "gwr_dni_cutoff_counterexample.json"
        counterexample_path.write_text(
            json.dumps(first_counterexample, indent=2) + "\n",
            encoding="utf-8",
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
