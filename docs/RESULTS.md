# Results Map

The README tells the story from the smallest visible facts: one prime, the composites after it, the divisor counts inside the gap, and the next prime at the first later divisor count of `2`.

This document is the map of what the repository currently carries.

It keeps three states separate:

- theorem results proved in `PROOF.md`
- generator and model surfaces validated by audit or measurement
- empirical or legacy engineering results whose scope is exactly the tested regime

## Claim language and the mandatory `10^18` surface

Program policy (canonical: root `AGENTS.md` **Mandatory 10^18 Evidence Surface**;
short rule: `.grok/rules/pgs-10e18-evidence-surface.md`):

- **Theorem rows** in this map remain theorem under `PROOF.md` hypotheses and
  finite premises. They are not bounded by finite implementation ladders.
- **Validated / verified** language for generator, walk, probe, or audit
  implementation claims requires an **executed** surface at magnitude `10^18`
  in the same evidence package. The production generator reference form is the
  decade ladder `10^8` through `10^18` (256 primes per decade; 2816 primes on
  the committed surface).
- Surfaces that stop below `10^18` may still be reported as measured on their
  exact regime. They must not be summarized as program-level verified or
  validated.
- A `10^18` measured or audit pass is implementation evidence. It does not by
  itself prove RH, PNT, or RSA-scale claims.

## Proved Theorem Foundation

The formal proof reference is [PROOF.md](PROOF.md).

It states and proves the direct deterministic next-prime theorem: given a known prime `p`, exact divisor counts determine the next prime `q`.

It also proves the prime-gap maximizer theorem: inside any prime gap with a nonempty interior, the comparison function `F(n)` is maximized exactly at the leftmost interior integer with minimum divisor count. In zero-excess coordinates, `F(n)=-E(n)`, so the same theorem says that this integer is the leftmost minimum-excess interior integer.

It proves universal bounded compression (2026-07-05): for every consecutive prime gap with nonempty interior, the GWR-selected witness `w` satisfies `w - p <= max(64, ceil(0.5 * log(q)^2))`. The Prime-Square Proximity Theorem closes the square branch at Cramér scale via near-root exclusion and modulus-link collision. This is a proved bound on the selected-witness offset; it does not by itself prove RH, PNT, or every classical formulation of Cramér's conjecture for raw gap size `q - p`.

These are universal theorems. The finite verification surfaces are exhaustive for the stated ranges and complete the proofs. Audit tables record provenance.

## PGS-To-RH Reading Path

For the PGS-to-RH argument, read [docs/rh](docs/rh/README.md). That bundle
reads the proved local theorem foundation through exact DNI-to-zeta compression,
with bridge coordinate `H(n)=log n+E(n)`, and the remaining
source-to-spectral placement target:

```text
divisor counts -> PGS local theorems -> DNI-to-zeta compression
-> source-to-spectral placement target -> pole placement/RH sentence
```

`PROOF.md` controls the local PGS theorem status. It does not itself prove RH.
`docs/rh` carries the RH reading path built on that source layer and records
the current obstruction to the no-extra-carrier residual route.

## PGS Prime Generator

The prime generator turns the interval story into an output record:

```json
{"p": 89, "q": 97}
```

The generator outputs exactly `p` and `q` for each given prime `p`. Diagnostics, source labels, verification records, and audit results stay outside the outputted stream.

Unlike a conventional prime generator, it selects the successor prime from deterministic prime-gap-structure chamber state. Generation excludes trial division, Miller-Rabin, probabilistic primality tests, sieve-based prime generation, fallback prime search, and `nextprime` inside generation.

The current production path has `9588 / 9588` exact PGS outputs with `0` failures on `11..100000`, and `2816 / 2816` exact PGS outputs with `0` incorrect candidates on the `10^8` through `10^18` decade-window validation surface.

## Divisor Normalization Identity

The preferred Divisor Normalization Identity coordinate is zero excess:

$$E(n)=\left(\frac{d(n)}{2}-1\right)\log n$$

For every integer `n > 1`, primes are exactly the zero-excess integers. The
dual coordinate remains:

$$Z(n)=n^{1-d(n)/2}$$

Equivalently, `Z(n)=e^{-E(n)}`. This is an exact coordinate reformulation, not
a new theorem. It supplies the fixed prime-centered score foundation behind the
selected-composite comparison: minimizing `E(n)` is the same selection as
maximizing `Z(n)` or maximizing `F(n)=-E(n)`.

## Reduced Gap-Type Model

The Prime Gap Generative Model v1.0 studies the persistent reduced gap-type surface, not the full raw gap-size sequence as a theorem.

On that reduced surface, the type stream closes to a persistent `14`-state core.

The dominant dynamical object is the Semiprime Wheel Attractor:

- `o2_odd_semiprime|d<=4`
- `o4_odd_semiprime|d<=4`
- `o6_odd_semiprime|d<=4`

The frozen `v1.0` model combines a `14`-state core grammar, a transition-rule layer, and a higher-divisor-triggered long-horizon controller.

Reference operating profiles:

- local fidelity: pooled-window concentration L1 `0.0116`
- balanced operating profile: pooled-window concentration L1 `0.0150`, full-walk three-step concentration `0.5564`
- long-horizon study: full-walk three-step concentration `0.6278`

## Recursive Walk and Closure

The exact recursive walk repeats the direct divisor-count next-prime step from prime to prime.

On the current verified surface, the transition rule is exact on `743,075 / 743,075` rows from the combined $10^6 + 10^7$ next-gap surface, and the recursive walk records `664,578 / 664,578` exact consecutive next-prime recoveries from prime `11` through prime `10,000,121` with `0` skipped gaps. The sampled decade ladder from $10^2$ through $10^18$ also stayed at exact hit rate `1.0` with `0` skipped gaps across `860` measured recursive steps.

The No-Later-Simpler-Composite condition says that once the GWR-selected integer appears, no later interior composite with strictly smaller divisor count precedes the next prime. This is an exact corollary of the proved GWR theorem. The separate stress surface through `10^18` records zero observed violations.

## Bounded Compression (Proved)

Universal bounded compression is proved in [PROOF.md](PROOF.md) (2026-07-05). For every consecutive prime gap with nonempty interior, the GWR-selected witness `w` satisfies

```text
w - p <= C(q) = max(64, ceil(0.5 * log(q)^2))
```

This bound sits at the Cramér scale, the same `(log q)^2` envelope as Cramér's conjecture. It is established deterministically from divisor-count invariants, not probabilistic models.

Closure components:

- **Finite base** (`q < e^16`): max selected-witness offset `60` (proved)
- **Residual K=128 elimination**: odd-adjacent high-τ witness branches (proved under stated hypotheses)
- **Prime-Square Proximity Theorem**: square branch `r^2 - p <= C(q)` (proved 2026-07-05)

**Boundary.** This bounds the selected-witness offset `w - p`. It does not by itself prove RH, PNT, or every classical formulation of Cramér's conjecture for raw gap size `q - p`. A Lean 4 formalization is in progress as a machine-checked mirror.

**Audit corroboration** (not proof boundaries): square-branch falsification sweeps remain clean through tested regimes. For example, prime roots `300M` to `400M` with `5,084,001` tested yielded no counterexample and a max utilization of `0.70`.

The old fixed cutoff theorem `{2:44, 4:60, 6:60}` is false and invalidated. It fails at `q = 24,098,209`, where the square branch gives `E(q) = 72 > 60`.

Under square exclusion, the GWR-selected integer is exactly the first interior integer with `d(n)=4`. This is exact on full scans through `2x10^7`.

## Falsified interpretive claims (measured)

These rows record killed interpretive extensions of proved local structure. They do not demote theorems in `PROOF.md`.

| Date | Claim | Status | Regime / evidence |
| --- | --- | --- | --- |
| 2026-07-24 | Residual-mean elevation after Gap Winner: mean `tau` on residual `(w, q)` strictly exceeds mean `tau` on pre-valve `(p, w)` for every both-sided nonempty gap (and residual/pre ratio increases with `tau(w)`) | **Falsified** (H1 and H2). About 60–64% of eligible gaps reverse on mid-scale surfaces. NLS undercuts remain 0. | `p ≤ 2e6`; package `experiments/gap-winner-one-way-complexity-valve-falsification-2026-07/` |
| 2026-07-25 | Unique Floor Dichotomy U2: among gaps with min-\(\tau\) floor \(m=4\) and length \(g \ge 20\), multi-tie rate \(\lvert L\rvert \ge 2\) is at least \(0.99\) (long non-square corridors almost surely multi-tie) | **Falsified** on the executed decade ladder. Multi rate \(0.9429\) (\(1421/1507\)). Mid-scale consecutive \(p \le 10^7\) still held U2; the high-scale ladder kills it. U1/U3 not falsified under stated ceilings on that ladder. | Decade ladder \(10^8..10^{18}\), 256 primes/decade (2805 gaps) plus mid-scale consecutive; package `experiments/unique-floor-dichotomy-falsification-2026-07/` |

Truncation of residual search for lower-complexity certificates continues to rest on GWR, No-Later-Simpler-Composite, and bounded compression alone. It does not require residual mean elevation, dual right-pin as a hard certificate, or near-certain multi-tie on every moderate-length semiprime floor.

## Legacy Prefilter

The Z-band cryptographic prefilter is a legacy validated artifact and a downstream engineering use of the normalization program.

Its public surface includes `CDLPrimeGeodesicPrefilter`, `generate_prime`, `generate_rsa_prime`, `FIXED_POINT_V`, `DEFAULT_MR_BASES`, `proxy_z()`, and `is_prime_candidate()`.

In that legacy path, `proxy_z = 1.0` means the candidate survived the current gated factor tables and advances to Miller-Rabin. It is not a primality proof by itself.

Empirical benchmark surfaces include:

- $2.09\times$ end-to-end speedup across $300$ deterministic $2048$-bit RSA keypairs
- $2.82\times$ end-to-end speedup across $50$ deterministic $4096$-bit RSA keypairs
- $90.97\,\%$ to $91.07\,\%$ Miller-Rabin reduction in the current covered-table configuration

## RSA Endpoint Structure Law

RSA moduli do expose deterministic endpoint structure. The live RSA v2 law is
reciprocal deadline-signature correction plus oriented endpoint-chain closure,
a public PGS endpoint-class resolver.

On the current committed RSA ladder:

- `rsa_v2_40bit_static_001`: public reciprocal deadline-signature correction
  resolves the endpoint class as `(1048559, 1048589)`.
- `rsa_v2_50bit_static_001`: V2 residual path remained unresolved under joint cell
  `C1T2L1`. V3 carrier reciprocal closure (2026-08-07) finds the public pair
  `(32047633, 32059651)` with `N//L == U` and `N//U == L`, remainder 6170868,
  `delta_c = 30 ≤ boundD = 45`, deadline=tail signatures match, historical false
  class blocked. Emitted under `resolved_by = carrier_reciprocal_closure` and
  `closure_status = endpoint_class_by_reciprocal_deadline_signature_correction`.
  Status: **measured-on-regime-only / hypothesis**. Not a theorem. Not a
  factorisation claim. First-tail window fixed at `[-12, 6]`.
- `rsa_v2_64bit_static_001`: public mutual certificate closure resolves the
  endpoint class as `(3221225473, 3221275501)`.

**Residual code history (measured, not theorem):**

| Layer | 50-bit residual / resolve path |
| --- | --- |
| RSA v2 refined runner pin | `unresolved_by_reciprocal_carrier_misalignment` |
| rsa-v3 after dual-gap D | `unresolved_by_first_tail_misalignment` |
| rsa-v3 joint residual cell R | `unresolved_by_joint_cell_C1T2L1` (R = (1,2,1), pinch_S = 54) |
| rsa-v3 V3 carrier reciprocal (2026-08-07) | `resolved_by_carrier_reciprocal_closure` → endpoint class `[32047633, 32059651]` |

40/64-bit resolve under public rules. 50-bit now has a measured reciprocal
candidate under the same closure_status used by the 40-bit golden. Historical
false class `(32047651, 32059633)` stays anti-admitted. Residual-map status for
dual-gap D and cell R remains **hypothesis**. Packages:
`research/06-cryptology-rsa/experiments/live-solver/rsa-v3/residual_discriminator_v2/`,
`.../output/DOCUMENTATION_LOCK_50BIT_V3.md`,
`.../output/residual_discriminator_v3_resolve_report.html`.

This is a measured RSA endpoint-structure result, not a universal RSA-scale
theorem. Audit confirms the exact 40-bit and 64-bit factor pairs after public
inference. The 50-bit V3 path is a public reciprocal floor pair, not a claim of
integer factorisation. Audit does not define the inference rule.

Reference document:
`research/06-cryptology-rsa/docs/endpoint_structure_law.md`.

## Links Into The Repository

- [docs/core/LEFTMOST_MINIMUM_DIVISOR_RULE.md](docs/core/LEFTMOST_MINIMUM_DIVISOR_RULE.md) explains the selected composite.
- [docs/core/DIVISOR_NORMALIZATION_IDENTITY.md](docs/core/DIVISOR_NORMALIZATION_IDENTITY.md) explains zero excess and the dual fixed prime-centered score.
- [docs/rh](docs/rh/README.md) gives the PGS-to-RH reading path and status ledger.
- [docs/PRIME_GAP_GENERATOR.md](docs/PRIME_GAP_GENERATOR.md) explains the minimal `{"p": ..., "q": ...}` generator.
- [docs/core/PRIME_GAP_GENERATIVE_MODEL.md](docs/core/PRIME_GAP_GENERATIVE_MODEL.md) explains the reduced gap-type model.
- [docs/core/RECURSIVE_PRIME_WALK.md](docs/core/RECURSIVE_PRIME_WALK.md) explains the recursive walk, closure condition, cutoff falsification, and dominant `d=4` regime.
- [experiments/gap-winner-one-way-complexity-valve-falsification-2026-07/](../experiments/gap-winner-one-way-complexity-valve-falsification-2026-07/) records the mid-scale falsification of residual-mean elevation after the Gap Winner.
- [experiments/unique-floor-dichotomy-falsification-2026-07/](../experiments/unique-floor-dichotomy-falsification-2026-07/) records unique-floor U2 falsification on the \(10^8..10^{18}\) decade ladder (U1/U3 still hold under stated ceilings on that surface).
