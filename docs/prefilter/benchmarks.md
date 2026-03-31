# Benchmarks

The current validated production numbers come from the extracted Python implementation built around the **Divisor Curvature Identity** (DCI) \(Z(n) = n^{1 - d(n)/2}\).

## End-to-End RSA Key Generation

- `2048` bits, `300` deterministic keypairs:
  baseline `291938.126792` ms
  accelerated `139942.831833` ms
  speedup `2.09x`
  Miller-Rabin reduction `90.97%`
- `4096` bits, `50` deterministic keypairs:
  baseline `757750.922792` ms
  accelerated `268557.631625` ms
  speedup `2.82x`
  Miller-Rabin reduction `91.07%`

## Candidate-Loop Screening

- `2048`-bit control corpus:
  proxy rejection `91.02%`
  pipeline speedup `2.95x`
- `4096`-bit control corpus:
  proxy rejection `91.41%`
  pipeline speedup `3.33x`

## DCI Calibration

- `29/29` calibration primes stayed on `Z = 1.0`
- `0` composite false fixed points

## Table-Depth Structural Sweep

The repository also includes a deterministic sweep that fixes covered prime-table depth,
varies candidate bit length, and writes a report plus SVG plot showing whether rejection
tracks table depth rather than prime density.

## Reproduction Commands

Candidate benchmark:

```bash
python3 benchmarks/python/prefilter/candidate_benchmark.py \
  --exact-bits 20 \
  --exact-count 256 \
  --crypto-bits 2048 \
  --crypto-count 1024 \
  --bonus-crypto-bits 4096 \
  --bonus-crypto-count 256 \
  --proxy-trial-prime-limit 200003 \
  --proxy-chunk-size 256 \
  --proxy-tail-prime-limit 300007 \
  --proxy-tail-chunk-size 256 \
  --proxy-deep-tail-prime-limit 1000003 \
  --proxy-deep-tail-chunk-size 256 \
  --proxy-deep-tail-min-bits 4096 \
  --mr-bases 2 3 5 7 11 13 17 19
```

RSA benchmark:

```bash
python3 benchmarks/python/prefilter/rsa_keygen_benchmark.py \
  --rsa-bits 2048 \
  --rsa-keypair-count 300 \
  --bonus-rsa-bits 4096 \
  --bonus-rsa-keypair-count 50 \
  --public-exponent 65537
```

RSA sweep benchmark:

```bash
python3 benchmarks/python/prefilter/rsa_sweep_benchmark.py \
  --max-rsa-bits 4096 \
  --public-exponent 65537 \
  --output-dir benchmarks/output/python/prefilter/rsa_sweep
```

Table-depth sweep:

```bash
python3 benchmarks/python/prefilter/table_depth_sweep.py \
  --output-dir benchmarks/output/python/prefilter/table_depth_sweep \
  --bit-lengths 2048 4096 8192 16384 \
  --table-limits 300007 1000003 3000000 \
  --candidate-count 1024
```

End-to-end 8192-bit RSA table-depth sweep:

```bash
python3 benchmarks/python/prefilter/rsa_table_depth_sweep.py \
  --output-dir benchmarks/output/python/prefilter/rsa_table_depth_sweep \
  --rsa-bits 8192 \
  --keypair-count 2 \
  --table-limits 300007 1000003 3000000
```
