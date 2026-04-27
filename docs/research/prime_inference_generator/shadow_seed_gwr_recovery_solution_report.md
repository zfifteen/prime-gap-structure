# Shadow Seed Recovery Bridge Report

The Minimal PGS Generator blocker was the high-scale semiprime-shadow lane. At
low scale, chamber closure already emitted the next prime for every tested
anchor. At high scale, the same chamber rule often selected a composite
left-side shadow inside the gap. Earlier bridge logic could recover from those
rows, but the source accounting did not separate pure PGS selection from
exact arithmetic recovery.

The implemented solution changes the role of that shadow. The composite
candidate is no longer treated as a failed answer. It is treated as a placed
seed inside the current gap. From that seed, the generator performs a
deterministic rightward recovery and emits the first endpoint it reaches. That
recovery is an operational bridge because the terminal selection still uses
exact divisor arithmetic. It is not yet a pure PGS next-prime selection rule. The emitted
stream remains exactly:

```json
{"p": 89, "q": 97}
```

No source label, confidence field, certificate, or metadata is added to the
emitted record. Source information stays in the sidecar diagnostics, where the
bridge is labeled `shadow_seed_recovery`.

## Blocker

The restart generator had three relevant stages:

1. `pgs_chamber_closure_v2` selected the first wheel-open offset whose smaller
   admissible offsets were closed by visible chamber evidence.
2. If that selected value was prime, the row was counted as `PGS`.
3. If that selected value was composite, the generator used a chain bridge or
   fallback path to preserve correctness.

This worked completely on the exact low-scale surfaces:

| Surface | Emitted | Confirmed | Audit failures | PGS | Fallback |
|---|---:|---:|---:|---:|---:|
| `11..100000` | 9,588 | 9,588 | 0 | 100.00% | 0.00% |
| `11..1000000` | 78,494 | 78,494 | 0 | 100.00% | 0.00% |

At high scale, the same rule exposed a repeatable failure mode. The selected
candidate was usually a composite to the left of the true next prime. Those rows
were not random misses; they were semiprime-shadow rows. The chain bridge made
them operationally correct, but the bridge did not solve the PGS displacement
target because it still depended on a non-PGS terminal decision.

The problem was therefore not coverage. The generator already knew how to emit
correctly in exact mode. The blocker was source classification:

```text
composite chamber-closure seed -> bridge/fallback -> correct q
```

became:

```text
composite chamber-closure seed -> shadow-seed recovery bridge -> correct q
```

## Failed Intermediate Paths

Several probes clarified what was not the solution.

The horizon-law probe measured the least-factor frontier of false pre-terminal
chain nodes. No tested simple law closed every false node across `10^12`,
`10^15`, and `10^18` while materially beating the square-root comparator.

The two-lane probe showed that false nodes have two obstruction lanes:

```text
low-factor lane
sqrt-adjacent lane
```

That was a real diagnostic improvement, but the half-square-root closure was a
generic two-sided divisor-search comparator, not a PGS next-prime law.

The decisive shift was to stop asking which chain node looked terminal and to
ask what the false chamber candidate actually represented. The false candidate
was a placed interior seed. Once that is true, the right object is not the
whole chain. The right object is recovery from the seed.

## Implemented Bridge

The new bridge source is:

```text
shadow_seed_recovery
```

It is implemented in
[`simple_pgs_generator.py`](../../../src/python/z_band_prime_predictor/simple_pgs_generator.py).

Generation order is now:

1. Build the `pgs_chamber_closure_v2` certificate.
2. Let `q0` be the chamber-closure candidate.
3. If `q0` passes deterministic divisor checking, emit `q0` as `PGS` under
   `pgs_chamber_closure_v2`.
4. If `q0` is composite, treat `q0` as the shadow seed.
5. Run `shadow_seed_gwr_recovery_result(p, q0 - p, candidate_bound)`.
6. Emit the recovered endpoint under `shadow_seed_recovery`, with rule id
   `shadow_seed_trial_recovery_v1`.
7. Preserve the old chain and full fallback paths as guards after this step.

The important implementation point is that the trigger is generator-visible.
It does not depend on downstream audit:

```text
PGS chamber closure selects q0.
Generator arithmetic checks q0.
If q0 is composite, q0 becomes the recovery seed.
```

The audit module still validates after emission only. The source label is not
counted as pure `PGS`.

## Why The Bridge Works On The Tested Surface

A semiprime-shadow row has this observable structure:

```text
p < q0 < q
```

where:

- `p` is the accepted anchor prime;
- `q0` is the chamber-selected composite shadow;
- `q` is the true next prime after `p`.

The old interpretation treated `q0` as a wrong terminal answer. The new
interpretation treats it as a placed gap-interior seed. Because `q0` lies to
the right of `p` and to the left of `q`, rightward recovery from `q0` lands on
the same endpoint `q`.

That converts the high-scale blocker from:

```text
find terminal node among chain candidates
```

into:

```text
recover endpoint from placed shadow seed
```

The probe results show that this recovers every emitted high-scale row without
needing `chain_horizon_closure`, `chain_fallback`, or full fallback in the
sampled high-scale probe. The result is operationally strong, but the
rightward terminal step is still exact arithmetic, so these rows remain bridge
rows until a label-free PGS replacement is derived.

## High-Scale Probe Result

The high-scale probe is
[`simple_pgs_high_scale_chain_probe.py`](../../../benchmarks/python/predictor/simple_pgs_high_scale_chain_probe.py).
Its committed result summary is
[`output/simple_pgs_shadow_seed_gwr_solution_probe/summary.json`](../../../output/simple_pgs_shadow_seed_gwr_solution_probe/summary.json).

| Scale | Sample | Emitted | Unresolved | Audit failures | Pure PGS | Chamber closure | Shadow seed recovery | Chain/fallback |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `10^12` | 256 | 253 | 3 | 0 | 59.68% | 151 | 102 / 40.32% | 0 |
| `10^15` | 256 | 249 | 7 | 0 | 43.37% | 108 | 141 / 56.63% | 0 |
| `10^18` | 256 | 250 | 6 | 0 | 42.00% | 105 | 145 / 58.00% | 0 |

The unresolved rows are probe-mode rows where full fallback was deliberately
disabled. They are not wrong emissions. In exact production mode, the generator
keeps deterministic fallback paths so it does not return unresolved.

## Exact Low-Scale Result

The exact low-scale reports are:

- [`output/simple_pgs_shadow_seed_gwr_solution_1e5/report.json`](../../../output/simple_pgs_shadow_seed_gwr_solution_1e5/report.json)
- [`output/simple_pgs_shadow_seed_gwr_solution_1e6/report.json`](../../../output/simple_pgs_shadow_seed_gwr_solution_1e6/report.json)

| Surface | Anchors scanned | Emitted | Confirmed | Audit failures | PGS | Fallback | Status |
|---|---:|---:|---:|---:|---:|---:|---|
| `11..100000` | 9,588 | 9,588 | 9,588 | 0 | 100.00% | 0.00% | `PGS_PASS` |
| `11..1000000` | 78,494 | 78,494 | 78,494 | 0 | 100.00% | 0.00% | `PGS_PASS` |

## Contract Preservation

The implementation preserves the minimal generator contract:

- emitted records contain only `p` and `q`;
- source labels remain sidecar-only;
- audit remains outside the generator;
- no old graph generator code is imported;
- no `sympy`, `nextprime`, `isprime`, `primerange`, Miller-Rabin, CLI parsing,
  JSON writing, report writing, or audit code was added to the generator
  module.

The focused test file is
[`test_simple_pgs_generator.py`](../../../tests/python/predictor/test_simple_pgs_generator.py).
The validation run passed:

```text
17 passed
```

The forbidden-token scan on the generator file returned an empty list.

## What Changed Conceptually

The old model was:

```text
shadow = failed candidate
chain = repair search object
terminal node = missing certificate
```

The new model is:

```text
shadow = placed interior seed
rightward recovery = endpoint recovery
terminal node search = unnecessary for these rows
```

That is the bridge milestone. The high-scale lane was not solved by deriving a
static terminal-node label. It was made operationally recoverable by
reinterpreting the shadow as a seed with enough positional information to
recover the right endpoint through exact arithmetic.

## Remaining Engineering Work

The implemented bridge is a research milestone and an integration-ready
recovery path. Before crypto-keygen use, two engineering tasks remain:

1. Replace the current trial-division hot path in shadow recovery with the
   approved deterministic primality backend for the production wrapper.
2. Characterize unresolved high-scale probe rows and decide whether
   `candidate_bound=128` should become a dynamic bound in probe mode.

The current result is still strong: on every emitted high-scale sampled row
through `10^18`, audit failures are zero and chain/fallback counts are zero.
The honest source split is pure chamber-closure PGS plus
`shadow_seed_recovery` bridge rows.
