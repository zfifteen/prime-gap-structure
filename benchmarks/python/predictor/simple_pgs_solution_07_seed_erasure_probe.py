"""Probe the seed-erasure boundary law."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from math import isqrt
from pathlib import Path

from sympy import nextprime


DEFAULT_ROWS_PATH = Path("output/simple_pgs_shadow_seed_gwr_solution_probe/rows.jsonl")
DEFAULT_OUTPUT_DIR = Path("output/simple_pgs_solution_07_seed_erasure_probe")
DEFAULT_CANDIDATE_BOUND = 128
DEFAULT_TRACE_WINDOW = 128
DEFAULT_VISIBLE_DIVISOR_BOUND = 10_000
WHEEL_OPEN_RESIDUES_MOD30 = {1, 7, 11, 13, 17, 19, 23, 29}


def percent(numerator: int, denominator: int) -> float:
    return 0.0 if int(denominator) == 0 else 100.0 * int(numerator) / int(denominator)


def divisor_witness(n: int, max_divisor: int) -> int | None:
    for divisor in range(2, min(isqrt(int(n)), int(max_divisor)) + 1):
        if int(n) % divisor == 0:
            return divisor
    return None


def visible_open(n: int, visible_divisor_bound: int) -> bool:
    if int(n) % 30 not in WHEEL_OPEN_RESIDUES_MOD30:
        return False
    return divisor_witness(int(n), int(visible_divisor_bound)) is None


def load_source_rows(path: Path) -> list[dict[str, object]]:
    with path.open() as handle:
        return [json.loads(line) for line in handle]


def target_rows(source_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for row in source_rows:
        if row.get("source") not in {"shadow_seed_recovery", "unresolved"}:
            continue
        p = int(row["p"])
        q = row.get("q")
        rows.append(
            {
                "scale": int(row["scale"]),
                "p": p,
                "seed": int(row["chain_seed"]),
                "source": row["source"],
                "true_q": int(q) if q is not None else int(nextprime(p)),
                "audit_true_q_source": "artifact" if q is not None else "audit_nextprime",
            }
        )
    return rows


def candidate_stream(
    p: int,
    seed: int,
    candidate_bound: int,
    visible_divisor_bound: int,
) -> list[int]:
    upper = int(p) + int(candidate_bound)
    return [
        n
        for n in range(int(seed) + 1, upper + 1)
        if visible_open(n, visible_divisor_bound)
    ]


def seed_extra_closes(
    rule_id: str,
    p: int,
    seed: int,
    candidate: int,
    n: int,
) -> bool:
    seed_offset = int(seed) - int(p)
    if rule_id == "literal_reanchor_identity":
        return False
    if rule_id == "seed_offset_phase_wall":
        return seed_offset > 0 and (int(n) - int(p)) % seed_offset == 0
    if rule_id == "candidate_margin_phase_wall":
        margin = int(candidate) - int(seed)
        return margin > 0 and (int(n) - int(seed)) % margin == 0
    raise ValueError(f"unknown rule_id: {rule_id}")


def seed_erasure_defect(
    rule_id: str,
    p: int,
    seed: int,
    candidate: int,
    trace_window: int,
    visible_divisor_bound: int,
) -> int:
    defect = 0
    for n in range(int(candidate) + 1, int(candidate) + int(trace_window) + 1):
        if not visible_open(n, visible_divisor_bound):
            continue
        if seed_extra_closes(rule_id, p, seed, candidate, n):
            defect += 1
    return defect


def select_candidate(
    rule_id: str,
    p: int,
    seed: int,
    candidate_bound: int,
    trace_window: int,
    visible_divisor_bound: int,
) -> tuple[int | None, int | None, int]:
    candidates = candidate_stream(p, seed, candidate_bound, visible_divisor_bound)
    best_candidate: int | None = None
    best_defect: int | None = None
    for candidate in candidates:
        defect = seed_erasure_defect(
            rule_id,
            p,
            seed,
            candidate,
            trace_window,
            visible_divisor_bound,
        )
        if best_defect is None or defect < best_defect:
            best_defect = defect
            best_candidate = candidate
        if defect == 0:
            return candidate, defect, len(candidates)
    return best_candidate, best_defect, len(candidates)


def failure_mode(selected: int | None, true_q: int) -> str:
    if selected is None:
        return "no_selection"
    if int(selected) == int(true_q):
        return "correct"
    if int(selected) < int(true_q):
        return "selected_too_early"
    return "selected_too_late"


def evaluate(
    rows: list[dict[str, object]],
    candidate_bound: int,
    trace_window: int,
    visible_divisor_bound: int,
) -> list[dict[str, object]]:
    rule_ids = [
        "literal_reanchor_identity",
        "seed_offset_phase_wall",
        "candidate_margin_phase_wall",
    ]
    result_rows: list[dict[str, object]] = []
    for row in rows:
        p = int(row["p"])
        seed = int(row["seed"])
        true_q = int(row["true_q"])
        for rule_id in rule_ids:
            selected, defect, visible_count = select_candidate(
                rule_id,
                p,
                seed,
                candidate_bound,
                trace_window,
                visible_divisor_bound,
            )
            true_defect = (
                seed_erasure_defect(
                    rule_id,
                    p,
                    seed,
                    true_q,
                    trace_window,
                    visible_divisor_bound,
                )
                if visible_open(true_q, visible_divisor_bound)
                else ""
            )
            result_rows.append(
                {
                    "scale": int(row["scale"]),
                    "source": row["source"],
                    "rule_id": rule_id,
                    "anchor_p": p,
                    "seed_q0": seed,
                    "true_q_for_audit_only": true_q,
                    "audit_true_q_source": row["audit_true_q_source"],
                    "candidate_bound": int(candidate_bound),
                    "trace_window": int(trace_window),
                    "visible_candidate_count": visible_count,
                    "selected_q": selected if selected is not None else "",
                    "selected_defect": defect if defect is not None else "",
                    "true_q_defect": true_defect,
                    "selected_delta_from_true": "" if selected is None else selected - true_q,
                    "failure_mode": failure_mode(selected, true_q),
                    "pure_pgs_eligible_input": row["source"] == "shadow_seed_recovery",
                }
            )
    return result_rows


def summarize(
    selection_rows: list[dict[str, object]],
    source_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    emitted_sources = {"PGS", "shadow_seed_recovery", "chain_horizon_closure", "chain_fallback", "fallback"}
    emitted = Counter()
    pgs = Counter()
    for row in source_rows:
        scale = int(row["scale"])
        if row.get("source") in emitted_sources:
            emitted[scale] += 1
        if row.get("source") == "PGS":
            pgs[scale] += 1

    grouped: dict[tuple[int, str, str], list[dict[str, object]]] = defaultdict(list)
    for row in selection_rows:
        grouped[(int(row["scale"]), str(row["source"]), str(row["rule_id"]))].append(row)

    summaries: list[dict[str, object]] = []
    for (scale, source, rule_id), rows in sorted(grouped.items()):
        modes = Counter(str(row["failure_mode"]) for row in rows)
        correct = modes["correct"]
        failures = modes["selected_too_early"] + modes["selected_too_late"]
        no_selection = modes["no_selection"]
        projected_pgs_percent = percent(pgs[scale] + correct, emitted[scale])
        pure_input = all(bool(row["pure_pgs_eligible_input"]) for row in rows)
        zero_defect_true = sum(1 for row in rows if row["true_q_defect"] == 0)
        zero_defect_selected = sum(1 for row in rows if row["selected_defect"] == 0)
        summaries.append(
            {
                "scale": scale,
                "source": source,
                "rule_id": rule_id,
                "rows": len(rows),
                "correct": correct,
                "selected_too_early": modes["selected_too_early"],
                "selected_too_late": modes["selected_too_late"],
                "no_selection": no_selection,
                "would_create_audit_failures": failures,
                "projected_pgs_percent": projected_pgs_percent,
                "precision_percent": percent(correct, correct + failures),
                "false_positive_percent": percent(failures, len(rows)),
                "true_q_zero_defect_count": zero_defect_true,
                "selected_zero_defect_count": zero_defect_selected,
                "pure_pgs_eligible_input": pure_input,
                "promotion_eligible": (
                    source == "shadow_seed_recovery"
                    and pure_input
                    and failures == 0
                    and no_selection == 0
                    and projected_pgs_percent >= 50.0
                ),
            }
        )
    return summaries


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        path.write_text("", newline="\n")
        return
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=Path, default=DEFAULT_ROWS_PATH)
    parser.add_argument("--candidate-bound", type=int, default=DEFAULT_CANDIDATE_BOUND)
    parser.add_argument("--trace-window", type=int, default=DEFAULT_TRACE_WINDOW)
    parser.add_argument("--visible-divisor-bound", type=int, default=DEFAULT_VISIBLE_DIVISOR_BOUND)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    source_rows = load_source_rows(args.rows)
    targets = target_rows(source_rows)
    selection_rows = evaluate(
        targets,
        args.candidate_bound,
        args.trace_window,
        args.visible_divisor_bound,
    )
    summary_rows = summarize(selection_rows, source_rows)
    contract_rows = [
        {
            "required_object": "literal seed-erasure trace in current chamber state",
            "materialized_in_current_artifacts": False,
            "probe_handling": "tested identity baseline; it collapses to first visible-open",
        },
        {
            "required_object": "placed-seed influence",
            "materialized_in_current_artifacts": False,
            "probe_handling": "tested two explicit seed-phase integrations",
        },
    ]

    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.output_dir / "seed_erasure_selection_rows.csv", selection_rows)
    write_csv(args.output_dir / "seed_erasure_summary.csv", summary_rows)
    write_csv(args.output_dir / "materialized_contract.csv", contract_rows)

    eligible = [row for row in summary_rows if row["promotion_eligible"]]
    payload = {
        "verdict": (
            "promotion_eligible"
            if eligible
            else "rejected_no_seed_erasure_rule_met_promotion_gate"
        ),
        "candidate_bound": args.candidate_bound,
        "trace_window": args.trace_window,
        "visible_divisor_bound": args.visible_divisor_bound,
        "target_rows": len(targets),
        "eligible_rule_count": len(eligible),
        "eligible_rules": eligible,
        "artifacts": {
            "selection_rows": str(args.output_dir / "seed_erasure_selection_rows.csv"),
            "summary": str(args.output_dir / "seed_erasure_summary.csv"),
            "materialized_contract": str(args.output_dir / "materialized_contract.csv"),
        },
    }
    (args.output_dir / "summary.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
