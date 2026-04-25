#!/usr/bin/env python3
"""Bug audit for the graph v4/v5 scale failure at anchor 10193."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

from sympy import factorint, primerange

try:
    from .boundary_certificate_graph_solver import (
        UNRESOLVED_LATER_DOMINATION_V4_RELATION,
        base_relations,
        candidate_nodes,
        propagate_005a_r,
        propagate_unresolved_later_domination,
        propagate_unresolved_later_domination_v2,
        propagate_unresolved_later_domination_v3,
        propagate_unresolved_later_domination_v5,
        target_no_carrier_reset_evidence_status,
    )
    from .composite_exclusion_boundary_probe import (
        CANDIDATE_STATUS_REJECTED,
        CANDIDATE_STATUS_RESOLVED_SURVIVOR,
        CANDIDATE_STATUS_UNRESOLVED,
        certified_divisor_class,
        eliminate_candidates,
        first_legal_carrier,
    )
    from .offline_pgs_certificate_emitter import first_prime_after
    from .resolved_boundary_lock_separator_probe import jsonable
except ImportError:  # pragma: no cover - direct script execution
    MODULE_DIR = Path(__file__).resolve().parent
    if str(MODULE_DIR) not in sys.path:
        sys.path.insert(0, str(MODULE_DIR))
    from boundary_certificate_graph_solver import (
        UNRESOLVED_LATER_DOMINATION_V4_RELATION,
        base_relations,
        candidate_nodes,
        propagate_005a_r,
        propagate_unresolved_later_domination,
        propagate_unresolved_later_domination_v2,
        propagate_unresolved_later_domination_v3,
        propagate_unresolved_later_domination_v5,
        target_no_carrier_reset_evidence_status,
    )
    from composite_exclusion_boundary_probe import (
        CANDIDATE_STATUS_REJECTED,
        CANDIDATE_STATUS_RESOLVED_SURVIVOR,
        CANDIDATE_STATUS_UNRESOLVED,
        certified_divisor_class,
        eliminate_candidates,
        first_legal_carrier,
    )
    from offline_pgs_certificate_emitter import first_prime_after
    from resolved_boundary_lock_separator_probe import jsonable


DEFAULT_OUTPUT_DIR = Path("output/prime_inference_generator")
SUMMARY_FILENAME = "graph_v4_failure_bug_audit_summary.json"
RECORD_FILENAME = "graph_v4_failure_bug_audit_record.json"


def build_parser() -> argparse.ArgumentParser:
    """Build the graph v4 failure bug-audit CLI."""
    parser = argparse.ArgumentParser(
        description="Audit the graph v4/v5 scale failure at anchor 10193.",
    )
    parser.add_argument("--anchor", type=int, default=10193)
    parser.add_argument("--candidate-bound", type=int, default=128)
    parser.add_argument("--witness-bound", type=int, default=127)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser


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


def first_prime_after_with_cap(anchor_p: int, cap: int) -> int | None:
    """Return the first audited prime after the anchor within a fixed cap."""
    return next(primerange(anchor_p + 1, cap + 1), None)


def active_offsets(nodes: dict[int, dict[str, Any]], status: str) -> list[int]:
    """Return active offsets for one graph status."""
    return [
        offset
        for offset, node in sorted(nodes.items())
        if node["status"] == status and not bool(node["absorbed"])
    ]


def snapshot_node(node: dict[str, Any]) -> dict[str, Any]:
    """Return one candidate node snapshot."""
    carrier = node["carrier"]
    return {
        "offset": int(node["offset"]),
        "n": int(node["n"]),
        "status": node["status"],
        "absorbed": bool(node["absorbed"]),
        "absorbed_by": node["absorbed_by"],
        "carrier_offset": carrier["carrier_offset"],
        "carrier_d": carrier["carrier_d"],
        "carrier_family": carrier["carrier_family"],
        "single_hole_closure_used": bool(node["single_hole_closure_used"]),
        "unresolved_reasons": list(node["unresolved_reasons"]),
        "rejection_reasons": list(node["rejection_reasons"]),
        "reset_evidence_status": node.get("reset_evidence_status"),
    }


def snapshot_phase(label: str, nodes: dict[int, dict[str, Any]]) -> dict[str, Any]:
    """Return a complete graph snapshot for one phase."""
    candidates = [snapshot_node(node) for _, node in sorted(nodes.items())]
    return {
        "phase": label,
        "resolved_offsets": active_offsets(nodes, CANDIDATE_STATUS_RESOLVED_SURVIVOR),
        "unresolved_offsets": active_offsets(nodes, CANDIDATE_STATUS_UNRESOLVED),
        "rejected_offsets": [
            offset
            for offset, node in sorted(nodes.items())
            if node["status"] == CANDIDATE_STATUS_REJECTED
        ],
        "absorbed_offsets": [
            offset for offset, node in sorted(nodes.items()) if bool(node["absorbed"])
        ],
        "candidates": candidates,
    }


def candidate_by_offset(
    snapshot: dict[str, Any],
    offset: int,
) -> dict[str, Any] | None:
    """Return one candidate snapshot by offset."""
    for candidate in snapshot["candidates"]:
        if int(candidate["offset"]) == offset:
            return candidate
    return None


def status_by_phase(
    phase_snapshots: dict[str, dict[str, Any]],
    offset: int,
) -> dict[str, dict[str, Any] | None]:
    """Return compact status data for one offset across all phases."""
    result: dict[str, dict[str, Any] | None] = {}
    for phase, snapshot in phase_snapshots.items():
        candidate = candidate_by_offset(snapshot, offset)
        if candidate is None:
            result[phase] = None
            continue
        result[phase] = {
            "status": candidate["status"],
            "absorbed": candidate["absorbed"],
            "absorbed_by": candidate["absorbed_by"],
            "rejection_reasons": candidate["rejection_reasons"],
            "unresolved_reasons": candidate["unresolved_reasons"],
            "reset_evidence_status": candidate["reset_evidence_status"],
        }
    return result


def certified_between(
    anchor_p: int,
    source_offset: int,
    target_offset: int,
    witness_bound: int,
) -> list[dict[str, Any]]:
    """Return certified divisor classes between two offsets."""
    rows: list[dict[str, Any]] = []
    for offset in range(source_offset + 1, target_offset):
        certificate = certified_divisor_class(anchor_p + offset, witness_bound)
        if certificate is None:
            continue
        rows.append(
            {
                "offset": offset,
                "n": anchor_p + offset,
                "divisor_class": certificate["divisor_class"],
                "family": certificate["family"],
                "certificate": certificate["certificate"],
            }
        )
    return rows


def active_reset_evidence_between(
    anchor_p: int,
    source_offset: int,
    target_offset: int,
    nodes: dict[int, dict[str, Any]],
    witness_bound: int,
) -> list[dict[str, Any]]:
    """Return certified divisor classes not hidden by active-graph removal."""
    rows: list[dict[str, Any]] = []
    for offset in range(source_offset + 1, target_offset):
        node = nodes.get(offset)
        if node is None:
            continue
        if node["status"] == CANDIDATE_STATUS_REJECTED or bool(node["absorbed"]):
            continue
        certificate = certified_divisor_class(anchor_p + offset, witness_bound)
        if certificate is None:
            continue
        rows.append(
            {
                "offset": offset,
                "n": anchor_p + offset,
                "divisor_class": certificate["divisor_class"],
                "family": certificate["family"],
                "certificate": certificate["certificate"],
            }
        )
    return rows


def ignored_nodes_between(
    source_offset: int,
    target_offset: int,
    nodes: dict[int, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Return rejected or absorbed active-graph nodes between two offsets."""
    rows: list[dict[str, Any]] = []
    for offset in range(source_offset + 1, target_offset):
        node = nodes.get(offset)
        if node is None:
            continue
        if node["status"] != CANDIDATE_STATUS_REJECTED and not bool(node["absorbed"]):
            continue
        rows.append(
            {
                "offset": offset,
                "n": node["n"],
                "status": node["status"],
                "absorbed": bool(node["absorbed"]),
                "absorbed_by": node["absorbed_by"],
                "rejection_reasons": list(node["rejection_reasons"]),
            }
        )
    return rows


def apply_v4_with_log(
    anchor_p: int,
    nodes: dict[int, dict[str, Any]],
    witness_bound: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Apply v4 exactly enough to log each mutation and precondition."""
    relations: list[dict[str, Any]] = []
    steps: list[dict[str, Any]] = []
    while True:
        active_resolved = active_offsets(nodes, CANDIDATE_STATUS_RESOLVED_SURVIVOR)
        if len(active_resolved) != 1:
            break
        source_offset = active_resolved[0]
        source_node = nodes[source_offset]
        if bool(source_node["single_hole_closure_used"]):
            break
        later_unresolved = [
            offset
            for offset in active_offsets(nodes, CANDIDATE_STATUS_UNRESOLVED)
            if offset > source_offset
        ]
        if not later_unresolved:
            break
        target_offset = later_unresolved[0]
        target_carrier = first_legal_carrier(anchor_p, target_offset, witness_bound)
        target_has_legal_carrier = target_carrier["carrier_d"] is not None
        reset_status = "NOT_EVALUATED"
        if not target_has_legal_carrier:
            reset_status = target_no_carrier_reset_evidence_status(
                anchor_p,
                source_offset,
                target_offset,
                source_node["carrier"],
                target_carrier,
                nodes,
                witness_bound,
            )
        step = {
            "source_offset": source_offset,
            "target_offset": target_offset,
            "active_resolved_count": len(active_resolved),
            "source_single_hole_closure_used": bool(
                source_node["single_hole_closure_used"]
            ),
            "target_has_legal_carrier": target_has_legal_carrier,
            "target_no_carrier_reset_status": reset_status,
            "applied": False,
        }
        if target_has_legal_carrier or reset_status != "NO_ACTIVE_RESET_EVIDENCE":
            steps.append(step)
            break

        target_node = nodes[target_offset]
        target_node["status"] = CANDIDATE_STATUS_REJECTED
        target_node["absorbed"] = True
        target_node["absorbed_by"] = source_offset
        target_node["reset_evidence_status"] = reset_status
        target_node["rejection_reasons"].append(
            "UNRESOLVED_LATER_DOMINATION_V4_BY_"
            f"{source_offset}_TARGET_NO_CARRIER_NO_ACTIVE_RESET_EVIDENCE"
        )
        target_node["unresolved_reasons"] = []
        target_node["unresolved_interior_offsets"] = []
        relation = {
            "relation_type": UNRESOLVED_LATER_DOMINATION_V4_RELATION,
            "source_offset": source_offset,
            "target_offset": target_offset,
            "effect": "ABSORBS_NEAREST_LATER_UNRESOLVED_CANDIDATE",
            "reset_evidence_status": reset_status,
            "reasons": [
                "ACTIVE_GRAPH_HAS_ONE_RESOLVED_SURVIVOR",
                "SOURCE_RESOLVED_SURVIVOR",
                "SOURCE_SINGLE_HOLE_CLOSURE_USED_FALSE",
                "TARGET_NEAREST_LATER_UNRESOLVED",
                "TARGET_HAS_NO_LEGAL_CARRIER",
                "NO_ACTIVE_RESET_EVIDENCE_IN_EXISTING_GRAPH_FACTS",
            ],
        }
        relation["preconditions"] = dict(step)
        step["applied"] = True
        relations.append(relation)
        steps.append(step)
    return relations, steps


def run_audit(
    anchor_p: int,
    candidate_bound: int,
    witness_bound: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Run the focused graph v4/v5 failure bug audit."""
    started = time.perf_counter()
    row = base_row(anchor_p, candidate_bound, witness_bound)
    nodes = candidate_nodes(row, witness_bound)
    relations = base_relations(row)
    phase_snapshots: dict[str, dict[str, Any]] = {
        "base": snapshot_phase("base", nodes)
    }

    relations.extend(propagate_005a_r(anchor_p, nodes, witness_bound))
    phase_snapshots["after_005A_R"] = snapshot_phase("after_005A_R", nodes)

    relations.extend(
        propagate_unresolved_later_domination(anchor_p, nodes, witness_bound)
    )
    phase_snapshots["after_v1"] = snapshot_phase("after_v1", nodes)

    relations.extend(
        propagate_unresolved_later_domination_v2(anchor_p, nodes, witness_bound)
    )
    phase_snapshots["after_v2"] = snapshot_phase("after_v2", nodes)

    relations.extend(
        propagate_unresolved_later_domination_v3(anchor_p, nodes, witness_bound)
    )
    phase_snapshots["after_v3"] = snapshot_phase("after_v3", nodes)

    v4_relations, v4_steps = apply_v4_with_log(anchor_p, nodes, witness_bound)
    relations.extend(v4_relations)
    phase_snapshots["after_v4"] = snapshot_phase("after_v4", nodes)

    relations.extend(
        propagate_unresolved_later_domination_v5(anchor_p, nodes, witness_bound)
    )
    phase_snapshots["after_v5"] = snapshot_phase("after_v5", nodes)

    resolved_after_v5 = active_offsets(nodes, CANDIDATE_STATUS_RESOLVED_SURVIVOR)
    unresolved_after_v5 = active_offsets(nodes, CANDIDATE_STATUS_UNRESOLVED)
    solved_after_v5 = len(resolved_after_v5) == 1 and not unresolved_after_v5
    emitted_offset = int(resolved_after_v5[0]) if solved_after_v5 else None
    emitted_q_hat = None if emitted_offset is None else anchor_p + emitted_offset
    actual_next_prime = first_prime_after_with_cap(
        anchor_p,
        anchor_p + max(10_000, candidate_bound * 16),
    )
    actual_offset = None if actual_next_prime is None else actual_next_prime - anchor_p
    audit_first = (
        None if emitted_q_hat is None else first_prime_after(anchor_p, emitted_q_hat)
    )
    relation_that_absorbed_true = None
    if actual_offset is not None:
        for relation in relations:
            if int(relation.get("target_offset") or -1) == actual_offset:
                relation_that_absorbed_true = relation
                break

    false_source_offset = emitted_offset
    true_boundary_offset = actual_offset
    source_for_reset = false_source_offset if false_source_offset is not None else 0
    target_for_reset = true_boundary_offset if true_boundary_offset is not None else 0
    after_v3_nodes = candidate_nodes(row, witness_bound)
    propagate_005a_r(anchor_p, after_v3_nodes, witness_bound)
    propagate_unresolved_later_domination(anchor_p, after_v3_nodes, witness_bound)
    propagate_unresolved_later_domination_v2(anchor_p, after_v3_nodes, witness_bound)
    propagate_unresolved_later_domination_v3(anchor_p, after_v3_nodes, witness_bound)
    target_carrier = first_legal_carrier(anchor_p, target_for_reset, witness_bound)
    target_reset_status = target_no_carrier_reset_evidence_status(
        anchor_p,
        source_for_reset,
        target_for_reset,
        after_v3_nodes[source_for_reset]["carrier"],
        target_carrier,
        after_v3_nodes,
        witness_bound,
    )
    raw_reset = certified_between(
        anchor_p,
        source_for_reset,
        target_for_reset,
        witness_bound,
    )
    active_reset = active_reset_evidence_between(
        anchor_p,
        source_for_reset,
        target_for_reset,
        after_v3_nodes,
        witness_bound,
    )
    ignored_nodes = ignored_nodes_between(source_for_reset, target_for_reset, after_v3_nodes)

    v4_true_step = next(
        (
            step
            for step in v4_steps
            if true_boundary_offset is not None
            and int(step["target_offset"]) == true_boundary_offset
        ),
        None,
    )
    emitted_factorization = (
        None
        if emitted_q_hat is None
        else {str(prime): int(exp) for prime, exp in factorint(emitted_q_hat).items()}
    )
    record = {
        "anchor_p": anchor_p,
        "candidate_bound": candidate_bound,
        "witness_bound": witness_bound,
        "reproduce_failure_bool": (
            emitted_q_hat is not None
            and actual_next_prime is not None
            and emitted_q_hat != actual_next_prime
        ),
        "emitted_q_hat": emitted_q_hat,
        "emitted_offset": emitted_offset,
        "emitted_q_hat_factorization": emitted_factorization,
        "actual_next_prime": actual_next_prime,
        "actual_boundary_offset": actual_offset,
        "emitted_matches_actual_bool": emitted_q_hat == actual_next_prime,
        "relation_that_absorbed_true_boundary": relation_that_absorbed_true,
        "phase_snapshots": phase_snapshots,
        "true_boundary_in_candidate_set": (
            actual_offset in [int(offset) for offset in row["candidate_offsets"]]
        ),
        "true_boundary_status_by_phase": (
            {}
            if actual_offset is None
            else status_by_phase(phase_snapshots, actual_offset)
        ),
        "false_source_offset": false_source_offset,
        "false_source_status_by_phase": (
            {}
            if false_source_offset is None
            else status_by_phase(phase_snapshots, false_source_offset)
        ),
        "v4_target_offset": (
            None if v4_true_step is None else int(v4_true_step["target_offset"])
        ),
        "v4_target_is_true_boundary": v4_true_step is not None,
        "v4_preconditions": {
            "active_resolved_count": None
            if v4_true_step is None
            else int(v4_true_step["active_resolved_count"]),
            "source_single_hole_closure_used": None
            if v4_true_step is None
            else bool(v4_true_step["source_single_hole_closure_used"]),
            "target_has_legal_carrier": None
            if v4_true_step is None
            else bool(v4_true_step["target_has_legal_carrier"]),
            "target_no_carrier_reset_status": None
            if v4_true_step is None
            else v4_true_step["target_no_carrier_reset_status"],
            "active_reset_evidence_status": target_reset_status,
        },
        "v4_steps": v4_steps,
        "raw_reset_evidence_between_source_and_true": raw_reset,
        "active_reset_evidence_between_source_and_true": active_reset,
        "certified_divisor_classes_between_source_and_true": raw_reset,
        "ignored_rejected_or_absorbed_nodes_between_source_and_true": ignored_nodes,
        "audit_backend_confirms_first_boundary": {
            "solver_audit_first_prime_after_anchor_to_emitted": audit_first,
            "independent_first_prime_after_anchor_with_cap": actual_next_prime,
            "audit_checks_first_prime_not_just_primality": True,
        },
        "direct_solve_rejected_offsets": phase_snapshots["after_v5"][
            "rejected_offsets"
        ],
        "direct_solve_absorbed_offsets": phase_snapshots["after_v5"][
            "absorbed_offsets"
        ],
        "direct_solve_resolved_offsets": phase_snapshots["after_v5"][
            "resolved_offsets"
        ],
        "direct_solve_unresolved_offsets": phase_snapshots["after_v5"][
            "unresolved_offsets"
        ],
    }
    bug_checks = {
        "single_anchor_reproduces_range_failure": record["reproduce_failure_bool"],
        "candidate_set_contains_true_boundary": record["true_boundary_in_candidate_set"],
        "audit_checks_first_prime_not_just_primality": True,
        "true_boundary_absorbed_by_v4": (
            relation_that_absorbed_true is not None
            and relation_that_absorbed_true["relation_type"]
            == UNRESOLVED_LATER_DOMINATION_V4_RELATION
        ),
        "v4_ignored_raw_reset_evidence": bool(raw_reset) and not bool(active_reset),
        "v4_absorbed_resolved_candidate": (
            candidate_by_offset(phase_snapshots["after_v3"], target_for_reset)
            is not None
            and candidate_by_offset(phase_snapshots["after_v3"], target_for_reset)[
                "status"
            ]
            == CANDIDATE_STATUS_RESOLVED_SURVIVOR
            and relation_that_absorbed_true is not None
        ),
        "v4_absorbed_unresolved_true_boundary": (
            candidate_by_offset(phase_snapshots["after_v3"], target_for_reset)
            is not None
            and candidate_by_offset(phase_snapshots["after_v3"], target_for_reset)[
                "status"
            ]
            == CANDIDATE_STATUS_UNRESOLVED
            and relation_that_absorbed_true is not None
        ),
    }
    record["bug_checks"] = bug_checks
    likely_cause = (
        "unsafe_v4_relation_active_graph_reset_too_permissive"
        if bug_checks["single_anchor_reproduces_range_failure"]
        and bug_checks["candidate_set_contains_true_boundary"]
        and bug_checks["true_boundary_absorbed_by_v4"]
        and bug_checks["v4_absorbed_unresolved_true_boundary"]
        else "implementation_bug_or_unclassified"
    )
    summary = {
        "mode": "offline_graph_v4_failure_bug_audit",
        "anchor_p": anchor_p,
        "candidate_bound": candidate_bound,
        "witness_bound": witness_bound,
        "reproduce_failure_bool": record["reproduce_failure_bool"],
        "emitted_q_hat": emitted_q_hat,
        "emitted_offset": emitted_offset,
        "actual_next_prime": actual_next_prime,
        "actual_boundary_offset": actual_offset,
        "emitted_matches_actual_bool": record["emitted_matches_actual_bool"],
        "relation_that_absorbed_true_boundary": None
        if relation_that_absorbed_true is None
        else relation_that_absorbed_true["relation_type"],
        "bug_checks": bug_checks,
        "likely_cause": likely_cause,
        "exact_phase_where_true_boundary_is_lost": "after_v4"
        if bug_checks["true_boundary_absorbed_by_v4"]
        else "not_classified",
        "recommended_next_action": (
            "Quarantine v4/v5 outside the last clean surface and design a "
            "label-free v4 reset guard that does not treat absence of active "
            "certified evidence as sufficient for empty-carrier absorption."
        ),
        "production_approved": False,
        "cryptographic_use_approved": False,
        "pure_emission_added": False,
        "solver_rules_changed": False,
        "runtime_seconds": time.perf_counter() - started,
    }
    return record, summary


def write_artifacts(
    record: dict[str, Any],
    summary: dict[str, Any],
    output_dir: Path,
) -> dict[str, Path]:
    """Write LF-terminated bug-audit JSON artifacts."""
    output_dir.mkdir(parents=True, exist_ok=True)
    record_path = output_dir / RECORD_FILENAME
    record_path.write_text(
        json.dumps(jsonable(record), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    summary_path = output_dir / SUMMARY_FILENAME
    summary_path.write_text(
        json.dumps(jsonable(summary), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return {"record_path": record_path, "summary_path": summary_path}


def main(argv: list[str] | None = None) -> int:
    """Run the graph v4 failure bug audit and write artifacts."""
    args = build_parser().parse_args(argv)
    record, summary = run_audit(
        anchor_p=args.anchor,
        candidate_bound=args.candidate_bound,
        witness_bound=args.witness_bound,
    )
    write_artifacts(record, summary, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
