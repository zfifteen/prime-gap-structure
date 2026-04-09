"""Tests for the packaged PNT/GWR predictor helper."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from sympy import divisor_count


ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = ROOT / "src" / "python"

if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

import z_band_prime_predictor as predictor


def test_placed_seed_recovery_is_exact():
    """A composite seed inside one prime gap recovers the right endpoint exactly."""
    assert predictor.placed_prime_from_seed(4) == 5
    assert predictor.placed_prime_from_seed(10) == 11
    assert predictor.placed_prime_from_seed(16) == 17


def test_gwr_predict_succeeds_when_the_requested_carrier_is_still_ahead():
    """Witness recovery works when the target divisor carrier remains in-gap."""
    assert predictor.gwr_predict(8, d=3) == (11, 9, None)
    assert predictor.gwr_predict(14, d=4) == (17, 14, 25)
    assert predictor.gwr_predict(42, d=8) == (43, 42, None)


def test_gwr_predict_fails_fast_when_the_seed_is_past_the_last_carrier():
    """The corrected implementation should stop instead of drifting into later gaps."""
    with pytest.raises(ValueError, match="no d=3 witness"):
        predictor.gwr_predict(10, d=3)

    with pytest.raises(ValueError, match="no d=4 witness"):
        predictor.gwr_predict(4, d=4)


def test_predict_nth_prime_stays_explicitly_open():
    """The nth-prime predictor should fail explicitly until the seed problem is solved."""
    with pytest.raises(NotImplementedError, match="seed-tightness problem remains open"):
        predictor.predict_nth_prime(100)


def test_d4_gap_profile_returns_exact_gap_geometry():
    """The dominant d=4 path should expose the exact spoiler and in-gap carriers."""
    profile = predictor.d4_gap_profile(13, 17)

    assert profile == {
        "left_prime": 13,
        "right_prime": 17,
        "gap_has_d4": True,
        "last_pre_gap_d4": 10,
        "first_in_gap_d4": 14,
        "last_in_gap_d4": 15,
    }


def test_divisor_gap_profile_returns_exact_corridor_geometry():
    """The generic divisor-class profile should expose the exact corridor."""
    profile = predictor.divisor_gap_profile(17, 19, 6)

    assert profile == {
        "left_prime": 17,
        "right_prime": 19,
        "divisor_target": 6,
        "gap_has_target_carrier": True,
        "last_pre_gap_carrier": 12,
        "first_in_gap_carrier": 18,
        "last_in_gap_carrier": 18,
        "corridor_start": 13,
        "corridor_end": 18,
        "corridor_width": 6,
    }


def test_seed_hits_d4_corridor_matches_the_exact_spoiler_rule():
    """A seed must lie after the last pre-gap d=4 carrier and before the last in-gap one."""
    assert predictor.seed_hits_d4_corridor(11, 13, 17) is True
    assert predictor.seed_hits_d4_corridor(10, 13, 17) is False
    assert predictor.seed_hits_d4_corridor(16, 13, 17) is False
    assert predictor.seed_hits_d4_corridor(4, 3, 5) is False


def test_pnt_gwr_d4_candidate_is_available_as_an_approximate_surface():
    """The approximate dominant-regime candidate path should remain deterministic."""
    candidate, witness, seed = predictor.pnt_gwr_d4_candidate(100)

    assert seed == predictor.pnt_seed(100)
    assert witness == predictor.W_d(seed, 4)
    assert candidate > seed


def test_high_decade_witness_search_stays_exact():
    """The fast interval kernel should preserve exact witness recovery near 10^18."""
    start = 10**18 - 64
    stop_exclusive = 10**18 + 512

    expected = None
    for value in range(start, stop_exclusive):
        if divisor_count(value) == 4:
            expected = value
            break
    assert expected is not None
    assert predictor.W_d(start, 4, stop_exclusive=stop_exclusive) == expected
