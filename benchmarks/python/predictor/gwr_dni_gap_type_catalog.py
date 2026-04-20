#!/usr/bin/env python3
"""Catalog distinct exact GWR/DNI gap types on the deterministic 10^18 surface."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import time
from collections import Counter
from pathlib import Path

from sympy import nextprime


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT_DIR = ROOT / "output"
DEFAULT_EXACT_MAX_RIGHT_PRIME = 1_000_000
DEFAULT_MIN_POWER = 7
DEFAULT_MAX_POWER = 18
DEFAULT_WINDOW_STEPS = 256
GAP_TYPE_PROBE_PATH = Path(__file__).with_name("gwr_dni_gap_type_probe.py")
FAMILY_COLORS = {
    "prime_square": "#7a3b69",
    "prime_cube": "#b07aa1",
    "even_semiprime": "#dd8452",
    "odd_semiprime": "#4c72b0",
    "higher_divisor_even": "#55a868",
    "higher_divisor_odd": "#8172b2",
}


def load_gap_type_probe():
    """Load the exact gap-type probe from its sibling file."""
    spec = importlib.util.spec_from_file_location("gwr_dni_gap_type_probe", GAP_TYPE_PROBE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load gwr_dni_gap_type_probe module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


GAP_TYPE_PROBE = load_gap_type_probe()
CARRIER_FAMILIES = GAP_TYPE_PROBE.CARRIER_FAMILIES


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Catalog exact GWR/DNI gap types on the deterministic surface "
            "through 10^18."
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for JSON, CSV, and plot artifacts.",
    )
    parser.add_argument(
        "--exact-max-right-prime",
        type=int,
        default=DEFAULT_EXACT_MAX_RIGHT_PRIME,
        help="Largest right prime on the exact baseline type surface.",
    )
    parser.add_argument(
        "--min-power",
        type=int,
        default=DEFAULT_MIN_POWER,
        help="Smallest sampled decade power m in the start anchor 10^m.",
    )
    parser.add_argument(
        "--max-power",
        type=int,
        default=DEFAULT_MAX_POWER,
        help="Largest sampled decade power m in the start anchor 10^m.",
    )
    parser.add_argument(
        "--window-steps",
        type=int,
        default=DEFAULT_WINDOW_STEPS,
        help="Number of consecutive typed gaps sampled from each decade anchor.",
    )
    return parser


def baseline_surface_label(exact_max_right_prime: int) -> tuple[str, str]:
    """Return stable machine and display labels for the exact baseline surface."""
    if exact_max_right_prime < 2:
        raise ValueError("exact_max_right_prime must be at least 2")

    power = int(round(math.log10(exact_max_right_prime)))
    if 10**power == exact_max_right_prime:
        return f"baseline_1e{power}", f"<=10^{power}"
    return f"baseline_{exact_max_right_prime}", f"<={exact_max_right_prime:,}"


def start_prime_for_power(power: int) -> int:
    """Return the first prime at or above one decade anchor."""
    if power < 1:
        raise ValueError("power must be at least 1")
    return int(nextprime(10**power - 1))


def count_share_payload(counter: Counter[str], total: int) -> dict[str, dict[str, float | int]]:
    """Return count/share payload entries in stable key order."""
    payload: dict[str, dict[str, float | int]] = {}
    for key in sorted(counter):
        count = int(counter[key])
        payload[key] = {
            "count": count,
            "share": count / total if total else 0.0,
        }
    return payload


def family_distribution(rows: list[dict[str, object]]) -> dict[str, dict[str, float | int]]:
    """Return the coarse family distribution for one row surface."""
    counter = Counter(str(row["carrier_family"]) for row in rows)
    payload: dict[str, dict[str, float | int]] = {}
    total = len(rows)
    for family in CARRIER_FAMILIES:
        count = int(counter.get(family, 0))
        payload[family] = {
            "count": count,
            "share": count / total if total else 0.0,
        }
    return payload


def top_exact_types(rows: list[dict[str, object]], limit: int = 10) -> list[dict[str, object]]:
    """Return the leading exact type keys on one surface."""
    counter = Counter(str(row["type_key"]) for row in rows)
    total = len(rows)
    return [
        {
            "type_key": key,
            "count": int(count),
            "share": count / total if total else 0.0,
        }
        for key, count in counter.most_common(limit)
    ]


def walk_type_rows_from(current_right_prime: int, steps: int) -> list[dict[str, object]]:
    """Return consecutive exact type rows from one prime-start anchor."""
    if steps < 1:
        raise ValueError("steps must be at least 1")

    rows: list[dict[str, object]] = []
    q = int(current_right_prime)
    for row_index in range(steps):
        row = GAP_TYPE_PROBE.gap_type_row(q, gap_index=row_index + 1)
        rows.append(row)
        q = int(row["next_right_prime"])
    return rows


def catalog_surfaces(
    exact_max_right_prime: int,
    min_power: int,
    max_power: int,
    window_steps: int,
) -> list[dict[str, object]]:
    """Return the ordered exact baseline plus sampled decade surfaces."""
    if exact_max_right_prime < 2:
        raise ValueError("exact_max_right_prime must be at least 2")
    if min_power < 1:
        raise ValueError("min_power must be at least 1")
    if max_power < min_power:
        raise ValueError("max_power must be at least min_power")
    if window_steps < 1:
        raise ValueError("window_steps must be at least 1")

    baseline_label, baseline_display = baseline_surface_label(exact_max_right_prime)
    surfaces = [
        {
            "surface_label": baseline_label,
            "surface_display_label": baseline_display,
            "surface_kind": "exact_baseline",
            "power": None,
            "start_right_prime": 3,
            "rows": GAP_TYPE_PROBE.type_rows(exact_max_right_prime),
        }
    ]

    for power in range(min_power, max_power + 1):
        start_right_prime = start_prime_for_power(power)
        surfaces.append(
            {
                "surface_label": f"10^{power}",
                "surface_display_label": f"10^{power}",
                "surface_kind": "sampled_decade_window",
                "power": power,
                "start_right_prime": start_right_prime,
                "rows": walk_type_rows_from(start_right_prime, window_steps),
            }
        )

    return surfaces


def summarize_surfaces(
    surfaces: list[dict[str, object]],
    exact_max_right_prime: int,
    window_steps: int,
) -> tuple[dict[str, object], list[dict[str, object]]]:
    """Aggregate the catalog surfaces into JSON summary and CSV detail rows."""
    if not surfaces:
        raise ValueError("surfaces must not be empty")

    detail_rows: list[dict[str, object]] = []
    overall_rows: list[dict[str, object]] = []
    union_types: set[str] = set()
    common_types: set[str] | None = None
    first_seen_rows: dict[str, dict[str, object]] = {}
    first_seen_surface_counts = Counter()
    surface_summaries: list[dict[str, object]] = []

    for surface in surfaces:
        rows = surface["rows"]
        surface_label = str(surface["surface_label"])
        surface_display_label = str(surface["surface_display_label"])
        surface_kind = str(surface["surface_kind"])
        power = surface["power"]
        surface_types = {str(row["type_key"]) for row in rows}
        new_rows_by_type: dict[str, dict[str, object]] = {}

        for row_index, row in enumerate(rows, start=1):
            type_key = str(row["type_key"])
            detail_rows.append(
                {
                    "surface_label": surface_label,
                    "surface_display_label": surface_display_label,
                    "surface_kind": surface_kind,
                    "power": power,
                    "surface_row_index": row_index,
                    "gap_index": int(row["gap_index"]) if row["gap_index"] is not None else None,
                    "current_right_prime": int(row["current_right_prime"]),
                    "next_right_prime": int(row["next_right_prime"]),
                    "next_gap_width": int(row["next_gap_width"]),
                    "residue_mod30": int(row["residue_mod30"]),
                    "first_open_offset": int(row["first_open_offset"]),
                    "winner": int(row["winner"]),
                    "next_dmin": int(row["next_dmin"]),
                    "next_peak_offset": int(row["next_peak_offset"]),
                    "carrier_family": str(row["carrier_family"]),
                    "type_key": type_key,
                }
            )
            overall_rows.append(row)

            if type_key in union_types or type_key in new_rows_by_type:
                continue
            new_rows_by_type[type_key] = row
            first_seen_rows[type_key] = {
                "type_key": type_key,
                "first_seen_surface_label": surface_label,
                "first_seen_surface_display_label": surface_display_label,
                "current_right_prime": int(row["current_right_prime"]),
                "next_gap_width": int(row["next_gap_width"]),
                "next_dmin": int(row["next_dmin"]),
                "next_peak_offset": int(row["next_peak_offset"]),
                "carrier_family": str(row["carrier_family"]),
            }
            first_seen_surface_counts[surface_label] += 1

        union_types.update(surface_types)
        common_types = surface_types if common_types is None else common_types & surface_types
        first_seen_examples = sorted(
            new_rows_by_type.values(),
            key=lambda row: (
                int(row["next_dmin"]),
                int(row["next_peak_offset"]),
                str(row["carrier_family"]),
                str(row["type_key"]),
            ),
        )

        surface_summaries.append(
            {
                "surface_label": surface_label,
                "surface_display_label": surface_display_label,
                "surface_kind": surface_kind,
                "power": power,
                "start_right_prime": int(surface["start_right_prime"]),
                "gap_count": len(rows),
                "distinct_exact_type_count": len(surface_types),
                "new_exact_type_count": len(new_rows_by_type),
                "cumulative_distinct_exact_type_count": len(union_types),
                "max_next_peak_offset": max(int(row["next_peak_offset"]) for row in rows),
                "max_next_dmin": max(int(row["next_dmin"]) for row in rows),
                "family_distribution": family_distribution(rows),
                "top_exact_types": top_exact_types(rows),
                "first_seen_exact_type_examples": [
                    {
                        "type_key": str(row["type_key"]),
                        "current_right_prime": int(row["current_right_prime"]),
                        "next_gap_width": int(row["next_gap_width"]),
                        "next_dmin": int(row["next_dmin"]),
                        "next_peak_offset": int(row["next_peak_offset"]),
                        "carrier_family": str(row["carrier_family"]),
                    }
                    for row in first_seen_examples[:10]
                ],
            }
        )

    baseline_label = str(surfaces[0]["surface_label"])
    post_baseline_new_rows = [
        payload
        for payload in first_seen_rows.values()
        if str(payload["first_seen_surface_label"]) != baseline_label
    ]
    post_baseline_new_family_counter = Counter(
        str(payload["carrier_family"]) for payload in post_baseline_new_rows
    )
    post_baseline_new_dmin_counter = Counter(
        str(payload["next_dmin"]) for payload in post_baseline_new_rows
    )
    overall_family_counter = Counter(str(row["carrier_family"]) for row in overall_rows)
    overall_type_counter = Counter(str(row["type_key"]) for row in overall_rows)
    display_by_label = {
        str(surface["surface_label"]): str(surface["surface_display_label"])
        for surface in surfaces
    }

    summary = {
        "type_key_definition": {
            "format": "o{first_open}_d{winner_d}_a{winner_offset}_{family}",
            "first_open_offsets_observed": sorted(
                {int(row["first_open_offset"]) for row in overall_rows}
            ),
            "carrier_families": list(CARRIER_FAMILIES),
        },
        "exact_baseline_max_right_prime": exact_max_right_prime,
        "sampled_window_steps": window_steps,
        "surface_count": len(surfaces),
        "surface_order": [summary_row["surface_label"] for summary_row in surface_summaries],
        "surface_display_order": [
            summary_row["surface_display_label"] for summary_row in surface_summaries
        ],
        "union_distinct_exact_type_count": len(union_types),
        "post_baseline_new_exact_type_count": len(post_baseline_new_rows),
        "common_exact_type_count": len(common_types) if common_types is not None else 0,
        "common_exact_types": sorted(common_types) if common_types is not None else [],
        "distinct_first_open_offsets": sorted(
            {int(row["first_open_offset"]) for row in overall_rows}
        ),
        "distinct_dmin_values": sorted({int(row["next_dmin"]) for row in overall_rows}),
        "max_observed_peak_offset": max(int(row["next_peak_offset"]) for row in overall_rows),
        "max_observed_dmin": max(int(row["next_dmin"]) for row in overall_rows),
        "first_seen_counts_by_surface_label": {
            label: int(first_seen_surface_counts.get(label, 0))
            for label in [summary_row["surface_label"] for summary_row in surface_summaries]
        },
        "first_seen_counts_by_surface_display_label": {
            display_by_label[label]: int(first_seen_surface_counts.get(label, 0))
            for label in [summary_row["surface_label"] for summary_row in surface_summaries]
        },
        "post_baseline_new_type_family_distribution": count_share_payload(
            post_baseline_new_family_counter,
            len(post_baseline_new_rows),
        ),
        "post_baseline_new_type_dmin_distribution": count_share_payload(
            post_baseline_new_dmin_counter,
            len(post_baseline_new_rows),
        ),
        "overall_family_distribution": count_share_payload(
            overall_family_counter,
            len(overall_rows),
        ),
        "overall_top_exact_types": [
            {
                "type_key": key,
                "count": int(count),
                "share": count / len(overall_rows),
            }
            for key, count in overall_type_counter.most_common(20)
        ],
        "post_baseline_new_exact_types": sorted(
            post_baseline_new_rows,
            key=lambda payload: (
                str(payload["first_seen_surface_label"]),
                int(payload["next_dmin"]),
                int(payload["next_peak_offset"]),
                str(payload["type_key"]),
            ),
        ),
        "surface_summaries": surface_summaries,
    }

    return summary, detail_rows


def plot_overview(summary: dict[str, object], output_path: Path) -> None:
    """Render one compact overview plot for the catalog surface."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    surface_summaries = summary["surface_summaries"]
    labels = [row["surface_display_label"] for row in surface_summaries]
    x_positions = list(range(len(labels)))
    cumulative_counts = [
        int(row["cumulative_distinct_exact_type_count"]) for row in surface_summaries
    ]
    new_counts = [int(row["new_exact_type_count"]) for row in surface_summaries]

    fig, axes = plt.subplots(2, 1, figsize=(12, 9), constrained_layout=True)

    axes[0].bar(
        x_positions,
        new_counts,
        color="#c44e52",
        alpha=0.78,
        label="New exact types first seen on surface",
    )
    axes[0].plot(
        x_positions,
        cumulative_counts,
        color="#2f5aa8",
        marker="o",
        linewidth=2.2,
        label="Cumulative distinct exact types",
    )
    axes[0].set_title("Exact gap-type alphabet across the deterministic 10^18 catalog surface")
    axes[0].set_ylabel("Exact type count")
    axes[0].set_xticks(x_positions)
    axes[0].set_xticklabels(labels, rotation=35, ha="right")
    axes[0].grid(axis="y", alpha=0.25)
    axes[0].legend(loc="upper left")

    bottoms = [0.0] * len(labels)
    for family in CARRIER_FAMILIES:
        shares = [
            float(row["family_distribution"][family]["share"]) for row in surface_summaries
        ]
        axes[1].bar(
            x_positions,
            shares,
            bottom=bottoms,
            color=FAMILY_COLORS[family],
            label=family.replace("_", " "),
        )
        bottoms = [bottom + share for bottom, share in zip(bottoms, shares)]

    axes[1].set_title("Coarse carrier families stay fixed while their shares drift")
    axes[1].set_ylabel("Share of typed gaps")
    axes[1].set_ylim(0.0, 1.0)
    axes[1].set_xticks(x_positions)
    axes[1].set_xticklabels(labels, rotation=35, ha="right")
    axes[1].grid(axis="y", alpha=0.25)
    axes[1].legend(loc="upper right", ncol=2)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=200)
    plt.close(fig)


def main(argv: list[str] | None = None) -> int:
    """Run the gap-type catalog and write JSON, CSV, and plot artifacts."""
    args = build_parser().parse_args(argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    started = time.perf_counter()
    surfaces = catalog_surfaces(
        exact_max_right_prime=args.exact_max_right_prime,
        min_power=args.min_power,
        max_power=args.max_power,
        window_steps=args.window_steps,
    )
    summary, detail_rows = summarize_surfaces(
        surfaces,
        exact_max_right_prime=args.exact_max_right_prime,
        window_steps=args.window_steps,
    )
    summary["runtime_seconds"] = time.perf_counter() - started

    summary_path = args.output_dir / "gwr_dni_gap_type_catalog_summary.json"
    detail_path = args.output_dir / "gwr_dni_gap_type_catalog_details.csv"
    plot_path = args.output_dir / "gwr_dni_gap_type_catalog_overview.png"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    fieldnames = [
        "surface_label",
        "surface_display_label",
        "surface_kind",
        "power",
        "surface_row_index",
        "gap_index",
        "current_right_prime",
        "next_right_prime",
        "next_gap_width",
        "residue_mod30",
        "first_open_offset",
        "winner",
        "next_dmin",
        "next_peak_offset",
        "carrier_family",
        "type_key",
    ]
    with detail_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(detail_rows)

    plot_overview(summary, plot_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
