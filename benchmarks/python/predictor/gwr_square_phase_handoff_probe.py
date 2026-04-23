#!/usr/bin/env python3
"""Probe whether d=4 square-phase utilization predicts next-gap triad return."""

from __future__ import annotations

import argparse
import csv
import json
import math
import time
from collections import Counter, defaultdict
from pathlib import Path

from sympy import nextprime


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DETAIL_CSV = ROOT / "output" / "gwr_dni_gap_type_catalog_details.csv"
DEFAULT_OUTPUT_DIR = ROOT / "output"
DEFAULT_SAMPLE_MIN_POWER = 7
DEFAULT_SAMPLE_MAX_POWER = 18
DEFAULT_MIN_STRATUM_COUNT = 8
TRIAD_STATES = (
    "o2_odd_semiprime|d<=4",
    "o4_odd_semiprime|d<=4",
    "o6_odd_semiprime|d<=4",
)
TAIL_QUANTILE_DENOMINATOR = 5
STRATA_CSV_FIELDS = (
    "surface_group",
    "population",
    "scheme_name",
    "stratum_key",
    "count",
    "low_count",
    "high_count",
    "low_utilization_min",
    "low_utilization_max",
    "high_utilization_min",
    "high_utilization_max",
    "low_next_triad_share",
    "high_next_triad_share",
    "lift",
)


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Measure whether current d=4 square-phase utilization predicts "
            "next-gap return to the odd-semiprime triad."
        ),
    )
    parser.add_argument(
        "--detail-csv",
        type=Path,
        default=DEFAULT_DETAIL_CSV,
        help="Catalog detail CSV emitted by gwr_dni_gap_type_catalog.py.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for JSON and CSV artifacts.",
    )
    parser.add_argument(
        "--sample-min-power",
        type=int,
        default=DEFAULT_SAMPLE_MIN_POWER,
        help="Smallest sampled decade power included in the pooled sampled-window surface.",
    )
    parser.add_argument(
        "--sample-max-power",
        type=int,
        default=DEFAULT_SAMPLE_MAX_POWER,
        help="Largest sampled decade power included in the pooled sampled-window surface.",
    )
    parser.add_argument(
        "--min-stratum-count",
        type=int,
        default=DEFAULT_MIN_STRATUM_COUNT,
        help="Minimum row count required before a matched utilization split is scored.",
    )
    return parser


def d_bucket(next_dmin: int) -> str:
    """Return the coarse divisor bucket used by the reduced grammar."""
    if next_dmin <= 4:
        return "d<=4"
    if next_dmin <= 16:
        return "5<=d<=16"
    if next_dmin <= 64:
        return "17<=d<=64"
    return "d>64"


def reduced_state(row: dict[str, object]) -> str:
    """Return the reduced-state label for one catalog row."""
    return f"o{row['first_open_offset']}_{row['carrier_family']}|{d_bucket(int(row['next_dmin']))}"


def square_phase_payload(winner: int, next_right_prime: int) -> dict[str, float | int]:
    """Return the square-phase utilization payload for one d=4 winner gap."""
    next_square_root = int(nextprime(math.isqrt(winner)))
    next_square = next_square_root * next_square_root
    threat_distance = next_square - winner
    if threat_distance <= 0:
        raise ValueError("next prime square must lie strictly above the winner")
    used_distance = next_right_prime - winner
    return {
        "next_prime_square": next_square,
        "square_threat_distance": threat_distance,
        "square_arrival_margin": next_square - next_right_prime,
        "square_phase_utilization": used_distance / threat_distance,
    }


def load_detail_rows(detail_csv: Path) -> list[dict[str, object]]:
    """Load the catalog detail CSV."""
    if not detail_csv.exists():
        raise FileNotFoundError(f"detail CSV does not exist: {detail_csv}")

    with detail_csv.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError("detail CSV must contain at least one row")
    return rows


def d4_transition_rows(detail_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    """Return one row per current d=4 gap with next-gap handoff data attached."""
    by_surface: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in detail_rows:
        by_surface[str(row["surface_label"])].append(row)

    transitions: list[dict[str, object]] = []
    for surface_label in sorted(by_surface):
        surface_rows = sorted(
            by_surface[surface_label],
            key=lambda row: int(row["surface_row_index"]),
        )
        for current_row, next_row in zip(surface_rows[:-1], surface_rows[1:]):
            current_dmin = int(current_row["next_dmin"])
            if current_dmin != 4:
                continue

            current_winner = int(current_row["winner"])
            current_next_right_prime = int(current_row["next_right_prime"])
            square_payload = square_phase_payload(
                winner=current_winner,
                next_right_prime=current_next_right_prime,
            )
            next_state = reduced_state(next_row)

            transitions.append(
                {
                    "surface_label": str(current_row["surface_label"]),
                    "surface_kind": str(current_row["surface_kind"]),
                    "power": (
                        None
                        if str(current_row["power"]) == ""
                        else int(current_row["power"])
                    ),
                    "current_right_prime": int(current_row["current_right_prime"]),
                    "current_gap_width": int(current_row["next_gap_width"]),
                    "current_residue_mod30": int(current_row["residue_mod30"]),
                    "current_first_open_offset": int(current_row["first_open_offset"]),
                    "current_peak_offset": int(current_row["next_peak_offset"]),
                    "current_carrier_family": str(current_row["carrier_family"]),
                    "current_state": reduced_state(current_row),
                    "current_winner": current_winner,
                    "current_next_right_prime": current_next_right_prime,
                    "next_state": next_state,
                    "next_carrier_family": str(next_row["carrier_family"]),
                    "next_dmin": int(next_row["next_dmin"]),
                    "next_is_triad": int(next_state in TRIAD_STATES),
                    **square_payload,
                }
            )

    if not transitions:
        raise ValueError("detail surface did not contain any d=4 transitions")
    return transitions


def family_distribution(rows: list[dict[str, object]]) -> dict[str, float]:
    """Return next-family shares in descending-count order."""
    counter = Counter(str(row["next_carrier_family"]) for row in rows)
    total = len(rows)
    return {
        family: counter[family] / total
        for family, _count in counter.most_common()
    }


def tail_quintile_metrics(rows: list[dict[str, object]]) -> dict[str, object]:
    """Return low-versus-high utilization tail metrics."""
    if len(rows) < TAIL_QUANTILE_DENOMINATOR:
        raise ValueError("need at least five rows for tail-quintile metrics")

    ordered = sorted(rows, key=lambda row: float(row["square_phase_utilization"]))
    tail_count = max(1, len(ordered) // TAIL_QUANTILE_DENOMINATOR)
    low_rows = ordered[:tail_count]
    high_rows = ordered[-tail_count:]

    return {
        "tail_count": tail_count,
        "low_utilization_range": [
            float(low_rows[0]["square_phase_utilization"]),
            float(low_rows[-1]["square_phase_utilization"]),
        ],
        "high_utilization_range": [
            float(high_rows[0]["square_phase_utilization"]),
            float(high_rows[-1]["square_phase_utilization"]),
        ],
        "low_next_triad_share": sum(int(row["next_is_triad"]) for row in low_rows) / tail_count,
        "high_next_triad_share": sum(int(row["next_is_triad"]) for row in high_rows) / tail_count,
        "low_next_d_le4_share": sum(int(int(row["next_dmin"]) <= 4) for row in low_rows) / tail_count,
        "high_next_d_le4_share": sum(int(int(row["next_dmin"]) <= 4) for row in high_rows) / tail_count,
        "low_next_family_distribution": family_distribution(low_rows),
        "high_next_family_distribution": family_distribution(high_rows),
    }


def matched_split_metrics(
    rows: list[dict[str, object]],
    *,
    stratum_keys: tuple[str, ...],
    min_stratum_count: int,
) -> tuple[dict[str, object], list[dict[str, object]]]:
    """Compare lower versus higher utilization halves within the same stratum mix."""
    strata: dict[tuple[object, ...], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        strata[tuple(row[key] for key in stratum_keys)].append(row)

    low_weighted_share = 0.0
    high_weighted_share = 0.0
    total_weight = 0.0
    positive_lift_strata_count = 0
    negative_lift_strata_count = 0
    equal_lift_strata_count = 0
    stratum_rows: list[dict[str, object]] = []

    for key, members in sorted(strata.items()):
        if len(members) < min_stratum_count:
            continue

        ordered = sorted(members, key=lambda row: float(row["square_phase_utilization"]))
        half_count = len(ordered) // 2
        if half_count == 0:
            continue

        low_rows = ordered[:half_count]
        high_rows = ordered[-half_count:]
        low_share = sum(int(row["next_is_triad"]) for row in low_rows) / half_count
        high_share = sum(int(row["next_is_triad"]) for row in high_rows) / half_count
        lift = low_share - high_share
        positive_lift_strata_count += int(lift > 0)
        negative_lift_strata_count += int(lift < 0)
        equal_lift_strata_count += int(lift == 0)
        low_weighted_share += half_count * low_share
        high_weighted_share += half_count * high_share
        total_weight += half_count

        stratum_rows.append(
            {
                "stratum_key": "|".join(str(component) for component in key),
                "count": len(members),
                "low_count": half_count,
                "high_count": half_count,
                "low_utilization_min": float(low_rows[0]["square_phase_utilization"]),
                "low_utilization_max": float(low_rows[-1]["square_phase_utilization"]),
                "high_utilization_min": float(high_rows[0]["square_phase_utilization"]),
                "high_utilization_max": float(high_rows[-1]["square_phase_utilization"]),
                "low_next_triad_share": low_share,
                "high_next_triad_share": high_share,
                "lift": lift,
            }
        )

    if total_weight == 0:
        raise ValueError("matched split produced no usable strata")

    summary = {
        "stratum_keys": list(stratum_keys),
        "matched_strata_count": len(stratum_rows),
        "matched_total_weight_per_side": int(total_weight),
        "low_next_triad_share": low_weighted_share / total_weight,
        "high_next_triad_share": high_weighted_share / total_weight,
        "lift": (low_weighted_share - high_weighted_share) / total_weight,
        "positive_lift_strata_count": positive_lift_strata_count,
        "negative_lift_strata_count": negative_lift_strata_count,
        "equal_lift_strata_count": equal_lift_strata_count,
    }
    return summary, stratum_rows


def population_summary(
    rows: list[dict[str, object]],
    *,
    base_scheme_keys: tuple[str, ...],
    confirm_scheme_keys: tuple[str, ...],
    residue_confirm_scheme_keys: tuple[str, ...],
    min_stratum_count: int,
) -> tuple[dict[str, object], dict[str, list[dict[str, object]]]]:
    """Return summary payload plus stratum detail rows for one population."""
    if not rows:
        raise ValueError("population rows must not be empty")

    base_summary, base_rows = matched_split_metrics(
        rows,
        stratum_keys=base_scheme_keys,
        min_stratum_count=min_stratum_count,
    )
    confirm_summary, confirm_rows = matched_split_metrics(
        rows,
        stratum_keys=confirm_scheme_keys,
        min_stratum_count=min_stratum_count,
    )
    residue_confirm_summary, residue_confirm_rows = matched_split_metrics(
        rows,
        stratum_keys=residue_confirm_scheme_keys,
        min_stratum_count=min_stratum_count,
    )

    return (
        {
            "transition_count": len(rows),
            "tail_quintile": tail_quintile_metrics(rows),
            "matched_base_scheme": base_summary,
            "matched_gap_width_confirmatory_scheme": confirm_summary,
            "matched_gap_width_residue_confirmatory_scheme": residue_confirm_summary,
        },
        {
            "matched_base_scheme": base_rows,
            "matched_gap_width_confirmatory_scheme": confirm_rows,
            "matched_gap_width_residue_confirmatory_scheme": residue_confirm_rows,
        },
    )


def _write_strata_csv(path: Path, rows: list[dict[str, object]]) -> None:
    """Write one LF-terminated strata CSV."""
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=STRATA_CSV_FIELDS,
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def summarize_surface_groups(
    transitions: list[dict[str, object]],
    *,
    sample_min_power: int,
    sample_max_power: int,
    min_stratum_count: int,
) -> tuple[dict[str, object], list[dict[str, object]]]:
    """Return the JSON summary plus flattened stratum detail rows."""
    baseline_rows = [
        row for row in transitions if str(row["surface_label"]) == "baseline_1e6"
    ]
    sampled_rows = [
        row
        for row in transitions
        if str(row["surface_kind"]) == "sampled_decade_window"
        and row["power"] is not None
        and sample_min_power <= int(row["power"]) <= sample_max_power
    ]

    if not baseline_rows:
        raise ValueError("baseline_1e6 transitions were not found in the catalog detail CSV")
    if not sampled_rows:
        raise ValueError("requested sampled transition surface is empty")

    summary: dict[str, object] = {
        "sample_power_range": [sample_min_power, sample_max_power],
        "min_stratum_count": min_stratum_count,
        "surface_groups": {},
    }
    flattened_strata_rows: list[dict[str, object]] = []

    surface_specs = (
        (
            "baseline_1e6",
            "exact <=1e6",
            baseline_rows,
        ),
        (
            f"sampled_windows_1e{sample_min_power}_1e{sample_max_power}",
            f"sampled windows 10^{sample_min_power}..10^{sample_max_power}",
            sampled_rows,
        ),
    )

    for surface_group, display_label, surface_rows in surface_specs:
        all_d4_summary, all_d4_strata = population_summary(
            surface_rows,
            base_scheme_keys=(
                "current_carrier_family",
                "current_peak_offset",
                "current_first_open_offset",
            ),
            confirm_scheme_keys=(
                "current_carrier_family",
                "current_peak_offset",
                "current_first_open_offset",
                "current_gap_width",
            ),
            residue_confirm_scheme_keys=(
                "current_carrier_family",
                "current_peak_offset",
                "current_first_open_offset",
                "current_gap_width",
                "current_residue_mod30",
            ),
            min_stratum_count=min_stratum_count,
        )

        odd_semiprime_rows = [
            row for row in surface_rows if str(row["current_carrier_family"]) == "odd_semiprime"
        ]
        odd_semiprime_summary, odd_semiprime_strata = population_summary(
            odd_semiprime_rows,
            base_scheme_keys=("current_peak_offset", "current_first_open_offset"),
            confirm_scheme_keys=(
                "current_peak_offset",
                "current_first_open_offset",
                "current_gap_width",
            ),
            residue_confirm_scheme_keys=(
                "current_peak_offset",
                "current_first_open_offset",
                "current_gap_width",
                "current_residue_mod30",
            ),
            min_stratum_count=min_stratum_count,
        )

        summary["surface_groups"][surface_group] = {
            "display_label": display_label,
            "transition_count": len(surface_rows),
            "all_d4": all_d4_summary,
            "odd_semiprime_only": odd_semiprime_summary,
        }

        for population, scheme_rows_map in (
            ("all_d4", all_d4_strata),
            ("odd_semiprime_only", odd_semiprime_strata),
        ):
            for scheme_name, scheme_rows in scheme_rows_map.items():
                for row in scheme_rows:
                    flattened_strata_rows.append(
                        {
                            "surface_group": surface_group,
                            "population": population,
                            "scheme_name": scheme_name,
                            **row,
                        }
                    )

    return summary, flattened_strata_rows


def main(argv: list[str] | None = None) -> int:
    """Run the square-phase handoff probe and write artifacts."""
    args = build_parser().parse_args(argv)
    if args.sample_min_power < 1:
        raise ValueError("sample_min_power must be at least 1")
    if args.sample_max_power < args.sample_min_power:
        raise ValueError("sample_max_power must be at least sample_min_power")
    if args.min_stratum_count < 2:
        raise ValueError("min_stratum_count must be at least 2")

    started_at = time.time()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    detail_rows = load_detail_rows(args.detail_csv)
    transitions = d4_transition_rows(detail_rows)
    summary, strata_rows = summarize_surface_groups(
        transitions,
        sample_min_power=args.sample_min_power,
        sample_max_power=args.sample_max_power,
        min_stratum_count=args.min_stratum_count,
    )
    summary["detail_csv"] = str(args.detail_csv)
    summary["transition_count"] = len(transitions)
    summary["runtime_seconds"] = time.time() - started_at

    summary_path = args.output_dir / "gwr_square_phase_handoff_summary.json"
    strata_path = args.output_dir / "gwr_square_phase_handoff_strata.csv"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    _write_strata_csv(strata_path, strata_rows)

    baseline = summary["surface_groups"]["baseline_1e6"]["all_d4"]["matched_base_scheme"]
    sampled_key = f"sampled_windows_1e{args.sample_min_power}_1e{args.sample_max_power}"
    sampled = summary["surface_groups"][sampled_key]["all_d4"]["matched_base_scheme"]
    print(
        "gwr-square-phase-handoff:"
        f" transitions={summary['transition_count']}"
        f" baseline_lift={baseline['lift']}"
        f" sampled_lift={sampled['lift']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
