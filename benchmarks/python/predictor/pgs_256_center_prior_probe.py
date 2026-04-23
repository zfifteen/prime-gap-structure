#!/usr/bin/env python3
"""Probe fixed factor-side center priors on the 256-bit challenge surface."""

from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PREDICTOR_DIR = Path(__file__).resolve().parent
for path in (ROOT / "src" / "python", PREDICTOR_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import pgs_geofac_scaleup as base


DEFAULT_OUTPUT_DIR = ROOT / "output" / "geofac_scaleup"
DEFAULT_SCALE_BITS = 256
DEFAULT_RUNG = 1
DEFAULT_MIN_CENTER_BITS = 96
DEFAULT_MAX_CENTER_BITS = 108
SUMMARY_FILENAME = "pgs_256_center_prior_probe_summary.json"
DETAIL_FILENAME = "pgs_256_center_prior_probe_details.csv"
DETAIL_FIELDS = [
    "mode",
    "center_bits",
    "case_id",
    "small_factor_bits",
    "factor_in_final_window",
    "best_window_rank",
    "exact_recovery",
    "route_order_exact_recovery",
    "router_probe_count",
    "local_prime_tests",
    "local_prime_tests_route_order",
]


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description="Probe fixed factor-side center priors on the 256-bit challenge surface.",
    )
    parser.add_argument(
        "--scale-bits",
        type=int,
        default=DEFAULT_SCALE_BITS,
        help="Challenge surface bit size to probe.",
    )
    parser.add_argument(
        "--rung",
        type=int,
        choices=tuple(sorted(base.RUNG_CONFIGS)),
        default=DEFAULT_RUNG,
        help="Zoom rung to probe.",
    )
    parser.add_argument(
        "--min-center-bits",
        type=int,
        default=DEFAULT_MIN_CENTER_BITS,
        help="Minimum fixed small-factor bit guess to test.",
    )
    parser.add_argument(
        "--max-center-bits",
        type=int,
        default=DEFAULT_MAX_CENTER_BITS,
        help="Maximum fixed small-factor bit guess to test.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for JSON and CSV artifacts.",
    )
    parser.add_argument(
        "--route-only",
        action="store_true",
        help="Measure router quality only and skip local exact recovery.",
    )
    parser.add_argument(
        "--skip-baselines",
        action="store_true",
        help="Skip the pure-PGS and audited-prior comparison rows.",
    )
    return parser


def challenge_cases(scale_bits: int) -> list[base.ScaleupCase]:
    """Return the deterministic challenge-like cases for one stage."""
    return [case for case in base.CORPUS[scale_bits] if case.family == "challenge_like"][:1]


def route_case_fixed_center(
    case: base.ScaleupCase,
    rung: int,
    center_bits: int,
) -> tuple[list[base.BitWindow], int]:
    """Return the routed windows for one fixed small-factor bit guess."""
    config = base.RUNG_CONFIGS[rung]
    search_center = float(center_bits) - 0.5
    search_midpoint = base._anchor_from_log2(search_center, rounding="nearest")
    search_lo = max(config.widths[0] / 2.0, search_center - (config.widths[0] / 2.0))
    search_hi = min(
        case.case_bits - (config.widths[0] / 2.0),
        search_center + (config.widths[0] / 2.0),
    )
    beam_ranges = [(search_lo, search_hi)]
    beam_windows: list[base.BitWindow] = []
    probe_count = 0

    for level_index, width_bits in enumerate(config.widths):
        current_windows: list[base.BitWindow] = []
        points_per_range = config.scan_points if level_index == 0 else 2
        for range_index, (range_lo, range_hi) in enumerate(beam_ranges):
            centers = base._linspace(range_lo, range_hi, points_per_range)
            for center_index, center_log2 in enumerate(centers):
                midpoint_override = None
                if level_index == 0 and range_index == 0 and center_index == (points_per_range // 2):
                    midpoint_override = search_midpoint
                window, window_probes = base._scored_window(
                    case,
                    center_log2,
                    width_bits,
                    config.router_seed_budget,
                    midpoint_override=midpoint_override,
                )
                probe_count += window_probes
                current_windows.append(window)

        anchor_window, anchor_probes = base._scored_window(
            case,
            search_center,
            width_bits,
            config.router_seed_budget,
            midpoint_override=search_midpoint if level_index == 0 else None,
        )
        probe_count += anchor_probes
        current_windows.append(anchor_window)

        ranked_windows = base._dedupe_windows(current_windows, max(1, config.beam_width - 1))
        beam_windows = base._dedupe_windows([anchor_window] + ranked_windows, config.beam_width)
        if level_index + 1 >= len(config.widths):
            continue

        next_width = config.widths[level_index + 1]
        beam_ranges = []
        for window in beam_windows:
            half_span = max(width_bits / 8.0, next_width / 2.0)
            beam_ranges.append(
                (
                    max(next_width / 2.0, window.center_log2 - half_span),
                    min(case.case_bits - next_width / 2.0, window.center_log2 + half_span),
                )
            )

    return beam_windows[: config.top_windows], probe_count


def evaluate_fixed_center(
    case: base.ScaleupCase,
    scale_bits: int,
    rung: int,
    center_bits: int,
    route_only: bool = False,
) -> dict[str, object]:
    """Evaluate one case under one fixed small-factor bit guess."""
    config = base.RUNG_CONFIGS[rung]
    windows, probe_count = route_case_fixed_center(case, rung, center_bits)
    factor_log2 = case.small_factor_log2
    best_rank = None
    for index, window in enumerate(windows, start=1):
        if base._window_contains_factor(window, factor_log2):
            best_rank = index
            break

    factor_in_final_window = best_rank is not None
    if route_only:
        factor_recovered = None
        factor_recovered_route_order = None
        local_prime_tests = None
        local_prime_tests_route_order = None
    else:
        factor_recovered, local_prime_tests, factor_recovered_route_order, local_prime_tests_route_order = (
            base._local_pgs_search(
                case,
                windows,
                config.local_seed_budget,
                config.router_only_prime_budget,
                scale_bits,
            )
        )
    return {
        "mode": "fixed_center_bits",
        "center_bits": center_bits,
        "case_id": case.case_id,
        "small_factor_bits": case.small_factor.bit_length(),
        "factor_in_final_window": factor_in_final_window,
        "best_window_rank": best_rank,
        "exact_recovery": factor_recovered,
        "route_order_exact_recovery": factor_recovered_route_order,
        "router_probe_count": probe_count,
        "local_prime_tests": local_prime_tests,
        "local_prime_tests_route_order": local_prime_tests_route_order,
    }


def summarize_rows(rows: list[dict[str, object]]) -> dict[str, object]:
    """Return one summary payload for comparable result rows."""
    if not rows:
        raise ValueError("rows must not be empty")

    best_ranks = [
        int(row["best_window_rank"])
        for row in rows
        if row["best_window_rank"] is not None
    ]
    exact_rows = [row for row in rows if row["exact_recovery"] is not None]
    route_order_rows = [row for row in rows if row["route_order_exact_recovery"] is not None]
    local_rows = [row for row in rows if row["local_prime_tests"] is not None]
    local_route_rows = [row for row in rows if row["local_prime_tests_route_order"] is not None]
    return {
        "case_count": len(rows),
        "router_top1_recall": sum(int(bool(row["best_window_rank"] == 1)) for row in rows) / len(rows),
        "router_top4_recall": sum(int(bool(row["factor_in_final_window"])) for row in rows) / len(rows),
        "median_best_window_rank": (
            float(statistics.median(best_ranks)) if best_ranks else None
        ),
        "exact_recovery_recall": (
            sum(int(bool(row["exact_recovery"])) for row in exact_rows) / len(exact_rows)
            if exact_rows
            else None
        ),
        "route_order_exact_recovery_recall": (
            sum(int(bool(row["route_order_exact_recovery"])) for row in route_order_rows)
            / len(route_order_rows)
            if route_order_rows
            else None
        ),
        "total_router_probe_count": sum(int(row["router_probe_count"]) for row in rows),
        "total_local_prime_tests": (
            sum(int(row["local_prime_tests"]) for row in local_rows) if local_rows else None
        ),
        "total_local_prime_tests_route_order": (
            sum(int(row["local_prime_tests_route_order"]) for row in local_route_rows)
            if local_route_rows
            else None
        ),
    }


def baseline_rows(
    cases: list[base.ScaleupCase],
    scale_bits: int,
    rung: int,
    router_mode: str,
    route_only: bool = False,
) -> list[dict[str, object]]:
    """Return one baseline row set using the live scale-up harness."""
    rows: list[dict[str, object]] = []
    for case in cases:
        if route_only:
            windows, probe_count = base._route_case(case, rung, seed=0, router_mode=router_mode)
            factor_log2 = case.small_factor_log2
            best_rank = None
            for index, window in enumerate(windows, start=1):
                if base._window_contains_factor(window, factor_log2):
                    best_rank = index
                    break
            row = {
                "factor_in_final_window": best_rank is not None,
                "best_window_rank": best_rank,
                "factor_recovered": None,
                "factor_recovered_route_order": None,
                "router_probe_count": probe_count,
                "local_prime_tests": None,
                "local_prime_tests_route_order": None,
            }
        else:
            metrics = base._evaluate_case(case, scale_bits, rung, seed=0, router_mode=router_mode)
            row = dict(metrics.row)
        rows.append(
            {
                "mode": router_mode,
                "center_bits": None,
                "case_id": case.case_id,
                "small_factor_bits": case.small_factor.bit_length(),
                "factor_in_final_window": bool(row["factor_in_final_window"]),
                "best_window_rank": row["best_window_rank"],
                "exact_recovery": (
                    None if row["factor_recovered"] is None else bool(row["factor_recovered"])
                ),
                "route_order_exact_recovery": (
                    None
                    if row["factor_recovered_route_order"] is None
                    else bool(row["factor_recovered_route_order"])
                ),
                "router_probe_count": int(row["router_probe_count"]),
                "local_prime_tests": (
                    None if row["local_prime_tests"] is None else int(row["local_prime_tests"])
                ),
                "local_prime_tests_route_order": (
                    None
                    if row["local_prime_tests_route_order"] is None
                    else int(row["local_prime_tests_route_order"])
                ),
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    """Write one LF-terminated CSV detail file."""
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=DETAIL_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    """Run the fixed-center prior probe and write its artifacts."""
    args = build_parser().parse_args()
    if args.min_center_bits > args.max_center_bits:
        raise ValueError("min_center_bits must not exceed max_center_bits")

    started = time.perf_counter()
    cases = challenge_cases(args.scale_bits)
    if not cases:
        raise ValueError(f"no challenge_like cases found for scale_bits={args.scale_bits}")

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    detail_rows: list[dict[str, object]] = []
    fixed_center_summaries: dict[str, dict[str, object]] = {}
    best_center_bits = None
    best_center_key = None

    for center_bits in range(args.min_center_bits, args.max_center_bits + 1):
        rows = [
            evaluate_fixed_center(
                case,
                args.scale_bits,
                args.rung,
                center_bits,
                route_only=args.route_only,
            )
            for case in cases
        ]
        detail_rows.extend(rows)
        summary = summarize_rows(rows)
        fixed_center_summaries[str(center_bits)] = summary
        rank_key = (
            -float(summary["router_top4_recall"]),
            -float(summary["router_top1_recall"]),
            -float(summary["exact_recovery_recall"] or 0.0),
            int(summary["total_router_probe_count"]),
            int(summary["total_local_prime_tests"] or 0),
            center_bits,
        )
        if best_center_key is None or rank_key < best_center_key:
            best_center_key = rank_key
            best_center_bits = center_bits

    pure_summary = None
    audited_summary = None
    if not args.skip_baselines:
        pure_rows = baseline_rows(
            cases,
            args.scale_bits,
            args.rung,
            router_mode="pure_pgs",
            route_only=args.route_only,
        )
        audited_rows = baseline_rows(
            cases,
            args.scale_bits,
            args.rung,
            router_mode="audited_family_prior",
            route_only=args.route_only,
        )
        detail_rows.extend(pure_rows)
        detail_rows.extend(audited_rows)
        pure_summary = summarize_rows(pure_rows)
        audited_summary = summarize_rows(audited_rows)

    summary = {
        "scale_bits": args.scale_bits,
        "rung": args.rung,
        "evaluation_mode": ("route_only" if args.route_only else "route_plus_local_recovery"),
        "target_case_ids": [case.case_id for case in cases],
        "target_moduli": [str(case.n) for case in cases],
        "tested_center_bits": list(range(args.min_center_bits, args.max_center_bits + 1)),
        "best_fixed_center_bits": best_center_bits,
        "best_fixed_center_summary": None if best_center_bits is None else fixed_center_summaries[str(best_center_bits)],
        "fixed_center_summaries": fixed_center_summaries,
        "pure_pgs_summary": pure_summary,
        "audited_family_prior_summary": audited_summary,
        "runtime_seconds": time.perf_counter() - started,
    }

    summary_path = output_dir / SUMMARY_FILENAME
    detail_path = output_dir / DETAIL_FILENAME
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    write_csv(detail_path, detail_rows)

    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
