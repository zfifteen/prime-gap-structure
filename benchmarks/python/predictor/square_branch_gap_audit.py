#!/usr/bin/env python3
"""Audit prime-square offsets against fixed and dynamic cutoff surfaces."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

from sympy import prevprime, primerange

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmarks.python.predictor.gwr_dni_recursive_walk import dynamic_cutoff, first_open_offset

DEFAULT_MAX_PRIME = 100_000
DEFAULT_OUTPUT_DIR = ROOT / "output"
CSV_FIELDS = [
    "p",
    "square",
    "previous_prime",
    "offset",
    "o_q",
    "fixed_cutoff",
    "dynamic_cutoff",
]


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description="Audit prime-square offsets against fixed and dynamic cutoff surfaces.",
    )
    parser.add_argument(
        "--max-prime",
        type=int,
        default=DEFAULT_MAX_PRIME,
        help="Maximum prime p to audit; the script scans p^2 for all primes p <= max-prime.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for JSON and CSV artifacts.",
    )
    return parser


def cutoff_for_branch(first_open: int) -> int:
    """Return the falsified fixed cutoff for one first-open branch."""
    if first_open == 2:
        return 44
    if first_open in (4, 6):
        return 60
    raise ValueError(f"unsupported first_open_offset {first_open}")


def write_csv(path: Path, rows: list[dict[str, int]]) -> None:
    """Write one LF-terminated CSV file."""
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def audit_square_branch(max_prime: int) -> tuple[dict[str, object], list[dict[str, int]], list[dict[str, int]]]:
    """Return the square-branch audit summary, all rows, and violation rows."""
    all_rows: list[dict[str, int]] = []
    violation_rows: list[dict[str, int]] = []
    branch_maxima: dict[int, dict[str, int] | None] = {2: None, 4: None, 6: None}
    global_max: dict[str, int] | None = None

    for p in primerange(2, max_prime + 1):
        square = p * p
        previous_prime = int(prevprime(square))
        offset = square - previous_prime
        first_open = first_open_offset(previous_prime % 30)
        cutoff = cutoff_for_branch(first_open)
        row = {
            "p": int(p),
            "square": int(square),
            "previous_prime": previous_prime,
            "offset": int(offset),
            "o_q": int(first_open),
            "fixed_cutoff": int(cutoff),
            "dynamic_cutoff": int(dynamic_cutoff(previous_prime)),
        }
        all_rows.append(row)

        branch_current = branch_maxima[first_open]
        if branch_current is None or offset > int(branch_current["offset"]):
            branch_maxima[first_open] = row

        if global_max is None or offset > int(global_max["offset"]):
            global_max = row

        if offset > cutoff:
            violation_rows.append(row)

    if global_max is None:
        raise ValueError("max_prime produced no prime rows")

    summary = {
        "max_prime": int(max_prime),
        "tested_prime_count": len(all_rows),
        "violation_count": len(violation_rows),
        "global_max_offset": int(global_max["offset"]),
        "global_max_row": global_max,
        "max_dynamic_cutoff_utilization": max(
            float(row["offset"]) / float(row["dynamic_cutoff"]) for row in all_rows
        ),
        "dynamic_cutoff_covers_all_rows": all(
            int(row["offset"]) <= int(row["dynamic_cutoff"]) for row in all_rows
        ),
        "max_offset_by_o_q": {
            str(branch): (
                None
                if branch_maxima[branch] is None
                else {
                    "offset": int(branch_maxima[branch]["offset"]),
                    "fixed_cutoff": int(branch_maxima[branch]["fixed_cutoff"]),
                    "dynamic_cutoff": int(branch_maxima[branch]["dynamic_cutoff"]),
                    "dynamic_cutoff_utilization": (
                        float(branch_maxima[branch]["offset"])
                        / float(branch_maxima[branch]["dynamic_cutoff"])
                    ),
                    "row": branch_maxima[branch],
                }
            )
            for branch in (2, 4, 6)
        },
    }
    return summary, all_rows, violation_rows


def main() -> int:
    """Run the square-branch audit and write artifacts."""
    args = build_parser().parse_args()
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    summary, all_rows, violation_rows = audit_square_branch(args.max_prime)

    summary_path = output_dir / "square_branch_gap_audit_summary.json"
    all_csv_path = output_dir / "square_branch_gap_audit_all.csv"
    violations_csv_path = output_dir / "square_branch_gap_audit_violations.csv"

    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    write_csv(all_csv_path, all_rows)
    write_csv(violations_csv_path, violation_rows)

    print(
        "square-branch-gap-audit:"
        f" primes={summary['tested_prime_count']}"
        f" violations={summary['violation_count']}"
        f" global_max_offset={summary['global_max_offset']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
