import math

def floor_density(N, window, stride):
    """
    Measures density of bidirectional floor identities near isqrt(N).
    """
    s = math.isqrt(N)
    start = max(2, s - window)
    end = s + window
    
    tested = 0
    passed = 0
    
    for x in range(start, end + 1, stride):
        tested += 1
        y = N // x
        if y > 0 and N // y == x:
            passed += 1
            
    rate = passed / tested if tested > 0 else 0.0
    return tested, passed, rate
