"""Tests for the ROTR7 / sigma0 SHA nonce phase probe."""

from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "benchmarks" / "python" / "sha_nonce" / "rotr7_phase_probe.py"


def load_module():
    """Load the probe module directly from its file path."""
    spec = importlib.util.spec_from_file_location("rotr7_phase_probe", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load ROTR7 phase probe module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_half_shifted_recentering_preserves_low_byte_coordinate():
    """Reset-centered offsets should recover the low byte across both alignments."""
    module = load_module()

    aligned_start = 0
    shifted_start = 128

    for centered_offset in (0, 1, 29, 128, 255):
        aligned_nonce = module.recentered_nonce(aligned_start, centered_offset)
        shifted_nonce = module.recentered_nonce(shifted_start, centered_offset)
        assert aligned_nonce % 256 == centered_offset
        assert shifted_nonce % 256 == centered_offset


def test_harmonic_component_recovers_known_k7_phase():
    """The harmonic extractor should recover a synthetic k=7 sinusoid."""
    module = load_module()
    values = [
        math.cos(2.0 * math.pi * 7.0 * offset / 256.0 - 0.5)
        for offset in range(256)
    ]

    component = module.harmonic_component(values, 7)

    assert component["amplitude"] > 100.0
    assert abs(component["phase_radians"] + 0.5) < 1e-9


def test_probe_emits_artifacts_from_existing_observed_json(tmp_path):
    """The phase probe should emit JSON and SVG from a deterministic observed artifact."""
    module = load_module()
    output_dir = tmp_path / "rotr7_phase_probe"

    assert (
        module.main(
            [
                "--observed-json",
                str(
                    ROOT
                    / "benchmarks"
                    / "output"
                    / "python"
                    / "sha_nonce"
                    / "reset_centered_argmin_probe"
                    / "reset_centered_argmin_probe.json"
                ),
                "--output-dir",
                str(output_dir),
            ]
        )
        == 0
    )

    json_path = output_dir / "rotr7_phase_probe.json"
    svg_path = output_dir / "rotr7_phase_probe.svg"
    assert json_path.exists()
    assert svg_path.exists()

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["target_harmonic"] == 7
    assert len(payload["observed_mean_profile"]) == 256
    assert len(payload["rows"]) == 4
