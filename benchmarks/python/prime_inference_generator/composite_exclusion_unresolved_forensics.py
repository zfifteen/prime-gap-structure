#!/usr/bin/env python3
"""Forensics for true-boundary-unresolved composite-exclusion cases.

This script is offline theorem discovery. It runs the composite-exclusion probe,
then inspects only rows where the classical next-boundary label remained
UNRESOLVED after label-free elimination.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

try:
    from .composite_exclusion_boundary_probe import (
        CANDIDATE_STATUS_UNRESOLVED,
        run_probe,
    )
except ImportError:  # pragma: no cover - direct script execution
    MODULE_DIR = Path(__file__).resolve().parent
    if str(MODULE_DIR) not in sys.path:
        sys.path.insert(0, str(MODULE_DIR))
    from composite_exclusion_boundary_probe import (
        CANDIDATE_STATUS_UNRESOLVED,
        run_probe,
    )


DEFAULT_OUTPUT_DIR = Path("output/prime_inference_generator")
SUMMARY_FILENAME = "composite_exclusion_unresolved_forensics_summary.json"
RECORDS_FILENAME = "composite_exclusion_unresolved_forensics_records.jsonl"


def build_parser() -> argparse.ArgumentParser:
    """Build the unresolved-boundary forensics CLI."""
    parser = argparse.ArgumentParser(
        description="Offline forensics for true-boundary-unresolved rows.",
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


def missing_evidence_for_candidate(candidate_record: dict[str, Any]) -> list[str]:
    """Return missing evidence categories for one unresolved candidate."""
    missing: list[str] = []
    unresolved_reasons = set(candidate_record["unresolved_reasons"])
    if "UNRESOLVED_INTERIOR_OPEN" in unresolved_reasons:
        missing.extend(
            [
                "unclosed_open_interior",
                "insufficient_composite_witness",
                "closure_not_certified",
            ]
        )
    if candidate_record["status"] == CANDIDATE_STATUS_UNRESOLVED:
        missing.append("unresolved_alternative_domination")
    return missing


def resolving_rule_candidates(candidate_record: dict[str, Any]) -> list[str]:
    """Return PGS rule families that could resolve the missing evidence."""
    candidates: list[str] = []
    unresolved_reasons = set(candidate_record["unresolved_reasons"])
    if "UNRESOLVED_INTERIOR_OPEN" in unresolved_reasons:
        candidates.append("legal_composite_closure_certificate")
        candidates.append("bounded_witness_extension")
    if candidate_record["status"] == CANDIDATE_STATUS_UNRESOLVED:
        candidates.append("unresolved_alternative_domination_lemma")
    return candidates


def forensic_record(row: dict[str, Any]) -> dict[str, Any]:
    """Return one unresolved-true-boundary forensic record."""
    actual_offset = int(row["actual_boundary_offset_label"])
    resolved_survivor = int(row["survivors"][0]) if row["survivors"] else None
    actual_record = record_by_offset(row, actual_offset)
    survivor_record = (
        record_by_offset(row, resolved_survivor)
        if resolved_survivor is not None
        else None
    )
    missing_evidence = missing_evidence_for_candidate(actual_record)
    resolving_rules = resolving_rule_candidates(actual_record)
    unresolved_interior_offsets = [
        int(offset) for offset in actual_record["unresolved_interior_offsets"]
    ]

    return {
        "anchor_p": int(row["anchor_p"]),
        "resolved_survivor": resolved_survivor,
        "actual_boundary_label": actual_offset,
        "unresolved_true_boundary_candidate": actual_offset,
        "survivor_to_actual_delta": (
            None if resolved_survivor is None else actual_offset - resolved_survivor
        ),
        "why_resolved_survivor_survived": {
            "status": None if survivor_record is None else survivor_record["status"],
            "rejection_reasons": (
                [] if survivor_record is None else survivor_record["rejection_reasons"]
            ),
            "unresolved_reasons": (
                [] if survivor_record is None else survivor_record["unresolved_reasons"]
            ),
            "unresolved_interior_offsets": (
                []
                if survivor_record is None
                else survivor_record["unresolved_interior_offsets"]
            ),
        },
        "why_true_boundary_was_unresolved": {
            "status": actual_record["status"],
            "unresolved_reasons": actual_record["unresolved_reasons"],
            "unresolved_interior_offsets": unresolved_interior_offsets,
            "unresolved_interior_count": len(unresolved_interior_offsets),
        },
        "which_evidence_was_missing": missing_evidence,
        "which_pgs_rule_would_resolve_it": resolving_rules,
    }


def run_forensics(
    start_anchor: int,
    max_anchor: int,
    candidate_bound: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run unresolved-boundary forensics."""
    started = time.perf_counter()
    rows, probe_summary = run_probe(
        start_anchor=start_anchor,
        max_anchor=max_anchor,
        candidate_bound=candidate_bound,
    )
    unresolved_rows = [
        row
        for row in rows
        if row["true_boundary_status"] == CANDIDATE_STATUS_UNRESOLVED
    ]
    records = [forensic_record(row) for row in unresolved_rows]
    missing_counts: Counter[str] = Counter()
    resolving_rule_counts: Counter[str] = Counter()
    unresolved_interior_count_distribution: Counter[int] = Counter()
    delta_distribution: Counter[int] = Counter()
    for record in records:
        missing_counts.update(record["which_evidence_was_missing"])
        resolving_rule_counts.update(record["which_pgs_rule_would_resolve_it"])
        unresolved_interior_count_distribution.update(
            [int(record["why_true_boundary_was_unresolved"]["unresolved_interior_count"])]
        )
        if record["survivor_to_actual_delta"] is not None:
            delta_distribution.update([int(record["survivor_to_actual_delta"])])

    summary = {
        "mode": "offline_composite_exclusion_unresolved_forensics",
        "start_anchor": start_anchor,
        "max_anchor": max_anchor,
        "candidate_bound": candidate_bound,
        "row_count": probe_summary["row_count"],
        "true_boundary_unresolved_count": len(records),
        "true_boundary_rejected_count": probe_summary[
            "true_boundary_rejected_count"
        ],
        "resolved_survivor_count": probe_summary["unique_survivor_count"],
        "unique_resolved_survivor_count": probe_summary[
            "unique_resolved_survivor_count"
        ],
        "missing_evidence_counts": missing_counts,
        "candidate_resolving_rule_counts": resolving_rule_counts,
        "unresolved_interior_count_distribution": (
            unresolved_interior_count_distribution
        ),
        "survivor_to_actual_delta_distribution": delta_distribution,
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
    """Run unresolved-boundary forensics and write artifacts."""
    args = build_parser().parse_args(argv)
    records, summary = run_forensics(
        start_anchor=args.start_anchor,
        max_anchor=args.max_anchor,
        candidate_bound=args.candidate_bound,
    )
    write_artifacts(records, summary, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
