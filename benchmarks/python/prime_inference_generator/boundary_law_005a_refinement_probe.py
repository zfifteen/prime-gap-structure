#!/usr/bin/env python3
"""Offline refinement probe for Boundary Law 005A."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

try:
    from .higher_divisor_pressure_lock_activation_profile import (
        DEFAULT_SURFACES,
        parse_surface,
        surface_profile,
    )
    from .resolved_boundary_lock_separator_probe import jsonable
except ImportError:  # pragma: no cover - direct script execution
    MODULE_DIR = Path(__file__).resolve().parent
    if str(MODULE_DIR) not in sys.path:
        sys.path.insert(0, str(MODULE_DIR))
    from higher_divisor_pressure_lock_activation_profile import (
        DEFAULT_SURFACES,
        parse_surface,
        surface_profile,
    )
    from resolved_boundary_lock_separator_probe import jsonable


DEFAULT_OUTPUT_DIR = Path("output/prime_inference_generator")
SUMMARY_FILENAME = "boundary_law_005a_refinement_summary.json"
ROWS_FILENAME = "boundary_law_005a_refinement_rows.jsonl"
ACTIVATIONS_FILENAME = "boundary_law_005a_refinement_activations.jsonl"


def build_parser() -> argparse.ArgumentParser:
    """Build the 005A refinement CLI."""
    parser = argparse.ArgumentParser(
        description="Offline zero-wrong refinement probe for Boundary Law 005A.",
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
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for JSON and JSONL artifacts.",
    )
    return parser


def refinement_selected(record: dict[str, Any]) -> bool:
    """Return whether 005A-R keeps this 005A activation."""
    return not bool(record["single_hole_closure_used"])


def refinement_record(record: dict[str, Any]) -> dict[str, Any]:
    """Return one activation record with refinement classification."""
    selected = refinement_selected(record)
    unique = bool(record["unique_resolved_after_absorption_bool"])
    wrong = int(record["resolved_candidate_offset"]) != int(
        record["actual_boundary_offset_label"]
    )
    if selected and wrong:
        status = "SELECTED_WRONG"
    elif selected and unique:
        status = "KEPT_UNIQUE_SUCCESS"
    elif selected:
        status = "KEPT_NON_UNIQUE_ACTIVATION"
    elif unique:
        status = "DROPPED_UNIQUE_SUCCESS"
    else:
        status = "DROPPED_NON_UNIQUE_ACTIVATION"
    return {
        **record,
        "refinement_selected": selected,
        "refinement_status": status,
    }


def first_failure(records: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Return the first refinement failure example, if present."""
    for record in records:
        if not bool(record["refinement_selected"]):
            continue
        actual = int(record["actual_boundary_offset_label"])
        resolved = int(record["resolved_candidate_offset"])
        if resolved != actual:
            return {
                "failure_type": "WRONG_SELECTION",
                "anchor_p": int(record["anchor_p"]),
                "resolved_candidate_offset": resolved,
                "actual_boundary_offset_label": actual,
            }
        if not bool(record["unique_resolved_after_absorption_bool"]):
            return {
                "failure_type": "SELECTED_NON_UNIQUE_ACTIVATION",
                "anchor_p": int(record["anchor_p"]),
                "resolved_candidate_offset": resolved,
                "actual_boundary_offset_label": actual,
            }
    return None


def surface_row(
    surface: str,
    candidate_bound: int,
    witness_bound: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Return refinement records and one surface row."""
    parse_surface(surface)
    activations, _, base_summary = surface_profile(
        surface,
        candidate_bound,
        witness_bound,
        0,
    )
    records = [refinement_record(record) for record in activations]
    selected = [
        record for record in records if bool(record["refinement_selected"])
    ]
    dropped = [
        record for record in records if not bool(record["refinement_selected"])
    ]
    kept_unique = [
        record
        for record in selected
        if bool(record["unique_resolved_after_absorption_bool"])
    ]
    dropped_unique = [
        record
        for record in dropped
        if bool(record["unique_resolved_after_absorption_bool"])
    ]
    kept_non_unique = [
        record
        for record in selected
        if not bool(record["unique_resolved_after_absorption_bool"])
    ]
    dropped_non_unique = [
        record
        for record in dropped
        if not bool(record["unique_resolved_after_absorption_bool"])
    ]
    wrong_count = sum(
        1
        for record in selected
        if int(record["resolved_candidate_offset"])
        != int(record["actual_boundary_offset_label"])
    )
    true_boundary_rejected_count = sum(
        1
        for record in selected
        if int(record["actual_boundary_offset_label"])
        in [int(offset) for offset in record["absorbed_unresolved_offsets"]]
    )
    hard_passed = (
        wrong_count == 0
        and true_boundary_rejected_count == 0
        and not kept_non_unique
        and (not activations or bool(kept_unique))
    )
    row = {
        "surface": surface,
        "candidate_bound": candidate_bound,
        "witness_bound": witness_bound,
        "activation_count": len(records),
        "selected_activation_count": len(selected),
        "dropped_activation_count": len(dropped),
        "unique_success_count": len(kept_unique),
        "non_unique_activation_count": len(kept_non_unique),
        "wrong_count": wrong_count,
        "false_selected_count": wrong_count,
        "true_boundary_rejected_count": true_boundary_rejected_count,
        "absorption_wrong_count": wrong_count,
        "safe_abstain_count": (
            int(base_summary["safe_abstain_count"]) + len(dropped)
        ),
        "kept_unique_successes": len(kept_unique),
        "dropped_unique_successes": len(dropped_unique),
        "kept_non_unique_activations": len(kept_non_unique),
        "dropped_non_unique_activations": len(dropped_non_unique),
        "hard_passed": hard_passed,
        "first_failure_example": first_failure(records),
    }
    return records, row


def run_refinement(
    surfaces: list[str],
    candidate_bound: int,
    witness_bound: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    """Run the 005A-R refinement probe."""
    started = time.perf_counter()
    all_records: list[dict[str, Any]] = []
    rows: list[dict[str, Any]] = []
    for surface in surfaces:
        records, row = surface_row(surface, candidate_bound, witness_bound)
        all_records.extend(records)
        rows.append(row)
    summary = {
        "mode": "offline_boundary_law_005a_refinement_probe",
        "candidate_bound": candidate_bound,
        "witness_bound": witness_bound,
        "surfaces": surfaces,
        "activation_count": sum(int(row["activation_count"]) for row in rows),
        "selected_activation_count": sum(
            int(row["selected_activation_count"]) for row in rows
        ),
        "dropped_activation_count": sum(
            int(row["dropped_activation_count"]) for row in rows
        ),
        "unique_success_count": sum(
            int(row["unique_success_count"]) for row in rows
        ),
        "non_unique_activation_count": sum(
            int(row["non_unique_activation_count"]) for row in rows
        ),
        "wrong_count": sum(int(row["wrong_count"]) for row in rows),
        "false_selected_count": sum(
            int(row["false_selected_count"]) for row in rows
        ),
        "true_boundary_rejected_count": sum(
            int(row["true_boundary_rejected_count"]) for row in rows
        ),
        "absorption_wrong_count": sum(
            int(row["absorption_wrong_count"]) for row in rows
        ),
        "safe_abstain_count": sum(
            int(row["safe_abstain_count"]) for row in rows
        ),
        "kept_unique_successes": sum(
            int(row["kept_unique_successes"]) for row in rows
        ),
        "dropped_unique_successes": sum(
            int(row["dropped_unique_successes"]) for row in rows
        ),
        "kept_non_unique_activations": sum(
            int(row["kept_non_unique_activations"]) for row in rows
        ),
        "dropped_non_unique_activations": sum(
            int(row["dropped_non_unique_activations"]) for row in rows
        ),
        "surface_rows": rows,
        "all_surfaces_hard_passed": all(bool(row["hard_passed"]) for row in rows),
        "boundary_law_005a_refinement_status": "offline_candidate_refinement_only",
        "boundary_law_005_status": "candidate_grade_only",
        "prime_emission_status": "forbidden",
        "runtime_seconds": time.perf_counter() - started,
    }
    return all_records, rows, summary


def write_artifacts(
    records: list[dict[str, Any]],
    rows: list[dict[str, Any]],
    summary: dict[str, Any],
    output_dir: Path,
) -> dict[str, Path]:
    """Write LF-terminated JSONL records and JSON summary."""
    output_dir.mkdir(parents=True, exist_ok=True)
    activations_path = output_dir / ACTIVATIONS_FILENAME
    with activations_path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(jsonable(record), sort_keys=True) + "\n")

    rows_path = output_dir / ROWS_FILENAME
    with rows_path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(jsonable(row), sort_keys=True) + "\n")

    summary_path = output_dir / SUMMARY_FILENAME
    summary_path.write_text(
        json.dumps(jsonable(summary), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return {
        "activations_path": activations_path,
        "rows_path": rows_path,
        "summary_path": summary_path,
    }


def main(argv: list[str] | None = None) -> int:
    """Run the 005A-R refinement probe and write artifacts."""
    args = build_parser().parse_args(argv)
    records, rows, summary = run_refinement(
        surfaces=args.surfaces,
        candidate_bound=args.candidate_bound,
        witness_bound=args.witness_bound,
    )
    write_artifacts(records, rows, summary, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
