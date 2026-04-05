#!/usr/bin/env python3
"""Compare observed SHA nonce argmin phase against nonce-word ROTR7 and sigma0 phase."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


DEFAULT_OBSERVED_JSON = Path(
    "benchmarks/output/python/sha_nonce/reset_centered_argmin_probe/"
    "reset_centered_argmin_probe.json"
)
DEFAULT_OUTPUT_DIR = Path("benchmarks/output/python/sha_nonce/rotr7_phase_probe")
WINDOW_SIZE = 256
K_TARGET = 7
ALIGNMENTS = ("aligned", "half_shifted")


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Compare the observed reset-centered SHA nonce argmin profile against "
            "the k=7 phase induced by ROTR7 and sigma0 on the nonce word."
        )
    )
    parser.add_argument(
        "--observed-json",
        type=Path,
        default=DEFAULT_OBSERVED_JSON,
        help="Path to the reset-centered argmin probe JSON artifact.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for JSON and SVG artifacts.",
    )
    return parser


def ror(value: int, shift: int) -> int:
    """Return the 32-bit rotate-right of one word."""
    return ((value >> shift) | ((value << (32 - shift)) & 0xFFFFFFFF)) & 0xFFFFFFFF


def xor3(left: int, middle: int, right: int) -> int:
    """Return the xor of three 32-bit words."""
    return left ^ middle ^ right


def small_sigma0(value: int) -> int:
    """Return the SHA-256 small sigma 0 transform."""
    return xor3(ror(value, 7), ror(value, 18), value >> 3)


def reset_offset_for_window_start(window_start: int) -> int:
    """Return the low-byte reset offset inside one 256-wide window."""
    return (-window_start) % WINDOW_SIZE


def recentered_nonce(window_start: int, centered_offset: int) -> int:
    """Return the nonce that lands at one reset-centered offset."""
    raw_offset = (centered_offset + reset_offset_for_window_start(window_start)) % WINDOW_SIZE
    return window_start + raw_offset


def nonce_word(nonce: int) -> int:
    """Return the second-block nonce word used by SHA-256 in this repo's probes."""
    return int.from_bytes(nonce.to_bytes(4, "little"), "big")


def load_observed_payload(path: Path) -> dict[str, object]:
    """Load the observed reset-centered profile payload."""
    return json.loads(path.read_text(encoding="utf-8"))


def observed_mean_profile(payload: dict[str, object]) -> list[float]:
    """Return the mean observed reset-centered z-score profile."""
    rows = payload["rows"]
    aligned = rows[0]["reset_centered_z_scores"]
    shifted = rows[1]["reset_centered_z_scores"]
    return [(left + right) / 2.0 for left, right in zip(aligned, shifted)]


def model_profiles(payload: dict[str, object]) -> dict[str, list[float]]:
    """Return deterministic model profiles across the exact window set."""
    header_count = int(payload["headers"])
    windows_per_header = int(payload["windows_per_header"])
    profiles = {
        "rotr7_word_value": [0.0] * WINDOW_SIZE,
        "sigma0_word_value": [0.0] * WINDOW_SIZE,
        "rotr7_top_byte": [0.0] * WINDOW_SIZE,
        "sigma0_top_byte": [0.0] * WINDOW_SIZE,
    }
    total_windows = 0

    for alignment in ALIGNMENTS:
        nonce_shift = 0 if alignment == "aligned" else WINDOW_SIZE // 2
        for header_index in range(header_count):
            base_nonce = header_index * 2 * WINDOW_SIZE * windows_per_header + nonce_shift
            for window_index in range(windows_per_header):
                window_start = base_nonce + window_index * WINDOW_SIZE
                for centered_offset in range(WINDOW_SIZE):
                    nonce = recentered_nonce(window_start, centered_offset)
                    word = nonce_word(nonce)
                    rotr7_value = ror(word, 7)
                    sigma0_value = small_sigma0(word)
                    profiles["rotr7_word_value"][centered_offset] += rotr7_value
                    profiles["sigma0_word_value"][centered_offset] += sigma0_value
                    profiles["rotr7_top_byte"][centered_offset] += (
                        rotr7_value >> 24
                    ) & 0xFF
                    profiles["sigma0_top_byte"][centered_offset] += (
                        sigma0_value >> 24
                    ) & 0xFF
                total_windows += 1

    return {
        label: [value / total_windows for value in values]
        for label, values in profiles.items()
    }


def centered(values: list[float]) -> list[float]:
    """Return one centered copy of the profile."""
    mean = sum(values) / len(values)
    return [value - mean for value in values]


def harmonic_component(values: list[float], harmonic: int) -> dict[str, object]:
    """Return the exact harmonic component and its phase metrics."""
    profile = centered(values)
    n = len(profile)
    real = 0.0
    imag = 0.0
    for offset, value in enumerate(profile):
        angle = 2.0 * math.pi * harmonic * offset / n
        real += value * math.cos(angle)
        imag -= value * math.sin(angle)
    amplitude = math.hypot(real, imag)
    phase = math.atan2(imag, real)
    scale = 2.0 / n
    component = [
        scale
        * (
            real * math.cos(2.0 * math.pi * harmonic * offset / n)
            - imag * math.sin(2.0 * math.pi * harmonic * offset / n)
        )
        for offset in range(n)
    ]
    peak_offset = ((-phase) * n / (2.0 * math.pi * harmonic)) % (n / harmonic)
    crests = [peak_offset + index * (n / harmonic) for index in range(harmonic)]
    return {
        "harmonic": harmonic,
        "real": real,
        "imag": imag,
        "amplitude": amplitude,
        "phase_radians": phase,
        "period": n / harmonic,
        "principal_peak_offset": peak_offset,
        "crest_offsets": crests,
        "component": component,
    }


def wrap_phase_difference(left: float, right: float) -> float:
    """Return one wrapped phase difference in [-pi, pi]."""
    delta = left - right
    while delta <= -math.pi:
        delta += 2.0 * math.pi
    while delta > math.pi:
        delta -= 2.0 * math.pi
    return delta


def nearest_crest_distance(crest_offsets: list[float], target_offset: float) -> float:
    """Return the distance from one target offset to the nearest crest."""
    return min(abs(offset - target_offset) for offset in crest_offsets)


def build_payload(
    observed_payload: dict[str, object],
    observed_json_path: Path,
) -> dict[str, object]:
    """Build the full comparison payload."""
    observed_profile = observed_mean_profile(observed_payload)
    observed_component = harmonic_component(observed_profile, K_TARGET)
    modeled = model_profiles(observed_payload)

    rows = []
    for label, profile in modeled.items():
        component = harmonic_component(profile, K_TARGET)
        rows.append(
            {
                "label": label,
                "profile": profile,
                "k7_component": component["component"],
                "k7_amplitude": component["amplitude"],
                "k7_phase_radians": component["phase_radians"],
                "k7_period": component["period"],
                "k7_principal_peak_offset": component["principal_peak_offset"],
                "k7_crest_offsets": component["crest_offsets"],
                "phase_difference_vs_observed_radians": wrap_phase_difference(
                    component["phase_radians"],
                    observed_component["phase_radians"],
                ),
                "nearest_crest_distance_to_offset_29": nearest_crest_distance(
                    component["crest_offsets"],
                    29.0,
                ),
            }
        )

    return {
        "observed_json": str(observed_json_path),
        "headers": observed_payload["headers"],
        "windows_per_header": observed_payload["windows_per_header"],
        "total_windows_per_alignment": observed_payload["total_windows_per_alignment"],
        "target_harmonic": K_TARGET,
        "observed_mean_profile": observed_profile,
        "observed_k7_component": observed_component["component"],
        "observed_k7_amplitude": observed_component["amplitude"],
        "observed_k7_phase_radians": observed_component["phase_radians"],
        "observed_k7_period": observed_component["period"],
        "observed_k7_principal_peak_offset": observed_component["principal_peak_offset"],
        "observed_k7_crest_offsets": observed_component["crest_offsets"],
        "rows": rows,
    }


def render_svg(payload: dict[str, object], output_path: Path) -> None:
    """Render one compact SVG showing observed and modeled k=7 components."""
    offsets = list(range(WINDOW_SIZE))
    observed = payload["observed_mean_profile"]
    observed_k7 = payload["observed_k7_component"]
    colors = {
        "rotr7_word_value": "#1864ab",
        "sigma0_word_value": "#c92a2a",
        "rotr7_top_byte": "#2b8a3e",
        "sigma0_top_byte": "#f08c00",
    }

    y_values = observed + observed_k7[:]
    for row in payload["rows"]:
        y_values.extend(row["k7_component"])
    y_min = min(y_values)
    y_max = max(y_values)
    if y_min == y_max:
        y_min -= 1.0
        y_max += 1.0

    width = 1200
    height = 900
    margin_left = 90
    margin_right = 40
    margin_top = 70
    margin_bottom = 60
    panel_gap = 70
    panel_height = (height - margin_top - margin_bottom - 2 * panel_gap) / 3.0
    plot_width = width - margin_left - margin_right

    def x_at(offset: int) -> float:
        return margin_left + (offset / (WINDOW_SIZE - 1)) * plot_width

    def y_at(panel_index: int, value: float) -> float:
        top = margin_top + panel_index * (panel_height + panel_gap)
        return top + panel_height * (1.0 - (value - y_min) / (y_max - y_min))

    def polyline(panel_index: int, values: list[float]) -> str:
        return " ".join(
            f"{x_at(offset):.2f},{y_at(panel_index, value):.2f}"
            for offset, value in enumerate(values)
        )

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<style>',
        'text { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; fill: #1f2933; }',
        '.title { font-size: 28px; font-weight: 700; }',
        '.subtitle { font-size: 16px; fill: #52606d; }',
        '.panel-title { font-size: 18px; font-weight: 600; }',
        '.axis { stroke: #cbd2d9; stroke-width: 1; }',
        '.tick { stroke: #9aa5b1; stroke-width: 1; }',
        '.label { font-size: 13px; fill: #52606d; }',
        '</style>',
        '<text x="600" y="38" class="title" text-anchor="middle">ROTR7 / sigma0 Phase Probe</text>',
        '<text x="600" y="62" class="subtitle" text-anchor="middle">Observed reset-centered argmin profile vs modeled k=7 phase from the nonce word</text>',
    ]

    panel_titles = (
        "Observed mean reset-centered profile",
        "Observed k=7 component",
        "Modeled k=7 components",
    )
    for panel_index, panel_title in enumerate(panel_titles):
        top = margin_top + panel_index * (panel_height + panel_gap)
        bottom = top + panel_height
        lines.append(
            f'<text x="{margin_left}" y="{top - 16:.2f}" class="panel-title">{panel_title}</text>'
        )
        lines.append(
            f'<line x1="{margin_left}" y1="{y_at(panel_index, 0.0):.2f}" '
            f'x2="{width - margin_right}" y2="{y_at(panel_index, 0.0):.2f}" class="axis"/>'
        )
        lines.append(
            f'<line x1="{margin_left}" y1="{top:.2f}" x2="{margin_left}" y2="{bottom:.2f}" class="axis"/>'
        )
        for tick in (0, 64, 128, 192, 255):
            lines.append(
                f'<line x1="{x_at(tick):.2f}" y1="{top:.2f}" x2="{x_at(tick):.2f}" y2="{bottom:.2f}" class="tick" opacity="0.35"/>'
            )
            lines.append(
                f'<text x="{x_at(tick):.2f}" y="{bottom + 22:.2f}" class="label" text-anchor="middle">{tick}</text>'
            )

    lines.append(
        f'<polyline fill="none" stroke="#0b7285" stroke-width="2" points="{polyline(0, observed)}"/>'
    )
    lines.append(
        f'<polyline fill="none" stroke="#5f3dc4" stroke-width="2" points="{polyline(1, observed_k7)}"/>'
    )

    legend_x = width - margin_right - 210
    legend_y = margin_top + 2 * (panel_height + panel_gap) - 20
    for index, row in enumerate(payload["rows"]):
        color = colors[row["label"]]
        y = legend_y + 22 * index
        lines.append(
            f'<line x1="{legend_x}" y1="{y}" x2="{legend_x + 28}" y2="{y}" stroke="{color}" stroke-width="3"/>'
        )
        lines.append(
            f'<text x="{legend_x + 36}" y="{y + 5}" class="label">{row["label"]}</text>'
        )
        lines.append(
            f'<polyline fill="none" stroke="{color}" stroke-width="2" points="{polyline(2, row["k7_component"])}"/>'
        )

    lines.append('</svg>')
    output_path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    """Run the phase probe."""
    parser = build_parser()
    args = parser.parse_args(argv)

    observed_payload = load_observed_payload(args.observed_json)
    payload = build_payload(observed_payload, args.observed_json)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.output_dir / "rotr7_phase_probe.json"
    svg_path = args.output_dir / "rotr7_phase_probe.svg"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    render_svg(payload, svg_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
