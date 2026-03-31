# Exact Raw Composite Z Field: Figure Note

This note collects the rendered figures for the exact raw composite `Z` gap-edge study and states the empirical result directly.

The figures are generated from:

- `benchmarks/output/python/gap_ridge/raw_z_gap_edge/raw_z_gap_edge_run_all.json`
- `benchmarks/python/gap_ridge/raw_z_gap_edge_plots.py`

## Main Result

Across the tested regimes, the exact raw composite field
\[
Z(n) = n^{1 - d(n)/2}
\]
does not place the strongest within-gap composite near the midpoint of a prime gap.

It places that peak on a near-edge ridge, and that ridge is carried predominantly by `d(n) = 4` composites.

The strongest supported statement from the current runs is:

- edge-distance-`2` enrichment stays near `2x` from the exact `10^6` run through sampled `10^10` windows,
- the `d(n) = 4` carrier enrichment strengthens with scale, rising from `4.116x` at `10^6` to about `5.76x` in even-window `10^10` runs and about `5.93x` in fixed-seed `10^10` runs,
- the left edge remains the dominant side of the ridge throughout the tested regimes.

## Regime Confirmation

This figure shows that the edge-distance-`2` enrichment remains stable near `2x`, while the `d(n) = 4` carrier enrichment strengthens as the scale increases.

![Regime enrichment confirmation](../../benchmarks/output/python/gap_ridge/raw_z_gap_edge/regime_enrichment_2d.svg)

## Peak Position by Edge Distance

This figure compares the observed location of the gap-local raw-`Z` maximum against the exact within-gap baseline. The observed peak mass is concentrated much closer to the prime boundaries than baseline predicts.

![Observed versus baseline edge-distance distribution](../../benchmarks/output/python/gap_ridge/raw_z_gap_edge/edge_distance_distribution_2d.svg)

## Carrier Divisor Count

This figure compares the divisor count of the composite carrying the gap-local raw-`Z` maximum against the exact within-gap baseline. The ridge is overwhelmingly carried by `d(n) = 4` composites rather than by the generic within-gap divisor mix.

![Observed versus baseline carrier divisor distribution](../../benchmarks/output/python/gap_ridge/raw_z_gap_edge/carrier_divisor_distribution_2d.svg)

## Representative Gap Slice

This figure shows one exact prime-gap slice from the `10^6` regime. The profile is not midpoint-centered. The local maximum rises close to the boundary at an edge distance of `2`, and the peak carrier is a `d(n) = 4` composite.

![Representative prime-gap raw-Z profile](../../benchmarks/output/python/gap_ridge/raw_z_gap_edge/representative_gap_profile_2d.svg)

## 3D Edge-Distance Enrichment Surface

This figure resolves the same effect over two variables at once: gap size and edge distance. The elevated surface sits on the low edge-distance side rather than over the center.

![Gap-size by edge-distance enrichment surface](../../benchmarks/output/python/gap_ridge/raw_z_gap_edge/gap_size_edge_distance_enrichment_3d.png)

## 3D Carrier Enrichment Surface

This figure resolves the carrier effect over gap size and divisor count. The dominant high surface is the `d(n) = 4` carrier band.

![Gap-size by carrier-divisor enrichment surface](../../benchmarks/output/python/gap_ridge/raw_z_gap_edge/gap_size_carrier_enrichment_3d.png)

## Reproduction

Run:

```bash
python3 benchmarks/python/gap_ridge/raw_z_gap_edge_run_all.py \
  > benchmarks/output/python/gap_ridge/raw_z_gap_edge/raw_z_gap_edge_run_all.json

python3 benchmarks/python/gap_ridge/raw_z_gap_edge_plots.py
```
