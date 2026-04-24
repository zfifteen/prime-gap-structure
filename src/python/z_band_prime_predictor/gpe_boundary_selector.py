"""Milestone 1 boundary-selector contract for the GWR-DNI prime engine.

This module replaces the false closure rule ``winner + 1`` with the narrow
selector interface required by the GPE roadmap:

    q^+ = B(q, S, w, d(w))

Milestone 1 does not claim that the selector law is solved. The selector either
receives enough explicit state to emit the exact boundary or it fails
explicitly. The exact divisor-field oracle remains external to the runtime
selector path and is used here only to build validation rows.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

from .gwr_boundary_walk import gwr_next_gap_profile


class InsufficientBoundarySelectorStateError(RuntimeError):
    """Raised when the current selector state cannot determine the boundary."""


@dataclass(frozen=True)
class GPEBoundarySelectorState:
    """Minimal milestone-1 selector state.

    ``boundary_offset`` is optional on purpose. When it is missing, the
    selector must fail explicitly instead of inventing a closure rule.
    """

    boundary_offset: int | None = None


@dataclass(frozen=True)
class GPEBoundarySelectorRow:
    """One exact oracle row for milestone-1 boundary-selector validation."""

    current_prime: int
    winner: int
    winner_divisor_class: int
    next_prime: int
    boundary_offset: int


@dataclass(frozen=True)
class GPEBoundarySelectorValidation:
    """One selector-vs-oracle comparison row."""

    row: GPEBoundarySelectorRow
    observed_next_prime: int

    @property
    def matches_oracle(self) -> bool:
        """Return whether the selector matched the exact boundary."""
        return self.observed_next_prime == self.row.next_prime


BoundarySelector = Callable[[int, GPEBoundarySelectorState, int, int], int]
BoundaryStateFactory = Callable[[GPEBoundarySelectorRow], GPEBoundarySelectorState]


def oracle_boundary_selector_row(current_prime: int) -> GPEBoundarySelectorRow:
    """Return the exact selector row for one known prime anchor."""
    profile = gwr_next_gap_profile(current_prime)
    winner_offset = profile["winner_offset"]
    winner_divisor_class = profile["winner_d"]
    if winner_offset is None or winner_divisor_class is None:
        raise ValueError(f"prime {current_prime} has no interior winner row")

    boundary_offset = int(profile["gap_boundary_offset"])
    winner = current_prime + int(winner_offset)
    return GPEBoundarySelectorRow(
        current_prime=current_prime,
        winner=winner,
        winner_divisor_class=int(winner_divisor_class),
        next_prime=int(profile["next_prime"]),
        boundary_offset=boundary_offset,
    )


def select_next_boundary_prime(
    current_prime: int,
    state: GPEBoundarySelectorState,
    winner: int,
    winner_divisor_class: int,
) -> int:
    """Return the exact next boundary prime from explicit selector state.

    This milestone-1 selector has one deterministic path:

    - validate the selector inputs;
    - read the explicit boundary offset from state;
    - fail if that offset is absent or does not lie strictly to the right of
      the winner.
    """

    if current_prime < 2:
        raise ValueError("current_prime must be at least 2")
    if winner <= current_prime:
        raise ValueError("winner must lie strictly to the right of current_prime")
    winner_offset = winner - current_prime
    if winner_divisor_class < 3:
        raise ValueError("winner_divisor_class must describe one composite winner")

    boundary_offset = state.boundary_offset
    if boundary_offset is None:
        raise InsufficientBoundarySelectorStateError(
            "boundary selector state does not determine the exact boundary offset"
        )
    if boundary_offset <= winner_offset:
        raise ValueError("boundary_offset must lie strictly to the right of the winner")

    return current_prime + boundary_offset


def validate_boundary_selector(
    current_primes: Iterable[int],
    selector: BoundarySelector,
    state_factory: BoundaryStateFactory,
) -> list[GPEBoundarySelectorValidation]:
    """Compare one selector against the exact oracle on a pinned prime surface."""
    rows: list[GPEBoundarySelectorValidation] = []
    for current_prime in current_primes:
        row = oracle_boundary_selector_row(current_prime)
        observed_next_prime = selector(
            row.current_prime,
            state_factory(row),
            row.winner,
            row.winner_divisor_class,
        )
        rows.append(
            GPEBoundarySelectorValidation(
                row=row,
                observed_next_prime=observed_next_prime,
            )
        )
    return rows


__all__ = [
    "BoundarySelector",
    "BoundaryStateFactory",
    "GPEBoundarySelectorRow",
    "GPEBoundarySelectorState",
    "GPEBoundarySelectorValidation",
    "InsufficientBoundarySelectorStateError",
    "oracle_boundary_selector_row",
    "select_next_boundary_prime",
    "validate_boundary_selector",
]
