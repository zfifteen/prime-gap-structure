#!/usr/bin/env python3
"""Offline search for a carrier-lock condition.

This script studies candidate GWR pressure ceilings after the failed naive
ceiling rule. It classifies each candidate ceiling as safe or unsafe only after
the label-free pressure and exclusion records exist.
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
        CANDIDATE_STATUS_REJECTED,
        CANDIDATE_STATUS_RESOLVED_SURVIVOR,
        CANDIDATE_STATUS_UNRESOLVED,
    )
    from .right_boundary_pressure_ceiling_probe import (
        CEILING_STATUS_CANDIDATE,
        WHEEL_OPEN_RESIDUES_MOD30,
        certified_divisor_class,
        pressure_ceiling,
        run_probe_exclusion,
    )
except ImportError:  # pragma: no cover - direct script execution
    MODULE_DIR = Path(__file__).resolve().parent
    if str(MODULE_DIR) not in sys.path:
        sys.path.insert(0, str(MODULE_DIR))
    from composite_exclusion_boundary_probe import (
        CANDIDATE_STATUS_REJECTED,
        CANDIDATE_STATUS_RESOLVED_SURVIVOR,
        CANDIDATE_STATUS_UNRESOLVED,
    )
    from right_boundary_pressure_ceiling_probe import (
        CEILING_STATUS_CANDIDATE,
        WHEEL_OPEN_RESIDUES_MOD30,
        certified_divisor_class,
        pressure_ceiling,
        run_probe_exclusion,
    )


DEFAULT_OUTPUT_DIR = Path("output/prime_inference_generator")
SUMMARY_FILENAME = "carrier_lock_condition_probe_summary.json"
RECORDS_FILENAME = "carrier_lock_condition_probe_records.jsonl"
LOCK_RULE_NAMES = (
    "unresolved_alternatives_before_threat",
    "higher_divisor_pressure_before_threat",
    "single_resolved_no_unresolved_before_threat",
    "all_resolved_candidates_before_threat",
    "semiprime_carrier_square_threat",
    "no_higher_divisor_pressure_before_threat",
)


def build_parser() -> argparse.ArgumentParser:
    """Build the carrier-lock condition search CLI."""
    parser = argparse.ArgumentParser(
        description="Offline carrier-lock condition search.",
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
        help="Largest witness factor used for positive structure.",
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


def candidate_counts_below_threat(row: dict[str, Any], threat_offset: int) -> dict[str, Any]:
    """Return candidate status counts before a pressure threat."""
    records_by_offset = {
        int(record["offset"]): record for record in row["candidate_status_records"]
    }
    candidate_offsets = [
        int(offset)
        for offset in row["candidate_offsets"]
        if int(offset) < threat_offset
    ]
    survivors: list[int] = []
    unresolved: list[int] = []
    rejected: list[int] = []
    for offset in candidate_offsets:
        status = str(records_by_offset[offset]["status"])
        if status == CANDIDATE_STATUS_RESOLVED_SURVIVOR:
            survivors.append(offset)
        elif status == CANDIDATE_STATUS_UNRESOLVED:
            unresolved.append(offset)
        elif status == CANDIDATE_STATUS_REJECTED:
            rejected.append(offset)

    return {
        "candidate_count_before_threat": len(candidate_offsets),
        "resolved_before_threat": survivors,
        "resolved_before_threat_count": len(survivors),
        "unresolved_before_threat": unresolved,
        "unresolved_before_threat_count": len(unresolved),
        "rejected_before_threat": rejected,
        "rejected_before_threat_count": len(rejected),
        "unique_resolved_before_threat": (
            survivors[0] if len(survivors) == 1 and not unresolved else None
        ),
    }


def legal_ladder_features(
    anchor_p: int,
    threat_offset: int,
    witness_bound: int,
) -> list[str]:
    """Return label-free ladder tokens up to the candidate threat."""
    features: list[str] = []
    for offset in range(1, threat_offset + 1):
        n = anchor_p + offset
        certificate = certified_divisor_class(n, witness_bound)
        if certificate is not None:
            features.append(
                f"{offset}:D{certificate['divisor_class']}:{certificate['family']}"
            )
        elif n % 30 in WHEEL_OPEN_RESIDUES_MOD30:
            features.append(f"{offset}:OPEN_UNKNOWN")
        else:
            features.append(f"{offset}:WHEEL_CLOSED")
    return features


def pressure_profiles(
    anchor_p: int,
    carrier_offset: int,
    carrier_d: int,
    threat_offset: int,
    witness_bound: int,
) -> dict[str, Any]:
    """Return label-free pressure profiles before the threat."""
    square_offsets: list[int] = []
    higher_offsets: list[int] = []
    semiprime_offsets: list[int] = []
    for offset in range(carrier_offset + 1, threat_offset + 1):
        n = anchor_p + offset
        certificate = certified_divisor_class(n, witness_bound)
        if certificate is None:
            continue
        divisor_class = int(certificate["divisor_class"])
        family = str(certificate["family"])
        power = certificate["certificate"]
        if (
            family == "known_basis_prime_power"
            and int(power.get("exponent", 0)) == 2
        ):
            square_offsets.append(offset)
        if divisor_class > carrier_d:
            higher_offsets.append(offset)
        if family == "known_basis_semiprime":
            semiprime_offsets.append(offset)

    return {
        "square_pressure": {
            "known_square_offsets_to_threat": square_offsets,
            "known_square_count_to_threat": len(square_offsets),
            "threat_is_known_square": bool(
                square_offsets and square_offsets[-1] == threat_offset
            ),
        },
        "higher_divisor_pressure": {
            "higher_divisor_offsets_before_threat": higher_offsets,
            "higher_d_pressure_total_before_threat": len(higher_offsets),
        },
        "semiprime_pressure": {
            "semiprime_offsets_to_threat": semiprime_offsets,
            "semiprime_count_to_threat": len(semiprime_offsets),
        },
    }


def resolved_survivor_pair_status(row: dict[str, Any]) -> dict[str, Any]:
    """Return the resolved-survivor pair status for one anchor."""
    actual = int(row["actual_boundary_offset_label"])
    survivors = [int(offset) for offset in row["survivors"]]
    false_survivors = [offset for offset in survivors if offset != actual]
    if not survivors:
        status = "no_resolved_survivor"
    elif len(survivors) == 1 and survivors[0] == actual:
        status = "single_true_resolved_survivor"
    elif len(survivors) == 1:
        status = "single_false_resolved_survivor"
    elif len(survivors) == 2 and actual in survivors:
        status = "true_false_resolved_pair"
    elif len(survivors) == 2:
        status = "two_resolved_survivors_without_true"
    elif actual in survivors:
        status = "multi_resolved_with_true"
    else:
        status = "multi_resolved_without_true"
    return {
        "resolved_survivor_pair_status": status,
        "resolved_survivor_offsets": survivors,
        "false_resolved_survivor_offsets": false_survivors,
        "true_boundary_resolved_bool": actual in survivors,
    }


def previous_chamber_state(
    previous_row: dict[str, Any] | None,
) -> dict[str, Any]:
    """Return previous-row context for transition forensics."""
    if previous_row is None:
        return {
            "previous_anchor_p": None,
            "previous_gap_offset_label": None,
            "previous_anchor_residue_mod30": None,
            "previous_survivor_count": None,
            "previous_unresolved_count": None,
            "label_derived": True,
        }
    return {
        "previous_anchor_p": int(previous_row["anchor_p"]),
        "previous_gap_offset_label": int(previous_row["actual_boundary_offset_label"]),
        "previous_anchor_residue_mod30": int(previous_row["anchor_p"]) % 30,
        "previous_survivor_count": int(previous_row["survivor_count"]),
        "previous_unresolved_count": int(previous_row["unresolved_count"]),
        "label_derived": True,
    }


def extension_change_offsets(
    anchor_p: int,
    carrier_offset: int,
    carrier_d: int,
    actual_boundary_offset: int,
    witness_bound: int,
) -> list[int]:
    """Return label-audited carrier-reset offsets inside the actual chamber."""
    offsets: list[int] = []
    for offset in range(carrier_offset + 1, actual_boundary_offset):
        certificate = certified_divisor_class(anchor_p + offset, witness_bound)
        if certificate is None:
            continue
        if int(certificate["divisor_class"]) < carrier_d:
            offsets.append(offset)
    return offsets


def carrier_lock_record(
    row: dict[str, Any],
    previous_row: dict[str, Any] | None,
    candidate_bound: int,
    witness_bound: int,
) -> dict[str, Any] | None:
    """Return one candidate carrier-lock forensics record."""
    anchor_p = int(row["anchor_p"])
    ceiling = pressure_ceiling(anchor_p, candidate_bound, witness_bound)
    if ceiling["ceiling_status"] != CEILING_STATUS_CANDIDATE:
        return None

    actual = int(row["actual_boundary_offset_label"])
    carrier_offset = int(ceiling["carrier_offset"])
    carrier_d = int(ceiling["carrier_d"])
    threat_offset = int(ceiling["threat_T"])
    reset_bool = actual >= threat_offset
    candidate_counts = candidate_counts_below_threat(row, threat_offset)
    pressure = pressure_profiles(
        anchor_p,
        carrier_offset,
        carrier_d,
        threat_offset,
        witness_bound,
    )
    extension_changes = extension_change_offsets(
        anchor_p,
        carrier_offset,
        carrier_d,
        actual,
        witness_bound,
    )

    return {
        "anchor_p": anchor_p,
        "carrier_w": int(ceiling["carrier_w"]),
        "carrier_d": carrier_d,
        "carrier_family": ceiling["carrier_family"],
        "carrier_offset": carrier_offset,
        "threat_t": int(ceiling["threat_n"]),
        "threat_d": int(ceiling["threat_d"]),
        "threat_offset": threat_offset,
        "threat_family": ceiling["threat_family"],
        "actual_boundary_offset_label": actual,
        "ceiling_safe_bool": not reset_bool,
        "reset_bool": reset_bool,
        "previous_chamber_state": previous_chamber_state(previous_row),
        "carrier_ladder_legal_features": legal_ladder_features(
            anchor_p,
            threat_offset,
            witness_bound,
        ),
        **pressure,
        **resolved_survivor_pair_status(row),
        **candidate_counts,
        "extension_change_offsets": extension_changes,
        "extension_preserves_carrier_bool": not extension_changes,
        "extension_changes_carrier_bool": bool(extension_changes),
    }


def observable_tokens(record: dict[str, Any]) -> list[str]:
    """Return label-free observable tokens for safe/reset comparison."""
    previous = record["previous_chamber_state"]
    return [
        f"carrier_d:{record['carrier_d']}",
        f"carrier_family:{record['carrier_family']}",
        f"threat_d:{record['threat_d']}",
        f"threat_family:{record['threat_family']}",
        f"resolved_pair:{record['resolved_survivor_pair_status']}",
        f"previous_gap:{previous['previous_gap_offset_label']}",
        f"square_count:{record['square_pressure']['known_square_count_to_threat']}",
        "threat_is_square:"
        f"{record['square_pressure']['threat_is_known_square']}",
        "has_higher_divisor_pressure:"
        f"{bool(record['higher_divisor_pressure']['higher_d_pressure_total_before_threat'])}",
        "has_semiprime_pressure:"
        f"{bool(record['semiprime_pressure']['semiprime_count_to_threat'])}",
        "has_unresolved_before_threat:"
        f"{bool(record['unresolved_before_threat_count'])}",
        "unique_resolved_before_threat:"
        f"{record['unique_resolved_before_threat'] is not None}",
    ]


def lock_rule_selects(rule_name: str, record: dict[str, Any]) -> bool:
    """Return whether a label-blind lock rule selects this ceiling as safe."""
    if rule_name == "unresolved_alternatives_before_threat":
        return bool(record["unresolved_before_threat_count"])
    if rule_name == "higher_divisor_pressure_before_threat":
        return bool(
            record["higher_divisor_pressure"]["higher_d_pressure_total_before_threat"]
        )
    if rule_name == "single_resolved_no_unresolved_before_threat":
        return record["unique_resolved_before_threat"] is not None
    if rule_name == "all_resolved_candidates_before_threat":
        return (
            record["candidate_count_before_threat"]
            == record["resolved_before_threat_count"]
            and record["candidate_count_before_threat"] > 0
        )
    if rule_name == "semiprime_carrier_square_threat":
        return (
            record["carrier_family"] == "known_basis_semiprime"
            and record["threat_family"] == "known_basis_prime_power"
            and record["threat_d"] == 3
            and record["square_pressure"]["threat_is_known_square"]
        )
    if rule_name == "no_higher_divisor_pressure_before_threat":
        return not bool(
            record["higher_divisor_pressure"]["higher_d_pressure_total_before_threat"]
        )
    raise ValueError(f"unknown lock rule: {rule_name}")


def lock_rule_report(rule_name: str, records: list[dict[str, Any]]) -> dict[str, Any]:
    """Return zero-wrong acceptance metrics for one lock predicate."""
    selected = [record for record in records if lock_rule_selects(rule_name, record)]
    unsafe = [record for record in selected if bool(record["reset_bool"])]
    safe = [record for record in selected if bool(record["ceiling_safe_bool"])]
    first_unsafe = [
        {
            "anchor_p": record["anchor_p"],
            "carrier_offset": record["carrier_offset"],
            "threat_offset": record["threat_offset"],
            "actual_boundary_offset_label": record[
                "actual_boundary_offset_label"
            ],
        }
        for record in unsafe[:5]
    ]
    passes = len(unsafe) == 0 and len(safe) > 0
    return {
        "rule_name": rule_name,
        "eligible_for_pure_generation": True,
        "cases_tested": len(records),
        "safe_ceiling_classified_count": len(safe),
        "unsafe_reset_misclassified_as_safe": len(unsafe),
        "abstain_count": len(records) - len(selected),
        "first_unsafe_examples": first_unsafe,
        "passes_zero_wrong_gate": passes,
        "status": "candidate" if passes else "rejected",
    }


def candidate_lock_observable_counts(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Return safe/reset counts for label-free observable tokens."""
    counts: dict[str, Counter] = {}
    for record in records:
        bucket = "unsafe_reset" if bool(record["reset_bool"]) else "safe_ceiling"
        for token in observable_tokens(record):
            counts.setdefault(token, Counter())[bucket] += 1
    return {
        token: {
            "safe_ceiling": int(counter["safe_ceiling"]),
            "unsafe_reset": int(counter["unsafe_reset"]),
        }
        for token, counter in sorted(counts.items())
    }


def run_probe(
    start_anchor: int,
    max_anchor: int,
    candidate_bound: int,
    witness_bound: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run the carrier-lock condition search."""
    started = time.perf_counter()
    rows, exclusion_summary = run_probe_exclusion(
        start_anchor,
        max_anchor,
        candidate_bound,
        witness_bound,
    )
    records: list[dict[str, Any]] = []
    previous_row: dict[str, Any] | None = None
    for row in rows:
        record = carrier_lock_record(row, previous_row, candidate_bound, witness_bound)
        if record is not None:
            records.append(record)
        previous_row = row

    rule_reports = [
        lock_rule_report(rule_name, records) for rule_name in LOCK_RULE_NAMES
    ]
    candidate_rules = [
        report["rule_name"]
        for report in rule_reports
        if bool(report["passes_zero_wrong_gate"])
    ]
    safe_records = [record for record in records if bool(record["ceiling_safe_bool"])]
    reset_records = [record for record in records if bool(record["reset_bool"])]
    summary = {
        "mode": "offline_carrier_lock_condition_search",
        "start_anchor": start_anchor,
        "max_anchor": max_anchor,
        "candidate_bound": candidate_bound,
        "witness_bound": witness_bound,
        "row_count": len(records),
        "safe_ceiling_count": len(safe_records),
        "unsafe_reset_count": len(reset_records),
        "candidate_lock_observable_counts": candidate_lock_observable_counts(records),
        "lock_rule_reports": rule_reports,
        "candidate_lock_predicates": candidate_rules,
        "first_candidate_lock_predicate": (
            None if not candidate_rules else candidate_rules[0]
        ),
        "exclusion_summary": {
            "true_boundary_rejected_count": exclusion_summary[
                "true_boundary_rejected_count"
            ],
            "true_boundary_status_counts": exclusion_summary[
                "true_boundary_status_counts"
            ],
            "unique_resolved_survivor_count": exclusion_summary[
                "unique_resolved_survivor_count"
            ],
        },
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
    """Run the carrier-lock condition search and write artifacts."""
    args = build_parser().parse_args(argv)
    records, summary = run_probe(
        start_anchor=args.start_anchor,
        max_anchor=args.max_anchor,
        candidate_bound=args.candidate_bound,
        witness_bound=args.witness_bound,
    )
    write_artifacts(records, summary, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
