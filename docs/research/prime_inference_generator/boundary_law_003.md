# Next-Prime Law 003: First Carrier-Bearing Chamber Certificate

Next-Prime Law 003 moves the first positive target away from the empty anchor-11
chamber. The target is a chamber where PGS has actual interior structure: a
composite interior, a definable GWR carrier, a divisor-count selected integer, and a
closure condition that can be inspected without classical endpoint detection.

This note uses the small chamber from anchor `13` to proposed endpoint `17` as
the first probe. It does not emit yet. It establishes the carrier-bearing
certificate and identifies the remaining uniqueness gap.

## Name

First Carrier-Bearing Chamber Certificate.

The law asks whether a nonempty chamber with a GWR-compatible carrier can force
its right endpoint from PGS structure alone.

## Target Probe

The first probe is:

$$p = 13$$

with proposed endpoint:

$$q_{hat} = 17$$

The proposed interior is:

$$I = \{14, 15, 16\}$$

This chamber is small enough to audit by hand and large enough to contain
nontrivial carrier structure.

## Allowed Inputs

- externally supplied anchor prime `p = 13`;
- proposed endpoint supplied by the candidate law, not by a next-prime oracle;
- deterministic factor witnesses for proposed interior composites;
- divisor counts derived from those explicit witnesses;
- GWR leftmost-minimum carrier logic;
- no-later-simpler comparison against explicitly identified later interior
  points;
- deterministic wheel arithmetic.

## Forbidden Inputs

Next-Prime Law 003 must not use:

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
- hardcoded prime outputs;
- the fact that `17` is classically prime.

The string `17` may appear only as the proposed endpoint in the law probe. It
must not be used as a known prime.

## Proposed Chamber Certificate

For the proposed interior:

$$I = \{14, 15, 16\}$$

the concrete composite witnesses are:

- `14 = 2 * 7`, so `d(14) = 4`;
- `15 = 3 * 5`, so `d(15) = 4`;
- `16 = 2^4`, so `d(16) = 5`.

The minimum divisor class inside the proposed chamber is:

$$d_{min} = 4$$

The leftmost carrier of that class is:

$$w = 14$$

The selection metadata is:

- `winner_carrier_w: 14`
- `winner_offset: 1`
- `winner_divisor_count: 4`
- `winner_family: "semiprime"`

This is the first meaningful carrier-bearing certificate in the Milestone 1
sequence.

## GWR Compatibility

The GWR requirement for the proposed chamber is satisfied at the certificate
level:

- every interior point has an explicit composite witness;
- the interior divisor counts are known from those witnesses;
- the minimum divisor class is `4`;
- the leftmost minimum-class carrier is `14`.

This proves that the proposed chamber has coherent GWR structure. It does not
by itself prove that the chamber endpoint is forced at `17`.

## No-Later-Simpler Closure

Inside the proposed chamber after the selected integer:

- `15` has divisor count `4`, not lower than the selected integer;
- `16` has divisor count `5`, not lower than the selected integer.

There is no later lower-divisor interior threat before the proposed endpoint.

The local no-later-simpler status is:

- `closure_status: "no_later_simpler_inside_proposed_chamber"`
- `threat_margin: null`

This is an interior closure statement. It does not yet rule out a lower-divisor
threat after `17` if the chamber were allowed to continue.

## Competing Endpoint Analysis

The proposed endpoint `17` is wheel-open from anchor `13` at offset `4`.

Earlier positive offsets are:

- offset `1`: `14`, closed by concrete composite witness;
- offset `2`: `15`, closed by concrete composite witness;
- offset `3`: `16`, closed by concrete composite witness.

Therefore no smaller candidate next prime remains inside the proposed chamber.

This establishes:

- the proposed interior is closed;
- the proposed chamber has a GWR-selected integer;
- no smaller offset in the proposed chamber can be the endpoint.

It does not establish that the first position after the closed carrier-bearing
chamber is uniquely forced as the right endpoint.

## Endpoint Uniqueness Gap

The current certificate still separates three statements:

- `14`, `15`, and `16` are composite interior points;
- `14` is the GWR-compatible leftmost minimum carrier;
- `17` is the first candidate after the closed proposed chamber.

The missing implication is:

$$\text{closed carrier-bearing chamber with no later simpler interior threat} \Rightarrow \text{forced next prime}$$

That implication is stronger than chamber consistency. It is not proved here.

## Current Status

Next-Prime Law 003 does not yet emit.

For the anchor-13 probe:

- `closure_status: "carrier_chamber_closed"`
- `competing_boundary_status: "no_smaller_candidate_inside_chamber"`
- `uniqueness_status: "unresolved"`
- `inference_status: "failed_closed"`
- `failure_reason: "MISSING_CARRIER_BOUNDARY_UNIQUENESS"`

The law succeeds at finding the first structurally meaningful PGS chamber. It
fails to prove that the chamber structure forces the right endpoint.

## Emission Rule

Pure mode may emit under `boundary_law_003` only when:

1. the proposed interior has deterministic composite certificates;
2. the proposed interior has a GWR-compatible selected integer;
3. later lower-divisor threats are excluded or bounded by PGS structure;
4. all smaller proposed endpoint positions are closed;
5. a carrier-bearing uniqueness theorem forces `q_hat`.

Until those five conditions hold, pure mode must emit a failure record.

## Failure Contract

If the carrier selected integer cannot be established, emit:

- `rule_set_version: "boundary_law_003"`
- `inference_status: "failed_closed"`
- `failure_reason: "NO_GWR_CARRIER"`

If the proposed interior cannot be fully closed, emit:

- `rule_set_version: "boundary_law_003"`
- `inference_status: "failed_closed"`
- `failure_reason: "INCOMPLETE_CHAMBER_CERTIFICATE"`

If lower-divisor threats remain unresolved, emit:

- `rule_set_version: "boundary_law_003"`
- `inference_status: "failed_closed"`
- `failure_reason: "UNRESOLVED_THREAT_CLOSURE"`

If the uniqueness theorem is missing, emit:

- `rule_set_version: "boundary_law_003"`
- `inference_status: "failed_closed"`
- `failure_reason: "MISSING_CARRIER_BOUNDARY_UNIQUENESS"`

## Next Search Direction

Next-Prime Law 003 shows that moving to a carrier-bearing chamber fixes the
degeneracy of the anchor-11 case, but it does not by itself solve endpoint
uniqueness.

The next proof task is to determine whether GWR/DNI plus no-later-simpler
closure can force a endpoint, or whether the current certificates only validate
candidate chambers after a proposed endpoint has already been chosen.

If the latter is true, the missing theorem is not anchor-specific. It is a
general bridge from chamber consistency to next-prime inference.
