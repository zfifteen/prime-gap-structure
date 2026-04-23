"""Tests for the fixed one-step semiprime factor walker."""

from __future__ import annotations

import math
import sys
from pathlib import Path

from sympy import primerange

ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = ROOT / "src" / "python"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from z_band_prime_predictor import (
    gwr_semiprime_factor_step,
    gwr_semiprime_factor_walk,
    orient_semiprime_anchor,
    select_factor_progress_candidate,
)


def toy_odd_distinct_semiprimes(max_n: int) -> list[int]:
    """Return the pinned toy odd distinct semiprime corpus up to max_n."""
    odd_primes = [prime for prime in primerange(3, max_n + 1)]
    corpus: list[int] = []
    for index, left_prime in enumerate(odd_primes):
        for right_prime in odd_primes[index + 1 :]:
            n = left_prime * right_prime
            if n > max_n:
                break
            corpus.append(n)
    corpus.sort()
    return corpus


def test_factor_step_recovers_factor_for_39():
    """The sentinel modulus 39 should recover factor 3 from the first step."""
    step = gwr_semiprime_factor_step(39)

    assert step["selected_anchor"] == 33
    assert step["selected_role"] == "previous"
    assert step["selected_is_first_d4"] is True
    assert step["candidate_gcd"] == 3
    assert step["factor_progress"] is True
    assert step["factor_found"] is True
    assert step["factor"] == 3
    assert step["cofactor"] == 13
    assert step["stop_reason"] == "factor_found"


def test_factor_step_fails_fast_when_candidate_has_no_shared_factor():
    """The walker should stop immediately when the selected anchor gives no gcd hit."""
    step = gwr_semiprime_factor_step(35)

    assert step["selected_anchor"] == 33
    assert step["candidate_gcd"] == 1
    assert step["factor_progress"] is False
    assert step["factor_found"] is False
    assert step["factor"] is None
    assert step["cofactor"] is None
    assert step["stop_reason"] == "no_factor_progress"


def test_factor_step_reports_no_candidate_when_local_pool_is_empty():
    """The walker should fail explicitly when no lower odd semiprime exists locally."""
    step = gwr_semiprime_factor_step(15)

    assert step["candidate_count"] == 0
    assert step["selected_anchor"] is None
    assert step["factor_found"] is False
    assert step["stop_reason"] == "no_odd_semiprime_candidate"


def test_factor_walk_wraps_the_single_step_contract():
    """The walk wrapper should return one step and the same terminal result."""
    walk = gwr_semiprime_factor_walk(39)

    assert walk["step_count"] == 1
    assert walk["factor_found"] is True
    assert walk["factor"] == 3
    assert walk["cofactor"] == 13
    assert walk["stop_reason"] == "factor_found"
    assert len(walk["steps"]) == 1
    assert walk["steps"][0]["selected_anchor"] == 33


def test_selector_is_deterministic_on_oriented_anchor():
    """The selected factor-progress candidate should be stable for one anchor."""
    summary = orient_semiprime_anchor(39)
    selected_a = select_factor_progress_candidate(summary, 39)
    selected_b = select_factor_progress_candidate(summary, 39)

    assert selected_a == selected_b
    assert selected_a is not None
    assert selected_a["n"] == 33


def test_reduced_toy_surface_has_pinned_factor_hit_count():
    """The fixed one-step walker should keep its reduced-surface hit count."""
    corpus = toy_odd_distinct_semiprimes(500)
    hit_count = 0
    no_progress_count = 0
    no_candidate_count = 0

    for modulus in corpus:
        step = gwr_semiprime_factor_step(modulus)
        if step["factor_found"]:
            hit_count += 1
            factor = int(step["factor"])
            assert factor not in (1, modulus)
            assert modulus % factor == 0
        elif step["stop_reason"] == "no_factor_progress":
            no_progress_count += 1
            assert step["selected_anchor"] is not None
            assert math.gcd(modulus, int(step["selected_anchor"])) == 1
        else:
            no_candidate_count += 1
            assert step["stop_reason"] == "no_odd_semiprime_candidate"

    assert len(corpus) == 93
    assert hit_count == 8
    assert no_progress_count == 61
    assert no_candidate_count == 24


def test_factor_step_rejects_non_composite_anchor():
    """Prime anchors are outside the factor-first walk contract."""
    try:
        gwr_semiprime_factor_step(13)
    except ValueError as exc:
        assert "composite" in str(exc)
    else:
        raise AssertionError("gwr_semiprime_factor_step(13) should raise ValueError")
