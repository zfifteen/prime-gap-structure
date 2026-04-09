#!/usr/bin/env python3
"""Research helpers for the placed PNT/GWR prime formula."""

from __future__ import annotations

from math import isqrt, log

from sympy import divisor_count, isprime, nextprime, prevprime


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


def W_d(x: int, d: int, stop_exclusive: int | None = None) -> int:
    """
    Return the first composite at or after x with exactly d divisors.

    When stop_exclusive is provided, fail explicitly if the search leaves the
    admissible interval before finding the requested carrier.
    """
    if d < 3:
        raise ValueError("d must be at least 3")

    witness = max(4, int(x))
    while True:
        if stop_exclusive is not None and witness >= stop_exclusive:
            raise ValueError(
                f"no d={d} witness exists in [{int(x)}, {stop_exclusive})"
            )
        if not isprime(witness) and divisor_count(witness) == d:
            return witness
        witness += 1


def gap_dmin(p: int, q: int) -> int | None:
    """Return the minimum interior divisor count for one prime gap."""
    if q <= p:
        raise ValueError("q must be larger than p")
    if q - p <= 1:
        return None

    interior = range(p + 1, q)
    return min(divisor_count(k) for k in interior)


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
    approximate candidate, or use sympy.prime(n) for the exact tautological
    value during audit work.
    """
    raise NotImplementedError(
        "Exact predict_nth_prime is not implemented because the seed-tightness "
        "problem remains open. Use pnt_gwr_d4_candidate(n) for the current "
        "approximate dominant-regime candidate."
    )


def run_tests() -> bool:
    """Run a minimal exact self-check for the placed formula helpers."""
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


if __name__ == "__main__":
    raise SystemExit(0 if run_tests() else 1)
