# Legal Ladder Collision Forensics

The legal ladder search found no eligible zero-collision state on the meaningful
surfaces. The next question is what the contaminated perfect ladder knows that
the legal ladder does not.

This note records the first forensic run:

- anchors: `11..10_000`
- prefix: `8`
- legal state: `known_composite_divisor_ladder`
- collision buckets inspected: first `10`

The run is offline theorem discovery. It does not change the pure generator and
does not authorize Next-Prime Law 005.

## Result

The legal state has collisions:

- rows: `1225`
- collision buckets: `29`
- inspected buckets: `10`

The first `10` collision buckets are separated by illegal prime-marker
information:

- `prime_marker_positions`: `10/10`
- `prime_marker_masked_ladder`: `10/10`
- `contaminated_carrier_identity`: `9/10`
- `previous_gap_width`: `8/10`

The repeated missing observable is not a legal composite-structure token. It is
the prime-marker structure itself.

## Interpretation

The contaminated `carrier_ladder` and `previous_gap_ladder` states distinguish
colliding legal states because they know where prime-position masks occur inside
the prefix. That is exactly the information pure generation is not allowed to
use.

The current legal ladder does not merely need more collision testing. It needs a
PGS-native observable that can replace the separating power of prime-marker
positions without identifying primes.

## Next-Prime Law 005 Status

Next-Prime Law 005 is not approved.

Current status:

- `first_zero_collision_eligible_state_vector: null`
- `candidate_missing_observable: prime_marker_positions`
- `inference_status: "blocked"`

## Next Candidate Families

The next legal feature family should not reintroduce prime markers. The next
reasonable candidates are:

- `legal_ladder_plus_square_pressure`
- `legal_ladder_plus_semiprime_pressure`
- `legal_ladder_plus_threat_schedule`

Each candidate must remain eligible for pure generation and must be tested
against the same collision-forensics gate.
