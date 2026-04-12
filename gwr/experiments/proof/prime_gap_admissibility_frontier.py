#!/usr/bin/env python3
"""Canonicalize exact hard cases for the local admissibility route."""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

import gmpy2
import numpy as np


ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = ROOT / "src" / "python"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from z_band_prime_composite_field import divisor_counts_segment


EARLIER_SPOILER_SCAN_PATH = ROOT / "gwr" / "experiments" / "proof" / "earlier_spoiler_scan.py"
LARGE_PRIME_REDUCER_PATH = ROOT / "gwr" / "experiments" / "proof" / "large_prime_reducer.py"

DEFAULT_WHEEL_MODULUS = 30_030
DEFAULT_EARLY_WINDOW = 128
DEFAULT_HIGH_DIVISOR_CUTOFF = 64
DEFAULT_LOW_CLASS_RESIDUALS = (4, 6, 8, 12, 16, 24, 32, 48)
DEFAULT_TOP_CASES = 50
DEFAULT_TOP_STATES = 50


def load_module(module_name: str, path: Path):
    """Load one helper module directly from its file path."""
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


EARLIER_SPOILER_SCAN = load_module(
    "prime_gap_admissibility_frontier_earlier_spoiler_scan",
    EARLIER_SPOILER_SCAN_PATH,
)
LARGE_PRIME_REDUCER = load_module(
    "prime_gap_admissibility_frontier_large_prime_reducer",
    LARGE_PRIME_REDUCER_PATH,
)


@dataclass(frozen=True)
class AutomaticWindowRow:
    """One automatic `w < k + K` elimination row by earlier divisor class."""

    earlier_divisor_count: int
    minimal_earlier_value: int
    automatic_window_eliminated: bool

    def to_dict(self) -> dict[str, int | bool]:
        """Return a JSON-ready mapping."""
        return asdict(self)


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Canonicalize exact prime-gap hard cases by local chamber state and "
            "emit a frontier summary for the local admissibility route."
        ),
    )
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument(
        "--interval-hi",
        type=int,
        default=None,
        help="Exclusive natural-number upper bound for exact interval mode.",
    )
    source_group.add_argument(
        "--checkpoint-dir",
        type=Path,
        default=None,
        help="Directory of segmented no-early-spoiler JSON checkpoints.",
    )
    parser.add_argument(
        "--interval-lo",
        type=int,
        default=2,
        help="Inclusive lower bound for exact interval mode.",
    )
    parser.add_argument(
        "--wheel-modulus",
        type=int,
        default=DEFAULT_WHEEL_MODULUS,
        help="Wheel modulus used in the chamber-state key.",
    )
    parser.add_argument(
        "--early-window",
        type=int,
        default=DEFAULT_EARLY_WINDOW,
        help="Window K used in the square-free chamber model.",
    )
    parser.add_argument(
        "--high-divisor-cutoff",
        type=int,
        default=DEFAULT_HIGH_DIVISOR_CUTOFF,
        help="Bucket every earlier divisor class at or above this value together.",
    )
    parser.add_argument(
        "--low-class-residual",
        action="append",
        type=int,
        default=None,
        help="Repeat to override the low-class residual set kept exact in the chamber key.",
    )
    parser.add_argument(
        "--top-cases",
        type=int,
        default=DEFAULT_TOP_CASES,
        help="Number of exact frontier rows to retain.",
    )
    parser.add_argument(
        "--top-states",
        type=int,
        default=DEFAULT_TOP_STATES,
        help="Number of chamber states to retain.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional JSON output path.",
    )
    return parser


def _round_float(value: float) -> float:
    """Return a stable JSON float."""
    return float(f"{value:.18g}")


def log_score_margin(
    earlier_value: int,
    earlier_divisor_count: int,
    winner_value: int,
    winner_divisor_count: int,
) -> float:
    """Return the positive winner-minus-earlier log-score margin."""
    earlier_score = (1.0 - earlier_divisor_count / 2.0) * math.log(earlier_value)
    winner_score = (1.0 - winner_divisor_count / 2.0) * math.log(winner_value)
    return winner_score - earlier_score


def critical_ratio_margin(
    earlier_value: int,
    earlier_divisor_count: int,
    winner_value: int,
    winner_divisor_count: int,
) -> tuple[float, float, float, float]:
    """Return the critical ratio, actual ratio, margin, and bridge load."""
    critical_ratio = (earlier_divisor_count - 2) / (winner_divisor_count - 2)
    actual_ratio = math.log(winner_value) / math.log(earlier_value)
    ratio_margin = critical_ratio - actual_ratio
    critical_excess = critical_ratio - 1.0
    actual_excess = actual_ratio - 1.0
    bridge_load = actual_excess / critical_excess
    return critical_ratio, actual_ratio, ratio_margin, bridge_load


def is_prime_square(value: int) -> bool:
    """Return whether one integer is exactly the square of a prime."""
    if value <= 0:
        return False
    value_mpz = gmpy2.mpz(value)
    if not gmpy2.is_square(value_mpz):
        return False
    root = gmpy2.isqrt(value_mpz)
    return bool(gmpy2.is_prime(root))


def next_prime_square_at_or_after(value: int) -> int:
    """Return the least prime square at or above one value."""
    if value <= 4:
        return 4
    root = int(gmpy2.isqrt(value))
    if root * root < value:
        root += 1
    candidate = max(2, root)
    while True:
        if gmpy2.is_prime(candidate):
            return candidate * candidate
        candidate += 1


def first_offset_for_divisor_class(
    left_prime: int,
    gap_values: np.ndarray,
    gap_divisors: np.ndarray,
    divisor_class: int,
) -> int | None:
    """Return the left-prime offset of one divisor class if it appears."""
    indices = np.flatnonzero(gap_divisors == divisor_class)
    if indices.size == 0:
        return None
    return int(gap_values[int(indices[0])] - left_prime)


def first_later_dominator_offset(
    earlier_index: int,
    gap_values: np.ndarray,
    gap_divisors: np.ndarray,
) -> int:
    """Return the offset to the first later composite that beats one earlier candidate."""
    earlier_value = int(gap_values[earlier_index])
    earlier_divisor_count = int(gap_divisors[earlier_index])
    for later_index in range(earlier_index + 1, gap_values.size):
        later_value = int(gap_values[later_index])
        later_divisor_count = int(gap_divisors[later_index])
        if EARLIER_SPOILER_SCAN.score_strictly_greater(
            later_value,
            later_divisor_count,
            earlier_value,
            earlier_divisor_count,
        ):
            return later_value - earlier_value
    raise RuntimeError("No later dominator found for an exact earlier candidate")


def exact_case_key(case: dict[str, object]) -> tuple[int, int, int, int, int, int, int | None, int, int]:
    """Return the exact canonical key requested for one hard case."""
    return (
        int(case["gap"]),
        int(case["left_prime_mod_wheel"]),
        int(case["winner_divisor_count"]),
        int(case["earlier_divisor_count"]),
        int(case["earlier_offset"]),
        int(case["winner_offset"]),
        None if case["first_d4_offset"] is None else int(case["first_d4_offset"]),
        int(case["square_margin"]),
        int(case["first_later_dominator_offset"]),
    )


def earlier_divisor_bucket(
    earlier_divisor_count: int,
    high_divisor_cutoff: int,
    low_class_residuals: set[int],
) -> str:
    """Return the bucketed earlier divisor class for the chamber model."""
    if earlier_divisor_count >= high_divisor_cutoff:
        return f"{high_divisor_cutoff}+"
    if earlier_divisor_count in low_class_residuals:
        return str(earlier_divisor_count)
    return "automatic-low"


def chamber_bucket(value: int | None, early_window: int, *, none_label: str) -> str:
    """Bucket one offset-like chamber value into the finite local model."""
    if value is None:
        return none_label
    if value > early_window:
        return f">{early_window}"
    if value < -early_window:
        return f"<-{early_window}"
    return str(value)


def chamber_state_key(
    case: dict[str, object],
    *,
    early_window: int,
    high_divisor_cutoff: int,
    low_class_residuals: set[int],
) -> tuple[int, int, str, int, int, str, str, str]:
    """Return the finite square-free chamber-state key for one hard case."""
    return (
        int(case["left_prime_mod_wheel"]),
        int(case["winner_divisor_count"]),
        earlier_divisor_bucket(
            int(case["earlier_divisor_count"]),
            high_divisor_cutoff=high_divisor_cutoff,
            low_class_residuals=low_class_residuals,
        ),
        int(case["earlier_offset"]),
        int(case["winner_offset"]),
        chamber_bucket(int(case["first_d4_offset"]) if case["first_d4_offset"] is not None else None, early_window, none_label="none"),
        chamber_bucket(int(case["square_margin"]), early_window, none_label="none"),
        chamber_bucket(int(case["first_later_dominator_offset"]), early_window, none_label="none"),
    )


def unsupported_low_class(case: dict[str, object], low_class_residuals: set[int], high_divisor_cutoff: int) -> bool:
    """Return whether one case lies in the exact low-class residual band but outside the chosen set."""
    earlier_divisor_count = int(case["earlier_divisor_count"])
    return (
        earlier_divisor_count < high_divisor_cutoff
        and earlier_divisor_count not in low_class_residuals
        and earlier_divisor_count != int(case["winner_divisor_count"]) + 1
    )


def automatic_window_rows(
    *,
    high_divisor_cutoff: int,
    early_window: int,
    max_divisor_class: int,
) -> list[AutomaticWindowRow]:
    """Return the `w < k + K` automatic elimination table by earlier divisor class."""
    rows: list[AutomaticWindowRow] = []
    for earlier_divisor_count in range(high_divisor_cutoff, max_divisor_class + 1):
        minimal_earlier_value = LARGE_PRIME_REDUCER.min_n_with_tau(earlier_divisor_count)
        automatic_window_eliminated = (
            pow(minimal_earlier_value + early_window, earlier_divisor_count - 3)
            < pow(minimal_earlier_value, earlier_divisor_count - 2)
        )
        rows.append(
            AutomaticWindowRow(
                earlier_divisor_count=earlier_divisor_count,
                minimal_earlier_value=minimal_earlier_value,
                automatic_window_eliminated=automatic_window_eliminated,
            )
        )
    return rows


def analyze_gap_case(
    *,
    left_prime: int,
    right_prime: int,
    gap_values: np.ndarray,
    gap_divisors: np.ndarray,
    earlier_index: int,
    winner_index: int,
    wheel_modulus: int,
) -> dict[str, object]:
    """Return the exact annotated record for one earlier-versus-winner case."""
    earlier_value = int(gap_values[earlier_index])
    earlier_divisor_count = int(gap_divisors[earlier_index])
    winner_value = int(gap_values[winner_index])
    winner_divisor_count = int(gap_divisors[winner_index])

    first_d4_offset = first_offset_for_divisor_class(left_prime, gap_values, gap_divisors, 4)
    square_threat_value = next_prime_square_at_or_after(winner_value)
    for value_raw, divisor_raw in zip(gap_values[winner_index:], gap_divisors[winner_index:]):
        if int(divisor_raw) == 3 and is_prime_square(int(value_raw)):
            square_threat_value = int(value_raw)
            break
    square_margin = square_threat_value - right_prime
    dominator_offset = first_later_dominator_offset(earlier_index, gap_values, gap_divisors)
    log_margin = log_score_margin(
        earlier_value=earlier_value,
        earlier_divisor_count=earlier_divisor_count,
        winner_value=winner_value,
        winner_divisor_count=winner_divisor_count,
    )
    critical_ratio, actual_ratio, ratio_margin, bridge_load = critical_ratio_margin(
        earlier_value=earlier_value,
        earlier_divisor_count=earlier_divisor_count,
        winner_value=winner_value,
        winner_divisor_count=winner_divisor_count,
    )
    return {
        "left_prime": left_prime,
        "right_prime": right_prime,
        "gap": right_prime - left_prime,
        "left_prime_mod_wheel": left_prime % wheel_modulus,
        "winner_value": winner_value,
        "winner_divisor_count": winner_divisor_count,
        "winner_offset": winner_value - left_prime,
        "earlier_value": earlier_value,
        "earlier_divisor_count": earlier_divisor_count,
        "earlier_offset": earlier_value - left_prime,
        "first_d4_offset": first_d4_offset,
        "square_margin": square_margin,
        "first_later_dominator_offset": dominator_offset,
        "log_score_margin": _round_float(log_margin),
        "critical_ratio": _round_float(critical_ratio),
        "actual_log_ratio": _round_float(actual_ratio),
        "critical_ratio_margin": _round_float(ratio_margin),
        "bridge_load": _round_float(bridge_load),
    }


def _update_top_cases(
    bucket: list[dict[str, object]],
    case: dict[str, object],
    *,
    key: str,
    limit: int,
    reverse: bool = False,
) -> None:
    """Keep only the frontier cases for one ranking key."""
    bucket.append(case)
    bucket.sort(
        key=lambda row: (
            (-float(row[key]) if reverse else float(row[key])),
            int(row["winner_value"]),
            int(row["earlier_value"]),
        )
    )
    del bucket[limit:]


def summarize_cases(
    *,
    source_summary: dict[str, object],
    wheel_modulus: int,
    early_window: int,
    high_divisor_cutoff: int,
    low_class_residuals: set[int],
    top_states: int,
    max_automatic_divisor_class: int = 512,
    hard_case_count: int,
    square_branch_case_count: int,
    non_square_case_count: int,
    non_square_beyond_window_count: int,
    unsupported_low_class_case_count: int,
    unsupported_low_class_examples: list[dict[str, object]],
    unsupported_low_class_stats: dict[int, dict[str, object]],
    top_bridge_cases: list[dict[str, object]],
    top_ratio_cases: list[dict[str, object]],
    top_log_cases: list[dict[str, object]],
    top_exact_cases: list[dict[str, object]],
    exact_state_stats: dict[tuple[int, ...], dict[str, object]],
    chamber_state_stats: dict[tuple[object, ...], dict[str, object]],
    winner_class_stats: dict[int, dict[str, object]],
) -> dict[str, object]:
    """Return the exact frontier and chamber-state summaries from streamed stats."""
    exact_state_summary = [
        {
            "exact_state": list(key),
            "count": stats["count"],
            "min_critical_ratio_margin": _round_float(stats["min_critical_ratio_margin"]),
            "max_bridge_load": _round_float(stats["max_bridge_load"]),
            "representative": stats["representative"],
        }
        for key, stats in exact_state_stats.items()
    ]
    exact_state_summary.sort(
        key=lambda row: (
            row["min_critical_ratio_margin"],
            -row["count"],
            row["representative"]["winner_value"],
        )
    )

    chamber_state_summary = [
        {
            "chamber_state": list(key),
            "count": stats["count"],
            "min_critical_ratio_margin": _round_float(stats["min_critical_ratio_margin"]),
            "max_bridge_load": _round_float(stats["max_bridge_load"]),
            "representative": stats["representative"],
        }
        for key, stats in chamber_state_stats.items()
    ]
    chamber_state_summary.sort(
        key=lambda row: (
            row["min_critical_ratio_margin"],
            -row["count"],
            row["representative"]["winner_value"],
        )
    )

    automatic_rows = automatic_window_rows(
        high_divisor_cutoff=high_divisor_cutoff,
        early_window=early_window,
        max_divisor_class=max_automatic_divisor_class,
    )
    automatic_failures = [
        row.to_dict() for row in automatic_rows if not row.automatic_window_eliminated
    ]
    unsupported_low_class_summary = [
        {
            "earlier_divisor_count": divisor_class,
            "count": stats["count"],
            "min_critical_ratio_margin": _round_float(stats["min_critical_ratio_margin"]),
            "max_bridge_load": _round_float(stats["max_bridge_load"]),
            "representative": stats["representative"],
        }
        for divisor_class, stats in unsupported_low_class_stats.items()
    ]
    unsupported_low_class_summary.sort(
        key=lambda row: (
            row["min_critical_ratio_margin"],
            -row["count"],
            row["earlier_divisor_count"],
        )
    )
    winner_class_summary = [
        {
            "winner_divisor_count": winner_divisor_count,
            "count": stats["count"],
            "max_winner_offset": stats["max_winner_offset"],
            "min_critical_ratio_margin": _round_float(stats["min_critical_ratio_margin"]),
            "max_bridge_load": _round_float(stats["max_bridge_load"]),
            "representative": stats["representative"],
        }
        for winner_divisor_count, stats in winner_class_stats.items()
    ]
    winner_class_summary.sort(key=lambda row: row["winner_divisor_count"])

    return {
        "source_summary": source_summary,
        "wheel_modulus": wheel_modulus,
        "early_window": early_window,
        "high_divisor_cutoff": high_divisor_cutoff,
        "low_class_residuals": sorted(low_class_residuals),
        "hard_case_count": hard_case_count,
        "square_branch_case_count": square_branch_case_count,
        "non_square_case_count": non_square_case_count,
        "non_square_beyond_window_count": non_square_beyond_window_count,
        "unsupported_low_class_case_count": unsupported_low_class_case_count,
        "unsupported_low_class_examples": unsupported_low_class_examples,
        "unsupported_low_class_summary": unsupported_low_class_summary,
        "winner_class_summary": winner_class_summary,
        "top_bridge_load_cases": top_bridge_cases,
        "top_ratio_margin_cases": top_ratio_cases,
        "top_log_margin_cases": top_log_cases,
        "exact_case_rows": top_exact_cases,
        "exact_state_count": len(exact_state_summary),
        "exact_state_summary": exact_state_summary[:top_states],
        "chamber_state_count": len(chamber_state_summary),
        "chamber_state_summary": chamber_state_summary[:top_states],
        "automatic_window_elimination_summary": {
            "checked_divisor_classes": [row.to_dict() for row in automatic_rows],
            "failure_count": len(automatic_failures),
            "failures": automatic_failures,
        },
    }


def initialize_case_stats() -> dict[str, object]:
    """Return the mutable accumulator used while streaming exact hard cases."""
    return {
        "hard_case_count": 0,
        "square_branch_case_count": 0,
        "non_square_case_count": 0,
        "non_square_beyond_window_count": 0,
        "unsupported_low_class_case_count": 0,
        "unsupported_low_class_examples": [],
        "unsupported_low_class_stats": {},
        "top_bridge_cases": [],
        "top_ratio_cases": [],
        "top_log_cases": [],
        "top_exact_cases": [],
        "exact_state_stats": {},
        "chamber_state_stats": {},
        "winner_class_stats": {},
    }


def consume_case(
    stats: dict[str, object],
    *,
    case: dict[str, object],
    early_window: int,
    high_divisor_cutoff: int,
    low_class_residuals: set[int],
    top_cases: int,
    top_states: int,
) -> None:
    """Update the streamed frontier statistics with one exact hard case."""
    stats["hard_case_count"] = int(stats["hard_case_count"]) + 1

    _update_top_cases(
        stats["top_bridge_cases"],
        case,
        key="bridge_load",
        limit=top_states,
        reverse=True,
    )
    _update_top_cases(
        stats["top_ratio_cases"],
        case,
        key="critical_ratio_margin",
        limit=top_states,
        reverse=False,
    )
    _update_top_cases(
        stats["top_log_cases"],
        case,
        key="log_score_margin",
        limit=top_states,
        reverse=False,
    )
    _update_top_cases(
        stats["top_exact_cases"],
        case,
        key="critical_ratio_margin",
        limit=top_cases,
        reverse=False,
    )

    if int(case["winner_divisor_count"]) == 3:
        stats["square_branch_case_count"] = int(stats["square_branch_case_count"]) + 1
    else:
        stats["non_square_case_count"] = int(stats["non_square_case_count"]) + 1
        if int(case["winner_offset"]) > early_window:
            stats["non_square_beyond_window_count"] = int(stats["non_square_beyond_window_count"]) + 1

    winner_class_stats = stats["winner_class_stats"]
    winner_divisor_count = int(case["winner_divisor_count"])
    winner_stats = winner_class_stats.get(winner_divisor_count)
    if winner_stats is None:
        winner_class_stats[winner_divisor_count] = {
            "count": 1,
            "max_winner_offset": int(case["winner_offset"]),
            "min_critical_ratio_margin": float(case["critical_ratio_margin"]),
            "max_bridge_load": float(case["bridge_load"]),
            "representative": case,
        }
    else:
        winner_stats["count"] += 1
        winner_stats["max_winner_offset"] = max(
            int(winner_stats["max_winner_offset"]),
            int(case["winner_offset"]),
        )
        winner_stats["min_critical_ratio_margin"] = min(
            float(winner_stats["min_critical_ratio_margin"]),
            float(case["critical_ratio_margin"]),
        )
        winner_stats["max_bridge_load"] = max(
            float(winner_stats["max_bridge_load"]),
            float(case["bridge_load"]),
        )
        if float(case["critical_ratio_margin"]) < float(winner_stats["representative"]["critical_ratio_margin"]):
            winner_stats["representative"] = case

    if unsupported_low_class(
        case,
        low_class_residuals=low_class_residuals,
        high_divisor_cutoff=high_divisor_cutoff,
    ):
        stats["unsupported_low_class_case_count"] = int(stats["unsupported_low_class_case_count"]) + 1
        if len(stats["unsupported_low_class_examples"]) < 20:
            stats["unsupported_low_class_examples"].append(case)
        unsupported_low_class_stats = stats["unsupported_low_class_stats"]
        earlier_divisor_count = int(case["earlier_divisor_count"])
        unsupported_stats = unsupported_low_class_stats.get(earlier_divisor_count)
        if unsupported_stats is None:
            unsupported_low_class_stats[earlier_divisor_count] = {
                "count": 1,
                "min_critical_ratio_margin": float(case["critical_ratio_margin"]),
                "max_bridge_load": float(case["bridge_load"]),
                "representative": case,
            }
        else:
            unsupported_stats["count"] += 1
            unsupported_stats["min_critical_ratio_margin"] = min(
                float(unsupported_stats["min_critical_ratio_margin"]),
                float(case["critical_ratio_margin"]),
            )
            unsupported_stats["max_bridge_load"] = max(
                float(unsupported_stats["max_bridge_load"]),
                float(case["bridge_load"]),
            )
            if float(case["critical_ratio_margin"]) < float(unsupported_stats["representative"]["critical_ratio_margin"]):
                unsupported_stats["representative"] = case

    exact_key = exact_case_key(case)
    exact_state_stats = stats["exact_state_stats"]
    exact_stats = exact_state_stats.get(exact_key)
    if exact_stats is None:
        exact_state_stats[exact_key] = {
            "count": 1,
            "min_critical_ratio_margin": float(case["critical_ratio_margin"]),
            "max_bridge_load": float(case["bridge_load"]),
            "representative": case,
        }
    else:
        exact_stats["count"] += 1
        exact_stats["min_critical_ratio_margin"] = min(
            exact_stats["min_critical_ratio_margin"],
            float(case["critical_ratio_margin"]),
        )
        exact_stats["max_bridge_load"] = max(
            exact_stats["max_bridge_load"],
            float(case["bridge_load"]),
        )
        if float(case["critical_ratio_margin"]) < float(exact_stats["representative"]["critical_ratio_margin"]):
            exact_stats["representative"] = case

    chamber_key = chamber_state_key(
        case,
        early_window=early_window,
        high_divisor_cutoff=high_divisor_cutoff,
        low_class_residuals=low_class_residuals,
    )
    chamber_state_stats = stats["chamber_state_stats"]
    chamber_stats = chamber_state_stats.get(chamber_key)
    if chamber_stats is None:
        chamber_state_stats[chamber_key] = {
            "count": 1,
            "min_critical_ratio_margin": float(case["critical_ratio_margin"]),
            "max_bridge_load": float(case["bridge_load"]),
            "representative": case,
        }
    else:
        chamber_stats["count"] += 1
        chamber_stats["min_critical_ratio_margin"] = min(
            chamber_stats["min_critical_ratio_margin"],
            float(case["critical_ratio_margin"]),
        )
        chamber_stats["max_bridge_load"] = max(
            chamber_stats["max_bridge_load"],
            float(case["bridge_load"]),
        )
        if float(case["critical_ratio_margin"]) < float(chamber_stats["representative"]["critical_ratio_margin"]):
            chamber_stats["representative"] = case


def analyze_interval(
    *,
    lo: int,
    hi: int,
    wheel_modulus: int,
    early_window: int,
    high_divisor_cutoff: int,
    low_class_residuals: set[int],
    top_cases: int,
    top_states: int,
) -> dict[str, object]:
    """Analyze one exact interval directly."""
    if lo < 2:
        raise ValueError("interval lo must be at least 2")
    if hi <= lo:
        raise ValueError("interval hi must exceed lo")

    divisor_count = divisor_counts_segment(lo, hi)
    values = np.arange(lo, hi, dtype=np.int64)
    primes = values[divisor_count == 2]

    gap_count = 0
    earlier_candidate_count = 0
    stats = initialize_case_stats()

    for left_prime_raw, right_prime_raw in zip(primes[:-1], primes[1:]):
        left_prime = int(left_prime_raw)
        right_prime = int(right_prime_raw)
        gap = right_prime - left_prime
        if gap < 4:
            continue

        gap_count += 1
        left_index = left_prime - lo + 1
        right_index = right_prime - lo
        gap_values = values[left_index:right_index]
        gap_divisors = divisor_count[left_index:right_index]
        winner_divisor_count = int(np.min(gap_divisors))
        winner_index = int(np.flatnonzero(gap_divisors == winner_divisor_count)[0])

        for earlier_index in range(winner_index):
            earlier_candidate_count += 1
            case = analyze_gap_case(
                left_prime=left_prime,
                right_prime=right_prime,
                gap_values=gap_values,
                gap_divisors=gap_divisors,
                earlier_index=earlier_index,
                winner_index=winner_index,
                wheel_modulus=wheel_modulus,
            )
            consume_case(
                stats,
                case=case,
                early_window=early_window,
                high_divisor_cutoff=high_divisor_cutoff,
                low_class_residuals=low_class_residuals,
                top_cases=top_cases,
                top_states=top_states,
            )

    source_summary = {
        "mode": "exact_interval",
        "interval": {"lo": lo, "hi": hi},
        "gap_count": gap_count,
        "earlier_candidate_count": earlier_candidate_count,
        "retained_case_count": int(stats["hard_case_count"]),
        "top_case_limit": top_cases,
    }
    return summarize_cases(
        source_summary=source_summary,
        wheel_modulus=wheel_modulus,
        early_window=early_window,
        high_divisor_cutoff=high_divisor_cutoff,
        low_class_residuals=low_class_residuals,
        top_states=top_states,
        hard_case_count=int(stats["hard_case_count"]),
        square_branch_case_count=int(stats["square_branch_case_count"]),
        non_square_case_count=int(stats["non_square_case_count"]),
        non_square_beyond_window_count=int(stats["non_square_beyond_window_count"]),
        unsupported_low_class_case_count=int(stats["unsupported_low_class_case_count"]),
        unsupported_low_class_examples=stats["unsupported_low_class_examples"],
        unsupported_low_class_stats=stats["unsupported_low_class_stats"],
        top_bridge_cases=stats["top_bridge_cases"],
        top_ratio_cases=stats["top_ratio_cases"],
        top_log_cases=stats["top_log_cases"],
        top_exact_cases=stats["top_exact_cases"],
        exact_state_stats=stats["exact_state_stats"],
        chamber_state_stats=stats["chamber_state_stats"],
        winner_class_stats=stats["winner_class_stats"],
    )


def load_checkpoint_cases(checkpoint_dir: Path) -> list[dict[str, int | float]]:
    """Return the de-duplicated frontier cases retained by one checkpoint directory."""
    seen: dict[tuple[int, int, int, int], dict[str, int | float]] = {}
    for checkpoint_path in sorted(checkpoint_dir.glob("segment_*.json")):
        payload = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        for key in ("top_log_margin_cases", "top_ratio_margin_cases", "top_bridge_load_cases"):
            for row in payload[key]:
                case_key = (
                    int(row["left_prime"]),
                    int(row["right_prime"]),
                    int(row["winner_value"]),
                    int(row["earlier_value"]),
                )
                existing = seen.get(case_key)
                if existing is None:
                    seen[case_key] = row
                    continue
                if float(row["critical_ratio_margin"]) < float(existing["critical_ratio_margin"]):
                    seen[case_key] = row
    return list(seen.values())


def analyze_checkpoint_dir(
    *,
    checkpoint_dir: Path,
    wheel_modulus: int,
    early_window: int,
    high_divisor_cutoff: int,
    low_class_residuals: set[int],
    top_cases: int,
    top_states: int,
) -> dict[str, object]:
    """Analyze the exact frontier retained in one checkpoint directory."""
    if not checkpoint_dir.exists():
        raise ValueError(f"checkpoint directory does not exist: {checkpoint_dir}")

    checkpoint_cases = load_checkpoint_cases(checkpoint_dir)
    gap_cache: dict[tuple[int, int], tuple[np.ndarray, np.ndarray]] = {}
    stats = initialize_case_stats()

    for checkpoint_case in checkpoint_cases:
        left_prime = int(checkpoint_case["left_prime"])
        right_prime = int(checkpoint_case["right_prime"])
        gap_key = (left_prime, right_prime)
        gap_arrays = gap_cache.get(gap_key)
        if gap_arrays is None:
            gap_lo = left_prime + 1
            gap_hi = right_prime
            gap_divisors = divisor_counts_segment(gap_lo, gap_hi)
            gap_values = np.arange(gap_lo, gap_hi, dtype=np.int64)
            gap_arrays = (gap_values, gap_divisors)
            gap_cache[gap_key] = gap_arrays
        gap_values, gap_divisors = gap_arrays

        winner_value = int(checkpoint_case["winner_value"])
        winner_index = int(np.flatnonzero(gap_values == winner_value)[0])
        earlier_value = int(checkpoint_case["earlier_value"])
        earlier_index = int(np.flatnonzero(gap_values == earlier_value)[0])
        case = analyze_gap_case(
            left_prime=left_prime,
            right_prime=right_prime,
            gap_values=gap_values,
            gap_divisors=gap_divisors,
            earlier_index=earlier_index,
            winner_index=winner_index,
            wheel_modulus=wheel_modulus,
        )
        consume_case(
            stats,
            case=case,
            early_window=early_window,
            high_divisor_cutoff=high_divisor_cutoff,
            low_class_residuals=low_class_residuals,
            top_cases=top_cases,
            top_states=top_states,
        )

    source_summary = {
        "mode": "checkpoint_frontier",
        "checkpoint_dir": str(checkpoint_dir),
        "checkpoint_case_count": len(checkpoint_cases),
        "gap_count": len(gap_cache),
        "retained_case_count": int(stats["hard_case_count"]),
        "top_case_limit": top_cases,
    }
    return summarize_cases(
        source_summary=source_summary,
        wheel_modulus=wheel_modulus,
        early_window=early_window,
        high_divisor_cutoff=high_divisor_cutoff,
        low_class_residuals=low_class_residuals,
        top_states=top_states,
        hard_case_count=int(stats["hard_case_count"]),
        square_branch_case_count=int(stats["square_branch_case_count"]),
        non_square_case_count=int(stats["non_square_case_count"]),
        non_square_beyond_window_count=int(stats["non_square_beyond_window_count"]),
        unsupported_low_class_case_count=int(stats["unsupported_low_class_case_count"]),
        unsupported_low_class_examples=stats["unsupported_low_class_examples"],
        unsupported_low_class_stats=stats["unsupported_low_class_stats"],
        top_bridge_cases=stats["top_bridge_cases"],
        top_ratio_cases=stats["top_ratio_cases"],
        top_log_cases=stats["top_log_cases"],
        top_exact_cases=stats["top_exact_cases"],
        exact_state_stats=stats["exact_state_stats"],
        chamber_state_stats=stats["chamber_state_stats"],
        winner_class_stats=stats["winner_class_stats"],
    )


def main(argv: list[str] | None = None) -> int:
    """Run the exact frontier extractor."""
    parser = build_parser()
    args = parser.parse_args(argv)
    low_class_residuals = (
        set(args.low_class_residual)
        if args.low_class_residual
        else set(DEFAULT_LOW_CLASS_RESIDUALS)
    )

    if args.interval_hi is not None:
        payload = analyze_interval(
            lo=args.interval_lo,
            hi=args.interval_hi,
            wheel_modulus=args.wheel_modulus,
            early_window=args.early_window,
            high_divisor_cutoff=args.high_divisor_cutoff,
            low_class_residuals=low_class_residuals,
            top_cases=args.top_cases,
            top_states=args.top_states,
        )
    else:
        payload = analyze_checkpoint_dir(
            checkpoint_dir=args.checkpoint_dir,
            wheel_modulus=args.wheel_modulus,
            early_window=args.early_window,
            high_divisor_cutoff=args.high_divisor_cutoff,
            low_class_residuals=low_class_residuals,
            top_cases=args.top_cases,
            top_states=args.top_states,
        )

    serialized = json.dumps(payload, indent=2)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized + "\n", encoding="utf-8")

        rows_path = args.output.with_name(args.output.stem + "_rows.csv")
        header = (
            "left_prime,right_prime,gap,left_prime_mod_wheel,winner_value,winner_divisor_count,"
            "winner_offset,earlier_value,earlier_divisor_count,earlier_offset,first_d4_offset,"
            "square_margin,first_later_dominator_offset,critical_ratio_margin,bridge_load\n"
        )
        lines = [header]
        for row in payload["exact_case_rows"]:
            first_d4_offset = "" if row["first_d4_offset"] is None else str(row["first_d4_offset"])
            lines.append(
                ",".join(
                    [
                        str(row["left_prime"]),
                        str(row["right_prime"]),
                        str(row["gap"]),
                        str(row["left_prime_mod_wheel"]),
                        str(row["winner_value"]),
                        str(row["winner_divisor_count"]),
                        str(row["winner_offset"]),
                        str(row["earlier_value"]),
                        str(row["earlier_divisor_count"]),
                        str(row["earlier_offset"]),
                        first_d4_offset,
                        str(row["square_margin"]),
                        str(row["first_later_dominator_offset"]),
                        str(row["critical_ratio_margin"]),
                        str(row["bridge_load"]),
                    ]
                )
                + "\n"
            )
        rows_path.write_text("".join(lines), encoding="utf-8")

    print(serialized)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
