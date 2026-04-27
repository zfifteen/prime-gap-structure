# Composite-Exclusion Generator Path

Local state-vector search has not produced a compact next-prime-forcing law.

The current evidence is consistent across the failed paths:

- chamber certificates describe proposed interiors;
- GWR/DNI structure identifies selected-integer behavior inside a proposed chamber;
- legal ladder and pressure states can classify local structure;
- high-resolution legal states can separate labels, but they become
  table-like;
- compressed legal states reuse buckets, but then endpoint-offset collisions
  appear.

The next generator path should not add richer local fingerprints. It should
attempt constructive endpoint isolation by eliminating inadmissible candidates.

Next-Prime Law 005 is not approved by this note.

## Core Idea

The generator must not ask whether a candidate `q` is prime.

It may try to prove that other admissible candidates cannot be the right
endpoint.

For an input prime `p`, define a finite candidate set:

$$Q_B(p) = \{p + k : 0 < k \le B,\ p + k \text{ is wheel-open}\}$$

Each candidate `q_hat` proposes a chamber:

$$I(p, q\_hat) = \{p + 1,\ldots,q\_hat - 1\}$$

The exclusion process rejects a candidate only when legal PGS evidence
contradicts that proposed chamber. It emits a endpoint only if exactly one
candidate remains.

If zero or multiple candidates remain, pure generation fails closed.

## Status

This is a candidate generator path, not a positive inference result.

Current status:

- `candidate_name: composite_exclusion_generator_path`
- `boundary_law_005_status: not_approved`
- `emission_status: FAILED_CLOSED`
- `failure_reason: UNTESTED_EXCLUSION_PREDICATE`

## Allowed Evidence

The exclusion logic may use:

- input prime `p`;
- chosen wheel and wheel-open offsets;
- concrete composite witnesses already legal under the pure contract;
- wheel closure;
- integer square, cube, and power positions;
- bounded small-factor composite witnesses when recorded as positive evidence;
- GWR-selected integer structure computed from legal composite evidence;
- no-later-simpler closure when all ingredients are legal;
- square and threat pressure when expressed without primality recognition;
- previous accepted chamber metadata, if the generator has lawfully emitted the
  previous endpoint.

Positive composite evidence is allowed. Absence of a factor must not be treated
as primality evidence.

## Forbidden Evidence

The exclusion logic must not use:

- `nextprime`;
- `isprime`;
- `prime`;
- Miller-Rabin;
- trial division as a primality test;
- sieve-backed prime or divisor discovery;
- `d(n) = 2` recognition;
- full divisor-count ladders;
- prime-marker identity;
- actual next gap width;
- scan-to-first-prime behavior;
- the old recursive walker;
- `divisor_counts_segment`;
- a table of known prime gaps.

The offline probe may attach classical labels after elimination in order to
measure whether the survivor matches the actual next prime. Those labels are
not part of the elimination state.

## Candidate Rejection Rules

For each `q_hat` in `Q_B(p)`, form the proposed interior `I(p, q_hat)`.

Reject `q_hat` if any legal rule proves the proposed chamber invalid:

1. An interior wheel-open offset has a concrete composite witness inconsistent
   with being an open candidate next prime under the proposed chamber model.
2. A required interior position remains unresolved when the rule requires full
   legal closure of the chamber interior.
3. The chamber lacks a valid GWR-selected integer when the active exclusion model
   requires one.
4. A legal lower-divisor or lower-complexity threat appears after the proposed
   integer and before the proposed endpoint.
5. Square, power, or threat pressure contradicts the proposed chamber closure.
6. A smaller admissible candidate remains unresolved under the same evidence.
7. A deterministic PGS chamber rule rejects the proposed transition.

The first implementation should keep the rule set small. A candidate should
remain unresolved rather than be rejected by a weak or informal rule.

## Fail-Closed Contract

The exclusion process returns one of three outcomes:

- `UNIQUE_SURVIVOR`: exactly one candidate remains;
- `NO_SURVIVOR`: every candidate is rejected;
- `NO_UNIQUE_BOUNDARY`: more than one candidate remains.

Pure generation may emit only on `UNIQUE_SURVIVOR`, and only after the active
rule set has passed the forbidden-dependency gate.

Milestone 1 still requires external audit after emission.

## Offline Probe Shape

The first probe should be theorem discovery, not generation:

- script: `benchmarks/python/prime_inference_generator/composite_exclusion_boundary_probe.py`
- surface: input primes `11..10_000`
- candidate bound: `B = 64`

For each input prime, report:

- `anchor_p`
- `candidate_bound`
- `candidate_count`
- `rejected_count`
- `survivor_count`
- `survivors`
- `actual_boundary_offset_label`
- `unique_survivor_matches_label`
- `failure_reason`

Summary fields:

- `row_count`
- `unique_survivor_count`
- `no_survivor_count`
- `no_unique_boundary_count`
- `true_boundary_rejected_count`
- `unique_survivor_matches_label_count`
- `unique_survivor_matches_label_rate`
- `first_failure_record`
- `forbidden_dependency_status`

The probe may use classical labels only after exclusion. The elimination logic
must be inspectable without labels.

## Success Threshold

A serious Next-Prime Law 005 candidate requires:

- legal exclusion logic;
- zero forbidden dependencies in the elimination path;
- `survivor_count == 1` for every input prime on a meaningful exact surface;
- the unique survivor matches the classical label after audit;
- no table-like candidate encoding;
- a clear PGS interpretation of every rejection rule.

The first exploratory success threshold is weaker:

- high `unique_survivor_matches_label_rate`;
- low `true_boundary_rejected_count`;
- explicit unresolved cases rather than guessed emissions.

## Failure Signals

Reject or revise the path if:

- most input primes retain many survivors;
- the true next prime is frequently rejected;
- exclusion requires prime-marker identity;
- exclusion becomes trial division primality testing;
- unique survivors appear only because the candidate set is table-like;
- the bound `B` is doing the real work rather than the PGS rules.

## Interpretation

Composite exclusion changes the search target.

The failed state-vector path asked for a compact map from local features to the
next prime offset. Composite exclusion asks whether legal PGS evidence can
remove every other admissible candidate.

This is closer to a generator contract:

- generation does not certify primality;
- generation does not look up the next prime;
- generation emits only when deterministic PGS rules leave a unique endpoint
  candidate;
- validation remains a separate audit.

## Next Step

Implement the offline `composite_exclusion_boundary_probe.py` with a deliberately
small exclusion rule set. The first acceptable probe should prefer
`NO_UNIQUE_BOUNDARY` over speculative rejection.

Milestone 1 remains blocked until the exclusion logic produces a lawful unique
survivor and external audit confirms it.
