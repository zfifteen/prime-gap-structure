#!/usr/bin/env python3
"""Build the semiprime-branch d=4 layer baseline from committed repo surfaces."""

from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
import time
from pathlib import Path
from typing import Sequence

import gmpy2
import numpy as np


ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = ROOT / "src" / "python"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from z_band_prime_composite_field import divisor_counts_segment
from z_band_prime_gap_ridge.runs import build_even_window_starts


DEFAULT_OUTPUT_DIR = ROOT / "output" / "semiprime_branch"
DEFAULT_D4_SUMMARY_PATH = ROOT / "output" / "gwr_d4_arrival_validation_summary.json"
DEFAULT_D4_EXACT_CSV_PATH = ROOT / "output" / "gwr_d4_arrival_validation_exact.csv"
DEFAULT_D4_EVEN_CSV_PATH = ROOT / "output" / "gwr_d4_arrival_validation_even_bands.csv"
DEFAULT_PREFILTER_BENCHMARKS_PATH = (
    ROOT / "benchmarks" / "output" / "python" / "prefilter" / "benchmark_results.json"
)

_COUNT_KEYS = (
    "gap_count",
    "winner_d4_count",
    "winner_semiprime_count",
    "winner_prime_cube_count",
    "winner_other_d4_count",
    "winner_non_d4_count",
    "first_d4_match_count",
    "interior_square_violation_count",
)

_CSV_FIELDNAMES = [
    "scale",
    "window_mode",
    "window_size",
    "interval_count",
    "gap_count",
    "winner_d4_count",
    "winner_d4_share",
    "winner_semiprime_count",
    "winner_semiprime_share_of_d4",
    "winner_prime_cube_count",
    "winner_prime_cube_share_of_d4",
    "winner_other_d4_count",
    "winner_other_d4_share_of_d4",
    "winner_non_d4_count",
    "winner_non_d4_share",
    "first_d4_match_count",
    "first_d4_match_rate",
    "interior_square_violation_count",
    "interior_square_violation_rate",
    "median_winner_offset",
    "median_first_d4_offset",
    "max_gap",
    "runtime_seconds",
]

_COMMITTED_FIELD_MAP = {
    "gap_count": "gap_count",
    "winner_d4_count": "winner_d4_count",
    "winner_semiprime_count": "d4_winner_semiprime_count",
    "winner_prime_cube_count": "d4_winner_prime_cube_count",
    "first_d4_match_count": "d4_winner_equals_first_d4_count",
    "interior_square_violation_count": "d4_winner_with_interior_square_count",
}


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description="Build the semiprime-branch d=4 layer baseline artifacts.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for the baseline JSON and CSV artifacts.",
    )
    return parser


def is_prime_cube(n: int) -> bool:
    """Return whether n is a prime cube."""
    root, exact = gmpy2.iroot(n, 3)
    return bool(exact and gmpy2.is_prime(root))


def _empty_row(
    *,
    scale: int,
    window_mode: str,
    lo: int,
    hi: int,
    window_size: int,
) -> dict[str, object]:
    """Create one mutable baseline row."""
    return {
        "scale": scale,
        "window_mode": window_mode,
        "lo": lo,
        "hi": hi,
        "window_size": window_size,
        "interval_count": 0,
        "gap_count": 0,
        "winner_d4_count": 0,
        "winner_semiprime_count": 0,
        "winner_prime_cube_count": 0,
        "winner_other_d4_count": 0,
        "winner_non_d4_count": 0,
        "first_d4_match_count": 0,
        "interior_square_violation_count": 0,
        "median_winner_offset": None,
        "median_first_d4_offset": None,
        "max_gap": 0,
        "runtime_seconds": 0.0,
        "_winner_offsets": [],
        "_first_d4_offsets": [],
    }


def _finalize_row(row: dict[str, object]) -> dict[str, object]:
    """Fill derived shares and medians."""
    gap_count = int(row["gap_count"])
    winner_d4_count = int(row["winner_d4_count"])
    winner_semiprime_count = int(row["winner_semiprime_count"])
    winner_prime_cube_count = int(row["winner_prime_cube_count"])
    winner_other_d4_count = winner_d4_count - winner_semiprime_count - winner_prime_cube_count
    if winner_other_d4_count < 0:
        raise RuntimeError("winner_other_d4_count became negative")
    row["winner_other_d4_count"] = winner_other_d4_count
    row["winner_non_d4_count"] = gap_count - winner_d4_count
    row["winner_d4_share"] = winner_d4_count / gap_count if gap_count > 0 else None
    row["winner_non_d4_share"] = (
        int(row["winner_non_d4_count"]) / gap_count if gap_count > 0 else None
    )
    row["winner_semiprime_share_of_d4"] = (
        winner_semiprime_count / winner_d4_count if winner_d4_count > 0 else None
    )
    row["winner_prime_cube_share_of_d4"] = (
        winner_prime_cube_count / winner_d4_count if winner_d4_count > 0 else None
    )
    row["winner_other_d4_share_of_d4"] = (
        winner_other_d4_count / winner_d4_count if winner_d4_count > 0 else None
    )
    row["first_d4_match_rate"] = (
        int(row["first_d4_match_count"]) / winner_d4_count if winner_d4_count > 0 else None
    )
    row["interior_square_violation_rate"] = (
        int(row["interior_square_violation_count"]) / winner_d4_count
        if winner_d4_count > 0
        else None
    )
    winner_offsets = row["_winner_offsets"]
    first_d4_offsets = row["_first_d4_offsets"]
    if not isinstance(winner_offsets, list) or not isinstance(first_d4_offsets, list):
        raise RuntimeError("offset buckets must remain lists")
    row["median_winner_offset"] = (
        statistics.median(winner_offsets) if winner_offsets else None
    )
    row["median_first_d4_offset"] = (
        statistics.median(first_d4_offsets) if first_d4_offsets else None
    )
    return row


def _public_row(row: dict[str, object]) -> dict[str, object]:
    """Drop internal fields before writing artifacts."""
    return {key: value for key, value in row.items() if not key.startswith("_")}


def summarize_interval(
    lo: int,
    hi: int,
    *,
    scale: int,
    window_mode: str,
) -> dict[str, object]:
    """Summarize the d=4 layer on one deterministic interval."""
    started = time.perf_counter()
    divisor_count = divisor_counts_segment(lo, hi)
    values = np.arange(lo, hi, dtype=np.int64)
    primes = values[divisor_count == 2]
    log_values = np.log(values.astype(np.float64))

    row = _empty_row(
        scale=scale,
        window_mode=window_mode,
        lo=lo,
        hi=hi,
        window_size=hi - lo,
    )

    for left_prime, right_prime in zip(primes[:-1], primes[1:]):
        gap = int(right_prime - left_prime)
        if gap < 4:
            continue

        left_index = int(left_prime - lo + 1)
        right_index = int(right_prime - lo)
        gap_values = values[left_index:right_index]
        gap_divisors = divisor_count[left_index:right_index]
        scores = (
            (1.0 - gap_divisors.astype(np.float64) / 2.0)
            * log_values[left_index:right_index]
        )
        winner_index = int(np.argmax(scores))
        winner_n = int(gap_values[winner_index])
        winner_d = int(gap_divisors[winner_index])

        row["gap_count"] = int(row["gap_count"]) + 1
        row["max_gap"] = max(int(row["max_gap"]), gap)

        if winner_d != 4:
            continue

        d3_indices = np.flatnonzero(gap_divisors == 3)
        d4_indices = np.flatnonzero(gap_divisors == 4)
        if d4_indices.size == 0:
            raise RuntimeError("d=4 winner gap must contain at least the winner itself")

        first_d4_n = int(gap_values[int(d4_indices[0])])
        winner_offset = int(winner_n - left_prime)
        first_d4_offset = int(first_d4_n - left_prime)

        row["winner_d4_count"] = int(row["winner_d4_count"]) + 1
        row["_winner_offsets"].append(winner_offset)
        row["_first_d4_offsets"].append(first_d4_offset)

        if first_d4_n == winner_n:
            row["first_d4_match_count"] = int(row["first_d4_match_count"]) + 1

        if d3_indices.size > 0:
            row["interior_square_violation_count"] = (
                int(row["interior_square_violation_count"]) + 1
            )

        if is_prime_cube(winner_n):
            row["winner_prime_cube_count"] = int(row["winner_prime_cube_count"]) + 1
        else:
            row["winner_semiprime_count"] = int(row["winner_semiprime_count"]) + 1

    row["interval_count"] = 1
    row["runtime_seconds"] = time.perf_counter() - started
    return _finalize_row(row)


def aggregate_rows(
    rows: Sequence[dict[str, object]],
    *,
    scale: int,
    window_mode: str,
    window_size: int,
) -> dict[str, object]:
    """Aggregate multiple interval rows into one scale row."""
    aggregate = _empty_row(
        scale=scale,
        window_mode=window_mode,
        lo=min(int(row["lo"]) for row in rows),
        hi=max(int(row["hi"]) for row in rows),
        window_size=window_size,
    )
    for row in rows:
        for key in _COUNT_KEYS:
            aggregate[key] = int(aggregate[key]) + int(row[key])
        aggregate["interval_count"] = int(aggregate["interval_count"]) + int(row["interval_count"])
        aggregate["max_gap"] = max(int(aggregate["max_gap"]), int(row["max_gap"]))
        aggregate["runtime_seconds"] = float(aggregate["runtime_seconds"]) + float(
            row["runtime_seconds"]
        )
        winner_offsets = aggregate["_winner_offsets"]
        first_d4_offsets = aggregate["_first_d4_offsets"]
        if not isinstance(winner_offsets, list) or not isinstance(first_d4_offsets, list):
            raise RuntimeError("aggregate offset buckets must remain lists")
        winner_offsets.extend(row["_winner_offsets"])
        first_d4_offsets.extend(row["_first_d4_offsets"])
    return _finalize_row(aggregate)


def _read_json(path: Path) -> object:
    """Read a JSON file."""
    return json.loads(path.read_text(encoding="utf-8"))


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    """Read a CSV file into string-keyed rows."""
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def load_committed_surface_parameters() -> dict[str, object]:
    """Load the committed d=4 arrival schedule."""
    raw = _read_json(DEFAULT_D4_SUMMARY_PATH)
    if not isinstance(raw, dict):
        raise RuntimeError("committed d=4 summary must be a JSON object")
    parameters = raw.get("parameters")
    if not isinstance(parameters, dict):
        raise RuntimeError("committed d=4 summary must carry parameters")
    return parameters


def load_committed_surface_rows() -> dict[tuple[int, str], dict[str, str]]:
    """Load the committed exact and even-band rows keyed by scale and mode."""
    rows: dict[tuple[int, str], dict[str, str]] = {}
    for path in (DEFAULT_D4_EXACT_CSV_PATH, DEFAULT_D4_EVEN_CSV_PATH):
        for row in _read_csv_rows(path):
            scale = int(row["scale"])
            window_mode = row["window_mode"]
            key = (scale, window_mode)
            if key in rows:
                raise RuntimeError(f"duplicate committed row for {key}")
            rows[key] = row
    return rows


def verify_against_committed_surface(
    row: dict[str, object],
    committed_rows: dict[tuple[int, str], dict[str, str]],
) -> None:
    """Require parity with the committed d=4 arrival surface."""
    key = (int(row["scale"]), str(row["window_mode"]))
    committed = committed_rows.get(key)
    if committed is None:
        raise RuntimeError(f"missing committed row for {key}")
    if int(committed["window_size"]) != int(row["window_size"]):
        raise RuntimeError(f"window_size mismatch for {key}")
    if int(committed["interval_count"]) != int(row["interval_count"]):
        raise RuntimeError(f"interval_count mismatch for {key}")
    for local_field, committed_field in _COMMITTED_FIELD_MAP.items():
        local_value = int(row[local_field])
        committed_value = int(committed[committed_field])
        if local_value != committed_value:
            raise RuntimeError(
                f"committed-surface mismatch for {key} field {local_field}: "
                f"{local_value} != {committed_value}"
            )


def build_by_scale_rows() -> list[dict[str, object]]:
    """Rebuild the baseline rows on the committed schedule."""
    parameters = load_committed_surface_parameters()
    exact_limits = parameters.get("exact_limits")
    scales = parameters.get("scales")
    window_size = parameters.get("window_size")
    window_count = parameters.get("window_count")
    if not isinstance(exact_limits, list) or not isinstance(scales, list):
        raise RuntimeError("committed d=4 summary must provide exact_limits and scales")
    if not isinstance(window_size, int) or not isinstance(window_count, int):
        raise RuntimeError("committed d=4 summary must provide window_size and window_count")

    committed_rows = load_committed_surface_rows()
    rows: list[dict[str, object]] = []

    for exact_limit in exact_limits:
        if not isinstance(exact_limit, int):
            raise RuntimeError("exact_limits must stay integer-valued")
        row = summarize_interval(
            lo=2,
            hi=exact_limit + 1,
            scale=exact_limit,
            window_mode="exact",
        )
        verify_against_committed_surface(row, committed_rows)
        rows.append(row)

    for scale in scales:
        if not isinstance(scale, int):
            raise RuntimeError("scales must stay integer-valued")
        starts = build_even_window_starts(scale, window_size, window_count)
        interval_rows = [
            summarize_interval(
                lo=start,
                hi=start + window_size,
                scale=scale,
                window_mode="even",
            )
            for start in starts
        ]
        row = aggregate_rows(
            interval_rows,
            scale=scale,
            window_mode="even",
            window_size=window_size,
        )
        verify_against_committed_surface(row, committed_rows)
        rows.append(row)

    return rows


def summarize_documented_surface(rows: Sequence[dict[str, object]]) -> dict[str, object]:
    """Aggregate the full documented surface into one row-like summary."""
    combined = aggregate_rows(
        rows,
        scale=0,
        window_mode="documented_surface",
        window_size=0,
    )
    public = _public_row(combined)
    public.pop("scale", None)
    public.pop("window_mode", None)
    public.pop("window_size", None)
    public.pop("lo", None)
    public.pop("hi", None)
    return public


def load_prefilter_surface() -> dict[str, object]:
    """Load the current committed large-RSA prefilter surface."""
    raw = _read_json(DEFAULT_PREFILTER_BENCHMARKS_PATH)
    if not isinstance(raw, dict):
        raise RuntimeError("prefilter benchmark surface must be a JSON object")
    exact_calibration = raw.get("exact_calibration")
    proxy_calibration = raw.get("proxy_calibration")
    crypto_control = raw.get("crypto_control")
    proxy_crypto_pipeline = raw.get("proxy_crypto_pipeline")
    bonus_crypto_control = raw.get("bonus_crypto_control")
    bonus_proxy_crypto_pipeline = raw.get("bonus_proxy_crypto_pipeline")
    if not all(
        isinstance(section, dict)
        for section in (
            exact_calibration,
            proxy_calibration,
            crypto_control,
            proxy_crypto_pipeline,
            bonus_crypto_control,
            bonus_proxy_crypto_pipeline,
        )
    ):
        raise RuntimeError("prefilter benchmark surface is missing required sections")
    return {
        "source_path": str(DEFAULT_PREFILTER_BENCHMARKS_PATH.relative_to(ROOT)),
        "exact_calibration": {
            "prime_fixed_points": exact_calibration["numeric_fixed_points"],
            "prime_count": exact_calibration["prime_count"],
            "composite_false_fixed_points": exact_calibration["numeric_false_fixed_points"],
            "strict_contractions": exact_calibration["strict_contractions"],
            "proxy_false_fixed_points": proxy_calibration["false_fixed_points"],
        },
        "candidate_loop": {
            "rsa_2048": {
                "candidate_count": proxy_crypto_pipeline["candidate_count"],
                "rejected_by_proxy": proxy_crypto_pipeline["rejected_by_proxy"],
                "rejection_rate": proxy_crypto_pipeline["rejection_rate"],
                "survivors_to_miller_rabin": proxy_crypto_pipeline["survivors_to_miller_rabin"],
                "miller_rabin_pass_count": proxy_crypto_pipeline["miller_rabin_pass_count"],
                "miller_rabin_only_mean_ms": crypto_control["timing_ms"]["mean"],
                "pipeline_mean_ms": proxy_crypto_pipeline["pipeline_timing_ms"]["mean"],
                "proxy_mean_ms": proxy_crypto_pipeline["proxy_timing_ms"]["mean"],
            },
            "rsa_4096": {
                "candidate_count": bonus_proxy_crypto_pipeline["candidate_count"],
                "rejected_by_proxy": bonus_proxy_crypto_pipeline["rejected_by_proxy"],
                "rejection_rate": bonus_proxy_crypto_pipeline["rejection_rate"],
                "survivors_to_miller_rabin": bonus_proxy_crypto_pipeline["survivors_to_miller_rabin"],
                "miller_rabin_pass_count": bonus_proxy_crypto_pipeline["miller_rabin_pass_count"],
                "miller_rabin_only_mean_ms": bonus_crypto_control["timing_ms"]["mean"],
                "pipeline_mean_ms": bonus_proxy_crypto_pipeline["pipeline_timing_ms"]["mean"],
                "proxy_mean_ms": bonus_proxy_crypto_pipeline["proxy_timing_ms"]["mean"],
            },
        },
    }


def write_by_scale_csv(output_path: Path, rows: Sequence[dict[str, object]]) -> None:
    """Write the baseline by-scale CSV."""
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=_CSV_FIELDNAMES, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            public_row = _public_row(row)
            writer.writerow({name: public_row.get(name) for name in _CSV_FIELDNAMES})


def build_summary(rows: Sequence[dict[str, object]]) -> dict[str, object]:
    """Build the baseline summary JSON object."""
    parameters = load_committed_surface_parameters()
    exact_20m_row = next(
        row
        for row in rows
        if int(row["scale"]) == 20_000_000 and str(row["window_mode"]) == "exact"
    )
    return {
        "source_artifacts": {
            "d4_arrival_validation_summary_json": str(DEFAULT_D4_SUMMARY_PATH.relative_to(ROOT)),
            "d4_arrival_validation_exact_csv": str(DEFAULT_D4_EXACT_CSV_PATH.relative_to(ROOT)),
            "d4_arrival_validation_even_bands_csv": str(DEFAULT_D4_EVEN_CSV_PATH.relative_to(ROOT)),
            "prefilter_benchmark_results_json": str(
                DEFAULT_PREFILTER_BENCHMARKS_PATH.relative_to(ROOT)
            ),
        },
        "parameters": {
            "exact_limits": parameters["exact_limits"],
            "scales": parameters["scales"],
            "window_size": parameters["window_size"],
            "window_count": parameters["window_count"],
            "median_definition": "statistics.median over per-gap offsets on d=4 winner gaps",
        },
        "starting_facts": {
            "exact_20000000": {
                "gap_count": exact_20m_row["gap_count"],
                "winner_d4_count": exact_20m_row["winner_d4_count"],
                "winner_d4_share": exact_20m_row["winner_d4_share"],
                "winner_semiprime_count": exact_20m_row["winner_semiprime_count"],
                "winner_prime_cube_count": exact_20m_row["winner_prime_cube_count"],
                "winner_other_d4_count": exact_20m_row["winner_other_d4_count"],
                "first_d4_match_count": exact_20m_row["first_d4_match_count"],
                "interior_square_violation_count": exact_20m_row[
                    "interior_square_violation_count"
                ],
                "median_winner_offset": exact_20m_row["median_winner_offset"],
                "median_first_d4_offset": exact_20m_row["median_first_d4_offset"],
            },
        },
        "documented_surface_totals": summarize_documented_surface(rows),
        "prefilter_surface": load_prefilter_surface(),
        "by_scale": [_public_row(row) for row in rows],
    }


def main(argv: list[str] | None = None) -> int:
    """Build the baseline artifacts."""
    parser = build_parser()
    args = parser.parse_args(argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    rows = build_by_scale_rows()
    summary = build_summary(rows)

    summary_path = args.output_dir / "d4_layer_baseline_summary.json"
    by_scale_path = args.output_dir / "d4_layer_baseline_by_scale.csv"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    write_by_scale_csv(by_scale_path, rows)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
