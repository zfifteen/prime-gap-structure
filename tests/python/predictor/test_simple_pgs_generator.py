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
    CHAIN_FALLBACK_SOURCE,
    FALLBACK_SOURCE,
    PGS_SOURCE,
    emit_record,
    emit_records,
    first_prime_in_chamber,
    has_trial_divisor,
    next_prime_by_trial_division,
    pgs_gap_certificate,
)
from z_band_prime_predictor.simple_pgs_controller import (  # noqa: E402
    diagnostic_record,
    diagnostic_records,
    main as controller_main,
    summary,
)
from z_band_prime_predictor.simple_pgs_audit import (  # noqa: E402
    audit_report,
    audit_summary,
    main as audit_main,
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


def test_default_pgs_gap_two_rule_displaces_fallback_when_correct():
    """The first tiny PGS rule should only count when fallback agrees."""
    record = diagnostic_record(11)
    assert record["p"] == 11
    assert record["q"] == 13
    assert record["source"] == PGS_SOURCE
    assert record["certificate"]["rule_id"] == "pgs_chamber_closure_v2"
    assert record["certificate"]["gap_offset"] == 2
    assert record["certificate"]["fallback_agreed"] is True
    assert diagnostic_record(89)["source"] == PGS_SOURCE
    assert diagnostic_record(89)["certificate"]["gap_offset"] == 8


def test_small_gap_certificate_closes_every_interior_offset():
    """A PGS certificate must close every offset before q."""
    certificate = pgs_gap_certificate(23, 6)

    assert certificate["rule_id"] == "pgs_chamber_closure_v2"
    assert certificate["p"] == 23
    assert certificate["q"] == 29
    assert certificate["gap_offset"] == 6
    assert certificate["candidate_bound"] == 128
    assert certificate["closed_offsets_before_q"] == []
    assert certificate["closure_reason_by_offset"] == {}
    assert certificate["unclosed_offsets_before_q"] == []
    assert certificate["carrier_w"] == 23
    assert certificate["carrier_d"] == 2
    assert certificate["used_forbidden_tool"] is False
    assert certificate["fallback_agreed"] is False


def test_sidecar_diagnostics_report_source_outside_emitted_stream():
    """Diagnostics may report source without changing emitted records."""
    records = emit_records([23, 89], boundary_offsets={23: 6, 89: 2})
    diagnostics = diagnostic_records([23, 89], boundary_offsets={23: 6, 89: 2})

    assert records == [{"p": 23, "q": 29}, {"p": 89, "q": 97}]
    assert diagnostics[0]["source"] == PGS_SOURCE
    assert diagnostics[0]["certificate"]["gap_offset"] == 6
    assert diagnostics[1]["source"] == CHAIN_FALLBACK_SOURCE
    assert diagnostics[1]["chain_seed"] == 91
    assert diagnostics[1]["chain_limit"] == 8
    assert diagnostics[1]["chain_position_selected"] == 1
    assert diagnostics[1]["chain_fallback_success"] is True
    assert diagnostics[1]["full_fallback_used"] is False
    assert diagnostic_record(89)["certificate"]["gap_offset"] == 8


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


def test_cli_writes_lf_records_and_summary(tmp_path):
    """The controller CLI should write LF-terminated artifacts."""
    assert (
        controller_main(
            [
                "--anchors",
                "11,89",
                "--candidate-bound",
                "128",
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
    assert all(
        set(record)
        == {
            "p",
            "q",
            "source",
            "certificate",
            "chain_seed",
            "chain_limit",
            "chain_position_selected",
            "chain_nodes_checked",
            "chain_fallback_success",
            "full_fallback_used",
        }
        for record in diagnostics
    )
    assert diagnostics[0]["source"] == PGS_SOURCE
    assert diagnostics[0]["certificate"]["gap_offset"] == 2
    assert diagnostics[1]["source"] == PGS_SOURCE
    assert diagnostics[1]["certificate"]["gap_offset"] == 8
    assert json.loads(summary_path.read_text(encoding="utf-8")) == {
        "anchors": 2,
        "emitted": 2,
    }


def test_audit_cli_writes_report_outside_generator(tmp_path):
    """Audit/report output should come from the audit module, not generator."""
    generator_dir = tmp_path / "generated"
    audit_dir = tmp_path / "audit"
    assert (
        controller_main(
            [
                "--anchors",
                "11,89",
                "--candidate-bound",
                "128",
                "--output-dir",
                str(generator_dir),
            ]
        )
        == 0
    )
    assert (
        audit_main(
            [
                "--records",
                str(generator_dir / "records.jsonl"),
                "--diagnostics",
                str(generator_dir / "diagnostics.jsonl"),
                "--output-dir",
                str(audit_dir),
            ]
        )
        == 0
    )

    summary_path = audit_dir / "summary.json"
    report_path = audit_dir / "report.json"
    assert b"\r\n" not in summary_path.read_bytes()
    assert b"\r\n" not in report_path.read_bytes()
    assert json.loads(summary_path.read_text(encoding="utf-8")) == {
        "anchors": 2,
        "confirmed": 2,
        "emitted": 2,
        "failed": 0,
    }
    assert json.loads(report_path.read_text(encoding="utf-8")) == {
        "anchors_scanned": 2,
        "emitted_count": 2,
        "audit_confirmed": 2,
        "audit_failed": 0,
        "accuracy_status": "PASS",
        "pgs_status": "PGS_PASS",
        "pgs_count": 2,
        "chain_fallback_count": 0,
        "fallback_count": 0,
        "pgs_rate": 1.0,
        "chain_fallback_rate": 0.0,
        "fallback_rate": 0.0,
        "pgs_percent": 100.0,
        "chain_fallback_percent": 0.0,
        "fallback_percent": 0.0,
        "generator_status": "PGS_PASS",
        "pgs_by_rule": {"pgs_chamber_closure_v2": 2},
        "pgs_missing_certificate_count": 0,
        "first_failure": None,
    }


def test_audit_report_surfaces_fallback_displacement_metrics():
    """The report should make PGS displacement the visible metric."""
    records = emit_records([11, 23, 89])
    diagnostics = diagnostic_records([11, 23, 89])

    assert audit_report(records, diagnostics) == {
        "anchors_scanned": 3,
        "emitted_count": 3,
        "audit_confirmed": 3,
        "audit_failed": 0,
        "accuracy_status": "PASS",
        "pgs_status": "PGS_PASS",
        "pgs_count": 3,
        "chain_fallback_count": 0,
        "fallback_count": 0,
        "pgs_rate": 1.0,
        "chain_fallback_rate": 0.0,
        "fallback_rate": 0.0,
        "pgs_percent": 100.0,
        "chain_fallback_percent": 0.0,
        "fallback_percent": 0.0,
        "generator_status": "PGS_PASS",
        "pgs_by_rule": {"pgs_chamber_closure_v2": 3},
        "pgs_missing_certificate_count": 0,
        "first_failure": None,
    }


def test_new_generator_does_not_import_old_graph_generator():
    """The clean restart must not reuse the graph generator."""
    source = (
        SOURCE_DIR / "z_band_prime_predictor" / "simple_pgs_generator.py"
    ).read_text(encoding="utf-8")

    assert "prime_inference_generator" not in source
    assert "experimental_graph_prime_generator" not in source
    assert "boundary_certificate_graph" not in source


def test_new_generator_does_not_use_forbidden_classical_tools():
    """The generator must not call forbidden primality helpers."""
    source = (
        SOURCE_DIR / "z_band_prime_predictor" / "simple_pgs_generator.py"
    ).read_text(encoding="utf-8")

    forbidden_terms = [
        "sympy",
        "nextprime",
        "isprime",
        "primerange",
        "Miller",
        "miller",
    ]
    assert all(term not in source for term in forbidden_terms)


def test_new_generator_file_does_not_contain_audit_code():
    """Audit/report code must live outside the generator file."""
    source = (
        SOURCE_DIR / "z_band_prime_predictor" / "simple_pgs_generator.py"
    ).read_text(encoding="utf-8")

    forbidden_terms = [
        "audit",
        "report",
        "confirmed",
        "failed",
        "actual_q",
        "argparse",
        "json",
        "Path",
        "write",
        "diagnostic",
        "summary",
        "main",
    ]
    assert all(term not in source for term in forbidden_terms)


def test_controller_can_orchestrate_generation_and_audit(tmp_path):
    """The controller should orchestrate generation artifacts and audit."""
    assert (
        controller_main(
            [
                "--anchors",
                "11,23,89",
                "--candidate-bound",
                "128",
                "--audit",
                "--output-dir",
                str(tmp_path),
            ]
        )
        == 0
    )

    assert json.loads((tmp_path / "summary.json").read_text(encoding="utf-8")) == {
        "anchors": 3,
        "emitted": 3,
    }
    assert json.loads(
        (tmp_path / "audit_summary.json").read_text(encoding="utf-8")
    ) == {
        "anchors": 3,
        "emitted": 3,
        "confirmed": 3,
        "failed": 0,
    }
    assert json.loads((tmp_path / "report.json").read_text(encoding="utf-8")) == {
        "anchors_scanned": 3,
        "emitted_count": 3,
        "audit_confirmed": 3,
        "audit_failed": 0,
        "accuracy_status": "PASS",
        "pgs_status": "PGS_PASS",
        "pgs_count": 3,
        "chain_fallback_count": 0,
        "fallback_count": 0,
        "pgs_rate": 1.0,
        "chain_fallback_rate": 0.0,
        "fallback_rate": 0.0,
        "pgs_percent": 100.0,
        "chain_fallback_percent": 0.0,
        "fallback_percent": 0.0,
        "generator_status": "PGS_PASS",
        "pgs_by_rule": {"pgs_chamber_closure_v2": 3},
        "pgs_missing_certificate_count": 0,
        "first_failure": None,
    }
