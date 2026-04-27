# GWR Experiment Registry

This registry records the currently validated `Gap Winner Rule` (`GWR`)
surfaces in one place.

It is an index, not a second source of truth. The executable details and
machine-readable outputs remain in the linked scripts and JSON artifacts.

## Decision Rule

A tested regime validates `GWR` if and only if it contains zero counterexample
gaps where the raw-`Z` selected integer differs from the leftmost minimum-divisor integer.

## Registered Surfaces

| Label | Surface | Status | Counterexamples | Primary Artifact |
| --- | --- | --- | ---: | --- |
| legacy-committed | exact `10^6`, exact `10^7`, sampled even-window `10^8` through `10^18` | validated_on_tested_surface | 0 | [`lexicographic_peak_validation.json`](../../benchmarks/output/python/gap_ridge/lexicographic_peak_validation/lexicographic_peak_validation.json) |
| revalidation-2026-04-03 | exact `2 * 10^7`; sampled even-window and seeded-window `10^8` through `10^12`; enrichment probe at `10^9`; alternative score probes on exact `10^6` and sampled `10^9` | validated_on_new_tested_surface | 0 | [`lexicographic_rule_revalidation_summary.json`](../../output/lexicographic_rule_revalidation_summary.json) |

## Supporting Entry Points

- [`lexicographic_peak_validation.py`](../../benchmarks/python/gap_ridge/lexicographic_peak_validation.py)
- [`lexicographic_rule_revalidation.py`](../../benchmarks/python/gap_ridge/lexicographic_rule_revalidation.py)
- [`runs.py`](../../src/python/z_band_prime_gap_ridge/runs.py)

## Notes

- The first row preserves the legacy artifact naming.
- The second row records the first repo-native `GWR` revalidation package.
- Future entries should add a new row rather than rewrite the existing ones.
