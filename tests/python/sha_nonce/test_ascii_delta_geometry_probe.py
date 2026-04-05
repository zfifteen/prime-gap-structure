"""Smoke tests for the ASCII delta geometry probe."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = (
    ROOT / "benchmarks" / "python" / "sha_nonce" / "ascii_delta_geometry_probe.py"
)


def load_module():
    """Load the probe module directly from its file path."""
    spec = importlib.util.spec_from_file_location(
        "ascii_delta_geometry_probe",
        MODULE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load ASCII delta geometry probe module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_ascii_delta_probe_emits_expected_json(tmp_path):
    """The probe should emit JSON artifacts for a small deterministic run."""
    module = load_module()
    output_dir = tmp_path / "ascii_delta_geometry_probe"

    assert (
        module.main(
            [
                "--output-dir",
                str(output_dir),
                "--bit-length",
                "256",
                "--start-index",
                "95",
                "--batch-size",
                "16",
                "--batch-count",
                "2",
                "--prefilter-target-count",
                "2",
                "--mr-target-count",
                "1",
            ]
        )
        == 0
    )

    json_path = output_dir / "ascii_delta_geometry_probe.json"
    assert json_path.exists()

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["metadata"]["bit_length"] == 256
    assert payload["metadata"]["start_index"] == 95
    assert payload["metadata"]["batch_size"] == 16
    assert payload["metadata"]["batch_count"] == 2
    assert payload["metadata"]["total_indices"] == 32
    assert len(payload["ordering_summaries"]) == 5
    assert payload["ordering_summaries"][0]["label"] == "combined"
    assert len(payload["batch_rows"]) == 2


def test_geometry_features_capture_length_increase_and_trailing_zeros():
    """The feature extractor should capture the 999 -> 1000 rollover correctly."""
    module = load_module()
    features = module.compute_geometry_features(
        namespace="dni-research",
        bit_length=2048,
        previous_index=999,
        current_index=1000,
        counter=0,
    )

    assert features["changed_digits"] == 4
    assert features["trailing_zero_depth"] == 3
    assert features["length_increased"] is True
    assert isinstance(features["leftmost_delta_pos"], int)
