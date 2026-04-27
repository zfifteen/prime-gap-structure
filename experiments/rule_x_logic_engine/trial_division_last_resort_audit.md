# Trial-Division Last-Resort Audit

## Governing Contract

The intended generator contract is:

```text
Use PGS-derived rules first.
Use trial division only when no PGS rule resolves q.
Do not count a trial-division-confirmed candidate as pure PGS.
Do not use fallback confirmation to choose or label q inside the generator.
```

## Original Finding

The pre-fix generator did not satisfy that contract.

It outputs correct records, but trial division is still used inside the path that
reports `source = "PGS"`.

## Static Evidence

The generator contains these trial-division functions:

```text
src/python/z_band_prime_predictor/simple_pgs_generator.py:22
  has_trial_divisor(n)

src/python/z_band_prime_predictor/simple_pgs_generator.py:32
  divisor_witness(n, max_divisor)

src/python/z_band_prime_predictor/simple_pgs_generator.py:51
  next_prime_by_trial_division(p, candidate_bound)
```

The PGS selection-record path uses trial-division-backed composite witnesses:

```text
src/python/z_band_prime_predictor/simple_pgs_generator.py:66
  closure_reason(...)

src/python/z_band_prime_predictor/simple_pgs_generator.py:76
  witness = divisor_witness(n, max_divisor)
```

The promoted PGS output path also confirms the selected `q` by trial
division before returning `PGS`:

```text
src/python/z_band_prime_predictor/simple_pgs_generator.py:356
  resolve_q(...)

src/python/z_band_prime_predictor/simple_pgs_generator.py:381
  if not has_trial_divisor(q0):

src/python/z_band_prime_predictor/simple_pgs_generator.py:393
  return q0, PGS_SOURCE, certificate
```

Therefore, before the fix, `source = "PGS"` meant:

```text
PGS selection record selected q0,
then trial division confirmed q0,
then the row was labeled PGS.
```

That is not the same as:

```text
PGS alone selected q.
```

## Pre-Fix Runtime Evidence

Runtime audit on the promoted low-scale surface:

```text
surface: 11..100000
candidate_bound: 128
input primes: 9588
sources: {"PGS": 9588}
failures: 0
```

Trial-division calls observed during those `PGS` resolutions:

```text
divisor_witness via closure_reason: 43742 calls
has_trial_divisor via resolve_q: 9588 calls
```

No `fallback` source rows were outputted on this surface, yet trial division was
called on every outputted row.

## Pre-Fix Contract Status

```text
accuracy: PASS
coverage: PASS
trial-division-last-resort contract: FAIL
```

## Applied Fix

Separate the paths physically:

```text
PGS path:
  applies only PGS-derived rules;
  outputs source = "PGS" only without trial-division confirmation.

Fallback path:
  runs trial division only after the PGS path returns unresolved;
  outputs source = "fallback" or another non-PGS bridge label.

Audit path:
  may use classical tools after generation;
  must not choose q inside generation.
```

The immediate engineering target is to remove `has_trial_divisor(q0)` from the
`PGS` source decision and ensure any trial-division-confirmed row is not labeled
pure `PGS`.

This fix is now applied in:

```text
src/python/z_band_prime_predictor/simple_pgs_generator.py
tests/python/predictor/test_simple_pgs_generator.py
docs/specs/prime-gen/minimal_pgs_generator_logic.md
```

The corrected fix removes the `has_trial_divisor(q0)` check from `resolve_q`.
The production selection rule now uses exact divisor-count GWR/NLSC search-interval-reset
state instead of the earlier first-uneliminated-candidate shortcut. That is search interval
state, not fallback completion.

## Post-Fix Runtime Evidence

Runtime audit on the same low-scale surface:

```text
surface: 11..100000
candidate_bound: 128
input primes: 9588
sources: {"PGS": 9588}
failures: 0
PGS rows: 9588
fallback rows: 0
```

Instrumented call audit on the same surface:

```text
has_trial_divisor: 0 calls
divisor_witness: 0 calls
has_trial_divisor via resolve_q: 0 calls
```

The generator no longer performs the old fallback confirmation step on `q0`,
and the production PGS path no longer uses the trial-division helper functions.

High-scale production rerun:

```text
surface: 256 consecutive input primes per decade, 10^8 through 10^18
candidate_bound: 1024
input primes tested: 2816
PGS rows: 2816
fallback rows: 0
audit failures: 0
```

## Post-Fix Contract Status

```text
accuracy: PASS
coverage: PASS
no-inline-fallback-confirmation contract: PASS
PGS-purity accounting: PASS
```

## PGS-Only Refactor

The next generator iteration removes the displaced code paths entirely:

```text
PGS_GENERATOR_VERSION = 1.1.0
PGS_GENERATOR_FREEZE_ID = pgs_inference_generator_v1_1_pgs_only
```

The generator file no longer contains trial-division helpers, divisor-witness
search, shadow-seed recovery, chain fallback, or fallback prime search. If the
PGS selection rule does not resolve inside the supplied search bound, generation
raises `PGSUnresolvedError` instead of choosing `q` by another method.

Current focused test result:

```text
pytest -q tests/python/predictor/test_simple_pgs_generator.py
16 passed
```
