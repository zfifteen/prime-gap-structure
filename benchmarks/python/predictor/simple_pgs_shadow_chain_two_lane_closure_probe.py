"""Measure two-lane closure for false shadow-chain nodes.

This probe tests the narrow follow-up to the failed scalar horizon laws:
false shadow-chain nodes can be closed from the small-divisor side or from the
centered semiprime side. It is audit/probe code only; it does not change the
minimal generator or promote a pure PGS rule.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_FRONTIER_PATH = (
    ROOT
    / "output"
    / "simple_pgs_shadow_chain_horizon_law_probe"
    / "least_factor_frontier.csv"
)
DEFAULT_HORIZON_SUMMARY_PATH = (
    ROOT
    / "output"
    / "simple_pgs_shadow_chain_horizon_law_probe"
    / "horizon_law_summary.json"
)
DEFAULT_OUTPUT_DIR = (
    ROOT / "output" / "simple_pgs_shadow_chain_two_lane_closure_probe"
)
DEFAULT_FRACTIONS = (0.10, 0.20, 0.25, 1.0 / 3.0, 0.40, 0.50)
LOW_FACTOR_LANE = "low_factor"
SQRT_ADJACENT_LANE = "sqrt_adjacent"
NULL_HALF_SQRT = "H_two_lane_half_sqrt_null"


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description="Probe two-lane closure of false shadow-chain nodes.",
    )
    parser.add_argument(
        "--frontier-path",
        type=Path,
        default=DEFAULT_FRONTIER_PATH,
        help="least_factor_frontier.csv from the horizon-law probe.",
    )
    parser.add_argument(
        "--horizon-summary-path",
        type=Path,
        default=DEFAULT_HORIZON_SUMMARY_PATH,
        help="horizon_law_summary.json from the horizon-law probe.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for route-switch artifacts.",
    )
    return parser


def read_csv(path: Path) -> list[dict[str, str]]:
    """Read one CSV file."""
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(rows: list[dict[str, object]], path: Path) -> None:
    """Write LF-terminated CSV rows."""
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(rows[0]),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def write_json(payload: dict[str, object], path: Path) -> None:
    """Write LF-terminated JSON."""
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def percentile(values: list[float], pct: float) -> float:
    """Return nearest-rank percentile."""
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, math.ceil((pct / 100.0) * len(ordered)) - 1)
    return float(ordered[index])


def chain_key(row: dict[str, str]) -> tuple[int, int, int, int]:
    """Return the stable chain key for one frontier row."""
    return (
        int(row["scale"]),
        int(row["anchor_p"]),
        int(row["seed_s0"]),
        int(row["terminal_q"]),
    )


def load_scale_summaries(path: Path) -> dict[int, dict[str, object]]:
    """Load source summaries from the horizon-law probe."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    summaries: dict[int, dict[str, object]] = {}
    for row in payload.get("scales", []):
        summaries[int(row["scale"])] = dict(row)
    return summaries


def enrich_frontier_rows(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    """Add left, centered, and two-lane distances to false-node rows."""
    enriched: list[dict[str, object]] = []
    for row in rows:
        node = int(row["node_n"])
        least_factor = int(row["least_factor_for_audit_only"])
        sqrt_node = math.isqrt(node)
        left_distance = least_factor
        center_distance = sqrt_node - least_factor
        if center_distance < 0:
            center_distance = 0
        two_lane_distance = min(left_distance, center_distance)
        if left_distance <= center_distance:
            lane = LOW_FACTOR_LANE
            closure_lane = "small_shadow_horizon"
        else:
            lane = SQRT_ADJACENT_LANE
            closure_lane = "balanced_semiprime_center"
        seed_offset = int(row["seed_s0"]) - int(row["anchor_p"])
        enriched.append(
            {
                "scale": int(row["scale"]),
                "anchor_p": int(row["anchor_p"]),
                "seed_s0": int(row["seed_s0"]),
                "terminal_q": int(row["terminal_q"]),
                "terminal_index": int(row["terminal_index"]),
                "chain_index": int(row["chain_index"]),
                "node_n": node,
                "least_factor_for_audit_only": least_factor,
                "sqrt_node": sqrt_node,
                "left_distance": left_distance,
                "center_distance": center_distance,
                "sqrt_minus_least_factor": center_distance,
                "two_lane_distance": two_lane_distance,
                "least_factor_over_sqrt_node": least_factor / sqrt_node,
                "center_distance_over_sqrt_node": center_distance / sqrt_node,
                "two_lane_distance_over_sqrt_node": two_lane_distance / sqrt_node,
                "lane": lane,
                "closure_lane": closure_lane,
                "node_offset_from_anchor": int(row["node_offset_from_anchor"]),
                "node_offset_from_seed": int(row["node_offset_from_seed"]),
                "seed_offset": seed_offset,
                "delta_prev": int(row["delta_prev"]),
                "delta_next": row["delta_next"],
                "prefix_delta_vector": row["prefix_delta_vector"],
                "chain_delta_vector": row["chain_delta_vector"],
                "carrier_to_node_delta": int(row["node_offset_from_anchor"]),
                "node_mod_30": int(row["node_mod_30"]),
                "offset_mod_30": int(row["offset_mod_30"]),
                "candidate_bound": int(row["candidate_bound"]),
                "visible_divisor_bound": int(row["visible_divisor_bound"]),
            }
        )
    return enriched


def candidate_law_value(
    law_id: str,
    row: dict[str, object],
    residue_envelope: dict[tuple[int, int, int], float],
) -> int:
    """Return the absolute two-lane horizon for one candidate law."""
    node = int(row["node_n"])
    sqrt_node = int(row["sqrt_node"])
    visible_bound = int(row["visible_divisor_bound"])
    seed_offset = int(row["seed_offset"])
    chain_index = int(row["chain_index"])
    deltas = [int(value) for value in json.loads(str(row["chain_delta_vector"]))]
    if law_id == "H_two_lane_fixed_1e5":
        return 100_000
    if law_id == "H_two_lane_fixed_1m":
        return 1_000_000
    if law_id == "H_two_lane_log2":
        return max(64, math.ceil(0.5 * math.log(node) ** 2))
    if law_id == "H_two_lane_seed_offset_family":
        return visible_bound + (seed_offset * 1000)
    if law_id == "H_two_lane_chain_position_family":
        return visible_bound + (chain_index * visible_bound)
    if law_id == "H_two_lane_delta_vector_family":
        return visible_bound + (max(deltas) * visible_bound)
    if law_id == "H_two_lane_residue_lane_classifier":
        key = (
            int(row["node_mod_30"]),
            int(row["offset_mod_30"]),
            int(row["chain_index"]),
        )
        ratio = residue_envelope[key]
        return math.ceil(ratio * sqrt_node)
    if law_id == NULL_HALF_SQRT:
        return sqrt_node // 2
    raise ValueError(f"unsupported law_id {law_id}")


def law_ids() -> tuple[str, ...]:
    """Return the exact lane-local laws tested by this probe."""
    return (
        "H_two_lane_fixed_1e5",
        "H_two_lane_fixed_1m",
        "H_two_lane_log2",
        "H_two_lane_seed_offset_family",
        "H_two_lane_chain_position_family",
        "H_two_lane_delta_vector_family",
        "H_two_lane_residue_lane_classifier",
        NULL_HALF_SQRT,
    )


def build_residue_envelope(
    rows: list[dict[str, object]],
) -> dict[tuple[int, int, int], float]:
    """Return an audit-fitted residue envelope used only as replay evidence."""
    envelope: dict[tuple[int, int, int], float] = {}
    for row in rows:
        key = (
            int(row["node_mod_30"]),
            int(row["offset_mod_30"]),
            int(row["chain_index"]),
        )
        ratio = float(row["two_lane_distance_over_sqrt_node"])
        envelope[key] = max(envelope.get(key, 0.0), ratio)
    return envelope


def scale_lane_summary(scale: int, rows: list[dict[str, object]]) -> dict[str, object]:
    """Summarize low-factor versus sqrt-adjacent lane structure."""
    distances = [int(row["two_lane_distance"]) for row in rows]
    ratios = [float(row["two_lane_distance_over_sqrt_node"]) for row in rows]
    low_factor_count = sum(1 for row in rows if row["lane"] == LOW_FACTOR_LANE)
    sqrt_adjacent_count = sum(1 for row in rows if row["lane"] == SQRT_ADJACENT_LANE)
    return {
        "scale": int(scale),
        "false_node_count": len(rows),
        "low_factor_count": low_factor_count,
        "sqrt_adjacent_count": sqrt_adjacent_count,
        "max_two_lane_distance": max(distances) if distances else 0,
        "p95_two_lane_distance": percentile([float(value) for value in distances], 95),
        "max_two_lane_distance_over_sqrt": max(ratios) if ratios else 0.0,
        "p95_two_lane_distance_over_sqrt": percentile(ratios, 95),
    }


def summarize_law(
    scale: int,
    rows: list[dict[str, object]],
    summaries: dict[int, dict[str, object]],
    law_id: str,
    residue_envelope: dict[tuple[int, int, int], float],
) -> dict[str, object]:
    """Summarize one lane-local law on one scale."""
    chains: dict[tuple[int, int, int, int], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        chains[
            (
                int(row["scale"]),
                int(row["anchor_p"]),
                int(row["seed_s0"]),
                int(row["terminal_q"]),
            )
        ].append(row)

    closed_false_nodes = 0
    unclosed_false_nodes = 0
    fully_closed_false_chains = 0
    underclosed_false_chains = 0
    h_ratios: list[float] = []
    for chain_rows in chains.values():
        chain_closed = True
        for row in chain_rows:
            horizon = candidate_law_value(law_id, row, residue_envelope)
            h_ratios.append(horizon / int(row["sqrt_node"]))
            if int(row["two_lane_distance"]) <= horizon:
                closed_false_nodes += 1
            else:
                unclosed_false_nodes += 1
                chain_closed = False
        if chain_closed:
            fully_closed_false_chains += 1
        else:
            underclosed_false_chains += 1

    source = summaries[scale]
    emitted_count = int(source["emitted_count"])
    pgs_count = int(source["pgs_count"])
    zero_horizon_chains = int(source["zero_horizon_chains"])
    projected_two_lane_count = zero_horizon_chains + fully_closed_false_chains
    projected_bridge_covered_count = pgs_count + projected_two_lane_count
    projected_bridge_covered_percent = (
        0.0
        if emitted_count == 0
        else (projected_bridge_covered_count / emitted_count) * 100.0
    )
    audit_fitted = law_id == "H_two_lane_residue_lane_classifier"
    null_comparator = law_id == NULL_HALF_SQRT
    max_ratio = max(h_ratios) if h_ratios else 0.0
    p95_ratio = percentile(h_ratios, 95)
    materially_below_half = max_ratio < 0.45 and p95_ratio < 0.40
    promotion_eligible = (
        unclosed_false_nodes == 0
        and materially_below_half
        and not audit_fitted
        and not null_comparator
    )
    if unclosed_false_nodes:
        blocked_reason = "under_closes_false_nodes"
    elif audit_fitted:
        blocked_reason = "uses_audit_fitted_frontier_envelope"
    elif null_comparator:
        blocked_reason = "half_sqrt_null_comparator"
    elif not materially_below_half:
        blocked_reason = "not_materially_below_half_sqrt"
    else:
        blocked_reason = ""
    return {
        "scale": int(scale),
        "law_id": law_id,
        "false_nodes_total": len(rows),
        "false_nodes_closed": closed_false_nodes,
        "false_nodes_unclosed": unclosed_false_nodes,
        "false_node_closure_percent": (
            0.0 if not rows else (closed_false_nodes / len(rows)) * 100.0
        ),
        "chains_with_false_nodes": len(chains),
        "false_chains_fully_closed": fully_closed_false_chains,
        "false_chains_underclosed": underclosed_false_chains,
        "projected_bridge_covered_count": projected_bridge_covered_count,
        "projected_bridge_covered_percent": projected_bridge_covered_percent,
        "max_horizon_over_sqrt": max_ratio,
        "p95_horizon_over_sqrt": p95_ratio,
        "runtime_computable_without_least_factor": True,
        "audit_fitted": audit_fitted,
        "pure_pgs_eligible": promotion_eligible,
        "promotion_blocked_reason": blocked_reason,
    }


def summarize_fraction(
    scale: int,
    rows: list[dict[str, object]],
    summaries: dict[int, dict[str, object]],
    fraction: float,
) -> dict[str, object]:
    """Summarize one two-lane horizon fraction on one scale."""
    chains: dict[tuple[int, int, int, int], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        chains[
            (
                int(row["scale"]),
                int(row["anchor_p"]),
                int(row["seed_s0"]),
                int(row["terminal_q"]),
            )
        ].append(row)
    closed_false_nodes = 0
    unclosed_false_nodes = 0
    fully_closed_false_chains = 0
    underclosed_false_chains = 0
    ratios: list[float] = []
    lane_counts = {
        "small_shadow_horizon": 0,
        "balanced_semiprime_center": 0,
    }
    for chain_rows in chains.values():
        chain_closed = True
        for row in chain_rows:
            ratio = float(row["two_lane_distance_over_sqrt_node"])
            ratios.append(ratio)
            if str(row["closure_lane"]) in lane_counts:
                lane_counts[str(row["closure_lane"])] += 1
            if ratio <= fraction:
                closed_false_nodes += 1
            else:
                unclosed_false_nodes += 1
                chain_closed = False
        if chain_closed:
            fully_closed_false_chains += 1
        else:
            underclosed_false_chains += 1

    source = summaries[scale]
    emitted_count = int(source["emitted_count"])
    pgs_count = int(source["pgs_count"])
    zero_horizon_chains = int(source["zero_horizon_chains"])
    projected_two_lane_count = zero_horizon_chains + fully_closed_false_chains
    projected_bridge_covered_count = pgs_count + projected_two_lane_count
    projected_bridge_covered_percent = (
        0.0
        if emitted_count == 0
        else (projected_bridge_covered_count / emitted_count) * 100.0
    )
    return {
        "scale": int(scale),
        "two_lane_fraction": fraction,
        "false_nodes_total": len(rows),
        "false_nodes_closed": closed_false_nodes,
        "false_nodes_unclosed": unclosed_false_nodes,
        "false_node_closure_percent": (
            0.0 if not rows else (closed_false_nodes / len(rows)) * 100.0
        ),
        "chains_with_false_nodes": len(chains),
        "false_chains_fully_closed": fully_closed_false_chains,
        "false_chains_underclosed": underclosed_false_chains,
        "zero_horizon_chains": zero_horizon_chains,
        "projected_two_lane_chain_rows": projected_two_lane_count,
        "projected_bridge_covered_count": projected_bridge_covered_count,
        "projected_bridge_covered_percent": projected_bridge_covered_percent,
        "small_shadow_horizon_count": lane_counts["small_shadow_horizon"],
        "balanced_semiprime_center_count": lane_counts["balanced_semiprime_center"],
        "max_two_lane_distance_over_sqrt": max(ratios) if ratios else 0.0,
        "p95_two_lane_distance_over_sqrt": percentile(ratios, 95),
        "bridge_eligible": bool(rows) and unclosed_false_nodes == 0,
        "pure_pgs_eligible": False,
        "promotion_note": "bridge_only_uses_divisor_arithmetic_not_pure_pgs",
    }


def run_probe(
    frontier_path: Path,
    horizon_summary_path: Path,
    output_dir: Path,
) -> dict[str, object]:
    """Run the two-lane closure probe and write artifacts."""
    output_dir.mkdir(parents=True, exist_ok=True)
    frontier_rows = read_csv(frontier_path)
    enriched = enrich_frontier_rows(frontier_rows)
    summaries = load_scale_summaries(horizon_summary_path)
    residue_envelope = build_residue_envelope(enriched)
    rows_by_scale: dict[int, list[dict[str, object]]] = defaultdict(list)
    for row in enriched:
        rows_by_scale[int(row["scale"])].append(row)

    summary_rows: list[dict[str, object]] = []
    lane_summary_rows: list[dict[str, object]] = []
    law_rows: list[dict[str, object]] = []
    for scale in sorted(rows_by_scale):
        lane_summary_rows.append(scale_lane_summary(scale, rows_by_scale[scale]))
        for fraction in DEFAULT_FRACTIONS:
            summary_rows.append(
                summarize_fraction(
                    scale,
                    rows_by_scale[scale],
                    summaries,
                    float(fraction),
                )
            )
        for law_id in law_ids():
            law_rows.append(
                summarize_law(
                    scale,
                    rows_by_scale[scale],
                    summaries,
                    law_id,
                    residue_envelope,
                )
            )

    best_rows = [
        row
        for row in summary_rows
        if abs(float(row["two_lane_fraction"]) - 0.5) < 0.0000001
    ]
    all_scales_bridge_eligible = bool(best_rows) and all(
        bool(row["bridge_eligible"]) for row in best_rows
    )
    payload = {
        "frontier_path": str(frontier_path),
        "horizon_summary_path": str(horizon_summary_path),
        "fractions_tested": list(DEFAULT_FRACTIONS),
        "strongest_supported_result": (
            "two_lane_half_sqrt_closes_all_false_shadow_chain_nodes"
            if all_scales_bridge_eligible
            else "two_lane_half_sqrt_did_not_close_all_false_shadow_chain_nodes"
        ),
        "all_scales_bridge_eligible": all_scales_bridge_eligible,
        "pure_pgs_eligible": any(row["pure_pgs_eligible"] for row in law_rows),
        "promotion_note": "The two-lane law is an exact deterministic bridge, not a pure PGS selector.",
        "warning": (
            "The half-sqrt two-lane bound is a deterministic divisor-search "
            "bridge. It is not a pure PGS horizon law because it still depends "
            "on sqrt-side divisor search."
        ),
        "lane_summary_rows": lane_summary_rows,
        "law_rows": law_rows,
        "summary_rows": summary_rows,
    }
    write_csv(enriched, output_dir / "two_lane_frontier.csv")
    write_csv(lane_summary_rows, output_dir / "lane_summary.csv")
    write_csv(law_rows, output_dir / "two_lane_law_report.csv")
    write_csv(summary_rows, output_dir / "two_lane_summary.csv")
    write_json(payload, output_dir / "two_lane_summary.json")
    return payload


def main() -> None:
    """Run the CLI."""
    args = build_parser().parse_args()
    payload = run_probe(
        Path(args.frontier_path),
        Path(args.horizon_summary_path),
        Path(args.output_dir),
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
