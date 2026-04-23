#!/usr/bin/env python3
"""Search one tighter pure-PGS exact-shape entry-switch family on the toy semiprime lane surface."""

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
import pgs_semiprime_backward_refined_transition_law_search as refined_base


DEFAULT_OUTPUT_DIR = ROOT / "output" / "semiprime_branch"
DEFAULT_MAX_N = 5_000
DEFAULT_MAX_STEPS = 24
SUMMARY_FILENAME = "pgs_semiprime_backward_tighter_entry_law_search_summary.json"
LAW_ORDER = (
    "baseline_containing_if_prev_early_largegap_14",
    "exact_shape_entry_switch",
)
EXACT_SWITCH_MAP = {
    ("previous", True, True, 8, 2): ("previous", False, False, 8, 4),
    ("previous", True, True, 10, 4): ("previous", False, False, 10, 8),
    ("previous", True, True, 12, 4): ("previous", False, False, 12, 8),
    ("previous", True, True, 14, 2): ("previous", False, False, 14, 10),
    ("containing", True, True, 14, 2): ("containing", False, False, 14, 4),
    ("containing", True, True, 22, 4): ("containing", False, False, 22, 6),
    ("containing", True, True, 26, 2): ("containing", False, False, 26, 10),
}
BASELINE_LAW = "containing_if_prev_early_largegap_14"


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description="Search one tighter pure-PGS exact-shape entry-switch family on the toy semiprime lane surface.",
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
        help="Maximum backward steps per refined transition trace.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for the summary JSON artifact.",
    )
    return parser


def candidate_shape(candidate: dict[str, object]) -> tuple[object, ...]:
    """Return one exact PGS entry shape key."""
    return (
        str(candidate["role"]),
        bool(candidate["is_gwr_winner"]),
        bool(candidate["is_first_d4"]),
        int(candidate["gap_width"]),
        int(candidate["offset"]),
    )


def select_entry_candidate(law_id: str, odd_candidates: list[dict[str, object]]) -> dict[str, object]:
    """Return the selected entry candidate for one tighter law."""
    baseline = refined_base.select_entry_candidate(BASELINE_LAW, odd_candidates)
    if law_id == "baseline_containing_if_prev_early_largegap_14":
        return baseline
    if law_id != "exact_shape_entry_switch":
        raise ValueError(f"unknown law_id: {law_id}")

    target_shape = EXACT_SWITCH_MAP.get(candidate_shape(baseline))
    if target_shape is None:
        return baseline
    matching_candidates = [
        candidate for candidate in odd_candidates if candidate_shape(candidate) == target_shape
    ]
    if not matching_candidates:
        return baseline
    return min(matching_candidates, key=lambda candidate: int(candidate["n"]))


def run_case(law_id: str, modulus: int, max_steps: int) -> list[dict[str, object]]:
    """Run one deterministic tighter entry trace."""
    if max_steps < 1:
        raise ValueError("max_steps must be at least 1")

    left_factor, right_factor = lane_base.factor_pair(modulus)
    trace_rows: list[dict[str, object]] = []
    current_anchor = modulus
    visited = {modulus}
    lane_factor: int | None = None

    for step in range(1, max_steps + 1):
        summary = refined_base.cached_orient_anchor(current_anchor)
        candidates = [
            dict(candidate)
            for candidate in refined_base.cached_candidate_universe(current_anchor)
            if int(candidate["n"]) not in visited and int(candidate["n"]) < current_anchor
        ]
        odd_candidates = [candidate for candidate in candidates if str(candidate["kind"]) == "odd_semiprime"]
        prime_candidates = [candidate for candidate in candidates if str(candidate["kind"]) == "prime_boundary"]

        selected = None
        phase = None
        stop_reason = None
        lane_success = False
        factor_reach = False
        next_lane_factor = lane_factor

        if lane_factor is None:
            phase = "entry"
            if odd_candidates:
                selected = select_entry_candidate(law_id, odd_candidates)
                selected_lane_factors = sorted(
                    lane_base.odd_candidate_lane_factors(selected, left_factor, right_factor)
                )
                if not selected_lane_factors:
                    stop_reason = "not_odd_semiprime_lane"
                else:
                    next_lane_factor = int(selected_lane_factors[0])
            elif prime_candidates:
                selected = refined_base.select_closure_candidate(prime_candidates, lane_factor)
                stop_reason = "terminal_prime_nominee"
                if int(selected["n"]) in (left_factor, right_factor):
                    lane_success = True
                    factor_reach = True
            else:
                stop_reason = "no_candidate"
        else:
            if prime_candidates:
                phase = "closure"
                selected = refined_base.select_closure_candidate(prime_candidates, lane_factor)
                stop_reason = "lane_success_terminal_prime"
                lane_success = True
                if int(selected["n"]) == lane_factor:
                    factor_reach = True
            elif odd_candidates:
                phase = "continuation"
                selected = select_entry_candidate(law_id, odd_candidates)
                selected_lane_factors = sorted(
                    lane_base.odd_candidate_lane_factors(selected, left_factor, right_factor)
                )
                if lane_factor not in selected_lane_factors:
                    stop_reason = "lane_broken"
            else:
                phase = "closure"
                stop_reason = "lane_success_terminal_no_candidate"
                lane_success = True

        selected_lane_factors = (
            []
            if selected is None or str(selected["kind"]) != "odd_semiprime"
            else sorted(lane_base.odd_candidate_lane_factors(selected, left_factor, right_factor))
        )
        row = {
            "law_id": law_id,
            "n": modulus,
            "step": step,
            "phase": phase,
            "current_anchor": current_anchor,
            "selected_anchor": None if selected is None else int(selected["n"]),
            "selected_kind": None if selected is None else str(selected["kind"]),
            "selected_role": None if selected is None else str(selected["role"]),
            "selected_boundary_kind": None if selected is None else selected["boundary_kind"],
            "selected_is_gwr_winner": None if selected is None else bool(selected["is_gwr_winner"]),
            "selected_is_first_d4": None if selected is None else bool(selected["is_first_d4"]),
            "selected_offset": None if selected is None else selected["offset"],
            "selected_gap_width": None if selected is None else int(selected["gap_width"]),
            "selected_lane_factors": selected_lane_factors,
            "candidate_count": len(candidates),
            "odd_candidate_count": len(odd_candidates),
            "prime_candidate_count": len(prime_candidates),
            "lane_factor": next_lane_factor,
            "lane_success": lane_success,
            "factor_reach": factor_reach,
            "stop_reason": stop_reason,
        }
        trace_rows.append(row)

        if stop_reason is not None:
            return trace_rows

        visited.add(int(selected["n"]))
        current_anchor = int(selected["n"])
        lane_factor = next_lane_factor

    trace_rows[-1]["stop_reason"] = "lane_success_exhausted" if lane_factor is not None else "max_steps_exhausted"
    trace_rows[-1]["lane_success"] = lane_factor is not None
    trace_rows[-1]["lane_factor"] = lane_factor
    return trace_rows


def summarize_trace(trace_rows: list[dict[str, object]]) -> dict[str, object]:
    """Return the terminal payload for one tighter trace."""
    final_row = trace_rows[-1]
    return {
        "lane_success": bool(final_row["lane_success"]),
        "factor_reach": bool(final_row["factor_reach"]),
        "stop_reason": str(final_row["stop_reason"]),
        "step_count": len(trace_rows),
        "selected_anchor": final_row["selected_anchor"],
        "lane_factor": final_row["lane_factor"],
    }


def run_search(max_n: int, max_steps: int) -> tuple[list[dict[str, object]], dict[str, object]]:
    """Run the tighter family over the toy corpus."""
    corpus = lane_base.generate_toy_corpus(max_n)
    trace_rows: list[dict[str, object]] = []
    traces_by_law: dict[str, list[dict[str, object]]] = {law_id: [] for law_id in LAW_ORDER}

    for law_id in LAW_ORDER:
        for modulus in corpus:
            trace = run_case(law_id, modulus, max_steps=max_steps)
            trace_rows.extend(trace)
            traces_by_law[law_id].append(summarize_trace(trace))

    law_summaries: dict[str, dict[str, object]] = {}
    best_law = LAW_ORDER[0]
    best_lane_success_count = -1
    best_factor_reach_count = -1
    for law_id in LAW_ORDER:
        traces = traces_by_law[law_id]
        lane_success_count = sum(int(bool(item["lane_success"])) for item in traces)
        factor_reach_count = sum(int(bool(item["factor_reach"])) for item in traces)
        lane_steps = [int(item["step_count"]) for item in traces if bool(item["lane_success"])]
        failure_reason_counts: dict[str, int] = {}
        for item in traces:
            if bool(item["lane_success"]):
                continue
            stop_reason = str(item["stop_reason"])
            failure_reason_counts[stop_reason] = failure_reason_counts.get(stop_reason, 0) + 1
        first_lane_case = next(
            (int(corpus[index]) for index, item in enumerate(traces) if bool(item["lane_success"])),
            None,
        )
        law_summaries[law_id] = {
            "lane_success_count": lane_success_count,
            "lane_success_recall": (lane_success_count / len(corpus)) if corpus else 0.0,
            "factor_reach_count": factor_reach_count,
            "factor_reach_recall": (factor_reach_count / len(corpus)) if corpus else 0.0,
            "first_lane_case": first_lane_case,
            "median_steps_on_lane_success": (
                float(statistics.median(lane_steps)) if lane_steps else None
            ),
            "failure_reason_counts": failure_reason_counts,
        }
        if (lane_success_count, factor_reach_count) > (best_lane_success_count, best_factor_reach_count):
            best_lane_success_count = lane_success_count
            best_factor_reach_count = factor_reach_count
            best_law = law_id

    baseline_summary = json.loads(
        (DEFAULT_OUTPUT_DIR / refined_base.SUMMARY_FILENAME).read_text(encoding="utf-8")
    )
    baseline_best = int(baseline_summary["best_lane_success_count"])
    improvement_over_baseline = max(best_lane_success_count, 0) - baseline_best

    summary = {
        "max_n": max_n,
        "case_count": len(corpus),
        "max_steps": max_steps,
        "law_summaries": law_summaries,
        "best_law": best_law,
        "best_lane_success_count": max(best_lane_success_count, 0),
        "best_factor_reach_count": max(best_factor_reach_count, 0),
        "baseline_best_lane_success_count": baseline_best,
        "improvement_over_baseline": improvement_over_baseline,
        "searched_family_falsified": max(best_lane_success_count, 0) == 0,
    }
    return trace_rows, summary


def main(argv: list[str] | None = None) -> int:
    """Run the tighter entry family and emit the summary JSON."""
    parser = build_parser()
    args = parser.parse_args(argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    _trace_rows, summary = run_search(max_n=args.max_n, max_steps=args.max_steps)
    summary_path = args.output_dir / SUMMARY_FILENAME
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
