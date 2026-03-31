#!/usr/bin/env python3
"""Deterministic sweep of rejection collapse by covered prime-table depth."""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
import time
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

from sympy import primerange


ROOT = Path(__file__).resolve().parents[3]
MODULE_DIR = Path(__file__).resolve().parent
if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))

import candidate_benchmark as benchmark


DEFAULT_OUTPUT_DIR = ROOT / "benchmarks" / "output" / "python" / "prefilter" / "table_depth_sweep"
DEFAULT_BIT_LENGTHS = [2048, 4096, 8192, 16384]
DEFAULT_TABLE_LIMITS = [300007, 1000003, 3000000]
DEFAULT_CANDIDATE_COUNT = 1024
DEFAULT_NAMESPACE = "cdl-table-depth-sweep"
SVG_WIDTH = 1200
SVG_HEIGHT = 760
SVG_MARGIN_LEFT = 95
SVG_MARGIN_RIGHT = 180
SVG_MARGIN_TOP = 90
SVG_MARGIN_BOTTOM = 90
SERIES_COLORS = ["#0b6e4f", "#c84c09", "#2b59c3", "#8b1e3f", "#6a4c93"]


def parse_int_list(values: Sequence[str]) -> List[int]:
    """Parse a list of positive integers from argv tokens."""
    parsed = [int(value) for value in values]
    if not parsed:
        raise ValueError("at least one integer value is required")
    if any(value < 2 for value in parsed):
        raise ValueError("all values must be at least 2")
    return parsed


def odd_prime_density_estimate(bit_length: int) -> float:
    """Return the asymptotic prime density among odd integers near the given size."""
    return 2.0 / (bit_length * math.log(2.0))


def structural_survivor_rate(table_limit: int) -> float:
    """Return the odd-integer survivor rate after screening odd primes up to the limit."""
    survivor = 1.0
    for prime in primerange(3, table_limit + 1):
        survivor *= 1.0 - (1.0 / prime)
    return survivor


def structural_rejection_rate(table_limit: int) -> float:
    """Return the odd-integer rejection rate induced by the covered odd primes."""
    return 1.0 - structural_survivor_rate(table_limit)


def build_interval_tables(
    table_limit: int,
    chunk_size: int,
    primary_limit: int,
    tail_limit: int,
) -> Dict[str, object]:
    """Build the exact interval stack needed to cover odd primes up to one total limit."""
    if primary_limit < 3:
        raise ValueError("primary_limit must be at least 3")
    if tail_limit <= primary_limit:
        raise ValueError("tail_limit must exceed primary_limit")
    if table_limit < 3:
        raise ValueError("table_limit must be at least 3")

    if table_limit <= primary_limit:
        primary_table = benchmark.WheelPrimeTable(table_limit, chunk_size)
        return {
            "primary_table": primary_table,
            "tail_table": None,
            "deep_tail_table": None,
            "deep_tail_min_bits": None,
            "covered_prime_limit": table_limit,
        }

    primary_table = benchmark.WheelPrimeTable(primary_limit, chunk_size)
    if table_limit <= tail_limit:
        tail_table = benchmark.WheelPrimeTable(
            table_limit,
            chunk_size,
            start_exclusive=primary_limit,
        )
        return {
            "primary_table": primary_table,
            "tail_table": tail_table,
            "deep_tail_table": None,
            "deep_tail_min_bits": None,
            "covered_prime_limit": table_limit,
        }

    tail_table = benchmark.WheelPrimeTable(
        tail_limit,
        chunk_size,
        start_exclusive=primary_limit,
    )
    deep_tail_table = benchmark.WheelPrimeTable(
        table_limit,
        chunk_size,
        start_exclusive=tail_limit,
    )
    return {
        "primary_table": primary_table,
        "tail_table": tail_table,
        "deep_tail_table": deep_tail_table,
        "deep_tail_min_bits": 2,
        "covered_prime_limit": table_limit,
    }


def run_panel(
    bit_length: int,
    candidates: Sequence[int],
    table_limit: int,
    chunk_size: int,
    primary_limit: int,
    tail_limit: int,
) -> Dict[str, object]:
    """Measure one observed rejection panel against one fixed covered-prime limit."""
    tables = build_interval_tables(
        table_limit=table_limit,
        chunk_size=chunk_size,
        primary_limit=primary_limit,
        tail_limit=tail_limit,
    )
    primary_table = tables["primary_table"]
    tail_table = tables["tail_table"]
    deep_tail_table = tables["deep_tail_table"]
    deep_tail_min_bits = tables["deep_tail_min_bits"]

    factor_source_counts = {"primary": 0, "tail": 0, "deep_tail": 0, "survivor": 0, "even": 0}
    rejected = 0
    durations_ns: List[int] = []

    for candidate in candidates:
        start_ns = time.perf_counter_ns()
        proxy = benchmark.cheap_cdl_proxy(
            candidate,
            primary_table,
            tail_prime_table=tail_table,
            deep_tail_prime_table=deep_tail_table,
            deep_tail_min_bits=deep_tail_min_bits,
        )
        durations_ns.append(time.perf_counter_ns() - start_ns)
        factor_source = str(proxy["factor_source"])
        factor_source_counts[factor_source] = factor_source_counts.get(factor_source, 0) + 1
        if bool(proxy["rejected"]):
            rejected += 1

    count = len(candidates)
    observed_rejection_rate = rejected / count
    theoretical_rejection_rate = structural_rejection_rate(table_limit)
    odd_prime_density = odd_prime_density_estimate(bit_length)
    standard_error = math.sqrt(
        observed_rejection_rate * (1.0 - observed_rejection_rate) / count
    )

    return {
        "bit_length": bit_length,
        "candidate_count": count,
        "covered_prime_limit": table_limit,
        "covered_prime_count": sum(1 for _ in primerange(3, table_limit + 1)),
        "observed_rejection_rate": observed_rejection_rate,
        "theoretical_rejection_rate": theoretical_rejection_rate,
        "observed_minus_theory": observed_rejection_rate - theoretical_rejection_rate,
        "observed_standard_error": standard_error,
        "odd_prime_density_estimate": odd_prime_density,
        "odd_prime_reciprocal_density_estimate": 1.0 / odd_prime_density,
        "proxy_timing_ms": benchmark.summarize_durations_ms(durations_ns),
        "factor_source_counts": factor_source_counts,
        "intervals": {
            "primary_limit": primary_table.limit,
            "tail_limit": tail_table.limit if tail_table is not None else 0,
            "deep_tail_limit": deep_tail_table.limit if deep_tail_table is not None else 0,
            "deep_tail_min_bits": deep_tail_min_bits or 0,
        },
    }


def summarize_limit(rows: Sequence[Dict[str, object]]) -> Dict[str, float | int]:
    """Summarize observed spread across bit lengths for one table limit."""
    observed_rates = [float(row["observed_rejection_rate"]) for row in rows]
    theoretical_rate = float(rows[0]["theoretical_rejection_rate"])
    return {
        "covered_prime_limit": int(rows[0]["covered_prime_limit"]),
        "theoretical_rejection_rate": theoretical_rate,
        "observed_min_rejection_rate": min(observed_rates),
        "observed_max_rejection_rate": max(observed_rates),
        "observed_spread_percentage_points": (max(observed_rates) - min(observed_rates)) * 100.0,
        "asymptotic_speedup_if_proxy_free": 1.0 / (1.0 - theoretical_rate),
    }


def svg_x(bit_index: int, bit_count: int) -> float:
    """Map one bit-length index to an SVG x coordinate."""
    plot_width = SVG_WIDTH - SVG_MARGIN_LEFT - SVG_MARGIN_RIGHT
    if bit_count == 1:
        return SVG_MARGIN_LEFT + (plot_width / 2.0)
    return SVG_MARGIN_LEFT + (plot_width * bit_index / (bit_count - 1))


def svg_y(rate: float, y_min: float, y_max: float) -> float:
    """Map one rejection rate to an SVG y coordinate."""
    plot_height = SVG_HEIGHT - SVG_MARGIN_TOP - SVG_MARGIN_BOTTOM
    return SVG_MARGIN_TOP + ((y_max - rate) / (y_max - y_min)) * plot_height


def render_svg(
    rows: Sequence[Dict[str, object]],
    summaries: Sequence[Dict[str, float | int]],
    bit_lengths: Sequence[int],
) -> str:
    """Render one dependency-free SVG plot for the observed and theoretical rates."""
    all_rates = [float(row["observed_rejection_rate"]) for row in rows]
    all_rates.extend(float(summary["theoretical_rejection_rate"]) for summary in summaries)
    y_min = math.floor((min(all_rates) * 100.0 - 1.0) / 0.5) * 0.005
    y_max = math.ceil((max(all_rates) * 100.0 + 1.0) / 0.5) * 0.005
    y_min = max(0.0, y_min)
    y_max = min(1.0, y_max)
    tick_count = 6

    grouped_rows = {
        int(summary["covered_prime_limit"]): [
            row for row in rows if int(row["covered_prime_limit"]) == int(summary["covered_prime_limit"])
        ]
        for summary in summaries
    }

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_WIDTH}" height="{SVG_HEIGHT}" viewBox="0 0 {SVG_WIDTH} {SVG_HEIGHT}">',
        '<rect width="100%" height="100%" fill="#fcfbf7" />',
        '<text x="95" y="46" font-family="Menlo, Monaco, monospace" font-size="26" fill="#1f2933">Structural rejection collapse by table depth</text>',
        '<text x="95" y="72" font-family="Menlo, Monaco, monospace" font-size="14" fill="#52606d">Observed proxy rejection across deterministic odd candidate corpora, with exact structural ceilings for each covered prime limit</text>',
    ]

    for tick_index in range(tick_count + 1):
        fraction = tick_index / tick_count
        tick_rate = y_min + (y_max - y_min) * fraction
        y_value = svg_y(tick_rate, y_min, y_max)
        parts.append(
            f'<line x1="{SVG_MARGIN_LEFT}" y1="{y_value:.2f}" x2="{SVG_WIDTH - SVG_MARGIN_RIGHT}" y2="{y_value:.2f}" stroke="#d9e2ec" stroke-width="1" />'
        )
        parts.append(
            f'<text x="{SVG_MARGIN_LEFT - 14}" y="{y_value + 5:.2f}" text-anchor="end" font-family="Menlo, Monaco, monospace" font-size="13" fill="#486581">{tick_rate * 100.0:.1f}%</text>'
        )

    x_axis_y = SVG_HEIGHT - SVG_MARGIN_BOTTOM
    parts.append(
        f'<line x1="{SVG_MARGIN_LEFT}" y1="{x_axis_y}" x2="{SVG_WIDTH - SVG_MARGIN_RIGHT}" y2="{x_axis_y}" stroke="#243b53" stroke-width="1.5" />'
    )
    parts.append(
        f'<line x1="{SVG_MARGIN_LEFT}" y1="{SVG_MARGIN_TOP}" x2="{SVG_MARGIN_LEFT}" y2="{x_axis_y}" stroke="#243b53" stroke-width="1.5" />'
    )

    for bit_index, bit_length in enumerate(bit_lengths):
        x_value = svg_x(bit_index, len(bit_lengths))
        parts.append(
            f'<line x1="{x_value:.2f}" y1="{SVG_MARGIN_TOP}" x2="{x_value:.2f}" y2="{x_axis_y}" stroke="#e4e7eb" stroke-width="1" />'
        )
        parts.append(
            f'<text x="{x_value:.2f}" y="{x_axis_y + 28}" text-anchor="middle" font-family="Menlo, Monaco, monospace" font-size="13" fill="#243b53">{bit_length}</text>'
        )

    parts.append(
        f'<text x="{(SVG_MARGIN_LEFT + SVG_WIDTH - SVG_MARGIN_RIGHT) / 2.0:.2f}" y="{SVG_HEIGHT - 28}" text-anchor="middle" font-family="Menlo, Monaco, monospace" font-size="14" fill="#243b53">Candidate bit length</text>'
    )
    parts.append(
        f'<text x="24" y="{(SVG_MARGIN_TOP + x_axis_y) / 2.0:.2f}" transform="rotate(-90 24 {(SVG_MARGIN_TOP + x_axis_y) / 2.0:.2f})" text-anchor="middle" font-family="Menlo, Monaco, monospace" font-size="14" fill="#243b53">Composite rejection rate</text>'
    )

    for color_index, summary in enumerate(summaries):
        color = SERIES_COLORS[color_index % len(SERIES_COLORS)]
        limit = int(summary["covered_prime_limit"])
        theory_rate = float(summary["theoretical_rejection_rate"])
        y_value = svg_y(theory_rate, y_min, y_max)
        parts.append(
            f'<line x1="{SVG_MARGIN_LEFT}" y1="{y_value:.2f}" x2="{SVG_WIDTH - SVG_MARGIN_RIGHT}" y2="{y_value:.2f}" stroke="{color}" stroke-width="2" stroke-dasharray="8 6" opacity="0.65" />'
        )
        ordered_rows = sorted(grouped_rows[limit], key=lambda row: int(row["bit_length"]))
        polyline_points = " ".join(
            f"{svg_x(bit_index, len(bit_lengths)):.2f},{svg_y(float(row['observed_rejection_rate']), y_min, y_max):.2f}"
            for bit_index, row in enumerate(ordered_rows)
        )
        parts.append(
            f'<polyline fill="none" stroke="{color}" stroke-width="3.5" points="{polyline_points}" />'
        )
        for bit_index, row in enumerate(ordered_rows):
            x_value = svg_x(bit_index, len(bit_lengths))
            y_point = svg_y(float(row["observed_rejection_rate"]), y_min, y_max)
            parts.append(
                f'<circle cx="{x_value:.2f}" cy="{y_point:.2f}" r="5.5" fill="{color}" stroke="#fcfbf7" stroke-width="2" />'
            )

    legend_x = SVG_WIDTH - SVG_MARGIN_RIGHT + 24
    legend_y = SVG_MARGIN_TOP + 24
    parts.append(
        f'<text x="{legend_x}" y="{legend_y - 14}" font-family="Menlo, Monaco, monospace" font-size="14" fill="#243b53">Covered odd primes</text>'
    )
    for color_index, summary in enumerate(summaries):
        color = SERIES_COLORS[color_index % len(SERIES_COLORS)]
        limit = int(summary["covered_prime_limit"])
        y_value = legend_y + color_index * 58
        parts.append(
            f'<line x1="{legend_x}" y1="{y_value:.2f}" x2="{legend_x + 34}" y2="{y_value:.2f}" stroke="{color}" stroke-width="3.5" />'
        )
        parts.append(
            f'<line x1="{legend_x}" y1="{y_value + 14:.2f}" x2="{legend_x + 34}" y2="{y_value + 14:.2f}" stroke="{color}" stroke-width="2" stroke-dasharray="8 6" opacity="0.65" />'
        )
        parts.append(
            f'<text x="{legend_x + 44}" y="{y_value + 5:.2f}" font-family="Menlo, Monaco, monospace" font-size="13" fill="#243b53">≤ {limit:,}</text>'
        )
        parts.append(
            f'<text x="{legend_x + 44}" y="{y_value + 20:.2f}" font-family="Menlo, Monaco, monospace" font-size="12" fill="#52606d">observed / theory {float(summary["theoretical_rejection_rate"]) * 100.0:.2f}%</text>'
        )

    parts.append(
        f'<text x="{SVG_WIDTH - SVG_MARGIN_RIGHT}" y="{SVG_HEIGHT - 58}" text-anchor="end" font-family="Menlo, Monaco, monospace" font-size="12" fill="#52606d">solid: observed deterministic corpus rejection</text>'
    )
    parts.append(
        f'<text x="{SVG_WIDTH - SVG_MARGIN_RIGHT}" y="{SVG_HEIGHT - 38}" text-anchor="end" font-family="Menlo, Monaco, monospace" font-size="12" fill="#52606d">dashed: exact structural ceiling from covered small-prime set</text>'
    )
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def build_markdown_report(results: Dict[str, object]) -> str:
    """Build a compact Markdown report for the structural depth sweep."""
    rows = results["rows"]
    summaries = results["summaries"]
    bit_lengths = results["configuration"]["bit_lengths"]
    density_lines = [
        f"- `{bit_length}` bits: odd-candidate prime density estimate `{odd_prime_density_estimate(bit_length):.6%}`"
        for bit_length in bit_lengths
    ]

    lines = [
        "# Table-Depth Structural Sweep",
        "",
        f"Date: {results['experiment_date']}",
        "",
        "This sweep fixes the covered odd-prime limit, varies candidate bit length, and measures whether proxy rejection stays locked to the covered small-factor layer instead of following prime density.",
        "",
        "## Headline Findings",
        "",
    ]

    for summary in summaries:
        lines.append(
            f"- With covered odd primes through `{int(summary['covered_prime_limit']):,}`, the exact structural rejection ceiling is `{float(summary['theoretical_rejection_rate']):.2%}` and the observed spread across the bit-length sweep was `{float(summary['observed_spread_percentage_points']):.3f}` percentage points."
        )

    lines.extend(
        [
            "",
            "## Odd-Candidate Prime Density Reference",
            "",
            *density_lines,
            "",
            "## Per-Panel Results",
            "",
            "| Covered odd primes | Bit length | Candidates | Observed rejection | Theory | Observed - theory | Proxy mean (ms) |",
            "|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )

    for row in rows:
        lines.append(
            f"| {int(row['covered_prime_limit']):,} | {int(row['bit_length'])} | {int(row['candidate_count'])} | {float(row['observed_rejection_rate']):.6%} | {float(row['theoretical_rejection_rate']):.6%} | {float(row['observed_minus_theory']):+.6%} | {float(row['proxy_timing_ms']['mean']):.6f} |"
        )

    lines.extend(
        [
            "",
            "## Sweep Summary",
            "",
            "| Covered odd primes | Theory rejection | Observed min | Observed max | Spread (pp) | Ideal MR-only speedup ceiling |",
            "|---:|---:|---:|---:|---:|---:|",
        ]
    )

    for summary in summaries:
        lines.append(
            f"| {int(summary['covered_prime_limit']):,} | {float(summary['theoretical_rejection_rate']):.6%} | {float(summary['observed_min_rejection_rate']):.6%} | {float(summary['observed_max_rejection_rate']):.6%} | {float(summary['observed_spread_percentage_points']):.3f} | {float(summary['asymptotic_speedup_if_proxy_free']):.6f}x |"
        )

    lines.extend(
        [
            "",
            "## Reproduction",
            "",
            "```bash",
            results["reproduction_command"],
            "```",
            "",
            "Artifacts written by this sweep:",
            "",
            "- `table_depth_sweep_results.json`",
            "- `table_depth_sweep_results.csv`",
            "- `TABLE_DEPTH_SWEEP_REPORT.md`",
            "- `table_depth_collapse.svg`",
            "",
        ]
    )
    return "\n".join(lines)


def run_sweep(
    output_dir: Path,
    bit_lengths: Sequence[int],
    table_limits: Sequence[int],
    candidate_count: int,
    chunk_size: int,
    primary_limit: int,
    tail_limit: int,
    namespace: str,
) -> Dict[str, object]:
    """Run the deterministic structural depth sweep and write local artifacts."""
    if candidate_count < 1:
        raise ValueError("candidate_count must be at least 1")
    if len(bit_lengths) < 1:
        raise ValueError("bit_lengths must not be empty")
    if len(table_limits) < 1:
        raise ValueError("table_limits must not be empty")

    candidate_sets = {
        bit_length: benchmark.deterministic_odd_candidates(
            bit_length,
            candidate_count,
            namespace=f"{namespace}:{bit_length}",
        )
        for bit_length in bit_lengths
    }

    rows: List[Dict[str, object]] = []
    for table_limit in table_limits:
        for bit_length in bit_lengths:
            rows.append(
                run_panel(
                    bit_length=bit_length,
                    candidates=candidate_sets[bit_length],
                    table_limit=table_limit,
                    chunk_size=chunk_size,
                    primary_limit=primary_limit,
                    tail_limit=tail_limit,
                )
            )

    summaries = [
        summarize_limit(
            [row for row in rows if int(row["covered_prime_limit"]) == table_limit]
        )
        for table_limit in table_limits
    ]

    output_dir.mkdir(parents=True, exist_ok=True)
    svg_text = render_svg(rows, summaries, bit_lengths)
    results = {
        "experiment_date": time.strftime("%Y-%m-%d"),
        "configuration": {
            "bit_lengths": list(bit_lengths),
            "table_limits": list(table_limits),
            "candidate_count": candidate_count,
            "chunk_size": chunk_size,
            "primary_limit": primary_limit,
            "tail_limit": tail_limit,
            "namespace": namespace,
        },
        "rows": rows,
        "summaries": summaries,
        "reproduction_command": (
            "python3 benchmarks/python/prefilter/table_depth_sweep.py "
            f"--output-dir {output_dir} "
            f"--bit-lengths {' '.join(str(value) for value in bit_lengths)} "
            f"--table-limits {' '.join(str(value) for value in table_limits)} "
            f"--candidate-count {candidate_count} "
            f"--chunk-size {chunk_size} "
            f"--primary-limit {primary_limit} "
            f"--tail-limit {tail_limit} "
            f"--namespace {namespace}"
        ),
    }

    json_path = output_dir / "table_depth_sweep_results.json"
    csv_path = output_dir / "table_depth_sweep_results.csv"
    markdown_path = output_dir / "TABLE_DEPTH_SWEEP_REPORT.md"
    svg_path = output_dir / "table_depth_collapse.svg"

    csv_rows = [
        {
            "covered_prime_limit": int(row["covered_prime_limit"]),
            "bit_length": int(row["bit_length"]),
            "candidate_count": int(row["candidate_count"]),
            "covered_prime_count": int(row["covered_prime_count"]),
            "observed_rejection_rate": f"{float(row['observed_rejection_rate']):.12f}",
            "theoretical_rejection_rate": f"{float(row['theoretical_rejection_rate']):.12f}",
            "observed_minus_theory": f"{float(row['observed_minus_theory']):+.12f}",
            "observed_standard_error": f"{float(row['observed_standard_error']):.12f}",
            "odd_prime_density_estimate": f"{float(row['odd_prime_density_estimate']):.12f}",
            "odd_prime_reciprocal_density_estimate": f"{float(row['odd_prime_reciprocal_density_estimate']):.12f}",
            "proxy_mean_ms": f"{float(row['proxy_timing_ms']['mean']):.12f}",
            "primary_hits": int(row["factor_source_counts"]["primary"]),
            "tail_hits": int(row["factor_source_counts"]["tail"]),
            "deep_tail_hits": int(row["factor_source_counts"]["deep_tail"]),
            "survivors": int(row["factor_source_counts"]["survivor"]),
        }
        for row in rows
    ]
    fieldnames = list(csv_rows[0].keys())

    json_path.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(csv_rows)
    markdown_path.write_text(build_markdown_report(results), encoding="utf-8")
    svg_path.write_text(svg_text, encoding="utf-8")

    return results


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Deterministic sweep of rejection collapse by prime-table depth."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for JSON, CSV, Markdown, and SVG artifacts.",
    )
    parser.add_argument(
        "--bit-lengths",
        type=int,
        nargs="+",
        default=DEFAULT_BIT_LENGTHS,
        help="Candidate bit lengths to sweep.",
    )
    parser.add_argument(
        "--table-limits",
        type=int,
        nargs="+",
        default=DEFAULT_TABLE_LIMITS,
        help="Covered odd-prime limits to sweep.",
    )
    parser.add_argument(
        "--candidate-count",
        type=int,
        default=DEFAULT_CANDIDATE_COUNT,
        help="Number of deterministic odd candidates per bit length.",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=benchmark.DEFAULT_PROXY_CHUNK_SIZE,
        help="Primes folded into each deterministic GCD batch.",
    )
    parser.add_argument(
        "--primary-limit",
        type=int,
        default=benchmark.DEFAULT_PROXY_TRIAL_PRIME_LIMIT,
        help="Upper bound of the primary interval.",
    )
    parser.add_argument(
        "--tail-limit",
        type=int,
        default=benchmark.DEFAULT_PROXY_TAIL_PRIME_LIMIT,
        help="Upper bound of the tail interval.",
    )
    parser.add_argument(
        "--namespace",
        type=str,
        default=DEFAULT_NAMESPACE,
        help="Deterministic namespace for the candidate stream.",
    )
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    """Run the sweep and print a compact terminal summary."""
    args = parse_args(argv)
    results = run_sweep(
        output_dir=args.output_dir,
        bit_lengths=parse_int_list([str(value) for value in args.bit_lengths]),
        table_limits=parse_int_list([str(value) for value in args.table_limits]),
        candidate_count=args.candidate_count,
        chunk_size=args.chunk_size,
        primary_limit=args.primary_limit,
        tail_limit=args.tail_limit,
        namespace=args.namespace,
    )

    print("table depth sweep complete")
    for summary in results["summaries"]:
        print(
            f"<= {int(summary['covered_prime_limit']):,}:",
            f"theory {float(summary['theoretical_rejection_rate']):.2%},",
            f"observed spread {float(summary['observed_spread_percentage_points']):.3f} pp,",
            f"ideal MR-only speedup ceiling {float(summary['asymptotic_speedup_if_proxy_free']):.2f}x",
        )
    print(f"artifacts: {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
