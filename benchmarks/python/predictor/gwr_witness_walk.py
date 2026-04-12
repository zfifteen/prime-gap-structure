#!/usr/bin/env python3
"""Lockstep witness-map check against the exact divisor-field boundary walk.

This script compares two exact next-prime recovery paths from one known prime
q on the current repo field:

- Path A scans rightward and stops at the first value with d(n) == 2.
- Path B reads the exact winner profile, uses W_d(q + 1, winner_d) to recover
  the winner witness, and then scans from that witness to the same prime
  boundary.

Both paths are exact on the current divisor field. The field itself still
classifies large residuals with gmpy2.is_prime in
z_band_prime_composite_field.divisor_counts_segment.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = ROOT / "src" / "python"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from z_band_prime_composite_field import divisor_counts_segment
from z_band_prime_predictor import W_d, gwr_next_gap_profile

DEFAULT_OUTPUT_DIR = ROOT / "output"
DEFAULT_START_PRIME = 11
DEFAULT_STEPS = 1000
DEFAULT_SCAN_BLOCK = 64


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description="Run the exact GWR witness walk in lockstep with the exact boundary walk.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for summary JSON and detail CSV artifacts.",
    )
    parser.add_argument(
        "--start-prime",
        type=int,
        default=DEFAULT_START_PRIME,
        help="Known prime anchor q for the first step.",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=DEFAULT_STEPS,
        help="Number of consecutive prime steps to check.",
    )
    parser.add_argument(
        "--scan-block",
        type=int,
        default=DEFAULT_SCAN_BLOCK,
        help="Exact divisor-field scan block size.",
    )
    return parser


def divisor_count_at(n: int) -> int:
    """Return the exact divisor count at one integer."""
    if n < 1:
        raise ValueError("n must be at least 1")
    return int(divisor_counts_segment(n, n + 1)[0])


def previous_prime(n: int) -> int:
    """Return the largest prime less than or equal to one integer."""
    if n < 2:
        raise ValueError("no primes less than or equal to 1")

    cursor = n
    while cursor >= 2:
        if divisor_count_at(cursor) == 2:
            return cursor
        cursor -= 1
    return 2


def scan_to_first_prime(start: int, block: int = DEFAULT_SCAN_BLOCK) -> int:
    """Return the first prime at or after one starting integer by divisor scan."""
    if start < 2:
        return 2
    if block < 1:
        raise ValueError("block must be positive")

    cursor = start
    while True:
        counts = divisor_counts_segment(cursor, cursor + block)
        for index, raw_d in enumerate(counts):
            if int(raw_d) == 2:
                return cursor + index
        cursor += block


def boundary_scan_next_prime(q: int, block: int = DEFAULT_SCAN_BLOCK) -> int:
    """Return the next prime after one known prime by exact divisor scan."""
    if q < 2:
        raise ValueError("q must be at least 2")
    if divisor_count_at(q) != 2:
        raise ValueError("q must be prime")
    return scan_to_first_prime(q + 1, block=block)


def witness_map_next_prime(q: int, block: int = DEFAULT_SCAN_BLOCK) -> tuple[int, dict[str, int | bool | None]]:
    """Recover the next prime from the winner profile plus the witness map."""
    if q < 2:
        raise ValueError("q must be at least 2")
    if divisor_count_at(q) != 2:
        raise ValueError("q must be prime")

    profile = gwr_next_gap_profile(q, block=block)
    winner_d = profile["winner_d"]
    winner_offset = profile["winner_offset"]
    winner_n = q + winner_offset if winner_offset is not None else None
    next_prime_boundary = int(profile["next_prime"])

    if winner_d is None:
        witness = None
        next_prime_via_witness = next_prime_boundary
        witness_matches_winner = True
    else:
        witness = int(W_d(q + 1, int(winner_d)))
        next_prime_via_witness = scan_to_first_prime(witness + 1, block=block)
        witness_matches_winner = witness == winner_n

    return next_prime_via_witness, {
        "q": q,
        "winner_d": winner_d,
        "winner_offset": winner_offset,
        "winner_n": winner_n,
        "witness": witness,
        "witness_matches_winner": witness_matches_winner,
        "gap_width": int(profile["gap_boundary_offset"]),
        "next_prime_boundary": next_prime_boundary,
        "next_prime_via_witness": next_prime_via_witness,
    }


def next_prime(n: int) -> int:
    """Return the smallest prime strictly greater than one integer."""
    if n < 2:
        return 2

    q = previous_prime(n)
    next_p, _profile = witness_map_next_prime(q)
    return next_p


def lockstep_compare(
    start_prime: int,
    steps: int,
    scan_block: int = DEFAULT_SCAN_BLOCK,
) -> tuple[list[dict[str, int | bool | None]], dict[str, object]]:
    """Run the exact boundary walk and witness walk in lockstep."""
    if steps < 0:
        raise ValueError("steps must be nonnegative")
    if divisor_count_at(start_prime) != 2:
        raise ValueError("start_prime must be prime")

    rows: list[dict[str, int | bool | None]] = []
    q = start_prime

    for step in range(1, steps + 1):
        path_a_next = boundary_scan_next_prime(q, block=scan_block)
        path_b_next, profile = witness_map_next_prime(q, block=scan_block)
        match = path_a_next == path_b_next

        row = {
            "step": step,
            "q": q,
            "path_a_next": path_a_next,
            "path_b_next": path_b_next,
            "winner_d": profile["winner_d"],
            "winner_offset": profile["winner_offset"],
            "winner_n": profile["winner_n"],
            "witness": profile["witness"],
            "witness_matches_winner": profile["witness_matches_winner"],
            "gap_width": profile["gap_width"],
            "match": match,
        }
        rows.append(row)
        if not match:
            break
        q = path_a_next

    divergence_count = sum(1 for row in rows if not bool(row["match"]))
    first_divergence = next((row for row in rows if not bool(row["match"])), None)
    summary = {
        "start_prime": start_prime,
        "steps_requested": steps,
        "steps_completed": len(rows),
        "matches": len(rows) - divergence_count,
        "divergences": divergence_count,
        "first_divergence": first_divergence,
        "all_witnesses_match_winner": all(bool(row["witness_matches_winner"]) for row in rows),
        "scan_block": scan_block,
    }
    return rows, summary


def write_artifacts(
    output_dir: Path,
    rows: list[dict[str, int | bool | None]],
    summary: dict[str, object],
) -> tuple[Path, Path]:
    """Write summary JSON and detail CSV artifacts."""
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = output_dir / "gwr_witness_walk_summary.json"
    detail_path = output_dir / "gwr_witness_walk_details.csv"

    with summary_path.open("w", encoding="utf-8", newline="") as handle:
        json.dump(summary, handle, indent=2)
        handle.write("\n")

    fieldnames = [
        "step",
        "q",
        "path_a_next",
        "path_b_next",
        "winner_d",
        "winner_offset",
        "winner_n",
        "witness",
        "witness_matches_winner",
        "gap_width",
        "match",
    ]
    with detail_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    return summary_path, detail_path


def main(argv: list[str] | None = None) -> int:
    """Run the lockstep witness walk and write artifacts."""
    parser = build_parser()
    args = parser.parse_args(argv)

    started = time.time()
    rows, summary = lockstep_compare(
        start_prime=args.start_prime,
        steps=args.steps,
        scan_block=args.scan_block,
    )
    summary["elapsed_seconds"] = time.time() - started
    summary_path, detail_path = write_artifacts(args.output_dir, rows, summary)

    print(f"steps requested: {summary['steps_requested']}")
    print(f"steps completed: {summary['steps_completed']}")
    print(f"matches:         {summary['matches']}")
    print(f"divergences:     {summary['divergences']}")
    if summary["first_divergence"] is None:
        print("surface consistent with the witness-map claim on all tested steps")
    else:
        print(f"first divergence: {summary['first_divergence']}")
    print(f"summary: {summary_path}")
    print(f"details: {detail_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
