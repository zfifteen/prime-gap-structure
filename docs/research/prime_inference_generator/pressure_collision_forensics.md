# Pressure Collision Forensics

The first pressure-state probe found no eligible zero-collision state on anchors
`11..10_000`, prefix `8`. The closest legal signal was
`previous_chamber_pressure_state`, with `30` collision buckets.

This note records the next forensic target: inspect those collisions directly
instead of adding new state families blindly.

## Target

- anchors: `11..10_000`
- prefix: `8`
- state: `previous_chamber_pressure_state`
- collision buckets: all

## Minimum Artifact Fields

Each collision bucket records:

- `boundary_offsets_observed`
- `anchors_by_bucket`
- `shared_previous_state`
- `legal_feature_deltas`
- `candidate_missing_observable`

The summary records:

- `collision_bucket_count`
- `written_collision_bucket_count`
- `candidate_missing_observable_counts`

## Interpretation Rule

The next state family should be selected from the repeated missing observables,
not guessed. If the collisions are mostly separated by current legal ladder or
square pressure, the next probe should combine those with previous-chamber
state. If they require exact semiprime or exact divisor pressure, the result is
useful but not yet pure-eligible.

Next-Prime Law 005 remains blocked until a legal state reaches zero collisions on
the meaningful surface.

## Result

The run over anchors `11..10_000`, prefix `8`, state
`previous_chamber_pressure_state` found:

- `row_count: 1225`
- `collision_bucket_count: 30`
- `written_collision_bucket_count: 30`

Candidate missing observable counts:

- `square_pressure_plus_previous_chamber`: `30`
- `semiprime_pressure_plus_previous_chamber`: `30`
- `previous_plus_exact_carrier_pressure`: `30`
- `higher_divisor_pressure_plus_previous_chamber`: `29`
- `previous_plus_threat_schedule`: `29`
- `previous_gap_width_class`: `16`

The strongest legal next candidate is `previous_chamber_plus_square_pressure`.
It varies in every collision bucket and does not require prime-marker identity,
future next-prime offset, or exact factorization. Exact semiprime, integer, and
threat-schedule variants also separate the collisions, but they are not
pure-eligible in their current form.

Next-Prime Law 005 remains blocked until the combined state is tested and reaches
zero collisions on the meaningful surface.
