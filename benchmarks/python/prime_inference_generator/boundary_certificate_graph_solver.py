#!/usr/bin/env python3
"""Boundary-certificate graph solver for accepted PGS exclusion rules."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

try:
    from .composite_exclusion_boundary_probe import (
        CANDIDATE_STATUS_REJECTED,
        CANDIDATE_STATUS_RESOLVED_SURVIVOR,
        CANDIDATE_STATUS_UNRESOLVED,
        WHEEL_OPEN_RESIDUES_MOD30,
        bounded_composite_witness,
        certified_divisor_class,
        eliminate_candidates,
        first_legal_carrier,
        higher_divisor_pressure_lock_selected,
        power_closure_witness,
    )
    from .boundary_certificate_graph_entropy_audit import (
        EntropyAuditWriter,
        StageRecord,
        build_entropy_row,
    )
    from .offline_pgs_certificate_emitter import anchor_primes, first_prime_after
    from .resolved_boundary_lock_separator_probe import jsonable
except ImportError:  # pragma: no cover - direct script execution
    MODULE_DIR = Path(__file__).resolve().parent
    if str(MODULE_DIR) not in sys.path:
        sys.path.insert(0, str(MODULE_DIR))
    from composite_exclusion_boundary_probe import (
        CANDIDATE_STATUS_REJECTED,
        CANDIDATE_STATUS_RESOLVED_SURVIVOR,
        CANDIDATE_STATUS_UNRESOLVED,
        WHEEL_OPEN_RESIDUES_MOD30,
        bounded_composite_witness,
        certified_divisor_class,
        eliminate_candidates,
        first_legal_carrier,
        higher_divisor_pressure_lock_selected,
        power_closure_witness,
    )
    from boundary_certificate_graph_entropy_audit import (
        EntropyAuditWriter,
        StageRecord,
        build_entropy_row,
    )
    from offline_pgs_certificate_emitter import anchor_primes, first_prime_after
    from resolved_boundary_lock_separator_probe import jsonable


DEFAULT_OUTPUT_DIR = Path("output/prime_inference_generator")
RECORDS_FILENAME = "boundary_certificate_graph_solver_records.jsonl"
SUMMARY_FILENAME = "boundary_certificate_graph_solver_summary.json"
AUDIT_SUMMARY_FILENAME = "boundary_certificate_graph_solver_audit_summary.json"
ENTROPY_ROWS_FILENAME = "boundary_certificate_graph_entropy_rows.jsonl"
ENTROPY_STALLS_FILENAME = "boundary_certificate_graph_entropy_stalls.jsonl"
ENTROPY_SUMMARY_FILENAME = "boundary_certificate_graph_entropy_summary.json"
RULE_SET = "005A-R"
SOLVER_VERSION = "v6"
UNRESOLVED_LATER_DOMINATION_RELATION = (
    "unresolved_later_domination_from_existing_graph_facts"
)
UNRESOLVED_LATER_DOMINATION_V2_RELATION = (
    "unresolved_later_domination_from_existing_graph_facts_v2"
)
UNRESOLVED_LATER_DOMINATION_V3_RELATION = (
    "unresolved_later_domination_from_existing_graph_facts_v3"
)
UNRESOLVED_LATER_DOMINATION_V4_RELATION = (
    "unresolved_later_domination_target_no_carrier_reset_discriminator"
)
UNRESOLVED_LATER_DOMINATION_V5_RELATION = (
    "unresolved_later_domination_post_v4_empty_source_carrier_extension"
)
UNRESOLVED_LATER_DOMINATION_REPAIRED_V4_RELATION = (
    "unresolved_later_domination_target_no_carrier_with_positive_nonboundary_guard"
)


def build_parser() -> argparse.ArgumentParser:
    """Build the boundary-certificate graph solver CLI."""
    parser = argparse.ArgumentParser(
        description="Solve experimental PGS boundary certificates by graph propagation.",
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
        "--audit-records",
        type=Path,
        default=None,
        help="Read emitted graph JSONL and write a separate audit summary.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for JSON and JSONL artifacts.",
    )
    return parser


def candidate_nodes(row: dict[str, Any], witness_bound: int) -> dict[int, dict[str, Any]]:
    """Return candidate graph nodes keyed by offset."""
    anchor_p = int(row["anchor_p"])
    nodes: dict[int, dict[str, Any]] = {}
    for record in row["candidate_status_records"]:
        offset = int(record["offset"])
        carrier = first_legal_carrier(anchor_p, offset, witness_bound)
        nodes[offset] = {
            "offset": offset,
            "n": anchor_p + offset,
            "status": str(record["status"]),
            "initial_status": str(record["status"]),
            "absorbed": False,
            "absorbed_by": None,
            "rule_family": record.get("rule_family"),
            "rejection_reasons": list(record["rejection_reasons"]),
            "unresolved_reasons": list(record["unresolved_reasons"]),
            "unresolved_interior_offsets": list(record["unresolved_interior_offsets"]),
            "single_hole_closure_used": bool(
                record.get("single_hole_positive_witness_closure")
            ),
            "closure_reasons": list(record["closure_reasons"]),
            "carrier": carrier,
        }
    return nodes


def base_relations(row: dict[str, Any]) -> list[dict[str, Any]]:
    """Return graph relations already established by accepted eliminator rules."""
    relations: list[dict[str, Any]] = []
    for record in row["candidate_status_records"]:
        offset = int(record["offset"])
        status = str(record["status"])
        rule_family = record.get("rule_family")
        if status == CANDIDATE_STATUS_REJECTED:
            relations.append(
                {
                    "relation_type": str(rule_family or "candidate_rejected"),
                    "source_offset": None,
                    "target_offset": offset,
                    "effect": "REJECTS_CANDIDATE",
                    "reasons": list(record["rejection_reasons"]),
                }
            )
        if bool(record.get("single_hole_positive_witness_closure")):
            relations.append(
                {
                    "relation_type": "single_hole_positive_witness_closure",
                    "source_offset": int(record.get("single_hole_closed_offset")),
                    "target_offset": offset,
                    "effect": "RESOLVES_CANDIDATE",
                    "reasons": list(record["closure_reasons"]),
                }
            )

    ceiling = row["carrier_locked_pressure_ceiling"]
    if bool(ceiling["applied"]):
        for offset in ceiling["pruned_offsets"]:
            relations.append(
                {
                    "relation_type": "carrier_locked_pressure_ceiling",
                    "source_offset": ceiling["threat_offset"],
                    "target_offset": int(offset),
                    "effect": "PRUNES_CANDIDATE",
                    "reasons": [
                        f"CARRIER_LOCKED_PRESSURE_CEILING_BEFORE_{ceiling['threat_offset']}"
                    ],
                }
            )
    return relations


def propagate_005a_r(
    anchor_p: int,
    nodes: dict[int, dict[str, Any]],
    witness_bound: int,
) -> list[dict[str, Any]]:
    """Propagate accepted 005A-R locked absorption until stable."""
    relations: list[dict[str, Any]] = []
    changed = True
    while changed:
        changed = False
        for offset in sorted(nodes):
            node = nodes[offset]
            if node["status"] != CANDIDATE_STATUS_RESOLVED_SURVIVOR:
                continue
            if bool(node["single_hole_closure_used"]):
                continue
            later_unresolved = [
                target_offset
                for target_offset, target_node in sorted(nodes.items())
                if target_offset > offset
                and target_node["status"] == CANDIDATE_STATUS_UNRESOLVED
                and not bool(target_node["absorbed"])
            ]
            if not higher_divisor_pressure_lock_selected(
                anchor_p,
                offset,
                later_unresolved,
                witness_bound,
            ):
                continue
            for target_offset in later_unresolved:
                target_node = nodes[target_offset]
                target_node["status"] = CANDIDATE_STATUS_REJECTED
                target_node["absorbed"] = True
                target_node["absorbed_by"] = offset
                target_node["rejection_reasons"].append(
                    f"005A_R_HIGHER_DIVISOR_LOCKED_ABSORPTION_BY_{offset}"
                )
                target_node["unresolved_reasons"] = []
                target_node["unresolved_interior_offsets"] = []
                relations.append(
                    {
                        "relation_type": "005A_R_locked_absorption",
                        "source_offset": offset,
                        "target_offset": target_offset,
                        "effect": "ABSORBS_LATER_UNRESOLVED_CANDIDATE",
                        "reasons": [
                            f"HIGHER_DIVISOR_PRESSURE_LOCK_BY_{offset}",
                            "SINGLE_HOLE_CLOSURE_USED_FALSE",
                        ],
                    }
                )
                changed = True
    return relations


def carrier_identity(carrier: dict[str, Any]) -> tuple[Any, ...]:
    """Return the comparable identity for one legal carrier."""
    return (
        carrier["carrier_offset"],
        carrier["carrier_d"],
        carrier["carrier_family"],
    )


def reset_evidence_status(
    anchor_p: int,
    source_offset: int,
    target_offset: int,
    source_carrier: dict[str, Any],
    witness_bound: int,
) -> str:
    """Return whether existing graph facts show reset evidence in an extension."""
    source_d = source_carrier["carrier_d"]
    if source_d is None:
        return "UNKNOWN"

    target_carrier = first_legal_carrier(anchor_p, target_offset, witness_bound)
    if carrier_identity(source_carrier) != carrier_identity(target_carrier):
        return "POSITIVE_RESET_EVIDENCE"

    for offset in range(source_offset + 1, target_offset):
        certificate = certified_divisor_class(anchor_p + offset, witness_bound)
        if certificate is None:
            continue
        if int(certificate["divisor_class"]) <= int(source_d):
            return "POSITIVE_RESET_EVIDENCE"
    return "NO_RESET_EVIDENCE"


def active_graph_reset_evidence_status(
    anchor_p: int,
    source_offset: int,
    target_offset: int,
    source_carrier: dict[str, Any],
    nodes: dict[int, dict[str, Any]],
    witness_bound: int,
) -> str:
    """Return reset evidence visible in the active candidate graph."""
    source_d = source_carrier["carrier_d"]
    if source_d is None:
        return "UNKNOWN"

    target_carrier = first_legal_carrier(anchor_p, target_offset, witness_bound)
    if carrier_identity(source_carrier) != carrier_identity(target_carrier):
        return "POSITIVE_RESET_EVIDENCE"

    for offset in range(source_offset + 1, target_offset):
        node = nodes.get(offset)
        if node is None:
            continue
        if node["status"] == CANDIDATE_STATUS_REJECTED or bool(node["absorbed"]):
            continue
        certificate = certified_divisor_class(anchor_p + offset, witness_bound)
        if certificate is None:
            continue
        if int(certificate["divisor_class"]) <= int(source_d):
            return "POSITIVE_RESET_EVIDENCE"
    return "NO_ACTIVE_RESET_EVIDENCE"


def target_no_carrier_reset_evidence_status(
    anchor_p: int,
    source_offset: int,
    target_offset: int,
    source_carrier: dict[str, Any],
    target_carrier: dict[str, Any],
    nodes: dict[int, dict[str, Any]],
    witness_bound: int,
) -> str:
    """Return active reset evidence for a target with no legal carrier."""
    if target_carrier["carrier_d"] is not None:
        return "UNKNOWN"

    source_d = source_carrier["carrier_d"]
    for offset in range(source_offset + 1, target_offset):
        node = nodes.get(offset)
        if node is None:
            continue
        if node["status"] == CANDIDATE_STATUS_REJECTED or bool(node["absorbed"]):
            continue
        certificate = certified_divisor_class(anchor_p + offset, witness_bound)
        if certificate is None:
            continue
        if source_d is None or int(certificate["divisor_class"]) <= int(source_d):
            return "POSITIVE_RESET_EVIDENCE"
    return "NO_ACTIVE_RESET_EVIDENCE"


def propagate_unresolved_later_domination(
    anchor_p: int,
    nodes: dict[int, dict[str, Any]],
    witness_bound: int,
) -> list[dict[str, Any]]:
    """Absorb nearest later unresolved candidates under a no-reset graph fact."""
    relations: list[dict[str, Any]] = []
    changed = True
    while changed:
        changed = False
        for source_offset in sorted(nodes):
            source_node = nodes[source_offset]
            if source_node["status"] != CANDIDATE_STATUS_RESOLVED_SURVIVOR:
                continue
            if bool(source_node["single_hole_closure_used"]):
                continue

            later_unresolved = [
                target_offset
                for target_offset, target_node in sorted(nodes.items())
                if target_offset > source_offset
                and target_node["status"] == CANDIDATE_STATUS_UNRESOLVED
                and not bool(target_node["absorbed"])
            ]
            for target_offset in later_unresolved:
                if any(
                    source_offset < intermediate_offset < target_offset
                    for intermediate_offset in later_unresolved
                ):
                    continue
                reset_status = reset_evidence_status(
                    anchor_p,
                    source_offset,
                    target_offset,
                    source_node["carrier"],
                    witness_bound,
                )
                if reset_status != "NO_RESET_EVIDENCE":
                    continue
                target_node = nodes[target_offset]
                target_node["status"] = CANDIDATE_STATUS_REJECTED
                target_node["absorbed"] = True
                target_node["absorbed_by"] = source_offset
                target_node["reset_evidence_status"] = reset_status
                target_node["rejection_reasons"].append(
                    "UNRESOLVED_LATER_DOMINATION_BY_"
                    f"{source_offset}_NO_RESET_EVIDENCE"
                )
                target_node["unresolved_reasons"] = []
                target_node["unresolved_interior_offsets"] = []
                relations.append(
                    {
                        "relation_type": UNRESOLVED_LATER_DOMINATION_RELATION,
                        "source_offset": source_offset,
                        "target_offset": target_offset,
                        "effect": "ABSORBS_NEAREST_LATER_UNRESOLVED_CANDIDATE",
                        "reset_evidence_status": reset_status,
                        "reasons": [
                            "SOURCE_RESOLVED_SURVIVOR",
                            "SOURCE_SINGLE_HOLE_CLOSURE_USED_FALSE",
                            "TARGET_NEAREST_LATER_UNRESOLVED",
                            "CARRIER_IDENTITY_PRESERVED",
                            "NO_RESET_EVIDENCE_IN_EXISTING_GRAPH_FACTS",
                        ],
                    }
                )
                changed = True
    return relations


def propagate_unresolved_later_domination_v2(
    anchor_p: int,
    nodes: dict[int, dict[str, Any]],
    witness_bound: int,
) -> list[dict[str, Any]]:
    """Absorb nearest later unresolved candidates under active-graph no-reset."""
    relations: list[dict[str, Any]] = []
    changed = True
    while changed:
        changed = False
        for source_offset in sorted(nodes):
            source_node = nodes[source_offset]
            if source_node["status"] != CANDIDATE_STATUS_RESOLVED_SURVIVOR:
                continue
            if bool(source_node["single_hole_closure_used"]):
                continue

            later_unresolved = [
                target_offset
                for target_offset, target_node in sorted(nodes.items())
                if target_offset > source_offset
                and target_node["status"] == CANDIDATE_STATUS_UNRESOLVED
                and not bool(target_node["absorbed"])
            ]
            for target_offset in later_unresolved:
                if any(
                    source_offset < intermediate_offset < target_offset
                    for intermediate_offset in later_unresolved
                ):
                    continue
                reset_status = active_graph_reset_evidence_status(
                    anchor_p,
                    source_offset,
                    target_offset,
                    source_node["carrier"],
                    nodes,
                    witness_bound,
                )
                if reset_status != "NO_ACTIVE_RESET_EVIDENCE":
                    continue
                target_node = nodes[target_offset]
                target_node["status"] = CANDIDATE_STATUS_REJECTED
                target_node["absorbed"] = True
                target_node["absorbed_by"] = source_offset
                target_node["reset_evidence_status"] = reset_status
                target_node["rejection_reasons"].append(
                    "UNRESOLVED_LATER_DOMINATION_V2_BY_"
                    f"{source_offset}_NO_ACTIVE_RESET_EVIDENCE"
                )
                target_node["unresolved_reasons"] = []
                target_node["unresolved_interior_offsets"] = []
                relations.append(
                    {
                        "relation_type": UNRESOLVED_LATER_DOMINATION_V2_RELATION,
                        "source_offset": source_offset,
                        "target_offset": target_offset,
                        "effect": "ABSORBS_NEAREST_LATER_UNRESOLVED_CANDIDATE",
                        "reset_evidence_status": reset_status,
                        "reasons": [
                            "SOURCE_RESOLVED_SURVIVOR",
                            "SOURCE_SINGLE_HOLE_CLOSURE_USED_FALSE",
                            "TARGET_NEAREST_LATER_UNRESOLVED",
                            "CARRIER_IDENTITY_PRESERVED",
                            "NO_ACTIVE_RESET_EVIDENCE_IN_EXISTING_GRAPH_FACTS",
                        ],
                    }
                )
                changed = True
    return relations


def propagate_unresolved_later_domination_v3(
    anchor_p: int,
    nodes: dict[int, dict[str, Any]],
    witness_bound: int,
) -> list[dict[str, Any]]:
    """Absorb nearest later unresolved candidates from empty-carrier sources."""
    relations: list[dict[str, Any]] = []
    changed = True
    while changed:
        changed = False
        active_resolved_offsets = [
            offset
            for offset, node in sorted(nodes.items())
            if node["status"] == CANDIDATE_STATUS_RESOLVED_SURVIVOR
        ]
        if len(active_resolved_offsets) != 1:
            return relations

        for source_offset in active_resolved_offsets:
            source_node = nodes[source_offset]
            if bool(source_node["single_hole_closure_used"]):
                continue
            if source_node["carrier"]["carrier_d"] is not None:
                continue

            later_unresolved = [
                target_offset
                for target_offset, target_node in sorted(nodes.items())
                if target_offset > source_offset
                and target_node["status"] == CANDIDATE_STATUS_UNRESOLVED
                and not bool(target_node["absorbed"])
            ]
            if not later_unresolved:
                continue

            target_offset = later_unresolved[0]
            target_carrier = first_legal_carrier(
                anchor_p,
                target_offset,
                witness_bound,
            )
            if target_carrier["carrier_d"] is None:
                continue
            if int(target_carrier["carrier_offset"]) <= source_offset:
                continue

            target_node = nodes[target_offset]
            target_node["status"] = CANDIDATE_STATUS_REJECTED
            target_node["absorbed"] = True
            target_node["absorbed_by"] = source_offset
            target_node["reset_evidence_status"] = (
                "EMPTY_SOURCE_CARRIER_EXTENSION_FACT"
            )
            target_node["rejection_reasons"].append(
                "UNRESOLVED_LATER_DOMINATION_V3_BY_"
                f"{source_offset}_EMPTY_SOURCE_CARRIER_EXTENSION"
            )
            target_node["unresolved_reasons"] = []
            target_node["unresolved_interior_offsets"] = []
            relations.append(
                {
                    "relation_type": UNRESOLVED_LATER_DOMINATION_V3_RELATION,
                    "source_offset": source_offset,
                    "target_offset": target_offset,
                    "effect": "ABSORBS_NEAREST_LATER_UNRESOLVED_CANDIDATE",
                    "reset_evidence_status": (
                        "EMPTY_SOURCE_CARRIER_EXTENSION_FACT"
                    ),
                    "reasons": [
                        "ACTIVE_GRAPH_HAS_ONE_RESOLVED_SURVIVOR",
                        "SOURCE_RESOLVED_SURVIVOR",
                        "SOURCE_SINGLE_HOLE_CLOSURE_USED_FALSE",
                        "SOURCE_HAS_NO_LEGAL_CARRIER",
                        "TARGET_NEAREST_LATER_UNRESOLVED",
                        "TARGET_HAS_FIRST_LEGAL_CARRIER_AFTER_SOURCE",
                    ],
                }
            )
            changed = True
    return relations


def propagate_unresolved_later_domination_v4(
    anchor_p: int,
    nodes: dict[int, dict[str, Any]],
    witness_bound: int,
) -> list[dict[str, Any]]:
    """Absorb nearest no-carrier unresolved targets with no active reset evidence."""
    relations: list[dict[str, Any]] = []
    changed = True
    while changed:
        changed = False
        active_resolved_offsets = [
            offset
            for offset, node in sorted(nodes.items())
            if node["status"] == CANDIDATE_STATUS_RESOLVED_SURVIVOR
        ]
        if len(active_resolved_offsets) != 1:
            return relations

        source_offset = active_resolved_offsets[0]
        source_node = nodes[source_offset]
        if bool(source_node["single_hole_closure_used"]):
            return relations

        later_unresolved = [
            target_offset
            for target_offset, target_node in sorted(nodes.items())
            if target_offset > source_offset
            and target_node["status"] == CANDIDATE_STATUS_UNRESOLVED
            and not bool(target_node["absorbed"])
        ]
        if not later_unresolved:
            return relations

        target_offset = later_unresolved[0]
        target_carrier = first_legal_carrier(
            anchor_p,
            target_offset,
            witness_bound,
        )
        if target_carrier["carrier_d"] is not None:
            return relations

        reset_status = target_no_carrier_reset_evidence_status(
            anchor_p,
            source_offset,
            target_offset,
            source_node["carrier"],
            target_carrier,
            nodes,
            witness_bound,
        )
        if reset_status != "NO_ACTIVE_RESET_EVIDENCE":
            return relations

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
        relations.append(
            {
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
        )
        changed = True
    return relations


def propagate_unresolved_later_domination_v5(
    anchor_p: int,
    nodes: dict[int, dict[str, Any]],
    witness_bound: int,
) -> list[dict[str, Any]]:
    """Re-evaluate empty-source legal-carrier extension after v4 removals."""
    relations: list[dict[str, Any]] = []
    changed = True
    while changed:
        changed = False
        active_resolved_offsets = [
            offset
            for offset, node in sorted(nodes.items())
            if node["status"] == CANDIDATE_STATUS_RESOLVED_SURVIVOR
        ]
        if len(active_resolved_offsets) != 1:
            return relations

        source_offset = active_resolved_offsets[0]
        source_node = nodes[source_offset]
        if bool(source_node["single_hole_closure_used"]):
            return relations
        if source_node["carrier"]["carrier_d"] is not None:
            return relations

        later_unresolved = [
            target_offset
            for target_offset, target_node in sorted(nodes.items())
            if target_offset > source_offset
            and target_node["status"] == CANDIDATE_STATUS_UNRESOLVED
            and not bool(target_node["absorbed"])
        ]
        if not later_unresolved:
            return relations

        target_offset = later_unresolved[0]
        target_carrier = first_legal_carrier(
            anchor_p,
            target_offset,
            witness_bound,
        )
        if target_carrier["carrier_d"] is None:
            return relations
        if int(target_carrier["carrier_offset"]) <= source_offset:
            return relations

        target_node = nodes[target_offset]
        target_node["status"] = CANDIDATE_STATUS_REJECTED
        target_node["absorbed"] = True
        target_node["absorbed_by"] = source_offset
        target_node["reset_evidence_status"] = (
            "POST_V4_EMPTY_SOURCE_CARRIER_EXTENSION_FACT"
        )
        target_node["rejection_reasons"].append(
            "UNRESOLVED_LATER_DOMINATION_V5_BY_"
            f"{source_offset}_POST_V4_EMPTY_SOURCE_CARRIER_EXTENSION"
        )
        target_node["unresolved_reasons"] = []
        target_node["unresolved_interior_offsets"] = []
        relations.append(
            {
                "relation_type": UNRESOLVED_LATER_DOMINATION_V5_RELATION,
                "source_offset": source_offset,
                "target_offset": target_offset,
                "effect": "ABSORBS_NEAREST_LATER_UNRESOLVED_CANDIDATE",
                "reset_evidence_status": (
                    "POST_V4_EMPTY_SOURCE_CARRIER_EXTENSION_FACT"
                ),
                "reasons": [
                    "ACTIVE_GRAPH_HAS_ONE_RESOLVED_SURVIVOR",
                    "SOURCE_RESOLVED_SURVIVOR",
                    "SOURCE_SINGLE_HOLE_CLOSURE_USED_FALSE",
                    "SOURCE_HAS_NO_LEGAL_CARRIER",
                    "TARGET_NEAREST_LATER_UNRESOLVED",
                    "TARGET_HAS_FIRST_LEGAL_CARRIER_AFTER_SOURCE",
                    "V4_NO_CARRIER_BLOCKERS_REMOVED_BEFORE_REEVALUATION",
                ],
            }
        )
        changed = True
    return relations


def target_beyond_locked_pressure_ceiling(
    row: dict[str, Any],
    target_offset: int,
) -> bool:
    """Return whether a target lies beyond a selected pressure ceiling."""
    ceiling = row["carrier_locked_pressure_ceiling"]
    if not bool(ceiling.get("lock_selected")):
        return False
    threat_offset = ceiling.get("threat_offset")
    if threat_offset is None:
        return False
    return int(target_offset) >= int(threat_offset)


def target_has_positive_nonboundary_certificate(
    anchor_p: int,
    target_offset: int,
    nodes: dict[int, dict[str, Any]],
    row: dict[str, Any],
    witness_bound: int,
) -> bool:
    """Return whether the target has positive non-boundary evidence."""
    target_n = anchor_p + target_offset
    return (
        bounded_composite_witness(target_n) is not None
        or power_closure_witness(target_n) is not None
        or certified_divisor_class(target_n, witness_bound) is not None
        or target_n % 30 not in WHEEL_OPEN_RESIDUES_MOD30
        or nodes[target_offset]["initial_status"] == CANDIDATE_STATUS_REJECTED
        or target_beyond_locked_pressure_ceiling(row, target_offset)
    )


def propagate_unresolved_later_domination_repaired_v4(
    anchor_p: int,
    nodes: dict[int, dict[str, Any]],
    row: dict[str, Any],
    witness_bound: int,
) -> list[dict[str, Any]]:
    """Absorb nearest no-carrier targets only with positive non-boundary evidence."""
    relations: list[dict[str, Any]] = []
    changed = True
    while changed:
        changed = False
        active_resolved_offsets = [
            offset
            for offset, node in sorted(nodes.items())
            if node["status"] == CANDIDATE_STATUS_RESOLVED_SURVIVOR
        ]
        if len(active_resolved_offsets) != 1:
            return relations

        source_offset = active_resolved_offsets[0]
        source_node = nodes[source_offset]
        if bool(source_node["single_hole_closure_used"]):
            return relations

        later_unresolved = [
            target_offset
            for target_offset, target_node in sorted(nodes.items())
            if target_offset > source_offset
            and target_node["status"] == CANDIDATE_STATUS_UNRESOLVED
            and not bool(target_node["absorbed"])
        ]
        if not later_unresolved:
            return relations

        target_offset = later_unresolved[0]
        target_carrier = first_legal_carrier(
            anchor_p,
            target_offset,
            witness_bound,
        )
        if target_carrier["carrier_d"] is not None:
            return relations

        reset_status = target_no_carrier_reset_evidence_status(
            anchor_p,
            source_offset,
            target_offset,
            source_node["carrier"],
            target_carrier,
            nodes,
            witness_bound,
        )
        if reset_status != "NO_ACTIVE_RESET_EVIDENCE":
            return relations
        if not target_has_positive_nonboundary_certificate(
            anchor_p,
            target_offset,
            nodes,
            row,
            witness_bound,
        ):
            return relations

        target_node = nodes[target_offset]
        target_node["status"] = CANDIDATE_STATUS_REJECTED
        target_node["absorbed"] = True
        target_node["absorbed_by"] = source_offset
        target_node["reset_evidence_status"] = reset_status
        target_node["rejection_reasons"].append(
            "REPAIRED_V4_POSITIVE_NONBOUNDARY_BY_"
            f"{source_offset}_TARGET_{target_offset}"
        )
        target_node["unresolved_reasons"] = []
        target_node["unresolved_interior_offsets"] = []
        relations.append(
            {
                "relation_type": UNRESOLVED_LATER_DOMINATION_REPAIRED_V4_RELATION,
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
                    "TARGET_HAS_POSITIVE_NONBOUNDARY_CERTIFICATE",
                ],
            }
        )
        changed = True
    return relations


def relation_count(
    relations: list[dict[str, Any]],
    relation_type: str,
) -> int:
    """Return the count of a relation type in a relation list."""
    return sum(
        1 for relation in relations if relation["relation_type"] == relation_type
    )


def active_offsets_from_records(records: list[dict[str, Any]]) -> list[int]:
    """Return non-rejected candidate offsets from status records."""
    return [
        int(record["offset"])
        for record in records
        if record["status"] != CANDIDATE_STATUS_REJECTED
    ]


def stage_record_from_records(
    stage: str,
    records: list[dict[str, Any]],
) -> StageRecord:
    """Return an entropy stage record from candidate status records."""
    return StageRecord(
        stage=stage,
        active_offsets=active_offsets_from_records(records),
        rejected_offsets=[
            int(record["offset"])
            for record in records
            if record["status"] == CANDIDATE_STATUS_REJECTED
        ],
        resolved_offsets=[
            int(record["offset"])
            for record in records
            if record["status"] == CANDIDATE_STATUS_RESOLVED_SURVIVOR
        ],
        unresolved_offsets=[
            int(record["offset"])
            for record in records
            if record["status"] == CANDIDATE_STATUS_UNRESOLVED
        ],
    )


def stage_record_from_nodes(
    stage: str,
    nodes: dict[int, dict[str, Any]],
) -> StageRecord:
    """Return an entropy stage record from active graph nodes."""
    return StageRecord(
        stage=stage,
        active_offsets=[
            offset
            for offset, node in sorted(nodes.items())
            if node["status"] != CANDIDATE_STATUS_REJECTED
            and not bool(node["absorbed"])
        ],
        rejected_offsets=[
            offset
            for offset, node in sorted(nodes.items())
            if node["status"] == CANDIDATE_STATUS_REJECTED
        ],
        absorbed_offsets=[
            offset for offset, node in sorted(nodes.items()) if bool(node["absorbed"])
        ],
        resolved_offsets=[
            offset
            for offset, node in sorted(nodes.items())
            if node["status"] == CANDIDATE_STATUS_RESOLVED_SURVIVOR
        ],
        unresolved_offsets=[
            offset
            for offset, node in sorted(nodes.items())
            if node["status"] == CANDIDATE_STATUS_UNRESOLVED
            and not bool(node["absorbed"])
        ],
    )


def entropy_base_stage_records(
    anchor_p: int,
    candidate_bound: int,
    witness_bound: int,
    ceiling_row: dict[str, Any],
) -> list[StageRecord]:
    """Return entropy records for the non-mutating base solver stages."""
    positive_row = eliminate_candidates(
        anchor_p,
        candidate_bound,
        enable_single_hole_positive_witness_closure=False,
        witness_bound=witness_bound,
        enable_carrier_locked_pressure_ceiling=False,
        enable_higher_divisor_pressure_locked_absorption=False,
    )
    single_hole_row = eliminate_candidates(
        anchor_p,
        candidate_bound,
        enable_single_hole_positive_witness_closure=True,
        witness_bound=witness_bound,
        enable_carrier_locked_pressure_ceiling=False,
        enable_higher_divisor_pressure_locked_absorption=False,
    )
    return [
        StageRecord(
            "initial",
            active_offsets=list(ceiling_row["candidate_offsets"]),
        ),
        stage_record_from_records(
            "after_positive_composite_rejection",
            positive_row["candidate_status_records"],
        ),
        stage_record_from_records(
            "after_single_hole_positive_witness_closure",
            single_hole_row["candidate_status_records"],
        ),
        stage_record_from_records(
            "after_carrier_locked_pressure_ceiling",
            ceiling_row["candidate_status_records"],
        ),
    ]


def solve_anchor(
    anchor_p: int,
    candidate_bound: int,
    witness_bound: int,
    entropy_writer: EntropyAuditWriter | None = None,
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    """Solve one anchor graph without classical validation."""
    row = eliminate_candidates(
        anchor_p,
        candidate_bound,
        enable_single_hole_positive_witness_closure=True,
        witness_bound=witness_bound,
        enable_carrier_locked_pressure_ceiling=True,
        carrier_lock_predicate="unresolved_alternatives_before_threat",
        enable_higher_divisor_pressure_locked_absorption=False,
    )
    stage_records = entropy_base_stage_records(
        anchor_p,
        candidate_bound,
        witness_bound,
        row,
    )
    nodes = candidate_nodes(row, witness_bound)
    relations = base_relations(row)
    relations.extend(propagate_005a_r(anchor_p, nodes, witness_bound))
    stage_records.append(
        stage_record_from_nodes("after_005A_R_locked_absorption", nodes)
    )
    relations.extend(
        propagate_unresolved_later_domination(anchor_p, nodes, witness_bound)
    )
    stage_records.append(
        stage_record_from_nodes("after_v1_unresolved_later_domination", nodes)
    )
    relations.extend(
        propagate_unresolved_later_domination_v2(anchor_p, nodes, witness_bound)
    )
    stage_records.append(
        stage_record_from_nodes("after_v2_active_graph_reset_refinement", nodes)
    )
    relations.extend(
        propagate_unresolved_later_domination_v3(anchor_p, nodes, witness_bound)
    )
    stage_records.append(
        stage_record_from_nodes("after_v3_empty_source_extension", nodes)
    )
    relations.extend(
        propagate_unresolved_later_domination_repaired_v4(
            anchor_p,
            nodes,
            row,
            witness_bound,
        )
    )
    stage_records.append(
        stage_record_from_nodes(
            "after_repaired_v4_positive_nonboundary_guard",
            nodes,
        )
    )
    stage_records.append(stage_record_from_nodes("final", nodes))

    if entropy_writer is not None:
        entropy_writer.write_row(
            build_entropy_row(
                anchor_p=anchor_p,
                candidate_bound=candidate_bound,
                witness_bound=witness_bound,
                stage_records=stage_records,
            )
        )

    rejected_offsets = [
        offset
        for offset, node in sorted(nodes.items())
        if node["status"] == CANDIDATE_STATUS_REJECTED
    ]
    absorbed_offsets = [
        offset
        for offset, node in sorted(nodes.items())
        if bool(node["absorbed"])
    ]
    resolved_offsets = [
        offset
        for offset, node in sorted(nodes.items())
        if node["status"] == CANDIDATE_STATUS_RESOLVED_SURVIVOR
    ]
    unresolved_offsets = [
        offset
        for offset, node in sorted(nodes.items())
        if node["status"] == CANDIDATE_STATUS_UNRESOLVED
    ]
    graph_row = {
        "anchor_p": anchor_p,
        "candidate_bound": candidate_bound,
        "witness_bound": witness_bound,
        "candidate_offsets": list(row["candidate_offsets"]),
        "relations": relations,
        "rejected_offsets": rejected_offsets,
        "absorbed_offsets": absorbed_offsets,
        "resolved_offsets_after_solve": resolved_offsets,
        "unresolved_offsets_after_solve": unresolved_offsets,
        "solved_bool": len(resolved_offsets) == 1 and not unresolved_offsets,
        "new_relation_applied_count": relation_count(
            relations,
            UNRESOLVED_LATER_DOMINATION_RELATION,
        )
        + relation_count(
            relations,
            UNRESOLVED_LATER_DOMINATION_V2_RELATION,
        )
        + relation_count(
            relations,
            UNRESOLVED_LATER_DOMINATION_V3_RELATION,
        )
        + relation_count(
            relations,
            UNRESOLVED_LATER_DOMINATION_REPAIRED_V4_RELATION,
        ),
        "v1_relation_applied_count": relation_count(
            relations,
            UNRESOLVED_LATER_DOMINATION_RELATION,
        ),
        "v2_relation_applied_count": relation_count(
            relations,
            UNRESOLVED_LATER_DOMINATION_V2_RELATION,
        ),
        "v3_relation_applied_count": relation_count(
            relations,
            UNRESOLVED_LATER_DOMINATION_V3_RELATION,
        ),
        "v4_relation_applied_count": relation_count(
            relations,
            UNRESOLVED_LATER_DOMINATION_V4_RELATION,
        ),
        "v5_relation_applied_count": relation_count(
            relations,
            UNRESOLVED_LATER_DOMINATION_V5_RELATION,
        ),
        "repaired_relation_applied_count": relation_count(
            relations,
            UNRESOLVED_LATER_DOMINATION_REPAIRED_V4_RELATION,
        ),
    }
    if not graph_row["solved_bool"]:
        return None, graph_row

    boundary_offset = int(resolved_offsets[0])
    carrier = nodes[boundary_offset]["carrier"]
    record = {
        "record_type": "PGS_INFERRED_PRIME_EXPERIMENTAL_GRAPH",
        "inference_status": "INFERRED_BY_BOUNDARY_CERTIFICATE_GRAPH_V6",
        "rule_set": RULE_SET,
        "solver_version": SOLVER_VERSION,
        "anchor_p": anchor_p,
        "inferred_prime_q_hat": anchor_p + boundary_offset,
        "boundary_offset": boundary_offset,
        "rule_path": [
            "positive_composite_rejection",
            "single_hole_positive_witness_closure",
            "carrier_locked_pressure_ceiling",
            "005A_R_locked_absorption",
            UNRESOLVED_LATER_DOMINATION_RELATION,
            UNRESOLVED_LATER_DOMINATION_V2_RELATION,
            UNRESOLVED_LATER_DOMINATION_V3_RELATION,
            UNRESOLVED_LATER_DOMINATION_REPAIRED_V4_RELATION,
        ],
        "absorbed_candidates": absorbed_offsets,
        "rejected_candidates": rejected_offsets,
        "resolved_candidates_after_solve": resolved_offsets,
        "unresolved_candidates_after_solve": unresolved_offsets,
        "production_approved": False,
        "cryptographic_use_approved": False,
        "classical_audit_required": True,
        "classical_audit_status": "NOT_RUN",
        "candidate_bound": candidate_bound,
        "witness_bound": witness_bound,
        "gwr_carrier": carrier["carrier_w"],
        "gwr_carrier_offset": carrier["carrier_offset"],
        "gwr_carrier_d": carrier["carrier_d"],
        "gwr_carrier_family": carrier["carrier_family"],
        "relation_count": len(relations),
        "new_relation_applied_count": relation_count(
            relations,
            UNRESOLVED_LATER_DOMINATION_RELATION,
        )
        + relation_count(
            relations,
            UNRESOLVED_LATER_DOMINATION_V2_RELATION,
        )
        + relation_count(
            relations,
            UNRESOLVED_LATER_DOMINATION_V3_RELATION,
        )
        + relation_count(
            relations,
            UNRESOLVED_LATER_DOMINATION_REPAIRED_V4_RELATION,
        ),
        "v1_relation_applied_count": relation_count(
            relations,
            UNRESOLVED_LATER_DOMINATION_RELATION,
        ),
        "v2_relation_applied_count": relation_count(
            relations,
            UNRESOLVED_LATER_DOMINATION_V2_RELATION,
        ),
        "v3_relation_applied_count": relation_count(
            relations,
            UNRESOLVED_LATER_DOMINATION_V3_RELATION,
        ),
        "v4_relation_applied_count": relation_count(
            relations,
            UNRESOLVED_LATER_DOMINATION_V4_RELATION,
        ),
        "v5_relation_applied_count": relation_count(
            relations,
            UNRESOLVED_LATER_DOMINATION_V5_RELATION,
        ),
        "repaired_relation_applied_count": relation_count(
            relations,
            UNRESOLVED_LATER_DOMINATION_REPAIRED_V4_RELATION,
        ),
        "candidate_count": len(nodes),
    }
    return record, graph_row


def solve_range(
    start_anchor: int,
    max_anchor: int,
    candidate_bound: int,
    witness_bound: int,
    entropy_writer: EntropyAuditWriter | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Solve all anchor graphs in the requested inclusive surface."""
    started = time.perf_counter()
    records: list[dict[str, Any]] = []
    graph_rows: list[dict[str, Any]] = []
    for anchor_p in anchor_primes(start_anchor, max_anchor):
        record, graph_row = solve_anchor(
            anchor_p,
            candidate_bound,
            witness_bound,
            entropy_writer=entropy_writer,
        )
        graph_rows.append(graph_row)
        if record is not None:
            records.append(record)

    summary = {
        "record_type": "PGS_GRAPH_SOLVER_SUMMARY",
        "mode": "offline_boundary_certificate_graph_solver",
        "rule_set": RULE_SET,
        "solver_version": SOLVER_VERSION,
        "anchor_range": f"{start_anchor}..{max_anchor}",
        "candidate_bound": candidate_bound,
        "witness_bound": witness_bound,
        "graph_solved_count": len(records),
        "abstain_count": len(graph_rows) - len(records),
        "graph_abstain_count": len(graph_rows) - len(records),
        "new_relation_applied_count": sum(
            int(row["new_relation_applied_count"]) for row in graph_rows
        ),
        "new_relation_solution_count": sum(
            1
            for record in records
            if int(record["new_relation_applied_count"]) > 0
        ),
        "v1_relation_applied_count": sum(
            int(row["v1_relation_applied_count"]) for row in graph_rows
        ),
        "v2_relation_applied_count": sum(
            int(row["v2_relation_applied_count"]) for row in graph_rows
        ),
        "v2_relation_solution_count": sum(
            1
            for record in records
            if int(record["v2_relation_applied_count"]) > 0
        ),
        "v3_relation_applied_count": sum(
            int(row["v3_relation_applied_count"]) for row in graph_rows
        ),
        "v3_relation_solution_count": sum(
            1
            for record in records
            if int(record["v3_relation_applied_count"]) > 0
        ),
        "v4_relation_applied_count": sum(
            int(row["v4_relation_applied_count"]) for row in graph_rows
        ),
        "v4_relation_solution_count": sum(
            1
            for record in records
            if int(record["v4_relation_applied_count"]) > 0
        ),
        "v5_relation_applied_count": sum(
            int(row["v5_relation_applied_count"]) for row in graph_rows
        ),
        "v5_relation_solution_count": sum(
            1
            for record in records
            if int(record["v5_relation_applied_count"]) > 0
        ),
        "repaired_relation_applied_count": sum(
            int(row["repaired_relation_applied_count"]) for row in graph_rows
        ),
        "repaired_relation_solution_count": sum(
            1
            for record in records
            if int(record["repaired_relation_applied_count"]) > 0
        ),
        "production_approved": False,
        "cryptographic_use_approved": False,
        "classical_audit_required": True,
        "classical_audit_status": "NOT_RUN",
        "entropy_audit_rows": ENTROPY_ROWS_FILENAME,
        "entropy_audit_stalls": ENTROPY_STALLS_FILENAME,
        "entropy_audit_summary": ENTROPY_SUMMARY_FILENAME,
        "accepted_rule_families": [
            "positive_composite_rejection",
            "single_hole_positive_witness_closure",
            "carrier_locked_pressure_ceiling",
            "005A_R_locked_absorption",
            UNRESOLVED_LATER_DOMINATION_RELATION,
            UNRESOLVED_LATER_DOMINATION_V2_RELATION,
            UNRESOLVED_LATER_DOMINATION_V3_RELATION,
            UNRESOLVED_LATER_DOMINATION_REPAIRED_V4_RELATION,
        ],
        "wrong_count": None,
        "first_failure": None,
        "runtime_seconds": time.perf_counter() - started,
    }
    return records, summary


def write_solver_artifacts(
    records: list[dict[str, Any]],
    summary: dict[str, Any],
    output_dir: Path,
) -> dict[str, Path]:
    """Write LF-terminated graph-solver JSONL and summary JSON."""
    output_dir.mkdir(parents=True, exist_ok=True)
    records_path = output_dir / RECORDS_FILENAME
    with records_path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(jsonable(record), sort_keys=True) + "\n")

    summary_path = output_dir / SUMMARY_FILENAME
    summary_path.write_text(
        json.dumps(jsonable(summary), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return {
        "records_path": records_path,
        "summary_path": summary_path,
    }


def audit_graph_records(records_path: Path) -> dict[str, Any]:
    """Audit graph-emitted records after emission using classical validation."""
    started = time.perf_counter()
    records = [
        json.loads(line)
        for line in records_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    confirmed_count = 0
    new_relation_correct_count = 0
    new_relation_wrong_count = 0
    v2_relation_correct_count = 0
    v2_relation_wrong_count = 0
    v3_relation_correct_count = 0
    v3_relation_wrong_count = 0
    v4_relation_correct_count = 0
    v4_relation_wrong_count = 0
    v5_relation_correct_count = 0
    v5_relation_wrong_count = 0
    repaired_relation_correct_count = 0
    repaired_relation_wrong_count = 0
    first_failure: dict[str, Any] | None = None
    for record in records:
        anchor_p = int(record["anchor_p"])
        inferred_prime_q_hat = int(record["inferred_prime_q_hat"])
        first_after_anchor = first_prime_after(anchor_p, inferred_prime_q_hat)
        confirmed = first_after_anchor == inferred_prime_q_hat
        used_new_relation = int(record.get("new_relation_applied_count", 0)) > 0
        used_v2_relation = int(record.get("v2_relation_applied_count", 0)) > 0
        used_v3_relation = int(record.get("v3_relation_applied_count", 0)) > 0
        used_v4_relation = int(record.get("v4_relation_applied_count", 0)) > 0
        used_v5_relation = int(record.get("v5_relation_applied_count", 0)) > 0
        used_repaired_relation = (
            int(record.get("repaired_relation_applied_count", 0)) > 0
        )
        if confirmed:
            confirmed_count += 1
            if used_new_relation:
                new_relation_correct_count += 1
            if used_v2_relation:
                v2_relation_correct_count += 1
            if used_v3_relation:
                v3_relation_correct_count += 1
            if used_v4_relation:
                v4_relation_correct_count += 1
            if used_v5_relation:
                v5_relation_correct_count += 1
            if used_repaired_relation:
                repaired_relation_correct_count += 1
            continue
        if used_new_relation:
            new_relation_wrong_count += 1
        if used_v2_relation:
            v2_relation_wrong_count += 1
        if used_v3_relation:
            v3_relation_wrong_count += 1
        if used_v4_relation:
            v4_relation_wrong_count += 1
        if used_v5_relation:
            v5_relation_wrong_count += 1
        if used_repaired_relation:
            repaired_relation_wrong_count += 1
        if first_failure is None:
            first_failure = {
                "anchor_p": anchor_p,
                "inferred_prime_q_hat": inferred_prime_q_hat,
                "first_prime_after_anchor": first_after_anchor,
            }
    audited_count = len(records)
    failed_count = audited_count - confirmed_count
    return {
        "audited_count": audited_count,
        "confirmed_count": confirmed_count,
        "failed_count": failed_count,
        "new_relation_correct_count_after_audit": new_relation_correct_count,
        "new_relation_wrong_count_after_audit": new_relation_wrong_count,
        "v2_relation_correct_count_after_audit": v2_relation_correct_count,
        "v2_relation_wrong_count_after_audit": v2_relation_wrong_count,
        "v3_relation_correct_count_after_audit": v3_relation_correct_count,
        "v3_relation_wrong_count_after_audit": v3_relation_wrong_count,
        "v4_relation_correct_count_after_audit": v4_relation_correct_count,
        "v4_relation_wrong_count_after_audit": v4_relation_wrong_count,
        "v5_relation_correct_count_after_audit": v5_relation_correct_count,
        "v5_relation_wrong_count_after_audit": v5_relation_wrong_count,
        "repaired_relation_correct_count_after_audit": (
            repaired_relation_correct_count
        ),
        "repaired_relation_wrong_count_after_audit": repaired_relation_wrong_count,
        "first_failure": first_failure,
        "validation_backend": "sympy.primerange_first_boundary",
        "runtime_seconds": time.perf_counter() - started,
    }


def write_audit_summary(summary: dict[str, Any], output_dir: Path) -> Path:
    """Write the LF-terminated graph audit summary JSON."""
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = output_dir / AUDIT_SUMMARY_FILENAME
    summary_path.write_text(
        json.dumps(jsonable(summary), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return summary_path


def main(argv: list[str] | None = None) -> int:
    """Run graph solving or downstream graph-record audit."""
    args = build_parser().parse_args(argv)
    if args.audit_records is not None:
        audit_summary = audit_graph_records(args.audit_records)
        write_audit_summary(audit_summary, args.output_dir)
        return 0

    with EntropyAuditWriter(args.output_dir) as entropy_writer:
        records, summary = solve_range(
            start_anchor=args.start_anchor,
            max_anchor=args.max_anchor,
            candidate_bound=args.candidate_bound,
            witness_bound=args.witness_bound,
            entropy_writer=entropy_writer,
        )
    write_solver_artifacts(records, summary, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
