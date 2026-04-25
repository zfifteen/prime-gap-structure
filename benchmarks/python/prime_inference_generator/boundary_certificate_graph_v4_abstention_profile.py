#!/usr/bin/env python3
"""Profile Graph Solver v3 abstentions for the next graph relation."""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

try:
    from .boundary_certificate_graph_solver import (
        active_graph_reset_evidence_status,
        candidate_nodes,
        carrier_identity,
        reset_evidence_status,
        solve_anchor,
    )
    from .composite_exclusion_boundary_probe import (
        CANDIDATE_STATUS_REJECTED,
        CANDIDATE_STATUS_RESOLVED_SURVIVOR,
        CANDIDATE_STATUS_UNRESOLVED,
        eliminate_candidates,
        first_legal_carrier,
    )
    from .offline_pgs_certificate_emitter import anchor_primes, first_prime_after
    from .resolved_boundary_lock_separator_probe import jsonable
except ImportError:  # pragma: no cover - direct script execution
    MODULE_DIR = Path(__file__).resolve().parent
    if str(MODULE_DIR) not in sys.path:
        sys.path.insert(0, str(MODULE_DIR))
    from boundary_certificate_graph_solver import (
        active_graph_reset_evidence_status,
        candidate_nodes,
        carrier_identity,
        reset_evidence_status,
        solve_anchor,
    )
    from composite_exclusion_boundary_probe import (
        CANDIDATE_STATUS_REJECTED,
        CANDIDATE_STATUS_RESOLVED_SURVIVOR,
        CANDIDATE_STATUS_UNRESOLVED,
        eliminate_candidates,
        first_legal_carrier,
    )
    from offline_pgs_certificate_emitter import anchor_primes, first_prime_after
    from resolved_boundary_lock_separator_probe import jsonable


DEFAULT_OUTPUT_DIR = Path("output/prime_inference_generator")
SUMMARY_FILENAME = "boundary_certificate_graph_v4_abstention_profile_summary.json"
ROWS_FILENAME = "boundary_certificate_graph_v4_abstention_profile_rows.jsonl"
RULE_SET = "005A-R"
SOLVER_VERSION = "v3"
ABSTAIN_REASON_CATEGORIES = (
    "TRUE_BOUNDARY_RESOLVED_BUT_UNRESOLVED_LATER_REMAIN",
    "TRUE_BOUNDARY_RESOLVED_WITH_MULTIPLE_RESOLVED_SURVIVORS",
    "TRUE_BOUNDARY_UNRESOLVED",
    "MULTIPLE_RESOLVED_SURVIVORS",
    "UNRESOLVED_CANDIDATES_AFTER_SOLVE",
    "TRUE_BOUNDARY_REJECTED_OR_ABSORBED",
    "TRUE_BOUNDARY_NOT_IN_CANDIDATE_SET",
    "OTHER",
)
TRUE_BOUNDARY_STATUSES = (
    "RESOLVED",
    "UNRESOLVED",
    "REJECTED",
    "ABSORBED",
    "NOT_IN_CANDIDATE_SET",
)
RECOMMENDATION_BY_HINT = {
    "UNKNOWN_RESET_STATE_DISCRIMINATOR": (
        "unresolved_later_domination_target_no_carrier_reset_discriminator"
    ),
    "ACTIVE_RESET_EVIDENCE_DISCRIMINATOR": (
        "unresolved_later_domination_active_reset_discriminator"
    ),
    "LEGAL_CARRIER_SOURCE_EXTENSION_DISCRIMINATOR": (
        "unresolved_later_domination_legal_carrier_source_extension"
    ),
    "RERUN_ACTIVE_NO_RESET_DOMINATION_AFTER_V3": (
        "rerun_active_no_reset_domination_after_v3"
    ),
    "FALSE_RESOLVED_SURVIVOR_REJECTION_PROFILE": (
        "false_resolved_survivor_rejection_profile"
    ),
    "TRUE_BOUNDARY_CLOSURE_PROFILE": "true_boundary_closure_profile",
    "NO_UNRESOLVED_TARGET": "no_v4_relation_recommended",
    "UNRESOLVED_LATER_DOMINATION_REFINEMENT": (
        "unresolved_later_domination_refinement"
    ),
}


def build_parser() -> argparse.ArgumentParser:
    """Build the v4 abstention-profile CLI."""
    parser = argparse.ArgumentParser(
        description="Profile Graph Solver v3 abstentions for a v4 relation.",
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


def base_row(anchor_p: int, candidate_bound: int, witness_bound: int) -> dict[str, Any]:
    """Return the accepted pre-graph eliminator row for one anchor."""
    return eliminate_candidates(
        anchor_p,
        candidate_bound,
        enable_single_hole_positive_witness_closure=True,
        witness_bound=witness_bound,
        enable_carrier_locked_pressure_ceiling=True,
        carrier_lock_predicate="unresolved_alternatives_before_threat",
        enable_higher_divisor_pressure_locked_absorption=False,
    )


def nodes_after_v3(
    row: dict[str, Any],
    graph_row: dict[str, Any],
    witness_bound: int,
) -> dict[int, dict[str, Any]]:
    """Return candidate nodes with v3 graph statuses applied."""
    nodes = candidate_nodes(row, witness_bound)
    rejected = {int(offset) for offset in graph_row["rejected_offsets"]}
    resolved = {int(offset) for offset in graph_row["resolved_offsets_after_solve"]}
    unresolved = {
        int(offset) for offset in graph_row["unresolved_offsets_after_solve"]
    }
    absorbed = {int(offset) for offset in graph_row["absorbed_offsets"]}
    for offset, node in nodes.items():
        node["absorbed"] = offset in absorbed
        if offset in resolved:
            node["status"] = CANDIDATE_STATUS_RESOLVED_SURVIVOR
        elif offset in unresolved:
            node["status"] = CANDIDATE_STATUS_UNRESOLVED
        elif offset in rejected:
            node["status"] = CANDIDATE_STATUS_REJECTED
    return nodes


def true_boundary_status(
    actual_offset: int | None,
    graph_row: dict[str, Any],
) -> str:
    """Return the true-boundary status after v3 graph solving."""
    if actual_offset is None:
        return "NOT_IN_CANDIDATE_SET"
    candidate_offsets = {int(offset) for offset in graph_row["candidate_offsets"]}
    if actual_offset not in candidate_offsets:
        return "NOT_IN_CANDIDATE_SET"
    if actual_offset in {int(offset) for offset in graph_row["absorbed_offsets"]}:
        return "ABSORBED"
    if actual_offset in {
        int(offset) for offset in graph_row["resolved_offsets_after_solve"]
    }:
        return "RESOLVED"
    if actual_offset in {
        int(offset) for offset in graph_row["unresolved_offsets_after_solve"]
    }:
        return "UNRESOLVED"
    if actual_offset in {int(offset) for offset in graph_row["rejected_offsets"]}:
        return "REJECTED"
    return "NOT_IN_CANDIDATE_SET"


def abstain_reasons(
    status: str,
    resolved: list[int],
    unresolved: list[int],
    actual_offset: int | None,
) -> list[str]:
    """Return observed v3 abstention reasons."""
    reasons: list[str] = []
    if status == "NOT_IN_CANDIDATE_SET":
        reasons.append("TRUE_BOUNDARY_NOT_IN_CANDIDATE_SET")
    if status in {"REJECTED", "ABSORBED"}:
        reasons.append("TRUE_BOUNDARY_REJECTED_OR_ABSORBED")
    if status == "UNRESOLVED":
        reasons.append("TRUE_BOUNDARY_UNRESOLVED")
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
    """Return one deterministic primary abstention reason."""
    for category in ABSTAIN_REASON_CATEGORIES:
        if category in reasons:
            return category
    return "OTHER"


def nearest_later_offset(source_offset: int | None, offsets: list[int]) -> int | None:
    """Return the nearest offset greater than the source offset."""
    if source_offset is None:
        return None
    later = [offset for offset in offsets if offset > source_offset]
    return min(later) if later else None


def nearest_unresolved_after_each_resolved(
    resolved: list[int],
    unresolved: list[int],
) -> list[dict[str, int | None]]:
    """Return nearest unresolved targets for every resolved source."""
    return [
        {
            "resolved_offset": offset,
            "nearest_unresolved_offset": nearest_later_offset(offset, unresolved),
        }
        for offset in resolved
    ]


def choose_source_offset(
    actual_offset: int | None,
    status: str,
    resolved: list[int],
) -> int | None:
    """Choose one source candidate for v4 profiling."""
    if status == "RESOLVED" and actual_offset in resolved:
        return actual_offset
    if resolved:
        return resolved[0]
    return None


def carrier_field(
    carrier: dict[str, Any] | None,
    key: str,
) -> Any:
    """Return one carrier field with None for absent carriers."""
    if carrier is None:
        return None
    return carrier[key]


def why_v1_abstained(
    source_offset: int | None,
    target_offset: int | None,
    nodes: dict[int, dict[str, Any]],
    anchor_p: int,
    witness_bound: int,
) -> str:
    """Return the observed v1 abstention reason for one source-target pair."""
    if source_offset is None:
        return "NO_SOURCE_CANDIDATE"
    if target_offset is None:
        return "NO_TARGET_CANDIDATE"
    source = nodes[source_offset]
    target = nodes[target_offset]
    if source["status"] != CANDIDATE_STATUS_RESOLVED_SURVIVOR:
        return "SOURCE_NOT_RESOLVED_SURVIVOR"
    if bool(source["single_hole_closure_used"]):
        return "SOURCE_SINGLE_HOLE_CLOSURE_USED_TRUE"
    if target["status"] != CANDIDATE_STATUS_UNRESOLVED:
        return "TARGET_NOT_UNRESOLVED"
    reset_status = reset_evidence_status(
        anchor_p,
        source_offset,
        target_offset,
        source["carrier"],
        witness_bound,
    )
    if reset_status != "NO_RESET_EVIDENCE":
        return f"RESET_STATUS_{reset_status}"
    return "V1_APPLICABLE_AFTER_V3"


def why_v2_abstained(
    source_offset: int | None,
    target_offset: int | None,
    nodes: dict[int, dict[str, Any]],
    anchor_p: int,
    witness_bound: int,
) -> str:
    """Return the observed v2 abstention reason for one source-target pair."""
    if source_offset is None:
        return "NO_SOURCE_CANDIDATE"
    if target_offset is None:
        return "NO_TARGET_CANDIDATE"
    source = nodes[source_offset]
    target = nodes[target_offset]
    if source["status"] != CANDIDATE_STATUS_RESOLVED_SURVIVOR:
        return "SOURCE_NOT_RESOLVED_SURVIVOR"
    if bool(source["single_hole_closure_used"]):
        return "SOURCE_SINGLE_HOLE_CLOSURE_USED_TRUE"
    if target["status"] != CANDIDATE_STATUS_UNRESOLVED:
        return "TARGET_NOT_UNRESOLVED"
    reset_status = active_graph_reset_evidence_status(
        anchor_p,
        source_offset,
        target_offset,
        source["carrier"],
        nodes,
        witness_bound,
    )
    if reset_status != "NO_ACTIVE_RESET_EVIDENCE":
        return f"ACTIVE_RESET_STATUS_{reset_status}"
    return "V2_APPLICABLE_AFTER_V3"


def why_v3_abstained(
    source_offset: int | None,
    target_offset: int | None,
    resolved: list[int],
    nodes: dict[int, dict[str, Any]],
    anchor_p: int,
    witness_bound: int,
) -> str:
    """Return the observed v3 abstention reason for one source-target pair."""
    if len(resolved) != 1:
        return "ACTIVE_GRAPH_NOT_SINGLE_RESOLVED"
    if source_offset is None:
        return "NO_SOURCE_CANDIDATE"
    if target_offset is None:
        return "NO_TARGET_CANDIDATE"
    source = nodes[source_offset]
    if bool(source["single_hole_closure_used"]):
        return "SOURCE_SINGLE_HOLE_CLOSURE_USED_TRUE"
    if source["carrier"]["carrier_d"] is not None:
        return "SOURCE_HAS_LEGAL_CARRIER"
    target_carrier = first_legal_carrier(anchor_p, target_offset, witness_bound)
    if target_carrier["carrier_d"] is None:
        return "TARGET_HAS_NO_LEGAL_CARRIER"
    if int(target_carrier["carrier_offset"]) <= source_offset:
        return "TARGET_FIRST_CARRIER_NOT_AFTER_SOURCE"
    return "V3_APPLICABLE_AFTER_V3"


def v4_hint(
    status: str,
    resolved: list[int],
    unresolved: list[int],
    why_v1: str,
    why_v2: str,
    why_v3: str,
) -> str:
    """Return the candidate v4 relation hint from observed v3 structure."""
    if status == "UNRESOLVED":
        return "TRUE_BOUNDARY_CLOSURE_PROFILE"
    if len(resolved) > 1:
        return "FALSE_RESOLVED_SURVIVOR_REJECTION_PROFILE"
    if not unresolved:
        return "NO_UNRESOLVED_TARGET"
    if why_v2 == "V2_APPLICABLE_AFTER_V3":
        return "RERUN_ACTIVE_NO_RESET_DOMINATION_AFTER_V3"
    if why_v3 == "SOURCE_HAS_LEGAL_CARRIER":
        return "LEGAL_CARRIER_SOURCE_EXTENSION_DISCRIMINATOR"
    if why_v2 == "ACTIVE_RESET_STATUS_POSITIVE_RESET_EVIDENCE":
        return "ACTIVE_RESET_EVIDENCE_DISCRIMINATOR"
    if why_v2 == "ACTIVE_RESET_STATUS_UNKNOWN":
        return "UNKNOWN_RESET_STATE_DISCRIMINATOR"
    return "UNRESOLVED_LATER_DOMINATION_REFINEMENT"


def profile_row(
    anchor_p: int,
    candidate_bound: int,
    witness_bound: int,
    graph_row: dict[str, Any],
    row: dict[str, Any],
    actual_offset: int | None,
) -> dict[str, Any]:
    """Return one v4 abstention-profile row."""
    nodes = nodes_after_v3(row, graph_row, witness_bound)
    resolved = [int(offset) for offset in graph_row["resolved_offsets_after_solve"]]
    unresolved = [
        int(offset) for offset in graph_row["unresolved_offsets_after_solve"]
    ]
    rejected = [int(offset) for offset in graph_row["rejected_offsets"]]
    absorbed = [int(offset) for offset in graph_row["absorbed_offsets"]]
    status = true_boundary_status(actual_offset, graph_row)
    reasons = abstain_reasons(status, resolved, unresolved, actual_offset)
    source_offset = choose_source_offset(actual_offset, status, resolved)
    target_offset = nearest_later_offset(source_offset, unresolved)
    source_node = nodes.get(source_offset) if source_offset is not None else None
    target_carrier = (
        first_legal_carrier(anchor_p, target_offset, witness_bound)
        if target_offset is not None
        else None
    )
    source_carrier = source_node["carrier"] if source_node is not None else None
    source_has_carrier = bool(
        source_carrier is not None and source_carrier["carrier_d"] is not None
    )
    target_has_carrier = bool(
        target_carrier is not None and target_carrier["carrier_d"] is not None
    )
    identity_preserved = (
        bool(source_has_carrier and target_has_carrier)
        and carrier_identity(source_carrier) == carrier_identity(target_carrier)
    )
    target_carrier_after_source = (
        source_offset is not None
        and target_has_carrier
        and int(target_carrier["carrier_offset"]) > source_offset
    )
    active_reset_status = (
        active_graph_reset_evidence_status(
            anchor_p,
            source_offset,
            target_offset,
            source_carrier,
            nodes,
            witness_bound,
        )
        if source_offset is not None
        and target_offset is not None
        and source_carrier is not None
        else "NO_SOURCE_OR_TARGET"
    )
    why_v1 = why_v1_abstained(
        source_offset,
        target_offset,
        nodes,
        anchor_p,
        witness_bound,
    )
    why_v2 = why_v2_abstained(
        source_offset,
        target_offset,
        nodes,
        anchor_p,
        witness_bound,
    )
    why_v3 = why_v3_abstained(
        source_offset,
        target_offset,
        resolved,
        nodes,
        anchor_p,
        witness_bound,
    )
    empty_carrier_applicable = (
        len(resolved) == 1
        and source_node is not None
        and target_offset is not None
        and not bool(source_node["single_hole_closure_used"])
        and not source_has_carrier
        and target_carrier_after_source
    )
    return {
        "anchor_p": anchor_p,
        "actual_boundary_offset_label": actual_offset,
        "resolved_offsets_after_v3": resolved,
        "unresolved_offsets_after_v3": unresolved,
        "rejected_offsets_after_v3": rejected,
        "absorbed_offsets_after_v3": absorbed,
        "true_boundary_status_after_v3": status,
        "abstain_reason_after_v3": primary_abstain_reason(reasons),
        "abstain_reasons_after_v3": reasons,
        "nearest_unresolved_after_true": nearest_later_offset(
            actual_offset,
            unresolved,
        ),
        "nearest_unresolved_after_each_resolved": (
            nearest_unresolved_after_each_resolved(resolved, unresolved)
        ),
        "source_candidate_offset": source_offset,
        "source_candidate_has_carrier": source_has_carrier,
        "source_candidate_carrier_offset": carrier_field(
            source_carrier,
            "carrier_offset",
        ),
        "source_candidate_carrier_d": carrier_field(source_carrier, "carrier_d"),
        "source_candidate_carrier_family": carrier_field(
            source_carrier,
            "carrier_family",
        ),
        "source_single_hole_closure_used": (
            None
            if source_node is None
            else bool(source_node["single_hole_closure_used"])
        ),
        "target_candidate_offset": target_offset,
        "target_has_carrier": target_has_carrier,
        "target_carrier_offset": carrier_field(target_carrier, "carrier_offset"),
        "target_carrier_d": carrier_field(target_carrier, "carrier_d"),
        "target_carrier_family": carrier_field(target_carrier, "carrier_family"),
        "carrier_identity_preserved_bool": identity_preserved,
        "target_first_legal_carrier_after_source_bool": target_carrier_after_source,
        "active_reset_evidence_status": active_reset_status,
        "empty_carrier_extension_applicable_bool": empty_carrier_applicable,
        "why_v1_abstained": why_v1,
        "why_v2_abstained": why_v2,
        "why_v3_abstained": why_v3,
        "candidate_v4_relation_hint": v4_hint(
            status,
            resolved,
            unresolved,
            why_v1,
            why_v2,
            why_v3,
        ),
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
    """Return v4 abstention-profile summary metrics."""
    abstain_counts = Counter(row["abstain_reason_after_v3"] for row in rows)
    status_counts = Counter(row["true_boundary_status_after_v3"] for row in rows)
    v1_counts = Counter(row["why_v1_abstained"] for row in rows)
    v2_counts = Counter(row["why_v2_abstained"] for row in rows)
    v3_counts = Counter(row["why_v3_abstained"] for row in rows)
    hint_counts = Counter(row["candidate_v4_relation_hint"] for row in rows)
    recommended = (
        RECOMMENDATION_BY_HINT[hint_counts.most_common(1)[0][0]]
        if hint_counts
        else "NO_V4_RELATION_RECOMMENDED"
    )
    return {
        "mode": "offline_boundary_certificate_graph_v4_abstention_profile",
        "rule_set": RULE_SET,
        "solver_version": SOLVER_VERSION,
        "anchor_range": f"{start_anchor}..{max_anchor}",
        "candidate_bound": candidate_bound,
        "witness_bound": witness_bound,
        "anchors_evaluated": anchors_evaluated,
        "v3_graph_solved_count": graph_solved_count,
        "v3_graph_abstain_count": len(rows),
        "v3_graph_confirmed_count": graph_confirmed_count,
        "v3_graph_failed_count": graph_failed_count,
        "abstain_reason_counts": {
            category: int(abstain_counts.get(category, 0))
            for category in ABSTAIN_REASON_CATEGORIES
        },
        "true_boundary_status_counts": {
            status: int(status_counts.get(status, 0))
            for status in TRUE_BOUNDARY_STATUSES
        },
        "remaining_unresolved_later_count": int(
            abstain_counts.get(
                "TRUE_BOUNDARY_RESOLVED_BUT_UNRESOLVED_LATER_REMAIN",
                0,
            )
        ),
        "remaining_multiple_resolved_count": int(
            abstain_counts.get(
                "TRUE_BOUNDARY_RESOLVED_WITH_MULTIPLE_RESOLVED_SURVIVORS",
                0,
            )
        ),
        "remaining_true_boundary_unresolved_count": int(
            abstain_counts.get("TRUE_BOUNDARY_UNRESOLVED", 0)
        ),
        "v1_abstain_reason_counts": {
            reason: int(count) for reason, count in v1_counts.most_common()
        },
        "v2_abstain_reason_counts": {
            reason: int(count) for reason, count in v2_counts.most_common()
        },
        "v3_abstain_reason_counts": {
            reason: int(count) for reason, count in v3_counts.most_common()
        },
        "candidate_v4_relation_hint_counts": {
            hint: int(count) for hint, count in hint_counts.most_common()
        },
        "first_20_remaining_later_unresolved_examples": [
            row
            for row in rows
            if row["abstain_reason_after_v3"]
            == "TRUE_BOUNDARY_RESOLVED_BUT_UNRESOLVED_LATER_REMAIN"
        ][:20],
        "first_20_multiple_resolved_examples": [
            row
            for row in rows
            if row["abstain_reason_after_v3"]
            == "TRUE_BOUNDARY_RESOLVED_WITH_MULTIPLE_RESOLVED_SURVIVORS"
        ][:20],
        "first_20_true_boundary_unresolved_examples": [
            row
            for row in rows
            if row["abstain_reason_after_v3"] == "TRUE_BOUNDARY_UNRESOLVED"
        ][:20],
        "recommended_v4_relation": recommended,
        "classical_labels_status": "reporting_only_after_v3_graph_state",
        "production_approved": False,
        "cryptographic_use_approved": False,
        "pure_emission_added": False,
        "v4_relation_added": False,
        "runtime_seconds": runtime_seconds,
    }


def run_profile(
    start_anchor: int,
    max_anchor: int,
    candidate_bound: int,
    witness_bound: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run the v4 abstention profile over one anchor surface."""
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
        row = base_row(anchor_p, candidate_bound, witness_bound)
        rows.append(
            profile_row(
                anchor_p,
                candidate_bound,
                witness_bound,
                graph_row,
                row,
                actual_offset,
            )
        )

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
    """Write LF-terminated v4 profile JSONL and summary JSON."""
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
    """Run the v4 abstention profile."""
    args = build_parser().parse_args(argv)
    rows, summary = run_profile(
        start_anchor=args.start_anchor,
        max_anchor=args.max_anchor,
        candidate_bound=args.candidate_bound,
        witness_bound=args.witness_bound,
    )
    write_artifacts(rows, summary, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
