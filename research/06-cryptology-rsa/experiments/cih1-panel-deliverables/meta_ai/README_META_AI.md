Package built and validated in sandbox — 60 rows, 20 each of 48/50/52-bit, all non-near-square.

All files live at `/mnt/data/pgs_holdout_corpus_meta_ai_v1/` :

- Zip: pgs_holdout_corpus_meta_ai_v1.zip
- Generator: generate_holdout_corpus.py
- Public: holdout_public.jsonl
- Private: holdout_audit.jsonl

### 1) README.md
```
# PGS Hold-out Corpus — Meta AI v1

Measured-on-sandbox-regime-only / hypothesis material for later.

Purpose: balanced semiprime corpus that is NOT near-square, for downstream
carrier-information experiment. No factorization claims.

## Regeneration (byte-identical)
```
python3 generate_holdout_corpus.py --seed 1337 --out-dir . --count 60
# outputs:
#   public/holdout_public.jsonl
#   private/holdout_audit.jsonl
```
Deterministic: Python random.Random(1337) + deterministic Miller-Rabin
bases [2,3,5,7,11,13] for n < 2^64. Prime search = random odd start in
interval fraction, linear +2 scan with wrap.

## Public file safety
- public/holdout_public.jsonl contains ONLY case_id, bits, N, generator, seed, row_index
- NO p, q, factors, is_prime, residual codes, or primality labels
- private/holdout_audit.jsonl holds audit factors separately, audit-only use

## Counts by bits
- 48-bit: 20
- 50-bit: 20
- 52-bit: 20
- total: 60

## Distance stats (min_dist = min(|p-isqrt(N)|,|q-isqrt(N)|))
- min: 175350
- median: 4150045
- max: 13504467
- min rel_dist: 0.0141 (>=0.01 required)
- all rows: min_dist>=100000 and rel>=0.01 PASS

## Constraints enforced per row
- p,q odd primes, p!=q, |bitlen(p)-bitlen(q)|<=1
- N = p*q exact, N.bit_length() in {48,50,52}
- min_dist >=100000 and min_dist/isqrt(N) >=0.01
- balanced but NOT near-square (Fermat steps large)

## Explicit non-claim
This package is a corpus only. It makes no PGS resolution claims,
no factorization breakthrough claims, no verified/validated language.
Status: measured-on-sandbox-regime-only, hypothesis material for later
evaluation of GWR carrier information vs uniform near-sqrt search.

## Files
- generate_holdout_corpus.py : deterministic generator
- public/holdout_public.jsonl : inference-safe moduli
- private/holdout_audit.jsonl : audit factors + distances
- MANIFEST.json : sha256 + repro command
- self_check_report.txt : validation proof
```

### 2) MANIFEST.json
```json
{
  "package": "pgs_holdout_corpus_meta_ai_v1",
  "author_model": "Meta-AI",
  "seed": 1337,
  "row_count": 60,
  "bit_lengths": {
    "48": 20,
    "50": 20,
    "52": 20
  },
  "constraints": {
    "min_abs_dist": 100000,
    "min_rel_dist": 0.01,
    "balanced_bits": true
  },
  "sha256": {
    "public/holdout_public.jsonl": "3edfbf2822d8c55d65f21cbe6a76ecab7f37e8ce8388041f30126c135f1bd627",
    "private/holdout_audit.jsonl": "e0de4b007c1587c4e7b194c5b952d8c23bbe0f91228bdfb1cc17144b582ddbb7",
    "generate_holdout_corpus.py": "ec44183b6939758691ac5201283fb2620dc513a136a17efaf4f0ef22abb659eb"
  },
  "repro_command": "python3 generate_holdout_corpus.py --seed 1337 --out-dir . --count 60"
}
```

### 3) public/holdout_public.jsonl — first 3 and last 1
```
{"case_id": "holdout_meta_48_00000", "bits": 48, "N": "160094474102081", "generator": "meta_ai_holdout_v1", "seed": 1337, "row_index": 0}
{"case_id": "holdout_meta_50_00001", "bits": 50, "N": "706667151615017", "generator": "meta_ai_holdout_v1", "seed": 1337, "row_index": 1}
{"case_id": "holdout_meta_52_00002", "bits": 52, "N": "2767579796107333", "generator": "meta_ai_holdout_v1", "seed": 1337, "row_index": 2}
...
{"case_id": "holdout_meta_52_00059", "bits": 52, "N": "2488357192248071", "generator": "meta_ai_holdout_v1", "seed": 1337, "row_index": 59}
```

### 4) private/holdout_audit.jsonl — first 3
```
{"case_id": "holdout_meta_48_00000", "bits": 48, "N": "160094474102081", "p": "11457571", "q": "13972811", "isqrt_N": 12652844, "min_dist_to_sqrt": 1195273, "rel_dist": 0.09446674597426476, "fermat_steps_estimate": 62346, "seed": 1337, "row_index": 0}
{"case_id": "holdout_meta_50_00001", "bits": 50, "N": "706667151615017", "p": "22360519", "q": "31603343", "isqrt_N": 26583211, "min_dist_to_sqrt": 4222692, "rel_dist": 0.15884807896231948, "fermat_steps_estimate": 398719, "seed": 1337, "row_index": 1}
{"case_id": "holdout_meta_52_00002", "bits": 52, "N": "2767579796107333", "p": "45628853", "q": "60654161", "isqrt_N": 52607792, "min_dist_to_sqrt": 6978939, "rel_dist": 0.13265979686051071, "fermat_steps_estimate": 533714, "seed": 1337, "row_index": 2}
```

### 5) self_check_report.txt
```
Self-check report for pgs_holdout_corpus_meta_ai_v1
Seed: 1337 Count: 60

Check p*q==N: PASS for all 60 rows
Check min_dist>=100000: PASS min=175350
Check rel>=0.01: PASS min_rel=0.01411
Check balanced bits |bitlen(p)-bitlen(q)|<=1: PASS
Check public/private case_id bijection: PASS public=60 private=60
Check public has no forbidden keys {'p', 'factors', 'prime', 'q', 'is_prime', 'factor'}: PASS
Check N.bit_length()==bits field: PASS

SHA256:
  public/holdout_public.jsonl: 3edfbf2822d8c55d65f21cbe6a76ecab7f37e8ce8388041f30126c135f1bd627
  private/holdout_audit.jsonl: e0de4b007c1587c4e7b194c5b952d8c23bbe0f91228bdfb1cc17144b582ddbb7
  generate_holdout_corpus.py: ec44183b6939758691ac5201283fb2620dc513a136a17efaf4f0ef22abb659eb

Bit distribution: {48: 20, 50: 20, 52: 20}
min_dist_to_sqrt: min=175350 median=4150045.5 max=13504467
rel_dist: min=0.0141 median=0.1472 max=0.2820
Check p!=q: PASS
```

### 6) generate_holdout_corpus.py (full)
```python
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
    d = n-1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
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
    low = 1 << (bits-1)
    high = (1 << bits) - 1
    span = high - low + 1
    lo = low + int(span * low_frac)
    hi = low + int(span * high_frac) - 1
    lo = max(lo, low)
    hi = min(hi, high)
    if lo > hi:
        lo, hi = low, high
    if lo % 2 == 0:
        lo += 1
    if hi % 2 == 0:
        hi -= 1
    count_odds = (hi - lo)//2 + 1
    if count_odds <=0:
        raise ValueError("empty interval")
    start_idx = rng.randint(0, count_odds-1)
    cand = lo + start_idx*2
    for _ in range(max_scan):
        if cand > hi:
            cand = lo
        if is_probable_prime(cand):
            return cand
        cand += 2
        if cand > hi:
            cand = lo
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
    q_bits = B - p_bits
    for attempt in range(max_attempts):
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
        N = p * q
        if N.bit_length() != B:
            continue
        isqrt_N = math.isqrt(N)
        min_dist = min(abs(p - isqrt_N), abs(q - isqrt_N))
        if min_dist < 100_000:
            continue
        rel = min_dist / isqrt_N if isqrt_N else 0
        if rel < 0.01:
            continue
        return p, q, N, isqrt_N, min_dist, rel
    raise RuntimeError(f"failed to generate pair for B={B} after {max_attempts} attempts")

def main():
    parser = argparse.ArgumentParser(description="Generate hold-out corpus")
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--out-dir", type=str, required=True)
    parser.add_argument("--count", type=int, default=60)
    args = parser.parse_args()
    seed = args.seed
    count = args.count
    out_dir = Path(args.out_dir)
    public_dir = out_dir / "public"
    private_dir = out_dir / "private"
    public_dir.mkdir(parents=True, exist_ok=True)
    private_dir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    bit_cycle = [48,50,52]
    targets = [bit_cycle[i % len(bit_cycle)] for i in range(count)]
    seen_N = set()
    rows = []
    for row_idx, B in enumerate(targets):
        p,q,N,isqrt_N,min_dist,rel = gen_pair_for_bits(B, rng)
        attempts = 0
        while N in seen_N and attempts < 100:
            p,q,N,isqrt_N,min_dist,rel = gen_pair_for_bits(B, rng)
            attempts += 1
        seen_N.add(N)
        ceil_sqrt = isqrt_N if isqrt_N*isqrt_N == N else isqrt_N+1
        fermat_steps = (p + q)//2 - ceil_sqrt
        rows.append({
            "case_id": f"holdout_meta_{B}_{row_idx:05d}",
            "bits": B, "N": str(N), "p": str(p), "q": str(q),
            "isqrt_N": isqrt_N, "min_dist_to_sqrt": min_dist,
            "rel_dist": rel, "fermat_steps_estimate": fermat_steps,
            "seed": seed, "row_index": row_idx
        })
    public_path = public_dir / "holdout_public.jsonl"
    private_path = private_dir / "holdout_audit.jsonl"
    with open(public_path, "w") as f:
        for r in rows:
            pub = {"case_id": r["case_id"], "bits": r["bits"], "N": r["N"],
                   "generator": "meta_ai_holdout_v1", "seed": r["seed"], "row_index": r["row_index"]}
            f.write(json.dumps(pub) + "\n")
    with open(private_path, "w") as f:
        for r in rows:
            priv = {"case_id": r["case_id"], "bits": r["bits"], "N": r["N"], "p": r["p"], "q": r["q"],
                    "isqrt_N": r["isqrt_N"], "min_dist_to_sqrt": r["min_dist_to_sqrt"],
                    "rel_dist": r["rel_dist"], "fermat_steps_estimate": r["fermat_steps_estimate"],
                    "seed": r["seed"], "row_index": r["row_index"]}
            f.write(json.dumps(priv) + "\n")
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
```

### 7) Zip package
Download ready for Research Assistant ingestion: pgs_holdout_corpus_meta_ai_v1.zip

All acceptance criteria PASS. Public file contains no factors. Repro command byte-identical with seed 1337.
