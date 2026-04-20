"""Tests for the reduced gap-type generative grammar probe."""

from __future__ import annotations

import importlib.util
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = (
    ROOT / "benchmarks" / "python" / "predictor" / "gwr_dni_gap_type_generative_probe.py"
)


def load_module():
    """Load the generative probe module from its file path."""
    spec = importlib.util.spec_from_file_location(
        "gwr_dni_gap_type_generative_probe",
        MODULE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load gwr_dni_gap_type_generative_probe module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_balanced_cycle_preserves_weighted_counts():
    """The deterministic cycle should preserve the requested support exactly."""
    module = load_module()
    cycle = module.balanced_cycle(Counter({"A": 3, "B": 2, "C": 1}))

    assert len(cycle) == 6
    assert Counter(cycle) == Counter({"A": 3, "B": 2, "C": 1})


def test_summary_detects_14_state_core_and_second_order_pair_gain():
    """The held-out surface should favor the second-order grammar on pair structure."""
    module = load_module()
    rows = module.load_rows(ROOT / "output" / "gwr_dni_gap_type_catalog_details.csv")
    summary, synthetic_rows = module.summarize(
        rows=rows,
        train_surfaces=[f"10^{power}" for power in range(7, 18)],
        held_surface="10^18",
        synthetic_length=512,
    )

    comparisons = summary["model_comparisons"]
    assert summary["core_state_count"] == 14
    assert len(summary["core_states"]) == 14
    assert comparisons["second_order_rotor"]["reduced_state_pair_l1"] < (
        comparisons["first_order_rotor"]["reduced_state_pair_l1"]
    )
    assert comparisons["second_order_rotor"]["reduced_state_pair_l1"] < (
        comparisons["iid_balanced_cycle"]["reduced_state_pair_l1"]
    )
    assert comparisons["second_order_rotor"]["triad_share_error"] < (
        comparisons["first_order_rotor"]["triad_share_error"]
    )
    assert comparisons["second_order_rotor"]["triad_share_error"] < (
        comparisons["iid_balanced_cycle"]["triad_share_error"]
    )
    assert len(synthetic_rows) == 512


def test_entry_point_writes_generative_artifacts(tmp_path):
    """The CLI entry point should emit JSON, CSV, and PNG artifacts."""
    module = load_module()

    assert module.main(
        [
            "--detail-csv",
            str(ROOT / "output" / "gwr_dni_gap_type_catalog_details.csv"),
            "--output-dir",
            str(tmp_path),
            "--synthetic-length",
            "256",
        ]
    ) == 0

    summary_path = tmp_path / "gwr_dni_gap_type_generative_probe_summary.json"
    csv_path = tmp_path / "gwr_dni_gap_type_generative_probe_synthetic.csv"
    plot_path = tmp_path / "gwr_dni_gap_type_generative_probe_overview.png"
    assert summary_path.exists()
    assert csv_path.exists()
    assert plot_path.exists()

    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["core_state_count"] == 14
    assert "second_order_rotor" in payload["model_comparisons"]
    assert payload["second_order_synthetic_summary"]["synthetic_length"] == 256
