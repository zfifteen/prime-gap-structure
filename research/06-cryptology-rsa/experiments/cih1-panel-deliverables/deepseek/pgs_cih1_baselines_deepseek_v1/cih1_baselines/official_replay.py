"""Official fixture constants and replay check."""
import math
from .fermat import fermat_steps
from .primality import is_prime

OFFICIAL_FIXTURES = [
    {
        'bits': 40,
        'N': 1099507433251,
        'p': 1048559,
        'q': 1048589,
    },
    {
        'bits': 50,
        'N': 1027435935526951,
        'p': 30729371,
        'q': 33434981,
    },
    {
        'bits': 64,
        'N': 10376454699372036973,
        'p': 3221225473,
        'q': 3221275501,
    },
]

def replay_official():
    """Run official replay and return list of result dicts."""
    results = []
    for fix in OFFICIAL_FIXTURES:
        N = fix['N']
        p = fix['p']
        q = fix['q']
        s = math.isqrt(N)
        d1 = abs(p - s)
        d2 = abs(q - s)
        min_dist = min(d1, d2)
        rel = min_dist / s if s else 0.0
        steps, f1, f2 = fermat_steps(N)
        product_ok = (p * q == N)
        both_prime_ok = is_prime(p) and is_prime(q)
        near_square = (min_dist < 100_000) or (rel < 0.01)
        classification = "near_square_fermat_class" if near_square else "non_near_square"
        results.append({
            'bits': fix['bits'],
            'N': N,
            'p': p,
            'q': q,
            'isqrt': s,
            'min_dist': min_dist,
            'rel': rel,
            'fermat_steps': steps,
            'fermat_factors': (f1, f2),
            'product_ok': product_ok,
            'both_prime_ok': both_prime_ok,
            'near_square_flag': near_square,
            'classification': classification,
        })
    return results
