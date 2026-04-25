# Executive Summary: PGS Prime Generator

## Purpose

The PGS Prime Generator implements a deterministic architecture for inferring prime boundaries from Prime Gap Structure (PGS) analysis. It generates PGS-inferred primes from anchor primes by applying Gap Winner Rule (GWR), Divisor Normalized Inference (DNI), raw-Z/log-Z scoring, divisor class dominance, absorption locks, carrier-locked pressure ceilings, and no-later-simpler-composite closure. The generator locates the next prime boundary inside the composite gap chamber without invoking Miller-Rabin, trial division, sieves, or any classical primality testing during the inference phase. Classical validation occurs externally post-emission to audit outputs.

## Core Idea

Traditional prime generation tests candidates for primality. The PGS Prime Generator inverts this: given a known anchor prime \(p\) and the deterministic arithmetic structure of the subsequent composite gap interior \(I = \{p+1, \dots, q-1\}\), it infers the right boundary \(q\) where PGS rules force uniqueness. The raw-Z score defines carrier dominance:

\[
Z_{\mathrm{raw}}(n) = n^{1 - d(n)/2}, \quad L(n) = \ln Z_{\mathrm{raw}}(n) = \left(1 - \frac{d(n)}{2}\right) \ln n
\]

where \(d(n)\) is the divisor count. GWR selects the leftmost minimum-\(d(n)\) carrier as the log-Z argmax. Inference proceeds via exclusion of composites, resolution of survivors, and dominance rules ensuring no later lower-divisor threat \(T_<(w)\) overtakes the winner carrier \(w\) before boundary closure.

## Architecture

The architecture comprises four layers:

1. **Anchor Layer**: Accepts a known prime \(p\) from external seeds or prior emissions.
2. **PGS Inference Layer**: Scans candidate chambers up to a bound (e.g., 128), applies exclusion rules (positive composite witnesses, interior open unclosed), carrier locks (higher-divisor pressure before threat), absorption (resolved boundary lock separator, unresolved alternatives closure), and ceilings (carrier-locked pressure). Resolves unique survivors via dominance.
3. **Emission Layer**: Outputs PGS-inferred prime \(q_{\hat{}}\) with metadata: anchor \(p\), gap width, winner carrier \(w\), offset, \(d(w)\), threat margin \(T_<(w) - q_{\hat{}}\), rule set (e.g., 005A-R), inference status.
4. **External Validation Layer**: Applies SymPy `isprime`, Miller-Rabin, or ECPP post-emission. Reports confirmed/inferred counts without feedback to generation.

Modes include pure inference (no validation), audit (post-generation check), and debug (diagnostic only).

## Key Rules

- **Gap Winner Rule (GWR)**: The gap interior log-Z argmax is the leftmost minimum-divisor carrier. Proved via hierarchical local dominator theorem and lexicographic raw-Z dominance over exact surfaces to \(10^{12}\).
- **Divisor Normalized Inference (DNI)**: Structures chamber via wheel-open admissibility and divisor ladders (known-composite only).
- **No-Later-Simpler-Composite Closure**: Post-GWR carrier \(w\), the boundary precedes any \(m > w\) with \(d(m) < d(w)\).
- **Boundary Law 005A-R**: Activates on higher-divisor pressure lock without single-hole positive witness closure. Excludes candidates via carrier-locked ceilings (unresolved alternatives before threat) and absorption. Refinement drops non-unique activations, retains 36 unique successes.
- **Absorption Locks**: Higher-divisor pressure locked absorption rejects false resolved survivors; resolved boundary lock separator prunes via pressure dominance.
- **Pressure Ceilings**: Carrier lock if higher-divisor/semiprime pressure holds before threat \(T\).

All rules use PGS-native observables: divisor counts via bounded scan, no primality oracles.

## Milestones

- **Milestone 1A**: Offline PGS certificate emitter produces 36 boundary certificates via composite exclusion probe, confirming interior closure and GWR winners.
- **Milestone 1B**: Experimental PGS prime emitter under 005A-R emits 36 PGS-inferred primes from anchor 11, with 100% unique resolution and zero wrongs on surfaces 11–1,100,000 (candidate-bound 128, witness-bound 127).

Milestone 0 scaffold enforces purity via forbidden-dependency gate, failing closed on `BOUNDARY_LAW_UNAVAILABLE`.

## Current Status

The generator achieves experimental readiness. Pure mode emits JSONL traces and summaries with LF endings. Tests validate 36/36 audited inferences on origin surfaces; shifted windows (100k–200k, 1M–1.1M) safe-abstain with zero activations/wrongs. Boundary Law 005A-R passes hardening gates: zero wrongs, absorption safe, unique successes preserved. Production emission forbidden; classical audit mandatory. Purity enforced: no `nextprime`, `isprime`, sieves in inference.

## Experimental Results

- **Composite Exclusion Probe**: On 11–1M, average rejected 20.4/candidate-bound-64; unique resolved survivors 48% true boundaries pre-005A-R.
- **005A-R Refinement**: 48 activations → 36 selected (unique successes), 12 dropped (non-unique); zero wrongs, 114k safe abstains.
- **Higher-Divisor Lock Hardening**: 1M anchors, zero unsafe absorptions; action population matches hardening profile.
- **Carrier Lock Probes**: Unresolved-alternatives-before-threat predicate separates safe ceilings (true boundary pre-\(T\)) from resets.
- **Forensics**: Zero true-boundary rejections; single-hole closures resolve 12% unresolved; pressure states show zero-collision candidates (e.g., square_pressure_state).
- **Audit**: 36/36 confirmed via SymPy on 005A-R emissions.

Surfaces: exact consecutive to 1M+, spot checks to 1.1M.

## Non-Goals

- Cryptographic certification without external validation.
- Miller-Rabin/sieve replacement.
- Probabilistic filtering or randomization.
- Factorization or RSA breaking.
- Infinite-scale unconditional inference (bounds explicit).
- Widening to non-PGS rules without user request.

## Implications for Prime Generation and Crypto Prefiltering

PGS inference reframes generation as structural prediction, decoupling proposal from proof. For prime generation, it yields auditable traces explaining *why* \(q_{\hat{}}\) via carrier dominance/threat margins, enabling research into gap anatomy. In crypto prefiltering, deterministic rejection of 91% composites (per geodesic prefilter baseline) combines with inference for hybrid pipelines: PGS proposes survivors, Miller-Rabin confirms. End-to-end speedups potential (2x+ observed in related benchmarks) by minimizing probable-prime tests. Security: validated primes indistinguishable from classical; inference accelerates keygen without weakening proofs.

## Future Roadmap

1. Integrate 005A-R into pure MVP: emit from 11, target 10k consecutive confirmed.
2. Harden carrier locks: audit previous-chamber reset vs. shift on 10M surface.
3. Compress states: deploy zero-collision vectors (multiplicity_pressure_histogram) for finite-state engine.
4. Scale benchmarks: 10^7 exact walk, large-anchor spots (10^12+).
5. Theorem bridge: prove PGS chamber → unique boundary via threat-margin closure.
6. Ports: Java/C parity with Python vectors.
7. Deployment: Hybrid prefilter+generator for RSA keygen, measured vs. OpenSSL.
