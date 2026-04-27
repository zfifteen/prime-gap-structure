# GWR Claim Hierarchy

This note fixes the claim structure for `Gap Winner Rule` (`GWR`) work in this
repo so theorem-backed statements, exact corollaries, and empirical
consequences do not get mixed.

## 1. Primary Exact Theorem

**Lexicographic Raw-`Z` Dominance Theorem**

For composite integers, if $a < b$ and

$$
d(a) \le d(b),
$$

then the implemented log-score satisfies

$$
L(a) > L(b),
$$

where

$$
L(n)=\left(1-\frac{d(n)}{2}\right)\ln(n).
$$

Primary note:

- [lexicographic_raw_z_dominance_theorem.md](./lexicographic_raw_z_dominance_theorem.md)

## 2. Prime-Gap Selected integer Law

**Gap Winner Rule (`GWR`)**

`GWR` is the proved universal prime-selected interior integer theorem carried by the current
repo proof surface.

Inside a prime gap, the raw-$Z$ maximizer among interior composites is exactly the
leftmost minimizer:

1. minimal divisor count $d(n)$,
2. then leftmost interior integer.

The visible proof chain is:

- theorem statement in
  [gwr_hierarchical_local_dominator_theorem.md](./gwr_hierarchical_local_dominator_theorem.md),
- later-side closure by
  [lexicographic_raw_z_dominance_theorem.md](./lexicographic_raw_z_dominance_theorem.md),
- earlier-side local admissibility closure in
  [prime_gap_admissibility_theorem.md](./prime_gap_admissibility_theorem.md),
- residual low-class closure in
  [../../output/gwr_proof/residual_class_closure_20260413_0008.json](../../output/gwr_proof/residual_class_closure_20260413_0008.json)
  and
  [../../output/gwr_proof/residual_class_closure_20260413_1104.json](../../output/gwr_proof/residual_class_closure_20260413_1104.json),
- top-level summary in [../../GWR_PROOF.md](../../GWR_PROOF.md).

## 3. Exact Corollaries And Direct Consequences

These follow from the proved maximizer rule or are presented as direct consequence
notes in the repo:

- [prime_gap_exclusion_consequences.md](./prime_gap_exclusion_consequences.md)
- [prime_boundary_placement_finding.md](./prime_boundary_placement_finding.md)

## 4. Empirical Consequences On The Tested Surface

These are measured consequences of the proved law on the committed surfaces:

- [closure_constraint_findings.md](./closure_constraint_findings.md)
- [dominant_d4_arrival_reduction_findings.md](./dominant_d4_arrival_reduction_findings.md)
- $d(n)=4$ selected integer dominance,
- left-half selected integer dominance,
- frequent edge-distance-`2` selected integers,
- exact recursive walk hit rate `1.0` on the committed tested ladders.

## 5. Robustness Claims

These should remain explicitly empirical unless separately proved.

Examples:

- nearby score factors such as `log(n+1)`,
- small smooth perturbations of the logarithmic factor,
- alternate sampling surfaces or window placements.

## 6. Historical Route

The older bridge-era route and proof-progress notes are now archived:

- [../archive/pre-proof/README.md](../archive/pre-proof/README.md)

Use those files for continuity only, not for the visible proof-facing status.
