#!/usr/bin/env python3
"""Pre-registered word-position sweep probe for argmin harmonic channels.

Moves the nonce to different 32-bit word positions inside the second SHA-256
message block and records the crest offset and amplitude of six tracked
harmonics (k=7, 14, 27, 55, 71, 86) for each placement.

Baseline: w=3 (nonce at W[3], bytes 76-79 of the 80-byte input -- the standard
bitcoin-header second block layout used in reset_centered_argmin_probe.py).

Pre-registered decision rules (do not alter before running):
  Rule A: if k=14, 27, 55 all shift by the same delta_crest when w changes,
          they share one schedule path.
  Rule B: ratio delta_crest(k=27) / delta_crest(k=14) discriminates between
          same-path (ratio=1) and different-path (ratio!=1) hypotheses.
  Rule C: if k=71 and k=86 shift with k=14/27/55, they belong to the same
          family; different shift -> separate sources.
  Amplitude gate: if amp(w) < 0.5 * amp(w=3) for a harmonic, mark its crest
          as unreliable in the output (crest set to null).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
from pathlib import Path

DEFAULT_OUTPUT_DIR = Path(
    "benchmarks/output/python/sha_nonce/nonce_word_position_sweep_probe"
)
WINDOW_SIZE = 256
DEFAULT_HEADERS = 4
DEFAULT_WINDOWS_PER_HEADER = 8192
TRACKED_HARMONICS = [7, 14, 27, 55, 71, 86]
BASELINE_WORD_INDEX = 3
AMPLITUDE_GATE_FRACTION = 0.5

# Word positions to sweep. W[0..3] are within the padding block for a
# standard 80-byte bitcoin header. W[4..7] require a modified block layout
# and are included for the path-discrimination test only.
DEFAULT_WORD_INDICES = [0, 1, 3, 7]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Sweep the nonce across message word positions and record "
            "argmin harmonic crest offsets and amplitudes."
        )
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
    )
    parser.add_argument(
        "--headers",
        type=int,
        default=DEFAULT_HEADERS,
    )
    parser.add_argument(
        "--windows-per-header",
        type=int,
        default=DEFAULT_WINDOWS_PER_HEADER,
    )
    parser.add_argument(
        "--word-indices",
        type=int,
        nargs="+",
        default=DEFAULT_WORD_INDICES,
        help="Message word positions to probe (0-based, 0..15).",
    )
    return parser


def deterministic_header_prefix(index: int) -> bytes:
    """Return the same deterministic seed as reset_centered_argmin_probe."""
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


def build_block(prefix76: bytes, word_index: int, nonce: int) -> bytes:
    """Build an 80-byte block with the nonce placed at the given word index.

    Standard layout (word_index=3):
      W[0]=prefix[64:68], W[1]=prefix[68:72], W[2]=prefix[72:76], W[3]=nonce

    Non-standard placement: the 80-byte block is constructed so that the
    nonce occupies W[word_index] (bytes word_index*4 .. word_index*4+3).
    The remaining word slots are filled from the deterministic prefix bytes
    (wrapping as needed) so that the only variable is the nonce word.
    """
    # Fill a 16-word (64-byte second block) with prefix material, then overwrite
    # the target word with the nonce.
    # For the standard second block the first 76 bytes come from the header;
    # bytes 64-79 are: W[0..3]. We extend the prefix to 64 bytes for non-std
    # word positions.
    padded_prefix = (prefix76 * 2)[:64]  # deterministic fill, 64 bytes
    words = list(struct.unpack_from("<16I", padded_prefix + b"\x00" * (64 - len(padded_prefix[:64]))))
    words[word_index] = nonce & 0xFFFFFFFF
    block = struct.pack("<16I", *words)
    # SHA-256 needs an 80-byte input for bitcoin headers; pad to 80.
    return block[:80] if len(block) >= 80 else block + b"\x00" * (80 - len(block))


def argmin_offset_for_word(
    prefix76: bytes, word_index: int, window_start: int
) -> int:
    """Return the argmin offset inside one 256-wide nonce window."""
    best_offset = 0
    best_digest = hashlib.sha256(
        build_block(prefix76, word_index, window_start)
    ).digest()
    for offset in range(1, WINDOW_SIZE):
        nonce = window_start + offset
        digest = hashlib.sha256(
            build_block(prefix76, word_index, nonce)
        ).digest()
        if digest < best_digest:
            best_digest = digest
            best_offset = offset
    return best_offset


def reset_offset_for_window_start(window_start: int) -> int:
    return (-window_start) % WINDOW_SIZE


def collect_reset_centered_profile(
    header_count: int,
    windows_per_header: int,
    word_index: int,
) -> list[int]:
    """Return the 256-bin reset-centered argmin histogram for one word position."""
    counts = [0] * WINDOW_SIZE
    for header_index in range(header_count):
        prefix = deterministic_header_prefix(header_index)
        base_nonce = header_index * 2 * WINDOW_SIZE * windows_per_header
        for window_index in range(windows_per_header):
            window_start = base_nonce + window_index * WINDOW_SIZE
            position = argmin_offset_for_word(prefix, word_index, window_start)
            reset_offset = reset_offset_for_window_start(window_start)
            centered = (position - reset_offset) % WINDOW_SIZE
            counts[centered] += 1
    return counts


def harmonic_amp_and_crest(
    counts: list[int],
    k: int,
) -> tuple[float, float | None]:
    """Return (amplitude, crest_offset) for harmonic k of the count profile.

    Amplitude is normalised to [0, 1] (peak-to-null ratio relative to N/2).
    Crest is the principal crest offset in [0, 256). Returns None for crest
    if the amplitude is below the gate threshold (computed by caller).
    """
    N = len(counts)
    null = sum(counts) / N
    residual = [c - null for c in counts]
    # DFT coefficient at frequency k
    coeff = sum(
        residual[n] * (math.cos(2 * math.pi * k * n / N) - 1j * math.sin(2 * math.pi * k * n / N))
        for n in range(N)
    )
    amp = abs(coeff) / (N / 2)
    phase_rad = math.atan2(coeff.imag, coeff.real)
    # Principal crest: where cos(2*pi*k*n/N + phase) is maximised
    # crest_offset = -phase / (2*pi/N) mod N/k ... take principal in [0, N)
    crest = (-phase_rad * N / (2 * math.pi * k)) % (N / k)
    # Map to the crest nearest to 0 in the reset-centered frame
    crest_in_period = crest % (N / k)
    return amp, crest_in_period


def analyse_word_position(
    header_count: int,
    windows_per_header: int,
    word_index: int,
    baseline_amps: dict[int, float] | None,
) -> dict[str, object]:
    """Run the probe for one word position and return the result row."""
    counts = collect_reset_centered_profile(
        header_count, windows_per_header, word_index
    )
    row: dict[str, object] = {"word_index": word_index}
    for k in TRACKED_HARMONICS:
        amp, crest = harmonic_amp_and_crest(counts, k)
        row[f"k{k}_amp"] = round(amp, 6)
        if baseline_amps is not None:
            base = baseline_amps.get(k, 0.0)
            reliable = amp >= AMPLITUDE_GATE_FRACTION * base
        else:
            reliable = True
        row[f"k{k}_crest"] = round(crest, 4) if reliable else None
        row[f"k{k}_crest_reliable"] = reliable
    return row


def compute_delta_rows(rows: list[dict]) -> list[dict]:
    """Compute crest and amplitude deltas relative to the baseline row."""
    baseline = next((r for r in rows if r["word_index"] == BASELINE_WORD_INDEX), None)
    if baseline is None:
        return []
    deltas = []
    for row in rows:
        if row["word_index"] == BASELINE_WORD_INDEX:
            continue
        delta: dict[str, object] = {
            "word_index": row["word_index"],
            "vs_word_index": BASELINE_WORD_INDEX,
        }
        for k in TRACKED_HARMONICS:
            b_crest = baseline.get(f"k{k}_crest")
            r_crest = row.get(f"k{k}_crest")
            if b_crest is not None and r_crest is not None:
                delta[f"k{k}_delta_crest"] = round(r_crest - b_crest, 4)
            else:
                delta[f"k{k}_delta_crest"] = None
            b_amp = baseline.get(f"k{k}_amp", 0.0)
            r_amp = row.get(f"k{k}_amp", 0.0)
            delta[f"k{k}_delta_amp"] = round(r_amp - b_amp, 6)
        deltas.append(delta)
    return deltas


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Ensure baseline word index is always included.
    word_indices = sorted(set(args.word_indices) | {BASELINE_WORD_INDEX})

    rows: list[dict] = []
    baseline_amps: dict[int, float] | None = None

    # Run baseline first so amplitude gate is available for subsequent rows.
    print(f"Running baseline w={BASELINE_WORD_INDEX} ...")
    baseline_row = analyse_word_position(
        args.headers, args.windows_per_header, BASELINE_WORD_INDEX, None
    )
    rows.append(baseline_row)
    baseline_amps = {k: baseline_row[f"k{k}_amp"] for k in TRACKED_HARMONICS}

    for w in word_indices:
        if w == BASELINE_WORD_INDEX:
            continue
        print(f"Running w={w} ...")
        row = analyse_word_position(
            args.headers, args.windows_per_header, w, baseline_amps
        )
        rows.append(row)

    # Sort rows by word_index for readability.
    rows.sort(key=lambda r: r["word_index"])
    delta_rows = compute_delta_rows(rows)

    payload = {
        "baseline_word_index": BASELINE_WORD_INDEX,
        "window_size": WINDOW_SIZE,
        "headers": args.headers,
        "windows_per_header": args.windows_per_header,
        "total_windows": args.headers * args.windows_per_header,
        "tracked_harmonics": TRACKED_HARMONICS,
        "amplitude_gate_fraction": AMPLITUDE_GATE_FRACTION,
        "decision_rules": {
            "rule_A": "k=14,27,55 same delta_crest -> same schedule path",
            "rule_B": "ratio delta_crest(k27)/delta_crest(k14): 1=same-path, !=1=different-path",
            "rule_C": "k=71,86 shift with k=14 family -> same source; different -> separate",
        },
        "rows": rows,
        "delta_rows": delta_rows,
    }

    out_path = args.output_dir / "nonce_word_position_sweep_probe.json"
    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Written: {out_path}")

    # Print a human-readable summary of the delta rows.
    print("\nDelta summary (vs baseline w=3):")
    for dr in delta_rows:
        w = dr["word_index"]
        parts = []
        for k in TRACKED_HARMONICS:
            dc = dr.get(f"k{k}_delta_crest")
            dc_str = f"{dc:+.2f}" if dc is not None else "n/a"
            parts.append(f"k{k}:{dc_str}")
        print(f"  w={w}: " + "  ".join(parts))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
