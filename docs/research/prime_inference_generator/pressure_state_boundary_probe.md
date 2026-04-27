# Pressure-State Endpoint Probe

The legal ladder conflict forensics showed that direct ladder recovery is
blocked by missing prime-marker structure. The next theorem-search target is a
different class of observable: pressure states.

The pressure-state probe is offline theorem discovery. It does not change the
pure generator and does not authorize Next-Prime Law 005.

## Objective

Find a PGS-native pressure observable that can separate next-prime offsets without
using prime-marker identity, next-prime lookup, future next-prime offset, or a
hidden endpoint scan.

## Tested State Families

The initial probe tests:

- `square_pressure_state`
- `semiprime_pressure_state`
- `higher_divisor_pressure_state`
- `threat_schedule_state`
- `previous_chamber_pressure_state`
- `carrier_plus_pressure_state`

Every state reports:

- `eligible_for_pure_generation`
- `row_count`
- `distinct_state_count`
- `collision_count`
- `collision_rate`
- `first_collision_examples`
- `zero_collision`

The summary also reports:

- `first_zero_collision_eligible_state_vector`

## Legality Rule

Exact semiprime, exact divisor, and exact threat states are useful theorem
discovery probes, but they are not automatically legal for pure generation.

A state is ineligible if it uses:

- future next-prime offset;
- current gap width;
- prime-marker identity or `d = 2`;
- stop-at-first-prime behavior;
- `nextprime` or `isprime` as a state feature;
- exact factorization not available as a PGS-native observable.

Previous-search-interval pressure is treated as conditionally legal for recursive
generation because a prior accepted endpoint can carry previous-gap context
forward. It is not a first-input prime endpoint theorem by itself.

## Initial Surface

The first approved surface is:

- input primes: `11..10_000`
- prefix: `8`

If no eligible zero-conflict pressure state appears on that surface, Endpoint
Law 005 remains blocked.

## Initial Result

The first run used input primes `11..10_000` with prefix `8`.

No eligible zero-conflict pressure state appeared:

- `first_zero_collision_eligible_state_vector: null`

Conflict counts:

- `square_pressure_state`: `268`
- `previous_chamber_pressure_state`: `30`
- `carrier_plus_pressure_state`: `224`

The exact semiprime, higher-divisor, and threat-schedule states also collided,
and they are ineligible as pure-generation states because they use exact
factorization, `d = 2`, `isprime`, or equivalent non-pure information.

Next-Prime Law 005 remains blocked.

## Combined-State Result

The next run tested combined previous-search-interval states:

- `previous_chamber_plus_square_pressure_state`
- `previous_chamber_plus_higher_divisor_pressure_state`
- `previous_chamber_plus_threat_schedule_state`
- `previous_chamber_plus_square_and_higher_pressure_state`
- `previous_chamber_plus_square_and_threat_state`

Surfaces:

- input primes `11..10_000`, prefix `8`
- input primes `11..100_000`, prefixes `8, 12, 16, 24, 32`

The legal candidate did not close:

- `previous_chamber_plus_square_pressure_state`, `11..10_000`, prefix `8`:
  `224` conflict buckets;
- `previous_chamber_plus_square_pressure_state`, `11..100_000`, prefix `32`:
  `2056` conflict buckets.

The first zero-conflict eligible state remains:

- `first_zero_collision_eligible_state_vector: null`

The ineligible exact higher-divisor variants became strong theorem-search
signals:

- `previous_chamber_plus_higher_divisor_pressure_state`, `11..100_000`,
  prefix `32`: `0` conflicts;
- `previous_chamber_plus_square_and_higher_pressure_state`, `11..100_000`,
  prefix `32`: `0` conflicts.

Those states are not Next-Prime Law 005 candidates because they use exact
divisor/prime-marker internals. They indicate that higher-divisor pressure may
be the next observable to legalize.
