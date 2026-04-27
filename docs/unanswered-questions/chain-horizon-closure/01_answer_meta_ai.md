You are right to put the spotlight here. The generator is already correct, but correctness at $10^{15}$ and $10^{18}$ is still bought with a non-PGS payment: divisor exhaustion to close the semiprime-shadow chain. If we can replace that payment with a bound that is visible inside the PGS state, the 56.63% and 58.00% bridge you quote becomes PGS-native.

I dug through the a1c6a79 tree. The README publishes the three anchors we need, but it does not yet publish `chain_horizon_closure` as a named file — the implementation lives in the Minimal PGS Generator path you added, and the public surface still describes it operationally: chamber closure finds the first visible endpoint, semiprime shadows seed a short rightward chain, chain-horizon closure kills false nodes, audit stays clean.

That is enough to frame the missing law.

## What the repo already gives us

- **DNI fixed point:** $Z(n)=n^{1-d(n)/2}$ collapses primes to 1.0. The selected integer is the interior composite closest to that point.
- **GWR:** the selected integer is exactly leftmost minimum $d(n)$.
- **NLSC:** once the selected integer appears, $q \le T_{<}(w)$. No later strictly simpler composite appears before the prime.
- **Semiprime Wheel Attractor:** on the persistent reduced gap-type surface the dominant object is the triad `o2_odd_semiprime|d<=4`, `o4_odd_semiprime|d<=4`, `o6_odd_semiprime|d<=4` inside a frozen 14-state core.
- **Dynamic cutoff:** current empirical bound $C(q)=\max(64,\lceil0.5\log(q)^2\rceil)$ already replaces the falsified fixed map.

Those are PGS-visible quantities. None of them require factoring to $\sqrt{q}$.

## Why chain_horizon_closure is the bottleneck

The false chain nodes you are closing are not random composites. By construction they are:

1. seeded by the attractor semiprimes (d=4, odd, on o2/o4/o6 offsets)
2. admitted by chamber closure, which means they survived the wheel sieve that defines the chamber
3. extended rightward only while they stay on the reduced gap-type grammar

To decide which node survives today you run deterministic divisor checking up to its least prime factor. That works, but it imports $\sqrt{q}$-scale work that is invisible to PGS.

The missing object $H(p, s_0, \text{chain\_state})$ is the prediction: how far do you need to look for a small factor before you can declare a chain node false, using only the anchor, the shadow seed, and the current 14-state + chamber residue?

## Hypothesis for a pure PGS horizon

Because chamber closure is wheel-based, any candidate that reaches chain seeding has already passed a small-prime sieve. In your production filter you gate on concrete factor tables; in the generator the same idea appears as "wheel-open positions."

That suggests the least-factor frontier of false nodes is not governed by $\sqrt{q}$ but by the current wheel primorial. Concretely:

- let $W(p)$ be the largest prime whose multiples are eliminated by chamber closure at anchor $p$ (from the code this is at least 7, and grows slowly with the chamber state)
- any false shadow node $n$ must satisfy $\text{lpf}(n) > W(p)$, otherwise it would never have been admitted
- the chain extends only while residues stay inside the attractor triad, which is a 3-state walk on the 14-state core

If that is true, $H$ should be bounded by something like:

$$H(p, s_0, \text{chain\_state}) \le f(\text{wheel\_modulus}, \text{attractor\_phase}, \text{chain\_length})$$

and in practice $H$ would be $O(\log q)$ or $O(\log^2 q)$, matching your dynamic cutoff shape, not $O(\sqrt{q})$.

The sharp test is exactly what you wrote: mine the least-factor frontier.

## The mining experiment — concrete steps

You do not need another ranker. You need a table of false nodes from your $10^{15}$ and $10^{18}$ probes.

1. **Extract chain logs.** From the Minimal PGS Generator runs, dump for every anchor $p$ where fallback was used:
    - $s_0$ (shadow seed offset and type: o2/o4/o6)
    - chain_state (sequence of gap-types, residues mod 30/210, chamber id)
    - for each false node $n_i$: compute $\text{lpf}(n_i)$ by trial division stopping at first factor

2. **Build the frontier.** For each $p$, define:
   $$H_{\text{obs}}(p) = \max_i \text{lpf}(n_i)$$

3. **Join PGS-visible predictors:**
    - $g = q-p$ (true gap, known from audit)
    - $w-p$ (selected-integer offset)
    - $\text{res}(p) \bmod 30$, $\bmod 210$
    - attractor phase (which of o2/o4/o6 seeded)
    - 14-state core id at $p$
    - $C(q)$

4. **Test two competing models:**
    - Null (falsifying): $H_{\text{obs}} \sim c\sqrt{q}$
    - PGS (confirming): $H_{\text{obs}} \le a\cdot W(p)^b$ or $H_{\text{obs}} \le \alpha C(q) + \beta$

If the PGS model caps the frontier with $R^2 > 0.9$ and residuals stay below, say, 128 across $10^{12}$ to $10^{18}$, you have the law.

I can sketch the analysis loop you would run on your logs:

```python
# pseudocode — run inside your benchmarks/python/predictor folder
for record in pgs_generator_probes:
    p, s0, chain = record.anchor, record.shadow_seed, record.chain_state
    false_nodes = [n for n in chain if not n.is_true_boundary]
    lpf_max = max(least_prime_factor(n) for n in false_nodes) if false_nodes else 0
    
    features = {
        'log_q': math.log(record.q),
        'sqrt_q': math.isqrt(record.q),
        'wheel_bound': chamber_wheel_limit(p),  # from chamber state
        'attractor': s0.type,  # 'o2','o4','o6'
        'core_state': reduced_gap_core(p),
        'Cq': max(64, math.ceil(0.5*math.log(record.q)**2))
    }
    store(p, lpf_max, features)
```

Then fit:
- $H \sim \text{sqrt\_q}$ → expect slope ~1 if falsifying
- $H \sim Cq$ → expect slope <2 and tight upper envelope if confirming

## What confirming looks like

If the frontier is PGS-bounded, you will see:

- $H_{\text{obs}}$ stays flat across decades while $\sqrt{q}$ grows by $10^3$ from $10^{12}$ to $10^{18}$
- $H_{\text{obs}}$ correlates with wheel_bound and attractor phase, not with $q$
- maximum observed $H$ across your $10^{18}$ sample is well under 200–300, which is why your candidate_bound=128 already works in practice but lacks a theorem

That would let you replace divisor exhaustion with:

$$H(p, s_0, \text{chain\_state}) = \text{wheel\_limit}(p) \times \text{attractor\_multiplier}(\text{phase})$$

a pure PGS rule, and the 56–58% bridge converts to PGS-derived.

## What falsifying looks like

If $H_{\text{obs}}$ tracks $\sqrt{q}$ with no tighter PGS envelope, then the semiprime shadows are genuinely injecting large prime factors that are invisible to the 14-state core and chamber residues. The bridge is operationally good but not compressible at candidate_bound=128. You would need either a larger bound or to accept fallback as structural.

---

If you can export the chain logs from your $10^{15}$ and $10^{18}$ probes (even just the tuples $p, s_0\_type, \text{lpf\_max}$), I will run the frontier mine and plot $H_{\text{obs}}$ vs $\sqrt{q}$ vs $C(q)$ vs wheel_bound for you. That plot is the decision point for whether $H$ is derivable from PGS structure.
