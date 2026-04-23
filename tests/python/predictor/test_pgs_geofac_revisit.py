"""Tests for the research-only PGS-assisted geofac revisit harness."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "benchmarks" / "python" / "predictor" / "pgs_geofac_revisit.py"


def load_module():
    """Load the benchmark runner as a module."""
    spec = importlib.util.spec_from_file_location("pgs_geofac_revisit", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load pgs_geofac_revisit module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _strip_timing(summary: dict[str, object]) -> dict[str, object]:
    """Return one summary copy without wall-clock fields."""
    result = dict(summary)
    result.pop("total_wall_time_ms", None)
    return result


def _strip_row_timing(rows) -> list[dict[str, object]]:
    """Return one row list copy without wall-clock fields."""
    comparable_rows: list[dict[str, object]] = []
    for metric in rows:
        row = dict(metric.row)
        row.pop("wall_time_ms", None)
        comparable_rows.append(row)
    return comparable_rows


def test_midscale_corpus_is_committed_and_canonical_case_is_first():
    """The expanded midscale corpus should be fixed and start with the canonical wall case."""
    module = load_module()

    assert len(module.MIDSCALE_BALANCED_CASES) == 24
    canonical = module.MIDSCALE_BALANCED_CASES[0]
    assert canonical.case_id == "mid_47_wall"
    assert canonical.n == canonical.p * canonical.q
    assert canonical.n.bit_length() == 47


def test_official_midscale_audit_is_deterministic():
    """The fixed wall-break audit should reproduce identical rows except timing."""
    module = load_module()
    rows_a, summary_a = module.run_revisit(
        method="pgs_controller",
        regime="midscale_balanced",
        case_count=None,
        seed=0,
        budget_primes=module.OFFICIAL_MIDSCALE_BUDGET_PRIMES,
        budget_shells=module.OFFICIAL_MIDSCALE_BUDGET_SHELLS,
        max_half_width=module.OFFICIAL_MIDSCALE_MAX_HALF_WIDTH,
    )
    rows_b, summary_b = module.run_revisit(
        method="pgs_controller",
        regime="midscale_balanced",
        case_count=None,
        seed=0,
        budget_primes=module.OFFICIAL_MIDSCALE_BUDGET_PRIMES,
        budget_shells=module.OFFICIAL_MIDSCALE_BUDGET_SHELLS,
        max_half_width=module.OFFICIAL_MIDSCALE_MAX_HALF_WIDTH,
    )

    assert _strip_row_timing(rows_a) == _strip_row_timing(rows_b)
    assert _strip_timing(summary_a) == _strip_timing(summary_b)


def test_archive_baselines_still_fail_the_canonical_47bit_wall_case():
    """The old archive baselines should still miss the canonical 47-bit case."""
    module = load_module()
    audit = module.run_midscale_wall_break_audit(seed=0)

    geofac_rows = audit["methods"]["geofac_baseline"]["rows"]
    wheel_rows = audit["methods"]["wheel_baseline"]["rows"]
    geofac_summary = audit["methods"]["geofac_baseline"]["summary"]
    wheel_summary = audit["methods"]["wheel_baseline"]["summary"]

    assert geofac_rows[0].row["factor_in_budget"] is False
    assert wheel_rows[0].row["factor_in_budget"] is False
    assert geofac_summary["acceptance"]["wall_break_passed"] is False
    assert wheel_summary["acceptance"]["wall_break_passed"] is False


def test_pgs_controller_breaks_the_official_midscale_wall():
    """The pure PGS controller should clear the fixed wall-break acceptance gate."""
    module = load_module()
    audit = module.run_midscale_wall_break_audit(seed=0)
    summary = audit["methods"]["pgs_controller"]["summary"]
    acceptance = summary["acceptance"]

    assert acceptance["canonical_47bit_recovered"] is True
    assert acceptance["expanded_midscale_recall"] >= module.OFFICIAL_MIDSCALE_MIN_RECALL
    assert acceptance["beats_geofac_baseline"] is True
    assert acceptance["beats_wheel_baseline"] is True
    assert acceptance["survives_false_signal_control"] is True
    assert acceptance["wall_break_passed"] is True


def test_hybrid_does_not_get_credit_when_random_rerank_also_clears_the_gate():
    """Hybrid should fail the official acceptance gate when the pseudo-random rerank also passes."""
    module = load_module()
    audit = module.run_midscale_wall_break_audit(seed=0)
    hybrid_summary = audit["methods"]["hybrid"]["summary"]
    hybrid_acceptance = hybrid_summary["acceptance"]

    assert hybrid_summary["false_signal_control"]["factor_in_budget_recall"] >= module.OFFICIAL_MIDSCALE_MIN_RECALL
    assert hybrid_acceptance["canonical_47bit_recovered"] is True
    assert hybrid_acceptance["survives_false_signal_control"] is False
    assert hybrid_acceptance["wall_break_passed"] is False


def test_challenge_like_pgs_paths_run_without_overflow():
    """The challenge-like PGS paths should complete without the old int64 overflow."""
    module = load_module()
    for method in ("pgs_controller", "hybrid"):
        rows, summary = module.run_revisit(
            method=method,
            regime="challenge_like_unbalanced",
            case_count=3,
            seed=5,
            budget_primes=64,
            budget_shells=12,
            max_half_width=1 << 26,
        )
        assert len(rows) == 3
        assert summary["case_count"] == 3
        assert summary["acceptance"] is None


def test_cli_writes_official_midscale_acceptance_summary(tmp_path: Path):
    """The CLI should emit the acceptance object on the official midscale audit."""
    module = load_module()
    exit_code = module.main(
        [
            "--method",
            "pgs_controller",
            "--regime",
            "midscale_balanced",
            "--seed",
            "0",
            "--budget-primes",
            str(module.OFFICIAL_MIDSCALE_BUDGET_PRIMES),
            "--budget-shells",
            str(module.OFFICIAL_MIDSCALE_BUDGET_SHELLS),
            "--max-half-width",
            str(module.OFFICIAL_MIDSCALE_MAX_HALF_WIDTH),
            "--output-dir",
            str(tmp_path),
        ]
    )

    assert exit_code == 0
    summary_json = tmp_path / "pgs_controller_midscale_balanced_summary.json"
    assert summary_json.exists()

    summary = json.loads(summary_json.read_text(encoding="utf-8"))
    assert summary["method"] == "pgs_controller"
    assert summary["regime"] == "midscale_balanced"
    assert summary["case_count"] == 24
    assert summary["acceptance"]["wall_break_passed"] is True
