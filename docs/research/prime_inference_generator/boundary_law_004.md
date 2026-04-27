# Next-Prime Law 004: First Endpoint-Forcing Predicate

Endpoint Laws 001 through 003 tested search interval certification. They did not produce
a lawful output because search-interval consistency is not endpoint force. Endpoint
Law 004 changes the target: identify a predicate that makes the search interval stop.

This note surveys candidate next-prime-forcing predicates under the pure
generation contract. It does not output a value. Its status is
`BOUNDARY_FORCING_REQUIRES_NEW_THEOREM`.

## Name

First Endpoint-Forcing Predicate.

The law asks for a deterministic PGS predicate that takes input prime and search interval
state and returns a unique `q_hat` without primality testing, next-prime lookup,
or next-prime discovery by scanning to `d(n) = 2`.

## Required Predicate Contract

A next-prime-forcing predicate must:

- start from an externally supplied input prime `p`;
- use only PGS-computable search-interval state;
- identify a unique next-prime offset;
- distinguish a forced endpoint from an admissible candidate;
- fail closed when the endpoint is not unique;
- output enough metadata to reproduce the inference.

It must not assume the proposed interval endpoint and then merely verify that the
interior is coherent.

## Forbidden Mechanisms

Next-Prime Law 004 rejects any predicate that outputs because:

- the endpoint is classically known;
- the candidate is first wheel-open;
- the proposed interval is internally coherent;
- there is no smaller candidate next prime inside the assumed search interval;
- the old recursive walker finds the endpoint;
- a scan reaches `d(n) = 2`;
- trial division, sieve generation, Miller-Rabin, `isprime`, or `nextprime`
  identifies the endpoint.

The standard is unchanged: PGS must force `q_hat`; audit only confirms
afterward.

## Candidate 1: First Post-Integer Admissible Closure

Statement:

After a GWR-selected integer is established, the first admissible open offset satisfying
local closure constraints is forced as the right endpoint.

Input-prime-13 probe:

- integer: `w = 14`;
- divisor class: `d(w) = 4`;
- later proposed interior points: `15`, `16`;
- first post-search interval open candidate: `17`.

What it establishes:

- the search interval has a integer;
- no smaller endpoint inside the proposed interval survives;
- local interior closure is coherent.

What remains missing:

- a proof that the first admissible post-integer closure point must be the
  endpoint;
- a rule that distinguishes first admissible post-integer candidate from a
  later endpoint without checking primality.

Status:

`FAILED_CLOSED`

Failure reason:

`FIRST_POST_CARRIER_ADMISSIBILITY_NOT_FORCE`

## Candidate 2: Threat-Margin Closure

Statement:

The endpoint must occur before the first later lower-divisor threat overtakes
the GWR-selected integer.

For a selected integer `w`, define:

$$T_{<}(w) = \min \{m > w : d(m) < d(w)\}$$

The closure condition is:

$$q < T_{<}(w)$$

What it establishes:

- a valid upper constraint on the endpoint when `T_{<}(w)` is known;
- a no-later-simpler interval in which the endpoint must lie;
- a useful threat margin after a proposed `q_hat` is known.

What remains missing:

- a unique endpoint point inside the interval;
- a way to compute the endpoint without searching for primality;
- a reason that one admissible point in the interval is forced over another.

Status:

`FAILED_CLOSED`

Failure reason:

`THREAT_MARGIN_BOUNDS_INTERVAL_NOT_POINT`

## Candidate 3: DNI Fixed-Point Endpoint

Statement:

A endpoint occurs where the normalized search interval transition reaches the prime
fixed-point locus, without classical primality testing.

The desired predicate would map search-interval state to a unique offset:

$$B(p, S, w, d(w)) = q_{hat}$$

where `S` is the PGS state and `w` is the active integer.

What it establishes:

- a plausible form for a true next-prime-forcing law;
- a direct path from normalized search-interval state to endpoint output if solved.

What remains missing:

- the actual invariant equation or transition law that returns one offset;
- proof that the returned offset is unique;
- a worked input prime where the returned offset is derived without using a known
  prime endpoint.

Status:

`BOUNDARY_FORCING_REQUIRES_NEW_THEOREM`

Failure reason:

`NO_DNI_FIXED_POINT_BOUNDARY_MAP`

## Candidate 4: Recursive Witness Closure

Statement:

Once `d_min` and selected-integer offset are known, a deterministic witness map returns a
candidate next prime without calling `nextprime`.

What it establishes:

- a possible implementation shape for a pure next-prime selection rule;
- a route from interior selected-integer metadata to a next-prime offset.

What remains missing:

- a witness map that is not trained on, derived from, or validated inline by
  classical next-prime discovery;
- a proof that the witness map returns a unique endpoint;
- evidence that the map is not only replaying known prime gaps.

Status:

`FAILED_CLOSED`

Failure reason:

`NO_PURE_RECURSIVE_WITNESS_MAP`

## Candidate 5: Finite-State Transition Law

Statement:

A reduced gap-type or search interval-state model predicts the next prime offset
from state transitions rather than primality detection.

What it establishes:

- a possible compressed symbolic route to next-prime inference;
- a natural place to encode recurring GWR/DNI search interval regimes.

What remains missing:

- a finite state whose transition output is a next-prime offset, not just a gap
  type or consistency label;
- exact recovery without classical feedback during generation;
- a proof that the state transition is deterministic and unique for the active
  search interval.

Status:

`FAILED_CLOSED`

Failure reason:

`FINITE_STATE_BOUNDARY_OUTPUT_UNPROVED`

## Current Result

No candidate predicate in this note currently forces a endpoint.

The strongest supported result is:

PGS search-interval diagnostic records can establish interior closure, GWR-selected integers,
leftmost-minimum integers, and local no-later-simpler consistency. They do not
yet imply a unique next prime.

Status:

`BOUNDARY_FORCING_REQUIRES_NEW_THEOREM`

## Missing Theorem

The missing theorem is a next-prime-forcing theorem external to search interval
certification:

$$\text{PGS search-interval state} \Rightarrow \text{unique right endpoint offset}$$

For a selected-integer-bearing search interval, the desired form is:

$$B(p, S, w, d(w)) = q_{hat}$$

where `B` is deterministic, non-classical, and fails when the state is
ambiguous.

## Output Rule

Pure mode may output under `boundary_law_004` only if one candidate predicate is
upgraded from a diagnostic record or bound into a unique next-prime map.

Until then, pure mode must output:

- `rule_set_version: "boundary_law_004"`
- `inference_status: "failed_closed"`
- `failure_reason: "BOUNDARY_FORCING_REQUIRES_NEW_THEOREM"`

## Next Search Direction

The next research task is not another small search-interval diagnostic record. It is to search
for the missing function:

$$B(p, S, w, d(w))$$

The most promising paths are:

- derive a DNI fixed-point next-prime map;
- find a pure recursive witness map that is not classical next-prime discovery;
- prove a finite-state transition law that outputs next-prime offsets exactly.

If none of these closes, the result is still clean: GWR/DNI currently describes
and constrains proposed intervals, but a separate next-prime-forcing theorem is
needed before pure prime inference can output.
