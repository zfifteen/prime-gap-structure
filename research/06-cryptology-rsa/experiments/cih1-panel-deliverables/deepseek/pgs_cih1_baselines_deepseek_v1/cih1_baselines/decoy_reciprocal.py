"""Find decoy reciprocal pairs near sqrt(N) that are not the true factors."""
import math

def find_decoys(N: int, p: int, q: int, window: int, max_samples: int):
    """
    Scan x in [s-window, s+window] for floor-reciprocal pairs not equal to the factors.
    Returns (list_of_x, count_available_estimate).
    """
    s = math.isqrt(N)
    lo = max(2, s - window)
    hi = s + window
    decoys = []
    total_available = 0
    for x in range(lo, hi + 1):
        y = N // x
        if y <= 0:
            continue
        if (N // y) != x:
            continue
        # reciprocal pair (x, y)
        if x * y == N:
            continue
        # exclude true factors if known (p,q > 0)
        if p and q:
            if x in (p, q) or y in (p, q):
                continue
        total_available += 1
        if len(decoys) < max_samples:
            decoys.append(x)
    return decoys, total_available
