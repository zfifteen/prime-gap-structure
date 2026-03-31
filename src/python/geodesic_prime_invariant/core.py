"""Exact DCI invariant helpers."""

from __future__ import annotations

import math
import sys


FIXED_POINT_V = math.e ** 2 / 2.0
FIXED_POINT_TOLERANCE = 1e-12
LOG_FLOAT_MIN = math.log(sys.float_info.min)


def exact_divisor_count(n: int) -> int:
    """Compute the exact divisor count with the direct O(sqrt n) path."""
    if n < 1:
        return 0

    count = 0
    divisor = 1
    while divisor * divisor <= n:
        if n % divisor == 0:
            count += 1 if divisor * divisor == n else 2
        divisor += 1
    return count


def exact_z_normalize(n: int, v: float = FIXED_POINT_V) -> float:
    """Evaluate the exact DCI normalization at the fixed-point traversal rate."""
    if n <= 1:
        return 0.0

    divisor_total = exact_divisor_count(n)
    exponent = (1.0 - divisor_total / 2.0) * math.log(n)
    return 0.0 if exponent < LOG_FLOAT_MIN else math.exp(exponent)
