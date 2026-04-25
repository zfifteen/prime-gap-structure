#!/usr/bin/env python3
"""Deterministic Mersenne-exponent pre-gap GWR predictor.

The script validates the known Mersenne-exponent surface, records the exact
pre-gap winner signature for each exponent, and optionally scans prime
exponents through one bound.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

from sympy import isprime, nextprime, prevprime


ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = ROOT / "src" / "python"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from z_band_prime_composite_field import divisor_counts_segment


DEFAULT_OUTPUT_DIR = ROOT / "output"
CLAIM_D_LIMIT = 8
CLAIM_GAP_LIMIT = 24
KNOWN_MERSENNE_EXPONENTS = (
    2,
    3,
    5,
    7,
    13,
    17,
    19,
    31,
    61,
    89,
    107,
    127,
    521,
    607,
    1279,
    2203,
    2281,
    3217,
    4253,
    4423,
    9689,
    9941,
    11213,
    19937,
    21701,
    23209,
    44497,
    86243,
    110503,
    132049,
    216091,
    756839,
    859433,
    1257787,
    1398269,
    2976221,
    3021377,
    6972593,
    13466917,
    20996011,
    24036583,
    25964951,
    30402457,
    32582657,
    37156667,
    42643801,
    43112609,
    57885161,
    74207281,
    77232917,
    82589933,
    136279841,
)


@dataclass(frozen=True)
class PreGapSignature:
    exponent: int
    preceding_prime: int | None
    preceding_gap: int | None
    winner: int | None
    winner_offset: int | None
    winner_divisor_count: int | None
    claim_filter_pass: bool
    calibrated_filter_pass: bool | None = None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate and apply the deterministic Mersenne pre-gap GWR predictor.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for JSON and CSV artifacts.",
    )
    parser.add_argument(
        "--scan-max",
        type=int,
        default=None,
        help="Optional inclusive upper exponent bound for deterministic candidate scanning.",
    )
    return parser


def pre_gap_signature(exponent: int) -> PreGapSignature:
    """Return the exact leftmost minimum-divisor carrier before one prime exponent."""
    if exponent < 2:
        raise ValueError("exponent must be at least 2")
    if not isprime(exponent):
        raise ValueError(f"exponent {exponent} is not prime")
    if exponent == 2:
        return PreGapSignature(exponent, None, None, None, None, None, False)

    preceding = int(prevprime(exponent))
    gap = exponent - preceding
    if gap <= 1:
        return PreGapSignature(exponent, preceding, gap, None, None, None, False)

    counts = divisor_counts_segment(preceding + 1, exponent)
    best_index = min(range(len(counts)), key=lambda index: int(counts[index]))
    winner = preceding + 1 + best_index
    winner_d = int(counts[best_index])
    claim_pass = winner_d <= CLAIM_D_LIMIT and gap <= CLAIM_GAP_LIMIT
    return PreGapSignature(
        exponent=exponent,
        preceding_prime=preceding,
        preceding_gap=gap,
        winner=winner,
        winner_offset=winner - preceding,
        winner_divisor_count=winner_d,
        claim_filter_pass=claim_pass,
    )


def known_surface_rows() -> list[PreGapSignature]:
    """Return exact pre-gap signatures for the known Mersenne exponents."""
    return [pre_gap_signature(exponent) for exponent in KNOWN_MERSENNE_EXPONENTS]


def calibrated_limits(rows: list[PreGapSignature]) -> tuple[int, int]:
    """Return the smallest rectangular envelope containing known nonempty rows."""
    nonempty = [row for row in rows if row.winner_divisor_count is not None]
    if not nonempty:
        raise ValueError("known surface has no nonempty pre-gap rows")
    max_d = max(int(row.winner_divisor_count) for row in nonempty)
    max_gap = max(int(row.preceding_gap) for row in nonempty if row.preceding_gap is not None)
    return max_d, max_gap


def apply_calibrated_filter(rows: list[PreGapSignature], d_limit: int, gap_limit: int) -> list[PreGapSignature]:
    """Attach the known-surface calibrated filter result to each row."""
    filtered: list[PreGapSignature] = []
    for row in rows:
        if row.winner_divisor_count is None or row.preceding_gap is None:
            passes = False
        else:
            passes = row.winner_divisor_count <= d_limit and row.preceding_gap <= gap_limit
        filtered.append(
            PreGapSignature(
                exponent=row.exponent,
                preceding_prime=row.preceding_prime,
                preceding_gap=row.preceding_gap,
                winner=row.winner,
                winner_offset=row.winner_offset,
                winner_divisor_count=row.winner_divisor_count,
                claim_filter_pass=row.claim_filter_pass,
                calibrated_filter_pass=passes,
            )
        )
    return filtered


def summarize(rows: list[PreGapSignature], d_limit: int, gap_limit: int) -> dict[str, object]:
    """Return one summary payload for the known Mersenne-exponent surface."""
    nonempty = [row for row in rows if row.winner_divisor_count is not None]
    gapped = [row for row in rows if row.preceding_gap is not None]
    d_counter = Counter(int(row.winner_divisor_count) for row in nonempty)
    claim_failures = [
        asdict(row)
        for row in nonempty
        if not row.claim_filter_pass
    ]
    calibrated_failures = [
        asdict(row)
        for row in nonempty
        if not row.calibrated_filter_pass
    ]
    return {
        "known_mersenne_exponent_count": len(rows),
        "nonempty_pre_gap_count": len(nonempty),
        "average_preceding_gap_including_empty_p3": sum(int(row.preceding_gap) for row in gapped) / len(gapped),
        "average_preceding_gap_nonempty": sum(int(row.preceding_gap) for row in nonempty) / len(nonempty),
        "winner_divisor_count_distribution": {
            str(key): {"count": value, "share": value / len(nonempty)}
            for key, value in sorted(d_counter.items())
        },
        "claim_filter": {
            "winner_divisor_count_limit": CLAIM_D_LIMIT,
            "preceding_gap_limit": CLAIM_GAP_LIMIT,
            "known_nonempty_pass_count": sum(1 for row in nonempty if row.claim_filter_pass),
            "known_nonempty_failure_count": len(claim_failures),
            "failures": claim_failures,
        },
        "calibrated_known_surface_filter": {
            "winner_divisor_count_limit": d_limit,
            "preceding_gap_limit": gap_limit,
            "known_nonempty_pass_count": sum(1 for row in nonempty if row.calibrated_filter_pass),
            "known_nonempty_failure_count": len(calibrated_failures),
            "failures": calibrated_failures,
        },
    }


def scan_candidates(scan_max: int, d_limit: int, gap_limit: int) -> list[PreGapSignature]:
    """Return prime exponents through scan_max accepted by the calibrated envelope."""
    if scan_max < 2:
        raise ValueError("scan_max must be at least 2")

    rows: list[PreGapSignature] = []
    exponent = 2
    while exponent <= scan_max:
        row = pre_gap_signature(exponent)
        if (
            row.winner_divisor_count is not None
            and row.preceding_gap is not None
            and row.winner_divisor_count <= d_limit
            and row.preceding_gap <= gap_limit
        ):
            rows.append(
                PreGapSignature(
                    exponent=row.exponent,
                    preceding_prime=row.preceding_prime,
                    preceding_gap=row.preceding_gap,
                    winner=row.winner,
                    winner_offset=row.winner_offset,
                    winner_divisor_count=row.winner_divisor_count,
                    claim_filter_pass=row.claim_filter_pass,
                    calibrated_filter_pass=True,
                )
            )
        exponent = int(nextprime(exponent))
    return rows


def write_csv(path: Path, rows: list[PreGapSignature]) -> None:
    """Write signature rows with LF line endings."""
    fieldnames = list(asdict(rows[0]).keys()) if rows else list(PreGapSignature.__dataclass_fields__)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    started = time.perf_counter()
    rows = known_surface_rows()
    d_limit, gap_limit = calibrated_limits(rows)
    rows = apply_calibrated_filter(rows, d_limit, gap_limit)
    summary = summarize(rows, d_limit, gap_limit)

    candidate_rows: list[PreGapSignature] = []
    if args.scan_max is not None:
        candidate_rows = scan_candidates(args.scan_max, d_limit, gap_limit)
        summary["candidate_scan"] = {
            "scan_max": args.scan_max,
            "accepted_candidate_count": len(candidate_rows),
            "accepted_exponents": [row.exponent for row in candidate_rows],
        }

    summary["runtime_seconds"] = time.perf_counter() - started
    summary_path = args.output_dir / "mersenne_prime_predictor_summary.json"
    known_path = args.output_dir / "mersenne_prime_predictor_known_surface.csv"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8", newline="\n")
    write_csv(known_path, rows)

    if args.scan_max is not None:
        write_csv(args.output_dir / "mersenne_prime_predictor_candidates.csv", candidate_rows)

    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
