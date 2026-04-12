"""Exact divisor-field boundary walk for next-prime recovery.

This module exposes a minimal standalone shell over the repo's exact divisor
field. It does not introduce a new primality engine. The underlying field in
``z_band_prime_composite_field.divisor_counts_segment`` still classifies large
residuals with ``gmpy2.is_prime``.

So the routines here are exact on the current repo field and on the same
verified surface as the unbounded DNI/GWR recursive walk, but they should be
described honestly as divisor-field boundary walks rather than as a new
primality-free foundation.
"""

from __future__ import annotations

from z_band_prime_composite_field import divisor_counts_segment


DEFAULT_SCAN_BLOCK = 64


def _divisor_count_at(n: int) -> int:
    """Return the exact divisor count at one integer."""
    if n < 1:
        raise ValueError("n must be at least 1")
    return int(divisor_counts_segment(n, n + 1)[0])


def gwr_next_gap_profile(q: int, block: int = DEFAULT_SCAN_BLOCK) -> dict[str, int | None]:
    """Return the exact divisor-field boundary profile for the gap after one prime.

    The contract is narrow:

    - ``q`` must be prime;
    - scanning stops at the first rightward value with ``d(n) == 2``;
    - the returned winner fields record the minimum interior divisor class and
      its leftmost carrier offset when the gap has an interior.

    For ``q = 2``, the gap ``(2, 3)`` has no interior composite, so the winner
    fields are ``None`` and the prime boundary is still returned exactly.
    """
    if q < 2:
        raise ValueError("q must be at least 2")
    if block < 1:
        raise ValueError("block must be positive")
    if _divisor_count_at(q) != 2:
        raise ValueError("q must be prime")

    cursor = q + 1
    base_offset = 1
    winner_d: int | None = None
    winner_offset: int | None = None

    while True:
        counts = divisor_counts_segment(cursor, cursor + block)
        for index, raw_d in enumerate(counts):
            d = int(raw_d)
            offset = base_offset + index
            if d == 2:
                return {
                    "current_prime": q,
                    "next_prime": q + offset,
                    "gap_boundary_offset": offset,
                    "winner_d": winner_d,
                    "winner_offset": winner_offset,
                }
            if winner_d is None or d < winner_d or (d == winner_d and offset < winner_offset):
                winner_d = d
                winner_offset = offset

        cursor += block
        base_offset += block


def gwr_next_prime(q: int, block: int = DEFAULT_SCAN_BLOCK) -> int:
    """Return the next prime after one known prime by exact divisor-field scan.

    This is an exact computation on the current repo field. The return value is
    the first rightward boundary where ``d(n) == 2``.
    """
    profile = gwr_next_gap_profile(q, block=block)
    return int(profile["next_prime"])


def next_prime_after(n: int, block: int = DEFAULT_SCAN_BLOCK) -> int:
    """Return the first prime strictly larger than ``n`` by divisor-field scan.

    When ``n`` is prime, this delegates to ``gwr_next_prime`` and returns the
    next prime gap boundary after that anchor. When ``n`` is composite, this
    routine performs a direct rightward divisor-field scan and returns the first
    value with ``d(n) == 2``. That composite-anchor path is exact, but it is
    not a separate GWR theorem claim about non-prime anchors.
    """
    if n < 2:
        return 2
    if block < 1:
        raise ValueError("block must be positive")

    if _divisor_count_at(n) == 2:
        return gwr_next_prime(n, block=block)

    cursor = n + 1
    while True:
        counts = divisor_counts_segment(cursor, cursor + block)
        for index, raw_d in enumerate(counts):
            if int(raw_d) == 2:
                return cursor + index
        cursor += block


__all__ = [
    "DEFAULT_SCAN_BLOCK",
    "gwr_next_gap_profile",
    "gwr_next_prime",
    "next_prime_after",
]
