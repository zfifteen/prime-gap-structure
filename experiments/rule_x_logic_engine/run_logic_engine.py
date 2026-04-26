#!/usr/bin/env python3
"""Tiny candidate-boundary logic engine for GWR/NLSC consistency collapse."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path


WHEEL_OPEN_MOD30 = {1, 7, 11, 13, 17, 19, 23, 29}
STATUS_REJECTED = "REJECTED"
STATUS_UNRESOLVED = "UNRESOLVED"
STATUS_RESOLVED_SURVIVOR = "RESOLVED_SURVIVOR"
STATUS_SURVIVES = "SURVIVES"


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    limit = math.isqrt(n)
    factor = 5
    while factor <= limit:
        if n % factor == 0 or n % (factor + 2) == 0:
            return False
        factor += 6
    return True


def next_prime_after(n: int) -> int:
    candidate = n + 1
    while not is_prime(candidate):
        candidate += 1
    return candidate


def divisor_count(n: int) -> int:
    remaining = n
    total = 1
    factor = 2
    while factor * factor <= remaining:
        if remaining % factor == 0:
            exponent = 0
            while remaining % factor == 0:
                remaining //= factor
                exponent += 1
            total *= exponent + 1
        factor += 1 if factor == 2 else 2
    if remaining > 1:
        total *= 2
    return total


def primes_between(start: int, stop: int) -> list[int]:
    return [n for n in range(start, stop + 1) if is_prime(n)]


def candidate_offsets(anchor_p: int, candidate_bound: int) -> list[int]:
    return [
        offset
        for offset in range(1, candidate_bound + 1)
        if (anchor_p + offset) % 30 in WHEEL_OPEN_MOD30
    ]


def bounded_composite_witness(n: int, witness_bound: int) -> int | None:
    for factor in range(2, min(witness_bound, math.isqrt(n)) + 1):
        if n % factor == 0:
            return factor
    return None


def known_composite_by_witness(n: int, witness_bound: int) -> bool:
    return n % 30 not in WHEEL_OPEN_MOD30 or bounded_composite_witness(n, witness_bound) is not None


def chamber_carrier(anchor_p: int, offset: int) -> dict[str, int | None]:
    composites: list[tuple[int, int]] = []
    for n in range(anchor_p + 1, anchor_p + offset):
        if not is_prime(n):
            composites.append((n, divisor_count(n)))
    if not composites:
        return {
            "carrier": None,
            "carrier_offset": None,
            "carrier_d": None,
            "post_carrier_lower_d_count": 0,
            "post_carrier_ge_d_count": 0,
        }
    carrier, carrier_d = min(composites, key=lambda item: (item[1], item[0]))
    post = [(n, d) for n, d in composites if n > carrier]
    return {
        "carrier": carrier,
        "carrier_offset": carrier - anchor_p,
        "carrier_d": carrier_d,
        "post_carrier_lower_d_count": sum(1 for _, d in post if d < carrier_d),
        "post_carrier_ge_d_count": sum(1 for _, d in post if d >= carrier_d),
    }


def witness_chamber_carrier(
    anchor_p: int, offset: int, witness_bound: int
) -> dict[str, object]:
    composites: list[tuple[int, int]] = []
    unresolved: list[int] = []
    for n in range(anchor_p + 1, anchor_p + offset):
        if known_composite_by_witness(n, witness_bound):
            composites.append((n, divisor_count(n)))
        else:
            unresolved.append(n - anchor_p)
    if not composites:
        return {
            "carrier": None,
            "carrier_offset": None,
            "carrier_d": None,
            "unresolved_offsets": unresolved,
        }
    carrier, carrier_d = min(composites, key=lambda item: (item[1], item[0]))
    return {
        "carrier": carrier,
        "carrier_offset": carrier - anchor_p,
        "carrier_d": carrier_d,
        "unresolved_offsets": unresolved,
    }


def label_free_status(anchor_p: int, offset: int, witness_bound: int) -> dict[str, object]:
    candidate_q = anchor_p + offset
    witness = bounded_composite_witness(candidate_q, witness_bound)
    carrier = witness_chamber_carrier(anchor_p, offset, witness_bound)
    shadow_threshold = next_prime_after(witness_bound) ** 2
    if witness is not None:
        return {
            "label_status": STATUS_REJECTED,
            "label_reasons": f"CANDIDATE_WITNESS_FACTOR_{witness}",
            "label_unresolved_offsets": "",
            "label_carrier": carrier["carrier"],
            "label_carrier_offset": carrier["carrier_offset"],
            "label_carrier_d": carrier["carrier_d"],
        }
    unresolved = list(carrier["unresolved_offsets"])
    unresolved_reasons: list[str] = []
    if unresolved:
        unresolved_reasons.append("UNRESOLVED_INTERIOR_OPEN")
    if candidate_q >= shadow_threshold:
        unresolved_reasons.append("SEMIPRIME_SHADOW_LANDMARK_HOLD")
    if unresolved_reasons:
        return {
            "label_status": STATUS_UNRESOLVED,
            "label_reasons": " ".join(unresolved_reasons),
            "label_unresolved_offsets": " ".join(str(offset) for offset in unresolved),
            "label_carrier": carrier["carrier"],
            "label_carrier_offset": carrier["carrier_offset"],
            "label_carrier_d": carrier["carrier_d"],
        }
    return {
        "label_status": STATUS_RESOLVED_SURVIVOR,
        "label_reasons": "",
        "label_unresolved_offsets": "",
        "label_carrier": carrier["carrier"],
        "label_carrier_offset": carrier["carrier_offset"],
        "label_carrier_d": carrier["carrier_d"],
    }


def analyze_candidate(anchor_p: int, offset: int, witness_bound: int) -> dict[str, object]:
    candidate_q = anchor_p + offset
    carrier = chamber_carrier(anchor_p, offset)
    label = label_free_status(anchor_p, offset, witness_bound)
    interior_primes = primes_between(anchor_p + 1, candidate_q - 1)
    exact_reasons: list[str] = []
    structural_reasons: list[str] = []

    if carrier["post_carrier_lower_d_count"]:
        structural_reasons.append("NLSC_VIOLATION")
    if carrier["carrier"] is None:
        structural_reasons.append("NO_INTERIOR_COMPOSITE_CARRIER")

    if not is_prime(candidate_q):
        exact_reasons.append("CANDIDATE_COMPOSITE")
    if interior_primes:
        exact_reasons.append("INTERIOR_PRIME_BEFORE_CANDIDATE")
    exact_reasons.extend(structural_reasons)

    return {
        "anchor_p": anchor_p,
        "offset": offset,
        "candidate_q": candidate_q,
        "carrier": carrier["carrier"],
        "carrier_offset": carrier["carrier_offset"],
        "carrier_d": carrier["carrier_d"],
        "post_carrier_lower_d_count": carrier["post_carrier_lower_d_count"],
        "post_carrier_ge_d_count": carrier["post_carrier_ge_d_count"],
        "label_status": label["label_status"],
        "label_reasons": label["label_reasons"],
        "label_unresolved_offsets": label["label_unresolved_offsets"],
        "label_carrier": label["label_carrier"],
        "label_carrier_offset": label["label_carrier_offset"],
        "label_carrier_d": label["label_carrier_d"],
        "interior_prime_offsets": " ".join(str(n - anchor_p) for n in interior_primes),
        "structural_status": STATUS_REJECTED if structural_reasons else STATUS_SURVIVES,
        "structural_reasons": " ".join(structural_reasons),
        "exact_status": STATUS_REJECTED if exact_reasons else STATUS_SURVIVES,
        "exact_reasons": " ".join(exact_reasons),
    }


def first_carrier_lock(
    anchor_p: int, candidate_bound: int, require_prime_candidate: bool = False
) -> dict[str, object]:
    """Return the first-carrier lock and its first lower-divisor threat."""
    for offset in range(1, candidate_bound + 1):
        if require_prime_candidate and not is_prime(anchor_p + offset):
            continue
        carrier = chamber_carrier(anchor_p, offset)
        if carrier["carrier"] is not None:
            carrier_offset = int(carrier["carrier_offset"])
            carrier_d = int(carrier["carrier_d"])
            for threat_offset in range(carrier_offset + 1, candidate_bound + 1):
                threat_n = anchor_p + threat_offset
                if is_prime(threat_n):
                    continue
                threat_d = divisor_count(threat_n)
                if threat_d < carrier_d:
                    return {
                        "locked": True,
                        "lock_carrier": carrier["carrier"],
                        "lock_carrier_offset": carrier_offset,
                        "lock_carrier_d": carrier_d,
                        "threat": threat_n,
                        "threat_offset": threat_offset,
                        "threat_d": threat_d,
                    }
            return {
                "locked": True,
                "lock_carrier": carrier["carrier"],
                "lock_carrier_offset": carrier_offset,
                "lock_carrier_d": carrier_d,
                "threat": None,
                "threat_offset": None,
                "threat_d": None,
            }
    return {
        "locked": False,
        "lock_carrier": None,
        "lock_carrier_offset": None,
        "lock_carrier_d": None,
        "threat": None,
        "threat_offset": None,
        "threat_d": None,
    }


def label_free_survivor_lock(
    anchor_p: int, candidate_bound: int, witness_bound: int
) -> dict[str, object]:
    """Return the first label-free resolved carrier lock and certified threat."""
    for offset in candidate_offsets(anchor_p, candidate_bound):
        label = label_free_status(anchor_p, offset, witness_bound)
        if label["label_status"] != STATUS_RESOLVED_SURVIVOR:
            continue
        if label["label_carrier"] is None:
            continue
        carrier_offset = int(label["label_carrier_offset"])
        carrier_d = int(label["label_carrier_d"])
        for threat_offset in range(carrier_offset + 1, candidate_bound + 1):
            threat_n = anchor_p + threat_offset
            if not known_composite_by_witness(threat_n, witness_bound):
                continue
            threat_d = divisor_count(threat_n)
            if threat_d < carrier_d:
                return {
                    "locked": True,
                    "lock_carrier": label["label_carrier"],
                    "lock_carrier_offset": carrier_offset,
                    "lock_carrier_d": carrier_d,
                    "threat": threat_n,
                    "threat_offset": threat_offset,
                    "threat_d": threat_d,
                }
        return {
            "locked": True,
            "lock_carrier": label["label_carrier"],
            "lock_carrier_offset": carrier_offset,
            "lock_carrier_d": carrier_d,
            "threat": None,
            "threat_offset": None,
            "threat_d": None,
        }
    return {
        "locked": False,
        "lock_carrier": None,
        "lock_carrier_offset": None,
        "lock_carrier_d": None,
        "threat": None,
        "threat_offset": None,
        "threat_d": None,
    }


def reset_transitions(records: list[dict[str, object]], actual_offset: int) -> list[dict[str, object]]:
    """Return carrier changes as candidate chambers extend rightward."""
    transitions: list[dict[str, object]] = []
    previous_carrier = None
    previous_offset = None
    previous_d = None
    for record in records:
        carrier = record["carrier"]
        carrier_offset = record["carrier_offset"]
        carrier_d = record["carrier_d"]
        if carrier is None:
            continue
        if previous_carrier is None:
            previous_carrier = carrier
            previous_offset = carrier_offset
            previous_d = carrier_d
            continue
        if carrier == previous_carrier:
            continue
        transitions.append(
            {
                "anchor_p": record["anchor_p"],
                "candidate_offset": record["offset"],
                "old_carrier": previous_carrier,
                "old_carrier_offset": previous_offset,
                "old_carrier_d": previous_d,
                "new_carrier": carrier,
                "new_carrier_offset": carrier_offset,
                "new_carrier_d": carrier_d,
                "actual_offset": actual_offset,
                "reset_before_actual_boundary": int(carrier_offset) < actual_offset,
                "reset_at_or_after_actual_boundary": int(carrier_offset) >= actual_offset,
            }
        )
        previous_carrier = carrier
        previous_offset = carrier_offset
        previous_d = carrier_d
    return transitions


def analyze_anchor(
    anchor_p: int, candidate_bound: int, witness_bound: int
) -> tuple[list[dict[str, object]], dict[str, object], list[dict[str, object]]]:
    records = [
        analyze_candidate(anchor_p, offset, witness_bound)
        for offset in candidate_offsets(anchor_p, candidate_bound)
    ]
    next_prime = next(q for q in range(anchor_p + 1, anchor_p + candidate_bound + 1) if is_prime(q))
    actual_offset = next_prime - anchor_p
    lock = first_carrier_lock(anchor_p, candidate_bound)
    survivor_lock = first_carrier_lock(
        anchor_p, candidate_bound, require_prime_candidate=True
    )
    label_lock = label_free_survivor_lock(anchor_p, candidate_bound, witness_bound)
    lock_threat_offset = lock["threat_offset"]
    survivor_lock_threat_offset = survivor_lock["threat_offset"]
    label_lock_threat_offset = label_lock["threat_offset"]
    for record in records:
        rule_x_reasons: list[str] = []
        survivor_lock_reasons: list[str] = []
        label_lock_reasons: list[str] = []
        if lock_threat_offset is not None and int(record["offset"]) > int(lock_threat_offset):
            rule_x_reasons.append("FIRST_CARRIER_LOCK_LOWER_D_THREAT_CEILING")
        if (
            survivor_lock_threat_offset is not None
            and int(record["offset"]) > int(survivor_lock_threat_offset)
        ):
            survivor_lock_reasons.append(
                "SURVIVOR_CARRIER_LOCK_LOWER_D_THREAT_CEILING"
            )
        if record["label_status"] == STATUS_REJECTED:
            label_lock_reasons.append(str(record["label_reasons"]))
        if (
            label_lock_threat_offset is not None
            and int(record["offset"]) > int(label_lock_threat_offset)
        ):
            label_lock_reasons.append("LABEL_FREE_LOCK_LOWER_D_THREAT_CEILING")
        if label_lock_reasons:
            label_lock_status = STATUS_REJECTED
        else:
            label_lock_status = str(record["label_status"])
        record["rule_x_status"] = STATUS_REJECTED if rule_x_reasons else STATUS_SURVIVES
        record["rule_x_reasons"] = " ".join(rule_x_reasons)
        record["survivor_lock_status"] = (
            STATUS_REJECTED if survivor_lock_reasons else STATUS_SURVIVES
        )
        record["survivor_lock_reasons"] = " ".join(survivor_lock_reasons)
        record["label_lock_status"] = label_lock_status
        record["label_lock_reasons"] = " ".join(label_lock_reasons)
        record["lock_carrier"] = lock["lock_carrier"]
        record["lock_carrier_offset"] = lock["lock_carrier_offset"]
        record["lock_carrier_d"] = lock["lock_carrier_d"]
        record["lock_threat"] = lock["threat"]
        record["lock_threat_offset"] = lock["threat_offset"]
        record["lock_threat_d"] = lock["threat_d"]
        record["survivor_lock_carrier"] = survivor_lock["lock_carrier"]
        record["survivor_lock_carrier_offset"] = survivor_lock["lock_carrier_offset"]
        record["survivor_lock_carrier_d"] = survivor_lock["lock_carrier_d"]
        record["survivor_lock_threat"] = survivor_lock["threat"]
        record["survivor_lock_threat_offset"] = survivor_lock["threat_offset"]
        record["survivor_lock_threat_d"] = survivor_lock["threat_d"]
        record["label_lock_carrier"] = label_lock["lock_carrier"]
        record["label_lock_carrier_offset"] = label_lock["lock_carrier_offset"]
        record["label_lock_carrier_d"] = label_lock["lock_carrier_d"]
        record["label_lock_threat"] = label_lock["threat"]
        record["label_lock_threat_offset"] = label_lock["threat_offset"]
        record["label_lock_threat_d"] = label_lock["threat_d"]

    structural_survivors = [
        int(record["offset"])
        for record in records
        if record["structural_status"] == "SURVIVES"
    ]
    rule_x_survivors = [
        int(record["offset"])
        for record in records
        if record["rule_x_status"] == "SURVIVES"
    ]
    survivor_lock_survivors = [
        int(record["offset"])
        for record in records
        if record["survivor_lock_status"] == "SURVIVES"
    ]
    label_active_survivors = [
        int(record["offset"])
        for record in records
        if record["label_lock_status"] != STATUS_REJECTED
    ]
    label_resolved_survivors = [
        int(record["offset"])
        for record in records
        if record["label_lock_status"] == STATUS_RESOLVED_SURVIVOR
    ]
    label_unresolved_survivors = [
        int(record["offset"])
        for record in records
        if record["label_lock_status"] == STATUS_UNRESOLVED
    ]
    exact_survivors = [
        int(record["offset"])
        for record in records
        if record["exact_status"] == "SURVIVES"
    ]
    rule_x_true_rejected = actual_offset not in rule_x_survivors
    survivor_lock_true_rejected = actual_offset not in survivor_lock_survivors
    label_lock_true_rejected = actual_offset not in label_active_survivors
    label_lock_unique_resolved = (
        len(label_resolved_survivors) == 1 and not label_unresolved_survivors
    )
    label_lock_unique_resolved_match = (
        label_lock_unique_resolved and label_resolved_survivors == [actual_offset]
    )
    summary = {
        "anchor_p": anchor_p,
        "actual_q": next_prime,
        "actual_offset": actual_offset,
        "candidate_count": len(records),
        "structural_survivor_count": len(structural_survivors),
        "structural_survivors": structural_survivors,
        "rule_x_survivor_count": len(rule_x_survivors),
        "rule_x_survivors": rule_x_survivors,
        "rule_x_true_rejected": rule_x_true_rejected,
        "survivor_lock_survivor_count": len(survivor_lock_survivors),
        "survivor_lock_survivors": survivor_lock_survivors,
        "survivor_lock_true_rejected": survivor_lock_true_rejected,
        "label_active_survivor_count": len(label_active_survivors),
        "label_active_survivors": label_active_survivors,
        "label_resolved_survivor_count": len(label_resolved_survivors),
        "label_resolved_survivors": label_resolved_survivors,
        "label_unresolved_survivor_count": len(label_unresolved_survivors),
        "label_unresolved_survivors": label_unresolved_survivors,
        "label_lock_true_rejected": label_lock_true_rejected,
        "label_lock_unique_resolved": label_lock_unique_resolved,
        "label_lock_unique_resolved_match": label_lock_unique_resolved_match,
        "lock_carrier": lock["lock_carrier"],
        "lock_carrier_offset": lock["lock_carrier_offset"],
        "lock_carrier_d": lock["lock_carrier_d"],
        "lock_threat": lock["threat"],
        "lock_threat_offset": lock["threat_offset"],
        "lock_threat_d": lock["threat_d"],
        "survivor_lock_carrier": survivor_lock["lock_carrier"],
        "survivor_lock_carrier_offset": survivor_lock["lock_carrier_offset"],
        "survivor_lock_carrier_d": survivor_lock["lock_carrier_d"],
        "survivor_lock_threat": survivor_lock["threat"],
        "survivor_lock_threat_offset": survivor_lock["threat_offset"],
        "survivor_lock_threat_d": survivor_lock["threat_d"],
        "label_lock_carrier": label_lock["lock_carrier"],
        "label_lock_carrier_offset": label_lock["lock_carrier_offset"],
        "label_lock_carrier_d": label_lock["lock_carrier_d"],
        "label_lock_threat": label_lock["threat"],
        "label_lock_threat_offset": label_lock["threat_offset"],
        "label_lock_threat_d": label_lock["threat_d"],
        "exact_survivor_count": len(exact_survivors),
        "exact_survivors": exact_survivors,
        "exact_unique_match": exact_survivors == [actual_offset],
    }
    return records, summary, reset_transitions(records, actual_offset)


def write_csv(path: Path, rows: list[dict[str, object]], columns: list[str]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def run(
    start_anchor: int,
    max_anchor: int,
    candidate_bound: int,
    witness_bound: int,
    out_dir: Path,
) -> dict[str, object]:
    out_dir.mkdir(parents=True, exist_ok=True)
    anchors = [p for p in range(start_anchor, max_anchor + 1) if is_prime(p) and p >= 11]
    all_records: list[dict[str, object]] = []
    anchor_rows: list[dict[str, object]] = []
    all_transitions: list[dict[str, object]] = []
    for anchor_p in anchors:
        records, summary, transitions = analyze_anchor(anchor_p, candidate_bound, witness_bound)
        all_records.extend(records)
        anchor_rows.append(summary)
        all_transitions.extend(transitions)

    exact_unique_matches = sum(1 for row in anchor_rows if row["exact_unique_match"])
    structural_unique = sum(1 for row in anchor_rows if row["structural_survivor_count"] == 1)
    exact_unique = sum(1 for row in anchor_rows if row["exact_survivor_count"] == 1)
    structural_rejections = sum(1 for row in all_records if row["structural_status"] == "REJECTED")
    rule_x_rejections = sum(1 for row in all_records if row["rule_x_status"] == "REJECTED")
    rule_x_true_rejections = sum(1 for row in anchor_rows if row["rule_x_true_rejected"])
    rule_x_unique = sum(1 for row in anchor_rows if row["rule_x_survivor_count"] == 1)
    survivor_lock_rejections = sum(
        1 for row in all_records if row["survivor_lock_status"] == "REJECTED"
    )
    survivor_lock_true_rejections = sum(
        1 for row in anchor_rows if row["survivor_lock_true_rejected"]
    )
    survivor_lock_unique = sum(
        1 for row in anchor_rows if row["survivor_lock_survivor_count"] == 1
    )
    label_lock_rejections = sum(
        1 for row in all_records if row["label_lock_status"] == STATUS_REJECTED
    )
    label_lock_true_rejections = sum(
        1 for row in anchor_rows if row["label_lock_true_rejected"]
    )
    label_lock_unique_resolved = sum(
        1 for row in anchor_rows if row["label_lock_unique_resolved"]
    )
    label_lock_unique_resolved_match = sum(
        1 for row in anchor_rows if row["label_lock_unique_resolved_match"]
    )
    label_lock_active_unique = sum(
        1 for row in anchor_rows if row["label_active_survivor_count"] == 1
    )
    exact_rejections = sum(1 for row in all_records if row["exact_status"] == "REJECTED")
    reset_before_actual = sum(
        1 for row in all_transitions if row["reset_before_actual_boundary"]
    )

    summary = {
        "start_anchor": start_anchor,
        "max_anchor": max_anchor,
        "candidate_bound": candidate_bound,
        "witness_bound": witness_bound,
        "anchor_count": len(anchor_rows),
        "candidate_count": len(all_records),
        "structural_rejection_count": structural_rejections,
        "structural_unique_anchor_count": structural_unique,
        "rule_x_rejection_count": rule_x_rejections,
        "rule_x_unique_anchor_count": rule_x_unique,
        "rule_x_true_boundary_rejected_count": rule_x_true_rejections,
        "survivor_lock_rejection_count": survivor_lock_rejections,
        "survivor_lock_unique_anchor_count": survivor_lock_unique,
        "survivor_lock_true_boundary_rejected_count": (
            survivor_lock_true_rejections
        ),
        "label_lock_rejection_count": label_lock_rejections,
        "label_lock_active_unique_anchor_count": label_lock_active_unique,
        "label_lock_unique_resolved_anchor_count": label_lock_unique_resolved,
        "label_lock_unique_resolved_match_count": label_lock_unique_resolved_match,
        "label_lock_true_boundary_rejected_count": label_lock_true_rejections,
        "reset_transition_count": len(all_transitions),
        "reset_before_actual_boundary_count": reset_before_actual,
        "exact_rejection_count": exact_rejections,
        "exact_unique_anchor_count": exact_unique,
        "exact_unique_match_count": exact_unique_matches,
        "verdict": (
            "exact_consistency_collapse"
            if exact_unique_matches == len(anchor_rows)
            else "not_collapsed"
        ),
    }

    write_csv(
        out_dir / "candidate_records.csv",
        all_records,
        [
            "anchor_p",
            "offset",
            "candidate_q",
            "carrier",
            "carrier_offset",
            "carrier_d",
            "post_carrier_lower_d_count",
            "post_carrier_ge_d_count",
            "label_status",
            "label_reasons",
            "label_unresolved_offsets",
            "label_carrier",
            "label_carrier_offset",
            "label_carrier_d",
            "lock_carrier",
            "lock_carrier_offset",
            "lock_carrier_d",
            "lock_threat",
            "lock_threat_offset",
            "lock_threat_d",
            "survivor_lock_carrier",
            "survivor_lock_carrier_offset",
            "survivor_lock_carrier_d",
            "survivor_lock_threat",
            "survivor_lock_threat_offset",
            "survivor_lock_threat_d",
            "label_lock_carrier",
            "label_lock_carrier_offset",
            "label_lock_carrier_d",
            "label_lock_threat",
            "label_lock_threat_offset",
            "label_lock_threat_d",
            "interior_prime_offsets",
            "structural_status",
            "structural_reasons",
            "rule_x_status",
            "rule_x_reasons",
            "survivor_lock_status",
            "survivor_lock_reasons",
            "label_lock_status",
            "label_lock_reasons",
            "exact_status",
            "exact_reasons",
        ],
    )
    write_csv(
        out_dir / "anchor_summary.csv",
        anchor_rows,
        [
            "anchor_p",
            "actual_q",
            "actual_offset",
            "candidate_count",
            "structural_survivor_count",
            "structural_survivors",
            "rule_x_survivor_count",
            "rule_x_survivors",
            "rule_x_true_rejected",
            "survivor_lock_survivor_count",
            "survivor_lock_survivors",
            "survivor_lock_true_rejected",
            "label_active_survivor_count",
            "label_active_survivors",
            "label_resolved_survivor_count",
            "label_resolved_survivors",
            "label_unresolved_survivor_count",
            "label_unresolved_survivors",
            "label_lock_true_rejected",
            "label_lock_unique_resolved",
            "label_lock_unique_resolved_match",
            "lock_carrier",
            "lock_carrier_offset",
            "lock_carrier_d",
            "lock_threat",
            "lock_threat_offset",
            "lock_threat_d",
            "survivor_lock_carrier",
            "survivor_lock_carrier_offset",
            "survivor_lock_carrier_d",
            "survivor_lock_threat",
            "survivor_lock_threat_offset",
            "survivor_lock_threat_d",
            "label_lock_carrier",
            "label_lock_carrier_offset",
            "label_lock_carrier_d",
            "label_lock_threat",
            "label_lock_threat_offset",
            "label_lock_threat_d",
            "exact_survivor_count",
            "exact_survivors",
            "exact_unique_match",
        ],
    )
    write_csv(
        out_dir / "reset_transitions.csv",
        all_transitions,
        [
            "anchor_p",
            "candidate_offset",
            "old_carrier",
            "old_carrier_offset",
            "old_carrier_d",
            "new_carrier",
            "new_carrier_offset",
            "new_carrier_d",
            "actual_offset",
            "reset_before_actual_boundary",
            "reset_at_or_after_actual_boundary",
        ],
    )
    with (out_dir / "summary.json").open("w") as handle:
        json.dump(summary, handle, indent=2)
        handle.write("\n")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start-anchor", type=int, default=11)
    parser.add_argument("--max-anchor", type=int, default=200)
    parser.add_argument("--candidate-bound", type=int, default=64)
    parser.add_argument("--witness-bound", type=int, default=31)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "results_11_200_b64",
    )
    args = parser.parse_args()
    summary = run(
        args.start_anchor,
        args.max_anchor,
        args.candidate_bound,
        args.witness_bound,
        args.out_dir,
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
