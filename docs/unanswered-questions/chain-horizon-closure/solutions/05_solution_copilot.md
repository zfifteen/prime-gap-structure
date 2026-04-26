**Recommendation — Run the least‑factor frontier mining experiment now and use its empirical maxima to accept or reject each LLM proposal; do not change `chain_horizon_closure` until that data is in hand.**

### Quick verdict (1–2 sentences)
**The single decisive step is an empirical least‑factor frontier sweep** (stratified by anchor/gap type, scales \(10^{12}\!-\!10^{18}\)) that records the *maximum* least factor among false chain nodes per anchor. If that maximum admits a PGS‑visible bound \(\ll\sqrt{q}\), implement the corresponding `H(p,s0,chain_state)`; otherwise accept that deterministic divisor exhaustion is necessary.

---

### Comparison of the candidate answers (summary table)

| **Answer file** | **Core claim** | **Testable prediction** | **Practical strength** |
|---|---:|---|---|
| **01_answer_meta_ai.md** | Meta‑analysis / high‑level plan | Predicts existence of compact PGS bound | Strong on experimental design; weak on concrete `H` |
| **02_asnwer_grok.md** | Residue/wheel‑based bound | `H` derived from wheel residues/gap pattern | Plausible; directly testable via wheel‑limited horizon metric |
| **03_asnwer_deepseek.md** | Statistical/ML fit to frontier | `H` as fitted polylog function | Useful as heuristic; needs provable link to PGS |
| **04_answer_copilot.md** | Code‑first collector + integration | Provides instrumentation plan | High practical value; accelerates data collection |
| **05_answer_chatgpt.md** | Theorem‑style derivation attempt | Claims analytic bound from divisor algebra | Ambitious; likely to fail without new number‑theory lemma |
| **06_answer_xai_grok.md** | Hybrid: residue + anchor invariants | `H` from combined residue/anchor invariants | Promising if residues explain frontier tail |

---

### For each answer: experiment to run and expected decisive observation

1. **Meta AI (01)**
    - **Experiment:** Full least‑factor frontier sweep (pilot 10k anchors at \(10^{15}\)).
    - **Decision rule:** If frontier max \( \le H_{\text{meta}}(p,s_0,\ldots)\) for all samples → accept.
    - **What to capture:** per‑anchor max least factor, stage where factor found (trial bound B).

2. **Grok residue hypothesis (02)**
    - **Experiment:** For each false node, compute residue vector modulo wheel primes; test whether largest admissible small prime consistent with residues upper‑bounds least factor.
    - **Decisive sign:** frontier max explained by wheel primes only.

3. **DeepSeek statistical fit (03)**
    - **Experiment:** Fit frontier tail to candidate forms: polylog, power law, \(C(\log q)^k\).
    - **Decisive sign:** fitted bound \( \ll \sqrt{q}\) with negligible false negatives.

4. **Copilot instrumentation (04)**
    - **Experiment:** Implement collector module and run pilot.
    - **Decisive sign:** reliable, low‑overhead data capture enabling the other tests.

5. **ChatGPT theorem attempt (05)**
    - **Experiment:** Attempt to prove small bound from divisor algebra on sampled counterexamples.
    - **Decisive sign:** existence of counterexamples with least factor \(\sim\sqrt{q}\) falsifies.

6. **xAI hybrid (06)**
    - **Experiment:** Build composite invariant (anchor size, seed residues, gap vector) and test deterministic bound.
    - **Decisive sign:** zero/near‑zero false negatives across scales.

---

### Concrete experimental protocol (implementation checklist)
- **Collector**: hook into `chain_horizon_closure` probe mode; log NDJSON with fields: `p,q,s0,chain_gaps,residues,n,least_factor,found_stage`.
- **Trial bounds**: Stage A trial up to \(B=2^{20}\); Stage B wheel‑sieved up to wheel max; mark `horizon > B` if not found.
- **Sampling**: stratify by gap type (o2,o4,o6), collect ≥10k anchors per scale.
- **Analysis**: compute per‑anchor frontier max, empirical CDF, fit candidate `H` forms, compute false‑negative rate.
- **Decision thresholds**: require **zero** false negatives for acceptance as deterministic `H` (or vanishing rate with provable tail control).

---

### Risks, limitations, and next steps
- **Risk:** Pilot may show rare extreme anchors with least factor \(\sim\sqrt{q}\); that falsifies compressibility at `candidate_bound=128`.
- **Mitigation:** If rare extremes exist, consider raising `candidate_bound` or accept hybrid fallback.
- **Next step (practical):** I will produce the **collector skeleton** and the **analysis notebook** patches you can drop into the repo; start with the collector so you can run the pilot immediately.
