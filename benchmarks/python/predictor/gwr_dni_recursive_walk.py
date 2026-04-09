#!/usr/bin/env python3
"""Recursive gap walk driven by the extended DNI lex-min transition rule.

The walk starts from one known prime gap and advances step by step:

    1. From the current right prime, compute divisor counts at offsets
       1..cutoff (12 prefix + bounded extension stopping at the first
       prime).  The piecewise cutoff bounds by first_open_offset are
       {2: 44, 4: 60, 6: 60}.

    2. Take the lexicographic minimum (smallest divisor count, then
       smallest offset) over composites in that window.  This gives
       (next_dmin, next_peak_offset).

    3. Use W_d(current_right_prime, next_dmin) to recover the immediate
       next prime.

    4. Advance the walk state to the new gap and repeat.
"""

from __future__ import annotations

import argparse
import csv
import json
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
EXTENDED_CUTOFF_MAP = {2: 44, 4: 60, 6: 60}
PREFIX_LEN = 12


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description="Recursive gap walk using the extended DNI lex-min transition rule.",
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
    return parser


def first_open_offset(residue: int) -> int:
    """Return the first even offset whose class is open mod 30."""
    for offset in (2, 4, 6, 8, 10, 12):
        candidate = (residue + offset) % 30
        if candidate % 3 != 0 and candidate % 5 != 0:
            return offset
    raise RuntimeError(f"no wheel-open offset found for residue {residue}")


def predict_next_gap(current_right_prime: int) -> tuple[int, int]:
    """Predict (next_dmin, next_peak_offset) using the extended DNI lex-min rule.

    Returns the predicted divisor class and its first-carrier offset from
    current_right_prime.

    The rule:
      Stage 1 -- scan offsets 1..12 from current_right_prime, collecting
        divisor counts.  Track the lex-min (smallest d, then smallest offset).
        If any offset value is a prime (d=2) or missing, the gap is narrow
        and the scan covers the full interior; return immediately.
      Stage 2 -- if all 12 offsets are composite (d >= 3) and the prefix
        minimum exceeds 3, extend the scan through offsets 13..cutoff,
        stopping at the first prime (d=2, marking the gap boundary).
    """
    rp = current_right_prime
    foo = first_open_offset(rp % 30)
    cutoff = EXTENDED_CUTOFF_MAP.get(foo, 60)

    # Stage 1: offsets 1..12
    prefix_hi = rp + PREFIX_LEN + 1
    prefix_counts = divisor_counts_segment(rp + 1, prefix_hi)

    best_d: int | None = None
    best_offset: int | None = None
    all_composite = True

    for i in range(len(prefix_counts)):
        d = int(prefix_counts[i])
        offset = i + 1
        if d <= 2:
            # Hit a prime (or 1); gap boundary within the prefix window.
            # The gap interior is only offsets before this point.
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

    # Stage 2: extend through offsets 13..cutoff, stopping at gap boundary
    if cutoff > PREFIX_LEN:
        ext_lo = rp + PREFIX_LEN + 1
        ext_hi = rp + cutoff + 1
        extended_counts = divisor_counts_segment(ext_lo, ext_hi)
        for i in range(len(extended_counts)):
            d = int(extended_counts[i])
            offset = PREFIX_LEN + 1 + i
            if d == 2:  # prime = gap boundary
                break
            if d < best_d or (d == best_d and offset < best_offset):
                best_d = d
                best_offset = offset

    return best_d, best_offset


def dni_recursive_step(
    current_gap_index: int,
    current_left_prime: int,
    current_right_prime: int,
) -> dict[str, object]:
    """Advance one step of the DNI-driven recursive gap walk.

    Returns a record with the predicted next prime, exact verification,
    and skip count.
    """
    if current_right_prime <= current_left_prime:
        raise ValueError("current_right_prime must exceed current_left_prime")

    predicted_dmin, predicted_peak_offset = predict_next_gap(current_right_prime)

    # Recover the next prime via W_d witness
    witness = W_d(current_right_prime + 1, predicted_dmin)
    predicted_next_prime = int(nextprime(witness - 1))

    # Exact ground truth
    exact_next_prime = int(nextprime(current_right_prime))
    exact_hit = predicted_next_prime == exact_next_prime

    # Count skipped gaps
    skipped = 0
    if not exact_hit:
        cursor = current_right_prime
        while cursor < predicted_next_prime:
            cursor = int(nextprime(cursor))
            if cursor < predicted_next_prime:
                skipped += 1
            elif cursor == predicted_next_prime:
                break
            else:
                skipped = -1  # overshoot
                break

    return {
        "current_gap_index": current_gap_index,
        "current_left_prime": current_left_prime,
        "current_right_prime": current_right_prime,
        "current_gap_width": current_right_prime - current_left_prime,
        "predicted_dmin": predicted_dmin,
        "predicted_peak_offset": predicted_peak_offset,
        "witness": witness,
        "predicted_next_prime": predicted_next_prime,
        "exact_next_prime": exact_next_prime,
        "exact_hit": exact_hit,
        "skipped_gap_count": skipped,
    }


def run_walk(start_gap_index: int, steps: int) -> tuple[list[dict], dict]:
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
        row = dni_recursive_step(gap_index, left_prime, right_prime)
        row["step"] = step + 1
        rows.append(row)

        # Advance along the PREDICTED chain (use predicted next prime)
        left_prime = int(nextprime(row["predicted_next_prime"] - 1) - 1)
        # Actually, for a true recursive walk, the next gap starts at
        # (prevprime(predicted_next_prime), predicted_next_prime).
        # But if the prediction is exact, this is just
        # (current_right_prime, predicted_next_prime).
        if row["exact_hit"]:
            left_prime = right_prime
            right_prime = int(row["predicted_next_prime"])
            gap_index += 1
        else:
            # Walk to the predicted prime's gap
            from sympy import prevprime
            left_prime = int(prevprime(row["predicted_next_prime"]))
            right_prime = int(row["predicted_next_prime"])
            gap_index += 1 + int(row["skipped_gap_count"])

    exact_hits = sum(1 for r in rows if r["exact_hit"])
    total_skipped = sum(int(r["skipped_gap_count"]) for r in rows)
    summary = {
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
    return rows, summary


def main(argv: list[str] | None = None) -> int:
    """Run the DNI recursive walk and write artifacts."""
    args = build_parser().parse_args(argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    started = time.perf_counter()
    rows, summary = run_walk(args.start_gap_index, args.steps)
    summary["runtime_seconds"] = time.perf_counter() - started

    summary_path = args.output_dir / "gwr_dni_recursive_walk_summary.json"
    detail_path = args.output_dir / "gwr_dni_recursive_walk_details.csv"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    fieldnames = [
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
    with detail_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
