#!/usr/bin/env python3
"""Research-only PGS-assisted geofac revisit harness."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from sympy import isprime, prevprime


ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = ROOT / "src" / "python"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from z_band_prime_predictor import gwr_next_prime, next_prime_after


CORPUS_PATH = Path(__file__).with_name("midscale_balanced_corpus.json")
DEFAULT_OUTPUT_DIR = ROOT / "output" / "geofac_revisit"
DEFAULT_BUDGET_PRIMES = 96
DEFAULT_BUDGET_SHELLS = 24
DEFAULT_GEOfAC_J = 25
OFFICIAL_MIDSCALE_BUDGET_PRIMES = 128
OFFICIAL_MIDSCALE_BUDGET_SHELLS = 12
OFFICIAL_MIDSCALE_MAX_HALF_WIDTH = 16_384
OFFICIAL_MIDSCALE_MIN_RECALL = 0.50
OFFICIAL_RECALL_ADVANTAGE = 0.25
OFFICIAL_WALL_BREAK_METHODS = (
    "geofac_baseline",
    "wheel_baseline",
    "pgs_controller",
    "hybrid",
)
SCORE_CONTROL_METHODS = (
    "geofac_baseline",
    "wheel_baseline",
    "hybrid",
)
MAX_GWR_BOUNDARY = (1 << 63) - 2
PHI_INV = (math.sqrt(5.0) - 1.0) / 2.0
SQRT5_INV = 1.0 / math.sqrt(5.0)
SEED_DENOMINATOR = float(1 << 53)
ROW_FIELDNAMES = [
    "n",
    "p",
    "q",
    "method",
    "regime",
    "seed",
    "factor_found",
    "factor_in_budget",
    "best_factor_distance",
    "best_factor_rank",
    "shell_hit_index",
    "prime_tests",
    "candidate_tests",
    "wall_time_ms",
    "shell_widths_visited",
]


@dataclass(frozen=True)
class SemiprimeCase:
    """One deterministic semiprime case with known factors."""

    case_id: str
    n: int
    p: int
    q: int

    @property
    def sqrt_n(self) -> int:
        return int(math.isqrt(self.n))


@dataclass
class CaseMetrics:
    """One completed case evaluation."""

    row: dict[str, object]
    prime_tests_before_shell_hit: int | None


@dataclass(frozen=True)
class SummaryOptions:
    """One immutable run configuration."""

    method: str
    regime: str
    case_count: int
    seed: int
    budget_primes: int
    budget_shells: int
    max_half_width: int


def _load_committed_cases(path: Path) -> tuple[SemiprimeCase, ...]:
    """Load one committed deterministic semiprime corpus."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    return tuple(
        SemiprimeCase(
            case_id=str(item["case_id"]),
            n=int(item["n"]),
            p=int(item["p"]),
            q=int(item["q"]),
        )
        for item in payload
    )


TOY_BALANCED_CASES = (
    SemiprimeCase(
        case_id="toy_gate_30",
        n=1_073_217_479,
        p=32_749,
        q=32_771,
    ),
    SemiprimeCase(
        case_id="toy_arctan_a",
        n=169_435_573_207,
        p=165_707,
        q=1_022_501,
    ),
    SemiprimeCase(
        case_id="toy_arctan_b",
        n=208_983_991_939,
        p=332_011,
        q=629_449,
    ),
    SemiprimeCase(
        case_id="toy_arctan_c",
        n=166_062_540_197,
        p=314_263,
        q=528_419,
    ),
)

MIDSCALE_BALANCED_CASES = _load_committed_cases(CORPUS_PATH)

CHALLENGE_LIKE_CASES = (
    SemiprimeCase(
        case_id="challenge_shell_89",
        n=309_485_361_667_157_571_406_375_357,
        p=17_592_181_044_401,
        q=17_592_211_044_557,
    ),
    SemiprimeCase(
        case_id="challenge_unbalanced_83",
        n=5_000_000_115_994_000_670_184_277,
        p=1_000_000_012_313,
        q=5_000_000_054_429,
    ),
    SemiprimeCase(
        case_id="challenge_127_archive",
        n=137_524_771_864_208_156_028_430_259_349_934_309_717,
        p=10_508_623_501_177_419_659,
        q=13_086_849_276_577_416_863,
    ),
)

REGIME_CASE_MAP = {
    "toy_balanced": TOY_BALANCED_CASES,
    "midscale_balanced": MIDSCALE_BALANCED_CASES,
    "challenge_like_unbalanced": CHALLENGE_LIKE_CASES,
}

REGIME_DEFAULT_MAX_HALF_WIDTH = {
    "toy_balanced": 1 << 20,
    "midscale_balanced": 1 << 22,
    "challenge_like_unbalanced": 2_000_000_000_000_000_000,
}


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description="Research-only PGS-assisted geofac revisit harness.",
    )
    parser.add_argument(
        "--method",
        choices=OFFICIAL_WALL_BREAK_METHODS,
        required=True,
        help="Search method to evaluate.",
    )
    parser.add_argument(
        "--regime",
        choices=("toy_balanced", "midscale_balanced", "challenge_like_unbalanced"),
        required=True,
        help="Deterministic semiprime regime to evaluate.",
    )
    parser.add_argument(
        "--cases",
        type=int,
        default=None,
        help="Number of leading deterministic cases to evaluate.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=0,
        help="Deterministic integer seed for quasi-Monte Carlo ordering.",
    )
    parser.add_argument(
        "--budget-primes",
        type=int,
        default=DEFAULT_BUDGET_PRIMES,
        help="Total divisibility-test budget across all shells.",
    )
    parser.add_argument(
        "--budget-shells",
        type=int,
        default=DEFAULT_BUDGET_SHELLS,
        help="Maximum number of shells to visit.",
    )
    parser.add_argument(
        "--max-half-width",
        type=int,
        default=None,
        help="Maximum shell half-width. Defaults by regime.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for the JSONL and JSON artifacts.",
    )
    return parser


def _seed_fraction(seed: int, salt: int) -> float:
    """Return one deterministic fraction in [0, 1)."""
    payload = f"{seed}:{salt}".encode("utf-8")
    digest = hashlib.sha256(payload).digest()
    value = int.from_bytes(digest[:8], "big") >> 11
    return value / SEED_DENOMINATOR


def _wheel_open_mod30(n: int) -> bool:
    """Return whether n lies on the odd mod-30 wheel."""
    if n <= 1 or n % 2 == 0:
        return False
    residue = n % 30
    return residue in (1, 7, 11, 13, 17, 19, 23, 29)


def _base_half_width(sqrt_n: int) -> int:
    """Return the default base shell half-width."""
    return max(64, math.ceil(math.log(sqrt_n) ** 2))


def _shell_half_widths(sqrt_n: int, budget_shells: int, max_half_width: int) -> list[int]:
    """Return the geometric shell ladder."""
    if budget_shells < 1:
        raise ValueError("budget_shells must be at least 1")
    if max_half_width < 64:
        raise ValueError("max_half_width must be at least 64")

    widths: list[int] = []
    width = _base_half_width(sqrt_n)
    for _ in range(budget_shells):
        current = min(width, max_half_width)
        if widths and current == widths[-1]:
            break
        widths.append(current)
        if current >= max_half_width:
            break
        width *= 2
    return widths


def _shell_intervals(
    sqrt_n: int,
    inner_half_width: int,
    outer_half_width: int,
) -> tuple[tuple[int, int] | None, tuple[int, int] | None]:
    """Return the left and right shell annuli."""
    if outer_half_width <= inner_half_width:
        raise ValueError("outer_half_width must exceed inner_half_width")

    left_lo = max(2, sqrt_n - outer_half_width)
    left_hi = sqrt_n - inner_half_width - 1
    right_lo = sqrt_n + inner_half_width + 1
    right_hi = sqrt_n + outer_half_width

    left = (left_lo, left_hi) if left_lo <= left_hi else None
    right = (right_lo, right_hi) if right_lo <= right_hi else None
    return left, right


def _dirichlet_kernel(x: float, j: int) -> float:
    """Return the archive-style Dirichlet kernel."""
    total = 1.0
    for k in range(1, j + 1):
        total += 2.0 * math.cos(k * x)
    return total


def _zeta_modulation(x: float, n: int) -> float:
    """Return the archive-style bit-derived zeta modulation."""
    modulation = 1.0
    for k in range(8):
        if (n >> k) & 1:
            modulation += 0.5 * math.cos((k + 1) * x * 1.618 + float(k + 1) / 13.0)
    return abs(modulation)


def geofac_resonance_score(n: int, candidate: int) -> float:
    """Return one archive-derived resonance score."""
    frac = (n % candidate) / float(candidate)
    x = 2.0 * math.pi * frac
    return abs(_dirichlet_kernel(x, DEFAULT_GEOfAC_J)) * _zeta_modulation(x, n)


def pseudo_random_score(seed: int, n: int, candidate: int) -> float:
    """Return one deterministic pseudo-random control score."""
    payload = f"{seed}:{n}:{candidate}".encode("utf-8")
    digest = hashlib.sha256(payload).digest()
    value = int.from_bytes(digest[:8], "big")
    return value / float(1 << 64)


def _candidate_sort_key(score: float, candidate: int, sqrt_n: int) -> tuple[float, int, int]:
    """Return the stable descending rank key for one scored candidate."""
    return (-score, abs(candidate - sqrt_n), candidate)


def _qmc_shell_candidates(
    sqrt_n: int,
    inner_half_width: int,
    outer_half_width: int,
    count: int,
    seed: int,
    *,
    wheel_only: bool,
) -> list[int]:
    """Return one deterministic QMC-style candidate set from one shell."""
    if count < 1:
        return []

    span = outer_half_width - inner_half_width
    if span < 1:
        return []

    candidates: list[int] = []
    seen: set[int] = set()
    phase_mag = _seed_fraction(seed, outer_half_width ^ (count << 8))
    phase_side = _seed_fraction(seed, inner_half_width ^ 0x9E3779B97F4A7C15)
    max_attempts = max(64, count * 32)

    for index in range(max_attempts):
        magnitude_u = (phase_mag + (index + 1) * PHI_INV) % 1.0
        side_u = (phase_side + (index + 1) * SQRT5_INV) % 1.0
        magnitude = inner_half_width + 1 + int(magnitude_u * span)
        sign = -1 if side_u < 0.5 else 1
        candidate = sqrt_n + sign * magnitude

        if candidate <= 1 or candidate in seen:
            continue
        if candidate % 2 == 0:
            candidate += 1 if sign > 0 else -1
        if abs(candidate - sqrt_n) <= inner_half_width or abs(candidate - sqrt_n) > outer_half_width:
            continue
        if candidate <= 1 or candidate in seen:
            continue
        if wheel_only:
            if not _wheel_open_mod30(candidate):
                continue
        elif candidate % 2 == 0:
            continue

        seen.add(candidate)
        candidates.append(candidate)
        if len(candidates) >= count:
            break

    return candidates


def _left_prime_seed(boundary: int, lower_bound: int) -> int | None:
    """Return the nearest prime at or below one boundary inside one shell."""
    if boundary < 2:
        return None
    try:
        candidate = int(prevprime(boundary + 1))
    except ValueError:
        return None
    if candidate < lower_bound:
        return None
    return candidate


def _next_wheel_open_candidate(boundary: int) -> int:
    """Return the first odd mod-30 wheel-open candidate strictly above boundary."""
    candidate = max(7, boundary + 1)
    if candidate % 2 == 0:
        candidate += 1
    while not _wheel_open_mod30(candidate):
        candidate += 2
    return candidate


def _next_prime_after_revisit(boundary: int) -> int:
    """Return the next prime after boundary on the revisit runtime path."""
    if boundary <= MAX_GWR_BOUNDARY:
        return int(next_prime_after(int(boundary)))

    candidate = _next_wheel_open_candidate(boundary)
    while not isprime(candidate):
        candidate = _next_wheel_open_candidate(candidate)
    return candidate


def _next_prime_successor_revisit(prime: int) -> int:
    """Return the prime immediately after prime on the revisit runtime path."""
    if prime <= MAX_GWR_BOUNDARY:
        return int(gwr_next_prime(int(prime)))

    candidate = _next_wheel_open_candidate(prime)
    while not isprime(candidate):
        candidate = _next_wheel_open_candidate(candidate)
    return candidate


def _right_prime_seed(boundary: int, upper_bound: int) -> int | None:
    """Return the nearest prime strictly above one boundary inside one shell."""
    candidate = _next_prime_after_revisit(boundary)
    if candidate > upper_bound:
        return None
    return candidate


def _pgs_shell_prime_candidates(
    sqrt_n: int,
    inner_half_width: int,
    outer_half_width: int,
    limit: int | None = None,
) -> list[int]:
    """Return one deterministic center-out prime sequence from one shell."""
    if limit is not None and limit < 1:
        return []

    left_interval, right_interval = _shell_intervals(
        sqrt_n,
        inner_half_width,
        outer_half_width,
    )
    left = None
    right = None
    left_floor = None
    right_ceiling = None

    if left_interval is not None:
        left_floor, left_boundary = left_interval[0], left_interval[1]
        left = _left_prime_seed(left_boundary, left_floor)
    if right_interval is not None:
        right_boundary, right_ceiling = right_interval[0], right_interval[1]
        right = _right_prime_seed(right_boundary - 1, right_ceiling)

    candidates: list[int] = []
    while left is not None or right is not None:
        if limit is not None and len(candidates) >= limit:
            break

        left_distance = abs(left - sqrt_n) if left is not None else None
        right_distance = abs(right - sqrt_n) if right is not None else None

        choose_left = False
        if left is not None and right is None:
            choose_left = True
        elif left is not None and right is not None:
            choose_left = bool(left_distance <= right_distance)

        if choose_left:
            candidates.append(int(left))
            if left_floor is None or left <= left_floor:
                left = None
            else:
                left = _left_prime_seed(left - 2, left_floor)
        else:
            candidates.append(int(right))
            if right_ceiling is None or right >= right_ceiling:
                right = None
            else:
                next_right = _next_prime_successor_revisit(int(right))
                right = next_right if next_right <= right_ceiling else None

    return candidates


def _median_or_none(values: list[int]) -> float | None:
    """Return the median of one integer list or None."""
    return float(statistics.median(values)) if values else None


def _record_tested_candidate(
    candidate: int,
    case: SemiprimeCase,
    shell_index: int,
    rank: int,
    best_factor_distance: int | None,
    best_factor_rank: int | None,
    shell_hit_index: int | None,
) -> tuple[int, int | None, int | None]:
    """Update per-case best-distance and shell-hit metrics."""
    distance = min(abs(candidate - case.p), abs(candidate - case.q))
    if best_factor_distance is None or distance < best_factor_distance:
        best_factor_distance = distance
        best_factor_rank = rank
    if distance == 0 and shell_hit_index is None:
        shell_hit_index = shell_index
    return best_factor_distance, best_factor_rank, shell_hit_index


def _score_candidates(
    candidates: list[int],
    case: SemiprimeCase,
    sqrt_n: int,
    seed: int,
    *,
    score_kind: str,
) -> list[int]:
    """Return the candidates in deterministic descending score order."""
    if score_kind == "none":
        return candidates
    if score_kind not in ("geofac", "random_control"):
        raise ValueError(f"unsupported score_kind {score_kind}")

    scored: list[tuple[tuple[float, int, int], int]] = []
    for candidate in candidates:
        if score_kind == "geofac":
            score = geofac_resonance_score(case.n, candidate)
        else:
            score = pseudo_random_score(seed, case.n, candidate)
        scored.append((_candidate_sort_key(score, candidate, sqrt_n), candidate))
    scored.sort(key=lambda item: item[0])
    return [candidate for _, candidate in scored]


def _evaluate_case(
    case: SemiprimeCase,
    regime: str,
    method: str,
    seed: int,
    budget_primes: int,
    budget_shells: int,
    max_half_width: int,
    *,
    score_kind: str = "geofac",
) -> CaseMetrics:
    """Evaluate one case under one method."""
    if budget_primes < 1:
        raise ValueError("budget_primes must be at least 1")
    if budget_shells < 1:
        raise ValueError("budget_shells must be at least 1")

    sqrt_n = case.sqrt_n
    shell_widths = _shell_half_widths(sqrt_n, budget_shells, max_half_width)
    candidate_tests = 0
    prime_tests = 0
    factor_found = False
    factor_in_budget = False
    best_factor_distance: int | None = None
    best_factor_rank: int | None = None
    shell_hit_index: int | None = None
    prime_tests_before_shell_hit: int | None = None
    shell_widths_visited: list[int] = []
    started = time.perf_counter()

    for shell_index, outer_half_width in enumerate(shell_widths, start=1):
        if candidate_tests >= budget_primes:
            break

        shell_widths_visited.append(outer_half_width)
        inner_half_width = 0 if shell_index == 1 else shell_widths[shell_index - 2]

        if method == "geofac_baseline":
            remaining_budget = budget_primes - candidate_tests
            remaining_shells = len(shell_widths) - shell_index + 1
            shell_quota = max(1, remaining_budget // remaining_shells)
            shell_candidates = _qmc_shell_candidates(
                sqrt_n,
                inner_half_width,
                outer_half_width,
                shell_quota,
                seed + shell_index,
                wheel_only=False,
            )
            ordered_candidates = _score_candidates(
                shell_candidates,
                case,
                sqrt_n,
                seed,
                score_kind=score_kind,
            )
        elif method == "wheel_baseline":
            remaining_budget = budget_primes - candidate_tests
            remaining_shells = len(shell_widths) - shell_index + 1
            shell_quota = max(1, remaining_budget // remaining_shells)
            shell_candidates = _qmc_shell_candidates(
                sqrt_n,
                inner_half_width,
                outer_half_width,
                shell_quota,
                seed + shell_index,
                wheel_only=True,
            )
            ordered_candidates = _score_candidates(
                shell_candidates,
                case,
                sqrt_n,
                seed,
                score_kind=score_kind,
            )
        elif method == "pgs_controller":
            ordered_candidates = _pgs_shell_prime_candidates(
                sqrt_n,
                inner_half_width,
                outer_half_width,
            )
        elif method == "hybrid":
            shell_candidates = _pgs_shell_prime_candidates(
                sqrt_n,
                inner_half_width,
                outer_half_width,
            )
            ordered_candidates = _score_candidates(
                shell_candidates,
                case,
                sqrt_n,
                seed,
                score_kind=score_kind,
            )
        else:
            raise ValueError(f"unsupported method {method}")

        for candidate in ordered_candidates:
            if candidate_tests >= budget_primes:
                break

            candidate_tests += 1
            if method in ("pgs_controller", "hybrid"):
                prime_tests += 1
            else:
                prime_tests += int(isprime(candidate))

            (
                best_factor_distance,
                best_factor_rank,
                shell_hit_index,
            ) = _record_tested_candidate(
                candidate,
                case,
                shell_index,
                candidate_tests,
                best_factor_distance,
                best_factor_rank,
                shell_hit_index,
            )

            if case.n % candidate == 0 and candidate not in (1, case.n):
                factor_found = True
                factor_in_budget = True
                if prime_tests_before_shell_hit is None:
                    prime_tests_before_shell_hit = prime_tests
                break

        if factor_found:
            break

    elapsed_ms = (time.perf_counter() - started) * 1000.0
    row = {
        "n": case.n,
        "p": case.p,
        "q": case.q,
        "method": method,
        "regime": regime,
        "seed": seed,
        "factor_found": factor_found,
        "factor_in_budget": factor_in_budget,
        "best_factor_distance": best_factor_distance,
        "best_factor_rank": best_factor_rank,
        "shell_hit_index": shell_hit_index,
        "prime_tests": prime_tests,
        "candidate_tests": candidate_tests,
        "wall_time_ms": elapsed_ms,
        "shell_widths_visited": shell_widths_visited,
    }
    return CaseMetrics(
        row=row,
        prime_tests_before_shell_hit=prime_tests_before_shell_hit,
    )


def _selected_cases(regime: str, count: int | None) -> list[SemiprimeCase]:
    """Return the leading deterministic cases for one regime."""
    all_cases = list(REGIME_CASE_MAP[regime])
    if count is None:
        return all_cases
    if count < 1:
        raise ValueError("cases must be at least 1")
    return all_cases[: min(count, len(all_cases))]


def _summarize_rows(
    options: SummaryOptions,
    rows: list[CaseMetrics],
    *,
    baseline_reference: list[CaseMetrics] | None,
    false_signal_control: list[CaseMetrics] | None,
    acceptance: dict[str, object] | None,
) -> dict[str, object]:
    """Build the summary JSON payload."""
    public_rows = [metric.row for metric in rows]
    factor_in_budget_count = sum(int(bool(row["factor_in_budget"])) for row in public_rows)
    factor_found_count = sum(int(bool(row["factor_found"])) for row in public_rows)
    best_factor_ranks = [
        int(row["best_factor_rank"])
        for row in public_rows
        if row["best_factor_rank"] is not None
    ]
    shell_hit_indices = [
        int(row["shell_hit_index"])
        for row in public_rows
        if row["shell_hit_index"] is not None
    ]
    best_factor_distances = [
        int(row["best_factor_distance"])
        for row in public_rows
        if row["best_factor_distance"] is not None
    ]
    prime_tests_before_hit = [
        int(metric.prime_tests_before_shell_hit)
        for metric in rows
        if metric.prime_tests_before_shell_hit is not None
    ]
    total_candidate_tests = sum(int(row["candidate_tests"]) for row in public_rows)
    total_prime_tests = sum(int(row["prime_tests"]) for row in public_rows)
    total_wall_time_ms = sum(float(row["wall_time_ms"]) for row in public_rows)

    candidate_count_reduction = 0.0 if options.method == "geofac_baseline" else None
    prime_test_reduction = 0.0 if options.method == "geofac_baseline" else None
    if baseline_reference is not None:
        reference_candidate_tests = sum(
            int(metric.row["candidate_tests"]) for metric in baseline_reference
        )
        reference_prime_tests = sum(int(metric.row["prime_tests"]) for metric in baseline_reference)
        if reference_candidate_tests > 0:
            candidate_count_reduction = (
                reference_candidate_tests - total_candidate_tests
            ) / reference_candidate_tests
        if reference_prime_tests > 0:
            prime_test_reduction = (
                reference_prime_tests - total_prime_tests
            ) / reference_prime_tests

    false_signal_payload = None
    if false_signal_control is not None:
        control_rows = [metric.row for metric in false_signal_control]
        control_recall = sum(int(bool(row["factor_in_budget"])) for row in control_rows) / len(
            control_rows
        )
        control_ranks = [
            int(row["best_factor_rank"])
            for row in control_rows
            if row["best_factor_rank"] is not None
        ]
        control_prime_before_hit = [
            int(metric.prime_tests_before_shell_hit)
            for metric in false_signal_control
            if metric.prime_tests_before_shell_hit is not None
        ]
        method_recall = factor_in_budget_count / len(public_rows)
        method_rank = _median_or_none(best_factor_ranks)
        control_rank = _median_or_none(control_ranks)
        method_prime_before_hit = _median_or_none(prime_tests_before_hit)
        control_prime_before_hit_median = _median_or_none(control_prime_before_hit)
        survives = False
        if method_recall > control_recall:
            survives = True
        elif method_recall == control_recall:
            if method_rank is not None and control_rank is not None and method_rank < control_rank:
                survives = True
            elif (
                method_rank == control_rank
                and method_prime_before_hit is not None
                and control_prime_before_hit_median is not None
                and method_prime_before_hit < control_prime_before_hit_median
            ):
                survives = True
        false_signal_payload = {
            "method": options.method,
            "control_mode": "pseudo_random_rerank",
            "factor_in_budget_recall": control_recall,
            "median_best_factor_rank": control_rank,
            "median_prime_tests_before_shell_hit": control_prime_before_hit_median,
            "survives_false_signal_control": survives,
        }

    return {
        "method": options.method,
        "regime": options.regime,
        "case_count": len(public_rows),
        "seed": options.seed,
        "budget_primes": options.budget_primes,
        "budget_shells": options.budget_shells,
        "max_half_width": options.max_half_width,
        "factor_found_recall": factor_found_count / len(public_rows),
        "factor_in_budget_recall": factor_in_budget_count / len(public_rows),
        "median_best_factor_distance": _median_or_none(best_factor_distances),
        "median_best_factor_rank": _median_or_none(best_factor_ranks),
        "median_shell_hit_index": _median_or_none(shell_hit_indices),
        "median_prime_tests_before_shell_hit": _median_or_none(prime_tests_before_hit),
        "total_candidate_tests": total_candidate_tests,
        "total_prime_tests": total_prime_tests,
        "candidate_count_reduction_vs_geofac_baseline": candidate_count_reduction,
        "prime_test_reduction_vs_geofac_baseline": prime_test_reduction,
        "total_wall_time_ms": total_wall_time_ms,
        "false_signal_control": false_signal_payload,
        "acceptance": acceptance,
    }


def _run_method_core(
    method: str,
    regime: str,
    cases: list[SemiprimeCase],
    seed: int,
    budget_primes: int,
    budget_shells: int,
    max_half_width: int,
    *,
    acceptance: dict[str, object] | None = None,
) -> tuple[list[CaseMetrics], dict[str, object]]:
    """Run one method on one explicit case list."""
    rows = [
        _evaluate_case(
            case,
            regime,
            method,
            seed,
            budget_primes,
            budget_shells,
            max_half_width,
        )
        for case in cases
    ]

    baseline_reference = None
    if method != "geofac_baseline":
        baseline_reference = [
            _evaluate_case(
                case,
                regime,
                "geofac_baseline",
                seed,
                budget_primes,
                budget_shells,
                max_half_width,
            )
            for case in cases
        ]

    false_signal_control = None
    if method in SCORE_CONTROL_METHODS:
        false_signal_control = [
            _evaluate_case(
                case,
                regime,
                method,
                seed,
                budget_primes,
                budget_shells,
                max_half_width,
                score_kind="random_control",
            )
            for case in cases
        ]

    summary = _summarize_rows(
        SummaryOptions(
            method=method,
            regime=regime,
            case_count=len(cases),
            seed=seed,
            budget_primes=budget_primes,
            budget_shells=budget_shells,
            max_half_width=max_half_width,
        ),
        rows,
        baseline_reference=baseline_reference,
        false_signal_control=false_signal_control,
        acceptance=acceptance,
    )
    return rows, summary


def _control_rows_for_method(
    method: str,
    regime: str,
    cases: list[SemiprimeCase],
    seed: int,
    budget_primes: int,
    budget_shells: int,
    max_half_width: int,
) -> list[CaseMetrics] | None:
    """Return the pseudo-random control rows for one score-driven method."""
    if method not in SCORE_CONTROL_METHODS:
        return None
    return [
        _evaluate_case(
            case,
            regime,
            method,
            seed,
            budget_primes,
            budget_shells,
            max_half_width,
            score_kind="random_control",
        )
        for case in cases
    ]


def _is_official_midscale_audit(
    regime: str,
    cases: list[SemiprimeCase],
    budget_primes: int,
    budget_shells: int,
    max_half_width: int,
) -> bool:
    """Return whether one run matches the official wall-break audit."""
    if regime != "midscale_balanced":
        return False
    if budget_primes != OFFICIAL_MIDSCALE_BUDGET_PRIMES:
        return False
    if budget_shells != OFFICIAL_MIDSCALE_BUDGET_SHELLS:
        return False
    if max_half_width != OFFICIAL_MIDSCALE_MAX_HALF_WIDTH:
        return False
    return [case.case_id for case in cases] == [case.case_id for case in MIDSCALE_BALANCED_CASES]


def run_midscale_wall_break_audit(seed: int = 0) -> dict[str, object]:
    """Run the fixed midscale wall-break audit across all four methods."""
    cases = list(MIDSCALE_BALANCED_CASES)
    method_payloads: dict[str, dict[str, object]] = {}

    for method in OFFICIAL_WALL_BREAK_METHODS:
        rows, summary = _run_method_core(
            method,
            "midscale_balanced",
            cases,
            seed,
            OFFICIAL_MIDSCALE_BUDGET_PRIMES,
            OFFICIAL_MIDSCALE_BUDGET_SHELLS,
            OFFICIAL_MIDSCALE_MAX_HALF_WIDTH,
        )
        method_payloads[method] = {
            "rows": rows,
            "summary": summary,
        }

    geofac_recall = float(
        method_payloads["geofac_baseline"]["summary"]["factor_in_budget_recall"]
    )
    wheel_recall = float(method_payloads["wheel_baseline"]["summary"]["factor_in_budget_recall"])

    for method in OFFICIAL_WALL_BREAK_METHODS:
        rows = method_payloads[method]["rows"]
        summary = method_payloads[method]["summary"]
        canonical_recovered = bool(rows[0].row["factor_in_budget"])
        recall = float(summary["factor_in_budget_recall"])
        control_rows = _control_rows_for_method(
            method,
            "midscale_balanced",
            cases,
            seed,
            OFFICIAL_MIDSCALE_BUDGET_PRIMES,
            OFFICIAL_MIDSCALE_BUDGET_SHELLS,
            OFFICIAL_MIDSCALE_MAX_HALF_WIDTH,
        )
        if method == "pgs_controller":
            survives_false_signal_control = True
        else:
            control = summary["false_signal_control"]
            control_canonical_recovered = bool(
                control_rows is not None and control_rows[0].row["factor_in_budget"]
            )
            control_recall = float(control["factor_in_budget_recall"]) if control is not None else 0.0
            control_wall_break_like_passed = (
                control_canonical_recovered
                and control_recall >= OFFICIAL_MIDSCALE_MIN_RECALL
                and (control_recall - geofac_recall) >= OFFICIAL_RECALL_ADVANTAGE
                and (control_recall - wheel_recall) >= OFFICIAL_RECALL_ADVANTAGE
            )
            survives_false_signal_control = bool(
                control is not None
                and control["survives_false_signal_control"]
                and not control_wall_break_like_passed
            )
        acceptance = {
            "canonical_47bit_recovered": canonical_recovered,
            "expanded_midscale_recall": recall,
            "beats_geofac_baseline": (recall - geofac_recall) >= OFFICIAL_RECALL_ADVANTAGE,
            "beats_wheel_baseline": (recall - wheel_recall) >= OFFICIAL_RECALL_ADVANTAGE,
            "survives_false_signal_control": survives_false_signal_control,
            "wall_break_passed": (
                canonical_recovered
                and recall >= OFFICIAL_MIDSCALE_MIN_RECALL
                and (recall - geofac_recall) >= OFFICIAL_RECALL_ADVANTAGE
                and (recall - wheel_recall) >= OFFICIAL_RECALL_ADVANTAGE
                and survives_false_signal_control
            ),
        }
        summary["acceptance"] = acceptance

    return {
        "regime": "midscale_balanced",
        "seed": seed,
        "budget_primes": OFFICIAL_MIDSCALE_BUDGET_PRIMES,
        "budget_shells": OFFICIAL_MIDSCALE_BUDGET_SHELLS,
        "max_half_width": OFFICIAL_MIDSCALE_MAX_HALF_WIDTH,
        "methods": method_payloads,
    }


def run_revisit(
    method: str,
    regime: str,
    case_count: int | None,
    seed: int,
    budget_primes: int,
    budget_shells: int,
    max_half_width: int | None,
) -> tuple[list[CaseMetrics], dict[str, object]]:
    """Run the full revisit evaluation without writing artifacts."""
    resolved_max_half_width = (
        REGIME_DEFAULT_MAX_HALF_WIDTH[regime]
        if max_half_width is None
        else int(max_half_width)
    )
    cases = _selected_cases(regime, case_count)
    rows, summary = _run_method_core(
        method,
        regime,
        cases,
        seed,
        budget_primes,
        budget_shells,
        resolved_max_half_width,
    )

    if _is_official_midscale_audit(
        regime,
        cases,
        budget_primes,
        budget_shells,
        resolved_max_half_width,
    ):
        audit = run_midscale_wall_break_audit(seed)
        acceptance = dict(audit["methods"][method]["summary"]["acceptance"])
        summary["acceptance"] = acceptance

    return rows, summary


def write_rows_jsonl(output_path: Path, rows: list[CaseMetrics]) -> None:
    """Write the per-case rows as JSONL."""
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        for metric in rows:
            handle.write(json.dumps(metric.row, sort_keys=False) + "\n")


def write_rows_csv(output_path: Path, rows: list[CaseMetrics]) -> None:
    """Write the per-case rows as CSV."""
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=ROW_FIELDNAMES, lineterminator="\n")
        writer.writeheader()
        for metric in rows:
            writer.writerow({name: metric.row.get(name) for name in ROW_FIELDNAMES})


def main(argv: list[str] | None = None) -> int:
    """Run the revisit harness and emit artifacts."""
    parser = build_parser()
    args = parser.parse_args(argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    rows, summary = run_revisit(
        method=args.method,
        regime=args.regime,
        case_count=args.cases,
        seed=args.seed,
        budget_primes=args.budget_primes,
        budget_shells=args.budget_shells,
        max_half_width=args.max_half_width,
    )

    file_stem = f"{args.method}_{args.regime}"
    rows_jsonl_path = args.output_dir / f"{file_stem}_rows.jsonl"
    rows_csv_path = args.output_dir / f"{file_stem}_rows.csv"
    summary_path = args.output_dir / f"{file_stem}_summary.json"

    write_rows_jsonl(rows_jsonl_path, rows)
    write_rows_csv(rows_csv_path, rows)
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
