#!/usr/bin/env python3
"""Forensics for resolved-boundary absorption safety.

This probe tests resolved-chamber absorption as an offline hypothesis only. It
does not add a generator rule and does not approve Boundary Law 005.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

try:
    from .composite_exclusion_boundary_probe import (
        WHEEL_OPEN_RESIDUES_MOD30,
        certified_divisor_class,
        run_probe,
    )
except ImportError:  # pragma: no cover - direct script execution
    MODULE_DIR = Path(__file__).resolve().parent
    if str(MODULE_DIR) not in sys.path:
        sys.path.insert(0, str(MODULE_DIR))
    from composite_exclusion_boundary_probe import (
        WHEEL_OPEN_RESIDUES_MOD30,
        certified_divisor_class,
        run_probe,
    )


DEFAULT_OUTPUT_DIR = Path("output/prime_inference_generator")
SUMMARY_FILENAME = "resolved_boundary_absorption_safety_probe_summary.json"
RECORDS_FILENAME = "resolved_boundary_absorption_safety_probe_records.jsonl"
LOCK_PREDICATE = "unresolved_alternatives_before_threat"

STATUS_SAFE_TRUE = "ABSORPTION_SAFE_TRUE"
STATUS_UNSAFE_FALSE = "ABSORPTION_UNSAFE_FALSE"
STATUS_NONSELECTIVE = "ABSORPTION_NONSELECTIVE"
STATUS_ABSTAINS = "ABSORPTION_ABSTAINS"


def build_parser() -> argparse.ArgumentParser:
    """Build the absorption safety probe CLI."""
    parser = argparse.ArgumentParser(
        description="Offline resolved-boundary absorption safety probe.",
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


def candidate_carrier(
    anchor_p: int,
    candidate_offset: int,
    witness_bound: int,
) -> dict[str, Any]:
    """Return the first legal composite carrier inside a candidate chamber."""
    for offset in range(1, candidate_offset):
        certificate = certified_divisor_class(anchor_p + offset, witness_bound)
        if certificate is None:
            continue
        return {
            "carrier_offset": offset,
            "carrier_w": anchor_p + offset,
            "carrier_d": int(certificate["divisor_class"]),
            "carrier_family": str(certificate["family"]),
        }
    return {
        "carrier_offset": None,
        "carrier_w": None,
        "carrier_d": None,
        "carrier_family": None,
    }


def carrier_identity(carrier: dict[str, Any]) -> tuple[Any, ...]:
    """Return the comparable identity for a carrier record."""
    return (
        carrier["carrier_offset"],
        carrier["carrier_d"],
        carrier["carrier_family"],
    )


def interval_pressure(
    anchor_p: int,
    start_offset: int,
    end_offset: int,
    carrier_d: int | None,
    witness_bound: int,
) -> dict[str, Any]:
    """Return legal reset and pressure evidence between two offsets."""
    reset_offsets: list[int] = []
    higher_offsets: list[int] = []
    square_offsets: list[int] = []
    semiprime_offsets: list[int] = []
    for offset in range(start_offset + 1, end_offset):
        n = anchor_p + offset
        certificate = certified_divisor_class(n, witness_bound)
        if certificate is None:
            continue
        divisor_class = int(certificate["divisor_class"])
        family = str(certificate["family"])
        if carrier_d is not None and divisor_class <= carrier_d:
            reset_offsets.append(offset)
        if carrier_d is not None and divisor_class > carrier_d:
            higher_offsets.append(offset)
        if family == "known_basis_semiprime":
            semiprime_offsets.append(offset)
        payload = certificate["certificate"]
        if (
            family == "known_basis_prime_power"
            and int(payload.get("exponent", 0)) == 2
        ):
            square_offsets.append(offset)

    return {
        "reset_evidence_offsets": reset_offsets,
        "higher_divisor_pressure_offsets": higher_offsets,
        "square_pressure_offsets": square_offsets,
        "semiprime_pressure_offsets": semiprime_offsets,
    }


def raw_absorption_record(
    row: dict[str, Any],
    resolved_offset: int,
    witness_bound: int,
) -> dict[str, Any]:
    """Return one resolved-candidate absorption record before status assignment."""
    anchor_p = int(row["anchor_p"])
    actual = int(row["actual_boundary_offset_label"])
    unresolved_offsets = [int(offset) for offset in row["unresolved"]]
    later_unresolved = [
        offset for offset in unresolved_offsets if offset > resolved_offset
    ]
    resolved_is_wheel_open = (
        (anchor_p + resolved_offset) % 30 in WHEEL_OPEN_RESIDUES_MOD30
    )
    wheel_open_inside_later_count = (
        len(later_unresolved) if resolved_is_wheel_open else 0
    )
    absorbs_all = (
        bool(later_unresolved)
        and wheel_open_inside_later_count == len(later_unresolved)
    )
    resolved_carrier = candidate_carrier(anchor_p, resolved_offset, witness_bound)
    resolved_identity = carrier_identity(resolved_carrier)
    later_carriers = [
        {
            "candidate_offset": offset,
            **candidate_carrier(anchor_p, offset, witness_bound),
        }
        for offset in later_unresolved
    ]
    later_identities = [
        carrier_identity(record) for record in later_carriers
    ]
    carrier_shared = (
        bool(later_identities)
        and all(identity == resolved_identity for identity in later_identities)
    )
    extension_changes_carrier = any(
        identity != resolved_identity for identity in later_identities
    )
    pressure_records = [
        interval_pressure(
            anchor_p,
            resolved_offset,
            offset,
            resolved_carrier["carrier_d"],
            witness_bound,
        )
        for offset in later_unresolved
    ]
    reset_offsets = sorted(
        {
            reset_offset
            for pressure in pressure_records
            for reset_offset in pressure["reset_evidence_offsets"]
        }
    )
    higher_offsets = sorted(
        {
            pressure_offset
            for pressure in pressure_records
            for pressure_offset in pressure["higher_divisor_pressure_offsets"]
        }
    )
    square_offsets = sorted(
        {
            square_offset
            for pressure in pressure_records
            for square_offset in pressure["square_pressure_offsets"]
        }
    )
    semiprime_offsets = sorted(
        {
            semiprime_offset
            for pressure in pressure_records
            for semiprime_offset in pressure["semiprime_pressure_offsets"]
        }
    )
    would_eliminate_true = (
        resolved_offset != actual and actual in later_unresolved
    )
    would_select_false = resolved_offset != actual and absorbs_all
    return {
        "anchor_p": anchor_p,
        "actual_boundary_offset_label": actual,
        "resolved_survivor_offsets": [int(offset) for offset in row["survivors"]],
        "false_resolved_survivor_offsets": [
            int(offset) for offset in row["survivors"] if int(offset) != actual
        ],
        "unresolved_candidate_offsets": unresolved_offsets,
        "resolved_candidate_offset": resolved_offset,
        "resolved_candidate_is_true_label": resolved_offset == actual,
        "later_unresolved_candidate_offsets": later_unresolved,
        "resolved_candidate_wheel_open_inside_later_count": (
            wheel_open_inside_later_count
        ),
        "absorbs_all_later_unresolved_bool": absorbs_all,
        "carrier_identity_shared_with_later_bool": carrier_shared,
        "extension_changes_carrier_bool": extension_changes_carrier,
        "extension_reset_evidence_bool": bool(reset_offsets),
        "would_rule_a_select_false_resolved_survivor": would_select_false,
        "would_rule_a_eliminate_true_boundary_candidate": would_eliminate_true,
        "resolved_survivor_carrier": resolved_carrier,
        "later_unresolved_candidate_carriers": later_carriers,
        "carrier_same_as_true_boundary_chamber": (
            resolved_offset == actual and carrier_shared
        ),
        "reset_evidence_between_resolved_and_unresolved": reset_offsets,
        "higher_divisor_pressure_between_resolved_and_unresolved": higher_offsets,
        "square_pressure_between_resolved_and_unresolved": square_offsets,
        "semiprime_pressure_between_resolved_and_unresolved": semiprime_offsets,
    }


def candidate_records(
    row: dict[str, Any],
    witness_bound: int,
) -> list[dict[str, Any]]:
    """Return raw absorption records for all resolved candidates in one row."""
    return [
        raw_absorption_record(row, int(offset), witness_bound)
        for offset in row["survivors"]
    ]


def assign_statuses(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Assign candidate absorption statuses after row-local comparison."""
    records_by_anchor: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        records_by_anchor[int(record["anchor_p"])].append(record)

    updated_records: list[dict[str, Any]] = []
    for anchor_records in records_by_anchor.values():
        false_absorbs = any(
            bool(record["would_rule_a_select_false_resolved_survivor"])
            for record in anchor_records
        )
        for record in anchor_records:
            updated = dict(record)
            absorbs_all = bool(record["absorbs_all_later_unresolved_bool"])
            is_true = bool(record["resolved_candidate_is_true_label"])
            if not absorbs_all:
                status = STATUS_ABSTAINS
                failure_reason = "DOES_NOT_ABSORB_ALL_LATER_UNRESOLVED"
            elif not is_true:
                status = STATUS_UNSAFE_FALSE
                failure_reason = "FALSE_RESOLVED_SURVIVOR_ABSORBS_LATER"
            elif false_absorbs:
                status = STATUS_NONSELECTIVE
                failure_reason = "FALSE_RESOLVED_SURVIVOR_SHARES_ABSORPTION_PATTERN"
            else:
                status = STATUS_SAFE_TRUE
                failure_reason = None
            if bool(record["would_rule_a_eliminate_true_boundary_candidate"]):
                status = STATUS_UNSAFE_FALSE
                failure_reason = "FALSE_RESOLVED_SURVIVOR_ABSORBS_TRUE_BOUNDARY"
            updated["candidate_absorption_status"] = status
            updated["failure_reason"] = failure_reason
            updated_records.append(updated)
    return updated_records


def run_forensics(
    start_anchor: int,
    max_anchor: int,
    candidate_bound: int,
    witness_bound: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run the absorption safety probe."""
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
    raw_records: list[dict[str, Any]] = []
    for row in rows:
        raw_records.extend(candidate_records(row, witness_bound))
    records = assign_statuses(raw_records)

    true_records = [
        record for record in records if bool(record["resolved_candidate_is_true_label"])
    ]
    false_records = [
        record
        for record in records
        if not bool(record["resolved_candidate_is_true_label"])
    ]
    true_absorbs_all_count = sum(
        1 for record in true_records if bool(record["absorbs_all_later_unresolved_bool"])
    )
    false_absorbs_all_count = sum(
        1 for record in false_records if bool(record["absorbs_all_later_unresolved_bool"])
    )
    would_select_false_count = sum(
        1
        for record in records
        if bool(record["would_rule_a_select_false_resolved_survivor"])
    )
    would_eliminate_true_count = sum(
        1
        for record in records
        if bool(record["would_rule_a_eliminate_true_boundary_candidate"])
    )
    status_counts = Counter(
        str(record["candidate_absorption_status"]) for record in records
    )
    feature_counts_by_label = {
        "true_carrier_identity_shared_with_later_count": sum(
            1
            for record in true_records
            if bool(record["carrier_identity_shared_with_later_bool"])
        ),
        "false_carrier_identity_shared_with_later_count": sum(
            1
            for record in false_records
            if bool(record["carrier_identity_shared_with_later_bool"])
        ),
        "true_extension_changes_carrier_count": sum(
            1
            for record in true_records
            if bool(record["extension_changes_carrier_bool"])
        ),
        "false_extension_changes_carrier_count": sum(
            1
            for record in false_records
            if bool(record["extension_changes_carrier_bool"])
        ),
        "true_extension_reset_evidence_count": sum(
            1
            for record in true_records
            if bool(record["extension_reset_evidence_bool"])
        ),
        "false_extension_reset_evidence_count": sum(
            1
            for record in false_records
            if bool(record["extension_reset_evidence_bool"])
        ),
    }
    rule_a_wrong_count = sum(
        1
        for record in records
        if bool(record["would_rule_a_select_false_resolved_survivor"])
        or bool(record["would_rule_a_eliminate_true_boundary_candidate"])
    )
    absorption_pattern_separates = (
        true_absorbs_all_count > 0
        and false_absorbs_all_count == 0
        and would_eliminate_true_count == 0
    )
    summary = {
        "mode": "offline_resolved_boundary_absorption_safety_probe",
        "start_anchor": start_anchor,
        "max_anchor": max_anchor,
        "candidate_bound": candidate_bound,
        "witness_bound": witness_bound,
        "single_hole_positive_witness_closure_enabled": True,
        "carrier_locked_pressure_ceiling_enabled": True,
        "carrier_lock_predicate": LOCK_PREDICATE,
        "row_count": probe_summary["row_count"],
        "resolved_candidate_count": len(records),
        "true_resolved_candidate_count": len(true_records),
        "false_resolved_candidate_count": len(false_records),
        "true_absorbs_all_later_count": true_absorbs_all_count,
        "false_absorbs_all_later_count": false_absorbs_all_count,
        "rule_a_safe_absorption_count": int(status_counts[STATUS_SAFE_TRUE]),
        "rule_a_wrong_count": rule_a_wrong_count,
        "rule_a_abstain_count": int(status_counts[STATUS_ABSTAINS]),
        "would_rule_a_select_false_resolved_survivor_count": (
            would_select_false_count
        ),
        "would_rule_a_eliminate_true_boundary_candidate_count": (
            would_eliminate_true_count
        ),
        "absorption_pattern_separates_true_from_false": (
            absorption_pattern_separates
        ),
        "candidate_absorption_status_counts": status_counts,
        "feature_counts_by_label": feature_counts_by_label,
        "true_boundary_rejected_count": probe_summary[
            "true_boundary_rejected_count"
        ],
        "unique_resolved_survivor_count": probe_summary[
            "unique_resolved_survivor_count"
        ],
        "boundary_law_005_status": "not_approved",
        "prime_emission_status": "forbidden",
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
    """Run the absorption safety probe and write artifacts."""
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
