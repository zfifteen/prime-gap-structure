#!/usr/bin/env python3
"""Forensics for unresolved alternatives after locked-ceiling integration."""

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
        CANDIDATE_STATUS_RESOLVED_SURVIVOR,
        bounded_composite_witness,
        certified_divisor_class,
        run_probe,
        single_hole_positive_witness,
    )
except ImportError:  # pragma: no cover - direct script execution
    MODULE_DIR = Path(__file__).resolve().parent
    if str(MODULE_DIR) not in sys.path:
        sys.path.insert(0, str(MODULE_DIR))
    from composite_exclusion_boundary_probe import (
        CANDIDATE_STATUS_RESOLVED_SURVIVOR,
        bounded_composite_witness,
        certified_divisor_class,
        run_probe,
        single_hole_positive_witness,
    )


DEFAULT_OUTPUT_DIR = Path("output/prime_inference_generator")
SUMMARY_FILENAME = "unresolved_alternative_closure_forensics_summary.json"
RECORDS_FILENAME = "unresolved_alternative_closure_forensics_records.jsonl"
LOCK_PREDICATE = "unresolved_alternatives_before_threat"


def build_parser() -> argparse.ArgumentParser:
    """Build the unresolved-alternative forensics CLI."""
    parser = argparse.ArgumentParser(
        description="Offline unresolved-alternative closure forensics.",
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
        "--witness-bound",
        type=int,
        default=97,
        help="Largest positive witness factor.",
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
        return {
            str(key): int(count)
            for key, count in sorted(value.items(), key=lambda item: str(item[0]))
        }
    if isinstance(value, dict):
        return {key: jsonable(item) for key, item in value.items()}
    return value


def candidate_record_by_offset(row: dict[str, Any], offset: int) -> dict[str, Any]:
    """Return the candidate record for one offset."""
    for record in row["candidate_status_records"]:
        if int(record["offset"]) == offset:
            return record
    raise ValueError(f"candidate offset {offset} not present for anchor {row['anchor_p']}")


def missing_witness_records(
    anchor_p: int,
    offsets: list[int],
    witness_bound: int,
) -> list[dict[str, Any]]:
    """Return closure diagnostics for unresolved interior offsets."""
    records: list[dict[str, Any]] = []
    for offset in offsets:
        n = anchor_p + offset
        bounded_witness = bounded_composite_witness(n)
        extended_witness = single_hole_positive_witness(n, witness_bound)
        structural_certificate = certified_divisor_class(n, witness_bound)
        records.append(
            {
                "offset": offset,
                "n": n,
                "bounded_witness_factor": bounded_witness,
                "extended_witness_factor": extended_witness,
                "structural_certificate": structural_certificate,
                "positive_witness_available": (
                    bounded_witness is not None
                    or extended_witness is not None
                    or structural_certificate is not None
                ),
            }
        )
    return records


def carrier_status(
    anchor_p: int,
    candidate_offset: int,
    witness_bound: int,
) -> dict[str, Any]:
    """Return whether the candidate chamber has a legal composite carrier."""
    for offset in range(1, candidate_offset):
        certificate = certified_divisor_class(anchor_p + offset, witness_bound)
        if certificate is not None:
            return {
                "candidate_has_gwr_carrier": True,
                "carrier_offset": offset,
                "carrier_w": anchor_p + offset,
                "carrier_d": certificate["divisor_class"],
                "carrier_family": certificate["family"],
            }
    return {
        "candidate_has_gwr_carrier": False,
        "carrier_offset": None,
        "carrier_w": None,
        "carrier_d": None,
        "carrier_family": None,
    }


def threat_status(
    candidate_offset: int,
    ceiling: dict[str, Any],
) -> dict[str, Any]:
    """Return candidate position relative to the locked ceiling, if any."""
    if not bool(ceiling.get("applied")):
        return {
            "candidate_threat_status": "NO_LOCKED_CEILING",
            "threat_offset": None,
        }
    threat_offset = int(ceiling["threat_offset"])
    if candidate_offset < threat_offset:
        status = "BEFORE_LOCKED_THREAT"
    elif candidate_offset == threat_offset:
        status = "AT_LOCKED_THREAT"
    else:
        status = "AFTER_LOCKED_THREAT"
    return {
        "candidate_threat_status": status,
        "threat_offset": threat_offset,
    }


def unresolved_reason_counts(candidate_record: dict[str, Any]) -> Counter[str]:
    """Return unresolved reason counts for one candidate."""
    reasons = list(candidate_record["unresolved_reasons"])
    if not reasons:
        return Counter(["NO_UNRESOLVED_REASON"])
    return Counter(str(reason) for reason in reasons)


def closure_status(witness_records: list[dict[str, Any]]) -> str:
    """Return all-hole positive witness closure status."""
    if not witness_records:
        return "NO_OPEN_INTERIOR_HOLES"
    if all(bool(record["positive_witness_available"]) for record in witness_records):
        return "ALL_HOLES_POSITIVE_WITNESS_CLOSABLE"
    if any(bool(record["positive_witness_available"]) for record in witness_records):
        return "PARTIAL_POSITIVE_WITNESS_CLOSURE"
    return "NO_POSITIVE_WITNESS_CLOSURE"


def target_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return rows where true boundary is resolved but not unique."""
    return [
        row
        for row in rows
        if row["true_boundary_status"] == CANDIDATE_STATUS_RESOLVED_SURVIVOR
        and not bool(row["unique_resolved_survivor"])
    ]


def forensic_record(
    row: dict[str, Any],
    unresolved_offset: int,
    witness_bound: int,
) -> dict[str, Any]:
    """Return one unresolved alternative forensic record."""
    anchor_p = int(row["anchor_p"])
    actual = int(row["actual_boundary_offset_label"])
    candidate_record = candidate_record_by_offset(row, unresolved_offset)
    holes = [
        int(offset) for offset in candidate_record["unresolved_interior_offsets"]
    ]
    witness_records = missing_witness_records(anchor_p, holes, witness_bound)
    if unresolved_offset < actual:
        relation = "before_true"
    elif unresolved_offset > actual:
        relation = "after_true"
    else:
        relation = "at_true"
    ceiling = row["carrier_locked_pressure_ceiling"]
    carrier = carrier_status(anchor_p, unresolved_offset, witness_bound)
    threat = threat_status(unresolved_offset, ceiling)
    return {
        "anchor_p": anchor_p,
        "actual_boundary_offset_label": actual,
        "unresolved_candidate_offset": unresolved_offset,
        "unresolved_candidate_relation_to_true_boundary": relation,
        "unresolved_reason_counts": unresolved_reason_counts(candidate_record),
        "unclosed_open_interior_count": len(holes),
        "missing_witness_offsets": witness_records,
        **carrier,
        "candidate_closure_status": closure_status(witness_records),
        **threat,
        "candidate_bound_position": (
            "at_candidate_bound"
            if unresolved_offset == int(row["candidate_bound"])
            else "inside_candidate_bound"
        ),
        "candidate_pruned_by_locked_ceiling_bool": bool(
            candidate_record.get("carrier_locked_pressure_ceiling_rejection")
        ),
    }


def run_forensics(
    start_anchor: int,
    max_anchor: int,
    candidate_bound: int,
    witness_bound: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run unresolved-alternative closure forensics."""
    started = time.perf_counter()
    rows, probe_summary = run_probe(
        start_anchor=start_anchor,
        max_anchor=max_anchor,
        candidate_bound=candidate_bound,
        enable_single_hole_positive_witness_closure=True,
        witness_bound=witness_bound,
        enable_carrier_locked_pressure_ceiling=True,
        carrier_lock_predicate=LOCK_PREDICATE,
    )
    selected_rows = target_rows(rows)
    records: list[dict[str, Any]] = []
    for row in selected_rows:
        for unresolved_offset in row["unresolved"]:
            records.append(forensic_record(row, int(unresolved_offset), witness_bound))

    relation_counts = Counter(
        record["unresolved_candidate_relation_to_true_boundary"]
        for record in records
    )
    hole_count_distribution = Counter(
        int(record["unclosed_open_interior_count"]) for record in records
    )
    single_hole_count = sum(
        1 for record in records if int(record["unclosed_open_interior_count"]) == 1
    )
    multi_hole_count = sum(
        1 for record in records if int(record["unclosed_open_interior_count"]) > 1
    )
    missing_witness_bound_distribution = Counter()
    unresolved_reason_pattern_counts: Counter[str] = Counter()
    closure_status_counts = Counter(
        str(record["candidate_closure_status"]) for record in records
    )
    for record in records:
        unresolved_reason_pattern_counts.update(
            ["|".join(sorted(record["unresolved_reason_counts"].keys()))]
        )
        for witness in record["missing_witness_offsets"]:
            factor = witness["extended_witness_factor"]
            if factor is not None:
                missing_witness_bound_distribution.update([int(factor)])
            elif witness["bounded_witness_factor"] is not None:
                missing_witness_bound_distribution.update(
                    [int(witness["bounded_witness_factor"])]
                )
            elif witness["structural_certificate"] is not None:
                missing_witness_bound_distribution.update(["STRUCTURAL"])
            else:
                missing_witness_bound_distribution.update(["NO_WITNESS"])

    summary = {
        "mode": "offline_unresolved_alternative_closure_forensics",
        "start_anchor": start_anchor,
        "max_anchor": max_anchor,
        "candidate_bound": candidate_bound,
        "witness_bound": witness_bound,
        "single_hole_positive_witness_closure_enabled": True,
        "carrier_locked_pressure_ceiling_enabled": True,
        "carrier_lock_predicate": LOCK_PREDICATE,
        "target_row_count": len(selected_rows),
        "unresolved_alternative_count": len(records),
        "before_true_count": int(relation_counts["before_true"]),
        "after_true_count": int(relation_counts["after_true"]),
        "single_hole_count": single_hole_count,
        "multi_hole_count": multi_hole_count,
        "hole_count_distribution": hole_count_distribution,
        "missing_witness_bound_distribution": missing_witness_bound_distribution,
        "unresolved_reason_pattern_counts": unresolved_reason_pattern_counts,
        "candidate_closure_status_counts": closure_status_counts,
        "true_boundary_rejected_count": probe_summary[
            "true_boundary_rejected_count"
        ],
        "unique_resolved_survivor_count": probe_summary[
            "unique_resolved_survivor_count"
        ],
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
    """Run unresolved-alternative closure forensics and write artifacts."""
    args = build_parser().parse_args(argv)
    records, summary = run_forensics(
        start_anchor=args.start_anchor,
        max_anchor=args.max_anchor,
        candidate_bound=args.candidate_bound,
        witness_bound=args.witness_bound,
    )
    write_artifacts(records, summary, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
