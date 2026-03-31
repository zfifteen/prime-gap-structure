#!/usr/bin/env python3
"""Run exact raw composite Z gap-edge reproductions on evenly spaced windows."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from raw_z_gap_edge_runs import (
    DEFAULT_WINDOW_COUNT,
    DEFAULT_WINDOW_SCALES,
    DEFAULT_WINDOW_SIZE,
    build_even_window_starts,
    run_window_sweep,
)


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser for evenly spaced window sweeps."""
    parser = argparse.ArgumentParser(
        description="Run exact raw-Z gap-edge reproductions on evenly spaced windows.",
    )
    parser.add_argument(
        "--scales",
        type=int,
        nargs="+",
        default=list(DEFAULT_WINDOW_SCALES),
        help="Natural-number scales to sample with fixed-size windows.",
    )
    parser.add_argument(
        "--window-size",
        type=int,
        default=DEFAULT_WINDOW_SIZE,
        help="Width of each exact sampled window.",
    )
    parser.add_argument(
        "--window-count",
        type=int,
        default=DEFAULT_WINDOW_COUNT,
        help="Number of windows per sampled scale.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the requested evenly spaced window sweeps and emit JSON."""
    args = build_parser().parse_args(argv)
    starts_by_scale = {
        scale: build_even_window_starts(scale, args.window_size, args.window_count)
        for scale in args.scales
    }
    rows = run_window_sweep(
        args.scales,
        args.window_size,
        starts_by_scale,
        window_mode="even",
    )
    print(json.dumps([row.to_dict() for row in rows], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
