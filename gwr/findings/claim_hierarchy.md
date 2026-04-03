# GWR Claim Hierarchy

This note fixes the claim structure for `Gap Winner Rule` (`GWR`) work in this
repo so theorem-backed statements and empirical statements do not get mixed.

## 1. Primary Theorem

**Lexicographic Raw-`Z` Dominance Theorem**

This is the deepest exact theorem currently established in the repo notes.

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

Equivalently, the earlier composite wins whenever it also has no larger divisor
count.

This theorem is exact and global in the ordered direction. It is not specific
to prime gaps.

Primary note:

- [`lexicographic_raw_z_dominance_theorem.md`](./lexicographic_raw_z_dominance_theorem.md)

## 2. Prime-Gap Winner Law

**Gap Winner Rule (`GWR`)**

This is the current prime-gap winner law on the tested surface.

Inside a prime gap, the raw-$Z$ winner among interior composites is exactly the
lexicographic winner:

1. minimal divisor count $d(n)$,
2. then leftmost interior integer.

The exact ordered dominance theorem supplies local structure beneath this law,
but it does not by itself prove GWR on arbitrary gap interiors. GWR remains the
separate prime-gap statement whose surface is validated empirically in this
repo.

Canonical note:

- [`gap_winner_rule.md`](./gap_winner_rule.md)

## 3. Prime-Gap Theorem Candidates

These are narrower than full GWR but stronger than descriptive plot-level
observations.

### `No-Later-Simpler-Composite Theorem`

This is the closure theorem candidate:

- once the implemented winner appears, the next prime closes the gap before any
  later strictly simpler composite can enter the interior.

Primary note:

- [`no_later_simpler_composite_theorem.md`](./no_later_simpler_composite_theorem.md)

### `Square-Exclusion First-d=4 Theorem`

This is the dominant-case theorem candidate:

- in gaps with no interior prime square and at least one interior $d=4$
  carrier, the implemented winner is the first such $d=4$ carrier.

Primary note:

- [`square_exclusion_first_d4_theorem.md`](./square_exclusion_first_d4_theorem.md)

## 4. Empirical Consequences On The Tested Surface

These are not separate laws. They are consequences of `GWR` on the tested
prime-gap surface.

Use this category for statements such as:

- $d(n)=4$ winner dominance,
- left-half winner dominance,
- frequent edge-distance-`2` winners.

When writing about them, say that `GWR` explains them on the tested surface.

## 5. Robustness Claims

These should remain explicitly empirical unless separately proved.

Examples:

- nearby score factors such as `log(n+1)`,
- small smooth perturbations of the logarithmic factor,
- alternate sampling surfaces or window placements.

The exact theorem is about the implemented log-score $L(n)$, equivalently
raw-$Z$ under monotone logarithm. Robustness findings for nearby scores are
separate evidence, not part of the theorem.

## 6. Novelty Framing

Use this structure:

- the ordered dominance theorem is the exact mathematical statement,
- `GWR` is the prime-gap winner law,
- the closure and dominant-$d=4$ notes are theorem candidates built from that
  winner law,
- novelty status remains an external literature question and should be stated
  carefully.

Safe wording:

`GWR appears to be a new empirical law on the tested surface, and no matching
prior theorem has yet been identified in the literature search done so far.`

## 7. Preferred Master Framing

Use this sentence when a compact overview is needed:

`The Gap Winner Rule is the current prime-gap winner law; the Lexicographic Raw-Z Dominance Theorem supplies its exact ordered backbone, and the dominant d=4 reduction plus No-Later-Simpler-Composite condition supply its leading mechanism and closure consequence on the tested surface.`
