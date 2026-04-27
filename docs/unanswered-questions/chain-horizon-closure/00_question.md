The most significant unanswered question is:

**Can `chain_horizon_closure` be turned into a pure PGS next-prime selection rule by deriving the divisor-horizon law from PGS structure, instead of using fallback divisor exhaustion?**

Right now the generator has the correct operational shape:

- search-interval closure finds the first visible candidate next prime;
- semiprime shadows seed a short rightward chain;
- chain-horizon closure closes false chain nodes;
- downstream audit confirms zero failures on tested surfaces.

But the high-scale bridge still depends on deterministic divisor checking to decide which chain node survives. That means the generator is accurate, but the high-scale terminal decision is not yet predominantly PGS-derived.

The precise missing object is:

```text
H(p, s0, chain_state)
```

where `H` predicts the divisor horizon needed to close the false semiprime-shadow chain nodes before the true next prime.

If we can derive that horizon from PGS-visible quantities, then the current bridge becomes a real PGS selection rule. That would convert the major high-scale non-PGS portion:

- `56.63%` at `10^15`
- `58.00%` at `10^18`

into PGS-derived output, or at least sharply reduce it.

The sharpest next experiment is not another ranker. It is:

**Mine the least-factor maximum of false chain nodes and determine whether its maximum is governed by a PGS-visible invariant of the input prime, shadow seed, chain gaps, residues, or search-interval state.**

Falsifying result: if the required horizon tracks `sqrt(q)` with no smaller PGS-visible bound, then the bridge is operationally good but not compressible into a pure local PGS rule at `candidate_bound=128`.

Confirming result: if the required horizon is bounded by a deterministic expression much smaller than `sqrt(q)` using only PGS-visible state, that is the missing theorem.
