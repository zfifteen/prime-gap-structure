#!/usr/bin/env python3
"""Probe whether current winner parity steers the next-gap triad lane."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import time
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sympy import nextprime


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT_DIR = ROOT / "output"
DEFAULT_POWERS = (12, 13, 14, 15)
DEFAULT_WINDOW_STEPS = 2048
GAP_TYPE_PROBE_PATH = Path(__file__).with_name("gwr_dni_gap_type_probe.py")
TRIAD_STATES = (
    "o2_odd_semiprime|d<=4",
    "o4_odd_semiprime|d<=4",
    "o6_odd_semiprime|d<=4",
)
LANE_ORDER = TRIAD_STATES
LANE_COLORS = {
    "o2_odd_semiprime|d<=4": "#dd8452",
    "o4_odd_semiprime|d<=4": "#4c72b0",
    "o6_odd_semiprime|d<=4": "#55a868",
}


def load_gap_type_probe():
    """Load the exact gap-type probe from its sibling file."""
    spec = importlib.util.spec_from_file_location("gwr_dni_gap_type_probe", GAP_TYPE_PROBE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load gwr_dni_gap_type_probe module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


GAP_TYPE_PROBE = load_gap_type_probe()


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Compare next-gap triad-lane shares after even versus odd current "
            "winners, matched on current gap width and first-open offset."
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
        help="Decade-anchor powers whose consecutive windows are probed.",
    )
    parser.add_argument(
        "--window-steps",
        type=int,
        default=DEFAULT_WINDOW_STEPS,
        help="Number of consecutive transitions sampled from each power anchor.",
    )
    return parser


def d_bucket(next_dmin: int) -> str:
    """Return the coarse divisor bucket used by the reduced grammar."""
    if next_dmin <= 4:
        return "d<=4"
    if next_dmin <= 16:
        return "5<=d<=16"
    if next_dmin <= 64:
        return "17<=d<=64"
    return "d>64"


def reduced_state(row: dict[str, object]) -> str:
    """Return the reduced-state label for one exact winner row."""
    return f"o{row['first_open_offset']}_{row['carrier_family']}|{d_bucket(int(row['next_dmin']))}"


def start_prime_for_power(power: int) -> int:
    """Return the first prime at or above one decade anchor."""
    if power < 1:
        raise ValueError("power must be at least 1")
    return int(nextprime(10**power - 1))


def walk_rows_from(start_right_prime: int, steps: int) -> list[dict[str, object]]:
    """Return one consecutive typed prime-gap walk."""
    if steps < 1:
        raise ValueError("steps must be at least 1")

    rows: list[dict[str, object]] = []
    current_right_prime = int(start_right_prime)
    for gap_index in range(steps):
        row = dict(GAP_TYPE_PROBE.gap_type_row(current_right_prime, gap_index=gap_index + 1))
        row["state"] = reduced_state(row)
        row["winner_parity"] = "even" if int(row["winner"]) % 2 == 0 else "odd"
        rows.append(row)
        current_right_prime = int(row["next_right_prime"])
    return rows


def current_to_next_transitions(power: int, window_steps: int) -> list[dict[str, object]]:
    """Return flattened current-to-next transition rows for one power anchor."""
    start_right_prime = start_prime_for_power(power)
    rows = walk_rows_from(start_right_prime, window_steps + 1)

    transitions: list[dict[str, object]] = []
    for index in range(window_steps):
        current_row = rows[index]
        next_row = rows[index + 1]
        transitions.append(
            {
                "power": power,
                "current_right_prime": int(current_row["current_right_prime"]),
                "current_gap_width": int(current_row["next_gap_width"]),
                "current_first_open_offset": int(current_row["first_open_offset"]),
                "current_next_dmin": int(current_row["next_dmin"]),
                "current_winner": int(current_row["winner"]),
                "current_winner_parity": str(current_row["winner_parity"]),
                "current_carrier_family": str(current_row["carrier_family"]),
                "next_right_prime": int(current_row["next_right_prime"]),
                "next_state": str(next_row["state"]),
                "next_lane": str(next_row["state"]) if str(next_row["state"]) in TRIAD_STATES else "non_triad",
                "next_is_triad": int(str(next_row["state"]) in TRIAD_STATES),
            }
        )
    return transitions


def share_by_lane(counter: Counter[str], total: float) -> dict[str, float]:
    """Return one stable lane-share payload."""
    if total <= 0:
        return {lane: 0.0 for lane in LANE_ORDER}
    return {lane: counter.get(lane, 0.0) / total for lane in LANE_ORDER}


def share_difference_payload(
    even_shares: dict[str, float],
    odd_shares: dict[str, float],
) -> dict[str, float]:
    """Return the even-minus-odd share differences in stable lane order."""
    return {lane: even_shares[lane] - odd_shares[lane] for lane in LANE_ORDER}


def matched_lane_metrics(transitions: list[dict[str, object]]) -> dict[str, object]:
    """Return matched-stratum lane metrics for one transition surface."""
    parity_count = Counter(str(row["current_winner_parity"]) for row in transitions)
    next_triad_count = Counter()
    next_lane_by_parity = {"even": Counter(), "odd": Counter()}
    next_triad_lane_by_parity = {"even": Counter(), "odd": Counter()}
    strata: dict[tuple[int, int], dict[str, list[dict[str, object]]]] = defaultdict(
        lambda: {"even": [], "odd": []}
    )

    for row in transitions:
        parity = str(row["current_winner_parity"])
        next_triad_count[parity] += int(row["next_is_triad"])
        lane = str(row["next_lane"])
        next_lane_by_parity[parity][lane] += 1
        if lane in TRIAD_STATES:
            next_triad_lane_by_parity[parity][lane] += 1
        key = (int(row["current_gap_width"]), int(row["current_first_open_offset"]))
        strata[key][parity].append(row)

    matched_lane_weighted = {"even": Counter(), "odd": Counter()}
    matched_triad_lane_weighted = {"even": Counter(), "odd": Counter()}
    matched_triads = {"even": 0.0, "odd": 0.0}
    matched_totals = {"even": 0.0, "odd": 0.0}
    stratum_rows: list[dict[str, object]] = []

    for (gap_width, first_open_offset), parity_rows in sorted(strata.items()):
        even_rows = parity_rows["even"]
        odd_rows = parity_rows["odd"]
        even_count = len(even_rows)
        odd_count = len(odd_rows)
        overlap = min(even_count, odd_count)
        if overlap == 0:
            continue

        even_lane_counter = Counter(str(row["next_lane"]) for row in even_rows)
        odd_lane_counter = Counter(str(row["next_lane"]) for row in odd_rows)
        even_triad_lane_counter = Counter(
            str(row["next_lane"]) for row in even_rows if str(row["next_lane"]) in TRIAD_STATES
        )
        odd_triad_lane_counter = Counter(
            str(row["next_lane"]) for row in odd_rows if str(row["next_lane"]) in TRIAD_STATES
        )

        even_triad_share = sum(even_triad_lane_counter.values()) / even_count
        odd_triad_share = sum(odd_triad_lane_counter.values()) / odd_count

        matched_totals["even"] += overlap
        matched_totals["odd"] += overlap
        matched_triads["even"] += overlap * even_triad_share
        matched_triads["odd"] += overlap * odd_triad_share

        for lane, count in even_lane_counter.items():
            matched_lane_weighted["even"][lane] += overlap * count / even_count
        for lane, count in odd_lane_counter.items():
            matched_lane_weighted["odd"][lane] += overlap * count / odd_count

        even_triad_total = sum(even_triad_lane_counter.values())
        odd_triad_total = sum(odd_triad_lane_counter.values())
        if even_triad_total > 0 and odd_triad_total > 0:
            for lane, count in even_triad_lane_counter.items():
                matched_triad_lane_weighted["even"][lane] += overlap * count / even_triad_total
            for lane, count in odd_triad_lane_counter.items():
                matched_triad_lane_weighted["odd"][lane] += overlap * count / odd_triad_total

        stratum_rows.append(
            {
                "gap_width": gap_width,
                "first_open_offset": first_open_offset,
                "even_count": even_count,
                "odd_count": odd_count,
                "matched_weight": overlap,
                "even_next_triad_share": even_triad_share,
                "odd_next_triad_share": odd_triad_share,
                "even_minus_odd_next_triad_share": even_triad_share - odd_triad_share,
                "even_o2_share": even_lane_counter.get("o2_odd_semiprime|d<=4", 0) / even_count,
                "odd_o2_share": odd_lane_counter.get("o2_odd_semiprime|d<=4", 0) / odd_count,
                "even_o4_share": even_lane_counter.get("o4_odd_semiprime|d<=4", 0) / even_count,
                "odd_o4_share": odd_lane_counter.get("o4_odd_semiprime|d<=4", 0) / odd_count,
                "even_o6_share": even_lane_counter.get("o6_odd_semiprime|d<=4", 0) / even_count,
                "odd_o6_share": odd_lane_counter.get("o6_odd_semiprime|d<=4", 0) / odd_count,
            }
        )

    matched_even_lane_shares = share_by_lane(matched_lane_weighted["even"], matched_totals["even"])
    matched_odd_lane_shares = share_by_lane(matched_lane_weighted["odd"], matched_totals["odd"])
    matched_even_lane_within_triad = share_by_lane(
        matched_triad_lane_weighted["even"],
        sum(matched_triad_lane_weighted["even"].values()),
    )
    matched_odd_lane_within_triad = share_by_lane(
        matched_triad_lane_weighted["odd"],
        sum(matched_triad_lane_weighted["odd"].values()),
    )

    unmatched_even_lane_shares = share_by_lane(next_lane_by_parity["even"], parity_count["even"])
    unmatched_odd_lane_shares = share_by_lane(next_lane_by_parity["odd"], parity_count["odd"])

    return {
        "transition_count": len(transitions),
        "even_count": int(parity_count["even"]),
        "odd_count": int(parity_count["odd"]),
        "unmatched_next_triad_share": {
            "even": next_triad_count["even"] / parity_count["even"] if parity_count["even"] else 0.0,
            "odd": next_triad_count["odd"] / parity_count["odd"] if parity_count["odd"] else 0.0,
        },
        "unmatched_lane_shares": {
            "even": unmatched_even_lane_shares,
            "odd": unmatched_odd_lane_shares,
        },
        "unmatched_lane_share_difference": share_difference_payload(
            unmatched_even_lane_shares,
            unmatched_odd_lane_shares,
        ),
        "matched_strata_count": len(stratum_rows),
        "matched_total_weight_per_parity": int(round(matched_totals["even"])),
        "matched_next_triad_share": {
            "even": matched_triads["even"] / matched_totals["even"] if matched_totals["even"] else 0.0,
            "odd": matched_triads["odd"] / matched_totals["odd"] if matched_totals["odd"] else 0.0,
        },
        "matched_lane_shares": {
            "even": matched_even_lane_shares,
            "odd": matched_odd_lane_shares,
        },
        "matched_lane_share_difference": share_difference_payload(
            matched_even_lane_shares,
            matched_odd_lane_shares,
        ),
        "matched_lane_shares_within_triad": {
            "even": matched_even_lane_within_triad,
            "odd": matched_odd_lane_within_triad,
        },
        "matched_lane_share_difference_within_triad": share_difference_payload(
            matched_even_lane_within_triad,
            matched_odd_lane_within_triad,
        ),
        "top_overlap_strata": sorted(
            stratum_rows,
            key=lambda row: (-int(row["matched_weight"]), int(row["gap_width"]), int(row["first_open_offset"])),
        )[:12],
        "stratum_rows": stratum_rows,
    }


def combine_power_summaries(power_summaries: list[dict[str, object]]) -> dict[str, object]:
    """Aggregate the per-power summaries into one pooled payload."""
    if not power_summaries:
        raise ValueError("power_summaries must not be empty")

    weights_even = sum(int(summary["matched_total_weight_per_parity"]) for summary in power_summaries)
    weights_odd = weights_even
    triad_even_num = sum(
        int(summary["matched_total_weight_per_parity"]) * float(summary["matched_next_triad_share"]["even"])
        for summary in power_summaries
    )
    triad_odd_num = sum(
        int(summary["matched_total_weight_per_parity"]) * float(summary["matched_next_triad_share"]["odd"])
        for summary in power_summaries
    )
    lane_even_num = Counter()
    lane_odd_num = Counter()
    triad_lane_even_num = Counter()
    triad_lane_odd_num = Counter()
    for summary in power_summaries:
        weight = int(summary["matched_total_weight_per_parity"])
        for lane in LANE_ORDER:
            lane_even_num[lane] += weight * float(summary["matched_lane_shares"]["even"][lane])
            lane_odd_num[lane] += weight * float(summary["matched_lane_shares"]["odd"][lane])
            triad_lane_even_num[lane] += (
                weight * float(summary["matched_next_triad_share"]["even"])
                * float(summary["matched_lane_shares_within_triad"]["even"][lane])
            )
            triad_lane_odd_num[lane] += (
                weight * float(summary["matched_next_triad_share"]["odd"])
                * float(summary["matched_lane_shares_within_triad"]["odd"][lane])
            )

    matched_even_lane_shares = share_by_lane(lane_even_num, weights_even)
    matched_odd_lane_shares = share_by_lane(lane_odd_num, weights_odd)
    matched_even_triad_share = triad_even_num / weights_even if weights_even else 0.0
    matched_odd_triad_share = triad_odd_num / weights_odd if weights_odd else 0.0
    matched_even_lane_within_triad = share_by_lane(triad_lane_even_num, triad_even_num)
    matched_odd_lane_within_triad = share_by_lane(triad_lane_odd_num, triad_odd_num)

    return {
        "matched_total_weight_per_parity": int(weights_even),
        "matched_next_triad_share": {
            "even": matched_even_triad_share,
            "odd": matched_odd_triad_share,
        },
        "matched_lane_shares": {
            "even": matched_even_lane_shares,
            "odd": matched_odd_lane_shares,
        },
        "matched_lane_share_difference": share_difference_payload(
            matched_even_lane_shares,
            matched_odd_lane_shares,
        ),
        "matched_lane_shares_within_triad": {
            "even": matched_even_lane_within_triad,
            "odd": matched_odd_lane_within_triad,
        },
        "matched_lane_share_difference_within_triad": share_difference_payload(
            matched_even_lane_within_triad,
            matched_odd_lane_within_triad,
        ),
    }


def write_strata_csv(strata_rows: list[dict[str, object]], csv_path: Path) -> None:
    """Write the matched-stratum audit table."""
    fieldnames = [
        "power",
        "gap_width",
        "first_open_offset",
        "even_count",
        "odd_count",
        "matched_weight",
        "even_next_triad_share",
        "odd_next_triad_share",
        "even_minus_odd_next_triad_share",
        "even_o2_share",
        "odd_o2_share",
        "even_o4_share",
        "odd_o4_share",
        "even_o6_share",
        "odd_o6_share",
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(strata_rows)


def build_overview_plot(summary: dict[str, object], plot_path: Path) -> None:
    """Render the matched-triad and lane-difference overview plot."""
    powers = [int(payload["power"]) for payload in summary["powers"]]
    even_triad = [float(payload["matched_next_triad_share"]["even"]) for payload in summary["powers"]]
    odd_triad = [float(payload["matched_next_triad_share"]["odd"]) for payload in summary["powers"]]
    lane_diffs = {
        lane: [
            float(payload["matched_lane_share_difference_within_triad"][lane])
            for payload in summary["powers"]
        ]
        for lane in LANE_ORDER
    }

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))

    x_positions = list(range(len(powers)))
    bar_width = 0.36
    axes[0].bar(
        [value - bar_width / 2 for value in x_positions],
        even_triad,
        width=bar_width,
        label="even winner",
        color="#4c72b0",
    )
    axes[0].bar(
        [value + bar_width / 2 for value in x_positions],
        odd_triad,
        width=bar_width,
        label="odd winner",
        color="#dd8452",
    )
    axes[0].set_xticks(x_positions, [f"10^{power}" for power in powers])
    axes[0].set_ylim(0.0, 1.0)
    axes[0].set_ylabel("Matched next-gap triad share")
    axes[0].set_title("Matched Triad Retention")
    axes[0].legend(frameon=False)

    lane_width = 0.22
    lane_offsets = (-lane_width, 0.0, lane_width)
    for lane_index, lane in enumerate(LANE_ORDER):
        axes[1].bar(
            [value + lane_offsets[lane_index] for value in x_positions],
            lane_diffs[lane],
            width=lane_width,
            label=lane.replace("_odd_semiprime|d<=4", ""),
            color=LANE_COLORS[lane],
        )
    axes[1].axhline(0.0, color="#444444", linewidth=1.0)
    axes[1].set_xticks(x_positions, [f"10^{power}" for power in powers])
    axes[1].set_ylabel("Even minus odd matched share within triad")
    axes[1].set_title("Matched Lane Tilt Inside The Triad")
    axes[1].legend(frameon=False)

    fig.tight_layout()
    fig.savefig(plot_path, dpi=200)
    plt.close(fig)


def main(argv: list[str] | None = None) -> int:
    """Run the winner-parity next-opening probe."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.window_steps < 1:
        raise ValueError("window-steps must be at least 1")
    if not args.powers:
        raise ValueError("at least one power must be provided")

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    start_time = time.time()
    power_summaries: list[dict[str, object]] = []
    strata_rows: list[dict[str, object]] = []
    for power in args.powers:
        transitions = current_to_next_transitions(power, args.window_steps)
        power_summary = matched_lane_metrics(transitions)
        power_summary["power"] = int(power)
        power_summary["start_right_prime"] = start_prime_for_power(power)
        power_summaries.append(power_summary)
        for row in power_summary["stratum_rows"]:
            strata_row = dict(row)
            strata_row["power"] = int(power)
            strata_rows.append(strata_row)
        del power_summary["stratum_rows"]

    combined = combine_power_summaries(power_summaries)
    summary = {
        "powers": power_summaries,
        "combined": combined,
        "window_steps": int(args.window_steps),
        "runtime_seconds": time.time() - start_time,
    }

    summary_path = output_dir / "gwr_winner_parity_next_opening_probe_summary.json"
    strata_path = output_dir / "gwr_winner_parity_next_opening_probe_strata.csv"
    plot_path = output_dir / "gwr_winner_parity_next_opening_probe_overview.png"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_strata_csv(strata_rows, strata_path)
    build_overview_plot(summary, plot_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
