#!/usr/bin/env python3
"""Build the committed scale-up corpus for the router-to-PGS harness."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from sympy import nextprime, prevprime


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT_PATH = Path(__file__).with_name("scaleup_corpus.json")
STEP = 4096
FIXED_POINT_BITS = 40
TARGET_MODERATE_LOG = 0.7
ARCHIVED_127_P = 10_508_623_501_177_419_659
ARCHIVED_127_Q = 13_086_849_276_577_416_863
ARCHIVED_127_N = ARCHIVED_127_P * ARCHIVED_127_Q
ARCHIVED_127_LOG = math.log(ARCHIVED_127_Q / ARCHIVED_127_P)
ARCHIVED_SHAPE_TOLERANCE = 0.02
STAGE_BITS = (127, 160, 192, 224, 256, 384, 512, 768, 1024, 1536, 2048, 3072, 4096)


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description="Build the committed router-to-PGS scale-up corpus.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help="Output JSON path.",
    )
    return parser


def _anchor_from_log2(log2_value: float) -> int:
    """Return one deterministic integer anchor from a base-2 logarithm."""
    floor_value = math.floor(log2_value)
    fraction = log2_value - floor_value
    multiplier = int(round((2.0 ** fraction) * (1 << FIXED_POINT_BITS)))
    return ((1 << floor_value) * multiplier) >> FIXED_POINT_BITS


def _balanced_pair(bits: int, index: int) -> tuple[int, int]:
    """Return one balanced semiprime factor pair."""
    anchor = math.isqrt(1 << (bits - 1)) + index * STEP
    while True:
        p = int(prevprime(anchor + 1))
        q = int(nextprime(anchor))
        n = p * q
        imbalance = abs(math.log(q / p))
        if n.bit_length() == bits and imbalance <= 1e-4:
            return p, q
        anchor += STEP


def _moderate_pair(bits: int, index: int) -> tuple[int, int]:
    """Return one moderate-unbalanced semiprime factor pair."""
    target_log2_p = ((bits - 1) - (TARGET_MODERATE_LOG / math.log(2.0))) / 2.0
    anchor = _anchor_from_log2(target_log2_p) + index * STEP
    target_min = 1 << (bits - 1)

    while True:
        p = int(nextprime(anchor))
        q = int(nextprime(max(3, target_min // p)))
        n = p * q
        imbalance = math.log(q / p)
        if n.bit_length() == bits and 0.5 <= imbalance <= 0.9:
            return p, q
        anchor += STEP


def _archived_shape_pair(bits: int, index: int) -> tuple[int, int]:
    """Return one archived-shape semiprime factor pair."""
    target_log2_p = ((bits - 1) - (ARCHIVED_127_LOG / math.log(2.0))) / 2.0
    anchor = _anchor_from_log2(target_log2_p) + index * STEP
    target_min = 1 << (bits - 1)

    while True:
        p = int(nextprime(anchor))
        q = int(nextprime(max(3, target_min // p)))
        n = p * q
        imbalance = math.log(q / p)
        if n.bit_length() == bits and abs(imbalance - ARCHIVED_127_LOG) <= ARCHIVED_SHAPE_TOLERANCE:
            return p, q
        anchor += STEP


def _challenge_pair(bits: int, index: int) -> tuple[int, int]:
    """Return one challenge-like semiprime factor pair."""
    target_log2_p = math.floor(0.40 * bits) - 0.5
    anchor = _anchor_from_log2(target_log2_p) + index * STEP
    target_min = 1 << (bits - 1)

    while True:
        p = int(nextprime(anchor))
        q = int(nextprime(max(3, target_min // p)))
        n = p * q
        if n.bit_length() == bits:
            return p, q
        anchor += STEP


def _case_payload(case_id: str, family: str, case_bits: int, p: int, q: int) -> dict[str, object]:
    """Return one JSON-serializable case payload."""
    return {
        "case_id": case_id,
        "family": family,
        "case_bits": case_bits,
        "n": p * q,
        "p": p,
        "q": q,
    }


def build_corpus() -> dict[str, list[dict[str, object]]]:
    """Build the full committed stage corpus."""
    corpus: dict[str, list[dict[str, object]]] = {}

    for stage_bits in STAGE_BITS:
        rows: list[dict[str, object]] = []

        if stage_bits == 127:
            for case_bits in (80, 96, 112, 127):
                p, q = _balanced_pair(case_bits, 0)
                rows.append(
                    _case_payload(
                        f"s{stage_bits}_balanced_{case_bits}",
                        "balanced",
                        case_bits,
                        p,
                        q,
                    )
                )

            for case_bits in (80, 96, 112, 127):
                p, q = _moderate_pair(case_bits, 0)
                rows.append(
                    _case_payload(
                        f"s{stage_bits}_moderate_{case_bits}",
                        "moderate_unbalanced",
                        case_bits,
                        p,
                        q,
                    )
                )

            for case_bits in (80, 96, 112):
                p, q = _archived_shape_pair(case_bits, 0)
                rows.append(
                    _case_payload(
                        f"s{stage_bits}_archived_shape_{case_bits}",
                        "archived_shape",
                        case_bits,
                        p,
                        q,
                    )
                )
            rows.append(
                _case_payload(
                    "s127_archived_shape_archived",
                    "archived_shape",
                    127,
                    ARCHIVED_127_P,
                    ARCHIVED_127_Q,
                )
            )
        elif stage_bits in (160, 192, 224, 256):
            for index in range(2):
                p, q = _balanced_pair(stage_bits, index)
                rows.append(
                    _case_payload(
                        f"s{stage_bits}_balanced_{index + 1}",
                        "balanced",
                        stage_bits,
                        p,
                        q,
                    )
                )

            for index in range(3):
                p, q = _moderate_pair(stage_bits, index)
                rows.append(
                    _case_payload(
                        f"s{stage_bits}_moderate_{index + 1}",
                        "moderate_unbalanced",
                        stage_bits,
                        p,
                        q,
                    )
                )

            for index in range(3):
                p, q = _challenge_pair(stage_bits, index)
                rows.append(
                    _case_payload(
                        f"s{stage_bits}_challenge_{index + 1}",
                        "challenge_like",
                        stage_bits,
                        p,
                        q,
                    )
                )
        else:
            p, q = _balanced_pair(stage_bits, 0)
            rows.append(
                _case_payload(
                    f"s{stage_bits}_balanced_1",
                    "balanced",
                    stage_bits,
                    p,
                    q,
                )
            )

            p, q = _moderate_pair(stage_bits, 0)
            rows.append(
                _case_payload(
                    f"s{stage_bits}_moderate_1",
                    "moderate_unbalanced",
                    stage_bits,
                    p,
                    q,
                )
            )

            for index in range(2):
                p, q = _challenge_pair(stage_bits, index)
                rows.append(
                    _case_payload(
                        f"s{stage_bits}_challenge_{index + 1}",
                        "challenge_like",
                        stage_bits,
                        p,
                        q,
                    )
                )

        corpus[str(stage_bits)] = rows

    return corpus


def main(argv: list[str] | None = None) -> int:
    """Build and write the committed corpus."""
    args = build_parser().parse_args(argv)
    corpus = build_corpus()
    args.output.write_text(json.dumps(corpus, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "stage_count": len(corpus)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
