"""Unit checks for pure-PGS divisor-horizon law."""

from __future__ import annotations

import math

from z_band_prime_predictor.pure_pgs_horizon import (
    default_pure_horizon,
    h_ubc,
    h_visible_plus_2max_gap,
    pure_pgs_horizon,
)


def test_h_ubc_matches_proved_cutoff():
    assert h_ubc(100) == 64
    assert h_ubc(10**6) == max(64, math.ceil(0.5 * math.log(10**6) ** 2))
    assert h_ubc(10**18) == max(64, math.ceil(0.5 * math.log(10**18) ** 2))
    # At 10^18 the UBC horizon is still tiny vs sqrt(q) ~ 10^9
    assert h_ubc(10**18) < 2000


def test_visible_2maxgap_tight():
    assert h_visible_plus_2max_gap(10_000, [2, 4, 6]) == 10_000 + 12
    assert h_visible_plus_2max_gap(64, []) == 64


def test_default_pure_horizon_ubc():
    h = default_pure_horizon(p=10**12, s0=10**12 + 30, chain_deltas=[6, 12])
    assert h == h_ubc(10**12 + 128)
    assert h < math.isqrt(10**12 + 128)


def test_modes_are_local():
    for mode in ("ubc", "visible_2maxgap", "visible_maxgap"):
        h = pure_pgs_horizon(
            10**15, 10**15 + 90, [30, 60],
            visible_divisor_bound=10_000, mode=mode,
        )
        assert h < 100_000  # orders of magnitude below sqrt(10^15)
