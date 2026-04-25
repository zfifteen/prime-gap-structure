"""Minimal emit-all PGS iprime generator."""

from __future__ import annotations

import argparse
import json
from math import isqrt
from pathlib import Path


DEFAULT_CANDIDATE_BOUND = 128
PGS_SOURCE = "PGS"
FALLBACK_SOURCE = "fallback"


def has_trial_divisor(n: int) -> bool:
    """Return True when trial division finds a concrete divisor."""
    if n < 2:
        return True
    for divisor in range(2, isqrt(n) + 1):
        if n % divisor == 0:
            return True
    return False


def first_prime_in_chamber(p: int, chamber_width: int) -> int | None:
    """Return the first trial-division prime in the current chamber."""
    for candidate in range(int(p) + 1, int(p) + int(chamber_width) + 1):
        if not has_trial_divisor(candidate):
            return candidate
    return None


def next_prime_by_trial_division(
    p: int,
    candidate_bound: int = DEFAULT_CANDIDATE_BOUND,
) -> int:
    """Return the next prime using deterministic chamber expansion."""
    chamber_width = int(candidate_bound)
    if chamber_width < 1:
        raise ValueError("candidate_bound must be positive")
    while True:
        q = first_prime_in_chamber(int(p), chamber_width)
        if q is not None:
            return q
        chamber_width *= 2


def resolve_q(
    p: int,
    boundary_offset: int | None = None,
    candidate_bound: int = DEFAULT_CANDIDATE_BOUND,
) -> tuple[int, str]:
    """Resolve q and report whether PGS or fallback selected it."""
    fallback_q = next_prime_by_trial_division(int(p), candidate_bound)
    if boundary_offset is None:
        return fallback_q, FALLBACK_SOURCE
    pgs_q = int(p) + int(boundary_offset)
    if has_trial_divisor(pgs_q) or pgs_q != fallback_q:
        return fallback_q, FALLBACK_SOURCE
    return pgs_q, PGS_SOURCE


def emit_record(
    p: int,
    boundary_offset: int | None = None,
    candidate_bound: int = DEFAULT_CANDIDATE_BOUND,
) -> dict[str, int]:
    """Emit one minimal accurate iprime record."""
    q, _source = resolve_q(int(p), boundary_offset, candidate_bound)
    return {
        "p": int(p),
        "q": q,
    }


def emit_records(
    anchors: list[int],
    boundary_offsets: dict[int, int] | None = None,
    candidate_bound: int = DEFAULT_CANDIDATE_BOUND,
) -> list[dict[str, int]]:
    """Emit one minimal record per anchor."""
    offsets = {} if boundary_offsets is None else boundary_offsets
    return [
        emit_record(anchor, offsets.get(anchor), candidate_bound)
        for anchor in anchors
    ]


def diagnostic_record(
    p: int,
    boundary_offset: int | None = None,
    candidate_bound: int = DEFAULT_CANDIDATE_BOUND,
) -> dict[str, int | str]:
    """Return one sidecar diagnostic record."""
    q, source = resolve_q(int(p), boundary_offset, candidate_bound)
    return {
        "p": int(p),
        "q": q,
        "source": source,
    }


def diagnostic_records(
    anchors: list[int],
    boundary_offsets: dict[int, int] | None = None,
    candidate_bound: int = DEFAULT_CANDIDATE_BOUND,
) -> list[dict[str, int | str]]:
    """Return sidecar diagnostics for emitted records."""
    offsets = {} if boundary_offsets is None else boundary_offsets
    return [
        diagnostic_record(anchor, offsets.get(anchor), candidate_bound)
        for anchor in anchors
    ]


def summary(records: list[dict[str, int]]) -> dict[str, int]:
    """Return the minimal unaudited run summary."""
    return {
        "anchors": len(records),
        "emitted": len(records),
    }


def audit_summary(records: list[dict[str, int]]) -> dict[str, int]:
    """Return the minimal downstream audit summary."""
    from sympy import nextprime

    confirmed = 0
    for record in records:
        if int(nextprime(int(record["p"]))) == int(record["q"]):
            confirmed += 1
    return {
        "anchors": len(records),
        "emitted": len(records),
        "confirmed": confirmed,
        "failed": len(records) - confirmed,
    }


def write_jsonl(records: list[dict[str, int | str]], path: Path) -> None:
    """Write LF-terminated records."""
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record) + "\n")


def write_json(summary_record: dict[str, int], path: Path) -> None:
    """Write one LF-terminated summary."""
    path.write_text(json.dumps(summary_record, indent=2) + "\n", encoding="utf-8")


def parse_anchors(raw: str) -> list[int]:
    """Parse a comma-separated anchor list."""
    return [int(part) for part in raw.split(",") if part.strip()]


def build_parser() -> argparse.ArgumentParser:
    """Build the minimal generator CLI."""
    parser = argparse.ArgumentParser(description="Emit minimal PGS iprime records.")
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
    """Run the minimal generator."""
    args = build_parser().parse_args(argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    anchors = parse_anchors(args.anchors)
    records = emit_records(anchors, candidate_bound=args.candidate_bound)
    diagnostics = diagnostic_records(anchors, candidate_bound=args.candidate_bound)
    write_jsonl(records, args.output_dir / "records.jsonl")
    write_jsonl(diagnostics, args.output_dir / "diagnostics.jsonl")
    write_json(
        audit_summary(records) if args.audit else summary(records),
        args.output_dir / "summary.json",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
