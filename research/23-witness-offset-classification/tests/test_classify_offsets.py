"""Unit tests for the witness-offset classifier.

The tests pin small GWR selections and the frozen decision rules. The 10^6
aggregate is the script's job, not a unit test.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "classify_offsets.py"


def load_classifier():
    spec = importlib.util.spec_from_file_location("classify_offsets_ch23", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def classifier():
    return load_classifier()


def test_divisor_walk_kinds_match_known_integers(classifier):
    counts, kinds = classifier.build_divisor_count_and_kind(50)
    assert counts[1] == 1
    assert counts[12] == 6
    assert counts[25] == 3
    assert counts[27] == 4
    assert counts[16] == 5
    assert counts[14] == 4
    assert counts[49] == 3
    assert counts[8] == 4
    assert counts[30] == 8
    assert kinds[25] == classifier.KIND_PRIME_SQUARE
    assert kinds[49] == classifier.KIND_PRIME_SQUARE
    assert kinds[27] == classifier.KIND_PRIME_CUBE
    assert kinds[8] == classifier.KIND_PRIME_CUBE
    assert kinds[16] == classifier.KIND_HIGHER_PRIME_POWER
    assert kinds[14] == classifier.KIND_TWO_PRIME_PRODUCT
    assert kinds[35] == classifier.KIND_TWO_PRIME_PRODUCT
    assert kinds[12] == classifier.KIND_OTHER
    assert kinds[30] == classifier.KIND_OTHER
    assert kinds[11] == classifier.KIND_OTHER


def test_gap_after_11_selects_12(classifier):
    witnesses = classifier.select_gap_witnesses(20)
    first = witnesses[0]
    assert first.left_prime == 11
    assert first.right_prime == 13
    assert first.selected_witness == 12
    assert first.offset == 1
    assert first.divisor_count == 6
    assert first.winner_kind == classifier.KIND_OTHER


def test_gap_after_23_selects_the_prime_square_25(classifier):
    witnesses = classifier.select_gap_witnesses(30)
    gap = next(witness for witness in witnesses if witness.left_prime == 23)
    assert gap.right_prime == 29
    assert gap.selected_witness == 25
    assert gap.offset == 2
    assert gap.divisor_count == 3
    assert gap.winner_kind == classifier.KIND_PRIME_SQUARE


def test_l1_dies_on_the_even_semiprime_at_offset_1(classifier):
    witnesses = classifier.select_gap_witnesses(20)
    decision = classifier.decide_l1(witnesses)
    assert decision.status == classifier.STATUS_KILLED
    assert decision.first_counterexample["left_prime"] == 13
    assert decision.first_counterexample["selected_witness"] == 14
    assert decision.first_counterexample["offset"] == 1


def test_l2_dies_when_the_low_band_holds_a_divisor_count_other_than_4(classifier):
    witnesses = classifier.select_gap_witnesses(20)
    decision = classifier.decide_l2(witnesses)
    assert decision.status == classifier.STATUS_KILLED
    assert decision.first_counterexample["left_prime"] == 11
    assert decision.first_counterexample["selected_witness"] == 12
    assert decision.counterexample_count >= 1


def test_synthetic_l2_overlap_is_a_kill(classifier):
    band_and_tau_six = classifier.GapWitness(
        left_prime=11,
        right_prime=13,
        selected_witness=12,
        offset=1,
        divisor_count=6,
        left_prime_mod_30=11,
        winner_kind=classifier.KIND_OTHER,
    )
    decision = classifier.decide_l2([band_and_tau_six])
    assert decision.status == classifier.STATUS_KILLED
    assert decision.counterexample_count == 1


def test_l3_abstains_when_every_extreme_is_a_small_fraction(classifier):
    extreme = classifier.GapWitness(
        left_prime=100,
        right_prime=160,
        selected_witness=121,
        offset=21,
        divisor_count=3,
        left_prime_mod_30=10,
        winner_kind=classifier.KIND_PRIME_SQUARE,
    )
    decision = classifier.decide_l3([extreme])
    assert decision.status == classifier.STATUS_ABSTAINED
    assert extreme.fractional_position_is_at_least_one_half() is False


def test_l3_survives_when_an_extreme_reaches_half_the_gap(classifier):
    extreme = classifier.GapWitness(
        left_prime=100,
        right_prime=140,
        selected_witness=121,
        offset=21,
        divisor_count=4,
        left_prime_mod_30=10,
        winner_kind=classifier.KIND_TWO_PRIME_PRODUCT,
    )
    decision = classifier.decide_l3([extreme])
    assert decision.status == classifier.STATUS_SURVIVED
    assert extreme.fractional_position_is_at_least_one_half() is True


def test_l3_dies_when_an_extreme_has_divisor_count_at_least_5(classifier):
    extreme = classifier.GapWitness(
        left_prime=100,
        right_prime=200,
        selected_witness=130,
        offset=30,
        divisor_count=6,
        left_prime_mod_30=10,
        winner_kind=classifier.KIND_OTHER,
    )
    decision = classifier.decide_l3([extreme])
    assert decision.status == classifier.STATUS_KILLED
    assert decision.first_counterexample["divisor_count"] == 6


def test_l3_abstains_when_the_regime_has_no_extreme(classifier):
    ordinary = classifier.GapWitness(
        left_prime=11,
        right_prime=13,
        selected_witness=12,
        offset=1,
        divisor_count=6,
        left_prime_mod_30=11,
        winner_kind=classifier.KIND_OTHER,
    )
    decision = classifier.decide_l3([ordinary])
    assert decision.status == classifier.STATUS_ABSTAINED


def test_l4_ignores_a_twin_gap_and_dies_on_a_synthetic_longer_chamber(classifier):
    twin = classifier.GapWitness(
        left_prime=29,
        right_prime=31,
        selected_witness=30,
        offset=1,
        divisor_count=8,
        left_prime_mod_30=29,
        winner_kind=classifier.KIND_OTHER,
    )
    ignored = classifier.decide_l4([twin])
    assert ignored.status == classifier.STATUS_UNRESOLVED

    longer = classifier.GapWitness(
        left_prime=59,
        right_prime=67,
        selected_witness=60,
        offset=1,
        divisor_count=12,
        left_prime_mod_30=29,
        winner_kind=classifier.KIND_OTHER,
    )
    killed = classifier.decide_l4([longer])
    assert killed.status == classifier.STATUS_KILLED
    assert killed.first_counterexample["left_prime"] == 59


def test_l4_survives_when_every_applicable_gap_leaves_the_multiple_of_30(classifier):
    moved = classifier.GapWitness(
        left_prime=89,
        right_prime=97,
        selected_witness=91,
        offset=2,
        divisor_count=4,
        left_prime_mod_30=29,
        winner_kind=classifier.KIND_TWO_PRIME_PRODUCT,
    )
    decision = classifier.decide_l4([moved])
    assert decision.status == classifier.STATUS_SURVIVED
    assert decision.counterexample_count == 0


def test_summary_names_the_square_envelope_without_using_it_as_an_l_predicate(
    classifier,
):
    witnesses = classifier.select_gap_witnesses(40)
    summary = classifier.summarize_witnesses(witnesses, 40)
    envelope = summary["square_envelope"]
    assert envelope["offset_threshold"] == 24
    assert envelope["failure_count"] == 0
    names = [row["name"] for row in summary["decisions"]]
    assert names == ["L1", "L2", "L3", "L4"]


def test_compact_scan_matches_the_witness_list_on_a_small_limit(classifier):
    limit = 1500
    witnesses = classifier.select_gap_witnesses(limit)
    scanned = classifier.scan_regime(limit)
    assert scanned["gap_count"] == len(witnesses)
    assert scanned["max_offset"] == max(witness.offset for witness in witnesses)
    list_l4 = classifier.decide_l4(witnesses)
    scanned_l4 = next(row for row in scanned["decisions"] if row["name"] == "L4")
    assert scanned_l4["status"] == list_l4.status
    assert scanned_l4["counterexample_count"] == list_l4.counterexample_count
    mechanism = scanned["l4_neighbor_mechanism"]
    assert (
        mechanism["saved_by_p_plus_2"]
        + mechanism["saved_by_p_plus_3"]
        + mechanism["saved_later"]
        + mechanism["multiple_of_30_is_the_witness"]
        == scanned["l4_applicable_count"]
    )


def test_empty_interior_is_rejected(classifier):
    with pytest.raises(classifier.WitnessTableError):
        classifier.leftmost_minimum_divisor([0, 1, 2, 2], 2, 3)
