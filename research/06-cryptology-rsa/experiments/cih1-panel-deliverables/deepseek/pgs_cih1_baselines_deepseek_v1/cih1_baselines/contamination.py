"""Near-square contamination flags and audit integrity."""
import math
from . import primality

def compute_contamination(case_row: dict, audit_row: dict):
    """
    Compute contamination flags for one case.
    case_row: dict with 'case_id', 'N'
    audit_row: dict with 'case_id', 'p', 'q'
    Returns dict with keys:
      min_dist, rel, near_square_flag, product_ok, both_prime_ok
    Also flags audit_integrity_fail if product mismatch or factors not prime.
    """
    N = case_row['N']
    p = audit_row['p']
    q = audit_row['q']
    s = math.isqrt(N)
    d1 = abs(p - s)
    d2 = abs(q - s)
    min_dist = min(d1, d2)
    rel = min_dist / s if s else 0.0
    near_square_flag = (min_dist < 100_000) or (rel < 0.01)

    product_ok = (p * q == N)
    both_prime_ok = primality.is_prime(p) and primality.is_prime(q)
    return {
        'case_id': case_row['case_id'],
        'min_dist': min_dist,
        'rel': rel,
        'near_square_flag': near_square_flag,
        'product_ok': product_ok,
        'both_prime_ok': both_prime_ok,
        'audit_integrity_fail': not (product_ok and both_prime_ok)
    }
