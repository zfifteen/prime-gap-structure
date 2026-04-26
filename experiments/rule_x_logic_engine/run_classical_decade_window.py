#!/usr/bin/env python3
"""Classical next-prime decade-window baseline."""

from __future__ import annotations

import argparse
import csv
import json
import time
from pathlib import Path

from sympy import isprime, nextprime


WHEEL_OPEN_MOD30 = {1, 7, 11, 13, 17, 19, 23, 29}


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


def analyze_anchor(anchor_p: int, candidate_bound: int) -> dict[str, object]:
    offsets = candidate_offsets(anchor_p, candidate_bound)
    actual_offset = int(nextprime(anchor_p)) - anchor_p
    emitted_offset: int | None = None
    tested_count = 0

    for offset in offsets:
        tested_count += 1
        if isprime(anchor_p + offset):
            emitted_offset = offset
            break

    return {
        "anchor_p": anchor_p,
        "actual_offset": actual_offset,
        "candidate_count": len(offsets),
        "tested_count": tested_count,
        "emitted_offset": emitted_offset,
        "exact_match": emitted_offset == actual_offset,
        "false_emit": emitted_offset is not None and emitted_offset != actual_offset,
        "candidate_bound_miss": actual_offset > candidate_bound,
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
        "tested_count",
        "emitted_offset",
        "exact_match",
        "false_emit",
        "candidate_bound_miss",
    ]
    with (out_dir / "anchor_summary.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    total_seconds = time.perf_counter() - start_time
    candidate_count = sum(int(row["candidate_count"]) for row in rows)
    tested_count = sum(int(row["tested_count"]) for row in rows)
    exact_match_count = sum(1 for row in rows if row["exact_match"])
    false_emit_count = sum(1 for row in rows if row["false_emit"])
    candidate_bound_miss_count = sum(1 for row in rows if row["candidate_bound_miss"])
    summary = {
        "power": power,
        "decade_start": start,
        "window_anchors": window_anchors,
        "candidate_bound": candidate_bound,
        "anchor_count": len(rows),
        "candidate_count": candidate_count,
        "tested_count": tested_count,
        "exact_match_count": exact_match_count,
        "false_emit_count": false_emit_count,
        "candidate_bound_miss_count": candidate_bound_miss_count,
        "setup_seconds": setup_seconds,
        "evaluation_seconds": evaluation_seconds,
        "write_seconds": time.perf_counter() - write_start,
        "total_seconds": total_seconds,
        "anchors_per_second": len(rows) / total_seconds if total_seconds else 0.0,
        "tested_candidates_per_second": tested_count / total_seconds if total_seconds else 0.0,
        "window_candidates_per_second": candidate_count / total_seconds if total_seconds else 0.0,
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
