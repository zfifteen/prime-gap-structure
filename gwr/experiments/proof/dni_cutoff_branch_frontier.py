#!/usr/bin/env python3
"""Extract the exact branch frontier for the DNI cutoff theorem."""

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


DEFAULT_MIN_RIGHT_PRIME = 11
DEFAULT_MAX_RIGHT_PRIME = 10**6
DEFAULT_OUTPUT = ROOT / "output" / "gwr_proof" / "dni_cutoff_branch_frontier_1e6.json"


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description="Extract the exact branch frontier for the DNI cutoff theorem.",
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
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Summary JSON output path.",
    )
    return parser


def _first_tested_prime(min_right_prime: int) -> int:
    """Return the first odd prime at or above the requested lower bound."""
    if min_right_prime <= 3:
        return 3
    return int(nextprime(min_right_prime - 1))


def _frontier_csv_path(summary_path: Path) -> Path:
    """Return the frontier CSV path paired with one summary JSON path."""
    return summary_path.with_name(summary_path.stem + "_rows.csv")


def _branch_key(comparison: dict[str, object]) -> tuple[int, int]:
    """Return the canonical proof branch key."""
    return (
        int(comparison["first_open_offset"]),
        int(comparison["exact_next_dmin"]),
    )


def _make_summary_row(comparison: dict[str, object]) -> dict[str, object]:
    """Return the branch summary row for one extremal exact case."""
    return {
        "first_open_offset": int(comparison["first_open_offset"]),
        "exact_next_dmin": int(comparison["exact_next_dmin"]),
        "count": 0,
        "cutoff": int(comparison["cutoff"]),
        "max_exact_next_peak_offset": int(comparison["exact_next_peak_offset"]),
        "max_cutoff_utilization": float(comparison["cutoff_utilization"]),
        "argmax_current_right_prime": int(comparison["current_right_prime"]),
        "argmax_next_prime": int(comparison["exact_next_prime"]),
        "argmax_gap_width": int(comparison["exact_gap_width"]),
        "argmax_gap_boundary_offset": int(comparison["exact_gap_boundary_offset"]),
    }


def _frontier_row(comparison: dict[str, object]) -> dict[str, object]:
    """Return one branch frontier certificate row."""
    exact_peak_offset = int(comparison["exact_next_peak_offset"])
    ladder = list(comparison["exact_divisor_ladder"])[:exact_peak_offset]
    return {
        "current_right_prime": int(comparison["current_right_prime"]),
        "next_prime": int(comparison["exact_next_prime"]),
        "gap_width": int(comparison["exact_gap_width"]),
        "first_open_offset": int(comparison["first_open_offset"]),
        "exact_next_dmin": int(comparison["exact_next_dmin"]),
        "exact_next_peak_offset": exact_peak_offset,
        "cutoff": int(comparison["cutoff"]),
        "cutoff_utilization": float(comparison["cutoff_utilization"]),
        "exact_gap_boundary_offset": int(comparison["exact_gap_boundary_offset"]),
        "divisor_ladder": " ".join(str(value) for value in ladder),
    }


def run_frontier(
    min_right_prime: int,
    max_right_prime: int,
) -> tuple[dict[str, object], list[dict[str, object]]]:
    """Return the exact branch frontier summary plus frontier rows."""
    if min_right_prime < 3:
        raise ValueError("min_right_prime must be at least 3")
    if max_right_prime < min_right_prime:
        raise ValueError("max_right_prime must be at least min_right_prime")

    current_right_prime = _first_tested_prime(min_right_prime)
    first_tested_right_prime: int | None = None
    last_tested_right_prime: int | None = None
    tested_gap_count = 0
    branch_summary: dict[tuple[int, int], dict[str, object]] = {}
    frontier_rows: list[dict[str, object]] = []

    while current_right_prime <= max_right_prime:
        comparison = walk.compare_transition_rules(current_right_prime)
        tested_gap_count += 1
        if first_tested_right_prime is None:
            first_tested_right_prime = current_right_prime
        last_tested_right_prime = current_right_prime

        key = _branch_key(comparison)
        row = branch_summary.get(key)
        if row is None:
            row = _make_summary_row(comparison)
            branch_summary[key] = row
            frontier_rows.append(_frontier_row(comparison))

        row["count"] = int(row["count"]) + 1
        peak_offset = int(comparison["exact_next_peak_offset"])
        cutoff_utilization = float(comparison["cutoff_utilization"])
        if peak_offset > int(row["max_exact_next_peak_offset"]):
            row["max_exact_next_peak_offset"] = peak_offset
            row["max_cutoff_utilization"] = cutoff_utilization
            row["argmax_current_right_prime"] = int(comparison["current_right_prime"])
            row["argmax_next_prime"] = int(comparison["exact_next_prime"])
            row["argmax_gap_width"] = int(comparison["exact_gap_width"])
            row["argmax_gap_boundary_offset"] = int(comparison["exact_gap_boundary_offset"])
            frontier_rows.append(_frontier_row(comparison))

        current_right_prime = int(nextprime(current_right_prime))

    branch_rows = sorted(
        branch_summary.values(),
        key=lambda row: (
            -float(row["max_cutoff_utilization"]),
            -int(row["max_exact_next_peak_offset"]),
            int(row["first_open_offset"]),
            int(row["exact_next_dmin"]),
        ),
    )

    summary = {
        "interval": {
            "min_right_prime": min_right_prime,
            "max_right_prime": max_right_prime,
        },
        "tested_gap_count": tested_gap_count,
        "first_tested_right_prime": first_tested_right_prime,
        "last_tested_right_prime": last_tested_right_prime,
        "branch_count": len(branch_rows),
        "branch_summary": branch_rows,
        "global_max_peak_branch": branch_rows[0] if branch_rows else None,
    }
    return summary, frontier_rows


def main(argv: list[str] | None = None) -> int:
    """Run the exact branch frontier extractor and emit JSON plus CSV."""
    args = build_parser().parse_args(argv)
    args.output.parent.mkdir(parents=True, exist_ok=True)

    summary, frontier_rows = run_frontier(
        args.min_right_prime,
        args.max_right_prime,
    )
    args.output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    frontier_path = _frontier_csv_path(args.output)
    fieldnames = [
        "current_right_prime",
        "next_prime",
        "gap_width",
        "first_open_offset",
        "exact_next_dmin",
        "exact_next_peak_offset",
        "cutoff",
        "cutoff_utilization",
        "exact_gap_boundary_offset",
        "divisor_ladder",
    ]
    with frontier_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(frontier_rows)

    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
