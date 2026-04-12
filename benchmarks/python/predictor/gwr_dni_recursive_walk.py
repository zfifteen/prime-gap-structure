#!/usr/bin/env python3
"""Recursive gap walk driven by the DNI lex-min transition rule.

Modes:

  unbounded
    Exact by construction. Scan divisor counts until the first prime boundary.

  bounded
    Use the dynamic log-squared cutoff C(q) = max(64, ceil(0.5 * log(q)^2)).
    Return the next-gap profile only if the prime boundary appears by that
    cutoff. Otherwise fail explicitly.

  compare
    Run bounded and unbounded in lockstep and record any divergence.

The walk advances by reading the next-gap profile and moving directly to the
prime boundary. When the 12-offset prefix locks at delta <= 3, the bounded
path recovers that boundary from the witness map instead of continuing the
extended divisor scan.
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

DEFAULT_OUTPUT_DIR = ROOT / "output"
DEFAULT_START_GAP_INDEX = 4
DEFAULT_STEPS = 100
PREFIX_LEN = 12
EXACT_SCAN_BLOCK = 64


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Recursive gap walk: direct-boundary bounded and unbounded modes.",
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
    """Return the dynamic log-squared cutoff for prime q."""
    return max(64, math.ceil(0.5 * math.log(q) ** 2))


def _scan_prefix_state(current_right_prime: int) -> tuple[int, int, int | None]:
    """Return the 12-offset lex-min state and any in-prefix prime boundary."""
    rp = current_right_prime
    best_d: int | None = None
    best_offset: int | None = None

    prefix_counts = divisor_counts_segment(rp + 1, rp + PREFIX_LEN + 1)
    for index, raw_d in enumerate(prefix_counts):
        d = int(raw_d)
        offset = index + 1
        if d == 2:
            if best_d is None or best_offset is None:
                raise ValueError(f"empty next gap from prime {rp}")
            return best_d, best_offset, offset
        if best_d is None or d < best_d or (d == best_d and offset < best_offset):
            best_d = d
            best_offset = offset

    if best_d is None or best_offset is None:
        raise ValueError(f"empty next gap from prime {rp}")

    return best_d, best_offset, None


def exact_next_gap_profile(
    current_right_prime: int,
    scan_block: int = EXACT_SCAN_BLOCK,
) -> dict[str, object]:
    """Return the exact next-gap lex-min profile by scanning to the prime boundary."""
    if scan_block < 1:
        raise ValueError("scan_block must be positive")

    rp = current_right_prime
    next_start = rp + 1
    base_offset = 1
    best_d: int | None = None
    best_offset: int | None = None
    divisor_ladder: list[int] = []

    while True:
        counts = divisor_counts_segment(next_start, next_start + scan_block)
        for index, raw_d in enumerate(counts):
            d = int(raw_d)
            offset = base_offset + index
            if d == 2:
                if best_d is None or best_offset is None:
                    raise ValueError(f"empty next gap from prime {rp}")
                return {
                    "current_right_prime": rp,
                    "next_prime": rp + offset,
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


def bounded_next_gap_profile(current_right_prime: int) -> dict[str, int]:
    """Return the bounded next-gap profile when the prime boundary lies by cutoff."""
    rp = current_right_prime
    cutoff = dynamic_cutoff(rp)
    best_d, best_offset, prefix_prime_offset = _scan_prefix_state(rp)

    if prefix_prime_offset is not None:
        return {
            "current_right_prime": rp,
            "next_prime": rp + prefix_prime_offset,
            "gap_boundary_offset": prefix_prime_offset,
            "next_dmin": best_d,
            "next_peak_offset": best_offset,
        }

    if best_d <= 3:
        next_prime_value = int(nextprime(rp + best_offset - 1))
        gap_boundary_offset = next_prime_value - rp
        if gap_boundary_offset > cutoff:
            raise RuntimeError(
                f"bounded cutoff missed the next prime boundary for {rp} by cutoff {cutoff}"
            )
        return {
            "current_right_prime": rp,
            "next_prime": next_prime_value,
            "gap_boundary_offset": gap_boundary_offset,
            "next_dmin": best_d,
            "next_peak_offset": best_offset,
        }

    ext_lo = rp + PREFIX_LEN + 1
    ext_hi = rp + cutoff + 1
    extended_counts = divisor_counts_segment(ext_lo, ext_hi)
    for index, raw_d in enumerate(extended_counts):
        d = int(raw_d)
        offset = PREFIX_LEN + 1 + index
        if d == 2:
            if best_d is None or best_offset is None:
                raise ValueError(f"empty next gap from prime {rp}")
            return {
                "current_right_prime": rp,
                "next_prime": rp + offset,
                "gap_boundary_offset": offset,
                "next_dmin": best_d,
                "next_peak_offset": best_offset,
            }
        if d < best_d or (d == best_d and offset < best_offset):
            best_d = d
            best_offset = offset

    raise RuntimeError(
        f"bounded cutoff missed the next prime boundary for {rp} by cutoff {cutoff}"
    )


def next_gap_profile(current_right_prime: int, mode: str) -> dict[str, int]:
    """Dispatch to the selected next-gap profile engine."""
    if mode == "bounded":
        return bounded_next_gap_profile(current_right_prime)
    if mode == "unbounded":
        exact = exact_next_gap_profile(current_right_prime)
        return {
            "current_right_prime": int(exact["current_right_prime"]),
            "next_prime": int(exact["next_prime"]),
            "gap_boundary_offset": int(exact["gap_boundary_offset"]),
            "next_dmin": int(exact["next_dmin"]),
            "next_peak_offset": int(exact["next_peak_offset"]),
        }
    raise ValueError(f"unsupported mode {mode}")


def predict_next_gap_unbounded(current_right_prime: int) -> tuple[int, int]:
    """Return the exact next-gap lex-min over the full composite interior."""
    profile = next_gap_profile(current_right_prime, "unbounded")
    return int(profile["next_dmin"]), int(profile["next_peak_offset"])


def predict_next_gap_bounded(current_right_prime: int) -> tuple[int, int]:
    """Return the bounded next-gap lex-min over offsets up to the cutoff."""
    rp = current_right_prime
    best_d, best_offset, prefix_prime_offset = _scan_prefix_state(rp)
    if prefix_prime_offset is not None or best_d <= 3:
        return best_d, best_offset

    cutoff = dynamic_cutoff(rp)
    counts = divisor_counts_segment(rp + PREFIX_LEN + 1, rp + cutoff + 1)
    for index, raw_d in enumerate(counts):
        d = int(raw_d)
        offset = PREFIX_LEN + 1 + index
        if d == 2:
            break
        if d < best_d or (d == best_d and offset < best_offset):
            best_d = d
            best_offset = offset

    return best_d, best_offset


def predict_next_gap(current_right_prime: int) -> tuple[int, int]:
    """Backward-compatible alias for the bounded transition rule."""
    return predict_next_gap_bounded(current_right_prime)


def predict_next_gap_exact(current_right_prime: int) -> tuple[int, int, int]:
    """Return the exact next-gap lex-min and the prime-boundary offset."""
    profile = exact_next_gap_profile(current_right_prime)
    return (
        int(profile["next_dmin"]),
        int(profile["next_peak_offset"]),
        int(profile["gap_boundary_offset"]),
    )


def compare_transition_rules(current_right_prime: int) -> dict[str, object]:
    """Compare the bounded cutoff rule against the exact next-gap oracle."""
    first_open = first_open_offset(current_right_prime % 30)
    cutoff = dynamic_cutoff(current_right_prime)
    bounded_dmin, bounded_peak_offset = predict_next_gap_bounded(current_right_prime)
    exact = exact_next_gap_profile(current_right_prime)
    exact_peak_offset = int(exact["next_peak_offset"])
    exact_boundary_offset = int(exact["gap_boundary_offset"])
    try:
        bounded_profile = bounded_next_gap_profile(current_right_prime)
        bounded_gap_boundary_offset: int | None = int(
            bounded_profile["gap_boundary_offset"]
        )
        bounded_next_prime: int | None = int(bounded_profile["next_prime"])
    except RuntimeError:
        bounded_gap_boundary_offset = None
        bounded_next_prime = None

    return {
        "current_right_prime": current_right_prime,
        "first_open_offset": first_open,
        "cutoff": cutoff,
        "bounded_next_dmin": bounded_dmin,
        "bounded_next_peak_offset": bounded_peak_offset,
        "bounded_gap_boundary_offset": bounded_gap_boundary_offset,
        "bounded_next_prime": bounded_next_prime,
        "exact_next_dmin": int(exact["next_dmin"]),
        "exact_next_peak_offset": exact_peak_offset,
        "exact_gap_boundary_offset": exact_boundary_offset,
        "exact_next_prime": int(exact["next_prime"]),
        "exact_gap_width": int(exact["gap_width"]),
        "matches_cutoff_rule": (
            bounded_dmin == int(exact["next_dmin"])
            and bounded_peak_offset == exact_peak_offset
        ),
        "cutoff_utilization": exact_peak_offset / cutoff,
        "boundary_utilization": exact_boundary_offset / cutoff,
        "overshoot_margin": max(0, exact_peak_offset - cutoff),
        "exact_divisor_ladder": list(exact["divisor_ladder"]),
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

    if mode == "compare":
        bounded = bounded_next_gap_profile(rp)
        exact = next_gap_profile(rp, "unbounded")
        bounded_miss = (
            int(bounded["next_prime"]) != int(exact["next_prime"])
            or int(bounded["next_dmin"]) != int(exact["next_dmin"])
            or int(bounded["next_peak_offset"]) != int(exact["next_peak_offset"])
            or int(bounded["gap_boundary_offset"]) != int(exact["gap_boundary_offset"])
        )
        profile = exact
    else:
        profile = next_gap_profile(rp, mode)
        bounded = None
        bounded_miss = False

    predicted_next_prime = int(profile["next_prime"])
    exact_next_prime = predicted_next_prime if mode == "unbounded" else int(
        next_gap_profile(rp, "unbounded")["next_prime"]
    )

    record: dict[str, object] = {
        "current_gap_index": current_gap_index,
        "current_left_prime": current_left_prime,
        "current_right_prime": rp,
        "current_gap_width": rp - current_left_prime,
        "predicted_dmin": int(profile["next_dmin"]),
        "predicted_peak_offset": int(profile["next_peak_offset"]),
        "predicted_gap_boundary_offset": int(profile["gap_boundary_offset"]),
        "predicted_next_prime": predicted_next_prime,
        "exact_next_prime": exact_next_prime,
        "exact_hit": predicted_next_prime == exact_next_prime,
        "skipped_gap_count": 0 if predicted_next_prime == exact_next_prime else -1,
    }

    if mode == "compare":
        assert bounded is not None
        record["bounded_dmin"] = int(bounded["next_dmin"])
        record["bounded_peak_offset"] = int(bounded["next_peak_offset"])
        record["bounded_gap_boundary_offset"] = int(bounded["gap_boundary_offset"])
        record["bounded_next_prime"] = int(bounded["next_prime"])
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

        left_prime = right_prime
        right_prime = int(row["predicted_next_prime"])
        gap_index += 1

    exact_hits = sum(1 for r in rows if r["exact_hit"])
    summary: dict[str, object] = {
        "mode": mode,
        "start_gap_index": start_gap_index,
        "steps": steps,
        "first_left_prime": int(rows[0]["current_left_prime"]),
        "first_right_prime": int(rows[0]["current_right_prime"]),
        "final_predicted_next_prime": int(rows[-1]["predicted_next_prime"]),
        "exact_hit_count": exact_hits,
        "exact_hit_rate": exact_hits / steps,
        "total_skipped_gaps": 0,
        "mean_skipped_gaps": 0.0,
        "max_skipped_gaps": 0,
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
        "predicted_gap_boundary_offset",
        "predicted_next_prime",
        "exact_next_prime",
        "exact_hit",
        "skipped_gap_count",
    ]
    compare_fields = [
        "bounded_dmin",
        "bounded_peak_offset",
        "bounded_gap_boundary_offset",
        "bounded_next_prime",
        "bounded_miss",
    ]
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
