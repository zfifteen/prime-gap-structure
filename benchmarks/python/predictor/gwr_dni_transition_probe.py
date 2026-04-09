#!/usr/bin/env python3
"""Probe which deterministic DNI state controls the immediate next gap."""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

from sympy import nextprime


ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = ROOT / "src" / "python"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from z_band_prime_composite_field import divisor_counts_segment
from z_band_prime_predictor import W_d, divisor_gap_profile, gap_dmin

DEFAULT_OUTPUT_DIR = ROOT / "output"
DEFAULT_MAX_RIGHT_PRIME = 1_000_000
PREFIX_OFFSETS = tuple(range(1, 13))
PREFIX_SIGNATURE_CUTOFFS = (2, 4, 6, 8, 10, 12)


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description="Probe immediate next-gap DNI transition structure.",
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
        help="Largest current right-end prime q included in the transition probe.",
    )
    return parser


def first_open_offset(residue: int) -> int:
    """Return the first even offset after one residue whose class is open mod 30."""
    for offset in (2, 4, 6, 8, 10, 12):
        candidate = (residue + offset) % 30
        if candidate % 3 != 0 and candidate % 5 != 0:
            return offset
    raise RuntimeError(f"no wheel-open offset found for residue {residue}")


def state_signature(row: dict[str, object], keys: tuple[str, ...]) -> tuple[object, ...]:
    """Return one deterministic state signature for one configured key bundle."""
    return tuple(row[key] for key in keys)


def analyze_bundle(rows: list[dict[str, object]], keys: tuple[str, ...]) -> dict[str, object]:
    """Measure how tightly one state bundle constrains the next-gap DNI state."""
    support: dict[tuple[object, ...], Counter[tuple[object, object]]] = defaultdict(Counter)
    for row in rows:
        if row["next_gap_empty"]:
            target = ("empty", None)
        else:
            target = (row["next_dmin"], row["next_peak_offset"])
        support[state_signature(row, keys)][target] += 1

    unique_state_count = 0
    unique_observation_count = 0
    max_support_size = 0
    for counter in support.values():
        support_size = len(counter)
        max_support_size = max(max_support_size, support_size)
        if support_size == 1:
            unique_state_count += 1
            unique_observation_count += sum(counter.values())

    total_observations = len(rows)
    return {
        "state_keys": list(keys),
        "distinct_state_count": len(support),
        "unique_state_count": unique_state_count,
        "unique_state_rate": unique_state_count / len(support),
        "unique_observation_count": unique_observation_count,
        "unique_observation_share": unique_observation_count / total_observations,
        "max_target_support_size": max_support_size,
    }


def transition_rows(max_right_prime: int) -> list[dict[str, object]]:
    """Build deterministic current-gap to next-gap DNI transition rows."""
    if max_right_prime < 5:
        raise ValueError("max_right_prime must be at least 5")

    rows: list[dict[str, object]] = []
    left_prime = 2
    current_right_prime = 3
    gap_index = 1
    while current_right_prime <= max_right_prime:
        next_right_prime = int(nextprime(current_right_prime))
        current_gap_width = current_right_prime - left_prime
        current_dmin = gap_dmin(left_prime, current_right_prime)
        current_peak_offset = None
        if current_dmin is not None:
            current_profile = divisor_gap_profile(left_prime, current_right_prime, int(current_dmin))
            current_peak_offset = int(current_profile["first_in_gap_carrier"]) - left_prime

        next_gap_width = next_right_prime - current_right_prime
        next_dmin = gap_dmin(current_right_prime, next_right_prime)
        next_gap_empty = next_dmin is None
        next_peak_offset = None
        oracle_witness = None
        oracle_exact = None
        if next_dmin is not None:
            next_profile = divisor_gap_profile(current_right_prime, next_right_prime, int(next_dmin))
            next_peak_offset = int(next_profile["first_in_gap_carrier"]) - current_right_prime
            oracle_witness = W_d(current_right_prime, int(next_dmin), stop_exclusive=next_right_prime)
            oracle_exact = int(nextprime(oracle_witness - 1)) == next_right_prime

        residue_mod30 = current_right_prime % 30
        prefix_hi = min(next_right_prime, current_right_prime + len(PREFIX_OFFSETS) + 1)
        prefix_counts = divisor_counts_segment(current_right_prime + 1, prefix_hi)
        prefix_map = {
            f"prefix_d_{offset}": (
                int(prefix_counts[offset - 1]) if offset <= len(prefix_counts) else None
            )
            for offset in PREFIX_OFFSETS
        }
        rows.append(
            {
                "gap_index": gap_index,
                "current_left_prime": left_prime,
                "current_right_prime": current_right_prime,
                "current_gap_width": current_gap_width,
                "current_dmin": current_dmin,
                "current_peak_offset": current_peak_offset,
                "residue_mod30": residue_mod30,
                "first_open_offset": first_open_offset(residue_mod30),
                "next_right_prime": next_right_prime,
                "next_gap_width": next_gap_width,
                "next_gap_empty": next_gap_empty,
                "next_dmin": next_dmin,
                "next_peak_offset": next_peak_offset,
                "oracle_witness": oracle_witness,
                "oracle_exact": oracle_exact,
                **prefix_map,
            }
        )

        left_prime = current_right_prime
        current_right_prime = next_right_prime
        gap_index += 1

    return rows


def summarize_rows(rows: list[dict[str, object]]) -> dict[str, object]:
    """Aggregate transition rows into deterministic DNI-state summaries."""
    if not rows:
        raise ValueError("rows must not be empty")

    nonempty_rows = [row for row in rows if not row["next_gap_empty"]]
    next_dmin_counter = Counter(int(row["next_dmin"]) for row in nonempty_rows)
    peak_offset_shares: dict[str, float] = {}
    prefix_min_match_shares: dict[str, float] = {}
    prefix_peak_exact_shares: dict[str, float] = {}
    for cutoff in (1, 2, 3, 4, 5, 6, 8, 10, 12):
        peak_offset_shares[str(cutoff)] = (
            sum(int(int(row["next_peak_offset"]) <= cutoff) for row in nonempty_rows) / len(nonempty_rows)
        )
        prefix_min_match_count = 0
        prefix_peak_exact_count = 0
        for row in nonempty_rows:
            prefix_values = [
                int(row[f"prefix_d_{offset}"])
                for offset in range(1, cutoff + 1)
                if row[f"prefix_d_{offset}"] is not None
            ]
            if min(prefix_values) == int(row["next_dmin"]):
                prefix_min_match_count += 1
                first_match_offset = next(
                    offset
                    for offset in range(1, cutoff + 1)
                    if row[f"prefix_d_{offset}"] is not None
                    and int(row[f"prefix_d_{offset}"]) == int(row["next_dmin"])
                )
                if first_match_offset == int(row["next_peak_offset"]):
                    prefix_peak_exact_count += 1
        prefix_min_match_shares[str(cutoff)] = prefix_min_match_count / len(nonempty_rows)
        prefix_peak_exact_shares[str(cutoff)] = prefix_peak_exact_count / len(nonempty_rows)
    peak_within_first_open_share = (
        sum(
            int(int(row["next_peak_offset"]) <= int(row["first_open_offset"]))
            for row in nonempty_rows
        )
        / len(nonempty_rows)
    )
    residue_counters: dict[str, dict[str, int]] = {}
    open_offset_counters: dict[str, dict[str, int]] = {}
    for residue in sorted({int(row["residue_mod30"]) for row in rows}):
        counter = Counter(
            "empty" if row["next_gap_empty"] else int(row["next_dmin"])
            for row in rows
            if int(row["residue_mod30"]) == residue
        )
        residue_counters[str(residue)] = {str(key): int(value) for key, value in counter.items()}
    for open_offset in sorted({int(row["first_open_offset"]) for row in rows}):
        counter = Counter(
            "empty" if row["next_gap_empty"] else int(row["next_dmin"])
            for row in rows
            if int(row["first_open_offset"]) == open_offset
        )
        open_offset_counters[str(open_offset)] = {str(key): int(value) for key, value in counter.items()}

    bundle_specs = [
        ("residue_mod30",),
        ("first_open_offset",),
        ("current_dmin",),
        ("residue_mod30", "current_dmin"),
        ("first_open_offset", "current_dmin"),
        ("residue_mod30", "current_gap_width"),
        ("residue_mod30", "current_gap_width", "current_dmin"),
        ("residue_mod30", "current_gap_width", "current_dmin", "current_peak_offset"),
    ]
    for cutoff in PREFIX_SIGNATURE_CUTOFFS:
        prefix_keys = tuple(f"prefix_d_{offset}" for offset in range(1, cutoff + 1))
        bundle_specs.append(("residue_mod30", "first_open_offset", *prefix_keys))
        bundle_specs.append(
            (
                "residue_mod30",
                "current_gap_width",
                "current_dmin",
                "first_open_offset",
                *prefix_keys,
            )
        )

    return {
        "max_right_prime": int(rows[-1]["current_right_prime"]),
        "transition_count": len(rows),
        "nonempty_next_gap_count": len(nonempty_rows),
        "empty_next_gap_count": len(rows) - len(nonempty_rows),
        "empty_next_gap_share": (len(rows) - len(nonempty_rows)) / len(rows),
        "oracle_exact_rate_nonempty": (
            sum(int(bool(row["oracle_exact"])) for row in nonempty_rows) / len(nonempty_rows)
            if nonempty_rows
            else None
        ),
        "next_peak_offset_le_share": peak_offset_shares,
        "prefix_min_match_share": prefix_min_match_shares,
        "prefix_peak_exact_share": prefix_peak_exact_shares,
        "next_peak_within_first_open_share": peak_within_first_open_share,
        "next_dmin_distribution": {str(key): int(value) for key, value in next_dmin_counter.items()},
        "residue_mod30_to_next_dmin": residue_counters,
        "first_open_offset_to_next_dmin": open_offset_counters,
        "bundle_ambiguity": [analyze_bundle(rows, keys) for keys in bundle_specs],
    }


def main(argv: list[str] | None = None) -> int:
    """Run the transition probe and write JSON plus CSV artifacts."""
    args = build_parser().parse_args(argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    started = time.perf_counter()
    rows = transition_rows(args.max_right_prime)
    summary = summarize_rows(rows)
    summary["runtime_seconds"] = time.perf_counter() - started

    summary_path = args.output_dir / "gwr_dni_transition_probe_summary.json"
    detail_path = args.output_dir / "gwr_dni_transition_probe_details.csv"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    fieldnames = [
        "gap_index",
        "current_left_prime",
        "current_right_prime",
        "current_gap_width",
        "current_dmin",
        "current_peak_offset",
        "residue_mod30",
        "first_open_offset",
        "next_right_prime",
        "next_gap_width",
        "next_gap_empty",
        "next_dmin",
        "next_peak_offset",
        "oracle_witness",
        "oracle_exact",
    ]
    fieldnames.extend(f"prefix_d_{offset}" for offset in PREFIX_OFFSETS)
    with detail_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
