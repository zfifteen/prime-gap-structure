"""Probe a carrier-transition threat gate for shadow-seed boundary margins.

This probe tests a single deterministic hypothesis:

- Define a post-seed "carrier threat" as the first wheel-open value whose
  PGS-visible closure reason is a small divisor witness (<= threat_witness_bound).
- Select the last anchor-visible-open candidate strictly before that threat.

The intent is to test whether a visible carrier-transition event can separate
true right boundaries from visible-open impostors without changing emitted
records or relying on audit labels inside a selector.
"""

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

from z_band_prime_predictor.simple_pgs_controller import write_json  # noqa: E402
from z_band_prime_predictor.simple_pgs_generator import (  # noqa: E402
    DEFAULT_CANDIDATE_BOUND,
    DEFAULT_VISIBLE_DIVISOR_BOUND,
    PGS_SOURCE,
    SHADOW_SEED_RECOVERY_SOURCE,
    WHEEL_OPEN_RESIDUES_MOD30,
    closure_reason,
)


DEFAULT_INPUT_ROWS = (
    ROOT / "output" / "simple_pgs_shadow_seed_gwr_solution_probe" / "rows.jsonl"
)
DEFAULT_OUTPUT_DIR = (
    ROOT / "output" / "simple_pgs_solution_11_carrier_threat_margin_probe"
)
DEFAULT_THREAT_WITNESS_BOUND = 97

RULE_ID = "T1_last_visible_open_before_low_witness_threat"


def read_jsonl(path: Path) -> list[dict[str, object]]:
    """Read JSONL rows."""
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


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


def parse_divisor_witness(reason: str) -> int | None:
    """Return a parsed divisor witness from a closure_reason string."""
    if not reason.startswith("divisor_witness:"):
        return None
    _, raw = reason.split(":", 1)
    return int(raw)


def is_wheel_open(n: int) -> bool:
    """Return whether n is open on the mod-30 wheel."""
    return int(n) % 30 in WHEEL_OPEN_RESIDUES_MOD30


def is_anchor_visible_open(p: int, n: int, visible_divisor_bound: int) -> bool:
    """Return whether n is anchor-visible open."""
    if not is_wheel_open(int(n)):
        return False
    offset = int(n) - int(p)
    return closure_reason(int(p), int(offset), int(visible_divisor_bound)) is None


def visible_open_nodes_after_seed(
    p: int,
    seed_q0: int,
    candidate_bound: int,
    visible_divisor_bound: int,
) -> list[int]:
    """Return anchor-visible open candidates strictly after seed_q0."""
    upper = int(p) + int(candidate_bound)
    return [
        candidate
        for candidate in range(int(seed_q0) + 1, upper + 1)
        if is_anchor_visible_open(int(p), int(candidate), int(visible_divisor_bound))
    ]


def first_post_seed_threat(
    p: int,
    seed_q0: int,
    candidate_bound: int,
    visible_divisor_bound: int,
    threat_witness_bound: int,
) -> tuple[int | None, int | None]:
    """Return the first post-seed low-witness threat (n, witness)."""
    upper = int(p) + int(candidate_bound)
    for candidate in range(int(seed_q0) + 1, upper + 1):
        if not is_wheel_open(int(candidate)):
            continue
        offset = int(candidate) - int(p)
        reason = closure_reason(int(p), int(offset), int(visible_divisor_bound))
        if not reason:
            continue
        witness = parse_divisor_witness(str(reason))
        if witness is None:
            continue
        if int(witness) <= int(threat_witness_bound):
            return int(candidate), int(witness)
    return None, None


def pick_last_visible_open_before_threat(
    visible_open: list[int],
    threat_n: int | None,
) -> int | None:
    """Return last visible-open candidate strictly before threat_n."""
    if threat_n is None:
        return None
    before = [candidate for candidate in visible_open if int(candidate) < int(threat_n)]
    return int(before[-1]) if before else None


def failure_mode(pick: int | None, recovered_q: int) -> str:
    """Return selection failure mode."""
    if pick is None:
        return "no_selection"
    if int(pick) == int(recovered_q):
        return "correct"
    if int(pick) < int(recovered_q):
        return "selected_too_early"
    return "selected_too_late"


def run_probe(
    input_rows: Path,
    output_dir: Path,
    scales: list[int],
    candidate_bound: int,
    visible_divisor_bound: int,
    threat_witness_bound: int,
) -> dict[str, object]:
    """Run the carrier-threat probe."""
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = read_jsonl(input_rows)
    surface = [
        row
        for row in rows
        if int(row["scale"]) in scales
        and row["source"] in {PGS_SOURCE, SHADOW_SEED_RECOVERY_SOURCE}
    ]

    base_pgs_by_scale = {
        scale: sum(
            1
            for row in surface
            if int(row["scale"]) == scale and row["source"] == PGS_SOURCE
        )
        for scale in scales
    }
    emitted_by_scale = {
        scale: sum(
            1
            for row in surface
            if int(row["scale"]) == scale and row.get("q") is not None
        )
        for scale in scales
    }
    shadow_count_by_scale = {
        scale: sum(
            1
            for row in surface
            if int(row["scale"]) == scale
            and row["source"] == SHADOW_SEED_RECOVERY_SOURCE
        )
        for scale in scales
    }

    event_rows: list[dict[str, object]] = []
    rule_rows: list[dict[str, object]] = []
    for scale in scales:
        modes: Counter[str] = Counter()
        selected = 0
        correct = 0
        threat_found = 0
        for row in surface:
            if int(row["scale"]) != scale or row["source"] != SHADOW_SEED_RECOVERY_SOURCE:
                continue
            p = int(row["p"])
            seed_q0 = int(row["chain_seed"])
            recovered_q = int(row["q"])

            visible_open = visible_open_nodes_after_seed(
                p,
                seed_q0,
                int(candidate_bound),
                int(visible_divisor_bound),
            )
            visible_index = {n: i + 1 for i, n in enumerate(visible_open)}
            threat_n, threat_witness = first_post_seed_threat(
                p,
                seed_q0,
                int(candidate_bound),
                int(visible_divisor_bound),
                int(threat_witness_bound),
            )
            if threat_n is not None:
                threat_found += 1
            pick = pick_last_visible_open_before_threat(visible_open, threat_n)
            mode = failure_mode(pick, recovered_q)
            modes[mode] += 1
            if pick is not None:
                selected += 1
            if mode == "correct":
                correct += 1

            event_rows.append(
                {
                    "scale": scale,
                    "anchor_p": p,
                    "seed_q0": seed_q0,
                    "recovered_q_for_audit_only": recovered_q,
                    "true_margin_q_minus_q0": recovered_q - seed_q0,
                    "visible_open_count_after_seed": len(visible_open),
                    "true_visible_open_ordinal_of_q": visible_index.get(recovered_q, 0),
                    "threat_witness_bound": int(threat_witness_bound),
                    "threat_n": "" if threat_n is None else int(threat_n),
                    "threat_witness": "" if threat_witness is None else int(threat_witness),
                    "threat_delta_from_seed": "" if threat_n is None else int(threat_n) - seed_q0,
                    "selected_candidate_n": "" if pick is None else int(pick),
                    "predicted_margin_qhat_minus_q0": "" if pick is None else int(pick) - seed_q0,
                    "predicted_visible_open_ordinal": "" if pick is None else visible_index.get(int(pick), 0),
                    "margin_error_qhat_minus_q": "" if pick is None else int(pick) - recovered_q,
                    "failure_mode": mode,
                }
            )

        failures = selected - correct
        emitted = emitted_by_scale[scale]
        projected = 0.0 if emitted == 0 else (base_pgs_by_scale[scale] + correct) / emitted * 100.0
        rule_rows.append(
            {
                "scale": scale,
                "rule_id": RULE_ID,
                "shadow_seed_rows": shadow_count_by_scale[scale],
                "threat_found_rows": threat_found,
                "top1_selected": selected,
                "top1_correct": correct,
                "top1_recall": 0.0 if shadow_count_by_scale[scale] == 0 else correct / shadow_count_by_scale[scale],
                "would_convert_shadow_recovery_to_pgs": correct,
                "would_create_audit_failures": failures,
                "projected_pgs_percent": projected,
                "promotion_eligible": failures == 0 and projected >= 50.0,
                "failure_mode_selected_too_early": modes["selected_too_early"],
                "failure_mode_selected_too_late": modes["selected_too_late"],
                "failure_mode_no_selection": modes["no_selection"],
            }
        )

    eligible = all(
        bool(row["promotion_eligible"])
        for row in rule_rows
    )
    for row in rule_rows:
        row["promotion_eligible"] = eligible

    summary = {
        "input_rows": str(input_rows),
        "scales": scales,
        "candidate_bound": int(candidate_bound),
        "visible_divisor_bound": int(visible_divisor_bound),
        "threat_witness_bound": int(threat_witness_bound),
        "event_row_count": len(event_rows),
        "rule_rows": rule_rows,
        "promotion_eligible_rules": [RULE_ID] if eligible else [],
        "strongest_result": (
            "carrier_threat_gate_does_not_promote"
            if not eligible
            else "carrier_threat_gate_promotes"
        ),
    }
    write_csv(event_rows, output_dir / "carrier_threat_event_rows.csv")
    write_csv(rule_rows, output_dir / "carrier_threat_rule_report.csv")
    write_json(summary, output_dir / "summary.json")
    return summary


def build_parser() -> argparse.ArgumentParser:
    """Build CLI parser."""
    parser = argparse.ArgumentParser(
        description="Probe a low-witness carrier-threat gate for shadow-seed recovery."
    )
    parser.add_argument("--input-rows", type=Path, default=DEFAULT_INPUT_ROWS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--scales", type=int, nargs="+", default=[10**12, 10**15, 10**18])
    parser.add_argument("--candidate-bound", type=int, default=DEFAULT_CANDIDATE_BOUND)
    parser.add_argument(
        "--visible-divisor-bound",
        type=int,
        default=DEFAULT_VISIBLE_DIVISOR_BOUND,
    )
    parser.add_argument(
        "--threat-witness-bound",
        type=int,
        default=DEFAULT_THREAT_WITNESS_BOUND,
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run CLI."""
    args = build_parser().parse_args(argv)
    summary = run_probe(
        args.input_rows,
        args.output_dir,
        [int(scale) for scale in args.scales],
        int(args.candidate_bound),
        int(args.visible_divisor_bound),
        int(args.threat_witness_bound),
    )
    eligible = bool(summary["promotion_eligible_rules"])
    print(
        "event_rows={event_row_count} promotion_eligible={eligible} strongest_result={result}".format(
            event_row_count=summary["event_row_count"],
            eligible="yes" if eligible else "no",
            result=summary["strongest_result"],
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
