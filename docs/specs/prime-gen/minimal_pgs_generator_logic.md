# Minimal PGS Generator Logic

Current production iteration:

```text
PGS Inference Generator v1.1
PGS_GENERATOR_VERSION = 1.1.0
PGS_GENERATOR_FREEZE_ID = pgs_inference_generator_v1_1_pgs_only
```

Release note:
[PGS Inference Generator v1.1](../../releases/pgs_inference_generator_v1_1_pgs_only.md).

The generator has one job: start from an accepted anchor prime `p` and emit the
next prime `q` selected by the PGS next-prime selection rule.

Each emitted line has exactly two fields:

```json
{"p": 11, "q": 13}
```

`q` is the generator's PGS-selected next-prime output. A separate downstream
audit checks every emitted record after emission. Audit is verification, not
the mechanism that chooses `q`.

## Stage 1: Anchor

The anchor `p` is the current accepted prime. The generator accepts `p` as
input. It does not prove `p` during generation.

For every resolved anchor, the generator emits exactly one record. If the PGS
selector does not resolve inside the supplied chamber bound, the generator
raises `PGSUnresolvedError`. It does not run a backup prime search.

## Stage 2: Chamber

The chamber is the finite interval to the right of `p` inspected by the PGS
selector.

Inside the chamber, the generator uses:

- offsets from the anchor;
- wheel-open positions;
- exact divisor-count state;
- GWR-selected integer structure;
- no-later-simpler-composite ceilings;
- chamber-reset next-prime state.

The chamber is not a place to ask a primality oracle which number is prime. It
is the local arithmetic region where the PGS rule decides the next prime.

## Stage 3: Integer

GWR identifies the simplest leftmost integer `w` inside the chamber.

The integer is not the endpoint. It is a landmark that orients the local PGS
state. The rule `q = w + 1` is false as a general rule and is forbidden.

## Stage 4: Endpoint Rule

The production next-prime selection rule is Rule X with chamber reset:

- build wheel-open candidate next-prime hypotheses;
- reject candidates with composite divisor-count state;
- preserve semiprime-shadow landmarks as unresolved landmarks instead of
  promoting them to endpoint survivors;
- lock the GWR-selected integer only after a resolved survivor exists;
- apply the lower-divisor threat ceiling after integer lock;
- identify the first resolved survivor `r`;
- reset the chamber at `r`;
- classify later unresolved candidates as post-reset chamber material;
- emit `r` as the proposed next prime.

In compact form:

$$q = B(p, S, w, d(w))$$

where `S` is the exact divisor-count chamber state needed to make the endpoint
choice single-valued.

## Stage 5: Emission

For each resolved anchor `p`, the generator emits exactly one line:

```json
{"p": 11, "q": 13}
```

The line contains no extra fields. It contains no selected-integer data, relation
history, proof object, approval flags, counters, status categories, source
labels, or hidden diagnostics.

The generator script contains generation logic only. It does not contain
artifact writing, audit, reporting, command-line orchestration, fallback prime
search, trial division, or downstream validation helpers.

Sidecar diagnostics are produced by the controller, not by the emitted stream.
The current production generator source is always `PGS` when a record is
emitted.

## Validation Surfaces

Low exact production surfaces:

```text
11..1000      anchors 164     PGS 164     failures 0
11..10000     anchors 1225    PGS 1225    failures 0
11..100000    anchors 9588    PGS 9588    failures 0
11..1000000   anchors 78494   PGS 78494   failures 0
```

High-scale decade-window surface:

```text
surface: 256 consecutive prime anchors per decade, 10^8 through 10^18
candidate_bound: 1024
anchors tested: 2816
PGS emissions: 2816
audit failures: 0
```

## Forbidden Generator Tools

Generation must not call or contain:

- trial division;
- fallback prime search;
- `isPrime`;
- Miller-Rabin;
- `nextprime`;
- probabilistic primality tests;
- ECPP;
- PARI primality checks;
- sieve-based prime generation.

Downstream audit may use classical validation after emission. Audit code must
not live in the generator file and must not choose `q` inside generation.

## Completion Standard

A complete PGS-only generator satisfies these conditions on a declared surface:

- every accepted anchor on the surface emits exactly one record;
- every emitted `q` is the actual next prime after `p`;
- every record has exactly `p` and `q`;
- no forbidden tool is used inside generation;
- unresolved cases fail explicitly with `PGSUnresolvedError`;
- downstream audit checks the emitted records after generation.
