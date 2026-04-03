"""Tests for the production CDL Z-Band prefilter module."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest
from sympy import isprime


SOURCE_DIR = Path(__file__).resolve().parents[3] / "src" / "python"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

import geodesic_prime_prefilter.prefilter as prefilter
from geodesic_prime_invariant import exact_divisor_count


def test_prefilter_rejects_small_factor_composites_and_keeps_prime_band():
    """The production proxy should contract easy composites and keep prime survivors."""
    geodesic = prefilter.CDLPrimeZBandPrefilter(bit_length=32, namespace="unit")

    assert geodesic.is_prime_candidate(101) is True
    assert geodesic.proxy_z(101) == 1.0

    composite = 3 * 101
    assert geodesic.is_prime_candidate(composite) is False
    assert geodesic.proxy_z(composite) < 1.0
    assert geodesic.is_prime_candidate(100) is False
    assert geodesic.proxy_z(100) < 1.0


def test_large_composite_underflow_stays_explicitly_rejected():
    """Very large rejected composites should clamp cleanly instead of overflowing logs."""
    geodesic = prefilter.CDLPrimeZBandPrefilter(bit_length=2048, namespace="unit:large")
    composite = 3 * ((1 << 2046) + 1)

    assert geodesic.is_prime_candidate(composite) is False
    assert geodesic.proxy_z(composite) == 0.0


def test_generate_prime_matches_first_baseline_survivor_on_same_stream():
    """The integrated generator should return the same first prime as MR-only search."""
    namespace = "unit:baseline"
    expected = None
    index = 0
    seen = set()

    while expected is None:
        candidate = prefilter.deterministic_odd_candidate(32, index, namespace=namespace)
        index += 1
        if candidate in seen:
            continue
        seen.add(candidate)
        if math.gcd(candidate - 1, 65537) != 1:
            continue
        if prefilter.miller_rabin_fixed_bases(candidate, prefilter.DEFAULT_MR_BASES):
            expected = candidate

    geodesic = prefilter.CDLPrimeZBandPrefilter(bit_length=32, namespace=namespace)
    actual = geodesic.generate_prime(public_exponent=65537)

    assert actual == expected
    assert prefilter.miller_rabin_fixed_bases(actual, prefilter.DEFAULT_MR_BASES) is True


def test_prefilter_exposes_tunable_tables_and_bounds_dedup_memory():
    """Constructor parameters should tune the tables while large-bit streams skip dedup storage."""
    small = prefilter.CDLPrimeZBandPrefilter(
        bit_length=32,
        namespace="unit:small",
        primary_prime_limit=97,
        primary_chunk_size=8,
        tail_prime_limit=127,
        tail_chunk_size=8,
        deep_tail_prime_limit=191,
        deep_tail_chunk_size=8,
        deep_tail_min_bits=64,
    )
    large = prefilter.CDLPrimeZBandPrefilter(bit_length=256, namespace="unit:large")

    assert small.primary_table.limit == 97
    assert small.tail_table.limit == 127
    assert small.deep_tail_min_bits == 64
    assert small._seen_candidates == set()
    assert large._seen_candidates is None
    assert small.primary_table is prefilter.get_cached_wheel_prime_table(97, 8)


def test_generate_prime_rejects_known_strong_pseudoprime():
    """The public acceptance path should not accept the fixed-base pseudoprime example."""
    geodesic = prefilter.CDLPrimeZBandPrefilter(bit_length=64, namespace="unit:pseudoprime")
    pseudoprime = 341550071728321

    assert prefilter.miller_rabin_fixed_bases(pseudoprime, prefilter.DEFAULT_MR_BASES) is True
    assert geodesic.is_probable_prime(pseudoprime) is False


def test_generate_prime_validates_public_exponent_up_front():
    """Invalid RSA exponents should fail fast instead of spinning the search loop."""
    geodesic = prefilter.CDLPrimeZBandPrefilter(bit_length=32, namespace="unit:exp")

    with pytest.raises(ValueError, match="public_exponent"):
        geodesic.generate_prime(public_exponent=2)


def test_generate_rsa_prime_hits_exact_small_scale_fixed_point():
    """A generated small RSA prime should satisfy the exact DNI condition."""
    prime = prefilter.generate_rsa_prime(bit_length=32, namespace="unit:rsa")

    assert isprime(prime) is True
    assert exact_divisor_count(prime) == 2
    assert math.isclose(
        math.exp((1.0 - exact_divisor_count(prime) / 2.0) * math.log(prime)),
        1.0,
        rel_tol=prefilter.FIXED_POINT_TOLERANCE,
        abs_tol=prefilter.FIXED_POINT_TOLERANCE,
    )
