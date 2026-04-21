#!/usr/bin/env python3
"""Find the smallest hidden state that improves next-gap triad-return prediction."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

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
    run_git,
    sigmoid_log_loss,
    stage_commit_push,
    utc_timestamp_compact,
    utc_timestamp_iso,
    write_json,
)


DEFAULT_OUTPUT_DIR = ROOT / "output"
DEFAULT_POWERS = (12, 13, 14, 15)
DEFAULT_WINDOW_STEPS = 2048
TASK_BRANCH = "codex/research-hidden-state-miner"
FIRST_LAUNCH_BASE_BRANCH = "origin/codex/even-winner-next-opening-probe"
PARITY_PROBE_REMOTE_BRANCH = "origin/codex/even-winner-next-opening-probe"
PARITY_PROBE_PATH = Path(__file__).with_name("gwr_winner_parity_next_opening_probe.py")
PARITY_SUMMARY_PATH = ROOT / "output" / "gwr_winner_parity_next_opening_probe_summary.json"
PARITY_FINDINGS_PATH = ROOT / "gwr" / "findings" / "winner_parity_next_opening_probe_findings.md"
SUMMARY_PATH = ROOT / "output" / "gwr_hidden_state_miner_summary.json"
CANDIDATES_CSV_PATH = ROOT / "output" / "gwr_hidden_state_miner_candidates.csv"
HISTORY_PATH = ROOT / "output" / "gwr_hidden_state_miner_history.jsonl"
PLOT_PATH = ROOT / "output" / "gwr_hidden_state_miner_overview.png"
FINDINGS_PATH = ROOT / "gwr" / "findings" / "hidden_state_miner_findings.md"
TEST_PATH = ROOT / "tests" / "python" / "predictor" / "test_gwr_hidden_state_miner.py"

CANDIDATE_SPECS = (
    ("current_winner_parity", ("current_winner_parity",)),
    ("current_winner_offset", ("current_winner_offset",)),
    ("current_carrier_family", ("current_carrier_family",)),
    ("current_d_bucket", ("current_d_bucket",)),
    ("previous_reduced_state", ("previous_reduced_state",)),
    ("previous_winner_parity", ("previous_winner_parity",)),
    ("previous_carrier_family", ("previous_carrier_family",)),
    ("current_winner_parity+current_winner_offset", ("current_winner_parity", "current_winner_offset")),
    (
        "current_winner_parity+current_carrier_family",
        ("current_winner_parity", "current_carrier_family"),
    ),
    (
        "current_winner_parity+previous_reduced_state",
        ("current_winner_parity", "previous_reduced_state"),
    ),
)
LANE_ORDER = (
    "o2_odd_semiprime|d<=4",
    "o4_odd_semiprime|d<=4",
    "o6_odd_semiprime|d<=4",
)


def load_parity_probe():
    """Load the winner-parity next-opening probe from its file path."""
    spec = importlib.util.spec_from_file_location("gwr_winner_parity_next_opening_probe", PARITY_PROBE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load gwr_winner_parity_next_opening_probe module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PARITY_PROBE = load_parity_probe()


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Identify the smallest extra deterministic hidden state that improves "
            "next-gap triad-return prediction beyond width/open matching."
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for JSON, CSV, and PNG artifacts.",
    )
    parser.add_argument(
        "--powers",
        type=int,
        nargs="+",
        default=list(DEFAULT_POWERS),
        help="Decade-anchor powers whose exact windows are probed.",
    )
    parser.add_argument(
        "--window-steps",
        type=int,
        default=DEFAULT_WINDOW_STEPS,
        help="Number of scored transitions sampled from each power anchor.",
    )
    return parser


def candidate_value(row: dict[str, object], candidate_id: str) -> str:
    """Return the candidate label for one transition row."""
    field_map = dict(CANDIDATE_SPECS)
    if candidate_id not in field_map:
        raise KeyError(f"unknown candidate id: {candidate_id}")
    fields = field_map[candidate_id]
    return "|".join(str(row[field]) for field in fields)


def current_to_next_rows(power: int, window_steps: int) -> list[dict[str, object]]:
    """Return transition rows with current, previous, and next context."""
    if window_steps < 1:
        raise ValueError("window_steps must be at least 1")

    rows = PARITY_PROBE.walk_rows_from(
        start_right_prime=PARITY_PROBE.start_prime_for_power(power),
        steps=window_steps + 2,
    )
    transitions: list[dict[str, object]] = []
    for index in range(1, window_steps + 1):
        previous_row = rows[index - 1]
        current_row = rows[index]
        next_row = rows[index + 1]
        transitions.append(
            {
                "power": power,
                "current_gap_width": int(current_row["next_gap_width"]),
                "current_first_open_offset": int(current_row["first_open_offset"]),
                "current_winner_offset": int(current_row["next_peak_offset"]),
                "current_winner_parity": str(current_row["winner_parity"]),
                "current_carrier_family": str(current_row["carrier_family"]),
                "current_d_bucket": PARITY_PROBE.d_bucket(int(current_row["next_dmin"])),
                "previous_reduced_state": str(previous_row["state"]),
                "previous_winner_parity": str(previous_row["winner_parity"]),
                "previous_carrier_family": str(previous_row["carrier_family"]),
                "next_state": str(next_row["state"]),
                "next_is_triad": int(str(next_row["state"]) in set(PARITY_PROBE.TRIAD_STATES)),
            }
        )
    return transitions


def log_loss_by_context(
    rows: list[dict[str, object]],
    candidate_id: str | None,
) -> tuple[float, dict[tuple[object, ...], float]]:
    """Return the mean smoothed log loss for one context definition."""
    counter: dict[tuple[object, ...], list[int]] = defaultdict(lambda: [0, 0])
    for row in rows:
        key = (row["current_gap_width"], row["current_first_open_offset"])
        if candidate_id is not None:
            key = (*key, candidate_value(row, candidate_id))
        counter[key][0] += int(row["next_is_triad"])
        counter[key][1] += 1

    probability_by_key: dict[tuple[object, ...], float] = {}
    for key, (positive_count, total_count) in counter.items():
        probability_by_key[key], _ = sigmoid_log_loss(positive_count, total_count)

    total_loss = 0.0
    for row in rows:
        key = (row["current_gap_width"], row["current_first_open_offset"])
        if candidate_id is not None:
            key = (*key, candidate_value(row, candidate_id))
        probability = probability_by_key[key]
        total_loss += -(
            math.log(probability) if int(row["next_is_triad"]) else math.log(1.0 - probability)
        )
    return total_loss / len(rows), probability_by_key


def label_distributions(
    rows: list[dict[str, object]],
    candidate_id: str,
) -> tuple[dict[str, float], dict[str, dict[str, float]], dict[str, int]]:
    """Return per-label triad shares, within-triad lane shares, and supports."""
    triad_hits = Counter()
    triad_totals = Counter()
    lane_counters: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        label = candidate_value(row, candidate_id)
        triad_totals[label] += 1
        triad_hits[label] += int(row["next_is_triad"])
        if int(row["next_is_triad"]):
            lane_counters[label][str(row["next_state"])] += 1

    triad_share = {
        label: triad_hits[label] / triad_totals[label]
        for label in sorted(triad_totals)
    }
    within_triad = {}
    for label in sorted(triad_totals):
        total = sum(lane_counters[label].values())
        if total == 0:
            within_triad[label] = {lane: 0.0 for lane in LANE_ORDER}
            continue
        within_triad[label] = {
            lane: lane_counters[label].get(lane, 0) / total
            for lane in LANE_ORDER
        }
    return triad_share, within_triad, {label: int(count) for label, count in triad_totals.items()}


def lane_shift_l1(
    left_distribution: dict[str, float],
    right_distribution: dict[str, float],
) -> float:
    """Return the L1 distance between two lane distributions."""
    return sum(abs(left_distribution[lane] - right_distribution[lane]) for lane in LANE_ORDER)


def evaluate_candidate(
    rows: list[dict[str, object]],
    candidate_id: str,
) -> dict[str, object]:
    """Score one candidate against the width/open baseline."""
    baseline_loss, _ = log_loss_by_context(rows, candidate_id=None)
    candidate_loss, _ = log_loss_by_context(rows, candidate_id=candidate_id)
    triad_share, within_triad, support = label_distributions(rows, candidate_id)
    observed_labels = sorted(triad_share)

    best_label = max(observed_labels, key=lambda label: (triad_share[label], support[label], label))
    worst_label = min(observed_labels, key=lambda label: (triad_share[label], -support[label], label))
    lane_shift = lane_shift_l1(within_triad[best_label], within_triad[worst_label])

    per_power_gain = {}
    for power in sorted({int(row["power"]) for row in rows}):
        power_rows = [row for row in rows if int(row["power"]) == power]
        power_baseline, _ = log_loss_by_context(power_rows, candidate_id=None)
        power_candidate, _ = log_loss_by_context(power_rows, candidate_id=candidate_id)
        per_power_gain[str(power)] = power_baseline - power_candidate

    return {
        "candidate_id": candidate_id,
        "primitive_count": len(dict(CANDIDATE_SPECS)[candidate_id]),
        "candidate_cardinality": len(observed_labels),
        "row_count": len(rows),
        "baseline_log_loss": baseline_loss,
        "candidate_log_loss": candidate_loss,
        "log_loss_gain": baseline_loss - candidate_loss,
        "matched_next_triad_lift": triad_share[best_label] - triad_share[worst_label],
        "within_triad_lane_l1_shift": lane_shift,
        "best_label": best_label,
        "worst_label": worst_label,
        "best_label_support": support[best_label],
        "worst_label_support": support[worst_label],
        "best_label_triad_share": triad_share[best_label],
        "worst_label_triad_share": triad_share[worst_label],
        "per_power_log_loss_gain": per_power_gain,
        "label_support": support,
        "label_triad_share": triad_share,
        "label_within_triad_lane_share": within_triad,
    }


def rank_candidates(candidate_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    """Return the candidates ordered by the relay selection rule."""
    return sorted(
        candidate_rows,
        key=lambda row: (
            -float(row["log_loss_gain"]),
            int(row["primitive_count"]),
            int(row["candidate_cardinality"]),
            -int(row["row_count"]),
            str(row["candidate_id"]),
        ),
    )


def write_candidates_csv(candidate_rows: list[dict[str, object]], csv_path: Path) -> None:
    """Write the candidate ranking table."""
    fieldnames = [
        "candidate_id",
        "primitive_count",
        "candidate_cardinality",
        "row_count",
        "baseline_log_loss",
        "candidate_log_loss",
        "log_loss_gain",
        "matched_next_triad_lift",
        "within_triad_lane_l1_shift",
        "best_label",
        "worst_label",
        "best_label_support",
        "worst_label_support",
        "best_label_triad_share",
        "worst_label_triad_share",
        "beats_parity_alone",
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
            lineterminator="\n",
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(candidate_rows)


def build_overview_plot(summary: dict[str, object], plot_path: Path) -> None:
    """Render one compact overview plot for the top candidate and parity."""
    best_candidate = summary["best_candidate"]
    parity_candidate = summary["parity_candidate"]
    powers = [f"10^{power}" for power in summary["powers"]]
    x_positions = list(range(len(powers)))

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    axes[0].bar(
        ["parity", best_candidate["candidate_id"]],
        [
            float(parity_candidate["log_loss_gain"]),
            float(best_candidate["log_loss_gain"]),
        ],
        color=["#999999", "#4c72b0"],
    )
    axes[0].set_ylabel("Log-loss gain over width/open baseline")
    axes[0].set_title("Best Hidden State vs Parity")

    axes[1].plot(
        x_positions,
        [float(parity_candidate["per_power_log_loss_gain"][str(power)]) for power in summary["powers"]],
        marker="o",
        color="#999999",
        label="parity",
    )
    axes[1].plot(
        x_positions,
        [float(best_candidate["per_power_log_loss_gain"][str(power)]) for power in summary["powers"]],
        marker="o",
        color="#4c72b0",
        label=best_candidate["candidate_id"],
    )
    axes[1].set_xticks(x_positions, powers)
    axes[1].set_ylabel("Per-power log-loss gain")
    axes[1].set_title("Per-Power Stability")
    axes[1].legend(frameon=False)

    fig.tight_layout()
    fig.savefig(plot_path, dpi=220)
    plt.close(fig)


def findings_markdown(summary: dict[str, object]) -> str:
    """Render the findings note for the hidden-state miner."""
    best_candidate = summary["best_candidate"]
    parity_candidate = summary["parity_candidate"]
    genuine_hidden_state = (
        bool(summary["beats_parity_alone"])
        and "carrier_family" not in str(best_candidate["candidate_id"])
    )
    opening = (
        f"The strongest hidden-state candidate on the current `10^12..10^15` surface is "
        f"`{best_candidate['candidate_id']}`, which improves matched next-gap triad-return "
        f"log loss by `{best_candidate['log_loss_gain']:.6f}` over the width/open baseline."
    )
    if summary["beats_parity_alone"]:
        opening += (
            f" It beats parity alone by `{best_candidate['log_loss_gain'] - parity_candidate['log_loss_gain']:.6f}`."
        )
    else:
        opening += " It does not beat parity alone."

    interpretation = (
        "This looks like a genuinely new hidden state."
        if genuine_hidden_state
        else "This currently looks more like a restatement of already-visible family structure than a new hidden state."
    )

    lines = [
        "# Hidden-State Miner Findings",
        "",
        opening,
        "",
        interpretation,
        "",
        "## Current Winner",
        "",
        f"- best candidate: `{best_candidate['candidate_id']}`",
        f"- primitive count: `{best_candidate['primitive_count']}`",
        f"- candidate cardinality: `{best_candidate['candidate_cardinality']}`",
        f"- matched next-triad lift: `{best_candidate['matched_next_triad_lift']:.4f}`",
        f"- within-triad lane L1 shift: `{best_candidate['within_triad_lane_l1_shift']:.4f}`",
        f"- best label: `{best_candidate['best_label']}` with triad share `{best_candidate['best_label_triad_share']:.4f}`",
        f"- worst label: `{best_candidate['worst_label']}` with triad share `{best_candidate['worst_label_triad_share']:.4f}`",
        "",
        "## Parity Baseline",
        "",
        f"- parity log-loss gain: `{parity_candidate['log_loss_gain']:.6f}`",
        f"- parity matched next-triad lift: `{parity_candidate['matched_next_triad_lift']:.4f}`",
        "",
        "## Per-Power Gains",
        "",
    ]
    for power in summary["powers"]:
        lines.append(
            f"- `10^{power}`: `{best_candidate['per_power_log_loss_gain'][str(power)]:.6f}`"
        )
    lines.extend(
        [
            "",
            "## Reading",
            "",
            "The main question after this run is whether the best candidate survives once current winner offset is added as a direct control inside the parity probe itself, rather than only as a hidden-state label.",
            "",
            "## Artifacts",
            "",
            "- [hidden-state miner script](../../benchmarks/python/predictor/gwr_hidden_state_miner.py)",
            "- [summary JSON](../../output/gwr_hidden_state_miner_summary.json)",
            "- [candidate CSV](../../output/gwr_hidden_state_miner_candidates.csv)",
            "- [history JSONL](../../output/gwr_hidden_state_miner_history.jsonl)",
            "- ![Hidden-state miner overview](../../output/gwr_hidden_state_miner_overview.png)",
        ]
    )
    return "\n".join(lines) + "\n"


def summarize(
    powers: list[int],
    window_steps: int,
    parity_probe_source_commit: str,
) -> dict[str, object]:
    """Build the hidden-state miner summary on the current parity-probe surface."""
    rows: list[dict[str, object]] = []
    for power in powers:
        rows.extend(current_to_next_rows(power, window_steps))

    candidate_rows = [
        evaluate_candidate(rows, candidate_id)
        for candidate_id, _ in CANDIDATE_SPECS
    ]
    ranked_rows = rank_candidates(candidate_rows)
    parity_candidate = next(row for row in candidate_rows if row["candidate_id"] == "current_winner_parity")
    for row in ranked_rows:
        row["beats_parity_alone"] = bool(float(row["log_loss_gain"]) > float(parity_candidate["log_loss_gain"]) + 1e-12)

    best_candidate = ranked_rows[0]
    return {
        "powers": powers,
        "window_steps": window_steps,
        "parity_probe_source_commit": parity_probe_source_commit,
        "candidate_count": len(candidate_rows),
        "baseline_files": {
            "parity_summary_json": str(PARITY_SUMMARY_PATH.relative_to(ROOT)),
            "parity_findings_markdown": str(PARITY_FINDINGS_PATH.relative_to(ROOT)),
        },
        "parity_candidate": parity_candidate,
        "best_candidate": best_candidate,
        "beats_parity_alone": bool(best_candidate["beats_parity_alone"]),
        "candidate_rankings": ranked_rows,
    }


def run_targeted_pytest() -> None:
    """Run the targeted hidden-state miner test file."""
    subprocess.run(
        ["python3", "-m", "pytest", "-q", str(TEST_PATH.relative_to(ROOT))],
        check=True,
        cwd=ROOT,
        text=True,
    )


def main(argv: list[str] | None = None) -> int:
    """Run one full hourly hidden-state miner task."""
    args = build_parser().parse_args(argv)
    started = time.perf_counter()
    compact_timestamp = utc_timestamp_compact()
    previous_history_row = read_last_jsonl_row(HISTORY_PATH)
    starting_head, current_head = prepare_task_branch(
        branch_name=TASK_BRANCH,
        first_launch_base_branch=FIRST_LAUNCH_BASE_BRANCH,
    )
    _ = current_head
    if not PARITY_SUMMARY_PATH.exists() or not PARITY_FINDINGS_PATH.exists():
        raise FileNotFoundError("parity baseline artifacts are missing on the task branch")
    parity_probe_source_commit = run_git("rev-parse", PARITY_PROBE_REMOTE_BRANCH)
    summary = summarize(
        powers=list(args.powers),
        window_steps=args.window_steps,
        parity_probe_source_commit=parity_probe_source_commit,
    )
    summary["history_seed_present"] = previous_history_row is not None
    summary["runtime_seconds"] = time.perf_counter() - started
    write_json(SUMMARY_PATH, summary)
    write_candidates_csv(summary["candidate_rankings"], CANDIDATES_CSV_PATH)
    build_overview_plot(summary, PLOT_PATH)
    FINDINGS_PATH.write_text(findings_markdown(summary), encoding="utf-8")

    history_row = {
        "run_timestamp_utc": utc_timestamp_iso(),
        "branch": TASK_BRANCH,
        "head_commit": starting_head,
        "parity_probe_source_commit": parity_probe_source_commit,
        "window_steps": int(args.window_steps),
        "candidate_count": int(summary["candidate_count"]),
        "best_candidate_id": str(summary["best_candidate"]["candidate_id"]),
        "best_log_loss_gain": float(summary["best_candidate"]["log_loss_gain"]),
        "best_matched_lift": float(summary["best_candidate"]["matched_next_triad_lift"]),
        "beats_parity_alone": bool(summary["beats_parity_alone"]),
        "blocked_reason": None,
    }
    append_jsonl_row(HISTORY_PATH, history_row)
    run_targeted_pytest()
    run_git("checkout", TASK_BRANCH)
    current_branch = run_git("branch", "--show-current")
    if current_branch != TASK_BRANCH:
        raise RuntimeError(f"hidden-state miner expected branch `{TASK_BRANCH}`, but is on `{current_branch}`")
    stage_commit_push(
        branch_name=TASK_BRANCH,
        artifact_paths=[
            Path(__file__),
            TEST_PATH,
            SUMMARY_PATH,
            CANDIDATES_CSV_PATH,
            HISTORY_PATH,
            PLOT_PATH,
            FINDINGS_PATH,
        ],
        commit_message=f"hidden-state-miner: {compact_timestamp}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
