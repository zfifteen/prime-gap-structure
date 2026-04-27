# Label-Free Integer-Lock Experiment Findings

## Executive Summary

The next experiment confirms the selected-integer-lock path is real, but only when the
positive-witness horizon is strong enough to prevent false early survivors.

On prime anchors `11..100000` with candidate offsets up to `128`, the
full-small-scale witness run produced:

```text
label_lock_true_boundary_rejected_count = 0
label_lock_unique_resolved_match_count = 2231 / 9588
```

That means the label-free logic engine inferred the exact next prime for
`2231` anchors and rejected the true next prime zero times on this surface.

The lower witness horizons expose the obstruction:

| witness bound | true rejected | unique resolved | unique matches |
|---:|---:|---:|---:|
| `97` | `507` | `2584` | `2107` |
| `127` | `331` | `2457` | `2144` |
| `317` | `0` | `2231` | `2231` |

The unsafe rows are not failures of selected-integer-lock pressure itself. They are
premature locks caused by false early survivors whose composite witness lies
above the current witness bound.

## Domain

```text
prime anchors: 11..100000
candidate bound: 128
witness bound: 317
anchors tested: 9588
candidate hypotheses: 324809
```

The bound `317` is above `sqrt(100128)`, so every composite candidate in this
finite run has a positive factor witness inside the experiment horizon.

## Main Result

| Layer | Rejections | Unique anchors | True endpoint rejected |
|---|---:|---:|---:|
| GWR/NLSC only | `0` | `0` | `0` |
| Naive first-integer lock | `297753` | `4162` | `7297` |
| Oracle survivor lock | `90607` | `1429` | `0` |
| Label-free full-witness lock | `241248` | `2231` | `0` |

The label-free full-witness lock gives the strongest useful result in this
experiment: more exact unique inferences than the oracle survivor-lock contrast,
with the same zero true-next-prime rejection count.

## Interpretation

The logic engine now has a working finite consistency-collapse rule:

```text
reject candidate composites by positive witness;
hold candidates with unresolved interior opens;
lock the selected integer only after a resolved survivor exists;
reject later candidates beyond the first certified lower-divisor threat.
```

The rule is not yet a production theorem because the finite run used a witness
horizon large enough to certify every composite on this small surface. But it
does identify the missing condition precisely:

```text
the lock is safe when no false early survivor can masquerade as a endpoint.
```

The next target is a bounded PGS-visible witness horizon that preserves the
`0` true-rejection result without requiring full trial-division coverage.

## Obstruction Found

At `witness_bound = 97`, the first failures begin when early composite
candidates lack a small enough positive witness. Example:

```text
anchor p = 10607
actual offset = 6
false resolved survivor = 2
lock selected-integer offset = 1
threat offset = 3
```

The false offset `2` survives because its composite factor is outside the
`97` witness horizon. The engine locks too early, then the lower-divisor threat
incorrectly rejects the true next prime.

Increasing the witness horizon to `317` removes this class of premature lock
on the tested surface.
