#!/usr/bin/env python3
"""Run the Modular Congestion Scaling falsification experiment."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np


ZONE_RADIUS = 1_000_000
COVERAGE_LIMIT = 0.25
PRESSURE_PERCENTILE_LIMIT = 90.0


def primes_up_to(limit: int) -> list[int]:
    sieve = bytearray(b"\x01") * (limit + 1)
    if limit >= 0:
        sieve[0] = 0
    if limit >= 1:
        sieve[1] = 0
    root = math.isqrt(limit)
    for p in range(2, root + 1):
        if sieve[p]:
            start = p * p
            sieve[start : limit + 1 : p] = b"\x00" * (((limit - start) // p) + 1)
    return [i for i, is_prime in enumerate(sieve) if is_prime]


def h_value(x: int) -> int:
    return math.ceil(math.log(x) ** 2)


def h_ranges(x0: int, n: int) -> list[tuple[int, int, int]]:
    ranges: list[tuple[int, int, int]] = []
    start = x0
    current = h_value(start)
    for x in range(x0 + 1, n + 1):
        h = h_value(x)
        if h != current:
            ranges.append((start, x - 1, current))
            start = x
            current = h
    ranges.append((start, n, current))
    return ranges


def prime_gaps(primes: list[int], x0: int, n: int) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    max_gap = 0
    max_excess = 0.0
    for p, q in zip(primes, primes[1:]):
        gap = q - p
        is_record = gap > max_gap
        excess = gap / (math.log(p) ** 2)
        is_champagne = is_record and excess > 1.15 * max_excess
        if x0 <= p and q <= n and is_record:
            rows.append(
                {
                    "p": p,
                    "q": q,
                    "gap": gap,
                    "is_record": True,
                    "is_champagne": is_champagne,
                }
            )
        if is_record:
            max_gap = gap
            max_excess = max(max_excess, excess)
    return rows


def merged_coverage(zones: list[tuple[int, int]], x0: int, n: int) -> tuple[list[tuple[int, int]], int]:
    if not zones:
        return [], 0
    zones.sort()
    merged: list[list[int]] = []
    for start, end in zones:
        clipped_start = max(start, x0)
        clipped_end = min(end, n)
        if clipped_start > clipped_end:
            continue
        if not merged or clipped_start > merged[-1][1] + 1:
            merged.append([clipped_start, clipped_end])
        else:
            merged[-1][1] = max(merged[-1][1], clipped_end)
    coverage = sum(end - start + 1 for start, end in merged)
    return [(start, end) for start, end in merged], coverage


def inside_zones(x: int, zones: list[tuple[int, int]]) -> bool:
    left = 0
    right = len(zones)
    while left < right:
        mid = (left + right) // 2
        start, end = zones[mid]
        if x < start:
            right = mid
        elif x > end:
            left = mid + 1
        else:
            return True
    return False


def nearest_prior_center(x: int, centers: list[int]) -> int | None:
    idx = np.searchsorted(np.asarray(centers, dtype=np.int64), x, side="right") - 1
    if idx < 0:
        return None
    return centers[int(idx)]


def write_csv(path: Path, rows: list[dict[str, object]], columns: list[str]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def run(x0: int, n: int, out_dir: Path) -> dict[str, object]:
    out_dir.mkdir(parents=True, exist_ok=True)
    h_max = h_value(n)
    primes = primes_up_to(n)
    active_primes = primes_up_to(h_max)
    events = prime_gaps(primes, x0, n)

    xs_len = n - x0 + 1
    mcs = np.empty(xs_len, dtype=np.float64)
    pressure_rows: list[dict[str, object]] = []
    centers: list[int] = []
    zones: list[tuple[int, int]] = []
    phase_centers: list[int] = []

    open_len = n - x0 + h_max + 1
    open_slots = np.ones(open_len + 1, dtype=np.bool_)
    open_slots[0] = False
    added_prime_index = 0
    running_max = -1.0
    running_rank = 0
    phase_running_max = -1.0
    phase_density_multiplier = 1.0
    phase_prime_index = 0

    for start, end, h in h_ranges(x0, n):
        while added_prime_index < len(active_primes) and active_primes[added_prime_index] <= h:
            ell = active_primes[added_prime_index]
            first = ((x0 + 1 + ell - 1) // ell) * ell
            offset = first - x0
            open_slots[offset : open_len + 1 : ell] = False
            added_prime_index += 1

        while phase_prime_index < len(active_primes) and active_primes[phase_prime_index] <= h:
            ell = active_primes[phase_prime_index]
            phase_density_multiplier *= ell / (ell - 1)
            phase_prime_index += 1

        prefix = np.empty(open_len + 1, dtype=np.int32)
        prefix[0] = 0
        np.cumsum(open_slots[1:], dtype=np.int32, out=prefix[1:])

        start_idx = start - x0
        end_idx = end - x0
        indexes = np.arange(start_idx, end_idx + 1, dtype=np.int64)
        counts = prefix[indexes + h] - prefix[indexes]
        values = np.divide(
            added_prime_index * h,
            counts,
            out=np.full(counts.shape, math.inf, dtype=np.float64),
            where=counts != 0,
        )
        mcs[start_idx : end_idx + 1] = values

        phase_value = added_prime_index * phase_density_multiplier
        if phase_value > phase_running_max:
            phase_centers.append(start)
            phase_running_max = phase_value

        prior = np.empty(values.shape, dtype=np.float64)
        prior[0] = running_max
        if len(values) > 1:
            prior[1:] = np.maximum.accumulate(values[:-1])
            prior[1:] = np.maximum(prior[1:], running_max)
        local_hits = np.flatnonzero(values > prior)
        for hit in local_hits:
            center = start + int(hit)
            running_max = float(values[hit])
            running_rank += 1
            centers.append(center)
            zones.append((center - ZONE_RADIUS, center + ZONE_RADIUS))
            pressure_rows.append(
                {
                    "center": center,
                    "mcs": running_max,
                    "h": h,
                    "constraint_count": added_prime_index,
                    "open_slots": int(counts[hit]),
                    "running_rank": running_rank,
                }
            )

    merged_zones, coverage = merged_coverage(zones, x0, n)
    phase_zones, phase_coverage = merged_coverage(
        [(c - ZONE_RADIUS, c + ZONE_RADIUS) for c in phase_centers], x0, n
    )

    sorted_mcs = np.sort(mcs[np.isfinite(mcs)])
    gap_rows: list[dict[str, object]] = []
    missed_records = 0
    missed_champagne = 0
    record_percentiles: list[float] = []
    champagne_percentiles: list[float] = []
    phase_hits = 0

    for event in events:
        p = int(event["p"])
        value = float(mcs[p - x0])
        percentile = 100.0 * float(np.searchsorted(sorted_mcs, value, side="right")) / float(len(sorted_mcs))
        prior = nearest_prior_center(p, centers)
        in_zone = inside_zones(p, merged_zones)
        in_phase_zone = inside_zones(p, phase_zones)
        if in_phase_zone:
            phase_hits += 1
        if not in_zone:
            missed_records += 1
            if bool(event["is_champagne"]):
                missed_champagne += 1
        record_percentiles.append(percentile)
        if bool(event["is_champagne"]):
            champagne_percentiles.append(percentile)
        gap_rows.append(
            {
                "p": p,
                "q": event["q"],
                "gap": event["gap"],
                "is_record": event["is_record"],
                "is_champagne": event["is_champagne"],
                "mcs_at_p": value,
                "mcs_percentile": percentile,
                "nearest_prior_zone_center": "" if prior is None else prior,
                "distance_to_prior_zone": "" if prior is None else p - prior,
                "inside_predicted_zone": in_zone,
            }
        )

    coverage_fraction = coverage / xs_len
    record_median = float(np.median(record_percentiles)) if record_percentiles else math.nan
    champagne_median = float(np.median(champagne_percentiles)) if champagne_percentiles else math.nan
    phase_hit_rate = phase_hits / len(events) if events else math.nan

    if missed_records:
        verdict = "falsified_record_miss"
    elif missed_champagne:
        verdict = "falsified_champagne_miss"
    elif coverage_fraction >= COVERAGE_LIMIT:
        verdict = "not_predictive_coverage_too_large"
    elif record_median < PRESSURE_PERCENTILE_LIMIT:
        verdict = "not_predictive_pressure_rank_low"
    elif phase_hit_rate == 1.0:
        verdict = "not_distinguished_from_average_density"
    else:
        verdict = "finite_validated"

    summary = {
        "x0": x0,
        "n": n,
        "record_count": len(events),
        "champagne_count": sum(1 for row in gap_rows if row["is_champagne"]),
        "missed_record_count": missed_records,
        "missed_champagne_count": missed_champagne,
        "predicted_zone_count": len(pressure_rows),
        "merged_predicted_zone_count": len(merged_zones),
        "predicted_zone_coverage_fraction": coverage_fraction,
        "record_median_mcs_percentile": record_median,
        "champagne_median_mcs_percentile": champagne_median,
        "phase_blind_control_hit_rate": phase_hit_rate,
        "phase_blind_coverage_fraction": phase_coverage / xs_len,
        "verdict": verdict,
    }

    write_csv(
        out_dir / "pressure_zones.csv",
        pressure_rows,
        ["center", "mcs", "h", "constraint_count", "open_slots", "running_rank"],
    )
    write_csv(
        out_dir / "gap_events.csv",
        gap_rows,
        [
            "p",
            "q",
            "gap",
            "is_record",
            "is_champagne",
            "mcs_at_p",
            "mcs_percentile",
            "nearest_prior_zone_center",
            "distance_to_prior_zone",
            "inside_predicted_zone",
        ],
    )
    with (out_dir / "summary.json").open("w") as handle:
        json.dump(summary, handle, indent=2)
        handle.write("\n")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--x0", type=int, default=1_000_000)
    parser.add_argument("--n", type=int, default=10_000_000)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "results_1e6_1e7",
    )
    args = parser.parse_args()
    summary = run(args.x0, args.n, args.out_dir)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
