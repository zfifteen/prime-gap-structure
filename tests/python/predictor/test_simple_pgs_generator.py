"""Tests for the minimal PGS iprime generator restart."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = ROOT / "src" / "python"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from z_band_prime_predictor.simple_pgs_generator import (  # noqa: E402
    FALLBACK_SOURCE,
    PGS_SOURCE,
    audit_summary,
    diagnostic_record,
    diagnostic_records,
    emit_record,
    emit_records,
    first_prime_in_chamber,
    has_trial_divisor,
    main,
    next_prime_by_trial_division,
    summary,
)


def test_record_has_only_p_and_q():
    """The minimal record contract should stay physically small."""
    record = emit_record(11)

    assert set(record) == {"p", "q"}
    assert record == {"p": 11, "q": 13}


def test_emit_records_never_withholds_an_anchor():
    """Every supplied anchor should produce exactly one iprime candidate."""
    anchors = [11, 23, 89]
    records = emit_records(anchors)

    assert len(records) == len(anchors)
    assert [record["p"] for record in records] == anchors
    assert all(set(record) == {"p", "q"} for record in records)


def test_explicit_boundary_offset_can_emit_q():
    """A correct deterministic selector result can emit q."""
    records = emit_records([23], boundary_offsets={23: 6})

    assert records == [{"p": 23, "q": 29}]


def test_sidecar_diagnostics_report_source_outside_emitted_stream():
    """Diagnostics may report source without changing emitted records."""
    records = emit_records([23, 89], boundary_offsets={23: 6, 89: 2})
    diagnostics = diagnostic_records([23, 89], boundary_offsets={23: 6, 89: 2})

    assert records == [{"p": 23, "q": 29}, {"p": 89, "q": 97}]
    assert diagnostics == [
        {"p": 23, "q": 29, "source": PGS_SOURCE},
        {"p": 89, "q": 97, "source": FALLBACK_SOURCE},
    ]
    assert diagnostic_record(89) == {
        "p": 89,
        "q": 97,
        "source": FALLBACK_SOURCE,
    }


def test_fallback_tests_all_integer_divisors_to_sqrt():
    """The fallback divisor check should be complete and mechanical."""
    assert not has_trial_divisor(2)
    assert has_trial_divisor(49)
    assert has_trial_divisor(91)
    assert has_trial_divisor(121)
    assert not has_trial_divisor(97)


def test_fallback_uses_trial_division_next_prime_with_chamber_expansion():
    """The fallback should return the actual next prime."""
    assert first_prime_in_chamber(89, 1) is None
    assert first_prime_in_chamber(89, 8) == 97
    assert next_prime_by_trial_division(89) == 97
    assert next_prime_by_trial_division(89, candidate_bound=1) == 97
    assert emit_record(89) == {"p": 89, "q": 97}


def test_bad_boundary_offset_falls_back_to_correct_prime():
    """An incorrect selector result must not produce a wrong q."""
    assert emit_records([89], boundary_offsets={89: 2}) == [{"p": 89, "q": 97}]


def test_minimal_summaries_have_only_requested_counts():
    """Summaries should not grow metadata fields."""
    records = emit_records([11, 89])

    assert summary(records) == {"anchors": 2, "emitted": 2}
    assert audit_summary(records) == {
        "anchors": 2,
        "emitted": 2,
        "confirmed": 2,
        "failed": 0,
    }


def test_cli_writes_lf_records_and_summary(tmp_path):
    """The tiny CLI should write LF-terminated artifacts."""
    assert (
        main(
            [
                "--anchors",
                "11,89",
                "--candidate-bound",
                "1",
                "--audit",
                "--output-dir",
                str(tmp_path),
            ]
        )
        == 0
    )

    records_path = tmp_path / "records.jsonl"
    diagnostics_path = tmp_path / "diagnostics.jsonl"
    summary_path = tmp_path / "summary.json"
    assert b"\r\n" not in records_path.read_bytes()
    assert b"\r\n" not in diagnostics_path.read_bytes()
    assert b"\r\n" not in summary_path.read_bytes()

    records = [
        json.loads(line)
        for line in records_path.read_text(encoding="utf-8").splitlines()
    ]
    assert all(set(record) == {"p", "q"} for record in records)
    diagnostics = [
        json.loads(line)
        for line in diagnostics_path.read_text(encoding="utf-8").splitlines()
    ]
    assert all(set(record) == {"p", "q", "source"} for record in diagnostics)
    assert all(record["source"] == FALLBACK_SOURCE for record in diagnostics)
    assert json.loads(summary_path.read_text(encoding="utf-8")) == {
        "anchors": 2,
        "confirmed": 2,
        "emitted": 2,
        "failed": 0,
    }


def test_new_generator_does_not_import_old_graph_generator():
    """The clean restart must not reuse the graph generator."""
    source = (
        SOURCE_DIR / "z_band_prime_predictor" / "simple_pgs_generator.py"
    ).read_text(encoding="utf-8")

    assert "prime_inference_generator" not in source
    assert "experimental_graph_prime_generator" not in source
    assert "boundary_certificate_graph" not in source
