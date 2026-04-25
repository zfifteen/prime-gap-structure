#!/usr/bin/env python3
"""Offline PGS boundary certificate emitter for the 005A-R candidate rule."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

from sympy import primerange

try:
    from .composite_exclusion_boundary_probe import eliminate_candidates
    from .higher_divisor_pressure_lock_hardening import (
        has_higher_divisor_pressure,
    )
    from .resolved_boundary_absorption_safety_probe import candidate_carrier
    from .resolved_boundary_lock_separator_probe import (
        candidate_record_by_offset,
        jsonable,
    )
except ImportError:  # pragma: no cover - direct script execution
    MODULE_DIR = Path(__file__).resolve().parent
    if str(MODULE_DIR) not in sys.path:
        sys.path.insert(0, str(MODULE_DIR))
    from composite_exclusion_boundary_probe import eliminate_candidates
    from higher_divisor_pressure_lock_hardening import (
        has_higher_divisor_pressure,
    )
    from resolved_boundary_absorption_safety_probe import candidate_carrier
    from resolved_boundary_lock_separator_probe import (
        candidate_record_by_offset,
        jsonable,
    )


DEFAULT_OUTPUT_DIR = Path("output/prime_inference_generator")
CERTIFICATES_FILENAME = "offline_pgs_boundary_certificates.jsonl"
SUMMARY_FILENAME = "offline_pgs_certificate_emitter_summary.json"
AUDIT_SUMMARY_FILENAME = "offline_pgs_certificate_audit_summary.json"
RULE_SET = "005A-R"


def build_parser() -> argparse.ArgumentParser:
    """Build the offline certificate emitter CLI."""
    parser = argparse.ArgumentParser(
        description="Emit or audit offline PGS boundary certificates.",
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
        default=1_000_000,
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
        "--audit-certificates",
        type=Path,
        default=None,
        help="Read emitted certificate JSONL and write an audit summary.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for JSON and JSONL artifacts.",
    )
    return parser


def anchor_primes(start_anchor: int, max_anchor: int) -> list[int]:
    """Return known anchor primes in the requested inclusive range."""
    return [
        int(anchor)
        for anchor in primerange(start_anchor, max_anchor + 1)
    ]


def unique_resolved_survivor_offset(row: dict[str, Any]) -> int | None:
    """Return the unique resolved survivor offset, if the row has one."""
    survivors = [int(offset) for offset in row["survivors"]]
    unresolved = [int(offset) for offset in row["unresolved"]]
    if len(survivors) == 1 and not unresolved:
        return survivors[0]
    return None


def certificate_from_activation(
    pre_row: dict[str, Any],
    post_row: dict[str, Any],
    resolved_offset: int,
    candidate_bound: int,
    witness_bound: int,
) -> dict[str, Any]:
    """Build one offline certificate record from a selected 005A-R activation."""
    anchor_p = int(pre_row["anchor_p"])
    carrier = candidate_carrier(anchor_p, resolved_offset, witness_bound)
    absorbed_offsets = [
        int(offset)
        for offset in post_row["higher_divisor_pressure_locked_absorption"][
            "absorbed_offsets"
        ]
    ]
    return {
        "record_type": "OFFLINE_PGS_BOUNDARY_CERTIFICATE",
        "certificate_status": "CANDIDATE_CERTIFICATE",
        "pure_emission_approved": False,
        "classical_audit_status": "NOT_RUN",
        "anchor_p": anchor_p,
        "candidate_q_hat": anchor_p + resolved_offset,
        "boundary_offset": resolved_offset,
        "rule_set": RULE_SET,
        "candidate_bound": candidate_bound,
        "witness_bound": witness_bound,
        "gwr_carrier": carrier["carrier_w"],
        "gwr_carrier_offset": carrier["carrier_offset"],
        "gwr_carrier_d": carrier["carrier_d"],
        "gwr_carrier_family": carrier["carrier_family"],
        "higher_divisor_pressure_lock": True,
        "single_hole_closure_used": False,
        "absorbed_alternative_count": len(absorbed_offsets),
        "rejected_candidate_count": int(post_row["rejected_count"]),
        "unresolved_candidate_count": int(post_row["unresolved_count"]),
        "resolved_survivor_count": int(post_row["survives_count"]),
        "action_population_audited": False,
        "selection_wrong_count": None,
        "absorption_wrong_count": None,
        "true_boundary_rejected_count": None,
    }


def selected_activation_offsets(
    pre_row: dict[str, Any],
    witness_bound: int,
) -> list[int]:
    """Return 005A-R selected offsets from the pre-absorption row."""
    anchor_p = int(pre_row["anchor_p"])
    unresolved = [int(offset) for offset in pre_row["unresolved"]]
    selected: list[int] = []
    for resolved_offset in pre_row["survivors"]:
        offset = int(resolved_offset)
        candidate = candidate_record_by_offset(pre_row, offset)
        if bool(candidate.get("single_hole_positive_witness_closure")):
            continue
        later_unresolved = [
            unresolved_offset
            for unresolved_offset in unresolved
            if unresolved_offset > offset
        ]
        if has_higher_divisor_pressure(
            anchor_p,
            offset,
            later_unresolved,
            witness_bound,
        ):
            selected.append(offset)
    return selected


def emit_certificates(
    start_anchor: int,
    max_anchor: int,
    candidate_bound: int,
    witness_bound: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Emit offline PGS boundary certificates without classical audit."""
    started = time.perf_counter()
    records: list[dict[str, Any]] = []
    for anchor_p in anchor_primes(start_anchor, max_anchor):
        pre_row = eliminate_candidates(
            anchor_p,
            candidate_bound,
            enable_single_hole_positive_witness_closure=True,
            witness_bound=witness_bound,
            enable_carrier_locked_pressure_ceiling=True,
            carrier_lock_predicate="unresolved_alternatives_before_threat",
            enable_higher_divisor_pressure_locked_absorption=False,
        )
        selected_offsets = selected_activation_offsets(pre_row, witness_bound)
        if not selected_offsets:
            continue
        post_row = eliminate_candidates(
            anchor_p,
            candidate_bound,
            enable_single_hole_positive_witness_closure=True,
            witness_bound=witness_bound,
            enable_carrier_locked_pressure_ceiling=True,
            carrier_lock_predicate="unresolved_alternatives_before_threat",
            enable_higher_divisor_pressure_locked_absorption=True,
        )
        unique_offset = unique_resolved_survivor_offset(post_row)
        for resolved_offset in selected_offsets:
            if unique_offset != resolved_offset:
                continue
            records.append(
                certificate_from_activation(
                    pre_row,
                    post_row,
                    resolved_offset,
                    candidate_bound,
                    witness_bound,
                )
            )

    summary = {
        "rule_set": RULE_SET,
        "anchor_range": f"{start_anchor}..{max_anchor}",
        "candidate_bound": candidate_bound,
        "witness_bound": witness_bound,
        "certificate_count": len(records),
        "pure_emission_approved": False,
        "classical_audit_required": True,
        "classical_audit_status": "NOT_RUN",
        "wrong_count": None,
        "false_selected_count": None,
        "true_boundary_rejected_count": None,
        "absorption_wrong_count": None,
        "first_failure_example": None,
        "runtime_seconds": time.perf_counter() - started,
    }
    return records, summary


def write_emission_artifacts(
    records: list[dict[str, Any]],
    summary: dict[str, Any],
    output_dir: Path,
) -> dict[str, Path]:
    """Write LF-terminated certificate JSONL and summary JSON."""
    output_dir.mkdir(parents=True, exist_ok=True)
    certificates_path = output_dir / CERTIFICATES_FILENAME
    with certificates_path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(jsonable(record), sort_keys=True) + "\n")

    summary_path = output_dir / SUMMARY_FILENAME
    summary_path.write_text(
        json.dumps(jsonable(summary), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return {
        "certificates_path": certificates_path,
        "summary_path": summary_path,
    }


def first_prime_after(anchor_p: int, candidate_q_hat: int) -> int | None:
    """Return the first classical prime after the anchor up to the candidate."""
    for value in primerange(anchor_p + 1, candidate_q_hat + 1):
        return int(value)
    return None


def audit_certificates(certificates_path: Path) -> dict[str, Any]:
    """Audit emitted certificates after emission using classical validation."""
    started = time.perf_counter()
    records = [
        json.loads(line)
        for line in certificates_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    confirmed_count = 0
    first_failure: dict[str, Any] | None = None
    for record in records:
        anchor_p = int(record["anchor_p"])
        candidate_q_hat = int(record["candidate_q_hat"])
        first_after_anchor = first_prime_after(anchor_p, candidate_q_hat)
        confirmed = first_after_anchor == candidate_q_hat
        if confirmed:
            confirmed_count += 1
            continue
        if first_failure is None:
            first_failure = {
                "anchor_p": anchor_p,
                "candidate_q_hat": candidate_q_hat,
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
    """Write the LF-terminated audit summary JSON."""
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = output_dir / AUDIT_SUMMARY_FILENAME
    summary_path.write_text(
        json.dumps(jsonable(summary), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return summary_path


def main(argv: list[str] | None = None) -> int:
    """Emit certificates or audit previously emitted certificates."""
    args = build_parser().parse_args(argv)
    if args.audit_certificates is not None:
        audit_summary = audit_certificates(args.audit_certificates)
        write_audit_summary(audit_summary, args.output_dir)
        return 0

    records, summary = emit_certificates(
        start_anchor=args.start_anchor,
        max_anchor=args.max_anchor,
        candidate_bound=args.candidate_bound,
        witness_bound=args.witness_bound,
    )
    write_emission_artifacts(records, summary, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
