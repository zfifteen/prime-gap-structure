# Next-Prime Law 002: Minimal Closed Chamber Certificate

Next-Prime Law 002 is the next candidate after Next-Prime Law 001 failed to close.
The change is the standard of evidence. The law does not infer a endpoint from
first wheel-open admissibility alone. It requires a complete PGS chamber
certificate that forces the proposed endpoint.

This is a design note, not an emitting implementation. If the certificate cannot
force a unique endpoint without classical primality lookup, pure mode must remain
failed closed.

## Name

Minimal Closed Chamber Certificate.

The law asks whether a proposed endpoint can be emitted only after the generator
has a closed chamber certificate for the interval before it and a deterministic
reason that no smaller admissible endpoint competes with it.

## Candidate Contract

Given an anchor prime `p` and proposed endpoint `q_hat`, Next-Prime Law 002 may
emit `q_hat` only if it can construct a certificate with:

- anchor prime `p`;
- proposed endpoint `q_hat`;
- interior `I = {p + 1, ..., q_hat - 1}`;
- verified chamber closure for every integer in `I`;
- GWR-compatible selected integer data, or an explicit empty-chamber base case;
- no-later-simpler closure for the active selected-integer regime;
- no unresolved competing chamber with smaller admissible endpoint;
- an explicit reason `q_hat` is forced rather than merely allowed.

If any field is missing or unresolved, the law fails closed.

## Allowed Inputs

- the externally supplied anchor prime;
- a proposed endpoint supplied by a PGS rule, not by a primality oracle;
- deterministic wheel arithmetic;
- deterministic composite witnesses for interior values;
- PGS carrier metadata inside the proposed chamber;
- GWR/DNI ordering of interior carriers;
- no-later-simpler threat metadata when the chamber has a selected integer carrier;
- a named empty-chamber base case, if such a base case is proved.

## Forbidden Inputs

Next-Prime Law 002 must not use:

- Miller-Rabin;
- `nextprime`;
- `isprime`;
- `prime`;
- `prevprime`;
- trial-division primality testing as a endpoint test;
- sieve-backed divisor counting;
- scanning until `d(n) = 2`;
- the old recursive predictor;
- a committed prime list;
- hardcoded prime outputs.

Interior compositeness evidence is allowed only when it is a concrete
deterministic witness for an interior integer. It must not become a search for
the next prime endpoint.

## Certificate Shape

A Next-Prime Law 002 certificate should record:

- `anchor_prime_p`;
- `proposed_boundary_q_hat`;
- `interior_start`;
- `interior_stop`;
- `interior_composite_witnesses`;
- `winner_carrier_w`;
- `winner_offset`;
- `winner_divisor_count`;
- `winner_family`;
- `first_open_offset`;
- `closure_status`;
- `threat_margin`;
- `competing_boundary_status`;
- `uniqueness_status`;
- `failure_reason`, if unresolved.

For an empty chamber, the certificate must state that no positive-offset carrier
exists before the proposed endpoint and must identify the theorem that turns
that empty chamber into a forced endpoint.

## Anchor-11 Probe

For the first anchor:

$$p = 11$$

The tempting proposed endpoint is:

$$q_{hat} = 13$$

The interior is:

$$I = \{12\}$$

The integer `12` has concrete composite witnesses from the wheel basis:

- `12 = 2 * 6`
- `12 = 3 * 4`

This establishes that the chamber interior before `13` is closed. It does not
establish that `13` is forced as the endpoint.

## GWR/DNI Relevance

For `p = 11` and `q_hat = 13`, the proposed interior contains no open composite
carrier. The GWR-selected integer fields are null. Therefore the standard GWR carrier and
no-later-simpler closure machinery has no positive carrier to operate on.

Next-Prime Law 002 has two possible paths:

- prove an empty-chamber base case that forces the first open endpoint;
- reject this anchor as outside the carrier-bearing GWR/DNI regime.

The first path would revive Next-Prime Law 001 with a stronger certificate. The
second path keeps Milestone 1 blocked at anchor `11` and pushes the first
positive target to a later anchor with a nonempty chamber.

## Competing Endpoint Requirement

The law must separate three statements:

- the interior before `q_hat` is closed;
- `q_hat` is an admissible candidate next prime;
- `q_hat` is the unique inferred next prime.

Only the third statement permits emission.

For anchor `11`, the current certificate proves the first two statements:

- `12` is composite by concrete witness;
- `13` is the first wheel-open admissible candidate.

It does not prove the third statement. The certificate does not rule out the
possibility that the first open candidate is not forced by PGS structure.

## Current Status

Next-Prime Law 002 does not yet emit.

For the anchor-11 probe:

- `closure_status: "interior_closed"`
- `competing_boundary_status: "no_smaller_open_candidate"`
- `uniqueness_status: "unresolved"`
- `inference_status: "failed_closed"`
- `failure_reason: "MISSING_UNIQUENESS_IMPLICATION"`

The law improves the evidence standard over Next-Prime Law 001, but the same
mathematical bridge remains missing for the empty-chamber case.

## Exact Missing Theorem

The missing theorem is:

$$\text{closed minimal chamber plus first open candidate} \Rightarrow \text{forced next prime}$$

For anchor `11`, this reduces to:

$$12 \text{ closed and } 13 \text{ first open} \Rightarrow 13 \text{ forced as endpoint}$$

That implication is stronger than admissibility. It is not proved here.

## Emission Rule

Pure mode may emit under `boundary_law_002` only when:

1. every interior integer has a deterministic composite certificate;
2. the proposed endpoint comes from a PGS rule rather than a primality oracle;
3. all smaller candidate next primes are ruled out by the chamber certificate;
4. a PGS uniqueness theorem forces `q_hat` as the next prime.

Until those four conditions hold, pure mode must emit a failure record.

## Failure Contract

If the uniqueness theorem is missing, emit:

- `rule_set_version: "boundary_law_002"`
- `inference_status: "failed_closed"`
- `failure_reason: "MISSING_UNIQUENESS_IMPLICATION"`

If the interior closure certificate itself is incomplete, emit:

- `rule_set_version: "boundary_law_002"`
- `inference_status: "failed_closed"`
- `failure_reason: "INCOMPLETE_CHAMBER_CERTIFICATE"`

If a competing smaller admissible chamber remains unresolved, emit:

- `rule_set_version: "boundary_law_002"`
- `inference_status: "failed_closed"`
- `failure_reason: "UNRESOLVED_COMPETING_BOUNDARY"`

## Next Search Direction

Next-Prime Law 002 identifies the same blocker more sharply: the project needs a
non-classical uniqueness theorem, not more admissibility evidence.

The next search should compare two regimes:

- empty-chamber anchors, where a first-open closure theorem would be needed;
- carrier-bearing anchors, where GWR/DNI and no-later-simpler closure may have
  enough structure to force a endpoint.

The first positive emission should come from whichever regime first supplies a
complete uniqueness bridge without classical endpoint detection.
