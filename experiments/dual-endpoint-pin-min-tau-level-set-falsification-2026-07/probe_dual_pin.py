#!/usr/bin/env python3
"""Falsification probe: dual right-pin of multi-tie min-tau level sets.

PGS objects first:
  - consecutive prime gap (p, q)
  - tau field on the interior
  - L = co-minimal level set of min tau
  - w = min L, w_R = max L
  - clearance = q - w_R

Hard claims under attack (insight package):
  P1: multi-tie clearance <= 32 on p_max = 2e6 regime
  P2: multi-tie clearance <= max(32, floor(0.25 * C(q))) on p_max = 1e7
  P3: multi-tie median clearance for g >= 20 stays <= 8 (flat vs g)

Field prep uses divisor accumulation and tau==2 primes.
No primality API chooses the level set.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import time
from collections import defaultdict
from pathlib import Path
from typing import Any


def dynamic_cutoff(q: int) -> int:
    return max(64, math.ceil(0.5 * math.log(q) ** 2))


def p2_bound(q: int) -> int:
    return max(32, int(0.25 * dynamic_cutoff(q)))


def divisor_counts(limit: int) -> list[int]:
    tau = [0] * (limit + 1)
    for d in range(1, limit + 1):
        for n in range(d, limit + 1, d):
            tau[n] += 1
    return tau


def primes_from_tau(tau: list[int]) -> list[int]:
    return [n for n in range(2, len(tau)) if tau[n] == 2]


def analyze_gap(p: int, q: int, tau: list[int]) -> dict[str, Any] | None:
    if q - p < 2:
        return None
    first = p + 1
    last = q - 1
    if last < first:
        return None
    min_tau = tau[first]
    for n in range(first + 1, last + 1):
        t = tau[n]
        if t < min_tau:
            min_tau = t
    level = [n for n in range(first, last + 1) if tau[n] == min_tau]
    w = level[0]
    w_r = level[-1]
    return {
        "p": p,
        "q": q,
        "g": q - p,
        "m": min_tau,
        "w": w,
        "w_R": w_r,
        "alpha": w - p,
        "clearance": q - w_r,
        "L_size": len(level),
        "C": dynamic_cutoff(q),
        "p2_bound": p2_bound(q),
        "multi_tie": len(level) >= 2,
    }


def median_int(values: list[int]) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    n = len(ordered)
    mid = n // 2
    if n % 2:
        return float(ordered[mid])
    return (ordered[mid - 1] + ordered[mid]) / 2.0


def percentile(values: list[int], p: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, int(math.ceil(p * len(ordered)) - 1)))
    return float(ordered[idx])


def run_probe(
    p_max: int,
    p_min: int = 11,
    sample_ce_cap: int = 50,
) -> dict[str, Any]:
    t0 = time.time()
    hard_limit = p_max + max(400, int(2 * math.log(p_max + 3) ** 2) + 200)
    tau = divisor_counts(hard_limit)
    primes = primes_from_tau(tau)

    multi_clearances: list[int] = []
    multi_g20_clearances: list[int] = []
    g_bin_clears: dict[int, list[int]] = defaultdict(list)

    n_gaps = 0
    n_multi = 0
    n_p1_hits = 0  # clearance > 32
    n_p2_hits = 0  # clearance > p2_bound
    max_clear = 0
    max_row: dict[str, Any] | None = None
    samples_clear_gt_32: list[dict[str, Any]] = []
    samples_p2: list[dict[str, Any]] = []
    theorem_breaks = 0

    for i, p in enumerate(primes):
        if p < p_min:
            continue
        if p > p_max:
            break
        if i + 1 >= len(primes):
            break
        q = primes[i + 1]
        if q >= hard_limit:
            break
        row = analyze_gap(p, q, tau)
        if row is None:
            continue
        n_gaps += 1
        if row["alpha"] > row["C"]:
            theorem_breaks += 1
        if not row["multi_tie"]:
            continue
        n_multi += 1
        c = int(row["clearance"])
        multi_clearances.append(c)
        if c > max_clear:
            max_clear = c
            max_row = dict(row)
        if row["g"] >= 20:
            multi_g20_clearances.append(c)
            g_bin_clears[(row["g"] // 10) * 10].append(c)
        if c > 32:
            n_p1_hits += 1
            if len(samples_clear_gt_32) < sample_ce_cap:
                samples_clear_gt_32.append(dict(row))
        if c > row["p2_bound"]:
            n_p2_hits += 1
            if len(samples_p2) < sample_ce_cap:
                samples_p2.append(dict(row))

    # P3: median for g>=20; linear climb check on bins with n>=100
    med_g20 = median_int(multi_g20_clearances)
    bin_rows: list[dict[str, Any]] = []
    for gb in sorted(g_bin_clears):
        xs = g_bin_clears[gb]
        if len(xs) < 100:
            continue
        bin_rows.append(
            {
                "g_bin": gb,
                "n": len(xs),
                "median_clearance": median_int(xs),
                "mean_clearance": sum(xs) / len(xs),
                "max_clearance": max(xs),
            }
        )
    linear_climb = False
    if len(bin_rows) >= 3:
        # crude: last median > first median + 2 and strictly increasing majority steps
        meds = [b["median_clearance"] for b in bin_rows if b["median_clearance"] is not None]
        if meds:
            increases = sum(1 for a, b in zip(meds, meds[1:]) if b > a)
            if meds[-1] is not None and meds[0] is not None:
                if meds[-1] > meds[0] + 2 and increases >= max(1, len(meds) - 2):
                    linear_climb = True

    p1_status = "holds" if n_p1_hits == 0 else "falsified"
    # P1 is only decisive on p_max<=2e6; still report raw hit count everywhere
    if p_max <= 2_000_000:
        p1_decision = p1_status
    else:
        p1_decision = "out_of_registered_window"

    p2_status = "holds" if n_p2_hits == 0 else "falsified"
    if p_max < 10_000_000:
        # intermediate regimes still report P2 bound hits
        p2_decision = p2_status
    else:
        p2_decision = p2_status

    p3_fail = (med_g20 is not None and med_g20 > 8.0) or linear_climb
    p3_status = "falsified" if p3_fail else "holds"

    elapsed = time.time() - t0
    return {
        "hypothesis": "dual_endpoint_pin_multi_tie_right_clearance",
        "status_language": "measured_on_regime_only",
        "regime": {
            "p_min": p_min,
            "p_max": p_max,
            "hard_limit": hard_limit,
        },
        "counts": {
            "gaps_nonempty": n_gaps,
            "multi_tie": n_multi,
            "clearance_gt_32": n_p1_hits,
            "clearance_gt_p2_bound": n_p2_hits,
            "theorem_left_breaks": theorem_breaks,
        },
        "metrics": {
            "max_clearance": max_clear,
            "mean_clearance": (
                sum(multi_clearances) / len(multi_clearances) if multi_clearances else None
            ),
            "median_clearance": median_int(multi_clearances),
            "p95_clearance": percentile(multi_clearances, 0.95),
            "median_clearance_g_ge_20": med_g20,
        },
        "max_clearance_row": max_row,
        "g_bins_g_ge_20_n100": bin_rows,
        "outcomes": {
            "P1_clearance_le_32": p1_decision,
            "P1_raw_status": p1_status,
            "P2_clearance_le_bound": p2_decision,
            "P3_median_flat": p3_status,
            "P1_falsified": n_p1_hits > 0 and p_max <= 2_000_000,
            "P2_falsified": n_p2_hits > 0,
            "P3_falsified": p3_fail,
            "linear_climb_detected": linear_climb,
        },
        "sample_clearance_gt_32": samples_clear_gt_32,
        "sample_p2_violations": samples_p2,
        "elapsed_seconds": elapsed,
    }


def write_ce_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Falsify dual multi-tie right-pin claims")
    parser.add_argument("--p-min", type=int, default=11)
    parser.add_argument("--p-max", type=int, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--csv-ce", type=Path, default=None)
    parser.add_argument("--sample-ce-cap", type=int, default=50)
    args = parser.parse_args()

    result = run_probe(
        p_max=args.p_max,
        p_min=args.p_min,
        sample_ce_cap=args.sample_ce_cap,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if args.csv_ce is not None:
        write_ce_csv(args.csv_ce, result["sample_clearance_gt_32"])

    print(
        json.dumps(
            {
                "p_max": args.p_max,
                "multi_tie": result["counts"]["multi_tie"],
                "max_clearance": result["metrics"]["max_clearance"],
                "clearance_gt_32": result["counts"]["clearance_gt_32"],
                "p2_hits": result["counts"]["clearance_gt_p2_bound"],
                "P1": result["outcomes"]["P1_clearance_le_32"],
                "P2": result["outcomes"]["P2_clearance_le_bound"],
                "P3": result["outcomes"]["P3_median_flat"],
                "max_row": result["max_clearance_row"],
                "elapsed_s": round(result["elapsed_seconds"], 3),
                "out": str(args.out),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
