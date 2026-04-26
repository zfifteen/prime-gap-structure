"""Audit tools for the minimal PGS iprime generator."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from sympy import nextprime

from z_band_prime_predictor.simple_pgs_generator import (
    CHAIN_FALLBACK_SOURCE,
    FALLBACK_SOURCE,
    PGS_SOURCE,
)


def audit_summary(records: list[dict[str, int]]) -> dict[str, int]:
    """Return the downstream audit summary."""
    confirmed = sum(1 for record in records if confirms_next_prime(record))
    return {
        "anchors": len(records),
        "emitted": len(records),
        "confirmed": confirmed,
        "failed": len(records) - confirmed,
    }


def confirms_next_prime(record: dict[str, int]) -> bool:
    """Return True when downstream audit confirms q is next after p."""
    return int(nextprime(int(record["p"]))) == int(record["q"])


def audit_report(
    records: list[dict[str, int]],
    diagnostics: list[dict[str, object]],
) -> dict[str, object]:
    """Return fallback-displacement metrics with downstream audit results."""
    confirmed = 0
    first_failure = None
    for record in records:
        actual_q = int(nextprime(int(record["p"])))
        if actual_q == int(record["q"]):
            confirmed += 1
        elif first_failure is None:
            first_failure = {
                "p": int(record["p"]),
                "q": int(record["q"]),
                "actual_q": actual_q,
            }
    pgs_count = sum(1 for record in diagnostics if record["source"] == PGS_SOURCE)
    chain_fallback_count = sum(
        1 for record in diagnostics if record["source"] == CHAIN_FALLBACK_SOURCE
    )
    fallback_count = sum(
        1 for record in diagnostics if record["source"] == FALLBACK_SOURCE
    )
    pgs_by_rule: dict[str, int] = {}
    missing_certificate = 0
    for record in diagnostics:
        if record["source"] != PGS_SOURCE:
            continue
        certificate = record.get("certificate")
        if not isinstance(certificate, dict):
            missing_certificate += 1
            continue
        rule_id = str(certificate["rule_id"])
        pgs_by_rule[rule_id] = pgs_by_rule.get(rule_id, 0) + 1
    emitted_count = len(records)
    pgs_rate = 0.0 if emitted_count == 0 else pgs_count / emitted_count
    chain_fallback_rate = (
        0.0 if emitted_count == 0 else chain_fallback_count / emitted_count
    )
    fallback_rate = 0.0 if emitted_count == 0 else fallback_count / emitted_count
    audit_failed = emitted_count - confirmed
    accuracy_status = "PASS" if audit_failed == 0 else "FAIL"
    if audit_failed != 0:
        pgs_status = "FAILING"
    elif pgs_rate >= 0.75:
        pgs_status = "PGS_PASS"
    elif pgs_rate >= 0.50:
        pgs_status = "MINIMAL_PASS"
    else:
        pgs_status = "FAILING"
    return {
        "anchors_scanned": len(records),
        "emitted_count": emitted_count,
        "audit_confirmed": confirmed,
        "audit_failed": audit_failed,
        "accuracy_status": accuracy_status,
        "pgs_status": pgs_status,
        "pgs_count": pgs_count,
        "chain_fallback_count": chain_fallback_count,
        "fallback_count": fallback_count,
        "pgs_rate": pgs_rate,
        "chain_fallback_rate": chain_fallback_rate,
        "fallback_rate": fallback_rate,
        "pgs_percent": pgs_rate * 100.0,
        "chain_fallback_percent": chain_fallback_rate * 100.0,
        "fallback_percent": fallback_rate * 100.0,
        "generator_status": pgs_status,
        "pgs_by_rule": pgs_by_rule,
        "pgs_missing_certificate_count": missing_certificate,
        "first_failure": first_failure,
    }


def read_jsonl(path: Path) -> list[dict[str, object]]:
    """Read a JSONL artifact."""
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def write_json(record: dict[str, object], path: Path) -> None:
    """Write one LF-terminated JSON object."""
    path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    """Build the audit CLI."""
    parser = argparse.ArgumentParser(description="Audit minimal PGS records.")
    parser.add_argument("--records", type=Path, required=True)
    parser.add_argument("--diagnostics", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run downstream audit for emitted records."""
    args = build_parser().parse_args(argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    records = read_jsonl(args.records)
    diagnostics = read_jsonl(args.diagnostics)
    write_json(audit_summary(records), args.output_dir / "summary.json")
    write_json(audit_report(records, diagnostics), args.output_dir / "report.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
