#!/usr/bin/env python3
"""Mine top one-step and two-step backward lane patterns on the toy semiprime surface."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = ROOT / "src" / "python"
PREDICTOR_DIR = Path(__file__).resolve().parent
for path in (SOURCE_DIR, PREDICTOR_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import pgs_semiprime_backward_law_search as lane_base
import pgs_semiprime_backward_transition_law_search as one_step
import pgs_semiprime_backward_two_step_transition_law_search as two_step


DEFAULT_OUTPUT_DIR = ROOT / "output" / "semiprime_branch"
DEFAULT_MAX_N = 5_000
SUMMARY_FILENAME = "pgs_semiprime_backward_pattern_miner_summary.json"


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description="Mine top one-step and two-step backward lane patterns on the toy semiprime surface.",
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


def compact_top(counter: Counter, limit: int = 10) -> list[dict[str, object]]:
    """Return one JSON-safe top-k list from a Counter."""
    rows: list[dict[str, object]] = []
    for key, count in counter.most_common(limit):
        rows.append({"key": list(key) if isinstance(key, tuple) else key, "count": count})
    return rows


def law_pattern_summary(
    module,
    law_id: str,
    corpus: list[int],
) -> dict[str, object]:
    """Return the mined pattern summary for one concrete law on one surface."""
    success_sequences: Counter = Counter()
    failure_endings: Counter = Counter()
    closure_contexts: Counter = Counter()
    miss_entry_patterns: Counter = Counter()
    immediate_good_entry_cases = 0

    for modulus in corpus:
        left_factor, right_factor = lane_base.factor_pair(modulus)
        trace = module.run_case(law_id, modulus, max_steps=24)
        final_row = trace[-1]
        sequence = tuple(
            (
                row.get("phase"),
                row.get("selected_kind"),
                row.get("selected_role"),
                row.get("stop_reason"),
            )
            for row in trace
        )
        if bool(final_row["lane_success"]):
            success_sequences[sequence] += 1
            if final_row.get("phase") == "closure":
                closure_contexts[
                    (
                        final_row.get("selected_boundary_kind"),
                        final_row.get("selected_role"),
                        final_row.get("prev_role_1") or final_row.get("previous_role"),
                        final_row.get("prev_offset_class_1") or final_row.get("previous_offset_class"),
                    )
                ] += 1
        else:
            failure_endings[
                (
                    final_row.get("phase"),
                    final_row.get("stop_reason"),
                    final_row.get("selected_kind"),
                    final_row.get("selected_role"),
                )
            ] += 1

        summary = lane_base.orient_anchor(modulus)
        candidates = lane_base.build_candidate_pool(summary, modulus, {modulus})
        odd_candidates = [candidate for candidate in candidates if str(candidate["kind"]) == "odd_semiprime"]
        if not odd_candidates:
            continue
        good_candidates = [
            candidate
            for candidate in odd_candidates
            if lane_base.odd_candidate_lane_factors(candidate, left_factor, right_factor)
        ]
        if good_candidates:
            immediate_good_entry_cases += 1

        selected_anchor = trace[0]["selected_anchor"]
        if selected_anchor is None:
            continue
        selected_entry = next(
            (candidate for candidate in odd_candidates if int(candidate["n"]) == int(selected_anchor)),
            None,
        )
        if selected_entry is None:
            continue
        if not lane_base.odd_candidate_lane_factors(selected_entry, left_factor, right_factor):
            miss_entry_patterns[
                (
                    selected_entry["role"],
                    bool(selected_entry["is_gwr_winner"]),
                    bool(selected_entry["is_first_d4"]),
                    int(selected_entry["gap_width"]),
                    int(selected_entry["offset"]),
                )
            ] += 1

    return {
        "law_id": law_id,
        "success_sequences": compact_top(success_sequences),
        "failure_endings": compact_top(failure_endings),
        "closure_contexts": compact_top(closure_contexts),
        "miss_entry_patterns": compact_top(miss_entry_patterns),
        "immediate_good_entry_case_count": immediate_good_entry_cases,
    }


def mine_patterns(max_n: int) -> dict[str, object]:
    """Return the full pattern-miner summary for the current best one-step and two-step laws."""
    corpus = lane_base.generate_toy_corpus(max_n)
    one_step_summary = json.loads(
        (DEFAULT_OUTPUT_DIR / one_step.SUMMARY_FILENAME).read_text(encoding="utf-8")
    )
    two_step_summary = json.loads(
        (DEFAULT_OUTPUT_DIR / two_step.SUMMARY_FILENAME).read_text(encoding="utf-8")
    )
    one_step_best = one_step_summary["best_law"]
    two_step_best = two_step_summary["best_law"]

    immediate_good_entry_cases = 0
    immediate_good_entry_roles: Counter = Counter()
    for modulus in corpus:
        left_factor, right_factor = lane_base.factor_pair(modulus)
        summary = lane_base.orient_anchor(modulus)
        candidates = lane_base.build_candidate_pool(summary, modulus, {modulus})
        good_candidates = [
            candidate
            for candidate in candidates
            if str(candidate["kind"]) == "odd_semiprime"
            and lane_base.odd_candidate_lane_factors(candidate, left_factor, right_factor)
        ]
        if not good_candidates:
            continue
        immediate_good_entry_cases += 1
        for candidate in good_candidates:
            immediate_good_entry_roles[str(candidate["role"])] += 1

    return {
        "max_n": max_n,
        "case_count": len(corpus),
        "one_step_best_law": one_step_best,
        "two_step_best_law": two_step_best,
        "immediate_good_entry_case_count": immediate_good_entry_cases,
        "immediate_good_entry_role_counts": dict(immediate_good_entry_roles),
        "one_step_patterns": law_pattern_summary(one_step, one_step_best, corpus),
        "two_step_patterns": law_pattern_summary(two_step, two_step_best, corpus),
    }


def main(argv: list[str] | None = None) -> int:
    """Run the backward-lane pattern miner and emit its summary JSON."""
    parser = build_parser()
    args = parser.parse_args(argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    summary = mine_patterns(max_n=args.max_n)
    summary_path = args.output_dir / SUMMARY_FILENAME
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
