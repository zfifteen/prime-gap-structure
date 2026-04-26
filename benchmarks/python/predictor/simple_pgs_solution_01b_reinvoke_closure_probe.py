"""Test Grok Solution 1b: re-invoke chamber closure from the shadow seed."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = ROOT / "src" / "python"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from z_band_prime_predictor.simple_pgs_generator import (  # noqa: E402
    DEFAULT_CANDIDATE_BOUND,
    DEFAULT_VISIBLE_DIVISOR_BOUND,
    PGS_SOURCE,
    admissible_offsets,
    closure_reason,
    pgs_probe_certificate,
)


DEFAULT_INPUT = (
    ROOT / "output" / "simple_pgs_shadow_seed_gwr_solution_probe" / "rows.jsonl"
)
DEFAULT_OUTPUT_DIR = ROOT / "output" / "simple_pgs_solution_01b_reinvoke_closure_probe"


def read_jsonl(path: Path) -> list[dict[str, object]]:
    """Read JSONL rows."""
    rows: list[dict[str, object]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                rows.append(json.loads(stripped))
    return rows


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


def write_json(record: dict[str, object], path: Path) -> None:
    """Write LF-terminated JSON."""
    path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")


def reanchor_closure_pick(
    seed_q0: int,
    candidate_bound: int,
    visible_divisor_bound: int,
) -> int | None:
    """Return chamber closure q when the shadow seed is used as the anchor."""
    certificate = pgs_probe_certificate(
        int(seed_q0),
        int(candidate_bound),
        int(visible_divisor_bound),
    )
    if certificate is None:
        return None
    return int(certificate["q"])


def start_offset_closure_pick(
    p: int,
    seed_q0: int,
    candidate_bound: int,
    visible_divisor_bound: int,
) -> int | None:
    """Return chamber closure q after the seed while keeping the original anchor."""
    seed_offset = int(seed_q0) - int(p)
    offsets = admissible_offsets(int(p), int(candidate_bound))
    for gap_offset in offsets:
        if gap_offset <= seed_offset:
            continue
        if closure_reason(int(p), gap_offset, int(visible_divisor_bound)) is not None:
            continue
        unclosed_before = False
        for previous_offset in offsets:
            if previous_offset <= seed_offset:
                continue
            if previous_offset >= gap_offset:
                break
            if (
                closure_reason(
                    int(p),
                    previous_offset,
                    int(visible_divisor_bound),
                )
                is None
            ):
                unclosed_before = True
                break
        if not unclosed_before:
            return int(p) + gap_offset
    return None


def rate(count: int, total: int) -> float:
    """Return count / total."""
    return 0.0 if int(total) == 0 else int(count) / int(total)


def failure_mode(pick: int | None, true_q: int) -> str:
    """Classify one selected q."""
    if pick is None:
        return "no_selection"
    if int(pick) == int(true_q):
        return "correct"
    if int(pick) < int(true_q):
        return "selected_too_early"
    return "selected_too_late"


def build_probe_rows(
    rows: list[dict[str, object]],
    candidate_bound: int,
    visible_divisor_bound: int,
) -> list[dict[str, object]]:
    """Build one result row per shadow-seed recovery row."""
    out: list[dict[str, object]] = []
    for row in rows:
        if row.get("source") != "shadow_seed_recovery":
            continue
        scale = int(row["scale"])
        p = int(row["p"])
        seed_q0 = int(row["chain_seed"])
        true_q = int(row["q"])
        picks = {
            "reanchor_at_seed": reanchor_closure_pick(
                seed_q0,
                candidate_bound,
                visible_divisor_bound,
            ),
            "same_anchor_start_after_seed": start_offset_closure_pick(
                p,
                seed_q0,
                candidate_bound,
                visible_divisor_bound,
            ),
        }
        for interpretation, pick in picks.items():
            out.append(
                {
                    "scale": scale,
                    "interpretation": interpretation,
                    "anchor_p": p,
                    "seed_q0": seed_q0,
                    "true_q_for_audit_only": true_q,
                    "selected_q": "" if pick is None else pick,
                    "selected_delta_from_true": ""
                    if pick is None
                    else int(pick) - true_q,
                    "failure_mode": failure_mode(pick, true_q),
                    "candidate_bound": int(candidate_bound),
                    "visible_divisor_bound": int(visible_divisor_bound),
                }
            )
    return out


def summarize(
    source_rows: list[dict[str, object]],
    probe_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    """Summarize projected effect of each interpretation."""
    emitted_by_scale: dict[int, int] = {}
    base_pgs_by_scale: dict[int, int] = {}
    for row in source_rows:
        scale = int(row["scale"])
        if row.get("q") is not None:
            emitted_by_scale[scale] = emitted_by_scale.get(scale, 0) + 1
        if row.get("source") == PGS_SOURCE:
            base_pgs_by_scale[scale] = base_pgs_by_scale.get(scale, 0) + 1

    groups: dict[tuple[int, str], list[dict[str, object]]] = {}
    for row in probe_rows:
        key = (int(row["scale"]), str(row["interpretation"]))
        groups.setdefault(key, []).append(row)

    out: list[dict[str, object]] = []
    for (scale, interpretation), rows in sorted(groups.items()):
        correct = sum(1 for row in rows if row["failure_mode"] == "correct")
        too_early = sum(1 for row in rows if row["failure_mode"] == "selected_too_early")
        too_late = sum(1 for row in rows if row["failure_mode"] == "selected_too_late")
        no_selection = sum(1 for row in rows if row["failure_mode"] == "no_selection")
        audit_failed = len(rows) - correct
        emitted = emitted_by_scale.get(scale, 0)
        projected_pgs = base_pgs_by_scale.get(scale, 0) + len(rows)
        out.append(
            {
                "scale": scale,
                "interpretation": interpretation,
                "shadow_seed_rows": len(rows),
                "correct": correct,
                "correct_percent": rate(correct, len(rows)) * 100.0,
                "audit_failed_if_promoted": audit_failed,
                "selected_too_early": too_early,
                "selected_too_late": too_late,
                "no_selection": no_selection,
                "emitted_count": emitted,
                "projected_pgs_count": projected_pgs,
                "projected_pgs_percent": rate(projected_pgs, emitted) * 100.0,
                "promotion_eligible": (
                    audit_failed == 0
                    and emitted > 0
                    and rate(projected_pgs, emitted) >= 0.50
                ),
            }
        )
    return out


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Test re-invoking chamber closure from a shadow seed."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--candidate-bound", type=int, default=DEFAULT_CANDIDATE_BOUND)
    parser.add_argument(
        "--visible-divisor-bound",
        type=int,
        default=DEFAULT_VISIBLE_DIVISOR_BOUND,
    )
    return parser.parse_args()


def main() -> int:
    """Run the probe."""
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    source_rows = read_jsonl(args.input)
    probe_rows = build_probe_rows(
        source_rows,
        int(args.candidate_bound),
        int(args.visible_divisor_bound),
    )
    summary_rows = summarize(source_rows, probe_rows)
    payload = {
        "solution_id": "grok_solution_01b_reinvoke_chamber_closure_from_shadow_seed",
        "generator_changed": False,
        "candidate_bound": int(args.candidate_bound),
        "visible_divisor_bound": int(args.visible_divisor_bound),
        "probe_rows": len(probe_rows),
        "summary_rows": summary_rows,
        "promotion_eligible": any(row["promotion_eligible"] for row in summary_rows),
        "verdict": "rejected",
        "reason": (
            "Both literal interpretations of chamber_closure(p, start=q0) select "
            "false right-side candidates on high-scale shadow-seed rows."
        ),
    }
    write_csv(probe_rows, args.output_dir / "rows.csv")
    write_csv(summary_rows, args.output_dir / "summary.csv")
    write_json(payload, args.output_dir / "summary.json")
    print(
        "solution_01b promotion_eligible={eligible} probe_rows={rows}".format(
            eligible=str(payload["promotion_eligible"]).lower(),
            rows=len(probe_rows),
        )
    )
    for row in summary_rows:
        print(
            "scale={scale} interpretation={interpretation} "
            "correct={correct}/{shadow_seed_rows} "
            "audit_failed_if_promoted={audit_failed_if_promoted} "
            "projected_pgs_percent={projected_pgs_percent:.2f}% "
            "promotion_eligible={promotion_eligible}".format(**row)
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
