"""Run deterministic scale checks for the minimal PGS generator."""

from __future__ import annotations

import argparse
import csv
import sys
from math import isqrt
from pathlib import Path

from sympy import isprime, prevprime


ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = ROOT / "src" / "python"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from z_band_prime_predictor.simple_pgs_audit import audit_report  # noqa: E402
from z_band_prime_predictor.simple_pgs_controller import (  # noqa: E402
    diagnostic_records,
    write_json,
    write_jsonl,
)
from z_band_prime_predictor.simple_pgs_generator import (  # noqa: E402
    PGS_SOURCE,
    emit_records,
    pgs_probe_certificate,
)


def sampled_anchors_near(scale: int, sample_size: int) -> list[int]:
    """Return deterministic prime anchors immediately below scale."""
    anchors: list[int] = []
    cursor = int(scale)
    while len(anchors) < int(sample_size):
        anchor = int(prevprime(cursor))
        anchors.append(anchor)
        cursor = anchor
    return anchors


def generator_status_for_rows(rows: list[dict[str, object]]) -> str:
    """Return the campaign status across tested scales."""
    if any(int(row["audit_failed"]) != 0 for row in rows):
        return "FAILING"
    if any(
        row["mode"] == "exact" and float(row["pgs_rate"]) < 0.50
        for row in rows
    ):
        return "FAILING"
    if any(
        row["mode"] == "pgs_probe" and float(row["pgs_certified_rate"]) < 0.50
        for row in rows
    ):
        return "FAILING"
    if all(
        (
            row["mode"] == "exact"
            and float(row["pgs_rate"]) >= 0.75
        )
        or (
            row["mode"] == "pgs_probe"
            and float(row["pgs_certified_rate"]) >= 0.75
        )
        for row in rows
    ):
        return "PGS_PASS"
    return "MINIMAL_PASS"


def pgs_probe_report(
    scale: int,
    anchors: list[int],
    candidate_bound: int,
    max_divisor_floor: int,
    required_floor: int,
) -> dict[str, object]:
    """Run PGS-only probe mode for a scale."""
    records: list[dict[str, int]] = []
    diagnostics: list[dict[str, object]] = []
    for anchor in anchors:
        certificate = pgs_probe_certificate(
            anchor,
            candidate_bound,
            max_divisor_floor,
        )
        if certificate is None:
            continue
        q = int(certificate["q"])
        records.append({"p": int(anchor), "q": q})
        diagnostics.append(
            {
                "p": int(anchor),
                "q": q,
                "source": PGS_SOURCE,
                "certificate": certificate,
            }
        )

    report = pgs_probe_audit_report(records, diagnostics)
    pgs_certified_count = len(records)
    fallback_required_count = len(anchors) - pgs_certified_count
    pgs_certified_rate = (
        0.0 if not anchors else pgs_certified_count / len(anchors)
    )
    fallback_required_rate = (
        0.0 if not anchors else fallback_required_count / len(anchors)
    )
    return {
        "scale": int(scale),
        "mode": "pgs_probe",
        "status": "completed",
        "skip_reason": None,
        "max_required_divisor_floor": required_floor,
        "anchors_scanned": len(anchors),
        "emitted_count": pgs_certified_count,
        "audit_confirmed": report["audit_confirmed"],
        "audit_failed": report["audit_failed"],
        "accuracy_status": "PASS" if report["audit_failed"] == 0 else "FAIL",
        "pgs_status": "FAILING",
        "pgs_count": pgs_certified_count,
        "chain_fallback_count": 0,
        "fallback_count": fallback_required_count,
        "pgs_rate": pgs_certified_rate,
        "chain_fallback_rate": 0.0,
        "fallback_rate": fallback_required_rate,
        "pgs_percent": pgs_certified_rate * 100.0,
        "chain_fallback_percent": 0.0,
        "fallback_percent": fallback_required_rate * 100.0,
        "pgs_certified_count": pgs_certified_count,
        "fallback_required_count": fallback_required_count,
        "pgs_certified_rate": pgs_certified_rate,
        "fallback_required_rate": fallback_required_rate,
        "pgs_certified_percent": pgs_certified_rate * 100.0,
        "fallback_required_percent": fallback_required_rate * 100.0,
        "generator_status": "FAILING",
        "pgs_by_rule": report["pgs_by_rule"],
        "pgs_missing_certificate_count": report["pgs_missing_certificate_count"],
        "first_failure": report["first_failure"],
    }


def pgs_probe_audit_report(
    records: list[dict[str, int]],
    diagnostics: list[dict[str, object]],
) -> dict[str, object]:
    """Audit PGS-probe rows without exact fallback next-prime lookup."""
    confirmed = 0
    first_failure = None
    for record in records:
        p = int(record["p"])
        q = int(record["q"])
        q_is_prime = bool(isprime(q))
        interior_has_prime = any(isprime(candidate) for candidate in range(p + 1, q))
        if q > p and q_is_prime and not interior_has_prime:
            confirmed += 1
        elif first_failure is None:
            first_failure = {
                "p": p,
                "q": q,
                "q_is_prime": q_is_prime,
                "interior_has_prime": interior_has_prime,
            }
    pgs_by_rule: dict[str, int] = {}
    missing_certificate = 0
    for row in diagnostics:
        certificate = row.get("certificate")
        if not isinstance(certificate, dict):
            missing_certificate += 1
            continue
        rule_id = str(certificate["rule_id"])
        pgs_by_rule[rule_id] = pgs_by_rule.get(rule_id, 0) + 1
    return {
        "audit_confirmed": confirmed,
        "audit_failed": len(records) - confirmed,
        "pgs_by_rule": pgs_by_rule,
        "pgs_missing_certificate_count": missing_certificate,
        "first_failure": first_failure,
    }


def run_scale(
    scale: int,
    sample_size: int,
    candidate_bound: int,
    max_divisor_floor: int,
) -> dict[str, object]:
    """Run one sampled scale check."""
    anchors = sampled_anchors_near(scale, sample_size)
    required_floor = max(isqrt(anchor + 1) for anchor in anchors)
    if required_floor > max_divisor_floor:
        return pgs_probe_report(
            scale,
            anchors,
            candidate_bound,
            max_divisor_floor,
            required_floor,
        )
    records = emit_records(anchors, candidate_bound=candidate_bound)
    diagnostics = diagnostic_records(anchors, candidate_bound=candidate_bound)
    report = audit_report(records, diagnostics)
    fallback_required_count = (
        int(report["chain_fallback_count"]) + int(report["fallback_count"])
    )
    fallback_required_rate = (
        0.0 if not anchors else fallback_required_count / len(anchors)
    )
    return {
        "scale": int(scale),
        "mode": "exact",
        "status": "completed",
        "skip_reason": None,
        "max_required_divisor_floor": required_floor,
        "pgs_certified_count": report["pgs_count"],
        "fallback_required_count": fallback_required_count,
        "pgs_certified_rate": report["pgs_rate"],
        "fallback_required_rate": fallback_required_rate,
        "pgs_certified_percent": report["pgs_percent"],
        "fallback_required_percent": fallback_required_rate * 100.0,
        **report,
    }


def write_csv(rows: list[dict[str, object]], path: Path) -> None:
    """Write LF-terminated CSV rows."""
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(rows[0]),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def build_parser() -> argparse.ArgumentParser:
    """Build the scale-sweep CLI."""
    parser = argparse.ArgumentParser(description="Run simple PGS scale sweep.")
    parser.add_argument("--anchors", type=int, nargs="+", required=True)
    parser.add_argument("--sample-size", type=int, required=True)
    parser.add_argument("--candidate-bound", type=int, required=True)
    parser.add_argument("--max-divisor-floor", type=int, default=10_000)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run all requested sampled scale checks."""
    args = build_parser().parse_args(argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows = [
        run_scale(
            scale,
            args.sample_size,
            args.candidate_bound,
            args.max_divisor_floor,
        )
        for scale in args.anchors
    ]
    campaign_status = generator_status_for_rows(rows)
    for row in rows:
        row["generator_status"] = campaign_status
    write_json({"rows": rows, "generator_status": campaign_status}, args.output_dir / "summary.json")
    write_jsonl(rows, args.output_dir / "rows.jsonl")
    write_csv(rows, args.output_dir / "rows.csv")
    for row in rows:
        print(
            "scale={scale} mode={mode} fallback_percent={fallback_percent:.2f}% "
            "chain_fallback_percent={chain_fallback_percent:.2f}% "
            "pgs_percent={pgs_percent:.2f}% audit_failed={audit_failed} "
            "accuracy_status={accuracy_status} pgs_status={pgs_status}".format(**row)
        )
    print({"generator_status": campaign_status, "rows": rows})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
