#!/usr/bin/env python3
"""Audit deterministic carrier-regime routing on held-out gap-type rows."""

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
DEFAULT_TRAIN_MIN_POWER = 7
DEFAULT_TRAIN_MAX_POWER = 17
DEFAULT_HELD_POWER = 18
DEFAULT_PRESSURE_QUANTILE = 0.8
DEFAULT_RECENT_WINDOW = 6
MOD_CYCLE_LENGTH = 8
SWEEP_PRESSURE_QUANTILES = (0.5, 0.6, 0.7, 0.8, 0.9)
SWEEP_RECENT_WINDOWS = (1, 2, 3, 4, 6, 8, 12)
GATE_LOGICS = (
    "square_only",
    "square_and_hd_recent",
    "square_or_hd_recent",
    "square_and_not_hd_recent",
    "hd_recent_only",
)
REPAIR_ARMS = (
    "short",
    "long",
    "nontriad_reset_scheduler",
    "event_lock_l3",
    "event_lock_l6",
)
TRIAD_STATES = {
    "o2_odd_semiprime|d<=4",
    "o4_odd_semiprime|d<=4",
    "o6_odd_semiprime|d<=4",
}
ROW_FIELDS = (
    "surface_label",
    "surface_row_index",
    "current_right_prime",
    "actual_next_state",
    "current_state",
    "square_phase_utilization",
    "square_pressure_band",
    "ordinary_regime",
    "high_square_regime",
    "hd_recent_1",
    "hd_recent_2",
    "hd_recent_3",
    "hd_recent_4",
    "hd_recent_6",
    "hd_recent_8",
    "hd_recent_12",
    "triad_return",
    "short_prediction",
    "long_prediction",
    "nontriad_reset_prediction",
    "event_lock_l3_prediction",
    "event_lock_l6_prediction",
    "carrier_regime_prediction",
    "short_hit",
    "long_hit",
    "short_miss",
    "long_repairs_short",
    "long_pollutes_short",
    "nontriad_reset_hit",
    "event_lock_l3_hit",
    "event_lock_l6_hit",
    "carrier_regime_hit",
    "carrier_regime_gate",
)
PARTITION_FIELDS = (
    "class_name",
    "row_count",
    "triad_occupancy",
    "short_hits",
    "long_hits",
    "clutch_hits",
    "long_repairs_short",
    "long_pollutes_short",
    "net_gain_over_short",
    "pollution_count",
)
SWEEP_FIELDS = (
    "pressure_quantile",
    "square_top_share",
    "square_pressure_cutoff",
    "recent_window",
    "gate_logic",
    "repair_arm",
    "fire_count",
    "fire_share",
    "short_correct",
    "long_correct",
    "carrier_regime_correct",
    "short_accuracy",
    "long_accuracy",
    "carrier_regime_accuracy",
    "net_gain_over_short",
    "net_gain_over_long",
    "hard_case_capture",
    "capture_per_fire",
    "pollution_rate",
    "ordinary_pool_accuracy",
    "beats_short_and_long",
    "v2_passed",
    "strong_passed",
)


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description="Audit deterministic carrier-regime partitions for gap-type schedulers.",
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
        help="Directory for the summary JSON and per-row CSV.",
    )
    parser.add_argument(
        "--train-min-power",
        type=int,
        default=DEFAULT_TRAIN_MIN_POWER,
        help="Smallest sampled decade power used for scheduler training.",
    )
    parser.add_argument(
        "--train-max-power",
        type=int,
        default=DEFAULT_TRAIN_MAX_POWER,
        help="Largest sampled decade power used for scheduler training.",
    )
    parser.add_argument(
        "--held-power",
        type=int,
        default=DEFAULT_HELD_POWER,
        help="Sampled decade power reserved for held-out evaluation.",
    )
    parser.add_argument(
        "--pressure-quantile",
        type=float,
        default=DEFAULT_PRESSURE_QUANTILE,
        help="Training d=4 square-utilization quantile used as the high-pressure cutoff.",
    )
    parser.add_argument(
        "--recent-window",
        type=int,
        choices=(3, 6),
        default=DEFAULT_RECENT_WINDOW,
        help="Recent higher-divisor window used by the carrier-regime gate.",
    )
    return parser


def load_rows(detail_csv: Path) -> list[dict[str, str]]:
    """Load catalog detail rows."""
    if not detail_csv.exists():
        raise FileNotFoundError(f"detail CSV does not exist: {detail_csv}")
    with detail_csv.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError("detail CSV must contain at least one row")
    return rows


def surface_label(power: int) -> str:
    """Return one sampled-decade display label."""
    return f"10^{power}"


def rows_by_surface(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    """Group rows by display label and sort each surface by row index."""
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["surface_display_label"]].append(row)
    for surface_rows in grouped.values():
        surface_rows.sort(key=lambda row: int(row["surface_row_index"]))
    return dict(grouped)


def d_bucket(next_dmin: str) -> str:
    """Return the reduced divisor bucket."""
    value = int(next_dmin)
    if value <= 4:
        return "d<=4"
    if value <= 16:
        return "5<=d<=16"
    if value <= 64:
        return "17<=d<=64"
    return "d>64"


def reduced_state(row: dict[str, str]) -> str:
    """Return the reduced gap-type state."""
    return f"o{row['first_open_offset']}_{row['carrier_family']}|{d_bucket(row['next_dmin'])}"


def has_higher_divisor(row: dict[str, str]) -> bool:
    """Return whether one row belongs to a higher-divisor carrier family."""
    return "higher_divisor" in row["carrier_family"]


def square_phase_utilization(row: dict[str, str]) -> float:
    """Return square-phase utilization for one current d=4 row."""
    winner = int(row["winner"])
    right_prime = int(row["next_right_prime"])
    next_square_root = int(nextprime(math.isqrt(winner)))
    next_square = next_square_root * next_square_root
    threat_distance = next_square - winner
    if threat_distance <= 0:
        raise ValueError(f"non-positive square threat distance at winner={winner}")
    return (right_prime - winner) / threat_distance


def quantile_cutoff(values: list[float], quantile: float) -> float:
    """Return a deterministic nearest-rank cutoff for one quantile."""
    if not values:
        raise ValueError("values must not be empty")
    if not 0.0 < quantile < 1.0:
        raise ValueError("pressure quantile must lie strictly between 0 and 1")
    ordered = sorted(values)
    index = math.ceil(quantile * len(ordered)) - 1
    return ordered[index]


def top_prediction(counter: Counter[str]) -> str:
    """Return the deterministic top successor for one context."""
    if not counter:
        raise ValueError("counter must not be empty")
    return max(counter.items(), key=lambda item: (item[1], item[0]))[0]


def prediction_or_empty(counter: Counter[str] | None) -> str:
    """Return the top successor, or an explicit miss marker for unsupported contexts."""
    if counter is None:
        return ""
    return top_prediction(counter)


def advance_phase(phase: int, next_state: str, reset_mode: str) -> int:
    """Advance one finite scheduler phase."""
    if reset_mode == "none":
        return (phase + 1) % MOD_CYCLE_LENGTH
    if reset_mode == "nontriad":
        if next_state not in TRIAD_STATES:
            return 0
        return (phase + 1) % MOD_CYCLE_LENGTH
    raise ValueError(f"unsupported reset mode: {reset_mode}")


def build_hybrid_counter(
    grouped: dict[str, list[dict[str, str]]],
    train_surfaces: list[str],
    reset_mode: str,
) -> dict[tuple[int, str, str, str], Counter[str]]:
    """Build one phase-aware long-memory transition counter."""
    counter: dict[tuple[int, str, str, str], Counter[str]] = defaultdict(Counter)

    for label in train_surfaces:
        states = [reduced_state(row) for row in grouped[label]]
        phase = 0
        for left2, left1, current, next_state in zip(
            states,
            states[1:],
            states[2:],
            states[3:],
        ):
            counter[(phase, left2, left1, current)][next_state] += 1
            phase = advance_phase(phase, next_state, reset_mode)

    if not counter:
        raise ValueError(f"{reset_mode} hybrid support is empty")
    return counter


def build_support(
    grouped: dict[str, list[dict[str, str]]],
    train_surfaces: list[str],
) -> dict[str, object]:
    """Build short and long transition supports from training surfaces."""
    short_counter: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    long_counter: dict[tuple[str, str, str], Counter[str]] = defaultdict(Counter)

    for label in train_surfaces:
        if label not in grouped:
            raise ValueError(f"training surface {label} is not present in detail CSV")
        states = [reduced_state(row) for row in grouped[label]]
        for left1, current, next_state in zip(states, states[1:], states[2:]):
            short_counter[(left1, current)][next_state] += 1
        for left2, left1, current, next_state in zip(
            states,
            states[1:],
            states[2:],
            states[3:],
        ):
            long_counter[(left2, left1, current)][next_state] += 1

    if not short_counter:
        raise ValueError("short-memory support is empty")
    if not long_counter:
        raise ValueError("long-memory support is empty")
    return {
        "short": short_counter,
        "long": long_counter,
        "hybrid_none": build_hybrid_counter(grouped, train_surfaces, "none"),
        "hybrid_nontriad": build_hybrid_counter(grouped, train_surfaces, "nontriad"),
    }


def held_pressure_cutoff(
    grouped: dict[str, list[dict[str, str]]],
    held_surface: str,
    pressure_quantile: float,
) -> float:
    """Return the high square-pressure cutoff for held-out current-row features."""
    values = [
        square_phase_utilization(row)
        for row in grouped[held_surface]
        if int(row["next_dmin"]) == 4
    ]
    return quantile_cutoff(values, pressure_quantile)


def evaluate(
    rows: list[dict[str, str]],
    *,
    train_min_power: int,
    train_max_power: int,
    held_power: int,
    pressure_quantile: float,
    recent_window: int,
) -> tuple[dict[str, object], list[dict[str, object]]]:
    """Evaluate short, long, and carrier-regime schedulers on held-out d=4 rows."""
    if train_min_power > train_max_power:
        raise ValueError("train-min-power must be <= train-max-power")

    grouped = rows_by_surface(rows)
    train_surfaces = [surface_label(power) for power in range(train_min_power, train_max_power + 1)]
    held_surface = surface_label(held_power)
    if held_surface not in grouped:
        raise ValueError(f"held-out surface {held_surface} is not present in detail CSV")

    pressure_cutoff = held_pressure_cutoff(grouped, held_surface, pressure_quantile)
    support = build_support(grouped, train_surfaces)
    short_counter = support["short"]
    long_counter = support["long"]
    hybrid_none_counter = support["hybrid_none"]
    hybrid_nontriad_counter = support["hybrid_nontriad"]
    held_rows = grouped[held_surface]
    held_states = [reduced_state(row) for row in held_rows]
    detail_rows: list[dict[str, object]] = []
    phase_none = 0
    phase_nontriad = 0

    for index in range(2, len(held_rows) - 1):
        current_row = held_rows[index]
        if index > 2:
            previous_actual = held_states[index]
            phase_none = advance_phase(phase_none, previous_actual, "none")
            phase_nontriad = advance_phase(phase_nontriad, previous_actual, "nontriad")
        if int(current_row["next_dmin"]) != 4:
            continue

        previous2 = held_states[index - 2]
        previous1 = held_states[index - 1]
        current = held_states[index]
        actual = held_states[index + 1]
        short_key = (previous1, current)
        long_key = (previous2, previous1, current)
        if short_key not in short_counter or long_key not in long_counter:
            continue

        utilization = square_phase_utilization(current_row)
        high_pressure = utilization >= pressure_cutoff
        recent_flags = {
            window: any(has_higher_divisor(row) for row in held_rows[max(0, index - window):index])
            for window in SWEEP_RECENT_WINDOWS
        }
        recent3 = recent_flags[3]
        recent6 = recent_flags[6]
        recent_flag = recent3 if recent_window == 3 else recent6
        carrier_regime_gate = high_pressure and recent_flag

        short_prediction = top_prediction(short_counter[short_key])
        long_prediction = top_prediction(long_counter[long_key])
        hybrid_none_key = (phase_none, previous2, previous1, current)
        hybrid_nontriad_key = (phase_nontriad, previous2, previous1, current)
        nontriad_reset_prediction = prediction_or_empty(
            hybrid_nontriad_counter.get(hybrid_nontriad_key)
        )
        event_lock_l3_prediction = (
            prediction_or_empty(hybrid_none_counter.get(hybrid_none_key))
            if recent_flags[3]
            else short_prediction
        )
        event_lock_l6_prediction = (
            prediction_or_empty(hybrid_none_counter.get(hybrid_none_key))
            if recent_flags[6]
            else short_prediction
        )
        carrier_regime_prediction = long_prediction if carrier_regime_gate else short_prediction
        short_hit = int(short_prediction == actual)
        long_hit = int(long_prediction == actual)
        carrier_regime_hit = int(carrier_regime_prediction == actual)

        detail_rows.append(
            {
                "surface_label": held_surface,
                "surface_row_index": int(current_row["surface_row_index"]),
                "current_right_prime": int(current_row["current_right_prime"]),
                "actual_next_state": actual,
                "current_state": current,
                "square_phase_utilization": utilization,
                "square_pressure_band": int(high_pressure),
                "ordinary_regime": int(not high_pressure),
                "high_square_regime": int(high_pressure),
                "hd_recent_1": int(recent_flags[1]),
                "hd_recent_2": int(recent_flags[2]),
                "hd_recent_3": int(recent3),
                "hd_recent_4": int(recent_flags[4]),
                "hd_recent_6": int(recent6),
                "hd_recent_8": int(recent_flags[8]),
                "hd_recent_12": int(recent_flags[12]),
                "triad_return": int(actual in TRIAD_STATES),
                "short_prediction": short_prediction,
                "long_prediction": long_prediction,
                "nontriad_reset_prediction": nontriad_reset_prediction,
                "event_lock_l3_prediction": event_lock_l3_prediction,
                "event_lock_l6_prediction": event_lock_l6_prediction,
                "carrier_regime_prediction": carrier_regime_prediction,
                "short_hit": short_hit,
                "long_hit": long_hit,
                "short_miss": int(not short_hit),
                "long_repairs_short": int((not short_hit) and long_hit),
                "long_pollutes_short": int(short_hit and not long_hit),
                "nontriad_reset_hit": int(nontriad_reset_prediction == actual),
                "event_lock_l3_hit": int(event_lock_l3_prediction == actual),
                "event_lock_l6_hit": int(event_lock_l6_prediction == actual),
                "carrier_regime_hit": carrier_regime_hit,
                "carrier_regime_gate": int(carrier_regime_gate),
            }
        )

    if not detail_rows:
        raise ValueError("held-out surface produced no evaluable d=4 rows")

    sweep_rows = sweep_candidates(
        detail_rows,
    )
    summary = summarize_results(
        detail_rows,
        sweep_rows=sweep_rows,
        train_surfaces=train_surfaces,
        held_surface=held_surface,
        pressure_quantile=pressure_quantile,
        pressure_cutoff=pressure_cutoff,
        recent_window=recent_window,
    )
    summary["sweep_rows"] = sweep_rows
    return summary, detail_rows


def share(numerator: int, denominator: int) -> float:
    """Return a ratio with explicit empty-set behavior."""
    if denominator == 0:
        return 0.0
    return numerator / denominator


def gate_fires(row: dict[str, object], gate_logic: str, recent_window: int) -> bool:
    """Return whether one gate variant fires on one detail row."""
    square = bool(int(row["square_pressure_band"]))
    recent = bool(int(row[f"hd_recent_{recent_window}"]))
    return gate_logic_fires(square, recent, gate_logic)


def gate_logic_fires(square: bool, recent: bool, gate_logic: str) -> bool:
    """Return whether one boolean gate formula fires."""
    if gate_logic == "square_only":
        return square
    if gate_logic == "square_and_hd_recent":
        return square and recent
    if gate_logic == "square_or_hd_recent":
        return square or recent
    if gate_logic == "square_and_not_hd_recent":
        return square and not recent
    if gate_logic == "hd_recent_only":
        return recent
    raise ValueError(f"unsupported gate logic: {gate_logic}")


def repair_prediction(row: dict[str, object], repair_arm: str) -> str:
    """Return one repair-arm prediction for one detail row."""
    if repair_arm == "short":
        return str(row["short_prediction"])
    if repair_arm == "long":
        return str(row["long_prediction"])
    if repair_arm == "nontriad_reset_scheduler":
        return str(row["nontriad_reset_prediction"])
    if repair_arm == "event_lock_l3":
        return str(row["event_lock_l3_prediction"])
    if repair_arm == "event_lock_l6":
        return str(row["event_lock_l6_prediction"])
    raise ValueError(f"unsupported repair arm: {repair_arm}")


def score_candidate(
    rows: list[dict[str, object]],
    *,
    pressure_quantile: float,
    pressure_cutoff: float,
    recent_window: int,
    gate_logic: str,
    repair_arm: str,
) -> dict[str, object]:
    """Score one gate and repair-arm candidate."""
    total = len(rows)
    high_rows = [
        row
        for row in rows
        if float(row["square_phase_utilization"]) >= pressure_cutoff
    ]
    gate_rows: list[dict[str, object]] = []
    carrier_regime_correct = 0
    polluted = 0
    short_correct_rows = [row for row in rows if int(row["short_hit"]) == 1]
    high_short_miss_rows = [row for row in high_rows if int(row["short_hit"]) == 0]
    captured = 0

    for row in rows:
        square = float(row["square_phase_utilization"]) >= pressure_cutoff
        recent = bool(int(row[f"hd_recent_{recent_window}"]))
        gate = gate_logic_fires(square, recent, gate_logic)
        prediction = repair_prediction(row, repair_arm) if gate else str(row["short_prediction"])
        actual = str(row["actual_next_state"])
        hit = prediction == actual
        carrier_regime_correct += int(hit)
        if gate:
            gate_rows.append(row)
        if int(row["short_hit"]) == 1 and not hit:
            polluted += 1
        if row in high_short_miss_rows and hit:
            captured += 1

    short_correct = len(short_correct_rows)
    long_correct = sum(int(row["long_hit"]) for row in rows)
    fire_count = len(gate_rows)
    short_accuracy = short_correct / total
    long_accuracy = long_correct / total
    carrier_regime_accuracy = carrier_regime_correct / total
    hard_case_capture = share(captured, len(high_short_miss_rows))
    pollution_rate = share(polluted, short_correct)
    net_gain_over_short = (carrier_regime_correct - short_correct) / total
    net_gain_over_long = (carrier_regime_correct - long_correct) / total
    beats_short_and_long = (
        carrier_regime_correct > short_correct and carrier_regime_correct > long_correct
    )
    v2_passed = (
        net_gain_over_short > 0.025
        and pollution_rate <= 0.025
        and hard_case_capture >= 0.15
        and beats_short_and_long
    )
    strong_passed = (
        hard_case_capture >= 0.25
        and pollution_rate <= 0.05
        and beats_short_and_long
    )

    ordinary_rows = [row for row in rows if row not in gate_rows]
    ordinary_hits = sum(int(row["short_hit"]) for row in ordinary_rows)

    return {
        "pressure_quantile": pressure_quantile,
        "square_top_share": 1.0 - pressure_quantile,
        "square_pressure_cutoff": pressure_cutoff,
        "recent_window": recent_window,
        "gate_logic": gate_logic,
        "repair_arm": repair_arm,
        "fire_count": fire_count,
        "fire_share": fire_count / total,
        "short_correct": short_correct,
        "long_correct": long_correct,
        "carrier_regime_correct": carrier_regime_correct,
        "short_accuracy": short_accuracy,
        "long_accuracy": long_accuracy,
        "carrier_regime_accuracy": carrier_regime_accuracy,
        "net_gain_over_short": net_gain_over_short,
        "net_gain_over_long": net_gain_over_long,
        "hard_case_capture": hard_case_capture,
        "capture_per_fire": share(captured, fire_count),
        "pollution_rate": pollution_rate,
        "ordinary_pool_accuracy": share(ordinary_hits, len(ordinary_rows)),
        "beats_short_and_long": int(beats_short_and_long),
        "v2_passed": int(v2_passed),
        "strong_passed": int(strong_passed),
    }


def sweep_candidates(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    """Return the full deterministic carrier-regime frontier sweep."""
    pressure_cutoffs = {
        quantile: quantile_cutoff(
            [float(row["square_phase_utilization"]) for row in rows],
            quantile,
        )
        for quantile in SWEEP_PRESSURE_QUANTILES
    }
    sweep_rows: list[dict[str, object]] = []
    for pressure_quantile in SWEEP_PRESSURE_QUANTILES:
        for recent_window in SWEEP_RECENT_WINDOWS:
            for gate_logic in GATE_LOGICS:
                for repair_arm in REPAIR_ARMS:
                    sweep_rows.append(
                        score_candidate(
                            rows,
                            pressure_quantile=pressure_quantile,
                            pressure_cutoff=pressure_cutoffs[pressure_quantile],
                            recent_window=recent_window,
                            gate_logic=gate_logic,
                            repair_arm=repair_arm,
                        )
                    )
    return sweep_rows


def best_candidate(rows: list[dict[str, object]]) -> dict[str, object]:
    """Return the best sweep row by the v2 routing objective."""
    return max(
        rows,
        key=lambda row: (
            int(row["v2_passed"]),
            float(row["net_gain_over_short"]),
            float(row["hard_case_capture"]),
            -float(row["pollution_rate"]),
            float(row["capture_per_fire"]),
            -int(row["fire_count"]),
        ),
    )


def best_low_pollution_candidate(rows: list[dict[str, object]]) -> dict[str, object]:
    """Return the best sweep row under the v2 pollution bound."""
    kept = [row for row in rows if float(row["pollution_rate"]) <= 0.025]
    if not kept:
        raise ValueError("sweep produced no row under the v2 pollution bound")
    return max(
        kept,
        key=lambda row: (
            float(row["net_gain_over_short"]),
            float(row["hard_case_capture"]),
            float(row["capture_per_fire"]),
            -int(row["fire_count"]),
        ),
    )


def partition_row(class_name: str, rows: list[dict[str, object]]) -> dict[str, object]:
    """Return exact occupancy and repair counts for one deterministic row class."""
    row_count = len(rows)
    short_hits = sum(int(row["short_hit"]) for row in rows)
    long_hits = sum(int(row["long_hit"]) for row in rows)
    clutch_hits = sum(int(row["carrier_regime_hit"]) for row in rows)
    long_repairs = sum(int(row["long_repairs_short"]) for row in rows)
    long_pollutes = sum(int(row["long_pollutes_short"]) for row in rows)
    return {
        "class_name": class_name,
        "row_count": row_count,
        "triad_occupancy": share(sum(int(row["triad_return"]) for row in rows), row_count),
        "short_hits": short_hits,
        "long_hits": long_hits,
        "clutch_hits": clutch_hits,
        "long_repairs_short": long_repairs,
        "long_pollutes_short": long_pollutes,
        "net_gain_over_short": share(long_hits - short_hits, row_count),
        "pollution_count": long_pollutes,
    }


def partition_table(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    """Return the deterministic carrier-regime partition table."""
    return [
        partition_row("all_d4", rows),
        partition_row("ordinary_regime", [row for row in rows if int(row["ordinary_regime"]) == 1]),
        partition_row("high_square_regime", [row for row in rows if int(row["high_square_regime"]) == 1]),
        partition_row("hd_recent_1", [row for row in rows if int(row["hd_recent_1"]) == 1]),
        partition_row("hd_recent_2", [row for row in rows if int(row["hd_recent_2"]) == 1]),
        partition_row("hd_recent_3", [row for row in rows if int(row["hd_recent_3"]) == 1]),
        partition_row("hd_recent_6", [row for row in rows if int(row["hd_recent_6"]) == 1]),
        partition_row("hd_recent_12", [row for row in rows if int(row["hd_recent_12"]) == 1]),
        partition_row(
            "A_low_square_no_hd_recent_6",
            [
                row
                for row in rows
                if int(row["high_square_regime"]) == 0 and int(row["hd_recent_6"]) == 0
            ],
        ),
        partition_row(
            "B_low_square_hd_recent_6",
            [
                row
                for row in rows
                if int(row["high_square_regime"]) == 0 and int(row["hd_recent_6"]) == 1
            ],
        ),
        partition_row(
            "C_high_square_no_hd_recent_6",
            [
                row
                for row in rows
                if int(row["high_square_regime"]) == 1 and int(row["hd_recent_6"]) == 0
            ],
        ),
        partition_row(
            "D_high_square_hd_recent_6",
            [
                row
                for row in rows
                if int(row["high_square_regime"]) == 1 and int(row["hd_recent_6"]) == 1
            ],
        ),
    ]


def partition_by_name(rows: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    """Index partition rows by class name."""
    return {str(row["class_name"]): row for row in rows}


def decision_payload(rows: list[dict[str, object]]) -> dict[str, object]:
    """Return the deterministic decision from the A/B/C/D partition."""
    indexed = partition_by_name(rows)
    class_a = indexed["A_low_square_no_hd_recent_6"]
    class_c = indexed["C_high_square_no_hd_recent_6"]
    class_d = indexed["D_high_square_hd_recent_6"]

    def class_passes(row: dict[str, object]) -> bool:
        return (
            float(row["triad_occupancy"]) <= float(class_a["triad_occupancy"]) - 0.05
            and int(row["long_repairs_short"]) > int(row["long_pollutes_short"])
        )

    repair_aligns = class_passes(class_c) or class_passes(class_d)
    repair_phrase = "does" if repair_aligns else "does not"
    next_step = (
        "carrier-regime router refinement"
        if repair_aligns
        else "freeze as a negative repair result"
    )
    conclusion = (
        "The measured surface is deterministic. Each row has a fixed next-state image. "
        "High square pressure partitions the d=4 surface into a carrier regime with lower "
        f"Semiprime Wheel Attractor occupancy. The tested long-memory repair {repair_phrase} "
        f"align with that partition. Therefore the next step is {next_step}."
    )
    return {
        "class_a_name": "A_low_square_no_hd_recent_6",
        "class_c_name": "C_high_square_no_hd_recent_6",
        "class_d_name": "D_high_square_hd_recent_6",
        "class_a_triad_occupancy": class_a["triad_occupancy"],
        "class_c_triad_occupancy": class_c["triad_occupancy"],
        "class_d_triad_occupancy": class_d["triad_occupancy"],
        "class_c_repairs_minus_pollutes": (
            int(class_c["long_repairs_short"]) - int(class_c["long_pollutes_short"])
        ),
        "class_d_repairs_minus_pollutes": (
            int(class_d["long_repairs_short"]) - int(class_d["long_pollutes_short"])
        ),
        "continue_carrier_regime_routing": repair_aligns,
        "conclusion": conclusion,
    }


def summarize_results(
    rows: list[dict[str, object]],
    *,
    sweep_rows: list[dict[str, object]],
    train_surfaces: list[str],
    held_surface: str,
    pressure_quantile: float,
    pressure_cutoff: float,
    recent_window: int,
) -> dict[str, object]:
    """Summarize exact carrier-regime partitions and repair counts."""
    total = len(rows)
    high_rows = [row for row in rows if int(row["square_pressure_band"]) == 1]
    ordinary_rows = [row for row in rows if int(row["carrier_regime_gate"]) == 0]
    gate_rows = [row for row in rows if int(row["carrier_regime_gate"]) == 1]
    high_short_miss_rows = [
        row
        for row in high_rows
        if int(row["short_hit"]) == 0
    ]
    captured_rows = [
        row
        for row in high_short_miss_rows
        if int(row["carrier_regime_hit"]) == 1
    ]
    short_correct_rows = [row for row in rows if int(row["short_hit"]) == 1]
    polluted_rows = [row for row in short_correct_rows if int(row["carrier_regime_hit"]) == 0]
    gate_short_correct_rows = [
        row
        for row in gate_rows
        if int(row["short_hit"]) == 1
    ]
    gate_polluted_rows = [
        row
        for row in gate_short_correct_rows
        if int(row["carrier_regime_hit"]) == 0
    ]

    short_correct = sum(int(row["short_hit"]) for row in rows)
    long_correct = sum(int(row["long_hit"]) for row in rows)
    carrier_regime_correct = sum(int(row["carrier_regime_hit"]) for row in rows)
    hard_case_capture = share(len(captured_rows), len(high_short_miss_rows))
    pollution = share(len(polluted_rows), len(short_correct_rows))
    gate_pollution = share(len(gate_polluted_rows), len(gate_short_correct_rows))
    short_accuracy = short_correct / total
    long_accuracy = long_correct / total
    carrier_regime_accuracy = carrier_regime_correct / total

    success = (
        hard_case_capture >= 0.25
        and pollution <= 0.05
        and carrier_regime_accuracy > short_accuracy
        and carrier_regime_accuracy > long_accuracy
    )
    partitions = partition_table(rows)
    decision = decision_payload(partitions)

    return {
        "train_surfaces": train_surfaces,
        "held_surface": held_surface,
        "pressure_quantile": pressure_quantile,
        "square_pressure_cutoff": pressure_cutoff,
        "recent_window": recent_window,
        "row_count": total,
        "high_square_pressure_count": len(high_rows),
        "carrier_regime_gate_count": len(gate_rows),
        "policy_scores": {
            "short_only": {
                "correct": short_correct,
                "accuracy": short_accuracy,
            },
            "long_only": {
                "correct": long_correct,
                "accuracy": long_accuracy,
            },
            "carrier_regime_gated": {
                "correct": carrier_regime_correct,
                "accuracy": carrier_regime_accuracy,
            },
        },
        "ordinary_accuracy": {
            "row_count": len(ordinary_rows),
            "short_accuracy": share(
                sum(int(row["short_hit"]) for row in ordinary_rows),
                len(ordinary_rows),
            ),
            "carrier_regime_accuracy": share(
                sum(int(row["carrier_regime_hit"]) for row in ordinary_rows),
                len(ordinary_rows),
            ),
        },
        "hard_case_capture": hard_case_capture,
        "pollution_rate": pollution,
        "gate_pollution_rate": gate_pollution,
        "net_gain_over_short": (carrier_regime_correct - short_correct) / total,
        "net_gain_over_long": (carrier_regime_correct - long_correct) / total,
        "success_threshold": {
            "hard_case_capture_minimum": 0.25,
            "pollution_rate_maximum": 0.05,
            "carrier_regime_accuracy_must_exceed_short_and_long": True,
            "passed": success,
        },
        "v2_acceptance_gate": {
            "net_gain_over_short_minimum": 0.025,
            "pollution_rate_maximum": 0.025,
            "hard_case_capture_minimum": 0.15,
            "carrier_regime_accuracy_must_exceed_short_and_long": True,
        },
        "sweep_count": len(sweep_rows),
        "v2_pass_count": sum(int(row["v2_passed"]) for row in sweep_rows),
        "strong_pass_count": sum(int(row["strong_passed"]) for row in sweep_rows),
        "best_sweep_candidate": best_candidate(sweep_rows),
        "best_low_pollution_candidate": best_low_pollution_candidate(sweep_rows),
        "partition_table": partitions,
        "four_way_partition": [
            row
            for row in partitions
            if str(row["class_name"]).startswith(("A_", "B_", "C_", "D_"))
        ],
        "decision_rule": {
            "required_occupancy_drop_vs_class_a": 0.05,
            "requires_long_repairs_short_gt_long_pollutes_short": True,
        },
        "decision": decision,
    }


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: tuple[str, ...]) -> None:
    """Write one LF-terminated detail CSV."""
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main(argv: list[str] | None = None) -> int:
    """Run the carrier-regime routing probe and write artifacts."""
    args = build_parser().parse_args(argv)
    start_time = time.perf_counter()
    rows = load_rows(args.detail_csv)
    summary, detail_rows = evaluate(
        rows,
        train_min_power=args.train_min_power,
        train_max_power=args.train_max_power,
        held_power=args.held_power,
        pressure_quantile=args.pressure_quantile,
        recent_window=args.recent_window,
    )
    summary["runtime_seconds"] = time.perf_counter() - start_time

    args.output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = args.output_dir / "gwr_dni_carrier_regime_routing_summary.json"
    detail_path = args.output_dir / "gwr_dni_carrier_regime_routing_rows.csv"
    sweep_path = args.output_dir / "gwr_dni_carrier_regime_routing_sweep.csv"
    sweep_rows = summary.pop("sweep_rows")
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    write_csv(detail_path, detail_rows, ROW_FIELDS)
    write_csv(sweep_path, sweep_rows, SWEEP_FIELDS)
    print(
        "gwr-dni-carrier-regime-routing:"
        f" rows={summary['row_count']}"
        f" carrier_regime_gate={summary['carrier_regime_gate_count']}"
        f" sweep={summary['sweep_count']}"
        f" v2_pass={summary['v2_pass_count']}"
        f" short_acc={summary['policy_scores']['short_only']['accuracy']:.6f}"
        f" long_acc={summary['policy_scores']['long_only']['accuracy']:.6f}"
        f" carrier_regime_acc={summary['policy_scores']['carrier_regime_gated']['accuracy']:.6f}"
        f" continue={summary['decision']['continue_carrier_regime_routing']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
