#!/usr/bin/env python3
"""Offline probe for single unresolved interior-open chamber holes.

This script studies true-boundary candidates that remain UNRESOLVED because
exactly one wheel-open interior offset lacks a legal closure certificate. It
does not emit primes and does not use labels inside the closure tests.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

try:
    from .composite_exclusion_boundary_probe import (
        CANDIDATE_STATUS_UNRESOLVED,
        COMPOSITE_WITNESS_FACTORS,
        WHEEL_OPEN_RESIDUES_MOD30,
        bounded_composite_witness,
        run_probe,
    )
except ImportError:  # pragma: no cover - direct script execution
    MODULE_DIR = Path(__file__).resolve().parent
    if str(MODULE_DIR) not in sys.path:
        sys.path.insert(0, str(MODULE_DIR))
    from composite_exclusion_boundary_probe import (
        CANDIDATE_STATUS_UNRESOLVED,
        COMPOSITE_WITNESS_FACTORS,
        WHEEL_OPEN_RESIDUES_MOD30,
        bounded_composite_witness,
        run_probe,
    )

from sympy import divisor_count, factorint


DEFAULT_OUTPUT_DIR = Path("output/prime_inference_generator")
SUMMARY_FILENAME = "single_hole_closure_probe_summary.json"
RECORDS_FILENAME = "single_hole_closure_probe_records.jsonl"
EXTENDED_POSITIVE_WITNESS_FACTORS = (
    37,
    41,
    43,
    47,
    53,
    59,
    61,
    67,
    71,
    73,
    79,
    83,
    89,
    97,
)


def build_parser() -> argparse.ArgumentParser:
    """Build the single-hole closure probe CLI."""
    parser = argparse.ArgumentParser(
        description="Offline single-hole chamber closure probe.",
    )
    parser.add_argument(
        "--start-anchor",
        type=int,
        default=11,
        help="Inclusive lower bound for prime anchors.",
    )
    parser.add_argument(
        "--max-anchor",
        type=int,
        default=10_000,
        help="Inclusive upper bound for prime anchors.",
    )
    parser.add_argument(
        "--candidate-bound",
        type=int,
        default=64,
        help="Largest candidate boundary offset.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for JSON and JSONL artifacts.",
    )
    return parser


def jsonable(value: Any) -> Any:
    """Convert nested tuples and Counters into JSON-ready values."""
    if isinstance(value, tuple):
        return [jsonable(item) for item in value]
    if isinstance(value, list):
        return [jsonable(item) for item in value]
    if isinstance(value, Counter):
        return {str(key): int(count) for key, count in sorted(value.items())}
    if isinstance(value, dict):
        return {key: jsonable(item) for key, item in value.items()}
    return value


def record_by_offset(row: dict[str, Any], offset: int) -> dict[str, Any]:
    """Return the candidate status record for one offset."""
    for record in row["candidate_status_records"]:
        if int(record["offset"]) == offset:
            return record
    raise ValueError(f"candidate offset {offset} not present for anchor {row['anchor_p']}")


def extended_positive_witness(n: int) -> int | None:
    """Return an extended positive factor witness, if one is present."""
    for factor in EXTENDED_POSITIVE_WITNESS_FACTORS:
        if factor < n and n % factor == 0:
            return factor
    return None


def power_status(n: int) -> dict[str, Any]:
    """Return direct integer-power composite evidence for n."""
    witnesses: list[dict[str, int]] = []
    for exponent in range(2, 7):
        root = 1
        while root**exponent < n:
            root += 1
        if root > 1 and root**exponent == n:
            witnesses.append({"base": root, "exponent": exponent})
    return {
        "is_power": bool(witnesses),
        "witnesses": witnesses,
    }


def exact_family(n: int) -> str:
    """Return exact factorization family for offline diagnostics."""
    factors = factorint(n)
    exponent_sum = sum(int(exponent) for exponent in factors.values())
    if len(factors) == 1 and exponent_sum == 1:
        return "prime"
    if len(factors) == 1:
        return "prime_power"
    if exponent_sum == 2:
        return "semiprime"
    return "composite"


def legal_witness_for_offset(anchor_p: int, offset: int) -> dict[str, Any] | None:
    """Return a legal composite witness record for one offset, if known."""
    n = anchor_p + offset
    witness = bounded_composite_witness(n)
    if witness is not None:
        return {"offset": offset, "n": n, "witness_factor": witness}
    if n % 30 not in WHEEL_OPEN_RESIDUES_MOD30:
        for factor in (2, 3, 5):
            if n % factor == 0:
                return {"offset": offset, "n": n, "witness_factor": factor}
    return None


def known_witnesses(
    anchor_p: int,
    candidate_offset: int,
    hole_offset: int,
    side: str,
) -> list[dict[str, Any]]:
    """Return legal composite witnesses before or after the unresolved hole."""
    if side == "before":
        offsets = range(1, hole_offset)
    elif side == "after":
        offsets = range(hole_offset + 1, candidate_offset)
    else:
        raise ValueError(f"unknown side {side}")

    witnesses: list[dict[str, Any]] = []
    for offset in offsets:
        record = legal_witness_for_offset(anchor_p, offset)
        if record is not None:
            witnesses.append(record)
    return witnesses


def gwr_carrier_from_known_witnesses(
    witnesses: list[dict[str, Any]],
) -> dict[str, Any]:
    """Return an offline GWR carrier from known composite witnesses."""
    if not witnesses:
        return {
            "gwr_carrier_w": None,
            "gwr_carrier_offset": None,
            "gwr_carrier_divisor_count": None,
        }
    carrier = min(
        witnesses,
        key=lambda record: (
            int(divisor_count(record["n"])),
            int(record["offset"]),
        ),
    )
    return {
        "gwr_carrier_w": int(carrier["n"]),
        "gwr_carrier_offset": int(carrier["offset"]),
        "gwr_carrier_divisor_count": int(divisor_count(carrier["n"])),
    }


def hole_relative_to_carrier(hole_offset: int, carrier_offset: int | None) -> str:
    """Return the hole position relative to the current carrier."""
    if carrier_offset is None:
        return "NO_CARRIER"
    if hole_offset < carrier_offset:
        return "BEFORE_CARRIER"
    if hole_offset == carrier_offset:
        return "AT_CARRIER"
    return "AFTER_CARRIER"


def closure_candidates(hole_n: int) -> list[str]:
    """Return legal closure candidates available for the hole."""
    candidates: list[str] = []
    if power_status(hole_n)["is_power"]:
        candidates.append("power_closure")
    if extended_positive_witness(hole_n) is not None:
        candidates.append("small_factor_positive_witness_closure")
    return candidates


def candidate_missing_rule(closure_rule_candidates: list[str]) -> str:
    """Return the missing-rule status for one single-hole case."""
    if closure_rule_candidates:
        return "LEGAL_CLOSURE_CANDIDATE_AVAILABLE"
    return "NEEDS_DOMINATION_OR_NEW_CLOSURE_CERTIFICATE"


def single_hole_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return rows where the true boundary is unresolved by exactly one hole."""
    selected: list[dict[str, Any]] = []
    for row in rows:
        if row["true_boundary_status"] != CANDIDATE_STATUS_UNRESOLVED:
            continue
        actual_offset = int(row["actual_boundary_offset_label"])
        actual_record = record_by_offset(row, actual_offset)
        if len(actual_record["unresolved_interior_offsets"]) == 1:
            selected.append(row)
    return selected


def forensic_record(row: dict[str, Any]) -> dict[str, Any]:
    """Return one single-hole closure forensic record."""
    anchor_p = int(row["anchor_p"])
    actual_offset = int(row["actual_boundary_offset_label"])
    actual_record = record_by_offset(row, actual_offset)
    hole_offset = int(actual_record["unresolved_interior_offsets"][0])
    hole_n = anchor_p + hole_offset
    before = known_witnesses(anchor_p, actual_offset, hole_offset, "before")
    after = known_witnesses(anchor_p, actual_offset, hole_offset, "after")
    carrier = gwr_carrier_from_known_witnesses(before + after)
    power = power_status(hole_n)
    extended_witness = extended_positive_witness(hole_n)
    active_witness = bounded_composite_witness(hole_n)
    exact_d = int(divisor_count(hole_n))
    family = exact_family(hole_n)
    closure_rule_candidates = closure_candidates(hole_n)

    return {
        "anchor_p": anchor_p,
        "actual_boundary_offset_label": actual_offset,
        "unresolved_open_offset": hole_offset,
        "unresolved_open_n": hole_n,
        "resolved_survivor_offset": (
            int(row["survivors"][0]) if row["survivors"] else None
        ),
        "candidate_chamber_width": actual_offset - 1,
        "known_composite_witnesses_before_hole": before,
        "known_composite_witnesses_after_hole": after,
        **carrier,
        "hole_relative_to_carrier": hole_relative_to_carrier(
            hole_offset,
            carrier["gwr_carrier_offset"],
        ),
        "hole_wheel_residue": hole_n % 30,
        "hole_square_status": {
            "is_square": math.isqrt(hole_n) ** 2 == hole_n,
            "root": math.isqrt(hole_n) if math.isqrt(hole_n) ** 2 == hole_n else None,
        },
        "hole_power_status": power,
        "hole_small_factor_witness_status": {
            "active_witness_factor": active_witness,
            "extended_witness_factor": extended_witness,
            "active_witness_factors": COMPOSITE_WITNESS_FACTORS,
            "extended_witness_factors": EXTENDED_POSITIVE_WITNESS_FACTORS,
        },
        "hole_semiprime_pressure": {
            "offline_exact_family": family,
            "is_semiprime": family == "semiprime",
        },
        "hole_higher_divisor_pressure": {
            "offline_exact_divisor_count": exact_d,
            "is_high_divisor": exact_d >= 6,
        },
        "closure_rule_candidates": closure_rule_candidates,
        "candidate_missing_rule": candidate_missing_rule(closure_rule_candidates),
    }


def run_closure_probe(
    start_anchor: int,
    max_anchor: int,
    candidate_bound: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run single-hole closure forensics."""
    started = time.perf_counter()
    rows, probe_summary = run_probe(
        start_anchor=start_anchor,
        max_anchor=max_anchor,
        candidate_bound=candidate_bound,
    )
    target_rows = single_hole_rows(rows)
    records = [forensic_record(row) for row in target_rows]
    closure_counter: Counter[str] = Counter()
    missing_rule_counter: Counter[str] = Counter()
    hole_relative_counter: Counter[str] = Counter()
    exact_family_counter: Counter[str] = Counter()
    divisor_count_counter: Counter[int] = Counter()
    for record in records:
        closure_counter.update(record["closure_rule_candidates"])
        missing_rule_counter.update([record["candidate_missing_rule"]])
        hole_relative_counter.update([record["hole_relative_to_carrier"]])
        exact_family_counter.update([record["hole_semiprime_pressure"]["offline_exact_family"]])
        divisor_count_counter.update(
            [int(record["hole_higher_divisor_pressure"]["offline_exact_divisor_count"])]
        )

    summary = {
        "mode": "offline_single_hole_closure_probe",
        "start_anchor": start_anchor,
        "max_anchor": max_anchor,
        "candidate_bound": candidate_bound,
        "row_count": probe_summary["row_count"],
        "true_boundary_unresolved_count": int(
            probe_summary["true_boundary_status_counts"].get("UNRESOLVED", 0)
        ),
        "single_hole_case_count": len(records),
        "single_hole_closure_candidate_count": sum(
            1 for record in records if record["closure_rule_candidates"]
        ),
        "power_closure_count": closure_counter["power_closure"],
        "small_factor_positive_witness_closure_count": closure_counter[
            "small_factor_positive_witness_closure"
        ],
        "true_boundary_rejected_count": probe_summary[
            "true_boundary_rejected_count"
        ],
        "candidate_missing_rule_counts": missing_rule_counter,
        "closure_rule_candidate_counts": closure_counter,
        "hole_relative_to_carrier_counts": hole_relative_counter,
        "hole_exact_family_counts": exact_family_counter,
        "hole_exact_divisor_count_distribution": divisor_count_counter,
        "first_records": records[:5],
        "boundary_law_005_status": "not_approved",
        "runtime_seconds": time.perf_counter() - started,
    }
    return records, summary


def write_artifacts(
    records: list[dict[str, Any]],
    summary: dict[str, Any],
    output_dir: Path,
) -> dict[str, Path]:
    """Write LF-terminated JSONL records and JSON summary."""
    output_dir.mkdir(parents=True, exist_ok=True)
    records_path = output_dir / RECORDS_FILENAME
    with records_path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(jsonable(record), sort_keys=True) + "\n")

    summary_path = output_dir / SUMMARY_FILENAME
    summary_path.write_text(
        json.dumps(jsonable(summary), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return {"records_path": records_path, "summary_path": summary_path}


def main(argv: list[str] | None = None) -> int:
    """Run the single-hole closure probe and write artifacts."""
    args = build_parser().parse_args(argv)
    records, summary = run_closure_probe(
        start_anchor=args.start_anchor,
        max_anchor=args.max_anchor,
        candidate_bound=args.candidate_bound,
    )
    write_artifacts(records, summary, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
