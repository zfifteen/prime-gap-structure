#!/usr/bin/env python3
"""Probe whether tractable Mersenne primes carry distinctive adjacent gap types."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import sys
import time
from collections import Counter
from pathlib import Path

from sympy import nextprime, prevprime


ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = ROOT / "src" / "python"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

DEFAULT_OUTPUT_DIR = ROOT / "output"
DEFAULT_WINDOW_RADIUS = 20
TRACTABLE_MERSENNE_EXPONENTS = (2, 3, 5, 7, 13, 17, 19, 31, 61)
GAP_TYPE_PROBE_PATH = Path(__file__).with_name("gwr_dni_gap_type_probe.py")


def load_gap_type_probe():
    """Load the exact gap-type probe from its sibling file."""
    spec = importlib.util.spec_from_file_location("gwr_dni_gap_type_probe", GAP_TYPE_PROBE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load gwr_dni_gap_type_probe module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


GAP_TYPE_PROBE = load_gap_type_probe()
CARRIER_FAMILIES = GAP_TYPE_PROBE.CARRIER_FAMILIES


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description="Probe adjacent GWR/DNI gap types around tractable Mersenne primes.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for JSON and CSV artifacts.",
    )
    parser.add_argument(
        "--window-radius",
        type=int,
        default=DEFAULT_WINDOW_RADIUS,
        help="Nearby-prime radius used for local exact-type context.",
    )
    return parser


def mersenne_prime(exponent: int) -> int:
    """Return the Mersenne prime candidate `2^p - 1` for one exponent."""
    if exponent < 2:
        raise ValueError("exponent must be at least 2")
    return (1 << exponent) - 1


def local_prime_window(center_prime: int, radius: int) -> list[int]:
    """Return one deterministic nearby-prime window around one center prime."""
    if radius < 0:
        raise ValueError("radius must be nonnegative")

    primes = [center_prime]
    cursor = center_prime
    for _ in range(radius):
        if cursor <= 2:
            break
        cursor = int(prevprime(cursor))
        primes.append(cursor)
        if cursor == 2:
            break

    cursor = center_prime
    for _ in range(radius):
        cursor = int(nextprime(cursor))
        primes.append(cursor)

    return sorted(set(primes))


def type_rank(counter: Counter[str], key: str) -> int | None:
    """Return one 1-based frequency rank for one type key."""
    count = counter.get(key)
    if count is None or count == 0:
        return None
    return 1 + sum(1 for value in counter.values() if value > count)


def local_type_context(
    center_prime: int,
    side: str,
    type_key: str,
    carrier_family: str,
    radius: int,
) -> dict[str, object]:
    """Measure how common one adjacent gap type is inside one nearby-prime window."""
    primes = local_prime_window(center_prime, radius)
    if side == "following":
        gap_rows = [GAP_TYPE_PROBE.gap_type_row(prime) for prime in primes if prime > 2]
    elif side == "preceding":
        gap_rows = [GAP_TYPE_PROBE.gap_type_row(int(prevprime(prime))) for prime in primes if prime > 3]
    else:
        raise ValueError("side must be 'preceding' or 'following'")

    exact_counter = Counter(str(row["type_key"]) for row in gap_rows)
    family_counter = Counter(str(row["carrier_family"]) for row in gap_rows)
    total = len(gap_rows)
    if total == 0:
        raise ValueError("local window produced no comparable gaps")

    return {
        "window_gap_count": total,
        "exact_type_count": int(exact_counter[type_key]),
        "exact_type_share": exact_counter[type_key] / total,
        "exact_type_rank": type_rank(exact_counter, type_key),
        "family_count": int(family_counter[carrier_family]),
        "family_share": family_counter[carrier_family] / total,
        "family_rank": type_rank(family_counter, carrier_family),
    }


def distribution(counter: Counter[str], total: int) -> dict[str, dict[str, float | int]]:
    """Convert one family counter into count/share payload entries."""
    payload: dict[str, dict[str, float | int]] = {}
    for key in CARRIER_FAMILIES:
        count = int(counter.get(key, 0))
        payload[key] = {
            "count": count,
            "share": count / total if total else 0.0,
        }
    return payload


def mersenne_rows(window_radius: int = DEFAULT_WINDOW_RADIUS) -> list[dict[str, object]]:
    """Return one row per tractable known Mersenne prime."""
    rows: list[dict[str, object]] = []
    for exponent in TRACTABLE_MERSENNE_EXPONENTS:
        current_prime = mersenne_prime(exponent)
        row: dict[str, object] = {
            "exponent": exponent,
            "mersenne_prime": current_prime,
            "digits": len(str(current_prime)),
        }

        preceding_type_key = None
        preceding_family = None
        preceding_gap_width = None
        preceding_peak_offset = None
        preceding_dmin = None
        if current_prime > 3:
            preceding_gap = GAP_TYPE_PROBE.gap_type_row(int(prevprime(current_prime)))
            preceding_type_key = str(preceding_gap["type_key"])
            preceding_family = str(preceding_gap["carrier_family"])
            preceding_gap_width = int(preceding_gap["next_gap_width"])
            preceding_peak_offset = int(preceding_gap["next_peak_offset"])
            preceding_dmin = int(preceding_gap["next_dmin"])
            preceding_context = local_type_context(
                current_prime,
                "preceding",
                preceding_type_key,
                preceding_family,
                window_radius,
            )
            row.update(
                {
                    "preceding_type_key": preceding_type_key,
                    "preceding_family": preceding_family,
                    "preceding_gap_width": preceding_gap_width,
                    "preceding_peak_offset": preceding_peak_offset,
                    "preceding_dmin": preceding_dmin,
                    "preceding_local_window_gap_count": int(preceding_context["window_gap_count"]),
                    "preceding_local_exact_type_count": int(preceding_context["exact_type_count"]),
                    "preceding_local_exact_type_share": float(preceding_context["exact_type_share"]),
                    "preceding_local_exact_type_rank": int(preceding_context["exact_type_rank"]),
                    "preceding_local_family_count": int(preceding_context["family_count"]),
                    "preceding_local_family_share": float(preceding_context["family_share"]),
                    "preceding_local_family_rank": int(preceding_context["family_rank"]),
                }
            )
        else:
            row.update(
                {
                    "preceding_type_key": None,
                    "preceding_family": None,
                    "preceding_gap_width": None,
                    "preceding_peak_offset": None,
                    "preceding_dmin": None,
                    "preceding_local_window_gap_count": None,
                    "preceding_local_exact_type_count": None,
                    "preceding_local_exact_type_share": None,
                    "preceding_local_exact_type_rank": None,
                    "preceding_local_family_count": None,
                    "preceding_local_family_share": None,
                    "preceding_local_family_rank": None,
                }
            )

        following_gap = GAP_TYPE_PROBE.gap_type_row(current_prime)
        following_type_key = str(following_gap["type_key"])
        following_family = str(following_gap["carrier_family"])
        following_context = local_type_context(
            current_prime,
            "following",
            following_type_key,
            following_family,
            window_radius,
        )
        row.update(
            {
                "following_type_key": following_type_key,
                "following_family": following_family,
                "following_gap_width": int(following_gap["next_gap_width"]),
                "following_peak_offset": int(following_gap["next_peak_offset"]),
                "following_dmin": int(following_gap["next_dmin"]),
                "following_local_window_gap_count": int(following_context["window_gap_count"]),
                "following_local_exact_type_count": int(following_context["exact_type_count"]),
                "following_local_exact_type_share": float(following_context["exact_type_share"]),
                "following_local_exact_type_rank": int(following_context["exact_type_rank"]),
                "following_local_family_count": int(following_context["family_count"]),
                "following_local_family_share": float(following_context["family_share"]),
                "following_local_family_rank": int(following_context["family_rank"]),
            }
        )
        rows.append(row)

    return rows


def summarize_rows(rows: list[dict[str, object]], window_radius: int) -> dict[str, object]:
    """Aggregate the tractable Mersenne rows into one summary payload."""
    if not rows:
        raise ValueError("rows must not be empty")

    preceding_rows = [row for row in rows if row["preceding_type_key"] is not None]
    following_rows = rows
    following_p_ge_5 = [row for row in rows if int(row["exponent"]) >= 5]
    preceding_family_counter = Counter(str(row["preceding_family"]) for row in preceding_rows)
    following_family_counter = Counter(str(row["following_family"]) for row in following_rows)
    preceding_type_counter = Counter(str(row["preceding_type_key"]) for row in preceding_rows)
    following_type_counter = Counter(str(row["following_type_key"]) for row in following_rows)
    p_ge_5_following_type_counter = Counter(str(row["following_type_key"]) for row in following_p_ge_5)

    return {
        "tractable_limit_reason": (
            "Current exact gap typing uses the repo's int64-based divisor-field segment path, "
            "so the tested known Mersenne-prime surface stops at exponent 61."
        ),
        "tractable_mersenne_exponents": list(TRACTABLE_MERSENNE_EXPONENTS),
        "local_window_radius": window_radius,
        "mersenne_prime_count": len(rows),
        "preceding_gap_count": len(preceding_rows),
        "following_gap_count": len(following_rows),
        "distinct_preceding_type_count": len(preceding_type_counter),
        "distinct_following_type_count": len(following_type_counter),
        "preceding_family_distribution": distribution(preceding_family_counter, len(preceding_rows)),
        "following_family_distribution": distribution(following_family_counter, len(following_rows)),
        "p_ge_5_following_all_odd_semiprime": all(
            str(row["following_family"]) == "odd_semiprime" for row in following_p_ge_5
        ),
        "p_ge_5_following_exact_type_distribution": {
            key: int(value) for key, value in p_ge_5_following_type_counter.items()
        },
        "p_ge_5_following_local_exact_rank_one_count": sum(
            int(int(row["following_local_exact_type_rank"]) == 1) for row in following_p_ge_5
        ),
        "p_ge_5_following_local_exact_share_min": min(
            float(row["following_local_exact_type_share"]) for row in following_p_ge_5
        ),
        "p_ge_5_following_local_exact_share_max": max(
            float(row["following_local_exact_type_share"]) for row in following_p_ge_5
        ),
    }


def main(argv: list[str] | None = None) -> int:
    """Run the tractable Mersenne probe and write JSON plus CSV artifacts."""
    args = build_parser().parse_args(argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    started = time.perf_counter()
    rows = mersenne_rows(window_radius=args.window_radius)
    summary = summarize_rows(rows, window_radius=args.window_radius)
    summary["runtime_seconds"] = time.perf_counter() - started

    summary_path = args.output_dir / "gwr_dni_mersenne_gap_type_probe_summary.json"
    detail_path = args.output_dir / "gwr_dni_mersenne_gap_type_probe_details.csv"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    fieldnames = [
        "exponent",
        "mersenne_prime",
        "digits",
        "preceding_type_key",
        "preceding_family",
        "preceding_gap_width",
        "preceding_peak_offset",
        "preceding_dmin",
        "preceding_local_window_gap_count",
        "preceding_local_exact_type_count",
        "preceding_local_exact_type_share",
        "preceding_local_exact_type_rank",
        "preceding_local_family_count",
        "preceding_local_family_share",
        "preceding_local_family_rank",
        "following_type_key",
        "following_family",
        "following_gap_width",
        "following_peak_offset",
        "following_dmin",
        "following_local_window_gap_count",
        "following_local_exact_type_count",
        "following_local_exact_type_share",
        "following_local_exact_type_rank",
        "following_local_family_count",
        "following_local_family_share",
        "following_local_family_rank",
    ]
    with detail_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
