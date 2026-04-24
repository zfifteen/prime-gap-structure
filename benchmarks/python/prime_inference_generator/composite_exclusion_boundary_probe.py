#!/usr/bin/env python3
"""Offline composite-exclusion boundary probe.

This script is theorem discovery, not pure generation. The elimination pass
uses only bounded positive composite witnesses. Classical labels are attached
after elimination to measure whether the true boundary was preserved.
"""

from __future__ import annotations

import argparse
import json
import math
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
SINGLE_HOLE_WITNESS_FACTORS = (
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
CANDIDATE_STATUS_RESOLVED_SURVIVOR = "RESOLVED_SURVIVOR"
CANDIDATE_STATUS_REJECTED = "REJECTED"
CANDIDATE_STATUS_UNRESOLVED = "UNRESOLVED"
KNOWN_PRIME_BASIS_PREFIX = (2, 3, 5)
CARRIER_LOCK_PREDICATE_CHOICES = (
    "unresolved_alternatives_before_threat",
    "higher_divisor_pressure_before_threat",
    "either",
    "both",
)
RULE_FAMILIES = [
    "wheel_closed_rejection",
    "positive_composite_witness_rejection",
    "interior_open_unclosed_rejection",
    "gwr_incompatibility_rejection",
    "no_later_simpler_violation_rejection",
    "square_pressure_rejection",
    "carrier_absence_rejection",
    "single_hole_positive_witness_closure",
    "carrier_locked_pressure_ceiling_rejection",
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
        "--enable-single-hole-positive-witness-closure",
        action="store_true",
        help="Close one unresolved interior-open slot by positive witness.",
    )
    parser.add_argument(
        "--witness-bound",
        type=int,
        default=31,
        help="Largest factor allowed for opt-in single-hole witness closure.",
    )
    parser.add_argument(
        "--enable-carrier-locked-pressure-ceiling",
        action="store_true",
        help="Prune candidates at or beyond an opt-in carrier-locked ceiling.",
    )
    parser.add_argument(
        "--carrier-lock-predicate",
        choices=CARRIER_LOCK_PREDICATE_CHOICES,
        default="either",
        help="Carrier-lock predicate used when the pressure ceiling flag is on.",
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


def single_hole_positive_witness(n: int, witness_bound: int) -> int | None:
    """Return an opt-in positive witness for single-hole closure."""
    for factor in SINGLE_HOLE_WITNESS_FACTORS:
        if factor > witness_bound:
            continue
        if factor < n and n % factor == 0:
            return factor
    return None


def power_closure_witness(n: int) -> dict[str, int] | None:
    """Return a direct integer-power witness for n, if one exists."""
    for exponent in range(2, 7):
        root = 1 if exponent != 2 else math.isqrt(n)
        if exponent != 2:
            while root**exponent < n:
                root += 1
        if root > 1 and root**exponent == n:
            return {"base": root, "exponent": exponent}
    return None


def known_basis(witness_bound: int) -> tuple[int, ...]:
    """Return the explicit small-prime basis available to the ceiling probe."""
    basis = (
        *KNOWN_PRIME_BASIS_PREFIX,
        *COMPOSITE_WITNESS_FACTORS,
        *SINGLE_HOLE_WITNESS_FACTORS,
    )
    return tuple(factor for factor in basis if factor <= witness_bound)


def certified_divisor_class(n: int, witness_bound: int) -> dict[str, Any] | None:
    """Return a positive divisor-class certificate for n, if available."""
    basis = known_basis(witness_bound)
    for base in basis:
        for exponent in range(2, 7):
            if base**exponent == n:
                return {
                    "divisor_class": exponent + 1,
                    "family": "known_basis_prime_power",
                    "certificate": {"base": base, "exponent": exponent},
                }

    for index, left in enumerate(basis):
        for right in basis[index + 1 :]:
            if left * right == n:
                return {
                    "divisor_class": 4,
                    "family": "known_basis_semiprime",
                    "certificate": {"left": left, "right": right},
                }
    return None


def candidate_pressure_ceiling(
    anchor_p: int,
    candidate_bound: int,
    witness_bound: int,
) -> dict[str, Any]:
    """Return a label-free lower-divisor pressure event, if available."""
    carrier: dict[str, Any] | None = None
    for offset in range(1, candidate_bound + 1):
        certificate = certified_divisor_class(anchor_p + offset, witness_bound)
        if certificate is None:
            continue
        carrier = {
            "carrier_w": anchor_p + offset,
            "carrier_offset": offset,
            "carrier_d": certificate["divisor_class"],
            "carrier_family": certificate["family"],
            "carrier_certificate": certificate["certificate"],
        }
        break

    if carrier is None:
        return {
            "ceiling_status": "NO_LEGAL_CARRIER",
            "applied": False,
            "carrier_w": None,
            "carrier_offset": None,
            "carrier_d": None,
            "carrier_family": None,
            "threat_offset": None,
            "threat_t": None,
            "threat_d": None,
            "threat_family": None,
        }

    carrier_offset = int(carrier["carrier_offset"])
    carrier_d = int(carrier["carrier_d"])
    for offset in range(carrier_offset + 1, candidate_bound + 1):
        certificate = certified_divisor_class(anchor_p + offset, witness_bound)
        if certificate is None:
            continue
        if int(certificate["divisor_class"]) >= carrier_d:
            continue
        return {
            **carrier,
            "ceiling_status": "CANDIDATE_GWR_PRESSURE_CEILING",
            "applied": False,
            "threat_offset": offset,
            "threat_t": anchor_p + offset,
            "threat_d": certificate["divisor_class"],
            "threat_family": certificate["family"],
            "threat_certificate": certificate["certificate"],
        }

    return {
        **carrier,
        "ceiling_status": "NO_LEGAL_THREAT",
        "applied": False,
        "threat_offset": None,
        "threat_t": None,
        "threat_d": None,
        "threat_family": None,
    }


def interior_open_offsets(anchor_p: int, candidate_offset: int) -> list[int]:
    """Return wheel-open interior offsets before a proposed boundary."""
    return [
        offset
        for offset in range(1, candidate_offset)
        if (anchor_p + offset) % 30 in WHEEL_OPEN_RESIDUES_MOD30
    ]


def classify_candidate(
    anchor_p: int,
    candidate_offset: int,
    enable_single_hole_positive_witness_closure: bool,
    witness_bound: int,
) -> dict[str, Any]:
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
            "closure_reasons": [],
            "closure_rule_family": None,
            "single_hole_positive_witness_closure": False,
            "power_closure_subset": False,
        }

    unresolved_offsets = [
        offset
        for offset in interior_open_offsets(anchor_p, candidate_offset)
        if bounded_composite_witness(anchor_p + offset) is None
    ]
    if unresolved_offsets:
        if (
            enable_single_hole_positive_witness_closure
            and len(unresolved_offsets) == 1
        ):
            hole_offset = unresolved_offsets[0]
            hole_n = anchor_p + hole_offset
            closure_witness = single_hole_positive_witness(hole_n, witness_bound)
            if closure_witness is not None:
                power_witness = power_closure_witness(hole_n)
                closure_reasons = [
                    f"SINGLE_HOLE_POSITIVE_WITNESS_FACTOR_{closure_witness}"
                ]
                if power_witness is not None:
                    closure_reasons.append(
                        "POWER_CLOSURE_"
                        f"{power_witness['base']}^{power_witness['exponent']}"
                    )
                return {
                    "offset": candidate_offset,
                    "status": CANDIDATE_STATUS_RESOLVED_SURVIVOR,
                    "rejection_reasons": [],
                    "unresolved_reasons": [],
                    "unresolved_interior_offsets": [],
                    "rule_family": None,
                    "closure_reasons": closure_reasons,
                    "closure_rule_family": "single_hole_positive_witness_closure",
                    "single_hole_positive_witness_closure": True,
                    "single_hole_positive_witness_factor": closure_witness,
                    "single_hole_closed_offset": hole_offset,
                    "power_closure_subset": power_witness is not None,
                }
        return {
            "offset": candidate_offset,
            "status": CANDIDATE_STATUS_UNRESOLVED,
            "rejection_reasons": [],
            "unresolved_reasons": ["UNRESOLVED_INTERIOR_OPEN"],
            "unresolved_interior_offsets": unresolved_offsets,
            "rule_family": "interior_open_unclosed_rejection",
            "closure_reasons": [],
            "closure_rule_family": None,
            "single_hole_positive_witness_closure": False,
            "power_closure_subset": False,
        }

    return {
        "offset": candidate_offset,
        "status": CANDIDATE_STATUS_RESOLVED_SURVIVOR,
        "rejection_reasons": [],
        "unresolved_reasons": [],
        "unresolved_interior_offsets": [],
        "rule_family": None,
        "closure_reasons": [],
        "closure_rule_family": None,
        "single_hole_positive_witness_closure": False,
        "power_closure_subset": False,
    }


def ceiling_lock_components(
    anchor_p: int,
    candidate_records: list[dict[str, Any]],
    ceiling: dict[str, Any],
    witness_bound: int,
) -> dict[str, bool]:
    """Return label-free carrier-lock component booleans."""
    threat_offset = int(ceiling["threat_offset"])
    carrier_offset = int(ceiling["carrier_offset"])
    carrier_d = int(ceiling["carrier_d"])
    unresolved_before_threat = any(
        int(record["offset"]) < threat_offset
        and record["status"] == CANDIDATE_STATUS_UNRESOLVED
        for record in candidate_records
    )
    higher_divisor_pressure = False
    for offset in range(carrier_offset + 1, threat_offset + 1):
        certificate = certified_divisor_class(anchor_p + offset, witness_bound)
        if certificate is None:
            continue
        if int(certificate["divisor_class"]) > carrier_d:
            higher_divisor_pressure = True
            break

    return {
        "unresolved_alternatives_before_threat": unresolved_before_threat,
        "higher_divisor_pressure_before_threat": higher_divisor_pressure,
    }


def carrier_lock_selected(
    predicate: str,
    components: dict[str, bool],
) -> bool:
    """Return whether the requested lock predicate fires."""
    unresolved = bool(components["unresolved_alternatives_before_threat"])
    higher = bool(components["higher_divisor_pressure_before_threat"])
    if predicate == "unresolved_alternatives_before_threat":
        return unresolved
    if predicate == "higher_divisor_pressure_before_threat":
        return higher
    if predicate == "either":
        return unresolved or higher
    if predicate == "both":
        return unresolved and higher
    raise ValueError(f"unknown carrier lock predicate: {predicate}")


def apply_carrier_locked_pressure_ceiling(
    anchor_p: int,
    candidate_records: list[dict[str, Any]],
    candidate_bound: int,
    witness_bound: int,
    carrier_lock_predicate: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Apply an opt-in label-free carrier-locked pressure ceiling."""
    ceiling = candidate_pressure_ceiling(anchor_p, candidate_bound, witness_bound)
    if ceiling["ceiling_status"] != "CANDIDATE_GWR_PRESSURE_CEILING":
        return candidate_records, {
            **ceiling,
            "carrier_lock_predicate": carrier_lock_predicate,
            "lock_components": {},
            "lock_selected": False,
            "pruned_offsets": [],
        }

    components = ceiling_lock_components(
        anchor_p,
        candidate_records,
        ceiling,
        witness_bound,
    )
    selected = carrier_lock_selected(carrier_lock_predicate, components)
    if not selected:
        return candidate_records, {
            **ceiling,
            "carrier_lock_predicate": carrier_lock_predicate,
            "lock_components": components,
            "lock_selected": False,
            "pruned_offsets": [],
        }

    threat_offset = int(ceiling["threat_offset"])
    updated_records: list[dict[str, Any]] = []
    pruned_offsets: list[int] = []
    for record in candidate_records:
        offset = int(record["offset"])
        if offset < threat_offset:
            updated_records.append(record)
            continue
        updated = dict(record)
        previous_status = str(updated["status"])
        if previous_status != CANDIDATE_STATUS_REJECTED:
            pruned_offsets.append(offset)
        updated["status"] = CANDIDATE_STATUS_REJECTED
        updated["rule_family"] = "carrier_locked_pressure_ceiling_rejection"
        updated["carrier_locked_pressure_ceiling_rejection"] = True
        updated["carrier_locked_pressure_ceiling_previous_status"] = previous_status
        updated["carrier_locked_pressure_ceiling_threat_offset"] = threat_offset
        updated["rejection_reasons"] = [
            *list(updated["rejection_reasons"]),
            f"CARRIER_LOCKED_PRESSURE_CEILING_BEFORE_{threat_offset}",
        ]
        updated["unresolved_reasons"] = []
        updated["unresolved_interior_offsets"] = []
        updated_records.append(updated)

    return updated_records, {
        **ceiling,
        "applied": True,
        "carrier_lock_predicate": carrier_lock_predicate,
        "lock_components": components,
        "lock_selected": True,
        "pruned_offsets": pruned_offsets,
    }


def candidate_summary(candidate_records: list[dict[str, Any]]) -> dict[str, Any]:
    """Return candidate lists and status maps after all label-free rules."""
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
    }


def eliminate_candidates(
    anchor_p: int,
    candidate_bound: int,
    enable_single_hole_positive_witness_closure: bool = False,
    witness_bound: int = 31,
    enable_carrier_locked_pressure_ceiling: bool = False,
    carrier_lock_predicate: str = "either",
) -> dict[str, Any]:
    """Run label-free composite exclusion for one anchor."""
    offsets = candidate_offsets(anchor_p, candidate_bound)
    candidate_records = [
        classify_candidate(
            anchor_p,
            offset,
            enable_single_hole_positive_witness_closure,
            witness_bound,
        )
        for offset in offsets
    ]
    ceiling_report = {
        "ceiling_status": "DISABLED",
        "applied": False,
        "carrier_lock_predicate": carrier_lock_predicate,
        "lock_components": {},
        "lock_selected": False,
        "pruned_offsets": [],
    }
    if enable_carrier_locked_pressure_ceiling:
        candidate_records, ceiling_report = apply_carrier_locked_pressure_ceiling(
            anchor_p,
            candidate_records,
            candidate_bound,
            witness_bound,
            carrier_lock_predicate,
        )
    summary = candidate_summary(candidate_records)

    return {
        "anchor_p": anchor_p,
        "candidate_bound": candidate_bound,
        "candidate_offsets": offsets,
        "candidate_count": len(offsets),
        **summary,
        "candidate_status_records": candidate_records,
        "single_hole_positive_witness_closure_enabled": (
            enable_single_hole_positive_witness_closure
        ),
        "carrier_locked_pressure_ceiling_enabled": (
            enable_carrier_locked_pressure_ceiling
        ),
        "carrier_lock_predicate": carrier_lock_predicate,
        "carrier_locked_pressure_ceiling": ceiling_report,
        "witness_bound": witness_bound,
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
    closure_applied_count = 0
    power_closure_subset_count = 0
    true_boundary_rejected_count = 0
    survivor_counts_after_rule: list[int] = []
    unique_survivor_count_after_rule = 0
    for row in rows:
        candidate_count = int(row["candidate_count"])
        actual = int(row["actual_boundary_offset_label"])
        rejected_offsets: set[int] = set()
        unresolved_offsets: set[int] = set()
        row_closure_applied_count = 0
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
            elif (
                rule_family == "single_hole_positive_witness_closure"
                and bool(record.get("single_hole_positive_witness_closure"))
            ):
                closure_applied_count += 1
                row_closure_applied_count += 1
                if bool(record.get("power_closure_subset")):
                    power_closure_subset_count += 1
            elif (
                rule_family == "carrier_locked_pressure_ceiling_rejection"
                and bool(record.get("carrier_locked_pressure_ceiling_rejection"))
            ):
                if (
                    record.get("carrier_locked_pressure_ceiling_previous_status")
                    != CANDIDATE_STATUS_REJECTED
                ):
                    rejected_offsets.add(offset)

        if rule_family == "single_hole_positive_witness_closure":
            survivors_after_rule = row_closure_applied_count
        else:
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
        "closure_applied_count": closure_applied_count,
        "power_closure_subset_count": power_closure_subset_count,
        "true_boundary_rejected_count": true_boundary_rejected_count,
        "average_survivor_count_after_rule": statistics.fmean(
            survivor_counts_after_rule
        ),
        "marginal_rejection_count": rejected_count,
        "unique_survivor_count_after_rule": unique_survivor_count_after_rule,
    }


def aggregate_counts(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Return shared summary metrics for labeled eliminator rows."""
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
    return {
        "unique_survivor_count": len(unique_rows),
        "unique_resolved_survivor_count": len(unique_resolved_rows),
        "no_survivor_count": no_survivor_count,
        "no_unique_boundary_count": no_unique_count,
        "true_boundary_rejected_count": len(true_boundary_rejected_rows),
        "true_boundary_unresolved_count": sum(
            1
            for row in rows
            if row["true_boundary_status"] == CANDIDATE_STATUS_UNRESOLVED
        ),
        "true_boundary_resolved_survivor_count": sum(
            1
            for row in rows
            if row["true_boundary_status"] == CANDIDATE_STATUS_RESOLVED_SURVIVOR
        ),
        "unique_survivor_match_count": len(unique_match_rows),
        "unique_survivor_match_rate": (
            0.0 if not unique_rows else len(unique_match_rows) / len(unique_rows)
        ),
        "average_candidate_count": statistics.fmean(candidate_counts),
        "average_rejected_count": statistics.fmean(rejected_counts),
        "average_unresolved_count": statistics.fmean(unresolved_counts),
        "average_survives_count": statistics.fmean(survivor_counts),
        "average_resolved_survivor_count": statistics.fmean(survivor_counts),
        "average_survivor_count": statistics.fmean(survivor_counts),
        "survivor_count_distribution": Counter(survivor_counts),
        "unresolved_count_distribution": Counter(unresolved_counts),
        "true_boundary_status_counts": Counter(
            str(row["true_boundary_status"]) for row in rows
        ),
    }


def single_hole_closure_report(rows: list[dict[str, Any]]) -> dict[str, int]:
    """Return attribution counts for the opt-in single-hole closure rule."""
    applied_count = 0
    true_boundary_closures = 0
    false_boundary_closures = 0
    power_closure_subset_count = 0
    for row in rows:
        actual = int(row["actual_boundary_offset_label"])
        for record in row["candidate_status_records"]:
            if not bool(record.get("single_hole_positive_witness_closure")):
                continue
            applied_count += 1
            if bool(record.get("power_closure_subset")):
                power_closure_subset_count += 1
            if int(record["offset"]) == actual:
                true_boundary_closures += 1
            else:
                false_boundary_closures += 1

    return {
        "single_hole_positive_witness_closure_applied_count": applied_count,
        "single_hole_positive_witness_true_boundary_closures": (
            true_boundary_closures
        ),
        "single_hole_positive_witness_false_boundary_closures": (
            false_boundary_closures
        ),
        "power_closure_subset_count": power_closure_subset_count,
    }


def carrier_locked_ceiling_report(rows: list[dict[str, Any]]) -> dict[str, int]:
    """Return attribution counts for the opt-in carrier-locked ceiling."""
    applied_count = 0
    true_boundary_safe_count = 0
    unsafe_count = 0
    false_candidate_pruned_count = 0
    true_boundary_pruned_count = 0
    for row in rows:
        ceiling = row["carrier_locked_pressure_ceiling"]
        if not bool(ceiling.get("applied")):
            continue
        applied_count += 1
        actual = int(row["actual_boundary_offset_label"])
        threat_offset = int(ceiling["threat_offset"])
        if actual < threat_offset:
            true_boundary_safe_count += 1
        else:
            unsafe_count += 1
        for offset in ceiling["pruned_offsets"]:
            if int(offset) == actual:
                true_boundary_pruned_count += 1
            else:
                false_candidate_pruned_count += 1

    return {
        "carrier_locked_ceiling_applied_count": applied_count,
        "carrier_locked_ceiling_true_boundary_safe_count": (
            true_boundary_safe_count
        ),
        "carrier_locked_ceiling_false_candidate_pruned_count": (
            false_candidate_pruned_count
        ),
        "carrier_locked_ceiling_unsafe_count": unsafe_count,
        "carrier_locked_ceiling_true_boundary_pruned_count": (
            true_boundary_pruned_count
        ),
    }


def run_probe(
    start_anchor: int,
    max_anchor: int,
    candidate_bound: int,
    enable_single_hole_positive_witness_closure: bool = False,
    witness_bound: int = 31,
    enable_carrier_locked_pressure_ceiling: bool = False,
    carrier_lock_predicate: str = "either",
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run label-free elimination, then attach labels for reporting."""
    if candidate_bound < 1:
        raise ValueError("candidate_bound must be at least 1")
    if max_anchor < start_anchor:
        raise ValueError("max_anchor must be at least start_anchor")
    if witness_bound < max(COMPOSITE_WITNESS_FACTORS):
        raise ValueError("witness_bound must be at least 31")
    if carrier_lock_predicate not in CARRIER_LOCK_PREDICATE_CHOICES:
        raise ValueError(f"unknown carrier lock predicate: {carrier_lock_predicate}")

    started = time.perf_counter()
    labels = label_offsets(start_anchor, max_anchor, candidate_bound)
    baseline_rows: list[dict[str, Any]] = []
    if enable_single_hole_positive_witness_closure:
        baseline_rows = [
            attach_label(
                eliminate_candidates(
                    anchor_p,
                    candidate_bound,
                    enable_single_hole_positive_witness_closure=False,
                    witness_bound=max(COMPOSITE_WITNESS_FACTORS),
                    enable_carrier_locked_pressure_ceiling=False,
                    carrier_lock_predicate=carrier_lock_predicate,
                ),
                label,
            )
            for anchor_p, label in labels.items()
        ]
    pre_ceiling_rows: list[dict[str, Any]] = []
    if enable_carrier_locked_pressure_ceiling:
        pre_ceiling_rows = [
            attach_label(
                eliminate_candidates(
                    anchor_p,
                    candidate_bound,
                    enable_single_hole_positive_witness_closure=(
                        enable_single_hole_positive_witness_closure
                    ),
                    witness_bound=witness_bound,
                    enable_carrier_locked_pressure_ceiling=False,
                    carrier_lock_predicate=carrier_lock_predicate,
                ),
                label,
            )
            for anchor_p, label in labels.items()
        ]
    rows = [
        attach_label(
            eliminate_candidates(
                anchor_p,
                candidate_bound,
                enable_single_hole_positive_witness_closure=(
                    enable_single_hole_positive_witness_closure
                ),
                witness_bound=witness_bound,
                enable_carrier_locked_pressure_ceiling=(
                    enable_carrier_locked_pressure_ceiling
                ),
                carrier_lock_predicate=carrier_lock_predicate,
            ),
            label,
        )
        for anchor_p, label in labels.items()
    ]
    first_failure_examples = [
        row
        for row in rows
        if row["failure_reason"] not in (None, "NO_UNIQUE_BOUNDARY")
    ][:5]
    rule_reports = [
        rule_family_report(rows, rule_family) for rule_family in RULE_FAMILIES
    ]
    metrics = aggregate_counts(rows)
    baseline_metrics = (
        aggregate_counts(baseline_rows)
        if enable_single_hole_positive_witness_closure
        else None
    )
    pre_ceiling_metrics = (
        aggregate_counts(pre_ceiling_rows)
        if enable_carrier_locked_pressure_ceiling
        else None
    )
    closure_report = single_hole_closure_report(rows)
    ceiling_report = carrier_locked_ceiling_report(rows)

    summary = {
        "mode": "offline_composite_exclusion_boundary_probe",
        "start_anchor": start_anchor,
        "max_anchor": max_anchor,
        "candidate_bound": candidate_bound,
        "single_hole_positive_witness_closure_enabled": (
            enable_single_hole_positive_witness_closure
        ),
        "carrier_locked_pressure_ceiling_enabled": (
            enable_carrier_locked_pressure_ceiling
        ),
        "carrier_lock_predicate": carrier_lock_predicate,
        "witness_bound": witness_bound,
        "row_count": len(rows),
        **metrics,
        "before_single_hole_closure_metrics": baseline_metrics,
        "before_carrier_locked_pressure_ceiling_metrics": pre_ceiling_metrics,
        **closure_report,
        **ceiling_report,
        "rule_family_reports": rule_reports,
        "first_failure_examples": first_failure_examples,
        "elimination_rule_set": (
            "composite_exclusion_single_hole_carrier_locked_ceiling_v1"
            if enable_carrier_locked_pressure_ceiling
            else "composite_exclusion_single_hole_closure_v1"
            if enable_single_hole_positive_witness_closure
            else "composite_exclusion_three_status_v1"
        ),
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
        enable_single_hole_positive_witness_closure=(
            args.enable_single_hole_positive_witness_closure
        ),
        witness_bound=args.witness_bound,
        enable_carrier_locked_pressure_ceiling=(
            args.enable_carrier_locked_pressure_ceiling
        ),
        carrier_lock_predicate=args.carrier_lock_predicate,
    )
    write_artifacts(rows, summary, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
