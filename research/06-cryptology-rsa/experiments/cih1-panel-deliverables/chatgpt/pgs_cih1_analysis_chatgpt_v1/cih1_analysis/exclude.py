"""Near-square exclusion calculations."""
from __future__ import annotations
import math

def exclusion_info(row, min_abs_dist_to_sqrt=100000, min_rel_dist_to_sqrt=0.01):
    n = row["N"]
    s = math.isqrt(n)
    dist = min(abs(row["p"] - s), abs(row["q"] - s))
    rel = dist / s if s else float("inf")
    # Audit-supplied values are retained only when consistent; calculations win.
    reasons = []
    if dist < int(min_abs_dist_to_sqrt):
        reasons.append("near_square_abs")
    if rel < float(min_rel_dist_to_sqrt):
        reasons.append("near_square_rel")
    return {
        "isqrt_N": s,
        "min_dist_to_sqrt": dist,
        "rel_dist": rel,
        "excluded": bool(reasons),
        "exclude_reason": ";".join(reasons) if reasons else None,
    }
