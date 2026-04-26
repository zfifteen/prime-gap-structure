"""Benchmark the minimal PGS generator fallback-displacement campaign."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from sympy import primerange


ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = ROOT / "src" / "python"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from z_band_prime_predictor.simple_pgs_audit import audit_report, audit_summary  # noqa: E402
from z_band_prime_predictor.simple_pgs_controller import (  # noqa: E402
    diagnostic_records,
    write_json,
    write_jsonl,
)
from z_band_prime_predictor.simple_pgs_generator import emit_records  # noqa: E402


def run_benchmark(
    anchors_start: int,
    anchors_stop: int,
    candidate_bound: int,
    output_dir: Path,
) -> dict[str, object]:
    """Run one benchmark surface and write artifacts."""
    output_dir.mkdir(parents=True, exist_ok=True)
    anchors = [int(p) for p in primerange(anchors_start, anchors_stop + 1)]
    records = emit_records(anchors, candidate_bound=candidate_bound)
    diagnostics = diagnostic_records(anchors, candidate_bound=candidate_bound)
    summary = audit_summary(records)
    report = audit_report(records, diagnostics)
    write_jsonl(records, output_dir / "records.jsonl")
    write_jsonl(diagnostics, output_dir / "diagnostics.jsonl")
    write_json(summary, output_dir / "audit_summary.json")
    write_json(report, output_dir / "report.json")
    return report


def build_parser() -> argparse.ArgumentParser:
    """Build the benchmark CLI."""
    parser = argparse.ArgumentParser(description="Run simple PGS benchmark.")
    parser.add_argument("--anchors-start", type=int, required=True)
    parser.add_argument("--anchors-stop", type=int, required=True)
    parser.add_argument("--candidate-bound", type=int, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the benchmark."""
    args = build_parser().parse_args(argv)
    report = run_benchmark(
        args.anchors_start,
        args.anchors_stop,
        args.candidate_bound,
        args.output_dir,
    )
    print(
        "fallback_percent={fallback_percent:.2f}% "
        "chain_fallback_percent={chain_fallback_percent:.2f}% "
        "pgs_percent={pgs_percent:.2f}% "
        "audit_failed={audit_failed} "
        "accuracy_status={accuracy_status} "
        "pgs_status={pgs_status}".format(**report)
    )
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
