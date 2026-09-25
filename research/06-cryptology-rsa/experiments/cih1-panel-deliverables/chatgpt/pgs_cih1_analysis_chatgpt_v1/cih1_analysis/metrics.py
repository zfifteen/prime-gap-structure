"""Primary CIH-1 distance metrics."""
from __future__ import annotations
import statistics

def score_case(row, control_distances):
    p, q, w = row["p"], row["q"], row["carrier_w"]
    dc = min(abs(w-p), abs(w-q))
    med = statistics.median(control_distances)
    mean = statistics.fmean(control_distances)
    return {
        "D_c": dc,
        "control_median_D_u": med,
        "control_mean_D_u": mean,
        "R": dc / max(1, med),
        "carrier_beats_control_median": dc < med,
    }
