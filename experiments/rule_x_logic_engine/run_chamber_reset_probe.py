#!/usr/bin/env python3
"""Probe the Rule X chamber-reset interpretation of later unresolved tails."""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from experiments.rule_x_logic_engine.run_decade_window import (
    STATUS_REJECTED,
    STATUS_RESOLVED_SURVIVOR,
    STATUS_UNRESOLVED,
    actual_offset,
    candidate_offsets,
    consecutive_prime_anchors,
    divisor_count,
    is_known_composite,
)


def final_states(anchor_p: int, candidate_bound: int) -> list[tuple[int, int, str]]:
    offsets = candidate_offsets(anchor_p, candidate_bound)
    offset_set = set(offsets)
    candidate_states: list[tuple[int, int, str, int | None, int | None]] = []
    unresolved_count = 0
    carrier_offset: int | None = None
    carrier_d: int | None = None

    for offset in range(1, candidate_bound + 1):
        n = anchor_p + offset
        if offset in offset_set:
            if is_known_composite(n):
                status = STATUS_REJECTED
            elif unresolved_count > 0:
                status = STATUS_UNRESOLVED
            else:
                status = STATUS_RESOLVED_SURVIVOR
            candidate_states.append((offset, n, status, carrier_offset, carrier_d))

        if is_known_composite(n):
            n_d = divisor_count(n)
            if carrier_d is None or n_d < carrier_d:
                carrier_offset = offset
                carrier_d = n_d
        else:
            unresolved_count += 1

    lock_carrier_offset: int | None = None
    lock_carrier_d: int | None = None
    for _, _, status, state_carrier_offset, state_carrier_d in candidate_states:
        if status == STATUS_RESOLVED_SURVIVOR and state_carrier_offset is not None:
            lock_carrier_offset = state_carrier_offset
            lock_carrier_d = state_carrier_d
            break

    threat_offset: int | None = None
    if lock_carrier_offset is not None and lock_carrier_d is not None:
        for offset in range(lock_carrier_offset + 1, candidate_bound + 1):
            n = anchor_p + offset
            if is_known_composite(n) and divisor_count(n) < lock_carrier_d:
                threat_offset = offset
                break

    active: list[tuple[int, int, str]] = []
    for offset, n, status, _, _ in candidate_states:
        final_status = status
        if threat_offset is not None and offset > threat_offset:
            final_status = STATUS_REJECTED
        if final_status != STATUS_REJECTED:
            active.append((offset, n, final_status))
    return active


def analyze_anchor(anchor_p: int, candidate_bound: int) -> dict[str, object]:
    q_offset = actual_offset(anchor_p)
    active = final_states(anchor_p, candidate_bound)
    resolved = [state for state in active if state[2] == STATUS_RESOLVED_SURVIVOR]
    unresolved = [state for state in active if state[2] == STATUS_UNRESOLVED]

    old_unique = len(resolved) == 1 and not unresolved
    reset_offset = resolved[0][0] if resolved else None
    tail_after_reset = [
        state for state in unresolved if reset_offset is not None and state[0] > reset_offset
    ]

    return {
        "anchor_p": anchor_p,
        "actual_offset": q_offset,
        "active_count": len(active),
        "resolved_count": len(resolved),
        "unresolved_count": len(unresolved),
        "old_unique_match": old_unique and resolved[0][0] == q_offset,
        "reset_emitted_offset": reset_offset,
        "reset_exact_match": reset_offset == q_offset,
        "reset_false_emit": reset_offset is not None and reset_offset != q_offset,
        "tail_after_reset_count": len(tail_after_reset),
        "all_unresolved_after_reset": len(tail_after_reset) == len(unresolved),
        "candidate_bound_miss": q_offset > candidate_bound,
    }


def run_decade(power: int, window_anchors: int, candidate_bound: int, out_dir: Path) -> dict[str, object]:
    start_time = time.perf_counter()
    anchors = consecutive_prime_anchors(10**power, window_anchors)
    setup_seconds = time.perf_counter() - start_time

    eval_start = time.perf_counter()
    rows = [analyze_anchor(anchor, candidate_bound) for anchor in anchors]
    evaluation_seconds = time.perf_counter() - eval_start

    write_start = time.perf_counter()
    out_dir.mkdir(parents=True, exist_ok=True)
    columns = [
        "anchor_p",
        "actual_offset",
        "active_count",
        "resolved_count",
        "unresolved_count",
        "old_unique_match",
        "reset_emitted_offset",
        "reset_exact_match",
        "reset_false_emit",
        "tail_after_reset_count",
        "all_unresolved_after_reset",
        "candidate_bound_miss",
    ]
    with (out_dir / "anchor_summary.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    total_seconds = time.perf_counter() - start_time
    old_unique_match_count = sum(1 for row in rows if row["old_unique_match"])
    reset_exact_match_count = sum(1 for row in rows if row["reset_exact_match"])
    reset_false_emit_count = sum(1 for row in rows if row["reset_false_emit"])
    tail_case_count = sum(1 for row in rows if int(row["tail_after_reset_count"]) > 0)
    tail_candidate_count = sum(int(row["tail_after_reset_count"]) for row in rows)
    summary = {
        "power": power,
        "decade_start": 10**power,
        "window_anchors": window_anchors,
        "candidate_bound": candidate_bound,
        "anchor_count": len(rows),
        "old_unique_match_count": old_unique_match_count,
        "reset_exact_match_count": reset_exact_match_count,
        "reset_false_emit_count": reset_false_emit_count,
        "tail_case_count": tail_case_count,
        "tail_candidate_count": tail_candidate_count,
        "candidate_bound_miss_count": sum(1 for row in rows if row["candidate_bound_miss"]),
        "all_unresolved_after_reset_count": sum(
            1 for row in rows if row["all_unresolved_after_reset"]
        ),
        "setup_seconds": setup_seconds,
        "evaluation_seconds": evaluation_seconds,
        "write_seconds": time.perf_counter() - write_start,
        "total_seconds": total_seconds,
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
