"""Classify high-scale PGS chamber-closure impostors."""

from __future__ import annotations

import argparse
import csv
import sys
from math import isqrt, prod
from pathlib import Path
from statistics import median

from sympy import factorint, nextprime, prevprime


ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = ROOT / "src" / "python"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from z_band_prime_predictor.simple_pgs_controller import (  # noqa: E402
    write_json,
    write_jsonl,
)
from z_band_prime_predictor.simple_pgs_generator import (  # noqa: E402
    admissible_offsets,
    pgs_probe_certificate,
)


LEFT_HORIZON_HIDDEN_IMPOSTOR = "LEFT_HORIZON_HIDDEN_IMPOSTOR"
LEFT_SEMIPRIME_SHADOW = "LEFT_SEMIPRIME_SHADOW"
TRUE_BOUNDARY_OUTSIDE_CHAMBER = "TRUE_BOUNDARY_OUTSIDE_CHAMBER"
RIGHT_OVERSTEP = "RIGHT_OVERSTEP"
OTHER_COMPOSITE_IMPOSTOR = "OTHER_COMPOSITE_IMPOSTOR"


def sampled_anchors_near(scale: int, sample_size: int) -> list[int]:
    """Return deterministic prime anchors immediately below scale."""
    anchors: list[int] = []
    cursor = int(scale)
    while len(anchors) < int(sample_size):
        anchor = int(prevprime(cursor))
        anchors.append(anchor)
        cursor = anchor
    return anchors


def factor_profile(n: int, candidate_bound: int) -> dict[str, object]:
    """Return audit-only factorization fields for n."""
    factors = {int(prime): int(exp) for prime, exp in factorint(int(n)).items()}
    least_factor = min(factors)
    cofactor = int(n) // least_factor
    divisor_count = prod(exp + 1 for exp in factors.values())
    exponent_sum = sum(factors.values())
    is_square = isqrt(int(n)) ** 2 == int(n)
    return {
        "least_factor": least_factor,
        "cofactor": cofactor,
        "divisor_count": divisor_count,
        "is_semiprime": exponent_sum == 2,
        "is_square": is_square,
        "is_prime_power": len(factors) == 1 and next(iter(factors.values())) > 1,
        "least_factor_gt_128": least_factor > 128,
        "least_factor_gt_317": least_factor > 317,
        "least_factor_gt_sqrt_candidate_bound_if_relevant": (
            least_factor > isqrt(int(candidate_bound))
        ),
    }


def failure_direction(emitted_q: int, true_q: int) -> str:
    """Return the relative position of the emitted impostor."""
    if int(emitted_q) < int(true_q):
        return "emitted_left_of_true"
    if int(emitted_q) > int(true_q):
        return "emitted_right_of_true"
    return "emitted_equals_true"


def classify_impostor(
    emitted_q: int,
    true_q: int,
    true_offset: int,
    candidate_bound: int,
    factor_fields: dict[str, object],
    max_divisor_floor: int,
    within_128: bool,
) -> str:
    """Return one structural impostor bucket."""
    if int(emitted_q) > int(true_q):
        return RIGHT_OVERSTEP
    if int(true_offset) > int(candidate_bound):
        return TRUE_BOUNDARY_OUTSIDE_CHAMBER

    emitted_is_composite = int(factor_fields["divisor_count"]) > 2
    if (
        int(emitted_q) < int(true_q)
        and emitted_is_composite
        and bool(factor_fields["is_semiprime"])
        and within_128
    ):
        return LEFT_SEMIPRIME_SHADOW
    if (
        int(emitted_q) < int(true_q)
        and emitted_is_composite
        and int(factor_fields["least_factor"]) > int(max_divisor_floor)
    ):
        return LEFT_HORIZON_HIDDEN_IMPOSTOR
    return OTHER_COMPOSITE_IMPOSTOR


def taxonomy_row(
    scale: int,
    p: int,
    certificate: dict[str, object],
    candidate_bound: int,
    max_divisor_floor: int,
) -> dict[str, object] | None:
    """Return a taxonomy row for one failed PGS-certified emission."""
    emitted_q = int(certificate["q"])
    true_q = int(nextprime(int(p)))
    if emitted_q == true_q:
        return None

    emitted_offset = emitted_q - int(p)
    true_offset = true_q - int(p)
    delta = true_q - emitted_q
    open_offsets = admissible_offsets(int(p), int(candidate_bound))
    right_open_after_emitted = [
        offset for offset in open_offsets if offset > emitted_offset
    ]
    right_open_before_true = [
        offset
        for offset in open_offsets
        if emitted_offset < offset < true_offset
    ]
    contains_true = {
        "within_16": (
            emitted_q < true_q
            and true_offset <= int(candidate_bound)
            and delta <= 16
        ),
        "within_32": (
            emitted_q < true_q
            and true_offset <= int(candidate_bound)
            and delta <= 32
        ),
        "within_64": (
            emitted_q < true_q
            and true_offset <= int(candidate_bound)
            and delta <= 64
        ),
        "within_128": (
            emitted_q < true_q
            and true_offset <= int(candidate_bound)
            and delta <= 128
        ),
    }
    factor_fields = factor_profile(emitted_q, candidate_bound)
    carrier_w = int(certificate["carrier_w"])
    impostor_class = classify_impostor(
        emitted_q,
        true_q,
        true_offset,
        candidate_bound,
        factor_fields,
        max_divisor_floor,
        bool(contains_true["within_128"]),
    )
    return {
        "scale": int(scale),
        "rule_id": str(certificate["rule_id"]),
        "anchor_p": int(p),
        "emitted_q": emitted_q,
        "true_q_for_audit_only": true_q,
        "emitted_offset": emitted_offset,
        "true_offset": true_offset,
        "delta_true_minus_emitted": delta,
        "failure_direction": failure_direction(emitted_q, true_q),
        "true_inside_candidate_bound": true_offset <= int(candidate_bound),
        "right_chamber_contains_true": contains_true,
        "emitted_factorization_for_audit_only": factor_fields,
        "carrier_w": carrier_w,
        "carrier_d": int(certificate["carrier_d"]),
        "carrier_offset": carrier_w - int(p),
        "carrier_to_emitted_delta": emitted_q - carrier_w,
        "carrier_to_true_delta": true_q - carrier_w,
        "predecessor_closure_count": len(certificate["closed_offsets_before_q"]),
        "right_open_candidates_after_emitted": len(right_open_after_emitted),
        "right_open_candidates_before_true": len(right_open_before_true),
        "impostor_class": impostor_class,
    }


def taxonomy_scale(
    scale: int,
    sample_size: int,
    candidate_bound: int,
    max_divisor_floor: int,
) -> list[dict[str, object]]:
    """Return failed-row taxonomy rows for one scale."""
    rows: list[dict[str, object]] = []
    for anchor in sampled_anchors_near(scale, sample_size):
        certificate = pgs_probe_certificate(
            anchor,
            candidate_bound,
            max_divisor_floor,
        )
        if certificate is None:
            continue
        row = taxonomy_row(
            scale,
            anchor,
            certificate,
            candidate_bound,
            max_divisor_floor,
        )
        if row is not None:
            rows.append(row)
    return rows


def class_count(rows: list[dict[str, object]], impostor_class: str) -> int:
    """Return the count for one impostor class."""
    return sum(1 for row in rows if row["impostor_class"] == impostor_class)


def within_count(rows: list[dict[str, object]], key: str) -> int:
    """Return count where true boundary appears within a right radius."""
    return sum(
        1 for row in rows if bool(row["right_chamber_contains_true"][key])
    )


def scale_summary(scale: int, rows: list[dict[str, object]]) -> dict[str, object]:
    """Return the required decision-table row for one scale."""
    deltas = [int(row["delta_true_minus_emitted"]) for row in rows]
    return {
        "scale": int(scale),
        "failure_count": len(rows),
        "left_hidden_impostor_count": class_count(
            rows,
            LEFT_HORIZON_HIDDEN_IMPOSTOR,
        ),
        "left_semiprime_shadow_count": class_count(rows, LEFT_SEMIPRIME_SHADOW),
        "true_boundary_outside_chamber_count": class_count(
            rows,
            TRUE_BOUNDARY_OUTSIDE_CHAMBER,
        ),
        "right_overstep_count": class_count(rows, RIGHT_OVERSTEP),
        "other_composite_impostor_count": class_count(
            rows,
            OTHER_COMPOSITE_IMPOSTOR,
        ),
        "median_true_minus_emitted": None if not deltas else median(deltas),
        "within_16_count": within_count(rows, "within_16"),
        "within_32_count": within_count(rows, "within_32"),
        "within_64_count": within_count(rows, "within_64"),
        "within_128_count": within_count(rows, "within_128"),
    }


def decision_from_summary(summary_rows: list[dict[str, object]]) -> str:
    """Return the next selector-family decision from taxonomy counts."""
    total_failures = sum(int(row["failure_count"]) for row in summary_rows)
    if total_failures == 0:
        return "NO_HIGH_SCALE_FAILURES"
    semiprime_or_hidden = sum(
        int(row["left_semiprime_shadow_count"])
        + int(row["left_hidden_impostor_count"])
        for row in summary_rows
    )
    outside = sum(
        int(row["true_boundary_outside_chamber_count"])
        for row in summary_rows
    )
    overstep = sum(int(row["right_overstep_count"]) for row in summary_rows)
    if semiprime_or_hidden * 2 > total_failures:
        return "RIGHTWARD_REORIENTATION"
    if outside * 2 > total_failures:
        return "DETERMINISTIC_CHAMBER_EXPANSION_BY_PGS_STATE"
    if overstep * 4 >= total_failures:
        return "ORDERING_REPAIR"
    return "SPLIT_BY_IMPOSTOR_CLASS_BEFORE_REPAIR"


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
    """Build the taxonomy CLI."""
    parser = argparse.ArgumentParser(
        description="Classify high-scale PGS chamber-closure impostors."
    )
    parser.add_argument("--scales", type=int, nargs="+", required=True)
    parser.add_argument("--sample-size", type=int, default=256)
    parser.add_argument("--candidate-bound", type=int, default=128)
    parser.add_argument("--max-divisor-floor", type=int, default=10_000)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the high-scale impostor taxonomy audit."""
    args = build_parser().parse_args(argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows_by_scale = {
        int(scale): taxonomy_scale(
            int(scale),
            args.sample_size,
            args.candidate_bound,
            args.max_divisor_floor,
        )
        for scale in args.scales
    }
    rows = [
        row
        for scale in args.scales
        for row in rows_by_scale[int(scale)]
    ]
    summary_rows = [
        scale_summary(scale, rows_by_scale[int(scale)])
        for scale in args.scales
    ]
    decision = decision_from_summary(summary_rows)
    write_jsonl(rows, args.output_dir / "impostor_rows.jsonl")
    write_json(
        {"decision": decision, "scales": summary_rows},
        args.output_dir / "summary.json",
    )
    write_csv(summary_rows, args.output_dir / "summary.csv")
    for row in summary_rows:
        print(
            "scale={scale} failures={failure_count} "
            "semiprime_shadow={left_semiprime_shadow_count} "
            "hidden={left_hidden_impostor_count} "
            "outside={true_boundary_outside_chamber_count} "
            "overstep={right_overstep_count} "
            "other={other_composite_impostor_count}".format(**row)
        )
    print(f"decision={decision}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
