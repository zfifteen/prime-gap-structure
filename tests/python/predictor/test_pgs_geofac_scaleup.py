"""Tests for the research-only PGS-first scale-up harness."""

from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path

from sympy import isprime


ROOT = Path(__file__).resolve().parents[3]
SCALEUP_MODULE_PATH = ROOT / "benchmarks" / "python" / "predictor" / "pgs_geofac_scaleup.py"
BUILDER_MODULE_PATH = ROOT / "benchmarks" / "python" / "predictor" / "build_scaleup_corpus.py"
CORPUS_PATH = ROOT / "benchmarks" / "python" / "predictor" / "scaleup_corpus.json"


def _load_module(name: str, path: Path):
    """Load one benchmark script as an importable module."""
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module {name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_scaleup():
    """Load the scale-up harness module."""
    return _load_module("pgs_geofac_scaleup", SCALEUP_MODULE_PATH)


def load_builder():
    """Load the committed corpus builder module."""
    return _load_module("build_scaleup_corpus", BUILDER_MODULE_PATH)


def _strip_summary_timing(summary: dict[str, object]) -> dict[str, object]:
    """Return one summary copy without timing fields."""
    comparable = dict(summary)
    comparable.pop("total_wall_time_ms", None)
    return comparable


def _strip_row_timing(rows) -> list[dict[str, object]]:
    """Return one comparable row list without timing fields."""
    comparable_rows: list[dict[str, object]] = []
    for metric in rows:
        row = dict(metric.row)
        row.pop("wall_time_ms", None)
        comparable_rows.append(row)
    return comparable_rows


def test_committed_scaleup_corpus_matches_deterministic_builder_and_127_contracts():
    """The committed corpus should match the builder sentinels and the rebuilt 127 families."""
    builder = load_builder()
    committed = json.loads(CORPUS_PATH.read_text(encoding="utf-8"))

    assert sorted(committed.keys(), key=int) == [str(bits) for bits in builder.STAGE_BITS]
    assert len(committed["127"]) == 12
    assert len(committed["160"]) == 8
    assert len(committed["4096"]) == 4

    family_counts: dict[str, int] = {}
    for row in committed["127"]:
        family_counts[row["family"]] = family_counts.get(row["family"], 0) + 1
    assert family_counts == {
        "balanced": 4,
        "moderate_unbalanced": 4,
        "archived_shape": 4,
    }

    balanced_80 = next(row for row in committed["127"] if row["case_id"] == "s127_balanced_80")
    assert (balanced_80["p"], balanced_80["q"]) == builder._balanced_pair(80, 0)

    moderate_127 = next(row for row in committed["127"] if row["case_id"] == "s127_moderate_127")
    assert (moderate_127["p"], moderate_127["q"]) == builder._moderate_pair(127, 0)

    archived_shape_80 = next(row for row in committed["127"] if row["case_id"] == "s127_archived_shape_80")
    assert (archived_shape_80["p"], archived_shape_80["q"]) == builder._archived_shape_pair(80, 0)

    archived = next(row for row in committed["127"] if row["case_id"] == "s127_archived_shape_archived")
    assert archived["family"] == "archived_shape"
    assert archived["p"] == builder.ARCHIVED_127_P
    assert archived["q"] == builder.ARCHIVED_127_Q
    assert archived["n"] == builder.ARCHIVED_127_N

    challenge_4096 = next(row for row in committed["4096"] if row["case_id"] == "s4096_challenge_1")
    assert (challenge_4096["p"], challenge_4096["q"]) == builder._challenge_pair(4096, 0)

    for row in committed["127"]:
        p = int(row["p"])
        q = int(row["q"])
        imbalance = abs(math.log(max(p, q) / min(p, q)))
        if row["family"] == "balanced":
            assert imbalance <= 1e-4
        elif row["family"] == "moderate_unbalanced":
            assert 0.5 <= imbalance <= 0.9
        else:
            assert abs(imbalance - builder.ARCHIVED_127_LOG) <= builder.ARCHIVED_SHAPE_TOLERANCE


def test_pgs_router_places_balanced_80_factor_side_in_top4_at_rung1():
    """The balanced 80-bit case should be centered at rank 1 and recover at rung 1."""
    module = load_scaleup()
    case = next(candidate for candidate in module.CORPUS[127] if candidate.case_id == "s127_balanced_80")

    windows, probe_count = module._route_case(case, 1, 0)
    metric = module._evaluate_case(case, 127, 1, 0)

    assert probe_count > 0
    assert len(windows) == module.RUNG_CONFIGS[1].top_windows
    assert module._window_contains_factor(windows[0], case.small_factor_log2) is True
    assert metric.row["best_window_rank"] == 1
    assert metric.row["factor_recovered"] is True


def test_pgs_router_places_archived_case_in_top4_by_rung2():
    """The archived 127-bit case should stay in top-4 and recover by rung 2."""
    module = load_scaleup()
    case = next(
        candidate for candidate in module.CORPUS[127] if candidate.case_id == module.ARCHIVED_CASE_ID
    )

    windows, probe_count = module._route_case(case, 2, 0)
    metric = module._evaluate_case(case, 127, 2, 0)
    ranks = [
        index
        for index, window in enumerate(windows, start=1)
        if module._window_contains_factor(window, case.small_factor_log2)
    ]

    assert probe_count > 0
    assert len(windows) == module.RUNG_CONFIGS[2].top_windows
    assert ranks
    assert min(ranks) <= 4
    assert metric.row["factor_recovered"] is True


def test_scaleup_subset_run_is_deterministic_except_timing():
    """A fixed subset run should reproduce identical rows and summary fields except timing."""
    module = load_scaleup()
    rows_a, summary_a = module.run_scaleup(127, 1, 1, 0)
    rows_b, summary_b = module.run_scaleup(127, 1, 1, 0)

    assert _strip_row_timing(rows_a) == _strip_row_timing(rows_b)
    assert _strip_summary_timing(summary_a) == _strip_summary_timing(summary_b)


def test_pgs_subset_does_not_claim_stage_acceptance():
    """A subset PGS run should never claim that the full stage passed."""
    module = load_scaleup()
    rows, summary = module.run_scaleup(127, 1, 1, 0)

    assert len(rows) == 1
    assert summary["case_count"] == 1
    assert summary["router"] == "pgs"
    assert summary["acceptance"]["full_stage_evaluated"] is False
    assert summary["acceptance"]["stage_passed"] is False
    assert "winner_router" not in summary


def test_big_int_prime_traversal_emits_unique_primes_at_4096_scale():
    """The big-int center-out walker should emit unique prime candidates at 4096 bits."""
    module = load_scaleup()
    case = module.CORPUS[4096][0]
    low = case.small_factor - 10_000
    high = case.small_factor + 10_000

    primes = module._center_out_primes_in_interval(case.small_factor, low, high, 4)

    assert len(primes) == 4
    assert len(set(primes)) == 4
    assert all(low <= prime <= high for prime in primes)
    assert all(isprime(prime) for prime in primes)


def test_local_pgs_seed_recovery_hits_factor_and_is_deterministic_on_narrow_interval():
    """A narrow known factor interval should recover deterministically by ranked PGS primes."""
    module = load_scaleup()
    case = next(candidate for candidate in module.CORPUS[127] if candidate.case_id == "s127_balanced_80")
    low = case.small_factor - 32
    high = case.small_factor + 32

    found, prime_tests = module._pgs_seed_recovery_in_interval(case, low, high, 64)
    ranked_a = module._ranked_recovered_primes_in_interval(case, low, high, 64)
    ranked_b = module._ranked_recovered_primes_in_interval(case, low, high, 64)

    assert found is True
    assert prime_tests >= 1
    assert ranked_a == ranked_b
    assert ranked_a
    assert case.small_factor in ranked_a


def test_official_127_audit_passes_on_first_passing_rung():
    """The official 127 audit should stop at and report the first passing rung."""
    module = load_scaleup()
    rows, summary = module.run_127_official_audit(0)

    assert len(rows) == 12
    assert summary["case_count"] == 12
    assert summary["acceptance"]["full_stage_evaluated"] is True
    assert summary["exact_recovery_recall"] >= 0.75
    assert summary["router_top4_recall"] >= 0.83
    assert summary["acceptance"]["archived_case_recovered"] is True
    assert summary["stage_passed"] is True
    assert summary["official_rung"] in (1, 2, 3)
    first_passing_rung = next(
        int(rung_text)
        for rung_text, rung_summary in summary["rung_summaries"].items()
        if rung_summary["acceptance"]["stage_passed"] is True
    )
    assert summary["official_rung"] == first_passing_rung


def test_cli_writes_scaleup_rows_and_summary(tmp_path: Path):
    """The CLI should write the expected row and summary artifacts for a subset run."""
    module = load_scaleup()
    exit_code = module.main(
        [
            "--scale-bits",
            "127",
            "--rung",
            "1",
            "--cases",
            "1",
            "--seed",
            "0",
            "--output-dir",
            str(tmp_path),
        ]
    )

    assert exit_code == 0

    rows_path = tmp_path / "pgs_scale127_r1_rows.jsonl"
    summary_path = tmp_path / "pgs_scale127_r1_summary.json"
    assert rows_path.exists()
    assert summary_path.exists()

    row_lines = rows_path.read_text(encoding="utf-8").splitlines()
    assert len(row_lines) == 1
    row = json.loads(row_lines[0])
    assert row["router"] == "pgs"
    assert row["scale_bits"] == 127
    assert row["rung"] == 1

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["router"] == "pgs"
    assert summary["scale_bits"] == 127
    assert summary["case_count"] == 1
    assert "winner_router" not in summary
    assert summary["acceptance"]["stage_passed"] is False
