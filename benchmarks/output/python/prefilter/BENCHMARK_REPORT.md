# Crypto Prefilter Benchmark Report

Date: 2026-03-31

This report benchmarks the exact **Divisor Normalization Identity** (DNI) $Z(n) = n^{1 - d(n)/2}$ calibration path where the current implementation is executable,
a deterministic CDL proxy backed by bit-length-gated interval-split chunked prime tables,
and fixed-base Miller-Rabin on deterministic cryptographic-scale odd candidates.

## Configuration

- `fixed_point_v`: 3.694528049465
- `exact_bits`: 20
- `exact_count`: 256
- `crypto_bits`: 2048
- `crypto_count`: 1024
- `bonus_crypto_bits`: 4096
- `bonus_crypto_count`: 256
- `proxy_trial_prime_limit`: 200003
- `proxy_chunk_size`: 256
- `proxy_tail_prime_limit`: 300007
- `proxy_tail_chunk_size`: 256
- `proxy_deep_tail_prime_limit`: 1000003
- `proxy_deep_tail_chunk_size`: 256
- `proxy_deep_tail_min_bits`: 4096
- `miller_rabin_bases`: [2, 3, 5, 7, 11, 13, 17, 19]
- `truth_check`: False

## Headline Findings

- The exact DNI path hit the fixed-point locus for `29` of `29` calibration primes within numeric tolerance, with `0` composite points on the locus.
- The deterministic proxy hit `29` fixed points on the same calibration corpus with `0` composite fixed points and calibration accuracy `100.00%`.
- On the same `20`-bit calibration corpus, fixed-base Miller-Rabin matched exact primality with accuracy `100.00%`.
- Mean runtime on the calibration corpus was `0.061570` ms per candidate for exact DNI `z_normalize`, `0.011647` ms for the deterministic proxy, and `0.001740` ms for Miller-Rabin.
- On the `2048`-bit control corpus, Miller-Rabin averaged `8.582226` ms per candidate and passed `1` of `1024` odd candidates; first pass index: `354`.
- The deterministic proxy rejected `932` of `1024` cryptographic candidates before Miller-Rabin (`91.02%`), cut the end-to-end pipeline to `2.949122` ms per candidate, and delivered a measured `2.91x` speedup over Miller-Rabin alone on this corpus.
- On the `4096`-bit bonus corpus, the same deterministic proxy rejected `234` of `256` candidates (`91.41%`), reduced mean runtime from `64.340912` ms to `19.300479` ms per candidate, and delivered a measured `3.33x` speedup.
- The current exact calibration path was intentionally not run on `2048`-bit arbitrary candidates because exact divisor counting still uses `O(sqrt n)` enumeration; the implied trial space is about `2^1024` divisibility checks per worst-case candidate.

## Exact Calibration

| Metric | Value |
|---|---:|
| Candidate count | 256 |
| Prime count | 29 |
| Composite count | 227 |
| Prime mean kappa | 3.688275 |
| Composite mean kappa | 16.754550 |
| Separation ratio | 4.542652 |
| Algebraic fixed points | 29 |
| Numeric fixed points | 29 |
| Numeric false fixed points | 0 |
| Strict composite contractions | 227 |
| Mean exact `z_normalize` time (ms) | 0.061570 |
| Mean Miller-Rabin time (ms) | 0.001740 |

## Proxy Calibration

| Metric | Value |
|---|---:|
| Trial prime limit | 200003 |
| Trial prime count | 17984 |
| Chunk size | 256 |
| Tail prime limit | 300007 |
| Tail prime count | 8013 |
| Tail chunk size | 256 |
| Deep tail prime limit | 1000003 |
| Deep tail prime count | 52501 |
| Deep tail chunk size | 256 |
| Deep tail minimum bits | 4096 |
| Fixed points | 29 |
| Composite false fixed points | 0 |
| Strict composite contractions | 227 |
| Accuracy | 100.000000% |
| Precision | 100.000000% |
| Recall | 100.000000% |
| Mean proxy time (ms) | 0.011647 |

## Crypto Control

| Metric | Value |
|---|---:|
| Candidate count | 1024 |
| Miller-Rabin pass count | 1 |
| Miller-Rabin pass rate | 0.097656% |
| First pass index | 354 |
| Mean Miller-Rabin time (ms) | 8.582226 |

## Proxy + Miller-Rabin Pipeline

| Metric | Value |
|---|---:|
| Trial prime limit | 200003 |
| Trial prime count | 17984 |
| Chunk size | 256 |
| Tail prime limit | 300007 |
| Tail prime count | 8013 |
| Tail chunk size | 256 |
| Deep tail prime limit | 1000003 |
| Deep tail prime count | 52501 |
| Deep tail chunk size | 256 |
| Deep tail minimum bits | 4096 |
| Rejected before Miller-Rabin | 932 |
| Rejection rate | 91.015625% |
| Survivors to Miller-Rabin | 92 |
| Survivor rate | 8.984375% |
| Miller-Rabin passes after proxy | 1 |
| First pass index after proxy | 354 |
| Mean proxy time (ms) | 0.245011 |
| Mean survivor Miller-Rabin time (ms) | 30.097927 |
| Mean pipeline time (ms) | 2.949122 |
| Speedup vs MR-only | 2.910095x |

## 4096-bit Bonus Control

| Metric | Value |
|---|---:|
| Candidate count | 256 |
| Miller-Rabin pass count | 0 |
| Miller-Rabin pass rate | 0.000000% |
| First pass index | none in corpus |
| Mean Miller-Rabin time (ms) | 64.340912 |

## 4096-bit Bonus Proxy + Miller-Rabin Pipeline

| Metric | Value |
|---|---:|
| Trial prime limit | 200003 |
| Trial prime count | 17984 |
| Chunk size | 256 |
| Tail prime limit | 300007 |
| Tail prime count | 8013 |
| Tail chunk size | 256 |
| Deep tail prime limit | 1000003 |
| Deep tail prime count | 52501 |
| Deep tail chunk size | 256 |
| Deep tail minimum bits | 4096 |
| Rejected before Miller-Rabin | 234 |
| Rejection rate | 91.406250% |
| Survivors to Miller-Rabin | 22 |
| Survivor rate | 8.593750% |
| Miller-Rabin passes after proxy | 0 |
| First pass index after proxy | none in corpus |
| Mean proxy time (ms) | 0.949357 |
| Mean survivor Miller-Rabin time (ms) | 213.540326 |
| Mean pipeline time (ms) | 19.300479 |
| Speedup vs MR-only | 3.333643x |

## Calibration Timing Ratios

| Ratio | Value |
|---|---:|
| Exact CDL / Miller-Rabin | 35.386856x |
| Exact CDL / Proxy | 5.286309x |
| Proxy / Miller-Rabin | 6.694058x |

## Predictive Extensions

Single-stage survivor-only prototype (commit `6b1851d`) tested; prime enrichment < 0.05% and not promoted.

## Reproduction

Run the benchmark again with:

```bash
python3 benchmarks/python/prefilter/candidate_benchmark.py --exact-bits 20 --exact-count 256 --crypto-bits 2048 --crypto-count 1024 --bonus-crypto-bits 4096 --bonus-crypto-count 256 --proxy-trial-prime-limit 200003 --proxy-chunk-size 256 --proxy-tail-prime-limit 300007 --proxy-tail-chunk-size 256 --proxy-deep-tail-prime-limit 1000003 --proxy-deep-tail-chunk-size 256 --proxy-deep-tail-min-bits 4096 --mr-bases 2 3 5 7 11 13 17 19
```

These output files are generated into the local benchmark output directory.

## End-to-End RSA Key Generation

- Baseline generated `2` deterministic `64`-bit keypairs in `0.235958` ms total (`8476.084727` keypairs/s).
- The accelerated path generated the same `2` keypairs in `1.139417` ms total (`1755.283623` keypairs/s) for a measured `0.21x` speedup.
- The proxy removed `16` Miller-Rabin calls (`80.00%` of baseline MR work) while preserving identical deterministic keypairs across both paths.
- Timing buckets in the accelerated path broke down into `0.923001` ms proxy filtering (`81.01%`), `0.132959` ms survivor Miller-Rabin (`11.67%`), `0.030334` ms RSA assembly/validation (`2.66%`), and `0.053123` ms residual search overhead (`4.66%`).
- Final keypair primes were confirmed by `sympy.isprime`; under the DNI, all `4` confirmed factors remain exactly on the `Z = 1.0` fixed-point locus.

| Metric | Baseline | Accelerated |
|---|---:|---:|
| Keypair count | 2 | 2 |
| Total wall time (ms) | 0.235958 | 1.139417 |
| Keypairs per second | 8476.084727 | 1755.283623 |
| Mean time per keypair (ms) | 0.117979 | 0.569708 |
| Mean candidates per prime | 5.000000 | 5.000000 |
| Total candidates tested | 20 | 20 |
| Total Miller-Rabin calls | 20 | 4 |
| Total proxy rejections | 0 | 16 |
| Proxy rejection contribution | 0.000000% | 80.000000% |
| Saved Miller-Rabin call rate | 0.000000% | 80.000000% |
| Proxy filtering time (ms) | 0.000000 | 0.923001 |
| Survivor Miller-Rabin time (ms) | 0.129956 | 0.132959 |
| RSA assembly + validation time (ms) | 0.032750 | 0.030334 |
| Residual search overhead (ms) | 0.073252 | 0.053123 |
| Proxy filtering share | 0.000000% | 81.006427% |
| Survivor Miller-Rabin share | 55.075903% | 11.669038% |
| RSA assembly + validation share | 13.879589% | 2.662239% |
| Residual search overhead share | 31.044508% | 4.662297% |
| Matching deterministic keypairs | 2 | 2 |

## 4096-bit RSA Spot-Check

- Baseline generated `1` deterministic `128`-bit keypairs in `0.608583` ms total (`1643.161245` keypairs/s).
- The accelerated path generated the same `1` keypairs in `9.304417` ms total (`107.475836` keypairs/s) for a measured `0.07x` speedup.
- The proxy removed `74` Miller-Rabin calls (`94.87%` of baseline MR work) while preserving identical deterministic keypairs across both paths.
- Timing buckets in the accelerated path broke down into `8.591464` ms proxy filtering (`92.34%`), `0.361749` ms survivor Miller-Rabin (`3.89%`), `0.187375` ms RSA assembly/validation (`2.01%`), and `0.163829` ms residual search overhead (`1.76%`).
- Final keypair primes were confirmed by `sympy.isprime`; under the DNI, all `2` confirmed factors remain exactly on the `Z = 1.0` fixed-point locus.

| Metric | Baseline | Accelerated |
|---|---:|---:|
| Keypair count | 1 | 1 |
| Total wall time (ms) | 0.608583 | 9.304417 |
| Keypairs per second | 1643.161245 | 107.475836 |
| Mean time per keypair (ms) | 0.608583 | 9.304417 |
| Mean candidates per prime | 39.000000 | 39.000000 |
| Total candidates tested | 78 | 78 |
| Total Miller-Rabin calls | 78 | 4 |
| Total proxy rejections | 0 | 74 |
| Proxy rejection contribution | 0.000000% | 94.871795% |
| Saved Miller-Rabin call rate | 0.000000% | 94.871795% |
| Proxy filtering time (ms) | 0.000000 | 8.591464 |
| Survivor Miller-Rabin time (ms) | 0.328963 | 0.361749 |
| RSA assembly + validation time (ms) | 0.036458 | 0.187375 |
| Residual search overhead (ms) | 0.243162 | 0.163829 |
| Proxy filtering share | 0.000000% | 92.337478% |
| Survivor Miller-Rabin share | 54.053925% | 3.887928% |
| RSA assembly + validation share | 5.990637% | 2.013828% |
| Residual search overhead share | 39.955437% | 1.760766% |
| Matching deterministic keypairs | 1 | 1 |

## RSA Reproduction

Run the end-to-end RSA benchmark again with:

```bash
python3 benchmarks/python/prefilter/rsa_keygen_benchmark.py --rsa-bits 64 --rsa-keypair-count 2 --bonus-rsa-bits 128 --bonus-rsa-keypair-count 1 --public-exponent 65537
```
