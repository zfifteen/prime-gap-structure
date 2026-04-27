# Executive Summary: PGS Prime Generator

## Purpose

The PGS Prime Generator is a deterministic successor-prime inference generator.
It starts from an accepted prime `p` and emits the next prime `q` as a minimal
two-field record:

```json
{"p": 89, "q": 97}
```

The current production generator is PGS-only. It contains no trial division, no
fallback prime search, no Miller-Rabin, no sieve generation, no `isprime`, and
no `nextprime`.

## Core Idea

Conventional prime generation scans candidate numbers and tests them until one
is accepted as prime. The PGS generator does not do that.

It examines the finite arithmetic interval immediately to the right of `p`,
uses exact divisor-count state to orient the local prime-gap structure, and
selects the next prime by the GWR/NLSC chamber-reset rule.

The production selector is:

```text
rule_id: pgs_chamber_reset_v1
state input: exact divisor-count field
next-prime selection rule: GWR/NLSC chamber-reset state
```

If the selector does not resolve inside the supplied chamber bound, the
generator raises `PGSUnresolvedError`. It does not run a backup prime search.

## Architecture

The production generator has one execution path:

```text
input prime p -> GWR/NLSC chamber-reset selector -> emit {"p": p, "q": q}
```

The emitted stream contains only `p` and `q`. Source labels, certificates,
diagnostics, timing, and audit results live outside the emitted stream.

Downstream audit validates emitted records after generation. Audit does not
choose `q` and does not feed back into generation.

## Current Production Result

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

## Current Version

```text
PGS_GENERATOR_VERSION = 1.1.0
PGS_GENERATOR_FREEZE_ID = pgs_inference_generator_v1_1_pgs_only
```

Release note:
[PGS Inference Generator v1.1](releases/pgs_inference_generator_v1_1_pgs_only.md).

Logic spec:
[Minimal PGS Generator Logic](specs/prime-gen/minimal_pgs_generator_logic.md).

## Endpoint Rule

The production next-prime selection rule applies these steps:

- build wheel-open candidate next-prime hypotheses;
- reject candidates with composite divisor-count state;
- preserve semiprime-shadow landmarks as unresolved landmarks;
- lock the GWR-selected integer only after a resolved survivor exists;
- apply the lower-divisor threat ceiling after integer lock;
- identify the first resolved survivor;
- reset the chamber at that survivor;
- classify later unresolved candidates as post-reset chamber material;
- emit the resolved survivor as `q`.

## Non-Goals

- proving the input input prime `p`;
- cryptographic certification inside the generator;
- primality testing inside the generator;
- trial-division fallback;
- Miller-Rabin or sieve replacement claims beyond the tested generator surface;
- theorem claims for every future scale.

The current accomplishment is narrower and concrete: the production generator
now emits exact successor-prime records on the declared test surfaces without
trial division or fallback search inside the generator.
