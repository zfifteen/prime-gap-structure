"""Milestone 2 NLSC branch surface for the GWR-DNI prime engine.

NLSC gives an invariant threat horizon. For the dominant ``d(w)=4`` branch,
that horizon is the next prime-square threat:

    q^+ <= S_+(w)

This module keeps that ceiling separate from exact boundary selection. The
oracle row records the exact divisor-field boundary and its NLSC horizon for
validation. The branch selector only returns a boundary when explicit
NLSC-framed selector state determines the square-ceiling margin; otherwise it
fails directly.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Hashable, Iterable

from .gpe_boundary_selector import (
    GPEBoundarySelectorRow,
    InsufficientBoundarySelectorStateError,
    oracle_boundary_selector_row,
)
from .predictor import d4_closure_ceiling


class UndefinedNLSCSelectorBranchError(RuntimeError):
    """Raised when the requested winner class has no Milestone 2 branch law."""


@dataclass(frozen=True)
class GPENLSCSelectorState:
    """Explicit Milestone 2 selector state for one branch row."""

    threat_horizon: int | None = None
    square_ceiling_margin: int | None = None


@dataclass(frozen=True)
class GPENLSCSelectorRow:
    """One exact oracle row with its branch-specific NLSC horizon."""

    boundary: GPEBoundarySelectorRow
    branch: int
    threat_horizon: int | None

    @property
    def current_prime(self) -> int:
        """Return the left boundary prime."""
        return self.boundary.current_prime

    @property
    def winner(self) -> int:
        """Return the GWR winner."""
        return self.boundary.winner

    @property
    def winner_divisor_class(self) -> int:
        """Return the winner divisor class."""
        return self.boundary.winner_divisor_class

    @property
    def next_prime(self) -> int:
        """Return the exact right boundary prime."""
        return self.boundary.next_prime

    @property
    def boundary_offset(self) -> int:
        """Return the exact boundary offset from the current prime."""
        return self.boundary.boundary_offset

    @property
    def nlsc_margin(self) -> int | None:
        """Return the remaining distance from the exact boundary to the horizon."""
        if self.threat_horizon is None:
            return None
        return self.threat_horizon - self.next_prime

    @property
    def square_phase_utilization(self) -> tuple[int, int] | None:
        """Return the used and available distance from winner to square horizon."""
        if self.threat_horizon is None:
            return None
        return self.next_prime - self.winner, self.threat_horizon - self.winner

    @property
    def square_ceiling_margin(self) -> int | None:
        """Return the exact distance from the square horizon to the boundary."""
        if self.threat_horizon is None:
            return None
        return self.threat_horizon - self.next_prime


@dataclass(frozen=True)
class GPENLSCSelectorValidation:
    """One NLSC branch selector comparison row."""

    row: GPENLSCSelectorRow
    observed_next_prime: int

    @property
    def matches_oracle(self) -> bool:
        """Return whether the branch selector matched the exact boundary."""
        return self.observed_next_prime == self.row.next_prime

    @property
    def inside_threat_horizon(self) -> bool:
        """Return whether the selected boundary remains inside the NLSC horizon."""
        if self.row.threat_horizon is None:
            return False
        return self.observed_next_prime <= self.row.threat_horizon


@dataclass(frozen=True)
class GPENLSCBranchTarget:
    """One observed Milestone 2 branch and its current selector status."""

    winner_divisor_class: int
    observed_rows: int
    selector_name: str | None
    threat_horizon_name: str | None
    unresolved_requirement: str | None

    @property
    def is_resolved(self) -> bool:
        """Return whether the branch has an exact selector law."""
        return self.unresolved_requirement is None


@dataclass(frozen=True)
class GPED4SquareMarginCollision:
    """One reduced d=4 state key that maps to multiple square-ceiling margins."""

    state_key: tuple[Hashable, ...]
    observed_margins: tuple[int, ...]
    row_count: int
    example_current_primes: tuple[int, ...]


NLSCSelector = Callable[[int, GPENLSCSelectorState, int, int], int]
NLSCStateFactory = Callable[[GPENLSCSelectorRow], GPENLSCSelectorState]
D4SquareMarginStateKey = Callable[[GPENLSCSelectorRow], tuple[Hashable, ...]]


def oracle_nlsc_selector_row(current_prime: int) -> GPENLSCSelectorRow:
    """Return one exact branch row with the applicable NLSC threat horizon."""
    boundary = oracle_boundary_selector_row(current_prime)
    threat_horizon = None
    if boundary.winner_divisor_class == 4:
        threat_horizon = d4_closure_ceiling(boundary.winner)

    return GPENLSCSelectorRow(
        boundary=boundary,
        branch=boundary.winner_divisor_class,
        threat_horizon=threat_horizon,
    )


def select_d4_nlsc_boundary_prime(
    current_prime: int,
    state: GPENLSCSelectorState,
    winner: int,
    winner_divisor_class: int,
) -> int:
    """Return the d=4 branch boundary from square-ceiling margin state."""
    if winner_divisor_class != 4:
        raise UndefinedNLSCSelectorBranchError(
            f"no Milestone 2 selector branch is defined for d(w)={winner_divisor_class}"
        )
    if current_prime < 2:
        raise ValueError("current_prime must be at least 2")
    if winner <= current_prime:
        raise ValueError("winner must lie strictly to the right of current_prime")

    threat_horizon = state.threat_horizon
    if threat_horizon is None:
        raise InsufficientBoundarySelectorStateError(
            "d=4 NLSC selector state does not include S_+(w)"
        )
    if threat_horizon <= winner:
        raise ValueError("threat_horizon must lie strictly to the right of the winner")

    square_ceiling_margin = state.square_ceiling_margin
    if square_ceiling_margin is None:
        raise InsufficientBoundarySelectorStateError(
            "d=4 NLSC branch law does not determine the square-ceiling margin"
        )
    if square_ceiling_margin < 1:
        raise ValueError("square_ceiling_margin must be positive")

    next_prime = threat_horizon - square_ceiling_margin
    if next_prime <= winner:
        raise ValueError("selected boundary must lie strictly to the right of the winner")
    return next_prime


def validate_d4_nlsc_selector(
    current_primes: Iterable[int],
    selector: NLSCSelector,
    state_factory: NLSCStateFactory,
) -> list[GPENLSCSelectorValidation]:
    """Compare one d=4 branch selector against exact oracle rows."""
    rows: list[GPENLSCSelectorValidation] = []
    for current_prime in current_primes:
        row = oracle_nlsc_selector_row(current_prime)
        if row.winner_divisor_class != 4:
            raise UndefinedNLSCSelectorBranchError(
                f"validation row q={current_prime} has d(w)={row.winner_divisor_class}"
            )

        observed_next_prime = selector(
            row.current_prime,
            state_factory(row),
            row.winner,
            row.winner_divisor_class,
        )
        rows.append(
            GPENLSCSelectorValidation(
                row=row,
                observed_next_prime=observed_next_prime,
            )
        )
    return rows


def audit_nlsc_branch_targets(current_primes: Iterable[int]) -> list[GPENLSCBranchTarget]:
    """Return observed branch-selector targets on one validation surface."""
    observed_counts: dict[int, int] = {}
    for current_prime in current_primes:
        row = oracle_nlsc_selector_row(current_prime)
        branch = row.winner_divisor_class
        observed_counts[branch] = observed_counts.get(branch, 0) + 1

    targets: list[GPENLSCBranchTarget] = []
    for branch in sorted(observed_counts):
        if branch == 4:
            targets.append(
                GPENLSCBranchTarget(
                    winner_divisor_class=branch,
                    observed_rows=observed_counts[branch],
                    selector_name="select_d4_nlsc_boundary_prime",
                    threat_horizon_name="S_+(w)",
                    unresolved_requirement=(
                        "derive the square-ceiling margin S_+(w)-q^+ from rulebook state"
                    ),
                )
            )
            continue

        targets.append(
            GPENLSCBranchTarget(
                winner_divisor_class=branch,
                observed_rows=observed_counts[branch],
                selector_name=None,
                threat_horizon_name=None,
                unresolved_requirement=f"define exact B_{branch}(q, S, w)",
            )
        )
    return targets


def audit_d4_square_margin_collisions(
    current_primes: Iterable[int],
    state_key_factory: D4SquareMarginStateKey,
) -> list[GPED4SquareMarginCollision]:
    """Return reduced d=4 state keys that do not select one square margin."""
    groups: dict[tuple[Hashable, ...], list[GPENLSCSelectorRow]] = {}
    for current_prime in current_primes:
        row = oracle_nlsc_selector_row(current_prime)
        if row.winner_divisor_class != 4:
            raise UndefinedNLSCSelectorBranchError(
                f"margin audit row q={current_prime} has d(w)={row.winner_divisor_class}"
            )
        if row.square_ceiling_margin is None:
            raise InsufficientBoundarySelectorStateError(
                f"margin audit row q={current_prime} has no square-ceiling margin"
            )
        key = state_key_factory(row)
        groups.setdefault(key, []).append(row)

    collisions: list[GPED4SquareMarginCollision] = []
    for state_key, rows in groups.items():
        margins = tuple(sorted({int(row.square_ceiling_margin) for row in rows}))
        if len(margins) <= 1:
            continue
        collisions.append(
            GPED4SquareMarginCollision(
                state_key=state_key,
                observed_margins=margins,
                row_count=len(rows),
                example_current_primes=tuple(row.current_prime for row in rows[:4]),
            )
        )

    collisions.sort(key=lambda collision: (repr(collision.state_key), collision.observed_margins))
    return collisions


__all__ = [
    "GPENLSCBranchTarget",
    "GPED4SquareMarginCollision",
    "GPENLSCSelectorRow",
    "GPENLSCSelectorState",
    "GPENLSCSelectorValidation",
    "D4SquareMarginStateKey",
    "NLSCSelector",
    "NLSCStateFactory",
    "UndefinedNLSCSelectorBranchError",
    "audit_d4_square_margin_collisions",
    "audit_nlsc_branch_targets",
    "oracle_nlsc_selector_row",
    "select_d4_nlsc_boundary_prime",
    "validate_d4_nlsc_selector",
]
