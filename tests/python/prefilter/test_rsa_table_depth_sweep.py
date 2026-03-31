"""Tests for the RSA table-depth sweep benchmark."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "benchmarks" / "python" / "prefilter" / "rsa_table_depth_sweep.py"


def load_module():
    """Load the RSA table-depth sweep module from its file path."""
    spec = importlib.util.spec_from_file_location("rsa_table_depth_sweep", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load RSA table-depth sweep module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_run_sweep_is_deterministic_on_small_panel(tmp_path):
    """A small deterministic sweep should write the expected artifact set."""
    module = load_module()
    results = module.run_sweep(
        output_dir=tmp_path,
        rsa_bits=64,
        keypair_count=2,
        table_limits=[19, 97],
        chunk_size=4,
        primary_limit=19,
        tail_limit=29,
        public_exponent=65537,
        namespace="unit-rsa-depth",
    )

    assert results["baseline"]["keypair_count"] == 2
    assert results["prime_fixed_points"]["fixed_point_count"] == 4
    assert [row["covered_prime_limit"] for row in results["rows"]] == [19, 97]
    assert all(
        row["saved_miller_rabin_call_rate"] == row["proxy_rejection_rate"]
        for row in results["rows"]
    )
    assert all(
        row["accelerated"]["total_candidates_tested"] == results["baseline"]["total_candidates_tested"]
        for row in results["rows"]
    )
    assert results["rows"][1]["accelerated"]["total_miller_rabin_calls"] <= results["rows"][0]["accelerated"]["total_miller_rabin_calls"]
    assert (tmp_path / "rsa_table_depth_sweep_results.json").exists()
    assert (tmp_path / "rsa_table_depth_sweep_results.csv").exists()
    assert (tmp_path / "RSA_TABLE_DEPTH_SWEEP_REPORT.md").exists()
    assert (tmp_path / "rsa_depth_speedup.svg").exists()
    assert (tmp_path / "rsa_depth_rejection.svg").exists()
    assert (tmp_path / "rsa_depth_timing_breakdown.svg").exists()
