#!/usr/bin/env python3
"""Summary-only scale runner for the Rule X logic engine."""

from __future__ import annotations

import argparse
import csv
import json
import math
import time
from pathlib import Path


WHEEL_OPEN_MOD30 = {1, 7, 11, 13, 17, 19, 23, 29}
STATUS_REJECTED = "REJECTED"
STATUS_UNRESOLVED = "UNRESOLVED"
STATUS_RESOLVED_SURVIVOR = "RESOLVED_SURVIVOR"


def prime_sieve(limit: int) -> bytearray:
    sieve = bytearray(b"\x01") * (limit + 1)
    if limit >= 0:
        sieve[0] = 0
    if limit >= 1:
        sieve[1] = 0
    for p in range(2, math.isqrt(limit) + 1):
        if sieve[p]:
            start = p * p
            sieve[start : limit + 1 : p] = b"\x00" * (((limit - start) // p) + 1)
    return sieve


def next_prime_after(n: int, prime_flags: bytearray) -> int:
    candidate = n + 1
    while not prime_flags[candidate]:
        candidate += 1
    return candidate


def divisor_counts(limit: int) -> list[int]:
    counts = [0] * (limit + 1)
    for divisor in range(1, limit + 1):
        for multiple in range(divisor, limit + 1, divisor):
            counts[multiple] += 1
    return counts


def witness_flags(limit: int, witness_bound: int) -> bytearray:
    flags = bytearray(limit + 1)
    for factor in range(2, witness_bound + 1):
        for multiple in range(factor * 2, limit + 1, factor):
            flags[multiple] = 1
    return flags


def candidate_offsets(anchor_p: int, candidate_bound: int) -> list[int]:
    return [
        offset
        for offset in range(1, candidate_bound + 1)
        if (anchor_p + offset) % 30 in WHEEL_OPEN_MOD30
    ]


def first_actual_offset(anchor_p: int, candidate_bound: int, prime_flags: bytearray) -> int:
    for offset in range(1, candidate_bound + 1):
        if prime_flags[anchor_p + offset]:
            return offset
    raise ValueError(f"candidate_bound does not reach next prime for anchor {anchor_p}")


def analyze_anchor(
    anchor_p: int,
    candidate_bound: int,
    witness_bound: int,
    shadow_threshold: int,
    prime_flags: bytearray,
    witness: bytearray,
    dcounts: list[int],
) -> dict[str, object]:
    offsets = candidate_offsets(anchor_p, candidate_bound)
    actual_offset = first_actual_offset(anchor_p, candidate_bound, prime_flags)
    candidate_states: list[tuple[int, str, int | None, int | None]] = []
    unresolved_count = 0
    carrier_offset: int | None = None
    carrier_d: int | None = None

    for offset in range(1, candidate_bound + 1):
        n = anchor_p + offset
        if offset in offsets:
            if witness[n]:
                status = STATUS_REJECTED
            elif unresolved_count > 0 or n >= shadow_threshold:
                status = STATUS_UNRESOLVED
            else:
                status = STATUS_RESOLVED_SURVIVOR
            candidate_states.append((offset, status, carrier_offset, carrier_d))

        if n % 30 not in WHEEL_OPEN_MOD30 or witness[n]:
            n_d = dcounts[n]
            if carrier_d is None or n_d < carrier_d:
                carrier_offset = offset
                carrier_d = n_d
        else:
            unresolved_count += 1

    lock_carrier_offset: int | None = None
    lock_carrier_d: int | None = None
    for offset, status, state_carrier_offset, state_carrier_d in candidate_states:
        if status == STATUS_RESOLVED_SURVIVOR and state_carrier_offset is not None:
            lock_carrier_offset = state_carrier_offset
            lock_carrier_d = state_carrier_d
            break

    threat_offset: int | None = None
    if lock_carrier_offset is not None and lock_carrier_d is not None:
        for offset in range(lock_carrier_offset + 1, candidate_bound + 1):
            n = anchor_p + offset
            if n % 30 in WHEEL_OPEN_MOD30 and not witness[n]:
                continue
            if dcounts[n] < lock_carrier_d:
                threat_offset = offset
                break

    active: list[int] = []
    resolved: list[int] = []
    unresolved: list[int] = []
    rejected_count = 0
    for offset, status, _, _ in candidate_states:
        final_status = status
        if threat_offset is not None and offset > threat_offset:
            final_status = STATUS_REJECTED
        if final_status == STATUS_REJECTED:
            rejected_count += 1
        else:
            active.append(offset)
            if final_status == STATUS_RESOLVED_SURVIVOR:
                resolved.append(offset)
            else:
                unresolved.append(offset)

    unique_resolved = len(resolved) == 1 and not unresolved
    return {
        "candidate_count": len(candidate_states),
        "rejected_count": rejected_count,
        "active_count": len(active),
        "resolved_count": len(resolved),
        "unresolved_count": len(unresolved),
        "unique_resolved": unique_resolved,
        "unique_resolved_match": unique_resolved and resolved[0] == actual_offset,
        "true_boundary_rejected": actual_offset not in active,
    }


def run(
    start_anchor: int,
    max_anchor: int,
    candidate_bound: int,
    witness_bound: int,
    out_dir: Path,
) -> dict[str, object]:
    total_start = time.perf_counter()
    out_dir.mkdir(parents=True, exist_ok=True)
    limit = max_anchor + candidate_bound + witness_bound + 100
    setup_start = time.perf_counter()
    prime_flags = prime_sieve(limit)
    dcounts = divisor_counts(max_anchor + candidate_bound)
    witness = witness_flags(max_anchor + candidate_bound, witness_bound)
    shadow_threshold = next_prime_after(witness_bound, prime_flags) ** 2
    setup_seconds = time.perf_counter() - setup_start

    anchors = [
        n for n in range(start_anchor, max_anchor + 1) if n >= 11 and prime_flags[n]
    ]
    eval_start = time.perf_counter()
    rows: list[dict[str, object]] = []
    totals = {
        "candidate_count": 0,
        "rejected_count": 0,
        "active_unique_count": 0,
        "unique_resolved_count": 0,
        "unique_resolved_match_count": 0,
        "true_boundary_rejected_count": 0,
    }
    for anchor_p in anchors:
        row = analyze_anchor(
            anchor_p,
            candidate_bound,
            witness_bound,
            shadow_threshold,
            prime_flags,
            witness,
            dcounts,
        )
        rows.append({"anchor_p": anchor_p, **row})
        totals["candidate_count"] += int(row["candidate_count"])
        totals["rejected_count"] += int(row["rejected_count"])
        if int(row["active_count"]) == 1:
            totals["active_unique_count"] += 1
        if bool(row["unique_resolved"]):
            totals["unique_resolved_count"] += 1
        if bool(row["unique_resolved_match"]):
            totals["unique_resolved_match_count"] += 1
        if bool(row["true_boundary_rejected"]):
            totals["true_boundary_rejected_count"] += 1
    eval_seconds = time.perf_counter() - eval_start

    write_start = time.perf_counter()
    summary = {
        "start_anchor": start_anchor,
        "max_anchor": max_anchor,
        "candidate_bound": candidate_bound,
        "witness_bound": witness_bound,
        "shadow_threshold": shadow_threshold,
        "anchor_count": len(anchors),
        **totals,
    }

    with (out_dir / "anchor_summary.csv").open("w", newline="") as handle:
        columns = [
            "anchor_p",
            "candidate_count",
            "rejected_count",
            "active_count",
            "resolved_count",
            "unresolved_count",
            "unique_resolved",
            "unique_resolved_match",
            "true_boundary_rejected",
        ]
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    with (out_dir / "summary.json").open("w") as handle:
        json.dump(summary, handle, indent=2)
        handle.write("\n")
    write_seconds = time.perf_counter() - write_start
    total_seconds = time.perf_counter() - total_start
    summary.update(
        {
            "setup_seconds": setup_seconds,
            "evaluation_seconds": eval_seconds,
            "write_seconds": write_seconds,
            "total_seconds": total_seconds,
            "anchors_per_second": len(anchors) / total_seconds if total_seconds else 0.0,
            "candidates_per_second": (
                totals["candidate_count"] / total_seconds if total_seconds else 0.0
            ),
        }
    )
    with (out_dir / "summary.json").open("w") as handle:
        json.dump(summary, handle, indent=2)
        handle.write("\n")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start-anchor", type=int, default=11)
    parser.add_argument("--max-anchor", type=int, required=True)
    parser.add_argument("--candidate-bound", type=int, default=128)
    parser.add_argument("--witness-bound", type=int, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    print(
        json.dumps(
            run(
                args.start_anchor,
                args.max_anchor,
                args.candidate_bound,
                args.witness_bound,
                args.out_dir,
            ),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
