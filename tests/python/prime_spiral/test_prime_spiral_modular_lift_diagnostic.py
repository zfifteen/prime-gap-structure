"""Tests for the prime-spiral modular-lift diagnostic script."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = (
    ROOT
    / "benchmarks"
    / "python"
    / "prime_spiral"
    / "prime_spiral_modular_lift_diagnostic.py"
)


def load_module():
    """Load the benchmark script from its file path."""
    spec = importlib.util.spec_from_file_location(
        "prime_spiral_modular_lift_diagnostic",
        MODULE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load prime_spiral_modular_lift_diagnostic module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_run_diagnostic_collapses_shifted_prime_zeta_and_blocks_lift():
    """The diagnostic should show collapse first and Jacobi failure second."""
    module = load_module()

    summary, plot_inputs = module.run_diagnostic(
        prime_limit=200,
        spiral_prime_count=40,
        q_series_limit=40,
        sigma=2.0,
        t_min=-4.0,
        t_max=4.0,
        t_samples=41,
        tau_real=0.31,
        tau_imag=0.91,
        z_real_samples=21,
        z_imag_samples=15,
        z_imag_half_span=0.2,
    )

    assert summary["dirichlet_collapse"]["status"] == "collapsed_to_shifted_prime_zeta"
    assert summary["dirichlet_collapse"]["max_absolute_difference"] < 1e-12
    assert summary["dirichlet_collapse"]["max_relative_difference"] < 1e-12
    assert summary["named_path_closure"]["prime_indicator_tau_only"] is True
    assert summary["named_path_closure"]["conclusion"].startswith("named_path_stays_tau_only")
    assert summary["jacobi_check"]["passes_weight_12_modular_checks"] is True
    assert summary["jacobi_check"]["fails_index_1_elliptic_check"] is True
    assert summary["jacobi_check"]["elliptic_tau_shift_residual_mean"] > 1.0
    assert summary["fourier_match"]["status"] == "blocked"
    assert plot_inputs["residual_grid"].shape == (15, 21)


def test_entry_point_writes_json_and_plot_artifacts(tmp_path):
    """The CLI should emit one JSON summary and three PNG artifacts."""
    module = load_module()

    assert (
        module.main(
            [
                "--prime-limit",
                "200",
                "--spiral-prime-count",
                "40",
                "--q-series-limit",
                "40",
                "--t-min",
                "-4",
                "--t-max",
                "4",
                "--t-samples",
                "41",
                "--z-real-samples",
                "21",
                "--z-imag-samples",
                "15",
                "--z-imag-half-span",
                "0.2",
                "--output-dir",
                str(tmp_path),
            ]
        )
        == 0
    )

    summary_path = tmp_path / "prime_spiral_modular_lift_diagnostic_summary.json"
    spiral_path = tmp_path / "prime_spiral_projection.png"
    collapse_path = tmp_path / "dirichlet_resonance_collapse.png"
    jacobi_path = tmp_path / "jacobi_tau_only_failure.png"

    assert summary_path.exists()
    assert spiral_path.exists()
    assert collapse_path.exists()
    assert jacobi_path.exists()

    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["dirichlet_collapse"]["status"] == "collapsed_to_shifted_prime_zeta"
    assert payload["jacobi_check"]["passes_weight_12_modular_checks"] is True
    assert payload["jacobi_check"]["fails_index_1_elliptic_check"] is True
    assert payload["fourier_match"]["status"] == "blocked"
