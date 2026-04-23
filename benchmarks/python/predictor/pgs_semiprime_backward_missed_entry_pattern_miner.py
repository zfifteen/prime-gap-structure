#!/usr/bin/env python3
"""Mine exact missed-entry switch patterns for the current refined backward lane law."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = ROOT / "src" / "python"
PREDICTOR_DIR = Path(__file__).resolve().parent
for path in (SOURCE_DIR, PREDICTOR_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import pgs_semiprime_backward_law_search as lane_base
import pgs_semiprime_backward_refined_transition_law_search as refined_base


DEFAULT_OUTPUT_DIR = ROOT / "output" / "semiprime_branch"
DEFAULT_MAX_N = 5_000
SUMMARY_FILENAME = "pgs_semiprime_backward_missed_entry_pattern_miner_summary.json"
TARGET_REFINED_LAW = "containing_if_prev_early_largegap_14"


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description="Mine exact missed-entry switch patterns for the current refined backward lane law.",
    )
    parser.add_argument(
        "--max-n",
        type=int,
        default=DEFAULT_MAX_N,
        help="Largest odd distinct semiprime N included in the toy corpus.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for the mined summary JSON artifact.",
    )
    return parser


def candidate_shape(candidate: dict[str, object]) -> tuple[object, ...]:
    """Return one exact JSON-safe PGS entry shape key."""
    return (
        str(candidate["role"]),
        bool(candidate["is_gwr_winner"]),
        bool(candidate["is_first_d4"]),
        int(candidate["gap_width"]),
        int(candidate["offset"]),
    )


def shape_key(shape: tuple[object, ...]) -> list[object]:
    """Convert one shape tuple into a JSON-safe list."""
    return list(shape)


def mine_missed_patterns(max_n: int) -> dict[str, object]:
    """Return the exact missed-entry switch surface for the current refined law."""
    corpus = lane_base.generate_toy_corpus(max_n)
    immediate_good_entry_count = 0
    missed_good_entry_count = 0
    selected_shape_counts: Counter = Counter()
    good_shape_counts: Counter = Counter()
    switch_stats: dict[tuple[object, ...], dict[tuple[object, ...], dict[str, object]]] = defaultdict(dict)

    for modulus in corpus:
        left_factor, right_factor = lane_base.factor_pair(modulus)
        summary = lane_base.orient_anchor(modulus)
        candidates = lane_base.build_candidate_pool(summary, modulus, {modulus})
        odd_candidates = [candidate for candidate in candidates if str(candidate["kind"]) == "odd_semiprime"]
        good_candidates = [
            candidate
            for candidate in odd_candidates
            if lane_base.odd_candidate_lane_factors(candidate, left_factor, right_factor)
        ]
        if not good_candidates:
            continue
        immediate_good_entry_count += 1

        selected = refined_base.select_entry_candidate(TARGET_REFINED_LAW, odd_candidates)
        if lane_base.odd_candidate_lane_factors(selected, left_factor, right_factor):
            continue

        missed_good_entry_count += 1
        selected_shape = candidate_shape(selected)
        selected_shape_counts[selected_shape] += 1
        for good_candidate in good_candidates:
            good_shape_counts[candidate_shape(good_candidate)] += 1

        alternative_shapes = {
            candidate_shape(candidate)
            for candidate in odd_candidates
            if candidate_shape(candidate) != selected_shape
        }
        for alternative_shape in sorted(alternative_shapes):
            matching_candidates = [
                candidate for candidate in odd_candidates if candidate_shape(candidate) == alternative_shape
            ]
            if not matching_candidates:
                continue
            chosen = min(matching_candidates, key=lambda candidate: int(candidate["n"]))
            bucket = switch_stats[selected_shape].setdefault(
                alternative_shape,
                {
                    "available_count": 0,
                    "alt_lane_success_count": 0,
                    "example_moduli": [],
                },
            )
            bucket["available_count"] = int(bucket["available_count"]) + 1
            if lane_base.odd_candidate_lane_factors(chosen, left_factor, right_factor):
                bucket["alt_lane_success_count"] = int(bucket["alt_lane_success_count"]) + 1
                if len(bucket["example_moduli"]) < 5:
                    bucket["example_moduli"].append(modulus)

    top_switch_rows: list[dict[str, object]] = []
    for selected_shape, alternatives in switch_stats.items():
        for alternative_shape, stats in alternatives.items():
            alt_lane_success_count = int(stats["alt_lane_success_count"])
            if alt_lane_success_count == 0:
                continue
            top_switch_rows.append(
                {
                    "selected_shape": shape_key(selected_shape),
                    "alternative_shape": shape_key(alternative_shape),
                    "available_count": int(stats["available_count"]),
                    "alt_lane_success_count": alt_lane_success_count,
                    "example_moduli": list(stats["example_moduli"]),
                }
            )
    top_switch_rows.sort(
        key=lambda row: (
            -int(row["alt_lane_success_count"]),
            -int(row["available_count"]),
            row["selected_shape"],
            row["alternative_shape"],
        )
    )

    return {
        "max_n": max_n,
        "case_count": len(corpus),
        "target_refined_law": TARGET_REFINED_LAW,
        "immediate_good_entry_count": immediate_good_entry_count,
        "missed_good_entry_count": missed_good_entry_count,
        "selected_shape_counts": [
            {"shape": shape_key(shape), "count": count}
            for shape, count in selected_shape_counts.most_common(12)
        ],
        "good_shape_counts": [
            {"shape": shape_key(shape), "count": count}
            for shape, count in good_shape_counts.most_common(12)
        ],
        "top_switch_rows": top_switch_rows[:12],
    }


def main(argv: list[str] | None = None) -> int:
    """Run the missed-entry miner and emit its summary JSON."""
    parser = build_parser()
    args = parser.parse_args(argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    summary = mine_missed_patterns(max_n=args.max_n)
    summary_path = args.output_dir / SUMMARY_FILENAME
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
