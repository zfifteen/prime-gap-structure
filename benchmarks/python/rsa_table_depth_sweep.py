#!/usr/bin/env python3
"""Deterministic end-to-end RSA table-depth sweep in the 4096-bit prime regime."""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
import time
from pathlib import Path
from typing import Dict, Iterable, List, Sequence


ROOT = Path(__file__).resolve().parents[2]
MODULE_DIR = Path(__file__).resolve().parent
if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))

import rsa_keygen_benchmark as rsa_benchmark
import table_depth_sweep as depth_sweep


DEFAULT_OUTPUT_DIR = ROOT / "benchmarks" / "output" / "python" / "rsa-table-depth-sweep"
DEFAULT_RSA_BITS = 8192
DEFAULT_KEYPAIR_COUNT = 2
DEFAULT_TABLE_LIMITS = [300007, 1000003, 3000000]
DEFAULT_NAMESPACE = "cdl-rsa-table-depth-sweep"
SVG_WIDTH = 1200
SVG_HEIGHT = 760
SVG_MARGIN_LEFT = 95
SVG_MARGIN_RIGHT = 80
SVG_MARGIN_TOP = 90
SVG_MARGIN_BOTTOM = 90
BAR_COLORS = ["#0b6e4f", "#c84c09", "#2b59c3", "#8b1e3f"]
STACK_COLORS = {
    "proxy": "#0b6e4f",
    "mr": "#c84c09",
    "assembly": "#2b59c3",
    "residual": "#9fb3c8",
}


def parse_int_list(values: Sequence[str]) -> List[int]:
    """Parse a non-empty list of positive integers."""
    parsed = [int(value) for value in values]
    if not parsed:
        raise ValueError("at least one integer value is required")
    if any(value < 2 for value in parsed):
        raise ValueError("all values must be at least 2")
    return parsed


def render_speedup_svg(results: Dict[str, object]) -> str:
    """Render speedup versus covered prime depth."""
    rows = results["rows"]
    labels = [f"<= {int(row['covered_prime_limit']):,}" for row in rows]
    values = [float(row["speedup"]) for row in rows]
    y_max = max(values) * 1.25
    plot_width = SVG_WIDTH - SVG_MARGIN_LEFT - SVG_MARGIN_RIGHT
    plot_height = SVG_HEIGHT - SVG_MARGIN_TOP - SVG_MARGIN_BOTTOM
    slot_width = plot_width / len(values)
    bar_width = slot_width * 0.58

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_WIDTH}" height="{SVG_HEIGHT}" viewBox="0 0 {SVG_WIDTH} {SVG_HEIGHT}">',
        '<rect width="100%" height="100%" fill="#fcfbf7" />',
        '<text x="95" y="46" font-family="Menlo, Monaco, monospace" font-size="26" fill="#1f2933">8192-bit RSA speedup by table depth</text>',
        '<text x="95" y="72" font-family="Menlo, Monaco, monospace" font-size="14" fill="#52606d">End-to-end deterministic RSA keygen speedup versus covered odd-prime depth</text>',
    ]

    for tick_index in range(6):
        tick_value = y_max * tick_index / 5.0
        y = SVG_MARGIN_TOP + plot_height - (tick_value / y_max) * plot_height
        parts.append(
            f'<line x1="{SVG_MARGIN_LEFT}" y1="{y:.2f}" x2="{SVG_WIDTH - SVG_MARGIN_RIGHT}" y2="{y:.2f}" stroke="#d9e2ec" stroke-width="1" />'
        )
        parts.append(
            f'<text x="{SVG_MARGIN_LEFT - 14}" y="{y + 5:.2f}" text-anchor="end" font-family="Menlo, Monaco, monospace" font-size="13" fill="#486581">{tick_value:.2f}x</text>'
        )

    axis_bottom = SVG_HEIGHT - SVG_MARGIN_BOTTOM
    parts.append(
        f'<line x1="{SVG_MARGIN_LEFT}" y1="{axis_bottom}" x2="{SVG_WIDTH - SVG_MARGIN_RIGHT}" y2="{axis_bottom}" stroke="#243b53" stroke-width="1.5" />'
    )
    parts.append(
        f'<line x1="{SVG_MARGIN_LEFT}" y1="{SVG_MARGIN_TOP}" x2="{SVG_MARGIN_LEFT}" y2="{axis_bottom}" stroke="#243b53" stroke-width="1.5" />'
    )

    for index, (label, value) in enumerate(zip(labels, values)):
        x_center = SVG_MARGIN_LEFT + slot_width * (index + 0.5)
        bar_height = (value / y_max) * plot_height
        bar_x = x_center - bar_width / 2.0
        bar_y = axis_bottom - bar_height
        color = BAR_COLORS[index % len(BAR_COLORS)]
        parts.append(
            f'<rect x="{bar_x:.2f}" y="{bar_y:.2f}" width="{bar_width:.2f}" height="{bar_height:.2f}" rx="6" fill="{color}" />'
        )
        parts.append(
            f'<text x="{x_center:.2f}" y="{bar_y - 10:.2f}" text-anchor="middle" font-family="Menlo, Monaco, monospace" font-size="14" fill="#243b53">{value:.2f}x</text>'
        )
        parts.append(
            f'<text x="{x_center:.2f}" y="{axis_bottom + 26:.2f}" text-anchor="middle" font-family="Menlo, Monaco, monospace" font-size="13" fill="#243b53">{label}</text>'
        )
        parts.append(
            f'<text x="{x_center:.2f}" y="{axis_bottom + 46:.2f}" text-anchor="middle" font-family="Menlo, Monaco, monospace" font-size="12" fill="#52606d">{float(rows[index]["proxy_rejection_rate"]) * 100.0:.2f}% reject</text>'
        )

    parts.append(
        f'<text x="{(SVG_MARGIN_LEFT + SVG_WIDTH - SVG_MARGIN_RIGHT) / 2.0:.2f}" y="{SVG_HEIGHT - 28}" text-anchor="middle" font-family="Menlo, Monaco, monospace" font-size="14" fill="#243b53">Covered odd-prime limit</text>'
    )
    parts.append(
        f'<text x="24" y="{(SVG_MARGIN_TOP + axis_bottom) / 2.0:.2f}" transform="rotate(-90 24 {(SVG_MARGIN_TOP + axis_bottom) / 2.0:.2f})" text-anchor="middle" font-family="Menlo, Monaco, monospace" font-size="14" fill="#243b53">End-to-end speedup</text>'
    )
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def render_rejection_svg(results: Dict[str, object]) -> str:
    """Render observed end-to-end rejection against the structural ceiling."""
    rows = results["rows"]
    labels = [f"{int(row['covered_prime_limit']):,}" for row in rows]
    observed = [float(row["proxy_rejection_rate"]) for row in rows]
    theory = [float(row["theoretical_rejection_rate"]) for row in rows]
    y_min = min(min(observed), min(theory)) - 0.01
    y_max = max(max(observed), max(theory)) + 0.01
    plot_width = SVG_WIDTH - SVG_MARGIN_LEFT - SVG_MARGIN_RIGHT
    plot_height = SVG_HEIGHT - SVG_MARGIN_TOP - SVG_MARGIN_BOTTOM
    slot_width = plot_width / max(1, len(rows) - 1)

    def x_coord(index: int) -> float:
        if len(rows) == 1:
            return SVG_MARGIN_LEFT + plot_width / 2.0
        return SVG_MARGIN_LEFT + slot_width * index

    def y_coord(value: float) -> float:
        return SVG_MARGIN_TOP + ((y_max - value) / (y_max - y_min)) * plot_height

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_WIDTH}" height="{SVG_HEIGHT}" viewBox="0 0 {SVG_WIDTH} {SVG_HEIGHT}">',
        '<rect width="100%" height="100%" fill="#fcfbf7" />',
        '<text x="95" y="46" font-family="Menlo, Monaco, monospace" font-size="26" fill="#1f2933">8192-bit RSA rejection versus structural ceiling</text>',
        '<text x="95" y="72" font-family="Menlo, Monaco, monospace" font-size="14" fill="#52606d">Observed end-to-end proxy rejection tracks the same small-prime depth ceiling seen in the candidate sweep</text>',
    ]

    for tick_index in range(6):
        tick_value = y_min + (y_max - y_min) * tick_index / 5.0
        y = y_coord(tick_value)
        parts.append(
            f'<line x1="{SVG_MARGIN_LEFT}" y1="{y:.2f}" x2="{SVG_WIDTH - SVG_MARGIN_RIGHT}" y2="{y:.2f}" stroke="#d9e2ec" stroke-width="1" />'
        )
        parts.append(
            f'<text x="{SVG_MARGIN_LEFT - 14}" y="{y + 5:.2f}" text-anchor="end" font-family="Menlo, Monaco, monospace" font-size="13" fill="#486581">{tick_value * 100.0:.2f}%</text>'
        )

    axis_bottom = SVG_HEIGHT - SVG_MARGIN_BOTTOM
    parts.append(
        f'<line x1="{SVG_MARGIN_LEFT}" y1="{axis_bottom}" x2="{SVG_WIDTH - SVG_MARGIN_RIGHT}" y2="{axis_bottom}" stroke="#243b53" stroke-width="1.5" />'
    )
    parts.append(
        f'<line x1="{SVG_MARGIN_LEFT}" y1="{SVG_MARGIN_TOP}" x2="{SVG_MARGIN_LEFT}" y2="{axis_bottom}" stroke="#243b53" stroke-width="1.5" />'
    )

    observed_points = " ".join(
        f"{x_coord(index):.2f},{y_coord(value):.2f}"
        for index, value in enumerate(observed)
    )
    theory_points = " ".join(
        f"{x_coord(index):.2f},{y_coord(value):.2f}"
        for index, value in enumerate(theory)
    )
    parts.append(
        f'<polyline fill="none" stroke="#0b6e4f" stroke-width="3.5" points="{observed_points}" />'
    )
    parts.append(
        f'<polyline fill="none" stroke="#c84c09" stroke-width="3" stroke-dasharray="8 6" points="{theory_points}" />'
    )

    for index, (label, observed_value, theory_value) in enumerate(zip(labels, observed, theory)):
        x = x_coord(index)
        parts.append(
            f'<circle cx="{x:.2f}" cy="{y_coord(observed_value):.2f}" r="6" fill="#0b6e4f" stroke="#fcfbf7" stroke-width="2" />'
        )
        parts.append(
            f'<circle cx="{x:.2f}" cy="{y_coord(theory_value):.2f}" r="5" fill="#c84c09" stroke="#fcfbf7" stroke-width="2" />'
        )
        parts.append(
            f'<text x="{x:.2f}" y="{axis_bottom + 26:.2f}" text-anchor="middle" font-family="Menlo, Monaco, monospace" font-size="13" fill="#243b53">{label}</text>'
        )
        parts.append(
            f'<text x="{x:.2f}" y="{axis_bottom + 46:.2f}" text-anchor="middle" font-family="Menlo, Monaco, monospace" font-size="12" fill="#52606d">{(observed_value - theory_value) * 100.0:+.2f} pp</text>'
        )

    legend_x = SVG_WIDTH - SVG_MARGIN_RIGHT - 230
    legend_y = SVG_MARGIN_TOP + 16
    parts.append(
        f'<line x1="{legend_x}" y1="{legend_y:.2f}" x2="{legend_x + 34}" y2="{legend_y:.2f}" stroke="#0b6e4f" stroke-width="3.5" />'
    )
    parts.append(
        f'<text x="{legend_x + 44}" y="{legend_y + 5:.2f}" font-family="Menlo, Monaco, monospace" font-size="13" fill="#243b53">observed end-to-end rejection</text>'
    )
    parts.append(
        f'<line x1="{legend_x}" y1="{legend_y + 24:.2f}" x2="{legend_x + 34}" y2="{legend_y + 24:.2f}" stroke="#c84c09" stroke-width="3" stroke-dasharray="8 6" />'
    )
    parts.append(
        f'<text x="{legend_x + 44}" y="{legend_y + 29:.2f}" font-family="Menlo, Monaco, monospace" font-size="13" fill="#243b53">structural ceiling from covered primes</text>'
    )

    parts.append(
        f'<text x="{(SVG_MARGIN_LEFT + SVG_WIDTH - SVG_MARGIN_RIGHT) / 2.0:.2f}" y="{SVG_HEIGHT - 28}" text-anchor="middle" font-family="Menlo, Monaco, monospace" font-size="14" fill="#243b53">Covered odd-prime limit</text>'
    )
    parts.append(
        f'<text x="24" y="{(SVG_MARGIN_TOP + axis_bottom) / 2.0:.2f}" transform="rotate(-90 24 {(SVG_MARGIN_TOP + axis_bottom) / 2.0:.2f})" text-anchor="middle" font-family="Menlo, Monaco, monospace" font-size="14" fill="#243b53">Composite rejection rate</text>'
    )
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def render_timing_breakdown_svg(results: Dict[str, object]) -> str:
    """Render stacked end-to-end timing bars for baseline and each depth."""
    baseline = results["baseline"]
    rows = results["rows"]
    cells = [
        {
            "label": "baseline",
            "proxy_ms": 0.0,
            "mr_ms": float(baseline["total_miller_rabin_time_ms"]),
            "assembly_ms": float(baseline["total_assembly_time_ms"]),
            "residual_ms": float(baseline["total_residual_time_ms"]),
        }
    ]
    for row in rows:
        cells.append(
            {
                "label": f"<= {int(row['covered_prime_limit']):,}",
                "proxy_ms": float(row["accelerated"]["total_proxy_time_ms"]),
                "mr_ms": float(row["accelerated"]["total_miller_rabin_time_ms"]),
                "assembly_ms": float(row["accelerated"]["total_assembly_time_ms"]),
                "residual_ms": float(row["accelerated"]["total_residual_time_ms"]),
            }
        )

    totals = [
        cell["proxy_ms"] + cell["mr_ms"] + cell["assembly_ms"] + cell["residual_ms"]
        for cell in cells
    ]
    y_max = max(totals) * 1.15
    plot_width = SVG_WIDTH - SVG_MARGIN_LEFT - SVG_MARGIN_RIGHT
    plot_height = SVG_HEIGHT - SVG_MARGIN_TOP - SVG_MARGIN_BOTTOM
    slot_width = plot_width / len(cells)
    bar_width = slot_width * 0.58

    def y_coord(value: float) -> float:
        return SVG_MARGIN_TOP + plot_height - (value / y_max) * plot_height

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_WIDTH}" height="{SVG_HEIGHT}" viewBox="0 0 {SVG_WIDTH} {SVG_HEIGHT}">',
        '<rect width="100%" height="100%" fill="#fcfbf7" />',
        '<text x="95" y="46" font-family="Menlo, Monaco, monospace" font-size="26" fill="#1f2933">8192-bit RSA timing breakdown by table depth</text>',
        '<text x="95" y="72" font-family="Menlo, Monaco, monospace" font-size="14" fill="#52606d">Stacked end-to-end wall time per deterministic sweep cell</text>',
    ]

    for tick_index in range(6):
        tick_value = y_max * tick_index / 5.0
        y = y_coord(tick_value)
        parts.append(
            f'<line x1="{SVG_MARGIN_LEFT}" y1="{y:.2f}" x2="{SVG_WIDTH - SVG_MARGIN_RIGHT}" y2="{y:.2f}" stroke="#d9e2ec" stroke-width="1" />'
        )
        parts.append(
            f'<text x="{SVG_MARGIN_LEFT - 14}" y="{y + 5:.2f}" text-anchor="end" font-family="Menlo, Monaco, monospace" font-size="13" fill="#486581">{tick_value / 1000.0:.1f}s</text>'
        )

    axis_bottom = SVG_HEIGHT - SVG_MARGIN_BOTTOM
    parts.append(
        f'<line x1="{SVG_MARGIN_LEFT}" y1="{axis_bottom}" x2="{SVG_WIDTH - SVG_MARGIN_RIGHT}" y2="{axis_bottom}" stroke="#243b53" stroke-width="1.5" />'
    )
    parts.append(
        f'<line x1="{SVG_MARGIN_LEFT}" y1="{SVG_MARGIN_TOP}" x2="{SVG_MARGIN_LEFT}" y2="{axis_bottom}" stroke="#243b53" stroke-width="1.5" />'
    )

    segments = [
        ("proxy_ms", "proxy"),
        ("mr_ms", "mr"),
        ("assembly_ms", "assembly"),
        ("residual_ms", "residual"),
    ]

    for index, cell in enumerate(cells):
        x_center = SVG_MARGIN_LEFT + slot_width * (index + 0.5)
        bar_x = x_center - bar_width / 2.0
        running = 0.0
        total = totals[index]
        for field, color_key in segments:
            segment = float(cell[field])
            if segment <= 0.0:
                continue
            y_top = y_coord(running + segment)
            y_bottom = y_coord(running)
            parts.append(
                f'<rect x="{bar_x:.2f}" y="{y_top:.2f}" width="{bar_width:.2f}" height="{y_bottom - y_top:.2f}" fill="{STACK_COLORS[color_key]}" />'
            )
            running += segment
        parts.append(
            f'<text x="{x_center:.2f}" y="{y_coord(total) - 10:.2f}" text-anchor="middle" font-family="Menlo, Monaco, monospace" font-size="13" fill="#243b53">{total / 1000.0:.1f}s</text>'
        )
        parts.append(
            f'<text x="{x_center:.2f}" y="{axis_bottom + 26:.2f}" text-anchor="middle" font-family="Menlo, Monaco, monospace" font-size="13" fill="#243b53">{cell["label"]}</text>'
        )

    legend_x = SVG_WIDTH - SVG_MARGIN_RIGHT - 210
    legend_y = SVG_MARGIN_TOP + 16
    legend_entries = [
        ("proxy", "proxy filtering"),
        ("mr", "survivor MR"),
        ("assembly", "assembly + validation"),
        ("residual", "residual search overhead"),
    ]
    for index, (color_key, label) in enumerate(legend_entries):
        y = legend_y + index * 24
        parts.append(
            f'<rect x="{legend_x}" y="{y - 10:.2f}" width="16" height="16" fill="{STACK_COLORS[color_key]}" />'
        )
        parts.append(
            f'<text x="{legend_x + 24}" y="{y + 3:.2f}" font-family="Menlo, Monaco, monospace" font-size="13" fill="#243b53">{label}</text>'
        )

    parts.append(
        f'<text x="{(SVG_MARGIN_LEFT + SVG_WIDTH - SVG_MARGIN_RIGHT) / 2.0:.2f}" y="{SVG_HEIGHT - 28}" text-anchor="middle" font-family="Menlo, Monaco, monospace" font-size="14" fill="#243b53">Baseline and accelerated depth cells</text>'
    )
    parts.append(
        f'<text x="24" y="{(SVG_MARGIN_TOP + axis_bottom) / 2.0:.2f}" transform="rotate(-90 24 {(SVG_MARGIN_TOP + axis_bottom) / 2.0:.2f})" text-anchor="middle" font-family="Menlo, Monaco, monospace" font-size="14" fill="#243b53">Total wall time</text>'
    )
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def build_markdown_report(results: Dict[str, object]) -> str:
    """Build a compact Markdown report for the RSA table-depth sweep."""
    baseline = results["baseline"]
    rows = results["rows"]
    lines = [
        "# RSA Table-Depth Sweep",
        "",
        f"Date: {results['experiment_date']}",
        "",
        "This sweep holds the deterministic RSA workload fixed at the first end-to-end regime that uses `4096`-bit prime candidates, then measures how deeper covered odd-prime tables change rejection, Miller-Rabin work, and wall time.",
        "",
        "## Configuration",
        "",
        f"- `rsa_bits`: {results['configuration']['rsa_bits']}",
        f"- `prime_bits`: {results['configuration']['prime_bits']}",
        f"- `keypair_count`: {results['configuration']['keypair_count']}",
        f"- `public_exponent`: {results['configuration']['public_exponent']}",
        f"- `table_limits`: {results['configuration']['table_limits']}",
        "",
        "## Headline Findings",
        "",
        f"- Baseline Miller-Rabin-only key generation took `{baseline['total_wall_time_ms'] / 1000.0:.3f}` s total for `{baseline['keypair_count']}` deterministic keypairs.",
    ]

    best_row = max(rows, key=lambda row: float(row["speedup"]))
    lines.append(
        f"- The fastest accelerated cell used covered odd primes through `{int(best_row['covered_prime_limit']):,}` and ran in `{float(best_row['accelerated']['total_wall_time_ms']) / 1000.0:.3f}` s for a measured `{float(best_row['speedup']):.3f}x` speedup."
    )
    lines.append(
        f"- In that best cell, proxy rejection was `{float(best_row['proxy_rejection_rate']):.2%}` against a structural ceiling of `{float(best_row['theoretical_rejection_rate']):.2%}`."
    )

    lines.extend(
        [
            "",
            "## Sweep Summary",
            "",
            "| Covered odd primes | Theory rejection | Observed rejection | Saved MR call rate | Speedup | Accelerated wall time (s) | Proxy time (s) | Survivor MR time (s) |",
            "|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )

    for row in rows:
        accelerated = row["accelerated"]
        lines.append(
            f"| {int(row['covered_prime_limit']):,} | {float(row['theoretical_rejection_rate']):.6%} | {float(row['proxy_rejection_rate']):.6%} | {float(row['saved_miller_rabin_call_rate']):.6%} | {float(row['speedup']):.6f}x | {float(accelerated['total_wall_time_ms']) / 1000.0:.6f} | {float(accelerated['total_proxy_time_ms']) / 1000.0:.6f} | {float(accelerated['total_miller_rabin_time_ms']) / 1000.0:.6f} |"
        )

    lines.extend(
        [
            "",
            "## Baseline Reference",
            "",
            "| Metric | Value |",
            "|---|---:|",
            f"| Total wall time (s) | {float(baseline['total_wall_time_ms']) / 1000.0:.6f} |",
            f"| Mean time per keypair (s) | {float(baseline['mean_time_per_keypair_ms']) / 1000.0:.6f} |",
            f"| Total candidates tested | {int(baseline['total_candidates_tested'])} |",
            f"| Total Miller-Rabin calls | {int(baseline['total_miller_rabin_calls'])} |",
            f"| Survivor Miller-Rabin time (s) | {float(baseline['total_miller_rabin_time_ms']) / 1000.0:.6f} |",
            f"| Assembly + validation time (s) | {float(baseline['total_assembly_time_ms']) / 1000.0:.6f} |",
            "",
            "## Reproduction",
            "",
            "```bash",
            results["reproduction_command"],
            "```",
            "",
            "Artifacts written by this sweep:",
            "",
            "- `rsa_table_depth_sweep_results.json`",
            "- `rsa_table_depth_sweep_results.csv`",
            "- `RSA_TABLE_DEPTH_SWEEP_REPORT.md`",
            "- `rsa_depth_speedup.svg`",
            "- `rsa_depth_rejection.svg`",
            "- `rsa_depth_timing_breakdown.svg`",
            "",
        ]
    )
    return "\n".join(lines)


def run_sweep(
    output_dir: Path,
    rsa_bits: int,
    keypair_count: int,
    table_limits: Sequence[int],
    chunk_size: int,
    primary_limit: int,
    tail_limit: int,
    public_exponent: int,
    namespace: str,
) -> Dict[str, object]:
    """Run the deterministic end-to-end RSA table-depth sweep."""
    if rsa_bits < 4 or rsa_bits % 2 != 0:
        raise ValueError("rsa_bits must be an even integer greater than or equal to 4")
    if keypair_count < 1:
        raise ValueError("keypair_count must be at least 1")

    prime_bits = rsa_bits // 2
    baseline, baseline_keypairs = rsa_benchmark.summarize_keygen_path(
        rsa_bits,
        keypair_count,
        public_exponent,
        rsa_benchmark.benchmark.DEFAULT_MR_BASES,
        namespace=namespace,
        use_proxy=False,
    )

    rows: List[Dict[str, object]] = []
    for table_limit in table_limits:
        tables = depth_sweep.build_interval_tables(
            table_limit=table_limit,
            chunk_size=chunk_size,
            primary_limit=primary_limit,
            tail_limit=tail_limit,
        )
        accelerated, accelerated_keypairs = rsa_benchmark.summarize_keygen_path(
            rsa_bits,
            keypair_count,
            public_exponent,
            rsa_benchmark.benchmark.DEFAULT_MR_BASES,
            namespace=namespace,
            use_proxy=True,
            prime_table=tables["primary_table"],
            tail_prime_table=tables["tail_table"],
            deep_tail_prime_table=tables["deep_tail_table"],
            deep_tail_min_bits=tables["deep_tail_min_bits"],
        )
        rsa_benchmark.compare_keypair_sets(baseline_keypairs, accelerated_keypairs)

        rows.append(
            {
                "covered_prime_limit": table_limit,
                "covered_prime_count": sum(1 for _ in depth_sweep.primerange(3, table_limit + 1)),
                "theoretical_rejection_rate": depth_sweep.structural_rejection_rate(table_limit),
                "speedup": baseline["total_wall_time_ms"] / accelerated["total_wall_time_ms"],
                "proxy_rejection_rate": accelerated["proxy_rejection_rate"],
                "saved_miller_rabin_call_rate": (
                    (baseline["total_miller_rabin_calls"] - accelerated["total_miller_rabin_calls"])
                    / baseline["total_miller_rabin_calls"]
                    if baseline["total_miller_rabin_calls"]
                    else 0.0
                ),
                "saved_miller_rabin_calls": (
                    baseline["total_miller_rabin_calls"] - accelerated["total_miller_rabin_calls"]
                ),
                "accelerated": accelerated,
            }
        )

    fixed_points = rsa_benchmark.confirm_prime_fixed_points(baseline_keypairs)
    output_dir.mkdir(parents=True, exist_ok=True)

    results = {
        "experiment_date": time.strftime("%Y-%m-%d"),
        "configuration": {
            "rsa_bits": rsa_bits,
            "prime_bits": prime_bits,
            "keypair_count": keypair_count,
            "table_limits": list(table_limits),
            "chunk_size": chunk_size,
            "primary_limit": primary_limit,
            "tail_limit": tail_limit,
            "public_exponent": public_exponent,
            "namespace": namespace,
        },
        "baseline": baseline,
        "prime_fixed_points": fixed_points,
        "rows": rows,
        "reproduction_command": (
            "python3 benchmarks/python/rsa_table_depth_sweep.py "
            f"--output-dir {output_dir} "
            f"--rsa-bits {rsa_bits} "
            f"--keypair-count {keypair_count} "
            f"--table-limits {' '.join(str(limit) for limit in table_limits)} "
            f"--chunk-size {chunk_size} "
            f"--primary-limit {primary_limit} "
            f"--tail-limit {tail_limit} "
            f"--public-exponent {public_exponent} "
            f"--namespace {namespace}"
        ),
    }

    json_path = output_dir / "rsa_table_depth_sweep_results.json"
    csv_path = output_dir / "rsa_table_depth_sweep_results.csv"
    markdown_path = output_dir / "RSA_TABLE_DEPTH_SWEEP_REPORT.md"
    speedup_svg_path = output_dir / "rsa_depth_speedup.svg"
    rejection_svg_path = output_dir / "rsa_depth_rejection.svg"
    timing_svg_path = output_dir / "rsa_depth_timing_breakdown.svg"

    json_path.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    csv_rows = [
        {
            "covered_prime_limit": int(row["covered_prime_limit"]),
            "covered_prime_count": int(row["covered_prime_count"]),
            "theoretical_rejection_rate": f"{float(row['theoretical_rejection_rate']):.12f}",
            "observed_rejection_rate": f"{float(row['proxy_rejection_rate']):.12f}",
            "saved_miller_rabin_call_rate": f"{float(row['saved_miller_rabin_call_rate']):.12f}",
            "saved_miller_rabin_calls": int(row["saved_miller_rabin_calls"]),
            "speedup": f"{float(row['speedup']):.12f}",
            "accelerated_total_wall_time_ms": f"{float(row['accelerated']['total_wall_time_ms']):.12f}",
            "accelerated_proxy_time_ms": f"{float(row['accelerated']['total_proxy_time_ms']):.12f}",
            "accelerated_miller_rabin_time_ms": f"{float(row['accelerated']['total_miller_rabin_time_ms']):.12f}",
            "accelerated_assembly_time_ms": f"{float(row['accelerated']['total_assembly_time_ms']):.12f}",
            "accelerated_residual_time_ms": f"{float(row['accelerated']['total_residual_time_ms']):.12f}",
        }
        for row in rows
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(csv_rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(csv_rows)
    markdown_path.write_text(build_markdown_report(results), encoding="utf-8")
    speedup_svg_path.write_text(render_speedup_svg(results), encoding="utf-8")
    rejection_svg_path.write_text(render_rejection_svg(results), encoding="utf-8")
    timing_svg_path.write_text(render_timing_breakdown_svg(results), encoding="utf-8")
    return results


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Deterministic end-to-end RSA sweep versus covered prime depth."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for JSON, CSV, Markdown, and SVG artifacts.",
    )
    parser.add_argument(
        "--rsa-bits",
        type=int,
        default=DEFAULT_RSA_BITS,
        help=f"RSA modulus bits for the sweep (default: {DEFAULT_RSA_BITS}).",
    )
    parser.add_argument(
        "--keypair-count",
        type=int,
        default=DEFAULT_KEYPAIR_COUNT,
        help=f"Deterministic keypairs to generate in each cell (default: {DEFAULT_KEYPAIR_COUNT}).",
    )
    parser.add_argument(
        "--table-limits",
        type=int,
        nargs="+",
        default=DEFAULT_TABLE_LIMITS,
        help="Covered odd-prime limits to sweep.",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=rsa_benchmark.benchmark.DEFAULT_PROXY_CHUNK_SIZE,
        help="Primes folded into each deterministic GCD batch.",
    )
    parser.add_argument(
        "--primary-limit",
        type=int,
        default=rsa_benchmark.benchmark.DEFAULT_PROXY_TRIAL_PRIME_LIMIT,
        help="Upper bound of the primary interval.",
    )
    parser.add_argument(
        "--tail-limit",
        type=int,
        default=rsa_benchmark.benchmark.DEFAULT_PROXY_TAIL_PRIME_LIMIT,
        help="Upper bound of the tail interval.",
    )
    parser.add_argument(
        "--public-exponent",
        type=int,
        default=rsa_benchmark.DEFAULT_PUBLIC_EXPONENT,
        help=(
            "RSA public exponent used for every sweep cell "
            f"(default: {rsa_benchmark.DEFAULT_PUBLIC_EXPONENT})."
        ),
    )
    parser.add_argument(
        "--namespace",
        type=str,
        default=DEFAULT_NAMESPACE,
        help="Deterministic namespace for candidate streams.",
    )
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    """Run the sweep and print a compact terminal summary."""
    args = parse_args(argv)
    results = run_sweep(
        output_dir=args.output_dir,
        rsa_bits=args.rsa_bits,
        keypair_count=args.keypair_count,
        table_limits=parse_int_list([str(value) for value in args.table_limits]),
        chunk_size=args.chunk_size,
        primary_limit=args.primary_limit,
        tail_limit=args.tail_limit,
        public_exponent=args.public_exponent,
        namespace=args.namespace,
    )
    print("rsa table depth sweep complete")
    print(
        "baseline:",
        f"{float(results['baseline']['total_wall_time_ms']) / 1000.0:.3f}s",
        f"for {results['baseline']['keypair_count']} keypairs",
    )
    for row in results["rows"]:
        print(
            f"<= {int(row['covered_prime_limit']):,}:",
            f"{float(row['speedup']):.3f}x speedup,",
            f"{float(row['proxy_rejection_rate']):.2%} rejection,",
            f"{float(row['accelerated']['total_wall_time_ms']) / 1000.0:.3f}s accelerated wall time",
        )
    print(f"artifacts: {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
