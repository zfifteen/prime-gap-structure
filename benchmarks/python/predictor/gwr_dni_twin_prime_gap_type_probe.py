#!/usr/bin/env python3
"""Probe outer GWR/DNI gap types around exact twin-prime pairs."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import sys
import time
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = ROOT / "src" / "python"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

DEFAULT_OUTPUT_DIR = ROOT / "output"
DEFAULT_MAX_RIGHT_PRIME = 1_000_000
LEFT_TWIN_RESIDUES = (11, 17, 29)
RIGHT_TWIN_RESIDUES = (1, 13, 19)
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
        description="Probe outer gap types around exact twin-prime pairs.",
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
        help="Largest current right-end prime included in the exact type surface.",
    )
    return parser


def type_surface(max_right_prime: int) -> tuple[list[dict[str, object]], dict[int, dict[str, object]], dict[int, dict[str, object]]]:
    """Return exact type rows plus preceding-gap lookup by prime."""
    rows = GAP_TYPE_PROBE.type_rows(max_right_prime)
    by_prime = {int(row["current_right_prime"]): row for row in rows}
    pre_by_prime: dict[int, dict[str, object]] = {}
    previous_gap = None
    for prime_value in sorted(by_prime):
        if previous_gap is not None:
            pre_by_prime[prime_value] = previous_gap
        previous_gap = by_prime[prime_value]
    return rows, by_prime, pre_by_prime


def exact_type_rows(max_right_prime: int) -> dict[str, list[dict[str, object]]]:
    """Return exact twin and baseline rows on one shared exact surface."""
    surface_rows, by_prime, pre_by_prime = type_surface(max_right_prime)
    all_primes = sorted(by_prime)

    all_following_rows = [
        {
            "prime": prime_value,
            "residue_mod30": prime_value % 30,
            "carrier_family": str(by_prime[prime_value]["carrier_family"]),
            "type_key": str(by_prime[prime_value]["type_key"]),
        }
        for prime_value in all_primes
    ]
    all_preceding_rows = [
        {
            "prime": prime_value,
            "residue_mod30": prime_value % 30,
            "carrier_family": str(pre_by_prime[prime_value]["carrier_family"]),
            "type_key": str(pre_by_prime[prime_value]["type_key"]),
        }
        for prime_value in all_primes
        if prime_value in pre_by_prime
    ]

    twin_pair_rows: list[dict[str, object]] = []
    for index, left_prime in enumerate(all_primes[:-1]):
        right_prime = all_primes[index + 1]
        if right_prime - left_prime != 2:
            continue

        preceding_gap = pre_by_prime.get(left_prime)
        following_gap = by_prime[right_prime]
        twin_pair_rows.append(
            {
                "left_prime": left_prime,
                "right_prime": right_prime,
                "left_residue_mod30": left_prime % 30,
                "right_residue_mod30": right_prime % 30,
                "preceding_type_key": (
                    None if preceding_gap is None else str(preceding_gap["type_key"])
                ),
                "preceding_family": (
                    None if preceding_gap is None else str(preceding_gap["carrier_family"])
                ),
                "preceding_gap_width": (
                    None if preceding_gap is None else int(preceding_gap["next_gap_width"])
                ),
                "following_type_key": str(following_gap["type_key"]),
                "following_family": str(following_gap["carrier_family"]),
                "following_gap_width": int(following_gap["next_gap_width"]),
                "same_outer_family": (
                    None
                    if preceding_gap is None
                    else str(preceding_gap["carrier_family"]) == str(following_gap["carrier_family"])
                ),
            }
        )

    twin_preceding_rows = [
        {
            "prime": int(row["left_prime"]),
            "residue_mod30": int(row["left_residue_mod30"]),
            "carrier_family": str(row["preceding_family"]),
            "type_key": str(row["preceding_type_key"]),
        }
        for row in twin_pair_rows
        if row["preceding_type_key"] is not None
    ]
    twin_following_rows = [
        {
            "prime": int(row["right_prime"]),
            "residue_mod30": int(row["right_residue_mod30"]),
            "carrier_family": str(row["following_family"]),
            "type_key": str(row["following_type_key"]),
        }
        for row in twin_pair_rows
    ]

    return {
        "surface_rows": surface_rows,
        "all_preceding_rows": all_preceding_rows,
        "all_following_rows": all_following_rows,
        "twin_pair_rows": twin_pair_rows,
        "twin_preceding_rows": twin_preceding_rows,
        "twin_following_rows": twin_following_rows,
    }


def family_comparison(
    twin_rows: list[dict[str, object]],
    baseline_rows: list[dict[str, object]],
) -> dict[str, dict[str, float | int | None]]:
    """Compare one twin-family distribution to one residue-conditioned baseline."""
    twin_counter = Counter(str(row["carrier_family"]) for row in twin_rows)
    baseline_counter = Counter(str(row["carrier_family"]) for row in baseline_rows)
    twin_total = len(twin_rows)
    baseline_total = len(baseline_rows)

    comparison: dict[str, dict[str, float | int | None]] = {}
    for family in CARRIER_FAMILIES:
        twin_count = int(twin_counter.get(family, 0))
        baseline_count = int(baseline_counter.get(family, 0))
        twin_share = twin_count / twin_total if twin_total else 0.0
        baseline_share = baseline_count / baseline_total if baseline_total else 0.0
        comparison[family] = {
            "twin_count": twin_count,
            "twin_share": twin_share,
            "baseline_count": baseline_count,
            "baseline_share": baseline_share,
            "share_delta": twin_share - baseline_share,
            "lift": (twin_share / baseline_share) if baseline_share else None,
        }
    return comparison


def summarize_rows(row_bundle: dict[str, list[dict[str, object]]], max_right_prime: int) -> dict[str, object]:
    """Aggregate the twin-pair surface into one summary payload."""
    twin_pair_rows = row_bundle["twin_pair_rows"]
    twin_preceding_rows = row_bundle["twin_preceding_rows"]
    twin_following_rows = row_bundle["twin_following_rows"]
    all_preceding_rows = row_bundle["all_preceding_rows"]
    all_following_rows = row_bundle["all_following_rows"]

    if not twin_pair_rows:
        raise ValueError("twin_pair_rows must not be empty")

    residue_conditioned_preceding = [
        row
        for row in all_preceding_rows
        if int(row["residue_mod30"]) in LEFT_TWIN_RESIDUES
    ]
    residue_conditioned_following = [
        row
        for row in all_following_rows
        if int(row["residue_mod30"]) in RIGHT_TWIN_RESIDUES
    ]

    pair_signature_counter = Counter(
        (
            str(row["preceding_type_key"]),
            str(row["following_type_key"]),
        )
        for row in twin_pair_rows
        if row["preceding_type_key"] is not None
    )
    preceding_type_counter = Counter(str(row["type_key"]) for row in twin_preceding_rows)
    following_type_counter = Counter(str(row["type_key"]) for row in twin_following_rows)

    return {
        "max_right_prime": max_right_prime,
        "surface_prime_count": len(row_bundle["surface_rows"]),
        "twin_pair_count": len(twin_pair_rows),
        "defined_preceding_twin_pair_count": len(twin_preceding_rows),
        "left_twin_residues_mod30": list(LEFT_TWIN_RESIDUES),
        "right_twin_residues_mod30": list(RIGHT_TWIN_RESIDUES),
        "preceding_family_vs_residue_baseline": family_comparison(
            twin_preceding_rows,
            residue_conditioned_preceding,
        ),
        "following_family_vs_residue_baseline": family_comparison(
            twin_following_rows,
            residue_conditioned_following,
        ),
        "distinct_preceding_type_count": len(preceding_type_counter),
        "distinct_following_type_count": len(following_type_counter),
        "distinct_outer_pair_signature_count": len(pair_signature_counter),
        "top_preceding_types": [
            {"type_key": key, "count": int(value), "share": value / len(twin_preceding_rows)}
            for key, value in preceding_type_counter.most_common(12)
        ],
        "top_following_types": [
            {"type_key": key, "count": int(value), "share": value / len(twin_following_rows)}
            for key, value in following_type_counter.most_common(12)
        ],
        "top_outer_pair_signatures": [
            {
                "preceding_type_key": preceding_key,
                "following_type_key": following_key,
                "count": int(value),
                "share": value / len(twin_preceding_rows),
            }
            for (preceding_key, following_key), value in pair_signature_counter.most_common(12)
        ],
        "same_outer_family_share": (
            sum(int(bool(row["same_outer_family"])) for row in twin_pair_rows if row["same_outer_family"] is not None)
            / len(twin_preceding_rows)
        ),
    }


def main(argv: list[str] | None = None) -> int:
    """Run the twin-prime probe and write JSON plus CSV artifacts."""
    args = build_parser().parse_args(argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    started = time.perf_counter()
    row_bundle = exact_type_rows(args.max_right_prime)
    summary = summarize_rows(row_bundle, max_right_prime=args.max_right_prime)
    summary["runtime_seconds"] = time.perf_counter() - started

    summary_path = args.output_dir / "gwr_dni_twin_prime_gap_type_probe_summary.json"
    detail_path = args.output_dir / "gwr_dni_twin_prime_gap_type_probe_details.csv"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    fieldnames = [
        "left_prime",
        "right_prime",
        "left_residue_mod30",
        "right_residue_mod30",
        "preceding_type_key",
        "preceding_family",
        "preceding_gap_width",
        "following_type_key",
        "following_family",
        "following_gap_width",
        "same_outer_family",
    ]
    with detail_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(row_bundle["twin_pair_rows"])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
