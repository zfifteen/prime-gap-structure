# Gap Winner Rule

## Statement

Inside each prime gap $(p, q)$ with at least one composite interior, assign each
interior integer $n$ the raw-$Z$ score

$$
Z(n) = \left(1 - \frac{d(n)}{2}\right)\ln(n).
$$

The `Gap Winner Rule` (`GWR`) says the raw-$Z$ argmax is exactly the interior
integer selected by this arithmetic order:

1. choose the smallest interior divisor count $d(n)$,
2. among interiors with that minimum, choose the leftmost one.

Equivalently, the raw-$Z$ winner and the lexicographic winner are the same
carrier on every tested gap.

## Legacy Name

This rule was first recorded in this repo under the legacy name
`Lexicographic Winner-Take-All Peak Rule`.

Going forward:

- use `Gap Winner Rule` or `GWR` in new prose,
- retain the legacy name where existing titles, figure labels, or filenames
  already depend on it.

## Current Tested Surface

The current repo validation surface includes:

- the committed legacy validation summary in
  [`benchmarks/output/python/gap_ridge/lexicographic_peak_validation/lexicographic_peak_validation.json`](../../benchmarks/output/python/gap_ridge/lexicographic_peak_validation/lexicographic_peak_validation.json)
- the extended revalidation summary in
  [`output/lexicographic_rule_revalidation_summary.json`](../../output/lexicographic_rule_revalidation_summary.json)

On those current surfaces, the repo reports zero counterexamples.

## Immediate Consequences On The Tested Surface

On the tested surface, `GWR` compresses several observed features into one
selection law:

- $d(n)=4$ winner dominance,
- left-half winner dominance,
- frequent edge-distance-`2` winners.

Those observations are not separate rules in the current interpretation. They
are consequences of the same winner law when it holds.
