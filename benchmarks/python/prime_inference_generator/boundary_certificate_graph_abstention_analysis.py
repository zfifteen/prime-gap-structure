#!/usr/bin/env python3
"""Abstention analysis for Boundary Certificate Graph Solver v0."""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

try:
    from .boundary_certificate_graph_solver import solve_anchor
    from .composite_exclusion_boundary_probe import eliminate_candidates
    from .offline_pgs_certificate_emitter import anchor_primes, first_prime_after
    from .resolved_boundary_lock_separator_probe import jsonable
except ImportError:  # pragma: no cover - direct script execution
    MODULE_DIR = Path(__file__).resolve().parent
    if str(MODULE_DIR) not in sys.path:
        sys.path.insert(0, str(MODULE_DIR))
    from boundary_certificate_graph_solver import solve_anchor
    from composite_exclusion_boundary_probe import eliminate_candidates
    from offline_pgs_certificate_emitter import anchor_primes, first_prime_after
    from resolved_boundary_lock_separator_probe import jsonable


DEFAULT_OUTPUT_DIR = Path("output/prime_inference_generator")
SUMMARY_FILENAME = "boundary_certificate_graph_abstention_analysis_summary.json"
ROWS_FILENAME = "boundary_certificate_graph_abstention_analysis_rows.jsonl"
RULE_SET = "005A-R"
SOLVER_VERSION = "v1"
TRUE_BOUNDARY_STATUSES = (
    "RESOLVED",
    "UNRESOLVED",
    "REJECTED",
    "ABSORBED",
    "NOT_IN_CANDIDATE_SET",
)
ABSTAIN_REASON_CATEGORIES = (
    "TRUE_BOUNDARY_RESOLVED_BUT_UNRESOLVED_LATER_REMAIN",
    "TRUE_BOUNDARY_RESOLVED_WITH_MULTIPLE_RESOLVED_SURVIVORS",
    "TRUE_BOUNDARY_UNRESOLVED",
    "NO_RESOLVED_SURVIVOR",
    "MULTIPLE_RESOLVED_SURVIVORS",
    "UNRESOLVED_CANDIDATES_AFTER_SOLVE",
    "TRUE_BOUNDARY_NOT_IN_CANDIDATE_SET",
    "TRUE_BOUNDARY_REJECTED_OR_ABSORBED",
    "OTHER",
)
MISSING_RELATION_PATTERNS = (
    "NEED_POST_BOUNDARY_ABSORPTION",
    "NEED_RESET_DISCRIMINATOR",
    "NEED_UNRESOLVED_LATER_DOMINATION",
    "NEED_FALSE_RESOLVED_SURVIVOR_REJECTION",
    "NEED_TRUE_BOUNDARY_CLOSURE",
    "NEED_MULTI_HOLE_CLOSURE",
    "NEED_CARRIER_LOCK_EXTENSION",
    "NEED_HIGHER_DIVISOR_LOCK_EXTENSION",
    "NEED_PREVIOUS_CHAMBER_MEMORY",
    "NEED_LARGER_CANDIDATE_BOUND",
    "UNKNOWN",
)
RECOMMENDATION_BY_PATTERN = {
    "NEED_POST_BOUNDARY_ABSORPTION": (
        "post_boundary_absorption_with_reset_lock_discriminator"
    ),
    "NEED_RESET_DISCRIMINATOR": "reset_discriminator_for_candidate_absorption",
    "NEED_UNRESOLVED_LATER_DOMINATION": (
        "unresolved_later_domination_from_existing_graph_facts"
    ),
    "NEED_FALSE_RESOLVED_SURVIVOR_REJECTION": (
        "false_resolved_survivor_rejection_with_structural_lock"
    ),
    "NEED_TRUE_BOUNDARY_CLOSURE": "true_boundary_chamber_completion_relation",
    "NEED_MULTI_HOLE_CLOSURE": "multi_hole_positive_witness_closure_relation",
    "NEED_CARRIER_LOCK_EXTENSION": "carrier_lock_extension_relation",
    "NEED_HIGHER_DIVISOR_LOCK_EXTENSION": "higher_divisor_lock_extension_relation",
    "NEED_PREVIOUS_CHAMBER_MEMORY": "previous_chamber_memory_relation",
    "NEED_LARGER_CANDIDATE_BOUND": "larger_candidate_bound_gate",
    "UNKNOWN": "additional_graph_abstention_forensics",
}


def build_parser() -> argparse.ArgumentParser:
    """Build the graph abstention-analysis CLI."""
    parser = argparse.ArgumentParser(
        description="Classify Boundary Certificate Graph Solver v0 abstentions.",
    )
    parser.add_argument(
        "--start-anchor",
        type=int,
        default=11,
        help="Inclusive lower bound for anchor primes.",
    )
    parser.add_argument(
        "--max-anchor",
        type=int,
        default=10_000,
        help="Inclusive upper bound for anchor primes.",
    )
    parser.add_argument(
        "--candidate-bound",
        type=int,
        default=128,
        help="Largest candidate boundary offset.",
    )
    parser.add_argument(
        "--witness-bound",
        type=int,
        default=127,
        help="Largest positive witness factor.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for JSON and JSONL artifacts.",
    )
    return parser


def actual_boundary_offset(anchor_p: int, candidate_bound: int) -> int | None:
    """Return the reporting-only audited next-boundary offset."""
    search_cap = anchor_p + max(10_000, candidate_bound * 16)
    boundary = first_prime_after(anchor_p, search_cap)
    if boundary is None:
        return None
    return int(boundary) - anchor_p


def candidate_record_by_offset(row: dict[str, Any], offset: int) -> dict[str, Any] | None:
    """Return one base candidate record by offset."""
    for record in row["candidate_status_records"]:
        if int(record["offset"]) == offset:
            return record
    return None


def true_boundary_status(
    actual_offset: int | None,
    graph_row: dict[str, Any],
) -> str:
    """Return the true-boundary status after graph solving."""
    if actual_offset is None:
        return "NOT_IN_CANDIDATE_SET"
    candidate_offsets = [int(offset) for offset in graph_row["candidate_offsets"]]
    if actual_offset not in candidate_offsets:
        return "NOT_IN_CANDIDATE_SET"
    absorbed = [int(offset) for offset in graph_row["absorbed_offsets"]]
    if actual_offset in absorbed:
        return "ABSORBED"
    resolved = [int(offset) for offset in graph_row["resolved_offsets_after_solve"]]
    if actual_offset in resolved:
        return "RESOLVED"
    unresolved = [
        int(offset) for offset in graph_row["unresolved_offsets_after_solve"]
    ]
    if actual_offset in unresolved:
        return "UNRESOLVED"
    rejected = [int(offset) for offset in graph_row["rejected_offsets"]]
    if actual_offset in rejected:
        return "REJECTED"
    return "NOT_IN_CANDIDATE_SET"


def abstain_reasons(
    status: str,
    resolved: list[int],
    unresolved: list[int],
    actual_offset: int | None,
) -> list[str]:
    """Return all observed abstain reason categories for one graph row."""
    reasons: list[str] = []
    if status == "NOT_IN_CANDIDATE_SET":
        reasons.append("TRUE_BOUNDARY_NOT_IN_CANDIDATE_SET")
    if status in {"REJECTED", "ABSORBED"}:
        reasons.append("TRUE_BOUNDARY_REJECTED_OR_ABSORBED")
    if status == "UNRESOLVED":
        reasons.append("TRUE_BOUNDARY_UNRESOLVED")
    if not resolved:
        reasons.append("NO_RESOLVED_SURVIVOR")
    if len(resolved) > 1:
        reasons.append("MULTIPLE_RESOLVED_SURVIVORS")
    if unresolved:
        reasons.append("UNRESOLVED_CANDIDATES_AFTER_SOLVE")
    if status == "RESOLVED" and len(resolved) > 1:
        reasons.append("TRUE_BOUNDARY_RESOLVED_WITH_MULTIPLE_RESOLVED_SURVIVORS")
    if (
        status == "RESOLVED"
        and actual_offset is not None
        and any(offset > actual_offset for offset in unresolved)
    ):
        reasons.append("TRUE_BOUNDARY_RESOLVED_BUT_UNRESOLVED_LATER_REMAIN")
    if not reasons:
        reasons.append("OTHER")
    return reasons


def primary_abstain_reason(reasons: list[str]) -> str:
    """Return one deterministic primary abstain reason."""
    for category in ABSTAIN_REASON_CATEGORIES:
        if category in reasons:
            return category
    return "OTHER"


def true_unresolved_hole_count(
    base_row: dict[str, Any],
    actual_offset: int | None,
) -> int:
    """Return unresolved interior count for the audited boundary candidate."""
    if actual_offset is None:
        return 0
    record = candidate_record_by_offset(base_row, actual_offset)
    if record is None:
        return 0
    return len(record["unresolved_interior_offsets"])


def missing_relation_reasons(
    status: str,
    resolved: list[int],
    unresolved: list[int],
    actual_offset: int | None,
    base_row: dict[str, Any],
) -> list[str]:
    """Return missing graph-relation pattern categories for one abstention."""
    patterns: list[str] = []
    unresolved_before_true = 0
    unresolved_after_true = 0
    if actual_offset is not None:
        unresolved_before_true = sum(1 for offset in unresolved if offset < actual_offset)
        unresolved_after_true = sum(1 for offset in unresolved if offset > actual_offset)

    if status == "NOT_IN_CANDIDATE_SET":
        patterns.append("NEED_LARGER_CANDIDATE_BOUND")
    elif status in {"REJECTED", "ABSORBED"}:
        patterns.append("UNKNOWN")
    elif status == "UNRESOLVED":
        hole_count = true_unresolved_hole_count(base_row, actual_offset)
        if hole_count > 1:
            patterns.append("NEED_MULTI_HOLE_CLOSURE")
        patterns.append("NEED_TRUE_BOUNDARY_CLOSURE")

    if status == "RESOLVED" and unresolved_after_true > 0:
        patterns.append("NEED_UNRESOLVED_LATER_DOMINATION")
        patterns.append("NEED_POST_BOUNDARY_ABSORPTION")
        patterns.append("NEED_RESET_DISCRIMINATOR")
    if status == "RESOLVED" and len(resolved) > 1:
        patterns.append("NEED_FALSE_RESOLVED_SURVIVOR_REJECTION")
        patterns.append("NEED_RESET_DISCRIMINATOR")
    if unresolved_before_true > 0:
        patterns.append("NEED_TRUE_BOUNDARY_CLOSURE")
    if not patterns:
        patterns.append("UNKNOWN")

    deduped: list[str] = []
    for pattern in patterns:
        if pattern not in deduped:
            deduped.append(pattern)
    return deduped


def primary_missing_relation(patterns: list[str]) -> str:
    """Return one deterministic primary missing-relation pattern."""
    priority = (
        "NEED_LARGER_CANDIDATE_BOUND",
        "NEED_TRUE_BOUNDARY_CLOSURE",
        "NEED_MULTI_HOLE_CLOSURE",
        "NEED_UNRESOLVED_LATER_DOMINATION",
        "NEED_POST_BOUNDARY_ABSORPTION",
        "NEED_FALSE_RESOLVED_SURVIVOR_REJECTION",
        "NEED_RESET_DISCRIMINATOR",
        "NEED_CARRIER_LOCK_EXTENSION",
        "NEED_HIGHER_DIVISOR_LOCK_EXTENSION",
        "NEED_PREVIOUS_CHAMBER_MEMORY",
        "UNKNOWN",
    )
    for pattern in priority:
        if pattern in patterns:
            return pattern
    return "UNKNOWN"


def abstention_record(
    graph_row: dict[str, Any],
    base_row: dict[str, Any],
    actual_offset: int | None,
) -> dict[str, Any]:
    """Return one abstention-analysis record."""
    resolved = [int(offset) for offset in graph_row["resolved_offsets_after_solve"]]
    unresolved = [
        int(offset) for offset in graph_row["unresolved_offsets_after_solve"]
    ]
    rejected = [int(offset) for offset in graph_row["rejected_offsets"]]
    absorbed = [int(offset) for offset in graph_row["absorbed_offsets"]]
    status = true_boundary_status(actual_offset, graph_row)
    false_resolved_count = (
        len(resolved)
        if actual_offset is None
        else sum(1 for offset in resolved if offset != actual_offset)
    )
    unresolved_before_true = (
        0
        if actual_offset is None
        else sum(1 for offset in unresolved if offset < actual_offset)
    )
    unresolved_after_true = (
        0
        if actual_offset is None
        else sum(1 for offset in unresolved if offset > actual_offset)
    )
    reasons = abstain_reasons(status, resolved, unresolved, actual_offset)
    patterns = missing_relation_reasons(
        status,
        resolved,
        unresolved,
        actual_offset,
        base_row,
    )
    return {
        "anchor_p": int(graph_row["anchor_p"]),
        "actual_boundary_offset_label": actual_offset,
        "graph_solution_status": "ABSTAIN",
        "resolved_candidates_after_solve": resolved,
        "unresolved_candidates_after_solve": unresolved,
        "rejected_candidates_after_solve": rejected,
        "absorbed_candidates_after_solve": absorbed,
        "true_boundary_status_after_solve": status,
        "false_resolved_candidate_count": false_resolved_count,
        "unresolved_after_true_count": unresolved_after_true,
        "unresolved_before_true_count": unresolved_before_true,
        "multiple_resolved_survivors_bool": len(resolved) > 1,
        "true_boundary_resolved_but_not_unique_bool": (
            status == "RESOLVED" and (len(resolved) != 1 or bool(unresolved))
        ),
        "true_boundary_unresolved_bool": status == "UNRESOLVED",
        "no_resolved_survivor_bool": not resolved,
        "abstain_reasons": reasons,
        "primary_abstain_reason": primary_abstain_reason(reasons),
        "first_missing_relation_guess": primary_missing_relation(patterns),
        "missing_relation_reasons": patterns,
    }


def summarize(
    start_anchor: int,
    max_anchor: int,
    candidate_bound: int,
    witness_bound: int,
    rows: list[dict[str, Any]],
    anchors_evaluated: int,
    graph_solved_count: int,
    graph_confirmed_count: int,
    graph_failed_count: int,
    runtime_seconds: float,
) -> dict[str, Any]:
    """Return abstention-analysis summary metrics."""
    abstain_reason_counts = Counter(
        row["primary_abstain_reason"] for row in rows
    )
    true_status_counts = Counter(
        row["true_boundary_status_after_solve"] for row in rows
    )
    missing_pattern_counts = Counter(
        row["first_missing_relation_guess"] for row in rows
    )
    top_patterns = [
        {"pattern": pattern, "count": int(count)}
        for pattern, count in missing_pattern_counts.most_common()
    ]
    dominant_pattern = top_patterns[0]["pattern"] if top_patterns else "UNKNOWN"
    recommended = RECOMMENDATION_BY_PATTERN[dominant_pattern]
    return {
        "mode": "offline_boundary_certificate_graph_abstention_analysis",
        "rule_set": RULE_SET,
        "solver_version": SOLVER_VERSION,
        "anchor_range": f"{start_anchor}..{max_anchor}",
        "candidate_bound": candidate_bound,
        "witness_bound": witness_bound,
        "anchors_evaluated": anchors_evaluated,
        "graph_solved_count": graph_solved_count,
        "graph_abstain_count": len(rows),
        "graph_confirmed_count": graph_confirmed_count,
        "graph_failed_count": graph_failed_count,
        "abstain_reason_counts": {
            category: int(abstain_reason_counts.get(category, 0))
            for category in ABSTAIN_REASON_CATEGORIES
        },
        "true_boundary_status_counts": {
            status: int(true_status_counts.get(status, 0))
            for status in TRUE_BOUNDARY_STATUSES
        },
        "missing_relation_pattern_counts": {
            pattern: int(missing_pattern_counts.get(pattern, 0))
            for pattern in MISSING_RELATION_PATTERNS
        },
        "top_missing_relation_patterns": top_patterns,
        "first_20_abstain_examples": rows[:20],
        "first_20_true_boundary_unresolved_examples": [
            row for row in rows if row["true_boundary_unresolved_bool"]
        ][:20],
        "first_20_true_boundary_resolved_but_later_unresolved_examples": [
            row
            for row in rows
            if (
                row["true_boundary_status_after_solve"] == "RESOLVED"
                and row["unresolved_after_true_count"] > 0
            )
        ][:20],
        "first_20_multiple_resolved_examples": [
            row for row in rows if row["multiple_resolved_survivors_bool"]
        ][:20],
        "recommended_next_relation": recommended,
        "dominant_missing_relation_pattern": dominant_pattern,
        "classical_labels_status": "reporting_only_after_graph_solve",
        "production_approved": False,
        "cryptographic_use_approved": False,
        "pure_emission_added": False,
        "boundary_law_005_status": "candidate_grade_only",
        "runtime_seconds": runtime_seconds,
    }


def run_analysis(
    start_anchor: int,
    max_anchor: int,
    candidate_bound: int,
    witness_bound: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run graph abstention analysis over one anchor surface."""
    started = time.perf_counter()
    rows: list[dict[str, Any]] = []
    graph_solved_count = 0
    graph_confirmed_count = 0
    graph_failed_count = 0
    anchors = anchor_primes(start_anchor, max_anchor)
    for anchor_p in anchors:
        record, graph_row = solve_anchor(anchor_p, candidate_bound, witness_bound)
        actual_offset = actual_boundary_offset(anchor_p, candidate_bound)
        if record is not None:
            graph_solved_count += 1
            if actual_offset is not None and int(record["boundary_offset"]) == actual_offset:
                graph_confirmed_count += 1
            else:
                graph_failed_count += 1
            continue
        base_row = eliminate_candidates(
            anchor_p,
            candidate_bound,
            enable_single_hole_positive_witness_closure=True,
            witness_bound=witness_bound,
            enable_carrier_locked_pressure_ceiling=True,
            carrier_lock_predicate="unresolved_alternatives_before_threat",
            enable_higher_divisor_pressure_locked_absorption=False,
        )
        rows.append(abstention_record(graph_row, base_row, actual_offset))

    summary = summarize(
        start_anchor,
        max_anchor,
        candidate_bound,
        witness_bound,
        rows,
        len(anchors),
        graph_solved_count,
        graph_confirmed_count,
        graph_failed_count,
        time.perf_counter() - started,
    )
    return rows, summary


def write_artifacts(
    rows: list[dict[str, Any]],
    summary: dict[str, Any],
    output_dir: Path,
) -> dict[str, Path]:
    """Write LF-terminated abstention-analysis JSONL and summary JSON."""
    output_dir.mkdir(parents=True, exist_ok=True)
    rows_path = output_dir / ROWS_FILENAME
    with rows_path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(jsonable(row), sort_keys=True) + "\n")

    summary_path = output_dir / SUMMARY_FILENAME
    summary_path.write_text(
        json.dumps(jsonable(summary), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return {
        "rows_path": rows_path,
        "summary_path": summary_path,
    }


def main(argv: list[str] | None = None) -> int:
    """Run graph abstention analysis."""
    args = build_parser().parse_args(argv)
    rows, summary = run_analysis(
        start_anchor=args.start_anchor,
        max_anchor=args.max_anchor,
        candidate_bound=args.candidate_bound,
        witness_bound=args.witness_bound,
    )
    write_artifacts(rows, summary, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
