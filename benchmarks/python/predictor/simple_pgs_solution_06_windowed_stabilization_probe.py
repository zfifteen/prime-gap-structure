"""Probe Copilot's windowed flux/pressure stabilization proposal."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from math import ceil, isqrt, log
from pathlib import Path

from sympy import nextprime


DEFAULT_ROWS_PATH = Path("output/simple_pgs_shadow_seed_gwr_solution_probe/rows.jsonl")
DEFAULT_OUTPUT_DIR = Path("output/simple_pgs_solution_06_windowed_stabilization_probe")
DEFAULT_VISIBLE_DIVISOR_BOUND = 10_000
WHEEL_OPEN_RESIDUES_MOD30 = {1, 7, 11, 13, 17, 19, 23, 29}


def divisor_witness(n: int, max_divisor: int) -> int | None:
    limit = min(isqrt(int(n)), int(max_divisor))
    for divisor in range(2, limit + 1):
        if int(n) % divisor == 0:
            return divisor
    return None


def closure_reason(p: int, offset: int, max_divisor: int) -> str | None:
    n = int(p) + int(offset)
    residue = n % 30
    if residue not in WHEEL_OPEN_RESIDUES_MOD30:
        return f"wheel_closed_residue:{residue}"
    witness = divisor_witness(n, max_divisor)
    if witness is not None and witness not in {1, n}:
        return f"divisor_witness:{witness}"
    return None


def percent(numerator: int, denominator: int) -> float:
    return 0.0 if int(denominator) == 0 else 100.0 * int(numerator) / int(denominator)


def load_source_rows(path: Path) -> list[dict[str, object]]:
    with path.open() as handle:
        return [json.loads(line) for line in handle]


def target_rows(source_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for row in source_rows:
        if row.get("source") not in {"shadow_seed_recovery", "unresolved"}:
            continue
        p = int(row["p"])
        true_q = row.get("q")
        rows.append(
            {
                "scale": int(row["scale"]),
                "p": p,
                "seed": int(row["chain_seed"]),
                "source": row["source"],
                "true_q": int(true_q) if true_q is not None else int(nextprime(p)),
                "audit_true_q_source": "artifact" if true_q is not None else "audit_nextprime",
            }
        )
    return rows


def window_width(p: int, minimum: int) -> int:
    return max(int(minimum), int(log(int(p)) ** 2))


def chamber_series(
    p: int,
    seed: int,
    width: int,
    visible_divisor_bound: int,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    visible_open_count = 0
    closed_count = 0
    for position, n in enumerate(range(int(seed) + 1, int(seed) + int(width) + 1), start=1):
        reason = closure_reason(int(p), n - int(p), int(visible_divisor_bound))
        is_open = reason is None
        if is_open:
            visible_open_count += 1
        else:
            closed_count += 1
        rows.append(
            {
                "position": position,
                "n": n,
                "visible_open": is_open,
                "closed": not is_open,
                "closure_reason": "" if reason is None else reason,
                "flux": visible_open_count,
                "pressure": closed_count / position,
            }
        )
    return rows


def pressure_declines_after(series: list[dict[str, object]], index: int, gap: int) -> bool:
    if index + gap >= len(series):
        return False
    values = [float(series[j]["pressure"]) for j in range(index, index + gap + 1)]
    return all(values[k] > values[k + 1] for k in range(len(values) - 1))


def local_pressure_peak_before(series: list[dict[str, object]], index: int, lookback: int) -> bool:
    start = max(0, index - int(lookback))
    window = series[start : index + 1]
    if not window:
        return False
    pressure = float(series[index]["pressure"])
    return pressure == max(float(row["pressure"]) for row in window)


def flux_constant_ending_at(series: list[dict[str, object]], index: int, gap: int) -> bool:
    if index - gap + 1 < 0:
        return False
    values = [int(series[j]["flux"]) for j in range(index - gap + 1, index + 1)]
    return len(set(values)) == 1


def no_late_open(series: list[dict[str, object]], index: int, gap: int) -> bool:
    if index + gap >= len(series):
        return False
    return not any(bool(series[j]["visible_open"]) for j in range(index + 1, index + gap + 1))


def select_literal(series: list[dict[str, object]], gap: int, lookback: int) -> int | None:
    for index, row in enumerate(series):
        if not flux_constant_ending_at(series, index, gap):
            continue
        if not local_pressure_peak_before(series, index, lookback):
            continue
        if not pressure_declines_after(series, index, gap):
            continue
        if not no_late_open(series, index, gap):
            continue
        return int(row["n"])
    return None


def select_boundary_open(series: list[dict[str, object]], gap: int, lookback: int) -> int | None:
    for index, row in enumerate(series):
        if not bool(row["visible_open"]):
            continue
        if not local_pressure_peak_before(series, max(0, index - 1), lookback):
            continue
        if not pressure_declines_after(series, max(0, index - 1), gap):
            continue
        if not no_late_open(series, index, gap):
            continue
        return int(row["n"])
    return None


def select_first_visible_open(series: list[dict[str, object]]) -> int | None:
    for row in series:
        if bool(row["visible_open"]):
            return int(row["n"])
    return None


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
    minimum_window: int,
    visible_divisor_bound: int,
) -> list[dict[str, object]]:
    result_rows: list[dict[str, object]] = []
    for row in rows:
        p = int(row["p"])
        seed = int(row["seed"])
        true_q = int(row["true_q"])
        width = window_width(p, minimum_window)
        gap = ceil(width / 8)
        series = chamber_series(p, seed, width + gap + 2, visible_divisor_bound)
        selected_by_rule = {
            "literal_flux_pressure_stabilization": select_literal(series, gap, width),
            "boundary_open_pressure_stabilization": select_boundary_open(series, gap, width),
            "first_visible_open_baseline": select_first_visible_open(series),
        }
        for rule_id, selected in selected_by_rule.items():
            result_rows.append(
                {
                    "scale": int(row["scale"]),
                    "source": row["source"],
                    "rule_id": rule_id,
                    "anchor_p": p,
                    "seed_q0": seed,
                    "true_q_for_audit_only": true_q,
                    "audit_true_q_source": row["audit_true_q_source"],
                    "window_width": width,
                    "stability_gap": gap,
                    "selected_q": selected if selected is not None else "",
                    "selected_delta_from_true": "" if selected is None else selected - true_q,
                    "failure_mode": failure_mode(selected, true_q),
                    "true_inside_window": true_q <= seed + width,
                    "selected_visible_open": (
                        ""
                        if selected is None
                        else closure_reason(p, selected - p, visible_divisor_bound) is None
                    ),
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
                "true_inside_window_count": sum(1 for row in rows if row["true_inside_window"]),
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
    parser.add_argument("--minimum-window", type=int, default=128)
    parser.add_argument("--visible-divisor-bound", type=int, default=DEFAULT_VISIBLE_DIVISOR_BOUND)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    source_rows = load_source_rows(args.rows)
    targets = target_rows(source_rows)
    selection_rows = evaluate(targets, args.minimum_window, args.visible_divisor_bound)
    summary_rows = summarize(selection_rows, source_rows)
    contract_rows = [
        {
            "required_object": "per-index emitted count / confirmed count",
            "materialized_in_current_artifacts": False,
            "probe_handling": "not used because confirmed count is downstream audit state",
        },
        {
            "required_object": "per-index visible candidate flux",
            "materialized_in_current_artifacts": False,
            "probe_handling": "synthesized from closure_reason over a local window",
        },
        {
            "required_object": "per-index chamber pressure",
            "materialized_in_current_artifacts": False,
            "probe_handling": "synthesized as closed-position density over a local window",
        },
    ]

    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.output_dir / "stabilization_selection_rows.csv", selection_rows)
    write_csv(args.output_dir / "stabilization_summary.csv", summary_rows)
    write_csv(args.output_dir / "materialized_contract.csv", contract_rows)

    eligible = [row for row in summary_rows if row["promotion_eligible"]]
    payload = {
        "verdict": (
            "promotion_eligible"
            if eligible
            else "rejected_no_windowed_stabilization_rule_met_promotion_gate"
        ),
        "minimum_window": args.minimum_window,
        "visible_divisor_bound": args.visible_divisor_bound,
        "target_rows": len(targets),
        "eligible_rule_count": len(eligible),
        "eligible_rules": eligible,
        "artifacts": {
            "selection_rows": str(args.output_dir / "stabilization_selection_rows.csv"),
            "summary": str(args.output_dir / "stabilization_summary.csv"),
            "materialized_contract": str(args.output_dir / "materialized_contract.csv"),
        },
    }
    (args.output_dir / "summary.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
