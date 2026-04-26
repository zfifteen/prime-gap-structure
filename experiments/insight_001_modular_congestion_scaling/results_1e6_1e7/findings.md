# Executive Summary

The Modular Congestion Scaling prediction is falsified on the finite domain
`[1,000,000, 10,000,000]`.

The run found `4` prime-gap records in the tested domain. The record gap
`4652353 -> 4652507` with gap length `154` did not land inside any predicted
modular interference zone. The nearest prior pressure-record center was
`1507157`, at distance `3,145,196`, exceeding the required `1,000,000` radius.

The miss is not caused by vacuous overcoverage. The merged predicted zone
covered `16.74619813931132%` of the tested coordinate domain, below the
experiment's `25%` maximum coverage threshold.

Verdict:

```text
falsified_record_miss
```

## Domain

```text
X0 = 1,000,000
N  = 10,000,000
```

The pressure field used:

$$H(x)=\lceil\log(x)^2\rceil$$

$$MCS(x)=\frac{k(x)H(x)}{A(x)}$$

where `k(x)` is the number of active prime constraints `ell <= H(x)` and
`A(x)` is the number of integers in `(x, x + H(x)]` coprime to every active
prime constraint.

## Summary Metrics

| Metric | Value |
|---|---:|
| Record gaps tested | `4` |
| Champagne gaps tested | `0` |
| Missed record gaps | `1` |
| Missed champagne gaps | `0` |
| Pressure-record centers | `17` |
| Merged predicted zones | `1` |
| Predicted-zone coverage | `0.1674619813931132` |
| Record median MCS percentile | `50.12783887468457` |
| Phase-blind control hit rate | `1.0` |
| Phase-blind coverage | `0.9859832237796418` |

The phase-blind control hit every tested record only because its zones covered
`98.59832237796418%` of the domain. That control is not a useful search
contraction.

## Record Events

| p | q | gap | MCS percentile | nearest prior center | distance | inside zone |
|---:|---:|---:|---:|---:|---:|---|
| `1349533` | `1349651` | `118` | `39.35242896084122` | `1090513` | `259020` | `true` |
| `1357201` | `1357333` | `132` | `99.07422232508641` | `1090513` | `266688` | `true` |
| `2010733` | `2010881` | `148` | `21.789786467801502` | `1507157` | `503576` | `true` |
| `4652353` | `4652507` | `154` | `60.90324878852791` | `1507157` | `3145196` | `false` |

## Interpretation

The stated prediction required major new gaps to occur within `1,000,000`
integers of a coordinate where local modular saturation reaches a new running
maximum. The record gap beginning at `4652353` violates that condition.

On this finite domain, the proposed modular pressure field does not provide the
claimed record-gap locator. The record endpoints also do not concentrate at
high pressure: their median pressure percentile is approximately `50.13`, not
above the required `90th` percentile.

The champagne-gap branch was not exercised in this domain because no record gap
exceeded the prior normalized excess by `15%`.
