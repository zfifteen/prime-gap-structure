#!/usr/bin/env python3
"""Offline composite-exclusion boundary probe.

This script is theorem discovery, not pure generation. The elimination pass
uses only bounded positive composite witnesses. Classical labels are attached
after elimination to measure whether the true boundary was preserved.
"""

from __future__ import annotations

import argparse
import json
import statistics
import time
from collections import Counter
from pathlib import Path
from typing import Any

from sympy import primerange


DEFAULT_OUTPUT_DIR = Path("output/prime_inference_generator")
SUMMARY_FILENAME = "composite_exclusion_boundary_probe_summary.json"
ROWS_FILENAME = "composite_exclusion_boundary_probe_rows.jsonl"
WHEEL_OPEN_RESIDUES_MOD30 = frozenset({1, 7, 11, 13, 17, 19, 23, 29})
COMPOSITE_WITNESS_FACTORS = (7, 11, 13, 17, 19, 23, 29, 31)
CANDIDATE_STATUS_RESOLVED_SURVIVOR = "RESOLVED_SURVIVOR"
CANDIDATE_STATUS_REJECTED = "REJECTED"
CANDIDATE_STATUS_UNRESOLVED = "UNRESOLVED"
RULE_FAMILIES = [
    "wheel_closed_rejection",
    "positive_composite_witness_rejection",
    "interior_open_unclosed_rejection",
    "gwr_incompatibility_rejection",
    "no_later_simpler_violation_rejection",
    "square_pressure_rejection",
    "carrier_absence_rejection",
]


def build_parser() -> argparse.ArgumentParser:
    """Build the composite-exclusion probe CLI."""
    parser = argparse.ArgumentParser(
        description="Offline composite-exclusion boundary probe.",
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


def candidate_offsets(anchor_p: int, candidate_bound: int) -> list[int]:
    """Return wheel-open candidate offsets within the finite bound."""
    return [
        offset
        for offset in range(1, candidate_bound + 1)
        if (anchor_p + offset) % 30 in WHEEL_OPEN_RESIDUES_MOD30
    ]


def bounded_composite_witness(n: int) -> int | None:
    """Return a bounded positive composite witness for n, if one is present."""
    for factor in COMPOSITE_WITNESS_FACTORS:
        if factor < n and n % factor == 0:
            return factor
    return None


def interior_open_offsets(anchor_p: int, candidate_offset: int) -> list[int]:
    """Return wheel-open interior offsets before a proposed boundary."""
    return [
        offset
        for offset in range(1, candidate_offset)
        if (anchor_p + offset) % 30 in WHEEL_OPEN_RESIDUES_MOD30
    ]


def classify_candidate(anchor_p: int, candidate_offset: int) -> dict[str, Any]:
    """Return the label-free status for one proposed boundary candidate."""
    candidate = anchor_p + candidate_offset
    witness = bounded_composite_witness(candidate)
    if witness is not None:
        return {
            "offset": candidate_offset,
            "status": CANDIDATE_STATUS_REJECTED,
            "rejection_reasons": [f"BOUNDED_COMPOSITE_WITNESS_FACTOR_{witness}"],
            "unresolved_reasons": [],
            "unresolved_interior_offsets": [],
            "rule_family": "positive_composite_witness_rejection",
        }

    unresolved_offsets = [
        offset
        for offset in interior_open_offsets(anchor_p, candidate_offset)
        if bounded_composite_witness(anchor_p + offset) is None
    ]
    if unresolved_offsets:
        return {
            "offset": candidate_offset,
            "status": CANDIDATE_STATUS_UNRESOLVED,
            "rejection_reasons": [],
            "unresolved_reasons": ["UNRESOLVED_INTERIOR_OPEN"],
            "unresolved_interior_offsets": unresolved_offsets,
            "rule_family": "interior_open_unclosed_rejection",
        }

    return {
        "offset": candidate_offset,
        "status": CANDIDATE_STATUS_RESOLVED_SURVIVOR,
        "rejection_reasons": [],
        "unresolved_reasons": [],
        "unresolved_interior_offsets": [],
        "rule_family": None,
    }


def eliminate_candidates(anchor_p: int, candidate_bound: int) -> dict[str, Any]:
    """Run label-free composite exclusion for one anchor."""
    offsets = candidate_offsets(anchor_p, candidate_bound)
    candidate_records = [classify_candidate(anchor_p, offset) for offset in offsets]
    survivors = [
        int(record["offset"])
        for record in candidate_records
        if record["status"] == CANDIDATE_STATUS_RESOLVED_SURVIVOR
    ]
    unresolved = [
        int(record["offset"])
        for record in candidate_records
        if record["status"] == CANDIDATE_STATUS_UNRESOLVED
    ]
    rejected = [
        int(record["offset"])
        for record in candidate_records
        if record["status"] == CANDIDATE_STATUS_REJECTED
    ]
    rejection_reasons = {
        str(record["offset"]): list(record["rejection_reasons"])
        for record in candidate_records
    }
    unresolved_reasons = {
        str(record["offset"]): list(record["unresolved_reasons"])
        for record in candidate_records
    }
    candidate_status_by_offset = {
        str(record["offset"]): record["status"] for record in candidate_records
    }

    return {
        "anchor_p": anchor_p,
        "candidate_bound": candidate_bound,
        "candidate_offsets": offsets,
        "candidate_count": len(offsets),
        "rejected_count": len(rejected),
        "unresolved_count": len(unresolved),
        "survives_count": len(survivors),
        "survivor_count": len(survivors),
        "rejected": rejected,
        "unresolved": unresolved,
        "survivors": survivors,
        "rejection_reasons_by_candidate": rejection_reasons,
        "unresolved_reasons_by_candidate": unresolved_reasons,
        "candidate_status_by_offset": candidate_status_by_offset,
        "candidate_status_records": candidate_records,
    }


def label_offsets(start_anchor: int, max_anchor: int, candidate_bound: int) -> dict[int, int]:
    """Return classical next-gap labels for reporting after elimination."""
    label_extension = max(10_000, candidate_bound * 16)
    primes = [
        int(prime)
        for prime in primerange(start_anchor, max_anchor + label_extension + 1)
    ]
    anchors = [prime for prime in primes if start_anchor <= prime <= max_anchor]
    if not anchors:
        raise ValueError("surface contains no prime anchors")

    labels: dict[int, int] = {}
    prime_index = {prime: index for index, prime in enumerate(primes)}
    for anchor in anchors:
        index = prime_index[anchor]
        if index + 1 >= len(primes):
            raise ValueError("label extension did not include the next prime")
        labels[anchor] = primes[index + 1] - anchor
    return labels


def attach_label(record: dict[str, Any], actual_boundary_offset: int) -> dict[str, Any]:
    """Attach the post-elimination classical boundary label."""
    survivors = list(record["survivors"])
    unresolved = list(record["unresolved"])
    candidate_offsets_list = list(record["candidate_offsets"])
    unique_survivor = survivors[0] if len(survivors) == 1 else None
    true_boundary_status = (
        str(record["candidate_status_by_offset"][str(actual_boundary_offset)])
        if actual_boundary_offset in candidate_offsets_list
        else "OUT_OF_BOUND"
    )
    true_boundary_rejected = true_boundary_status == CANDIDATE_STATUS_REJECTED
    unique_match = (
        unique_survivor is not None and unique_survivor == actual_boundary_offset
    )
    unique_resolved_survivor = len(survivors) == 1 and len(unresolved) == 0

    if true_boundary_rejected:
        failure_reason = "TRUE_BOUNDARY_REJECTED"
    elif true_boundary_status == "OUT_OF_BOUND":
        failure_reason = "TRUE_BOUNDARY_OUT_OF_BOUND"
    elif unique_resolved_survivor and unique_match:
        failure_reason = None
    elif unique_resolved_survivor:
        failure_reason = "UNIQUE_RESOLVED_SURVIVOR_LABEL_MISMATCH"
    elif not survivors and not unresolved:
        failure_reason = "NO_SURVIVOR"
    else:
        failure_reason = "NO_UNIQUE_BOUNDARY"

    labeled = dict(record)
    labeled.update(
        {
            "actual_boundary_offset_label": actual_boundary_offset,
            "actual_boundary_within_candidate_bound": (
                actual_boundary_offset in candidate_offsets_list
            ),
            "true_boundary_rejected": true_boundary_rejected,
            "true_boundary_status": true_boundary_status,
            "unique_resolved_survivor": unique_resolved_survivor,
            "unique_survivor_matches_label": unique_match,
            "failure_reason": failure_reason,
        }
    )
    return labeled


def rule_family_report(rows: list[dict[str, Any]], rule_family: str) -> dict[str, Any]:
    """Return per-rule-family rejection and ablation metrics."""
    rejected_count = 0
    unresolved_count = 0
    true_boundary_rejected_count = 0
    survivor_counts_after_rule: list[int] = []
    unique_survivor_count_after_rule = 0
    for row in rows:
        candidate_count = int(row["candidate_count"])
        actual = int(row["actual_boundary_offset_label"])
        rejected_offsets: set[int] = set()
        unresolved_offsets: set[int] = set()
        for record in row["candidate_status_records"]:
            offset = int(record["offset"])
            if (
                rule_family == "positive_composite_witness_rejection"
                and record["status"] == CANDIDATE_STATUS_REJECTED
            ):
                rejected_offsets.add(offset)
            elif (
                rule_family == "interior_open_unclosed_rejection"
                and record["status"] == CANDIDATE_STATUS_UNRESOLVED
            ):
                unresolved_offsets.add(offset)

        survivors_after_rule = candidate_count - len(rejected_offsets) - len(
            unresolved_offsets
        )
        survivor_counts_after_rule.append(survivors_after_rule)
        if survivors_after_rule == 1:
            unique_survivor_count_after_rule += 1
        if actual in rejected_offsets:
            true_boundary_rejected_count += 1
        rejected_count += len(rejected_offsets)
        unresolved_count += len(unresolved_offsets)

    return {
        "rule_family": rule_family,
        "rejected_count": rejected_count,
        "unresolved_count": unresolved_count,
        "true_boundary_rejected_count": true_boundary_rejected_count,
        "average_survivor_count_after_rule": statistics.fmean(
            survivor_counts_after_rule
        ),
        "marginal_rejection_count": rejected_count,
        "unique_survivor_count_after_rule": unique_survivor_count_after_rule,
    }


def run_probe(
    start_anchor: int,
    max_anchor: int,
    candidate_bound: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run label-free elimination, then attach labels for reporting."""
    if candidate_bound < 1:
        raise ValueError("candidate_bound must be at least 1")
    if max_anchor < start_anchor:
        raise ValueError("max_anchor must be at least start_anchor")

    started = time.perf_counter()
    labels = label_offsets(start_anchor, max_anchor, candidate_bound)
    rows = [
        attach_label(eliminate_candidates(anchor_p, candidate_bound), label)
        for anchor_p, label in labels.items()
    ]
    unique_rows = [row for row in rows if int(row["survivor_count"]) == 1]
    unique_resolved_rows = [
        row
        for row in rows
        if int(row["survivor_count"]) == 1 and int(row["unresolved_count"]) == 0
    ]
    true_boundary_rejected_rows = [
        row for row in rows if bool(row["true_boundary_rejected"])
    ]
    unique_match_rows = [
        row for row in unique_rows if bool(row["unique_survivor_matches_label"])
    ]
    no_survivor_count = sum(1 for row in rows if int(row["survivor_count"]) == 0)
    no_unique_count = len(rows) - len(unique_resolved_rows)
    survivor_counts = [int(row["survivor_count"]) for row in rows]
    unresolved_counts = [int(row["unresolved_count"]) for row in rows]
    rejected_counts = [int(row["rejected_count"]) for row in rows]
    candidate_counts = [int(row["candidate_count"]) for row in rows]
    first_failure_examples = [
        row
        for row in rows
        if row["failure_reason"] not in (None, "NO_UNIQUE_BOUNDARY")
    ][:5]
    rule_reports = [
        rule_family_report(rows, rule_family) for rule_family in RULE_FAMILIES
    ]

    summary = {
        "mode": "offline_composite_exclusion_boundary_probe",
        "start_anchor": start_anchor,
        "max_anchor": max_anchor,
        "candidate_bound": candidate_bound,
        "row_count": len(rows),
        "unique_survivor_count": len(unique_rows),
        "unique_resolved_survivor_count": len(unique_resolved_rows),
        "no_survivor_count": no_survivor_count,
        "no_unique_boundary_count": no_unique_count,
        "true_boundary_rejected_count": len(true_boundary_rejected_rows),
        "unique_survivor_match_count": len(unique_match_rows),
        "unique_survivor_match_rate": (
            0.0 if not unique_rows else len(unique_match_rows) / len(unique_rows)
        ),
        "average_candidate_count": statistics.fmean(candidate_counts),
        "average_rejected_count": statistics.fmean(rejected_counts),
        "average_unresolved_count": statistics.fmean(unresolved_counts),
        "average_survives_count": statistics.fmean(survivor_counts),
        "average_survivor_count": statistics.fmean(survivor_counts),
        "survivor_count_distribution": Counter(survivor_counts),
        "unresolved_count_distribution": Counter(unresolved_counts),
        "true_boundary_status_counts": Counter(
            str(row["true_boundary_status"]) for row in rows
        ),
        "rule_family_reports": rule_reports,
        "first_failure_examples": first_failure_examples,
        "elimination_rule_set": "composite_exclusion_three_status_v1",
        "boundary_law_005_status": "not_approved",
        "runtime_seconds": time.perf_counter() - started,
    }
    return rows, summary


def write_artifacts(
    rows: list[dict[str, Any]],
    summary: dict[str, Any],
    output_dir: Path,
) -> dict[str, Path]:
    """Write LF-terminated JSONL rows and JSON summary."""
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
    """Run the composite-exclusion boundary probe and write artifacts."""
    args = build_parser().parse_args(argv)
    rows, summary = run_probe(
        start_anchor=args.start_anchor,
        max_anchor=args.max_anchor,
        candidate_bound=args.candidate_bound,
    )
    write_artifacts(rows, summary, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
