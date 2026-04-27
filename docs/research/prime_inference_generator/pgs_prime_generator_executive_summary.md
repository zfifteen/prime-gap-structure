# PGS Prime Inference Generator Executive Summary

## Headline

The production PGS Prime Inference Generator is now PGS-only.

It starts from an accepted prime `p` and emits the next prime `q` without trial
division, fallback prime search, Miller-Rabin, sieve generation, `isprime`, or
`nextprime` inside the generator.

```json
{"p": 89, "q": 97}
```

Current production version:

```text
PGS_GENERATOR_VERSION = 1.1.0
PGS_GENERATOR_FREEZE_ID = pgs_inference_generator_v1_1_pgs_only
```

## Current Result

Low exact production surfaces:

```text
11..1000      input primes 164     PGS 164     unresolved 0     failures 0
11..10000     input primes 1225    PGS 1225    unresolved 0     failures 0
11..100000    input primes 9588    PGS 9588    unresolved 0     failures 0
11..1000000   input primes 78494   PGS 78494   unresolved 0     failures 0
```

High-scale decade-window surface:

```text
surface: 256 consecutive input primes per decade, 10^8 through 10^18
candidate_bound: 1024
input primes tested: 2816
PGS emissions: 2816
unresolved: 0
audit failures: 0
```

## What Changed

The earlier `v1.0` generator had already displaced fallback on the audited
production surfaces, but the code still carried explicit last-resort paths.

The `v1.1` generator removes those paths from the generator file. If the PGS
selector does not resolve inside the supplied chamber bound, generation raises
`PGSUnresolvedError` instead of choosing `q` by another method.

Removed from the production generator:

- trial division;
- fallback prime search;
- divisor-witness search;
- shadow-seed recovery;
- chain fallback;
- inline validation of emitted `q`.

## Endpoint Rule

The production selector is:

```text
rule_id: pgs_chamber_reset_v1
state input: exact divisor-count field
next-prime selection rule: GWR/NLSC chamber-reset state
```

The key chamber-reset interpretation is:

After the first resolved survivor appears, later unresolved candidates are
post-reset chamber material, not competing endpoints for the original input prime.

That converts the remaining candidate set into a consistency-collapse problem:
the endpoint is the first resolved survivor that leaves the earlier chamber
state coherent under GWR and NLSC.

## Repository Links

- Generator source:
  <https://github.com/zfifteen/prime-gap-structure/blob/main/src/python/z_band_prime_predictor/simple_pgs_generator.py>
- Generator logic specification:
  <https://github.com/zfifteen/prime-gap-structure/blob/main/docs/specs/prime-gen/minimal_pgs_generator_logic.md>
- PGS-only release note:
  <https://github.com/zfifteen/prime-gap-structure/blob/main/docs/releases/pgs_inference_generator_v1_1_pgs_only.md>
- Test surface:
  <https://github.com/zfifteen/prime-gap-structure/blob/main/tests/python/predictor/test_simple_pgs_generator.py>
- Rule X logic report:
  <https://github.com/zfifteen/prime-gap-structure/blob/main/docs/research/prime_inference_generator/rule_x_consistency_collapse_logic_engine.md>

## Scope

This is a production-generator result on the declared validation surfaces. It
is not yet a theorem for every future input prime at every scale.

The current accomplishment is concrete: the generator emits exact
successor-prime records on the tested low and high-scale surfaces with no trial
division or fallback search inside the generator.
