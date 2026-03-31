#!/usr/bin/env python3
"""Run the full exact raw composite Z gap-edge reproduction suite."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from raw_z_gap_edge_runs import (
    DEFAULT_FULL_LIMITS,
    DEFAULT_RANDOM_SEED,
    DEFAULT_WINDOW_COUNT,
    DEFAULT_WINDOW_SCALES,
    DEFAULT_WINDOW_SIZE,
    build_even_window_starts,
    build_seeded_window_starts,
    run_exact_limit,
    run_window_sweep,
)


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser for the full run suite."""
    parser = argparse.ArgumentParser(
        description="Run the full exact raw-Z gap-edge reproduction suite.",
    )
    parser.add_argument(
        "--full-limits",
        type=int,
        nargs="+",
        default=list(DEFAULT_FULL_LIMITS),
        help="Natural-number ceilings for exact full runs.",
    )
    parser.add_argument(
        "--window-scales",
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
    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_RANDOM_SEED,
        help="Deterministic seed used in fixed-seed sampled runs.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run every exact raw-Z reproduction and emit one JSON document."""
    args = build_parser().parse_args(argv)
    exact_rows = [run_exact_limit(limit).to_dict() for limit in args.full_limits]

    even_starts = {
        scale: build_even_window_starts(scale, args.window_size, args.window_count)
        for scale in args.window_scales
    }
    even_rows = [
        row.to_dict()
        for row in run_window_sweep(
            args.window_scales,
            args.window_size,
            even_starts,
            window_mode="even",
        )
    ]

    seeded_starts = {
        scale: build_seeded_window_starts(
            scale,
            args.window_size,
            args.window_count,
            args.seed,
        )
        for scale in args.window_scales
    }
    seeded_rows = [
        row.to_dict()
        for row in run_window_sweep(
            args.window_scales,
            args.window_size,
            seeded_starts,
            window_mode="seeded-random",
            seed=args.seed,
        )
    ]

    print(
        json.dumps(
            {
                "exact_full_runs": exact_rows,
                "even_window_runs": even_rows,
                "seeded_window_runs": seeded_rows,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
