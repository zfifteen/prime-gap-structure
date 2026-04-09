#!/usr/bin/env python3
"""Measure how the forward recursive GWR chain scales across prime decades."""

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

import gwr_recursive_gap_walk as walk


DEFAULT_OUTPUT_DIR = ROOT / "output"
DEFAULT_MAX_POWER = 10


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description="Sweep forward recursive GWR scaling across prime decades.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for JSON and CSV artifacts.",
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
    if power == 8:
        return 50
    if power == 9:
        return 25
    if power == 10:
        return 10
    if power == 11:
        return 3
    if power == 12:
        return 2
    return 1


def start_gap_for_power(power: int) -> tuple[int, int]:
    """Return the first prime gap whose right endpoint is at or above 10^power."""
    start_value = 10**power
    first_prime_at_or_above = int(nextprime(start_value - 1))
    left_prime = int(prevprime(first_prime_at_or_above))
    return left_prime, first_prime_at_or_above


def analyze_power(power: int) -> dict[str, object]:
    """Run one decade-scaling measurement."""
    if power < 2:
        raise ValueError("power must be at least 2")

    steps = steps_for_power(power)
    left_prime, right_prime = start_gap_for_power(power)
    started = time.perf_counter()
    _, summary = walk.run_recursive_walk_from_gap(1, left_prime, right_prime, steps)
    runtime_seconds = time.perf_counter() - started

    return {
        "power": power,
        "decade_start": 10**power,
        "steps": steps,
        "start_gap_index": None,
        "start_left_prime": left_prime,
        "start_right_prime": right_prime,
        "exact_immediate_hit_rate": summary["exact_immediate_hit_rate"],
        "mean_skipped_gap_count": summary["mean_skipped_gap_count"],
        "max_skipped_gap_count": summary["max_skipped_gap_count"],
        "recovery_exact_rate": summary["recovery_exact_rate"],
        "mean_next_gap_width": summary["mean_next_gap_width"],
        "runtime_seconds": runtime_seconds,
    }


def run_sweep(max_power: int) -> tuple[list[dict[str, object]], dict[str, object]]:
    """Run the decade sweep and return detail rows plus summary."""
    if max_power < 2:
        raise ValueError("max_power must be at least 2")

    rows = [analyze_power(power) for power in range(2, max_power + 1)]
    return rows, summarize_rows(rows)


def summarize_rows(rows: list[dict[str, object]]) -> dict[str, object]:
    """Aggregate one decade-scaling sweep."""
    if not rows:
        raise ValueError("rows must not be empty")

    count = len(rows)
    return {
        "power_start": int(rows[0]["power"]),
        "power_end": int(rows[-1]["power"]),
        "count": count,
        "mean_exact_immediate_hit_rate": sum(float(row["exact_immediate_hit_rate"]) for row in rows) / count,
        "mean_mean_skipped_gap_count": sum(float(row["mean_skipped_gap_count"]) for row in rows) / count,
        "max_runtime_seconds": max(float(row["runtime_seconds"]) for row in rows),
        "max_start_right_prime": max(int(row["start_right_prime"]) for row in rows),
        "all_recovery_exact": all(float(row["recovery_exact_rate"]) == 1.0 for row in rows),
    }


def main(argv: list[str] | None = None) -> int:
    """Run the scaling sweep and write JSON plus CSV artifacts."""
    args = build_parser().parse_args(argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    rows, summary = run_sweep(args.max_power)
    summary_path = args.output_dir / "gwr_recursive_gap_scaling_sweep_summary.json"
    detail_path = args.output_dir / "gwr_recursive_gap_scaling_sweep_details.csv"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    fieldnames = [
        "power",
        "decade_start",
        "steps",
        "start_gap_index",
        "start_left_prime",
        "start_right_prime",
        "exact_immediate_hit_rate",
        "mean_skipped_gap_count",
        "max_skipped_gap_count",
        "recovery_exact_rate",
        "mean_next_gap_width",
        "runtime_seconds",
    ]
    with detail_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
