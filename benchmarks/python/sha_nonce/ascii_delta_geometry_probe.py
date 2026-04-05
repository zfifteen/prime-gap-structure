#!/usr/bin/env python3
"""Probe whether ASCII payload-delta geometry reorders survivors on the contract stream."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SRC_PYTHON = ROOT / "src" / "python"
if str(SRC_PYTHON) not in sys.path:
    sys.path.insert(0, str(SRC_PYTHON))

from z_band_prime_prefilter.prefilter import (  # noqa: E402
    CDLPrimeZBandPrefilter,
    DEFAULT_NAMESPACE,
    deterministic_odd_candidate,
    miller_rabin_fixed_bases,
)


DEFAULT_OUTPUT_DIR = Path(
    "benchmarks/output/python/sha_nonce/ascii_delta_geometry_probe"
)
DEFAULT_BIT_LENGTH = 2048
DEFAULT_START_INDEX = 100_000
DEFAULT_BATCH_SIZE = 1024
DEFAULT_BATCH_COUNT = 100
DEFAULT_PAYLOAD_COUNTER = 0
DEFAULT_PREFILTER_TARGET_COUNT = 3
DEFAULT_MR_TARGET_COUNT = 1


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Measure whether ASCII payload-delta geometry advances prefilter or "
            "fixed-base Miller-Rabin survivors on the contract stream."
        )
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for JSON artifacts.",
    )
    parser.add_argument(
        "--namespace",
        default=DEFAULT_NAMESPACE,
        help="Namespace used in the contract payload.",
    )
    parser.add_argument(
        "--bit-length",
        type=int,
        default=DEFAULT_BIT_LENGTH,
        help="Candidate bit length.",
    )
    parser.add_argument(
        "--start-index",
        type=int,
        default=DEFAULT_START_INDEX,
        help="First index in the probed interval.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=DEFAULT_BATCH_SIZE,
        help="Indices per reorder batch.",
    )
    parser.add_argument(
        "--batch-count",
        type=int,
        default=DEFAULT_BATCH_COUNT,
        help="Number of batches.",
    )
    parser.add_argument(
        "--payload-counter",
        type=int,
        default=DEFAULT_PAYLOAD_COUNTER,
        help="Counter lane used for payload-geometry features.",
    )
    parser.add_argument(
        "--prefilter-target-count",
        type=int,
        default=DEFAULT_PREFILTER_TARGET_COUNT,
        help="Number of prefilter survivors tracked per batch.",
    )
    parser.add_argument(
        "--mr-target-count",
        type=int,
        default=DEFAULT_MR_TARGET_COUNT,
        help="Number of Miller-Rabin survivors tracked per batch.",
    )
    return parser


def contract_payload(
    namespace: str,
    bit_length: int,
    index: int,
    counter: int,
) -> str:
    """Return one contract payload string."""
    return f"{namespace}:{bit_length}:{index}:{counter}"


def count_changed_digits(previous_index: int, current_index: int) -> int:
    """Return the changed-digit count after left-padding the shorter decimal form."""
    previous_text = str(previous_index)
    current_text = str(current_index)
    width = max(len(previous_text), len(current_text))
    previous_padded = previous_text.zfill(width)
    current_padded = current_text.zfill(width)
    return sum(
        previous_char != current_char
        for previous_char, current_char in zip(previous_padded, current_padded)
    )


def trailing_zero_depth(index: int) -> int:
    """Return the decimal trailing-zero depth of the current index."""
    depth = 0
    text = str(index)
    for char in reversed(text):
        if char != "0":
            break
        depth += 1
    return depth


def leftmost_delta_position(previous_payload: str, current_payload: str) -> int:
    """Return the leftmost differing character position in the full payload."""
    shared_length = min(len(previous_payload), len(current_payload))
    for position in range(shared_length):
        if previous_payload[position] != current_payload[position]:
            return position
    return shared_length


def compute_geometry_features(
    namespace: str,
    bit_length: int,
    previous_index: int,
    current_index: int,
    counter: int,
) -> dict[str, int | bool]:
    """Return the payload-delta geometry features for one contract-step increment."""
    previous_payload = contract_payload(namespace, bit_length, previous_index, counter)
    current_payload = contract_payload(namespace, bit_length, current_index, counter)
    return {
        "leftmost_delta_pos": leftmost_delta_position(previous_payload, current_payload),
        "changed_digits": count_changed_digits(previous_index, current_index),
        "trailing_zero_depth": trailing_zero_depth(current_index),
        "length_increased": len(str(current_index)) > len(str(previous_index)),
    }


def ordering_labels() -> tuple[str, ...]:
    """Return the deterministic ordering labels emitted by this probe."""
    return (
        "combined",
        "leftmost_first",
        "changed_digits_first",
        "trailing_zero_first",
        "length_increase_first",
    )


def ordering_key(label: str, row: dict[str, object]) -> tuple[object, ...]:
    """Return the deterministic sort key for one ordering label."""
    features = row["features"]
    assert isinstance(features, dict)
    leftmost = int(features["leftmost_delta_pos"])
    changed_digits = int(features["changed_digits"])
    zero_depth = int(features["trailing_zero_depth"])
    length_increased = bool(features["length_increased"])
    index = int(row["index"])

    if label == "combined":
        return (
            0 if length_increased else 1,
            leftmost,
            -changed_digits,
            -zero_depth,
            index,
        )
    if label == "leftmost_first":
        return (leftmost, index)
    if label == "changed_digits_first":
        return (-changed_digits, index)
    if label == "trailing_zero_first":
        return (-zero_depth, index)
    if label == "length_increase_first":
        return (0 if length_increased else 1, index)
    raise ValueError(f"Unknown ordering label: {label}")


def survivor_positions(
    rows: list[dict[str, object]],
    key: str,
    target_count: int,
) -> list[int]:
    """Return survivor positions, padded by the batch miss sentinel when needed."""
    positions: list[int] = []
    miss_position = len(rows) + 1
    for rank, row in enumerate(rows, start=1):
        if bool(row[key]):
            positions.append(rank)
            if len(positions) == target_count:
                return positions
    while len(positions) < target_count:
        positions.append(miss_position)
    return positions


def mean_position(positions: list[int]) -> float:
    """Return the arithmetic mean of integer positions."""
    return sum(positions) / len(positions)


def signature_key(features: dict[str, int | bool]) -> tuple[int, int, int, bool]:
    """Return the aggregation key for one feature set."""
    return (
        int(features["leftmost_delta_pos"]),
        int(features["changed_digits"]),
        int(features["trailing_zero_depth"]),
        bool(features["length_increased"]),
    )


def run_probe(
    namespace: str,
    bit_length: int,
    start_index: int,
    batch_size: int,
    batch_count: int,
    payload_counter: int,
    prefilter_target_count: int,
    mr_target_count: int,
) -> dict[str, object]:
    """Run the ASCII-delta geometry benchmark and return JSON-ready results."""
    if batch_size < 1:
        raise ValueError("batch_size must be at least 1")
    if batch_count < 1:
        raise ValueError("batch_count must be at least 1")
    if prefilter_target_count < 1:
        raise ValueError("prefilter_target_count must be at least 1")
    if mr_target_count < 1:
        raise ValueError("mr_target_count must be at least 1")
    if start_index < 1:
        raise ValueError("start_index must be at least 1")
    if payload_counter < 0:
        raise ValueError("payload_counter must be non-negative")

    start_time = time.perf_counter()
    prefilter = CDLPrimeZBandPrefilter(bit_length=bit_length, namespace=namespace)

    ordering_stats = {
        label: {
            "prefilter_baseline_mean_sum": 0.0,
            "prefilter_reordered_mean_sum": 0.0,
            "prefilter_gain_sum": 0.0,
            "prefilter_advantage_batch_count": 0,
            "mr_baseline_mean_sum": 0.0,
            "mr_reordered_mean_sum": 0.0,
            "mr_gain_sum": 0.0,
            "mr_advantage_batch_count": 0,
        }
        for label in ordering_labels()
    }
    feature_signature_counts: dict[
        tuple[int, int, int, bool],
        dict[str, int | float | bool]
    ] = {}
    batch_rows: list[dict[str, object]] = []
    total_indices = batch_size * batch_count
    total_prefilter_survivors = 0
    total_mr_survivors = 0

    previous_index = start_index - 1
    for batch_index in range(batch_count):
        rows: list[dict[str, object]] = []
        batch_start_index = start_index + batch_index * batch_size
        for offset in range(batch_size):
            index = batch_start_index + offset
            features = compute_geometry_features(
                namespace=namespace,
                bit_length=bit_length,
                previous_index=previous_index,
                current_index=index,
                counter=payload_counter,
            )
            candidate = deterministic_odd_candidate(
                bit_length,
                index,
                namespace=namespace,
            )
            prefilter_survivor = prefilter.is_prime_candidate(candidate)
            mr_survivor = (
                miller_rabin_fixed_bases(candidate) if prefilter_survivor else False
            )
            row = {
                "index": index,
                "features": features,
                "prefilter_survivor": prefilter_survivor,
                "mr_survivor": mr_survivor,
            }
            rows.append(row)
            previous_index = index
            total_prefilter_survivors += int(prefilter_survivor)
            total_mr_survivors += int(mr_survivor)

            key = signature_key(features)
            signature_row = feature_signature_counts.get(key)
            if signature_row is None:
                signature_row = {
                    "leftmost_delta_pos": key[0],
                    "changed_digits": key[1],
                    "trailing_zero_depth": key[2],
                    "length_increased": key[3],
                    "count": 0,
                    "prefilter_survivor_count": 0,
                    "mr_survivor_count": 0,
                }
                feature_signature_counts[key] = signature_row
            signature_row["count"] = int(signature_row["count"]) + 1
            signature_row["prefilter_survivor_count"] = (
                int(signature_row["prefilter_survivor_count"]) + int(prefilter_survivor)
            )
            signature_row["mr_survivor_count"] = (
                int(signature_row["mr_survivor_count"]) + int(mr_survivor)
            )

        baseline_prefilter_positions = survivor_positions(
            rows,
            key="prefilter_survivor",
            target_count=prefilter_target_count,
        )
        baseline_mr_positions = survivor_positions(
            rows,
            key="mr_survivor",
            target_count=mr_target_count,
        )
        baseline_prefilter_mean = mean_position(baseline_prefilter_positions)
        baseline_mr_mean = mean_position(baseline_mr_positions)

        ordering_rows: dict[str, object] = {}
        for label in ordering_labels():
            reordered_rows = sorted(rows, key=lambda row: ordering_key(label, row))
            reordered_prefilter_positions = survivor_positions(
                reordered_rows,
                key="prefilter_survivor",
                target_count=prefilter_target_count,
            )
            reordered_mr_positions = survivor_positions(
                reordered_rows,
                key="mr_survivor",
                target_count=mr_target_count,
            )
            reordered_prefilter_mean = mean_position(reordered_prefilter_positions)
            reordered_mr_mean = mean_position(reordered_mr_positions)
            prefilter_gain = baseline_prefilter_mean - reordered_prefilter_mean
            mr_gain = baseline_mr_mean - reordered_mr_mean

            stat_row = ordering_stats[label]
            stat_row["prefilter_baseline_mean_sum"] = (
                float(stat_row["prefilter_baseline_mean_sum"]) + baseline_prefilter_mean
            )
            stat_row["prefilter_reordered_mean_sum"] = (
                float(stat_row["prefilter_reordered_mean_sum"]) + reordered_prefilter_mean
            )
            stat_row["prefilter_gain_sum"] = (
                float(stat_row["prefilter_gain_sum"]) + prefilter_gain
            )
            stat_row["prefilter_advantage_batch_count"] = (
                int(stat_row["prefilter_advantage_batch_count"])
                + int(reordered_prefilter_mean < baseline_prefilter_mean)
            )
            stat_row["mr_baseline_mean_sum"] = (
                float(stat_row["mr_baseline_mean_sum"]) + baseline_mr_mean
            )
            stat_row["mr_reordered_mean_sum"] = (
                float(stat_row["mr_reordered_mean_sum"]) + reordered_mr_mean
            )
            stat_row["mr_gain_sum"] = float(stat_row["mr_gain_sum"]) + mr_gain
            stat_row["mr_advantage_batch_count"] = (
                int(stat_row["mr_advantage_batch_count"])
                + int(reordered_mr_mean < baseline_mr_mean)
            )
            ordering_rows[label] = {
                "prefilter_positions": reordered_prefilter_positions,
                "prefilter_mean_position": reordered_prefilter_mean,
                "prefilter_position_gain": prefilter_gain,
                "mr_positions": reordered_mr_positions,
                "mr_mean_position": reordered_mr_mean,
                "mr_position_gain": mr_gain,
            }

        batch_rows.append(
            {
                "batch_index": batch_index,
                "start_index": batch_start_index,
                "end_index": batch_start_index + batch_size - 1,
                "baseline": {
                    "prefilter_positions": baseline_prefilter_positions,
                    "prefilter_mean_position": baseline_prefilter_mean,
                    "mr_positions": baseline_mr_positions,
                    "mr_mean_position": baseline_mr_mean,
                },
                "orderings": ordering_rows,
            }
        )

    elapsed_seconds = time.perf_counter() - start_time
    ordering_summary_rows: list[dict[str, object]] = []
    for label in ordering_labels():
        stat_row = ordering_stats[label]
        ordering_summary_rows.append(
            {
                "label": label,
                "avg_prefilter_baseline_position": (
                    float(stat_row["prefilter_baseline_mean_sum"]) / batch_count
                ),
                "avg_prefilter_reordered_position": (
                    float(stat_row["prefilter_reordered_mean_sum"]) / batch_count
                ),
                "avg_prefilter_position_gain": (
                    float(stat_row["prefilter_gain_sum"]) / batch_count
                ),
                "prefilter_advantage_batch_share": (
                    int(stat_row["prefilter_advantage_batch_count"]) / batch_count
                ),
                "avg_mr_baseline_position": (
                    float(stat_row["mr_baseline_mean_sum"]) / batch_count
                ),
                "avg_mr_reordered_position": (
                    float(stat_row["mr_reordered_mean_sum"]) / batch_count
                ),
                "avg_mr_position_gain": float(stat_row["mr_gain_sum"]) / batch_count,
                "mr_advantage_batch_share": (
                    int(stat_row["mr_advantage_batch_count"]) / batch_count
                ),
            }
        )

    feature_signature_rows = sorted(
        (
            {
                **row,
                "share": int(row["count"]) / total_indices,
                "prefilter_survivor_rate": (
                    int(row["prefilter_survivor_count"]) / int(row["count"])
                ),
                "mr_survivor_rate": int(row["mr_survivor_count"]) / int(row["count"]),
            }
            for row in feature_signature_counts.values()
        ),
        key=lambda row: (-int(row["count"]), row["leftmost_delta_pos"]),
    )

    return {
        "metadata": {
            "namespace": namespace,
            "bit_length": bit_length,
            "start_index": start_index,
            "batch_size": batch_size,
            "batch_count": batch_count,
            "payload_counter": payload_counter,
            "prefilter_target_count": prefilter_target_count,
            "mr_target_count": mr_target_count,
            "total_indices": total_indices,
            "elapsed_seconds": elapsed_seconds,
            "baseline_prefilter_survivor_rate": (
                total_prefilter_survivors / total_indices
            ),
            "baseline_mr_survivor_rate": total_mr_survivors / total_indices,
        },
        "ordering_summaries": ordering_summary_rows,
        "feature_signature_rows": feature_signature_rows,
        "batch_rows": batch_rows,
    }


def main(argv: list[str] | None = None) -> int:
    """Run the ASCII-delta geometry probe."""
    args = build_parser().parse_args(argv)
    payload = run_probe(
        namespace=args.namespace,
        bit_length=args.bit_length,
        start_index=args.start_index,
        batch_size=args.batch_size,
        batch_count=args.batch_count,
        payload_counter=args.payload_counter,
        prefilter_target_count=args.prefilter_target_count,
        mr_target_count=args.mr_target_count,
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.output_dir / "ascii_delta_geometry_probe.json"
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
