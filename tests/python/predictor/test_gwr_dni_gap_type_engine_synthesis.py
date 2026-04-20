"""Tests for the gap-type engine synthesis artifact builder."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "benchmarks" / "python" / "predictor" / "gwr_dni_gap_type_engine_synthesis.py"


def load_module():
    """Load the synthesis module from its file path."""
    spec = importlib.util.spec_from_file_location(
        "gwr_dni_gap_type_engine_synthesis",
        MODULE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load gwr_dni_gap_type_engine_synthesis module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_build_summary_freezes_expected_profiles():
    """The frozen engine summary should expose the chosen profiles and attractor."""
    module = load_module()
    summary = module.build_summary(
        generative=module.load_json(ROOT / "output" / "gwr_dni_gap_type_generative_probe_summary.json"),
        decode=module.load_json(ROOT / "output" / "gwr_dni_gap_type_engine_decode_summary.json"),
        scheduler=module.load_json(ROOT / "output" / "gwr_dni_gap_type_scheduler_probe_summary.json"),
        hybrid=module.load_json(ROOT / "output" / "gwr_dni_gap_type_hybrid_scheduler_probe_summary.json"),
        long_horizon=module.load_json(
            ROOT / "output" / "gwr_dni_gap_type_long_horizon_controller_probe_summary.json"
        ),
    )

    assert summary["version"] == "v1.0"
    assert summary["core_grammar"]["state_count"] == 14
    assert summary["core_grammar"]["attractor_name"] == "Semiprime Wheel Attractor"
    assert summary["frozen_profiles"]["local_fidelity"]["model_id"] == (
        "hybrid_lag2_mod8_reset_nontriad_scheduler"
    )
    assert summary["frozen_profiles"]["balanced_frontier"]["lock_length"] == 3
    assert summary["frozen_profiles"]["long_horizon_study"]["lock_length"] == 6
    assert summary["periodic_reset_signals"]["best_plain_cycle_length_by_pooled_window_l1"] == 11
    assert (
        summary["periodic_reset_signals"][
            "best_reset_higher_divisor_cycle_length_by_pooled_window_l1"
        ]
        == 2
    )


def test_entry_point_writes_synthesis_artifacts(tmp_path):
    """The CLI entry point should emit the frozen summary and overview PNG."""
    module = load_module()

    assert module.main(
        [
            "--output-dir",
            str(tmp_path),
        ]
    ) == 0

    summary_path = tmp_path / "gwr_dni_gap_type_engine_v1_summary.json"
    plot_path = tmp_path / "gwr_dni_gap_type_engine_v1_overview.png"
    assert summary_path.exists()
    assert plot_path.exists()

    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["core_grammar"]["state_count"] == 14
    assert payload["frozen_profiles"]["balanced_frontier"]["lock_length"] == 3
