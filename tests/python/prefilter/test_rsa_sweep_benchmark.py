"""Tests for the deterministic RSA benchmark sweep."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "benchmarks" / "python" / "prefilter" / "rsa_sweep_benchmark.py"


def load_module():
    """Load the RSA sweep benchmark module from its file path."""
    spec = importlib.util.spec_from_file_location("rsa_sweep_benchmark", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load RSA sweep benchmark module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_build_rsa_sweep_schedule_filters_to_requested_max_bits():
    """The sweep schedule should include only the deterministic cells up to the ceiling."""
    module = load_module()

    assert module.build_rsa_sweep_schedule(1024) == [(512, 100), (1024, 100)]


def test_run_rsa_sweep_executes_custom_small_schedule():
    """A custom small sweep should return one benchmark result per requested cell."""
    module = load_module()
    schedule = [(64, 2), (128, 1)]

    results = module.run_rsa_sweep(
        schedule=schedule,
        public_exponent=65537,
        namespace="unit:sweep",
    )

    assert [result["rsa_bits"] for result in results] == [64, 128]
    assert [result["keypair_count"] for result in results] == [2, 1]
    for result in results:
        assert result["matching_keypairs"] == result["keypair_count"]
        assert result["saved_miller_rabin_calls"] >= 0


def test_build_markdown_report_includes_all_cells():
    """The markdown report should summarize every sweep cell."""
    module = load_module()
    schedule = [(64, 2)]
    results = module.run_rsa_sweep(
        schedule=schedule,
        public_exponent=65537,
        namespace="unit:report",
    )

    report = module.build_markdown_report(schedule, results, public_exponent=65537)

    assert "# RSA Sweep Benchmark Report" in report
    assert "## RSA 64" in report
    assert "| RSA bits | Keypairs |" in report
