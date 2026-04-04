"""Smoke tests for the insight-probe artifact generator."""

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


def test_insight_probes_emits_expected_artifacts(tmp_path):
    """The insight-probe entry point should emit JSON and SVG artifacts."""
    lex_json = tmp_path / "lexicographic_peak_validation.json"
    lex_json.write_text(
        json.dumps(
            {
                "rows": [
                    {
                        "scale": 10_000,
                        "mode": "exact",
                        "gap_count": 100,
                        "match_count": 100,
                        "counterexample_count": 0,
                        "match_rate": 1.0,
                        "min_log_score_margin": 1e-4,
                    },
                    {
                        "scale": 100_000,
                        "mode": "even-window",
                        "gap_count": 80,
                        "match_count": 80,
                        "counterexample_count": 0,
                        "match_rate": 1.0,
                        "min_log_score_margin": 1e-5,
                    },
                ]
            }
        )
        + "\n",
        encoding="utf-8",
    )

    module = load_module("insight_probes")
    output_dir = tmp_path / "insight_probes"

    assert (
        module.main(
            [
                "--output-dir",
                str(output_dir),
                "--validation-json",
                str(lex_json),
                "--full-limits",
                "10000",
                "--window-scales",
                "100000",
                "--window-size",
                "10000",
                "--window-count",
                "2",
            ]
        )
        == 0
    )

    assert (output_dir / "d4_availability_vs_peak_share.json").exists()
    assert (output_dir / "d4_availability_vs_peak_share.svg").exists()
    assert (output_dir / "residue_mod30_right_edge_share.json").exists()
    assert (output_dir / "residue_mod30_right_edge_share.svg").exists()
    assert (output_dir / "p2_wheel_gate_split.json").exists()
    assert (output_dir / "p2_wheel_gate_split.svg").exists()
    assert (output_dir / "lexicographic_rule_match_by_scale.json").exists()
    assert (output_dir / "lexicographic_rule_match_by_scale.svg").exists()
    assert (output_dir / "lexicographic_rule_match_rate.json").exists()
    assert (output_dir / "lexicographic_rule_match_rate.svg").exists()

    lane_payload = json.loads((output_dir / "p2_wheel_gate_split.json").read_text(encoding="utf-8"))
    categories = {row["category"] for row in lane_payload["summary"]}
    assert {"p2_open", "p2_blocked", "first_open_2", "first_open_4", "first_open_6"} <= categories


def test_insight_probes_defaults_extend_through_10e18():
    """The insight-probe script should expose the full configured sampled-scale ladder."""
    module = load_module("insight_probes")
    args = module.build_parser().parse_args([])

    assert args.full_limits == [1_000_000, 10_000_000]
    assert args.window_scales == [
        100_000_000,
        1_000_000_000,
        10_000_000_000,
        100_000_000_000,
        1_000_000_000_000,
        10_000_000_000_000,
        100_000_000_000_000,
        1_000_000_000_000_000,
        10_000_000_000_000_000,
        100_000_000_000_000_000,
        1_000_000_000_000_000_000,
    ]
