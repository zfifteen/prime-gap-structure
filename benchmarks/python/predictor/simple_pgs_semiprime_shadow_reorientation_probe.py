"""Probe rightward reorientation from high-scale semiprime shadows."""

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
    closure_reason,
    pgs_probe_certificate,
)


LEFT_HORIZON_HIDDEN_IMPOSTOR = "LEFT_HORIZON_HIDDEN_IMPOSTOR"
LEFT_SEMIPRIME_SHADOW = "LEFT_SEMIPRIME_SHADOW"
TRUE_BOUNDARY_OUTSIDE_CHAMBER = "TRUE_BOUNDARY_OUTSIDE_CHAMBER"
RIGHT_OVERSTEP = "RIGHT_OVERSTEP"
OTHER_COMPOSITE_IMPOSTOR = "OTHER_COMPOSITE_IMPOSTOR"
RADII = (16, 32, 64, 128)
RANKERS = ("ranker_a", "ranker_b", "ranker_c", "ranker_d")


def sampled_anchors_near(scale: int, sample_size: int) -> list[int]:
    """Return deterministic prime anchors immediately below scale."""
    anchors: list[int] = []
    cursor = int(scale)
    while len(anchors) < int(sample_size):
        anchor = int(prevprime(cursor))
        anchors.append(anchor)
        cursor = anchor
    return anchors


def factor_profile(n: int) -> dict[str, object]:
    """Return audit-only factorization fields for n."""
    factors = {int(prime): int(exp) for prime, exp in factorint(int(n)).items()}
    least_factor = min(factors)
    divisor_count = prod(exp + 1 for exp in factors.values())
    exponent_sum = sum(factors.values())
    return {
        "least_factor": least_factor,
        "divisor_count": divisor_count,
        "is_semiprime": exponent_sum == 2,
    }


def classify_shadow(
    emitted_q: int,
    true_q: int,
    true_offset: int,
    candidate_bound: int,
    factor_fields: dict[str, object],
    max_divisor_floor: int,
) -> str:
    """Return the high-scale impostor class for a failed row."""
    if int(emitted_q) > int(true_q):
        return RIGHT_OVERSTEP
    if int(true_offset) > int(candidate_bound):
        return TRUE_BOUNDARY_OUTSIDE_CHAMBER
    if int(factor_fields["divisor_count"]) <= 2:
        return OTHER_COMPOSITE_IMPOSTOR
    if bool(factor_fields["is_semiprime"]):
        return LEFT_SEMIPRIME_SHADOW
    if int(factor_fields["least_factor"]) > int(max_divisor_floor):
        return LEFT_HORIZON_HIDDEN_IMPOSTOR
    return OTHER_COMPOSITE_IMPOSTOR


def closure_counts(
    p: int,
    offset: int,
    shadow_offset: int,
    open_offsets: list[int],
    max_divisor_floor: int,
) -> tuple[int, int]:
    """Return closed/unclosed counts between shadow and one candidate."""
    closed = 0
    unclosed = 0
    for prior in open_offsets:
        if prior <= int(shadow_offset):
            continue
        if prior >= int(offset):
            break
        if closure_reason(int(p), prior, max_divisor_floor) is None:
            unclosed += 1
        else:
            closed += 1
    return closed, unclosed


def visible_boundary_score(
    p: int,
    offset: int,
    shadow_offset: int,
    open_offsets: list[int],
    max_divisor_floor: int,
) -> tuple[int, int, int, int]:
    """Return a label-free boundary-likeness score for ranking."""
    closed, unclosed = closure_counts(
        p,
        offset,
        shadow_offset,
        open_offsets,
        max_divisor_floor,
    )
    self_open = closure_reason(int(p), int(offset), max_divisor_floor) is None
    return (
        1 if self_open else 0,
        closed - (2 * unclosed),
        closed,
        -abs(int(offset) - int(shadow_offset)),
    )


def right_offsets(
    p: int,
    shadow_offset: int,
    radius: int,
    candidate_bound: int,
) -> list[int]:
    """Return wheel-open offsets in the inspected right chamber."""
    return [
        offset
        for offset in admissible_offsets(int(p), int(candidate_bound))
        if int(shadow_offset) < offset <= int(shadow_offset) + int(radius)
    ]


def ranker_a(offsets: list[int], **_kwargs) -> list[int]:
    """Rank by first right-side wheel-open candidate."""
    return list(offsets)


def ranker_b(
    offsets: list[int],
    p: int,
    shadow_offset: int,
    open_offsets: list[int],
    max_divisor_floor: int,
    **_kwargs,
) -> list[int]:
    """Rank first candidate whose right predecessors are visibly closed."""
    def key(offset: int) -> tuple[int, int]:
        _closed, unclosed = closure_counts(
            p,
            offset,
            shadow_offset,
            open_offsets,
            max_divisor_floor,
        )
        self_open = closure_reason(int(p), int(offset), max_divisor_floor) is None
        return (0 if self_open and unclosed == 0 else 1, offset)

    return sorted(offsets, key=key)


def ranker_c(
    offsets: list[int],
    p: int,
    shadow_offset: int,
    open_offsets: list[int],
    max_divisor_floor: int,
    **_kwargs,
) -> list[int]:
    """Rank by chamber-closure boundary-likeness score."""
    return sorted(
        offsets,
        key=lambda offset: visible_boundary_score(
            p,
            offset,
            shadow_offset,
            open_offsets,
            max_divisor_floor,
        ),
        reverse=True,
    )


def ranker_d(
    offsets: list[int],
    p: int,
    shadow_offset: int,
    open_offsets: list[int],
    max_divisor_floor: int,
    predecessor_closure_count: int,
    **_kwargs,
) -> list[int]:
    """Rank first candidate not dominated by the shadow closure relation."""
    def key(offset: int) -> tuple[int, int, int]:
        closed, unclosed = closure_counts(
            p,
            offset,
            shadow_offset,
            open_offsets,
            max_divisor_floor,
        )
        self_open = closure_reason(int(p), int(offset), max_divisor_floor) is None
        dominated = closed < int(predecessor_closure_count)
        return (0 if self_open and not dominated else 1, unclosed, offset)

    return sorted(offsets, key=key)


def ranked_offsets(
    ranker_name: str,
    offsets: list[int],
    p: int,
    shadow_offset: int,
    open_offsets: list[int],
    max_divisor_floor: int,
    predecessor_closure_count: int,
) -> list[int]:
    """Return offsets ordered by one label-free ranker."""
    kwargs = {
        "p": int(p),
        "shadow_offset": int(shadow_offset),
        "open_offsets": open_offsets,
        "max_divisor_floor": int(max_divisor_floor),
        "predecessor_closure_count": int(predecessor_closure_count),
    }
    if ranker_name == "ranker_a":
        return ranker_a(offsets, **kwargs)
    if ranker_name == "ranker_b":
        return ranker_b(offsets, **kwargs)
    if ranker_name == "ranker_c":
        return ranker_c(offsets, **kwargs)
    if ranker_name == "ranker_d":
        return ranker_d(offsets, **kwargs)
    raise ValueError(f"unknown ranker: {ranker_name}")


def shadow_row(
    scale: int,
    p: int,
    certificate: dict[str, object],
    candidate_bound: int,
    max_divisor_floor: int,
) -> dict[str, object] | None:
    """Return one audit-assisted shadow row or None."""
    emitted_q = int(certificate["q"])
    true_q = int(nextprime(int(p)))
    if emitted_q == true_q:
        return None
    shadow_offset = emitted_q - int(p)
    true_offset = true_q - int(p)
    factors = factor_profile(emitted_q)
    impostor_class = classify_shadow(
        emitted_q,
        true_q,
        true_offset,
        candidate_bound,
        factors,
        max_divisor_floor,
    )
    if impostor_class not in {
        LEFT_SEMIPRIME_SHADOW,
        LEFT_HORIZON_HIDDEN_IMPOSTOR,
    }:
        return None

    open_offsets = admissible_offsets(int(p), int(candidate_bound))
    radius_details: dict[str, object] = {}
    for radius in RADII:
        offsets = right_offsets(p, shadow_offset, radius, candidate_bound)
        rank_details: dict[str, object] = {}
        for ranker_name in RANKERS:
            ordered = ranked_offsets(
                ranker_name,
                offsets,
                p,
                shadow_offset,
                open_offsets,
                max_divisor_floor,
                len(certificate["closed_offsets_before_q"]),
            )
            true_rank = (
                ordered.index(true_offset) + 1
                if true_offset in ordered
                else None
            )
            rank_details[ranker_name] = {
                "top_offset": ordered[0] if ordered else None,
                "true_rank": true_rank,
                "top1_hit": true_rank == 1,
                "top2_hit": true_rank is not None and true_rank <= 2,
                "top4_hit": true_rank is not None and true_rank <= 4,
                "top8_hit": true_rank is not None and true_rank <= 8,
            }
        radius_details[str(radius)] = {
            "right_chamber_candidate_count": max(
                0,
                min(int(candidate_bound), shadow_offset + radius) - shadow_offset,
            ),
            "right_chamber_open_candidate_count": len(offsets),
            "true_boundary_within_radius": (
                emitted_q < true_q
                and true_offset <= int(candidate_bound)
                and true_q - emitted_q <= int(radius)
            ),
            "rankers": rank_details,
        }

    return {
        "scale": int(scale),
        "rule_id": str(certificate["rule_id"]),
        "anchor_p": int(p),
        "shadow_s": emitted_q,
        "true_q_for_audit_only": true_q,
        "shadow_offset": shadow_offset,
        "true_offset": true_offset,
        "delta_true_minus_shadow": true_q - emitted_q,
        "impostor_class": impostor_class,
        "factorization_for_audit_only": factors,
        "predecessor_closure_count": len(certificate["closed_offsets_before_q"]),
        "true_boundary_right_of_shadow": emitted_q < true_q,
        "radius_details": radius_details,
    }


def build_shadow_rows(
    scales: list[int],
    sample_size: int,
    candidate_bound: int,
    max_divisor_floor: int,
) -> list[dict[str, object]]:
    """Return all audit-assisted shadow rows."""
    rows: list[dict[str, object]] = []
    for scale in scales:
        for anchor in sampled_anchors_near(scale, sample_size):
            certificate = pgs_probe_certificate(
                anchor,
                candidate_bound,
                max_divisor_floor,
            )
            if certificate is None:
                continue
            row = shadow_row(
                scale,
                anchor,
                certificate,
                candidate_bound,
                max_divisor_floor,
            )
            if row is not None:
                rows.append(row)
    return rows


def recall(count: int, shadow_count: int) -> float:
    """Return count / shadow_count."""
    return 0.0 if shadow_count == 0 else int(count) / int(shadow_count)


def median_rank(ranks: list[int]) -> int | float | None:
    """Return median rank or None."""
    return None if not ranks else median(ranks)


def summary_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    """Return one summary row per scale, radius, and ranker."""
    summaries: list[dict[str, object]] = []
    for scale in sorted({int(row["scale"]) for row in rows}):
        scale_rows = [row for row in rows if int(row["scale"]) == scale]
        for radius in RADII:
            within_count = sum(
                1
                for row in scale_rows
                if bool(row["radius_details"][str(radius)]["true_boundary_within_radius"])
            )
            true_right_count = sum(
                1 for row in scale_rows if bool(row["true_boundary_right_of_shadow"])
            )
            candidate_count = sum(
                int(row["radius_details"][str(radius)]["right_chamber_candidate_count"])
                for row in scale_rows
            )
            open_count = sum(
                int(
                    row["radius_details"][str(radius)][
                        "right_chamber_open_candidate_count"
                    ]
                )
                for row in scale_rows
            )
            for ranker_name in RANKERS:
                ranks = [
                    int(detail["true_rank"])
                    for row in scale_rows
                    if (
                        detail := row["radius_details"][str(radius)]["rankers"][
                            ranker_name
                        ]
                    )["true_rank"]
                    is not None
                ]
                top1 = sum(
                    1
                    for row in scale_rows
                    if bool(
                        row["radius_details"][str(radius)]["rankers"][ranker_name][
                            "top1_hit"
                        ]
                    )
                )
                top2 = sum(
                    1
                    for row in scale_rows
                    if bool(
                        row["radius_details"][str(radius)]["rankers"][ranker_name][
                            "top2_hit"
                        ]
                    )
                )
                top4 = sum(
                    1
                    for row in scale_rows
                    if bool(
                        row["radius_details"][str(radius)]["rankers"][ranker_name][
                            "top4_hit"
                        ]
                    )
                )
                top8 = sum(
                    1
                    for row in scale_rows
                    if bool(
                        row["radius_details"][str(radius)]["rankers"][ranker_name][
                            "top8_hit"
                        ]
                    )
                )
                shadow_count = len(scale_rows)
                summaries.append(
                    {
                        "scale": scale,
                        "radius": radius,
                        "ranker": ranker_name,
                        "shadow_count": shadow_count,
                        "true_boundary_right_of_shadow_count": true_right_count,
                        "true_boundary_within_radius_count": within_count,
                        "right_chamber_candidate_count": candidate_count,
                        "right_chamber_open_candidate_count": open_count,
                        "rank_of_true_boundary_by_boundary_score": median_rank(ranks),
                        "top1_recall": recall(top1, shadow_count),
                        "top2_recall": recall(top2, shadow_count),
                        "top4_recall": recall(top4, shadow_count),
                        "top8_recall": recall(top8, shadow_count),
                        "audit_failed_after_reorientation_if_top1": (
                            shadow_count - top1
                        ),
                    }
                )
    return summaries


def aggregate_summary(summary: list[dict[str, object]]) -> list[dict[str, object]]:
    """Return aggregate rows across all tested scales."""
    aggregates: list[dict[str, object]] = []
    for radius in RADII:
        for ranker_name in RANKERS:
            rows = [
                row
                for row in summary
                if int(row["radius"]) == radius and row["ranker"] == ranker_name
            ]
            shadow_count = sum(int(row["shadow_count"]) for row in rows)
            top1 = sum(
                int(row["shadow_count"]) - int(row["audit_failed_after_reorientation_if_top1"])
                for row in rows
            )
            top2 = sum(
                round(float(row["top2_recall"]) * int(row["shadow_count"]))
                for row in rows
            )
            top4 = sum(
                round(float(row["top4_recall"]) * int(row["shadow_count"]))
                for row in rows
            )
            top8 = sum(
                round(float(row["top8_recall"]) * int(row["shadow_count"]))
                for row in rows
            )
            within = sum(int(row["true_boundary_within_radius_count"]) for row in rows)
            aggregates.append(
                {
                    "scale": "ALL",
                    "radius": radius,
                    "ranker": ranker_name,
                    "shadow_count": shadow_count,
                    "true_boundary_right_of_shadow_count": sum(
                        int(row["true_boundary_right_of_shadow_count"])
                        for row in rows
                    ),
                    "true_boundary_within_radius_count": within,
                    "right_chamber_candidate_count": sum(
                        int(row["right_chamber_candidate_count"]) for row in rows
                    ),
                    "right_chamber_open_candidate_count": sum(
                        int(row["right_chamber_open_candidate_count"]) for row in rows
                    ),
                    "rank_of_true_boundary_by_boundary_score": None,
                    "top1_recall": recall(top1, shadow_count),
                    "top2_recall": recall(top2, shadow_count),
                    "top4_recall": recall(top4, shadow_count),
                    "top8_recall": recall(top8, shadow_count),
                    "audit_failed_after_reorientation_if_top1": shadow_count - top1,
                }
            )
    return aggregates


def decision(summary: list[dict[str, object]], aggregate: list[dict[str, object]]) -> str:
    """Return the next implementation direction from probe results."""
    r32_rows = [row for row in summary if int(row["radius"]) == 32]
    if r32_rows and all(
        float(row["true_boundary_within_radius_count"])
        / max(1, int(row["shadow_count"]))
        >= 0.80
        for row in r32_rows
    ):
        if max(float(row["top1_recall"]) for row in r32_rows) >= 0.50:
            return "IMPLEMENT_GUARDED_REORIENTATION"
        return "IMPLEMENT_BETTER_RIGHT_NEIGHBORHOOD_RANKER"
    r64_rows = [row for row in summary if int(row["radius"]) == 64]
    if r64_rows and all(
        float(row["true_boundary_within_radius_count"])
        / max(1, int(row["shadow_count"]))
        >= 0.80
        for row in r64_rows
    ):
        r64_aggregate = [
            row for row in aggregate if int(row["radius"]) == 64
        ]
        if max(float(row["top4_recall"]) for row in r64_aggregate) >= 0.80:
            return "ADD_SECOND_STAGE_RIGHT_CHAMBER_SELECTOR"
        return "IMPLEMENT_BETTER_RIGHT_NEIGHBORHOOD_RANKER"
    return "REORIENTATION_NEEDS_CHAMBER_EXPANSION"


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
    """Build the reorientation probe CLI."""
    parser = argparse.ArgumentParser(
        description="Probe rightward reorientation from semiprime shadows."
    )
    parser.add_argument("--scales", type=int, nargs="+", required=True)
    parser.add_argument("--sample-size", type=int, default=256)
    parser.add_argument("--candidate-bound", type=int, default=128)
    parser.add_argument("--max-divisor-floor", type=int, default=10_000)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the semiprime-shadow reorientation probe."""
    args = build_parser().parse_args(argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows = build_shadow_rows(
        [int(scale) for scale in args.scales],
        args.sample_size,
        args.candidate_bound,
        args.max_divisor_floor,
    )
    summaries = summary_rows(rows)
    aggregate = aggregate_summary(summaries)
    next_action = decision(summaries, aggregate)
    write_jsonl(rows, args.output_dir / "shadow_rows.jsonl")
    write_json(
        {"decision": next_action, "summary": summaries, "aggregate": aggregate},
        args.output_dir / "summary.json",
    )
    write_csv(summaries, args.output_dir / "summary.csv")
    write_csv(aggregate, args.output_dir / "aggregate_summary.csv")
    for row in summaries:
        if int(row["radius"]) in {32, 64} and row["ranker"] == "ranker_a":
            print(
                "scale={scale} radius={radius} shadows={shadow_count} "
                "within={true_boundary_within_radius_count} "
                "top1={top1_recall:.4f} top4={top4_recall:.4f}".format(**row)
            )
    print(f"decision={next_action}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
