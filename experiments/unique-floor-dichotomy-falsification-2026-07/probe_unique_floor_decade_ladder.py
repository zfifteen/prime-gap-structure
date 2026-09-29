#!/usr/bin/env python3
"""Decade-ladder pressure for Unique Floor Dichotomy through 10^18.

Surface form (program-style ladder):
  256 consecutive primes per decade, decades 10^8 through 10^18
  (11 anchors; 2816 primes; 2805 gaps if every decade completes).

For each gap after a known prime p:
  scan exact tau on (p, q) via repo divisor field,
  form L, m, uniqueness, score U1-U4.

Field prep uses z_band_prime_composite_field / gwr_boundary_walk.
Classical residual classification inside that field is the same stack as the
recursive walk; it does not choose the floor decision beyond tau values.

Status language: measured on the executed ladder. Not a theorem.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SYS_PY = ROOT / "src" / "python"
if str(SYS_PY) not in sys.path:
    sys.path.insert(0, str(SYS_PY))

from z_band_prime_composite_field import divisor_counts_segment  # noqa: E402
from z_band_prime_predictor.gwr_boundary_walk import (  # noqa: E402
    gwr_next_gap_profile,
    next_prime_after,
)


def dynamic_cutoff(q: int) -> int:
    return max(64, math.ceil(0.5 * math.log(q) ** 2))


def u1_ceiling_high(q: int) -> int:
    """High-scale unique m=4 ceiling: max(48, floor(0.5 * C(q)))."""
    return max(48, int(0.5 * dynamic_cutoff(q)))


def u3_ceiling_high(q: int) -> int:
    """High-scale unique m>=8 ceiling: max(16, floor(0.15 * C(q))).

    Mid-scale U3 used a constant 16. At Cramér scale a slight soft growth is
    registered so the hard kill is not a trivial log-scale false positive.
    """
    return max(16, int(0.15 * dynamic_cutoff(q)))


def analyze_gap_from_primes(p: int, q: int) -> dict[str, Any]:
    """Full min-tau level set on (p, q) using segment tau."""
    if q <= p + 1:
        return {
            "p": p,
            "q": q,
            "g": q - p,
            "m": None,
            "w": None,
            "alpha": None,
            "L_size": 0,
            "unique": False,
            "empty_interior": True,
            "C": dynamic_cutoff(q),
        }
    counts = divisor_counts_segment(p + 1, q)
    vals = [int(v) for v in counts]
    m = min(vals)
    level_idx = [i for i, v in enumerate(vals) if v == m]
    w = p + 1 + level_idx[0]
    return {
        "p": p,
        "q": q,
        "g": q - p,
        "m": m,
        "w": w,
        "alpha": w - p,
        "L_size": len(level_idx),
        "unique": len(level_idx) == 1,
        "empty_interior": False,
        "C": dynamic_cutoff(q),
        "u1_ceiling": u1_ceiling_high(q),
        "u3_ceiling": u3_ceiling_high(q),
    }


def walk_decade(
    decade: int,
    primes_per_decade: int,
) -> dict[str, Any]:
    """Sample primes_per_decade consecutive primes starting at first prime >= decade."""
    t0 = time.time()
    p = next_prime_after(decade - 1)
    primes = [p]
    gaps: list[dict[str, Any]] = []
    while len(primes) < primes_per_decade:
        left = primes[-1]
        prof = gwr_next_gap_profile(left)
        right = int(prof["next_prime"])
        row = analyze_gap_from_primes(left, right)
        # Cross-check leftmost winner against profile when interior nonempty
        if not row["empty_interior"] and prof.get("winner_offset") is not None:
            row["profile_winner_d"] = int(prof["winner_d"])
            row["profile_winner_offset"] = int(prof["winner_offset"])
            row["profile_match"] = (
                row["m"] == row["profile_winner_d"]
                and row["alpha"] == row["profile_winner_offset"]
            )
        gaps.append(row)
        primes.append(right)

    return {
        "decade": decade,
        "decade_exp": int(round(math.log10(decade))),
        "primes_per_decade": primes_per_decade,
        "first_p": primes[0],
        "last_p": primes[-1],
        "n_gaps": len(gaps),
        "gaps": gaps,
        "elapsed_seconds": time.time() - t0,
    }


def aggregate(decades: list[dict[str, Any]]) -> dict[str, Any]:
    all_gaps: list[dict[str, Any]] = []
    for d in decades:
        all_gaps.extend(d["gaps"])

    n_gaps = len(all_gaps)
    n_unique = sum(1 for g in all_gaps if g.get("unique"))
    n_multi = sum(1 for g in all_gaps if not g.get("empty_interior") and not g.get("unique"))

    u1_hits = [
        g
        for g in all_gaps
        if g.get("unique") and g.get("m") == 4 and g["g"] > g["u1_ceiling"]
    ]
    u3_hits = [
        g
        for g in all_gaps
        if g.get("unique") and g.get("m") is not None and g["m"] >= 8 and g["g"] > g["u3_ceiling"]
    ]

    m4_g20 = [g for g in all_gaps if g.get("m") == 4 and g["g"] >= 20]
    m4_g20_multi = [g for g in m4_g20 if not g["unique"]]
    multi_rate = (len(m4_g20_multi) / len(m4_g20)) if m4_g20 else None

    unique_m4 = [g for g in all_gaps if g.get("unique") and g.get("m") == 4]
    unique_m3 = [g for g in all_gaps if g.get("unique") and g.get("m") == 3]
    unique_m8 = [g for g in all_gaps if g.get("unique") and g.get("m") is not None and g["m"] >= 8]

    def max_row(rows: list[dict[str, Any]]) -> dict[str, Any] | None:
        if not rows:
            return None
        return max(rows, key=lambda r: r["g"])

    per_decade = []
    for d in decades:
        gs = d["gaps"]
        um4 = [g for g in gs if g.get("unique") and g.get("m") == 4]
        um3 = [g for g in gs if g.get("unique") and g.get("m") == 3]
        m4l = [g for g in gs if g.get("m") == 4 and g["g"] >= 20]
        per_decade.append(
            {
                "decade": d["decade"],
                "decade_exp": d["decade_exp"],
                "n_gaps": d["n_gaps"],
                "first_p": d["first_p"],
                "last_p": d["last_p"],
                "elapsed_seconds": d["elapsed_seconds"],
                "unique_m4_n": len(um4),
                "unique_m4_max_g": max((g["g"] for g in um4), default=0),
                "unique_m3_n": len(um3),
                "unique_m3_max_g": max((g["g"] for g in um3), default=0),
                "m4_g_ge_20": len(m4l),
                "m4_g_ge_20_multi_rate": (
                    sum(1 for g in m4l if not g["unique"]) / len(m4l) if m4l else None
                ),
            }
        )

    profile_checked = [
        g for g in all_gaps if "profile_match" in g
    ]
    profile_mismatches = sum(1 for g in profile_checked if not g["profile_match"])

    u1_falsified = len(u1_hits) > 0
    u2_falsified = multi_rate is not None and len(m4_g20) >= 50 and multi_rate < 0.99
    u2_insufficient = multi_rate is None or len(m4_g20) < 50
    u3_falsified = len(u3_hits) > 0
    u4_ok = any(g["g"] > 40 for g in unique_m3)

    return {
        "hypothesis": "unique_floor_dichotomy",
        "surface": "decade_ladder_1e8_1e18",
        "status_language": "measured_on_executed_decade_ladder_including_1e18",
        "counts": {
            "n_gaps": n_gaps,
            "unique": n_unique,
            "multi_tie": n_multi,
            "unique_m4": len(unique_m4),
            "unique_m3": len(unique_m3),
            "unique_m_ge8": len(unique_m8),
            "m4_g_ge_20": len(m4_g20),
            "m4_g_ge_20_multi": len(m4_g20_multi),
            "u1_hits": len(u1_hits),
            "u3_hits": len(u3_hits),
            "profile_checked": len(profile_checked),
            "profile_mismatches": profile_mismatches,
        },
        "metrics": {
            "max_g_unique_m4": max((g["g"] for g in unique_m4), default=0),
            "max_g_unique_m3": max((g["g"] for g in unique_m3), default=0),
            "max_g_unique_m_ge8": max((g["g"] for g in unique_m8), default=0),
            "multi_rate_m4_g_ge_20": multi_rate,
        },
        "max_rows": {
            "unique_m4": max_row(unique_m4),
            "unique_m3": max_row(unique_m3),
            "unique_m_ge8": max_row(unique_m8),
        },
        "per_decade": per_decade,
        "outcomes": {
            "U1_unique_m4_short_gap": "falsified" if u1_falsified else "holds",
            "U2_long_m4_multi_rate": (
                "insufficient_sample"
                if u2_insufficient
                else ("falsified" if u2_falsified else "holds")
            ),
            "U3_unique_high_floor_short": "falsified" if u3_falsified else "holds",
            "U4_square_long_unique_contrast": (
                "contrast_ok" if u4_ok else "contrast_missing_on_ladder"
            ),
            "U1_falsified": u1_falsified,
            "U2_falsified": u2_falsified,
            "U3_falsified": u3_falsified,
        },
        "sample_u1_hits": u1_hits[:20],
        "sample_u3_hits": u3_hits[:20],
        "sample_long_unique_m4": sorted(unique_m4, key=lambda r: -r["g"])[:20],
    }


def run_large_gap_csv(
    csv_path: Path,
    min_gap: int = 100,
    max_rows: int = 80,
) -> dict[str, Any]:
    """Adversarial long-gap supplement from external maximal-gap style list."""
    t0 = time.time()
    candidates: list[tuple[int, int]] = []
    with csv_path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            g = int(row["gap_size"])
            p = int(row["gap_start"])
            if g >= min_gap:
                candidates.append((p, g))
    candidates.sort(key=lambda x: -x[1])
    candidates = candidates[:max_rows]

    gaps: list[dict[str, Any]] = []
    for p, g_listed in candidates:
        q = p + g_listed
        # Confirm q is prime under field (tau==2); skip if list is stale
        try:
            tau_q = int(divisor_counts_segment(q, q + 1)[0])
            tau_p = int(divisor_counts_segment(p, p + 1)[0])
        except Exception as exc:  # noqa: BLE001
            gaps.append({"p": p, "g_listed": g_listed, "error": str(exc)})
            continue
        if tau_p != 2 or tau_q != 2:
            gaps.append(
                {
                    "p": p,
                    "q": q,
                    "g_listed": g_listed,
                    "skipped": "endpoint_not_tau2_under_field",
                    "tau_p": tau_p,
                    "tau_q": tau_q,
                }
            )
            continue
        row = analyze_gap_from_primes(p, q)
        row["g_listed"] = g_listed
        gaps.append(row)

    analyzed = [g for g in gaps if g.get("m") is not None]
    m4 = [g for g in analyzed if g["m"] == 4]
    m4_multi = [g for g in m4 if not g["unique"]]
    unique_m4 = [g for g in analyzed if g["unique"] and g["m"] == 4]
    u1_hits = [g for g in unique_m4 if g["g"] > g["u1_ceiling"]]

    return {
        "source": str(csv_path),
        "min_gap": min_gap,
        "max_rows": max_rows,
        "n_candidates": len(candidates),
        "n_analyzed": len(analyzed),
        "n_m4": len(m4),
        "n_m4_unique": len(unique_m4),
        "m4_multi_rate": (len(m4_multi) / len(m4)) if m4 else None,
        "max_g_unique_m4": max((g["g"] for g in unique_m4), default=0),
        "u1_hits": len(u1_hits),
        "sample_unique_m4": sorted(unique_m4, key=lambda r: -r["g"])[:10],
        "sample_u1_hits": u1_hits[:10],
        "elapsed_seconds": time.time() - t0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Unique-floor decade ladder to 10^18")
    parser.add_argument("--min-exp", type=int, default=8)
    parser.add_argument("--max-exp", type=int, default=18)
    parser.add_argument("--primes-per-decade", type=int, default=256)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parent
        / "artifacts"
        / "results_decade_ladder_1e8_1e18.json",
    )
    parser.add_argument(
        "--large-gap-csv",
        type=Path,
        default=ROOT / "data" / "external" / "primegap_list_records_1e12_1e18.csv",
    )
    parser.add_argument("--skip-large-gap-csv", action="store_true")
    parser.add_argument("--large-gap-max-rows", type=int, default=40)
    args = parser.parse_args()

    t0 = time.time()
    decades = []
    for exp in range(args.min_exp, args.max_exp + 1):
        decade = 10**exp
        print(f"[ladder] decade 10^{exp} ...", flush=True)
        block = walk_decade(decade, args.primes_per_decade)
        # drop full gap list from per-decade print size later; keep in memory for aggregate
        print(
            f"  first_p={block['first_p']} last_p={block['last_p']} "
            f"gaps={block['n_gaps']} elapsed={block['elapsed_seconds']:.2f}s",
            flush=True,
        )
        decades.append(block)

    summary = aggregate(decades)
    # Slim per-decade gap storage in output: drop raw gaps from decade blocks
    slim_decades = []
    for d in decades:
        slim = {k: v for k, v in d.items() if k != "gaps"}
        slim_decades.append(slim)

    large_gap = None
    if not args.skip_large_gap_csv and args.large_gap_csv.is_file():
        print("[ladder] large-gap CSV supplement ...", flush=True)
        large_gap = run_large_gap_csv(
            args.large_gap_csv,
            min_gap=100,
            max_rows=args.large_gap_max_rows,
        )
        print(
            f"  analyzed={large_gap['n_analyzed']} m4_multi_rate={large_gap['m4_multi_rate']} "
            f"u1_hits={large_gap['u1_hits']} elapsed={large_gap['elapsed_seconds']:.2f}s",
            flush=True,
        )

    payload = {
        "hypothesis": "unique_floor_dichotomy",
        "surface_definition": {
            "form": "decade_ladder",
            "min_exp": args.min_exp,
            "max_exp": args.max_exp,
            "primes_per_decade": args.primes_per_decade,
            "anchors": [10**e for e in range(args.min_exp, args.max_exp + 1)],
            "note": (
                "Sampled consecutive primes at decade anchors including 10^18. "
                "Not a full consecutive scan of all primes to 10^18."
            ),
        },
        "status_language": "measured_on_executed_decade_ladder_including_1e18",
        "u1_ceiling_rule": "max(48, floor(0.5 * C(q)))",
        "u3_ceiling_rule": "max(16, floor(0.15 * C(q)))",
        "decades": slim_decades,
        "aggregate": summary,
        "large_gap_csv_supplement": large_gap,
        "elapsed_seconds_total": time.time() - t0,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "out": str(args.out),
                "n_gaps": summary["counts"]["n_gaps"],
                "U1": summary["outcomes"]["U1_unique_m4_short_gap"],
                "U2": summary["outcomes"]["U2_long_m4_multi_rate"],
                "U3": summary["outcomes"]["U3_unique_high_floor_short"],
                "U4": summary["outcomes"]["U4_square_long_unique_contrast"],
                "max_g_unique_m4": summary["metrics"]["max_g_unique_m4"],
                "max_g_unique_m3": summary["metrics"]["max_g_unique_m3"],
                "multi_rate_m4_g20": summary["metrics"]["multi_rate_m4_g_ge_20"],
                "elapsed_s": round(time.time() - t0, 3),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
