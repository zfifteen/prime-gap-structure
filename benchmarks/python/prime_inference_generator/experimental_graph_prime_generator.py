#!/usr/bin/env python3
"""Experimental PGS graph prime generator CLI."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

try:
    from .boundary_certificate_graph_solver import (
        RULE_SET,
        UNRESOLVED_LATER_DOMINATION_RELATION,
        UNRESOLVED_LATER_DOMINATION_REPAIRED_V4_RELATION,
        UNRESOLVED_LATER_DOMINATION_V2_RELATION,
        UNRESOLVED_LATER_DOMINATION_V3_RELATION,
        UNRESOLVED_LATER_DOMINATION_V4_RELATION,
        UNRESOLVED_LATER_DOMINATION_V5_RELATION,
        base_relations,
        candidate_nodes,
        propagate_005a_r,
        propagate_unresolved_later_domination,
        propagate_unresolved_later_domination_repaired_v4,
        propagate_unresolved_later_domination_v2,
        propagate_unresolved_later_domination_v3,
        propagate_unresolved_later_domination_v4,
        propagate_unresolved_later_domination_v5,
        relation_count,
    )
    from .composite_exclusion_boundary_probe import (
        CANDIDATE_STATUS_REJECTED,
        CANDIDATE_STATUS_RESOLVED_SURVIVOR,
        CANDIDATE_STATUS_UNRESOLVED,
        WHEEL_OPEN_RESIDUES_MOD30,
        bounded_composite_witness,
        certified_divisor_class,
        eliminate_candidates,
        power_closure_witness,
    )
    from .offline_pgs_certificate_emitter import anchor_primes, first_prime_after
    from .resolved_boundary_lock_separator_probe import jsonable
except ImportError:  # pragma: no cover - direct script execution
    MODULE_DIR = Path(__file__).resolve().parent
    if str(MODULE_DIR) not in sys.path:
        sys.path.insert(0, str(MODULE_DIR))
    from boundary_certificate_graph_solver import (
        RULE_SET,
        UNRESOLVED_LATER_DOMINATION_RELATION,
        UNRESOLVED_LATER_DOMINATION_REPAIRED_V4_RELATION,
        UNRESOLVED_LATER_DOMINATION_V2_RELATION,
        UNRESOLVED_LATER_DOMINATION_V3_RELATION,
        UNRESOLVED_LATER_DOMINATION_V4_RELATION,
        UNRESOLVED_LATER_DOMINATION_V5_RELATION,
        base_relations,
        candidate_nodes,
        propagate_005a_r,
        propagate_unresolved_later_domination,
        propagate_unresolved_later_domination_repaired_v4,
        propagate_unresolved_later_domination_v2,
        propagate_unresolved_later_domination_v3,
        propagate_unresolved_later_domination_v4,
        propagate_unresolved_later_domination_v5,
        relation_count,
    )
    from composite_exclusion_boundary_probe import (
        CANDIDATE_STATUS_REJECTED,
        CANDIDATE_STATUS_RESOLVED_SURVIVOR,
        CANDIDATE_STATUS_UNRESOLVED,
        WHEEL_OPEN_RESIDUES_MOD30,
        bounded_composite_witness,
        certified_divisor_class,
        eliminate_candidates,
        power_closure_witness,
    )
    from offline_pgs_certificate_emitter import anchor_primes, first_prime_after
    from resolved_boundary_lock_separator_probe import jsonable


DEFAULT_OUTPUT_DIR = Path("output/prime_inference_generator")
RECORDS_FILENAME = "experimental_graph_prime_generator_records.jsonl"
SUMMARY_FILENAME = "experimental_graph_prime_generator_summary.json"
AUDIT_SUMMARY_FILENAME = "experimental_graph_prime_generator_audit_summary.json"
SOLVER_VERSIONS = ("v3", "v6", "risky-v5", "filtered-v5")


def build_parser() -> argparse.ArgumentParser:
    """Build the experimental graph generator CLI."""
    parser = argparse.ArgumentParser(
        description="Emit experimental PGS graph inferred-prime records.",
    )
    parser.add_argument("--solver-version", choices=SOLVER_VERSIONS, default="v6")
    parser.add_argument("--start-anchor", type=int, default=11)
    parser.add_argument("--max-anchor", type=int, default=100_000)
    parser.add_argument("--candidate-bound", type=int, default=128)
    parser.add_argument("--witness-bound", type=int, default=127)
    parser.add_argument("--emit-target", type=int, default=None)
    parser.add_argument("--audit", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser


def relation_counts(relations: list[dict[str, Any]]) -> dict[str, int]:
    """Return the relation counters exposed on generator records."""
    return {
        "new_relation_applied_count": (
            relation_count(relations, UNRESOLVED_LATER_DOMINATION_RELATION)
            + relation_count(relations, UNRESOLVED_LATER_DOMINATION_V2_RELATION)
            + relation_count(relations, UNRESOLVED_LATER_DOMINATION_V3_RELATION)
            + relation_count(relations, UNRESOLVED_LATER_DOMINATION_V4_RELATION)
            + relation_count(relations, UNRESOLVED_LATER_DOMINATION_V5_RELATION)
            + relation_count(
                relations,
                UNRESOLVED_LATER_DOMINATION_REPAIRED_V4_RELATION,
            )
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


def positive_nonboundary_filter_reasons(
    candidate_q_hat: int,
    witness_bound: int,
) -> list[str]:
    """Return label-free positive reasons that disqualify an emitted candidate."""
    reasons: list[str] = []
    if (
        bounded_composite_witness(candidate_q_hat) is not None
        or bounded_divisor_witness(candidate_q_hat, witness_bound) is not None
    ):
        reasons.append("bounded_composite_witness")
    if power_closure_witness(candidate_q_hat) is not None:
        reasons.append("power_witness")
    if certified_divisor_class(candidate_q_hat, witness_bound) is not None:
        reasons.append("certified_divisor_class_nonboundary_certificate")
    if candidate_q_hat % 30 not in WHEEL_OPEN_RESIDUES_MOD30:
        reasons.append("wheel_closed_status")
    return reasons


def bounded_divisor_witness(candidate_q_hat: int, witness_bound: int) -> int | None:
    """Return a concrete divisor within the active witness bound, if present."""
    for factor in range(2, witness_bound + 1):
        if factor < candidate_q_hat and candidate_q_hat % factor == 0:
            return factor
    return None


def solve_anchor_for_version(
    anchor_p: int,
    candidate_bound: int,
    witness_bound: int,
    solver_version: str,
) -> dict[str, Any] | None:
    """Return one experimental graph record, or None when the graph abstains."""
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
    relations.extend(
        propagate_unresolved_later_domination(anchor_p, nodes, witness_bound)
    )
    relations.extend(
        propagate_unresolved_later_domination_v2(anchor_p, nodes, witness_bound)
    )
    relations.extend(
        propagate_unresolved_later_domination_v3(anchor_p, nodes, witness_bound)
    )
    effective_solver_version = "risky-v5" if solver_version == "filtered-v5" else solver_version
    if effective_solver_version == "v6":
        relations.extend(
            propagate_unresolved_later_domination_repaired_v4(
                anchor_p,
                nodes,
                row,
                witness_bound,
            )
        )
    if effective_solver_version == "risky-v5":
        relations.extend(
            propagate_unresolved_later_domination_v4(
                anchor_p,
                nodes,
                witness_bound,
            )
        )
        relations.extend(
            propagate_unresolved_later_domination_v5(
                anchor_p,
                nodes,
                witness_bound,
            )
        )

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
    if len(resolved_offsets) != 1 or unresolved_offsets:
        return None

    boundary_offset = int(resolved_offsets[0])
    carrier = nodes[boundary_offset]["carrier"]
    return {
        "record_type": "PGS_INFERRED_PRIME_EXPERIMENTAL_GRAPH",
        "inference_status": (
            "INFERRED_BY_BOUNDARY_CERTIFICATE_GRAPH_"
            + solver_version.upper().replace("-", "_")
        ),
        "rule_set": RULE_SET,
        "solver_version": effective_solver_version,
        "anchor_p": anchor_p,
        "inferred_prime_q_hat": anchor_p + boundary_offset,
        "boundary_offset": boundary_offset,
        "absorbed_candidates": [
            offset for offset, node in sorted(nodes.items()) if bool(node["absorbed"])
        ],
        "rejected_candidates": [
            offset
            for offset, node in sorted(nodes.items())
            if node["status"] == CANDIDATE_STATUS_REJECTED
        ],
        "resolved_candidates_after_solve": resolved_offsets,
        "unresolved_candidates_after_solve": unresolved_offsets,
        "production_approved": False,
        "cryptographic_use_approved": False,
        "audit_required": True,
        "classical_audit_required": True,
        "classical_audit_status": "NOT_RUN",
        "candidate_bound": candidate_bound,
        "witness_bound": witness_bound,
        "gwr_carrier": carrier["carrier_w"],
        "gwr_carrier_offset": carrier["carrier_offset"],
        "gwr_carrier_d": carrier["carrier_d"],
        "gwr_carrier_family": carrier["carrier_family"],
        **relation_counts(relations),
    }


def emit_records(
    solver_version: str,
    start_anchor: int,
    max_anchor: int,
    candidate_bound: int,
    witness_bound: int,
    emit_target: int | None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Emit graph records for one solver version."""
    started = time.perf_counter()
    records: list[dict[str, Any]] = []
    seen: set[tuple[int, int]] = set()
    filter_reason_counts: dict[str, int] = {}
    first_filtered_examples: list[dict[str, Any]] = []
    risky_input_count = 0
    filtered_count = 0
    anchors_scanned = 0
    final_anchor_scanned: int | None = None
    for anchor_p in anchor_primes(start_anchor, max_anchor):
        anchors_scanned += 1
        final_anchor_scanned = anchor_p
        record = solve_anchor_for_version(
            anchor_p,
            candidate_bound,
            witness_bound,
            solver_version,
        )
        if record is None:
            continue
        if solver_version == "filtered-v5":
            risky_input_count += 1
            filter_reasons = positive_nonboundary_filter_reasons(
                int(record["inferred_prime_q_hat"]),
                witness_bound,
            )
            if filter_reasons:
                filtered_count += 1
                for reason in filter_reasons:
                    filter_reason_counts[reason] = (
                        filter_reason_counts.get(reason, 0) + 1
                    )
                if len(first_filtered_examples) < 20:
                    first_filtered_examples.append(
                        {
                            "anchor_p": int(record["anchor_p"]),
                            "inferred_prime_q_hat": int(
                                record["inferred_prime_q_hat"]
                            ),
                            "boundary_offset": int(record["boundary_offset"]),
                            "filter_status": (
                                "FILTERED_POSITIVE_NONBOUNDARY_CANDIDATE"
                            ),
                            "filter_reasons": filter_reasons,
                        }
                    )
                continue
            record["solver_version"] = "filtered-v5"
            record["inference_status"] = (
                "INFERRED_BY_BOUNDARY_CERTIFICATE_GRAPH_FILTERED_V5"
            )
            record["filter_status"] = "PASSED_POSITIVE_NONBOUNDARY_FILTER"
            record["filter_reasons"] = []
        key = (int(record["anchor_p"]), int(record["inferred_prime_q_hat"]))
        if key in seen:
            continue
        seen.add(key)
        records.append(record)
        if emit_target is not None and len(records) >= emit_target:
            break

    abstained_count = anchors_scanned - len(records)
    summary = {
        "record_type": "PGS_EXPERIMENTAL_GRAPH_GENERATOR_SUMMARY",
        "mode": "experimental_graph_prime_generator",
        "rule_set": RULE_SET,
        "solver_version": solver_version,
        "start_anchor": start_anchor,
        "max_anchor": max_anchor,
        "final_anchor_scanned": final_anchor_scanned,
        "candidate_bound": candidate_bound,
        "witness_bound": witness_bound,
        "emit_target": emit_target,
        "anchors_scanned": anchors_scanned,
        "emitted_count": len(records),
        "abstained_count": abstained_count,
        "coverage_rate": 0.0 if anchors_scanned == 0 else len(records) / anchors_scanned,
        "risky_input_count": risky_input_count
        if solver_version == "filtered-v5"
        else None,
        "filtered_count": filtered_count if solver_version == "filtered-v5" else 0,
        "filter_reason_counts": filter_reason_counts,
        "first_filtered_examples": first_filtered_examples,
        "audit_required": True,
        "audit_confirmed": None,
        "audit_failed": None,
        "first_failure": None,
        "production_approved": False,
        "cryptographic_use_approved": False,
        "runtime_seconds": time.perf_counter() - started,
    }
    return records, summary


def audit_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Audit emitted graph records after emission."""
    started = time.perf_counter()
    confirmed_count = 0
    first_failure: dict[str, Any] | None = None
    for record in records:
        anchor_p = int(record["anchor_p"])
        inferred_prime_q_hat = int(record["inferred_prime_q_hat"])
        first_after_anchor = first_prime_after(anchor_p, inferred_prime_q_hat)
        if first_after_anchor == inferred_prime_q_hat:
            confirmed_count += 1
            continue
        if first_failure is None:
            first_failure = {
                "anchor_p": anchor_p,
                "inferred_prime_q_hat": inferred_prime_q_hat,
                "first_prime_after_anchor": first_after_anchor,
            }
    audited_count = len(records)
    return {
        "audited_count": audited_count,
        "confirmed_count": confirmed_count,
        "failed_count": audited_count - confirmed_count,
        "first_failure": first_failure,
        "validation_backend": "sympy.primerange_first_boundary",
        "runtime_seconds": time.perf_counter() - started,
    }


def write_artifacts(
    records: list[dict[str, Any]],
    summary: dict[str, Any],
    audit_summary: dict[str, Any] | None,
    output_dir: Path,
) -> dict[str, Path]:
    """Write LF-terminated generator artifacts."""
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
    paths = {"records_path": records_path, "summary_path": summary_path}
    if audit_summary is not None:
        audit_path = output_dir / AUDIT_SUMMARY_FILENAME
        audit_path.write_text(
            json.dumps(jsonable(audit_summary), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        paths["audit_summary_path"] = audit_path
    return paths


def main(argv: list[str] | None = None) -> int:
    """Run the experimental graph prime generator."""
    args = build_parser().parse_args(argv)
    records, summary = emit_records(
        solver_version=args.solver_version,
        start_anchor=args.start_anchor,
        max_anchor=args.max_anchor,
        candidate_bound=args.candidate_bound,
        witness_bound=args.witness_bound,
        emit_target=args.emit_target,
    )
    audit_summary = None
    if args.audit:
        audit_summary = audit_records(records)
        summary["audit_confirmed"] = audit_summary["confirmed_count"]
        summary["audit_failed"] = audit_summary["failed_count"]
        summary["first_failure"] = audit_summary["first_failure"]
    write_artifacts(records, summary, audit_summary, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
