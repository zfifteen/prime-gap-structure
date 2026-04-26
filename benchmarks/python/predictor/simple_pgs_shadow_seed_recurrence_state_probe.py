"""Probe recurrence-state stop rules for shadow-seed recovery rows."""

from __future__ import annotations

import argparse
import csv
import json
import statistics
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_INPUT = (
    ROOT
    / "output"
    / "simple_pgs_shadow_seed_recovery_displacement_probe"
    / "candidate_rows.csv"
)
DEFAULT_OUTPUT_DIR = (
    ROOT / "output" / "simple_pgs_shadow_seed_recurrence_state_probe"
)


def read_csv(path: Path) -> list[dict[str, str]]:
    """Read CSV rows."""
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


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


def state_of(row: dict[str, str]) -> str:
    """Return the visible recurrence state for one candidate."""
    if row["wheel_open"] != "True":
        return "W"
    if row["visible_closure_reason"]:
        return "C"
    return "O"


def witness_bucket(raw: str) -> str:
    """Return a compact divisor-witness bucket."""
    if not raw:
        return "none"
    witness = int(raw)
    if witness <= 5:
        return "le5"
    if witness <= 30:
        return "le30"
    if witness <= 210:
        return "le210"
    if witness <= 1000:
        return "le1000"
    return "le10000"


def run_lengths(states: list[str], target: set[str]) -> list[int]:
    """Return run lengths over selected state symbols."""
    lengths: list[int] = []
    current = 0
    for state in states:
        if state in target:
            current += 1
        elif current:
            lengths.append(current)
            current = 0
    if current:
        lengths.append(current)
    return lengths


def compact_counts(counter: Counter[str]) -> str:
    """Return stable compact count text."""
    return "|".join(f"{key}:{counter[key]}" for key in sorted(counter))


def compact_ints(values: list[int]) -> str:
    """Return compact vector text."""
    return ".".join(str(value) for value in values)


def recurrence_signature(states: list[str]) -> str:
    """Return a compressed recurrence signature."""
    if not states:
        return ""
    out: list[str] = []
    last = states[0]
    count = 1
    for state in states[1:]:
        if state == last:
            count += 1
            continue
        out.append(f"{last}{count}")
        last = state
        count = 1
    out.append(f"{last}{count}")
    return ".".join(out[-8:])


def grouped_candidate_rows(
    rows: list[dict[str, str]],
    scales: set[int],
) -> dict[tuple[int, int, int], list[dict[str, str]]]:
    """Return candidate rows grouped by one shadow-seed event."""
    groups: dict[tuple[int, int, int], list[dict[str, str]]] = {}
    for row in rows:
        scale = int(row["scale"])
        if scale not in scales:
            continue
        key = (scale, int(row["anchor_p"]), int(row["seed_q0"]))
        groups.setdefault(key, []).append(row)
    for group in groups.values():
        group.sort(key=lambda row: int(row["candidate_index_from_seed"]))
    return groups


def enrich_group(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    """Return recurrence-state rows for one shadow-seed sequence."""
    states = [state_of(row) for row in rows]
    visible_open_positions = [
        index
        for index, state in enumerate(states)
        if state == "O"
    ]
    visible_open_gaps: list[int] = []
    state_rows: list[dict[str, object]] = []
    closure_counts: Counter[str] = Counter()
    witness_counts: Counter[str] = Counter()
    seen_open_offsets: list[int] = []
    for index, row in enumerate(rows):
        state = states[index]
        prefix_states = states[: index + 1]
        prefix_offsets = [
            int(candidate["candidate_offset_from_seed"])
            for candidate in rows[: index + 1]
            if state_of(candidate) == "O"
        ]
        if state == "O":
            current_offset = int(row["candidate_offset_from_seed"])
            if seen_open_offsets:
                visible_open_gaps.append(current_offset - seen_open_offsets[-1])
            seen_open_offsets.append(current_offset)
        reason = row["visible_closure_reason"]
        if reason:
            closure_counts[reason.split(":", 1)[0]] += 1
        witness_counts[witness_bucket(row["visible_divisor_witness_under_10000"])] += 1
        previous_transition = (
            "START" if index == 0 else f"{states[index - 1]}>{states[index]}"
        )
        next_transition = (
            "END"
            if index + 1 >= len(states)
            else f"{states[index]}>{states[index + 1]}"
        )
        max_gap = max(visible_open_gaps) if visible_open_gaps else 0
        median_gap = statistics.median(visible_open_gaps) if visible_open_gaps else 0
        state_rows.append(
            {
                "scale": int(row["scale"]),
                "anchor_p": int(row["anchor_p"]),
                "seed_q0": int(row["seed_q0"]),
                "recovered_q_for_audit_only": int(row["recovered_q_for_audit_only"]),
                "candidate_n": int(row["candidate_n"]),
                "is_recovered_q_for_audit_only": row["is_recovered_q_for_audit_only"],
                "prefix_length": index + 1,
                "prefix_visible_open_count": prefix_states.count("O"),
                "prefix_visible_closed_count": prefix_states.count("C"),
                "prefix_wheel_closed_count": prefix_states.count("W"),
                "prefix_delta_vector": compact_ints(visible_open_gaps[-8:]),
                "prefix_delta_multiset": compact_counts(
                    Counter(str(value) for value in visible_open_gaps)
                ),
                "prefix_mod30_vector": compact_ints(
                    [int(candidate["candidate_mod_30"]) for candidate in rows[: index + 1]][-12:]
                ),
                "prefix_mod210_vector": compact_ints(
                    [int(candidate["candidate_mod_210"]) for candidate in rows[: index + 1]][-12:]
                ),
                "prefix_visible_open_run_lengths": compact_ints(
                    run_lengths(prefix_states, {"O"})
                ),
                "prefix_closed_run_lengths": compact_ints(
                    run_lengths(prefix_states, {"C", "W"})
                ),
                "last_visible_open_gap": visible_open_gaps[-1] if visible_open_gaps else 0,
                "max_visible_open_gap_so_far": max_gap,
                "median_visible_open_gap_so_far": median_gap,
                "closure_reason_counts_so_far": compact_counts(closure_counts),
                "divisor_witness_bucket_counts_so_far": compact_counts(witness_counts),
                "state_transition_from_previous_candidate": previous_transition,
                "state_transition_to_next_candidate": next_transition,
                "recurrence_signature_i": recurrence_signature(prefix_states),
                "local_state_suffix": "".join(prefix_states[-8:]),
                "candidate_state": state,
                "visible_open_ordinal": (
                    visible_open_positions.index(index) + 1
                    if index in visible_open_positions
                    else 0
                ),
            }
        )
    return state_rows


def pick_rr1(rows: list[dict[str, object]]) -> dict[str, object] | None:
    """First candidate where a repeated local suffix breaks."""
    seen: set[str] = set()
    for index, row in enumerate(rows):
        suffix = str(row["local_state_suffix"])
        if index > 0 and suffix not in seen and str(rows[index - 1]["local_state_suffix"]) in seen:
            if row["candidate_state"] == "O":
                return row
        seen.add(suffix)
    return None


def pick_rr2(rows: list[dict[str, object]]) -> dict[str, object] | None:
    """First visible-open candidate whose gap exceeds all previous visible-open gaps."""
    best_gap = 0
    for row in rows:
        if row["candidate_state"] != "O":
            continue
        gap = int(row["last_visible_open_gap"])
        if gap > best_gap and best_gap > 0:
            return row
        best_gap = max(best_gap, gap)
    return None


def pick_rr3(rows: list[dict[str, object]]) -> dict[str, object] | None:
    """First candidate where next transition differs from the previous two."""
    transitions = [str(row["state_transition_to_next_candidate"]) for row in rows]
    for index, row in enumerate(rows):
        if index < 2 or row["candidate_state"] != "O":
            continue
        if transitions[index - 1] == transitions[index - 2] and transitions[index] != transitions[index - 1]:
            return row
    return None


def pick_rr4(rows: list[dict[str, object]]) -> dict[str, object] | None:
    """First visible-open candidate after closure counts stop adding categories."""
    last_counts = ""
    stable = 0
    for row in rows:
        counts = str(row["closure_reason_counts_so_far"])
        if counts == last_counts:
            stable += 1
        else:
            stable = 0
        last_counts = counts
        if row["candidate_state"] == "O" and stable >= 3:
            return row
    return None


def pick_rr5(rows: list[dict[str, object]]) -> dict[str, object] | None:
    """First visible-open candidate where the next suffix breaks the prefix suffix."""
    states = [str(row["candidate_state"]) for row in rows]
    for index, row in enumerate(rows):
        if row["candidate_state"] != "O" or index < 3 or index + 3 >= len(rows):
            continue
        left = "".join(states[max(0, index - 3) : index])
        right = "".join(states[index + 1 : index + 4])
        if left and right and left != right:
            return row
    return None


def pick_rr6(rows: list[dict[str, object]]) -> dict[str, object] | None:
    """First visible-open candidate after a closed run follows an open run."""
    states = [str(row["candidate_state"]) for row in rows]
    for index, row in enumerate(rows):
        if row["candidate_state"] != "O" or index < 2:
            continue
        if "O" in states[:index] and states[index - 1] in {"C", "W"}:
            return row
    return None


def pick_rr7(rows: list[dict[str, object]]) -> dict[str, object] | None:
    """First candidate in a new open-density regime."""
    for index, row in enumerate(rows):
        if row["candidate_state"] != "O" or index < 8:
            continue
        prefix = rows[:index]
        recent = rows[max(0, index - 8) : index]
        prefix_open = sum(1 for item in prefix if item["candidate_state"] == "O") / len(prefix)
        recent_open = sum(1 for item in recent if item["candidate_state"] == "O") / len(recent)
        if abs(recent_open - prefix_open) >= 0.20:
            return row
    return None


RULES = {
    "RR1_repeated_signature_break": pick_rr1,
    "RR2_visible_open_gap_record": pick_rr2,
    "RR3_transition_class_break": pick_rr3,
    "RR4_closure_counts_fixed_point": pick_rr4,
    "RR5_suffix_breaks_prefix_pattern": pick_rr5,
    "RR6_after_visible_open_impostor_run": pick_rr6,
    "RR7_new_open_density_regime": pick_rr7,
}


def failure_mode(pick: dict[str, object] | None, recovered_q: int) -> str:
    """Return failure-mode label."""
    if pick is None:
        return "no_selection"
    candidate = int(pick["candidate_n"])
    if candidate == int(recovered_q):
        return "correct"
    if candidate < int(recovered_q):
        return "selected_too_early"
    return "selected_too_late"


def summarize_rules(
    groups: dict[tuple[int, int, int], list[dict[str, object]]],
    scales: list[int],
    base_pgs_counts: dict[int, int],
    emitted_counts: dict[int, int],
) -> list[dict[str, object]]:
    """Return recurrence-rule summaries."""
    summaries: list[dict[str, object]] = []
    for scale in scales:
        scale_groups = {
            key: rows
            for key, rows in groups.items()
            if key[0] == scale
        }
        for rule_id, picker in RULES.items():
            modes: Counter[str] = Counter()
            correct = 0
            selected = 0
            for rows in scale_groups.values():
                recovered_q = int(rows[0]["recovered_q_for_audit_only"])
                pick = picker(rows)
                mode = failure_mode(pick, recovered_q)
                modes[mode] += 1
                if pick is not None:
                    selected += 1
                if mode == "correct":
                    correct += 1
            failures = selected - correct
            emitted = emitted_counts[scale]
            projected = 0.0 if emitted == 0 else (base_pgs_counts[scale] + correct) / emitted * 100.0
            useful = correct / len(scale_groups) >= 0.75 if scale_groups else False
            summaries.append(
                {
                    "scale": scale,
                    "rule_id": rule_id,
                    "shadow_seed_rows": len(scale_groups),
                    "top1_selected": selected,
                    "top1_correct": correct,
                    "top1_recall": 0.0 if not scale_groups else correct / len(scale_groups),
                    "would_convert_shadow_recovery_to_pgs": correct,
                    "would_create_audit_failures": failures,
                    "projected_pgs_percent": projected,
                    "promotion_eligible": failures == 0 and projected >= 50.0,
                    "research_candidate": useful,
                    "failure_mode_selected_too_early": modes["selected_too_early"],
                    "failure_mode_selected_too_late": modes["selected_too_late"],
                    "failure_mode_no_selection": modes["no_selection"],
                }
            )
    return summaries


def run_probe(
    input_path: Path,
    output_dir: Path,
    scales: list[int],
) -> dict[str, object]:
    """Run recurrence-state probe."""
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_rows = read_csv(input_path)
    grouped_raw = grouped_candidate_rows(raw_rows, set(scales))
    state_rows: list[dict[str, object]] = []
    groups: dict[tuple[int, int, int], list[dict[str, object]]] = {}
    for key, rows in grouped_raw.items():
        enriched = enrich_group(rows)
        groups[key] = enriched
        state_rows.extend(enriched)
    base_pgs_counts = {
        10**15: 108,
        10**18: 105,
    }
    emitted_counts = {
        10**15: 249,
        10**18: 250,
    }
    rule_rows = summarize_rules(groups, scales, base_pgs_counts, emitted_counts)
    promotion_rules = sorted(
        {
            str(row["rule_id"])
            for row in rule_rows
            if bool(row["promotion_eligible"])
        }
    )
    research_rules = sorted(
        {
            str(row["rule_id"])
            for row in rule_rows
            if bool(row["research_candidate"])
        }
    )
    summary = {
        "input": str(input_path),
        "scales": scales,
        "state_row_count": len(state_rows),
        "shadow_seed_rows": len(groups),
        "rule_rows": rule_rows,
        "promotion_eligible_rules": promotion_rules,
        "research_candidate_rules": research_rules,
        "strongest_result": (
            "recurrence_rules_do_not_promote; "
            "terminality_not_in_tested_prefix_transition_state"
        ),
    }
    write_csv(state_rows, output_dir / "recurrence_state_rows.csv")
    write_csv(rule_rows, output_dir / "recurrence_rule_report.csv")
    write_json(summary, output_dir / "summary.json")
    return summary


def build_parser() -> argparse.ArgumentParser:
    """Build CLI parser."""
    parser = argparse.ArgumentParser(
        description="Probe recurrence-state rules for shadow-seed recovery."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--scales", type=int, nargs="+", default=[10**15, 10**18])
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run CLI."""
    args = build_parser().parse_args(argv)
    summary = run_probe(args.input, args.output_dir, [int(scale) for scale in args.scales])
    print(
        "state_rows={state_row_count} shadow_seed_rows={shadow_seed_rows} "
        "promotion_eligible_rules={rules} strongest_result={strongest_result}".format(
            state_row_count=summary["state_row_count"],
            shadow_seed_rows=summary["shadow_seed_rows"],
            rules=",".join(summary["promotion_eligible_rules"]) or "none",
            strongest_result=summary["strongest_result"],
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
