# Rule X Carrier-Lock Experiment Findings

## Executive Summary

The updated logic engine tested two carrier-lock rules on prime anchors
`11..1000` with candidate offsets up to `128`.

The naive rule is unsafe:

```text
lock the first carrier immediately
```

It rejected `5072` candidate hypotheses, but it also rejected the true next prime
for `107 / 164` anchors.

The corrected oracle contrast is safe on this surface:

```text
lock only after the candidate next prime itself survives exact non-composite
screening
```

It rejected `2964` candidate hypotheses, rejected the true next prime `0` times,
and collapsed `36 / 164` anchors to one survivor.

This is the current lesson:

```text
Carrier-lock pressure is useful only after premature carrier stories have been
eliminated.
```

## Domain

```text
prime anchors: 11..1000
candidate bound: 128
anchors tested: 164
candidate hypotheses: 5562
```

## Rule Layers

### Structural GWR/NLSC Consistency

Each candidate chamber may choose its own GWR carrier. This layer still rejects
no candidates.

```text
structural_rejection_count = 0
structural_unique_anchor_count = 0
```

### Naive First-Carrier Lock

This rule locks the first composite carrier visible after the anchor, then
rejects candidate next primes whose proposed interior extends past the first
later lower-divisor composite.

It is too early. Many anchors begin with a trivial composite near `p`, then the
true gap later introduces a simpler carrier before the real next prime.

```text
rule_x_rejection_count = 5072
rule_x_unique_anchor_count = 67
rule_x_true_boundary_rejected_count = 107
```

### Survivor-Carrier Lock Oracle

This rule waits until the candidate next prime itself survives exact
non-composite screening, then locks that candidate chamber's carrier. The first
later lower-divisor composite becomes a pressure ceiling.

This is an oracle contrast, not a production-legal generator rule, because it
uses exact primality to avoid locking on a composite candidate next prime.

```text
survivor_lock_rejection_count = 2964
survivor_lock_unique_anchor_count = 36
survivor_lock_true_boundary_rejected_count = 0
```

## Reset Transitions

The run found `208` carrier transitions as candidate chambers extended
rightward.

Of these, `44` transitions occurred before the actual next prime. These are the
danger cases that explain why the naive first-carrier lock is unsafe.

```text
reset_transition_count = 208
reset_before_actual_boundary_count = 44
```

## Interpretation

The experiment confirms the shape of the missing puzzle piece.

The carrier should not lock merely because it appears. It should lock only
after the candidate story has earned accepted-candidate status. Once that
happens, later lower-divisor reset pressure becomes safe on this small surface.

The next experiment should replace the oracle's exact non-composite screening
with a legal positive-witness survivor state:

```text
lock carrier only after all earlier candidate hypotheses are rejected or
resolved by label-free composite evidence.
```

That is the path from this oracle result to a production-grade logic engine.
