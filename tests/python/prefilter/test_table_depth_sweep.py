"""Tests for the deterministic table-depth sweep."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "benchmarks" / "python" / "prefilter" / "table_depth_sweep.py"


def load_module():
    """Load the sweep module from its file path."""
    spec = importlib.util.spec_from_file_location("table_depth_sweep", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load table depth sweep module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_structural_rejection_rate_matches_small_manual_product():
    """The structural ceiling should match the exact small-prime survivor product."""
    module = load_module()
    expected_survivor = (
        (1.0 - 1.0 / 3.0)
        * (1.0 - 1.0 / 5.0)
        * (1.0 - 1.0 / 7.0)
        * (1.0 - 1.0 / 11.0)
        * (1.0 - 1.0 / 13.0)
        * (1.0 - 1.0 / 17.0)
        * (1.0 - 1.0 / 19.0)
    )

    assert module.structural_rejection_rate(19) == 1.0 - expected_survivor


def test_build_interval_tables_activates_expected_layers():
    """The interval builder should cover the requested limit with the minimal stack."""
    module = load_module()

    primary_only = module.build_interval_tables(19, chunk_size=4, primary_limit=19, tail_limit=29)
    assert primary_only["primary_table"].limit == 19
    assert primary_only["tail_table"] is None
    assert primary_only["deep_tail_table"] is None

    tail_only = module.build_interval_tables(29, chunk_size=4, primary_limit=19, tail_limit=29)
    assert tail_only["primary_table"].limit == 19
    assert tail_only["tail_table"].limit == 29
    assert tail_only["deep_tail_table"] is None

    with_deep_tail = module.build_interval_tables(
        97,
        chunk_size=4,
        primary_limit=19,
        tail_limit=29,
    )
    assert with_deep_tail["primary_table"].limit == 19
    assert with_deep_tail["tail_table"].limit == 29
    assert with_deep_tail["deep_tail_table"].limit == 97
    assert with_deep_tail["deep_tail_min_bits"] == 2


def test_run_sweep_is_deterministic_on_small_panel(tmp_path):
    """A small sweep should return stable structural rows and write all artifacts."""
    module = load_module()
    results = module.run_sweep(
        output_dir=tmp_path,
        bit_lengths=[64, 128],
        table_limits=[19, 97],
        candidate_count=32,
        chunk_size=4,
        primary_limit=19,
        tail_limit=29,
        namespace="unit",
    )

    assert [row["observed_rejection_rate"] for row in results["rows"]] == [0.6875, 0.6875, 0.78125, 0.75]
    assert [row["factor_source_counts"]["survivor"] for row in results["rows"]] == [10, 10, 7, 8]
    assert (tmp_path / "table_depth_sweep_results.json").exists()
    assert (tmp_path / "table_depth_sweep_results.csv").exists()
    assert (tmp_path / "TABLE_DEPTH_SWEEP_REPORT.md").exists()
    assert (tmp_path / "table_depth_collapse.svg").exists()
