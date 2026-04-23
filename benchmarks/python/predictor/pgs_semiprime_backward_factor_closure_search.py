#!/usr/bin/env python3
"""Search pure-PGS factor-closure laws after a fixed backward lane entry precondition."""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = ROOT / "src" / "python"
PREDICTOR_DIR = Path(__file__).resolve().parent
for path in (SOURCE_DIR, PREDICTOR_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import pgs_semiprime_backward_law_search as lane_base
import pgs_semiprime_backward_layered_hybrid_entry_law_search as entry_base


DEFAULT_OUTPUT_DIR = ROOT / "output" / "semiprime_branch"
DEFAULT_MAX_N = 5_000
DEFAULT_MAX_STEPS = 24
SUMMARY_FILENAME = "pgs_semiprime_backward_factor_closure_search_summary.json"
ENTRY_LAW = "layered_hybrid_exact_shape_entry_switch"
CLOSURE_LAW_ORDER = (
    "prime_left_boundary_control",
    "prime_prev_boundary_control",
    "odd_prev_small_gap_then_left_prime",
    "odd_prev_large_offset_then_left_prime",
    "odd_prev_winner_then_left_prime",
    "odd_containing_large_offset_then_left_prime",
)


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description="Search pure-PGS factor-closure laws after a fixed backward lane entry precondition.",
    )
    parser.add_argument(
        "--max-n",
        type=int,
        default=DEFAULT_MAX_N,
        help="Largest odd distinct semiprime N included in the toy corpus.",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=DEFAULT_MAX_STEPS,
        help="Maximum closure steps per modulus after the fixed entry step.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for the summary JSON artifact.",
    )
    return parser


def _candidate_rank(law_id: str, candidate: dict[str, object]) -> tuple[object, ...]:
    """Return the exact ranking key for one closure candidate under one law."""
    kind = str(candidate["kind"])
    role = str(candidate["role"])
    gap_width = int(candidate["gap_width"])
    offset = 10**9 if candidate["offset"] is None else int(candidate["offset"])
    boundary_kind = candidate["boundary_kind"]

    if law_id == "prime_left_boundary_control":
        return (
            0 if kind == "prime_boundary" and boundary_kind == "p_left" else 1,
            0 if kind == "prime_boundary" and boundary_kind == "p_prev" else 1,
            0 if kind == "odd_semiprime" else 1,
            gap_width,
            -offset,
            int(candidate["n"]),
        )
    if law_id == "prime_prev_boundary_control":
        return (
            0 if kind == "prime_boundary" and boundary_kind == "p_prev" else 1,
            0 if kind == "prime_boundary" and boundary_kind == "p_left" else 1,
            0 if kind == "odd_semiprime" else 1,
            gap_width,
            -offset,
            int(candidate["n"]),
        )
    if law_id == "odd_prev_small_gap_then_left_prime":
        return (
            0 if kind == "odd_semiprime" and role == "previous" else 1,
            gap_width,
            0 if bool(candidate["is_first_d4"]) else 1,
            -offset,
            0 if kind == "prime_boundary" and boundary_kind == "p_left" else 1,
            0 if kind == "prime_boundary" and boundary_kind == "p_prev" else 1,
            int(candidate["n"]),
        )
    if law_id == "odd_prev_large_offset_then_left_prime":
        return (
            0 if kind == "odd_semiprime" and role == "previous" else 1,
            0 if bool(candidate["is_first_d4"]) else 1,
            -offset,
            gap_width,
            0 if kind == "prime_boundary" and boundary_kind == "p_left" else 1,
            0 if kind == "prime_boundary" and boundary_kind == "p_prev" else 1,
            int(candidate["n"]),
        )
    if law_id == "odd_prev_winner_then_left_prime":
        return (
            0 if kind == "odd_semiprime" and role == "previous" else 1,
            0 if bool(candidate["is_gwr_winner"]) else 1,
            0 if bool(candidate["is_first_d4"]) else 1,
            -offset,
            gap_width,
            0 if kind == "prime_boundary" and boundary_kind == "p_left" else 1,
            0 if kind == "prime_boundary" and boundary_kind == "p_prev" else 1,
            int(candidate["n"]),
        )
    if law_id == "odd_containing_large_offset_then_left_prime":
        return (
            0 if kind == "odd_semiprime" and role == "containing" else 1,
            0 if bool(candidate["is_first_d4"]) else 1,
            -offset,
            gap_width,
            0 if kind == "prime_boundary" and boundary_kind == "p_left" else 1,
            0 if kind == "prime_boundary" and boundary_kind == "p_prev" else 1,
            int(candidate["n"]),
        )
    raise ValueError(f"unknown closure law: {law_id}")


def run_case(law_id: str, modulus: int, max_steps: int) -> list[dict[str, object]]:
    """Run one deterministic factor-closure trace for one modulus."""
    if max_steps < 1:
        raise ValueError("max_steps must be at least 1")

    left_factor, right_factor = lane_base.factor_pair(modulus)
    start_summary = lane_base.orient_anchor(modulus)
    start_candidates = lane_base.build_candidate_pool(start_summary, modulus, {modulus})
    odd_candidates = [candidate for candidate in start_candidates if str(candidate["kind"]) == "odd_semiprime"]

    if not odd_candidates:
        return [
            {
                "law_id": law_id,
                "n": modulus,
                "step": 0,
                "phase": "entry",
                "current_anchor": modulus,
                "selected_anchor": None,
                "selected_kind": None,
                "selected_role": None,
                "factor_reach": False,
                "stop_reason": "no_entry_candidate",
            }
        ]

    entry_candidate = entry_base.select_entry_candidate(ENTRY_LAW, odd_candidates)
    lane_factors = sorted(lane_base.odd_candidate_lane_factors(entry_candidate, left_factor, right_factor))
    if not lane_factors:
        return [
            {
                "law_id": law_id,
                "n": modulus,
                "step": 0,
                "phase": "entry",
                "current_anchor": modulus,
                "selected_anchor": int(entry_candidate["n"]),
                "selected_kind": str(entry_candidate["kind"]),
                "selected_role": str(entry_candidate["role"]),
                "factor_reach": False,
                "stop_reason": "entry_not_lane",
            }
        ]

    lane_factor = int(lane_factors[0])
    current_anchor = int(entry_candidate["n"])
    visited = {modulus, current_anchor}
    trace_rows: list[dict[str, object]] = [
        {
            "law_id": law_id,
            "n": modulus,
            "step": 0,
            "phase": "entry",
            "current_anchor": modulus,
            "selected_anchor": current_anchor,
            "selected_kind": str(entry_candidate["kind"]),
            "selected_role": str(entry_candidate["role"]),
            "lane_factor": lane_factor,
            "factor_reach": False,
            "stop_reason": None,
        }
    ]

    for step in range(1, max_steps + 1):
        summary = lane_base.orient_anchor(current_anchor)
        candidates = lane_base.build_candidate_pool(summary, current_anchor, visited)
        if not candidates:
            trace_rows.append(
                {
                    "law_id": law_id,
                    "n": modulus,
                    "step": step,
                    "phase": "closure",
                    "current_anchor": current_anchor,
                    "selected_anchor": None,
                    "selected_kind": None,
                    "selected_role": None,
                    "lane_factor": lane_factor,
                    "factor_reach": False,
                    "stop_reason": "no_candidate",
                }
            )
            return trace_rows

        selected = min(candidates, key=lambda candidate: _candidate_rank(law_id, candidate))
        selected_kind = str(selected["kind"])
        row = {
            "law_id": law_id,
            "n": modulus,
            "step": step,
            "phase": "closure",
            "current_anchor": current_anchor,
            "selected_anchor": int(selected["n"]),
            "selected_kind": selected_kind,
            "selected_role": str(selected["role"]),
            "lane_factor": lane_factor,
            "factor_reach": False,
            "stop_reason": None,
        }

        if selected_kind == "prime_boundary":
            row["factor_reach"] = int(selected["n"]) in (left_factor, right_factor)
            row["stop_reason"] = "factor_reach_terminal_prime" if row["factor_reach"] else "terminal_prime_miss"
            trace_rows.append(row)
            return trace_rows

        selected_lane_factors = lane_base.odd_candidate_lane_factors(selected, left_factor, right_factor)
        if lane_factor not in selected_lane_factors:
            row["stop_reason"] = "lane_broken"
            trace_rows.append(row)
            return trace_rows

        trace_rows.append(row)
        current_anchor = int(selected["n"])
        visited.add(current_anchor)

    trace_rows.append(
        {
            "law_id": law_id,
            "n": modulus,
            "step": max_steps + 1,
            "phase": "closure",
            "current_anchor": current_anchor,
            "selected_anchor": None,
            "selected_kind": None,
            "selected_role": None,
            "lane_factor": lane_factor,
            "factor_reach": False,
            "stop_reason": "max_steps_exhausted",
        }
    )
    return trace_rows


def summarize_trace(trace_rows: list[dict[str, object]]) -> dict[str, object]:
    """Return the terminal payload for one factor-closure trace."""
    final_row = trace_rows[-1]
    return {
        "entry_lane": trace_rows[0]["stop_reason"] is None,
        "factor_reach": bool(final_row["factor_reach"]),
        "stop_reason": str(final_row["stop_reason"]),
        "step_count": len(trace_rows) - 1,
        "selected_anchor": final_row["selected_anchor"],
    }


def run_search(max_n: int, max_steps: int) -> dict[str, object]:
    """Run the factor-closure law family over the toy corpus."""
    corpus = lane_base.generate_toy_corpus(max_n)
    traces_by_law: dict[str, list[dict[str, object]]] = {law_id: [] for law_id in CLOSURE_LAW_ORDER}

    for law_id in CLOSURE_LAW_ORDER:
        for modulus in corpus:
            trace = run_case(law_id, modulus, max_steps=max_steps)
            traces_by_law[law_id].append(summarize_trace(trace))

    law_summaries: dict[str, dict[str, object]] = {}
    best_law = CLOSURE_LAW_ORDER[0]
    best_factor_reach_count = -1
    entry_lane_count = 0
    if CLOSURE_LAW_ORDER:
        entry_lane_count = sum(int(bool(item["entry_lane"])) for item in traces_by_law[CLOSURE_LAW_ORDER[0]])

    for law_id in CLOSURE_LAW_ORDER:
        traces = traces_by_law[law_id]
        factor_reach_count = sum(int(bool(item["factor_reach"])) for item in traces)
        factor_steps = [int(item["step_count"]) for item in traces if bool(item["factor_reach"])]
        failure_reason_counts: dict[str, int] = {}
        for item in traces:
            if bool(item["factor_reach"]):
                continue
            stop_reason = str(item["stop_reason"])
            failure_reason_counts[stop_reason] = failure_reason_counts.get(stop_reason, 0) + 1
        first_factor_case = next(
            (int(corpus[index]) for index, item in enumerate(traces) if bool(item["factor_reach"])),
            None,
        )
        law_summaries[law_id] = {
            "factor_reach_count": factor_reach_count,
            "factor_reach_recall": (factor_reach_count / len(corpus)) if corpus else 0.0,
            "first_factor_case": first_factor_case,
            "median_steps_on_factor_reach": (
                float(statistics.median(factor_steps)) if factor_steps else None
            ),
            "failure_reason_counts": failure_reason_counts,
        }
        if factor_reach_count > best_factor_reach_count:
            best_factor_reach_count = factor_reach_count
            best_law = law_id

    return {
        "max_n": max_n,
        "case_count": len(corpus),
        "max_steps": max_steps,
        "fixed_entry_law": ENTRY_LAW,
        "entry_lane_count": entry_lane_count,
        "closure_law_summaries": law_summaries,
        "best_law": best_law,
        "best_factor_reach_count": max(best_factor_reach_count, 0),
        "searched_family_falsified": max(best_factor_reach_count, 0) == 0,
    }


def main(argv: list[str] | None = None) -> int:
    """Run the factor-closure search and emit its summary JSON."""
    parser = build_parser()
    args = parser.parse_args(argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    summary = run_search(max_n=args.max_n, max_steps=args.max_steps)
    summary_path = args.output_dir / SUMMARY_FILENAME
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
