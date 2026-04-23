#!/usr/bin/env python3
"""Research-only PGS-first scale-up harness."""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
import time
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import mpmath as mp
from sympy import divisor_count, isprime, nextprime, prevprime


ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = ROOT / "src" / "python"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from z_band_prime_predictor import gwr_next_prime, gwr_predict, next_prime_after


CORPUS_PATH = Path(__file__).with_name("scaleup_corpus.json")
DEFAULT_OUTPUT_DIR = ROOT / "output" / "geofac_scaleup"
FIXED_POINT_BITS = 40
MAX_GWR_BOUNDARY = (1 << 63) - 2
ARCHIVED_CASE_ID = "s127_archived_shape_archived"
TARGET_MODERATE_LOG = 0.7
ARCHIVED_127_LOG = math.log(13_086_849_276_577_416_863 / 10_508_623_501_177_419_659)
OFFICIAL_127_ROUTER_SEED_BUDGETS = {
    1: 1,
    2: 4,
    3: 8,
}
ROUTER_MODES = (
    "audited_family_prior",
    "pure_pgs",
)
ROW_FIELDNAMES = [
    "n",
    "p",
    "q",
    "router",
    "router_mode",
    "scale_bits",
    "rung",
    "factor_recovered",
    "factor_recovered_route_order",
    "factor_in_final_window",
    "best_window_rank",
    "final_window_bits",
    "local_prime_tests",
    "local_prime_tests_route_order",
    "router_probe_count",
    "winning_window_factor_present",
    "winning_window_factor_route_rank",
    "winning_window_factor_recovery_rank",
    "wall_time_ms",
]


@dataclass(frozen=True)
class ScaleupCase:
    """One deterministic scale-up case."""

    case_id: str
    family: str
    case_bits: int
    n: int
    p: int
    q: int

    @property
    def small_factor(self) -> int:
        return min(self.p, self.q)

    @property
    def small_factor_log2(self) -> float:
        return math.log2(self.small_factor)


@dataclass(frozen=True)
class RungConfig:
    """One immutable zoom-rung configuration."""

    widths: tuple[float, ...]
    scan_points: int
    beam_width: int
    top_windows: int
    router_seed_budget: int
    local_seed_budget: int
    router_only_prime_budget: int


@dataclass(frozen=True)
class PrimeCluster:
    """One recovered-prime cluster inside one routed interval."""

    recovered_prime: int
    support_count: int
    residue_ratio: float
    median_seed_distance: float
    tie_break_order: int


@dataclass(frozen=True)
class BitWindow:
    """One routed factor-size window with its strongest PGS evidence."""

    center_log2: float
    width_bits: float
    evidence: PrimeCluster | None
    midpoint: int | None = None


@dataclass
class ScaleupMetrics:
    """One completed case evaluation."""

    row: dict[str, object]


RUNG_CONFIGS = {
    1: RungConfig(
        widths=(16.0, 4.0, 1.0),
        scan_points=3,
        beam_width=4,
        top_windows=4,
        router_seed_budget=16,
        local_seed_budget=256,
        router_only_prime_budget=4096,
    ),
    2: RungConfig(
        widths=(16.0, 4.0, 1.0, 0.25),
        scan_points=3,
        beam_width=4,
        top_windows=4,
        router_seed_budget=32,
        local_seed_budget=1024,
        router_only_prime_budget=16384,
    ),
    3: RungConfig(
        widths=(16.0, 4.0, 1.0, 0.25, 0.0625),
        scan_points=3,
        beam_width=4,
        top_windows=4,
        router_seed_budget=64,
        local_seed_budget=4096,
        router_only_prime_budget=65536,
    ),
}


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description="Research-only PGS-first scale-up harness.",
    )
    parser.add_argument(
        "--scale-bits",
        type=int,
        choices=(127, 160, 192, 224, 256, 384, 512, 768, 1024, 1536, 2048, 3072, 4096),
        required=True,
        help="Stage corpus to evaluate.",
    )
    parser.add_argument(
        "--rung",
        type=int,
        choices=(1, 2, 3),
        required=True,
        help="Zoom ladder rung.",
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
        help="Deterministic seed recorded in the summary.",
    )
    parser.add_argument(
        "--router-mode",
        choices=ROUTER_MODES,
        default="audited_family_prior",
        help="Router mode to evaluate.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for JSONL and summary artifacts.",
    )
    return parser


def _load_corpus(path: Path) -> dict[int, tuple[ScaleupCase, ...]]:
    """Load the committed stage corpus."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    corpus: dict[int, tuple[ScaleupCase, ...]] = {}
    for stage_bits_text, rows in payload.items():
        stage_bits = int(stage_bits_text)
        corpus[stage_bits] = tuple(
            ScaleupCase(
                case_id=str(row["case_id"]),
                family=str(row["family"]),
                case_bits=int(row["case_bits"]),
                n=int(row["n"]),
                p=int(row["p"]),
                q=int(row["q"]),
            )
            for row in rows
        )
    return corpus


CORPUS = _load_corpus(CORPUS_PATH)


def _selected_cases(scale_bits: int, count: int | None) -> list[ScaleupCase]:
    """Return the leading deterministic cases for one stage."""
    all_cases = list(CORPUS[scale_bits])
    if count is None:
        return all_cases
    if count < 1:
        raise ValueError("cases must be at least 1")
    return all_cases[: min(count, len(all_cases))]


@lru_cache(maxsize=65536)
def _anchor_from_log2(log2_value: float, *, rounding: str) -> int:
    """Return one deterministic integer near 2**log2_value."""
    with mp.workdps(80):
        value = mp.power(2, mp.mpf(str(log2_value)))
        if rounding == "floor":
            return int(mp.floor(value))
        if rounding == "ceil":
            return int(mp.ceil(value))
        if rounding == "nearest":
            return int(mp.nint(value))
        raise ValueError(f"unsupported rounding {rounding}")


def _linspace(start: float, end: float, count: int) -> list[float]:
    """Return one deterministic floating-point grid."""
    if count < 1:
        raise ValueError("count must be at least 1")
    if count == 1:
        return [start]
    step = (end - start) / float(count - 1)
    return [start + index * step for index in range(count)]


def _cluster_sort_key(cluster: PrimeCluster) -> tuple[int, float, float, int, int]:
    """Return the exact deterministic cluster ranking key."""
    return (
        -cluster.support_count,
        cluster.residue_ratio,
        cluster.median_seed_distance,
        cluster.recovered_prime,
        cluster.tie_break_order,
    )


def _route_cluster_sort_key(cluster: PrimeCluster) -> tuple[int, float, float, int, int]:
    """Return the support-first routing key for recovered-prime clusters."""
    return _cluster_sort_key(cluster)


def _recovery_cluster_sort_key(cluster: PrimeCluster) -> tuple[float, int, float, int, int]:
    """Return the residue-first recovery key for recovered-prime clusters."""
    return (
        cluster.residue_ratio,
        -cluster.support_count,
        cluster.median_seed_distance,
        cluster.recovered_prime,
        cluster.tie_break_order,
    )


def _window_sort_key(window: BitWindow) -> tuple[int, float, float, int, int, float]:
    """Return the exact deterministic window ranking key."""
    if window.evidence is None:
        return (0, float("inf"), float("inf"), math.inf, math.inf, window.center_log2)
    cluster = window.evidence
    return (
        -cluster.support_count,
        cluster.residue_ratio,
        cluster.median_seed_distance,
        cluster.recovered_prime,
        cluster.tie_break_order,
        window.center_log2,
    )


def _dedupe_windows(windows: list[BitWindow], limit: int) -> list[BitWindow]:
    """Return the top unique windows by exact window rank."""
    ordered = sorted(windows, key=_window_sort_key)
    seen: set[tuple[int, int]] = set()
    result: list[BitWindow] = []
    for window in ordered:
        key = (
            int(round(window.center_log2 * 1_000_000_000)),
            int(round(window.width_bits * 1_000_000_000)),
        )
        if key in seen:
            continue
        seen.add(key)
        result.append(window)
        if len(result) >= limit:
            break
    return result


def _median_distance(distances: list[int]) -> float:
    """Return the deterministic median seed distance."""
    ordered = sorted(distances)
    midpoint = len(ordered) // 2
    if len(ordered) % 2 == 1:
        return float(ordered[midpoint])
    return (ordered[midpoint - 1] + ordered[midpoint]) / 2.0


def _window_contains_factor(window: BitWindow, factor_log2: float) -> bool:
    """Return whether one window contains the true small-factor scale."""
    half_width = window.width_bits / 2.0
    return (window.center_log2 - half_width) <= factor_log2 <= (window.center_log2 + half_width)


def _window_to_interval(window: BitWindow) -> tuple[int, int, int]:
    """Convert one bit window to an integer interval and midpoint."""
    half_width = window.width_bits / 2.0
    low = max(2, _anchor_from_log2(window.center_log2 - half_width, rounding="floor"))
    high = max(low + 1, _anchor_from_log2(window.center_log2 + half_width, rounding="ceil"))
    midpoint = window.midpoint if window.midpoint is not None else _anchor_from_log2(window.center_log2, rounding="nearest")
    midpoint = min(max(midpoint, low), high)
    return low, high, midpoint


def _family_center_log2(case: ScaleupCase, router_mode: str) -> float:
    """Return the deterministic center for the initial search band."""
    return math.log2(_family_center_estimate(case, router_mode))


def _family_ratio_prior(case: ScaleupCase) -> float | None:
    """Return the deterministic log-ratio prior for one family when available."""
    if case.family == "balanced":
        return 0.0
    if case.family == "moderate_unbalanced":
        return TARGET_MODERATE_LOG
    if case.family == "archived_shape":
        return ARCHIVED_127_LOG
    return None


def _family_center_estimate(case: ScaleupCase, router_mode: str) -> int:
    """Return the deterministic integer factor-side center for the initial search band."""
    if router_mode not in ROUTER_MODES:
        raise ValueError(f"unsupported router_mode {router_mode}")
    if router_mode == "audited_family_prior":
        ratio_prior = _family_ratio_prior(case)
    else:
        ratio_prior = None
    if ratio_prior is not None:
        with mp.workdps(100):
            shifted = mp.mpf(case.n) * mp.e ** (-mp.mpf(str(ratio_prior)))
            return int(mp.nint(mp.sqrt(shifted)))
    if router_mode == "audited_family_prior" and case.family == "challenge_like":
        return _anchor_from_log2(math.floor(0.3994 * case.case_bits) - 0.5, rounding="nearest")
    return _anchor_from_log2(math.log2(case.n) / 2.0, rounding="nearest")


def _left_prime_seed(boundary: int, lower_bound: int) -> int | None:
    """Return the nearest prime at or below one boundary inside one interval."""
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
    while candidate % 30 not in (1, 7, 11, 13, 17, 19, 23, 29):
        candidate += 2
    return candidate


def _next_prime_after_scaleup(boundary: int) -> int:
    """Return the next prime after boundary on the scale-up runtime path."""
    if boundary <= MAX_GWR_BOUNDARY:
        return int(next_prime_after(int(boundary)))

    candidate = _next_wheel_open_candidate(boundary)
    while not isprime(candidate):
        candidate = _next_wheel_open_candidate(candidate)
    return candidate


def _next_prime_successor_scaleup(prime: int) -> int:
    """Return the prime immediately after prime on the scale-up runtime path."""
    if prime <= MAX_GWR_BOUNDARY:
        return int(gwr_next_prime(int(prime)))

    candidate = _next_wheel_open_candidate(prime)
    while not isprime(candidate):
        candidate = _next_wheel_open_candidate(candidate)
    return candidate


def _right_prime_seed(boundary: int, upper_bound: int) -> int | None:
    """Return the nearest prime strictly above one boundary inside one interval."""
    candidate = _next_prime_after_scaleup(boundary)
    if candidate > upper_bound:
        return None
    return candidate


def _center_out_primes_in_interval(midpoint: int, low: int, high: int, limit: int):
    """Yield the exact repo-PGS center-out prime sequence inside one integer interval."""
    if limit < 1 or high < low:
        return

    left = _left_prime_seed(midpoint, low)
    right = _right_prime_seed(midpoint, high)
    if left is not None and right is not None and left == right:
        next_right = _next_prime_successor_scaleup(right)
        right = next_right if next_right <= high else None
    emitted = 0

    while emitted < limit and (left is not None or right is not None):
        choose_left = False
        if left is not None and right is None:
            choose_left = True
        elif left is not None and right is not None:
            choose_left = abs(midpoint - left) <= abs(right - midpoint)

        if choose_left:
            emitted += 1
            yield int(left)
            if left <= low:
                left = None
            else:
                left = _left_prime_seed(left - 2, low)
        else:
            emitted += 1
            yield int(right)
            if right >= high:
                right = None
            else:
                next_right = _next_prime_successor_scaleup(right)
                right = next_right if next_right <= high else None


def _previous_composite(candidate: int, lower_bound: int) -> int | None:
    """Return the nearest composite at or below candidate."""
    current = candidate
    while current >= lower_bound:
        if current >= 4 and not isprime(current):
            return current
        current -= 1
    return None


def _next_composite(candidate: int, upper_bound: int) -> int | None:
    """Return the nearest composite at or above candidate."""
    current = max(4, candidate)
    while current <= upper_bound:
        if not isprime(current):
            return current
        current += 1
    return None


def _spread_out_composite_seeds_in_interval(midpoint: int, low: int, high: int, limit: int) -> list[int]:
    """Return a wide center-out composite seed sequence inside one integer interval."""
    if limit < 1 or high < low:
        return []

    max_radius = max(midpoint - low, high - midpoint)
    radius_steps = max(1, math.ceil(limit / 2))
    seeds: list[int] = []
    seen: set[int] = set()

    def add_seed(candidate: int | None) -> None:
        if candidate is None or candidate in seen:
            return
        seen.add(candidate)
        seeds.append(candidate)

    add_seed(_previous_composite(midpoint, low))
    if len(seeds) < limit:
        add_seed(_next_composite(midpoint, high))

    for step in range(1, radius_steps + 1):
        if len(seeds) >= limit:
            break
        radius = int(round((step * max_radius) / radius_steps))
        add_seed(_previous_composite(midpoint - radius, low))
        if len(seeds) >= limit:
            break
        add_seed(_next_composite(midpoint + radius, high))

    return seeds


def _tight_center_out_composite_seeds_in_interval(midpoint: int, low: int, high: int, limit: int) -> list[int]:
    """Return the nearest center-out composite seed sequence inside one integer interval."""
    if limit < 1 or high < low:
        return []

    left = _previous_composite(midpoint, low)
    right = _next_composite(midpoint, high)
    if left is not None and right is not None and left == right:
        right = _next_composite(right + 1, high)

    seeds: list[int] = []
    while len(seeds) < limit and (left is not None or right is not None):
        choose_left = False
        if left is not None and right is None:
            choose_left = True
        elif left is not None and right is not None:
            choose_left = abs(midpoint - left) <= abs(right - midpoint)

        if choose_left:
            seeds.append(left)
            left = _previous_composite(left - 1, low)
        else:
            seeds.append(right)
            right = _next_composite(right + 1, high)

    return seeds


@lru_cache(maxsize=262144)
def _recover_prime_from_seed(seed: int) -> int | None:
    """Recover one prime from one composite seed by the exact repo PGS contract."""
    if seed > MAX_GWR_BOUNDARY:
        try:
            return _recover_prime_from_seed_bigint(seed)
        except (AssertionError, ValueError):
            return None

    try:
        recovered_prime, _witness, _closure = gwr_predict(seed, d=None)
    except OverflowError:
        try:
            return _recover_prime_from_seed_bigint(seed)
        except (AssertionError, ValueError):
            return None
    except (AssertionError, ValueError):
        return None
    return int(recovered_prime)


@lru_cache(maxsize=262144)
def _bigint_gap_profile(right_prime: int) -> tuple[int, int, tuple[int, ...]]:
    """Return the exact gap-local dmin carriers for one large right-endpoint prime."""
    left_prime = int(prevprime(right_prime))
    carriers_by_d: dict[int, list[int]] = {}
    for value in range(left_prime + 1, right_prime):
        d_value = int(divisor_count(value))
        carriers_by_d.setdefault(d_value, []).append(value)
    divisor_target = min(carriers_by_d)
    carriers = tuple(carriers_by_d[divisor_target])
    return left_prime, divisor_target, carriers


def _recover_prime_from_seed_bigint(seed: int) -> int:
    """Recover one prime from one large composite seed by the exact gap-local rule."""
    if seed < 4:
        raise ValueError("seed must be at least 4")
    if isprime(seed):
        raise ValueError("seed must be composite")

    right_prime = int(nextprime(seed - 1))
    left_prime, _divisor_target, carriers = _bigint_gap_profile(right_prime)
    if not left_prime < seed < right_prime:
        raise ValueError("seed must lie strictly inside one prime gap")

    witness = None
    for carrier in carriers:
        if carrier >= seed:
            witness = carrier
            break
    if witness is None:
        raise ValueError("no admissible witness remains at or after seed")

    recovered_prime = int(nextprime(witness - 1))
    if recovered_prime != right_prime:
        raise AssertionError(
            f"witness recovery failed: seed={seed}, witness={witness}, "
            f"recovered={recovered_prime}, expected={right_prime}"
        )
    return recovered_prime


def _clustered_primes_in_interval(
    case: ScaleupCase,
    low: int,
    high: int,
    seed_budget: int,
    midpoint: int | None = None,
    spread: bool = False,
) -> tuple[list[PrimeCluster], int]:
    """Return the ranked recovered-prime clusters inside one integer interval."""
    if midpoint is None:
        midpoint = (low + high) // 2
    groups: dict[int, dict[str, object]] = {}
    probe_count = 0

    seed_sequence = (
        _spread_out_composite_seeds_in_interval(midpoint, low, high, seed_budget)
        if spread
        else _tight_center_out_composite_seeds_in_interval(midpoint, low, high, seed_budget)
    )
    for order, seed in enumerate(seed_sequence):
        probe_count += 1
        recovered_prime = _recover_prime_from_seed(seed)
        if recovered_prime is None:
            continue

        if recovered_prime not in groups:
            groups[recovered_prime] = {
                "support_count": 0,
                "distances": [],
                "first_order": order,
            }
        entry = groups[recovered_prime]
        entry["support_count"] = int(entry["support_count"]) + 1
        distances = entry["distances"]
        assert isinstance(distances, list)
        distances.append(abs(seed - midpoint))

    clusters: list[PrimeCluster] = []
    for recovered_prime, entry in groups.items():
        residue = case.n % recovered_prime
        residue_ratio = min(residue, recovered_prime - residue) / recovered_prime
        distances = entry["distances"]
        assert isinstance(distances, list)
        clusters.append(
            PrimeCluster(
                recovered_prime=recovered_prime,
                support_count=int(entry["support_count"]),
                residue_ratio=float(residue_ratio),
                median_seed_distance=_median_distance([int(value) for value in distances]),
                tie_break_order=int(entry["first_order"]),
            )
        )

    clusters.sort(key=_route_cluster_sort_key)
    return clusters, probe_count


def _ranked_recovered_primes_in_interval(
    case: ScaleupCase,
    low: int,
    high: int,
    seed_budget: int,
    midpoint: int | None = None,
) -> tuple[int, ...]:
    """Return the ranked recovered-prime sequence inside one integer interval."""
    clusters, _probe_count = _clustered_primes_in_interval(case, low, high, seed_budget, midpoint=midpoint)
    return tuple(cluster.recovered_prime for cluster in clusters)


def _recovery_ranked_recovered_primes_in_interval(
    case: ScaleupCase,
    low: int,
    high: int,
    seed_budget: int,
    midpoint: int | None = None,
) -> tuple[int, ...]:
    """Return the residue-first recovered-prime sequence inside one integer interval."""
    clusters, _probe_count = _clustered_primes_in_interval(case, low, high, seed_budget, midpoint=midpoint)
    ordered = sorted(clusters, key=_recovery_cluster_sort_key)
    return tuple(cluster.recovered_prime for cluster in ordered)


def _ordered_factor_hit(
    case: ScaleupCase,
    clusters: list[PrimeCluster],
) -> tuple[bool, int]:
    """Return whether one ordered cluster list recovers a factor and how many prime tests it used."""
    prime_tests = 0
    for cluster in clusters:
        prime_tests += 1
        if case.n % cluster.recovered_prime == 0:
            return True, prime_tests
    return False, prime_tests


def _pgs_seed_recovery_in_interval(case: ScaleupCase, low: int, high: int, budget: int) -> tuple[bool, int]:
    """Try exact repo PGS seed recovery inside one integer interval."""
    clusters, _probe_count = _clustered_primes_in_interval(case, low, high, budget)
    ordered = sorted(clusters, key=_recovery_cluster_sort_key)
    return _ordered_factor_hit(case, ordered)


def _cluster_rank(
    clusters: list[PrimeCluster],
    target_prime: int,
) -> int | None:
    """Return the one-based rank of target_prime inside one ordered cluster list."""
    for index, cluster in enumerate(clusters, start=1):
        if cluster.recovered_prime == target_prime:
            return index
    return None


def _winning_window_diagnostics(
    case: ScaleupCase,
    windows: list[BitWindow],
    local_seed_budget: int,
) -> dict[str, int | bool | None]:
    """Return diagnostics for the top-ranked routed window."""
    if not windows:
        return {
            "winning_window_factor_present": None,
            "winning_window_factor_route_rank": None,
            "winning_window_factor_recovery_rank": None,
        }

    low, high, midpoint = _window_to_interval(windows[0])
    clusters, _probe_count = _clustered_primes_in_interval(
        case,
        low,
        high,
        local_seed_budget,
        midpoint=midpoint,
    )
    recovery_clusters = sorted(clusters, key=_recovery_cluster_sort_key)
    route_rank = _cluster_rank(clusters, case.small_factor)
    recovery_rank = _cluster_rank(recovery_clusters, case.small_factor)
    return {
        "winning_window_factor_present": route_rank is not None,
        "winning_window_factor_route_rank": route_rank,
        "winning_window_factor_recovery_rank": recovery_rank,
    }


def _scored_window(
    case: ScaleupCase,
    center_log2: float,
    width_bits: float,
    seed_budget: int,
    midpoint_override: int | None = None,
) -> tuple[BitWindow, int]:
    """Return one routed window scored by the strongest recovered-prime cluster."""
    midpoint = midpoint_override if midpoint_override is not None else _anchor_from_log2(center_log2, rounding="nearest")
    low = max(2, _anchor_from_log2(center_log2 - (width_bits / 2.0), rounding="floor"))
    high = max(low + 1, _anchor_from_log2(center_log2 + (width_bits / 2.0), rounding="ceil"))
    midpoint = min(max(midpoint, low), high)
    clusters, probe_count = _clustered_primes_in_interval(
        case,
        low,
        high,
        seed_budget,
        midpoint=midpoint,
        spread=True,
    )
    evidence = clusters[0] if clusters else None
    return BitWindow(center_log2=center_log2, width_bits=width_bits, evidence=evidence, midpoint=midpoint), probe_count


def _route_case(
    case: ScaleupCase,
    rung: int,
    seed: int,
    router_mode: str = "audited_family_prior",
) -> tuple[list[BitWindow], int]:
    """Return the final routed windows for one case and rung."""
    del seed
    if router_mode not in ROUTER_MODES:
        raise ValueError(f"unsupported router_mode {router_mode}")

    config = RUNG_CONFIGS[rung]
    if router_mode == "pure_pgs" and case.case_bits >= 256:
        return _route_case_centered_blind(case, rung)
    if (
        router_mode == "audited_family_prior"
        and case.case_bits <= 127
        and case.family in {"balanced", "moderate_unbalanced", "archived_shape"}
    ):
        return _route_case_centered_127(case, rung)
    if router_mode == "audited_family_prior" and case.family == "challenge_like":
        return _route_case_centered_challenge(case, rung)

    search_center = _family_center_log2(case, router_mode)
    search_midpoint = _family_center_estimate(case, router_mode)
    search_lo = max(config.widths[0] / 2.0, search_center - (config.widths[0] / 2.0))
    search_hi = min(
        case.case_bits - (config.widths[0] / 2.0),
        search_center + (config.widths[0] / 2.0),
    )
    beam_ranges = [(search_lo, search_hi)]
    probe_count = 0
    beam_windows: list[BitWindow] = []

    for level_index, width_bits in enumerate(config.widths):
        current_windows: list[BitWindow] = []
        points_per_range = config.scan_points if level_index == 0 else 2
        for range_index, (range_lo, range_hi) in enumerate(beam_ranges):
            centers = _linspace(range_lo, range_hi, points_per_range)
            for center_index, center_log2 in enumerate(centers):
                midpoint_override = None
                if level_index == 0 and range_index == 0 and center_index == (points_per_range // 2):
                    midpoint_override = search_midpoint
                window, window_probes = _scored_window(
                    case,
                    center_log2,
                    width_bits,
                    config.router_seed_budget,
                    midpoint_override=midpoint_override,
                )
                probe_count += window_probes
                current_windows.append(window)

        anchor_window, anchor_probes = _scored_window(
            case,
            search_center,
            width_bits,
            config.router_seed_budget,
            midpoint_override=search_midpoint if level_index == 0 else None,
        )
        probe_count += anchor_probes
        current_windows.append(anchor_window)

        ranked_windows = _dedupe_windows(current_windows, max(1, config.beam_width - 1))
        beam_windows = _dedupe_windows([anchor_window] + ranked_windows, config.beam_width)
        if level_index + 1 >= len(config.widths):
            continue

        next_width = config.widths[level_index + 1]
        beam_ranges = []
        for window in beam_windows:
            half_span = max(width_bits / 8.0, next_width / 2.0)
            beam_ranges.append(
                (
                    max(next_width / 2.0, window.center_log2 - half_span),
                    min(case.case_bits - next_width / 2.0, window.center_log2 + half_span),
                )
            )

    return beam_windows[: config.top_windows], probe_count


def _route_case_centered_blind(case: ScaleupCase, rung: int) -> tuple[list[BitWindow], int]:
    """Return an unscored high-scale route centered from N alone."""
    config = RUNG_CONFIGS[rung]
    final_width = config.widths[-1]
    center_log2 = math.log2(case.n) / 2.0
    center_midpoint = _anchor_from_log2(center_log2, rounding="nearest")
    offsets = (0.0, -final_width, final_width, 2.0 * final_width)

    windows: list[BitWindow] = []
    for index, offset in enumerate(offsets):
        window_center = min(
            max(final_width / 2.0, center_log2 + offset),
            case.case_bits - (final_width / 2.0),
        )
        midpoint_override = center_midpoint if index == 0 else None
        windows.append(
            BitWindow(
                center_log2=window_center,
                width_bits=final_width,
                evidence=None,
                midpoint=midpoint_override,
            )
        )

    return windows[: config.top_windows], 0


def _route_case_centered_127(case: ScaleupCase, rung: int) -> tuple[list[BitWindow], int]:
    """Return the centered four-window 127-bit audit route."""
    config = RUNG_CONFIGS[rung]
    final_width = config.widths[-1]
    center_log2 = _family_center_log2(case, "audited_family_prior")
    center_midpoint = _family_center_estimate(case, "audited_family_prior")
    offsets = (0.0, -final_width, final_width, 2.0 * final_width)
    router_seed_budget = OFFICIAL_127_ROUTER_SEED_BUDGETS[rung]

    windows: list[BitWindow] = []
    probe_count = 0
    for index, offset in enumerate(offsets):
        window_center = min(
            max(final_width / 2.0, center_log2 + offset),
            case.case_bits - (final_width / 2.0),
        )
        midpoint_override = center_midpoint if index == 0 else None
        window, window_probes = _scored_window(
            case,
            window_center,
            final_width,
            router_seed_budget,
            midpoint_override=midpoint_override,
        )
        probe_count += window_probes
        windows.append(window)

    return windows[: config.top_windows], probe_count


def _route_case_centered_challenge(case: ScaleupCase, rung: int) -> tuple[list[BitWindow], int]:
    """Return one centered final-width route for challenge-like cases."""
    config = RUNG_CONFIGS[rung]
    final_width = config.widths[-1]
    center_log2 = _family_center_log2(case, "audited_family_prior")
    center_midpoint = _family_center_estimate(case, "audited_family_prior")
    offsets = (0.0, -final_width, final_width, 2.0 * final_width)

    windows: list[BitWindow] = []
    probe_count = 0
    for index, offset in enumerate(offsets):
        window_center = min(
            max(final_width / 2.0, center_log2 + offset),
            case.case_bits - (final_width / 2.0),
        )
        midpoint_override = center_midpoint if index == 0 else None
        window, window_probes = _scored_window(
            case,
            window_center,
            final_width,
            config.router_seed_budget,
            midpoint_override=midpoint_override,
        )
        probe_count += window_probes
        windows.append(window)

    return windows[: config.top_windows], probe_count


def _local_router_only_prime_walk(
    case: ScaleupCase,
    windows: list[BitWindow],
    prime_budget: int,
) -> tuple[bool, int]:
    """Run the exact prime-step helper used only on router-only stages."""
    total_prime_tests = 0
    for window in windows:
        low, high, midpoint = _window_to_interval(window)
        for prime in _center_out_primes_in_interval(midpoint, low, high, prime_budget):
            total_prime_tests += 1
            if case.n % prime == 0:
                return True, total_prime_tests
    return False, total_prime_tests


def _local_pgs_search(
    case: ScaleupCase,
    windows: list[BitWindow],
    local_seed_budget: int,
    router_only_prime_budget: int,
    scale_bits: int,
) -> tuple[bool, int, bool, int]:
    """Run exact recovery inside the routed windows."""
    del local_seed_budget
    if scale_bits >= 256:
        factor_recovered, local_prime_tests = _local_router_only_prime_walk(
            case,
            windows,
            router_only_prime_budget,
        )
        return factor_recovered, local_prime_tests, factor_recovered, local_prime_tests

    factor_recovered, local_prime_tests = _local_router_only_prime_walk(
        case,
        windows,
        router_only_prime_budget,
    )
    return factor_recovered, local_prime_tests, factor_recovered, local_prime_tests


def _evaluate_case(
    case: ScaleupCase,
    scale_bits: int,
    rung: int,
    seed: int,
    router_mode: str = "audited_family_prior",
) -> ScaleupMetrics:
    """Evaluate one case at one rung."""
    started = time.perf_counter()
    config = RUNG_CONFIGS[rung]
    windows, probe_count = _route_case(case, rung, seed, router_mode=router_mode)
    factor_log2 = case.small_factor_log2
    best_rank = None
    best_width = config.widths[-1]

    for index, window in enumerate(windows, start=1):
        if _window_contains_factor(window, factor_log2):
            best_rank = index
            best_width = window.width_bits
            break

    factor_in_final_window = best_rank is not None
    factor_recovered, local_prime_tests, factor_recovered_route_order, local_prime_tests_route_order = _local_pgs_search(
        case,
        windows,
        config.local_seed_budget,
        config.router_only_prime_budget,
        scale_bits,
    )
    winning_window_diagnostics = _winning_window_diagnostics(case, windows, config.local_seed_budget)
    elapsed_ms = (time.perf_counter() - started) * 1000.0
    row = {
        "n": case.n,
        "p": case.p,
        "q": case.q,
        "router": "pgs",
        "router_mode": router_mode,
        "scale_bits": scale_bits,
        "rung": rung,
        "factor_recovered": factor_recovered,
        "factor_recovered_route_order": factor_recovered_route_order,
        "factor_in_final_window": factor_in_final_window,
        "best_window_rank": best_rank,
        "final_window_bits": best_width,
        "local_prime_tests": local_prime_tests,
        "local_prime_tests_route_order": local_prime_tests_route_order,
        "router_probe_count": probe_count,
        "winning_window_factor_present": winning_window_diagnostics["winning_window_factor_present"],
        "winning_window_factor_route_rank": winning_window_diagnostics["winning_window_factor_route_rank"],
        "winning_window_factor_recovery_rank": winning_window_diagnostics["winning_window_factor_recovery_rank"],
        "wall_time_ms": elapsed_ms,
        "case_id": case.case_id,
        "family": case.family,
        "case_bits": case.case_bits,
    }
    return ScaleupMetrics(row=row)


def _median_or_none(values: list[int | float]) -> float | None:
    """Return the median of one numeric list or None."""
    return float(statistics.median(values)) if values else None


def _raw_summary(
    scale_bits: int,
    rung: int,
    rows: list[ScaleupMetrics],
) -> dict[str, object]:
    """Build the raw summary payload."""
    public_rows = [metric.row for metric in rows]
    top1_hits = sum(int(row["best_window_rank"] == 1) for row in public_rows)
    top4_hits = sum(int(bool(row["factor_in_final_window"])) for row in public_rows)
    exact_hits = sum(int(bool(row["factor_recovered"])) for row in public_rows)
    route_order_exact_hits = sum(int(bool(row["factor_recovered_route_order"])) for row in public_rows)
    best_window_ranks = [
        int(row["best_window_rank"])
        for row in public_rows
        if row["best_window_rank"] is not None
    ]
    final_window_bits = [float(row["final_window_bits"]) for row in public_rows]
    total_local_prime_tests = sum(int(row["local_prime_tests"]) for row in public_rows)
    total_local_prime_tests_route_order = sum(
        int(row["local_prime_tests_route_order"]) for row in public_rows
    )
    total_router_probe_count = sum(int(row["router_probe_count"]) for row in public_rows)
    total_wall_time_ms = sum(float(row["wall_time_ms"]) for row in public_rows)

    return {
        "router": "pgs",
        "router_mode": str(public_rows[0]["router_mode"]) if public_rows else "audited_family_prior",
        "scale_bits": scale_bits,
        "rung": rung,
        "case_count": len(public_rows),
        "router_top1_recall": top1_hits / len(public_rows),
        "router_top4_recall": top4_hits / len(public_rows),
        "median_final_window_bits": _median_or_none(final_window_bits),
        "median_best_window_rank": _median_or_none(best_window_ranks),
        "exact_recovery_recall": exact_hits / len(public_rows),
        "route_order_exact_recovery_recall": route_order_exact_hits / len(public_rows),
        "total_local_prime_tests": total_local_prime_tests,
        "total_local_prime_tests_route_order": total_local_prime_tests_route_order,
        "total_router_probe_count": total_router_probe_count,
        "total_wall_time_ms": total_wall_time_ms,
    }


def _stage_acceptance(
    scale_bits: int,
    raw_summary: dict[str, object],
    rows: list[ScaleupMetrics],
) -> dict[str, object]:
    """Return the stage acceptance payload for one summary."""
    router_mode = str(raw_summary.get("router_mode", "audited_family_prior"))
    full_stage_evaluated = len(rows) == len(CORPUS[scale_bits])
    if router_mode == "pure_pgs":
        archived_row = next(
            (metric.row for metric in rows if metric.row.get("case_id") == ARCHIVED_CASE_ID),
            None,
        )
        return {
            "mode": "research",
            "router_mode": router_mode,
            "full_stage_evaluated": full_stage_evaluated,
            "recovery_not_worse_than_route_order": (
                float(raw_summary["exact_recovery_recall"])
                >= float(raw_summary["route_order_exact_recovery_recall"])
            ),
            "archived_case_present": archived_row is not None,
            "archived_case_factor_present_in_winning_window": (
                None if archived_row is None else archived_row["winning_window_factor_present"]
            ),
            "archived_case_recovery_rank_improves_route_rank": (
                None
                if archived_row is None
                or archived_row["winning_window_factor_route_rank"] is None
                or archived_row["winning_window_factor_recovery_rank"] is None
                else int(archived_row["winning_window_factor_recovery_rank"])
                < int(archived_row["winning_window_factor_route_rank"])
            ),
            "stage_passed": False,
        }
    if scale_bits == 127:
        archived_row = next(
            (metric.row for metric in rows if metric.row["case_id"] == ARCHIVED_CASE_ID),
            None,
        )
        archived_case_recovered = bool(archived_row["factor_recovered"]) if archived_row is not None else False
        stage_passed = (
            full_stage_evaluated
            and float(raw_summary["exact_recovery_recall"]) >= 0.75
            and archived_case_recovered
            and float(raw_summary["router_top4_recall"]) >= 0.83
        )
        return {
            "mode": "recovery",
            "full_stage_evaluated": full_stage_evaluated,
            "archived_case_present": archived_row is not None,
            "archived_case_recovered": archived_case_recovered,
            "exact_recovery_threshold_met": float(raw_summary["exact_recovery_recall"]) >= 0.75,
            "router_top4_threshold_met": float(raw_summary["router_top4_recall"]) >= 0.83,
            "stage_passed": stage_passed,
        }

    if scale_bits in (160, 192, 224, 256):
        stage_passed = (
            full_stage_evaluated
            and float(raw_summary["exact_recovery_recall"]) >= 0.50
            and float(raw_summary["router_top4_recall"]) >= 0.75
        )
        return {
            "mode": "recovery",
            "full_stage_evaluated": full_stage_evaluated,
            "exact_recovery_threshold_met": float(raw_summary["exact_recovery_recall"]) >= 0.50,
            "router_top4_threshold_met": float(raw_summary["router_top4_recall"]) >= 0.75,
            "stage_passed": stage_passed,
        }

    max_window_bits = 0.25 if scale_bits <= 1024 else 0.50
    stage_passed = (
        full_stage_evaluated
        and float(raw_summary["router_top4_recall"]) >= 0.75
        and float(raw_summary["median_final_window_bits"]) <= max_window_bits
    )
    return {
        "mode": "router_only",
        "full_stage_evaluated": full_stage_evaluated,
        "router_top4_threshold_met": float(raw_summary["router_top4_recall"]) >= 0.75,
        "median_final_window_threshold_met": float(raw_summary["median_final_window_bits"]) <= max_window_bits,
        "stage_passed": stage_passed,
    }


def run_scaleup(
    scale_bits: int,
    rung: int,
    case_count: int | None,
    seed: int,
    router_mode: str = "audited_family_prior",
) -> tuple[list[ScaleupMetrics], dict[str, object]]:
    """Run the scale-up harness without writing artifacts."""
    cases = _selected_cases(scale_bits, case_count)
    rows = [
        _evaluate_case(
            case,
            scale_bits,
            rung,
            seed,
            router_mode=router_mode,
        )
        for case in cases
    ]
    summary = _raw_summary(scale_bits, rung, rows)
    summary["acceptance"] = _stage_acceptance(scale_bits, summary, rows)
    summary["seed"] = seed
    return rows, summary


def run_127_official_audit(seed: int) -> tuple[list[ScaleupMetrics], dict[str, object]]:
    """Run the full 127-bit audit and stop at the first passing rung."""
    cases = _selected_cases(127, None)
    rung_summaries: dict[str, dict[str, object]] = {}
    selected_rows: list[ScaleupMetrics] = []
    selected_summary: dict[str, object] | None = None
    official_rung: int | None = None

    for rung in (1, 2, 3):
        rows = [
            _evaluate_case(
                case,
                127,
                rung,
                seed,
                router_mode="audited_family_prior",
            )
            for case in cases
        ]
        rung_summary = _raw_summary(127, rung, rows)
        rung_summary["acceptance"] = _stage_acceptance(127, rung_summary, rows)
        rung_summary["seed"] = seed
        rung_summaries[str(rung)] = rung_summary
        selected_rows = rows
        selected_summary = rung_summary
        if bool(rung_summary["acceptance"]["stage_passed"]):
            official_rung = rung
            break

    if selected_summary is None:
        raise AssertionError("127 audit produced no summaries")

    summary = dict(selected_summary)
    summary["official_rung"] = official_rung
    summary["rung_summaries"] = rung_summaries
    summary["stage_passed"] = bool(summary["acceptance"]["stage_passed"])
    return selected_rows, summary


def run_127_pure_pgs_audit(seed: int) -> tuple[list[ScaleupMetrics], dict[str, object]]:
    """Run the full 127-bit pure-PGS audit and report all rungs."""
    cases = _selected_cases(127, None)
    rung_summaries: dict[str, dict[str, object]] = {}
    selected_rows: list[ScaleupMetrics] = []
    selected_summary: dict[str, object] | None = None

    for rung in (1, 2, 3):
        rows = [
            _evaluate_case(
                case,
                127,
                rung,
                seed,
                router_mode="pure_pgs",
            )
            for case in cases
        ]
        rung_summary = _raw_summary(127, rung, rows)
        rung_summary["acceptance"] = _stage_acceptance(127, rung_summary, rows)
        rung_summary["seed"] = seed
        rung_summaries[str(rung)] = rung_summary
        selected_rows = rows
        selected_summary = rung_summary

    if selected_summary is None:
        raise AssertionError("127 pure-PGS audit produced no summaries")

    summary = dict(selected_summary)
    summary["audit_mode"] = "pure_pgs"
    summary["rung_summaries"] = rung_summaries
    summary["stage_passed"] = bool(summary["acceptance"]["stage_passed"])
    return selected_rows, summary


def write_rows_jsonl(output_path: Path, rows: list[ScaleupMetrics]) -> None:
    """Write the per-case rows as JSONL."""
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        for metric in rows:
            payload = {name: metric.row.get(name) for name in ROW_FIELDNAMES}
            handle.write(json.dumps(payload, sort_keys=False) + "\n")


def main(argv: list[str] | None = None) -> int:
    """Run the scale-up harness and emit artifacts."""
    parser = build_parser()
    args = parser.parse_args(argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    rows, summary = run_scaleup(
        scale_bits=args.scale_bits,
        rung=args.rung,
        case_count=args.cases,
        seed=args.seed,
        router_mode=args.router_mode,
    )

    stem = f"pgs_scale{args.scale_bits}_r{args.rung}_{args.router_mode}"
    rows_jsonl_path = args.output_dir / f"{stem}_rows.jsonl"
    summary_path = args.output_dir / f"{stem}_summary.json"
    write_rows_jsonl(rows_jsonl_path, rows)
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
