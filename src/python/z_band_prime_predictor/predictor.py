"""Production Python surface for the placed PNT/GWR prime predictor helpers."""

from __future__ import annotations

from functools import lru_cache
from math import isqrt, log

import numpy as np
from sympy import isprime, nextprime, prevprime

from z_band_prime_composite_field import divisor_counts_segment


DIVISOR_WINDOW_SPAN = 65_536


def li_inverse(n: int) -> float:
    """Return the two-term Cipolla approximation to Li^{-1}(n)."""
    if n < 2:
        raise ValueError("n must be at least 2")

    ln_n = log(n)
    ll_n = log(ln_n)
    return n * (ln_n + ll_n - 1.0 + (ll_n - 2.0) / ln_n)


def pnt_seed(n: int) -> int:
    """Return the integer PNT backbone seed for p_n."""
    return max(2, int(li_inverse(n)))


def _window_start_for(lo: int) -> int:
    """Return the inclusive aligned window start for one interval."""
    if lo < 1:
        raise ValueError("lo must be at least 1")
    return ((lo - 1) // DIVISOR_WINDOW_SPAN) * DIVISOR_WINDOW_SPAN + 1


@lru_cache(maxsize=64)
def _cached_divisor_window(window_lo: int):
    """Return one cached exact divisor-count window."""
    return divisor_counts_segment(window_lo, window_lo + DIVISOR_WINDOW_SPAN)


def _divisor_counts_interval(lo: int, hi: int):
    """Return exact divisor counts on one half-open interval."""
    if lo < 1:
        raise ValueError("lo must be at least 1")
    if hi <= lo:
        raise ValueError("hi must be larger than lo")

    pieces = []
    cursor = lo
    while cursor < hi:
        window_lo = _window_start_for(cursor)
        window_hi = window_lo + DIVISOR_WINDOW_SPAN
        counts = _cached_divisor_window(window_lo)
        take_hi = min(hi, window_hi)
        pieces.append(counts[cursor - window_lo : take_hi - window_lo])
        cursor = take_hi

    if len(pieces) == 1:
        return pieces[0]
    return np.concatenate(pieces)


def _first_value_with_divisors_at_or_after(
    start: int,
    d: int,
    stop_exclusive: int | None = None,
) -> int:
    """Return the first integer at or after start with exactly d divisors."""
    if d < 3:
        raise ValueError("d must be at least 3")

    search_lo = max(4, int(start))
    while True:
        search_hi = search_lo + DIVISOR_WINDOW_SPAN
        if stop_exclusive is not None:
            search_hi = min(search_hi, stop_exclusive)
        if search_hi <= search_lo:
            raise ValueError(
                f"no d={d} witness exists in [{int(start)}, {stop_exclusive})"
            )

        counts = _divisor_counts_interval(search_lo, search_hi)
        for offset, count in enumerate(counts):
            if int(count) == d:
                return search_lo + offset

        if stop_exclusive is not None and search_hi >= stop_exclusive:
            raise ValueError(
                f"no d={d} witness exists in [{int(start)}, {stop_exclusive})"
            )
        search_lo = search_hi


def _last_value_with_divisors_before(stop_exclusive: int, d: int) -> int | None:
    """Return the last integer below stop_exclusive with exactly d divisors."""
    if d < 3:
        raise ValueError("d must be at least 3")

    search_hi = int(stop_exclusive)
    while search_hi > 4:
        search_lo = max(4, search_hi - DIVISOR_WINDOW_SPAN)
        counts = _divisor_counts_interval(search_lo, search_hi)
        for offset in range(len(counts) - 1, -1, -1):
            if int(counts[offset]) == d:
                return search_lo + offset
        search_hi = search_lo
    return None


def W_d(x: int, d: int, stop_exclusive: int | None = None) -> int:
    """
    Return the first composite at or after x with exactly d divisors.

    When stop_exclusive is provided, fail explicitly if the search leaves the
    admissible interval before finding the requested carrier.
    """
    if d < 3:
        raise ValueError("d must be at least 3")
    return _first_value_with_divisors_at_or_after(x, d, stop_exclusive=stop_exclusive)


def gap_dmin(p: int, q: int) -> int | None:
    """Return the minimum interior divisor count for one prime gap."""
    if q <= p:
        raise ValueError("q must be larger than p")
    if q - p <= 1:
        return None

    return int(_divisor_counts_interval(p + 1, q).min())


def gap_from_interior_seed(seed: int) -> tuple[int, int]:
    """Return the prime gap containing one composite interior seed."""
    if seed < 4:
        raise ValueError("seed must be at least 4")
    if isprime(seed):
        raise ValueError("seed must be a composite interior point")

    right_prime = int(nextprime(seed - 1))
    left_prime = int(prevprime(right_prime))
    if not left_prime < seed < right_prime:
        raise ValueError("seed must lie strictly inside one prime gap")
    return left_prime, right_prime


def placed_prime_from_seed(seed: int) -> int:
    """Return the right endpoint prime of the gap containing the seed."""
    _, right_prime = gap_from_interior_seed(seed)
    return right_prime


def _last_composite_with_divisors_before(stop_exclusive: int, d: int) -> int | None:
    """Return the last composite with exactly d divisors below stop_exclusive."""
    return _last_value_with_divisors_before(stop_exclusive, d)


def divisor_gap_profile(left_prime: int, right_prime: int, d: int) -> dict[str, int | bool | None]:
    """Return the exact carrier geometry for one divisor class around one prime gap."""
    if d < 3:
        raise ValueError("d must be at least 3")
    if right_prime <= left_prime:
        raise ValueError("right_prime must be larger than left_prime")

    last_pre_gap_carrier = _last_value_with_divisors_before(left_prime, d)
    first_in_gap_carrier = None
    last_in_gap_carrier = None
    if right_prime - left_prime > 1:
        counts = _divisor_counts_interval(left_prime + 1, right_prime)
        for offset, count in enumerate(counts):
            if int(count) != d:
                continue
            carrier = left_prime + 1 + offset
            if first_in_gap_carrier is None:
                first_in_gap_carrier = carrier
            last_in_gap_carrier = carrier

    corridor_start = None
    corridor_end = None
    corridor_width = None
    if last_in_gap_carrier is not None:
        corridor_start = int(last_pre_gap_carrier) + 1 if last_pre_gap_carrier is not None else 4
        corridor_end = int(last_in_gap_carrier)
        corridor_width = corridor_end - corridor_start + 1

    return {
        "left_prime": left_prime,
        "right_prime": right_prime,
        "divisor_target": d,
        "gap_has_target_carrier": first_in_gap_carrier is not None,
        "last_pre_gap_carrier": last_pre_gap_carrier,
        "first_in_gap_carrier": first_in_gap_carrier,
        "last_in_gap_carrier": last_in_gap_carrier,
        "corridor_start": corridor_start,
        "corridor_end": corridor_end,
        "corridor_width": corridor_width,
    }


def d4_gap_profile(left_prime: int, right_prime: int) -> dict[str, int | bool | None]:
    """
    Return the exact dominant d=4 carrier geometry around one prime gap.

    The admissible seed corridor for the d=4 witness path is
    (last_pre_gap_d4, last_in_gap_d4]. Seeds at or below last_pre_gap_d4 are
    blocked by a pre-gap spoiler. Seeds above last_in_gap_d4 miss the target
    gap because no in-gap d=4 carrier remains.
    """
    if right_prime <= left_prime:
        raise ValueError("right_prime must be larger than left_prime")
    profile = divisor_gap_profile(left_prime, right_prime, 4)

    return {
        "left_prime": left_prime,
        "right_prime": right_prime,
        "gap_has_d4": bool(profile["gap_has_target_carrier"]),
        "last_pre_gap_d4": profile["last_pre_gap_carrier"],
        "first_in_gap_d4": profile["first_in_gap_carrier"],
        "last_in_gap_d4": profile["last_in_gap_carrier"],
    }


def seed_hits_d4_corridor(seed: int, left_prime: int, right_prime: int) -> bool:
    """Return whether one integer seed lies in the exact d=4 seed corridor."""
    profile = d4_gap_profile(left_prime, right_prime)
    last_in_gap_d4 = profile["last_in_gap_d4"]
    if last_in_gap_d4 is None:
        return False

    last_pre_gap_d4 = profile["last_pre_gap_d4"]
    return bool(
        (last_pre_gap_d4 is None or seed > last_pre_gap_d4) and seed <= last_in_gap_d4
    )


def d4_closure_ceiling(witness: int) -> int:
    """
    Return the first prime square strictly larger than one d=4 witness.

    This is the dominant-regime closure ceiling used only for d=4 witnesses.
    It is not a generic bound for arbitrary witnesses.
    """
    root = isqrt(witness) + 1
    while not isprime(root):
        root += 1
    return root * root


def gwr_predict(seed: int, d: int | None = None) -> tuple[int, int, int | None]:
    """
    Recover the gap's right endpoint from a placed seed when an admissible witness exists.

    If d is omitted, the function uses the true gap-local dmin. The witness
    search then succeeds exactly when a carrier of that divisor class still lies
    in [seed, p_n).
    """
    left_prime, right_prime = gap_from_interior_seed(seed)
    divisor_target = gap_dmin(left_prime, right_prime) if d is None else d
    if divisor_target is None:
        raise ValueError("the enclosing gap has no composite interior")

    witness = W_d(seed, divisor_target, stop_exclusive=right_prime)
    recovered_prime = int(nextprime(witness - 1))
    if recovered_prime != right_prime:
        raise AssertionError(
            f"witness recovery failed: seed={seed}, d={divisor_target}, "
            f"witness={witness}, recovered={recovered_prime}, expected={right_prime}"
        )

    closure = None
    if divisor_target == 4:
        closure = d4_closure_ceiling(witness)
        if right_prime > closure:
            raise AssertionError(
                f"d=4 closure ceiling violated: q={right_prime}, S_+(w)={closure}, w={witness}"
            )

    return right_prime, witness, closure


def pnt_gwr_d4_candidate(n: int) -> tuple[int, int, int]:
    """
    Return the current PNT-seeded dominant-regime candidate.

    This is an approximate research candidate only. It does not certify that
    the returned prime is p_n.
    """
    seed = pnt_seed(n)
    witness = W_d(seed, 4)
    return int(nextprime(witness - 1)), witness, seed


def predict_nth_prime(n: int) -> tuple[int, int, int]:
    """
    Exact nth-prime prediction remains open in this project.

    The current PNT seed does not place reliably enough to certify p_n without
    additional structure. Call pnt_gwr_d4_candidate(n) for the current
    approximate candidate.
    """
    raise NotImplementedError(
        "Exact predict_nth_prime is not implemented because the seed-tightness "
        "problem remains open. Use pnt_gwr_d4_candidate(n) for the current "
        "approximate dominant-regime candidate."
    )


def run_tests() -> bool:
    """Run a minimal exact self-check for the predictor helpers."""
    checks = [
        ("placed seed 4 -> 5", placed_prime_from_seed(4) == 5),
        ("placed seed 10 -> 11", placed_prime_from_seed(10) == 11),
        ("W_3(10) -> 25", W_d(10, 3) == 25),
        ("W_4(4) -> 6", W_d(4, 4) == 6),
        ("gwr_predict(8,3) -> 11", gwr_predict(8, d=3)[0] == 11),
        ("gwr_predict(14,4) -> 17", gwr_predict(14, d=4)[0] == 17),
    ]

    all_passed = True
    for label, passed in checks:
        print(f"{label}: {'PASS' if passed else 'FAIL'}")
        all_passed = all_passed and passed

    for seed, d in ((10, 3), (4, 4)):
        try:
            gwr_predict(seed, d=d)
        except ValueError:
            print(f"gwr_predict({seed}, d={d}) fail-fast: PASS")
        else:
            print(f"gwr_predict({seed}, d={d}) fail-fast: FAIL")
            all_passed = False

    try:
        predict_nth_prime(10)
    except NotImplementedError:
        print("predict_nth_prime(10) open-problem guard: PASS")
    else:
        print("predict_nth_prime(10) open-problem guard: FAIL")
        all_passed = False

    return all_passed
