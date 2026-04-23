"""Tests for the phase-budget hidden-state probe."""

from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = (
    ROOT
    / "benchmarks"
    / "python"
    / "predictor"
    / "gwr_phase_budget_hidden_state_probe.py"
)


def load_module():
    """Load the phase-budget hidden-state probe from disk."""
    spec = importlib.util.spec_from_file_location(
        "gwr_phase_budget_hidden_state_probe",
        MODULE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load gwr_phase_budget_hidden_state_probe module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_assign_phase_budget_bit_marks_non_d4_and_splits_d4_geometry():
    """The phase-budget bit should mark non-d4 rows and median-split d4 rows."""
    module = load_module()
    rows = [
        {
            "current_next_dmin": 4,
            "current_carrier_family": "odd_semiprime",
            "current_winner_offset": 1,
            "current_first_open_offset": 2,
            "current_square_phase_utilization": 0.1,
        },
        {
            "current_next_dmin": 4,
            "current_carrier_family": "odd_semiprime",
            "current_winner_offset": 1,
            "current_first_open_offset": 2,
            "current_square_phase_utilization": 0.4,
        },
        {
            "current_next_dmin": 4,
            "current_carrier_family": "odd_semiprime",
            "current_winner_offset": 1,
            "current_first_open_offset": 2,
            "current_square_phase_utilization": 0.9,
        },
        {
            "current_next_dmin": 3,
            "current_carrier_family": "prime_square",
            "current_winner_offset": 1,
            "current_first_open_offset": 4,
            "current_square_phase_utilization": None,
        },
    ]

    module.assign_phase_budget_bit(rows)

    assert rows[0]["phase_budget_bit"] == "d4_low"
    assert rows[1]["phase_budget_bit"] == "d4_high"
    assert rows[2]["phase_budget_bit"] == "d4_high"
    assert rows[3]["phase_budget_bit"] == "non_d4"


def test_summarize_matches_retained_high_scale_surface():
    """The retained high-scale catalog surface should keep the current pooled signal."""
    module = load_module()
    summary, strata = module.summarize(
        module.DEFAULT_DETAIL_CSV,
        min_power=12,
        max_power=18,
    )

    metrics = {
        row["candidate_id"]: row for row in summary["candidate_metrics"]
    }
    phase_stats = summary["phase_budget_label_stats"]
    overlay = summary["parity_previous_phase_overlay"]

    assert summary["transition_count"] == 1778
    assert math.isclose(summary["baseline_log_loss"], 0.5993080476093358)
    assert metrics["phase_budget_bit"]["log_loss_gain"] > metrics["current_winner_parity"]["log_loss_gain"]
    assert metrics["current_winner_parity+previous_reduced_state+phase_budget_bit"]["log_loss_gain"] > metrics["current_winner_parity+previous_reduced_state"]["log_loss_gain"]
    assert phase_stats["d4_low"]["support"] == 691
    assert phase_stats["d4_high"]["support"] == 730
    assert phase_stats["non_d4"]["support"] == 357
    assert phase_stats["d4_low"]["next_triad_share"] > phase_stats["d4_high"]["next_triad_share"]
    assert overlay["used_strata_count"] == 16
    assert overlay["positive_lift_strata_count"] == 11
    assert overlay["negative_lift_strata_count"] == 5
    assert math.isclose(overlay["balanced_weighted_lift"], 0.04508163857013867)
    assert len(strata) == overlay["used_strata_count"]


def test_cli_writes_artifacts(tmp_path):
    """The CLI entry point should emit summary, strata, and findings artifacts."""
    module = load_module()
    findings_path = tmp_path / "phase_budget_hidden_state_findings.md"

    assert (
        module.main(
            [
                "--output-dir",
                str(tmp_path),
                "--findings-path",
                str(findings_path),
            ]
        )
        == 0
    )

    summary_payload = json.loads(
        (tmp_path / "gwr_phase_budget_hidden_state_probe_summary.json").read_text(
            encoding="utf-8"
        )
    )
    strata_text = (tmp_path / "gwr_phase_budget_hidden_state_probe_strata.csv").read_text(
        encoding="utf-8"
    )
    findings_text = findings_path.read_text(encoding="utf-8")

    assert summary_payload["transition_count"] == 1778
    assert "balanced_weighted_lift" in summary_payload["parity_previous_phase_overlay"]
    assert "current_winner_parity" in strata_text
    assert "phase-budget label" in findings_text
