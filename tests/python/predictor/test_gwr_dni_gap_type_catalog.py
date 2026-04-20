"""Tests for the deterministic GWR/DNI gap-type catalog."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "benchmarks" / "python" / "predictor" / "gwr_dni_gap_type_catalog.py"


def load_module():
    """Load the gap-type catalog script from its file path."""
    spec = importlib.util.spec_from_file_location("gwr_dni_gap_type_catalog", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load gwr_dni_gap_type_catalog module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_summary_tracks_union_and_surface_bookkeeping():
    """A small catalog should report stable surface and union counts."""
    module = load_module()
    surfaces = module.catalog_surfaces(
        exact_max_right_prime=1_000,
        min_power=4,
        max_power=4,
        window_steps=8,
    )
    summary, detail_rows = module.summarize_surfaces(
        surfaces,
        exact_max_right_prime=1_000,
        window_steps=8,
    )

    assert len(surfaces) == 2
    assert summary["surface_count"] == 2
    assert summary["surface_order"] == ["baseline_1e3", "10^4"]
    assert summary["surface_display_order"] == ["<=10^3", "10^4"]
    assert summary["surface_summaries"][0]["gap_count"] == len(surfaces[0]["rows"])
    assert summary["surface_summaries"][1]["gap_count"] == 8
    assert summary["union_distinct_exact_type_count"] >= summary["surface_summaries"][0]["distinct_exact_type_count"]
    assert summary["distinct_first_open_offsets"] == [2, 4, 6]
    assert summary["common_exact_type_count"] <= summary["surface_summaries"][1]["distinct_exact_type_count"]
    assert summary["overall_top_exact_types"]
    assert len(detail_rows) == len(surfaces[0]["rows"]) + 8


def test_entry_point_writes_catalog_artifacts(tmp_path):
    """The CLI entry point should emit JSON, CSV, and PNG artifacts."""
    module = load_module()

    assert module.main(
        [
            "--output-dir",
            str(tmp_path),
            "--exact-max-right-prime",
            "1000",
            "--min-power",
            "4",
            "--max-power",
            "4",
            "--window-steps",
            "8",
        ]
    ) == 0

    summary_path = tmp_path / "gwr_dni_gap_type_catalog_summary.json"
    detail_path = tmp_path / "gwr_dni_gap_type_catalog_details.csv"
    plot_path = tmp_path / "gwr_dni_gap_type_catalog_overview.png"
    assert summary_path.exists()
    assert detail_path.exists()
    assert plot_path.exists()

    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["surface_count"] == 2
    assert payload["union_distinct_exact_type_count"] > 0
    assert payload["overall_family_distribution"]["odd_semiprime"]["count"] > 0
    assert payload["surface_summaries"][1]["gap_count"] == 8
