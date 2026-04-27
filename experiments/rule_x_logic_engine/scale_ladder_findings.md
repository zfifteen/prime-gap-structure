# Rule X Scale Ladder Findings

## Executive Summary

The Rule X consistency-collapse algorithm remained audit-clean through
`10^7` on the tested scale ladder.

The highest run was:

```text
input primes: 11..10000000
candidate_bound: 256
witness_bound: 3163
input primes tested: 664575
candidate hypotheses: 45108041
exact unique matches: 140984
true next prime rejections: 0
```

With a fixed witness horizon `B = 127`, coverage plateaus after the
semiprime-shadow landmark threshold `131^2 = 17161`. That is expected: above
the threshold, no-witness candidates are held open instead of promoted to
resolved candidates.

With a scale-matched witness horizon just above `sqrt(max_anchor +
candidate_bound)`, the algorithm resolves about `21%` to `23%` of input primes while
preserving zero true-next-prime rejections on every tested surface.

## Fixed Witness Horizon

These runs keep `witness_bound = 127` and `candidate_bound = 128`.

| max input prime | input primes | exact unique matches | match rate | true rejected |
|---:|---:|---:|---:|---:|
| `100000` | `9588` | `488` | `5.089695%` | `0` |
| `200000` | `17980` | `488` | `2.714127%` | `0` |
| `500000` | `41534` | `488` | `1.174941%` | `0` |
| `1000000` | `78494` | `488` | `0.621704%` | `0` |

The fixed-horizon ladder validates the semiprime-shadow landmark hold. It does
not reject the true next prime, but it stops gaining coverage once unresolved
landmarks dominate the candidate surface.

## Scale-Matched Witness Horizon

These runs choose a witness bound large enough that the semiprime-shadow
landmark threshold lies beyond the tested coordinate range.

| max input prime | candidate bound | witness bound | input primes | exact unique matches | match rate | true rejected |
|---:|---:|---:|---:|---:|---:|---:|
| `200000` | `128` | `449` | `17980` | `4121` | `22.919911%` | `0` |
| `500000` | `128` | `709` | `41534` | `9279` | `22.340733%` | `0` |
| `1000000` | `128` | `1009` | `78494` | `17249` | `21.974928%` | `0` |
| `1000000` | `256` | `1009` | `78494` | `17247` | `21.972380%` | `0` |
| `2000000` | `256` | `1423` | `148929` | `32446` | `21.786220%` | `0` |
| `5000000` | `256` | `2239` | `348509` | `74934` | `21.501310%` | `0` |
| `10000000` | `256` | `3163` | `664575` | `140984` | `21.214159%` | `0` |

The scale-matched ladder shows the algorithm is not a tiny-range artifact.
It preserves the hard safety condition:

```text
true_boundary_rejected_count = 0
```

through `664575` input primes and `45108041` candidate hypotheses.

## Interpretation

The model has two distinct regimes.

With a fixed witness horizon, the semiprime-shadow landmark hold correctly
turns no-witness two-factor risk into unresolved state. Safety is preserved,
but coverage plateaus.

With a scale-matched witness horizon, candidate composites are cleared far
enough for integer lock and lower-divisor threat ceilings to operate across
the whole tested domain. Coverage stabilizes near one fifth of input primes while
remaining audit-clean.

The next useful experiment is not another broad search. It is a bounded
witness-horizon law that keeps the fixed-horizon safety of semiprime-shadow
landmarks while recovering more of the scale-matched coverage.
