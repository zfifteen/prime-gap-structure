# DNI Near-Endpoint Raw-Z Peak

Prime gaps have interior composite points.

That is the observable setting for this concern. Between one prime and the next, every interior integer is composite. Once the **Divisor Normalization Identity** (DNI) $Z(n) = n^{1 - d(n)/2}$ is evaluated exactly on those interiors, the question is no longer whether composites lie inside the gap. The question is where the strongest raw composite $Z$ value tends to sit inside that gap.

The current repository result is that the strongest raw composite $Z$ value is not usually centered. It forms a near-edge ridge.

Up to $10^6$ on the natural number line:

- the gap-local raw-$Z$ maximum lands at edge distance $2$ in $43.6006\%$ of tested gaps versus an exact within-gap baseline of $22.1859\%$,
- the resulting edge-distance enrichment is $1.965\times$,
- the gap-local raw-$Z$ maximum is carried by a $d(n) = 4$ composite in $82.9027\%$ of tested gaps versus an exact within-gap baseline of $20.1401\%$,
- the resulting selected-divisor-count enrichment is $4.116\times$.

This is the near-endpoint raw-Z peak concern of the DNI. It is the study of where the strongest exact raw composite $Z$ value appears inside prime gaps and what kind of composite carries that peak.

## What Is Being Measured

The object under study is the exact raw DNI score function itself,

$$
Z(n) = n^{1 - d(n)/2},
$$

restricted to composite interiors of prime gaps.

For each consecutive prime gap $p < q$ with interior composites, the study evaluates the raw composite $Z$ value at every interior point and selects the single interior composite with the largest value. That point is the gap-local peak.

Two measurements then matter:

- how far that peak sits from the nearest edge of the gap,
- which divisor count carries that peak.

The edge-distance question tells us whether the score rises toward the endpoint or toward the midpoint. The selected-divisor-count question tells us which divisor class most often supports the peak. In the current exact runs, the answers are near-edge position and $d(n) = 4$ selected-divisor-count dominance.

## Why This Is A Separate Concern

The near-endpoint raw-Z peak result is not the same concern as the production prefilter.

The prefilter concern asks how the fixed-point locus is used operationally to remove composite work before Miller-Rabin. The near-endpoint raw-Z peak concern asks what structure the exact raw composite score values show inside prime gaps once exact divisor count is available.

It is also narrower than the full exact raw composite score-function concern. The broader concern studies the exact raw composite $Z$ score values themselves. The near-endpoint raw-Z peak concern studies one specific structure within that score function: the location and integer attaining the within-gap maximum.

## Exact Method

The method in this repository is deterministic and exact.

1. Fix one natural-number regime.
2. Compute exact divisor count $d(n)$ on that interval.
3. Identify every consecutive prime gap $p < q$ with $q - p \ge 4$.
4. Restrict attention to the composite interior points $p < n < q$.
5. Evaluate the raw DNI score function $Z(n) = n^{1 - d(n)/2}$ on those interiors.
6. Within each gap, select the single composite with the largest raw $Z$.
7. Compare the observed peak position and observed peak integer against exact within-gap baselines induced by the same interior.

The implementation compares peak candidates through the monotone identity

$$
\ln Z(n) = \left(1 - \frac{d(n)}{2}\right)\ln n
$$

only to preserve the ordering of the exact same raw score function without floating-point underflow. The quantity being studied remains raw $Z$.

In the normative Python helpers for this concern, exact divisor counts over intervals are supplied by the exact composite-field path, and the near-endpoint raw-Z peak summaries are produced by [the gap-ridge run helpers](../src/python/z_band_prime_gap_ridge/runs.py).

## Exact $10^6$ Result

The first full exact result in the repository is the natural-number run up to $10^6$.

$N = 1{,}000{,}000$

Prime gaps tested: $70{,}327$

| Metric | Observed | Exact baseline | Enrichment |
|---|---:|---:|---:|
| Gap-local max at edge distance $2$ | $43.6006\%$ | $22.1859\%$ | $1.965\times$ |
| Mean edge distance of gap-local max | $2.9283$ | $3.7792$ | $1.291\times$ closer to edge |
| Gap-local max within edge distance $\le 2$ | $58.8025\%$ | $48.2313\%$ | $1.219\times$ |
| Gap-local max carried by $d(n) = 4$ | $82.9027\%$ | $20.1401\%$ | $4.116\times$ |

Additional structure from the same run sharpens the picture:

- left edge wins in $74.5574\%$ of gaps,
- right edge wins in $16.0180\%$ of gaps,
- exact center wins in $9.4245\%$ of gaps.

The strongest supported reading of this table is that the raw composite score values does not build a midpoint ridge. It builds a near-edge low-divisor ridge, and that ridge is carried predominantly by $d(n) = 4$ composites.

## Lexicographic Peak Rule

The current repository now promotes the lexicographic peak rule to the proved
Gap Winner Rule theorem on the repo's current proof surface.

Across the tested regimes, the exact raw-$Z$ peak inside each prime gap matches
the leftmost minimizer:

1. choose the smallest interior divisor count $d(n)$,
2. if several interior composites share that minimum divisor count, choose the
   leftmost one.

This was first validated directly on the committed execution surface by a
counterexample search over exact $10^6$, exact $10^7$, and sampled larger-scale
regimes through $10^{18}$, with zero counterexamples on that surface. The
current closed proof surface combines that finite base with the elementary
later-side dominance theorem, the local admissibility route, and the residual-
class closure artifacts.

So the current best explanation of the measured ridge is no longer only
empirical: under the closed repo proof surface, the observed near-edge
low-divisor ridge is the gap-local expression of GWR.

## Gap-Size Structure

The edge effect is present across gap sizes, but its expression changes by regime.

In the exact $10^6$ run:

- gaps $4\text{-}10$ show edge-distance-$2$ share $51.1269\%$ and $d(n) = 4$ selected-divisor-count share $66.1648\%$,
- gaps $12\text{-}20$ show edge-distance-$2$ share $38.9273\%$ and $d(n) = 4$ selected-divisor-count share $98.5198\%$,
- gaps $22+$ show edge-distance-$2$ share $32.2688\%$ and $d(n) = 4$ selected-divisor-count share $99.4616\%$.

The near-edge location softens as gaps widen, but the low-divisor integer pattern strengthens. That is why the ridge is best described by two linked properties rather than by one alone:

- peak mass sits unusually close to the edge,
- the peak integer is unusually often a $d(n) = 4$ composite.

## Regime Confirmation

The repository also includes broader regime confirmation through larger-scale windowed runs.

Across the current committed execution surface summarized in the figure note:

- edge-distance-$2$ enrichment stays near $2\times$ from the exact $10^6$ run through sampled $10^{18}$ windows,
- the $d(n) = 4$ selected-divisor-count enrichment strengthens with scale, rising from $4.116\times$ at $10^6$ to about $7.56\times$ in even-window $10^{18}$ runs and about $9.19\times$ in fixed-seed $10^{18}$ runs,
- the left edge remains the dominant side of the ridge throughout the tested regimes.

This does not widen the claim beyond the current committed execution surface.
It says that the near-edge ridge pattern seen in the exact $10^6$ run
continues to appear in the larger sampled windows already committed to the
figure note.

## Reproduction Surface

The focused result note for the exact $10^6$ run is [docs/gap_ridge/raw_composite_z_gap_edge.md](./gap_ridge/raw_composite_z_gap_edge.md).

The figure note for the broader rendered regime surface is [docs/gap_ridge/raw_composite_z_gap_edge_figures.md](./gap_ridge/raw_composite_z_gap_edge_figures.md).

The session finding note for the selection rule is [docs/findings/lexicographic_winner_take_all_peak_rule.md](./findings/lexicographic_winner_take_all_peak_rule.md).

To reproduce the exact $10^6$ gap-edge study, run:

```bash
python3 benchmarks/python/gap_ridge/raw_z_gap_edge_study.py
```

To reproduce the broader rendered regime surface, run:

```bash
python3 benchmarks/python/gap_ridge/raw_z_gap_edge_run_all.py \
  > benchmarks/output/python/gap_ridge/raw_z_gap_edge/raw_z_gap_edge_run_all.json

python3 benchmarks/python/gap_ridge/raw_z_gap_edge_plots.py
```

Those artifacts keep this concern auditable from exact interval computation, to gap-local peak selection, to measured enrichment tables and figures.
