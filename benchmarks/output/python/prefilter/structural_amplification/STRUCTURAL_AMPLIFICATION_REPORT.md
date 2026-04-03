# Structural Amplification Verification

This report tests the fixed-pipeline amplification hypothesis directly on the deterministic RSA key-generation path.
The same prefilter setup is held fixed across the whole size ladder. Each size is rerun on the same deterministic workload, medians are taken across repeats, and the verdict is driven by a predeclared rule.

## Configuration

- `schedule`: [{'rsa_bits': 1024, 'keypair_count': 24}, {'rsa_bits': 2048, 'keypair_count': 12}, {'rsa_bits': 3072, 'keypair_count': 8}, {'rsa_bits': 4096, 'keypair_count': 6}, {'rsa_bits': 8192, 'keypair_count': 2}]
- `repetitions`: 3
- `evaluation_min_rsa_bits`: 2048
- `rejection_stability_tolerance`: 2.00%
- `public_exponent`: 65537

## Decision Rule

1. For RSA sizes at or above `2048`, the proxy rejection rate must stay within a `2.00%` band.
2. Baseline mean time per keypair must rise across the evaluation cells.
3. Proxy mean time per keypair must grow more slowly than baseline mean time per keypair between the first and last evaluation cells.
4. Median realized speedup must rise across the evaluation cells.
5. The final step in speedup must exceed the measured timing-noise band from the last two cells.

## Verdict

- `verdict`: **verified**
- Across RSA sizes `[2048, 3072, 4096, 8192]`, rejection stayed inside a `0.798` percentage-point band while median speedup kept rising.
- The final speedup step from `4096` to `8192` was `0.512869x` against a measured noise band of `0.062889x`.

## Verification Table

| RSA bits | Keypairs | Repeats | Rejection | Baseline mean/keypair (ms) | Proxy mean/keypair (ms) | Survivor MR mean/keypair (ms) | Speedup median | Speedup range | Ceiling | Ceiling share |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1024 | 24 | 3 | 91.316073% | 87.959604 | 30.754011 | 31.774626 | 1.282760x | 1.264699x..1.315472x | 11.515528x | 11.139398% |
| 2048 | 12 | 3 | 91.042048% | 751.221059 | 75.868970 | 247.823570 | 2.032357x | 2.024229x..2.144987x | 11.163265x | 18.205755% |
| 3072 | 8 | 3 | 91.317440% | 3991.494651 | 188.524665 | 1234.906690 | 2.598276x | 2.570266x..2.619038x | 11.517341x | 22.559686% |
| 4096 | 6 | 3 | 91.292766% | 16987.298528 | 460.499409 | 5290.083007 | 2.831369x | 2.791199x..2.870278x | 11.484704x | 24.653395% |
| 8192 | 2 | 3 | 91.839585% | 170917.934479 | 2355.057509 | 46811.805732 | 3.344239x | 3.303073x..3.349772x | 12.254279x | 27.290377% |

## Mechanism Check

- Baseline mean time growth factor across the evaluation regime: `227.520159x`.
- Proxy mean time growth factor across the evaluation regime: `31.041116x`.

Artifacts written by this verifier:

- `structural_amplification_results.json`
- `structural_amplification_results.csv`
- `STRUCTURAL_AMPLIFICATION_REPORT.md`
- `structural_amplification_speedup.svg`
- `structural_amplification_rejection.svg`
- `structural_amplification_costs.svg`

## Reproduction

```bash
python3 benchmarks/python/prefilter/structural_amplification_verifier.py --output-dir /Users/velocityworks/IdeaProjects/z-band-prime-prefilter/benchmarks/output/python/prefilter/structural_amplification --schedule 1024:24 2048:12 3072:8 4096:6 8192:2 --repetitions 3 --evaluation-min-rsa-bits 2048 --rejection-stability-tolerance 0.02 --public-exponent 65537 --namespace cdl-structural-amplification
```
