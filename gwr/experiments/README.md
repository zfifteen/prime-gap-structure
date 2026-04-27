# GWR Experiments

This directory tracks the executable and artifact surface for the `Gap Selected integer
Rule`.

## Proof Pursuit

- [`proof/`](./proof/):
  scripts and artifacts behind the proved GWR theorem, including the
  admissibility frontier, residual-class closure runs, and the older bridge
  certificate retained as historical comparison.

## Current Validation Entry Points

- [`benchmarks/python/gap_ridge/lexicographic_peak_validation.py`](../../benchmarks/python/gap_ridge/lexicographic_peak_validation.py)
  Legacy validation script for the committed tested surface.
- [`benchmarks/python/gap_ridge/lexicographic_rule_revalidation.py`](../../benchmarks/python/gap_ridge/lexicographic_rule_revalidation.py)
  Extended revalidation script with explicit selected integer comparisons, new sampled
  windows, enrichment statistics, and alternative score probes.

## Current Outputs

- [`benchmarks/output/python/gap_ridge/lexicographic_peak_validation/lexicographic_peak_validation.json`](../../benchmarks/output/python/gap_ridge/lexicographic_peak_validation/lexicographic_peak_validation.json)
- [`output/lexicographic_rule_revalidation_summary.json`](../../output/lexicographic_rule_revalidation_summary.json)
- [`output/lexicographic_rule_revalidation_report.md`](../../output/lexicographic_rule_revalidation_report.md)

## Registry

### Baseline committed surface

- exact `10^6`
- exact `10^7`
- sampled even-window ladder from `10^8` through `10^18`

### Extended revalidation surface

- exact `2 * 10^7`
- sampled even-window and seeded-window runs at `10^8`, `10^9`, `10^10`,
  `10^11`, and `10^12`
- enrichment measurement on the `10^9` even-window surface
- alternative score probes on exact `10^6` and sampled `10^9`

## Working Rule

For this subtree, a tested regime validates `GWR` if and only if it contains
zero counterexample gaps where the raw-`Z` selected integer differs from the
leftmost minimum-divisor integer.
