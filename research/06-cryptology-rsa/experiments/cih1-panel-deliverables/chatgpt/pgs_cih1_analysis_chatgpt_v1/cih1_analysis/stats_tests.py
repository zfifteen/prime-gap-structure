"""Dependency-free directional statistics."""
from __future__ import annotations
import math

def _binom_tail(k, n):
    # P[X >= k], X~Binomial(n,.5), exact integer arithmetic.
    if n == 0:
        return 1.0
    total = 2 ** n
    return sum(math.comb(n, i) for i in range(k, n+1)) / total

def sign_test_one_sided(positive, negative):
    n = positive + negative
    if n == 0:
        return 1.0
    return _binom_tail(positive, n)

def two_sided_sign_test(positive, negative):
    n = positive + negative
    if n == 0:
        return 1.0
    k = min(positive, negative)
    p = 2.0 * sum(math.comb(n, i) for i in range(0, k+1)) / (2 ** n)
    return min(1.0, p)

def directional_p_value(deltas):
    pos = sum(d > 0 for d in deltas)
    neg = sum(d < 0 for d in deltas)
    return sign_test_one_sided(pos, neg), two_sided_sign_test(pos, neg), pos, neg
