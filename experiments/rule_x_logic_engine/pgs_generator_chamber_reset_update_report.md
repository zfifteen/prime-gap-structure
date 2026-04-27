# PGS Generator Chamber-Reset Update Report

## Result

The minimal PGS generator now emits chamber-reset PGS certificates under:

```text
rule_id: pgs_chamber_reset_v1
```

The emitted generator record remains physically minimal:

```json
{"p": 11, "q": 13}
```

Rule status remains in sidecar diagnostics.

## Promoted Generator Check

The promoted generator path was checked on the full low-scale surface where the
existing deterministic arithmetic is cheap and complete:

```text
surface: 11..100000
candidate_bound: 128
input primes tested: 9588
PGS emissions: 9588
rule_id: pgs_chamber_reset_v1
failed emissions: 0
runtime: 0.344686 seconds
```

## High-Scale Rule Validation

The chamber-reset rule was separately validated in the decade-window experiment
through `10^18`:

```text
decades: 10^8 through 10^18
input primes per decade: 256
candidate_bound: 1024
input primes tested: 2816
exact matches: 2816
unresolved: 0
false emissions: 0
candidate-bound misses: 0
coverage: 100.000000%
```

The high-scale run remains an experiment-harness validation surface. The
generator module does not import classical high-scale primality helpers.

## Verification

```text
pytest -q tests/python/predictor/test_simple_pgs_generator.py
17 passed
```

LF line endings were verified for the updated generator, tests, and
documentation artifacts.
