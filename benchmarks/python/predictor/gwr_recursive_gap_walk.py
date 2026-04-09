#!/usr/bin/env python3
"""Flesh out the recursive GWR gap->prime->gap->prime algorithm on an exact surface."""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path

from sympy import nextprime, prevprime, prime


ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = ROOT / "src" / "python"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from z_band_prime_predictor import W_d, d4_gap_profile, divisor_gap_profile, gap_dmin

DEFAULT_OUTPUT_DIR = ROOT / "output"
DEFAULT_START_GAP_INDEX = 10
DEFAULT_STEPS = 50


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description="Walk exact prime gaps recursively and record the next-gap corridor.",
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


def gap_state(left_prime: int, right_prime: int) -> dict[str, object]:
    """Return one exact prime-gap state."""
    if right_prime <= left_prime:
        raise ValueError("right_prime must be larger than left_prime")

    d4_profile = d4_gap_profile(left_prime, right_prime)
    last_pre_gap_d4 = d4_profile["last_pre_gap_d4"]
    last_in_gap_d4 = d4_profile["last_in_gap_d4"]
    d4_corridor_start = (
        int(last_pre_gap_d4) + 1 if last_pre_gap_d4 is not None and last_in_gap_d4 is not None else None
    )
    d4_corridor_end = int(last_in_gap_d4) if last_in_gap_d4 is not None else None
    d4_corridor_width = (
        int(last_in_gap_d4) - int(last_pre_gap_d4)
        if last_pre_gap_d4 is not None and last_in_gap_d4 is not None
        else None
    )

    return {
        "left_prime": left_prime,
        "right_prime": right_prime,
        "gap_width": right_prime - left_prime,
        "interior_count": right_prime - left_prime - 1,
        "dmin": gap_dmin(left_prime, right_prime),
        "gap_has_d4": bool(d4_profile["gap_has_d4"]),
        "last_pre_gap_d4": last_pre_gap_d4,
        "first_in_gap_d4": d4_profile["first_in_gap_d4"],
        "last_in_gap_d4": last_in_gap_d4,
        "d4_corridor_start": d4_corridor_start,
        "d4_corridor_end": d4_corridor_end,
        "d4_corridor_width": d4_corridor_width,
    }


def divisor_corridor(left_prime: int, right_prime: int, divisor_target: int) -> dict[str, int | bool | None]:
    """Return the exact corridor for one requested divisor class on one prime gap."""
    if divisor_target < 3:
        raise ValueError("divisor_target must be at least 3")
    if right_prime <= left_prime:
        raise ValueError("right_prime must be larger than left_prime")
    return divisor_gap_profile(left_prime, right_prime, divisor_target)


def recover_prime_from_exact_gap(left_prime: int, right_prime: int) -> dict[str, object]:
    """
    Recover one gap's right endpoint prime from exact local gap structure.

    For nonempty gaps, the script uses the leftmost exact corridor seed for the
    gap-local minimum divisor class and then applies the witness recovery step.
    For twin gaps, the right endpoint is already the next prime.
    """
    if right_prime <= left_prime:
        raise ValueError("right_prime must be larger than left_prime")

    divisor_target = gap_dmin(left_prime, right_prime)
    if divisor_target is None:
        return {
            "recovery_mode": "empty_gap_endpoint",
            "recovered_prime": right_prime,
            "recovery_divisor_target": None,
            "recovery_seed": None,
            "recovery_witness": None,
            "recovery_corridor_start": None,
            "recovery_corridor_end": None,
            "recovery_corridor_width": None,
            "recovery_exact": True,
        }

    corridor = divisor_corridor(left_prime, right_prime, divisor_target)
    recovery_seed = corridor["corridor_start"]
    if recovery_seed is None:
        raise AssertionError(
            f"missing divisor corridor for ({left_prime}, {right_prime}) with d={divisor_target}"
        )
    recovery_witness = W_d(int(recovery_seed), int(divisor_target), stop_exclusive=right_prime)
    recovered_prime = int(nextprime(recovery_witness - 1))
    if recovered_prime != right_prime:
        raise AssertionError(
            f"prime recovery failed for ({left_prime}, {right_prime}): "
            f"d={divisor_target}, seed={recovery_seed}, witness={recovery_witness}, "
            f"recovered={recovered_prime}"
        )

    return {
        "recovery_mode": "witness",
        "recovered_prime": recovered_prime,
        "recovery_divisor_target": int(divisor_target),
        "recovery_seed": int(recovery_seed),
        "recovery_witness": int(recovery_witness),
        "recovery_corridor_start": corridor["corridor_start"],
        "recovery_corridor_end": corridor["corridor_end"],
        "recovery_corridor_width": corridor["corridor_width"],
        "recovery_exact": True,
    }


def forward_localize_next_prime_from_current_gap(
    current_gap_index: int,
    current_left_prime: int,
    current_right_prime: int,
) -> dict[str, object]:
    """
    Predict the next prime from one current exact gap by a forward GWR witness.

    The current production localizer uses the dominant d=4 witness started at
    the current gap's right endpoint. This is a genuine forward rule: it does
    not call nextprime on the current right prime to localize the next gap.
    """
    if current_gap_index < 1:
        raise ValueError("current_gap_index must be at least 1")
    if current_right_prime <= current_left_prime:
        raise ValueError("current_right_prime must be larger than current_left_prime")

    localizer_seed = current_right_prime
    localizer_divisor_target = 4
    localizer_witness = W_d(localizer_seed, localizer_divisor_target)
    predicted_next_prime = int(nextprime(localizer_witness - 1))
    predicted_next_left_prime = int(prevprime(predicted_next_prime))
    exact_immediate_next_right_prime = int(nextprime(current_right_prime))
    exact_immediate_hit = predicted_next_left_prime == current_right_prime
    skipped_gap_count = 0
    left_cursor = current_right_prime
    while left_cursor < predicted_next_left_prime:
        left_cursor = int(nextprime(left_cursor))
        skipped_gap_count += 1
    if left_cursor != predicted_next_left_prime:
        raise AssertionError(
            f"predicted next left prime mismatch: cursor={left_cursor}, predicted={predicted_next_left_prime}"
        )
    predicted_next_gap_index = current_gap_index + skipped_gap_count + 1

    return {
        "localizer_seed": localizer_seed,
        "localizer_divisor_target": localizer_divisor_target,
        "localizer_witness": localizer_witness,
        "predicted_next_left_prime": predicted_next_left_prime,
        "predicted_next_prime": predicted_next_prime,
        "predicted_next_gap_index": predicted_next_gap_index,
        "exact_immediate_next_right_prime": exact_immediate_next_right_prime,
        "exact_immediate_hit": exact_immediate_hit,
        "skipped_gap_count": skipped_gap_count,
    }


def gwr_recursive_gap_step(
    current_gap_index: int,
    current_left_prime: int,
    current_right_prime: int,
) -> dict[str, object]:
    """
    Advance one forward-localized GWR gap->prime->gap step.

    The current gap provides the state. A forward d=4 witness predicts the next
    prime. That predicted prime defines the next gap used for the following
    step. The exact immediate next prime is also recorded so the run can be
    evaluated against the true adjacent-gap surface.
    """
    if current_gap_index < 1:
        raise ValueError("current_gap_index must be at least 1")
    if current_right_prime <= current_left_prime:
        raise ValueError("current_right_prime must be larger than current_left_prime")

    current_state = gap_state(current_left_prime, current_right_prime)
    localization = forward_localize_next_prime_from_current_gap(
        current_gap_index,
        current_left_prime,
        current_right_prime,
    )
    next_left_prime = int(localization["predicted_next_left_prime"])
    next_right_prime = int(localization["predicted_next_prime"])
    next_state = gap_state(next_left_prime, next_right_prime)
    prime_recovery = recover_prime_from_exact_gap(next_left_prime, next_right_prime)

    next_d4_corridor_start = next_state["d4_corridor_start"]
    next_d4_corridor_end = next_state["d4_corridor_end"]

    return {
        "current_gap_index": current_gap_index,
        "next_gap_index": int(localization["predicted_next_gap_index"]),
        "current_left_prime": current_state["left_prime"],
        "current_right_prime": current_state["right_prime"],
        "current_gap_width": current_state["gap_width"],
        "current_dmin": current_state["dmin"],
        "current_gap_has_d4": current_state["gap_has_d4"],
        "current_last_pre_gap_d4": current_state["last_pre_gap_d4"],
        "current_first_in_gap_d4": current_state["first_in_gap_d4"],
        "current_last_in_gap_d4": current_state["last_in_gap_d4"],
        "next_left_prime": next_state["left_prime"],
        "next_right_prime": next_state["right_prime"],
        "next_gap_width": next_state["gap_width"],
        "next_dmin": next_state["dmin"],
        "next_gap_has_d4": next_state["gap_has_d4"],
        "next_last_pre_gap_d4": next_state["last_pre_gap_d4"],
        "next_first_in_gap_d4": next_state["first_in_gap_d4"],
        "next_last_in_gap_d4": next_state["last_in_gap_d4"],
        "next_d4_corridor_start": next_d4_corridor_start,
        "next_d4_corridor_end": next_d4_corridor_end,
        "next_d4_corridor_width": next_state["d4_corridor_width"],
        "localizer_seed": int(localization["localizer_seed"]),
        "localizer_divisor_target": int(localization["localizer_divisor_target"]),
        "localizer_witness": int(localization["localizer_witness"]),
        "exact_immediate_next_right_prime": int(localization["exact_immediate_next_right_prime"]),
        "exact_immediate_hit": bool(localization["exact_immediate_hit"]),
        "skipped_gap_count": int(localization["skipped_gap_count"]),
        "recovery_mode": prime_recovery["recovery_mode"],
        "recovered_next_prime": prime_recovery["recovered_prime"],
        "recovery_divisor_target": prime_recovery["recovery_divisor_target"],
        "recovery_seed": prime_recovery["recovery_seed"],
        "recovery_witness": prime_recovery["recovery_witness"],
        "recovery_corridor_start": prime_recovery["recovery_corridor_start"],
        "recovery_corridor_end": prime_recovery["recovery_corridor_end"],
        "recovery_corridor_width": prime_recovery["recovery_corridor_width"],
        "recovery_exact": prime_recovery["recovery_exact"],
        "next_gap_right_offset_from_current_right": next_right_prime - current_right_prime,
        "next_d4_corridor_start_offset_from_current_right": (
            int(next_d4_corridor_start) - current_right_prime
            if next_d4_corridor_start is not None
            else None
        ),
        "next_d4_corridor_end_offset_from_current_right": (
            int(next_d4_corridor_end) - current_right_prime
            if next_d4_corridor_end is not None
            else None
        ),
    }


def run_recursive_walk_from_gap(
    start_gap_index: int,
    start_left_prime: int,
    start_right_prime: int,
    steps: int,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    """Run one exact recursive gap walk from one known starting gap."""
    if start_gap_index < 1:
        raise ValueError("start_gap_index must be at least 1")
    if start_right_prime <= start_left_prime:
        raise ValueError("start_right_prime must be larger than start_left_prime")
    if steps < 1:
        raise ValueError("steps must be at least 1")

    current_left_prime = int(start_left_prime)
    current_right_prime = int(start_right_prime)
    rows: list[dict[str, object]] = []
    gap_index = start_gap_index

    for step in range(steps):
        row = gwr_recursive_gap_step(
            current_gap_index=gap_index,
            current_left_prime=current_left_prime,
            current_right_prime=current_right_prime,
        )
        row["step"] = step + 1
        rows.append(row)
        current_left_prime = int(row["next_left_prime"])
        current_right_prime = int(row["next_right_prime"])
        gap_index = int(row["next_gap_index"])

    return rows, summarize_rows(rows)


def run_recursive_walk(start_gap_index: int, steps: int) -> tuple[list[dict[str, object]], dict[str, object]]:
    """Run one exact recursive gap walk and return detail rows plus summary."""
    if start_gap_index < 1:
        raise ValueError("start_gap_index must be at least 1")
    if steps < 1:
        raise ValueError("steps must be at least 1")

    start_left_prime = int(prime(start_gap_index))
    start_right_prime = int(prime(start_gap_index + 1))
    return run_recursive_walk_from_gap(
        start_gap_index=start_gap_index,
        start_left_prime=start_left_prime,
        start_right_prime=start_right_prime,
        steps=steps,
    )


def summarize_rows(rows: list[dict[str, object]]) -> dict[str, object]:
    """Aggregate one recursive gap walk."""
    if not rows:
        raise ValueError("rows must not be empty")

    next_gap_has_d4_count = sum(int(row["next_gap_has_d4"]) for row in rows)
    next_gap_width_sum = sum(int(row["next_gap_width"]) for row in rows)
    recovery_exact_count = sum(int(row["recovery_exact"]) for row in rows)
    witness_recovery_count = sum(int(row["recovery_mode"] == "witness") for row in rows)
    empty_gap_endpoint_count = sum(
        int(row["recovery_mode"] == "empty_gap_endpoint") for row in rows
    )
    exact_immediate_hit_count = sum(int(row["exact_immediate_hit"]) for row in rows)
    skipped_gap_count_sum = sum(int(row["skipped_gap_count"]) for row in rows)
    corridor_start_offsets = [
        int(row["next_d4_corridor_start_offset_from_current_right"])
        for row in rows
        if row["next_d4_corridor_start_offset_from_current_right"] is not None
    ]
    corridor_end_offsets = [
        int(row["next_d4_corridor_end_offset_from_current_right"])
        for row in rows
        if row["next_d4_corridor_end_offset_from_current_right"] is not None
    ]
    corridor_widths = [
        int(row["next_d4_corridor_width"])
        for row in rows
        if row["next_d4_corridor_width"] is not None
    ]
    self_feeding_transition_count = sum(
        int(left_row["next_left_prime"] == right_row["current_left_prime"])
        and int(left_row["next_right_prime"] == right_row["current_right_prime"])
        for left_row, right_row in zip(rows, rows[1:])
    )

    return {
        "start_gap_index": int(rows[0]["current_gap_index"]),
        "steps": len(rows),
        "first_current_left_prime": int(rows[0]["current_left_prime"]),
        "first_current_right_prime": int(rows[0]["current_right_prime"]),
        "final_next_right_prime": int(rows[-1]["next_right_prime"]),
        "self_feeding_transition_count": self_feeding_transition_count,
        "predicted_chain_is_self_feeding": self_feeding_transition_count == len(rows) - 1,
        "next_gap_has_d4_count": next_gap_has_d4_count,
        "next_gap_has_d4_rate": next_gap_has_d4_count / len(rows),
        "exact_immediate_hit_count": exact_immediate_hit_count,
        "exact_immediate_hit_rate": exact_immediate_hit_count / len(rows),
        "mean_skipped_gap_count": skipped_gap_count_sum / len(rows),
        "max_skipped_gap_count": max(int(row["skipped_gap_count"]) for row in rows),
        "recovery_exact_count": recovery_exact_count,
        "recovery_exact_rate": recovery_exact_count / len(rows),
        "witness_recovery_count": witness_recovery_count,
        "empty_gap_endpoint_count": empty_gap_endpoint_count,
        "mean_next_gap_width": next_gap_width_sum / len(rows),
        "mean_next_d4_corridor_start_offset": (
            sum(corridor_start_offsets) / len(corridor_start_offsets)
            if corridor_start_offsets
            else None
        ),
        "mean_next_d4_corridor_end_offset": (
            sum(corridor_end_offsets) / len(corridor_end_offsets)
            if corridor_end_offsets
            else None
        ),
        "mean_next_d4_corridor_width": (
            sum(corridor_widths) / len(corridor_widths) if corridor_widths else None
        ),
    }


def main(argv: list[str] | None = None) -> int:
    """Run the recursive walk and write JSON plus CSV artifacts."""
    args = build_parser().parse_args(argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    started = time.perf_counter()
    rows, summary = run_recursive_walk(args.start_gap_index, args.steps)
    summary["runtime_seconds"] = time.perf_counter() - started

    summary_path = args.output_dir / "gwr_recursive_gap_walk_summary.json"
    detail_path = args.output_dir / "gwr_recursive_gap_walk_details.csv"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    fieldnames = [
        "step",
        "current_gap_index",
        "next_gap_index",
        "current_left_prime",
        "current_right_prime",
        "current_gap_width",
        "current_dmin",
        "current_gap_has_d4",
        "current_last_pre_gap_d4",
        "current_first_in_gap_d4",
        "current_last_in_gap_d4",
        "next_left_prime",
        "next_right_prime",
        "next_gap_width",
        "next_dmin",
        "next_gap_has_d4",
        "next_last_pre_gap_d4",
        "next_first_in_gap_d4",
        "next_last_in_gap_d4",
        "next_d4_corridor_start",
        "next_d4_corridor_end",
        "next_d4_corridor_width",
        "localizer_seed",
        "localizer_divisor_target",
        "localizer_witness",
        "exact_immediate_next_right_prime",
        "exact_immediate_hit",
        "skipped_gap_count",
        "recovery_mode",
        "recovered_next_prime",
        "recovery_divisor_target",
        "recovery_seed",
        "recovery_witness",
        "recovery_corridor_start",
        "recovery_corridor_end",
        "recovery_corridor_width",
        "recovery_exact",
        "next_gap_right_offset_from_current_right",
        "next_d4_corridor_start_offset_from_current_right",
        "next_d4_corridor_end_offset_from_current_right",
    ]
    with detail_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
