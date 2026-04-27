# Endpoint Forcing Theorem Search

Endpoint Laws 001 through 004 isolate the live blocker for the PGS Prime
Inference Generator. The pure scaffold is clean. The search-interval diagnostic records are
real. The missing ingredient is a theorem that turns PGS search-interval data into a
unique next prime.

The theorem search target is:

$$PGS\ search interval\ data \Rightarrow unique\ next\ endpoint$$

No candidate in this note is installed as a generator rule. The work here is
offline theorem discovery.

## Current Status

Milestone 1 remains blocked.

The strongest supported result is:

PGS search-interval diagnostic records can certify interior closure, GWR-selected integers,
leftmost-minimum integers, and local no-later-simpler consistency. They do not
yet force a unique next prime.

This means GWR is currently an interior maximizer rule. It is not yet a endpoint
generation law.

## Theorem Family 1: First-Open Endpoint Theorem

Claim form:

$$closed\ preopen\ search interval \Rightarrow first\ wheel-open\ candidate\ is\ endpoint$$

This is the theorem family behind Next-Prime Law 001 and the empty input-prime-11
probe.

Current status:

`FAILED_CLOSED`

Reason:

First wheel-open admissibility identifies a candidate. It does not force that
candidate to be the next prime.

Kill condition:

Any known input prime where the first wheel-open candidate is composite kills the
unqualified theorem. A surviving version would need additional PGS conditions
that do more than wheel admissibility.

## Theorem Family 2: Integer-Lock Endpoint Theorem

Claim form:

$$GWR\ integer + no\ later\ lower-divisor\ threat\ up\ to\ candidate\ q \Rightarrow q\ is\ endpoint$$

This is the theorem family behind Next-Prime Law 003 and the input prime-13 integer
probe.

Current status:

`FAILED_CLOSED`

Reason:

The selected-integer-lock diagnostic record establishes coherence inside a proposed interval. It
does not prove that the proposed interval must stop at the candidate next prime.

Kill condition:

Two different admissible candidate next primes with internally coherent integer
diagnostic records refute the unqualified theorem. A surviving version must identify
which candidate is forced and why.

## Theorem Family 3: Transition-State Endpoint Theorem

Claim form:

$$S(p) \Rightarrow g(p)$$

Here `S(p)` is a PGS state vector computed from allowed local or recursive
structure around input prime `p`, and `g(p)` is the next prime offset.

This is the most promising family because endpoint force may live between
search intervals rather than inside one proposed interval.

Current status:

`OPEN_THEOREM_SEARCH`

Reason:

The right object may be a deterministic transition state, not a self-certifying
search interval. A candidate state vector must map to one next-gap width on tested
surfaces before it can become a theorem candidate.

Kill condition:

The same allowed PGS state mapping to multiple next-next-prime offsets kills that
state vector. If all reasonable local state vectors collide, the theorem needs
longer memory, larger deterministic state, or a different invariant.

## Candidate State Ingredients

The transition-state search should test deterministic state vectors built from:

- input prime residue modulo the wheel;
- first-open offset;
- first selected-integer family;
- first selected divisor count;
- first selected-integer offset;
- early divisor ladder shape excluding prime-endpoint detection;
- lower-divisor threat schedule;
- previous gap state;
- previous GWR-selected integer type;
- semiprime-wheel attractor state.

The initial probe should start small. A state conflict is not a failure of the
project. It is information about which data cannot force a endpoint.

## Legal Ladder State Vectors

The contaminated ladder states use prime-marker masking. The legal ladder search
therefore adds state vectors that do not identify primes:

- `wheel_open_pattern`;
- `open_unknown_ladder`;
- `composite_witness_ladder`;
- `known_composite_divisor_ladder`;
- `carrier_ladder_no_prime_mask`;
- `carrier_plus_open_unknown_ladder`;
- `previous_gap_ladder_no_prime_mask`.

These states encode wheel-open positions as `OPEN_UNKNOWN`. They encode
wheel-closed positions with wheel-basis witness tokens such as `CLOSED_BY_2`.
They use exact divisor-class tokens such as `C5` only when the wheel-basis
factors fully determine the divisor count. They do not mark an offset as prime.

## Offline Probe Contract

The transition-state probe is not the generator. It may use classical labels
because it is theorem discovery.

The probe must:

1. Walk known validated prime gaps on a finite surface.
2. Compute candidate PGS state vectors for each input prime.
3. Attach the classical next gap width as a label.
4. Group rows by state vector.
5. Report conflicts where one state maps to multiple next-prime offsets.
6. Report the first tested state vector with zero conflicts, if one exists.

Output fields:

- `state_vector`
- `row_count`
- `distinct_state_count`
- `collision_count`
- `collision_examples`
- `max_bucket_size`
- `zero_collision`
- `uses_boundary_offset`
- `uses_gap_width`
- `uses_prime_marker_d2`
- `uses_stop_at_first_prime`
- `uses_nextprime_or_isprime`
- `boundary_offset_within_prefix_rate`
- `state_contains_boundary_token_rate`
- `eligible_for_pure_generation`
- `zero_collision_and_eligible`

This does not violate the pure generator contract. It is offline theorem
search. Any candidate found here must still be turned into a pure next-prime law
before generation can output a value.

## Leakage Audit Gate

Zero conflicts are not enough. A state vector is disqualified as a pure
generation candidate if it includes the next-prime offset, the current gap width,
prime-marker tokens, stop-at-first-prime behavior, `nextprime`, `isprime`, or an
equivalent endpoint-discovery mechanism.

For now, any state vector that uses `d = 2` or a masked prime-position token
inside the prefix is marked:

- `eligible_for_pure_generation: false`

That mark does not make the offline probe invalid. It keeps theorem discovery
separate from lawful generation.

## Current Legal Ladder Result

The first legal ladder expansion tested input primes `11..200`, `11..10_000`, and
`11..100_000` across prefixes `8, 12, 16, 24, 32`.

The contaminated `carrier_ladder` and `previous_gap_ladder` states keep zero
conflicts on these surfaces, but they remain ineligible because they use
prime-marker masking.

The legal shadow states do not yet supply a Next-Prime Law 005 candidate:

- `11..200`, prefix `12`: `known_composite_divisor_ladder` has zero conflicts;
- `11..10_000`, all tested prefixes: no eligible zero-conflict state;
- `11..100_000`, all tested prefixes: no eligible zero-conflict state.

The current result is:

- `first_zero_collision_eligible_state_vector: null`
- Milestone 1 remains blocked.

This indicates that the currently perfect ladder signal depends on illegal
prime-marker information. The legal shadow of that signal has not yet been
found.

## Next Next-Prime Law Candidate

If the transition-state probe finds a zero-conflict state vector on a meaningful
surface, the next candidate is:

Next-Prime Law 005: Finite Transition Next-Prime Law.

That law would still need to prove that the state vector is structurally valid
and not just fitted to classical labels.

## Current Conclusion

The next work is theorem discovery, not positive output.

Milestone 1 remains blocked until the project finds a next-prime-forcing theorem:

$$S(p) \Rightarrow g(p)$$

where `S(p)` is non-classical PGS state and `g(p)` is the unique next prime
offset.
