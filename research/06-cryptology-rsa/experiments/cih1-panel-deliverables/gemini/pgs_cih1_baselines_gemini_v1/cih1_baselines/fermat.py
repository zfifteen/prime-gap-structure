import math

def fermat_steps(N, limit=5_000_000):
    """
    Computes Fermat factorization steps.
    a0 = smallest integer a with a*a >= N.
    """
    a0 = math.isqrt(N)
    if a0 * a0 < N:
        a0 += 1
    
    a = a0
    steps = 0
    while steps <= limit:
        t = a * a - N
        if t >= 0:
            r = math.isqrt(t)
            if r * r == t:
                return steps, a - r, a + r
        a += 1
        steps += 1
        
    return None, None, None
