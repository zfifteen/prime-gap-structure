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
        eliminate_candidates,
        first_legal_carrier,
        higher_divisor_pressure_lock_selected,
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
        eliminate_candidates,
        first_legal_carrier,
        higher_divisor_pressure_lock_selected,
    )
    from offline_pgs_certificate_emitter import anchor_primes, first_prime_after
    from resolved_boundary_lock_separator_probe import jsonable


DEFAULT_OUTPUT_DIR = Path("output/prime_inference_generator")
RECORDS_FILENAME = "boundary_certificate_graph_solver_records.jsonl"
SUMMARY_FILENAME = "boundary_certificate_graph_solver_summary.json"
AUDIT_SUMMARY_FILENAME = "boundary_certificate_graph_solver_audit_summary.json"
RULE_SET = "005A-R"
SOLVER_VERSION = "v0"


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


def solve_anchor(
    anchor_p: int,
    candidate_bound: int,
    witness_bound: int,
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
    nodes = candidate_nodes(row, witness_bound)
    relations = base_relations(row)
    relations.extend(propagate_005a_r(anchor_p, nodes, witness_bound))

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
    }
    if not graph_row["solved_bool"]:
        return None, graph_row

    boundary_offset = int(resolved_offsets[0])
    carrier = nodes[boundary_offset]["carrier"]
    record = {
        "record_type": "PGS_INFERRED_PRIME_EXPERIMENTAL_GRAPH",
        "inference_status": "INFERRED_BY_BOUNDARY_CERTIFICATE_GRAPH_V0",
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
        "candidate_count": len(nodes),
    }
    return record, graph_row


def solve_range(
    start_anchor: int,
    max_anchor: int,
    candidate_bound: int,
    witness_bound: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Solve all anchor graphs in the requested inclusive surface."""
    started = time.perf_counter()
    records: list[dict[str, Any]] = []
    graph_rows: list[dict[str, Any]] = []
    for anchor_p in anchor_primes(start_anchor, max_anchor):
        record, graph_row = solve_anchor(anchor_p, candidate_bound, witness_bound)
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
        "production_approved": False,
        "cryptographic_use_approved": False,
        "classical_audit_required": True,
        "classical_audit_status": "NOT_RUN",
        "accepted_rule_families": [
            "positive_composite_rejection",
            "single_hole_positive_witness_closure",
            "carrier_locked_pressure_ceiling",
            "005A_R_locked_absorption",
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
    first_failure: dict[str, Any] | None = None
    for record in records:
        anchor_p = int(record["anchor_p"])
        inferred_prime_q_hat = int(record["inferred_prime_q_hat"])
        first_after_anchor = first_prime_after(anchor_p, inferred_prime_q_hat)
        confirmed = first_after_anchor == inferred_prime_q_hat
        if confirmed:
            confirmed_count += 1
            continue
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

    records, summary = solve_range(
        start_anchor=args.start_anchor,
        max_anchor=args.max_anchor,
        candidate_bound=args.candidate_bound,
        witness_bound=args.witness_bound,
    )
    write_solver_artifacts(records, summary, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
