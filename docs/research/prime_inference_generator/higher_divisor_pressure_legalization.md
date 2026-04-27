# Higher-Divisor Pressure Legalization

The exact higher-divisor pressure states separated next-prime offsets on the
tested surface, but they are not lawful generator states. They use exact divisor
buckets across the prefix, and those buckets include `d = 2` prime-marker
identity.

Next-Prime Law 005 is not approved by this note.

## Objective

Recover a legal shadow of the higher-divisor signal without using:

- exact factorization;
- prime markers;
- future next-prime offset;
- scan-to-first-prime behavior;
- `d = 2` recognition;
- full divisor-count ladders;
- the old recursive walker.

The probe is offline theorem discovery. It may attach classical next-gap labels
for collision measurement, but the candidate state vectors are separately
marked for pure-generation eligibility.

## Instrument

Script:

- `benchmarks/python/prime_inference_generator/higher_divisor_pressure_forensics.py`

Artifacts:

- `higher_divisor_pressure_forensics_summary.json`
- `higher_divisor_pressure_forensics_exact_states.jsonl`
- `higher_divisor_pressure_forensics_candidates.jsonl`

Each exact-state audit records:

- `state_vector_name`
- `collision_count`
- `eligible_for_pure_generation`
- `ineligibility_reasons`
- `uses_exact_factorization`
- `uses_prime_marker`
- `uses_future_boundary`
- `uses_scan_to_first_prime`
- `uses_d2_recognition`
- `uses_full_divisor_count`
- `uses_old_walker`
- `feature_components`
- `component_ablation_results`
- `minimal_illegal_component`

## Exact States Audited

The exact contaminated states are:

- `higher_divisor_pressure_state`
- `previous_chamber_plus_higher_divisor_pressure_state`
- `previous_chamber_plus_square_and_higher_pressure_state`

The audited components are:

- legal context: input prime residue, first-open offset, previous-gap bucket when
  present;
- legal square context when present;
- illegal higher-divisor context: `high_divisor_count`,
  `high_divisor_offsets`, and `divisor_bucket_ladder`.

## Legalization Candidates

The probe tests these legal approximations:

- `wheel_closed_density_pressure`
- `small_factor_witness_pressure`
- `bounded_composite_witness_pressure`
- `power_signature_pressure`
- `square_cube_power_pressure`
- `multiplicity_pressure_without_primality`
- `residue_class_pressure`
- `early_composite_run_pressure`

These states record known composite witnesses or integer power structure. They
do not classify an open position as prime when no witness is found.

## Results

Surface:

- input primes: `11..10_000`
- prefix: `32`
- rows: `1225`

Exact-state audit:

- `higher_divisor_pressure_state`: `0` collisions;
  `minimal_illegal_component: divisor_bucket_ladder`.
- `previous_chamber_plus_higher_divisor_pressure_state`: `0` collisions;
  no single necessary illegal component on this smaller surface.
- `previous_chamber_plus_square_and_higher_pressure_state`: `0` collisions;
  no single necessary illegal component on this smaller surface.

Legal candidate results:

- `bounded_composite_witness_pressure`: `0` collisions.
- `power_signature_pressure`: `0` collisions.
- `multiplicity_pressure_without_primality`: `0` collisions.
- `small_factor_witness_pressure`: `215` collisions.
- `wheel_closed_density_pressure`: `30` collisions.
- `square_cube_power_pressure`: `97` collisions.
- `residue_class_pressure`: `129` collisions.
- `early_composite_run_pressure`: `76` collisions.

Surface:

- input primes: `11..100_000`
- prefix: `32`
- rows: `9588`

Exact-state audit:

- `higher_divisor_pressure_state`: `0` collisions;
  `minimal_illegal_component: divisor_bucket_ladder`.
- `previous_chamber_plus_higher_divisor_pressure_state`: `0` collisions;
  `minimal_illegal_component: divisor_bucket_ladder`.
- `previous_chamber_plus_square_and_higher_pressure_state`: `0` collisions;
  `minimal_illegal_component: divisor_bucket_ladder`.

Removing `divisor_bucket_ladder` produces:

- `236` collisions for `higher_divisor_pressure_state`;
- `90` collisions for `previous_chamber_plus_higher_divisor_pressure_state`;
- `2` collisions for
  `previous_chamber_plus_square_and_higher_pressure_state`.

The smallest exposed illegal component is therefore:

- `divisor_bucket_ladder`

Legal candidate results on input primes `11..100_000`, prefix `32`:

- `bounded_composite_witness_pressure`: `0` collisions.
- `power_signature_pressure`: `0` collisions.
- `multiplicity_pressure_without_primality`: `0` collisions.
- `small_factor_witness_pressure`: `1331` collisions.
- `wheel_closed_density_pressure`: `37` collisions.
- `square_cube_power_pressure`: `228` collisions.
- `residue_class_pressure`: `202` collisions.
- `early_composite_run_pressure`: `1749` collisions.

The first zero-collision eligible state reported by the probe is:

- `bounded_composite_witness_pressure`

## Interpretation

The exact higher-divisor signal is carried by `divisor_bucket_ladder`. That
component is illegal because it contains full divisor buckets and marks `d = 2`
positions. The previous-square context can reduce the damage after ablation,
but it does not remove the illegal dependency.

Three legal approximations reached zero collisions on input primes `11..100_000`,
prefix `32`:

- bounded composite witnesses;
- integer power signature;
- fixed-small-factor multiplicity without primality.

These are candidate signals, not a next-prime-forcing theorem. They need a
separate anti-leakage and anti-table audit before any Next-Prime Law 005 note is
allowed. In particular, power offsets and bounded witness ladders must be
checked for disguised input prime identity, hidden primality classification, and
future-endpoint leakage.

## Status

Milestone 1 remains blocked.

Next-Prime Law 005 is not approved.

The next admissible work item is a focused legality stress test for the three
zero-collision eligible candidates:

- `bounded_composite_witness_pressure`
- `power_signature_pressure`
- `multiplicity_pressure_without_primality`
