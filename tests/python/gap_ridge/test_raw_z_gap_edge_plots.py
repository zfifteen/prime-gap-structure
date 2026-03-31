"""Smoke tests for the raw composite Z gap-edge plotting script."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BENCHMARKS_DIR = ROOT / "benchmarks" / "python" / "gap_ridge"


def load_module(name: str):
    """Load one benchmark module directly from its file path."""
    path = BENCHMARKS_DIR / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module {name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_plot_script_renders_expected_artifacts(tmp_path):
    """The plotting entry point should emit the requested 2D and 3D figures."""
    module = load_module("raw_z_gap_edge_plots")
    suite_path = tmp_path / "suite.json"
    suite_path.write_text(
        json.dumps(
            {
                "exact_full_runs": [
                    {
                        "scale": 1_000_000,
                        "gap_count": 70327,
                        "observed_edge2_share": 0.43600608585607237,
                        "baseline_edge2_share": 0.22185858570959013,
                        "edge2_enrichment": 1.9652432402449296,
                        "observed_d4_share": 0.8290272583787166,
                        "baseline_d4_share": 0.20140064321856735,
                        "d4_enrichment": 4.11630889122348,
                        "left_share": 0.7455742460221536,
                        "right_share": 0.16018030059578825,
                        "center_share": 0.0942454533820581,
                        "window_mode": "exact",
                        "window_size": 999999,
                        "sampled_gap_count": 70327,
                        "approximate_gap_count": 70327,
                        "seed": None,
                    }
                ],
                "even_window_runs": [
                    {
                        "scale": 100_000_000,
                        "gap_count": 5_321_132,
                        "observed_edge2_share": 0.37175604739743345,
                        "baseline_edge2_share": 0.18714011615272313,
                        "edge2_enrichment": 1.9865117914859427,
                        "observed_d4_share": 0.8240605570393668,
                        "baseline_d4_share": 0.16296585768001615,
                        "d4_enrichment": 5.0566454150010465,
                        "left_share": 0.7621983442620855,
                        "right_share": 0.1605318191693046,
                        "center_share": 0.07726983656860983,
                        "window_mode": "even",
                        "window_size": 10_000_000,
                        "sampled_gap_count": 5_321_132,
                        "approximate_gap_count": 5_321_132,
                        "seed": None,
                    }
                ],
                "seeded_window_runs": [
                    {
                        "scale": 100_000_000,
                        "gap_count": 5_351_254,
                        "observed_edge2_share": 0.37244429062795376,
                        "baseline_edge2_share": 0.18764832976667525,
                        "edge2_enrichment": 1.9847993909194745,
                        "observed_d4_share": 0.8242191456432455,
                        "baseline_d4_share": 0.16349705317471327,
                        "d4_enrichment": 5.041186551310398,
                        "left_share": 0.7618012525662209,
                        "right_share": 0.16052330911595675,
                        "center_share": 0.07767543831782232,
                        "window_mode": "seeded-random",
                        "window_size": 10_000_000,
                        "sampled_gap_count": 5_351_254,
                        "approximate_gap_count": 5_351_254,
                        "seed": 20260331,
                    }
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    output_dir = tmp_path / "plots"
    assert (
        module.main(
            [
                "--suite-json",
                str(suite_path),
                "--output-dir",
                str(output_dir),
                "--detail-limit",
                "10000",
                "--gap-size-threshold",
                "1",
            ]
        )
        == 0
    )

    assert (output_dir / "regime_enrichment_2d.svg").exists()
    assert (output_dir / "edge_distance_distribution_2d.svg").exists()
    assert (output_dir / "carrier_divisor_distribution_2d.svg").exists()
    assert (output_dir / "representative_gap_profile_2d.svg").exists()
    assert (output_dir / "gap_size_edge_distance_enrichment_3d.png").exists()
    assert (output_dir / "gap_size_carrier_enrichment_3d.png").exists()
