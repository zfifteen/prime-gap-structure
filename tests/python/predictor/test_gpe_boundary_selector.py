"""Tests for the milestone-1 GPE boundary-selector contract."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = ROOT / "src" / "python"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from z_band_prime_predictor import (
    GPEBoundarySelectorState,
    InsufficientBoundarySelectorStateError,
    oracle_boundary_selector_row,
    select_next_boundary_prime,
    validate_boundary_selector,
)


def state_from_exact_boundary(
    row,
) -> GPEBoundarySelectorState:
    """Return the explicit milestone-1 state for one exact oracle row."""
    return GPEBoundarySelectorState(boundary_offset=row.boundary_offset)


def test_oracle_boundary_selector_rows_cover_milestone_1_regressions():
    """The pinned regression rows should match the milestone-1 contract table."""
    expected = {
        13: (14, 4, 17),
        23: (25, 3, 29),
        73: (74, 4, 79),
    }

    for current_prime, (winner, winner_divisor_class, next_prime) in expected.items():
        row = oracle_boundary_selector_row(current_prime)
        assert row.winner == winner
        assert row.winner_divisor_class == winner_divisor_class
        assert row.next_prime == next_prime


def test_boundary_selector_returns_exact_prime_on_milestone_1_examples():
    """The explicit selector state should recover the exact boundary rows."""
    validations = validate_boundary_selector(
        current_primes=(13, 23, 73),
        selector=select_next_boundary_prime,
        state_factory=state_from_exact_boundary,
    )

    assert [item.observed_next_prime for item in validations] == [17, 29, 79]
    assert all(item.matches_oracle for item in validations)


def test_boundary_selector_rejects_false_winner_plus_one_closure():
    """The blocker row q=23 must not collapse to winner + 1."""
    row = oracle_boundary_selector_row(23)
    observed = select_next_boundary_prime(
        row.current_prime,
        GPEBoundarySelectorState(boundary_offset=row.boundary_offset),
        row.winner,
        row.winner_divisor_class,
    )

    assert observed == 29
    assert observed != row.winner + 1


def test_boundary_selector_fails_explicitly_without_boundary_state():
    """Missing selector state should fail explicitly instead of guessing."""
    row = oracle_boundary_selector_row(23)

    try:
        select_next_boundary_prime(
            row.current_prime,
            GPEBoundarySelectorState(),
            row.winner,
            row.winner_divisor_class,
        )
    except InsufficientBoundarySelectorStateError as exc:
        assert "does not determine" in str(exc)
    else:
        raise AssertionError("missing selector state should raise explicit failure")
