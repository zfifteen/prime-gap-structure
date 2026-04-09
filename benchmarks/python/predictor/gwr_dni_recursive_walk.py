#!/usr/bin/env python3
"""Recursive gap walk driven by the DNI lex-min transition rule.

Two walker variants are provided:

  unbounded  (exact by construction, unconditional)
    Scans d(q+1), d(q+2), ... until the first offset k with d(q+k) = 2.
    Over the composite interior before that boundary, takes the lex-min
    (smallest divisor count, then smallest offset).  No cutoff assumption.
    This version is exact at any scale by definition.

  bounded  (dynamic log-squared cutoff, empirically calibrated through p<=10^6)
    Uses C(q) = max(64, ceil(0.5 * log(q)^2)) as the scan cutoff.
    This replaces the falsified fixed map {2:44, 4:60, 6:60}.
    The open question is whether A=0.5 is sufficient at all scales.

  compare  (falsification mode)
    Runs both walkers in lockstep from the same starting prime.  Records
    any step where the bounded walker diverges from the unbounded oracle.
    A single bounded_miss event falsifies the dynamic cutoff conjecture.

The walk advances step by step:

    1. From the current right prime q, compute (delta(q), omega(q)) via
       the selected rule.
    2. Recover the next prime:
         q+ = nextprime(W_delta(q)(q+1) - 1)
    3. Advance the walk state to the new gap and repeat.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
import time
from pathlib import Path

from sympy import nextprime, prime

ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = ROOT / "src" / "python"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from z_band_prime_composite_field import divisor_counts_segment
from z_band_prime_predictor import W_d

DEFAULT_OUTPUT_DIR = ROOT / "output"
DEFAULT_START_GAP_INDEX = 4
DEFAULT_STEPS = 100
# FALSIFIED: fixed cutoff map, retained for reference only.
# Use dynamic_cutoff(q) instead.
EXTENDED_CUTOFF_MAP = {2: 44, 4: 60, 6: 60}
PREFIX_LEN = 12
EXACT_SCAN_BLOCK = 64


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Recursive gap walk: unbounded exact oracle vs dynamic bounded cutoff.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for JSON and CSV artifacts.",
    )
    parser.add_argument(
        "--start-gap-index",
        type=int,
        default=DEFAULT_START_GAP_INDEX,
        help="Gap index k for the starting gap (p_k, p_{k+1}).",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=DEFAULT_STEPS,
        help="Number of recursive gap transitions to record.",
    )
    parser.add_argument(
        "--mode",
        choices=["bounded", "unbounded", "compare"],
        default="bounded",
        help=(
            "bounded: use the dynamic log-squared cutoff walker (default). "
            "unbounded: use the exact oracle walker with no cutoff assumption. "
            "compare: run both in lockstep and record any divergence."
        ),
    )
    return parser


def first_open_offset(residue: int) -> int:
    """Return the first even offset whose residue class is open mod 30."""
    for offset in (2, 4, 6, 8, 10, 12):
        candidate = (residue + offset) % 30
        if candidate % 3 != 0 and candidate % 5 != 0:
            return offset
    raise RuntimeError(f"no wheel-open offset found for residue {residue}")


def dynamic_cutoff(q: int) -> int:
    """Return the dynamic log-squared cutoff for prime q.

    This replaces the falsified fixed map {2:44, 4:60, 6:60}.
    The bound is C(q) = ceil(A * log(q)^2) with A=0.5 for conservative
    headroom above the empirically observed A~0.32 through p<=10^6.
    Minimum value is 64 to cover all observed violations at small scale.
    """
    return max(64, math.ceil(0.5 * math.log(q) ** 2))


def predict_next_gap_unbounded(current_right_prime: int) -> tuple[int, int]:
    """Exact oracle: scan until the first prime boundary, no cutoff.

    Reads d(q+1), d(q+2), ... until the first k where d(q+k) = 2.
    The lex-min (delta, omega) over composite offsets before that boundary
    is exact by construction at any scale.  No conjecture is involved.
    """
    rp = current_right_prime
    best_d: int | None = None
    best_offset: int | None = None
    offset = 0
    while True:
        lo = rp + 1 + offset
        hi = lo + EXACT_SCAN_BLOCK
        counts = divisor_counts_segment(lo, hi)
        for i, d in enumerate(counts):
            d = int(d)
            k = offset + i + 1
            if d <= 2:
                if best_d is None:
                    raise ValueError(
                        f"twin prime gap from {rp}: no composite interior"
                    )
                return best_d, best_offset
            if best_d is None or d < best_d or (d == best_d and k < best_offset):
                best_d = d
                best_offset = k
        offset += EXACT_SCAN_BLOCK


def predict_next_gap_bounded(current_right_prime: int) -> tuple[int, int]:
    """Bounded walker: use dynamic_cutoff(q).

    Empirically calibrated through p<=10^6.  Not yet proved universal.
    The open question: does the lex-min carrier always appear by offset C(q)?
    """
    rp = current_right_prime
    cutoff = dynamic_cutoff(rp)

    prefix_hi = rp + PREFIX_LEN + 1
    prefix_counts = divisor_counts_segment(rp + 1, prefix_hi)

    best_d: int | None = None
    best_offset: int | None = None
    all_composite = True

    for i in range(len(prefix_counts)):
        d = int(prefix_counts[i])
        offset = i + 1
        if d <= 2:
            all_composite = False
            break
        if best_d is None or d < best_d or (d == best_d and offset < best_offset):
            best_d = d
            best_offset = offset

    if not all_composite or best_d is None:
        if best_d is None:
            raise ValueError(
                f"empty next gap from prime {rp} (twin prime with no interior)"
            )
        return best_d, best_offset

    if best_d <= 3:
        return best_d, best_offset

    if cutoff > PREFIX_LEN:
        ext_lo = rp + PREFIX_LEN + 1
        ext_hi = rp + cutoff + 1
        extended_counts = divisor_counts_segment(ext_lo, ext_hi)
        for i in range(len(extended_counts)):
            d = int(extended_counts[i])
            offset = PREFIX_LEN + 1 + i
            if d == 2:
                break
            if d < best_d or (d == best_d and offset < best_offset):
                best_d = d
                best_offset = offset

    return best_d, best_offset


def predict_next_gap(current_right_prime: int) -> tuple[int, int]:
    """Backward-compatible alias for the bounded transition rule."""
    return predict_next_gap_bounded(current_right_prime)


def exact_next_gap_profile(
    current_right_prime: int,
    scan_block: int = EXACT_SCAN_BLOCK,
) -> dict[str, object]:
    """Return the exact next-gap lex-min profile by scanning to the prime boundary."""
    if scan_block < 1:
        raise ValueError("scan_block must be positive")

    next_start = current_right_prime + 1
    base_offset = 1
    best_d: int | None = None
    best_offset: int | None = None
    divisor_ladder: list[int] = []

    while True:
        counts = divisor_counts_segment(next_start, next_start + scan_block)
        for index in range(len(counts)):
            d = int(counts[index])
            offset = base_offset + index
            if d == 2:
                if best_d is None or best_offset is None:
                    raise ValueError(
                        f"empty next gap from prime {current_right_prime}"
                    )
                return {
                    "current_right_prime": current_right_prime,
                    "next_prime": current_right_prime + offset,
                    "gap_boundary_offset": offset,
                    "gap_width": offset,
                    "next_dmin": best_d,
                    "next_peak_offset": best_offset,
                    "divisor_ladder": divisor_ladder,
                }
            divisor_ladder.append(d)
            if best_d is None or d < best_d or (d == best_d and offset < best_offset):
                best_d = d
                best_offset = offset

        next_start += scan_block
        base_offset += scan_block


def predict_next_gap_exact(current_right_prime: int) -> tuple[int, int, int]:
    """Return the exact next-gap lex-min and the prime-boundary offset."""
    profile = exact_next_gap_profile(current_right_prime)
    return (
        int(profile["next_dmin"]),
        int(profile["next_peak_offset"]),
        int(profile["gap_boundary_offset"]),
    )


def compare_transition_rules(current_right_prime: int) -> dict[str, object]:
    """Compare the dynamic bounded cutoff rule against the exact next-gap oracle."""
    first_open = first_open_offset(current_right_prime % 30)
    cutoff = dynamic_cutoff(current_right_prime)
    bounded_dmin, bounded_peak_offset = predict_next_gap_bounded(current_right_prime)
    exact_profile = exact_next_gap_profile(current_right_prime)
    exact_peak_offset = int(exact_profile["next_peak_offset"])

    return {
        "current_right_prime": current_right_prime,
        "first_open_offset": first_open,
        "cutoff": cutoff,
        "bounded_next_dmin": bounded_dmin,
        "bounded_next_peak_offset": bounded_peak_offset,
        "exact_next_dmin": int(exact_profile["next_dmin"]),
        "exact_next_peak_offset": exact_peak_offset,
        "exact_gap_boundary_offset": int(exact_profile["gap_boundary_offset"]),
        "exact_next_prime": int(exact_profile["next_prime"]),
        "exact_gap_width": int(exact_profile["gap_width"]),
        "matches_cutoff_rule": (
            bounded_dmin == int(exact_profile["next_dmin"])
            and bounded_peak_offset == exact_peak_offset
        ),
        "cutoff_utilization": exact_peak_offset / cutoff,
        "overshoot_margin": max(0, exact_peak_offset - cutoff),
        "exact_divisor_ladder": list(exact_profile["divisor_ladder"]),
    }


def dni_recursive_step(
    current_gap_index: int,
    current_left_prime: int,
    current_right_prime: int,
    mode: str = "bounded",
) -> dict[str, object]:
    """Advance one step of the DNI-driven recursive gap walk."""
    if current_right_prime <= current_left_prime:
        raise ValueError("current_right_prime must exceed current_left_prime")

    rp = current_right_prime

    if mode == "unbounded":
        pred_d, pred_offset = predict_next_gap_unbounded(rp)
        bounded_d = bounded_offset = None
        bounded_miss = False
    elif mode == "bounded":
        pred_d, pred_offset = predict_next_gap_bounded(rp)
        bounded_d = bounded_offset = None
        bounded_miss = False
    else:  # compare
        unbounded_d, unbounded_offset = predict_next_gap_unbounded(rp)
        bounded_d, bounded_offset = predict_next_gap_bounded(rp)
        bounded_miss = (bounded_d != unbounded_d) or (bounded_offset != unbounded_offset)
        pred_d, pred_offset = unbounded_d, unbounded_offset

    witness = W_d(rp + 1, pred_d)
    predicted_next_prime = int(nextprime(witness - 1))
    exact_next_prime = int(nextprime(rp))
    exact_hit = predicted_next_prime == exact_next_prime

    skipped = 0
    if not exact_hit:
        cursor = rp
        while cursor < predicted_next_prime:
            cursor = int(nextprime(cursor))
            if cursor < predicted_next_prime:
                skipped += 1
            elif cursor == predicted_next_prime:
                break
            else:
                skipped = -1
                break

    record: dict[str, object] = {
        "current_gap_index": current_gap_index,
        "current_left_prime": current_left_prime,
        "current_right_prime": rp,
        "current_gap_width": rp - current_left_prime,
        "predicted_dmin": pred_d,
        "predicted_peak_offset": pred_offset,
        "witness": witness,
        "predicted_next_prime": predicted_next_prime,
        "exact_next_prime": exact_next_prime,
        "exact_hit": exact_hit,
        "skipped_gap_count": skipped,
    }

    if mode == "compare":
        record["bounded_dmin"] = bounded_d
        record["bounded_peak_offset"] = bounded_offset
        record["bounded_miss"] = bounded_miss

    return record


def run_walk(start_gap_index: int, steps: int, mode: str = "bounded") -> tuple[list[dict], dict]:
    """Run the full recursive walk and return rows plus summary."""
    if start_gap_index < 2:
        raise ValueError("start_gap_index must be at least 2")
    if steps < 1:
        raise ValueError("steps must be at least 1")

    left_prime = int(prime(start_gap_index))
    right_prime = int(prime(start_gap_index + 1))
    gap_index = start_gap_index

    rows: list[dict[str, object]] = []
    for step in range(steps):
        row = dni_recursive_step(gap_index, left_prime, right_prime, mode)
        row["step"] = step + 1
        rows.append(row)

        if row["exact_hit"]:
            left_prime = right_prime
            right_prime = int(row["predicted_next_prime"])
            gap_index += 1
        else:
            from sympy import prevprime
            left_prime = int(prevprime(row["predicted_next_prime"]))
            right_prime = int(row["predicted_next_prime"])
            gap_index += 1 + int(row["skipped_gap_count"])

    exact_hits = sum(1 for r in rows if r["exact_hit"])
    total_skipped = sum(int(r["skipped_gap_count"]) for r in rows)

    summary: dict[str, object] = {
        "mode": mode,
        "start_gap_index": start_gap_index,
        "steps": steps,
        "first_left_prime": int(rows[0]["current_left_prime"]),
        "first_right_prime": int(rows[0]["current_right_prime"]),
        "final_predicted_next_prime": int(rows[-1]["predicted_next_prime"]),
        "exact_hit_count": exact_hits,
        "exact_hit_rate": exact_hits / steps,
        "total_skipped_gaps": total_skipped,
        "mean_skipped_gaps": total_skipped / steps,
        "max_skipped_gaps": max(int(r["skipped_gap_count"]) for r in rows),
    }

    if mode == "compare":
        bounded_misses = sum(1 for r in rows if r.get("bounded_miss"))
        summary["bounded_miss_count"] = bounded_misses
        summary["bounded_conjecture_held"] = bounded_misses == 0

    return rows, summary


def main(argv: list[str] | None = None) -> int:
    """Run the DNI recursive walk and write artifacts."""
    args = build_parser().parse_args(argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    started = time.perf_counter()
    rows, summary = run_walk(args.start_gap_index, args.steps, args.mode)
    summary["runtime_seconds"] = time.perf_counter() - started

    summary_path = args.output_dir / "gwr_dni_recursive_walk_summary.json"
    detail_path = args.output_dir / "gwr_dni_recursive_walk_details.csv"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    base_fields = [
        "step",
        "current_gap_index",
        "current_left_prime",
        "current_right_prime",
        "current_gap_width",
        "predicted_dmin",
        "predicted_peak_offset",
        "witness",
        "predicted_next_prime",
        "exact_next_prime",
        "exact_hit",
        "skipped_gap_count",
    ]
    compare_fields = ["bounded_dmin", "bounded_peak_offset", "bounded_miss"]
    fieldnames = base_fields + (compare_fields if args.mode == "compare" else [])

    with detail_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fieldnames, lineterminator="\n", extrasaction="ignore"
        )
        writer.writeheader()
        writer.writerows(rows)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
