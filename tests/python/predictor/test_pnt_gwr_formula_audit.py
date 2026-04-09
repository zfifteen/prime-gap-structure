"""Tests for the PNT/GWR placed-formula audit script."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "benchmarks" / "python" / "predictor" / "pnt_gwr_formula_audit.py"


def load_module():
    """Load the audit module directly from its file path."""
    spec = importlib.util.spec_from_file_location("pnt_gwr_formula_audit", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load pnt_gwr_formula_audit module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_direct_placed_nextprime_identity_holds_for_interior_seeds():
    """Any interior composite seed should recover the right endpoint by nextprime alone."""
    module = load_module()

    assert module.placed_prime_from_seed(4) == 5
    assert module.placed_prime_from_seed(10) == 11
    assert module.placed_prime_from_seed(16) == 17


def test_witness_search_counterexamples_appear_on_small_exact_surface():
    """The witness map is not exact for arbitrary in-gap seeds."""
    module = load_module()
    summary = module.analyze_exact_limit(100)

    assert summary["direct_nextprime_match_rate"] == 1.0
    assert summary["w_dmin_match_rate"] < 1.0
    assert summary["w_d4_match_rate"] < 1.0

    dmin_counterexample = summary["first_w_dmin_counterexample"]
    assert dmin_counterexample["left_prime"] == 7
    assert dmin_counterexample["right_prime"] == 11
    assert dmin_counterexample["seed"] == 10
    assert dmin_counterexample["divisor_target"] == 3
    assert dmin_counterexample["witness"] == 25
    assert dmin_counterexample["found_prime"] == 29

    d4_counterexample = summary["first_w_d4_counterexample"]
    assert d4_counterexample["left_prime"] == 3
    assert d4_counterexample["right_prime"] == 5
    assert d4_counterexample["seed"] == 4
    assert d4_counterexample["divisor_target"] == 4
    assert d4_counterexample["witness"] == 6
    assert d4_counterexample["found_prime"] == 7


def test_witness_search_is_exact_when_the_target_carrier_stays_ahead_of_seed():
    """The witness path works on seeds that still have an in-gap carrier ahead."""
    module = load_module()

    assert module.witness_prime_from_seed(8, 3) == 11
    assert module.witness_prime_from_seed(14, 4) == 17


def test_audit_entry_point_writes_json_summary(tmp_path):
    """The CLI entry point should emit the audit summary artifact."""
    module = load_module()

    assert module.main(["--output-dir", str(tmp_path), "--exact-limit", "1000"]) == 0

    summary_path = tmp_path / "pnt_gwr_formula_audit_summary.json"
    assert summary_path.exists()

    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["exact_limit"] == 1000
    assert payload["direct_nextprime_match_rate"] == 1.0
    assert payload["w_dmin_match_rate"] < 1.0
    assert payload["w_d4_match_rate"] < 1.0
