# Gap Winner Rule

## Statement

Inside each prime gap $(p, q)$ with at least one composite interior, assign each
interior integer $n$ the raw-$Z$ quantity

$$
Z_{\mathrm{raw}}(n) = n^{\,1 - d(n)/2}.
$$

For winner comparisons, the implementation uses the equivalent log-score

$$
L(n) = \ln Z_{\mathrm{raw}}(n) = \left(1 - \frac{d(n)}{2}\right)\ln(n).
$$

The Gap Winner Rule (GWR) says the log-score argmax, equivalently the raw-$Z$
argmax, is exactly the interior integer selected by this arithmetic order:

1. choose the smallest interior divisor count $d(n)$,
2. among interiors with that minimum, choose the leftmost one.

Equivalently, the log-score winner and the lexicographic winner are the same
carrier.

## Legacy Name

This rule was first recorded in this repo under the legacy name
`Lexicographic Winner-Take-All Peak Rule`.

Going forward:

- use `Gap Winner Rule` or `GWR` in new prose,
- retain the legacy name where existing titles, figure labels, or filenames
  already depend on it.

## Current Proof Surface

The historical validation surface includes:

- the committed legacy validation summary in
  [`benchmarks/output/python/gap_ridge/lexicographic_peak_validation/lexicographic_peak_validation.json`](../../benchmarks/output/python/gap_ridge/lexicographic_peak_validation/lexicographic_peak_validation.json)
- the extended revalidation summary in
  [`output/lexicographic_rule_revalidation_summary.json`](../../output/lexicographic_rule_revalidation_summary.json)

On those current surfaces, the repo reports zero counterexamples.

The current proof program is local rather than asymptotic.

- the later side is closed by
  [`lexicographic_raw_z_dominance_theorem.md`](./lexicographic_raw_z_dominance_theorem.md);
- the square branch is closed in
  [`prime_gap_admissibility_theorem.md`](./prime_gap_admissibility_theorem.md);
- the square-free branch is reduced there to a fixed early window
  $K = 128$ plus a finite low-class residual table;
- the deterministic admissibility artifacts are
  [`../../output/gwr_proof/prime_gap_admissibility_frontier_2e7.json`](../../output/gwr_proof/prime_gap_admissibility_frontier_2e7.json)
  and
  [`../../output/gwr_proof/prime_gap_admissibility_frontier_1e9_checkpoints.json`](../../output/gwr_proof/prime_gap_admissibility_frontier_1e9_checkpoints.json).

The older BHP bridge notes remain part of the repo history, but they are no
longer the live proof-critical route.

## Immediate Consequences

`GWR` compresses several observed features into one selection law:

- $d(n)=4$ winner dominance,
- left-half winner dominance,
- frequent edge-distance $2$ winners.

Those observations are not separate rules in the current interpretation. They
are consequences of the same winner law when it holds.
