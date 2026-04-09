#!/usr/bin/env python3
"""Run the exact forward GWR decade-scaling sweep from one self-contained script."""

from __future__ import annotations

import argparse
import csv
import json
import math
import time
from functools import lru_cache
from pathlib import Path

import gmpy2
import numpy as np
from sympy import nextprime, prevprime


SEGMENT_SIZE = 1_000_000
DIVISOR_WINDOW_SPAN = 65_536
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parents[3] / "output"
DEFAULT_MAX_POWER = 10
SUMMARY_FILENAME = "gwr_recursive_gap_scaling_sweep_summary.json"
DETAIL_FILENAME = "gwr_recursive_gap_scaling_sweep_details.csv"


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description="Sweep forward recursive GWR scaling across prime decades from one file.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for JSON and CSV artifacts.",
    )
    parser.add_argument(
        "--max-power",
        type=int,
        default=DEFAULT_MAX_POWER,
        help="Largest power m in the decade start 10^m.",
    )
    return parser


def _small_primes(limit: int) -> np.ndarray:
    """Return every prime up to one small sieve limit."""
    sieve = np.ones(limit + 1, dtype=bool)
    sieve[:2] = False
    root = int(limit ** 0.5)
    for prime in range(2, root + 1):
        if sieve[prime]:
            sieve[prime * prime : limit + 1 : prime] = False
    return np.flatnonzero(sieve)


def _segmented_primes(limit: int, segment_size: int = SEGMENT_SIZE):
    """Yield primes up to one limit without materializing the full sieve."""
    if limit < 2:
        return

    base_limit = int(math.isqrt(limit))
    base_primes = _small_primes(base_limit)

    for segment_lo in range(2, limit + 1, segment_size):
        segment_hi = min(segment_lo + segment_size - 1, limit)
        sieve = np.ones(segment_hi - segment_lo + 1, dtype=bool)
        for prime in base_primes:
            prime_int = int(prime)
            prime_square = prime_int * prime_int
            if prime_square > segment_hi:
                break
            start = max(prime_square, ((segment_lo + prime_int - 1) // prime_int) * prime_int)
            sieve[start - segment_lo : segment_hi - segment_lo + 1 : prime_int] = False

        for offset in np.flatnonzero(sieve):
            yield segment_lo + int(offset)


def divisor_counts_segment(lo: int, hi: int) -> np.ndarray:
    """Compute exact divisor counts on one contiguous natural-number interval."""
    if lo < 1:
        raise ValueError("lo must be at least 1")
    if hi <= lo:
        raise ValueError("hi must be larger than lo")

    size = hi - lo
    values = np.arange(lo, hi, dtype=np.int64)
    residual = values.copy()
    divisor_count = np.ones(size, dtype=np.uint32)
    cube_root_limit, exact = gmpy2.iroot(hi - 1, 3)
    cube_root_limit = int(cube_root_limit)
    if not exact and (cube_root_limit + 1) ** 3 <= hi - 1:
        cube_root_limit += 1

    for prime in _segmented_primes(cube_root_limit):
        start = ((lo + prime - 1) // prime) * prime
        indices = np.arange(start - lo, size, prime, dtype=np.int64)
        if indices.size == 0:
            continue

        subvalues = residual[indices].copy()
        exponent = np.zeros(indices.size, dtype=np.uint8)
        while True:
            mask = (subvalues % prime) == 0
            if not mask.any():
                break
            subvalues[mask] //= prime
            exponent[mask] += 1

        residual[indices] = subvalues
        nonzero = exponent != 0
        if nonzero.any():
            divisor_count[indices[nonzero]] *= (exponent[nonzero] + 1).astype(np.uint32)

    for index, remainder in enumerate(residual):
        if remainder == 1:
            continue

        remainder_mpz = gmpy2.mpz(int(remainder))
        if gmpy2.is_prime(remainder_mpz):
            divisor_count[index] *= 2
            continue

        if gmpy2.is_square(remainder_mpz):
            root = gmpy2.isqrt(remainder_mpz)
            if gmpy2.is_prime(root):
                divisor_count[index] *= 3
                continue

        divisor_count[index] *= 4

    if lo <= 1 < hi:
        divisor_count[1 - lo] = 1
    return divisor_count


def _window_start_for(lo: int) -> int:
    """Return the inclusive aligned window start for one interval."""
    if lo < 1:
        raise ValueError("lo must be at least 1")
    return ((lo - 1) // DIVISOR_WINDOW_SPAN) * DIVISOR_WINDOW_SPAN + 1


@lru_cache(maxsize=64)
def _cached_divisor_window(window_lo: int):
    """Return one cached exact divisor-count window."""
    return divisor_counts_segment(window_lo, window_lo + DIVISOR_WINDOW_SPAN)


def _divisor_counts_interval(lo: int, hi: int):
    """Return exact divisor counts on one half-open interval."""
    if lo < 1:
        raise ValueError("lo must be at least 1")
    if hi <= lo:
        raise ValueError("hi must be larger than lo")

    pieces = []
    cursor = lo
    while cursor < hi:
        window_lo = _window_start_for(cursor)
        window_hi = window_lo + DIVISOR_WINDOW_SPAN
        counts = _cached_divisor_window(window_lo)
        take_hi = min(hi, window_hi)
        pieces.append(counts[cursor - window_lo : take_hi - window_lo])
        cursor = take_hi

    if len(pieces) == 1:
        return pieces[0]
    return np.concatenate(pieces)


def _first_value_with_divisors_at_or_after(
    start: int,
    divisor_target: int,
    stop_exclusive: int | None = None,
) -> int:
    """Return the first integer at or after start with exactly divisor_target divisors."""
    if divisor_target < 3:
        raise ValueError("divisor_target must be at least 3")

    search_lo = max(4, int(start))
    while True:
        search_hi = search_lo + DIVISOR_WINDOW_SPAN
        if stop_exclusive is not None:
            search_hi = min(search_hi, stop_exclusive)
        if search_hi <= search_lo:
            raise ValueError(
                f"no d={divisor_target} witness exists in [{int(start)}, {stop_exclusive})"
            )

        counts = _divisor_counts_interval(search_lo, search_hi)
        for offset, count in enumerate(counts):
            if int(count) == divisor_target:
                return search_lo + offset

        if stop_exclusive is not None and search_hi >= stop_exclusive:
            raise ValueError(
                f"no d={divisor_target} witness exists in [{int(start)}, {stop_exclusive})"
            )
        search_lo = search_hi


def _last_value_with_divisors_before(stop_exclusive: int, divisor_target: int) -> int | None:
    """Return the last integer below stop_exclusive with exactly divisor_target divisors."""
    if divisor_target < 3:
        raise ValueError("divisor_target must be at least 3")

    search_hi = int(stop_exclusive)
    while search_hi > 4:
        search_lo = max(4, search_hi - DIVISOR_WINDOW_SPAN)
        counts = _divisor_counts_interval(search_lo, search_hi)
        for offset in range(len(counts) - 1, -1, -1):
            if int(counts[offset]) == divisor_target:
                return search_lo + offset
        search_hi = search_lo
    return None


def W_d(seed: int, divisor_target: int, stop_exclusive: int | None = None) -> int:
    """Return the first integer at or after seed with exactly divisor_target divisors."""
    return _first_value_with_divisors_at_or_after(
        seed,
        divisor_target,
        stop_exclusive=stop_exclusive,
    )


def gap_dmin(left_prime: int, right_prime: int) -> int | None:
    """Return the minimum interior divisor count for one prime gap."""
    if right_prime <= left_prime:
        raise ValueError("right_prime must be larger than left_prime")
    if right_prime - left_prime <= 1:
        return None
    return int(_divisor_counts_interval(left_prime + 1, right_prime).min())


def divisor_gap_profile(left_prime: int, right_prime: int, divisor_target: int) -> dict[str, int | bool | None]:
    """Return the exact carrier geometry for one divisor class around one prime gap."""
    if divisor_target < 3:
        raise ValueError("divisor_target must be at least 3")
    if right_prime <= left_prime:
        raise ValueError("right_prime must be larger than left_prime")

    last_pre_gap_carrier = _last_value_with_divisors_before(left_prime, divisor_target)
    first_in_gap_carrier = None
    last_in_gap_carrier = None
    if right_prime - left_prime > 1:
        counts = _divisor_counts_interval(left_prime + 1, right_prime)
        for offset, count in enumerate(counts):
            if int(count) != divisor_target:
                continue
            carrier = left_prime + 1 + offset
            if first_in_gap_carrier is None:
                first_in_gap_carrier = carrier
            last_in_gap_carrier = carrier

    corridor_start = None
    corridor_end = None
    corridor_width = None
    if last_in_gap_carrier is not None:
        corridor_start = int(last_pre_gap_carrier) + 1 if last_pre_gap_carrier is not None else 4
        corridor_end = int(last_in_gap_carrier)
        corridor_width = corridor_end - corridor_start + 1

    return {
        "left_prime": left_prime,
        "right_prime": right_prime,
        "divisor_target": divisor_target,
        "gap_has_target_carrier": first_in_gap_carrier is not None,
        "last_pre_gap_carrier": last_pre_gap_carrier,
        "first_in_gap_carrier": first_in_gap_carrier,
        "last_in_gap_carrier": last_in_gap_carrier,
        "corridor_start": corridor_start,
        "corridor_end": corridor_end,
        "corridor_width": corridor_width,
    }


def d4_gap_profile(left_prime: int, right_prime: int) -> dict[str, int | bool | None]:
    """Return the exact dominant d=4 carrier geometry around one prime gap."""
    profile = divisor_gap_profile(left_prime, right_prime, 4)
    return {
        "left_prime": left_prime,
        "right_prime": right_prime,
        "gap_has_d4": bool(profile["gap_has_target_carrier"]),
        "last_pre_gap_d4": profile["last_pre_gap_carrier"],
        "first_in_gap_d4": profile["first_in_gap_carrier"],
        "last_in_gap_d4": profile["last_in_gap_carrier"],
    }


def gap_state(left_prime: int, right_prime: int) -> dict[str, object]:
    """Return one exact prime-gap state."""
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


def recover_prime_from_exact_gap(left_prime: int, right_prime: int) -> dict[str, object]:
    """Recover one gap's right endpoint prime from exact local gap structure."""
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

    corridor = divisor_gap_profile(left_prime, right_prime, divisor_target)
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
    """Predict the next prime from one current exact gap by a forward d=4 witness."""
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

    return {
        "localizer_seed": localizer_seed,
        "localizer_divisor_target": localizer_divisor_target,
        "localizer_witness": localizer_witness,
        "predicted_next_left_prime": predicted_next_left_prime,
        "predicted_next_prime": predicted_next_prime,
        "predicted_next_gap_index": current_gap_index + skipped_gap_count + 1,
        "exact_immediate_next_right_prime": exact_immediate_next_right_prime,
        "exact_immediate_hit": exact_immediate_hit,
        "skipped_gap_count": skipped_gap_count,
    }


def gwr_recursive_gap_step(
    current_gap_index: int,
    current_left_prime: int,
    current_right_prime: int,
) -> dict[str, object]:
    """Advance one forward-localized GWR gap->prime->gap step."""
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

    return {
        "current_gap_index": current_gap_index,
        "next_gap_index": int(localization["predicted_next_gap_index"]),
        "current_left_prime": current_state["left_prime"],
        "current_right_prime": current_state["right_prime"],
        "current_gap_width": current_state["gap_width"],
        "current_dmin": current_state["dmin"],
        "current_gap_has_d4": current_state["gap_has_d4"],
        "next_left_prime": next_state["left_prime"],
        "next_right_prime": next_state["right_prime"],
        "next_gap_width": next_state["gap_width"],
        "next_dmin": next_state["dmin"],
        "next_gap_has_d4": next_state["gap_has_d4"],
        "next_d4_corridor_width": next_state["d4_corridor_width"],
        "localizer_seed": int(localization["localizer_seed"]),
        "localizer_divisor_target": int(localization["localizer_divisor_target"]),
        "localizer_witness": int(localization["localizer_witness"]),
        "exact_immediate_next_right_prime": int(localization["exact_immediate_next_right_prime"]),
        "exact_immediate_hit": bool(localization["exact_immediate_hit"]),
        "skipped_gap_count": int(localization["skipped_gap_count"]),
        "recovery_mode": prime_recovery["recovery_mode"],
        "recovered_next_prime": prime_recovery["recovered_prime"],
        "recovery_exact": prime_recovery["recovery_exact"],
    }


def summarize_walk_rows(rows: list[dict[str, object]]) -> dict[str, object]:
    """Aggregate one recursive gap walk."""
    if not rows:
        raise ValueError("rows must not be empty")

    count = len(rows)
    return {
        "steps": count,
        "exact_immediate_hit_rate": sum(int(row["exact_immediate_hit"]) for row in rows) / count,
        "mean_skipped_gap_count": sum(int(row["skipped_gap_count"]) for row in rows) / count,
        "max_skipped_gap_count": max(int(row["skipped_gap_count"]) for row in rows),
        "recovery_exact_rate": sum(int(row["recovery_exact"]) for row in rows) / count,
        "mean_next_gap_width": sum(int(row["next_gap_width"]) for row in rows) / count,
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
    gap_index = start_gap_index
    rows: list[dict[str, object]] = []

    for _ in range(steps):
        row = gwr_recursive_gap_step(gap_index, current_left_prime, current_right_prime)
        rows.append(row)
        current_left_prime = int(row["next_left_prime"])
        current_right_prime = int(row["next_right_prime"])
        gap_index = int(row["next_gap_index"])

    return rows, summarize_walk_rows(rows)


def steps_for_power(power: int) -> int:
    """Return the deterministic step budget for one decade regime."""
    if power <= 7:
        return 100
    if power == 8:
        return 50
    if power == 9:
        return 25
    if power == 10:
        return 10
    if power == 11:
        return 3
    if power == 12:
        return 2
    return 1


def start_gap_for_power(power: int) -> tuple[int, int]:
    """Return the first prime gap whose right endpoint is at or above 10^power."""
    start_value = 10**power
    first_prime_at_or_above = int(nextprime(start_value - 1))
    return int(prevprime(first_prime_at_or_above)), first_prime_at_or_above


def analyze_power(power: int) -> dict[str, object]:
    """Run one decade-scaling measurement."""
    if power < 2:
        raise ValueError("power must be at least 2")

    steps = steps_for_power(power)
    left_prime, right_prime = start_gap_for_power(power)
    started = time.perf_counter()
    _, summary = run_recursive_walk_from_gap(1, left_prime, right_prime, steps)
    runtime_seconds = time.perf_counter() - started

    return {
        "power": power,
        "decade_start": 10**power,
        "steps": steps,
        "start_gap_index": None,
        "start_left_prime": left_prime,
        "start_right_prime": right_prime,
        "exact_immediate_hit_rate": summary["exact_immediate_hit_rate"],
        "mean_skipped_gap_count": summary["mean_skipped_gap_count"],
        "max_skipped_gap_count": summary["max_skipped_gap_count"],
        "recovery_exact_rate": summary["recovery_exact_rate"],
        "mean_next_gap_width": summary["mean_next_gap_width"],
        "runtime_seconds": runtime_seconds,
    }


def summarize_rows(rows: list[dict[str, object]]) -> dict[str, object]:
    """Aggregate one decade-scaling sweep."""
    if not rows:
        raise ValueError("rows must not be empty")

    count = len(rows)
    return {
        "power_start": int(rows[0]["power"]),
        "power_end": int(rows[-1]["power"]),
        "count": count,
        "mean_exact_immediate_hit_rate": sum(float(row["exact_immediate_hit_rate"]) for row in rows) / count,
        "mean_mean_skipped_gap_count": sum(float(row["mean_skipped_gap_count"]) for row in rows) / count,
        "max_runtime_seconds": max(float(row["runtime_seconds"]) for row in rows),
        "max_start_right_prime": max(int(row["start_right_prime"]) for row in rows),
        "all_recovery_exact": all(float(row["recovery_exact_rate"]) == 1.0 for row in rows),
    }


def run_sweep(max_power: int) -> tuple[list[dict[str, object]], dict[str, object]]:
    """Run the decade sweep and return detail rows plus summary."""
    if max_power < 2:
        raise ValueError("max_power must be at least 2")

    rows = [analyze_power(power) for power in range(2, max_power + 1)]
    return rows, summarize_rows(rows)


def main(argv: list[str] | None = None) -> int:
    """Run the scaling sweep and write JSON plus CSV artifacts."""
    args = build_parser().parse_args(argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    rows, summary = run_sweep(args.max_power)
    summary_path = args.output_dir / SUMMARY_FILENAME
    detail_path = args.output_dir / DETAIL_FILENAME
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    fieldnames = [
        "power",
        "decade_start",
        "steps",
        "start_gap_index",
        "start_left_prime",
        "start_right_prime",
        "exact_immediate_hit_rate",
        "mean_skipped_gap_count",
        "max_skipped_gap_count",
        "recovery_exact_rate",
        "mean_next_gap_width",
        "runtime_seconds",
    ]
    with detail_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
