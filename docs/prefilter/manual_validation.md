# Manual Validation

This repository uses manual validation only.

## 1. Install the Python package

```bash
python3 -m pip install -e ./src/python
```

## 2. Run the Python test suite

```bash
pytest tests/python -q
```

## 3. Verify the golden vectors directly

```bash
pytest tests/python/test_vectors.py -q
```

## 4. Run the smoke candidate benchmark

```bash
python3 benchmarks/python/prefilter/candidate_benchmark.py \
  --exact-bits 20 \
  --exact-count 32 \
  --crypto-bits 256 \
  --crypto-count 32 \
  --bonus-crypto-bits 512 \
  --bonus-crypto-count 16 \
  --output-dir benchmarks/output/python/prefilter
```

## 5. Run the smoke RSA benchmark

```bash
python3 benchmarks/python/prefilter/rsa_keygen_benchmark.py \
  --rsa-bits 64 \
  --rsa-keypair-count 2 \
  --bonus-rsa-bits 128 \
  --bonus-rsa-keypair-count 1 \
  --public-exponent 65537 \
  --output-dir benchmarks/output/python/prefilter
```

## 6. Reproduce the full benchmark suite

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
  --mr-bases 2 3 5 7 11 13 17 19 \
  --output-dir benchmarks/output/python/prefilter
```

```bash
python3 benchmarks/python/prefilter/rsa_keygen_benchmark.py \
  --rsa-bits 2048 \
  --rsa-keypair-count 300 \
  --bonus-rsa-bits 4096 \
  --bonus-rsa-keypair-count 50 \
  --public-exponent 65537 \
  --output-dir benchmarks/output/python/prefilter
```

## 7. Run the deterministic RSA sweep up to 4096 bits

```bash
python3 benchmarks/python/prefilter/rsa_sweep_benchmark.py \
  --max-rsa-bits 4096 \
  --public-exponent 65537 \
  --output-dir benchmarks/output/python/prefilter/rsa_sweep
```

## 8. Run the exact raw composite Z gap-edge study

```bash
python3 benchmarks/python/gap_ridge/raw_z_gap_edge_study.py
```
