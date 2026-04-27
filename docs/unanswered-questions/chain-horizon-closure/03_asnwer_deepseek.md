Based on an analysis of the repository's code, particularly the `simple_pgs_generator.py` file, I can provide a detailed breakdown of the `chain_horizon_closure` problem and the path toward a potential solution.

### 1. The Current Operational Bridge
The generator's logic, as implemented in `chain_horizon_closure_result` (lines 66-85 of the code), currently relies on a critical fallback:
- It iterates through a chain of candidate offsets generated from semiprime shadows.
- For each candidate, it calls `divisor_witness(candidate, horizon_bound)`.
- **Crucially, when `horizon_bound` is `None`, the `divisor_witness` function defaults to full trial division up to `isqrt(n)`, which is deterministic divisor checking.** This is the non-PGS portion you identified.
- The first candidate that passes this full trial division test is selected as the next prime `q`.

This means the high-scale terminal decision is not yet predominantly PGS-derived; it depends on the full divisor exhaustion fallback.

### 2. The Core of the Question
The goal is to replace this deterministic fallback with a function `H(p, s0, chain_state)` that predicts the necessary divisor horizon. This horizon would be the minimum divisor bound needed to close all false semiprime-shadow chain nodes, allowing the true next prime to be identified using only PGS-visible quantities. The missing theorem is whether such a horizon can be derived from PGS structure alone.

### 3. Proposed Approach to Derive the Horizon Law
Your suggestion to "mine the least-factor frontier of false chain nodes" is apt. The key is to analyze the pattern of divisor witnesses for the false chain nodes that are closed during the chain-horizon process. The steps would be:

1.  **Data Collection**: For each generator step where `chain_horizon_closure` is invoked, record:
    - The input prime `p`.
    - The semiprime shadow seed `s0`.
    - The chain offsets and the corresponding composite candidates.
    - The specific divisor witness `w` that closed each false node.
    - The PGS-visible state at the time of the chain (gap offsets, residues modulo 30, chamber state, etc.).

2.  **Frontier Mining**: Identify the maximum divisor witness required across all false chain nodes for each step. This is the "least-factor frontier" you mentioned. The question is whether this maximum `w_max` can be bounded by a function of PGS-visible parameters, such as:
    - The input prime `p` or its logarithm.
    - The seed offset or the gap from the input prime to the seed.
    - The residue classes of the nodes in the chain.
    - The local density of semiprime shadows.

3.  **Invariant Search**: Look for a deterministic expression `H(p, s0, chain_state)` that consistently exceeds the observed `w_max` but is significantly smaller than `sqrt(q)`. The expression must be computable from PGS-visible information only, without performing full divisor tests.

### 4. Expected Outcomes and Implications
Based on your falsifying and confirming results:

- **Falsifying Outcome**: If the required horizon unavoidably tracks `sqrt(q)` for some cases, with no smaller PGS-visible bound, then the bridge is operationally good but not compressible into a pure local PGS rule at the current `candidate_bound=128`. The generator would retain its deterministic fallback for those cases, and the non-PGS portion would remain.

- **Confirming Outcome**: If the required horizon is bounded by a much smaller, PGS-visible expression (e.g., a function of the seed gap, residue, or a logarithmic term of `p`), this would be the missing theorem. It would convert the high-scale non-PGS portion (`56.63%` at `10^15` and `58.00%` at `10^18`) into PGS-derived output, sharply reducing or eliminating the bridge.

### 5. Next Steps in the Repository
The code already contains the instrumentation needed for this mining in `chain_horizon_closure_result`. The function returns `chain_horizon_closure_witnesses`, which records the divisor witnesses for closed nodes. By running the generator in a diagnostic mode that collects these witnesses alongside PGS state, you can gather the data to test the hypothesis.

The result of this analysis will determine whether the `chain_horizon_closure` can indeed be turned into a pure PGS next-prime selection rule, fulfilling the generator's design philosophy.
