#!/usr/bin/env python3
"""Classify exact GWR/DNI next-gap winners into deterministic gap types."""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import gmpy2


ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = ROOT / "src" / "python"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from z_band_prime_predictor import gwr_next_gap_profile

DEFAULT_OUTPUT_DIR = ROOT / "output"
DEFAULT_MAX_RIGHT_PRIME = 1_000_000
PEAK_OFFSET_CUTOFFS = (1, 2, 4, 6, 8, 10, 12)
CARRIER_FAMILIES = (
    "prime_square",
    "prime_cube",
    "even_semiprime",
    "odd_semiprime",
    "higher_divisor_even",
    "higher_divisor_odd",
)


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description="Classify exact GWR/DNI next-gap winners into gap types.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for JSON and CSV artifacts.",
    )
    parser.add_argument(
        "--max-right-prime",
        type=int,
        default=DEFAULT_MAX_RIGHT_PRIME,
        help="Largest current right-end prime q included in the exact scan.",
    )
    return parser


def first_open_offset(residue: int) -> int:
    """Return the first even offset after one residue whose class is open mod 30."""
    for offset in (2, 4, 6, 8, 10, 12):
        candidate = (residue + offset) % 30
        if candidate % 3 != 0 and candidate % 5 != 0:
            return offset
    raise RuntimeError(f"no wheel-open offset found for residue {residue}")


def prime_cube_root(n: int) -> int | None:
    """Return the prime cube root of n when n is exactly p^3."""
    root, exact = gmpy2.iroot(gmpy2.mpz(n), 3)
    if not exact or not gmpy2.is_prime(root):
        return None
    return int(root)


def carrier_family(winner: int, winner_d: int) -> str:
    """Return the coarse carrier family for one exact GWR/DNI winner."""
    if winner_d < 3:
        raise ValueError("winner_d must describe one composite winner")
    if winner_d == 3:
        return "prime_square"
    if winner_d == 4:
        if prime_cube_root(winner) is not None:
            return "prime_cube"
        if winner % 2 == 0:
            return "even_semiprime"
        return "odd_semiprime"
    if winner % 2 == 0:
        return "higher_divisor_even"
    return "higher_divisor_odd"


def type_key(first_open: int, winner_d: int, winner_offset: int, family: str) -> str:
    """Return one stable string key for one exact gap type."""
    return f"o{first_open}_d{winner_d}_a{winner_offset}_{family}"


def gap_type_row(current_right_prime: int, gap_index: int | None = None) -> dict[str, object]:
    """Classify the exact winner in the next gap after one current right prime."""
    profile = gwr_next_gap_profile(current_right_prime)
    winner_d = profile["winner_d"]
    winner_offset = profile["winner_offset"]
    if winner_d is None or winner_offset is None:
        raise ValueError(f"gap after {current_right_prime} has no interior winner")

    winner_d = int(winner_d)
    winner_offset = int(winner_offset)
    winner = current_right_prime + winner_offset
    residue = current_right_prime % 30
    first_open = first_open_offset(residue)
    family = carrier_family(winner, winner_d)

    return {
        "gap_index": gap_index,
        "current_right_prime": current_right_prime,
        "residue_mod30": residue,
        "first_open_offset": first_open,
        "next_right_prime": int(profile["next_prime"]),
        "next_gap_width": int(profile["gap_boundary_offset"]),
        "winner": winner,
        "next_dmin": winner_d,
        "next_peak_offset": winner_offset,
        "carrier_family": family,
        "type_key": type_key(first_open, winner_d, winner_offset, family),
    }


def type_rows(max_right_prime: int) -> list[dict[str, object]]:
    """Return exact gap-type rows up to one current right-prime cutoff."""
    if max_right_prime < 3:
        raise ValueError("max_right_prime must be at least 3")

    rows: list[dict[str, object]] = []
    current_right_prime = 3
    gap_index = 1
    while current_right_prime <= max_right_prime:
        row = gap_type_row(current_right_prime, gap_index=gap_index)
        rows.append(row)
        current_right_prime = int(row["next_right_prime"])
        gap_index += 1
    return rows


def distribution(counter: Counter[str], total: int) -> dict[str, dict[str, float | int]]:
    """Convert one counter into count/share payload entries."""
    payload: dict[str, dict[str, float | int]] = {}
    for key in CARRIER_FAMILIES:
        count = int(counter.get(key, 0))
        payload[key] = {
            "count": count,
            "share": count / total if total else 0.0,
        }
    return payload


def exact_type_summary(
    counter: Counter[tuple[int, int, int, str]],
    total: int,
    limit: int = 20,
) -> list[dict[str, object]]:
    """Return the leading exact gap types on the tested surface."""
    rows: list[dict[str, object]] = []
    for signature, count in counter.most_common(limit):
        first_open, winner_d, winner_offset, family = signature
        rows.append(
            {
                "type_key": type_key(first_open, winner_d, winner_offset, family),
                "first_open_offset": first_open,
                "next_dmin": winner_d,
                "next_peak_offset": winner_offset,
                "carrier_family": family,
                "count": int(count),
                "share": count / total,
            }
        )
    return rows


def multifamily_gap_width_examples(rows: list[dict[str, object]], limit: int = 12) -> list[dict[str, object]]:
    """Return small examples where one gap width splits across carrier families."""
    by_width: dict[int, dict[str, dict[str, object]]] = defaultdict(dict)
    for row in rows:
        width = int(row["next_gap_width"])
        family = str(row["carrier_family"])
        if family in by_width[width]:
            continue
        by_width[width][family] = {
            "carrier_family": family,
            "current_right_prime": int(row["current_right_prime"]),
            "winner": int(row["winner"]),
            "next_dmin": int(row["next_dmin"]),
            "next_peak_offset": int(row["next_peak_offset"]),
        }

    examples: list[dict[str, object]] = []
    for width in sorted(by_width):
        family_map = by_width[width]
        if len(family_map) < 2:
            continue
        examples.append(
            {
                "gap_width": width,
                "carrier_family_count": len(family_map),
                "carrier_families": list(family_map.keys()),
                "examples": list(family_map.values()),
            }
        )
        if len(examples) >= limit:
            break
    return examples


def summarize_rows(rows: list[dict[str, object]]) -> dict[str, object]:
    """Aggregate exact gap-type rows into deterministic summary artifacts."""
    if not rows:
        raise ValueError("rows must not be empty")

    family_counter = Counter(str(row["carrier_family"]) for row in rows)
    type_counter = Counter(
        (
            int(row["first_open_offset"]),
            int(row["next_dmin"]),
            int(row["next_peak_offset"]),
            str(row["carrier_family"]),
        )
        for row in rows
    )
    width_to_family_count: dict[str, int] = {}
    width_family_support: dict[int, set[str]] = defaultdict(set)
    first_open_family: dict[int, Counter[str]] = defaultdict(Counter)
    peak_offset_le_share: dict[str, float] = {}
    for row in rows:
        width_family_support[int(row["next_gap_width"])].add(str(row["carrier_family"]))
        first_open_family[int(row["first_open_offset"])][str(row["carrier_family"])] += 1
    for cutoff in PEAK_OFFSET_CUTOFFS:
        peak_offset_le_share[str(cutoff)] = (
            sum(int(int(row["next_peak_offset"]) <= cutoff) for row in rows) / len(rows)
        )
    for width in sorted(width_family_support):
        width_to_family_count[str(width)] = len(width_family_support[width])

    first_open_payload: dict[str, dict[str, dict[str, float | int]]] = {}
    for first_open in sorted(first_open_family):
        total = sum(first_open_family[first_open].values())
        first_open_payload[str(first_open)] = distribution(first_open_family[first_open], total)

    return {
        "max_right_prime": int(rows[-1]["current_right_prime"]),
        "gap_count": len(rows),
        "winner_offset_le_share": peak_offset_le_share,
        "carrier_family_distribution": distribution(family_counter, len(rows)),
        "distinct_carrier_family_count": len([family for family in CARRIER_FAMILIES if family_counter[family] > 0]),
        "distinct_exact_type_count": len(type_counter),
        "top_exact_types": exact_type_summary(type_counter, len(rows)),
        "first_open_offset_to_carrier_family": first_open_payload,
        "distinct_gap_width_count": len(width_family_support),
        "gap_width_to_carrier_family_count": width_to_family_count,
        "multifamily_gap_width_count": sum(
            int(len(families) >= 2) for families in width_family_support.values()
        ),
        "multifamily_gap_width_examples": multifamily_gap_width_examples(rows),
    }


def main(argv: list[str] | None = None) -> int:
    """Run the exact gap-type probe and write JSON plus CSV artifacts."""
    args = build_parser().parse_args(argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    started = time.perf_counter()
    rows = type_rows(args.max_right_prime)
    summary = summarize_rows(rows)
    summary["runtime_seconds"] = time.perf_counter() - started

    summary_path = args.output_dir / "gwr_dni_gap_type_probe_summary.json"
    detail_path = args.output_dir / "gwr_dni_gap_type_probe_details.csv"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    fieldnames = [
        "gap_index",
        "current_right_prime",
        "residue_mod30",
        "first_open_offset",
        "next_right_prime",
        "next_gap_width",
        "winner",
        "next_dmin",
        "next_peak_offset",
        "carrier_family",
        "type_key",
    ]
    with detail_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
