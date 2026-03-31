# Table-Depth Structural Sweep

Date: 2026-03-31

This sweep fixes the covered odd-prime limit, varies candidate bit length, and measures whether proxy rejection stays locked to the covered small-factor layer instead of following prime density.

## Headline Findings

- With covered odd primes through `300,007`, the exact structural rejection ceiling is `91.10%` and the observed spread across the bit-length sweep was `2.246` percentage points.
- With covered odd primes through `1,000,003`, the exact structural rejection ceiling is `91.87%` and the observed spread across the bit-length sweep was `1.831` percentage points.
- With covered odd primes through `3,000,000`, the exact structural rejection ceiling is `92.47%` and the observed spread across the bit-length sweep was `1.782` percentage points.

## Odd-Candidate Prime Density Reference

- `2048` bits: odd-candidate prime density estimate `0.140888%`
- `4096` bits: odd-candidate prime density estimate `0.070444%`
- `8192` bits: odd-candidate prime density estimate `0.035222%`
- `16384` bits: odd-candidate prime density estimate `0.017611%`

## Per-Panel Results

| Covered odd primes | Bit length | Candidates | Observed rejection | Theory | Observed - theory | Proxy mean (ms) |
|---:|---:|---:|---:|---:|---:|---:|
| 300,007 | 2048 | 4096 | 89.477539% | 91.096550% | -1.619011% | 0.267279 |
| 300,007 | 4096 | 4096 | 91.723633% | 91.096550% | +0.627083% | 0.305423 |
| 300,007 | 8192 | 4096 | 91.479492% | 91.096550% | +0.382942% | 0.713589 |
| 300,007 | 16384 | 4096 | 91.040039% | 91.096550% | -0.056511% | 1.683208 |
| 1,000,003 | 2048 | 4096 | 90.478516% | 91.872366% | -1.393850% | 0.765158 |
| 1,000,003 | 4096 | 4096 | 92.309570% | 91.872366% | +0.437204% | 0.901730 |
| 1,000,003 | 8192 | 4096 | 92.211914% | 91.872366% | +0.339548% | 1.947533 |
| 1,000,003 | 16384 | 4096 | 91.625977% | 91.872366% | -0.246390% | 4.595307 |
| 3,000,000 | 2048 | 4096 | 91.113281% | 92.471037% | -1.357756% | 2.112436 |
| 3,000,000 | 4096 | 4096 | 92.895508% | 92.471037% | +0.424471% | 2.417711 |
| 3,000,000 | 8192 | 4096 | 92.797852% | 92.471037% | +0.326814% | 4.979432 |
| 3,000,000 | 16384 | 4096 | 92.114258% | 92.471037% | -0.356779% | 12.495340 |

## Sweep Summary

| Covered odd primes | Theory rejection | Observed min | Observed max | Spread (pp) | Ideal MR-only speedup ceiling |
|---:|---:|---:|---:|---:|---:|
| 300,007 | 91.096550% | 89.477539% | 91.723633% | 2.246 | 11.231601x |
| 1,000,003 | 91.872366% | 90.478516% | 92.309570% | 1.831 | 12.303704x |
| 3,000,000 | 92.471037% | 91.113281% | 92.895508% | 1.782 | 13.282042x |

## Reproduction

```bash
python3 benchmarks/python/prefilter/table_depth_sweep.py --output-dir benchmarks/output/python/prefilter/table_depth_sweep --bit-lengths 2048 4096 8192 16384 --table-limits 300007 1000003 3000000 --candidate-count 4096 --chunk-size 256 --primary-limit 200003 --tail-limit 300007 --namespace cdl-table-depth-sweep
```

Artifacts written by this sweep:

- `table_depth_sweep_results.json`
- `table_depth_sweep_results.csv`
- `TABLE_DEPTH_SWEEP_REPORT.md`
- `table_depth_collapse.svg`
