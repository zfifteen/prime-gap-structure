#!/usr/bin/env python3
"""Audit the placed PNT/GWR witness formula on exact prime-gap surfaces."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
from sympy import divisor_count, nextprime


ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = ROOT / "src" / "python"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from z_band_prime_composite_field import divisor_counts_segment
from z_band_prime_predictor import W_d, placed_prime_from_seed


DEFAULT_OUTPUT_DIR = ROOT / "output"
DEFAULT_EXACT_LIMIT = 10_000


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description="Audit the placed witness formula on an exact prime-gap surface.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for the JSON audit summary.",
    )
    parser.add_argument(
        "--exact-limit",
        type=int,
        default=DEFAULT_EXACT_LIMIT,
        help="Exact natural-number limit for the audit surface.",
    )
    return parser


def witness_prime_from_seed(seed: int, divisor_target: int) -> int:
    """Return the prime recovered by the witness search started at seed."""
    witness = W_d(seed, divisor_target)
    return int(nextprime(witness - 1))


def _build_counterexample(
    *,
    left_prime: int,
    right_prime: int,
    seed: int,
    divisor_target: int,
    interior_values: np.ndarray,
    interior_divisors: np.ndarray,
) -> dict[str, object]:
    """Return one concrete seed-level counterexample record."""
    witness = W_d(seed, divisor_target)
    return {
        "left_prime": left_prime,
        "right_prime": right_prime,
        "seed": seed,
        "divisor_target": divisor_target,
        "witness": witness,
        "found_prime": int(nextprime(witness - 1)),
        "interior": [
            {"n": int(value), "d": int(divisor_value)}
            for value, divisor_value in zip(interior_values, interior_divisors, strict=True)
        ],
    }


def analyze_exact_limit(limit: int) -> dict[str, object]:
    """Audit direct and witness-based placed formulas on one exact interval."""
    if limit < 5:
        raise ValueError("limit must be at least 5")

    started = time.perf_counter()
    divisor_values = divisor_counts_segment(2, limit + 1)
    values = np.arange(2, limit + 1, dtype=np.int64)
    primes = values[divisor_values == 2]

    gap_count = 0
    seed_count = 0
    direct_success_count = 0
    witness_dmin_success_count = 0
    witness_d4_success_count = 0
    witness_dmin_admissible_seed_count = 0
    witness_d4_admissible_seed_count = 0
    first_w_dmin_counterexample: dict[str, object] | None = None
    first_w_d4_counterexample: dict[str, object] | None = None

    for left_prime, right_prime in zip(primes[:-1], primes[1:], strict=True):
        gap = int(right_prime - left_prime)
        if gap < 2:
            continue

        gap_count += 1
        left_index = int(left_prime - 2 + 1)
        right_index = int(right_prime - 2)
        interior_values = values[left_index:right_index]
        interior_divisors = divisor_values[left_index:right_index]
        dmin = int(interior_divisors.min())
        dmin_mask = interior_divisors == dmin
        d4_mask = interior_divisors == 4

        for seed_index, seed_value in enumerate(interior_values):
            seed = int(seed_value)
            seed_count += 1
            direct_success_count += int(placed_prime_from_seed(seed) == int(right_prime))

            has_dmin_witness_in_gap = bool(np.any(dmin_mask[seed_index:]))
            witness_dmin_admissible_seed_count += int(has_dmin_witness_in_gap)
            witness_dmin_success_count += int(has_dmin_witness_in_gap)
            if (not has_dmin_witness_in_gap) and first_w_dmin_counterexample is None:
                first_w_dmin_counterexample = _build_counterexample(
                    left_prime=int(left_prime),
                    right_prime=int(right_prime),
                    seed=seed,
                    divisor_target=dmin,
                    interior_values=interior_values,
                    interior_divisors=interior_divisors,
                )

            has_d4_witness_in_gap = bool(np.any(d4_mask[seed_index:]))
            witness_d4_admissible_seed_count += int(has_d4_witness_in_gap)
            witness_d4_success_count += int(has_d4_witness_in_gap)
            if (not has_d4_witness_in_gap) and first_w_d4_counterexample is None:
                first_w_d4_counterexample = _build_counterexample(
                    left_prime=int(left_prime),
                    right_prime=int(right_prime),
                    seed=seed,
                    divisor_target=4,
                    interior_values=interior_values,
                    interior_divisors=interior_divisors,
                )

    runtime_seconds = time.perf_counter() - started
    return {
        "exact_limit": limit,
        "gap_count": gap_count,
        "seed_count": seed_count,
        "direct_nextprime_match_count": direct_success_count,
        "direct_nextprime_match_rate": direct_success_count / seed_count,
        "w_dmin_match_count": witness_dmin_success_count,
        "w_dmin_match_rate": witness_dmin_success_count / seed_count,
        "w_dmin_admissible_seed_count": witness_dmin_admissible_seed_count,
        "w_dmin_admissible_seed_rate": witness_dmin_admissible_seed_count / seed_count,
        "w_d4_match_count": witness_d4_success_count,
        "w_d4_match_rate": witness_d4_success_count / seed_count,
        "w_d4_admissible_seed_count": witness_d4_admissible_seed_count,
        "w_d4_admissible_seed_rate": witness_d4_admissible_seed_count / seed_count,
        "first_w_dmin_counterexample": first_w_dmin_counterexample,
        "first_w_d4_counterexample": first_w_d4_counterexample,
        "runtime_seconds": runtime_seconds,
    }


def main(argv: list[str] | None = None) -> int:
    """Run the audit and write the JSON summary."""
    args = build_parser().parse_args(argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    summary = analyze_exact_limit(args.exact_limit)
    output_path = args.output_dir / "pnt_gwr_formula_audit_summary.json"
    output_path.write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
