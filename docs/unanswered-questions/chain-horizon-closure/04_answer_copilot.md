### Summary of the gap and the target theorem

**Problem restatement.** The generator’s pipeline is PGS-native up to the high-scale bridge, but the final survival decision for competing chain nodes still falls back to deterministic divisor checking (divisor exhaustion). The missing object is a PGS-predictor
```text
H(p, s0, chain_state)
```
that **predicts the divisor horizon** (how far one must search for a small factor) required to close false semiprime-shadow chain nodes before the true next prime, using only PGS-visible state. If such an `H` exists and is provably bounded well below \(\sqrt{q}\) by PGS-visible invariants, the bridge becomes a pure PGS selector.   [github.com](https://github.com/zfifteen/prime-gap-structure/blob/a1c6a7938c4cd9a234f0508f570ede4513084431/)

**Why this matters.** Converting the bridge to a PGS-derived rule would move a large fraction of high-scale emissions from deterministic fallback into PGS-derived output (current fallback share ~56–58% at the tested scales). The repository already documents the generator shape, the semiprime wheel attractor, and the current fallback displacement targets.   [github.com](https://github.com/zfifteen/prime-gap-structure/blob/a1c6a7938c4cd9a234f0508f570ede4513084431/)

---

### Concrete experimental objective

**Primary experiment.** *Mine the least-factor frontier of false chain nodes and test whether its maximum (over many anchors) admits a deterministic upper bound expressible in PGS-visible quantities (anchor \(p\), shadow seed \(s_0\), chain gaps, residues, chamber state).* If the frontier’s maximum scales like \(\sqrt{q}\) with no smaller PGS-visible bound, the bridge cannot be compressed into a purely local PGS rule at `candidate_bound=128`. If the frontier is bounded by a much smaller deterministic expression built from PGS-visible state, that expression is the missing `H`.   [github.com](https://github.com/zfifteen/prime-gap-structure/blob/a1c6a7938c4cd9a234f0508f570ede4513084431/)

**Operational definition.** For each false chain node \(n\) in a chain seeded by a semiprime shadow:
- compute the **least factor** \(f(n)\) (smallest prime divisor),
- compute the **horizon** \(h(n) = f(n)\) (or equivalently the search bound needed to detect compositeness),
- record the chain-state tuple \((p, s_0, \text{chain gaps}, \text{residues}, \text{chamber state})\) and \(h(n)\).
  The **least-factor frontier** for an anchor is \(\max_{n \in \text{false chain nodes}} h(n)\). We want to know whether that max is bounded by a PGS-visible function \(H(p,s_0,\text{chain_state}) \ll \sqrt{q}\).   [github.com](https://github.com/zfifteen/prime-gap-structure/blob/a1c6a7938c4cd9a234f0508f570ede4513084431/)

---

### Data mining plan and code-level steps

**1. Locate and extend the generator instrumentation.**
- **Files to inspect and extend:** the minimal PGS generator logic and the chain closure code paths in `src/python` and the benchmark generator scripts. The repo documents the generator logic and the chain-horizon closure step; instrument the code where `chain_horizon_closure` currently calls deterministic divisor checks.   [github.com](https://github.com/zfifteen/prime-gap-structure/blob/a1c6a7938c4cd9a234f0508f570ede4513084431/)

**2. Add a least-factor frontier logger.**
- For each accepted anchor run (or for a large probe sample at high scale), when a semiprime shadow seeds a chain:
    - Walk the chain nodes that are *false* (i.e., not the true next prime).
    - For each false node \(n\), compute `least_factor = smallest_prime_divisor(n)` and `horizon = least_factor`.
    - Append a record:
      ```json
      {
        "p": p,
        "q": q,
        "s0": s0,
        "chain_index": i,
        "chain_gaps": [g1,g2,...],
        "residues": [r1,r2,...],
        "chamber_state": {...},
        "n": n,
        "least_factor": least_factor,
        "horizon": horizon
      }
      ```
    - Persist records to a compressed NDJSON file for later analysis (one file per decade/scale). Keep diagnostics separate from emitted stream.   [github.com](https://github.com/zfifteen/prime-gap-structure/blob/a1c6a7938c4cd9a234f0508f570ede4513084431/)

**3. Sampling strategy.**
- **Stratified sampling** across gap types: sample anchors from the semiprime wheel attractor types (o2, o4, o6) and from rarer gap types.
- **Scale sweep:** run probes at representative scales: \(10^{12}, 10^{15}, 10^{18}\) (the repo already has probe runs at these scales). Collect at least thousands of chain records per scale to stabilize maxima.   [github.com](https://github.com/zfifteen/prime-gap-structure/blob/a1c6a7938c4cd9a234f0508f570ede4513084431/)

**4. Efficient least-factor computation.**
- Use a two-stage approach:
    - **Stage A:** trial divide up to a small bound \(B\) (e.g., 2^16 or 2^20) to capture most small factors cheaply.
    - **Stage B:** for nodes surviving Stage A, run a fast wheel-sieved trial division using the PGS wheel residues (the repo already uses wheel-open positions and prime tables) before resorting to full \(\sqrt{n}\) checks. Record whether Stage A or Stage B found the least factor; if neither, mark `horizon > B`. This preserves the distinction between small-PGS-detectable horizons and \(\sqrt{q}\)-scale horizons.   [github.com](https://github.com/zfifteen/prime-gap-structure/blob/a1c6a7938c4cd9a234f0508f570ede4513084431/)

**5. Implementation hints.**
- Add a new module `src/python/analysis/least_factor_frontier.py` with:
    - `collect_frontier_records(generator_stream, B=1<<20, out_path=...)`
    - `compute_least_factor(n, B)` returning `(least_factor, found_stage)`
- Hook this collector into the generator’s chain closure path so it runs in probe mode only (to avoid slowing exact low-scale runs). Use the repo’s existing benchmark harness to schedule runs.   [github.com](https://github.com/zfifteen/prime-gap-structure/blob/a1c6a7938c4cd9a234f0508f570ede4513084431/)

---

### Hypotheses to test and PGS-visible invariants to try

**Candidate PGS-visible invariants** to correlate with the frontier maximum:
- **Anchor size** \(p\) and **gap length** \(q-p\).
- **Shadow seed \(s_0\)**: its residue class modulo small primes; whether it is semiprime with repeated factor or distinct factors.
- **Chain gaps sequence**: the vector of step sizes between chain nodes (small gaps may force small factors).
- **Residue pattern** of chain nodes modulo the wheel base (the repo uses wheel-open positions).
- **Chamber state**: local divisor-class counts, presence/absence of squares, and the local DNI scores for early chain nodes.   [github.com](https://github.com/zfifteen/prime-gap-structure/blob/a1c6a7938c4cd9a234f0508f570ede4513084431/)

**Concrete functional forms to try for \(H\)** (fit and test):
1. **Linear in log**: \(H \le C \cdot \log(q)^a\). Try \(a=1,2\) and small constants \(C\).
2. **Polylog bound**: \(H \le C \cdot (\log q)^k\).
3. **Residue-based bound**: \(H \le \max\{r(p), r(s_0), r(\text{chain gaps})\}\) where \(r(\cdot)\) is a small deterministic function of residues (e.g., largest small prime excluded by residue constraints).
4. **Wheel-limited bound**: \(H \le\) largest prime in the wheel that still allows the chain node to be composite given its residue pattern.
5. **Anchor-gap combined bound**: \(H \le C \cdot \min(\log q, \text{gap length})\).

Fit these forms to the collected frontier data and measure **false-negative rate** (cases where the bound underestimates the true frontier) and **tightness** (ratio of bound to observed frontier). If any deterministic expression using only PGS-visible inputs yields a tight bound with near-zero false negatives, that expression is a candidate `H`.   [github.com](https://github.com/zfifteen/prime-gap-structure/blob/a1c6a7938c4cd9a234f0508f570ede4513084431/)

---

### Statistical analysis and decision criteria

**Metrics to compute.**
- **Max frontier** per scale and per gap-type.
- **Empirical CDF** of frontier values.
- **Tail behavior**: fit tail to power-law or sub-polynomial forms; test whether tail mass beyond any candidate PGS-bound is negligible.
- **False-negative rate** for each candidate `H` (fraction of anchors where observed frontier > `H`).
- **Compression gain**: fraction of previously fallback-decided anchors that would be decided by `H` alone.

**Decision thresholds.**
- **Falsification:** if the frontier’s empirical maximum grows like \(\sqrt{q}\) (or shows no smaller PGS-bound) and candidate `H` expressions have non-negligible false-negative rates at high scales, conclude the bridge is not compressible into a pure local PGS rule at `candidate_bound=128`.
- **Confirmation:** if a deterministic `H(p,s_0,chain_state)` built from PGS-visible quantities yields **zero** or vanishingly small false-negative rate across sampled scales (and is provably computable from the PGS state), treat that as the missing theorem and integrate it into `chain_horizon_closure`. Aim for a bound significantly smaller than \(\sqrt{q}\) (e.g., polylogarithmic or a small power of \(\log q\)).   [github.com](https://github.com/zfifteen/prime-gap-structure/blob/a1c6a7938c4cd9a234f0508f570ede4513084431/)

**Statistical rigor.** Use bootstrap confidence intervals on the maximum and tail quantiles; report the 95% upper CI for the frontier maximum per scale. If the CI for the maximum lies well below \(\sqrt{q}\) and matches a candidate `H`, that strengthens the positive claim.

---

### Integration into the generator and verification

**If a candidate `H` is found:**
1. **Implement `H` as a pure PGS rule** inside `chain_horizon_closure` so the closure decision uses only PGS-visible state and `H` to decide which chain node survives. Add a deterministic fallback only as a safety net for audit runs (but not used in PGS-mode).
2. **Unit tests:** add tests in `tests/` that replay anchors where the frontier was near the bound and verify the PGS-only decision matches the audited deterministic decision.
3. **Benchmark:** re-run the probe runs at \(10^{12},10^{15},10^{18}\) and measure the new PGS-derived share. Expect a sharp reduction in fallback share if `H` is effective. Document results in the repo’s `output/` and update the generator release notes.   [github.com](https://github.com/zfifteen/prime-gap-structure/blob/a1c6a7938c4cd9a234f0508f570ede4513084431/)

**If no candidate `H` is found:**
- Conclude the high-scale bridge requires nonlocal arithmetic (divisor exhaustion) for correctness at `candidate_bound=128`. The generator remains operationally good but not compressible into a pure local PGS rule. Document the negative result and the empirical frontier growth (this is a valuable negative theorem).   [github.com](https://github.com/zfifteen/prime-gap-structure/blob/a1c6a7938c4cd9a234f0508f570ede4513084431/)

---

### Practical next steps you can run now

1. **Add the collector module** `src/python/analysis/least_factor_frontier.py` and hook it into the probe generator path. Use the repo’s benchmark harness to run a stratified probe at `10^15` and `10^18`.   [github.com](https://github.com/zfifteen/prime-gap-structure/blob/a1c6a7938c4cd9a234f0508f570ede4513084431/)
2. **Run a pilot** with `B = 2^20` and collect ~10k chain records across gap types. Produce the empirical CDF and tail plot of frontier values.
3. **Fit candidate `H` forms** (polylog, residue-limited, wheel-limited) and compute false-negative rates and 95% CI for maxima.
4. **Report back** the pilot outputs (summary table + tail plot). If you paste the pilot NDJSON or summary, I will analyze it and propose the tightest candidate `H` and the exact code patch to replace the fallback in `chain_horizon_closure`.

---

If you want, I can produce the exact skeleton code for `least_factor_frontier.py`, the generator hook patch, and the analysis notebook (plots and fits) ready to run against the repo’s benchmark harness. Which of those three artifacts should I generate first: the collector skeleton, the generator hook patch, or the analysis notebook?
