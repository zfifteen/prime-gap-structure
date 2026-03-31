"""Tests for the end-to-end RSA key generation benchmark."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "benchmarks" / "python" / "prefilter" / "rsa_keygen_benchmark.py"


def load_module():
    """Load the RSA benchmark module from its file path."""
    spec = importlib.util.spec_from_file_location("rsa_keygen_benchmark", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load RSA key generation benchmark module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_deterministic_candidate_stream_is_reproducible():
    """The streaming candidate generator should stay deterministic."""
    module = load_module()
    first = []
    second = []
    first_stream = module.deterministic_candidate_stream(32, "unit")
    second_stream = module.deterministic_candidate_stream(32, "unit")

    for _ in range(5):
        first.append(next(first_stream))
        second.append(next(second_stream))

    assert first == second
    assert len(set(first)) == 5


def test_generate_rsa_keypair_proxy_matches_baseline_on_small_panel():
    """The accelerated path should land on the same deterministic keypair as baseline."""
    module = load_module()
    primary = module.benchmark.WheelPrimeTable(limit=19, chunk_size=4)
    tail = module.benchmark.WheelPrimeTable(limit=97, chunk_size=4, start_exclusive=19)
    deep_tail = module.benchmark.WheelPrimeTable(limit=127, chunk_size=4, start_exclusive=97)

    baseline = module.generate_rsa_keypair(
        rsa_bits=64,
        keypair_index=0,
        public_exponent=65537,
        mr_bases=[2, 3, 5, 7],
        namespace="unit",
        use_proxy=False,
    )
    accelerated = module.generate_rsa_keypair(
        rsa_bits=64,
        keypair_index=0,
        public_exponent=65537,
        mr_bases=[2, 3, 5, 7],
        namespace="unit",
        use_proxy=True,
        prime_table=primary,
        tail_prime_table=tail,
        deep_tail_prime_table=deep_tail,
        deep_tail_min_bits=128,
    )

    assert baseline["p"] == accelerated["p"]
    assert baseline["q"] == accelerated["q"]
    assert baseline["n"] == accelerated["n"]
    assert baseline["d"] == accelerated["d"]
    assert accelerated["proxy_rejections"] >= 0
    assert baseline["assembly_time_ns"] >= 0
    assert accelerated["proxy_time_ns"] >= 0
    assert accelerated["miller_rabin_time_ns"] >= 0
    assert accelerated["total_time_ns"] >= accelerated["assembly_time_ns"]


def test_build_proxy_tables_skips_deep_tail_below_gate():
    """The RSA benchmark should not build the deep tail when the gate is inactive."""
    module = load_module()
    primary, tail, deep_tail = module.build_proxy_tables(prime_bits=2048)

    assert primary is not None
    assert tail is not None
    assert deep_tail is None


def test_generate_rsa_keypair_validates_inputs():
    """Invalid RSA sizes and exponents should fail fast with clear errors."""
    module = load_module()

    with pytest.raises(ValueError, match="rsa_bits"):
        module.generate_rsa_keypair(
            rsa_bits=63,
            keypair_index=0,
            public_exponent=65537,
            mr_bases=[2, 3, 5, 7],
            namespace="unit",
            use_proxy=False,
        )

    with pytest.raises(ValueError, match="public_exponent"):
        module.generate_rsa_keypair(
            rsa_bits=64,
            keypair_index=0,
            public_exponent=2,
            mr_bases=[2, 3, 5, 7],
            namespace="unit",
            use_proxy=False,
        )


def test_run_rsa_keygen_benchmark_reports_matching_keypairs_and_fixed_points():
    """A small deterministic run should produce matching keypairs and confirmed fixed points."""
    module = load_module()
    result = module.run_rsa_keygen_benchmark(
        rsa_bits=64,
        keypair_count=2,
        public_exponent=65537,
        mr_bases=[2, 3, 5, 7],
        namespace="unit",
    )

    assert result["matching_keypairs"] == 2
    assert result["baseline"]["keypair_count"] == 2
    assert result["accelerated"]["keypair_count"] == 2
    assert result["prime_fixed_points"]["fixed_point_count"] == 4
    assert result["saved_miller_rabin_calls"] >= 0
    for path_name in ("baseline", "accelerated"):
        path = result[path_name]
        assert path["total_proxy_time_ms"] >= 0.0
        assert path["total_miller_rabin_time_ms"] >= 0.0
        assert path["total_assembly_time_ms"] >= 0.0
        assert path["total_residual_time_ms"] >= 0.0
        share_sum = (
            path["proxy_time_share"]
            + path["miller_rabin_time_share"]
            + path["assembly_time_share"]
            + path["residual_time_share"]
        )
        assert abs(share_sum - 1.0) < 1e-9
