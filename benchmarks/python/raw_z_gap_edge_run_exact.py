#!/usr/bin/env python3
"""Run full exact raw composite Z gap-edge reproductions at fixed limits."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from raw_z_gap_edge_runs import DEFAULT_FULL_LIMITS, run_exact_limit


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser for full exact raw-Z runs."""
    parser = argparse.ArgumentParser(
        description="Run full exact raw-Z gap-edge reproductions at fixed limits.",
    )
    parser.add_argument(
        "--limits",
        type=int,
        nargs="+",
        default=list(DEFAULT_FULL_LIMITS),
        help="Natural-number ceilings for exact full runs.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the requested full exact reproductions and emit JSON."""
    args = build_parser().parse_args(argv)
    rows = [run_exact_limit(limit).to_dict() for limit in args.limits]
    print(json.dumps(rows, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
