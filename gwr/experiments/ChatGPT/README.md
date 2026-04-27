Done — I reproduced the baseline workflow, added the explicit lexicographic counterexample check, ran the new surfaces, and wrote the report plus data artifacts.

I first audited the uploaded code and notes. `runs.py` defines `GapEdgeRunSummary`, identifies primes by `d(n) == 2`, enumerates gaps by zipping consecutive primes in the analyzed interval, and scores interiors with `(1 - d(n)/2) * log(n)` before selecting the selected integer with `np.argmax`.  The rule note states that validation means zero counterexamples on the tested surface and ties the phenomenon to `d(n)=4` dominance, left-edge dominance, and frequent edge-distance-2 peaks.  The prior JSON records 13 earlier regimes from exact `10^6` and `10^7` through sampled `10^18`, all with `match_rate = 1.0` and zero counterexamples across 4,423,459 tested gaps.

One practical fix was needed: the uploaded `runs.py` imports a missing helper module, so I recreated a compatible `z_band_prime_composite_field.divisor_counts_segment` implementation and left the `runs.py` math unchanged.

Highlights from the new runs:

* Exact to `5,000,000`: `316,048` eligible gaps, `0` counterexamples, `match_rate = 1.0`, `max_gap = 154`.
* New sampled surfaces on `10^8` through `10^12`, with 15 regime summaries total (even windows plus two seeded random placements): every regime had `0` counterexamples and `match_rate = 1.0`.
* Experiment C on the `10^9` mixed-window union: observed `d=4` selected-integer share `0.823936` versus baseline `0.152624` (`5.441864x` enrichment), `left_share = 0.765648`, `right_share = 0.161702`, `edge2_enrichment = 1.991244`.
* Experiment D: `log(n+1)` and `log(n) + n^(-1/2)` also produced zero counterexamples on the tested subset.

Key artifacts:

* [Markdown report](sandbox:/mnt/data/output/lexicographic_rule_revalidation_report.md)
* [Combined results JSON](sandbox:/mnt/data/output/lexicographic_rule_revalidation_results.json)
* [Experiment B summary CSV](sandbox:/mnt/data/output/experiment_b_windowed_validation.csv)
* [Experiment B per-window CSV](sandbox:/mnt/data/output/experiment_b_windowed_intervals.csv)
* [Experiment C stats CSV](sandbox:/mnt/data/output/experiment_c_enrichment_stats.csv)
* [Experiment D alt-scoring CSV](sandbox:/mnt/data/output/experiment_d_alt_scoring.csv)
* [Baseline 1e6 reproduction JSON](sandbox:/mnt/data/output/edge_run_1e6.json)
* [Exact 5e6 validation JSON](sandbox:/mnt/data/output/experiment_a_exact_5e6.json)
* [Runner script](sandbox:/mnt/data/lexi_validation_runs.py)
* [Compatible divisor-count helper](sandbox:/mnt/data/z_band_prime_composite_field.py)

The bottom line stayed very clean: on every new surface I tested, the raw-Z argmax still matched the leftmost minimizer exactly.
