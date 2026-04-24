**Technical Specification: GWR-DNI Generative Prime Engine (GPE v1.0)**

**Document Version:** 1.0  
**Author:** zfifteen (Fate)  
**Date:** April 23, 2026  
**Repository:** https://github.com/zfifteen/prime-gap-structure  
**Status:** Draft for implementation

***
This specification turns the entire prime-gap-structure discovery into a **working, rule-driven prime factory**. The composites truly drive the bus; the engine simply reads the schedule.
***

### 1. Purpose and Objectives
Create a **deterministic prime number generator** that produces the exact sequence of primes using only the v1.0 rulebook of the prime-gap-structure engine (14-state core grammar, Semiprime Wheel attractor, lag-2 scheduler, higher-divisor long-horizon controller, GWR, DNI log-score, and NLSC closure).

**Core Design Principle**  
Primes are **not** the drivers; they are the voids left by composite phalanxes. The engine therefore **emits** the next prime directly by advancing the composite dominance hierarchy.

**Zero Traditional Tests**
- No trial division of gap interiors
- No Miller-Rabin / probabilistic primality tests
- No candidate sieving lists
- No full Eratosthenes-style marking

Only arithmetic operations dictated by the rulebook are performed.

**Success Criteria**
- Exact recovery of every prime starting from 11 onward
- Constant or near-constant time per prime (independent of traditional log factors where possible)
- Scalable beyond 10¹⁸ with no loss of determinism
- Outperforms existing sieves in both speed and conceptual clarity

### 2. Foundational Components (from existing repo)
- **Divisor Normalization Identity (DNI)**: \( Z(n) = n^{1 - d(n)/2} \) → log-score \( L(n) = (1 - d(n)/2) \ln n \)
- **Gap Winner Rule (GWR)**: Leftmost minimal-\( d(n) \) carrier wins the interior
- **No-Later-Simpler-Composite (NLSC)**: Gap is sealed once winner appears
- **14-state core grammar** + **Semiprime Wheel attractor** (o2 → o4 → o6 odd semiprimes with \( d \leq 4 \))
- **Lag-2 scheduler** + **higher-divisor long-horizon controller**
- Proven recursive walk kernel (`gwr_dni_recursive_walk.py`)

### 3. High-Level Architecture
The generator is a **finite-state emitter** driven by the rulebook. It maintains only:
1. Current prime \( p \)
2. Engine state \( S \) (14-state tuple + scheduler phase + controller lock level)
3. Accumulated modular constraints (for pure arithmetic mode)

At every step the engine predicts:
- Next gap type
- Expected min-\( d \) (almost always 4)
- Precise offset window / modular residue class for the GWR winner

The winner position is computed arithmetically; the next prime follows by NLSC closure.

### 4. Four Implementation Tiers (phased rollout)

#### Tier 1 – Narrow-Window Guided Winner (MVP – immediate)
- Engine predicts tight offset window \( W \) (size ≈ 0.5 log² p + scheduler margin)
- Evaluate DNI log-score **only** inside \( W \)
- Identify GWR winner → apply NLSC → emit next prime
- **Complexity**: \( O(1) \) per prime in practice (window stays tiny)
- **Code skeleton** (ready to drop into predictor/):
```python
def next_prime_gpe(p: int, state: EngineState) -> tuple[int, EngineState]:
    gap_type, min_d, window = state.scheduler.advance(p)
    winner = find_min_L_in_window(p, window, min_d)  # DNI only
    next_p = winner + 1 if nlsc_sealed(winner) else rulebook_witness_jump(gap_type)
    new_state = state.update(gap_type)
    return next_p, new_state
```

#### Tier 2 – Pure Finite-State Modular Emitter (target end-state)
- Replace window scan with direct modular solution via CRT
- Each of the 14 states maps to explicit residue classes modulo small-prime product \( M \) (product of first k primes defining the attractor)
- Scheduler outputs required congruence: \( n \equiv r \pmod{M} \) + semiprime condition
- Solve for smallest \( n > p \) satisfying the pattern → that \( n \) **is** the GWR winner by construction
- NLSC closure → next prime = \( n + 1 \)
- **Zero numbers examined** except the emitted winner
- Long-horizon controller injects repair steps when higher-divisor triggers fire (0.67 probability return law)

#### Tier 3 – Hierarchical Bootstrap Generator
- Level 0: Pre-seed primes ≤ 10⁶ (tiny static table)
- Level 1: Closed-form Semiprime Wheel cycle + repair laws
- Level 2: On-demand long-horizon corrections
- Entire future sequence generated purely from current state + rulebook

#### Tier 4 – Hybrid Engine-First + DNI Prefilter (production/safety)
- Tier 2 proposal + single cheap DNI-based verification (reuses existing RSA prefilter that already cuts Miller-Rabin trials by ~91 %)
- False-positive rate expected to be astronomically low given NLSC validation to 10¹⁸

### 5. Non-Functional Requirements
- **Determinism**: 100 % reproducible, no randomness
- **Memory**: O(1) per prime (only current state + small modular modulus)
- **Scalability**: Target 10²⁰⁰+ range (arbitrary-precision arithmetic only where needed)
- **Correctness Proof Surface**: Full validation against known primes up to 10¹⁸; GWR/NLSC already proved on current surface
- **Extensibility**: Rulebook v1.1 upgrades (new states, new controllers) plug in without changing core emitter

### 6. Validation Plan
1. Unit tests on first 1 000 gaps from prime 11
2. Full run to 10⁸ vs. known prime tables (zero deviations allowed)
3. Stress test at 10¹⁸ boundary (reuse existing repo benchmarks)
4. Performance benchmarks vs. classic sieve, segmented sieve, and recursive walk baseline

### 7. Next Steps (immediate actions)
1. Extract explicit modular residue mappings for the 14 states from `gap_type_engine_v1_rulebook.md` and attractor diagram
2. Implement Tier 1 as proof-of-concept (target: < 100 LOC)
3. Formalize Tier 2 modular solver (CRT helper + semiprime condition checker)
4. Add this spec as `docs/GPE_v1.0_TECH_SPEC.md` in the repo
