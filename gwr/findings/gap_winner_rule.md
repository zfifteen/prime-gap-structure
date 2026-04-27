# Gap Winner Rule

## Statement

Inside each prime gap $(p, q)$ with at least one composite interior, assign each
interior integer $n$ the raw-$Z$ quantity

$$
Z_{\mathrm{raw}}(n) = n^{\,1 - d(n)/2}.
$$

For selected integer comparisons, the implementation uses the equivalent log-score

$$
L(n) = \ln Z_{\mathrm{raw}}(n) = \left(1 - \frac{d(n)}{2}\right)\ln(n).
$$

The Gap Winner Rule (GWR) says the log-score argmax, equivalently the raw-$Z$
argmax, is exactly the interior integer selected by this arithmetic order:

1. choose the smallest interior divisor count $d(n)$,
2. among interiors with that minimum, choose the leftmost one.

Equivalently, the log-score maximizer and the leftmost minimizer are the same
integer.

## Legacy Name

This rule was first recorded in this repo under the legacy name
`Lexicographic Winner-Take-All Peak Rule`.

Going forward:

- use `Gap Winner Rule` or `GWR` in new prose,
- retain the legacy name where existing titles, figure labels, or filenames
  already depend on it.

## Closed Proof Surface

The live proof-facing surface is now closed.

The canonical proof documents are:

- [gwr_hierarchical_local_dominator_theorem.md](./gwr_hierarchical_local_dominator_theorem.md)
- [lexicographic_raw_z_dominance_theorem.md](./lexicographic_raw_z_dominance_theorem.md)
- [prime_gap_admissibility_theorem.md](./prime_gap_admissibility_theorem.md)
- [../../GWR_PROOF.md](../../GWR_PROOF.md)

The closure artifacts that discharged the former low-class remainder are:

- [../../output/gwr_proof/residual_class_closure_20260413_0008.json](../../output/gwr_proof/residual_class_closure_20260413_0008.json)
- [../../output/gwr_proof/residual_class_closure_20260413_1104.json](../../output/gwr_proof/residual_class_closure_20260413_1104.json)

The exact audit surface behind that closure includes:

- [../../output/gwr_proof/parallel_no_early_counterexample candidate_5e9.json](../../output/gwr_proof/parallel_no_early_spoiler_5e9.json)
- [../../output/gwr_proof/earlier_counterexample candidate_local_dominator_scan_square_adjacent_1e12.json](../../output/gwr_proof/earlier_spoiler_local_dominator_scan_square_adjacent_1e12.json)

The historical validation summaries remain useful as audit record:

- [../../benchmarks/output/python/gap_ridge/lexicographic_peak_validation/lexicographic_peak_validation.json](../../benchmarks/output/python/gap_ridge/lexicographic_peak_validation/lexicographic_peak_validation.json)
- [../../output/lexicographic_rule_revalidation_summary.json](../../output/lexicographic_rule_revalidation_summary.json)

## Immediate Consequences

`GWR` compresses several observed features into one exact maximizer rule:

- $d(n)=4$ selected integer dominance,
- left-half selected integer dominance,
- frequent edge-distance $2$ selected integers.

Those observations are not separate rules in the current interpretation. They
are consequences of the proved maximizer rule.
