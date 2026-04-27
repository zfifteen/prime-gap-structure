# Next-Prime Law 001: First Open Chamber Closure

Next-Prime Law 001 is the first candidate law for Milestone 1 of the PGS Prime
Inference Generator. Its target is deliberately small: produce one lawful
emission from anchor prime `11` without classical primality testing or
next-prime lookup inside the generation loop.

This note is a design note, not a positive result. The law must not be installed
as an emitting rule until the uniqueness condition below is satisfied by PGS
inference rather than by external validation.

## Name

First Open Chamber Closure.

The chamber after anchor `11` has one closed integer before the first wheel-open
offset. Next-Prime Law 001 asks whether that first open offset can be inferred as
the right endpoint from PGS chamber structure alone.

## Allowed Inputs

- `anchor_prime_p = 11`
- deterministic mod-30 wheel residues
- first wheel-open even offset after the anchor
- PGS chamber metadata derived without primality testing
- rule-set version `boundary_law_001`

For the first anchor:

- `11 mod 30 = 11`
- offset `1` gives `12`, a wheel-closed integer
- offset `2` gives the first wheel-open position

## Forbidden Inputs

The law must not use:

- Miller-Rabin
- `nextprime`
- `isprime`
- `prime`
- `prevprime`
- trial-division primality testing
- sieve-backed divisor counting
- scanning until `d(n) = 2`
- the old recursive predictor
- a committed prime list
- hardcoded output `13`

The law may compute `q_hat = p + first_open_offset` only if the rule has first
established that the first open offset is the unique PGS-inferred next prime for
this chamber.

## Candidate Inference Steps

1. Read anchor prime `p = 11`.
2. Compute the first wheel-open even offset after `p` under the mod-30 wheel.
3. Record the pre-open chamber segment from offsets `1` through
   `first_open_offset - 1`.
4. Verify that every pre-open integer is wheel-closed by deterministic
   divisibility against the wheel basis.
5. Establish that no GWR carrier is required when the inferred chamber interior
   contains no admissible open composite carrier before the first open offset.
6. Infer `q_hat = p + first_open_offset`.
7. Emit `q_hat` only if the next-prime uniqueness condition below is resolved.

## Endpoint Uniqueness Condition

For anchor `11`, the rule must show from PGS chamber metadata alone that the
first wheel-open position is the right endpoint rather than merely the first
admissible candidate next prime.

The unresolved distinction is:

- candidate statement: the first possible open endpoint after `11` is `11 + 2`;
- next-prime statement: the next prime endpoint inferred by PGS is `11 + 2`.

Next-Prime Law 001 is not accepted as an emitting law until it proves the endpoint
statement without asking whether `11 + 2` is prime.

## Emitted Metadata

If the law resolves the endpoint, pure mode emits:

- `step_index: 1`
- `anchor_prime_p: 11`
- `inferred_prime_q_hat: 13`
- `inferred_gap_width: 2`
- `winner_carrier_w: null`
- `winner_offset: null`
- `winner_divisor_count: null`
- `winner_family: "empty_pre_open_chamber"`
- `first_open_offset: 2`
- `closure_status: "first_open_boundary_inferred"`
- `threat_margin: null`
- `rule_set_version: "boundary_law_001"`
- `inference_status: "inferred"`
- `failure_reason: null`

The null selection fields are intentional for this first anchor. The chamber has
no positive-offset open composite carrier before the inferred right endpoint.

## Failure Contract

If the law cannot prove unique next-prime inference, pure mode must emit:

- `inference_status: "failed_closed"`
- `failure_reason: "NO_UNIQUE_BOUNDARY"`
- `rule_set_version: "boundary_law_001"`

It must not guess, validate inline, scan to a prime endpoint, or fall back to
Milestone 0 behavior silently.

## Why This Is PGS Inference

The law is PGS inference only if the emitted next-prime value follows from the anchor,
the wheel-closed pre-open chamber, and the explicit empty-chamber closure rule.
The external audit may later confirm the emitted `q_hat`, but that confirmation
cannot participate in the generation step.

## First Test Anchor

The first test anchor is `11`.

Milestone 1 succeeds at the first hard target when pure mode emits one
`boundary_law_001` record from anchor `11`, and external audit afterward
confirms that emitted next-prime value.

The stretch target is `N > 1` consecutive inferred next primes. That target
requires an additional law or a generalized version of this one; this note does
not claim that generalization.

## Acceptance Criteria

Next-Prime Law 001 may be implemented behind `--rule-set boundary_law_001` only
after the unresolved next-prime uniqueness condition is closed.

The implementation must satisfy the existing forbidden-dependency gate. The pure
path must still default to the Milestone 0 fail-closed scaffold unless the rule
set is explicitly selected.

## Falsification Conditions

Next-Prime Law 001 fails if:

- the pure path uses a forbidden helper;
- the rule hardcodes the emitted next-prime value;
- the rule only identifies a candidate and calls it a endpoint;
- audit rejects the emitted `q_hat`;
- generation and validation become coupled;
- the rule cannot explain why the endpoint is unique.
