"""Floor reciprocity density sweep around isqrt(N)."""
import math

def floor_density(N: int, window: int, stride: int = 1):
    """
    Test floor reciprocity for x in [s-window, s+window] with step `stride`.
    Returns (tested, passed, pass_rate).
    """
    s = math.isqrt(N)
    lo = max(2, s - window)
    hi = s + window
    tested = 0
    passed = 0
    for x in range(lo, hi + 1, stride):
        tested += 1
        if x <= 0:
            continue
        y = N // x
        if y > 0 and (N // y) == x:
            passed += 1
    return tested, passed, passed / tested if tested else 0.0
