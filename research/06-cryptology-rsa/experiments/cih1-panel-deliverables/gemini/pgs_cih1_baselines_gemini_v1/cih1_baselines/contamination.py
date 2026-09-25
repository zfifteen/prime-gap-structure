import math

def check_contamination(N, p, q):
    """
    Evaluates near-square contamination per CIH-1 protocol.
    near_square iff min(|p-√N|, |q-√N|) < 100000 OR rel_dist < 0.01
    """
    s = math.isqrt(N)
    min_dist = min(abs(p - s), abs(q - s))
    rel_dist = min_dist / s if s > 0 else 0.0
    
    near_square = (min_dist < 100000) or (rel_dist < 0.01)
    
    return {
        "near_square": near_square,
        "min_dist": min_dist,
        "rel_dist": rel_dist,
        "isqrt": s
    }
