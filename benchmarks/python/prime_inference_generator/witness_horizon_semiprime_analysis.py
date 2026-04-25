#!/usr/bin/env python3
"""Measure witness-horizon semiprime impostors in filtered-v5 output."""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path
from statistics import median
from typing import Any

from sympy import factorint

try:
    from .experimental_graph_prime_generator import (
        audit_records,
        emit_records,
    )
    from .offline_pgs_certificate_emitter import first_prime_after
    from .resolved_boundary_lock_separator_probe import jsonable
except ImportError:  # pragma: no cover - direct script execution
    MODULE_DIR = Path(__file__).resolve().parent
    if str(MODULE_DIR) not in sys.path:
        sys.path.insert(0, str(MODULE_DIR))
    from experimental_graph_prime_generator import (
        audit_records,
        emit_records,
    )
    from offline_pgs_certificate_emitter import first_prime_after
    from resolved_boundary_lock_separator_probe import jsonable


DEFAULT_OUTPUT_DIR = Path("output/prime_inference_generator")
SUMMARY_FILENAME = "witness_horizon_semiprime_analysis_summary.json"
ROWS_FILENAME = "witness_horizon_semiprime_analysis_rows.jsonl"
DEFAULT_WITNESS_BOUNDS = "127,149,197,251,307"


def build_parser() -> argparse.ArgumentParser:
    """Build the witness-horizon analysis CLI."""
    parser = argparse.ArgumentParser(
        description="Measure filtered-v5 witness-horizon semiprime failures.",
    )
    parser.add_argument("--start-anchor", type=int, default=11)
    parser.add_argument("--max-anchor", type=int, default=100_000)
    parser.add_argument("--candidate-bound", type=int, default=128)
    parser.add_argument("--witness-bounds", default=DEFAULT_WITNESS_BOUNDS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser


def parse_witness_bounds(raw: str) -> list[int]:
    """Parse a comma-separated witness-bound list."""
    bounds = [int(item.strip()) for item in raw.split(",") if item.strip()]
    if not bounds:
        raise ValueError("at least one witness bound is required")
    return bounds


def expanded_factorization(n: int) -> tuple[list[int], dict[int, int]]:
    """Return downstream factorization data for one emitted value."""
    factorization = {int(prime): int(exp) for prime, exp in factorint(n).items()}
    factors: list[int] = []
    for prime, exp in factorization.items():
        factors.extend([prime] * exp)
    return sorted(factors), factorization


def classify_failure(
    record: dict[str, Any],
    witness_bound: int,
) -> dict[str, Any] | None:
    """Return downstream failure classification, or None for confirmed records."""
    anchor_p = int(record["anchor_p"])
    q_hat = int(record["inferred_prime_q_hat"])
    first = first_prime_after(anchor_p, q_hat)
    if first == q_hat:
        return None

    factors, factorization = expanded_factorization(q_hat)
    total_factor_count = len(factors)
    if total_factor_count == 1 and factors[0] == q_hat:
        failure_class = "PRIME_NOT_NEXT_BOUNDARY"
    elif total_factor_count == 2:
        failure_class = "SEMIPRIME"
    elif len(set(factors)) == 1 and total_factor_count > 1:
        failure_class = "PRIME_POWER"
    else:
        failure_class = "OTHER_COMPOSITE"

    least_factor = min(factors)
    return {
        "anchor_p": anchor_p,
        "inferred_prime_q_hat": q_hat,
        "boundary_offset": int(record["boundary_offset"]),
        "first_prime_after_anchor": first,
        "failure_class": failure_class,
        "factors": factors,
        "factorization": factorization,
        "least_factor": least_factor,
        "least_factor_minus_witness_bound": least_factor - witness_bound,
    }


def analyze_bound(
    witness_bound: int,
    start_anchor: int,
    max_anchor: int,
    candidate_bound: int,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Run filtered-v5 for one bound and classify all downstream failures."""
    started = time.perf_counter()
    records, generator_summary = emit_records(
        solver_version="filtered-v5",
        start_anchor=start_anchor,
        max_anchor=max_anchor,
        candidate_bound=candidate_bound,
        witness_bound=witness_bound,
        emit_target=None,
    )
    audit_summary = audit_records(records)
    failures = [
        failure
        for record in records
        if (failure := classify_failure(record, witness_bound)) is not None
    ]

    factor_counter: Counter[int] = Counter()
    least_factor_deltas: list[int] = []
    failure_class_counts: Counter[str] = Counter()
    for failure in failures:
        factor_counter.update(int(factor) for factor in failure["factors"])
        least_factor_deltas.append(int(failure["least_factor_minus_witness_bound"]))
        failure_class_counts[str(failure["failure_class"])] += 1

    failed_count = int(audit_summary["failed_count"])
    semiprime_count = int(failure_class_counts["SEMIPRIME"])
    row = {
        "witness_bound": witness_bound,
        "start_anchor": start_anchor,
        "max_anchor": max_anchor,
        "candidate_bound": candidate_bound,
        "anchors_scanned": int(generator_summary["anchors_scanned"]),
        "risky_input_count": int(generator_summary["risky_input_count"]),
        "filtered_count": int(generator_summary["filtered_count"]),
        "emitted_count": int(generator_summary["emitted_count"]),
        "confirmed_count": int(audit_summary["confirmed_count"]),
        "failed_count": failed_count,
        "coverage_rate": float(generator_summary["coverage_rate"]),
        "filter_reason_counts": dict(generator_summary["filter_reason_counts"]),
        "first_failure": audit_summary["first_failure"],
        "failure_class_counts": dict(sorted(failure_class_counts.items())),
        "semiprime_rate": 0.0 if failed_count == 0 else semiprime_count / failed_count,
        "factor_min": min(factor_counter) if factor_counter else None,
        "factor_max": max(factor_counter) if factor_counter else None,
        "factor_distribution": dict(sorted(factor_counter.items())),
        "least_factor_delta_min": min(least_factor_deltas)
        if least_factor_deltas
        else None,
        "least_factor_delta_median": median(least_factor_deltas)
        if least_factor_deltas
        else None,
        "least_factor_delta_max": max(least_factor_deltas)
        if least_factor_deltas
        else None,
        "first_20_failures": failures[:20],
        "production_approved": False,
        "cryptographic_use_approved": False,
        "classical_factorization_scope": "downstream_failure_classification_only",
        "runtime_seconds": time.perf_counter() - started,
    }
    return row, failures


def run_analysis(
    start_anchor: int,
    max_anchor: int,
    candidate_bound: int,
    witness_bounds: list[int],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run the witness-horizon analysis for all configured bounds."""
    started = time.perf_counter()
    rows: list[dict[str, Any]] = []
    for witness_bound in witness_bounds:
        row, _ = analyze_bound(
            witness_bound=witness_bound,
            start_anchor=start_anchor,
            max_anchor=max_anchor,
            candidate_bound=candidate_bound,
        )
        rows.append(row)

    summary = {
        "record_type": "WITNESS_HORIZON_SEMIPRIME_ANALYSIS_SUMMARY",
        "mode": "offline_witness_horizon_semiprime_analysis",
        "solver_version": "filtered-v5",
        "start_anchor": start_anchor,
        "max_anchor": max_anchor,
        "candidate_bound": candidate_bound,
        "witness_bounds": witness_bounds,
        "run_count": len(rows),
        "semiprime_front_by_witness_bound": [
            {
                "witness_bound": row["witness_bound"],
                "failed_count": row["failed_count"],
                "semiprime_rate": row["semiprime_rate"],
                "factor_min": row["factor_min"],
                "least_factor_delta_min": row["least_factor_delta_min"],
                "least_factor_delta_median": row["least_factor_delta_median"],
                "least_factor_delta_max": row["least_factor_delta_max"],
                "first_failure": row["first_failure"],
            }
            for row in rows
        ],
        "production_approved": False,
        "cryptographic_use_approved": False,
        "classical_factorization_scope": "downstream_failure_classification_only",
        "runtime_seconds": time.perf_counter() - started,
    }
    return rows, summary


def write_artifacts(
    rows: list[dict[str, Any]],
    summary: dict[str, Any],
    output_dir: Path,
) -> dict[str, Path]:
    """Write LF-terminated analysis artifacts."""
    output_dir.mkdir(parents=True, exist_ok=True)
    rows_path = output_dir / ROWS_FILENAME
    with rows_path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(jsonable(row), sort_keys=True) + "\n")

    summary_path = output_dir / SUMMARY_FILENAME
    summary_path.write_text(
        json.dumps(jsonable(summary), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return {"rows_path": rows_path, "summary_path": summary_path}


def main(argv: list[str] | None = None) -> int:
    """Run the witness-horizon semiprime analysis."""
    args = build_parser().parse_args(argv)
    rows, summary = run_analysis(
        start_anchor=args.start_anchor,
        max_anchor=args.max_anchor,
        candidate_bound=args.candidate_bound,
        witness_bounds=parse_witness_bounds(args.witness_bounds),
    )
    write_artifacts(rows, summary, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
