#!/usr/bin/env python3
"""Extract the exact ratio-form frontier for the no-early-spoiler condition."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = ROOT / "src" / "python"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from z_band_prime_composite_field import divisor_counts_segment


MARGIN_SCAN_PATH = ROOT / "gwr" / "experiments" / "proof" / "no_early_spoiler_margin_scan.py"
TOP_PAIR_LIMIT = 20


def load_margin_scan_module():
    """Load the exact margin-scan helpers directly from file."""
    module_name = "no_early_spoiler_margin_scan_runtime_frontier"
    spec = importlib.util.spec_from_file_location(module_name, MARGIN_SCAN_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load no_early_spoiler_margin_scan")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


MARGIN_SCAN = load_margin_scan_module()


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Extract the exact per-pair ratio frontier from the no-early-"
            "spoiler condition on one interval."
        ),
    )
    parser.add_argument(
        "--lo",
        type=int,
        default=2,
        help="Inclusive lower bound of the natural-number interval.",
    )
    parser.add_argument(
        "--hi",
        type=int,
        default=20_000_001,
        help="Exclusive upper bound of the natural-number interval.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional JSON output path.",
    )
    return parser


def analyze_interval(lo: int, hi: int) -> dict[str, object]:
    """Return the exact per-pair frontier for one interval."""
    if lo < 2:
        raise ValueError("lo must be at least 2")
    if hi <= lo:
        raise ValueError("hi must be greater than lo")

    divisor_count = divisor_counts_segment(lo, hi)
    values = np.arange(lo, hi, dtype=np.int64)
    primes = values[divisor_count == 2]

    pair_best_case: dict[tuple[int, int], dict[str, int | float]] = {}

    for left_prime_raw, right_prime_raw in zip(primes[:-1], primes[1:]):
        left_prime = int(left_prime_raw)
        right_prime = int(right_prime_raw)
        if right_prime - left_prime < 4:
            continue

        left_index = left_prime - lo + 1
        right_index = right_prime - lo
        gap_values = values[left_index:right_index]
        gap_divisors = divisor_count[left_index:right_index]

        winner_divisor_count = int(np.min(gap_divisors))
        winner_index = int(np.flatnonzero(gap_divisors == winner_divisor_count)[0])
        winner_value = int(gap_values[winner_index])

        for earlier_value_raw, earlier_divisor_raw in zip(
            gap_values[:winner_index],
            gap_divisors[:winner_index],
        ):
            earlier_value = int(earlier_value_raw)
            earlier_divisor_count = int(earlier_divisor_raw)
            if earlier_divisor_count <= winner_divisor_count:
                raise RuntimeError(
                    "winner is not the leftmost carrier of the minimal divisor class"
                )

            critical_ratio, actual_ratio, ratio_margin = MARGIN_SCAN.critical_ratio_margin(
                earlier_value,
                earlier_divisor_count,
                winner_value,
                winner_divisor_count,
            )
            log_margin = MARGIN_SCAN.log_score_margin(
                earlier_value,
                earlier_divisor_count,
                winner_value,
                winner_divisor_count,
            )
            case = MARGIN_SCAN._case_record(
                left_prime=left_prime,
                right_prime=right_prime,
                winner_value=winner_value,
                winner_divisor_count=winner_divisor_count,
                earlier_value=earlier_value,
                earlier_divisor_count=earlier_divisor_count,
                log_margin=log_margin,
                critical_ratio=critical_ratio,
                actual_ratio=actual_ratio,
                ratio_margin=ratio_margin,
            )

            key = (winner_divisor_count, earlier_divisor_count)
            best = pair_best_case.get(key)
            if best is None or float(case["critical_ratio_margin"]) < float(
                best["critical_ratio_margin"]
            ):
                pair_best_case[key] = case

    sorted_pairs = sorted(
        pair_best_case.values(),
        key=lambda row: (float(row["critical_ratio_margin"]), int(row["winner_value"])),
    )
    top_pairs = sorted_pairs[:TOP_PAIR_LIMIT]

    winner_frontier: dict[int, dict[str, int | float]] = {}
    for case in sorted_pairs:
        winner_divisor_count = int(case["winner_divisor_count"])
        if winner_divisor_count not in winner_frontier:
            winner_frontier[winner_divisor_count] = case

    winner_frontier_rows = [
        winner_frontier[winner_divisor_count]
        for winner_divisor_count in sorted(winner_frontier)
    ]

    return {
        "interval": {"lo": lo, "hi": hi},
        "decision_surface": (
            "Exact per-pair critical-ratio frontier for the no-early-spoiler "
            "condition against the true GWR carrier."
        ),
        "pair_count": len(pair_best_case),
        "top_ratio_frontier_pairs": top_pairs,
        "winner_class_frontier": winner_frontier_rows,
    }


def main(argv: list[str] | None = None) -> int:
    """Run the frontier extractor and emit a JSON artifact."""
    parser = build_parser()
    args = parser.parse_args(argv)
    payload = analyze_interval(args.lo, args.hi)
    serialized = json.dumps(payload, indent=2)

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized + "\n", encoding="utf-8")

    print(serialized)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
