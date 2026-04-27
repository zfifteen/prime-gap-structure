# Next-Prime Law 001 Input prime-11 Derivation

This note tests whether Next-Prime Law 001 closes for the first input prime. The target
is not to show that `13` is prime. The target is to show, using only allowed PGS
evidence, that input prime `11` uniquely closes at offset `2`.

The derivation does not close yet. It establishes the first-open candidate and
the empty pre-open chamber, but it does not derive the next-prime uniqueness step.
The emission status remains `FAILED_CLOSED`.

## Input prime: p = 11

The input prime is the externally supplied known prime:

$$p = 11$$

The generator may use `11` as the starting endpoint. It may not use a next-prime
oracle to learn the right endpoint.

## Candidate Endpoint: q_hat = 13

The first wheel-open even offset after `11` is `2`. The candidate next prime is:

$$q_{hat} = 11 + 2 = 13$$

This statement is only a candidate statement. It says that offset `2` is the
first admissible wheel-open position after the input prime. It does not by itself say
that offset `2` is the uniquely inferred PGS endpoint.

## Allowed Evidence Only

The allowed evidence is:

- the supplied input prime `p = 11`;
- arithmetic in the fixed mod-30 wheel;
- deterministic divisibility by the wheel basis for pre-open positions;
- the absence of a positive-offset open integer before offset `2`;
- Next-Prime Law 001 as a proposed empty-chamber closure rule.

For input prime `11`, the mod-30 residue is:

$$11 \equiv 11 \pmod{30}$$

The wheel-open residues are:

$$1, 7, 11, 13, 17, 19, 23, 29 \pmod{30}$$

Offset `1` gives residue `12`, which is closed by the wheel basis. Offset `2`
gives residue `13`, which is wheel-open.

## Forbidden Evidence Excluded

This derivation does not use:

- Miller-Rabin;
- `nextprime`;
- `isprime`;
- `prime`;
- `prevprime`;
- trial-division primality testing;
- sieve-backed divisor counting;
- scanning until `d(n) = 2`;
- the old recursive predictor;
- a committed prime list;
- the fact that `13` is classically prime.

The expression `q_hat = 13` appears only because `13 = 11 + 2`. It is not used
as a known prime.

## Chamber Model Before Endpoint

Before the candidate next prime at offset `2`, the chamber contains one integer:

$$I_{pre} = \{12\}$$

The integer `12` is wheel-closed because:

$$12 \equiv 12 \pmod{30}$$

Residue `12` is divisible by `2` and by `3` in the wheel basis. Therefore `12`
is not an admissible open candidate next prime and not an open GWR-selected integer.

The pre-open chamber has no positive-offset open composite integer.

## First-Open Offset Logic

The first wheel-open even offset after `11` is `2`.

The wheel computation establishes:

- offset `1` is closed;
- offset `2` is the first open position;
- no earlier open position exists.

This is a useful invariant. It proves that `11 + 2` is the first admissible
candidate under the wheel. It does not prove that the candidate is the right
endpoint.

## GWR/DNI Relevance

GWR normally identifies the leftmost integer of the minimum divisor-count class
inside a prime-gap interior. DNI and no-later-simpler closure use that integer
to constrain where the right endpoint must arrive before a later lower-divisor
threat overtakes the selected integer.

For the proposed input prime-11 chamber ending at offset `2`, there is no positive
open composite integer before the candidate next prime. The selection fields are
therefore null:

- `winner_carrier_w: null`
- `winner_offset: null`
- `winner_divisor_count: null`
- `winner_family: "empty_pre_open_chamber"`

This empty-chamber state is not the standard GWR-selected integer regime. Next-Prime Law
001 would need to define a lawful base case: if the pre-open chamber is closed
and contains no admissible integer, the first open position closes the chamber.

That base case is the exact mathematical content still needed.

## Why No Competing Endpoint Is Allowed

The current derivation rules out competing endpoints before offset `2`:

- offset `1` is wheel-closed;
- there is no earlier positive offset;
- no open integer exists before the first open offset.

The current derivation does not rule out the possibility that the first open
position is only a candidate and that the chamber continues to a later endpoint.
Ruling that out would require an empty-chamber closure principle stronger than
wheel admissibility.

The missing implication is:

$$\text{first open candidate after an empty pre-open chamber} \Rightarrow \text{unique right endpoint}$$

That implication is not yet established by PGS structure in this note.

## Exact Unresolved Step

The unresolved step is the conversion from admissibility to next-prime inference:

- established: `11 + 2` is the first wheel-open admissible candidate;
- not established: `11 + 2` is the unique PGS-inferred next prime.

Until that conversion is proved, Next-Prime Law 001 must not emit `q_hat = 13` in
pure mode.

## Emission Status: FAILED_CLOSED

The correct emission status is:

- `rule_set_version: "boundary_law_001"`
- `inference_status: "failed_closed"`
- `failure_reason: "NO_UNIQUE_BOUNDARY"`

Milestone 1 positive emission remains blocked. The next proof task is to
establish or reject the empty-chamber closure principle without using classical
validation or next-prime discovery.
