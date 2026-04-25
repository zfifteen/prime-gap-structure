# PGS Prime Inference Generator Executive Summary

## Headline

The PGS Prime Inference Generator now has a working generator-facing CLI that
emits experimental inferred next-prime boundary records, writes reproducible
JSONL/JSON artifacts, and audits emitted records downstream against
first-boundary semantics.

The strongest current result is the bounded high-coverage experimental mode:

```text
solver_version: v7-bounded
surface: anchors 11..100000
candidate_bound: 128
witness_bound: 317
anchors_scanned: 9588
emitted_count: 6039
confirmed_count: 6039
failed_count: 0
coverage_rate: 0.629850
generator_status: BOUNDED_ZERO_FAILURE_AUDITED
production_approved: false
cryptographic_use_approved: false
```

This is not production prime generation yet. It is a high-coverage,
audit-backed experimental generator mode with explicit non-production and
non-cryptographic status.

## Repository Links

- Generator CLI:
  <https://github.com/zfifteen/prime-gap-structure/blob/main/benchmarks/python/prime_inference_generator/experimental_graph_prime_generator.py>
- Graph solver:
  <https://github.com/zfifteen/prime-gap-structure/blob/main/benchmarks/python/prime_inference_generator/boundary_certificate_graph_solver.py>
- Generator documentation:
  <https://github.com/zfifteen/prime-gap-structure/blob/main/docs/research/prime_inference_generator/experimental_graph_prime_generator.md>
- Semiprime-shadow reorientation note:
  <https://github.com/zfifteen/prime-gap-structure/blob/main/docs/research/prime_inference_generator/semiprime_shadow_reorientation.md>
- Witness-horizon semiprime analysis:
  <https://github.com/zfifteen/prime-gap-structure/blob/main/docs/research/prime_inference_generator/witness_horizon_semiprime_impostors.md>
- Test surface:
  <https://github.com/zfifteen/prime-gap-structure/blob/main/tests/python/test_prime_inference_generator.py>

## What The Generator Does

For each anchor prime `p`, the generator builds a finite candidate-boundary
graph over offsets `q - p`. Candidate nodes carry PGS facts from the composite
exclusion engine:

- positive composite witness rejection;
- single-hole positive witness closure;
- carrier-locked pressure ceiling;
- higher-divisor locked absorption;
- unresolved-later domination relations;
- bounded positive nonboundary filters in the bounded mode.

The graph propagates label-free consequences until either exactly one resolved
candidate remains or the generator abstains. If exactly one candidate remains,
the CLI emits an experimental inferred-prime record.

Each emitted record states:

```text
record_type: PGS_INFERRED_PRIME_EXPERIMENTAL_GRAPH
production_approved: false
cryptographic_use_approved: false
audit_required: true
classical_audit_required: true
classical_audit_status: NOT_RUN
```

Downstream audit then checks whether `inferred_prime_q_hat` is the first
classical prime after `anchor_p`. This validation is not part of the generator
logic.

## Safety Boundary

The generator currently separates three concepts:

1. PGS graph emission.
2. Downstream classical audit.
3. Production or cryptographic approval.

Only the first step is generation. Classical validation is used after emission
to audit the emitted records. Production and cryptographic approvals remain
`false` in every current mode.

Forbidden inside generator logic:

- `isprime`;
- `nextprime`;
- Miller-Rabin;
- prime marker identity;
- audit labels;
- factorization;
- broad earliest-candidate selection;
- scalar ranking;
- broad resolved-chamber absorption.

Allowed downstream:

- first-boundary audit;
- failure classification;
- factorization of failed audit records;
- research analysis of failure structure.

## Current Modes

### v6

`v6` is the safe repaired graph baseline.

It uses accepted graph relations through the repaired no-carrier guard:

```text
unresolved_later_domination_target_no_carrier_with_positive_nonboundary_guard
```

On the `11..100000`, `candidate_bound = 128`, `witness_bound = 127` surface:

```text
emitted_count: 217
confirmed_count: 217
failed_count: 0
generator_status: SAFE_ZERO_FAILURE_AUDITED
```

This mode is safe but sparse.

### v7-bounded

`v7-bounded` is the current highest-coverage zero-failure experimental mode.

It runs the risky-v5 graph internally, then applies a label-free positive
nonboundary filter at a surface-specific sieve-complete witness horizon. It
requires:

```text
--candidate-bound 128
--witness-bound >= ceil_sqrt(max_anchor + candidate_bound)
--audit
--fail-on-audit-failure
```

On the `11..100000`, `candidate_bound = 128`, `witness_bound = 317` surface:

```text
risky_input_count: 7391
filtered_count: 1352
emitted_count: 6039
confirmed_count: 6039
failed_count: 0
generator_status: BOUNDED_ZERO_FAILURE_AUDITED
```

For this surface, `ceil_sqrt(max_anchor + candidate_bound) = 317`, so the
audited `witness_bound = 317` run is exactly at the sieve-complete threshold.

This mode is materially stronger than v6 in coverage, but it remains bounded
and experimental. It is not pure production emission.

### risky-v5

`risky-v5` is quarantined research mode. It is high coverage but unsafe.

On the `11..100000`, `candidate_bound = 128`, `witness_bound = 127` surface:

```text
emitted_count: 7391
confirmed_count: 6039
failed_count: 1352
```

It is exposed only behind explicit research opt-in.

### filtered-v5

`filtered-v5` is research-only. It runs risky-v5 internally and filters
positive nonboundary candidates. It helped expose the witness-horizon
semiprime phenomenon but still fails downstream audit at lower witness
horizons.

## Why v7-bounded Matters

The generator moved from sparse safe emission to high-coverage bounded
experimental emission.

The key transition:

```text
v6:
  emitted_count: 217
  confirmed_count: 217
  failed_count: 0

v7-bounded:
  emitted_count: 6039
  confirmed_count: 6039
  failed_count: 0
```

The coverage gain comes from using the high-recall graph line while rejecting
candidates with positive nonboundary evidence inside a declared witness
horizon. This does not make the generator pure or production-approved, but it
does make the bounded experimental app useful and reproducible.

## Semiprime Shadow Finding

The risky and filtered generator lines exposed a structured failure mode:
witness-horizon semiprime impostors.

At lower witness horizons, remaining false emissions were not random. They
clustered at semiprimes whose factors were just beyond the active witness
bound.

Observed frontier:

```text
witness_bound 127:
  first failure: 17947 = 131 * 137

witness_bound 149:
  first failure: 24613 = 151 * 163
  first 100 failures: 100 / 100 semiprimes

witness_bound 197:
  first failure: 41989 = 199 * 211
  first 100 failures: 100 / 100 semiprimes

witness_bound 251:
  first failure band moved beyond 251
```

A later reorientation analysis found that at `witness_bound = 251`:

```text
semiprime_shadow_count: 66
true_boundary_right_of_shadow: 66 / 66
median_boundary_minus_shadow_delta: 8
within_16_offsets: 55 / 66
within_32_offsets: 64 / 66
```

This suggests that semiprime false emissions are deterministic left-side
landmarks before nearby true boundaries. That is a generator-navigation clue,
not permission to factor inside generation. A future PGS-native rule must
detect shadow structure without classical factorization.

## Current Production Readiness

The app is usable as an audited experimental generator.

Working production-facing features:

- safe default CLI;
- explicit solver modes;
- research modes require explicit opt-in;
- audit gate via `--fail-on-audit-failure`;
- dashboard output via `--print-dashboard`;
- LF-terminated JSONL/JSON artifacts;
- downstream audit summaries;
- explicit generator statuses:
  - `AUDIT_NOT_RUN`;
  - `SAFE_ZERO_FAILURE_AUDITED`;
  - `BOUNDED_ZERO_FAILURE_AUDITED`;
  - `RESEARCH_ZERO_FAILURE_AUDITED`;
  - `AUDIT_FAILED`.

Still not production-ready:

- production emission remains false;
- cryptographic use remains false;
- v7-bounded depends on the surface-specific sieve-complete witness threshold;
- pure recursive generation is not approved;
- safe coverage outside the declared audited regime remains unclaimed.

## How To Reproduce The Main Result

Run:

```bash
python3 benchmarks/python/prime_inference_generator/experimental_graph_prime_generator.py \
  --solver-version v7-bounded \
  --start-anchor 11 \
  --max-anchor 100000 \
  --candidate-bound 128 \
  --witness-bound 317 \
  --audit \
  --fail-on-audit-failure \
  --print-dashboard \
  --output-dir output/prime_inference_generator/v7_bounded_w317_11_100000
```

Expected dashboard:

```text
solver_version: v7-bounded
anchors_scanned: 9588
emitted_count: 6039
audit_confirmed: 6039
audit_failed: 0
generator_status: BOUNDED_ZERO_FAILURE_AUDITED
production_approved: false
cryptographic_use_approved: false
first_failure: null
```

## Recommended Next Work

The highest-priority production-readiness task is to convert bounded
high-coverage behavior into a more PGS-native generator rule.

The next generator direction is:

1. Preserve `v7-bounded` as the current high-coverage audited experimental
   mode.
2. Use semiprime-shadow structure to design a label-free rightward
   reorientation mechanism.
3. Eliminate right-neighborhood composite candidates without factorization or
   audit labels.
4. Increase zero-failure emitted coverage beyond v6 without relying only on a
   larger witness horizon.
5. Keep `production_approved` and `cryptographic_use_approved` false until the
   rule set is audit-clean over a declared production regime and no classical
   dependency enters generation.

## Executive Status

The PGS Prime Inference Generator is no longer just a theorem-probe pipeline.
It is a working audited experimental generator app.

The current strongest claim is:

```text
The v7-bounded PGS graph generator emitted 6039 experimental inferred
next-prime boundary records on anchors 11..100000 with candidate_bound 128 and
witness_bound 317. A separate downstream first-boundary audit confirmed
6039 / 6039 records, with 0 failures. Production and cryptographic approvals
remain false.
```

That is the distributable result.
