"""Tests for the local PNT/GWR predictor research helper."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "docs" / "research" / "predictor" / "pnt_gwr_predictor.py"


def load_module():
    """Load the predictor helper directly from its file path."""
    spec = importlib.util.spec_from_file_location("pnt_gwr_predictor", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load pnt_gwr_predictor module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_placed_seed_recovery_is_exact():
    """A composite seed inside one prime gap recovers the right endpoint exactly."""
    module = load_module()

    assert module.placed_prime_from_seed(4) == 5
    assert module.placed_prime_from_seed(10) == 11
    assert module.placed_prime_from_seed(16) == 17


def test_gwr_predict_succeeds_when_the_requested_carrier_is_still_ahead():
    """Witness recovery works when the target divisor carrier remains in-gap."""
    module = load_module()

    assert module.gwr_predict(8, d=3) == (11, 9, None)
    assert module.gwr_predict(14, d=4) == (17, 14, 25)
    assert module.gwr_predict(42, d=8) == (43, 42, None)


def test_gwr_predict_fails_fast_when_the_seed_is_past_the_last_carrier():
    """The corrected implementation should stop instead of drifting into later gaps."""
    module = load_module()

    with pytest.raises(ValueError, match="no d=3 witness"):
        module.gwr_predict(10, d=3)

    with pytest.raises(ValueError, match="no d=4 witness"):
        module.gwr_predict(4, d=4)


def test_predict_nth_prime_stays_explicitly_open():
    """The nth-prime predictor should fail explicitly until the seed problem is solved."""
    module = load_module()

    with pytest.raises(NotImplementedError, match="seed-tightness problem remains open"):
        module.predict_nth_prime(100)


def test_pnt_gwr_d4_candidate_is_available_as_an_approximate_surface():
    """The approximate dominant-regime candidate path should remain deterministic."""
    module = load_module()

    candidate, witness, seed = module.pnt_gwr_d4_candidate(100)

    assert seed == module.pnt_seed(100)
    assert witness == module.W_d(seed, 4)
    assert candidate > seed
