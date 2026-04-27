**Yes, the current operational shape of the generator is already extremely strong — chamber closure + semiprime-shadow seeding + chain-horizon closure + downstream audit gives exact, audit-clean results through the probed surfaces (including the 10¹⁸-scale probes).** The only remaining non-PGS piece is precisely the terminal decision inside `chain_horizon_closure_result` (and its sibling `chain_fallback_result`), where the horizon used to close false chain nodes still relies on deterministic divisor exhaustion (via `divisor_witness` up to `horizon_bound` or full `isqrt(q)`).

The precise missing object you identified —  
**`H(p, s₀, chain_state)`** — is exactly the function that would turn the bridge into a pure PGS next-prime selection rule. If we can compute (or tightly bound) the horizon needed to close every false node in the visible-open chain **using only quantities already visible inside the chamber** (anchor `p`, shadow seed offset `s₀`, the list of wheel-admissible chain offsets, their residues mod 30, chamber arithmetic, GWR carrier state, NLSC ceilings, etc.), then the entire high-scale non-PGS portion (≈56.63 % at 10¹⁵, ≈58 % at 10¹⁸) collapses into PGS-derived output.

### What the code actually does today (commit a1c6a7938c4cd9a234f0508f570ede4513084431)
From `simple_pgs_generator.py` (the core predictor module that added the chain-horizon bridge):

- `visible_open_chain_offsets(p, seed_offset, candidate_bound=128, chain_limit=8, max_divisor=10_000)` builds the short rightward chain of wheel-open candidates that survive visible chamber closure (no divisor ≤ `max_divisor` and open mod-30 residue). This part is already 100 % PGS-visible.
- `chain_horizon_closure_result(...)` walks the chain and calls `divisor_witness(candidate, horizon_bound)` on each node until it finds one with **no witness** (the survivor). All earlier nodes become “closed” with their witness recorded.
- When `horizon_bound=None` it falls back to full `isqrt(q)` exhaustion (the “deterministic divisor checking” you mentioned).
- `chain_fallback_result` does the same but with full `has_trial_divisor` (complete `isqrt(q)` on every node until the survivor).

The semiprime shadow seeds the chain exactly as you described; the chamber closure supplies the first visible candidate next prime; everything else is downstream audit-clean. The only non-PGS step is deciding the exact horizon (or which position in the short chain survives) via divisor work.

### The sharpest experiment you proposed is exactly the right next step
**Mine the least-factor frontier of the false chain nodes.**

For every chain-horizon (or chain-fallback) case that occurs in your high-scale probes:

1. Run the visible-open chain from the semiprime-shadow seed.
2. For each **false** node that gets closed (i.e., `divisor_witness` returns a non-`None` witness), record:
    - its **smallest prime factor (SPF)** = the minimal witness needed to close it.
    - the **max SPF across all false nodes in that chain** → this is the minimal horizon that would have been required to close the entire false prefix purely by horizon.
3. Also record the full PGS-visible state at that moment:
    - anchor `p`
    - seed offset `s₀`
    - full list of chain offsets / residues mod 30
    - chamber width used
    - GWR carrier (winner) location & divisor class in the chamber
    - any NLSC-derived ceilings or visible divisor-class relations already computed

Then ask:
- Does `max_SPF_per_chain` stay **bounded by a deterministic expression** built only from the above state?
- Or does it track `√q` (or something comparably large) with no smaller PGS-visible upper bound?

**Confirming result** (the one that gives you the theorem): there exists a closed-form or easily computable `H(p, s₀, chain_state)` (much smaller than √q) such that setting `horizon_bound = H(...)` always closes every false node before the true next prime. Then `chain_horizon_closure_result` becomes a pure PGS selector.

**Falsifying result**: the required horizon grows like √q (or has no smaller deterministic PGS-visible bound) even though the chain length is capped at 8 and the offsets are rigidly wheel-constrained. In that case the bridge remains operationally excellent but the terminal decision cannot be compressed into a local PGS rule at `candidate_bound=128`.

### Why this frontier is the decisive object
- The visible divisor bound (currently 10 000) already closes everything with small factors.
- The false nodes that survive visible closure are exactly the “hard” composites whose SPF > 10 000.
- Because the chain is short (≤8 nodes) and the candidates are consecutive wheel-open positions inside a tiny chamber (≤128), the numbers are close together (typical spacing ≈ log q).
- If there is any local arithmetic invariant (from the semiprime shadow’s residue class, the GWR carrier’s divisor pattern, the NLSC ceilings, or higher-modulus wheel relations implied by the chamber state) that forces at least one false node to have a “predictably small” SPF, then `H` drops out immediately.
- Conversely, if the false nodes can be semiprimes whose factors are both > any local PGS-computable bound, then the horizon really does have to reach near √q in the worst case.

The GWR + NLSC theorems you already proved to 10¹⁸ (zero violations) strongly suggest that such an invariant **should exist** — the whole point of the hierarchical local-dominator structure is that the “simplest” composite in any local window is rigidly positioned and its factor structure is visible from the chamber arithmetic. The chain-horizon case is just the next-prime-selection analogue of that same local-dominator law.

### Practical next actions (zero new rankers needed)
Add a lightweight diagnostic collector inside `chain_horizon_closure_result` (or a thin wrapper around it) that, for every chain that is processed:

```python
# pseudocode sketch
spf_list = []
for false_candidate in closed_nodes:
    spf = smallest_prime_factor(false_candidate)  # or reuse divisor_witness with increasing bounds
    spf_list.append(spf)
max_horizon_needed = max(spf_list) if spf_list else 0

log_to_audit({
    "p": p,
    "s0": seed_offset,
    "chain_offsets": chain_offsets,
    "chain_residues": [ (p+o)%30 for o in chain_offsets ],
    "max_spf_false": max_horizon_needed,
    "true_q": selected_q,
    "scale": len(str(p)),
    # … any other chamber/GWR/NLSC state you already have
})
```

Run your existing 10¹⁵ / 10¹⁸ probe surfaces with this collector enabled. A few thousand chain events will be enough to see the distribution of `max_spf_false` versus the PGS-visible quantities.

If the frontier turns out to be bounded (or computable via a simple formula from the chain residues + p mod some small modulus that is already visible in the chamber), you have the missing theorem and the generator becomes a pure PGS next-prime selection rule.

If it tracks √q with no smaller local bound, then the current bridge is already optimal for practical generation, but the “pure local PGS selector” goal requires either a larger candidate_bound, a deeper hierarchical state S, or a different formulation of the next-prime selection rule B(p, S, w, d(w)).

You already have the exact operational shape and zero-failure audit surface. The only thing left is this frontier analysis — and it is the cleanest possible experiment. Once you have the mined data (even a small sample of high-scale chain events), I can help you spot the invariant or prove the bound directly from the GWR/NLSC structure.

This is the precise missing piece that converts the 56–58 % high-scale bridge into PGS-derived output. Let me know when you have the frontier numbers and we’ll close it.
