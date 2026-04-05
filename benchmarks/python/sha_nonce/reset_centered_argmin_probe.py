#!/usr/bin/env python3
"""Probe reset-centered argmin-position structure in SHA-256 nonce windows."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/z-band-prime-prefilter-mpl")

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt


DEFAULT_OUTPUT_DIR = Path(
    "benchmarks/output/python/sha_nonce/reset_centered_argmin_probe"
)
WINDOW_SIZE = 256
LOW_BYTE_MODULUS = 256
DEFAULT_HEADERS = 4
DEFAULT_WINDOWS_PER_HEADER = 8192
ALIGNMENTS = ("aligned", "half_shifted")
RESET_CENTER_PREFIX = 32


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Measure argmin-position histograms in 256-wide SHA-256 nonce windows "
            "under raw and reset-centered coordinates."
        )
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for JSON and SVG artifacts.",
    )
    parser.add_argument(
        "--headers",
        type=int,
        default=DEFAULT_HEADERS,
        help="Number of deterministic 76-byte header prefixes to scan.",
    )
    parser.add_argument(
        "--windows-per-header",
        type=int,
        default=DEFAULT_WINDOWS_PER_HEADER,
        help="Contiguous 256-wide windows to scan for each header prefix.",
    )
    return parser


def deterministic_header_prefix(index: int) -> bytes:
    """Return one deterministic 76-byte prefix for nonce-line probing."""
    seed = f"prime-gap-structure/sha-reset-argmin/{index}".encode("utf-8")
    chunks: list[bytes] = []
    counter = 0
    total = 0
    while total < 76:
        chunk = hashlib.sha256(seed + counter.to_bytes(4, "little")).digest()
        chunks.append(chunk)
        total += len(chunk)
        counter += 1
    return b"".join(chunks)[:76]


def reset_offset_for_window_start(window_start: int) -> int:
    """Return the low-byte carry-reset offset inside one 256-wide window."""
    return (-window_start) % LOW_BYTE_MODULUS


def recenter_offset(position: int, reset_offset: int) -> int:
    """Return one argmin position in reset-centered coordinates."""
    return (position - reset_offset) % WINDOW_SIZE


def argmin_offset_in_window(prefix: bytes, window_start: int) -> int:
    """Return the offset of the minimum SHA-256 digest inside one 256-wide window."""
    candidate = bytearray(prefix + window_start.to_bytes(4, "little"))
    best_offset = 0
    best_digest = hashlib.sha256(candidate).digest()

    for offset in range(1, WINDOW_SIZE):
        nonce = window_start + offset
        candidate[76:80] = nonce.to_bytes(4, "little")
        digest = hashlib.sha256(candidate).digest()
        if digest < best_digest:
            best_digest = digest
            best_offset = offset
    return best_offset


def exact_exchangeable_null(total_windows: int) -> list[float]:
    """Return the exact per-position expectation under exchangeable labels."""
    expected = total_windows / WINDOW_SIZE
    return [expected] * WINDOW_SIZE


def z_scores(observed: list[int], total_windows: int) -> list[float]:
    """Return exact per-position z-scores against the exchangeable null."""
    probability = 1.0 / WINDOW_SIZE
    expected = total_windows * probability
    variance = total_windows * probability * (1.0 - probability)
    if variance <= 0.0:
        return [0.0] * WINDOW_SIZE
    scale = math.sqrt(variance)
    return [(count - expected) / scale for count in observed]


def total_variation_distance(left: list[int], right: list[int]) -> float:
    """Return the total variation distance between two count profiles."""
    left_total = sum(left)
    right_total = sum(right)
    if left_total == 0 or right_total == 0:
        return 0.0
    return 0.5 * sum(
        abs((left_count / left_total) - (right_count / right_total))
        for left_count, right_count in zip(left, right)
    )


def collect_alignment_profile(
    header_count: int,
    windows_per_header: int,
    label: str,
) -> dict[str, object]:
    """Return raw and reset-centered argmin histograms for one alignment."""
    nonce_shift = 0 if label == "aligned" else WINDOW_SIZE // 2
    raw_counts = [0] * WINDOW_SIZE
    reset_centered_counts = [0] * WINDOW_SIZE
    per_header_rows: list[dict[str, int | float]] = []

    for header_index in range(header_count):
        prefix = deterministic_header_prefix(header_index)
        header_raw_counts = [0] * WINDOW_SIZE
        header_reset_counts = [0] * WINDOW_SIZE
        base_nonce = header_index * 2 * WINDOW_SIZE * windows_per_header + nonce_shift

        for window_index in range(windows_per_header):
            window_start = base_nonce + window_index * WINDOW_SIZE
            position = argmin_offset_in_window(prefix, window_start)
            reset_offset = reset_offset_for_window_start(window_start)
            centered = recenter_offset(position, reset_offset)
            raw_counts[position] += 1
            reset_centered_counts[centered] += 1
            header_raw_counts[position] += 1
            header_reset_counts[centered] += 1

        header_total = sum(header_raw_counts)
        per_header_rows.append(
            {
                "header_index": header_index,
                "window_count": header_total,
                "raw_reset_offset": reset_offset_for_window_start(base_nonce),
                "raw_offset_zero_count": header_raw_counts[0],
                "reset_center_offset_zero_count": header_reset_counts[0],
                "reset_center_prefix32_count": sum(
                    header_reset_counts[:RESET_CENTER_PREFIX]
                ),
                "reset_center_offset_zero_share": (
                    header_reset_counts[0] / header_total if header_total else 0.0
                ),
                "reset_center_prefix32_share": (
                    sum(header_reset_counts[:RESET_CENTER_PREFIX]) / header_total
                    if header_total
                    else 0.0
                ),
            }
        )

    total_windows = sum(raw_counts)
    expected = exact_exchangeable_null(total_windows)
    return {
        "label": label,
        "nonce_shift": nonce_shift,
        "total_windows": total_windows,
        "raw_reset_offset": reset_offset_for_window_start(nonce_shift),
        "raw_counts": raw_counts,
        "raw_z_scores": z_scores(raw_counts, total_windows),
        "reset_centered_counts": reset_centered_counts,
        "reset_centered_z_scores": z_scores(reset_centered_counts, total_windows),
        "exchangeable_null_counts": expected,
        "per_header_rows": per_header_rows,
        "reset_center_offset_zero_count": reset_centered_counts[0],
        "reset_center_prefix32_count": sum(reset_centered_counts[:RESET_CENTER_PREFIX]),
        "reset_center_offset_zero_share": (
            reset_centered_counts[0] / total_windows if total_windows else 0.0
        ),
        "reset_center_prefix32_share": (
            sum(reset_centered_counts[:RESET_CENTER_PREFIX]) / total_windows
            if total_windows
            else 0.0
        ),
        "raw_offset_zero_count": raw_counts[0],
        "raw_offset_zero_share": raw_counts[0] / total_windows if total_windows else 0.0,
    }


def build_payload(header_count: int, windows_per_header: int) -> dict[str, object]:
    """Run the exact probe and return the JSON-ready payload."""
    rows = [
        collect_alignment_profile(header_count, windows_per_header, label)
        for label in ALIGNMENTS
    ]
    aligned = rows[0]
    shifted = rows[1]

    return {
        "window_size": WINDOW_SIZE,
        "low_byte_modulus": LOW_BYTE_MODULUS,
        "headers": header_count,
        "windows_per_header": windows_per_header,
        "total_windows_per_alignment": aligned["total_windows"],
        "reset_center_prefix": RESET_CENTER_PREFIX,
        "null_model": "exact_exchangeable_permutation_expectation",
        "raw_total_variation_distance": total_variation_distance(
            aligned["raw_counts"],
            shifted["raw_counts"],
        ),
        "reset_centered_total_variation_distance": total_variation_distance(
            aligned["reset_centered_counts"],
            shifted["reset_centered_counts"],
        ),
        "rows": rows,
    }


def render_svg(payload: dict[str, object], output_path: Path) -> None:
    """Render a three-panel SVG summary."""
    rows = payload["rows"]
    aligned = rows[0]
    shifted = rows[1]
    offsets = list(range(WINDOW_SIZE))
    expected = aligned["exchangeable_null_counts"][0]

    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=False)

    axes[0].plot(offsets, aligned["raw_z_scores"], color="#0b7285", linewidth=1.5, label="aligned")
    axes[0].plot(offsets, shifted["raw_z_scores"], color="#c92a2a", linewidth=1.5, label="half_shifted")
    axes[0].axhline(0.0, color="#495057", linewidth=0.9, alpha=0.7)
    axes[0].axvline(aligned["raw_reset_offset"], color="#0b7285", linestyle="--", alpha=0.6)
    axes[0].axvline(shifted["raw_reset_offset"], color="#c92a2a", linestyle="--", alpha=0.6)
    axes[0].set_title("Raw Argmin Position Z-Scores")
    axes[0].set_ylabel("Z Score")
    axes[0].legend(loc="upper right")
    axes[0].grid(alpha=0.2, linewidth=0.6)

    axes[1].plot(
        offsets,
        aligned["reset_centered_z_scores"],
        color="#0b7285",
        linewidth=1.5,
        label="aligned",
    )
    axes[1].plot(
        offsets,
        shifted["reset_centered_z_scores"],
        color="#c92a2a",
        linewidth=1.5,
        label="half_shifted",
    )
    axes[1].axhline(0.0, color="#495057", linewidth=0.9, alpha=0.7)
    axes[1].axvline(0, color="#343a40", linestyle="--", alpha=0.6)
    axes[1].set_title("Reset-Centered Argmin Position Z-Scores")
    axes[1].set_ylabel("Z Score")
    axes[1].legend(loc="upper right")
    axes[1].grid(alpha=0.2, linewidth=0.6)

    zoom_offsets = list(range(RESET_CENTER_PREFIX))
    axes[2].plot(
        zoom_offsets,
        aligned["reset_centered_counts"][:RESET_CENTER_PREFIX],
        color="#0b7285",
        linewidth=1.5,
        label="aligned",
    )
    axes[2].plot(
        zoom_offsets,
        shifted["reset_centered_counts"][:RESET_CENTER_PREFIX],
        color="#c92a2a",
        linewidth=1.5,
        label="half_shifted",
    )
    axes[2].axhline(expected, color="#495057", linewidth=0.9, alpha=0.7, label="null")
    axes[2].axvline(0, color="#343a40", linestyle="--", alpha=0.6)
    axes[2].set_title("Reset-Centered Counts, First 32 Offsets")
    axes[2].set_xlabel("Reset-Centered Offset")
    axes[2].set_ylabel("Argmin Count")
    axes[2].legend(loc="upper right")
    axes[2].grid(alpha=0.2, linewidth=0.6)

    fig.tight_layout()
    fig.savefig(output_path, format="svg")
    plt.close(fig)


def main(argv: list[str] | None = None) -> int:
    """Run the reset-centered argmin-position probe."""
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.headers < 1:
        raise ValueError("headers must be at least 1")
    if args.windows_per_header < 1:
        raise ValueError("windows_per_header must be at least 1")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    payload = build_payload(args.headers, args.windows_per_header)

    json_path = args.output_dir / "reset_centered_argmin_probe.json"
    svg_path = args.output_dir / "reset_centered_argmin_probe.svg"
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    render_svg(payload, svg_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
