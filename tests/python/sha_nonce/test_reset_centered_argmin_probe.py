"""Smoke tests for the reset-centered SHA nonce argmin probe."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = (
    ROOT / "benchmarks" / "python" / "sha_nonce" / "reset_centered_argmin_probe.py"
)


def load_module():
    """Load the probe module directly from its file path."""
    spec = importlib.util.spec_from_file_location(
        "reset_centered_argmin_probe",
        MODULE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load reset-centered argmin probe module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_probe_emits_expected_artifacts(tmp_path):
    """The probe should emit JSON and SVG artifacts for a tiny deterministic run."""
    module = load_module()
    output_dir = tmp_path / "reset_centered_argmin_probe"

    assert (
        module.main(
            [
                "--output-dir",
                str(output_dir),
                "--headers",
                "1",
                "--windows-per-header",
                "8",
            ]
        )
        == 0
    )

    json_path = output_dir / "reset_centered_argmin_probe.json"
    svg_path = output_dir / "reset_centered_argmin_probe.svg"
    assert json_path.exists()
    assert svg_path.exists()

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["window_size"] == 256
    assert payload["headers"] == 1
    assert payload["windows_per_header"] == 8
    assert payload["total_windows_per_alignment"] == 8
    assert len(payload["rows"]) == 2
    assert payload["rows"][0]["label"] == "aligned"
    assert payload["rows"][1]["label"] == "half_shifted"


def test_reset_offsets_and_recentering_follow_little_endian_carry_boundaries():
    """Reset-centered positions should place the low-byte carry reset at offset zero."""
    module = load_module()

    assert module.reset_offset_for_window_start(0) == 0
    assert module.reset_offset_for_window_start(128) == 128
    assert module.reset_offset_for_window_start(256) == 0
    assert module.recenter_offset(128, 128) == 0
    assert module.recenter_offset(0, 128) == 128


def test_exchangeable_null_is_exactly_uniform():
    """The exact permutation null should assign equal expected mass to every offset."""
    module = load_module()

    expected = module.exact_exchangeable_null(512)

    assert len(expected) == 256
    assert expected[0] == 2.0
    assert all(value == 2.0 for value in expected)
