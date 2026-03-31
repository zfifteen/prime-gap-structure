"""Tests for the exact raw composite Z gap-edge run suite."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
BENCHMARKS_DIR = ROOT.parent / "benchmarks" / "python"


def load_module(name: str):
    """Load a benchmark helper or script module from its file path."""
    path = BENCHMARKS_DIR / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module {name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_helper_defaults_match_requested_run_surface():
    """The helper should expose the exact run families we want to reproduce."""
    module = load_module("raw_z_gap_edge_runs")

    assert module.DEFAULT_FULL_LIMITS == (1_000_000, 10_000_000)
    assert module.DEFAULT_WINDOW_SCALES == (
        100_000_000,
        1_000_000_000,
        10_000_000_000,
    )
    assert module.DEFAULT_WINDOW_SIZE == 10_000_000
    assert module.DEFAULT_WINDOW_COUNT == 10
    assert module.DEFAULT_RANDOM_SEED == 20260331


def test_gap_edge_summary_to_dict_keeps_fields_visible():
    """As a researcher, I want one plain mapping per run for JSON output."""
    module = load_module("raw_z_gap_edge_runs")
    row = module.GapEdgeRunSummary(
        scale=10,
        gap_count=3,
        observed_edge2_share=0.5,
        baseline_edge2_share=0.25,
        edge2_enrichment=2.0,
        observed_d4_share=0.75,
        baseline_d4_share=0.25,
        d4_enrichment=3.0,
        left_share=0.6,
        right_share=0.3,
        center_share=0.1,
        window_mode="exact",
    )

    assert row.to_dict()["scale"] == 10
    assert row.to_dict()["window_mode"] == "exact"


def test_placeholder_helper_sections_raise_not_implemented():
    """The seeded helper should now be wired and deterministic."""
    module = load_module("raw_z_gap_edge_runs")

    starts = module.build_seeded_window_starts(100, 10, 2, 7)
    assert starts == sorted(starts)


def test_even_window_starts_are_deterministic_and_evenly_spaced():
    """The even-window helper should expose the fixed deterministic segment starts."""
    module = load_module("raw_z_gap_edge_runs")

    assert module.build_even_window_starts(100, 10, 3) == [2, 47, 92]
    assert module.build_even_window_starts(100, 10, 1) == [2]


def test_seeded_window_starts_are_reproducible_and_sorted():
    """The fixed-seed helper should pick the same sorted windows every time."""
    module = load_module("raw_z_gap_edge_runs")

    first = module.build_seeded_window_starts(100, 10, 4, 20260331)
    second = module.build_seeded_window_starts(100, 10, 4, 20260331)

    assert first == second
    assert first == sorted(first)
    assert all(2 <= start < 92 for start in first)


def test_script_parsers_expose_expected_defaults():
    """Every thin CLI should surface the intended reproduction defaults."""
    exact = load_module("raw_z_gap_edge_run_exact")
    even = load_module("raw_z_gap_edge_run_even_windows")
    seeded = load_module("raw_z_gap_edge_run_seeded_windows")
    all_runs = load_module("raw_z_gap_edge_run_all")

    assert exact.build_parser().parse_args([]).limits == [1_000_000, 10_000_000]
    assert even.build_parser().parse_args([]).window_count == 10
    assert seeded.build_parser().parse_args([]).seed == 20260331
    assert all_runs.build_parser().parse_args([]).window_scales == [
        100_000_000,
        1_000_000_000,
        10_000_000_000,
    ]


def test_script_scaffold_propagates_placeholder_state_cleanly():
    """The seeded window CLI should now load without placeholder wiring."""
    load_module("raw_z_gap_edge_run_seeded_windows")


def test_exact_full_run_reproduces_known_million_scale_row():
    """The exact full-run helper should reproduce the established 10^6 result."""
    module = load_module("raw_z_gap_edge_runs")
    row = module.run_exact_limit(1_000_000)

    assert row.gap_count == 70327
    assert row.window_mode == "exact"
    assert row.observed_edge2_share == pytest.approx(0.43600608585607237)
    assert row.baseline_edge2_share == pytest.approx(0.22185858570959013)
    assert row.observed_d4_share == pytest.approx(0.8290272583787166)
    assert row.baseline_d4_share == pytest.approx(0.20140064321856735)


def test_exact_script_emits_json_for_requested_limits(capsys):
    """The exact CLI should emit one JSON row per requested full limit."""
    exact = load_module("raw_z_gap_edge_run_exact")

    assert exact.main(["--limits", "10000"]) == 0
    payload = capsys.readouterr().out

    assert "\"scale\": 10000" in payload
    assert "\"window_mode\": \"exact\"" in payload


def test_even_window_sweep_aggregates_interval_rows():
    """The even-window sweep should aggregate weighted interval summaries by scale."""
    module = load_module("raw_z_gap_edge_runs")
    rows = module.run_window_sweep(
        scales=[100_000],
        window_size=10_000,
        starts_by_scale={100_000: [2, 45_002]},
        window_mode="even",
    )

    assert len(rows) == 1
    row = rows[0]
    assert row.scale == 100_000
    assert row.window_mode == "even"
    assert row.window_size == 10_000
    assert row.sampled_gap_count == row.gap_count
    assert row.approximate_gap_count == row.sampled_gap_count * 5
    assert 0.0 < row.observed_edge2_share < 1.0
    assert 0.0 < row.observed_d4_share < 1.0


def test_even_window_script_emits_json_for_requested_scale(capsys):
    """The even-window CLI should emit one JSON row per requested sampled scale."""
    even = load_module("raw_z_gap_edge_run_even_windows")

    assert even.main(["--scales", "100000", "--window-size", "10000", "--window-count", "2"]) == 0
    payload = capsys.readouterr().out

    assert "\"scale\": 100000" in payload
    assert "\"window_mode\": \"even\"" in payload


def test_seeded_window_script_emits_json_for_requested_scale(capsys):
    """The seeded-window CLI should emit one JSON row per requested sampled scale."""
    seeded = load_module("raw_z_gap_edge_run_seeded_windows")

    assert (
        seeded.main(
            [
                "--scales",
                "100000",
                "--window-size",
                "10000",
                "--window-count",
                "2",
                "--seed",
                "7",
            ]
        )
        == 0
    )
    payload = capsys.readouterr().out

    assert "\"scale\": 100000" in payload
    assert "\"window_mode\": \"seeded-random\"" in payload
    assert "\"seed\": 7" in payload


def test_all_runs_entry_point_coordinates_sections_without_own_analysis(capsys):
    """As a user, I want one coordinator that just wires the exact run sections together."""
    all_runs = load_module("raw_z_gap_edge_run_all")
    helper = load_module("raw_z_gap_edge_runs")

    def fake_exact(limit: int):
        return helper.GapEdgeRunSummary(
            scale=limit,
            gap_count=1,
            observed_edge2_share=0.4,
            baseline_edge2_share=0.2,
            edge2_enrichment=2.0,
            observed_d4_share=0.8,
            baseline_d4_share=0.2,
            d4_enrichment=4.0,
            left_share=0.7,
            right_share=0.2,
            center_share=0.1,
            window_mode="exact",
        )

    def fake_even(scale: int, window_size: int, window_count: int):
        return [2 + scale + window_size + window_count]

    def fake_seeded(scale: int, window_size: int, window_count: int, seed: int):
        return [seed + scale + window_size + window_count]

    def fake_sweep(scales, window_size, starts_by_scale, window_mode, seed=None):
        return [
            helper.GapEdgeRunSummary(
                scale=scale,
                gap_count=len(starts_by_scale[scale]),
                observed_edge2_share=0.3,
                baseline_edge2_share=0.15,
                edge2_enrichment=2.0,
                observed_d4_share=0.75,
                baseline_d4_share=0.15,
                d4_enrichment=5.0,
                left_share=0.72,
                right_share=0.18,
                center_share=0.10,
                window_mode=window_mode,
                window_size=window_size,
                sampled_gap_count=10,
                approximate_gap_count=20,
                seed=seed,
            )
            for scale in scales
        ]

    all_runs.run_exact_limit = fake_exact
    all_runs.build_even_window_starts = fake_even
    all_runs.build_seeded_window_starts = fake_seeded
    all_runs.run_window_sweep = fake_sweep

    assert all_runs.main([]) == 0
    payload = capsys.readouterr().out

    assert "\"exact_full_runs\"" in payload
    assert "\"even_window_runs\"" in payload
    assert "\"seeded_window_runs\"" in payload
    assert "\"window_mode\": \"seeded-random\"" in payload
