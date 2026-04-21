#!/usr/bin/env python3
"""Test whether reset laws act like real phase kicks in the reduced gap engine."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import math
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Hashable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from hourly_research_relay_common import (
    ROOT,
    append_jsonl_row,
    prepare_task_branch,
    read_last_jsonl_row,
    remote_json,
    run_git,
    stage_commit_push,
    utc_timestamp_compact,
    utc_timestamp_iso,
    write_json,
)


DEFAULT_OUTPUT_DIR = ROOT / "output"
DEFAULT_DETAIL_CSV = ROOT / "output" / "gwr_dni_gap_type_catalog_details.csv"
DEFAULT_TRAIN_MIN_POWER = 7
DEFAULT_TRAIN_MAX_POWER = 17
DEFAULT_REFERENCE_MIN_POWER = 12
DEFAULT_REFERENCE_MAX_POWER = 18
DEFAULT_SYNTHETIC_LENGTH = 1_000_000
DEFAULT_WINDOW_LENGTH = 256
DEFAULT_MOD_CYCLE_LENGTH = 8
TASK_BRANCH = "codex/research-phase-reset-hunter"
FIRST_LAUNCH_BASE_BRANCH = "origin/codex/even-winner-next-opening-probe"
COMPRESSION_REMOTE_BRANCH = "origin/codex/research-compression-shock-probe"
COMPRESSION_SUMMARY_REMOTE_PATH = "output/gwr_compression_shock_probe_summary.json"
HIDDEN_STATE_REMOTE_BRANCH = "origin/codex/research-hidden-state-miner"
HIDDEN_STATE_SUMMARY_REMOTE_PATH = "output/gwr_hidden_state_miner_summary.json"
SUMMARY_PATH = ROOT / "output" / "gwr_phase_reset_hunter_summary.json"
RULES_CSV_PATH = ROOT / "output" / "gwr_phase_reset_hunter_rules.csv"
HISTORY_PATH = ROOT / "output" / "gwr_phase_reset_hunter_history.jsonl"
PLOT_PATH = ROOT / "output" / "gwr_phase_reset_hunter_overview.png"
FINDINGS_PATH = ROOT / "gwr" / "findings" / "phase_reset_hunter_findings.md"
TEST_PATH = ROOT / "tests" / "python" / "predictor" / "test_gwr_phase_reset_hunter.py"
COMPRESSION_PATH = Path(__file__).with_name("gwr_compression_shock_probe.py")


def load_module(module_path: Path, module_name: str):
    """Load one sibling module from disk."""
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


COMPRESSION = load_module(COMPRESSION_PATH, "gwr_compression_shock_probe_phase")
TRIAD_SET = COMPRESSION.TRIAD_SET
RESET_RULES = (
    "no_reset",
    "reset_on_even_winner",
    "reset_on_odd_winner",
    "reset_on_even_semiprime",
    "reset_on_odd_semiprime",
    "reset_on_nontriad",
    "reset_on_higher_divisor",
    "reset_on_best_hidden_state_label",
)
RULE_COLORS = {
    "no_reset": "#8c8c8c",
    "reset_on_even_winner": "#1f77b4",
    "reset_on_odd_winner": "#ff7f0e",
    "reset_on_even_semiprime": "#2ca02c",
    "reset_on_odd_semiprime": "#d62728",
    "reset_on_nontriad": "#9467bd",
    "reset_on_higher_divisor": "#8c564b",
    "reset_on_best_hidden_state_label": "#17becf",
}


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Layer candidate reset laws onto the compression winner and test "
            "whether any of them create a real phase kick."
        ),
    )
    parser.add_argument("--detail-csv", type=Path, default=DEFAULT_DETAIL_CSV)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--train-min-power", type=int, default=DEFAULT_TRAIN_MIN_POWER)
    parser.add_argument("--train-max-power", type=int, default=DEFAULT_TRAIN_MAX_POWER)
    parser.add_argument("--reference-min-power", type=int, default=DEFAULT_REFERENCE_MIN_POWER)
    parser.add_argument("--reference-max-power", type=int, default=DEFAULT_REFERENCE_MAX_POWER)
    parser.add_argument("--synthetic-length", type=int, default=DEFAULT_SYNTHETIC_LENGTH)
    parser.add_argument("--window-length", type=int, default=DEFAULT_WINDOW_LENGTH)
    parser.add_argument("--mod-cycle-length", type=int, default=DEFAULT_MOD_CYCLE_LENGTH)
    return parser


def base_recipe(model_id: str) -> str:
    """Return the base context recipe implied by the compression winner."""
    if model_id == "first_order_rotor":
        return "unsupported_order1"
    if model_id in {"second_order_rotor", "mod_cycle_scheduler"}:
        return "order2"
    if model_id in {
        "lag2_state_scheduler",
        "hybrid_lag2_mod8_scheduler",
        "hybrid_lag2_mod8_reset_hdiv_scheduler",
        "hybrid_lag2_mod8_reset_nontriad_scheduler",
    }:
        return "order3"
    if model_id in {
        "hidden_state_augmented_rotor",
        "hidden_state_phase_scheduler",
        "hidden_state_reset_scheduler",
    }:
        return "order2_hidden"
    raise ValueError(f"unsupported base model id: {model_id}")


def load_upstream_summaries() -> tuple[dict[str, object] | None, dict[str, object] | None, str | None]:
    """Return the upstream compression and hidden-state summaries, or the blocker."""
    try:
        compression_summary = remote_json(COMPRESSION_REMOTE_BRANCH, COMPRESSION_SUMMARY_REMOTE_PATH)
    except subprocess.CalledProcessError:
        return None, None, "missing upstream compression summary"
    try:
        hidden_state_summary = remote_json(HIDDEN_STATE_REMOTE_BRANCH, HIDDEN_STATE_SUMMARY_REMOTE_PATH)
    except subprocess.CalledProcessError:
        return compression_summary, None, "missing upstream hidden-state summary"
    if not compression_summary.get("models"):
        return compression_summary, hidden_state_summary, "compression summary does not contain an evaluated model set"
    if compression_summary.get("shock_winner_model_id") is None:
        return compression_summary, hidden_state_summary, "compression summary contains only a negative result"
    if not isinstance(hidden_state_summary.get("best_candidate"), dict):
        return compression_summary, hidden_state_summary, "hidden-state summary does not name a best candidate"
    return compression_summary, hidden_state_summary, None


def pseudo_row(
    state: str,
    peak_offset: int,
    winner_parity: str,
) -> dict[str, object]:
    """Return one synthetic row from carried context fields."""
    return {
        "state": state,
        "next_peak_offset": int(peak_offset),
        "carrier_family": state.split("|", 1)[0].split("_", 1)[1],
        "winner_parity": winner_parity,
    }


def hidden_label_from_rows(
    previous_row: dict[str, object] | None,
    current_row: dict[str, object],
    candidate_id: str,
) -> str:
    """Return the hidden-state label on the current row."""
    return COMPRESSION.candidate_label(previous_row, current_row, candidate_id)


def entropy(counter: Counter[int]) -> float:
    """Return the Shannon entropy of one discrete distribution."""
    total = sum(counter.values())
    if total == 0:
        return 0.0
    value = 0.0
    for count in counter.values():
        probability = count / total
        value -= probability * math.log(probability)
    return value


def reset_trigger(
    rule_id: str,
    previous_row: dict[str, object] | None,
    current_row: dict[str, object],
    candidate_id: str,
    best_hidden_label: str,
) -> bool:
    """Return whether one reset rule fires on the current row."""
    if rule_id == "no_reset":
        return False
    if rule_id == "reset_on_even_winner":
        return str(current_row["winner_parity"]) == "even"
    if rule_id == "reset_on_odd_winner":
        return str(current_row["winner_parity"]) == "odd"
    if rule_id == "reset_on_even_semiprime":
        return str(current_row["carrier_family"]) == "even_semiprime"
    if rule_id == "reset_on_odd_semiprime":
        return str(current_row["carrier_family"]) == "odd_semiprime"
    if rule_id == "reset_on_nontriad":
        return str(current_row["state"]) not in TRIAD_SET
    if rule_id == "reset_on_higher_divisor":
        return "higher_divisor" in str(current_row["carrier_family"])
    if rule_id == "reset_on_best_hidden_state_label":
        return hidden_label_from_rows(previous_row, current_row, candidate_id) == best_hidden_label
    raise ValueError(f"unsupported reset rule: {rule_id}")


def advance_phase(
    phase: int,
    rule_id: str,
    previous_row: dict[str, object] | None,
    current_row: dict[str, object],
    candidate_id: str,
    best_hidden_label: str,
    mod_cycle_length: int,
) -> int:
    """Advance the phase under one reset law."""
    if reset_trigger(rule_id, previous_row, current_row, candidate_id, best_hidden_label):
        return 0
    return (phase + 1) % mod_cycle_length


def context_from_rows(
    recipe: str,
    phase: int,
    left_row: dict[str, object],
    current_row: dict[str, object],
    candidate_id: str,
) -> Hashable:
    """Build one reset-hunter context from concrete rows."""
    if recipe == "order2":
        return (
            phase,
            str(left_row["state"]),
            str(current_row["state"]),
            int(current_row["next_peak_offset"]),
            str(current_row["winner_parity"]),
            "START" if COMPRESSION.candidate_uses_previous_winner_parity(candidate_id) is False else str(left_row["winner_parity"]),
        )
    if recipe == "order3":
        return (
            phase,
            str(left_row["state"]),
            str(current_row["state"]),
            int(current_row["next_peak_offset"]),
            str(current_row["winner_parity"]),
            "START" if COMPRESSION.candidate_uses_previous_winner_parity(candidate_id) is False else str(left_row["winner_parity"]),
        )
    if recipe == "order2_hidden":
        return (
            phase,
            str(left_row["state"]),
            str(current_row["state"]),
            hidden_label_from_rows(left_row, current_row, candidate_id),
            int(current_row["next_peak_offset"]),
            str(current_row["winner_parity"]),
            "START" if COMPRESSION.candidate_uses_previous_winner_parity(candidate_id) is False else str(left_row["winner_parity"]),
        )
    raise ValueError(f"unsupported recipe: {recipe}")


def current_rows_from_context(recipe: str, context: Hashable) -> tuple[dict[str, object], dict[str, object]]:
    """Reconstruct the current row pair from one context."""
    if recipe == "order2":
        _phase, left_state, current_state, current_peak, current_parity, left_parity = context
        return (
            pseudo_row(left_state, 0, "START" if left_parity == "START" else left_parity),
            pseudo_row(current_state, current_peak, current_parity),
        )
    if recipe == "order3":
        _phase, left_state, current_state, current_peak, current_parity, left_parity = context
        return (
            pseudo_row(left_state, 0, "START" if left_parity == "START" else left_parity),
            pseudo_row(current_state, current_peak, current_parity),
        )
    if recipe == "order2_hidden":
        _phase, left_state, current_state, _current_label, current_peak, current_parity, left_parity = context
        return (
            pseudo_row(left_state, 0, "START" if left_parity == "START" else left_parity),
            pseudo_row(current_state, current_peak, current_parity),
        )
    raise ValueError(f"unsupported recipe: {recipe}")


def successor_context(
    recipe: str,
    context: Hashable,
    next_payload: COMPRESSION.Payload,
    rule_id: str,
    candidate_id: str,
    best_hidden_label: str,
    mod_cycle_length: int,
) -> Hashable:
    """Advance one context with one emitted payload."""
    previous_row, current_row = current_rows_from_context(recipe, context)
    phase = int(context[0])
    next_phase = advance_phase(
        phase=phase,
        rule_id=rule_id,
        previous_row=previous_row,
        current_row=current_row,
        candidate_id=candidate_id,
        best_hidden_label=best_hidden_label,
        mod_cycle_length=mod_cycle_length,
    )
    next_row = COMPRESSION.synthetic_row(0, next_payload)
    if recipe == "order2":
        return (
            next_phase,
            str(current_row["state"]),
            str(next_row["state"]),
            int(next_row["next_peak_offset"]),
            str(next_row["winner_parity"]),
            "START" if COMPRESSION.candidate_uses_previous_winner_parity(candidate_id) is False else str(current_row["winner_parity"]),
        )
    if recipe == "order3":
        return (
            next_phase,
            str(current_row["state"]),
            str(next_row["state"]),
            int(next_row["next_peak_offset"]),
            str(next_row["winner_parity"]),
            "START" if COMPRESSION.candidate_uses_previous_winner_parity(candidate_id) is False else str(current_row["winner_parity"]),
        )
    if recipe == "order2_hidden":
        return (
            next_phase,
            str(current_row["state"]),
            str(next_row["state"]),
            hidden_label_from_rows(current_row, next_row, candidate_id),
            int(next_row["next_peak_offset"]),
            str(next_row["winner_parity"]),
            "START" if COMPRESSION.candidate_uses_previous_winner_parity(candidate_id) is False else str(current_row["winner_parity"]),
        )
    raise ValueError(f"unsupported recipe: {recipe}")


def build_rule_support(
    segments: list[list[dict[str, str]]],
    recipe: str,
    rule_id: str,
    candidate_id: str,
    best_hidden_label: str,
    mod_cycle_length: int,
) -> tuple[dict[Hashable, Counter[COMPRESSION.Payload]], Hashable, float, int]:
    """Build one reset-rule support and its reset signature."""
    counter: dict[Hashable, Counter[COMPRESSION.Payload]] = defaultdict(Counter)
    start_counter: Counter[Hashable] = Counter()
    rule_phase_counter: Counter[int] = Counter()
    control_phase_counter: Counter[int] = Counter()
    for segment in segments:
        rows = [COMPRESSION.synthetic_row(index + 1, COMPRESSION.extended_payload(row)) for index, row in enumerate(segment)]
        if recipe == "order2" and len(rows) < 3:
            continue
        if recipe == "order3" and len(rows) < 4:
            continue
        if recipe == "order2_hidden" and len(rows) < 3:
            continue
        phase = 0
        if recipe == "order2":
            start_counter[context_from_rows(recipe, phase, rows[0], rows[1], candidate_id)] += 1
            iterator = zip(rows, rows[1:], rows[2:])
        elif recipe == "order3":
            start_counter[context_from_rows(recipe, phase, rows[1], rows[2], candidate_id)] += 1
            iterator = zip(rows[1:], rows[2:], rows[3:])
        else:
            start_counter[context_from_rows(recipe, phase, rows[0], rows[1], candidate_id)] += 1
            iterator = zip(rows, rows[1:], rows[2:])

        for left_row, current_row, next_row in iterator:
            context = context_from_rows(recipe, phase, left_row, current_row, candidate_id)
            next_payload = (
                str(next_row["state"]),
                str(next_row["type_key"]),
                int(next_row["next_peak_offset"]),
                str(next_row["carrier_family"]),
                str(next_row["winner_parity"]),
            )
            counter[context][next_payload] += 1
            if reset_trigger(rule_id, left_row, current_row, candidate_id, best_hidden_label):
                rule_phase_counter[0] += 1
                control_phase_counter[(phase + 1) % mod_cycle_length] += 1
            phase = advance_phase(
                phase=phase,
                rule_id=rule_id,
                previous_row=left_row,
                current_row=current_row,
                candidate_id=candidate_id,
                best_hidden_label=best_hidden_label,
                mod_cycle_length=mod_cycle_length,
            )
    pruned = COMPRESSION.pruned_payload_counter(
        counter,
        lambda context, payload: successor_context(
            recipe=recipe,
            context=context,
            next_payload=payload,
            rule_id=rule_id,
            candidate_id=candidate_id,
            best_hidden_label=best_hidden_label,
            mod_cycle_length=mod_cycle_length,
        ),
    )
    start_context = COMPRESSION.choose_start_context(start_counter, pruned)
    signature_gain = entropy(control_phase_counter) - entropy(rule_phase_counter)
    return pruned, start_context, signature_gain, len(rule_phase_counter)


def simulate_rule(
    transition_counter: dict[Hashable, Counter[COMPRESSION.Payload]],
    start_context: Hashable,
    recipe: str,
    rule_id: str,
    candidate_id: str,
    best_hidden_label: str,
    synthetic_length: int,
    mod_cycle_length: int,
) -> list[dict[str, object]]:
    """Emit one deterministic reset-rule walk."""
    transition_rotors = {
        context: COMPRESSION.GEN_PROBE.Rotor(COMPRESSION.GEN_PROBE.balanced_cycle(counter))
        for context, counter in transition_counter.items()
    }
    previous_row, current_row = current_rows_from_context(recipe, start_context)
    rows = [previous_row, current_row]
    phase = int(start_context[0])
    while len(rows) < synthetic_length:
        if recipe == "order3" and len(rows) >= 3:
            left_row = rows[-2]
            current_row = rows[-1]
        else:
            left_row = rows[-2]
            current_row = rows[-1]
        if recipe == "order2":
            context = context_from_rows(recipe, phase, left_row, current_row, candidate_id)
        elif recipe == "order3":
            context = context_from_rows(recipe, phase, left_row, current_row, candidate_id)
        else:
            context = context_from_rows(recipe, phase, left_row, current_row, candidate_id)
        next_payload = transition_rotors[context].next()
        rows.append(COMPRESSION.synthetic_row(len(rows) + 1, next_payload))
        phase = advance_phase(
            phase=phase,
            rule_id=rule_id,
            previous_row=left_row,
            current_row=current_row,
            candidate_id=candidate_id,
            best_hidden_label=best_hidden_label,
            mod_cycle_length=mod_cycle_length,
        )
    return rows


def rank_reset_rules(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    """Return reset rules ordered by the task's selection rule."""
    return sorted(
        rows,
        key=lambda row: (
            float(row["pooled_window_concentration_l1"]),
            -float(row["three_step_concentration"]),
            -float(row["reset_signature_gain"]),
            int(row["distinct_reset_phases"]),
            str(row["rule_id"]),
        ),
    )


def write_rules_csv(rows: list[dict[str, object]], csv_path: Path) -> None:
    """Write the reset-rule comparison table."""
    fieldnames = [
        "rule_id",
        "pooled_window_concentration_l1",
        "one_step_concentration",
        "two_step_concentration",
        "three_step_concentration",
        "reset_signature_gain",
        "distinct_reset_phases",
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def build_overview_plot(summary: dict[str, object], plot_path: Path) -> None:
    """Render one compact reset-rule overview plot."""
    rows = summary["rules"]
    ordered = sorted(rows, key=lambda row: RESET_RULES.index(str(row["rule_id"])))
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    axes[0].bar(
        [str(row["rule_id"]) for row in ordered],
        [float(row["pooled_window_concentration_l1"]) for row in ordered],
        color=[RULE_COLORS[str(row["rule_id"])] for row in ordered],
    )
    axes[0].tick_params(axis="x", rotation=70)
    axes[0].set_ylabel("Pooled-window concentration L1")
    axes[0].set_title("Reset Rules by Fit")

    axes[1].bar(
        [str(row["rule_id"]) for row in ordered],
        [float(row["reset_signature_gain"]) for row in ordered],
        color=[RULE_COLORS[str(row["rule_id"])] for row in ordered],
    )
    axes[1].tick_params(axis="x", rotation=70)
    axes[1].set_ylabel("Reset-signature gain")
    axes[1].set_title("Phase-Kick Strength")

    fig.tight_layout()
    fig.savefig(plot_path, dpi=220)
    plt.close(fig)


def findings_markdown(summary: dict[str, object]) -> str:
    """Render the reset-hunter findings note."""
    if summary.get("blocked_reason") is not None:
        return "\n".join(
            [
                "# Phase-Reset Hunter Findings",
                "",
                f"This run blocked because `{summary['blocked_reason']}`.",
                "",
                "## Artifacts",
                "",
                "- [phase reset hunter script](../../benchmarks/python/predictor/gwr_phase_reset_hunter.py)",
                "- [summary JSON](../../output/gwr_phase_reset_hunter_summary.json)",
                "- [history JSONL](../../output/gwr_phase_reset_hunter_history.jsonl)",
            ]
        ) + "\n"

    best_rule = summary["best_rule"]
    best_nonparity = max(
        (row for row in summary["rules"] if row["rule_id"] not in {"reset_on_even_winner", "reset_on_odd_winner"}),
        key=lambda row: (
            -float(row["pooled_window_concentration_l1"]),
            float(row["three_step_concentration"]),
            float(row["reset_signature_gain"]),
        ),
        default=None,
    )
    parity_rows = [row for row in summary["rules"] if row["rule_id"] in {"reset_on_even_winner", "reset_on_odd_winner"}]
    best_parity = rank_reset_rules(parity_rows)[0] if parity_rows else None
    parity_beats_controls = (
        best_parity is not None
        and best_nonparity is not None
        and rank_reset_rules([best_parity, best_nonparity])[0]["rule_id"] == best_parity["rule_id"]
    )
    opening = (
        f"The best reset law over the `{summary['base_model_id']}` base recipe is `{best_rule['rule_id']}` "
        f"with pooled-window concentration L1 `{best_rule['pooled_window_concentration_l1']:.4f}`, "
        f"three-step concentration `{best_rule['three_step_concentration']:.4f}`, and "
        f"reset-signature gain `{best_rule['reset_signature_gain']:.4f}`."
    )
    interpretation = (
        "Parity behaves like a genuine phase kick on this surface."
        if parity_beats_controls
        else "The parity story collapses once reset-style controls are compared."
    )
    lines = [
        "# Phase-Reset Hunter Findings",
        "",
        opening,
        "",
        interpretation,
        "",
        "## Rule Table",
        "",
    ]
    for row in summary["ranking"]:
        lines.append(
            f"- `{row['rule_id']}`: pooled L1 `{row['pooled_window_concentration_l1']:.4f}`, three-step `{row['three_step_concentration']:.4f}`, reset gain `{row['reset_signature_gain']:.4f}`"
        )
    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            "- [phase reset hunter script](../../benchmarks/python/predictor/gwr_phase_reset_hunter.py)",
            "- [summary JSON](../../output/gwr_phase_reset_hunter_summary.json)",
            "- [rules CSV](../../output/gwr_phase_reset_hunter_rules.csv)",
            "- [history JSONL](../../output/gwr_phase_reset_hunter_history.jsonl)",
            "- ![Phase reset overview](../../output/gwr_phase_reset_hunter_overview.png)",
        ]
    )
    return "\n".join(lines) + "\n"


def run_targeted_pytest() -> None:
    """Run the targeted reset hunter tests."""
    subprocess.run(
        ["python3", "-m", "pytest", "-q", str(TEST_PATH.relative_to(ROOT))],
        check=True,
        cwd=ROOT,
        text=True,
    )


def summarize(
    frame: dict[str, object],
    compression_summary: dict[str, object],
    hidden_state_summary: dict[str, object],
    compression_source_commit: str,
    hidden_state_source_commit: str,
    synthetic_length: int,
    window_length: int,
    mod_cycle_length: int,
) -> dict[str, object]:
    """Build the phase-reset summary."""
    base_model_id = str(compression_summary["shock_winner_model_id"])
    recipe = base_recipe(base_model_id)
    candidate_id = str(hidden_state_summary["best_candidate"]["candidate_id"])
    best_hidden_label = str(hidden_state_summary["best_candidate"]["best_label"])
    rules: list[dict[str, object]] = []
    for rule_id in RESET_RULES:
        counter, start_context, signature_gain, distinct_reset_phases = build_rule_support(
            segments=frame["segments"],
            recipe=recipe,
            rule_id=rule_id,
            candidate_id=candidate_id,
            best_hidden_label=best_hidden_label,
            mod_cycle_length=mod_cycle_length,
        )
        synthetic_rows = simulate_rule(
            transition_counter=counter,
            start_context=start_context,
            recipe=recipe,
            rule_id=rule_id,
            candidate_id=candidate_id,
            best_hidden_label=best_hidden_label,
            synthetic_length=synthetic_length,
            mod_cycle_length=mod_cycle_length,
        )
        metrics = COMPRESSION.evaluate_synthetic_rows(
            synthetic_rows=synthetic_rows,
            real_window_concentrations=frame["real_window_concentrations"],
            real_family_distribution=frame["real_family_distribution"],
            real_peak_distribution=frame["real_peak_distribution"],
            real_higher_divisor_share=frame["real_higher_divisor_share"],
            window_length=window_length,
        )
        rules.append(
            {
                "rule_id": rule_id,
                "pooled_window_concentration_l1": float(metrics["pooled_window_concentration_l1"]),
                "one_step_concentration": float(metrics["full_walk_concentrations"]["one_step"]),
                "two_step_concentration": float(metrics["full_walk_concentrations"]["two_step"]),
                "three_step_concentration": float(metrics["full_walk_concentrations"]["three_step"]),
                "reset_signature_gain": float(signature_gain),
                "distinct_reset_phases": int(distinct_reset_phases),
            }
        )
    ranking = rank_reset_rules(rules)
    best_rule = ranking[0]
    return {
        "compression_source_commit": compression_source_commit,
        "hidden_state_source_commit": hidden_state_source_commit,
        "base_model_id": base_model_id,
        "rule_count": len(rules),
        "rules": rules,
        "ranking": ranking,
        "best_rule": best_rule,
    }


def write_blocked_outputs(
    blocked_reason: str,
    compression_source_commit: str | None,
    hidden_state_source_commit: str | None,
) -> dict[str, object]:
    """Write a blocked run's summary and findings."""
    summary = {
        "compression_source_commit": compression_source_commit,
        "hidden_state_source_commit": hidden_state_source_commit,
        "blocked_reason": blocked_reason,
        "rules": [],
        "rule_count": 0,
        "ranking": [],
        "best_rule": None,
    }
    write_json(SUMMARY_PATH, summary)
    write_rules_csv([], RULES_CSV_PATH)
    FINDINGS_PATH.write_text(findings_markdown(summary), encoding="utf-8")
    return summary


def main(argv: list[str] | None = None) -> int:
    """Run one full phase-reset hunter task."""
    args = build_parser().parse_args(argv)
    started = time.perf_counter()
    compact_timestamp = utc_timestamp_compact()
    previous_history_row = read_last_jsonl_row(HISTORY_PATH)
    starting_head, _current_head = prepare_task_branch(
        branch_name=TASK_BRANCH,
        first_launch_base_branch=FIRST_LAUNCH_BASE_BRANCH,
    )
    compression_summary, hidden_state_summary, blocked_reason = load_upstream_summaries()
    compression_source_commit = None
    hidden_state_source_commit = None
    if compression_summary is not None:
        compression_source_commit = run_git("rev-parse", COMPRESSION_REMOTE_BRANCH)
    if hidden_state_summary is not None:
        hidden_state_source_commit = run_git("rev-parse", HIDDEN_STATE_REMOTE_BRANCH)
    if blocked_reason is None and compression_summary is not None:
        recipe = base_recipe(str(compression_summary["shock_winner_model_id"]))
        if recipe == "unsupported_order1":
            blocked_reason = "phase reset hunter requires at least one-row memory beyond first_order_rotor"
    if blocked_reason is not None:
        summary = write_blocked_outputs(blocked_reason, compression_source_commit, hidden_state_source_commit)
        history_row = {
            "run_timestamp_utc": utc_timestamp_iso(),
            "branch": TASK_BRANCH,
            "head_commit": starting_head,
            "compression_source_commit": compression_source_commit,
            "hidden_state_source_commit": hidden_state_source_commit,
            "base_model_id": None if compression_summary is None else compression_summary.get("shock_winner_model_id"),
            "reset_rule_count": 0,
            "best_reset_rule_id": None,
            "best_pooled_l1": None,
            "best_three_step": None,
            "best_reset_signature_gain": None,
            "blocked_reason": blocked_reason,
        }
        append_jsonl_row(HISTORY_PATH, history_row)
        run_targeted_pytest()
        stage_commit_push(
            branch_name=TASK_BRANCH,
            artifact_paths=[Path(__file__), TEST_PATH, SUMMARY_PATH, RULES_CSV_PATH, HISTORY_PATH, FINDINGS_PATH],
            commit_message=f"phase-reset-hunter: {compact_timestamp}",
        )
        _ = summary
        return 0

    train_surfaces = [COMPRESSION.power_surface_label(power) for power in range(args.train_min_power, args.train_max_power + 1)]
    reference_surfaces = [
        COMPRESSION.power_surface_label(power)
        for power in range(args.reference_min_power, args.reference_max_power + 1)
    ]
    frame = COMPRESSION.build_training_frame(args.detail_csv, train_surfaces, reference_surfaces)
    summary = summarize(
        frame=frame,
        compression_summary=compression_summary,
        hidden_state_summary=hidden_state_summary,
        compression_source_commit=str(compression_source_commit),
        hidden_state_source_commit=str(hidden_state_source_commit),
        synthetic_length=int(args.synthetic_length),
        window_length=int(args.window_length),
        mod_cycle_length=int(args.mod_cycle_length),
    )
    summary["history_seed_present"] = previous_history_row is not None
    summary["runtime_seconds"] = time.perf_counter() - started
    write_json(SUMMARY_PATH, summary)
    write_rules_csv(summary["rules"], RULES_CSV_PATH)
    build_overview_plot(summary, PLOT_PATH)
    FINDINGS_PATH.write_text(findings_markdown(summary), encoding="utf-8")

    best_rule = summary["best_rule"]
    history_row = {
        "run_timestamp_utc": utc_timestamp_iso(),
        "branch": TASK_BRANCH,
        "head_commit": starting_head,
        "compression_source_commit": compression_source_commit,
        "hidden_state_source_commit": hidden_state_source_commit,
        "base_model_id": summary["base_model_id"],
        "reset_rule_count": int(summary["rule_count"]),
        "best_reset_rule_id": best_rule["rule_id"],
        "best_pooled_l1": float(best_rule["pooled_window_concentration_l1"]),
        "best_three_step": float(best_rule["three_step_concentration"]),
        "best_reset_signature_gain": float(best_rule["reset_signature_gain"]),
        "blocked_reason": None,
    }
    append_jsonl_row(HISTORY_PATH, history_row)
    run_targeted_pytest()
    stage_commit_push(
        branch_name=TASK_BRANCH,
        artifact_paths=[
            Path(__file__),
            TEST_PATH,
            SUMMARY_PATH,
            RULES_CSV_PATH,
            HISTORY_PATH,
            PLOT_PATH,
            FINDINGS_PATH,
        ],
        commit_message=f"phase-reset-hunter: {compact_timestamp}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
