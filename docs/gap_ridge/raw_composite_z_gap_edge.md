# Exact Raw Composite Z Field: Gap-Edge Ridge Study

This note records one exact-field observation on the natural number line up to `10^6`.

The field under study is the **Divisor Normalization Identity** (DNI) $Z(n) = n^{1 - d(n)/2}$ itself, evaluated with exact divisor count and restricted to composite interiors of prime gaps.

## Finding

Inside prime gaps up to `10^6`, the strongest raw composite `Z` value is not usually centered in the gap.

It is pulled toward the gap edge, and it is usually carried by a `d(n) = 4` composite.

More precisely:

- the gap-local raw-`Z` maximum lands at edge distance `2` in `43.6006%` of tested gaps,
- the exact within-gap position baseline for edge distance `2` is `22.1859%`,
- the resulting edge-distance enrichment is `1.965x`,
- the gap-local raw-`Z` maximum is carried by a `d(n) = 4` composite in `82.9027%` of tested gaps,
- the exact within-gap selected-divisor-count baseline for `d(n) = 4` is `20.1401%`,
- the resulting selected-divisor-count enrichment is `4.116x`.

The strongest supported interpretation is that the exact raw composite `Z` field forms a near-edge low-divisor ridge inside prime gaps rather than a midpoint ridge.

On the current tested surface, that ridge can be stated more sharply: the
gap-local raw-`Z` maximum matches the leftmost minimizer obtained by first
minimizing interior divisor count `d(n)` and then taking the leftmost integer
of that minimum.

## Method

The experiment is deterministic and exact.

1. Fix the natural-number ceiling at `10^6`.
2. Compute exact divisor count `d(n)` for every `n <= 10^6`.
3. Identify every consecutive prime gap `p < q` with `q - p >= 4`.
4. For every composite interior point `n` with `p < n < q`, evaluate the raw field `Z(n) = n^{1 - d(n)/2}`.
5. Within each gap, select the single composite with the largest raw `Z`.
6. Compare that observed peak to the exact baseline induced by the same gap interior:
   - position baseline: each interior position counted once,
   - selected-divisor-count baseline: each interior composite counted once when `d(n) = 4`.

The implementation compares raw `Z` values through the monotone identity
$\ln Z(n) = (1 - d(n)/2)\ln n$ only to preserve the ordering of the exact same raw field without floating-point underflow. The quantity being studied remains raw `Z`.

## Result Table

`N = 1,000,000`

Prime gaps tested: `70,327`

| Metric | Observed | Exact baseline | Enrichment |
|---|---:|---:|---:|
| Gap-local max at edge distance `2` | `43.6006%` | `22.1859%` | `1.965x` |
| Mean edge distance of gap-local max | `2.9283` | `3.7792` | `1.291x` closer to edge |
| Gap-local max within edge distance `<= 2` | `58.8025%` | `48.2313%` | `1.219x` |
| Gap-local max carried by `d(n) = 4` | `82.9027%` | `20.1401%` | `4.116x` |

Additional structure from the same run:

- left edge wins in `74.5574%` of gaps,
- right edge wins in `16.0180%` of gaps,
- exact center wins in `9.4245%` of gaps.

Gap-size split:

- gaps `4-10`: edge-distance-`2` share `51.1269%`, `d(n) = 4` share `66.1648%`
- gaps `12-20`: edge-distance-`2` share `38.9273%`, `d(n) = 4` share `98.5198%`
- gaps `22+`: edge-distance-`2` share `32.2688%`, `d(n) = 4` share `99.4616%`

## Ordering Interpretation

The current repository evidence now supports an exact tested ordering law for
the gap-local peak.

On the tested surface, the raw-`Z` selected integer is selected by:

1. smallest interior divisor count,
2. then leftmost position among those minima.

That discrete ordering explains why:

- `d(n) = 4` integers dominate the peak,
- left-edge wins dominate right-edge wins,
- edge-distance `2` appears so often as the selected integer location.

This remains an empirical repository result rather than a proof for every
possible gap, but it is stronger than a descriptive field metaphor alone.

## Reproduction

Run:

```bash
python3 benchmarks/python/gap_ridge/raw_z_gap_edge_study.py
```

The script prints the exact observed quantities and the exact within-gap baselines used in this note.
