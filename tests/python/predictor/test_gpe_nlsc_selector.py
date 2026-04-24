"""Tests for the Milestone 2 GPE NLSC selector surface."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = ROOT / "src" / "python"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from z_band_prime_predictor import (
    GPENLSCSelectorState,
    InsufficientBoundarySelectorStateError,
    UndefinedNLSCSelectorBranchError,
    audit_d4_square_margin_collisions,
    audit_nlsc_branch_targets,
    oracle_nlsc_selector_row,
    select_d4_nlsc_boundary_prime,
    validate_d4_nlsc_selector,
)


def state_from_exact_d4_row(row) -> GPENLSCSelectorState:
    """Return the explicit development state for one exact d=4 row."""
    return GPENLSCSelectorState(
        threat_horizon=row.threat_horizon,
        square_ceiling_margin=row.square_ceiling_margin,
    )


def test_d4_nlsc_oracle_rows_include_square_threat_horizon():
    """Dominant d=4 rows should expose the exact S_+(w) ceiling."""
    row = oracle_nlsc_selector_row(13)

    assert row.current_prime == 13
    assert row.winner == 14
    assert row.winner_divisor_class == 4
    assert row.next_prime == 17
    assert row.threat_horizon == 25
    assert row.nlsc_margin == 8
    assert row.square_phase_utilization == (3, 11)
    assert row.square_ceiling_margin == 8


def test_d4_nlsc_selector_matches_exact_boundary_on_branch_examples():
    """The branch harness should compare selected boundaries to exact rows."""
    validations = validate_d4_nlsc_selector(
        current_primes=(13, 73),
        selector=select_d4_nlsc_boundary_prime,
        state_factory=state_from_exact_d4_row,
    )

    assert [item.observed_next_prime for item in validations] == [17, 79]
    assert all(item.matches_oracle for item in validations)
    assert all(item.inside_threat_horizon for item in validations)


def test_d4_nlsc_selector_fails_without_boundary_law_state():
    """The NLSC ceiling alone must not be treated as exact boundary selection."""
    row = oracle_nlsc_selector_row(13)

    try:
        select_d4_nlsc_boundary_prime(
            row.current_prime,
            GPENLSCSelectorState(threat_horizon=row.threat_horizon),
            row.winner,
            row.winner_divisor_class,
        )
    except InsufficientBoundarySelectorStateError as exc:
        assert "does not determine the square-ceiling margin" in str(exc)
    else:
        raise AssertionError("missing d=4 branch law state should fail explicitly")


def test_d4_nlsc_selector_uses_square_margin_not_boundary_offset():
    """The d=4 selector should derive q+ from S_+(w)-margin."""
    row = oracle_nlsc_selector_row(27851)

    assert row.winner == 27857
    assert row.next_prime == 27883
    assert row.threat_horizon == 27889
    assert row.square_ceiling_margin == 6

    observed = select_d4_nlsc_boundary_prime(
        row.current_prime,
        GPENLSCSelectorState(
            threat_horizon=row.threat_horizon,
            square_ceiling_margin=row.square_ceiling_margin,
        ),
        row.winner,
        row.winner_divisor_class,
    )

    assert observed == row.threat_horizon - row.square_ceiling_margin
    assert observed == row.next_prime


def test_d4_square_margin_audit_reports_reduced_state_collision():
    """The known reduced d=4 type should not be treated as a margin selector."""

    def reduced_key(row):
        return (
            row.current_prime % 30,
            row.winner_divisor_class,
            row.winner - row.current_prime,
        )

    collisions = audit_d4_square_margin_collisions((13, 73), reduced_key)

    assert len(collisions) == 1
    collision = collisions[0]
    assert collision.state_key == (13, 4, 1)
    assert collision.observed_margins == (8, 42)
    assert collision.row_count == 2
    assert collision.example_current_primes == (13, 73)


def test_nlsc_selector_reports_unresolved_non_d4_branch():
    """Non-d4 rows should remain explicit unresolved branch targets."""
    row = oracle_nlsc_selector_row(23)

    assert row.winner_divisor_class == 3
    assert row.threat_horizon is None

    try:
        select_d4_nlsc_boundary_prime(
            row.current_prime,
            GPENLSCSelectorState(),
            row.winner,
            row.winner_divisor_class,
        )
    except UndefinedNLSCSelectorBranchError as exc:
        assert "d(w)=3" in str(exc)
    else:
        raise AssertionError("non-d4 branch should fail as an unresolved selector target")


def test_nlsc_branch_audit_reports_observed_unresolved_targets():
    """The Milestone 2 audit should expose every observed branch target."""
    targets = audit_nlsc_branch_targets((3, 5, 11, 29))

    assert [target.winner_divisor_class for target in targets] == [3, 4, 6, 8]
    assert [target.observed_rows for target in targets] == [1, 1, 1, 1]
    assert not any(target.is_resolved for target in targets)

    d4_target = next(target for target in targets if target.winner_divisor_class == 4)
    assert d4_target.selector_name == "select_d4_nlsc_boundary_prime"
    assert d4_target.threat_horizon_name == "S_+(w)"
    assert "square-ceiling margin" in str(d4_target.unresolved_requirement)

    d3_target = next(target for target in targets if target.winner_divisor_class == 3)
    assert d3_target.selector_name is None
    assert d3_target.threat_horizon_name is None
    assert d3_target.unresolved_requirement == "define exact B_3(q, S, w)"
