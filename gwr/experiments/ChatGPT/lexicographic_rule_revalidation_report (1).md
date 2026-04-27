# Lexicographic Winner-Take-All Peak Rule: Revalidation Report

## Overview

This report reproduces the uploaded raw-Z gap-ridge workflow and extends the explicit lexicographic-selected integer check onto new exact and sampled surfaces. The rule under test is simple: inside each eligible prime gap, choose the interior integer with the smallest divisor count `d(n)`, then break ties by taking the leftmost carrier. The claim is that this leftmost minimizer is exactly the same integer selected by the raw-Z argmax with score `(1 - d(n)/2) * log(n)` on every tested gap. Sources from the workspace are cited below as [A1], [A2], and [A3].

## Phase 1: Audit of the uploaded artifacts

| Artifact | What it contributes |
| --- | --- |
| runs.py | Defines GapEdgeRunSummary, exact/window helpers, and _analyze_interval with score = (1 - d/2) * log(n). |
| lexicographic_winner_take_all_peak_rule.md | States the exact rule, the zero-counterexample decision criterion, and the qualitative claims about d=4, left-edge bias, and edge-distance-2 enrichment. |
| lexicographic_peak_validation.json | Records 13 prior regimes, validation_status=validated_on_tested_surface, and 4,423,459 tested gaps in total. |

From `runs.py` [A1], `GapEdgeRunSummary` contains the following fields: `scale, gap_count, observed_edge2_share, baseline_edge2_share, edge2_enrichment, observed_d4_share, baseline_d4_share, d4_enrichment, left_share, right_share, center_share, window_mode, window_size, sampled_gap_count, approximate_gap_count, seed`.

The uploaded `_analyze_interval` implementation [A1] does the following, gap by gap:

1. compute divisor counts on an exact integer segment,
2. label primes as those entries with divisor count `2`,
3. enumerate prime gaps by zipping consecutive primes found in that segment,
4. skip gaps shorter than `4`,
5. score the interior composites by `(1 - d/2) * log(n)`,
6. choose the best carrier with `np.argmax`, and
7. summarize edge-distance-2, `d(n)=4`, and left/right/center selected-integer shares.

The natural-language note [A2] states the exact selection rule, the zero-counterexample validation criterion, and the qualitative explanation for `d(n)=4` dominance, left-edge dominance, and frequent edge-distance-2 peaks. The prior JSON artifact [A3] records the already-tested surface:

- exact 1,000,000: 70,327 / 70,327, max gap 114
- exact 10,000,000: 605,597 / 605,597, max gap 154
- sampled 100,000,000: 444,133 / 444,133, max gap 176
- sampled 1,000,000,000: 411,157 / 411,157, max gap 192
- sampled 10,000,000,000: 384,721 / 384,721, max gap 288
- sampled 100,000,000,000: 362,773 / 362,773, max gap 268
- sampled 1,000,000,000,000: 344,454 / 344,454, max gap 306
- sampled 10,000,000,000,000: 328,342 / 328,342, max gap 300
- sampled 100,000,000,000,000: 315,617 / 315,617, max gap 410
- sampled 1,000,000,000,000,000: 303,475 / 303,475, max gap 436
- sampled 10,000,000,000,000,000: 293,408 / 293,408, max gap 480
- sampled 100,000,000,000,000,000: 283,989 / 283,989, max gap 448
- sampled 1,000,000,000,000,000,000: 275,466 / 275,466, max gap 448

That prior surface totals 4,423,459 prime gaps with validation status `validated_on_tested_surface` and decision rule:

> validated on the tested surface if and only if every tested regime contains zero counterexample gaps where the exact raw-Z peak differs from the leftmost minimizer: smallest d(n), then leftmost

## Methods

I recreated the missing `z_band_prime_composite_field.divisor_counts_segment` helper expected by `runs.py` using a segmented factor-counting pass over `[lo, hi)`. That made it possible to import the uploaded `runs.py` unchanged and call `run_exact_limit(1_000_000)` end-to-end.

For the explicit lexicographic comparison layer, I wrote `validate_lexicographic_rule_on_interval(...)`. On each eligible gap it computes:

- `best_n_z`, `best_d_z`: the selected integer selected by the raw-Z argmax,
- `best_n_lex`, `best_d_lex`: the selected integer selected by “minimum divisor count, then leftmost”,
- `is_counterexample`: whether those two selected integers disagree.

The same routine also records `max_gap`, the smallest observed score margin between the top two interior scores on the tested surface, and the same enrichment statistics used in `runs.py`.

Window selection for Experiment B reused the uploaded helper policy from `runs.py` [A1]: deterministic even windows via `build_even_window_starts`, and fixed-seed random windows via `build_seeded_window_starts`. The exact parameter choices were:

- Experiment A: exact limit 5,000,000
- Experiment B: scales 100,000,000, 1,000,000,000, 10,000,000,000, 100,000,000,000, 1,000,000,000,000, window size 2,000,000, window count 4, random seeds 20260331, 20260401
- Experiment C: union of all unique sampled windows at scale `10^9` generated during Experiment B
- Experiment D: score functions `log(n)`, `log(n+1)`, and `log(n) + n^(-1/2)` on the exact `10^6` surface and the 4 even windows at scale `10^9`

## Reproduction check

The direct `runs.py` baseline run up to `10^6` completed successfully and produced a nontrivial summary with `gap_count=70,327`, `observed_edge2_share=0.436006`, `observed_d4_share=0.829027`, `left_share=0.745574`, and `right_share=0.160180`. That confirms the uploaded helper can be executed end-to-end on the recreated environment.

## Results

### Experiment A: new exact range

| limit | gap_count | counterexample_count | match_rate | max_gap | min_score_margin |
| --- | --- | --- | --- | --- | --- |
| 5,000,000 | 316,048 | 0 | 1.000000 | 154 | 0.000000200004 |

### Experiment B: new sampled higher scales and window placements

| scale | window_mode | seed | window_size | window_count | gap_count | counterexample_count | match_rate | max_gap | min_score_margin |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 100,000,000 | even-window | — | 2,000,000 | 4 | 444,133 | 0 | 1.000000 | 176 | 0.000000010000 |
| 100,000,000 | seeded-window | 20,260,331 | 2,000,000 | 4 | 415,991 | 0 | 1.000000 | 182 | 0.000000010722 |
| 100,000,000 | seeded-window | 20,260,401 | 2,000,000 | 4 | 412,274 | 0 | 1.000000 | 180 | 0.000000010780 |
| 1,000,000,000 | even-window | — | 2,000,000 | 4 | 411,157 | 0 | 1.000000 | 192 | 0.000000001000 |
| 1,000,000,000 | seeded-window | 20,260,331 | 2,000,000 | 4 | 376,941 | 0 | 1.000000 | 236 | 0.000000001074 |
| 1,000,000,000 | seeded-window | 20,260,401 | 2,000,000 | 4 | 368,768 | 0 | 1.000000 | 212 | 0.000000001080 |
| 10,000,000,000 | even-window | — | 2,000,000 | 4 | 384,721 | 0 | 1.000000 | 288 | 0.000000000100 |
| 10,000,000,000 | seeded-window | 20,260,331 | 2,000,000 | 4 | 331,375 | 0 | 1.000000 | 236 | 0.000000000107 |
| 10,000,000,000 | seeded-window | 20,260,401 | 2,000,000 | 4 | 341,830 | 0 | 1.000000 | 236 | 0.000000000129 |
| 100,000,000,000 | even-window | — | 2,000,000 | 4 | 362,773 | 0 | 1.000000 | 268 | 0.000000000010 |
| 100,000,000,000 | seeded-window | 20,260,331 | 2,000,000 | 4 | 303,102 | 0 | 1.000000 | 272 | 0.000000000011 |
| 100,000,000,000 | seeded-window | 20,260,401 | 2,000,000 | 4 | 311,023 | 0 | 1.000000 | 254 | 0.000000000013 |
| 1,000,000,000,000 | even-window | — | 2,000,000 | 4 | 344,454 | 0 | 1.000000 | 306 | 0.000000000001 |
| 1,000,000,000,000 | seeded-window | 20,260,331 | 2,000,000 | 4 | 278,200 | 0 | 1.000000 | 288 | 0.000000000001 |
| 1,000,000,000,000 | seeded-window | 20,260,401 | 2,000,000 | 4 | 285,778 | 0 | 1.000000 | 356 | 0.000000000001 |

### Experiment C: `d(n)=4` enrichment, left-edge dominance, and edge-distance-2 enrichment

| scale | gap_count | observed_d4_share | baseline_d4_share | d4_enrichment | left_share | right_share | edge2_enrichment |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1,000,000,000 | 1,156,866 | 0.823936 | 0.152624 | 5.441864 | 0.765648 | 0.161702 | 1.991244 |

On the `10^9` mixed-window union used for Experiment C, the selected integer divisor-count profile was dominated by `d=4`. The top observed selected divisor-count classes were: d=4: 953,183, d=8: 129,830, d=6: 36,049, d=16: 17,493, d=12: 15,269.

### Experiment D: robustness to small score perturbations

| score_function_name | range_description | gap_count | counterexample_count | match_rate | max_gap | min_score_margin |
| --- | --- | --- | --- | --- | --- | --- |
| log(n) | exact up to 1,000,000 | 70,327 | 0 | 1.000000 | 114 | 0.000001000063 |
| log(n) | 4 even windows at scale 10^9 (window size 2,000,000) | 411,157 | 0 | 1.000000 | 192 | 0.000000001000 |
| log(n+1) | exact up to 1,000,000 | 70,327 | 0 | 1.000000 | 114 | 0.000001000062 |
| log(n+1) | 4 even windows at scale 10^9 (window size 2,000,000) | 411,157 | 0 | 1.000000 | 192 | 0.000000001000 |
| log(n) + n^(-1/2) | exact up to 1,000,000 | 70,327 | 0 | 1.000000 | 114 | 0.000000999562 |
| log(n) + n^(-1/2) | 4 even windows at scale 10^9 (window size 2,000,000) | 411,157 | 0 | 1.000000 | 192 | 0.000000001000 |

## Discussion

No true counterexamples were found in any experiment: **true**. In every new exact and sampled regime, the raw-Z argmax matched the leftmost minimizer exactly.

The main predictions were confirmed on the new tested surfaces:

- zero-counterexample continuation held in the new exact run and in every new sampled window regime,
- `d(n)=4` selected integers remained strongly enriched relative to the interior baseline,
- selected integers remained strongly left-biased relative to right-side selected integers,
- edge-distance-2 selected integers stayed enriched relative to their positional baseline,
- modest smooth perturbations of `log(n)` did not introduce any counterexamples on the tested subset.

A numerical caution remains the same as in the uploaded prior JSON [A3]: score margins shrink with scale, so very small reported margins should be read as float64 resolution limits, not as logical evidence against the rule. In the present experiments the smallest margins on the new `10^8` through `10^12` sampled surfaces stayed positive, but they were already down near machine-resolution-sensitive territory by the top end of the prior surface in [A3].

The main limitations are finite coverage and sampling density. The new exact extension reaches `5 * 10^6`, not full exact coverage beyond that. The higher-scale work samples windows rather than exhaustively scanning every gap up to `10^12`. That said, the added surfaces test both deterministic and different random placements, so they do meaningfully probe whether the zero-counterexample result depends on one particular window choice.

## Reproduction appendix

### Files created or added

- `z_band_prime_composite_field.py` — compatible replacement for the missing divisor-count segment helper
- `lexi_validation_runs.py` — orchestration and experiment runner
- `output/edge_run_1e6.json`
- `output/experiment_a_exact_5e6.json`
- `output/experiment_b_windowed_validation.json`
- `output/experiment_b_windowed_validation.csv`
- `output/experiment_b_windowed_intervals.csv`
- `output/experiment_c_enrichment_stats.json`
- `output/experiment_c_enrichment_stats.csv`
- `output/experiment_d_alt_scoring.json`
- `output/experiment_d_alt_scoring.csv`
- `output/lexicographic_rule_revalidation_results.json`
- `output/lexicographic_rule_revalidation_report.md`

### How to run

```bash
cd /mnt/data
python lexi_validation_runs.py
```

### Environment and dependencies

- Python: 3.13.5
- NumPy: 2.3.5
- Standard library modules only beyond NumPy

### Approximate runtimes observed in this run

- baseline `run_exact_limit(1_000_000)`: 0.59 s
- Experiment A exact `5,000,000`: 6.64 s
- Experiment B total sampled sweep: 130.33 s
- Experiment C aggregation step: 24.97 s across its constituent windows
- Experiment D total: 29.97 s

## Source artifact citations

- [A1] `runs.py`
- [A2] `lexicographic_winner_take_all_peak_rule.md`
- [A3] `lexicographic_peak_validation.json`
