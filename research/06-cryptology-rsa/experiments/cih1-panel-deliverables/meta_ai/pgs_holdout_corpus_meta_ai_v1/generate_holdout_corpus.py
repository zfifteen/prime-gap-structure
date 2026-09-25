
#!/usr/bin/env python3
"""
Deterministic hold-out corpus generator for PGS RSA residual work.
Measured-on-sandbox-regime-only / hypothesis material.

RNG: Python random.Random with explicit seed (Mersenne Twister, deterministic)
Prime test: deterministic Miller-Rabin for n < 2^64 using bases [2,3,5,7,11,13]
           sufficient for < 3,474,749,660,383; our n < 2^27.
Prime search: random odd start in interval, linear +2 scan with wrap-around.
Balanced: |bitlen(p)-bitlen(q)| <=1 by construction (both = bits//2 for even B)
Near-square exclusion: min(|p-isqrt(N)|, |q-isqrt(N)|) >=100000 and rel>=0.01
"""

import argparse
import json
import math
import random
import hashlib
import os
import sys
from pathlib import Path

def is_probable_prime(n: int) -> bool:
    if n < 2:
        return False
    small_primes = [2,3,5,7,11,13,17,19,23,29]
    for p in small_primes:
        if n % p == 0:
            return n == p
    # write n-1 = d*2^s
    d = n-1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    # deterministic bases for < 3,474,749,660,383
    for a in [2,3,5,7,11,13]:
        if a >= n:
            continue
        x = pow(a, d, n)
        if x == 1 or x == n-1:
            continue
        for _ in range(s-1):
            x = (x*x) % n
            if x == n-1:
                break
        else:
            return False
    return True

def random_prime_in_interval(bits: int, low_frac: float, high_frac: float, rng: random.Random, max_scan=10000):
    """Return prime in fraction of [2^(bits-1), 2^bits-1]. low_frac inclusive, high_frac exclusive."""
    low = 1 << (bits-1)
    high = (1 << bits) - 1
    span = high - low + 1
    lo = low + int(span * low_frac)
    hi = low + int(span * high_frac) - 1
    # ensure within bounds
    lo = max(lo, low)
    hi = min(hi, high)
    if lo > hi:
        lo, hi = low, high
    # make odd bounds
    if lo % 2 == 0:
        lo += 1
    if hi % 2 == 0:
        hi -= 1
    # random start
    # number of odd numbers in interval
    count_odds = (hi - lo)//2 + 1
    if count_odds <=0:
        raise ValueError("empty interval")
    start_idx = rng.randint(0, count_odds-1)
    cand = lo + start_idx*2
    for _ in range(max_scan):
        if cand > hi:
            cand = lo  # wrap
        if is_probable_prime(cand):
            return cand
        cand += 2
        if cand > hi:
            cand = lo
    # if not found, expand search to full range as fallback
    cand = lo
    for _ in range(max_scan*2):
        if is_probable_prime(cand):
            return cand
        cand += 2
        if cand > high:
            cand = low | 1
    raise RuntimeError(f"failed to find prime in {bits} bits interval [{lo},{hi}]")

def gen_pair_for_bits(B: int, rng: random.Random, max_attempts=5000):
    p_bits = B // 2
    q_bits = B - p_bits  # for even B, same as p_bits
    # ensure balanced: diff <=1 automatically
    for attempt in range(max_attempts):
        # Bias to far apart: p lower half, q upper half
        # Occasionally try more extreme: lower quarter / upper quarter to increase distance
        if attempt % 3 == 0:
            p = random_prime_in_interval(p_bits, 0.0, 0.5, rng)
            q = random_prime_in_interval(q_bits, 0.5, 1.0, rng)
        elif attempt % 3 == 1:
            p = random_prime_in_interval(p_bits, 0.0, 0.35, rng)
            q = random_prime_in_interval(q_bits, 0.65, 1.0, rng)
        else:
            p = random_prime_in_interval(p_bits, 0.0, 0.4, rng)
            q = random_prime_in_interval(q_bits, 0.6, 1.0, rng)
        if p == q:
            continue
        # Ensure p <= q for consistency in distance calc? but min_dist uses both
        # Keep p as smaller to maximize distance? We have p from lower, q upper, so p<q likely
        N = p * q
        if N.bit_length() != B:
            # try swap bits if needed? For even B product may be B-1, skip
            continue
        isqrt_N = math.isqrt(N)
        min_dist = min(abs(p - isqrt_N), abs(q - isqrt_N))
        if min_dist < 100_000:
            continue
        rel = min_dist / isqrt_N if isqrt_N else 0
        if rel < 0.01:
            continue
        # Ensure p!=q already, and odd primes
        return p, q, N, isqrt_N, min_dist, rel
    raise RuntimeError(f"failed to generate pair for B={B} after {max_attempts} attempts")

def main():
    parser = argparse.ArgumentParser(description="Generate hold-out corpus")
    parser.add_argument("--seed", type=int, required=True, help="deterministic seed")
    parser.add_argument("--out-dir", type=str, required=True, help="output directory (will contain public/private)")
    parser.add_argument("--count", type=int, default=60, help="total rows")
    args = parser.parse_args()

    seed = args.seed
    count = args.count
    out_dir = Path(args.out_dir)
    public_dir = out_dir / "public"
    private_dir = out_dir / "private"
    public_dir.mkdir(parents=True, exist_ok=True)
    private_dir.mkdir(parents=True, exist_ok=True)

    rng = random.Random(seed)

    # Distribution: cycle 48,50,52
    bit_cycle = [48,50,52]
    # If count < 30, still use 50-bit only? But spec says mix allowed with >=10 per if mix.
    # We will distribute evenly.
    rows = []
    # Preallocate target bits list
    targets = []
    for i in range(count):
        targets.append(bit_cycle[i % len(bit_cycle)])

    # Shuffle targets deterministically to avoid ordering bias but reproducible
    # Use rng to shuffle
    # To keep reproducibility, we shuffle after generating list? That would affect pair generation order.
    # Instead keep cyclic order for simplicity and determinism.

    seen_N = set()
    for row_idx, B in enumerate(targets):
        p,q,N,isqrt_N,min_dist,rel = gen_pair_for_bits(B, rng)
        # Ensure unique N
        attempts = 0
        while N in seen_N and attempts < 100:
            p,q,N,isqrt_N,min_dist,rel = gen_pair_for_bits(B, rng)
            attempts += 1
        seen_N.add(N)
        ceil_sqrt = isqrt_N if isqrt_N*isqrt_N == N else isqrt_N+1
        fermat_steps = (p + q)//2 - ceil_sqrt
        rows.append({
            "case_id": f"holdout_meta_{B}_{row_idx:05d}",
            "bits": B,
            "N": str(N),
            "p": str(p),
            "q": str(q),
            "isqrt_N": isqrt_N,
            "min_dist_to_sqrt": min_dist,
            "rel_dist": rel,
            "fermat_steps_estimate": fermat_steps,
            "seed": seed,
            "row_index": row_idx
        })

    # Write public
    public_path = public_dir / "holdout_public.jsonl"
    private_path = private_dir / "holdout_audit.jsonl"
    with open(public_path, "w") as f:
        for r in rows:
            pub = {
                "case_id": r["case_id"],
                "bits": r["bits"],
                "N": r["N"],
                "generator": "meta_ai_holdout_v1",
                "seed": r["seed"],
                "row_index": r["row_index"]
            }
            f.write(json.dumps(pub) + "\n")
    with open(private_path, "w") as f:
        for r in rows:
            priv = {
                "case_id": r["case_id"],
                "bits": r["bits"],
                "N": r["N"],
                "p": r["p"],
                "q": r["q"],
                "isqrt_N": r["isqrt_N"],
                "min_dist_to_sqrt": r["min_dist_to_sqrt"],
                "rel_dist": r["rel_dist"],
                "fermat_steps_estimate": r["fermat_steps_estimate"],
                "seed": r["seed"],
                "row_index": r["row_index"]
            }
            f.write(json.dumps(priv) + "\n")

    # Summary
    from collections import Counter
    cnt = Counter(r["bits"] for r in rows)
    dists = [r["min_dist_to_sqrt"] for r in rows]
    print(f"Generated {len(rows)} rows: {dict(cnt)}")
    print(f"min_dist_to_sqrt: min={min(dists)} max={max(dists)} median={sorted(dists)[len(dists)//2]}")
    print(f"All rows satisfy min_dist>=100000 and rel>=0.01: {all(r['min_dist_to_sqrt']>=100000 and r['rel_dist']>=0.01 for r in rows)}")
    print(f"Public: {public_path}")
    print(f"Private: {private_path}")

if __name__ == "__main__":
    main()
