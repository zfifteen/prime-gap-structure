"""Tests for the PGS Prime Inference Generator Milestone 0 scaffold."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_DIR = ROOT / "benchmarks" / "python" / "prime_inference_generator"
CLI_PATH = MODULE_DIR / "pgs_prime_inference_mvp.py"
PURE_PATH = MODULE_DIR / "pure_generator.py"
GATE_PATH = MODULE_DIR / "forbidden_dependency_gate.py"
TRANSITION_PROBE_PATH = MODULE_DIR / "transition_state_boundary_probe.py"
COLLISION_FORENSICS_PATH = MODULE_DIR / "legal_ladder_collision_forensics.py"
PRESSURE_PROBE_PATH = MODULE_DIR / "pressure_state_boundary_probe.py"
PRESSURE_FORENSICS_PATH = MODULE_DIR / "pressure_collision_forensics.py"
HIGHER_DIVISOR_FORENSICS_PATH = (
    MODULE_DIR / "higher_divisor_pressure_forensics.py"
)
LEGAL_CANDIDATE_HARDENING_PATH = (
    MODULE_DIR / "legal_candidate_hardening_probe.py"
)
COMPRESSED_STATE_SEARCH_PATH = MODULE_DIR / "compressed_state_search.py"
COMPOSITE_EXCLUSION_PROBE_PATH = (
    MODULE_DIR / "composite_exclusion_boundary_probe.py"
)
COMPOSITE_EXCLUSION_UNRESOLVED_FORENSICS_PATH = (
    MODULE_DIR / "composite_exclusion_unresolved_forensics.py"
)
SINGLE_HOLE_CLOSURE_PROBE_PATH = MODULE_DIR / "single_hole_closure_probe.py"
RESOLVED_SURVIVOR_DOMINANCE_FORENSICS_PATH = (
    MODULE_DIR / "resolved_survivor_dominance_forensics.py"
)
RIGHT_BOUNDARY_PRESSURE_CEILING_PROBE_PATH = (
    MODULE_DIR / "right_boundary_pressure_ceiling_probe.py"
)
CARRIER_LOCK_CONDITION_PROBE_PATH = (
    MODULE_DIR / "carrier_lock_condition_probe.py"
)
RESIDUAL_AFTER_LOCKED_CEILING_FORENSICS_PATH = (
    MODULE_DIR / "residual_after_locked_ceiling_forensics.py"
)
UNRESOLVED_ALTERNATIVE_CLOSURE_FORENSICS_PATH = (
    MODULE_DIR / "unresolved_alternative_closure_forensics.py"
)
RESOLVED_BOUNDARY_ABSORPTION_SAFETY_PROBE_PATH = (
    MODULE_DIR / "resolved_boundary_absorption_safety_probe.py"
)
RESOLVED_BOUNDARY_LOCK_SEPARATOR_PROBE_PATH = (
    MODULE_DIR / "resolved_boundary_lock_separator_probe.py"
)
HIGHER_DIVISOR_PRESSURE_LOCK_HARDENING_PATH = (
    MODULE_DIR / "higher_divisor_pressure_lock_hardening.py"
)
HIGHER_DIVISOR_PRESSURE_LOCK_ACTIVATION_PROFILE_PATH = (
    MODULE_DIR / "higher_divisor_pressure_lock_activation_profile.py"
)
LOCK_NEAR_MISS_PROFILE_PATH = MODULE_DIR / "lock_near_miss_profile.py"
PREVIOUS_CHAMBER_RESET_LOCK_PROBE_PATH = (
    MODULE_DIR / "previous_chamber_reset_lock_probe.py"
)
PREVIOUS_TO_CURRENT_CARRIER_SHIFT_LOCK_HARDENING_PATH = (
    MODULE_DIR / "previous_to_current_carrier_shift_lock_hardening.py"
)
BOUNDARY_LAW_005_FAMILY_INTEGRATION_MATRIX_PATH = (
    MODULE_DIR / "boundary_law_005_family_integration_matrix.py"
)
BOUNDARY_LAW_005B_FAILURE_AUTOPSY_PATH = (
    MODULE_DIR / "boundary_law_005b_failure_autopsy.py"
)
ABSORPTION_LOCK_ACTION_POPULATION_AUDIT_PATH = (
    MODULE_DIR / "absorption_lock_action_population_audit.py"
)
BOUNDARY_LAW_005A_STRESS_PATH = MODULE_DIR / "boundary_law_005a_stress.py"
BOUNDARY_LAW_005A_REFINEMENT_PROBE_PATH = (
    MODULE_DIR / "boundary_law_005a_refinement_probe.py"
)
OFFLINE_PGS_CERTIFICATE_EMITTER_PATH = (
    MODULE_DIR / "offline_pgs_certificate_emitter.py"
)


def load_module(path: Path, name: str):
    """Load one module by file path."""
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_pure_cli_writes_fail_closed_artifacts(tmp_path):
    """Pure mode writes LF-terminated trace and summary without validation fields."""
    module = load_module(CLI_PATH, "pgs_prime_inference_mvp")

    assert module.main(["--mode", "pure", "--anchor-prime", "11", "--count", "5", "--output-dir", str(tmp_path)]) == 0

    trace_path = tmp_path / "pgs_prime_inference_pure_trace.jsonl"
    summary_path = tmp_path / "pgs_prime_inference_pure_summary.json"
    assert trace_path.exists()
    assert summary_path.exists()
    assert b"\r\n" not in trace_path.read_bytes()
    assert b"\r\n" not in summary_path.read_bytes()

    rows = [json.loads(line) for line in trace_path.read_text(encoding="utf-8").splitlines()]
    assert len(rows) == 1
    row = rows[0]
    assert row["anchor_prime_p"] == 11
    assert row["inferred_prime_q_hat"] is None
    assert row["inference_status"] == "failed_closed"
    assert row["failure_reason"] == "BOUNDARY_LAW_UNAVAILABLE"
    assert "validated_prime_bool" not in row
    assert "validation_backend" not in row

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["emitted_inferred_count"] == 0
    assert summary["generation_status"] == "failed_closed"
    assert summary["failure_reason"] == "BOUNDARY_LAW_UNAVAILABLE"
    assert summary["generation_failure_count"] == 1
    assert "confirmed_count" not in summary


def test_pure_cli_accepts_only_anchor_11(tmp_path):
    """Milestone 0 pure mode is intentionally pinned to anchor prime 11."""
    module = load_module(CLI_PATH, "pgs_prime_inference_mvp_bad_anchor")

    try:
        module.main(["--mode", "pure", "--anchor-prime", "13", "--count", "1", "--output-dir", str(tmp_path)])
    except ValueError as exc:
        assert "only supports anchor prime 11" in str(exc)
    else:
        raise AssertionError("pure mode should reject anchors other than 11")


def test_audit_reads_existing_jsonl_and_separates_generation_failures(tmp_path):
    """Audit mode reads the emitted trace and keeps generation failures separate."""
    module = load_module(CLI_PATH, "pgs_prime_inference_mvp_audit")
    pure_dir = tmp_path / "pure"
    audit_dir = tmp_path / "audit"

    assert module.main(["--mode", "pure", "--anchor-prime", "11", "--count", "3", "--output-dir", str(pure_dir)]) == 0
    trace_path = pure_dir / "pgs_prime_inference_pure_trace.jsonl"
    assert module.main(["--audit-existing-jsonl", str(trace_path), "--output-dir", str(audit_dir)]) == 0

    summary_path = audit_dir / "pgs_prime_inference_audit_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["generation_failure_count"] == 1
    assert summary["inferred_count"] == 0
    assert summary["confirmed_count"] == 0
    assert summary["validation_failure_count"] == 0
    assert summary["first_failure_index"] == 1
    assert summary["first_failed_record"]["failure_type"] == "generation_failure"


def test_forbidden_dependency_gate_passes_on_pure_module():
    """The pure generator path should remain free of forbidden dependencies."""
    gate = load_module(GATE_PATH, "prime_inference_forbidden_dependency_gate")

    assert gate.forbidden_dependency_violations(PURE_PATH) == []


def test_forbidden_dependency_gate_fails_on_synthetic_forbidden_import_and_call(tmp_path):
    """The gate catches forbidden classical and next-prime dependencies."""
    gate = load_module(GATE_PATH, "prime_inference_forbidden_dependency_gate_synthetic")
    fixture = tmp_path / "bad_pure.py"
    fixture.write_text(
        "from sympy import nextprime\n"
        "from z_band_prime_composite_field import divisor_counts_segment\n"
        "def run(q):\n"
        "    return nextprime(q) + int(divisor_counts_segment(q, q + 1)[0])\n",
        encoding="utf-8",
        newline="\n",
    )

    violations = gate.forbidden_dependency_violations(fixture)
    assert any("forbidden imported name nextprime" in item for item in violations)
    assert any("forbidden import from z_band_prime_composite_field" in item for item in violations)
    assert any("forbidden call nextprime" in item for item in violations)
    assert any("forbidden call divisor_counts_segment" in item for item in violations)


def test_pure_generator_source_does_not_import_old_predictor():
    """The pure path must not import the old recursive predictor walker."""
    source = PURE_PATH.read_text(encoding="utf-8")
    assert "gwr_dni_recursive_walk" not in source
    assert "z_band_prime_predictor" not in source
    assert "divisor_counts_segment" not in source


def test_transition_state_boundary_probe_writes_collision_reports(tmp_path):
    """The offline theorem-search probe should report state-vector collisions."""
    module = load_module(TRANSITION_PROBE_PATH, "transition_state_boundary_probe")

    assert (
        module.main(
            [
                "--start-prime",
                "11",
                "--max-anchor",
                "50",
                "--prefix-len",
                "6",
                "--output-dir",
                str(tmp_path),
            ]
        )
        == 0
    )

    rows_path = tmp_path / "transition_state_boundary_probe_rows.jsonl"
    summary_path = tmp_path / "transition_state_boundary_probe_summary.json"
    assert rows_path.exists()
    assert summary_path.exists()
    assert b"\r\n" not in rows_path.read_bytes()
    assert b"\r\n" not in summary_path.read_bytes()

    rows = [json.loads(line) for line in rows_path.read_text(encoding="utf-8").splitlines()]
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert rows
    assert summary["mode"] == "offline_theorem_search"
    assert summary["row_count"] == len(rows)
    assert summary["state_vectors"]

    first_report = summary["state_vectors"][0]
    assert {
        "state_vector",
        "row_count",
        "distinct_state_count",
        "collision_count",
        "collision_examples",
        "max_bucket_size",
        "zero_collision",
        "uses_boundary_offset",
        "uses_gap_width",
        "uses_prime_marker_d2",
        "uses_stop_at_first_prime",
        "uses_nextprime_or_isprime",
        "boundary_offset_within_prefix_rate",
        "state_contains_boundary_token_rate",
        "eligible_for_pure_generation",
        "zero_collision_and_eligible",
    } <= set(first_report)

    reports = {report["state_vector"]: report for report in summary["state_vectors"]}
    assert "first_zero_collision_eligible_state_vector" in summary
    assert reports["carrier_ladder"]["uses_prime_marker_d2"] is True
    assert reports["carrier_ladder"]["uses_nextprime_or_isprime"] is True
    assert reports["carrier_ladder"]["eligible_for_pure_generation"] is False
    assert reports["known_composite_divisor_ladder"]["uses_prime_marker_d2"] is False
    assert reports["known_composite_divisor_ladder"]["uses_gap_width"] is False
    assert reports["known_composite_divisor_ladder"]["eligible_for_pure_generation"] is True
    assert reports["wheel"]["eligible_for_pure_generation"] is True


def test_legal_ladder_collision_forensics_writes_required_fields(tmp_path):
    """Collision forensics should compare legal collisions to contaminated keys."""
    module = load_module(COLLISION_FORENSICS_PATH, "legal_ladder_collision_forensics")

    assert (
        module.main(
            [
                "--start-prime",
                "11",
                "--max-anchor",
                "500",
                "--prefix-len",
                "8",
                "--limit",
                "3",
                "--output-dir",
                str(tmp_path),
            ]
        )
        == 0
    )

    buckets_path = tmp_path / "legal_ladder_collision_forensics_buckets.jsonl"
    summary_path = tmp_path / "legal_ladder_collision_forensics_summary.json"
    assert buckets_path.exists()
    assert summary_path.exists()
    assert b"\r\n" not in buckets_path.read_bytes()
    assert b"\r\n" not in summary_path.read_bytes()

    records = [json.loads(line) for line in buckets_path.read_text(encoding="utf-8").splitlines()]
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert records
    assert summary["mode"] == "offline_collision_forensics"
    assert summary["state_vector_name"] == "known_composite_divisor_ladder"
    assert summary["written_collision_bucket_count"] == len(records)

    record = records[0]
    assert {
        "state_vector_name",
        "legal_state_key",
        "boundary_offsets_observed",
        "anchors_with_same_legal_state",
        "contaminated_carrier_ladder_keys",
        "contaminated_previous_gap_ladder_keys",
        "difference_between_legal_and_illegal_keys",
        "candidate_missing_observable",
    } <= set(record)


def test_legal_ladder_collision_forensics_rejects_contaminated_state(tmp_path):
    """Forensics should not accept contaminated states as legal targets."""
    module = load_module(
        COLLISION_FORENSICS_PATH,
        "legal_ladder_collision_forensics_reject",
    )

    try:
        module.main(
            [
                "--state-vector",
                "carrier_ladder",
                "--output-dir",
                str(tmp_path),
            ]
        )
    except ValueError as exc:
        assert "not a legal state vector" in str(exc)
    else:
        raise AssertionError("contaminated state vector should be rejected")


def test_pressure_state_boundary_probe_reports_legality_and_collisions(tmp_path):
    """Pressure-state probe should report collisions and per-state eligibility."""
    module = load_module(PRESSURE_PROBE_PATH, "pressure_state_boundary_probe")

    assert (
        module.main(
            [
                "--start-prime",
                "11",
                "--max-anchor",
                "200",
                "--prefix-len",
                "8",
                "--output-dir",
                str(tmp_path),
            ]
        )
        == 0
    )

    rows_path = tmp_path / "pressure_state_boundary_probe_rows.jsonl"
    summary_path = tmp_path / "pressure_state_boundary_probe_summary.json"
    assert rows_path.exists()
    assert summary_path.exists()
    assert b"\r\n" not in rows_path.read_bytes()
    assert b"\r\n" not in summary_path.read_bytes()

    rows = [json.loads(line) for line in rows_path.read_text(encoding="utf-8").splitlines()]
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert rows
    assert summary["mode"] == "offline_pressure_state_theorem_search"
    assert summary["row_count"] == len(rows)
    assert "first_zero_collision_eligible_state_vector" in summary

    reports = {report["state_vector_name"]: report for report in summary["state_vectors"]}
    assert reports["square_pressure_state"]["eligible_for_pure_generation"] is True
    assert reports["semiprime_pressure_state"]["uses_exact_factorization"] is True
    assert reports["semiprime_pressure_state"]["eligible_for_pure_generation"] is False
    assert reports["previous_chamber_pressure_state"]["uses_previous_gap_context"] is True
    assert (
        reports["previous_chamber_plus_square_pressure_state"][
            "eligible_for_pure_generation"
        ]
        is True
    )
    assert (
        reports["previous_chamber_plus_higher_divisor_pressure_state"][
            "eligible_for_pure_generation"
        ]
        is False
    )
    assert (
        reports["previous_chamber_plus_threat_schedule_state"][
            "uses_nextprime_or_isprime"
        ]
        is True
    )
    assert {
        "state_vector_name",
        "eligible_for_pure_generation",
        "row_count",
        "distinct_state_count",
        "collision_count",
        "collision_rate",
        "first_collision_examples",
        "zero_collision",
    } <= set(next(iter(reports.values())))


def test_pressure_collision_forensics_writes_collision_buckets(tmp_path):
    """Pressure collision forensics should write bucket deltas and summary counts."""
    module = load_module(PRESSURE_FORENSICS_PATH, "pressure_collision_forensics")

    assert (
        module.main(
            [
                "--start-prime",
                "11",
                "--max-anchor",
                "500",
                "--prefix-len",
                "8",
                "--output-dir",
                str(tmp_path),
            ]
        )
        == 0
    )

    buckets_path = tmp_path / "pressure_collision_forensics_buckets.jsonl"
    summary_path = tmp_path / "pressure_collision_forensics_summary.json"
    assert buckets_path.exists()
    assert summary_path.exists()
    assert b"\r\n" not in buckets_path.read_bytes()
    assert b"\r\n" not in summary_path.read_bytes()

    records = [json.loads(line) for line in buckets_path.read_text(encoding="utf-8").splitlines()]
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert records
    assert summary["mode"] == "offline_pressure_collision_forensics"
    assert summary["state_vector_name"] == "previous_chamber_pressure_state"
    assert summary["written_collision_bucket_count"] == len(records)
    assert "candidate_missing_observable_counts" in summary

    record = records[0]
    assert {
        "boundary_offsets_observed",
        "anchors_by_bucket",
        "shared_previous_state",
        "legal_feature_deltas",
        "candidate_missing_observable",
    } <= set(record)


def test_higher_divisor_pressure_forensics_reports_legalization_candidates(tmp_path):
    """Higher-divisor forensics should audit contamination and legal candidates."""
    module = load_module(
        HIGHER_DIVISOR_FORENSICS_PATH,
        "higher_divisor_pressure_forensics",
    )

    assert (
        module.main(
            [
                "--start-prime",
                "11",
                "--max-anchor",
                "500",
                "--prefix-len",
                "8",
                "--output-dir",
                str(tmp_path),
            ]
        )
        == 0
    )

    exact_path = tmp_path / "higher_divisor_pressure_forensics_exact_states.jsonl"
    candidates_path = tmp_path / "higher_divisor_pressure_forensics_candidates.jsonl"
    summary_path = tmp_path / "higher_divisor_pressure_forensics_summary.json"
    assert exact_path.exists()
    assert candidates_path.exists()
    assert summary_path.exists()
    assert b"\r\n" not in exact_path.read_bytes()
    assert b"\r\n" not in candidates_path.read_bytes()
    assert b"\r\n" not in summary_path.read_bytes()

    exact_records = [
        json.loads(line) for line in exact_path.read_text(encoding="utf-8").splitlines()
    ]
    candidate_records = [
        json.loads(line)
        for line in candidates_path.read_text(encoding="utf-8").splitlines()
    ]
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert exact_records
    assert candidate_records
    assert summary["mode"] == "offline_higher_divisor_pressure_forensics"
    assert summary["row_count"] > 0
    assert "first_zero_collision_eligible_state_vector" in summary
    assert "minimal_illegal_component" in summary

    exact = {record["state_vector_name"]: record for record in exact_records}
    audited = exact["previous_chamber_plus_higher_divisor_pressure_state"]
    assert audited["eligible_for_pure_generation"] is False
    assert audited["uses_exact_factorization"] is True
    assert audited["uses_d2_recognition"] is True
    assert audited["uses_old_walker"] is False
    assert {
        "state_vector_name",
        "collision_count",
        "eligible_for_pure_generation",
        "ineligibility_reasons",
        "uses_exact_factorization",
        "uses_prime_marker",
        "uses_future_boundary",
        "uses_scan_to_first_prime",
        "uses_d2_recognition",
        "uses_full_divisor_count",
        "uses_old_walker",
        "feature_components",
        "component_ablation_results",
        "minimal_illegal_component",
    } <= set(audited)

    candidates = {
        record["state_vector_name"]: record for record in candidate_records
    }
    small_factor = candidates["small_factor_witness_pressure"]
    assert small_factor["eligible_for_pure_generation"] is True
    assert small_factor["uses_prime_marker"] is False
    assert small_factor["uses_full_divisor_count"] is False


def test_legal_candidate_hardening_probe_reports_anti_table_metrics(tmp_path):
    """Legal candidate hardening should expose leakage and anti-table metrics."""
    module = load_module(
        LEGAL_CANDIDATE_HARDENING_PATH,
        "legal_candidate_hardening_probe",
    )

    assert (
        module.main(
            [
                "--start-anchor",
                "11",
                "--max-anchor",
                "500",
                "--prefix-len",
                "8",
                "--output-dir",
                str(tmp_path),
            ]
        )
        == 0
    )

    candidates_path = tmp_path / "legal_candidate_hardening_candidates.jsonl"
    summary_path = tmp_path / "legal_candidate_hardening_summary.json"
    assert candidates_path.exists()
    assert summary_path.exists()
    assert b"\r\n" not in candidates_path.read_bytes()
    assert b"\r\n" not in summary_path.read_bytes()

    candidate_records = [
        json.loads(line)
        for line in candidates_path.read_text(encoding="utf-8").splitlines()
    ]
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["mode"] == "offline_legal_candidate_hardening"
    assert summary["boundary_law_005_status"] == "not_approved"
    assert summary["row_count"] > 0
    assert len(candidate_records) == 3

    record = candidate_records[0]
    assert {
        "candidate_name",
        "eligible_for_pure_generation",
        "row_count",
        "distinct_state_count",
        "collision_count",
        "collision_rate",
        "max_bucket_size",
        "mean_bucket_size",
        "singleton_bucket_count",
        "singleton_bucket_rate",
        "state_entropy_estimate",
        "uses_anchor_value",
        "uses_future_boundary",
        "uses_prime_marker",
        "uses_full_divisor_count",
        "uses_exact_factorization",
        "uses_scan_to_first_prime",
        "uses_old_walker",
        "first_collision_examples",
        "table_like_state",
        "hardening_gate_status",
        "passes_hardening_gate",
    } <= set(record)

    reports = {item["candidate_name"]: item for item in candidate_records}
    for name in (
        "multiplicity_pressure_without_primality",
        "power_signature_pressure",
        "bounded_composite_witness_pressure",
    ):
        assert reports[name]["eligible_for_pure_generation"] is True
        assert reports[name]["uses_prime_marker"] is False
        assert reports[name]["uses_full_divisor_count"] is False
        assert reports[name]["uses_exact_factorization"] is False
        assert reports[name]["uses_anchor_value"] is False
        assert reports[name]["passes_hardening_gate"] is False
        assert reports[name]["hardening_gate_status"] in {
            "failed_collision_gate",
            "quarantined_table_like_state",
        }


def test_compressed_state_search_reports_collision_compression_frontier(tmp_path):
    """Compressed search should report collision and compression gates."""
    module = load_module(COMPRESSED_STATE_SEARCH_PATH, "compressed_state_search")

    assert (
        module.main(
            [
                "--start-anchor",
                "11",
                "--max-anchor",
                "500",
                "--prefix-len",
                "8",
                "--output-dir",
                str(tmp_path),
            ]
        )
        == 0
    )

    candidates_path = tmp_path / "compressed_state_search_candidates.jsonl"
    summary_path = tmp_path / "compressed_state_search_summary.json"
    assert candidates_path.exists()
    assert summary_path.exists()
    assert b"\r\n" not in candidates_path.read_bytes()
    assert b"\r\n" not in summary_path.read_bytes()

    candidate_records = [
        json.loads(line)
        for line in candidates_path.read_text(encoding="utf-8").splitlines()
    ]
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["mode"] == "offline_compressed_legal_state_search"
    assert summary["boundary_law_005_status"] == "not_approved"
    assert summary["row_count"] > 0
    assert "frontier_survivors" in summary
    assert len(candidate_records) == 10

    record = candidate_records[0]
    assert {
        "candidate_name",
        "row_count",
        "distinct_state_count",
        "distinct_state_ratio",
        "singleton_bucket_rate",
        "max_bucket_size",
        "mean_bucket_size",
        "collision_count",
        "collision_rate",
        "compression_score",
        "collision_examples",
        "passes_collision_gate",
        "passes_compression_gate",
        "passes_frontier_gate",
    } <= set(record)

    reports = {item["candidate_name"]: item for item in candidate_records}
    assert "multiplicity_pressure_histogram" in reports
    assert "multiplicity_pressure_coarse_counts" in reports
    assert reports["multiplicity_pressure_histogram"]["compression_score"] >= 0.0


def test_composite_exclusion_boundary_probe_writes_safe_elimination_artifacts(tmp_path):
    """Composite exclusion should report survivors and post-elimination labels."""
    module = load_module(
        COMPOSITE_EXCLUSION_PROBE_PATH,
        "composite_exclusion_boundary_probe",
    )

    assert (
        module.main(
            [
                "--start-anchor",
                "11",
                "--max-anchor",
                "500",
                "--candidate-bound",
                "64",
                "--output-dir",
                str(tmp_path),
            ]
        )
        == 0
    )

    rows_path = tmp_path / "composite_exclusion_boundary_probe_rows.jsonl"
    summary_path = tmp_path / "composite_exclusion_boundary_probe_summary.json"
    assert rows_path.exists()
    assert summary_path.exists()
    assert b"\r\n" not in rows_path.read_bytes()
    assert b"\r\n" not in summary_path.read_bytes()

    rows = [json.loads(line) for line in rows_path.read_text(encoding="utf-8").splitlines()]
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert rows
    assert summary["mode"] == "offline_composite_exclusion_boundary_probe"
    assert summary["boundary_law_005_status"] == "not_approved"
    assert summary["row_count"] == len(rows)
    assert "true_boundary_rejected_count" in summary
    assert "true_boundary_status_counts" in summary
    assert "average_rejected_count" in summary
    assert "average_unresolved_count" in summary
    assert "average_survives_count" in summary
    assert "unique_resolved_survivor_count" in summary
    assert "rule_family_reports" in summary
    assert "unique_survivor_match_rate" in summary

    row = rows[0]
    assert {
        "anchor_p",
        "candidate_offsets",
        "candidate_count",
        "rejected_count",
        "unresolved_count",
        "survives_count",
        "survivor_count",
        "survivors",
        "unresolved",
        "rejection_reasons_by_candidate",
        "unresolved_reasons_by_candidate",
        "candidate_status_by_offset",
        "actual_boundary_offset_label",
        "true_boundary_status",
        "unique_resolved_survivor",
        "unique_survivor_matches_label",
        "failure_reason",
    } <= set(row)

    rule_reports = {
        report["rule_family"]: report for report in summary["rule_family_reports"]
    }
    assert "positive_composite_witness_rejection" in rule_reports
    assert "interior_open_unclosed_rejection" in rule_reports
    for report in rule_reports.values():
        assert {
            "rejected_count",
            "true_boundary_rejected_count",
            "average_survivor_count_after_rule",
            "marginal_rejection_count",
            "unique_survivor_count_after_rule",
        } <= set(report)


def test_composite_exclusion_probe_integrates_single_hole_closure_flag(tmp_path):
    """The single-hole closure rule should be explicit and separately attributed."""
    module = load_module(
        COMPOSITE_EXCLUSION_PROBE_PATH,
        "composite_exclusion_boundary_probe_with_closure",
    )

    assert (
        module.main(
            [
                "--start-anchor",
                "11",
                "--max-anchor",
                "2000",
                "--candidate-bound",
                "64",
                "--enable-single-hole-positive-witness-closure",
                "--witness-bound",
                "97",
                "--output-dir",
                str(tmp_path),
            ]
        )
        == 0
    )

    summary_path = tmp_path / "composite_exclusion_boundary_probe_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["single_hole_positive_witness_closure_enabled"] is True
    assert summary["witness_bound"] == 97
    assert summary["before_single_hole_closure_metrics"] is not None
    assert summary["single_hole_positive_witness_closure_applied_count"] > 0
    assert summary["single_hole_positive_witness_true_boundary_closures"] > 0
    assert summary["true_boundary_rejected_count"] == 0

    rule_reports = {
        report["rule_family"]: report for report in summary["rule_family_reports"]
    }
    closure_report = rule_reports["single_hole_positive_witness_closure"]
    assert closure_report["closure_applied_count"] == summary[
        "single_hole_positive_witness_closure_applied_count"
    ]


def test_composite_exclusion_probe_integrates_carrier_locked_ceiling_flag(tmp_path):
    """Carrier-locked ceilings should be explicit and separately attributed."""
    module = load_module(
        COMPOSITE_EXCLUSION_PROBE_PATH,
        "composite_exclusion_boundary_probe_with_carrier_locked_ceiling",
    )

    assert (
        module.main(
            [
                "--start-anchor",
                "11",
                "--max-anchor",
                "500",
                "--candidate-bound",
                "64",
                "--enable-single-hole-positive-witness-closure",
                "--witness-bound",
                "97",
                "--enable-carrier-locked-pressure-ceiling",
                "--carrier-lock-predicate",
                "higher_divisor_pressure_before_threat",
                "--output-dir",
                str(tmp_path),
            ]
        )
        == 0
    )

    summary_path = tmp_path / "composite_exclusion_boundary_probe_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["carrier_locked_pressure_ceiling_enabled"] is True
    assert summary["carrier_lock_predicate"] == "higher_divisor_pressure_before_threat"
    assert summary["before_carrier_locked_pressure_ceiling_metrics"] is not None
    assert summary["carrier_locked_ceiling_applied_count"] > 0
    assert summary["carrier_locked_ceiling_true_boundary_safe_count"] > 0
    assert summary["carrier_locked_ceiling_false_candidate_pruned_count"] > 0
    assert summary["carrier_locked_ceiling_unsafe_count"] == 0
    assert summary["true_boundary_rejected_count"] == 0

    rule_reports = {
        report["rule_family"]: report for report in summary["rule_family_reports"]
    }
    ceiling_report = rule_reports["carrier_locked_pressure_ceiling_rejection"]
    assert ceiling_report["true_boundary_rejected_count"] == 0
    assert ceiling_report["marginal_rejection_count"] > 0


def test_composite_exclusion_probe_integrates_hd_locked_absorption_flag(tmp_path):
    """Higher-divisor locked absorption should be explicit and attributed."""
    module = load_module(
        COMPOSITE_EXCLUSION_PROBE_PATH,
        "composite_exclusion_boundary_probe_with_hd_locked_absorption",
    )

    assert (
        module.main(
            [
                "--start-anchor",
                "11",
                "--max-anchor",
                "500",
                "--candidate-bound",
                "64",
                "--enable-single-hole-positive-witness-closure",
                "--witness-bound",
                "97",
                "--enable-carrier-locked-pressure-ceiling",
                "--carrier-lock-predicate",
                "unresolved_alternatives_before_threat",
                "--enable-higher-divisor-pressure-locked-absorption",
                "--output-dir",
                str(tmp_path),
            ]
        )
        == 0
    )

    summary_path = tmp_path / "composite_exclusion_boundary_probe_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["higher_divisor_pressure_locked_absorption_enabled"] is True
    assert summary["boundary_law_005_status"] == "not_approved"
    assert summary["true_boundary_rejected_count"] == 0
    assert summary["unique_resolved_survivor_count"] > 0
    assert summary["higher_divisor_locked_absorption_applied_count"] > 0
    assert summary["higher_divisor_locked_absorption_correct_count"] > 0
    assert summary["higher_divisor_locked_absorption_wrong_count"] == 0
    assert summary["false_resolved_survivor_absorbed_count"] == 0

    rule_reports = {
        report["rule_family"]: report for report in summary["rule_family_reports"]
    }
    absorption_report = rule_reports[
        "higher_divisor_locked_absorption_rejection"
    ]
    assert absorption_report["true_boundary_rejected_count"] == 0
    assert absorption_report["marginal_rejection_count"] > 0


def test_composite_exclusion_probe_integrates_previous_carrier_shift_flag(tmp_path):
    """Previous-carrier shift locked absorption should be explicit and attributed."""
    module = load_module(
        COMPOSITE_EXCLUSION_PROBE_PATH,
        "composite_exclusion_boundary_probe_with_previous_carrier_shift",
    )

    assert (
        module.main(
            [
                "--start-anchor",
                "11",
                "--max-anchor",
                "500",
                "--candidate-bound",
                "64",
                "--enable-single-hole-positive-witness-closure",
                "--witness-bound",
                "97",
                "--enable-carrier-locked-pressure-ceiling",
                "--carrier-lock-predicate",
                "unresolved_alternatives_before_threat",
                "--enable-previous-carrier-shift-locked-absorption",
                "--output-dir",
                str(tmp_path),
            ]
        )
        == 0
    )

    summary_path = tmp_path / "composite_exclusion_boundary_probe_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["previous_carrier_shift_locked_absorption_enabled"] is True
    assert summary["locked_absorption_mode"] == "then"
    assert summary["boundary_law_005_status"] == "not_approved"
    assert summary["true_boundary_rejected_count"] == 0
    assert summary["unique_resolved_survivor_count"] > 0
    assert summary["previous_carrier_shift_locked_absorption_applied_count"] > 0
    assert summary["previous_carrier_shift_locked_absorption_correct_count"] > 0
    assert summary["previous_carrier_shift_locked_absorption_wrong_count"] == 0
    assert (
        summary["previous_carrier_shift_false_resolved_survivor_absorbed_count"]
        == 0
    )

    rule_reports = {
        report["rule_family"]: report for report in summary["rule_family_reports"]
    }
    absorption_report = rule_reports[
        "previous_carrier_shift_locked_absorption_rejection"
    ]
    assert absorption_report["true_boundary_rejected_count"] == 0
    assert absorption_report["marginal_rejection_count"] > 0


def test_composite_exclusion_eliminator_source_has_no_forbidden_helpers():
    """The eliminator body should not call classical boundary helpers."""
    source = COMPOSITE_EXCLUSION_PROBE_PATH.read_text(encoding="utf-8")
    eliminator_source = source.split("def eliminate_candidates", 1)[1].split(
        "def label_offsets",
        1,
    )[0]
    forbidden_tokens = (
        "isprime",
        "nextprime",
        "prevprime",
        "Miller",
        "divisor_count",
        "factorint",
        "gwr_dni_recursive_walk",
        "divisor_counts_segment",
    )
    for token in forbidden_tokens:
        assert token not in eliminator_source


def test_composite_exclusion_unresolved_forensics_reports_missing_evidence(tmp_path):
    """Unresolved forensics should classify true-boundary unresolved rows."""
    module = load_module(
        COMPOSITE_EXCLUSION_UNRESOLVED_FORENSICS_PATH,
        "composite_exclusion_unresolved_forensics",
    )

    assert (
        module.main(
            [
                "--start-anchor",
                "11",
                "--max-anchor",
                "500",
                "--candidate-bound",
                "64",
                "--output-dir",
                str(tmp_path),
            ]
        )
        == 0
    )

    records_path = tmp_path / "composite_exclusion_unresolved_forensics_records.jsonl"
    summary_path = tmp_path / "composite_exclusion_unresolved_forensics_summary.json"
    assert records_path.exists()
    assert summary_path.exists()
    assert b"\r\n" not in records_path.read_bytes()
    assert b"\r\n" not in summary_path.read_bytes()

    records = [
        json.loads(line)
        for line in records_path.read_text(encoding="utf-8").splitlines()
    ]
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["mode"] == "offline_composite_exclusion_unresolved_forensics"
    assert summary["boundary_law_005_status"] == "not_approved"
    assert summary["true_boundary_rejected_count"] == 0
    assert "missing_evidence_counts" in summary
    assert "candidate_resolving_rule_counts" in summary

    if records:
        record = records[0]
        assert {
            "anchor_p",
            "resolved_survivor",
            "actual_boundary_label",
            "unresolved_true_boundary_candidate",
            "why_resolved_survivor_survived",
            "why_true_boundary_was_unresolved",
            "which_evidence_was_missing",
            "which_pgs_rule_would_resolve_it",
        } <= set(record)


def test_single_hole_closure_probe_reports_closure_candidates(tmp_path):
    """Single-hole probe should report legal closure candidates and diagnostics."""
    module = load_module(
        SINGLE_HOLE_CLOSURE_PROBE_PATH,
        "single_hole_closure_probe",
    )

    assert (
        module.main(
            [
                "--start-anchor",
                "11",
                "--max-anchor",
                "500",
                "--candidate-bound",
                "64",
                "--output-dir",
                str(tmp_path),
            ]
        )
        == 0
    )

    records_path = tmp_path / "single_hole_closure_probe_records.jsonl"
    summary_path = tmp_path / "single_hole_closure_probe_summary.json"
    assert records_path.exists()
    assert summary_path.exists()
    assert b"\r\n" not in records_path.read_bytes()
    assert b"\r\n" not in summary_path.read_bytes()

    records = [
        json.loads(line)
        for line in records_path.read_text(encoding="utf-8").splitlines()
    ]
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["mode"] == "offline_single_hole_closure_probe"
    assert summary["boundary_law_005_status"] == "not_approved"
    assert summary["true_boundary_rejected_count"] == 0
    assert "single_hole_case_count" in summary
    assert "single_hole_closure_candidate_count" in summary
    assert "candidate_missing_rule_counts" in summary

    if records:
        record = records[0]
        assert {
            "anchor_p",
            "actual_boundary_offset_label",
            "unresolved_open_offset",
            "unresolved_open_n",
            "resolved_survivor_offset",
            "candidate_chamber_width",
            "known_composite_witnesses_before_hole",
            "known_composite_witnesses_after_hole",
            "gwr_carrier_w",
            "gwr_carrier_offset",
            "gwr_carrier_divisor_count",
            "hole_relative_to_carrier",
            "hole_wheel_residue",
            "hole_square_status",
            "hole_power_status",
            "hole_small_factor_witness_status",
            "hole_semiprime_pressure",
            "hole_higher_divisor_pressure",
            "candidate_missing_rule",
        } <= set(record)


def test_resolved_survivor_dominance_forensics_reports_rule_outcomes(tmp_path):
    """Dominance forensics should evaluate label-blind rules after selection."""
    module = load_module(
        RESOLVED_SURVIVOR_DOMINANCE_FORENSICS_PATH,
        "resolved_survivor_dominance_forensics",
    )

    assert (
        module.main(
            [
                "--start-anchor",
                "11",
                "--max-anchor",
                "2000",
                "--candidate-bound",
                "64",
                "--witness-bound",
                "97",
                "--output-dir",
                str(tmp_path),
            ]
        )
        == 0
    )

    records_path = tmp_path / "resolved_survivor_dominance_forensics_records.jsonl"
    summary_path = tmp_path / "resolved_survivor_dominance_forensics_summary.json"
    assert records_path.exists()
    assert summary_path.exists()
    assert b"\r\n" not in records_path.read_bytes()
    assert b"\r\n" not in summary_path.read_bytes()

    records = [
        json.loads(line)
        for line in records_path.read_text(encoding="utf-8").splitlines()
    ]
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["mode"] == "offline_resolved_survivor_dominance_forensics"
    assert summary["boundary_law_005_status"] == "not_approved"
    assert summary["true_boundary_rejected_count"] == 0
    assert "candidate_dominance_observable_counts" in summary
    assert "dominance_rule_reports" in summary

    report = summary["dominance_rule_reports"][0]
    assert {
        "rule_name",
        "eligible_for_pure_generation",
        "anchors_tested",
        "selection_made_count",
        "selection_correct_count",
        "selection_wrong_count",
        "selection_abstain_count",
        "selection_accuracy",
        "first_wrong_examples",
    } <= set(report)

    if records:
        record = records[0]
        assert {
            "anchor_p",
            "actual_boundary_offset_label",
            "resolved_survivor_offsets",
            "true_boundary_resolved_bool",
            "false_resolved_survivor_offsets",
            "resolved_survivor_count",
            "unresolved_count",
            "rejected_count",
            "resolved_survivor_metadata",
        } <= set(record)


def test_right_boundary_pressure_ceiling_probe_reports_candidate_ceiling(tmp_path):
    """Right-boundary ceiling probe should measure safety before any law claim."""
    module = load_module(
        RIGHT_BOUNDARY_PRESSURE_CEILING_PROBE_PATH,
        "right_boundary_pressure_ceiling_probe",
    )

    assert (
        module.main(
            [
                "--start-anchor",
                "11",
                "--max-anchor",
                "500",
                "--candidate-bound",
                "64",
                "--witness-bound",
                "97",
                "--output-dir",
                str(tmp_path),
            ]
        )
        == 0
    )

    rows_path = tmp_path / "right_boundary_pressure_ceiling_probe_rows.jsonl"
    summary_path = tmp_path / "right_boundary_pressure_ceiling_probe_summary.json"
    assert rows_path.exists()
    assert summary_path.exists()
    assert b"\r\n" not in rows_path.read_bytes()
    assert b"\r\n" not in summary_path.read_bytes()

    rows = [
        json.loads(line)
        for line in rows_path.read_text(encoding="utf-8").splitlines()
    ]
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert rows
    assert summary["mode"] == "offline_right_boundary_pressure_ceiling_probe"
    assert summary["boundary_law_005_status"] == "not_approved"
    assert summary["row_count"] == len(rows)
    assert "true_boundary_rejected_count" in summary
    assert "candidate_pressure_ceiling_count" in summary
    assert "average_candidate_count_before_ceiling" in summary
    assert "average_candidate_count_after_ceiling" in summary
    assert "unique_survivor_match_rate" in summary

    record = rows[0]
    assert {
        "anchor_p",
        "carrier_w",
        "carrier_d",
        "threat_T",
        "threat_type",
        "candidate_count_before_ceiling",
        "candidate_count_after_ceiling",
        "survivor_count",
        "unique_survivor",
        "actual_boundary_label_after_audit",
        "true_boundary_before_T",
        "true_boundary_rejected_count",
        "failure_reason",
    } <= set(record)


def test_right_boundary_pressure_ceiling_source_has_no_forbidden_helpers():
    """The candidate ceiling logic should not call classical boundary helpers."""
    source = RIGHT_BOUNDARY_PRESSURE_CEILING_PROBE_PATH.read_text(encoding="utf-8")
    ceiling_source = source.split("def certified_divisor_class", 1)[1].split(
        "def status_counts_below_ceiling",
        1,
    )[0]
    forbidden_tokens = (
        "isprime",
        "nextprime",
        "prevprime",
        "Miller",
        "divisor_count",
        "factorint",
        "gwr_dni_recursive_walk",
        "divisor_counts_segment",
    )
    for token in forbidden_tokens:
        assert token not in ceiling_source


def test_carrier_lock_condition_probe_reports_lock_candidates(tmp_path):
    """Carrier-lock search should separate safe ceilings from reset cases."""
    module = load_module(
        CARRIER_LOCK_CONDITION_PROBE_PATH,
        "carrier_lock_condition_probe",
    )

    assert (
        module.main(
            [
                "--start-anchor",
                "11",
                "--max-anchor",
                "500",
                "--candidate-bound",
                "64",
                "--witness-bound",
                "97",
                "--output-dir",
                str(tmp_path),
            ]
        )
        == 0
    )

    records_path = tmp_path / "carrier_lock_condition_probe_records.jsonl"
    summary_path = tmp_path / "carrier_lock_condition_probe_summary.json"
    assert records_path.exists()
    assert summary_path.exists()
    assert b"\r\n" not in records_path.read_bytes()
    assert b"\r\n" not in summary_path.read_bytes()

    records = [
        json.loads(line)
        for line in records_path.read_text(encoding="utf-8").splitlines()
    ]
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert records
    assert summary["mode"] == "offline_carrier_lock_condition_search"
    assert summary["boundary_law_005_status"] == "not_approved"
    assert summary["row_count"] == len(records)
    assert "candidate_lock_observable_counts" in summary
    assert "lock_rule_reports" in summary
    assert "candidate_lock_predicates" in summary

    report = summary["lock_rule_reports"][0]
    assert {
        "rule_name",
        "eligible_for_pure_generation",
        "cases_tested",
        "safe_ceiling_classified_count",
        "unsafe_reset_misclassified_as_safe",
        "abstain_count",
        "first_unsafe_examples",
        "passes_zero_wrong_gate",
        "status",
    } <= set(report)

    record = records[0]
    assert {
        "anchor_p",
        "carrier_w",
        "carrier_d",
        "carrier_family",
        "carrier_offset",
        "threat_t",
        "threat_d",
        "threat_offset",
        "threat_family",
        "actual_boundary_offset_label",
        "ceiling_safe_bool",
        "reset_bool",
        "previous_chamber_state",
        "carrier_ladder_legal_features",
        "square_pressure",
        "higher_divisor_pressure",
        "semiprime_pressure",
        "resolved_survivor_pair_status",
        "extension_preserves_carrier_bool",
        "extension_changes_carrier_bool",
    } <= set(record)


def test_carrier_lock_condition_source_has_no_forbidden_helpers():
    """Carrier-lock predicate logic should not call classical boundary helpers."""
    source = CARRIER_LOCK_CONDITION_PROBE_PATH.read_text(encoding="utf-8")
    predicate_source = source.split("def lock_rule_selects", 1)[1].split(
        "def lock_rule_report",
        1,
    )[0]
    forbidden_tokens = (
        "isprime",
        "nextprime",
        "prevprime",
        "Miller",
        "divisor_count",
        "factorint",
        "gwr_dni_recursive_walk",
        "divisor_counts_segment",
    )
    for token in forbidden_tokens:
        assert token not in predicate_source


def test_residual_after_locked_ceiling_forensics_reports_taxonomy(tmp_path):
    """Residual forensics should classify failures after the strongest safe mode."""
    module = load_module(
        RESIDUAL_AFTER_LOCKED_CEILING_FORENSICS_PATH,
        "residual_after_locked_ceiling_forensics",
    )

    assert (
        module.main(
            [
                "--start-anchor",
                "11",
                "--max-anchor",
                "500",
                "--candidate-bound",
                "64",
                "--witness-bound",
                "97",
                "--output-dir",
                str(tmp_path),
            ]
        )
        == 0
    )

    records_path = tmp_path / "residual_after_locked_ceiling_forensics_records.jsonl"
    summary_path = tmp_path / "residual_after_locked_ceiling_forensics_summary.json"
    assert records_path.exists()
    assert summary_path.exists()
    assert b"\r\n" not in records_path.read_bytes()
    assert b"\r\n" not in summary_path.read_bytes()

    records = [
        json.loads(line)
        for line in records_path.read_text(encoding="utf-8").splitlines()
    ]
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert records
    assert summary["mode"] == "offline_residual_after_locked_ceiling_forensics"
    assert summary["boundary_law_005_status"] == "not_approved"
    assert summary["carrier_lock_predicate"] == "unresolved_alternatives_before_threat"
    assert summary["row_count"] == len(records)
    assert "unique_resolved_survivor_count" in summary
    assert "true_boundary_rejected_count" in summary
    assert "true_boundary_unresolved_count" in summary
    assert "true_boundary_resolved_not_unique_count" in summary
    assert "average_resolved_survivor_count" in summary
    assert "average_unresolved_count" in summary
    assert "residual_failure_pattern_counts" in summary

    record = records[0]
    assert {
        "anchor_p",
        "actual_boundary_offset_label",
        "resolved_survivor_offsets",
        "unresolved_candidate_offsets",
        "rejected_candidate_offsets",
        "remaining_unresolved_reason_counts",
        "which_rule_pruned_what",
    } <= set(record)


def test_unresolved_alternative_closure_forensics_reports_taxonomy(tmp_path):
    """Unresolved-alternative forensics should classify live alternatives."""
    module = load_module(
        UNRESOLVED_ALTERNATIVE_CLOSURE_FORENSICS_PATH,
        "unresolved_alternative_closure_forensics",
    )

    assert (
        module.main(
            [
                "--start-anchor",
                "11",
                "--max-anchor",
                "500",
                "--candidate-bound",
                "64",
                "--witness-bound",
                "97",
                "--output-dir",
                str(tmp_path),
            ]
        )
        == 0
    )

    records_path = tmp_path / "unresolved_alternative_closure_forensics_records.jsonl"
    summary_path = tmp_path / "unresolved_alternative_closure_forensics_summary.json"
    assert records_path.exists()
    assert summary_path.exists()
    assert b"\r\n" not in records_path.read_bytes()
    assert b"\r\n" not in summary_path.read_bytes()

    records = [
        json.loads(line)
        for line in records_path.read_text(encoding="utf-8").splitlines()
    ]
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert records
    assert summary["mode"] == "offline_unresolved_alternative_closure_forensics"
    assert summary["boundary_law_005_status"] == "not_approved"
    assert summary["carrier_lock_predicate"] == "unresolved_alternatives_before_threat"
    assert "target_row_count" in summary
    assert "unresolved_alternative_count" in summary
    assert "before_true_count" in summary
    assert "after_true_count" in summary
    assert "single_hole_count" in summary
    assert "multi_hole_count" in summary
    assert "missing_witness_bound_distribution" in summary
    assert "unresolved_reason_pattern_counts" in summary

    record = records[0]
    assert {
        "anchor_p",
        "actual_boundary_offset_label",
        "unresolved_candidate_offset",
        "unresolved_candidate_relation_to_true_boundary",
        "unresolved_reason_counts",
        "unclosed_open_interior_count",
        "missing_witness_offsets",
        "candidate_has_gwr_carrier",
        "candidate_closure_status",
        "candidate_threat_status",
        "candidate_bound_position",
        "candidate_pruned_by_locked_ceiling_bool",
    } <= set(record)


def test_resolved_boundary_absorption_safety_probe_reports_rule_a_gate(tmp_path):
    """Absorption safety forensics should report Rule A wrongness metrics."""
    module = load_module(
        RESOLVED_BOUNDARY_ABSORPTION_SAFETY_PROBE_PATH,
        "resolved_boundary_absorption_safety_probe",
    )

    assert (
        module.main(
            [
                "--start-anchor",
                "11",
                "--max-anchor",
                "500",
                "--candidate-bound",
                "64",
                "--witness-bound",
                "97",
                "--output-dir",
                str(tmp_path),
            ]
        )
        == 0
    )

    records_path = tmp_path / "resolved_boundary_absorption_safety_probe_records.jsonl"
    summary_path = tmp_path / "resolved_boundary_absorption_safety_probe_summary.json"
    assert records_path.exists()
    assert summary_path.exists()
    assert b"\r\n" not in records_path.read_bytes()
    assert b"\r\n" not in summary_path.read_bytes()

    records = [
        json.loads(line)
        for line in records_path.read_text(encoding="utf-8").splitlines()
    ]
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert records
    assert summary["mode"] == "offline_resolved_boundary_absorption_safety_probe"
    assert summary["boundary_law_005_status"] == "not_approved"
    assert summary["prime_emission_status"] == "forbidden"
    assert summary["carrier_lock_predicate"] == "unresolved_alternatives_before_threat"
    assert "absorption_pattern_separates_true_from_false" in summary
    assert "rule_a_wrong_count" in summary
    assert "false_resolved_candidate_count" in summary
    assert "would_rule_a_select_false_resolved_survivor_count" in summary
    assert "would_rule_a_eliminate_true_boundary_candidate_count" in summary

    record = records[0]
    assert {
        "anchor_p",
        "actual_boundary_offset_label",
        "resolved_candidate_offset",
        "resolved_candidate_is_true_label",
        "later_unresolved_candidate_offsets",
        "resolved_candidate_wheel_open_inside_later_count",
        "absorbs_all_later_unresolved_bool",
        "carrier_identity_shared_with_later_bool",
        "extension_changes_carrier_bool",
        "extension_reset_evidence_bool",
        "would_rule_a_select_false_resolved_survivor",
        "would_rule_a_eliminate_true_boundary_candidate",
        "candidate_absorption_status",
        "failure_reason",
    } <= set(record)


def test_resolved_boundary_lock_separator_probe_reports_zero_wrong_gate(tmp_path):
    """Lock separator forensics should report zero-wrong candidate predicates."""
    module = load_module(
        RESOLVED_BOUNDARY_LOCK_SEPARATOR_PROBE_PATH,
        "resolved_boundary_lock_separator_probe",
    )

    assert (
        module.main(
            [
                "--start-anchor",
                "11",
                "--max-anchor",
                "500",
                "--candidate-bound",
                "64",
                "--witness-bound",
                "97",
                "--output-dir",
                str(tmp_path),
            ]
        )
        == 0
    )

    records_path = tmp_path / "resolved_boundary_lock_separator_probe_records.jsonl"
    summary_path = tmp_path / "resolved_boundary_lock_separator_probe_summary.json"
    assert records_path.exists()
    assert summary_path.exists()
    assert b"\r\n" not in records_path.read_bytes()
    assert b"\r\n" not in summary_path.read_bytes()

    records = [
        json.loads(line)
        for line in records_path.read_text(encoding="utf-8").splitlines()
    ]
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert records
    assert summary["mode"] == "offline_resolved_boundary_lock_separator_probe"
    assert summary["boundary_law_005_status"] == "not_approved"
    assert summary["prime_emission_status"] == "forbidden"
    assert summary["carrier_lock_predicate"] == "unresolved_alternatives_before_threat"
    assert "candidate_lock_separator_counts" in summary
    assert "zero_wrong_lock_candidates" in summary
    assert "lock_predicate_reports" in summary

    report = summary["lock_predicate_reports"][0]
    assert {
        "predicate_name",
        "eligible_for_pure_generation",
        "resolved_candidate_count",
        "locked_count",
        "true_locked_count",
        "false_locked_count",
        "selection_made_count",
        "selection_wrong_count",
        "selection_abstain_count",
        "passes_zero_wrong_gate",
        "first_false_examples",
    } <= set(report)

    record = records[0]
    assert {
        "anchor_p",
        "resolved_candidate_offset",
        "resolved_candidate_is_true_label",
        "actual_boundary_offset_label",
        "candidate_relation_to_true",
        "later_unresolved_candidate_count",
        "absorbs_all_later_unresolved_bool",
        "would_rule_a_eliminate_true_boundary_candidate",
        "carrier_offset",
        "carrier_divisor_count",
        "carrier_family",
        "carrier_same_as_true_candidate",
        "carrier_changes_when_extended_to_true_boundary",
        "carrier_changes_when_extended_to_next_unresolved",
        "extension_preserves_carrier",
        "extension_changes_carrier",
        "reset_evidence_between_candidate_and_true_boundary",
        "reset_evidence_between_candidate_and_later_unresolved",
        "higher_divisor_pressure_between_candidate_and_true",
        "higher_divisor_pressure_between_candidate_and_later_unresolved",
        "square_pressure_between_candidate_and_true",
        "semiprime_pressure_between_candidate_and_true",
        "single_hole_closure_used",
        "closure_support_count",
        "positive_witness_closure_count",
        "power_closure_count",
        "previous_chamber_pressure",
        "previous_gap_width_class",
    } <= set(record)


def test_higher_divisor_pressure_lock_hardening_reports_surface_matrix(tmp_path):
    """Higher-divisor lock hardening should report staged zero-wrong rows."""
    module = load_module(
        HIGHER_DIVISOR_PRESSURE_LOCK_HARDENING_PATH,
        "higher_divisor_pressure_lock_hardening",
    )

    assert (
        module.main(
            [
                "--start-anchor",
                "11",
                "--max-anchors",
                "500",
                "2000",
                "--candidate-bound",
                "64",
                "--witness-bound",
                "97",
                "--output-dir",
                str(tmp_path),
            ]
        )
        == 0
    )

    rows_path = tmp_path / "higher_divisor_pressure_lock_hardening_rows.jsonl"
    summary_path = tmp_path / "higher_divisor_pressure_lock_hardening_summary.json"
    assert rows_path.exists()
    assert summary_path.exists()
    assert b"\r\n" not in rows_path.read_bytes()
    assert b"\r\n" not in summary_path.read_bytes()

    rows = [
        json.loads(line)
        for line in rows_path.read_text(encoding="utf-8").splitlines()
    ]
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert len(rows) == 2
    assert summary["mode"] == "offline_higher_divisor_pressure_lock_hardening"
    assert summary["boundary_law_005_status"] == "not_approved"
    assert summary["prime_emission_status"] == "forbidden"
    assert "all_surfaces_zero_wrong" in summary

    record = rows[0]
    assert {
        "surface",
        "true_resolved_candidate_count",
        "false_resolved_candidate_count",
        "higher_divisor_pressure_lock_true_selected",
        "higher_divisor_pressure_lock_false_selected",
        "higher_divisor_pressure_lock_wrong_count",
        "selection_abstain_count",
        "selection_accuracy_when_made",
        "passes_zero_wrong_gate",
    } <= set(record)


def test_higher_divisor_pressure_lock_activation_profile_reports_regime(tmp_path):
    """Activation profile should report firing regimes without generation output."""
    module = load_module(
        HIGHER_DIVISOR_PRESSURE_LOCK_ACTIVATION_PROFILE_PATH,
        "higher_divisor_pressure_lock_activation_profile",
    )

    assert (
        module.main(
            [
                "--surfaces",
                "11..500",
                "1000..2000",
                "--candidate-bound",
                "64",
                "--witness-bound",
                "97",
                "--near-miss-limit",
                "20",
                "--output-dir",
                str(tmp_path),
            ]
        )
        == 0
    )

    activations_path = (
        tmp_path / "higher_divisor_pressure_lock_activation_records.jsonl"
    )
    near_misses_path = (
        tmp_path / "higher_divisor_pressure_lock_near_miss_records.jsonl"
    )
    summary_path = (
        tmp_path / "higher_divisor_pressure_lock_activation_profile_summary.json"
    )
    assert activations_path.exists()
    assert near_misses_path.exists()
    assert summary_path.exists()
    assert b"\r\n" not in activations_path.read_bytes()
    assert b"\r\n" not in near_misses_path.read_bytes()
    assert b"\r\n" not in summary_path.read_bytes()

    activations = [
        json.loads(line)
        for line in activations_path.read_text(encoding="utf-8").splitlines()
    ]
    near_misses = [
        json.loads(line)
        for line in near_misses_path.read_text(encoding="utf-8").splitlines()
    ]
    summary = json.loads(summary_path.read_text(encoding="utf-8"))

    assert summary["mode"] == "offline_higher_divisor_pressure_lock_activation_profile"
    assert summary["boundary_law_005_status"] == (
        "candidate_not_approved_for_generation"
    )
    assert summary["prime_emission_status"] == "forbidden"
    assert summary["wrong_count"] == 0
    assert summary["activation_count"] == len(activations)
    assert summary["safe_abstain_count"] > 0
    assert {
        "activation_by_gap_width",
        "activation_by_carrier_family",
        "activation_by_carrier_d",
        "activation_by_first_open_offset",
        "activation_by_previous_gap_width_class",
        "activation_by_pressure_signature",
        "activation_by_anchor_range_bucket",
        "non_unique_activation_count",
    } <= set(summary)

    if activations:
        activation = activations[0]
        assert {
            "anchor_p",
            "resolved_candidate_offset",
            "actual_boundary_offset_label",
            "candidate_bound",
            "witness_bound",
            "carrier_offset",
            "carrier_divisor_count",
            "carrier_family",
            "higher_divisor_pressure_signature",
            "higher_divisor_pressure_offset",
            "higher_divisor_pressure_d",
            "higher_divisor_pressure_offsets",
            "previous_gap_width",
            "previous_chamber_type",
            "first_open_offset",
            "single_hole_closure_used",
            "locked_absorption_count",
            "absorbed_unresolved_offsets",
            "nearest_unresolved_offsets_before_absorption",
            "unique_resolved_after_absorption_bool",
        } <= set(activation)

    assert near_misses
    near_miss = near_misses[0]
    assert {
        "anchor_p",
        "resolved_candidate_offset",
        "actual_boundary_offset_label",
        "why_lock_did_not_fire",
        "missing_pressure_component",
        "candidate_had_resolved_boundary_bool",
        "candidate_had_false_resolved_survivor_bool",
    } <= set(near_miss)


def test_lock_near_miss_profile_reports_adjacent_candidates(tmp_path):
    """Near-miss profile should classify abstentions without emission output."""
    module = load_module(
        LOCK_NEAR_MISS_PROFILE_PATH,
        "lock_near_miss_profile",
    )

    assert (
        module.main(
            [
                "--surfaces",
                "11..500",
                "1000..2000",
                "--candidate-bound",
                "64",
                "--witness-bound",
                "97",
                "--output-dir",
                str(tmp_path),
            ]
        )
        == 0
    )

    records_path = tmp_path / "lock_near_miss_profile_records.jsonl"
    summary_path = tmp_path / "lock_near_miss_profile_summary.json"
    assert records_path.exists()
    assert summary_path.exists()
    assert b"\r\n" not in records_path.read_bytes()
    assert b"\r\n" not in summary_path.read_bytes()

    records = [
        json.loads(line)
        for line in records_path.read_text(encoding="utf-8").splitlines()
    ]
    summary = json.loads(summary_path.read_text(encoding="utf-8"))

    assert summary["mode"] == "offline_higher_divisor_pressure_lock_near_miss_profile"
    assert summary["boundary_law_005_status"] == (
        "candidate_not_approved_for_generation"
    )
    assert summary["prime_emission_status"] == "forbidden"
    assert summary["near_miss_count"] == len(records)
    assert summary["near_miss_count"] > 0
    assert "near_miss_reason_counts" in summary
    assert "top_pressure_substitute_counts" in summary
    assert "candidate_adjacent_lock_families" in summary
    assert "best_next_lock_family_candidate" in summary

    record = records[0]
    assert {
        "anchor_p",
        "actual_boundary_offset_label",
        "resolved_candidate_offset",
        "later_unresolved_candidate_offsets",
        "false_resolved_survivor_offsets",
        "near_miss_reason_tags",
        "pressure_substitute_tags",
        "pressure_signature",
        "carrier_offset",
        "carrier_divisor_count",
        "carrier_family",
        "first_open_offset",
        "higher_divisor_before_candidate_offsets",
        "higher_divisor_after_unresolved_offsets",
        "square_pressure_between_candidate_and_later_unresolved",
        "semiprime_pressure_between_candidate_and_later_unresolved",
        "previous_gap_width_class",
    } <= set(record)


def test_previous_chamber_reset_lock_probe_reports_zero_wrong_candidates(tmp_path):
    """Previous-chamber probe should report predicate gates without emission."""
    module = load_module(
        PREVIOUS_CHAMBER_RESET_LOCK_PROBE_PATH,
        "previous_chamber_reset_lock_probe",
    )

    assert (
        module.main(
            [
                "--surfaces",
                "11..500",
                "1000..2000",
                "--candidate-bound",
                "64",
                "--witness-bound",
                "97",
                "--output-dir",
                str(tmp_path),
            ]
        )
        == 0
    )

    records_path = tmp_path / "previous_chamber_reset_lock_records.jsonl"
    summary_path = tmp_path / "previous_chamber_reset_lock_summary.json"
    assert records_path.exists()
    assert summary_path.exists()
    assert b"\r\n" not in records_path.read_bytes()
    assert b"\r\n" not in summary_path.read_bytes()

    records = [
        json.loads(line)
        for line in records_path.read_text(encoding="utf-8").splitlines()
    ]
    summary = json.loads(summary_path.read_text(encoding="utf-8"))

    assert summary["mode"] == "offline_previous_chamber_reset_lock_probe"
    assert summary["boundary_law_005_status"] == (
        "candidate_not_approved_for_generation"
    )
    assert summary["prime_emission_status"] == "forbidden"
    assert summary["candidate_count"] == len(records)
    assert "predicate_reports" in summary
    assert "zero_wrong_lock_candidates" in summary
    assert "best_lock_candidate" in summary
    assert "lock_wrong_count" in summary

    report = summary["predicate_reports"][0]
    assert {
        "predicate_name",
        "eligible_for_pure_generation",
        "lock_true_selected",
        "lock_false_selected",
        "lock_wrong_count",
        "lock_abstain_count",
        "selection_accuracy_when_made",
        "passes_zero_wrong_gate",
        "first_false_examples",
    } <= set(report)

    if records:
        record = records[0]
        assert {
            "anchor_p",
            "previous_left_prime",
            "previous_right_prime",
            "previous_gap_width",
            "previous_gwr_carrier_offset",
            "previous_gwr_carrier_d",
            "previous_gwr_carrier_family",
            "previous_first_open_offset",
            "previous_square_pressure",
            "previous_higher_divisor_pressure",
            "previous_semiprime_state",
            "resolved_candidate_offset",
            "resolved_candidate_is_true_label",
            "later_unresolved_count",
            "absorbs_all_later_unresolved_bool",
            "current_carrier_offset",
            "current_carrier_d",
            "current_carrier_family",
            "current_first_open_offset",
            "previous_to_current_transition_signature",
            "reset_lock_signature",
        } <= set(record)


def test_previous_to_current_carrier_shift_lock_hardening_reports_matrix(tmp_path):
    """Carrier shift hardening should report staged zero-wrong rows."""
    module = load_module(
        PREVIOUS_TO_CURRENT_CARRIER_SHIFT_LOCK_HARDENING_PATH,
        "previous_to_current_carrier_shift_lock_hardening",
    )

    assert (
        module.main(
            [
                "--surfaces",
                "11..500",
                "1000..2000",
                "--candidate-bound",
                "64",
                "--witness-bound",
                "97",
                "--output-dir",
                str(tmp_path),
            ]
        )
        == 0
    )

    rows_path = (
        tmp_path / "previous_to_current_carrier_shift_lock_hardening_rows.jsonl"
    )
    summary_path = (
        tmp_path / "previous_to_current_carrier_shift_lock_hardening_summary.json"
    )
    assert rows_path.exists()
    assert summary_path.exists()
    assert b"\r\n" not in rows_path.read_bytes()
    assert b"\r\n" not in summary_path.read_bytes()

    rows = [
        json.loads(line)
        for line in rows_path.read_text(encoding="utf-8").splitlines()
    ]
    summary = json.loads(summary_path.read_text(encoding="utf-8"))

    assert summary["mode"] == (
        "offline_previous_to_current_carrier_shift_lock_hardening"
    )
    assert summary["lock_name"] == "previous_to_current_carrier_shift_lock"
    assert summary["boundary_law_005b_status"] == (
        "lead_not_approved_for_generation"
    )
    assert summary["prime_emission_status"] == "forbidden"
    assert summary["surface_count"] == len(rows)
    assert "all_surfaces_zero_wrong" in summary
    assert "first_failed_surface" in summary

    record = rows[0]
    assert {
        "surface",
        "candidate_count",
        "true_candidate_count",
        "false_candidate_count",
        "previous_to_current_carrier_shift_lock_true_selected",
        "previous_to_current_carrier_shift_lock_false_selected",
        "previous_to_current_carrier_shift_lock_wrong_count",
        "selection_abstain_count",
        "selection_accuracy_when_made",
        "positive_selection_count",
        "passes_zero_wrong_gate",
    } <= set(record)


def test_boundary_law_005_family_integration_matrix_reports_modes(tmp_path):
    """005 family matrix should compare A/B modes without generator output."""
    module = load_module(
        BOUNDARY_LAW_005_FAMILY_INTEGRATION_MATRIX_PATH,
        "boundary_law_005_family_integration_matrix",
    )

    assert (
        module.main(
            [
                "--surfaces",
                "11..500",
                "1000..2000",
                "--candidate-bound",
                "64",
                "--witness-bound",
                "97",
                "--output-dir",
                str(tmp_path),
            ]
        )
        == 0
    )

    rows_path = tmp_path / "boundary_law_005_family_integration_matrix_rows.jsonl"
    summary_path = (
        tmp_path / "boundary_law_005_family_integration_matrix_summary.json"
    )
    assert rows_path.exists()
    assert summary_path.exists()
    assert b"\r\n" not in rows_path.read_bytes()
    assert b"\r\n" not in summary_path.read_bytes()

    rows = [
        json.loads(line)
        for line in rows_path.read_text(encoding="utf-8").splitlines()
    ]
    summary = json.loads(summary_path.read_text(encoding="utf-8"))

    assert summary["mode"] == "offline_boundary_law_005_family_integration_matrix"
    assert summary["boundary_law_005_status"] == (
        "candidate_family_not_approved_for_generation"
    )
    assert summary["prime_emission_status"] == "forbidden"
    assert summary["all_rows_hard_gate_passed"] is True
    assert {row["mode_name"] for row in rows} == {
        "005A_only",
        "005B_only",
        "005A_or_005B",
        "005A_then_005B",
    }

    record = rows[0]
    assert {
        "mode_name",
        "surface",
        "unique_resolved_survivor_count",
        "true_boundary_rejected_count",
        "absorption_correct_count",
        "absorption_wrong_count",
        "false_resolved_survivor_absorbed_count",
        "005A_applied_count",
        "005B_applied_count",
        "combined_applied_count",
        "hard_gate_passed",
    } <= set(record)


def test_boundary_law_005b_failure_autopsy_reproduces_anchor_3137(tmp_path):
    """005B failure autopsy should reproduce the false absorber at anchor 3137."""
    module = load_module(
        BOUNDARY_LAW_005B_FAILURE_AUTOPSY_PATH,
        "boundary_law_005b_failure_autopsy",
    )

    assert (
        module.main(
            [
                "--anchor",
                "3137",
                "--candidate-bound",
                "64",
                "--witness-bound",
                "97",
                "--output-dir",
                str(tmp_path),
            ]
        )
        == 0
    )

    record_path = tmp_path / "boundary_law_005b_failure_autopsy_record.json"
    summary_path = tmp_path / "boundary_law_005b_failure_autopsy_summary.json"
    assert record_path.exists()
    assert summary_path.exists()
    assert b"\r\n" not in record_path.read_bytes()
    assert b"\r\n" not in summary_path.read_bytes()

    record = json.loads(record_path.read_text(encoding="utf-8"))
    summary = json.loads(summary_path.read_text(encoding="utf-8"))

    assert summary["mode"] == "offline_boundary_law_005b_failure_autopsy"
    assert summary["failure_reproduced"] is True
    assert summary["boundary_law_005b_status"] == (
        "forensic_lead_not_absorption_rule"
    )
    assert summary["prime_emission_status"] == "forbidden"
    assert record["anchor_p"] == 3137
    assert record["false_absorber_offset"] == 12
    assert record["actual_boundary_offset"] == 26
    assert record["actual_boundary_offset"] in record[
        "absorption_targets_removed_by_false_absorber"
    ]
    assert record["candidate_boundary_witnesses"][
        "false_absorber_extended_positive_witness"
    ] == 47
    assert record["candidate_boundary_witnesses"][
        "actual_boundary_extended_positive_witness"
    ] is None
    assert record["what_hardening_probe_missed"][
        "hardening_target_row_conditions"
    ]["actual_boundary_resolved_before_absorption"] is False


def test_absorption_lock_action_population_audit_reports_coverage(tmp_path):
    """Action-population audit should compare hardening and integration sets."""
    module = load_module(
        ABSORPTION_LOCK_ACTION_POPULATION_AUDIT_PATH,
        "absorption_lock_action_population_audit",
    )

    assert (
        module.main(
            [
                "--surfaces",
                "11..500",
                "1000..2000",
                "--candidate-bound",
                "64",
                "--witness-bound",
                "97",
                "--output-dir",
                str(tmp_path),
            ]
        )
        == 0
    )

    rows_path = tmp_path / "absorption_lock_action_population_audit_rows.jsonl"
    summary_path = (
        tmp_path / "absorption_lock_action_population_audit_summary.json"
    )
    assert rows_path.exists()
    assert summary_path.exists()
    assert b"\r\n" not in rows_path.read_bytes()
    assert b"\r\n" not in summary_path.read_bytes()

    rows = [
        json.loads(line)
        for line in rows_path.read_text(encoding="utf-8").splitlines()
    ]
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    reports = {report["lock_name"]: report for report in summary["lock_reports"]}

    assert summary["mode"] == "offline_absorption_lock_action_population_audit"
    assert summary["boundary_law_005_status"] == "candidate_grade_only"
    assert summary["boundary_law_005a_status"] == (
        "candidate_grade_not_generator_approved"
    )
    assert summary["boundary_law_005b_status"] == "quarantined"
    assert summary["prime_emission_status"] == "forbidden"
    assert rows
    assert "005A_higher_divisor_pressure_lock" in reports
    assert "005B_previous_to_current_carrier_shift_lock" in reports
    assert reports["005A_higher_divisor_pressure_lock"][
        "missed_action_candidate_count"
    ] == 0
    assert reports["005B_previous_to_current_carrier_shift_lock"][
        "requires_hardening_expansion"
    ] is True

    record = rows[0]
    assert {
        "lock_name",
        "hardening_candidate_count",
        "integration_action_candidate_count",
        "missed_action_candidate_count",
        "missed_action_false_absorber_count",
        "missed_action_true_boundary_unresolved_count",
        "wrong_absorption_count",
        "requires_hardening_expansion",
        "first_missed_action_examples",
        "first_wrong_absorption_examples",
    } <= set(record)


def test_boundary_law_005a_stress_reports_hard_gate(tmp_path):
    """005A stress should report one-axis gate fields without emission output."""
    module = load_module(
        BOUNDARY_LAW_005A_STRESS_PATH,
        "boundary_law_005a_stress",
    )

    assert (
        module.main(
            [
                "--start-anchor",
                "11",
                "--max-anchor",
                "500",
                "--candidate-bound",
                "128",
                "--witness-bound",
                "97",
                "--output-dir",
                str(tmp_path),
            ]
        )
        == 0
    )

    rows_path = tmp_path / "boundary_law_005a_stress_rows.jsonl"
    summary_path = tmp_path / "boundary_law_005a_stress_summary.json"
    assert rows_path.exists()
    assert summary_path.exists()
    assert b"\r\n" not in rows_path.read_bytes()
    assert b"\r\n" not in summary_path.read_bytes()

    rows = [
        json.loads(line)
        for line in rows_path.read_text(encoding="utf-8").splitlines()
    ]
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    record = rows[0]

    assert summary["mode"] == "offline_boundary_law_005a_one_axis_stress"
    assert summary["stress_axis"] == "candidate_bound"
    assert summary["boundary_law_005_status"] == "candidate_grade_only"
    assert summary["prime_emission_status"] == "forbidden"
    assert summary["classical_labels_status"] == "external_audit_only"
    assert record["candidate_bound"] == 128
    assert record["witness_bound"] == 97
    assert {
        "candidate_bound",
        "witness_bound",
        "anchor_range",
        "true_boundary_rejected_count",
        "absorption_wrong_count",
        "false_resolved_survivor_absorbed_count",
        "unique_resolved_survivor_count",
        "005A_applied_count",
        "005A_correct_count",
        "005A_wrong_count",
        "safe_abstain_count",
        "action_population_match",
        "first_failure_example",
    } <= set(record)


def test_boundary_law_005a_refinement_probe_reports_split(tmp_path):
    """005A refinement probe should report selected and dropped activations."""
    module = load_module(
        BOUNDARY_LAW_005A_REFINEMENT_PROBE_PATH,
        "boundary_law_005a_refinement_probe",
    )

    assert (
        module.main(
            [
                "--surfaces",
                "11..500",
                "1000..2000",
                "--candidate-bound",
                "128",
                "--witness-bound",
                "127",
                "--output-dir",
                str(tmp_path),
            ]
        )
        == 0
    )

    activations_path = tmp_path / "boundary_law_005a_refinement_activations.jsonl"
    rows_path = tmp_path / "boundary_law_005a_refinement_rows.jsonl"
    summary_path = tmp_path / "boundary_law_005a_refinement_summary.json"
    assert activations_path.exists()
    assert rows_path.exists()
    assert summary_path.exists()
    assert b"\r\n" not in activations_path.read_bytes()
    assert b"\r\n" not in rows_path.read_bytes()
    assert b"\r\n" not in summary_path.read_bytes()

    rows = [
        json.loads(line)
        for line in rows_path.read_text(encoding="utf-8").splitlines()
    ]
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["mode"] == "offline_boundary_law_005a_refinement_probe"
    assert summary["boundary_law_005_status"] == "candidate_grade_only"
    assert summary["prime_emission_status"] == "forbidden"
    assert "all_surfaces_hard_passed" in summary
    assert {
        "activation_count",
        "selected_activation_count",
        "dropped_activation_count",
        "unique_success_count",
        "non_unique_activation_count",
        "wrong_count",
        "false_selected_count",
        "true_boundary_rejected_count",
        "absorption_wrong_count",
        "safe_abstain_count",
        "kept_unique_successes",
        "dropped_unique_successes",
        "kept_non_unique_activations",
        "dropped_non_unique_activations",
    } <= set(summary)

    record = rows[0]
    assert {
        "surface",
        "candidate_bound",
        "witness_bound",
        "activation_count",
        "selected_activation_count",
        "dropped_activation_count",
        "hard_passed",
        "first_failure_example",
    } <= set(record)


def test_offline_pgs_certificate_emitter_writes_and_audits(tmp_path):
    """Offline certificate emitter should not add pure emission behavior."""
    module = load_module(
        OFFLINE_PGS_CERTIFICATE_EMITTER_PATH,
        "offline_pgs_certificate_emitter",
    )

    assert (
        module.main(
            [
                "--start-anchor",
                "11",
                "--max-anchor",
                "500",
                "--candidate-bound",
                "128",
                "--witness-bound",
                "127",
                "--output-dir",
                str(tmp_path),
            ]
        )
        == 0
    )

    certificates_path = tmp_path / "offline_pgs_boundary_certificates.jsonl"
    summary_path = tmp_path / "offline_pgs_certificate_emitter_summary.json"
    assert certificates_path.exists()
    assert summary_path.exists()
    assert b"\r\n" not in certificates_path.read_bytes()
    assert b"\r\n" not in summary_path.read_bytes()

    certificates = [
        json.loads(line)
        for line in certificates_path.read_text(encoding="utf-8").splitlines()
    ]
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["rule_set"] == "005A-R"
    assert summary["certificate_count"] == len(certificates)
    assert summary["certificate_count"] > 0
    assert summary["pure_emission_approved"] is False
    assert summary["classical_audit_required"] is True
    assert summary["classical_audit_status"] == "NOT_RUN"

    certificate = certificates[0]
    assert certificate["record_type"] == "OFFLINE_PGS_BOUNDARY_CERTIFICATE"
    assert certificate["certificate_status"] == "CANDIDATE_CERTIFICATE"
    assert certificate["pure_emission_approved"] is False
    assert certificate["classical_audit_status"] == "NOT_RUN"
    assert certificate["rule_set"] == "005A-R"
    assert certificate["single_hole_closure_used"] is False
    assert {
        "anchor_p",
        "candidate_q_hat",
        "boundary_offset",
        "gwr_carrier",
        "gwr_carrier_offset",
        "gwr_carrier_d",
        "gwr_carrier_family",
        "higher_divisor_pressure_lock",
        "absorbed_alternative_count",
        "rejected_candidate_count",
        "unresolved_candidate_count",
        "resolved_survivor_count",
        "action_population_audited",
        "selection_wrong_count",
        "absorption_wrong_count",
        "true_boundary_rejected_count",
    } <= set(certificate)

    assert (
        module.main(
            [
                "--audit-certificates",
                str(certificates_path),
                "--output-dir",
                str(tmp_path),
            ]
        )
        == 0
    )
    audit_summary_path = tmp_path / "offline_pgs_certificate_audit_summary.json"
    assert audit_summary_path.exists()
    assert b"\r\n" not in audit_summary_path.read_bytes()
    audit_summary = json.loads(audit_summary_path.read_text(encoding="utf-8"))
    assert audit_summary["audited_count"] == len(certificates)
    assert audit_summary["confirmed_count"] == len(certificates)
    assert audit_summary["failed_count"] == 0
    assert "validation_backend" in audit_summary
