#!/usr/bin/env python3
"""Probe direct DNI next-gap rule candidates across one or more detail CSVs."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = ROOT / "src" / "python"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from z_band_prime_composite_field import divisor_counts_segment


PREFIX_OFFSETS = tuple(range(1, 13))
EXTENDED_CUTOFF_MAP = {2: 44, 4: 60, 6: 60}
LOW_DIVISOR_CLASSES = (3, 4, 6, 8, 10, 12)
MISS_COMPONENT_KEYS = (
    "current_gap_width",
    "current_dmin",
    "current_peak_offset",
    "first_open_offset",
    "pred_d",
    "pred_offset",
)
SMALL_CUTOFF_RULE_KEYS = {
    "universal": [],
    "first_open_piecewise": ["first_open_offset"],
}


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description="Probe direct DNI next-gap rule candidates from transition CSVs.",
    )
    parser.add_argument(
        "--train-detail-csv",
        type=Path,
        required=True,
        help="Training detail CSV from gwr_dni_transition_probe.py.",
    )
    parser.add_argument(
        "--test-detail-csv",
        type=Path,
        required=True,
        help="Test detail CSV from gwr_dni_transition_probe.py.",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        required=True,
        help="Summary JSON output path.",
    )
    return parser


def load_rows(path: Path) -> list[dict[str, str]]:
    """Load rows from one transition detail CSV."""
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def prefix_values(row: dict[str, str]) -> list[int | None]:
    """Return the first twelve divisor counts with blanks represented as None."""
    values: list[int | None] = []
    for offset in PREFIX_OFFSETS:
        raw = row[f"prefix_d_{offset}"]
        values.append(None if raw == "" else int(raw))
    return values


def lexicographic_min_present(values: list[int | None]) -> tuple[str, str]:
    """Return the smallest present divisor class and its first offset."""
    present = [(offset + 1, value) for offset, value in enumerate(values) if value is not None]
    offset, divisor_count = min(present, key=lambda item: (item[1], item[0]))
    return str(divisor_count), str(offset)


def rule_min_first(row: dict[str, str]) -> tuple[str, str]:
    """Return the direct min-first prediction from the twelve-step prefix."""
    return lexicographic_min_present(prefix_values(row))


def rule_extended_min(
    row: dict[str, str],
) -> tuple[str, str]:
    """Return the extended lex-min prediction with gap-boundary detection.

    The rule works in two stages:

    Stage 1 (offsets 1..12):
        Compute the standard 12-prefix lexicographic minimum.

    Stage 2 (offsets 13..cutoff):
        If ALL 12 prefix values are present (the gap extends past offset 12)
        and the prefix minimum exceeds 3, scan offsets 13 through the
        piecewise cutoff bound.  Stop the scan at the first offset whose
        divisor count is 2 (a prime, marking the gap boundary).  Among
        composites encountered, update the lex-min when a strictly lower
        divisor count appears.

    The piecewise cutoff bounds by first_open_offset are:
        2 -> 44,  4 -> 60,  6 -> 60
    These are exact upper bounds on next_peak_offset observed on the
    combined 10^6 + 10^7 surface.
    """
    pv = prefix_values(row)
    rp = int(row["current_right_prime"])
    foo = int(row["first_open_offset"])
    cutoff = EXTENDED_CUTOFF_MAP.get(foo, 60)

    # Stage 1: 12-prefix lex-min
    best_d: int | None = None
    best_offset: int | None = None
    all_present = True
    for i, d in enumerate(pv):
        if d is None:
            all_present = False
            continue
        if best_d is None or d < best_d or (d == best_d and (i + 1) < best_offset):
            best_d = d
            best_offset = i + 1

    # Narrow gap: prefix already covers the full gap interior
    if not all_present:
        return str(best_d), str(best_offset)

    # Lowest composite divisor class; no scan can improve
    if best_d is not None and best_d <= 3:
        return str(best_d), str(best_offset)

    # Stage 2: extend the scan through offsets 13..cutoff
    if cutoff > 12:
        ext_lo = rp + 13
        ext_hi = rp + cutoff + 1
        extended_counts = divisor_counts_segment(ext_lo, ext_hi)
        for i in range(len(extended_counts)):
            d = int(extended_counts[i])
            offset = 13 + i
            if d == 2:  # prime = gap boundary
                break
            if d < best_d or (d == best_d and offset < best_offset):
                best_d = d
                best_offset = offset

    return str(best_d), str(best_offset)


def ambiguous_prefix12_summary(rows: list[dict[str, str]]) -> dict[str, object]:
    """Return how often the raw twelve-step prefix alone is target-ambiguous."""
    support: dict[tuple[str, ...], Counter[tuple[str, str]]] = defaultdict(Counter)
    for row in rows:
        signature = tuple(row[f"prefix_d_{offset}"] for offset in PREFIX_OFFSETS)
        support[signature][(row["next_dmin"], row["next_peak_offset"])] += 1

    ambiguous = [
        (signature, counter)
        for signature, counter in support.items()
        if len(counter) > 1
    ]
    examples = []
    for signature, counter in ambiguous[:10]:
        examples.append(
            {
                "prefix_signature": list(signature),
                "targets": {
                    f"{d}:{offset}": count for (d, offset), count in counter.items()
                },
            }
        )
    return {
        "ambiguous_signature_count": len(ambiguous),
        "ambiguous_observation_count": sum(sum(counter.values()) for _, counter in ambiguous),
        "examples": examples,
    }


def direct_rule_accuracy(rows: list[dict[str, str]]) -> dict[str, object]:
    """Return the exactness of the direct min-first rule on one row set."""
    exact = sum(
        1
        for row in rows
        if rule_min_first(row) == (row["next_dmin"], row["next_peak_offset"])
    )
    return {
        "exact_count": exact,
        "row_count": len(rows),
        "exact_rate": exact / len(rows),
    }


def extended_rule_accuracy(rows: list[dict[str, str]]) -> dict[str, object]:
    """Return the exactness of the extended lex-min rule on one row set."""
    exact = sum(
        1
        for row in rows
        if rule_extended_min(row) == (row["next_dmin"], row["next_peak_offset"])
    )
    return {
        "exact_count": exact,
        "row_count": len(rows),
        "exact_rate": exact / len(rows),
    }


def miss_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """Return rows where the direct min-first rule fails, annotated with its prediction."""
    misses: list[dict[str, str]] = []
    for row in rows:
        pred_d, pred_offset = rule_min_first(row)
        if (pred_d, pred_offset) == (row["next_dmin"], row["next_peak_offset"]):
            continue
        annotated = dict(row)
        annotated["pred_d"] = pred_d
        annotated["pred_offset"] = pred_offset
        misses.append(annotated)
    return misses


def hit_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """Return rows where the direct min-first rule is already exact."""
    hits: list[dict[str, str]] = []
    for row in rows:
        pred_d, pred_offset = rule_min_first(row)
        if (pred_d, pred_offset) == (row["next_dmin"], row["next_peak_offset"]):
            annotated = dict(row)
            annotated["pred_d"] = pred_d
            annotated["pred_offset"] = pred_offset
            hits.append(annotated)
    return hits


def bundle_is_exact(rows: list[dict[str, str]], keys: tuple[str, ...]) -> bool:
    """Return whether one state bundle determines the actual next-gap target exactly."""
    support: dict[tuple[str, ...], tuple[str, str]] = {}
    for row in rows:
        signature = tuple(row[key] for key in keys)
        target = (row["next_dmin"], row["next_peak_offset"])
        previous = support.get(signature)
        if previous is None:
            support[signature] = target
            continue
        if previous != target:
            return False
    return True


def analyze_exact_bundle(rows: list[dict[str, str]], keys: tuple[str, ...]) -> dict[str, object]:
    """Return exact-state metrics for one bundle already known to be exact."""
    distinct_signatures = {tuple(row[key] for key in keys) for row in rows}
    return {
        "state_keys": list(keys),
        "distinct_state_count": len(distinct_signatures),
        "unique_state_count": len(distinct_signatures),
        "unique_state_rate": 1.0,
        "unique_observation_count": len(rows),
        "unique_observation_share": 1.0,
        "max_target_support_size": 1,
    }


def minimal_exact_miss_bundle(rows: list[dict[str, str]]) -> dict[str, object] | None:
    """Return the smallest exact correction bundle on the direct-rule miss surface."""
    if not rows:
        return None
    best_bundle = None
    best_score: tuple[int, int, int] | None = None
    for cutoff in range(1, len(PREFIX_OFFSETS) + 1):
        prefix_keys = tuple(f"prefix_d_{offset}" for offset in range(1, cutoff + 1))
        score = (len(prefix_keys), cutoff, 0)
        if (best_score is None or score <= best_score) and bundle_is_exact(rows, prefix_keys):
            bundle = analyze_exact_bundle(rows, prefix_keys)
            bundle["component_keys"] = []
            bundle["prefix_cutoff"] = cutoff
            bundle["total_key_count"] = len(prefix_keys)
            best_score = score
            best_bundle = bundle
        for component_count in range(1, len(MISS_COMPONENT_KEYS) + 1):
            for component_keys in combinations(MISS_COMPONENT_KEYS, component_count):
                keys = component_keys + prefix_keys
                score = (len(keys), cutoff, component_count)
                if best_score is not None and score > best_score:
                    continue
                if not bundle_is_exact(rows, keys):
                    continue
                bundle = analyze_exact_bundle(rows, keys)
                bundle["component_keys"] = list(component_keys)
                bundle["prefix_cutoff"] = cutoff
                bundle["total_key_count"] = len(keys)
                if best_score is None or score < best_score:
                    best_score = score
                    best_bundle = bundle
    return best_bundle


def bundle_is_disjoint_from_hits(
    miss_rows_only: list[dict[str, str]],
    hit_rows_only: list[dict[str, str]],
    keys: tuple[str, ...],
) -> bool:
    """Return whether miss signatures for one bundle never appear on the hit surface."""
    hit_signatures = {tuple(row[key] for key in keys) for row in hit_rows_only}
    for row in miss_rows_only:
        signature = tuple(row[key] for key in keys)
        if signature in hit_signatures:
            return False
    return True


def minimal_disjoint_miss_bundle(rows: list[dict[str, str]]) -> dict[str, object] | None:
    """Return the smallest exact miss bundle whose signatures do not occur on hits."""
    miss_rows_only = miss_rows(rows)
    if not miss_rows_only:
        return None
    hit_rows_only = hit_rows(rows)
    best_bundle = None
    best_score: tuple[int, int, int] | None = None
    for cutoff in range(1, len(PREFIX_OFFSETS) + 1):
        prefix_keys = tuple(f"prefix_d_{offset}" for offset in range(1, cutoff + 1))
        score = (len(prefix_keys), cutoff, 0)
        if (
            (best_score is None or score <= best_score)
            and bundle_is_exact(miss_rows_only, prefix_keys)
            and bundle_is_disjoint_from_hits(miss_rows_only, hit_rows_only, prefix_keys)
        ):
            bundle = analyze_exact_bundle(miss_rows_only, prefix_keys)
            bundle["component_keys"] = []
            bundle["prefix_cutoff"] = cutoff
            bundle["total_key_count"] = len(prefix_keys)
            best_score = score
            best_bundle = bundle
        for component_count in range(1, len(MISS_COMPONENT_KEYS) + 1):
            for component_keys in combinations(MISS_COMPONENT_KEYS, component_count):
                keys = component_keys + prefix_keys
                score = (len(keys), cutoff, component_count)
                if best_score is not None and score > best_score:
                    continue
                if not bundle_is_exact(miss_rows_only, keys):
                    continue
                if not bundle_is_disjoint_from_hits(miss_rows_only, hit_rows_only, keys):
                    continue
                bundle = analyze_exact_bundle(miss_rows_only, keys)
                bundle["component_keys"] = list(component_keys)
                bundle["prefix_cutoff"] = cutoff
                bundle["total_key_count"] = len(keys)
                if best_score is None or score < best_score:
                    best_score = score
                    best_bundle = bundle
    return best_bundle


def miss_surface_summary(rows: list[dict[str, str]]) -> dict[str, object]:
    """Return exact summaries on the direct-rule miss surface."""
    misses = miss_rows(rows)
    actual_offset_counts = Counter(int(row["next_peak_offset"]) for row in misses)
    actual_d_counts = Counter(int(row["next_dmin"]) for row in misses)
    predicted_d_counts = Counter(int(row["pred_d"]) for row in misses)
    current_gap_width_counts = Counter(int(row["current_gap_width"]) for row in misses)
    examples = []
    for row in misses[:10]:
        examples.append(
            {
                "current_right_prime": int(row["current_right_prime"]),
                "current_gap_width": int(row["current_gap_width"]),
                "current_dmin": int(row["current_dmin"]),
                "current_peak_offset": int(row["current_peak_offset"]),
                "first_open_offset": int(row["first_open_offset"]),
                "pred_d": int(row["pred_d"]),
                "pred_offset": int(row["pred_offset"]),
                "actual_d": int(row["next_dmin"]),
                "actual_offset": int(row["next_peak_offset"]),
            }
        )
    return {
        "miss_count": len(misses),
        "miss_share": len(misses) / len(rows),
        "actual_offset_counts": {str(key): int(value) for key, value in actual_offset_counts.most_common(20)},
        "actual_d_counts": {str(key): int(value) for key, value in actual_d_counts.most_common(20)},
        "predicted_d_counts": {str(key): int(value) for key, value in predicted_d_counts.most_common(20)},
        "current_gap_width_counts": {str(key): int(value) for key, value in current_gap_width_counts.most_common(20)},
        "minimal_exact_miss_bundle": minimal_exact_miss_bundle(misses),
        "minimal_disjoint_miss_bundle": minimal_disjoint_miss_bundle(rows),
        "examples": examples,
    }


def transfer_summary(
    train_rows: list[dict[str, str]],
    test_rows: list[dict[str, str]],
    keys: list[str],
) -> dict[str, object]:
    """Return exact transfer coverage for one exact-state family."""
    mapping: dict[tuple[str, ...], tuple[str, str]] = {}
    for row in train_rows:
        mapping[tuple(row[key] for key in keys)] = (row["next_dmin"], row["next_peak_offset"])

    covered = 0
    exact = 0
    for row in test_rows:
        signature = tuple(row[key] for key in keys)
        target = mapping.get(signature)
        if target is None:
            continue
        covered += 1
        if target == (row["next_dmin"], row["next_peak_offset"]):
            exact += 1

    return {
        "state_keys": keys,
        "covered_count": covered,
        "coverage_share": covered / len(test_rows),
        "exact_on_covered_share": (exact / covered) if covered else None,
    }


def low_divisor_first_position_family_exact(rows: list[dict[str, str]]) -> bool:
    """Return whether low-divisor first-position features alone determine the target exactly."""
    support: dict[tuple[str, ...], tuple[str, str]] = {}
    for row in rows:
        values = prefix_values(row)
        signature_values = []
        for divisor_class in LOW_DIVISOR_CLASSES:
            offset = next(
                (index + 1 for index, value in enumerate(values) if value == divisor_class),
                None,
            )
            signature_values.append("" if offset is None else str(offset))
        signature = tuple(signature_values)
        target = (row["next_dmin"], row["next_peak_offset"])
        previous = support.get(signature)
        if previous is None:
            support[signature] = target
            continue
        if previous != target:
            return False
    return True


def exact_cutoff_rule_summary(
    rows: list[dict[str, str]],
    keys: list[str],
) -> dict[str, object]:
    """Return one exact next-peak cutoff law keyed by current-gap invariants."""
    support: dict[tuple[str, ...], int] = {}
    for row in rows:
        signature = tuple(row[key] for key in keys)
        peak = int(row["next_peak_offset"])
        previous = support.get(signature)
        if previous is None or peak > previous:
            support[signature] = peak

    mean_cutoff = sum(support[tuple(row[key] for key in keys)] for row in rows) / len(rows)
    summary = {
        "state_keys": keys,
        "state_count": len(support),
        "max_cutoff": max(support.values()),
        "mean_cutoff": mean_cutoff,
        "peak_covered_share": 1.0,
    }
    if len(support) <= 20:
        summary["cutoff_map"] = {
            "|".join(signature) if signature else "global": cutoff
            for signature, cutoff in sorted(support.items())
        }
    return summary


def cutoff_rule_summary(rows: list[dict[str, str]]) -> dict[str, object]:
    """Return compact exact cutoff laws for the next-gap DNI ladder."""
    usable_rows = [row for row in rows if row["current_peak_offset"]]
    return {
        name: exact_cutoff_rule_summary(usable_rows, keys)
        for name, keys in SMALL_CUTOFF_RULE_KEYS.items()
    }


def summarize(train_rows: list[dict[str, str]], test_rows: list[dict[str, str]]) -> dict[str, object]:
    """Return the direct-rule probe summary."""
    combined_rows = train_rows + test_rows
    families = {
        "width_prefix12": ["current_gap_width"] + [f"prefix_d_{offset}" for offset in PREFIX_OFFSETS],
        "peak_prefix12": ["current_peak_offset"] + [f"prefix_d_{offset}" for offset in PREFIX_OFFSETS],
        "first_open_peak_prefix11": [
            "first_open_offset",
            "current_peak_offset",
        ]
        + [f"prefix_d_{offset}" for offset in range(1, 12)],
    }
    return {
        "train_row_count": len(train_rows),
        "test_row_count": len(test_rows),
        "combined_row_count": len(combined_rows),
        "prefix12_ambiguity": ambiguous_prefix12_summary(combined_rows),
        "direct_min_first_accuracy": direct_rule_accuracy(combined_rows),
        "extended_min_accuracy": extended_rule_accuracy(combined_rows),
        "direct_rule_miss_surface": miss_surface_summary(combined_rows),
        "cutoff_rules": cutoff_rule_summary(combined_rows),
        "low_divisor_first_position_family_exact": low_divisor_first_position_family_exact(combined_rows),
        "transfer": {
            name: transfer_summary(train_rows, test_rows, keys)
            for name, keys in families.items()
        },
    }


def main(argv: list[str] | None = None) -> int:
    """Run the direct-rule probe and write a summary JSON artifact."""
    args = build_parser().parse_args(argv)
    summary = summarize(load_rows(args.train_detail_csv), load_rows(args.test_detail_csv))
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
