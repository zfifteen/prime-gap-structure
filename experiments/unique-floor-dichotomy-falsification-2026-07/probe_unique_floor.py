#!/usr/bin/env python3
"""Falsification probe: Unique Floor Dichotomy.

PGS objects first:
  - consecutive prime gap (p, q)
  - tau on the interior
  - L = min-tau level set, m = min tau, w = min L
  - uniqueness |L|==1 vs multi-tie
  - gap length g = q - p

Claims under attack:
  U1: unique m=4 forces short g (regime-dependent ceiling)
  U2: among g>=20 and m=4, multi-tie rate >= 0.99
  U3: unique m>=8 forces g <= 16
  U4: unique m=3 may still have g > 40 (contrast arm)

No classical primality API chooses the floor set.
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


def u1_ceiling(p_max: int, q: int) -> int:
    """Hard g ceiling for unique m=4 under the registered schedule."""
    if p_max <= 5_000_000:
        return 40
    return max(48, int(0.5 * dynamic_cutoff(q)))


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
    return {
        "p": p,
        "q": q,
        "g": q - p,
        "m": min_tau,
        "w": w,
        "alpha": w - p,
        "L_size": len(level),
        "unique": len(level) == 1,
        "C": dynamic_cutoff(q),
    }


def run_probe(
    p_max: int,
    p_min: int = 11,
    sample_ce_cap: int = 40,
) -> dict[str, Any]:
    t0 = time.time()
    hard_limit = p_max + max(400, int(2 * math.log(p_max + 3) ** 2) + 200)
    tau = divisor_counts(hard_limit)
    primes = primes_from_tau(tau)

    n_gaps = 0
    n_unique = 0
    n_multi = 0

    # U1
    unique_m4: list[dict[str, Any]] = []
    u1_hits: list[dict[str, Any]] = []
    max_g_unique_m4 = 0
    max_g_unique_m4_row: dict[str, Any] | None = None

    # U2
    n_m4_g20 = 0
    n_m4_g20_multi = 0

    # U3
    unique_m_ge8: list[dict[str, Any]] = []
    u3_hits: list[dict[str, Any]] = []
    max_g_unique_m_ge8 = 0
    max_g_unique_m_ge8_row: dict[str, Any] | None = None

    # U4 contrast
    unique_m3: list[dict[str, Any]] = []
    max_g_unique_m3 = 0
    max_g_unique_m3_row: dict[str, Any] | None = None
    n_unique_m3_g_gt_40 = 0

    # per-m unique max g
    unique_max_g_by_m: dict[int, int] = defaultdict(int)
    unique_count_by_m: dict[int, int] = defaultdict(int)

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

        m = int(row["m"])
        g = int(row["g"])
        unique = bool(row["unique"])

        if unique:
            n_unique += 1
            unique_count_by_m[m] += 1
            if g > unique_max_g_by_m[m]:
                unique_max_g_by_m[m] = g
        else:
            n_multi += 1

        # U2 set
        if m == 4 and g >= 20:
            n_m4_g20 += 1
            if not unique:
                n_m4_g20_multi += 1

        if not unique:
            continue

        # unique only below
        if m == 4:
            unique_m4.append(row)
            if g > max_g_unique_m4:
                max_g_unique_m4 = g
                max_g_unique_m4_row = dict(row)
            ceil_g = u1_ceiling(p_max, q)
            if g > ceil_g:
                hit = dict(row)
                hit["u1_ceiling"] = ceil_g
                u1_hits.append(hit)
        elif m == 3:
            unique_m3.append(row)
            if g > max_g_unique_m3:
                max_g_unique_m3 = g
                max_g_unique_m3_row = dict(row)
            if g > 40:
                n_unique_m3_g_gt_40 += 1
        elif m >= 8:
            unique_m_ge8.append(row)
            if g > max_g_unique_m_ge8:
                max_g_unique_m_ge8 = g
                max_g_unique_m_ge8_row = dict(row)
            if g > 16:
                u3_hits.append(dict(row))

    multi_rate_m4_g20 = (
        n_m4_g20_multi / n_m4_g20 if n_m4_g20 else None
    )

    u1_falsified = len(u1_hits) > 0
    u2_falsified = (
        n_m4_g20 >= 1000 and multi_rate_m4_g20 is not None and multi_rate_m4_g20 < 0.99
    )
    u2_insufficient = n_m4_g20 < 1000
    u3_falsified = len(u3_hits) > 0
    u4_contrast_ok = n_unique_m3_g_gt_40 > 0

    def status(flag: bool, *, insufficient: bool = False) -> str:
        if insufficient:
            return "insufficient_sample"
        return "falsified" if flag else "holds"

    # sample long unique m4 for CSV (g descending)
    long_unique_m4 = sorted(unique_m4, key=lambda r: -r["g"])[:sample_ce_cap]
    sample_u1 = u1_hits[:sample_ce_cap]
    sample_u3 = u3_hits[:sample_ce_cap]

    by_m_table = [
        {
            "m": m,
            "unique_n": unique_count_by_m[m],
            "unique_max_g": unique_max_g_by_m[m],
        }
        for m in sorted(unique_count_by_m)
    ]

    elapsed = time.time() - t0
    return {
        "hypothesis": "unique_floor_dichotomy",
        "status_language": "measured_on_regime_only",
        "regime": {
            "p_min": p_min,
            "p_max": p_max,
            "hard_limit": hard_limit,
            "u1_ceiling_rule": (
                "40" if p_max <= 5_000_000 else "max(48, floor(0.5*C(q))) per row"
            ),
        },
        "counts": {
            "gaps_nonempty": n_gaps,
            "unique": n_unique,
            "multi_tie": n_multi,
            "unique_m4": len(unique_m4),
            "unique_m3": len(unique_m3),
            "unique_m_ge8": len(unique_m_ge8),
            "m4_g_ge_20": n_m4_g20,
            "m4_g_ge_20_multi": n_m4_g20_multi,
            "u1_hits": len(u1_hits),
            "u3_hits": len(u3_hits),
            "unique_m3_g_gt_40": n_unique_m3_g_gt_40,
            "theorem_left_breaks": theorem_breaks,
        },
        "metrics": {
            "max_g_unique_m4": max_g_unique_m4,
            "max_g_unique_m3": max_g_unique_m3,
            "max_g_unique_m_ge8": max_g_unique_m_ge8,
            "multi_rate_m4_g_ge_20": multi_rate_m4_g20,
        },
        "max_rows": {
            "unique_m4": max_g_unique_m4_row,
            "unique_m3": max_g_unique_m3_row,
            "unique_m_ge8": max_g_unique_m_ge8_row,
        },
        "unique_max_g_by_m": by_m_table,
        "outcomes": {
            "U1_unique_m4_short_gap": status(u1_falsified),
            "U2_long_m4_multi_rate": status(u2_falsified, insufficient=u2_insufficient),
            "U3_unique_high_floor_short": status(u3_falsified),
            "U4_square_long_unique_contrast": (
                "contrast_ok" if u4_contrast_ok else "contrast_missing"
            ),
            "U1_falsified": u1_falsified,
            "U2_falsified": u2_falsified,
            "U3_falsified": u3_falsified,
        },
        "sample_u1_hits": sample_u1,
        "sample_u3_hits": sample_u3,
        "sample_long_unique_m4": long_unique_m4,
        "elapsed_seconds": elapsed,
    }


def write_ce_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    # unify keys
    keys: list[str] = []
    seen = set()
    for r in rows:
        for k in r:
            if k not in seen:
                seen.add(k)
                keys.append(k)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Falsify Unique Floor Dichotomy")
    parser.add_argument("--p-min", type=int, default=11)
    parser.add_argument("--p-max", type=int, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--csv-ce", type=Path, default=None)
    parser.add_argument("--sample-ce-cap", type=int, default=40)
    args = parser.parse_args()

    result = run_probe(
        p_max=args.p_max,
        p_min=args.p_min,
        sample_ce_cap=args.sample_ce_cap,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    if args.csv_ce is not None:
        # Prefer hard hits; else long unique m4 samples
        rows = result["sample_u1_hits"] or result["sample_u3_hits"] or result["sample_long_unique_m4"]
        # tag source
        tagged = []
        for r in result["sample_u1_hits"]:
            rr = dict(r)
            rr["ce_class"] = "U1"
            tagged.append(rr)
        for r in result["sample_u3_hits"]:
            rr = dict(r)
            rr["ce_class"] = "U3"
            tagged.append(rr)
        if not tagged:
            for r in result["sample_long_unique_m4"]:
                rr = dict(r)
                rr["ce_class"] = "long_unique_m4"
                tagged.append(rr)
        write_ce_csv(args.csv_ce, tagged)

    print(
        json.dumps(
            {
                "p_max": args.p_max,
                "unique_m4_max_g": result["metrics"]["max_g_unique_m4"],
                "unique_m3_max_g": result["metrics"]["max_g_unique_m3"],
                "unique_m_ge8_max_g": result["metrics"]["max_g_unique_m_ge8"],
                "multi_rate_m4_g20": result["metrics"]["multi_rate_m4_g_ge_20"],
                "U1": result["outcomes"]["U1_unique_m4_short_gap"],
                "U2": result["outcomes"]["U2_long_m4_multi_rate"],
                "U3": result["outcomes"]["U3_unique_high_floor_short"],
                "U4": result["outcomes"]["U4_square_long_unique_contrast"],
                "u1_hits": result["counts"]["u1_hits"],
                "u3_hits": result["counts"]["u3_hits"],
                "max_m4": result["max_rows"]["unique_m4"],
                "elapsed_s": round(result["elapsed_seconds"], 3),
                "out": str(args.out),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
