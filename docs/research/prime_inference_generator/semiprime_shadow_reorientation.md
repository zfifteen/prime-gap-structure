# Semiprime Shadow Reorientation

## Status

This note records an offline, audit-backed finding from the PGS Prime
Inference Generator line. It is not production pure emission. It does not
approve cryptographic use. It does not authorize factorization inside solver
logic.

The current use of classical validation and factorization is downstream only:
first the generator emits records, then the audit classifies failures. Any
future generator rule must replace factorization with a label-free PGS shadow
detector before it can become solver logic.

## Core Finding

In the filtered-v5 PGS graph runs, semiprime false emissions are not random
errors. They appear as deterministic left-side landmarks immediately before the
true prime endpoint regime.

Observed surface:

```text
solver: filtered-v5
candidate_bound: 128
witness_bound: 251
input primes: 11..100000
```

Result:

```text
semiprime_shadow_count: 66
true_boundary_right_of_shadow: 66 / 66
median_boundary_minus_shadow_delta: 8
within_16_offsets: 55 / 66
within_32_offsets: 64 / 66
true_boundary_base_status: UNRESOLVED in 66 / 66
true_boundary_after_risky_v5: REJECTED in 66 / 66
```

## Interpretation

A semiprime shadow is not merely a false positive.

It is a endpoint-like composite whose factor obstruction lies just beyond the
active witness horizon. Because that obstruction is hidden, the graph treats
the semiprime as a prematurely resolved next prime. The true next prime then
appears nearby to the right.

The observed deterministic structure is:

```text
horizon-hidden semiprime
  -> false resolved next prime surrogate
  -> absorbs unresolved right-side candidates
  -> true next prime is among the absorbed right-side candidates
```

## Operational Lesson

A semiprime shadow should not just be filtered out. It should eventually
trigger rightward reorientation.

The current filtered-v5 behavior is:

```text
semiprime shadow detected
=> discard emission
=> abstain
```

The future generator-facing behavior to investigate is:

```text
semiprime shadow detected
=> mark shadow as left-side landmark
=> inspect right-neighborhood chamber
=> search for first lawful right-side endpoint transition
=> emit only if a label-free rightward certificate is found
```

## Candidate Mechanism

When filtered-v5 emits a candidate `s` and downstream audit classifies it as a
semiprime shadow, the graph should treat `s` as a landmark, not as the answer.

Let:

```text
p = input prime prime
s = semiprime shadow candidate
q = true next prime candidate
```

Observed relation:

```text
p < s < q
q - s is usually small
q was unresolved before risky absorption
q was rejected or absorbed by the false shadow endpoint
```

This suggests a future graph relation family:

```text
SEMIPRIME_SHADOW_RIGHTWARD_REORIENTATION
```

Possible shape:

```text
If a endpoint-like candidate has shadow structure,
and the graph has unresolved candidates to its right,
then the shadow cannot authorize final emission.
Instead, the graph must re-open the right-neighborhood and look for a
right-side endpoint certificate.
```

## Safety Endpoint

This is not yet a pure generator rule.

Current evidence uses downstream factorization to identify semiprime shadows.
That is allowed only in research and audit. A production PGS rule must replace
factorization with a label-free shadow detector.

Allowed current use:

```text
offline audit
failure analysis
right-neighborhood profiling
candidate relation discovery
```

Forbidden current use:

```text
pure prime emission
production approval
cryptographic approval
factorization inside solver logic
classical validation inside generation
```

## Next Research Question

Can PGS detect shadow structure without factoring the emitted candidate?

The needed future rule is not:

```text
semiprime detected by factorization => search right
```

The needed PGS-native rule is:

```text
endpoint-like candidate with hidden-obstruction signature
=> rightward reorientation required
```

## Generator Implication

The semiprime failure mode is not dead weight. It is a navigation signal.

The graph should treat semiprime shadows as deterministic markers that it has
arrived just before the true next prime, then use local gap structure to the
right to recover the endpoint without broad absorption.

The next generator-facing implementation should not put factorization into the
solver. It should build a deterministic right-neighborhood inspection path over
already emitted filtered-v5 shadow failures, then look for label-free PGS facts
that distinguish the true right-side endpoint from the shadow surrogate.
