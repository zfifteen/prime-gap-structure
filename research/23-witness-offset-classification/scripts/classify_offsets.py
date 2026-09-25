"""Classify GWR witness offsets by divisor type and left-prime residue.

The selected witness is the leftmost minimum-divisor integer inside a prime
gap. This module builds that witness from the divisor-count field, then
scores the four predicates frozen in CONTRACT.md.

Run from the repository root:

    python3 research/23-witness-offset-classification/scripts/classify_offsets.py --limit 1000000
"""

from __future__ import annotations

import argparse
import array
import json
import math
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Sequence

PUBLISHED_GAP_COUNT = 78_493
PUBLISHED_MAX_OFFSET = 48
PUBLISHED_MEDIAN_OFFSET = 2
PUBLISHED_LIMIT = 1_000_000

PREDICATE_L1 = (
    "If the winner kind is two_prime_product, the offset is in {2, 4, 6, 8, 10}."
)
PREDICATE_L2 = (
    "The set of gaps whose offset lies in {1, 2, 3, 4, 5} equals the set of "
    "gaps whose selected witness has divisor count 4."
)
PREDICATE_L3 = (
    "Offsets strictly above 20 are a trichotomy: killed when any has divisor "
    "count at least 5; survived on the regime when every one has divisor count "
    "at most 4 and at least one has fractional position at least 1/2; abstained "
    "when every one has divisor count at most 4 and fractional position below 1/2."
)
PREDICATE_L4 = (
    "If the left prime is greater than 5, congruent to 29 modulo 30, and the "
    "next prime is at least 4 larger, the offset is not 1."
)

L1_OFFSETS = frozenset({2, 4, 6, 8, 10})
L2_BAND = frozenset({1, 2, 3, 4, 5})
EXTREME_OFFSET_FLOOR = 20
SQUARE_ENVELOPE_OFFSET = 24
LEFT_PRIME_START = 10
WHEEL_RESIDUE = 29
WHEEL_MODULUS = 30

KIND_PRIME_SQUARE = "prime_square"
KIND_PRIME_CUBE = "prime_cube"
KIND_TWO_PRIME_PRODUCT = "two_prime_product"
KIND_HIGHER_PRIME_POWER = "higher_prime_power"
KIND_OTHER = "other"

STATUS_KILLED = "killed"
STATUS_SURVIVED = "survived_on_regime"
STATUS_ABSTAINED = "abstained"
STATUS_UNRESOLVED = "unresolved"


class WitnessTableError(ValueError):
    """The divisor-count table cannot support GWR selection on this limit."""


@dataclass(frozen=True)
class GapWitness:
    """One GWR selection inside a single prime gap."""

    left_prime: int
    right_prime: int
    selected_witness: int
    offset: int
    divisor_count: int
    left_prime_mod_30: int
    winner_kind: str

    def fractional_position_is_at_least_one_half(self) -> bool:
        """Return whether `(w - p) / (q - p)` is at least one half.

        The comparison stays on integers: `2 * offset >= gap`.
        """

        gap = self.right_prime - self.left_prime
        return 2 * self.offset >= gap


@dataclass(frozen=True)
class PredicateDecision:
    """Status of one frozen predicate on one list of witnesses."""

    name: str
    predicate: str
    status: str
    counterexample_count: int
    first_counterexample: dict[str, int | str] | None
    detail: str


def kind_from_divisor_walk(*, exponent: int, residual_divisor_count: int) -> str:
    """Read the winner kind off one smallest-prime-factor step.

    A residual divisor count of 1 means the integer is a pure prime power.
    Exponent 1 with a prime residual means a product of two distinct primes.
    """

    if exponent < 1:
        raise WitnessTableError("exponent must be positive")
    if residual_divisor_count == 1:
        if exponent == 2:
            return KIND_PRIME_SQUARE
        if exponent == 3:
            return KIND_PRIME_CUBE
        if exponent >= 4:
            return KIND_HIGHER_PRIME_POWER
        return KIND_OTHER
    if exponent == 1 and residual_divisor_count == 2:
        return KIND_TWO_PRIME_PRODUCT
    return KIND_OTHER


def build_divisor_count_and_kind(limit: int) -> tuple[list[int], list[str]]:
    """Return divisor counts and winner kinds for every integer from 0 through `limit`.

    The smallest-prime-factor table is the same walk `divisor_counts_up_to`
    uses in the divisor-count field. Kinds are labels on that walk. They are
    not a primality decision.
    """

    if limit < 2:
        raise WitnessTableError("limit must be at least 2")

    smallest_prime_factor = list(range(limit + 1))
    smallest_prime_factor[1] = 1
    root = int(limit**0.5)
    for candidate in range(2, root + 1):
        if smallest_prime_factor[candidate] != candidate:
            continue
        start = candidate * candidate
        for multiple in range(start, limit + 1, candidate):
            if smallest_prime_factor[multiple] == multiple:
                smallest_prime_factor[multiple] = candidate

    divisor_count = [0] * (limit + 1)
    winner_kind = [KIND_OTHER] * (limit + 1)
    divisor_count[1] = 1
    for integer in range(2, limit + 1):
        prime = smallest_prime_factor[integer]
        residual = integer
        exponent = 0
        while residual % prime == 0:
            residual //= prime
            exponent += 1
        divisor_count[integer] = divisor_count[residual] * (exponent + 1)
        winner_kind[integer] = kind_from_divisor_walk(
            exponent=exponent,
            residual_divisor_count=divisor_count[residual],
        )
    return divisor_count, winner_kind


def leftmost_minimum_divisor(
    divisor_count: Sequence[int], left_prime: int, right_prime: int
) -> int:
    """Return the leftmost interior integer whose divisor count is minimal."""

    if right_prime <= left_prime + 1:
        raise WitnessTableError(
            f"gap ({left_prime}, {right_prime}) has an empty interior"
        )
    minimum = min(divisor_count[n] for n in range(left_prime + 1, right_prime))
    for integer in range(left_prime + 1, right_prime):
        if divisor_count[integer] == minimum:
            return integer
    raise WitnessTableError(
        f"gap ({left_prime}, {right_prime}) has no minimum divisor count"
    )


def select_gap_witnesses(limit: int) -> list[GapWitness]:
    """Select the GWR witness for every prime gap with left prime in `[10, limit)`."""

    if limit <= LEFT_PRIME_START:
        raise WitnessTableError(
            f"limit must be greater than {LEFT_PRIME_START} so the regime is nonempty"
        )
    divisor_count, winner_kind = build_divisor_count_and_kind(limit)
    primes = [
        integer
        for integer in range(LEFT_PRIME_START, limit)
        if divisor_count[integer] == 2
    ]
    if len(primes) < 2:
        raise WitnessTableError(
            f"limit {limit} contains fewer than two primes at or above 10"
        )
    witnesses: list[GapWitness] = []
    for left_prime, right_prime in zip(primes, primes[1:]):
        selected = leftmost_minimum_divisor(divisor_count, left_prime, right_prime)
        witnesses.append(
            GapWitness(
                left_prime=left_prime,
                right_prime=right_prime,
                selected_witness=selected,
                offset=selected - left_prime,
                divisor_count=divisor_count[selected],
                left_prime_mod_30=left_prime % WHEEL_MODULUS,
                winner_kind=winner_kind[selected],
            )
        )
    return witnesses


def _record(witness: GapWitness) -> dict[str, int | str]:
    gap = witness.right_prime - witness.left_prime
    return {
        "left_prime": witness.left_prime,
        "right_prime": witness.right_prime,
        "selected_witness": witness.selected_witness,
        "offset": witness.offset,
        "divisor_count": witness.divisor_count,
        "left_prime_mod_30": witness.left_prime_mod_30,
        "winner_kind": witness.winner_kind,
        "gap": gap,
    }


def decide_l1(witnesses: Sequence[GapWitness]) -> PredicateDecision:
    """Score the frozen two-prime-product offset set."""

    failures = [
        witness
        for witness in witnesses
        if witness.winner_kind == KIND_TWO_PRIME_PRODUCT
        and witness.offset not in L1_OFFSETS
    ]
    first = _record(failures[0]) if failures else None
    status = STATUS_KILLED if failures else STATUS_SURVIVED
    detail = (
        f"{len(failures)} two_prime_product witnesses fall outside {{2, 4, 6, 8, 10}}"
        if failures
        else "every two_prime_product witness on this regime has offset in {2, 4, 6, 8, 10}"
    )
    return PredicateDecision(
        name="L1",
        predicate=PREDICATE_L1,
        status=status,
        counterexample_count=len(failures),
        first_counterexample=first,
        detail=detail,
    )


def decide_l2(witnesses: Sequence[GapWitness]) -> PredicateDecision:
    """Score set equality between the low offset band and divisor count 4."""

    failures = [
        witness
        for witness in witnesses
        if (witness.offset in L2_BAND) != (witness.divisor_count == 4)
    ]
    first = _record(failures[0]) if failures else None
    status = STATUS_KILLED if failures else STATUS_SURVIVED
    detail = (
        "the low band and the divisor-count-4 set differ"
        if failures
        else "the low band equals the divisor-count-4 set on this regime"
    )
    return PredicateDecision(
        name="L2",
        predicate=PREDICATE_L2,
        status=status,
        counterexample_count=len(failures),
        first_counterexample=first,
        detail=detail,
    )


def decide_l3(witnesses: Sequence[GapWitness]) -> PredicateDecision:
    """Score the extreme-offset trichotomy frozen in the contract."""

    extremes = [
        witness for witness in witnesses if witness.offset > EXTREME_OFFSET_FLOOR
    ]
    if not extremes:
        return PredicateDecision(
            name="L3",
            predicate=PREDICATE_L3,
            status=STATUS_ABSTAINED,
            counterexample_count=0,
            first_counterexample=None,
            detail="this regime has no offset above 20",
        )
    high_tau = [witness for witness in extremes if witness.divisor_count >= 5]
    if high_tau:
        return PredicateDecision(
            name="L3",
            predicate=PREDICATE_L3,
            status=STATUS_KILLED,
            counterexample_count=len(high_tau),
            first_counterexample=_record(high_tau[0]),
            detail=(
                "an offset above 20 has divisor count at least 5, so the "
                "envelope is wider than the first divisor-count-4 arrival"
            ),
        )
    large_fraction = [
        witness
        for witness in extremes
        if witness.fractional_position_is_at_least_one_half()
    ]
    if large_fraction:
        return PredicateDecision(
            name="L3",
            predicate=PREDICATE_L3,
            status=STATUS_SURVIVED,
            counterexample_count=0,
            first_counterexample=_record(large_fraction[0]),
            detail=(
                f"{len(large_fraction)} extremes sit at fractional position "
                "at least 1/2, with divisor count at most 4"
            ),
        )
    return PredicateDecision(
        name="L3",
        predicate=PREDICATE_L3,
        status=STATUS_ABSTAINED,
        counterexample_count=0,
        first_counterexample=_record(extremes[0]),
        detail=(
            f"all {len(extremes)} offsets above 20 have divisor count at most 4 "
            "and fractional position below 1/2"
        ),
    )


def l4_antecedent_holds(witness: GapWitness) -> bool:
    """Return whether L4's wheel hypothesis applies to this gap."""

    return (
        witness.left_prime > 5
        and witness.left_prime_mod_30 == WHEEL_RESIDUE
        and witness.right_prime >= witness.left_prime + 4
    )


def decide_l4(witnesses: Sequence[GapWitness]) -> PredicateDecision:
    """Score the frozen claim that a multiple of 30 is not the witness in a longer chamber."""

    applicable = [witness for witness in witnesses if l4_antecedent_holds(witness)]
    if not applicable:
        return PredicateDecision(
            name="L4",
            predicate=PREDICATE_L4,
            status=STATUS_UNRESOLVED,
            counterexample_count=0,
            first_counterexample=None,
            detail="no gap on this regime meets the 29-mod-30 longer-chamber antecedent",
        )
    failures = [witness for witness in applicable if witness.offset == 1]
    if failures:
        return PredicateDecision(
            name="L4",
            predicate=PREDICATE_L4,
            status=STATUS_KILLED,
            counterexample_count=len(failures),
            first_counterexample=_record(failures[0]),
            detail=(
                f"{len(failures)} of {len(applicable)} applicable gaps keep offset 1"
            ),
        )
    return PredicateDecision(
        name="L4",
        predicate=PREDICATE_L4,
        status=STATUS_SURVIVED,
        counterexample_count=0,
        first_counterexample=None,
        detail=(f"all {len(applicable)} applicable gaps have offset different from 1"),
    )


def _median_offset(offsets: Sequence[int]) -> int | float:
    ordered = sorted(offsets)
    count = len(ordered)
    if count == 0:
        raise WitnessTableError("median requires at least one offset")
    middle = count // 2
    if count % 2 == 1:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2


def _histogram(witnesses: Sequence[GapWitness], key) -> dict[str, dict[str, int]]:
    grouped: dict[str, list[GapWitness]] = {}
    for witness in witnesses:
        grouped.setdefault(str(key(witness)), []).append(witness)
    summary: dict[str, dict[str, int]] = {}
    for label, group in sorted(grouped.items(), key=lambda item: item[0]):
        offsets = [witness.offset for witness in group]
        summary[label] = {
            "count": len(group),
            "min_offset": min(offsets),
            "max_offset": max(offsets),
        }
    return summary


def proved_ceiling(right_prime: int) -> int:
    """Return the proved compression ceiling at the right prime.

    `log` here is the natural log, matching `PROOF.md`. The ceiling uses
    `math.ceil` on that real value. On the `10^6` regime the integer offsets
    sit far below the ceiling, so a one-ulp log error cannot hide a breach.
    """

    if right_prime < 3:
        raise WitnessTableError("right prime must be at least 3")
    logarithmic = 0.5 * math.log(right_prime) ** 2
    return max(64, math.ceil(logarithmic))


def summarize_witnesses(
    witnesses: Sequence[GapWitness], limit: int
) -> dict[str, object]:
    """Build the JSON document for one regime."""

    if not witnesses:
        raise WitnessTableError("summary requires at least one witness")
    offsets = [witness.offset for witness in witnesses]
    maximum = max(witnesses, key=lambda witness: (witness.offset, -witness.left_prime))
    ceiling_breaches = [
        witness
        for witness in witnesses
        if witness.offset > proved_ceiling(witness.right_prime)
    ]
    decisions = [
        decide_l1(witnesses),
        decide_l2(witnesses),
        decide_l3(witnesses),
        decide_l4(witnesses),
    ]
    largest = sorted(
        witnesses, key=lambda witness: (-witness.offset, witness.left_prime)
    )[:8]
    applicable_l4 = [witness for witness in witnesses if l4_antecedent_holds(witness)]
    square_envelope_failures = [
        witness
        for witness in witnesses
        if witness.offset >= SQUARE_ENVELOPE_OFFSET
        and witness.winner_kind != KIND_PRIME_SQUARE
    ]
    median = _median_offset(offsets)
    sanity_ok = (
        limit == PUBLISHED_LIMIT
        and len(witnesses) == PUBLISHED_GAP_COUNT
        and maximum.offset == PUBLISHED_MAX_OFFSET
        and median == PUBLISHED_MEDIAN_OFFSET
        and not ceiling_breaches
    )
    return {
        "regime": f"left primes from {LEFT_PRIME_START} inclusive to {limit} exclusive",
        "limit": limit,
        "gap_count": len(witnesses),
        "max_offset": maximum.offset,
        "median_offset": median,
        "mean_offset_numerator": sum(offsets),
        "sanity_matches_chapter_22": sanity_ok,
        "published_comparison": {
            "gap_count": PUBLISHED_GAP_COUNT,
            "max_offset": PUBLISHED_MAX_OFFSET,
            "median_offset": PUBLISHED_MEDIAN_OFFSET,
            "limit": PUBLISHED_LIMIT,
        },
        "compression_ceiling_breaches": len(ceiling_breaches),
        "max_offset_witness": _record(maximum),
        "largest_offsets": [_record(witness) for witness in largest],
        "l4_applicable_count": len(applicable_l4),
        "l4_min_offset": min(
            (witness.offset for witness in applicable_l4), default=None
        ),
        "extreme_count_by_kind": _histogram(
            [witness for witness in witnesses if witness.offset > EXTREME_OFFSET_FLOOR],
            lambda witness: witness.winner_kind,
        ),
        "square_envelope": {
            "predicate": (
                "Every witness with offset at least 24 has winner kind prime_square. "
                "This sentence was read off the 10^6 kind table. A later limit is the test."
            ),
            "offset_threshold": SQUARE_ENVELOPE_OFFSET,
            "failure_count": len(square_envelope_failures),
            "first_failure": (
                _record(square_envelope_failures[0])
                if square_envelope_failures
                else None
            ),
        },
        "decisions": [asdict(decision) for decision in decisions],
        "by_winner_kind": _histogram(witnesses, lambda witness: witness.winner_kind),
        "by_divisor_count": _histogram(
            witnesses, lambda witness: witness.divisor_count
        ),
        "by_left_prime_mod_30": _histogram(
            witnesses, lambda witness: witness.left_prime_mod_30
        ),
        "offset_histogram": {
            str(offset): count for offset, count in sorted(Counter(offsets).items())
        },
    }


def build_compact_divisor_tables(limit: int) -> tuple[array.array, array.array]:
    """Return smallest-prime-factor and divisor-count tables as compact arrays.

    The tables match `build_divisor_count_and_kind`. The compact form is what
    makes a `10^8` pass fit in memory.
    """

    if limit < 2:
        raise WitnessTableError("limit must be at least 2")
    smallest_prime_factor = array.array("I", range(limit + 1))
    smallest_prime_factor[1] = 1
    root = int(limit**0.5)
    for candidate in range(2, root + 1):
        if smallest_prime_factor[candidate] != candidate:
            continue
        start = candidate * candidate
        for multiple in range(start, limit + 1, candidate):
            if smallest_prime_factor[multiple] == multiple:
                smallest_prime_factor[multiple] = candidate

    divisor_count = array.array("H", [0]) * (limit + 1)
    divisor_count[1] = 1
    for integer in range(2, limit + 1):
        prime = smallest_prime_factor[integer]
        residual = integer
        exponent = 0
        while residual % prime == 0:
            residual //= prime
            exponent += 1
        value = divisor_count[residual] * (exponent + 1)
        if value > 65535:
            raise WitnessTableError(
                f"divisor count of {integer} does not fit in 16 bits"
            )
        divisor_count[integer] = value
    return smallest_prime_factor, divisor_count


def kind_at(
    integer: int,
    smallest_prime_factor: array.array,
    divisor_count: array.array,
) -> str:
    """Read one integer's winner kind from the compact tables."""

    prime = smallest_prime_factor[integer]
    residual = integer
    exponent = 0
    while residual % prime == 0:
        residual //= prime
        exponent += 1
    return kind_from_divisor_walk(
        exponent=exponent,
        residual_divisor_count=int(divisor_count[residual]),
    )


def _median_from_histogram(offset_counts: Counter[int]) -> int | float:
    total = sum(offset_counts.values())
    if total == 0:
        raise WitnessTableError("median requires at least one offset")
    target_low = (total - 1) // 2
    target_high = total // 2
    seen = 0
    low_value = None
    high_value = None
    for offset, count in sorted(offset_counts.items()):
        next_seen = seen + count
        if low_value is None and next_seen > target_low:
            low_value = offset
        if high_value is None and next_seen > target_high:
            high_value = offset
            break
        seen = next_seen
    if low_value is None or high_value is None:
        raise WitnessTableError("histogram median missed its middle rank")
    if total % 2 == 1:
        return high_value
    return (low_value + high_value) / 2


def scan_regime(limit: int) -> dict[str, object]:
    """Score the frozen predicates without keeping every gap witness.

    Neighbor counts explain L4. `saved_by_p_plus_2` means `p + 2` already has
    fewer divisors than the multiple of 30 at `p + 1`. `saved_by_p_plus_3`
    means `p + 3` does, after `p + 2` does not. `saved_later` means both
    neighbors have at least as many divisors as `p + 1`, and a later interior
    integer carries the minimum.
    """

    if limit <= LEFT_PRIME_START:
        raise WitnessTableError(
            f"limit must be greater than {LEFT_PRIME_START} so the regime is nonempty"
        )
    smallest_prime_factor, divisor_count = build_compact_divisor_tables(limit)
    gap_count = 0
    max_offset = 0
    max_record: dict[str, int | str] | None = None
    offset_counts: Counter[int] = Counter()
    kind_counts: Counter[str] = Counter()
    kind_max: dict[str, int] = {}
    l1_failures = 0
    l1_first: dict[str, int | str] | None = None
    l2_failures = 0
    l2_first: dict[str, int | str] | None = None
    l3_high_tau = 0
    l3_high_tau_first: dict[str, int | str] | None = None
    l3_large_fraction = 0
    l3_large_fraction_first: dict[str, int | str] | None = None
    l3_extremes = 0
    l4_applicable = 0
    l4_failures = 0
    l4_failure_records: list[dict[str, int | str]] = []
    l4_min_offset: int | None = None
    saved_by_p_plus_2 = 0
    saved_by_p_plus_3 = 0
    saved_later = 0
    multiple_of_30_is_the_witness = 0
    saved_later_min_gap: int | None = None
    saved_later_example: dict[str, int | str] | None = None
    square_failures = 0
    square_first: dict[str, int | str] | None = None
    ceiling_breaches = 0
    previous_prime: int | None = None

    for integer in range(LEFT_PRIME_START, limit):
        if smallest_prime_factor[integer] != integer:
            continue
        if previous_prime is None:
            previous_prime = integer
            continue
        left_prime = previous_prime
        right_prime = integer
        previous_prime = integer
        gap_count += 1
        selected = left_prime + 1
        minimum = int(divisor_count[selected])
        multiplicity = 1
        for interior in range(left_prime + 2, right_prime):
            value = int(divisor_count[interior])
            if value < minimum:
                minimum = value
                selected = interior
                multiplicity = 1
            elif value == minimum:
                multiplicity += 1
        offset = selected - left_prime
        kind = kind_at(selected, smallest_prime_factor, divisor_count)
        record = {
            "left_prime": left_prime,
            "right_prime": right_prime,
            "selected_witness": selected,
            "offset": offset,
            "divisor_count": int(divisor_count[selected]),
            "left_prime_mod_30": left_prime % WHEEL_MODULUS,
            "winner_kind": kind,
            "gap": right_prime - left_prime,
            "minimum_multiplicity": multiplicity,
        }
        offset_counts[offset] += 1
        kind_counts[kind] += 1
        kind_max[kind] = max(kind_max.get(kind, 0), offset)
        if offset > max_offset:
            max_offset = offset
            max_record = record
        if offset > proved_ceiling(right_prime):
            ceiling_breaches += 1
        if kind == KIND_TWO_PRIME_PRODUCT and offset not in L1_OFFSETS:
            l1_failures += 1
            if l1_first is None:
                l1_first = record
        if (offset in L2_BAND) != (divisor_count[selected] == 4):
            l2_failures += 1
            if l2_first is None:
                l2_first = record
        if offset > EXTREME_OFFSET_FLOOR:
            l3_extremes += 1
            if divisor_count[selected] >= 5:
                l3_high_tau += 1
                if l3_high_tau_first is None:
                    l3_high_tau_first = record
            elif 2 * offset >= right_prime - left_prime:
                l3_large_fraction += 1
                if l3_large_fraction_first is None:
                    l3_large_fraction_first = record
        if offset >= SQUARE_ENVELOPE_OFFSET and kind != KIND_PRIME_SQUARE:
            square_failures += 1
            if square_first is None:
                square_first = record
        if (
            left_prime > 5
            and left_prime % WHEEL_MODULUS == WHEEL_RESIDUE
            and right_prime >= left_prime + 4
        ):
            l4_applicable += 1
            if l4_min_offset is None or offset < l4_min_offset:
                l4_min_offset = offset
            tau_at_multiple = int(divisor_count[left_prime + 1])
            tau_at_next = int(divisor_count[left_prime + 2])
            tau_at_third = int(divisor_count[left_prime + 3])
            if tau_at_next < tau_at_multiple:
                saved_by_p_plus_2 += 1
            elif tau_at_third < tau_at_multiple:
                saved_by_p_plus_3 += 1
            elif offset == 1:
                multiple_of_30_is_the_witness += 1
            else:
                saved_later += 1
                gap = right_prime - left_prime
                if saved_later_min_gap is None or gap < saved_later_min_gap:
                    saved_later_min_gap = gap
                    saved_later_example = record
            if offset == 1:
                l4_failures += 1
                if len(l4_failure_records) < 20:
                    l4_failure_records.append(record)

    if gap_count == 0 or max_record is None:
        raise WitnessTableError(f"limit {limit} produced no prime gaps")

    if l3_high_tau:
        l3_status = STATUS_KILLED
        l3_count = l3_high_tau
        l3_first = l3_high_tau_first
        l3_detail = (
            "an offset above 20 has divisor count at least 5, so the "
            "envelope is wider than the first divisor-count-4 arrival"
        )
    elif l3_extremes == 0:
        l3_status = STATUS_ABSTAINED
        l3_count = 0
        l3_first = None
        l3_detail = "this regime has no offset above 20"
    elif l3_large_fraction:
        l3_status = STATUS_SURVIVED
        l3_count = 0
        l3_first = l3_large_fraction_first
        l3_detail = (
            f"{l3_large_fraction} extremes sit at fractional position "
            "at least 1/2, with divisor count at most 4"
        )
    else:
        l3_status = STATUS_ABSTAINED
        l3_count = 0
        l3_first = None
        l3_detail = (
            f"all {l3_extremes} offsets above 20 have divisor count at most 4 "
            "and fractional position below 1/2"
        )

    if l4_applicable == 0:
        l4_status = STATUS_UNRESOLVED
        l4_detail = (
            "no gap on this regime meets the 29-mod-30 longer-chamber antecedent"
        )
    elif l4_failures:
        l4_status = STATUS_KILLED
        l4_detail = f"{l4_failures} of {l4_applicable} applicable gaps keep offset 1"
    else:
        l4_status = STATUS_SURVIVED
        l4_detail = f"all {l4_applicable} applicable gaps have offset different from 1"

    decisions = [
        {
            "name": "L1",
            "predicate": PREDICATE_L1,
            "status": STATUS_KILLED if l1_failures else STATUS_SURVIVED,
            "counterexample_count": l1_failures,
            "first_counterexample": l1_first,
            "detail": (
                f"{l1_failures} two_prime_product witnesses fall outside {{2, 4, 6, 8, 10}}"
                if l1_failures
                else "every two_prime_product witness on this regime has offset in {2, 4, 6, 8, 10}"
            ),
        },
        {
            "name": "L2",
            "predicate": PREDICATE_L2,
            "status": STATUS_KILLED if l2_failures else STATUS_SURVIVED,
            "counterexample_count": l2_failures,
            "first_counterexample": l2_first,
            "detail": (
                "the low band and the divisor-count-4 set differ"
                if l2_failures
                else "the low band equals the divisor-count-4 set on this regime"
            ),
        },
        {
            "name": "L3",
            "predicate": PREDICATE_L3,
            "status": l3_status,
            "counterexample_count": l3_count,
            "first_counterexample": l3_first,
            "detail": l3_detail,
        },
        {
            "name": "L4",
            "predicate": PREDICATE_L4,
            "status": l4_status,
            "counterexample_count": l4_failures,
            "first_counterexample": l4_failure_records[0]
            if l4_failure_records
            else None,
            "counterexamples": l4_failure_records,
            "detail": l4_detail,
        },
    ]
    median = _median_from_histogram(offset_counts)
    sanity_ok = (
        limit == PUBLISHED_LIMIT
        and gap_count == PUBLISHED_GAP_COUNT
        and max_offset == PUBLISHED_MAX_OFFSET
        and median == PUBLISHED_MEDIAN_OFFSET
        and ceiling_breaches == 0
    )
    return {
        "regime": f"left primes from {LEFT_PRIME_START} inclusive to {limit} exclusive",
        "limit": limit,
        "scanner": "compact",
        "gap_count": gap_count,
        "max_offset": max_offset,
        "median_offset": median,
        "sanity_matches_chapter_22": sanity_ok,
        "compression_ceiling_breaches": ceiling_breaches,
        "max_offset_witness": max_record,
        "l4_applicable_count": l4_applicable,
        "l4_min_offset": l4_min_offset,
        "l4_neighbor_mechanism": {
            "saved_by_p_plus_2": saved_by_p_plus_2,
            "saved_by_p_plus_3": saved_by_p_plus_3,
            "saved_later": saved_later,
            "multiple_of_30_is_the_witness": multiple_of_30_is_the_witness,
            "saved_later_min_gap": saved_later_min_gap,
            "saved_later_example": saved_later_example,
        },
        "square_envelope": {
            "predicate": (
                "Every witness with offset at least 24 has winner kind prime_square. "
                "This sentence was read off the 10^6 kind table. A later limit is the test."
            ),
            "offset_threshold": SQUARE_ENVELOPE_OFFSET,
            "failure_count": square_failures,
            "first_failure": square_first,
        },
        "by_winner_kind": {
            kind: {"count": kind_counts[kind], "max_offset": kind_max[kind]}
            for kind in sorted(kind_counts)
        },
        "decisions": decisions,
    }


def write_summary(limit: int, destination: Path) -> dict[str, object]:
    """Select witnesses, score predicates, and write one JSON summary."""

    witnesses = select_gap_witnesses(limit)
    summary = summarize_witnesses(witnesses, limit)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def main(argv: Sequence[str] | None = None) -> int:
    """Write the classification summary for one left-prime limit."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=PUBLISHED_LIMIT)
    parser.add_argument(
        "--scan",
        action="store_true",
        help="Use the compact scanner. Required for limits above 10^7.",
    )
    parser.add_argument(
        "--destination",
        type=Path,
        default=None,
        help="JSON path. Defaults to classification_<limit>.json beside this chapter.",
    )
    args = parser.parse_args(argv)
    chapter = Path(__file__).resolve().parents[1]
    destination = args.destination
    if destination is None:
        destination = chapter / f"classification_{args.limit}.json"
    if args.scan:
        summary = scan_regime(args.limit)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    else:
        summary = write_summary(args.limit, destination)
    decision_rows = summary["decisions"]
    if not isinstance(decision_rows, list):
        raise WitnessTableError("decisions summary is missing")
    printable_decisions = []
    for row in decision_rows:
        if not isinstance(row, dict):
            raise WitnessTableError("decision row is missing")
        printable_decisions.append(
            {
                "name": row["name"],
                "status": row["status"],
                "counterexample_count": row["counterexample_count"],
            }
        )
    print(f"Wrote {destination}")
    print(
        json.dumps(
            {
                "gap_count": summary["gap_count"],
                "max_offset": summary["max_offset"],
                "median_offset": summary["median_offset"],
                "sanity_matches_chapter_22": summary["sanity_matches_chapter_22"],
                "decisions": printable_decisions,
            },
            indent=2,
        )
    )
    if args.limit == PUBLISHED_LIMIT and not summary["sanity_matches_chapter_22"]:
        print("Sanity check against chapter 22 failed", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
