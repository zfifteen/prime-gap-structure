#!/usr/bin/env python3
"""Measure exact DNI recursive-walk scaling across prime decades."""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path

from sympy import nextprime, prevprime


ROOT = Path(__file__).resolve().parents[3]
BENCHMARK_DIR = ROOT / "benchmarks" / "python" / "predictor"
if str(BENCHMARK_DIR) not in sys.path:
    sys.path.insert(0, str(BENCHMARK_DIR))

import gwr_dni_recursive_walk as walk


DEFAULT_OUTPUT_DIR = ROOT / "output"
DEFAULT_MIN_POWER = 2
DEFAULT_MAX_POWER = 18


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description="Sweep exact DNI recursive-walk scaling across prime decades.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for JSON and CSV artifacts.",
    )
    parser.add_argument(
        "--min-power",
        type=int,
        default=DEFAULT_MIN_POWER,
        help="Smallest power m in the decade start 10^m.",
    )
    parser.add_argument(
        "--max-power",
        type=int,
        default=DEFAULT_MAX_POWER,
        help="Largest power m in the decade start 10^m.",
    )
    return parser


def steps_for_power(power: int) -> int:
    """Return the deterministic step budget for one decade regime."""
    if power <= 7:
        return 100
    if power <= 10:
        return 50
    if power <= 13:
        return 20
    return 10


def start_gap_for_power(power: int) -> tuple[int, int]:
    """Return the first prime gap whose right endpoint is at or above 10^power."""
    start_value = 10**power
    first_prime_at_or_above = int(nextprime(start_value - 1))
    left_prime = int(prevprime(first_prime_at_or_above))
    return left_prime, first_prime_at_or_above


def run_walk_from_gap(
    left_prime: int,
    right_prime: int,
    steps: int,
) -> list[dict[str, object]]:
    """Run the exact DNI recursive walk from one known gap."""
    if steps < 1:
        raise ValueError("steps must be at least 1")

    current_left_prime = left_prime
    current_right_prime = right_prime
    current_gap_index = 1
    rows: list[dict[str, object]] = []

    for step in range(steps):
        row = walk.dni_recursive_step(
            current_gap_index,
            current_left_prime,
            current_right_prime,
        )
        first_open = walk.first_open_offset(current_right_prime % 30)
        scan_cutoff = walk.EXTENDED_CUTOFF_MAP[first_open]
        row["step"] = step + 1
        row["first_open_offset"] = first_open
        row["scan_cutoff"] = scan_cutoff
        row["cutoff_utilization"] = float(row["predicted_peak_offset"]) / float(scan_cutoff)
        rows.append(row)

        if row["exact_hit"]:
            current_left_prime = current_right_prime
            current_right_prime = int(row["predicted_next_prime"])
            current_gap_index += 1
            continue

        current_left_prime = int(prevprime(int(row["predicted_next_prime"])))
        current_right_prime = int(row["predicted_next_prime"])
        current_gap_index += 1 + int(row["skipped_gap_count"])

    return rows


def analyze_power(power: int) -> dict[str, object]:
    """Run one exact decade-scaling measurement."""
    if power < 2:
        raise ValueError("power must be at least 2")

    steps = steps_for_power(power)
    left_prime, right_prime = start_gap_for_power(power)
    started = time.perf_counter()
    rows = run_walk_from_gap(left_prime, right_prime, steps)
    runtime_seconds = time.perf_counter() - started

    exact_hit_count = sum(1 for row in rows if row["exact_hit"])
    total_skipped_gaps = sum(int(row["skipped_gap_count"]) for row in rows)
    first_open_2_count = sum(1 for row in rows if int(row["first_open_offset"]) == 2)
    first_open_4_count = sum(1 for row in rows if int(row["first_open_offset"]) == 4)
    first_open_6_count = sum(1 for row in rows if int(row["first_open_offset"]) == 6)

    return {
        "power": power,
        "decade_start": 10**power,
        "steps": steps,
        "start_left_prime": left_prime,
        "start_right_prime": right_prime,
        "final_predicted_next_prime": int(rows[-1]["predicted_next_prime"]),
        "exact_hit_rate": exact_hit_count / steps,
        "total_skipped_gaps": total_skipped_gaps,
        "mean_skipped_gap_count": total_skipped_gaps / steps,
        "max_skipped_gap_count": max(int(row["skipped_gap_count"]) for row in rows),
        "mean_predicted_peak_offset": (
            sum(int(row["predicted_peak_offset"]) for row in rows) / steps
        ),
        "max_predicted_peak_offset": max(int(row["predicted_peak_offset"]) for row in rows),
        "mean_cutoff_utilization": (
            sum(float(row["cutoff_utilization"]) for row in rows) / steps
        ),
        "max_cutoff_utilization": max(float(row["cutoff_utilization"]) for row in rows),
        "first_open_2_share": first_open_2_count / steps,
        "first_open_4_share": first_open_4_count / steps,
        "first_open_6_share": first_open_6_count / steps,
        "runtime_seconds": runtime_seconds,
        "runtime_seconds_per_step": runtime_seconds / steps,
    }


def run_sweep(min_power: int, max_power: int) -> tuple[list[dict[str, object]], dict[str, object]]:
    """Run the decade sweep and return detail rows plus summary."""
    if min_power < 2:
        raise ValueError("min_power must be at least 2")
    if max_power < min_power:
        raise ValueError("max_power must be at least min_power")

    rows = [analyze_power(power) for power in range(min_power, max_power + 1)]
    return rows, summarize_rows(rows)


def summarize_rows(rows: list[dict[str, object]]) -> dict[str, object]:
    """Aggregate one exact decade-scaling sweep."""
    if not rows:
        raise ValueError("rows must not be empty")

    count = len(rows)
    return {
        "power_start": int(rows[0]["power"]),
        "power_end": int(rows[-1]["power"]),
        "count": count,
        "mean_exact_hit_rate": sum(float(row["exact_hit_rate"]) for row in rows) / count,
        "mean_mean_skipped_gap_count": sum(float(row["mean_skipped_gap_count"]) for row in rows) / count,
        "all_zero_skips": all(int(row["total_skipped_gaps"]) == 0 for row in rows),
        "all_exact_hits": all(float(row["exact_hit_rate"]) == 1.0 for row in rows),
        "max_runtime_seconds": max(float(row["runtime_seconds"]) for row in rows),
        "max_runtime_seconds_per_step": max(float(row["runtime_seconds_per_step"]) for row in rows),
        "max_start_right_prime": max(int(row["start_right_prime"]) for row in rows),
        "max_final_predicted_next_prime": max(int(row["final_predicted_next_prime"]) for row in rows),
        "max_observed_peak_offset": max(int(row["max_predicted_peak_offset"]) for row in rows),
        "max_observed_cutoff_utilization": max(float(row["max_cutoff_utilization"]) for row in rows),
    }


def main(argv: list[str] | None = None) -> int:
    """Run the exact DNI scaling sweep and write JSON plus CSV artifacts."""
    args = build_parser().parse_args(argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    rows, summary = run_sweep(args.min_power, args.max_power)
    summary_path = args.output_dir / "gwr_dni_recursive_gap_scaling_sweep_summary.json"
    detail_path = args.output_dir / "gwr_dni_recursive_gap_scaling_sweep_details.csv"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    fieldnames = [
        "power",
        "decade_start",
        "steps",
        "start_left_prime",
        "start_right_prime",
        "final_predicted_next_prime",
        "exact_hit_rate",
        "total_skipped_gaps",
        "mean_skipped_gap_count",
        "max_skipped_gap_count",
        "mean_predicted_peak_offset",
        "max_predicted_peak_offset",
        "mean_cutoff_utilization",
        "max_cutoff_utilization",
        "first_open_2_share",
        "first_open_4_share",
        "first_open_6_share",
        "runtime_seconds",
        "runtime_seconds_per_step",
    ]
    with detail_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
