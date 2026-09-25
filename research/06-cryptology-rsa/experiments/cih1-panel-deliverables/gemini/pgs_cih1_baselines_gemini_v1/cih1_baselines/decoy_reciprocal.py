import math
import random

def find_decoy_reciprocals(N, p, q, samples, window):
    """
    Finds random non-factor pairs that satisfy bidirectional floor.
    """
    s = math.isqrt(N)
    start = max(2, s - window)
    end = s + window
    
    decoys = []
    attempts = 0
    
    while len(decoys) < samples and attempts < 10000:
        attempts += 1
        x = random.randint(start, end)
        if x == p or x == q:
            continue
            
        y = N // x
        if y > 0 and N // y == x:
            decoys.append((x, y))
            
    return decoys
