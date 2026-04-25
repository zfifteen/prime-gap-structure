#!/usr/bin/env python3
"""Activation profile for the higher-divisor pressure lock."""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

try:
    from .composite_exclusion_boundary_probe import (
        certified_divisor_class,
        run_probe,
    )
    from .higher_divisor_pressure_lock_hardening import has_higher_divisor_pressure
    from .resolved_boundary_lock_separator_probe import (
        candidate_record_by_offset,
        gap_width_class,
        jsonable,
        resolved_record,
    )
except ImportError:  # pragma: no cover - direct script execution
    MODULE_DIR = Path(__file__).resolve().parent
    if str(MODULE_DIR) not in sys.path:
        sys.path.insert(0, str(MODULE_DIR))
    from composite_exclusion_boundary_probe import (
        certified_divisor_class,
        run_probe,
    )
    from higher_divisor_pressure_lock_hardening import has_higher_divisor_pressure
    from resolved_boundary_lock_separator_probe import (
        candidate_record_by_offset,
        gap_width_class,
        jsonable,
        resolved_record,
    )


DEFAULT_OUTPUT_DIR = Path("output/prime_inference_generator")
SUMMARY_FILENAME = "higher_divisor_pressure_lock_activation_profile_summary.json"
ACTIVATIONS_FILENAME = "higher_divisor_pressure_lock_activation_records.jsonl"
NEAR_MISSES_FILENAME = "higher_divisor_pressure_lock_near_miss_records.jsonl"
DEFAULT_SURFACES = ("11..1000000", "100000..200000", "1000000..1100000")


def build_parser() -> argparse.ArgumentParser:
    """Build the activation profile CLI."""
    parser = argparse.ArgumentParser(
        description="Offline activation profile for higher-divisor pressure lock.",
    )
    parser.add_argument(
        "--surfaces",
        nargs="+",
        default=list(DEFAULT_SURFACES),
        help="Inclusive anchor surfaces formatted as START..MAX.",
    )
    parser.add_argument(
        "--candidate-bound",
        type=int,
        default=64,
        help="Largest candidate boundary offset.",
    )
    parser.add_argument(
        "--witness-bound",
        type=int,
        default=97,
        help="Largest positive witness factor.",
    )
    parser.add_argument(
        "--near-miss-limit",
        type=int,
        default=200,
        help="Maximum near-miss records to write.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for JSON and JSONL artifacts.",
    )
    return parser


def parse_surface(surface: str) -> tuple[int, int]:
    """Parse one inclusive surface string."""
    parts = surface.split("..")
    if len(parts) != 2:
        raise ValueError(f"surface must be START..MAX: {surface}")
    start_anchor = int(parts[0].replace("_", ""))
    max_anchor = int(parts[1].replace("_", ""))
    if max_anchor < start_anchor:
        raise ValueError(f"surface max must be >= start: {surface}")
    return start_anchor, max_anchor


def first_open_offset(anchor_p: int) -> int | None:
    """Return the first wheel-open offset from one anchor."""
    for offset in range(1, 31):
        if (anchor_p + offset) % 30 in {1, 7, 11, 13, 17, 19, 23, 29}:
            return offset
    return None


def pressure_signature(record: dict[str, Any]) -> str:
    """Return a compact pressure signature token."""
    higher = len(record["higher_divisor_pressure_between_candidate_and_later_unresolved"])
    reset = len(record["reset_evidence_between_candidate_and_later_unresolved"])
    square = len(record["square_pressure_between_candidate_and_later_unresolved"])
    semiprime = len(record["semiprime_pressure_between_candidate_and_later_unresolved"])
    return f"H{higher}_R{reset}_S{square}_SP{semiprime}"


def anchor_range_bucket(anchor_p: int) -> str:
    """Return the 100000-wide anchor bucket for one activation."""
    bucket_start = (anchor_p // 100_000) * 100_000
    return f"{bucket_start}..{bucket_start + 99_999}"


def pressure_offset_class(
    anchor_p: int,
    pressure_offsets: list[int],
    witness_bound: int,
) -> tuple[int | None, int | None]:
    """Return the first higher-divisor pressure offset and divisor class."""
    if not pressure_offsets:
        return None, None
    pressure_offset = int(pressure_offsets[0])
    certificate = certified_divisor_class(anchor_p + pressure_offset, witness_bound)
    pressure_d = (
        None if certificate is None else int(certificate["divisor_class"])
    )
    return pressure_offset, pressure_d


def activation_record(
    pre_row: dict[str, Any],
    post_row: dict[str, Any],
    previous_row: dict[str, Any] | None,
    resolved_offset: int,
    candidate_bound: int,
    witness_bound: int,
) -> dict[str, Any]:
    """Return one activation record."""
    record = resolved_record(pre_row, previous_row, resolved_offset, witness_bound)
    candidate = candidate_record_by_offset(pre_row, resolved_offset)
    later_unresolved = [
        int(offset)
        for offset in pre_row["unresolved"]
        if int(offset) > resolved_offset
    ]
    previous_gap = record["previous_chamber_pressure"]["previous_gap_width"]
    pressure_offsets = [
        int(offset)
        for offset in record[
            "higher_divisor_pressure_between_candidate_and_later_unresolved"
        ]
    ]
    pressure_offset, pressure_d = pressure_offset_class(
        int(pre_row["anchor_p"]),
        pressure_offsets,
        witness_bound,
    )
    return {
        "anchor_p": int(pre_row["anchor_p"]),
        "resolved_candidate_offset": resolved_offset,
        "actual_boundary_offset_label": int(pre_row["actual_boundary_offset_label"]),
        "candidate_bound": candidate_bound,
        "witness_bound": witness_bound,
        "carrier_offset": record["carrier_offset"],
        "carrier_divisor_count": record["carrier_divisor_count"],
        "carrier_family": record["carrier_family"],
        "higher_divisor_pressure_signature": pressure_signature(record),
        "higher_divisor_pressure_offset": pressure_offset,
        "higher_divisor_pressure_d": pressure_d,
        "higher_divisor_pressure_offsets": record[
            "higher_divisor_pressure_between_candidate_and_later_unresolved"
        ],
        "previous_gap_width": previous_gap,
        "previous_chamber_type": (
            None if previous_row is None else str(previous_row["true_boundary_status"])
        ),
        "first_open_offset": first_open_offset(int(pre_row["anchor_p"])),
        "single_hole_closure_used": bool(
            candidate.get("single_hole_positive_witness_closure")
        ),
        "locked_absorption_count": len(later_unresolved),
        "absorbed_unresolved_offsets": later_unresolved,
        "nearest_unresolved_offsets_before_absorption": later_unresolved[:5],
        "unique_resolved_after_absorption_bool": bool(
            post_row["unique_resolved_survivor"]
        ),
        "previous_gap_width_class": gap_width_class(previous_gap),
        "anchor_range_bucket": anchor_range_bucket(int(pre_row["anchor_p"])),
    }


def near_miss_reason(
    row: dict[str, Any],
    resolved_offset: int,
    witness_bound: int,
) -> tuple[str, str]:
    """Return why a resolved candidate did not activate the lock."""
    unresolved = [int(offset) for offset in row["unresolved"]]
    later_unresolved = [offset for offset in unresolved if offset > resolved_offset]
    if not later_unresolved:
        return "NO_LATER_UNRESOLVED", "later_unresolved"
    if not has_higher_divisor_pressure(
        int(row["anchor_p"]),
        resolved_offset,
        later_unresolved,
        witness_bound,
    ):
        return "NO_HIGHER_DIVISOR_PRESSURE", "higher_divisor_pressure"
    return "LOCK_FIRED", "none"


def near_miss_record(
    row: dict[str, Any],
    resolved_offset: int,
    witness_bound: int,
) -> dict[str, Any]:
    """Return one near-miss record."""
    reason, missing_component = near_miss_reason(row, resolved_offset, witness_bound)
    actual = int(row["actual_boundary_offset_label"])
    return {
        "anchor_p": int(row["anchor_p"]),
        "resolved_candidate_offset": resolved_offset,
        "actual_boundary_offset_label": actual,
        "why_lock_did_not_fire": reason,
        "missing_pressure_component": missing_component,
        "candidate_had_resolved_boundary_bool": resolved_offset == actual,
        "candidate_had_false_resolved_survivor_bool": resolved_offset != actual,
    }


def surface_profile(
    surface: str,
    candidate_bound: int,
    witness_bound: int,
    near_miss_remaining: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    """Return activation and near-miss records for one surface."""
    start_anchor, max_anchor = parse_surface(surface)
    pre_rows, _ = run_probe(
        start_anchor=start_anchor,
        max_anchor=max_anchor,
        candidate_bound=candidate_bound,
        enable_single_hole_positive_witness_closure=True,
        witness_bound=witness_bound,
        enable_carrier_locked_pressure_ceiling=True,
        carrier_lock_predicate="unresolved_alternatives_before_threat",
        enable_higher_divisor_pressure_locked_absorption=False,
    )
    post_rows, _ = run_probe(
        start_anchor=start_anchor,
        max_anchor=max_anchor,
        candidate_bound=candidate_bound,
        enable_single_hole_positive_witness_closure=True,
        witness_bound=witness_bound,
        enable_carrier_locked_pressure_ceiling=True,
        carrier_lock_predicate="unresolved_alternatives_before_threat",
        enable_higher_divisor_pressure_locked_absorption=True,
    )
    post_rows_by_anchor = {
        int(row["anchor_p"]): row for row in post_rows
    }
    activation_records: list[dict[str, Any]] = []
    near_miss_records: list[dict[str, Any]] = []
    previous_row: dict[str, Any] | None = None
    safe_abstain_count = 0
    wrong_count = 0
    for row in pre_rows:
        post_row = post_rows_by_anchor[int(row["anchor_p"])]
        unresolved = [int(offset) for offset in row["unresolved"]]
        actual = int(row["actual_boundary_offset_label"])
        for resolved_offset in row["survivors"]:
            offset = int(resolved_offset)
            later_unresolved = [
                unresolved_offset
                for unresolved_offset in unresolved
                if unresolved_offset > offset
            ]
            if has_higher_divisor_pressure(
                int(row["anchor_p"]),
                offset,
                later_unresolved,
                witness_bound,
            ):
                if offset != actual:
                    wrong_count += 1
                activation_records.append(
                    activation_record(
                        row,
                        post_row,
                        previous_row,
                        offset,
                        candidate_bound,
                        witness_bound,
                    )
                )
                continue
            safe_abstain_count += 1
            if len(near_miss_records) < near_miss_remaining:
                near_miss_records.append(near_miss_record(row, offset, witness_bound))
        previous_row = row

    unique_success_count = sum(
        1
        for record in activation_records
        if bool(record["unique_resolved_after_absorption_bool"])
    )
    return activation_records, near_miss_records, {
        "surface": surface,
        "row_count": len(pre_rows),
        "activation_count": len(activation_records),
        "unique_success_count": unique_success_count,
        "safe_abstain_count": safe_abstain_count,
        "wrong_count": wrong_count,
    }


def count_by(records: list[dict[str, Any]], key: str) -> dict[str, int]:
    """Return string-keyed counts for one activation field."""
    return dict(
        sorted(
            Counter(str(record[key]) for record in records).items(),
            key=lambda item: item[0],
        )
    )


def aggregate_counts(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Return activation aggregate counts."""
    return {
        "activation_by_gap_width": count_by(records, "resolved_candidate_offset"),
        "activation_by_carrier_family": count_by(records, "carrier_family"),
        "activation_by_carrier_d": count_by(records, "carrier_divisor_count"),
        "activation_by_first_open_offset": count_by(records, "first_open_offset"),
        "activation_by_previous_gap_width_class": count_by(
            records,
            "previous_gap_width_class",
        ),
        "activation_by_pressure_signature": count_by(
            records,
            "higher_divisor_pressure_signature",
        ),
        "activation_by_anchor_range_bucket": count_by(
            records,
            "anchor_range_bucket",
        ),
    }


def run_profile(
    surfaces: list[str],
    candidate_bound: int,
    witness_bound: int,
    near_miss_limit: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    """Run the activation profile."""
    started = time.perf_counter()
    all_activations: list[dict[str, Any]] = []
    all_near_misses: list[dict[str, Any]] = []
    surface_summaries: list[dict[str, Any]] = []
    remaining = near_miss_limit
    for surface in surfaces:
        activations, near_misses, summary = surface_profile(
            surface,
            candidate_bound,
            witness_bound,
            remaining,
        )
        all_activations.extend(activations)
        all_near_misses.extend(near_misses)
        surface_summaries.append(summary)
        remaining = max(0, near_miss_limit - len(all_near_misses))

    wrong_count = sum(int(summary["wrong_count"]) for summary in surface_summaries)
    profile_summary = {
        "mode": "offline_higher_divisor_pressure_lock_activation_profile",
        "surfaces": surfaces,
        "candidate_bound": candidate_bound,
        "witness_bound": witness_bound,
        "activation_count": len(all_activations),
        "unique_success_count": sum(
            int(summary["unique_success_count"]) for summary in surface_summaries
        ),
        "non_unique_activation_count": len(all_activations) - sum(
            int(summary["unique_success_count"]) for summary in surface_summaries
        ),
        "safe_abstain_count": sum(
            int(summary["safe_abstain_count"]) for summary in surface_summaries
        ),
        "wrong_count": wrong_count,
        "surface_summaries": surface_summaries,
        **aggregate_counts(all_activations),
        "boundary_law_005_status": "candidate_not_approved_for_generation",
        "prime_emission_status": "forbidden",
        "runtime_seconds": time.perf_counter() - started,
    }
    return all_activations, all_near_misses, profile_summary


def write_artifacts(
    activation_records: list[dict[str, Any]],
    near_miss_records: list[dict[str, Any]],
    summary: dict[str, Any],
    output_dir: Path,
) -> dict[str, Path]:
    """Write LF-terminated JSONL records and JSON summary."""
    output_dir.mkdir(parents=True, exist_ok=True)
    activations_path = output_dir / ACTIVATIONS_FILENAME
    with activations_path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in activation_records:
            handle.write(json.dumps(jsonable(record), sort_keys=True) + "\n")

    near_misses_path = output_dir / NEAR_MISSES_FILENAME
    with near_misses_path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in near_miss_records:
            handle.write(json.dumps(jsonable(record), sort_keys=True) + "\n")

    summary_path = output_dir / SUMMARY_FILENAME
    summary_path.write_text(
        json.dumps(jsonable(summary), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return {
        "activations_path": activations_path,
        "near_misses_path": near_misses_path,
        "summary_path": summary_path,
    }


def main(argv: list[str] | None = None) -> int:
    """Run the activation profile and write artifacts."""
    args = build_parser().parse_args(argv)
    activations, near_misses, summary = run_profile(
        surfaces=args.surfaces,
        candidate_bound=args.candidate_bound,
        witness_bound=args.witness_bound,
        near_miss_limit=args.near_miss_limit,
    )
    write_artifacts(activations, near_misses, summary, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
