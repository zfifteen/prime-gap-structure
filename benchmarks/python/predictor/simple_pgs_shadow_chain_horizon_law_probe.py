"""Mine horizon laws for false shadow-chain nodes."""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path
from statistics import median

from sympy import factorint


ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = ROOT / "src" / "python"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from simple_pgs_high_scale_chain_probe import run_probe, scale_summary  # noqa: E402
from z_band_prime_predictor.simple_pgs_controller import write_json  # noqa: E402
from z_band_prime_predictor.simple_pgs_generator import (  # noqa: E402
    CHAIN_FALLBACK_SOURCE,
    CHAIN_HORIZON_CLOSURE_SOURCE,
    DEFAULT_CANDIDATE_BOUND,
    DEFAULT_CHAIN_LIMIT,
    DEFAULT_VISIBLE_DIVISOR_BOUND,
    FALLBACK_SOURCE,
    PGS_SOURCE,
    admissible_offsets,
    closure_reason,
    visible_open_chain_offsets,
)


DEFAULT_SCALES = (10**12, 10**15, 10**18)
DEFAULT_ROWS_PATHS = (
    Path("output/simple_pgs_chain_horizon_closure_1e12_exact_sweep/rows.jsonl"),
    Path("output/simple_pgs_chain_horizon_closure_high_scale_probe/rows.jsonl"),
)
DEFAULT_SCALE_SUMMARY_PATHS = (
    Path("output/simple_pgs_chain_horizon_closure_1e12_exact_sweep/summary.json"),
    Path("output/simple_pgs_chain_horizon_closure_high_scale_probe/summary.json"),
)
DEFAULT_PER_ANCHOR_ROWS = {
    10**12: Path("output/simple_pgs_chain_horizon_closure_1e12_probe/rows.jsonl"),
    10**15: Path("output/simple_pgs_chain_horizon_closure_high_scale_probe/rows.jsonl"),
    10**18: Path("output/simple_pgs_chain_horizon_closure_high_scale_probe/rows.jsonl"),
}
CHAIN_SOURCES = {CHAIN_HORIZON_CLOSURE_SOURCE, CHAIN_FALLBACK_SOURCE}
H_SQRT = "H_sqrt"
NON_PROMOTABLE_LAWS = {
    H_SQRT,
    "H_visible_plus_position_64",
}


def read_jsonl(path: Path) -> list[dict[str, object]]:
    """Read JSONL rows."""
    if not path.exists():
        return []
    rows: list[dict[str, object]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def source_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    """Return per-anchor source rows from one JSONL payload."""
    return [row for row in rows if "p" in row and "source" in row]


def rows_by_scale(rows: list[dict[str, object]]) -> dict[int, list[dict[str, object]]]:
    """Group per-anchor source rows by scale."""
    grouped: dict[int, list[dict[str, object]]] = {}
    for row in source_rows(rows):
        scale = int(row["scale"])
        grouped.setdefault(scale, []).append(row)
    return grouped


def load_summary_rows(paths: list[Path]) -> dict[int, dict[str, object]]:
    """Load aggregate source summaries by scale."""
    summaries: dict[int, dict[str, object]] = {}
    for path in paths:
        if not path.exists():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        rows = payload.get("rows", [])
        if isinstance(rows, list):
            for row in rows:
                if isinstance(row, dict) and "scale" in row:
                    summaries[int(row["scale"])] = row
    return summaries


def load_or_generate_rows(
    scales: list[int],
    rows_paths: list[Path],
    sample_size: int,
    candidate_bound: int,
    chain_limit: int,
    visible_divisor_bound: int,
    output_dir: Path,
) -> dict[int, list[dict[str, object]]]:
    """Load existing per-anchor rows, regenerating missing scales."""
    grouped: dict[int, list[dict[str, object]]] = {}
    for path in rows_paths:
        for scale, rows in rows_by_scale(read_jsonl(path)).items():
            grouped.setdefault(scale, []).extend(rows)

    for scale in scales:
        if grouped.get(scale):
            continue
        fallback_path = DEFAULT_PER_ANCHOR_ROWS.get(scale)
        if fallback_path is not None:
            rows = rows_by_scale(read_jsonl(fallback_path)).get(scale, [])
            if rows:
                grouped[scale] = rows
                continue

        source_dir = output_dir / f"source_rows_{scale}"
        run_probe(
            [int(scale)],
            int(sample_size),
            int(candidate_bound),
            int(chain_limit),
            int(visible_divisor_bound),
            source_dir,
        )
        rows = rows_by_scale(read_jsonl(source_dir / "rows.jsonl")).get(scale, [])
        grouped[scale] = rows
    return grouped


def exact_least_factor(n: int) -> int:
    """Return the least nontrivial factor for audit-only mining."""
    factors = factorint(int(n))
    if not factors or list(factors) == [int(n)]:
        return int(n)
    return int(min(factors))


def visible_reason(
    p: int,
    offset: int,
    visible_divisor_bound: int,
) -> str | None:
    """Return visible closure evidence for one offset."""
    return closure_reason(int(p), int(offset), int(visible_divisor_bound))


def closure_vector_before(
    p: int,
    seed_offset: int,
    node_offset: int,
    visible_divisor_bound: int,
) -> tuple[list[str], int, int]:
    """Return visible closure vector before one node."""
    reasons: list[str] = []
    closed = 0
    open_count = 0
    for offset in admissible_offsets(int(p), int(node_offset) - 1):
        if offset <= int(seed_offset):
            continue
        reason = visible_reason(p, offset, visible_divisor_bound)
        if reason is None:
            open_count += 1
            reasons.append(f"{offset}:open")
        else:
            closed += 1
            reasons.append(f"{offset}:{reason}")
    return reasons, closed, open_count


def chain_offsets(
    p: int,
    seed_s0: int,
    candidate_bound: int,
    chain_limit: int,
    visible_divisor_bound: int,
) -> list[int]:
    """Return visible-open chain offsets from one seed."""
    return visible_open_chain_offsets(
        int(p),
        int(seed_s0) - int(p),
        int(candidate_bound),
        int(chain_limit),
        int(visible_divisor_bound),
    )


def chain_delta_vector(seed_offset: int, offsets: list[int]) -> list[int]:
    """Return deltas between seed and chain nodes."""
    deltas: list[int] = []
    previous = int(seed_offset)
    for offset in offsets:
        deltas.append(int(offset) - previous)
        previous = int(offset)
    return deltas


def json_value(value: object) -> str:
    """Return compact JSON for CSV cells."""
    return json.dumps(value, separators=(",", ":"))


def frontier_rows_for_chain(
    row: dict[str, object],
    candidate_bound: int,
    chain_limit: int,
    visible_divisor_bound: int,
) -> tuple[list[dict[str, object]], dict[str, object] | None]:
    """Return false-node frontier rows and one chain summary."""
    if row.get("source") not in CHAIN_SOURCES or row.get("q") is None:
        return [], None
    p = int(row["p"])
    seed_s0 = int(row["chain_seed"])
    terminal_q = int(row["q"])
    seed_offset = seed_s0 - p
    offsets = chain_offsets(
        p,
        seed_s0,
        candidate_bound,
        chain_limit,
        visible_divisor_bound,
    )
    nodes = [p + offset for offset in offsets]
    if terminal_q not in nodes:
        return [], None
    terminal_index = nodes.index(terminal_q) + 1
    deltas = chain_delta_vector(seed_offset, offsets)
    false_rows: list[dict[str, object]] = []
    least_factors: list[int] = []
    for index in range(1, terminal_index):
        node = nodes[index - 1]
        node_offset = offsets[index - 1]
        previous_offset = seed_offset if index == 1 else offsets[index - 2]
        next_offset = offsets[index] if index < len(offsets) else None
        delta_prev = node_offset - previous_offset
        delta_next = None if next_offset is None else next_offset - node_offset
        least_factor = exact_least_factor(node)
        least_factors.append(least_factor)
        reasons, closed_before, open_before = closure_vector_before(
            p,
            seed_offset,
            node_offset,
            visible_divisor_bound,
        )
        false_rows.append(
            {
                "scale": int(row["scale"]),
                "anchor_p": p,
                "seed_s0": seed_s0,
                "terminal_q": terminal_q,
                "terminal_index": terminal_index,
                "chain_index": index,
                "node_n": node,
                "least_factor_for_audit_only": least_factor,
                "least_factor_over_sqrt_node": least_factor / math.isqrt(node),
                "least_factor_over_visible_bound": least_factor
                / int(visible_divisor_bound),
                "node_offset_from_anchor": node_offset,
                "node_offset_from_seed": node_offset - seed_offset,
                "delta_prev": delta_prev,
                "delta_next": delta_next,
                "prefix_delta_vector": json_value(deltas[:index]),
                "chain_delta_vector": json_value(deltas),
                "node_mod_30": node % 30,
                "offset_mod_30": node_offset % 30,
                "visible_closed_count_before_node": closed_before,
                "visible_open_count_before_node": open_before,
                "closure_reason_vector_before_node": json_value(reasons),
                "candidate_bound": int(candidate_bound),
                "visible_divisor_bound": int(visible_divisor_bound),
                "required_horizon": 0,
                "zero_horizon": False,
                "required_horizon_over_sqrt_terminal": 0.0,
            }
        )
    required_horizon = max(least_factors) if least_factors else 0
    zero_horizon = terminal_index == 1
    over_sqrt_terminal = (
        0.0
        if required_horizon == 0
        else required_horizon / math.isqrt(terminal_q)
    )
    for frontier_row in false_rows:
        frontier_row["required_horizon"] = required_horizon
        frontier_row["zero_horizon"] = zero_horizon
        frontier_row["required_horizon_over_sqrt_terminal"] = over_sqrt_terminal
    return false_rows, {
        "scale": int(row["scale"]),
        "anchor_p": p,
        "seed_s0": seed_s0,
        "terminal_q": terminal_q,
        "terminal_index": terminal_index,
        "chain_delta_vector": deltas,
        "required_horizon": required_horizon,
        "zero_horizon": zero_horizon,
        "required_horizon_over_sqrt_terminal": over_sqrt_terminal,
    }


def horizon_laws(
    chain: dict[str, object],
    candidate_bound: int,
    visible_divisor_bound: int,
) -> dict[str, int]:
    """Return candidate horizon bounds for one chain."""
    anchor_p = int(chain["anchor_p"])
    seed_s0 = int(chain["seed_s0"])
    terminal_index = int(chain["terminal_index"])
    deltas = [int(value) for value in chain["chain_delta_vector"]]
    max_gap = max(deltas) if deltas else 0
    scale_n = anchor_p + int(candidate_bound)
    return {
        "H_visible": int(visible_divisor_bound),
        "H_dynamic_log2": max(64, math.ceil(0.5 * math.log(scale_n) ** 2)),
        "H_visible_plus_max_gap": int(visible_divisor_bound) + max_gap,
        "H_visible_plus_2max_gap": int(visible_divisor_bound) + (2 * max_gap),
        "H_visible_plus_position_64": int(visible_divisor_bound)
        + (terminal_index * 64),
        "H_visible_plus_seed_offset_1000": int(visible_divisor_bound)
        + ((seed_s0 - anchor_p) * 1000),
        "H_fixed_100k": 100_000,
        "H_fixed_1m": 1_000_000,
        "H_scale_quarter": math.floor(scale_n ** 0.25),
        "H_scale_third": math.floor(scale_n ** (1 / 3)),
        H_SQRT: math.isqrt(scale_n),
    }


def promotion_blocked_reason(law_id: str, ratios: list[float]) -> str:
    """Return why one horizon law cannot be promoted."""
    if law_id == H_SQRT:
        return "fallback_ceiling_comparator"
    if law_id == "H_visible_plus_position_64":
        return "uses_terminal_index_from_chain_result"
    if not ratios:
        return "no_chain_rows"
    if percentile(ratios, 95) >= 0.5:
        return "does_not_materially_beat_h_sqrt"
    return ""


def percentile(values: list[float], pct: float) -> float:
    """Return nearest-rank percentile."""
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, math.ceil((pct / 100.0) * len(ordered)) - 1)
    return float(ordered[index])


def summarize_scale_sources(
    scale: int,
    rows: list[dict[str, object]],
    sample_size: int,
    summary_row: dict[str, object] | None,
) -> dict[str, object]:
    """Return source percentages, preferring exact aggregate summaries."""
    if summary_row is not None:
        return {
            "scale": int(scale),
            "sample_size": int(summary_row.get("sample_size", sample_size)),
            "emitted_count": int(summary_row["emitted_count"]),
            "unresolved_count": int(summary_row.get("unresolved_count", 0)),
            "audit_failed": int(summary_row["audit_failed"]),
            "pgs_count": int(summary_row["pgs_count"]),
            "chain_horizon_closure_count": int(
                summary_row.get("chain_horizon_closure_count", 0)
            ),
            "chain_fallback_count": int(summary_row.get("chain_fallback_count", 0)),
            "fallback_count": int(summary_row.get("fallback_count", 0)),
            "pgs_percent": float(summary_row["pgs_percent"]),
            "chain_horizon_closure_percent": float(
                summary_row.get("chain_horizon_closure_percent", 0.0)
            ),
            "chain_fallback_percent": float(
                summary_row.get("chain_fallback_percent", 0.0)
            ),
            "fallback_percent": float(summary_row.get("fallback_percent", 0.0)),
            "unresolved_percent": float(summary_row.get("unresolved_percent", 0.0)),
        }
    return scale_summary(int(scale), rows, int(sample_size))


def law_report_rows(
    scale: int,
    chains: list[dict[str, object]],
    source_summary: dict[str, object],
    candidate_bound: int,
    visible_divisor_bound: int,
) -> list[dict[str, object]]:
    """Return horizon-law report rows for one scale."""
    reports: list[dict[str, object]] = []
    emitted_count = int(source_summary["emitted_count"])
    pgs_count = int(source_summary["pgs_count"])
    false_nodes_total = sum(1 for chain in chains if int(chain["required_horizon"]) > 0)
    false_node_count = 0
    for chain in chains:
        terminal_index = int(chain["terminal_index"])
        false_node_count += max(0, terminal_index - 1)
    laws = sorted(horizon_laws(chains[0], candidate_bound, visible_divisor_bound)) if chains else []
    for law_id in laws:
        false_nodes_closed = 0
        false_nodes_unclosed = 0
        chains_fully_closed = 0
        chains_under_closed = 0
        ratios: list[float] = []
        for chain in chains:
            h_value = horizon_laws(
                chain,
                candidate_bound,
                visible_divisor_bound,
            )[law_id]
            required_horizon = int(chain["required_horizon"])
            terminal_q = int(chain["terminal_q"])
            ratios.append(h_value / math.isqrt(terminal_q))
            if h_value >= required_horizon:
                chains_fully_closed += 1
            else:
                chains_under_closed += 1
            if required_horizon == 0:
                continue
            terminal_index = int(chain["terminal_index"])
            closed_for_chain = terminal_index - 1 if h_value >= required_horizon else None
            if closed_for_chain is None:
                closed_for_chain = 0
            false_nodes_closed += closed_for_chain
            false_nodes_unclosed += (terminal_index - 1) - closed_for_chain
        first_survivor_correct_count = chains_fully_closed
        projected_pgs_count = pgs_count + first_survivor_correct_count
        projected_pgs_rate = 0.0 if emitted_count == 0 else projected_pgs_count / emitted_count
        law_block_reason = promotion_blocked_reason(law_id, ratios)
        if chains_under_closed > 0:
            block_reason = "under_closes_false_nodes"
        else:
            block_reason = law_block_reason
        materially_beats_sqrt = block_reason == ""
        promotion_eligible = (
            bool(chains)
            and chains_under_closed == 0
            and materially_beats_sqrt
            and law_id not in NON_PROMOTABLE_LAWS
        )
        reports.append(
            {
                "scale": int(scale),
                "law_id": law_id,
                "chain_rows": len(chains),
                "chains_with_false_nodes": false_nodes_total,
                "false_nodes_total": false_node_count,
                "false_nodes_closed": false_nodes_closed,
                "false_nodes_unclosed": false_nodes_unclosed,
                "chains_fully_closed": chains_fully_closed,
                "chains_under_closed": chains_under_closed,
                "first_survivor_correct_count": first_survivor_correct_count,
                "projected_pgs_count": projected_pgs_count,
                "projected_pgs_rate": projected_pgs_rate,
                "projected_pgs_percent": projected_pgs_rate * 100.0,
                "max_h_over_sqrt_node": max(ratios) if ratios else 0.0,
                "p95_h_over_sqrt_node": percentile(ratios, 95),
                "promotion_eligible": promotion_eligible,
                "promotion_blocked_reason": "" if promotion_eligible else block_reason,
            }
        )
    return reports


def frontier_stats(chains: list[dict[str, object]]) -> dict[str, object]:
    """Return required-horizon summary stats."""
    horizons = [int(chain["required_horizon"]) for chain in chains]
    false_horizons = [value for value in horizons if value > 0]
    if not horizons:
        return {
            "chain_rows": 0,
            "zero_horizon_chains": 0,
            "median_required_horizon": 0,
            "p95_required_horizon": 0,
            "max_required_horizon": 0,
        }
    return {
        "chain_rows": len(chains),
        "zero_horizon_chains": sum(1 for value in horizons if value == 0),
        "median_required_horizon": median(horizons),
        "p95_required_horizon": percentile(horizons, 95),
        "max_required_horizon": max(horizons),
        "median_false_required_horizon": median(false_horizons)
        if false_horizons
        else 0,
    }


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


def run_horizon_law_probe(
    scales: list[int],
    rows_paths: list[Path],
    scale_summary_paths: list[Path],
    sample_size: int,
    candidate_bound: int,
    chain_limit: int,
    visible_divisor_bound: int,
    output_dir: Path,
) -> dict[str, object]:
    """Run the horizon-law probe and write artifacts."""
    output_dir.mkdir(parents=True, exist_ok=True)
    source_rows_by_scale = load_or_generate_rows(
        scales,
        rows_paths,
        sample_size,
        candidate_bound,
        chain_limit,
        visible_divisor_bound,
        output_dir,
    )
    summary_rows = load_summary_rows(scale_summary_paths)
    frontier_rows: list[dict[str, object]] = []
    law_rows: list[dict[str, object]] = []
    scale_summaries: list[dict[str, object]] = []
    all_chains_by_scale: dict[int, list[dict[str, object]]] = {}
    for scale in scales:
        rows = source_rows_by_scale.get(scale, [])
        source_summary = summarize_scale_sources(
            scale,
            rows,
            sample_size,
            summary_rows.get(scale),
        )
        chains: list[dict[str, object]] = []
        for row in rows:
            rows_for_chain, chain = frontier_rows_for_chain(
                row,
                candidate_bound,
                chain_limit,
                visible_divisor_bound,
            )
            frontier_rows.extend(rows_for_chain)
            if chain is not None:
                chains.append(chain)
        all_chains_by_scale[scale] = chains
        law_rows.extend(
            law_report_rows(
                scale,
                chains,
                source_summary,
                candidate_bound,
                visible_divisor_bound,
            )
        )
        scale_summaries.append(
            {
                **source_summary,
                **frontier_stats(chains),
            }
        )

    laws = sorted({row["law_id"] for row in law_rows})
    global_promotions: dict[str, bool] = {}
    for law_id in laws:
        rows_for_law = [row for row in law_rows if row["law_id"] == law_id]
        global_promotions[law_id] = (
            len(rows_for_law) == len(scales)
            and all(bool(row["promotion_eligible"]) for row in rows_for_law)
        )
    promoted = [law_id for law_id, eligible in global_promotions.items() if eligible]
    summary = {
        "scales": scale_summaries,
        "candidate_bound": int(candidate_bound),
        "chain_limit": int(chain_limit),
        "visible_divisor_bound": int(visible_divisor_bound),
        "law_promotion_eligible": global_promotions,
        "promoted_laws": promoted,
        "negative_result": not promoted,
        "negative_result_reason": None
        if promoted
        else (
            "No tested simple horizon family closed all false pre-terminal "
            "chain nodes while materially beating H_sqrt on every scale."
        ),
    }
    write_csv(frontier_rows, output_dir / "least_factor_frontier.csv")
    write_csv(law_rows, output_dir / "horizon_law_report.csv")
    write_json(summary, output_dir / "horizon_law_summary.json")
    return summary


def build_parser() -> argparse.ArgumentParser:
    """Build the horizon-law probe CLI."""
    parser = argparse.ArgumentParser(
        description="Mine shadow-chain least-factor frontier horizon laws."
    )
    parser.add_argument("--anchors", type=int, nargs="+", default=list(DEFAULT_SCALES))
    parser.add_argument("--sample-size", type=int, default=256)
    parser.add_argument("--candidate-bound", type=int, default=DEFAULT_CANDIDATE_BOUND)
    parser.add_argument("--chain-limit", type=int, default=DEFAULT_CHAIN_LIMIT)
    parser.add_argument(
        "--visible-divisor-bound",
        type=int,
        default=DEFAULT_VISIBLE_DIVISOR_BOUND,
    )
    parser.add_argument(
        "--rows-path",
        type=Path,
        action="append",
        default=[],
    )
    parser.add_argument(
        "--scale-summary-path",
        type=Path,
        action="append",
        default=[],
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output/simple_pgs_shadow_chain_horizon_law_probe"),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the horizon-law probe."""
    args = build_parser().parse_args(argv)
    rows_paths = args.rows_path or list(DEFAULT_ROWS_PATHS)
    scale_summary_paths = args.scale_summary_path or list(DEFAULT_SCALE_SUMMARY_PATHS)
    summary = run_horizon_law_probe(
        [int(scale) for scale in args.anchors],
        rows_paths,
        scale_summary_paths,
        int(args.sample_size),
        int(args.candidate_bound),
        int(args.chain_limit),
        int(args.visible_divisor_bound),
        args.output_dir,
    )
    for row in summary["scales"]:
        print(
            "scale={scale} pgs={pgs_percent:.2f}% "
            "chain_horizon_closure={chain_horizon_closure_percent:.2f}% "
            "chain_fallback={chain_fallback_percent:.2f}% "
            "fallback={fallback_percent:.2f}% unresolved={unresolved_percent:.2f}% "
            "max_required_horizon={max_required_horizon}".format(**row)
        )
    if summary["promoted_laws"]:
        print({"promoted_laws": summary["promoted_laws"]})
    else:
        print({"negative_result": summary["negative_result_reason"]})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
