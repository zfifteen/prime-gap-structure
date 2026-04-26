"""Probe Claude's shadow-seed boundary recovery law."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from math import isqrt
from pathlib import Path

from sympy import factorint


DEFAULT_ROWS_PATH = Path("output/simple_pgs_shadow_seed_gwr_solution_probe/rows.jsonl")
DEFAULT_CANDIDATES_PATH = Path(
    "output/simple_pgs_shadow_seed_recovery_displacement_probe/candidate_rows.csv"
)
DEFAULT_OUTPUT_DIR = Path("output/simple_pgs_solution_05_ssbrl_probe")
DEFAULT_CANDIDATE_BOUND = 128
DEFAULT_VISIBLE_DIVISOR_BOUND = 10_000
WHEEL_OPEN_RESIDUES_MOD30 = {1, 7, 11, 13, 17, 19, 23, 29}


def percent(numerator: int, denominator: int) -> float:
    return 0.0 if int(denominator) == 0 else 100.0 * int(numerator) / int(denominator)


def small_primes(limit: int) -> list[int]:
    if limit < 2:
        return []
    sieve = bytearray(b"\x01") * (limit + 1)
    sieve[0:2] = b"\x00\x00"
    for n in range(2, isqrt(limit) + 1):
        if sieve[n]:
            start = n * n
            sieve[start : limit + 1 : n] = b"\x00" * (((limit - start) // n) + 1)
    return [n for n in range(2, limit + 1) if sieve[n]]


def load_source_rows(path: Path) -> list[dict[str, object]]:
    with path.open() as handle:
        return [json.loads(line) for line in handle]


def shadow_rows(source_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "scale": int(row["scale"]),
            "p": int(row["p"]),
            "q": int(row["q"]),
            "seed": int(row["chain_seed"]),
        }
        for row in source_rows
        if row.get("source") == "shadow_seed_recovery"
    ]


def load_materialized_witnesses(path: Path) -> dict[tuple[int, int, int], set[int]]:
    groups: dict[tuple[int, int, int], set[int]] = defaultdict(set)
    with path.open(newline="") as handle:
        for row in csv.DictReader(handle):
            key = (int(row["scale"]), int(row["anchor_p"]), int(row["seed_q0"]))
            witness = row["visible_divisor_witness_under_10000"]
            if witness:
                groups[key].add(int(witness))
    return dict(groups)


def least_factor_for_audit_only(n: int) -> int:
    factors = factorint(int(n))
    return min(int(factor) for factor in factors)


def open_under_walls(candidate: int, walls: list[int] | set[int]) -> bool:
    return all(int(candidate) % int(wall) != 0 for wall in walls)


def residue_advance(
    seed: int,
    upper: int,
    walls: list[int] | set[int],
    require_wheel_open: bool,
) -> tuple[int | None, int]:
    checked = 0
    for candidate in range(int(seed) + 1, int(upper) + 1):
        checked += 1
        if require_wheel_open and candidate % 30 not in WHEEL_OPEN_RESIDUES_MOD30:
            continue
        if open_under_walls(candidate, walls):
            return candidate, checked
    return None, checked


def least_factor_progression(
    seed: int,
    upper: int,
    least_factor: int,
    walls: list[int] | set[int],
    require_wheel_open: bool,
) -> tuple[int | None, int]:
    checked = 0
    candidate = int(seed) + int(least_factor)
    while candidate <= int(upper):
        checked += 1
        if (
            (not require_wheel_open or candidate % 30 in WHEEL_OPEN_RESIDUES_MOD30)
            and open_under_walls(candidate, walls)
        ):
            return candidate, checked
        candidate += int(least_factor)
    return None, checked


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
    witnesses_by_key: dict[tuple[int, int, int], set[int]],
    candidate_bound: int,
    visible_divisor_bound: int,
) -> list[dict[str, object]]:
    prime_walls = small_primes(int(visible_divisor_bound))
    integer_walls = list(range(2, int(visible_divisor_bound) + 1))
    rule_ids = [
        "visible_prime_residue_advance",
        "visible_prime_residue_advance_wheel_open",
        "visible_integer_residue_advance",
        "visible_integer_residue_advance_wheel_open",
        "materialized_witness_residue_advance",
        "materialized_witness_residue_advance_wheel_open",
        "audit_q0_plus_least_factor",
        "audit_least_factor_progression_visible_prime",
        "audit_least_factor_progression_visible_prime_wheel_open",
    ]
    result_rows: list[dict[str, object]] = []
    for row in rows:
        scale = int(row["scale"])
        p = int(row["p"])
        seed = int(row["seed"])
        true_q = int(row["q"])
        upper = p + int(candidate_bound)
        key = (scale, p, seed)
        witnesses = witnesses_by_key.get(key, set())
        least_factor = least_factor_for_audit_only(seed)
        for rule_id in rule_ids:
            materialized_missing = rule_id.startswith("materialized") and key not in witnesses_by_key
            selected: int | None
            checked: int
            if materialized_missing:
                selected = None
                checked = 0
            elif rule_id == "visible_prime_residue_advance":
                selected, checked = residue_advance(seed, upper, prime_walls, False)
            elif rule_id == "visible_prime_residue_advance_wheel_open":
                selected, checked = residue_advance(seed, upper, prime_walls, True)
            elif rule_id == "visible_integer_residue_advance":
                selected, checked = residue_advance(seed, upper, integer_walls, False)
            elif rule_id == "visible_integer_residue_advance_wheel_open":
                selected, checked = residue_advance(seed, upper, integer_walls, True)
            elif rule_id == "materialized_witness_residue_advance":
                selected, checked = residue_advance(seed, upper, witnesses, False)
            elif rule_id == "materialized_witness_residue_advance_wheel_open":
                selected, checked = residue_advance(seed, upper, witnesses, True)
            elif rule_id == "audit_q0_plus_least_factor":
                candidate = seed + least_factor
                selected = candidate if candidate <= upper else None
                checked = 1
            elif rule_id == "audit_least_factor_progression_visible_prime":
                selected, checked = least_factor_progression(
                    seed,
                    upper,
                    least_factor,
                    prime_walls,
                    False,
                )
            elif rule_id == "audit_least_factor_progression_visible_prime_wheel_open":
                selected, checked = least_factor_progression(
                    seed,
                    upper,
                    least_factor,
                    prime_walls,
                    True,
                )
            else:
                raise ValueError(f"unknown rule_id: {rule_id}")
            result_rows.append(
                {
                    "scale": scale,
                    "rule_id": rule_id,
                    "anchor_p": p,
                    "seed_q0": seed,
                    "true_q_for_audit_only": true_q,
                    "upper_bound": upper,
                    "seed_least_factor_for_audit_only": least_factor,
                    "seed_to_true_delta": true_q - seed,
                    "least_factor_equals_seed_to_true_delta": least_factor == true_q - seed,
                    "selected_q": selected if selected is not None else "",
                    "selected_delta_from_true": "" if selected is None else selected - true_q,
                    "failure_mode": failure_mode(selected, true_q),
                    "positions_checked": checked,
                    "materialized_witness_count": len(witnesses),
                    "did_evaluate": not materialized_missing,
                    "failure_reason": (
                        "missing_materialized_candidate_rows"
                        if materialized_missing
                        else ""
                    ),
                    "pure_pgs_eligible_input": not rule_id.startswith("audit_"),
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

    grouped: dict[tuple[int, str], list[dict[str, object]]] = defaultdict(list)
    for row in selection_rows:
        grouped[(int(row["scale"]), str(row["rule_id"]))].append(row)

    summaries: list[dict[str, object]] = []
    for (scale, rule_id), rows in sorted(grouped.items()):
        modes = Counter(str(row["failure_mode"]) for row in rows)
        correct = modes["correct"]
        failures = modes["selected_too_early"] + modes["selected_too_late"]
        no_selection = modes["no_selection"]
        projected_pgs_percent = percent(pgs[scale] + correct, emitted[scale])
        pure_input = all(bool(row["pure_pgs_eligible_input"]) for row in rows)
        summaries.append(
            {
                "scale": scale,
                "rule_id": rule_id,
                "shadow_rows": len(rows),
                "evaluated_rows": sum(1 for row in rows if row["did_evaluate"]),
                "correct": correct,
                "selected_too_early": modes["selected_too_early"],
                "selected_too_late": modes["selected_too_late"],
                "no_selection": no_selection,
                "would_create_audit_failures": failures,
                "projected_pgs_percent": projected_pgs_percent,
                "pure_pgs_eligible_input": pure_input,
                "promotion_eligible": (
                    pure_input
                    and failures == 0
                    and no_selection == 0
                    and projected_pgs_percent >= 50.0
                ),
            }
        )
    return summaries


def materialized_rows(
    shadow: list[dict[str, object]],
    witnesses_by_key: dict[tuple[int, int, int], set[int]],
) -> list[dict[str, object]]:
    counts = Counter(int(row["scale"]) for row in shadow)
    materialized = Counter()
    for row in shadow:
        key = (int(row["scale"]), int(row["p"]), int(row["seed"]))
        if key in witnesses_by_key:
            materialized[int(row["scale"])] += 1
    return [
        {
            "scale": scale,
            "shadow_rows": counts[scale],
            "rows_with_materialized_candidate_stream": materialized[scale],
            "rows_missing_materialized_candidate_stream": counts[scale] - materialized[scale],
            "materialized_percent": percent(materialized[scale], counts[scale]),
        }
        for scale in sorted(counts)
    ]


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
    parser.add_argument("--candidate-rows", type=Path, default=DEFAULT_CANDIDATES_PATH)
    parser.add_argument("--candidate-bound", type=int, default=DEFAULT_CANDIDATE_BOUND)
    parser.add_argument("--visible-divisor-bound", type=int, default=DEFAULT_VISIBLE_DIVISOR_BOUND)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    source_rows = load_source_rows(args.rows)
    shadow = shadow_rows(source_rows)
    witnesses = load_materialized_witnesses(args.candidate_rows)
    selection_rows = evaluate(
        shadow,
        witnesses,
        args.candidate_bound,
        args.visible_divisor_bound,
    )
    summary_rows = summarize(selection_rows, source_rows)
    materialized = materialized_rows(shadow, witnesses)
    contract_rows = [
        {
            "required_object": "seed blocking witness r in chamber_state",
            "materialized_in_current_artifacts": False,
            "probe_handling": "computed with audit-only factorization for signal tests",
        },
        {
            "required_object": "sieve_primes / active wall primes",
            "materialized_in_current_artifacts": False,
            "probe_handling": "tested visible prime walls, visible integer walls, and materialized candidate witnesses separately",
        },
        {
            "required_object": "residue vector at q0",
            "materialized_in_current_artifacts": False,
            "probe_handling": "recomputed residue tests in probe; not promotable as current pure PGS state",
        },
    ]

    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.output_dir / "ssbrl_selection_rows.csv", selection_rows)
    write_csv(args.output_dir / "ssbrl_summary.csv", summary_rows)
    write_csv(args.output_dir / "materialized_coverage.csv", materialized)
    write_csv(args.output_dir / "materialized_contract.csv", contract_rows)

    eligible = [row for row in summary_rows if row["promotion_eligible"]]
    payload = {
        "verdict": (
            "promotion_eligible"
            if eligible
            else "rejected_no_ssbrl_rule_met_promotion_gate"
        ),
        "candidate_bound": args.candidate_bound,
        "visible_divisor_bound": args.visible_divisor_bound,
        "shadow_rows": len(shadow),
        "eligible_rule_count": len(eligible),
        "eligible_rules": eligible,
        "materialized_coverage": materialized,
        "artifacts": {
            "selection_rows": str(args.output_dir / "ssbrl_selection_rows.csv"),
            "summary": str(args.output_dir / "ssbrl_summary.csv"),
            "materialized_coverage": str(args.output_dir / "materialized_coverage.csv"),
            "materialized_contract": str(args.output_dir / "materialized_contract.csv"),
        },
    }
    (args.output_dir / "summary.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
