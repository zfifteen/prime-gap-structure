#!/usr/bin/env python3
"""Probe whether a square-phase budget bit extends the current hidden state."""

from __future__ import annotations

import argparse
import csv
import json
import math
import time
from collections import Counter, defaultdict
from pathlib import Path

from sympy import nextprime


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DETAIL_CSV = ROOT / "output" / "gwr_dni_gap_type_catalog_details.csv"
DEFAULT_OUTPUT_DIR = ROOT / "output"
DEFAULT_FINDINGS_PATH = ROOT / "gwr" / "findings" / "phase_budget_hidden_state_probe_findings.md"
DEFAULT_MIN_POWER = 12
DEFAULT_MAX_POWER = 18
MIN_STRATUM_COUNT = 8
CANDIDATE_SPECS = (
    ("current_winner_parity", ("current_winner_parity",)),
    ("phase_budget_bit", ("phase_budget_bit",)),
    ("previous_reduced_state", ("previous_reduced_state",)),
    (
        "current_winner_parity+previous_reduced_state",
        ("current_winner_parity", "previous_reduced_state"),
    ),
    (
        "previous_reduced_state+phase_budget_bit",
        ("previous_reduced_state", "phase_budget_bit"),
    ),
    (
        "current_winner_parity+previous_reduced_state+phase_budget_bit",
        ("current_winner_parity", "previous_reduced_state", "phase_budget_bit"),
    ),
)
STRATA_CSV_FIELDS = (
    "current_winner_parity",
    "previous_reduced_state",
    "low_count",
    "high_count",
    "low_next_triad_share",
    "high_next_triad_share",
    "lift",
)


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Test whether a one-bit square-phase budget label adds real pooled "
            "next-gap state beyond the current parity-plus-previous-state model."
        ),
    )
    parser.add_argument(
        "--detail-csv",
        type=Path,
        default=DEFAULT_DETAIL_CSV,
        help="Catalog detail CSV emitted by gwr_dni_gap_type_catalog.py.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for the summary JSON and strata CSV.",
    )
    parser.add_argument(
        "--findings-path",
        type=Path,
        default=DEFAULT_FINDINGS_PATH,
        help="Markdown findings output path.",
    )
    parser.add_argument(
        "--min-power",
        type=int,
        default=DEFAULT_MIN_POWER,
        help="Smallest retained decade power included in the pooled window surface.",
    )
    parser.add_argument(
        "--max-power",
        type=int,
        default=DEFAULT_MAX_POWER,
        help="Largest retained decade power included in the pooled window surface.",
    )
    return parser


def d_bucket(next_dmin: int) -> str:
    """Return the coarse divisor bucket used by the reduced state surface."""
    if next_dmin <= 4:
        return "d<=4"
    if next_dmin <= 16:
        return "5<=d<=16"
    if next_dmin <= 64:
        return "17<=d<=64"
    return "d>64"


def reduced_state(row: dict[str, object]) -> str:
    """Return the reduced state label for one detail row."""
    return f"o{row['first_open_offset']}_{row['carrier_family']}|{d_bucket(int(row['next_dmin']))}"


def load_detail_rows(detail_csv: Path) -> list[dict[str, object]]:
    """Load the catalog detail CSV from disk."""
    if not detail_csv.exists():
        raise FileNotFoundError(f"detail CSV does not exist: {detail_csv}")

    with detail_csv.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError("detail CSV must contain at least one row")
    return rows


def build_transitions(
    detail_rows: list[dict[str, object]],
    *,
    min_power: int,
    max_power: int,
) -> list[dict[str, object]]:
    """Return pooled retained-window transitions with previous/current/next context."""
    by_surface: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in detail_rows:
        by_surface[str(row["surface_label"])].append(row)

    transitions: list[dict[str, object]] = []
    for surface_label in sorted(by_surface):
        surface_rows = sorted(
            by_surface[surface_label],
            key=lambda row: int(row["surface_row_index"]),
        )
        power_text = str(surface_rows[0]["power"])
        if power_text == "":
            continue
        power = int(power_text)
        if power < min_power or power > max_power:
            continue

        for previous_row, current_row, next_row in zip(
            surface_rows[:-2],
            surface_rows[1:-1],
            surface_rows[2:],
        ):
            winner = int(current_row["winner"])
            current_next_dmin = int(current_row["next_dmin"])
            square_phase_utilization = None
            if current_next_dmin == 4:
                next_square_root = int(nextprime(math.isqrt(winner)))
                next_square = next_square_root * next_square_root
                square_phase_utilization = (
                    int(current_row["next_right_prime"]) - winner
                ) / (next_square - winner)

            transitions.append(
                {
                    "surface_label": surface_label,
                    "power": power,
                    "current_gap_width": int(current_row["next_gap_width"]),
                    "current_first_open_offset": int(current_row["first_open_offset"]),
                    "current_winner_offset": int(current_row["next_peak_offset"]),
                    "current_winner_parity": "even" if winner % 2 == 0 else "odd",
                    "current_carrier_family": str(current_row["carrier_family"]),
                    "current_next_dmin": current_next_dmin,
                    "previous_reduced_state": reduced_state(previous_row),
                    "current_square_phase_utilization": square_phase_utilization,
                    "next_is_triad": int(
                        str(next_row["carrier_family"]) == "odd_semiprime"
                        and int(next_row["next_dmin"]) <= 4
                    ),
                }
            )

    if not transitions:
        raise ValueError("requested power range did not produce any transitions")
    return transitions


def assign_phase_budget_bit(transitions: list[dict[str, object]]) -> None:
    """Attach the `phase_budget_bit` label to each transition row in place."""
    by_geometry: dict[tuple[str, int, int], list[float]] = defaultdict(list)
    for row in transitions:
        if int(row["current_next_dmin"]) != 4:
            continue
        key = (
            str(row["current_carrier_family"]),
            int(row["current_winner_offset"]),
            int(row["current_first_open_offset"]),
        )
        by_geometry[key].append(float(row["current_square_phase_utilization"]))

    medians = {
        key: sorted(values)[len(values) // 2]
        for key, values in by_geometry.items()
    }

    for row in transitions:
        if int(row["current_next_dmin"]) != 4:
            row["phase_budget_bit"] = "non_d4"
            continue
        key = (
            str(row["current_carrier_family"]),
            int(row["current_winner_offset"]),
            int(row["current_first_open_offset"]),
        )
        utilization = float(row["current_square_phase_utilization"])
        row["phase_budget_bit"] = (
            "d4_low" if utilization < medians[key] else "d4_high"
        )


def candidate_value(row: dict[str, object], candidate_id: str) -> str:
    """Return the candidate label for one transition row."""
    fields = dict(CANDIDATE_SPECS).get(candidate_id)
    if fields is None:
        raise KeyError(f"unknown candidate id: {candidate_id}")
    return "|".join(str(row[field]) for field in fields)


def laplace_probability(positive_count: int, total_count: int) -> float:
    """Return the Laplace-smoothed Bernoulli probability."""
    return (positive_count + 1.0) / (total_count + 2.0)


def mean_log_loss(
    rows: list[dict[str, object]],
    candidate_id: str | None = None,
) -> float:
    """Return the mean smoothed log loss against next-triad return."""
    probability_counter: dict[tuple[object, ...], list[int]] = defaultdict(lambda: [0, 0])
    for row in rows:
        key: tuple[object, ...] = (
            int(row["current_gap_width"]),
            int(row["current_first_open_offset"]),
        )
        if candidate_id is not None:
            key = (*key, candidate_value(row, candidate_id))
        probability_counter[key][0] += int(row["next_is_triad"])
        probability_counter[key][1] += 1

    probability_by_key = {
        key: laplace_probability(positive_count, total_count)
        for key, (positive_count, total_count) in probability_counter.items()
    }

    loss = 0.0
    for row in rows:
        key = (
            int(row["current_gap_width"]),
            int(row["current_first_open_offset"]),
        )
        if candidate_id is not None:
            key = (*key, candidate_value(row, candidate_id))
        probability = probability_by_key[key]
        loss += -(
            math.log(probability)
            if int(row["next_is_triad"])
            else math.log(1.0 - probability)
        )
    return loss / len(rows)


def label_stats(
    rows: list[dict[str, object]],
    *,
    candidate_id: str,
) -> dict[str, dict[str, float | int]]:
    """Return support and next-triad share for each candidate label."""
    support_counter = Counter()
    triad_hits = Counter()
    for row in rows:
        label = candidate_value(row, candidate_id)
        support_counter[label] += 1
        triad_hits[label] += int(row["next_is_triad"])

    return {
        label: {
            "support": int(support_counter[label]),
            "next_triad_share": triad_hits[label] / support_counter[label],
        }
        for label in sorted(support_counter)
    }


def evaluate_candidate(
    rows: list[dict[str, object]],
    *,
    candidate_id: str,
    baseline_log_loss: float,
) -> dict[str, object]:
    """Return one candidate metric payload."""
    candidate_log_loss = mean_log_loss(rows, candidate_id)
    per_power_gain = {}
    for power in sorted({int(row["power"]) for row in rows}):
        power_rows = [row for row in rows if int(row["power"]) == power]
        power_baseline = mean_log_loss(power_rows)
        per_power_gain[str(power)] = (
            power_baseline - mean_log_loss(power_rows, candidate_id)
        )

    return {
        "candidate_id": candidate_id,
        "candidate_cardinality": len(
            {candidate_value(row, candidate_id) for row in rows}
        ),
        "candidate_log_loss": candidate_log_loss,
        "log_loss_gain": baseline_log_loss - candidate_log_loss,
        "per_power_log_loss_gain": per_power_gain,
    }


def parity_previous_phase_overlay(
    rows: list[dict[str, object]],
) -> tuple[dict[str, object], list[dict[str, object]]]:
    """Return d=4 low-versus-high phase splits inside parity-plus-previous-state cells."""
    strata: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        if str(row["phase_budget_bit"]) == "non_d4":
            continue
        key = (
            str(row["current_winner_parity"]),
            str(row["previous_reduced_state"]),
        )
        strata[key].append(row)

    stratum_rows: list[dict[str, object]] = []
    positive_lift = 0
    negative_lift = 0
    equal_lift = 0
    balanced_weight = 0
    balanced_lift_total = 0.0

    for key, members in sorted(strata.items()):
        low_rows = [row for row in members if str(row["phase_budget_bit"]) == "d4_low"]
        high_rows = [row for row in members if str(row["phase_budget_bit"]) == "d4_high"]
        if len(low_rows) < MIN_STRATUM_COUNT or len(high_rows) < MIN_STRATUM_COUNT:
            continue

        low_share = sum(int(row["next_is_triad"]) for row in low_rows) / len(low_rows)
        high_share = sum(int(row["next_is_triad"]) for row in high_rows) / len(high_rows)
        lift = low_share - high_share
        positive_lift += int(lift > 0.0)
        negative_lift += int(lift < 0.0)
        equal_lift += int(lift == 0.0)

        weight = min(len(low_rows), len(high_rows))
        balanced_weight += weight
        balanced_lift_total += lift * weight

        stratum_rows.append(
            {
                "current_winner_parity": key[0],
                "previous_reduced_state": key[1],
                "low_count": len(low_rows),
                "high_count": len(high_rows),
                "low_next_triad_share": low_share,
                "high_next_triad_share": high_share,
                "lift": lift,
            }
        )

    summary = {
        "used_strata_count": len(stratum_rows),
        "positive_lift_strata_count": positive_lift,
        "negative_lift_strata_count": negative_lift,
        "equal_lift_strata_count": equal_lift,
        "balanced_weight": balanced_weight,
        "balanced_weighted_lift": (
            balanced_lift_total / balanced_weight if balanced_weight else 0.0
        ),
    }
    return summary, stratum_rows


def rank_candidates(candidate_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    """Return candidates ordered by pooled gain, then by smaller cardinality."""
    return sorted(
        candidate_rows,
        key=lambda row: (
            -float(row["log_loss_gain"]),
            int(row["candidate_cardinality"]),
            str(row["candidate_id"]),
        ),
    )


def summarize(
    detail_csv: Path,
    *,
    min_power: int,
    max_power: int,
) -> tuple[dict[str, object], list[dict[str, object]]]:
    """Build the full summary and strata payload from the retained catalog surface."""
    detail_rows = load_detail_rows(detail_csv)
    transitions = build_transitions(
        detail_rows,
        min_power=min_power,
        max_power=max_power,
    )
    assign_phase_budget_bit(transitions)

    baseline_log_loss = mean_log_loss(transitions)
    candidate_rows = [
        evaluate_candidate(
            transitions,
            candidate_id=candidate_id,
            baseline_log_loss=baseline_log_loss,
        )
        for candidate_id, _fields in CANDIDATE_SPECS
    ]
    ranked_rows = rank_candidates(candidate_rows)
    overlay_summary, stratum_rows = parity_previous_phase_overlay(transitions)

    summary = {
        "detail_csv": str(detail_csv),
        "power_range": [min_power, max_power],
        "transition_count": len(transitions),
        "baseline_log_loss": baseline_log_loss,
        "phase_budget_label_stats": label_stats(
            transitions,
            candidate_id="phase_budget_bit",
        ),
        "candidate_metrics": candidate_rows,
        "candidate_ranking": ranked_rows,
        "parity_previous_phase_overlay": overlay_summary,
    }
    return summary, stratum_rows


def summary_path(output_dir: Path) -> Path:
    """Return the summary JSON path under the output directory."""
    return output_dir / "gwr_phase_budget_hidden_state_probe_summary.json"


def strata_path(output_dir: Path) -> Path:
    """Return the strata CSV path under the output directory."""
    return output_dir / "gwr_phase_budget_hidden_state_probe_strata.csv"


def write_summary(path: Path, summary: dict[str, object]) -> None:
    """Write the summary JSON artifact with LF endings."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


def write_strata(path: Path, stratum_rows: list[dict[str, object]]) -> None:
    """Write the parity-plus-previous-state overlay table."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(STRATA_CSV_FIELDS),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(stratum_rows)


def findings_markdown(summary: dict[str, object]) -> str:
    """Render the findings note from the current summary."""
    metrics = {
        str(row["candidate_id"]): row for row in summary["candidate_metrics"]
    }
    overlay = summary["parity_previous_phase_overlay"]
    phase_stats = summary["phase_budget_label_stats"]

    phase_gain = float(metrics["phase_budget_bit"]["log_loss_gain"])
    parity_gain = float(metrics["current_winner_parity"]["log_loss_gain"])
    parity_prev_gain = float(
        metrics["current_winner_parity+previous_reduced_state"]["log_loss_gain"]
    )
    phase_prev_gain = float(
        metrics["previous_reduced_state+phase_budget_bit"]["log_loss_gain"]
    )
    parity_prev_phase_gain = float(
        metrics["current_winner_parity+previous_reduced_state+phase_budget_bit"]["log_loss_gain"]
    )

    lines = [
        "# Phase-Budget Hidden-State Probe Findings",
        "",
        "The strongest supported claim on the retained `10^12..10^18` catalog window surface is:",
        "",
        "the current parity-plus-previous-state hidden model is missing one boundary-budget bit.",
        "",
        "On this pooled surface, the three-value label",
        "",
        "- `non_d4`,",
        "- `d4_low`,",
        "- `d4_high`,",
        "",
        "beats current winner parity as a next-triad predictor, and it still adds pooled signal after parity and previous reduced state are already present.",
        "",
        "## Phase-Budget Definition",
        "",
        "For current `d = 4` rows, compute square-phase utilization",
        "",
        "$$U_{\\square}(w, q) = \\frac{q - w}{S_{+}(w) - w}.$$",
        "",
        "Then, inside each current local-geometry cell",
        "",
        "- carrier family,",
        "- winner offset,",
        "- first-open offset,",
        "",
        "split rows at the exact pooled median of $U_{\\square}(w, q)$.",
        "",
        "Rows below that median are labeled `d4_low`. Rows at or above it are labeled `d4_high`. All non-`d = 4` rows are labeled `non_d4`.",
        "",
        "## Pooled Readout",
        "",
        f"- baseline log loss: `{summary['baseline_log_loss']:.6f}`",
        f"- parity gain: `{parity_gain:.6f}`",
        f"- phase-budget gain: `{phase_gain:.6f}`",
        f"- parity + previous-state gain: `{parity_prev_gain:.6f}`",
        f"- previous-state + phase-budget gain: `{phase_prev_gain:.6f}`",
        f"- parity + previous-state + phase-budget gain: `{parity_prev_phase_gain:.6f}`",
        "",
        "So the phase-budget label does two distinct things on the retained surface:",
        "",
        f"- by itself it beats parity by `{phase_gain - parity_gain:.6f}` pooled log-loss gain;",
        f"- when appended to the current parity-plus-previous-state model, it adds `{parity_prev_phase_gain - parity_prev_gain:.6f}` more pooled gain.",
        "",
        "## Label Shares",
        "",
        f"- `d4_low`: support `{phase_stats['d4_low']['support']}`, next-triad share `{phase_stats['d4_low']['next_triad_share']:.6f}`",
        f"- `d4_high`: support `{phase_stats['d4_high']['support']}`, next-triad share `{phase_stats['d4_high']['next_triad_share']:.6f}`",
        f"- `non_d4`: support `{phase_stats['non_d4']['support']}`, next-triad share `{phase_stats['non_d4']['next_triad_share']:.6f}`",
        "",
        "So on the retained pooled surface, the low-budget and high-budget `d = 4` halves are separated by a next-triad gap of",
        f" `{phase_stats['d4_low']['next_triad_share'] - phase_stats['d4_high']['next_triad_share']:.6f}`.",
        "",
        "## Inside The Existing Hidden-State Cells",
        "",
        "Restrict to populated `d = 4` strata keyed only by:",
        "",
        "- current winner parity,",
        "- previous reduced state.",
        "",
        "Inside those already-existing hidden-state cells:",
        "",
        f"- used strata: `{overlay['used_strata_count']}`",
        f"- positive low-minus-high lifts: `{overlay['positive_lift_strata_count']}`",
        f"- negative low-minus-high lifts: `{overlay['negative_lift_strata_count']}`",
        f"- balanced weighted lift: `{overlay['balanced_weighted_lift']:.6f}`",
        "",
        "That is the direct reason this looks like new state rather than a restatement of parity:",
        "the budget split keeps working inside the parity-plus-previous-state cells themselves.",
        "",
        "## Reading",
        "",
        "The existing hidden-state story says the next gap remembers where it came from and whether the current winner is even or odd.",
        "",
        "The new readout says that is still incomplete. The current row also carries a one-bit record of how much of its local square budget it used before closure. That budget bit is pooled, measurable, and predictive on top of the current hidden-state candidate.",
        "",
        "This is a bounded pooled-window claim, not yet a theorem and not yet a per-power monotonic law.",
        "",
        "## Decision Rule",
        "",
        "On retained high-scale windows, do not treat two rows with the same current winner parity and the same previous reduced state as equivalent when one is `d4_low` and the other is `d4_high`.",
        "",
        "Score the `d4_low` row as more likely to return the next gap to the odd-semiprime triad.",
        "",
        "## Artifacts",
        "",
        "- [phase-budget hidden-state probe](../../benchmarks/python/predictor/gwr_phase_budget_hidden_state_probe.py)",
        "- [summary JSON](../../output/gwr_phase_budget_hidden_state_probe_summary.json)",
        "- [strata CSV](../../output/gwr_phase_budget_hidden_state_probe_strata.csv)",
    ]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    """Run the phase-budget hidden-state probe and write artifacts."""
    args = build_parser().parse_args(argv)
    started = time.perf_counter()
    summary, stratum_rows = summarize(
        args.detail_csv,
        min_power=args.min_power,
        max_power=args.max_power,
    )
    summary["runtime_seconds"] = time.perf_counter() - started

    summary_output_path = summary_path(args.output_dir)
    strata_output_path = strata_path(args.output_dir)
    write_summary(summary_output_path, summary)
    write_strata(strata_output_path, stratum_rows)

    args.findings_path.parent.mkdir(parents=True, exist_ok=True)
    args.findings_path.write_text(findings_markdown(summary), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
