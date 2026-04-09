#!/usr/bin/env python3
"""Compatibility wrapper around the packaged PNT/GWR predictor helpers."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = ROOT / "src" / "python"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from z_band_prime_predictor import (  # noqa: E402
    W_d,
    d4_closure_ceiling,
    gap_dmin,
    gap_from_interior_seed,
    gwr_predict,
    li_inverse,
    placed_prime_from_seed,
    pnt_gwr_d4_candidate,
    pnt_seed,
    predict_nth_prime,
    run_tests,
)


if __name__ == "__main__":
    raise SystemExit(0 if run_tests() else 1)
