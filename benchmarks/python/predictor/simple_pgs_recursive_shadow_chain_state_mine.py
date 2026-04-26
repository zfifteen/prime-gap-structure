"""Mine recursive state breaks inside high-scale shadow chains."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = ROOT / "src" / "python"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from z_band_prime_predictor.simple_pgs_controller import (  # noqa: E402
    write_json,
    write_jsonl,
)
from z_band_prime_predictor.simple_pgs_generator import (  # noqa: E402
    CHAIN_FALLBACK_SOURCE,
    DEFAULT_CHAIN_LIMIT,
    DEFAULT_VISIBLE_DIVISOR_BOUND,
    PGS_SOURCE,
    admissible_offsets,
    closure_reason,
    visible_open_chain_offsets,
)


RULE_IDS = (
    "rule_r1_first_recursive_signature_break",
    "rule_r2_first_delta_multiset_incompatible",
    "rule_r3_first_recursive_open_density_drop",
    "rule_r4_first_hidden_proxy_loss",
    "rule_r5_first_no_recursive_hidden_successor",
    "rule_r6_best_ranker_b_after_any_break",
)


def read_jsonl(path: Path) -> list[dict[str, object]]:
    """Read LF-terminated JSONL rows."""
    rows: list[dict[str, object]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def visible_reason(
    p: int,
    offset: int,
    visible_divisor_bound: int,
) -> str | None:
    """Return bounded visible closure evidence for one offset."""
    return closure_reason(int(p), int(offset), int(visible_divisor_bound))


def reason_category(reason: str | None) -> str:
    """Return a compact closure category."""
    if reason is None:
        return "open"
    return reason.split(":", 1)[0]


def closure_vector_between(
    p: int,
    left_offset: int,
    right_offset: int,
    visible_divisor_bound: int,
) -> list[str]:
    """Return closure categories between two offsets."""
    vector: list[str] = []
    for offset in admissible_offsets(int(p), int(right_offset) - 1):
        if offset <= int(left_offset):
            continue
        vector.append(reason_category(visible_reason(p, offset, visible_divisor_bound)))
    return vector


def hidden_proxy_vector(length: int) -> list[str]:
    """Return the label-free proxy for visible-open unresolved chain nodes."""
    return ["visible_open_unresolved"] * int(length)


def multiset(values: list[int]) -> dict[str, int]:
    """Return a JSON-stable multiset."""
    return {str(key): int(count) for key, count in sorted(Counter(values).items())}


def density(count: int, span: int) -> float:
    """Return count / span."""
    return 0.0 if int(span) <= 0 else int(count) / int(span)


def rank_maps(
    p: int,
    seed_offset: int,
    candidate_bound: int,
    visible_divisor_bound: int,
) -> dict[str, dict[int, int]]:
    """Return ranker maps over the seed-right chamber."""
    open_offsets = admissible_offsets(int(p), int(candidate_bound))
    right_offsets = [offset for offset in open_offsets if offset > int(seed_offset)]

    def closed_open_before(offset: int) -> tuple[int, int]:
        closed = 0
        open_count = 0
        for prior in open_offsets:
            if prior <= int(seed_offset):
                continue
            if prior >= int(offset):
                break
            if visible_reason(p, prior, visible_divisor_bound) is None:
                open_count += 1
            else:
                closed += 1
        return closed, open_count

    ranker_b = sorted(
        right_offsets,
        key=lambda offset: (
            0
            if visible_reason(p, offset, visible_divisor_bound) is None
            and closed_open_before(offset)[1] == 0
            else 1,
            offset,
        ),
    )
    ranker_c = sorted(
        right_offsets,
        key=lambda offset: (
            1 if visible_reason(p, offset, visible_divisor_bound) is None else 0,
            closed_open_before(offset)[0] - (2 * closed_open_before(offset)[1]),
            closed_open_before(offset)[0],
            -abs(offset - int(seed_offset)),
        ),
        reverse=True,
    )
    return {
        "ranker_b": {offset: rank for rank, offset in enumerate(ranker_b, start=1)},
        "ranker_c": {offset: rank for rank, offset in enumerate(ranker_c, start=1)},
    }


def chain_offsets_from_seed(
    p: int,
    seed: int,
    candidate_bound: int,
    chain_limit: int,
    visible_divisor_bound: int,
) -> list[int]:
    """Return visible-open chain offsets after seed."""
    return visible_open_chain_offsets(
        int(p),
        int(seed) - int(p),
        int(candidate_bound),
        int(chain_limit),
        int(visible_divisor_bound),
    )


def recursive_offsets_from_node(
    p: int,
    node: int,
    candidate_bound: int,
    recursive_depth: int,
    visible_divisor_bound: int,
) -> list[int]:
    """Return recursive visible-open offsets after one chain node."""
    return visible_open_chain_offsets(
        int(p),
        int(node) - int(p),
        int(candidate_bound),
        int(recursive_depth),
        int(visible_divisor_bound),
    )


def breaks_prefix_signature(
    prefix_deltas: list[int],
    prefix_mods: list[int],
    recursive_deltas: list[int],
    recursive_mods: list[int],
) -> bool:
    """Return True when recursive continuation changes prefix state."""
    if not recursive_deltas:
        return True
    prefix_tail_deltas = prefix_deltas[-len(recursive_deltas) :]
    prefix_tail_mods = prefix_mods[-len(recursive_mods) :]
    return (
        recursive_deltas != prefix_tail_deltas
        or recursive_mods != prefix_tail_mods
    )


def row_for_node(
    record: dict[str, object],
    chain_offsets: list[int],
    index: int,
    candidate_bound: int,
    recursive_depth: int,
    visible_divisor_bound: int,
    ranks: dict[str, dict[int, int]],
) -> dict[str, object]:
    """Return one recursive state row."""
    p = int(record["p"])
    seed = int(record["chain_seed"])
    seed_offset = seed - p
    true_q = int(record["q"])
    node_offset = int(chain_offsets[index - 1])
    node = p + node_offset

    prefix_offsets = chain_offsets[:index]
    prefix_positions = list(range(0, index + 1))
    prefix_nodes = [seed] + [p + offset for offset in prefix_offsets]
    prefix_delta_vector = [
        prefix_offsets[i] - (seed_offset if i == 0 else prefix_offsets[i - 1])
        for i in range(index)
    ]
    prefix_mod30_vector = [value % 30 for value in prefix_nodes]
    prefix_closure_vector: list[str] = []
    previous_offset = seed_offset
    for offset in prefix_offsets:
        prefix_closure_vector.extend(
            closure_vector_between(p, previous_offset, offset, visible_divisor_bound)
        )
        previous_offset = offset

    recursive_offsets = recursive_offsets_from_node(
        p,
        node,
        candidate_bound,
        recursive_depth,
        visible_divisor_bound,
    )
    recursive_nodes = [node] + [p + offset for offset in recursive_offsets]
    recursive_delta_vector = [
        recursive_offsets[i] - (node_offset if i == 0 else recursive_offsets[i - 1])
        for i in range(len(recursive_offsets))
    ]
    recursive_mod30_vector = [value % 30 for value in recursive_nodes]
    recursive_closure_vector: list[str] = []
    previous_offset = node_offset
    for offset in recursive_offsets:
        recursive_closure_vector.extend(
            closure_vector_between(p, previous_offset, offset, visible_divisor_bound)
        )
        previous_offset = offset

    prefix_span = max(1, node_offset - seed_offset)
    recursive_span = (
        0 if not recursive_offsets else recursive_offsets[-1] - node_offset
    )
    prefix_open_density = density(len(prefix_offsets), prefix_span)
    recursive_open_density = density(len(recursive_offsets), recursive_span)
    prefix_reason_set = set(prefix_closure_vector)
    recursive_reason_set = set(recursive_closure_vector)
    prefix_sum = sum(prefix_delta_vector)
    recursive_sum = sum(recursive_delta_vector)
    repeats = not breaks_prefix_signature(
        prefix_delta_vector,
        prefix_mod30_vector,
        recursive_delta_vector,
        recursive_mod30_vector,
    )
    return {
        "scale": int(record["scale"]),
        "anchor_p": p,
        "seed_s0": seed,
        "true_q_for_audit_only": true_q,
        "chain_index": index,
        "node": node,
        "is_terminal_for_audit_only": node == true_q,
        "prefix_positions": prefix_positions,
        "prefix_delta_vector": prefix_delta_vector,
        "prefix_delta_multiset": multiset(prefix_delta_vector),
        "prefix_mod30_vector": prefix_mod30_vector,
        "prefix_closure_reason_vector": prefix_closure_vector,
        "prefix_hidden_obstruction_proxy_vector": hidden_proxy_vector(len(prefix_offsets)),
        "recursive_delta_vector": recursive_delta_vector,
        "recursive_delta_multiset": multiset(recursive_delta_vector),
        "recursive_mod30_vector": recursive_mod30_vector,
        "recursive_closure_reason_vector": recursive_closure_vector,
        "recursive_hidden_obstruction_proxy_vector": hidden_proxy_vector(
            len(recursive_offsets)
        ),
        "prefix_to_recursive_delta_ratio": (
            None if prefix_sum == 0 else recursive_sum / prefix_sum
        ),
        "prefix_to_recursive_open_density_change": (
            recursive_open_density - prefix_open_density
        ),
        "prefix_to_recursive_closure_reason_change": len(
            prefix_reason_set.symmetric_difference(recursive_reason_set)
        ),
        "recursive_chain_repeats_prefix_signature": repeats,
        "recursive_chain_breaks_prefix_signature": not repeats,
        "ranker_b_rank": ranks["ranker_b"].get(node_offset),
        "ranker_c_rank": ranks["ranker_c"].get(node_offset),
    }


def recursive_rows_for_record(
    record: dict[str, object],
    candidate_bound: int,
    chain_limit: int,
    recursive_depth: int,
    visible_divisor_bound: int,
) -> list[dict[str, object]]:
    """Return recursive state rows for one chain_fallback record."""
    p = int(record["p"])
    seed = int(record["chain_seed"])
    chain_offsets = chain_offsets_from_seed(
        p,
        seed,
        candidate_bound,
        chain_limit,
        visible_divisor_bound,
    )
    ranks = rank_maps(
        p,
        seed - p,
        candidate_bound,
        visible_divisor_bound,
    )
    return [
        row_for_node(
            record,
            chain_offsets,
            index,
            candidate_bound,
            recursive_depth,
            visible_divisor_bound,
            ranks,
        )
        for index in range(1, len(chain_offsets) + 1)
    ]


def compatible_with_prefix_multiset(row: dict[str, object]) -> bool:
    """Return True when recursive deltas are contained in the prefix multiset."""
    prefix = Counter(
        {
            int(key): int(value)
            for key, value in dict(row["prefix_delta_multiset"]).items()
        }
    )
    recursive = Counter(
        {
            int(key): int(value)
            for key, value in dict(row["recursive_delta_multiset"]).items()
        }
    )
    return all(prefix[key] >= value for key, value in recursive.items())


def hidden_proxy_lost(row: dict[str, object]) -> bool:
    """Return True when recursive continuation has fewer open-obstruction nodes."""
    return len(row["recursive_hidden_obstruction_proxy_vector"]) < len(
        row["prefix_hidden_obstruction_proxy_vector"]
    )


def no_recursive_hidden_successor(row: dict[str, object]) -> bool:
    """Return True when the recursive chain stops immediately."""
    return len(row["recursive_hidden_obstruction_proxy_vector"]) == 0


def rule_matches(rule_id: str, row: dict[str, object]) -> bool:
    """Return True when a node satisfies one recursive stop rule."""
    if rule_id == "rule_r1_first_recursive_signature_break":
        return bool(row["recursive_chain_breaks_prefix_signature"])
    if rule_id == "rule_r2_first_delta_multiset_incompatible":
        return not compatible_with_prefix_multiset(row)
    if rule_id == "rule_r3_first_recursive_open_density_drop":
        return float(row["prefix_to_recursive_open_density_change"]) < 0.0
    if rule_id == "rule_r4_first_hidden_proxy_loss":
        return hidden_proxy_lost(row)
    if rule_id == "rule_r5_first_no_recursive_hidden_successor":
        return no_recursive_hidden_successor(row)
    if rule_id == "rule_r6_best_ranker_b_after_any_break":
        return any(
            rule_matches(candidate, row)
            for candidate in RULE_IDS[:5]
        )
    raise ValueError(f"unknown rule: {rule_id}")


def select_row(rule_id: str, rows: list[dict[str, object]]) -> dict[str, object] | None:
    """Select one node by one recursive stop rule."""
    candidates = [row for row in rows if rule_matches(rule_id, row)]
    if not candidates:
        return None
    if rule_id == "rule_r6_best_ranker_b_after_any_break":
        return min(
            candidates,
            key=lambda row: (row["ranker_b_rank"] or 10_000, row["chain_index"]),
        )
    return candidates[0]


def rate(count: int, total: int) -> float:
    """Return count / total."""
    return 0.0 if int(total) == 0 else int(count) / int(total)


def summarize(
    rows: list[dict[str, object]],
    probe_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    """Return recursive rule summary rows."""
    grouped: dict[tuple[int, int], list[dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault((int(row["scale"]), int(row["anchor_p"])), []).append(row)
    base_by_scale: dict[int, dict[str, int]] = {}
    for row in probe_rows:
        scale = int(row["scale"])
        base = base_by_scale.setdefault(
            scale,
            {"emitted": 0, "pgs": 0, "chain": 0},
        )
        if row["q"] is not None:
            base["emitted"] += 1
        if row["source"] == PGS_SOURCE:
            base["pgs"] += 1
        if row["source"] == CHAIN_FALLBACK_SOURCE:
            base["chain"] += 1

    summaries: list[dict[str, object]] = []
    for scale in sorted(base_by_scale):
        chains = [
            chain for key, chain in grouped.items() if key[0] == scale
        ]
        base = base_by_scale[scale]
        for rule_id in RULE_IDS:
            selected = [select_row(rule_id, chain) for chain in chains]
            selected = [row for row in selected if row is not None]
            correct = sum(1 for row in selected if bool(row["is_terminal_for_audit_only"]))
            failures = len(selected) - correct
            projected_pgs = base["pgs"] + correct
            summaries.append(
                {
                    "scale": scale,
                    "rule_id": rule_id,
                    "chain_rows": len(chains),
                    "selected_count": len(selected),
                    "top1_correct": correct,
                    "top1_recall": rate(correct, len(chains)),
                    "would_convert_chain_fallback_to_pgs": correct,
                    "would_create_audit_failures": failures,
                    "projected_pgs_rate": rate(projected_pgs, base["emitted"]),
                    "projected_pgs_percent": rate(projected_pgs, base["emitted"]) * 100.0,
                    "zero_failure_conversions": correct if failures == 0 else 0,
                }
            )
    return summaries


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
    """Build the recursive chain-state miner CLI."""
    parser = argparse.ArgumentParser(
        description="Mine recursive shadow-chain terminal state."
    )
    parser.add_argument("--anchors", type=int, nargs="+", required=True)
    parser.add_argument("--sample-size", type=int, required=True)
    parser.add_argument("--candidate-bound", type=int, default=128)
    parser.add_argument("--chain-limit", type=int, default=DEFAULT_CHAIN_LIMIT)
    parser.add_argument("--recursive-depth", type=int, default=4)
    parser.add_argument(
        "--visible-divisor-bound",
        type=int,
        default=DEFAULT_VISIBLE_DIVISOR_BOUND,
    )
    parser.add_argument(
        "--probe-rows",
        type=Path,
        default=Path("output/simple_pgs_high_scale_chain_probe/rows.jsonl"),
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run recursive shadow-chain state mining."""
    args = build_parser().parse_args(argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    scale_set = {int(scale) for scale in args.anchors}
    probe_rows = [
        row
        for row in read_jsonl(args.probe_rows)
        if int(row["scale"]) in scale_set
    ]
    limited_probe_rows: list[dict[str, object]] = []
    for scale in args.anchors:
        scale_rows = [row for row in probe_rows if int(row["scale"]) == int(scale)]
        limited_probe_rows.extend(scale_rows[: int(args.sample_size)])
    probe_rows = limited_probe_rows
    chain_rows = [row for row in probe_rows if row["source"] == CHAIN_FALLBACK_SOURCE]
    recursive_rows: list[dict[str, object]] = []
    for record in chain_rows:
        recursive_rows.extend(
            recursive_rows_for_record(
                record,
                args.candidate_bound,
                args.chain_limit,
                args.recursive_depth,
                args.visible_divisor_bound,
            )
        )
    summaries = summarize(recursive_rows, probe_rows)
    write_jsonl(recursive_rows, args.output_dir / "recursive_rows.jsonl")
    write_csv(summaries, args.output_dir / "summary.csv")
    write_json({"summary": summaries}, args.output_dir / "summary.json")
    for row in summaries:
        print(
            "scale={scale} rule={rule_id} selected={selected_count} "
            "top1={top1_recall:.4f} failures={would_create_audit_failures} "
            "projected_pgs={projected_pgs_percent:.2f}%".format(**row)
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
