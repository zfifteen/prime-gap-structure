#!/usr/bin/env python3
"""Experimental PGS inferred-prime emitter for the 005A-R candidate rule."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

try:
    from .offline_pgs_certificate_emitter import (
        RULE_SET,
        audit_certificates,
        emit_certificates,
    )
    from .resolved_boundary_lock_separator_probe import jsonable
except ImportError:  # pragma: no cover - direct script execution
    MODULE_DIR = Path(__file__).resolve().parent
    if str(MODULE_DIR) not in sys.path:
        sys.path.insert(0, str(MODULE_DIR))
    from offline_pgs_certificate_emitter import (
        RULE_SET,
        audit_certificates,
        emit_certificates,
    )
    from resolved_boundary_lock_separator_probe import jsonable


DEFAULT_OUTPUT_DIR = Path("output/prime_inference_generator")
RECORDS_FILENAME = "experimental_pgs_inferred_primes.jsonl"
SUMMARY_FILENAME = "experimental_pgs_prime_emitter_summary.json"
AUDIT_SUMMARY_FILENAME = "experimental_pgs_prime_audit_summary.json"
CERTIFICATE_COMPAT_FILENAME = "_experimental_certificate_compat.jsonl"


def build_parser() -> argparse.ArgumentParser:
    """Build the experimental inferred-prime emitter CLI."""
    parser = argparse.ArgumentParser(
        description="Emit or audit experimental PGS inferred-prime records.",
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
        "--audit-records",
        type=Path,
        default=None,
        help="Read emitted experimental JSONL and write an audit summary.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for JSON and JSONL artifacts.",
    )
    return parser


def inferred_record(certificate: dict[str, Any]) -> dict[str, Any]:
    """Convert one offline certificate into an experimental inference record."""
    return {
        "record_type": "PGS_INFERRED_PRIME_EXPERIMENTAL",
        "inference_status": "INFERRED_BY_005A_R",
        "rule_set": RULE_SET,
        "anchor_p": int(certificate["anchor_p"]),
        "inferred_prime_q_hat": int(certificate["candidate_q_hat"]),
        "boundary_offset": int(certificate["boundary_offset"]),
        "production_approved": False,
        "cryptographic_use_approved": False,
        "classical_audit_required": True,
        "classical_audit_status": "NOT_RUN",
        "candidate_bound": int(certificate["candidate_bound"]),
        "witness_bound": int(certificate["witness_bound"]),
        "gwr_carrier": certificate["gwr_carrier"],
        "gwr_carrier_offset": certificate["gwr_carrier_offset"],
        "gwr_carrier_d": certificate["gwr_carrier_d"],
        "gwr_carrier_family": certificate["gwr_carrier_family"],
        "higher_divisor_pressure_lock": True,
        "single_hole_closure_used": False,
        "absorbed_alternative_count": int(
            certificate["absorbed_alternative_count"]
        ),
        "resolved_survivor_count": int(certificate["resolved_survivor_count"]),
        "unresolved_candidate_count": int(certificate["unresolved_candidate_count"]),
        "rejected_candidate_count": int(certificate["rejected_candidate_count"]),
    }


def emit_experimental_records(
    start_anchor: int,
    max_anchor: int,
    candidate_bound: int,
    witness_bound: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Emit experimental inferred-prime records from 005A-R certificates."""
    started = time.perf_counter()
    certificates, _ = emit_certificates(
        start_anchor=start_anchor,
        max_anchor=max_anchor,
        candidate_bound=candidate_bound,
        witness_bound=witness_bound,
    )
    records = [inferred_record(certificate) for certificate in certificates]
    summary = {
        "record_type": "PGS_EXPERIMENTAL_INFERENCE_SUMMARY",
        "rule_set": RULE_SET,
        "anchor_range": f"{start_anchor}..{max_anchor}",
        "emitted_count": len(records),
        "production_approved": False,
        "cryptographic_use_approved": False,
        "classical_audit_required": True,
        "classical_audit_status": "NOT_RUN",
        "candidate_bound": candidate_bound,
        "witness_bound": witness_bound,
        "runtime_seconds": time.perf_counter() - started,
    }
    return records, summary


def write_emission_artifacts(
    records: list[dict[str, Any]],
    summary: dict[str, Any],
    output_dir: Path,
) -> dict[str, Path]:
    """Write LF-terminated experimental JSONL and summary JSON."""
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


def certificate_compat_record(record: dict[str, Any]) -> dict[str, Any]:
    """Return the certificate-shaped subset needed by the shared audit helper."""
    return {
        "anchor_p": int(record["anchor_p"]),
        "candidate_q_hat": int(record["inferred_prime_q_hat"]),
    }


def audit_experimental_records(records_path: Path, output_dir: Path) -> dict[str, Any]:
    """Audit emitted experimental records after emission."""
    records = [
        json.loads(line)
        for line in records_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    output_dir.mkdir(parents=True, exist_ok=True)
    compat_path = output_dir / CERTIFICATE_COMPAT_FILENAME
    with compat_path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            compat = certificate_compat_record(record)
            handle.write(json.dumps(jsonable(compat), sort_keys=True) + "\n")
    audit_summary = audit_certificates(compat_path)
    compat_path.unlink()
    return audit_summary


def write_audit_summary(summary: dict[str, Any], output_dir: Path) -> Path:
    """Write the LF-terminated experimental audit summary JSON."""
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = output_dir / AUDIT_SUMMARY_FILENAME
    summary_path.write_text(
        json.dumps(jsonable(summary), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return summary_path


def main(argv: list[str] | None = None) -> int:
    """Emit or audit experimental inferred-prime records."""
    args = build_parser().parse_args(argv)
    if args.audit_records is not None:
        audit_summary = audit_experimental_records(args.audit_records, args.output_dir)
        write_audit_summary(audit_summary, args.output_dir)
        return 0

    records, summary = emit_experimental_records(
        start_anchor=args.start_anchor,
        max_anchor=args.max_anchor,
        candidate_bound=args.candidate_bound,
        witness_bound=args.witness_bound,
    )
    write_emission_artifacts(records, summary, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
