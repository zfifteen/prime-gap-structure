#!/usr/bin/env python3
"""High-scale decade-window runner for the Rule X logic engine."""

from __future__ import annotations

import argparse
import csv
import json
import math
import time
from functools import lru_cache
from pathlib import Path

from sympy import factorint, nextprime


WHEEL_OPEN_MOD30 = {1, 7, 11, 13, 17, 19, 23, 29}
STATUS_REJECTED = "REJECTED"
STATUS_UNRESOLVED = "UNRESOLVED"
STATUS_RESOLVED_SURVIVOR = "RESOLVED_SURVIVOR"


@lru_cache(maxsize=None)
def factors(n: int) -> tuple[tuple[int, int], ...]:
    return tuple(sorted((int(p), int(e)) for p, e in factorint(n).items()))


def is_prime_exact(n: int) -> bool:
    return factors(n) == ((n, 1),)


def divisor_count(n: int) -> int:
    total = 1
    for _, exponent in factors(n):
        total *= exponent + 1
    return total


def is_known_composite(n: int) -> bool:
    return n % 30 not in WHEEL_OPEN_MOD30 or not is_prime_exact(n)


def candidate_offsets(anchor_p: int, candidate_bound: int) -> list[int]:
    return [
        offset
        for offset in range(1, candidate_bound + 1)
        if (anchor_p + offset) % 30 in WHEEL_OPEN_MOD30
    ]


def consecutive_prime_anchors(start: int, count: int) -> list[int]:
    anchors: list[int] = []
    current = int(nextprime(start - 1))
    for _ in range(count):
        anchors.append(current)
        current = int(nextprime(current))
    return anchors


def actual_offset(anchor_p: int) -> int:
    return int(nextprime(anchor_p)) - anchor_p


def analyze_anchor(anchor_p: int, candidate_bound: int) -> dict[str, object]:
    offsets = candidate_offsets(anchor_p, candidate_bound)
    q_offset = actual_offset(anchor_p)
    if q_offset > candidate_bound:
        return {
            "anchor_p": anchor_p,
            "actual_offset": q_offset,
            "candidate_count": len(offsets),
            "rejected_count": 0,
            "active_count": 0,
            "resolved_count": 0,
            "unresolved_count": 0,
            "unique_resolved": False,
            "unique_resolved_match": False,
            "true_boundary_rejected": False,
            "candidate_bound_miss": True,
        }

    candidate_states: list[tuple[int, str, int | None, int | None]] = []
    unresolved_count = 0
    carrier_offset: int | None = None
    carrier_d: int | None = None

    offset_set = set(offsets)
    for offset in range(1, candidate_bound + 1):
        n = anchor_p + offset
        if offset in offset_set:
            if is_known_composite(n):
                status = STATUS_REJECTED
            elif unresolved_count > 0:
                status = STATUS_UNRESOLVED
            else:
                status = STATUS_RESOLVED_SURVIVOR
            candidate_states.append((offset, status, carrier_offset, carrier_d))

        if is_known_composite(n):
            n_d = divisor_count(n)
            if carrier_d is None or n_d < carrier_d:
                carrier_offset = offset
                carrier_d = n_d
        else:
            unresolved_count += 1

    lock_carrier_offset: int | None = None
    lock_carrier_d: int | None = None
    for _, status, state_carrier_offset, state_carrier_d in candidate_states:
        if status == STATUS_RESOLVED_SURVIVOR and state_carrier_offset is not None:
            lock_carrier_offset = state_carrier_offset
            lock_carrier_d = state_carrier_d
            break

    threat_offset: int | None = None
    if lock_carrier_offset is not None and lock_carrier_d is not None:
        for offset in range(lock_carrier_offset + 1, candidate_bound + 1):
            n = anchor_p + offset
            if not is_known_composite(n):
                continue
            if divisor_count(n) < lock_carrier_d:
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
        "anchor_p": anchor_p,
        "actual_offset": q_offset,
        "candidate_count": len(candidate_states),
        "rejected_count": rejected_count,
        "active_count": len(active),
        "resolved_count": len(resolved),
        "unresolved_count": len(unresolved),
        "unique_resolved": unique_resolved,
        "unique_resolved_match": unique_resolved and resolved[0] == q_offset,
        "true_boundary_rejected": q_offset not in active,
        "candidate_bound_miss": False,
    }


def run_decade(power: int, window_anchors: int, candidate_bound: int, out_dir: Path) -> dict[str, object]:
    start_time = time.perf_counter()
    start = 10**power
    anchors = consecutive_prime_anchors(start, window_anchors)
    setup_seconds = time.perf_counter() - start_time

    eval_start = time.perf_counter()
    rows = [analyze_anchor(anchor, candidate_bound) for anchor in anchors]
    evaluation_seconds = time.perf_counter() - eval_start

    write_start = time.perf_counter()
    out_dir.mkdir(parents=True, exist_ok=True)
    columns = [
        "anchor_p",
        "actual_offset",
        "candidate_count",
        "rejected_count",
        "active_count",
        "resolved_count",
        "unresolved_count",
        "unique_resolved",
        "unique_resolved_match",
        "true_boundary_rejected",
        "candidate_bound_miss",
    ]
    with (out_dir / "anchor_summary.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    total_seconds = time.perf_counter() - start_time
    candidate_count = sum(int(row["candidate_count"]) for row in rows)
    summary = {
        "power": power,
        "decade_start": start,
        "window_anchors": window_anchors,
        "candidate_bound": candidate_bound,
        "anchor_count": len(rows),
        "candidate_count": candidate_count,
        "unique_resolved_count": sum(1 for row in rows if row["unique_resolved"]),
        "unique_resolved_match_count": sum(
            1 for row in rows if row["unique_resolved_match"]
        ),
        "true_boundary_rejected_count": sum(
            1 for row in rows if row["true_boundary_rejected"]
        ),
        "candidate_bound_miss_count": sum(
            1 for row in rows if row["candidate_bound_miss"]
        ),
        "setup_seconds": setup_seconds,
        "evaluation_seconds": evaluation_seconds,
        "write_seconds": time.perf_counter() - write_start,
        "total_seconds": total_seconds,
        "anchors_per_second": len(rows) / total_seconds if total_seconds else 0.0,
        "candidates_per_second": candidate_count / total_seconds if total_seconds else 0.0,
        "factor_cache_size": factors.cache_info().currsize,
    }
    with (out_dir / "summary.json").open("w") as handle:
        json.dump(summary, handle, indent=2)
        handle.write("\n")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--min-power", type=int, default=8)
    parser.add_argument("--max-power", type=int, default=18)
    parser.add_argument("--window-anchors", type=int, default=256)
    parser.add_argument("--candidate-bound", type=int, default=1024)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    rows = []
    for power in range(args.min_power, args.max_power + 1):
        summary = run_decade(
            power,
            args.window_anchors,
            args.candidate_bound,
            args.out_dir / f"10e{power}",
        )
        rows.append(summary)
        print(json.dumps(summary, indent=2))

    with (args.out_dir / "summary.json").open("w") as handle:
        json.dump({"rows": rows}, handle, indent=2)
        handle.write("\n")


if __name__ == "__main__":
    main()
