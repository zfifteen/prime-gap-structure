# Prime Gap Structure

![Prime Gap Structure hero](docs/assets/prime-gap-structure-hero.jpg)

This repository now carries three major prime-gap results:

- a proved local arithmetic selection law inside prime gaps;
- a frozen hierarchical finite-state engine for reduced prime-gap types.
- a Prime-Gap Inference Generator that infers the successor prime from the
  arithmetic structure of the interval after a given prime, instead of scanning
  candidates until a primality test succeeds.

Take the consecutive primes `23` and `29`. The integers between them are
`24, 25, 26, 27, 28`. Their divisor counts are:

- `d(24) = 8`
- `d(25) = 3`
- `d(26) = 4`
- `d(27) = 4`
- `d(28) = 6`

So `25` wins this gap because it has the smallest divisor count present.

Now take `89` and `97`. The interior integers are
`90, 91, 92, 93, 94, 95, 96`. Their divisor counts are:

- `d(90) = 12`
- `d(91) = 4`
- `d(92) = 6`
- `d(93) = 4`
- `d(94) = 4`
- `d(95) = 4`
- `d(96) = 12`

Here the smallest divisor count present is `4`, and the leftmost integer with
that divisor count is `91`, so `91` wins.

These examples show the local arithmetic choice that anchors the repository.

## Three Headline Results

- **Gap Winner Rule (GWR):** on the repository's current proof surface, the
  implemented divisor-normalization score picks exactly the leftmost interior
  integer with minimum divisor count in every prime gap.
- **Prime Gap Generative Engine v1.0:** on the persistent reduced gap-type
  surface, prime-gap types close to a frozen hierarchical finite-state engine
  with a stable `14`-state core.
- **Prime-Gap Inference Generator:** the generator emits one two-field
  `{"p": ..., "q": ...}` record per given prime `p`, keeps diagnostics outside
  the emitted stream, and selects the successor prime `q` from the arithmetic
  consistency of the interval after `p`, rather than by a conventional
  next-prime search. The current production iteration is `v1.1`.

## Gap Winner Rule

The **Gap Winner Rule (GWR)** says:

1. inside a prime gap, find the smallest divisor count present among the
   interior composites;
2. if more than one interior composite has that divisor count, take the
   leftmost one.

That chosen interior integer is the selected integer of the gap.

The headline mathematical result carried by the repository is that the
implemented divisor-normalization score picks exactly that same integer in
every prime gap. The theorem statement is
[Gap Winner Rule — Hierarchical Local-Dominator Law](gwr/findings/gwr_hierarchical_local_dominator_theorem.md),
and the proof surface is summarized in [GWR_PROOF.md](GWR_PROOF.md).

## Prime Gap Generative Engine v1.0

The second headline result in the repository is the frozen engine on the
persistent reduced gap-type surface. This is a result about the persistent
reduced gap-type surface, not yet a theorem about the full raw gap-size
sequence.

On that reduced surface, the type stream closes to a persistent `14`-state
core. Its dominant dynamical object is the **Semiprime Wheel Attractor**:

- `o2_odd_semiprime|d<=4`
- `o4_odd_semiprime|d<=4`
- `o6_odd_semiprime|d<=4`

The frozen `v1.0` engine has three layers:

1. core grammar;
2. scheduler;
3. higher-divisor-triggered long-horizon controller.

Its reference operating profiles are:

- local fidelity: pooled-window concentration L1 `0.0116`
- balanced frontier: pooled-window concentration L1 `0.0150`,
  full-walk three-step concentration `0.5564`
- long-horizon study: full-walk three-step concentration `0.6278`

See also:

- [Prime Gap Generative Engine v1.0 release note](docs/releases/prime_gap_generative_engine_v1_0.md)
- [Gap-type engine v1.0 freeze note](gwr/findings/gap_type_engine_v1_freeze.md)
- [Gap-type engine v1.0 rulebook](gwr/findings/gap_type_engine_v1_rulebook.md)
- [Hierarchical engine paper draft](docs/research/predictor/prime_gap_hierarchical_engine_paper_draft.md)
- [Engine overview figure](output/gwr_dni_gap_type_engine_v1_overview.png)

## Prime-Gap Inference Generator

The third headline result is the Prime-Gap Inference Generator. It emits one
record for each given prime:

```json
{"p": 89, "q": 97}
```

The emitted stream is deliberately small: exactly `p` and `q`. Source labels,
diagnostics, certificates, and audit results stay outside the generator output.

The current production iteration is
[PGS Inference Generator v1.1](docs/releases/pgs_inference_generator_v1_1_pgs_only.md).

Conventional prime generation works by scanning candidate numbers and testing
them until one proves prime. The Prime-Gap Inference Generator is different. It
starts from a given prime `p`, examines a finite interval to the right of `p`,
and uses the composite numbers in that interval to infer the successor prime
`q`.

The generator treats the gap as a consistency problem:

```text
Which candidate q leaves a valid prime gap interval after p?
```

The key structural discovery is that once the first candidate `q` is forced by
the interval to its left, later candidates are no longer possible successors of
the original `p`. They belong to intervals that begin after `q`. That
distinction turned the remaining not-yet-excluded candidates into evidence
that the gap had already closed.

The generator is now PGS-only. The production generator contains no trial
division and no fallback prime search. Probabilistic primality tests,
Miller-Rabin, sieves, and oracle-style `nextprime` calls are also excluded from
generation. Classical validation remains downstream audit after emission.

On the current production generator surface, exact emission is preserved and the
PGS selector applies exact divisor-count GWR/NLSC chamber-reset state:

```text
surface: 11..100000
candidate interval width: 128
primes tested: 9588
PGS-labeled emissions: 9588
failed emissions: 0
incorrect candidates: 0
coverage: 100.00%
```

The same production selector now reproduces the high-scale decade-window
surface through `10^18`:

```text
surface: 256 consecutive primes per decade, 10^8 through 10^18
candidate interval width: 1024
primes tested: 2816
exact matches: 2816
undecided cases: 0
incorrect candidates: 0
search-window misses: 0
coverage: 100.00%
```

The implementation contract and lower-level mechanism are recorded in
[Generator Logic Specification](docs/specs/prime-gen/minimal_pgs_generator_logic.md).
The current release note is
[PGS Inference Generator v1.1](docs/releases/pgs_inference_generator_v1_1_pgs_only.md).
The detailed technical note is the
[logic-engine report](docs/research/prime_inference_generator/rule_x_consistency_collapse_logic_engine.md),
and the high-scale validation report is
[Decade-Window Validation Report](experiments/rule_x_logic_engine/chamber_reset_decade_ladder_1e8_1e18_a256_b1024/report.md).

## Why The Score Exists

The score exists because the repo wants one number per interior composite, so a
whole gap can be compared as a single ordered field rather than as a list of
cases.

Divisor count already tells part of the story: fewer divisors means less
factor structure. But divisor count alone does not give one scalar quantity for
the whole gap, and it does not explain what the selected integer is winning relative to.

The divisor-normalization program builds that scalar by using primes as the
reference class. Its purpose is to answer one concrete question:

> Which composite in the gap comes closest to the prime baseline?

The normalization is built so that every prime lands at the same fixed point,
`Z = 1.0`, while composites fall below that point. That makes the selected integer easy
to interpret: it is the interior composite closest to the prime fixed point
under the normalization.

The raw quantity is

$$
Z_{\mathrm{raw}}(n) = n^{1 - d(n)/2}
$$

and the implementation compares interiors using its logarithm

$$
L(n) = \ln Z_{\mathrm{raw}}(n) = \left(1 - \frac{d(n)}{2}\right)\ln(n).
$$

Maximizing `Z_raw(n)` and maximizing `L(n)` pick the same selected integer. The score is
there to turn the gap interior into one exact competition, not to decorate the
rule with jargon.

## What This Repository Carries

This repository now carries three visible lines of work:

- the proved GWR theorem and its proof surface;
- the reduced gap-type engine and pattern results on the persistent reduced
  surface;
- the Prime-Gap Inference Generator and downstream deterministic DNI-based
  predictor and prefilter work.

The GWR theorem remains the theorem foundation. The gap-type engine is the second
headline prime-gap result. The Prime-Gap Inference Generator is the current
operational inferred-prime generator milestone. The recursive walk and
deterministic filter are downstream deterministic instruments built from the
same normalization.

## Novel Structures in This Repository

The repository now carries the following named structures and results:

- **Gap Winner Rule (GWR):** inside any prime gap, the log-score argmax is
  exactly the leftmost integer with minimum interior divisor count. On the
  repository's current proof surface, this is a proved universal prime-gap
  maximizer theorem summarized in [GWR_PROOF.md](GWR_PROOF.md) and recorded in
  [gwr/findings/gwr_hierarchical_local_dominator_theorem.md](gwr/findings/gwr_hierarchical_local_dominator_theorem.md).
- **Divisor Normalization Identity (DNI):** `Z(n) = n^(1 - d(n)/2)` is an
  exact arithmetic identity collapsing all primes to `Z = 1.0`.
- **Gap-type catalog / reduced state surface:** the repository defines a
  deterministic reduced gap-type surface and catalogs it through sampled
  windows to `10^18`, with a persistent `14`-state core on the settled
  high-scale surface. See
  [gwr/findings/gap_type_catalog_through_1e18.md](gwr/findings/gap_type_catalog_through_1e18.md)
  and
  [gwr/findings/gap_type_sequence_grammar_findings.md](gwr/findings/gap_type_sequence_grammar_findings.md).
- **Semiprime Wheel Attractor:** the triad
  `o2_odd_semiprime|d<=4`, `o4_odd_semiprime|d<=4`,
  `o6_odd_semiprime|d<=4` is the dominant dynamical object on the persistent
  reduced gap-type surface. See
  [gwr/findings/gap_type_engine_v1_freeze.md](gwr/findings/gap_type_engine_v1_freeze.md).
- **Hierarchical finite-state engine:** on the persistent reduced gap-type
  surface, the frozen `v1.0` engine combines a `14`-state core grammar, a
  scheduler layer, and a higher-divisor-triggered long-horizon controller. See
  [docs/releases/prime_gap_generative_engine_v1_0.md](docs/releases/prime_gap_generative_engine_v1_0.md)
  and
  [gwr/findings/gap_type_engine_v1_rulebook.md](gwr/findings/gap_type_engine_v1_rulebook.md).
- **Prime-Gap Inference Generator:** the generator emits exactly `p` and `q`
  for each given prime `p`, with downstream audit and source diagnostics
  outside the emitted stream. Unlike a conventional prime generator, it selects
  the successor prime from the arithmetic consistency of the interval after
  `p`, without a trial-division or fallback prime-search path inside the
  generator. The current production path has `9588 / 9588` exact PGS emissions
  with `0` failures on `11..100000`, and
  `2816 / 2816` exact PGS emissions with `0` incorrect candidates on the `10^8`
  through `10^18` decade-window validation surface.
- **No-Later-Simpler-Composite (NLSC) condition:** once the GWR-selected integer
  appears, no later interior composite with strictly smaller divisor count
  precedes the next prime. Zero violations observed through `10^18`.
- **Dominant d=4 arrival reduction:** under square exclusion, the GWR-selected integer
  is exactly the first interior integer with `d(n)=4`. Exact on full scans through
  `2x10^7`.
- **Dynamic cutoff conjecture:** `C(q) = max(64, ceil(0.5 * log(q)^2))` bounds
  the GWR-selected integer offset for the bounded walker. Empirically calibrated through
  `p <= 10^6`. The fixed map `{2:44, 4:60, 6:60}` is falsified at
  `q = 24,098,209`.

## Divisor Normalization Identity

The raw-$Z$ quantity exists because the repo wants a normalization in which the
entire prime class lands at one fixed point while composites fall below it.

The construction starts from the divisor normalization load

$$
\kappa(n) = \frac{d(n) \cdot \ln(n)}{e^{2}}
$$

and then passes that load through the Z-transform:

$$
Z(n) = \frac{n}{\exp(v \cdot \kappa(n))}
$$

where $v$ is the normalization scaling parameter.

For the prime-gap structure program in this repository, the distinguished value is

$$
v = \frac{e^{2}}{2}
$$

because it produces an exact cancellation. Substitute the Divisor Normalization Equation into the Z-transform:

$$
Z(n) = \frac{n}{\exp\left(v \cdot \frac{d(n) \cdot \ln(n)}{e^{2}}\right)}
$$

Now set $v = e^{2}/2$:

$$Z(n) = \frac{n}{\exp\left(\frac{e^{2}}{2} \cdot \frac{d(n) \cdot \ln(n)}{e^{2}}\right)}$$

$$Z(n) = \frac{n}{\exp\left(\frac{d(n)}{2} \cdot \ln(n)\right)}$$

$$Z(n) = \frac{n}{n^{d(n)/2}}$$

$$Z(n) = n^{1 - d(n)/2}$$

So the **Divisor Normalization Identity** (DNI) $Z(n) = n^{1 - d(n)/2}$ is

$$
Z(n) = n^{1 - d(n)/2}
$$

This has an immediate effect:

- Prime: $d(p) = 2$, so $Z(p) = 1$
- Semiprime with two distinct prime factors: $d(n) = 4$, so $Z(n) = 1/n$
- Composite in general: $d(n) > 2$, so $Z(n) < 1$

Under the exact DNI, the entire prime class collapses to the fixed-point locus $Z = 1.0$. Composites are pushed strictly below that locus.

This fixed-point collapse is the mathematical base of the repository. It is
the invariant behind both the prime-gap theorem and the downstream
deterministic filter.

## GWR Proof Surface

The central maximizer rule in this repository is that the log-score argmax inside
a prime gap collapses to a simpler arithmetic choice:

1. minimize the interior divisor count $d(n)$,
2. among ties, take the leftmost interior integer.

That is the Gap Winner Rule.

The formal theorem file expresses this as a hierarchical local-dominator law.
The proof is closed on the repository's current proof surface: ordered
dominance closes the later side, the local admissibility theorem closes the
earlier side, the residual-class closure artifacts discharge the former
low-class remainder, and the exact no-early-spoiler audits through
$p < 5 \times 10^9$ plus the square-adjacent stress surface at $10^{12}$
remain clean.

See [gwr/story/README.md](gwr/story/README.md),
[GWR_PROOF.md](GWR_PROOF.md),
[gwr/findings/gwr_hierarchical_local_dominator_theorem.md](gwr/findings/gwr_hierarchical_local_dominator_theorem.md),
[gwr/findings/gap_winner_rule.md](gwr/findings/gap_winner_rule.md), and
[gwr/findings/prime_gap_admissibility_theorem.md](gwr/findings/prime_gap_admissibility_theorem.md).

## Exact Recursive Prime Walk

The most jarring combined predictor result in the repository is this: once the
implemented score maximizer appears inside a prime gap, the next prime arrives before
any later interior composite with strictly smaller divisor count can appear.
That closure law is what lets the unbounded DNI/GWR walker recover the next
prime exactly from the ordered divisor structure of the next-gap interior.

Given a known prime `q`, the oracle scans divisor counts to the right until the
successor prime, takes the lexicographic minimum over the composite
interior, and recovers the next prime by the witness map. That mechanism is
exact by construction. No cutoff theorem is involved.

On the current verified surface, that mechanism supports an exact deterministic
no-skip sequential walk. The transition rule is exact on `743,075 / 743,075`
rows from the combined $10^6 + 10^7$ next-gap surface, and the recursive walk
records `664,578 / 664,578` exact consecutive next-prime recoveries from prime
`11` through prime `10,000,121` with `0` skipped gaps. The sampled decade
ladder from $10^2$ through $10^18$ also stayed at exact hit rate `1.0` with
`0` skipped gaps across `860` measured recursive steps.

The predictor note is documented in
[docs/research/predictor/gwr_dni_exact_recursive_prime_walk_note.md](docs/research/predictor/gwr_dni_exact_recursive_prime_walk_note.md),
and the live implementation is
[benchmarks/python/predictor/gwr_dni_recursive_walk.py](benchmarks/python/predictor/gwr_dni_recursive_walk.py).

![Exact DNI recursive-walk performance](docs/research/predictor/figures/gwr_dni_recursive_gap_scaling_performance.png)

## Dynamic Cutoff and Square-Branch Falsification

The old fixed cutoff theorem `{2:44, 4:60, 6:60}` is false. It fails at
`q = 24,098,209`, where the square branch gives `E(q) = 72 > 60`. The bounded
walker in the repo no longer treats that fixed map as live.

The current bounded compression is empirical:
`C(q) = max(64, ceil(0.5 * log(q)^2))`. Through the direct square-branch audit
at `p <= 10^6`, the repo tested `78,498` prime squares, found `7,477`
violations of the old fixed map, and observed maximum square offset `246`.
The compare mode in the recursive walker is the live falsification instrument:
it runs the bounded and unbounded walkers in lockstep and records any bounded
miss immediately.

See
[benchmarks/python/predictor/square_branch_gap_audit.py](benchmarks/python/predictor/square_branch_gap_audit.py),
[benchmarks/python/predictor/gwr_dni_recursive_walk.py](benchmarks/python/predictor/gwr_dni_recursive_walk.py),
and
[docs/research/predictor/gwr_dni_exact_recursive_prime_walk_note.md](docs/research/predictor/gwr_dni_exact_recursive_prime_walk_note.md).

## No-Later-Simpler-Composite

The strongest closure consequence currently documented in the repository is
this: once the implemented score maximizer appears inside a prime gap, the next prime
arrives before any later interior composite with strictly smaller divisor
count can appear.

This is the closure law behind the exact recursive walk. After the selected integer
appears, the gap interior does not later produce a simpler composite before
the next prime closes the interval.

In symbols, if $w$ is the implemented log-score maximizer in the gap $(p, q)$ and

$$
T_{<}(w) = \min \{\, n > w : d(n) < d(w) \,\},
$$

then the closure condition is

$$
q \le T_{<}(w).
$$

This is an exact corollary of the proved GWR theorem. The separate
question is whether it can stand on its own as a direct prime-gap theorem without
using GWR as the parent result. The current documented surface includes a
deterministic even-band ladder at every decade from $10^8$ through $10^{18}$
with zero observed violations.

See
[gwr/findings/closure_constraint_findings.md](gwr/findings/closure_constraint_findings.md),
[gwr/findings/claim_hierarchy.md](gwr/findings/claim_hierarchy.md),
and
[docs/current_headline_results.md](docs/current_headline_results.md).

## Dominant d=4 Reduction

In the dominant selected-integer regime, the tested gaps admit no interior prime square,
and the implemented score maximizer is exactly the first interior integer with
$d(n)=4$.

That gives the leading regime a visible mechanism: square exclusion first,
then first-`d=4` arrival. The stricter semiprime-only slogan is false; a thin
prime-cube exception family survives inside the broader `d=4` class.

See
[gwr/findings/dominant_d4_arrival_reduction_findings.md](gwr/findings/dominant_d4_arrival_reduction_findings.md)
and
[gwr/findings/claim_hierarchy.md](gwr/findings/claim_hierarchy.md).

## Deterministic Filter Performance

This fixed-point separation is one downstream engineering use of the method.
Cryptographic prime generation spends most of its time on candidates that are
composite and never need a full probable-prime path. The exact DNI provides
the invariant target. The production implementation below is the bounded
deterministic surrogate calibrated against that target rather than a runtime
exact-divisor evaluator.

Because confirmed primes live at $Z = 1.0$ under the DNI and composites
contract below it, the filter creates a clean structural separation in
normalized space. That separation makes it possible to reject many candidates
before paying the full cost of primality testing on remaining candidates.

Empirically, this extracted Python path produced:

- $2.09\times$ end-to-end speedup across $300$ deterministic $2048$-bit RSA keypairs
- $2.82\times$ end-to-end speedup across $50$ deterministic $4096$-bit RSA keypairs
- $90.97\,\%$ to $91.07\,\%$ Miller-Rabin reduction in the current covered-table configuration

Those numbers are not a side note. They are the production consequence of the
same invariant program, carried through a narrow deterministic runtime path
that rejects many doomed candidates before Miller-Rabin.

See [docs/prefilter/benchmarks.md](docs/prefilter/benchmarks.md) and
[technical-note/technical_note.md](technical-note/technical_note.md).

## Production Filter Path

The exact DNI depends on exact divisor count. That exact path is valuable as
the derivation and as the oracle, but it is not the runtime path for
cryptographic-scale key generation.

The production implementation in this repository therefore uses a deterministic
surrogate with the same invariant target:

- generate deterministic odd candidates from a SHA-256 namespace/index stream
- reject immediately when a concrete factor appears in the gated prime tables
- keep candidates that survive table rejection on the locus convention
  `proxy_z = 1.0`
- run fixed-base Miller-Rabin on those remaining candidates
- apply final `sympy.isprime` confirmation in the current Python path

In the production path, `proxy_z = 1.0` means only that the candidate survived
the current gated factor tables and therefore advances to Miller-Rabin. It is
not a primality proof by itself.

The current measured rejection rate comes from the covered prime-table depth of
this implementation. The repository includes deterministic table-depth sweeps
to show that dependence directly rather than attributing the `~91%` figure to
runtime exact DNI evaluation.

## Empirical Results

### End-to-End RSA Key Generation

- $2048$ bits, $300$ deterministic keypairs:  
  baseline $291938.126792$ ms  
  accelerated $139942.831833$ ms  
  speedup $2.09\times$  
  Miller-Rabin reduction $90.97\,\%$
- $4096$ bits, $50$ deterministic keypairs:  
  baseline $757750.922792$ ms  
  accelerated $268557.631625$ ms  
  speedup $2.82\times$  
  Miller-Rabin reduction $91.07\,\%$

### Candidate-Loop Screening

- $2048$-bit control corpus:  
  proxy rejection $91.02\,\%$  
  pipeline speedup $2.95\times$
- $4096$-bit control corpus:  
  proxy rejection $91.41\,\%$  
  pipeline speedup $3.33\times$

### DNI Calibration

- $29/29$ calibration primes stayed on $Z = 1.0$
- $0$ composite false fixed points

### Exact Raw Composite Z Field

- This is a separate exact-field concern from the production filter.
- Up to $10^6$ on the natural number line, the strongest exact raw composite
  $Z$ value inside a prime gap lands at edge-distance $2$ in $43.6006\%$ of
  gaps versus an exact within-gap baseline of $22.1859\%$, and is carried by a
  $d(n)=4$ composite in $82.9027\%$ of gaps versus a baseline of $20.1401\%$.
- Later repository notes sharpen that ridge picture into the current selected integer
  theorem: GWR says the implemented log-score maximizer is the arithmetic choice
  “minimize interior divisor count, then take the leftmost integer,” and the
  current proof route reduces the remaining earlier-side burden to a finite
  local admissibility closure. The tested surfaces
  remain the finite base, stress surface, and audit record for that proof chain.
- The dedicated closure study then strengthens the right-edge reading further:
  on the current documented even-band ladder through $10^{18}$, once the
  selected integer appears, no later strictly simpler composite is observed before the
  next prime closes the gap.

See [docs/gap_ridge/raw_composite_z_gap_edge.md](docs/gap_ridge/raw_composite_z_gap_edge.md),
[gwr/findings/gap_winner_rule.md](gwr/findings/gap_winner_rule.md), and
[gwr/findings/closure_constraint_findings.md](gwr/findings/closure_constraint_findings.md).

See [docs/prefilter/benchmarks.md](docs/prefilter/benchmarks.md) for the curated benchmark summary and [docs/prefilter/manual_validation.md](docs/prefilter/manual_validation.md) for the exact reproduction commands.

## Python API

Install the Python package from the repo root:

```bash
python3 -m pip install -e ./src/python
```

## License

This repository is source-available under the
[Business Source License 1.1](LICENSE).

The current grant keeps the code open for research, evaluation, and other
non-production work, and it also permits internal production use for smaller
organizations under the Additional Use Grant in [LICENSE](LICENSE).

Commercial production use outside that grant requires a separate commercial
license. For licensing terms, support, or private commercial use, contact
`dionisio.lopez@icloud.com`.

Each version converts to [Apache License, Version 2.0](LICENSE) four years
after that version is first publicly distributed under the Business Source
License 1.1.

Versions that were first publicly distributed before this change under the MIT
license remain available under those earlier terms.
