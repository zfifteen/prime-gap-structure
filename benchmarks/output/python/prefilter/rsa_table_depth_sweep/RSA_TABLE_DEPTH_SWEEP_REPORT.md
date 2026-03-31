# RSA Table-Depth Sweep

Date: 2026-03-31

This sweep holds the deterministic RSA workload fixed at the first end-to-end regime that uses `4096`-bit prime candidates, then measures how deeper covered odd-prime tables change rejection, Miller-Rabin work, and wall time.

## Configuration

- `rsa_bits`: 8192
- `prime_bits`: 4096
- `keypair_count`: 2
- `public_exponent`: 65537
- `table_limits`: [300007, 1000003, 3000000]

## Headline Findings

- Baseline Miller-Rabin-only key generation took `244.265` s total for `2` deterministic keypairs.
- The fastest accelerated cell used covered odd primes through `1,000,003` and ran in `79.514` s for a measured `3.072x` speedup.
- In that best cell, proxy rejection was `91.43%` against a structural ceiling of `91.87%`.

## Sweep Summary

| Covered odd primes | Theory rejection | Observed rejection | Saved MR call rate | Speedup | Accelerated wall time (s) | Proxy time (s) | Survivor MR time (s) |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 300,007 | 91.096550% | 90.308123% | 90.308123% | 2.835541x | 86.143903 | 1.237412 | 80.979567 |
| 1,000,003 | 91.872366% | 91.428571% | 91.428571% | 3.071985x | 79.513592 | 3.541108 | 72.091973 |
| 3,000,000 | 92.471037% | 92.072829% | 92.072829% | 3.015842x | 80.993816 | 9.651933 | 67.375069 |

## Baseline Reference

| Metric | Value |
|---|---:|
| Total wall time (s) | 244.264574 |
| Mean time per keypair (s) | 122.132287 |
| Total candidates tested | 3570 |
| Total Miller-Rabin calls | 3570 |
| Survivor Miller-Rabin time (s) | 240.295672 |
| Assembly + validation time (s) | 3.881435 |

## Reproduction

```bash
python3 benchmarks/python/prefilter/rsa_table_depth_sweep.py --output-dir benchmarks/output/python/prefilter/rsa_table_depth_sweep --rsa-bits 8192 --keypair-count 2 --table-limits 300007 1000003 3000000 --chunk-size 256 --primary-limit 200003 --tail-limit 300007 --public-exponent 65537 --namespace cdl-rsa-table-depth-sweep
```

Artifacts written by this sweep:

- `rsa_table_depth_sweep_results.json`
- `rsa_table_depth_sweep_results.csv`
- `RSA_TABLE_DEPTH_SWEEP_REPORT.md`
- `rsa_depth_speedup.svg`
- `rsa_depth_rejection.svg`
- `rsa_depth_timing_breakdown.svg`
