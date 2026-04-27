# Lexicographic Winner-Take-All Peak Rule Revalidation

## Overview

Inside each prime gap `(p, q)`, the raw-`Z` integer is the interior composite that maximizes `(1 - d(n) / 2) * ln(n)`.
The leftmost minimizer-take-all rule says the same integer is obtained by a simpler order: minimize `d(n)` over the interior, then choose the leftmost integer of that minimum.
This revalidation extended the committed surface from `10^6`, `10^7`, `10^8`, `10^9`, `10^10`, `10^11`, `10^12`, `10^13`, `10^14`, `10^15`, `10^16`, `10^17`, `10^18` into a new exact run, new sampled multi-seed windows, and a small alternative-score probe. No counterexamples were found on any new tested surface.

## Methods

The implementation follows the existing near-endpoint raw-Z peak machinery in [`runs.py`](../src/python/z_band_prime_gap_ridge/runs.py), which computes divisor counts on an exact interval, identifies primes as `d(n) = 2`, enumerates adjacent-prime gaps, and scores each interior integer with raw-`Z` using `np.argmax` on `(1 - d/2) * log(n)`.
The rule statement and previously committed findings come from [`lexicographic_winner_take_all_peak_rule.md`](../docs/findings/lexicographic_winner_take_all_peak_rule.md), and the prior validation surface comes from [`lexicographic_peak_validation.json`](../benchmarks/output/python/gap_ridge/lexicographic_peak_validation/lexicographic_peak_validation.json).
For each gap with at least one interior composite (`gap >= 4`), the revalidation code computed `best_n_z`, `best_d_z`, `best_n_lex`, and `best_d_lex`. A counterexample is any gap where either `best_n` or `best_d` differs between the raw-`Z` argmax and the leftmost minimizer.
Sampled windows used two deterministic placement families: evenly spaced starts from `build_even_window_starts`, and fixed-seed starts from `build_seeded_window_starts` with seeds `20260331` and `20260401`. The sampled window size was `2,000,000` and the window count was `4` per regime.
Experiment A used one new exact full range up to `20,000,000`. Experiment B used sampled scales `10^8`, `10^9`, `10^10`, `10^11`, and `10^12`. Experiment C reused the `10^9` even-window regime to measure selected integer enrichment. Experiment D probed three score factors on a smaller surface: baseline `log(n)`, `log(n + 1)`, and `log(n) + 0.001 * n^(-1/2)`.

## Results

### Experiment A: New Exact Range

| limit | gap_count | counterexample_count | match_rate | max_gap | min_log_score_margin | runtime_s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 20,000,000 | 1,163,198 | 0 | 1.000000 | 180 | 5.000119429610095e-08 | 24.86 |

### Experiment B: New Sampled Multi-Seed Windows

| scale | window_mode | seed | window_size | window_count | gap_count | counterexample_count | match_rate | max_gap | min_log_score_margin | runtime_s |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 100,000,000 | even-window |  | 2,000,000 | 4 | 444,133 | 0 | 1.000000 | 176 | 1.000001503825843e-08 | 10.77 |
| 100,000,000 | seeded-window | 20260331 | 2,000,000 | 4 | 415,991 | 0 | 1.000000 | 182 | 1.072191579964965e-08 | 10.91 |
| 100,000,000 | seeded-window | 20260401 | 2,000,000 | 4 | 412,274 | 0 | 1.000000 | 180 | 1.07796402915028e-08 | 10.99 |
| 1,000,000,000 | even-window |  | 2,000,000 | 4 | 411,157 | 0 | 1.000000 | 192 | 1.000000082740371e-09 | 11.27 |
| 1,000,000,000 | seeded-window | 20260331 | 2,000,000 | 4 | 376,941 | 0 | 1.000000 | 236 | 1.073612310165117e-09 | 12.15 |
| 1,000,000,000 | seeded-window | 20260401 | 2,000,000 | 4 | 368,768 | 0 | 1.000000 | 212 | 1.079506262158247e-09 | 12.30 |
| 10,000,000,000 | even-window |  | 2,000,000 | 4 | 384,721 | 0 | 1.000000 | 288 | 9.99982319171977e-11 | 12.33 |
| 10,000,000,000 | seeded-window | 20260331 | 2,000,000 | 4 | 331,375 | 0 | 1.000000 | 236 | 1.073736655143875e-10 | 13.97 |
| 10,000,000,000 | seeded-window | 20260401 | 2,000,000 | 4 | 341,830 | 0 | 1.000000 | 236 | 1.292832507715502e-10 | 13.30 |
| 100,000,000,000 | even-window |  | 2,000,000 | 4 | 362,773 | 0 | 1.000000 | 268 | 9.99733629214461e-12 | 13.29 |
| 100,000,000,000 | seeded-window | 20260331 | 2,000,000 | 4 | 303,102 | 0 | 1.000000 | 272 | 1.073630073733511e-11 | 15.03 |
| 100,000,000,000 | seeded-window | 20260401 | 2,000,000 | 4 | 311,023 | 0 | 1.000000 | 254 | 1.292832507715502e-11 | 14.60 |
| 1,000,000,000,000 | even-window |  | 2,000,000 | 4 | 344,454 | 0 | 1.000000 | 306 | 9.983125437429408e-13 | 14.28 |
| 1,000,000,000,000 | seeded-window | 20260331 | 2,000,000 | 4 | 278,200 | 0 | 1.000000 | 288 | 1.072919530997751e-12 | 16.36 |
| 1,000,000,000,000 | seeded-window | 20260401 | 2,000,000 | 4 | 285,778 | 0 | 1.000000 | 356 | 1.289635065404582e-12 | 15.99 |

### Experiment C: `d(n)=4` Enrichment and Left-Edge Dominance

| scale | regime | gap_count | observed_d4_share | baseline_d4_share | d4_enrichment | left_share | right_share | center_share | observed_edge2_share | baseline_edge2_share | edge2_enrichment |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1,000,000,000 | even-window | 411,157 | 0.824648 | 0.180219 | 4.575815 | 0.762283 | 0.161053 | 0.076664 | 0.368667 | 0.104817 | 3.517240 |

### Experiment D: Alternative Score Factors

| score_function_name | range_description | gap_count | counterexample_count | match_rate | max_gap | min_log_score_margin | runtime_s |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| log | exact to 1,000,000 | 70,327 | 0 | 1.000000 | 114 | 1.000062503919708e-06 | 1.01 |
| log | 4 even windows of width 2,000,000 at scale 1,000,000,000 | 411,157 | 0 | 1.000000 | 192 | 1.000000082740371e-09 | 11.19 |
| log_plus_one | exact to 1,000,000 | 70,327 | 0 | 1.000000 | 114 | 1.000061503830807e-06 | 1.01 |
| log_plus_one | 4 even windows of width 2,000,000 at scale 1,000,000,000 | 411,157 | 0 | 1.000000 | 192 | 1.000000082740371e-09 | 11.13 |
| log_plus_inv_sqrt_eps_0.001 | exact to 1,000,000 | 70,327 | 0 | 1.000000 | 114 | 1.000062004763436e-06 | 1.02 |
| log_plus_inv_sqrt_eps_0.001 | 4 even windows of width 2,000,000 at scale 1,000,000,000 | 411,157 | 0 | 1.000000 | 192 | 1.000000082740371e-09 | 11.26 |

## Discussion

No counterexamples were found in any new experiment. The raw-`Z` argmax and the leftmost minimizer agreed on every tested gap.
The new exact run extended the committed exact surface from `10^7` to `2 * 10^7`, covering 1,163,198 interior prime gaps with zero disagreements.
The sampled multi-seed runs also stayed at match rate `1.0` across every tested scale and seed. Changing window placement changed the sampled gap counts and local maximum gaps, but it did not produce a single disagreement.
On the `10^9` enrichment probe, selected integers were `d(n)=4` in 82.465% of tested gaps versus a baseline interior `d(n)=4` share of 18.022%. Selected integers landed in the left half in 76.228% of gaps and at edge-distance `2` in 36.867% of gaps, with edge-distance `2` enriched by a factor of 3.517.
The alternative-score probe also stayed at match rate `1.0` on the tested smaller surfaces, which supports the prediction that the divisor-order term dominates modest smooth perturbations of the logarithmic factor.
The prior committed surface already reported zero counterexamples on scales through `10^18`, with prior gap counts `10^6`: 70,327, `10^7`: 605,597, `10^8`: 444,133, `10^9`: 411,157, `10^10`: 384,721, `10^11`: 362,773, `10^12`: 344,454, `10^13`: 328,342, `10^14`: 315,617, `10^15`: 303,475, `10^16`: 293,408, `10^17`: 283,989, `10^18`: 275,466. This revalidation did not attempt a larger exact full scan than `2 * 10^7`, and it did not exhaustively resample every scale above `10^12`.
The prior surface already reached floating-point margin collapse to `0.0` at scales `10^15`, `10^16`, `10^17`, `10^18`. Those zero margins are numerical resolution limits in `float64`, not logical counterexamples, because the raw-`Z` argmax and leftmost minimizer still agreed exactly.

## Reproduction Appendix

Created or modified files:
- [`lexicographic_rule_revalidation.py`](../benchmarks/python/gap_ridge/lexicographic_rule_revalidation.py)
- [`test_lexicographic_rule_revalidation.py`](../tests/python/gap_ridge/test_lexicographic_rule_revalidation.py)
- [`edge_run_1e6.json`](./edge_run_1e6.json)
- [`lexicographic_rule_experiment_a.json`](./lexicographic_rule_experiment_a.json)
- [`lexicographic_rule_experiment_b.json`](./lexicographic_rule_experiment_b.json)
- [`lexicographic_rule_experiment_b.csv`](./lexicographic_rule_experiment_b.csv)
- [`lexicographic_rule_experiment_c.json`](./lexicographic_rule_experiment_c.json)
- [`lexicographic_rule_experiment_d.json`](./lexicographic_rule_experiment_d.json)
- [`lexicographic_rule_revalidation_summary.json`](./lexicographic_rule_revalidation_summary.json)

Commands:
- `python3 benchmarks/python/gap_ridge/lexicographic_rule_revalidation.py`
- `pytest tests/python/gap_ridge/test_lexicographic_rule_revalidation.py`

Environment:
- Python `3.x` via `python3`
- Packages: `numpy` and the local project modules under `src/python`

Observed runtimes on this machine:
- Experiment A exact `2e7`: about 24.86 s
- Experiment B sampled total: about 197.52 s across 15 regimes
- Experiment D alternative scores total: about 36.61 s
