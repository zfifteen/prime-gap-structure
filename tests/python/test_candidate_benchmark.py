"""Tests for the crypto prefilter benchmark utilities."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT.parent / "benchmarks" / "python" / "candidate_benchmark.py"


def load_module():
    """Load the benchmark module from its file path."""
    spec = importlib.util.spec_from_file_location("candidate_benchmark", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load crypto prefilter benchmark module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_deterministic_odd_candidates_are_reproducible():
    """The candidate corpus must stay deterministic and stay in the requested bit window."""
    module = load_module()
    first = module.deterministic_odd_candidates(32, 6)
    second = module.deterministic_odd_candidates(32, 6)

    assert first == second
    assert len(set(first)) == 6
    for candidate in first:
        assert candidate.bit_length() == 32
        assert candidate % 2 == 1


def test_miller_rabin_fixed_bases_matches_known_small_cases():
    """The control path should classify a small known panel correctly."""
    module = load_module()
    bases = [2, 3, 5, 7, 11]
    cases = {
        2: True,
        3: True,
        5: True,
        7: True,
        97: True,
        4: False,
        9: False,
        15: False,
        21: False,
        341: False,
        561: False,
        645: False,
    }

    for value, expected in cases.items():
        assert module.miller_rabin_fixed_bases(value, bases) is expected


def test_sieve_primes_is_deterministic_and_complete_on_small_limit():
    """The proxy's prime table should be deterministic and correct on a small window."""
    module = load_module()
    assert module.sieve_primes(20) == [2, 3, 5, 7, 11, 13, 17, 19]


def test_wheel_prime_table_builds_deterministic_chunks():
    """The precomputed table should expose stable prime and chunk metadata."""
    module = load_module()
    table = module.WheelPrimeTable(limit=97, chunk_size=8)

    assert table.limit == 97
    assert table.chunk_size == 8
    assert len(table.primes) == 24
    assert len(table.chunks) == 3
    assert len(table.chunk_products) == 3
    assert table.find_small_factor(303) == 3
    assert table.find_small_factor(101) is None


def test_wheel_prime_table_respects_interval_start():
    """Tail tables should scan only the primes above the primary interval."""
    module = load_module()
    table = module.WheelPrimeTable(limit=97, chunk_size=8, start_exclusive=19)

    assert table.start_exclusive == 19
    assert table.primes[0] == 23
    assert 19 not in table.primes
    assert table.find_small_factor(17 * 101) is None
    assert table.find_small_factor(23 * 101) == 23


def test_cheap_cdl_proxy_rejects_small_factor_composites_and_keeps_prime_band():
    """The deterministic proxy should reject obvious composites and preserve prime survivors."""
    module = load_module()
    table = module.WheelPrimeTable(limit=97, chunk_size=8)

    prime_proxy = module.cheap_cdl_proxy(101, table)
    composite_proxy = module.cheap_cdl_proxy(303, table)

    assert prime_proxy["rejected"] is False
    assert prime_proxy["z_hat"] == 1.0
    assert composite_proxy["rejected"] is True
    assert composite_proxy["smallest_factor"] == 3
    assert composite_proxy["z_hat"] < 1.0
    even_proxy = module.cheap_cdl_proxy(100, table)
    assert even_proxy["rejected"] is True
    assert even_proxy["smallest_factor"] == 2
    assert even_proxy["factor_source"] == "even"


def test_cheap_cdl_proxy_tail_interval_rejects_survivor_without_moving_prime_band():
    """The tail interval should catch later factors while keeping prime survivors at Z = 1."""
    module = load_module()
    primary_table = module.WheelPrimeTable(limit=19, chunk_size=4)
    tail_table = module.WheelPrimeTable(limit=97, chunk_size=4, start_exclusive=19)

    prime_proxy = module.cheap_cdl_proxy(101, primary_table, tail_prime_table=tail_table)
    composite_proxy = module.cheap_cdl_proxy(23 * 101, primary_table, tail_prime_table=tail_table)

    assert prime_proxy["rejected"] is False
    assert prime_proxy["factor_source"] == "survivor"
    assert prime_proxy["z_hat"] == 1.0
    assert composite_proxy["rejected"] is True
    assert composite_proxy["factor_source"] == "tail"
    assert composite_proxy["smallest_factor"] == 23


def test_cheap_cdl_proxy_deep_tail_gate_only_activates_at_or_above_threshold():
    """The deeper tail should stay dormant below the gate and reject only when the gate opens."""
    module = load_module()
    primary_table = module.WheelPrimeTable(limit=19, chunk_size=4)
    tail_table = module.WheelPrimeTable(limit=29, chunk_size=4, start_exclusive=19)
    deep_tail_table = module.WheelPrimeTable(limit=97, chunk_size=4, start_exclusive=29)
    composite = 31 * 101

    gated_off = module.cheap_cdl_proxy(
        composite,
        primary_table,
        tail_prime_table=tail_table,
        deep_tail_prime_table=deep_tail_table,
        deep_tail_min_bits=composite.bit_length() + 1,
    )
    gated_on = module.cheap_cdl_proxy(
        composite,
        primary_table,
        tail_prime_table=tail_table,
        deep_tail_prime_table=deep_tail_table,
        deep_tail_min_bits=composite.bit_length(),
    )

    assert gated_off["rejected"] is False
    assert gated_off["factor_source"] == "survivor"
    assert gated_on["rejected"] is True
    assert gated_on["factor_source"] == "deep_tail"
    assert gated_on["smallest_factor"] == 31


def test_exact_calibration_keeps_fixed_points_on_primes():
    """The calibration harness should preserve the prime DCI band on a small panel."""
    module = load_module()
    candidates = [3, 5, 9, 15, 21]
    result = module.run_exact_calibration(candidates, mr_bases=[2, 3, 5, 7])

    assert result["candidate_count"] == 5
    assert result["prime_count"] == 2
    assert result["composite_count"] == 3
    assert result["algebraic_fixed_points"] == 2
    assert result["numeric_false_fixed_points"] == 0
    assert result["strict_contractions"] == 3
    assert result["miller_rabin_control"]["false_positives"] == 0
    assert result["miller_rabin_control"]["false_negatives"] == 0


def test_proxy_pipeline_rejects_small_factor_composites_before_miller_rabin():
    """The proxy+MR path should reject easy composites before the control test runs."""
    module = load_module()
    primary_table = module.WheelPrimeTable(limit=19, chunk_size=4)
    tail_table = module.WheelPrimeTable(limit=97, chunk_size=4, start_exclusive=19)
    candidates = [101, 303, 509, 23 * 101]
    result = module.run_proxy_crypto_pipeline(
        candidates,
        prime_table=primary_table,
        tail_prime_table=tail_table,
        deep_tail_prime_table=None,
        deep_tail_min_bits=None,
        mr_bases=[2, 3, 5, 7],
        truth_check=True,
    )

    assert result["candidate_count"] == 4
    assert result["rejected_by_proxy"] == 2
    assert result["survivors_to_miller_rabin"] == 2
    assert result["classification"]["false_positives"] == 0
    assert result["classification"]["false_negatives"] == 0
