"""Tests for the gap-type engine decode artifact."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "benchmarks" / "python" / "predictor" / "gwr_dni_gap_type_engine_decode.py"


def load_module():
    """Load the engine decode module from its file path."""
    spec = importlib.util.spec_from_file_location(
        "gwr_dni_gap_type_engine_decode",
        MODULE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load gwr_dni_gap_type_engine_decode module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_higher_order_top_successor_share_detects_deterministic_cycle():
    """A short repeating sequence should be fully concentrated at each tested order."""
    module = load_module()
    sequence = ["A", "B", "A", "B", "A", "B", "A"]

    assert module.higher_order_top_successor_share(sequence, 1) == 1.0
    assert module.higher_order_top_successor_share(sequence, 2) == 1.0


def test_decode_rulebook_returns_bounded_rules_on_real_support():
    """The decoded rulebook should stay compact and expose the attractor rules."""
    module = load_module()
    detail_rows = module.GEN_PROBE.load_rows(ROOT / "output" / "gwr_dni_gap_type_catalog_details.csv")
    rows_by_surface = module.GEN_PROBE.surface_rows(detail_rows)
    train_surfaces = [f"10^{power}" for power in range(7, 18)]
    core_states = module.GEN_PROBE.persistent_core_states(rows_by_surface, train_surfaces)
    segments = module.GEN_PROBE.contiguous_core_segments(rows_by_surface, train_surfaces, core_states)
    support = module.GEN_PROBE.build_training_support(segments)

    rulebook = module.decode_rulebook(
        support["first_order_counter"],
        support["second_order_counter"],
    )

    assert len(rulebook) <= 12
    assert rulebook[0]["rule_id"].startswith("aggregate_")
    assert any("Semiprime Wheel Attractor" in row["natural_language"] for row in rulebook)


def test_load_record_rows_reads_local_primegap_extract():
    """The local record-gap extract should be present and nontrivial."""
    module = load_module()
    rows = module.load_record_rows(ROOT / "data" / "external" / "primegap_list_records_1e12_1e18.csv")

    assert len(rows) > 300
    assert rows[0]["gap_start"].isdigit()
    assert rows[-1]["gap_size"].isdigit()
