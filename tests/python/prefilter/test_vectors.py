"""Golden-vector parity tests for the standalone geodesic prefilter repo."""

from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = ROOT / "src" / "python"
BENCHMARK_PATH = ROOT / "benchmarks" / "python" / "prefilter" / "candidate_benchmark.py"
VECTORS_DIR = ROOT / "spec" / "vectors"

if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

import geodesic_prime_prefilter.prefilter as prefilter


def load_candidate_benchmark():
    """Load the candidate benchmark module from its file path."""
    spec = importlib.util.spec_from_file_location("candidate_benchmark", BENCHMARK_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load candidate benchmark module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_json(filename: str) -> dict:
    """Load one vector file from the shared spec directory."""
    return json.loads((VECTORS_DIR / filename).read_text(encoding="utf-8"))


def test_candidate_stream_vectors_match_python_generator():
    """The deterministic candidate stream must match the committed vector corpus."""
    payload = load_json("candidate_stream_32.json")

    for entry in payload["candidates"]:
        actual = prefilter.deterministic_odd_candidate(
            payload["bit_length"],
            entry["index"],
            namespace=payload["namespace"],
        )
        assert hex(actual) == entry["candidate_hex"]


def test_prefilter_decision_vectors_match_proxy_behavior():
    """The benchmark proxy behavior must match the committed decision vectors."""
    module = load_candidate_benchmark()
    payload = load_json("prefilter_decisions_32.json")
    primary = module.WheelPrimeTable(
        payload["primary_prime_limit"],
        payload["primary_chunk_size"],
    )
    tail = module.WheelPrimeTable(
        payload["tail_prime_limit"],
        payload["tail_chunk_size"],
        start_exclusive=payload["primary_prime_limit"],
    )
    deep_tail = module.WheelPrimeTable(
        payload["deep_tail_prime_limit"],
        payload["deep_tail_chunk_size"],
        start_exclusive=payload["tail_prime_limit"],
    )

    for entry in payload["decisions"]:
        candidate = int(entry["candidate_hex"], 16)
        proxy = module.cheap_cdl_proxy(
            candidate,
            primary,
            tail_prime_table=tail,
            deep_tail_prime_table=deep_tail,
            deep_tail_min_bits=payload["deep_tail_min_bits"],
        )
        actual_factor = None
        if proxy["smallest_factor"] is not None:
            actual_factor = hex(int(proxy["smallest_factor"]))

        assert bool(proxy["rejected"]) is entry["rejected"]
        assert proxy["factor_source"] == entry["factor_source"]
        assert actual_factor == entry["smallest_factor_hex"]
        assert math.isclose(proxy["z_hat"], entry["proxy_z"], rel_tol=1e-15, abs_tol=1e-15)
        assert math.isclose(proxy["d_est"], entry["d_est"], rel_tol=1e-15, abs_tol=1e-15)
        assert (math.gcd(candidate - 1, payload["public_exponent"]) == 1) is entry["public_exponent_ok"]


def test_fixed_point_vectors_match_exact_small_n_contract():
    """The small-n fixed-point vectors must match the exact DCI closed form."""
    module = load_candidate_benchmark()
    payload = load_json("fixed_points_small_n.json")

    assert math.isclose(payload["fixed_point_v"], prefilter.FIXED_POINT_V, rel_tol=0.0, abs_tol=0.0)
    for entry in payload["values"]:
        n = int(entry["n_hex"], 16)
        divisor_count = module.exact_divisor_count(n)
        z_value = module.exact_z_normalize(n)
        assert divisor_count == entry["divisor_count"]
        assert (divisor_count == 2) is entry["is_prime"]
        assert math.isclose(z_value, entry["z_at_fixed_point"], rel_tol=1e-15, abs_tol=1e-15)


def test_generate_prime_vectors_match_public_api():
    """The public generator must reproduce the committed deterministic prime outputs."""
    payload = load_json("generate_prime_cases.json")

    for case in payload["cases"]:
        generator = prefilter.CDLPrimeGeodesicPrefilter(
            bit_length=case["bit_length"],
            namespace=case["namespace"],
        )
        excluded = {int(value, 16) for value in case["excluded_values_hex"]}
        actual = generator.generate_prime(
            public_exponent=case["public_exponent"],
            excluded_values=excluded or None,
        )
        assert hex(actual) == case["expected_prime_hex"]
