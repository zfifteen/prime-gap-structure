"""Fermat factorisation baseline: steps and factor recovery."""
import math

def fermat_steps(N: int):
    """
    Return (steps, factor1, factor2) or (None, None, None) if timeout.
    steps = number of a increments after ceil_sqrt.
    factor1 = a - r, factor2 = a + r where r = isqrt(a^2 - N).
    """
    if N <= 1:
        return None, None, None
    a0 = math.isqrt(N)
    if a0 * a0 < N:
        a0 += 1
    a = a0
    steps = 0
    while steps <= 5_000_000:
        t = a * a - N
        r = math.isqrt(t)
        if r * r == t:
            return steps, a - r, a + r
        a += 1
        steps += 1
    return None, None, None
