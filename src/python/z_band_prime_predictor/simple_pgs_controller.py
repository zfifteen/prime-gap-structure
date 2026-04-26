"""Controller for the minimal PGS iprime generator."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from z_band_prime_predictor.simple_pgs_generator import (
    DEFAULT_CANDIDATE_BOUND,
    emit_records,
    resolve_q,
)


def diagnostic_record(
    p: int,
    boundary_offset: int | None = None,
    candidate_bound: int = DEFAULT_CANDIDATE_BOUND,
) -> dict[str, object]:
    """Return one sidecar diagnostic record."""
    q, source, certificate = resolve_q(int(p), boundary_offset, candidate_bound)
    fields = certificate if isinstance(certificate, dict) else {}
    return {
        "p": int(p),
        "q": q,
        "source": source,
        "certificate": certificate,
        "chain_seed": fields.get("chain_seed"),
        "chain_limit": fields.get("chain_limit"),
        "chain_position_selected": fields.get("chain_position_selected"),
        "chain_nodes_checked": fields.get("chain_nodes_checked", []),
        "chain_fallback_success": bool(fields.get("chain_fallback_success", False)),
        "full_fallback_used": bool(fields.get("full_fallback_used", False)),
    }


def diagnostic_records(
    anchors: list[int],
    boundary_offsets: dict[int, int] | None = None,
    candidate_bound: int = DEFAULT_CANDIDATE_BOUND,
) -> list[dict[str, object]]:
    """Return sidecar diagnostics for emitted records."""
    offsets = {} if boundary_offsets is None else boundary_offsets
    return [
        diagnostic_record(anchor, offsets.get(anchor), candidate_bound)
        for anchor in anchors
    ]


def summary(records: list[dict[str, int]]) -> dict[str, int]:
    """Return the minimal generation summary."""
    return {
        "anchors": len(records),
        "emitted": len(records),
    }


def write_jsonl(records: list[dict[str, object]], path: Path) -> None:
    """Write LF-terminated records."""
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record) + "\n")


def write_json(record: dict[str, object], path: Path) -> None:
    """Write one LF-terminated JSON object."""
    path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")


def parse_anchors(raw: str) -> list[int]:
    """Parse a comma-separated anchor list."""
    return [int(part) for part in raw.split(",") if part.strip()]


def build_parser() -> argparse.ArgumentParser:
    """Build the controller CLI."""
    parser = argparse.ArgumentParser(description="Run minimal PGS generation.")
    parser.add_argument("--anchors", required=True)
    parser.add_argument(
        "--candidate-bound",
        type=int,
        default=DEFAULT_CANDIDATE_BOUND,
    )
    parser.add_argument("--audit", action="store_true")
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run generation, artifact writing, and optional downstream audit."""
    args = build_parser().parse_args(argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    anchors = parse_anchors(args.anchors)
    records = emit_records(anchors, candidate_bound=args.candidate_bound)
    diagnostics = diagnostic_records(anchors, candidate_bound=args.candidate_bound)

    records_path = args.output_dir / "records.jsonl"
    diagnostics_path = args.output_dir / "diagnostics.jsonl"
    write_jsonl(records, records_path)
    write_jsonl(diagnostics, diagnostics_path)
    write_json(summary(records), args.output_dir / "summary.json")

    if args.audit:
        from z_band_prime_predictor.simple_pgs_audit import (
            audit_report,
            audit_summary,
        )

        write_json(audit_summary(records), args.output_dir / "audit_summary.json")
        write_json(audit_report(records, diagnostics), args.output_dir / "report.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
