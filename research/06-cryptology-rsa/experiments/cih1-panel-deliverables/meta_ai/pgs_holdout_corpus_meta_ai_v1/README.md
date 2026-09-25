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