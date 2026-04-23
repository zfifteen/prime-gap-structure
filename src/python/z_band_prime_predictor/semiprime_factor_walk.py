"""Deterministic factor-first semiprime walk on the local PGS neighborhood.

This module intentionally keeps a narrow contract.

- The anchor must be an odd composite inside the current exact divisor field.
- The local neighborhood is limited to the previous and containing prime gaps.
- The candidate pool contains only lower odd-semiprime interior carriers.
- Selection uses one fixed deterministic rule:
  previous gap first, then first d=4, then larger offset, then smaller n.
- The walk stops after one step.

That stop rule is deliberate. If the selected lower odd semiprime shares a
hidden factor with the modulus, ``gcd(modulus, candidate)`` reveals the factor
immediately. If it does not, this walker records explicit failure rather than
continuing on a weaker proxy target.
"""

from __future__ import annotations

import math

import gmpy2

from z_band_prime_composite_field import divisor_counts_segment
from z_band_prime_predictor.gwr_boundary_walk import gwr_next_gap_profile, next_prime_after


DEFAULT_SCAN_BLOCK = 64
MAX_FIELD_VALUE = (1 << 63) - 1 - DEFAULT_SCAN_BLOCK


def validate_semiprime_anchor(anchor: int) -> None:
    """Validate one odd composite anchor for the factor-first walk."""
    if anchor <= 3:
        raise ValueError("anchor must be greater than 3")
    if anchor % 2 == 0:
        raise ValueError("anchor must be odd")
    if anchor > MAX_FIELD_VALUE:
        raise ValueError(
            f"anchor={anchor} exceeds the current exact divisor-field range {MAX_FIELD_VALUE}"
        )
    if gmpy2.is_prime(anchor):
        raise ValueError("anchor must be composite")


def previous_prime_before(n: int, block: int = DEFAULT_SCAN_BLOCK) -> int:
    """Return the largest prime less than or equal to n by exact leftward scan."""
    if n < 2:
        raise ValueError("no prime exists below 2")
    if block < 1:
        raise ValueError("block must be positive")

    search_hi = n + 1
    while search_hi > 2:
        search_lo = max(2, search_hi - block)
        counts = divisor_counts_segment(search_lo, search_hi)
        for index in range(len(counts) - 1, -1, -1):
            if int(counts[index]) == 2:
                return search_lo + index
        search_hi = search_lo

    raise RuntimeError(f"failed to find a prime at or below {n}")


def prime_cube_root(n: int) -> int | None:
    """Return the prime cube root of n when n is exactly p^3."""
    root, exact = gmpy2.iroot(gmpy2.mpz(n), 3)
    if not exact or not gmpy2.is_prime(root):
        return None
    return int(root)


def carrier_family(n: int, divisor_count: int) -> str:
    """Return the coarse carrier family for one exact composite interior value."""
    if divisor_count < 3:
        raise ValueError("divisor_count must describe one composite interior value")
    if divisor_count == 3:
        return "prime_square"
    if divisor_count == 4:
        if prime_cube_root(n) is not None:
            return "prime_cube"
        if n % 2 == 0:
            return "even_semiprime"
        return "odd_semiprime"
    if n % 2 == 0:
        return "higher_divisor_even"
    return "higher_divisor_odd"


def _interior_rows(left_prime: int, right_prime: int, winner: int | None) -> list[dict[str, object]]:
    """Return the exact interior rows for one prime gap."""
    if right_prime - left_prime <= 1:
        return []

    values = list(range(left_prime + 1, right_prime))
    counts = divisor_counts_segment(left_prime + 1, right_prime)
    dmin = min(int(raw_d) for raw_d in counts)
    first_dmin = None
    first_d4 = None
    for value, raw_d in zip(values, counts):
        d = int(raw_d)
        if first_dmin is None and d == dmin:
            first_dmin = value
        if first_d4 is None and d == 4:
            first_d4 = value

    rows: list[dict[str, object]] = []
    for value, raw_d in zip(values, counts):
        d = int(raw_d)
        rows.append(
            {
                "n": value,
                "offset": value - left_prime,
                "d": d,
                "carrier_family": carrier_family(value, d),
                "is_gwr_winner": value == winner,
                "is_first_dmin": value == first_dmin,
                "is_first_d4": value == first_d4,
            }
        )
    return rows


def _build_gap(role: str, left_prime: int, right_prime: int, anchor: int) -> dict[str, object]:
    """Return one exact gap payload used by the factor-first walk."""
    profile = gwr_next_gap_profile(left_prime, block=DEFAULT_SCAN_BLOCK)
    if int(profile["next_prime"]) != right_prime:
        raise AssertionError(
            f"gap mismatch for role={role}: expected right_prime={right_prime}, "
            f"got {profile['next_prime']}"
        )

    winner_offset = profile["winner_offset"]
    winner = None if winner_offset is None else left_prime + int(winner_offset)
    return {
        "role": role,
        "left_prime": left_prime,
        "right_prime": right_prime,
        "gap_width": right_prime - left_prime,
        "contains_anchor": bool(left_prime < anchor < right_prime),
        "interior_rows": _interior_rows(left_prime, right_prime, winner),
    }


def orient_semiprime_anchor(anchor: int) -> dict[str, object]:
    """Return the previous and containing exact gap neighborhoods for one anchor."""
    validate_semiprime_anchor(anchor)

    p_left = previous_prime_before(anchor - 1, block=DEFAULT_SCAN_BLOCK)
    p_right = next_prime_after(anchor, block=DEFAULT_SCAN_BLOCK)
    p_prev = previous_prime_before(p_left - 1, block=DEFAULT_SCAN_BLOCK)
    gaps = [
        _build_gap("previous", p_prev, p_left, anchor),
        _build_gap("containing", p_left, p_right, anchor),
    ]
    return {
        "anchor": anchor,
        "scan_block": DEFAULT_SCAN_BLOCK,
        "p_prev": p_prev,
        "p_left": p_left,
        "p_right": p_right,
        "gaps": gaps,
    }


def build_factor_progress_pool(summary: dict[str, object], current_anchor: int) -> list[dict[str, object]]:
    """Return the lower odd-semiprime candidates available for one anchor."""
    candidates: list[dict[str, object]] = []
    for gap in summary["gaps"]:
        for row in gap["interior_rows"]:
            candidate = int(row["n"])
            if candidate >= current_anchor:
                continue
            if str(row["carrier_family"]) != "odd_semiprime":
                continue
            candidates.append(
                {
                    "n": candidate,
                    "role": str(gap["role"]),
                    "gap_width": int(gap["gap_width"]),
                    "offset": int(row["offset"]),
                    "is_gwr_winner": bool(row["is_gwr_winner"]),
                    "is_first_dmin": bool(row["is_first_dmin"]),
                    "is_first_d4": bool(row["is_first_d4"]),
                }
            )
    return candidates


def _role_priority(role: str) -> int:
    """Return the fixed role order used in the factor-first selector."""
    if role == "previous":
        return 0
    if role == "containing":
        return 1
    raise ValueError(f"unsupported role {role}")


def factor_progress_sort_key(candidate: dict[str, object]) -> tuple[object, ...]:
    """Return the fixed deterministic selector key for one odd-semiprime candidate."""
    return (
        _role_priority(str(candidate["role"])),
        0 if bool(candidate["is_first_d4"]) else 1,
        -int(candidate["offset"]),
        int(candidate["n"]),
    )


def select_factor_progress_candidate(
    summary: dict[str, object], current_anchor: int
) -> dict[str, object] | None:
    """Return the selected lower odd-semiprime candidate, if one exists."""
    candidates = build_factor_progress_pool(summary, current_anchor)
    if not candidates:
        return None
    return min(candidates, key=factor_progress_sort_key)


def gwr_semiprime_factor_step(modulus: int) -> dict[str, object]:
    """Run the one-step factor-first semiprime walk for one odd composite anchor."""
    summary = orient_semiprime_anchor(modulus)
    candidates = build_factor_progress_pool(summary, modulus)
    selected = select_factor_progress_candidate(summary, modulus)
    if selected is None:
        return {
            "modulus": modulus,
            "p_prev": int(summary["p_prev"]),
            "p_left": int(summary["p_left"]),
            "p_right": int(summary["p_right"]),
            "candidate_count": 0,
            "selected_anchor": None,
            "selected_role": None,
            "selected_gap_width": None,
            "selected_offset": None,
            "selected_is_first_d4": None,
            "candidate_gcd": 1,
            "factor_progress": False,
            "factor_found": False,
            "factor": None,
            "cofactor": None,
            "stop_reason": "no_odd_semiprime_candidate",
        }

    candidate_gcd = math.gcd(modulus, int(selected["n"]))
    factor_found = candidate_gcd not in (1, modulus)
    return {
        "modulus": modulus,
        "p_prev": int(summary["p_prev"]),
        "p_left": int(summary["p_left"]),
        "p_right": int(summary["p_right"]),
        "candidate_count": len(candidates),
        "selected_anchor": int(selected["n"]),
        "selected_role": str(selected["role"]),
        "selected_gap_width": int(selected["gap_width"]),
        "selected_offset": int(selected["offset"]),
        "selected_is_first_d4": bool(selected["is_first_d4"]),
        "candidate_gcd": int(candidate_gcd),
        "factor_progress": factor_found,
        "factor_found": factor_found,
        "factor": (int(candidate_gcd) if factor_found else None),
        "cofactor": (modulus // int(candidate_gcd) if factor_found else None),
        "stop_reason": "factor_found" if factor_found else "no_factor_progress",
    }


def gwr_semiprime_factor_walk(modulus: int) -> dict[str, object]:
    """Run the fixed one-step semiprime factor walk and return the full trace."""
    step = gwr_semiprime_factor_step(modulus)
    return {
        "modulus": modulus,
        "step_count": 1,
        "factor_progress": bool(step["factor_progress"]),
        "factor_found": bool(step["factor_found"]),
        "factor": step["factor"],
        "cofactor": step["cofactor"],
        "stop_reason": str(step["stop_reason"]),
        "steps": [step],
    }


__all__ = [
    "DEFAULT_SCAN_BLOCK",
    "MAX_FIELD_VALUE",
    "build_factor_progress_pool",
    "carrier_family",
    "factor_progress_sort_key",
    "gwr_semiprime_factor_step",
    "gwr_semiprime_factor_walk",
    "orient_semiprime_anchor",
    "previous_prime_before",
    "select_factor_progress_candidate",
    "validate_semiprime_anchor",
]
