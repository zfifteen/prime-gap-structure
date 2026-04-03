# GWR Claim Hierarchy

This note fixes the claim structure for `Gap Winner Rule` (`GWR`) work in this
repo so theorem-backed statements and empirical statements do not get mixed.

## 1. Primary Theorem

**Global raw-`Z` ordering theorem**

This is the deepest exact claim.

For composite integers, the raw-`Z` score

`Z(n) = (1 - d(n)/2) ln(n)`

is strictly ordered by the lexicographic order `(d(n), n)`, with smaller
divisor count first and, among equal divisor counts, smaller integer first.

This claim is global. It is not specific to prime gaps.

Primary note:

- [`global_raw_z_ordering_theorem.md`](./global_raw_z_ordering_theorem.md)

## 2. Immediate Corollary

**Gap Winner Rule (`GWR`)**

This is the prime-gap specialization of the global theorem.

Inside a prime gap, the raw-`Z` winner among interior composites is exactly the
lexicographic winner:

1. minimal divisor count `d(n)`,
2. then leftmost interior integer.

Canonical note:

- [`gap_winner_rule.md`](./gap_winner_rule.md)

## 3. Empirical Consequences On The Tested Surface

These are not separate laws. They are consequences of `GWR` on the tested
prime-gap surface.

Use this category for statements such as:

- `d(n)=4` winner dominance,
- left-half winner dominance,
- frequent edge-distance-`2` winners.

When writing about them, say that `GWR` explains them on the tested surface.

## 4. Robustness Claims

These should remain explicitly empirical unless separately proved.

Examples:

- nearby score factors such as `log(n+1)`,
- small smooth perturbations of the logarithmic factor,
- alternate sampling surfaces or window placements.

The exact global theorem is about raw-`Z` as defined. Robustness findings for
nearby scores are separate evidence, not part of the theorem.

## 5. Novelty Framing

Use this structure:

- the global ordering theorem is the exact mathematical statement,
- `GWR` is the prime-gap corollary under the preferred forward name,
- novelty status remains an external literature question and should be stated
  carefully.

Safe wording:

`GWR appears to be a new empirical law on the tested surface, and no matching
prior theorem has yet been identified in the literature search done so far.`

## 6. Preferred Master Framing

Use this sentence when a compact overview is needed:

`The Gap Winner Rule is the prime-gap corollary of a global raw-`Z` ordering theorem on composite integers.`
