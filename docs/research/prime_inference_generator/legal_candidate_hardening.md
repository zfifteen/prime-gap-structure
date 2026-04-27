# Legal Candidate Hardening

The first legal higher-divisor shadows did not survive the hardening gate.

The strongest conflict result belongs to
`multiplicity_pressure_without_primality`: it has zero conflicts on every
tested surface below. Its anti-table profile is decisive, however. It produces
one distinct state for every input prime on every tested surface:

- `distinct_state_ratio: 1.0`
- `singleton_bucket_rate: 1.0`
- `max_bucket_size: 1`

That is not acceptable endpoint-law evidence. It is a table-like state.

Next-Prime Law 005 is not approved by this note.

## Objective

Test the three legal zero-conflict signals from higher-divisor pressure
legalization:

- `bounded_composite_witness_pressure`
- `power_signature_pressure`
- `multiplicity_pressure_without_primality`

The probe checks both conflict behavior and anti-table behavior. A candidate
must not merely separate labels; it must do so without becoming a near-unique
input prime fingerprint.

## Instrument

Script:

- `benchmarks/python/prime_inference_generator/legal_candidate_hardening_probe.py`

Artifacts:

- `legal_candidate_hardening_summary.json`
- `legal_candidate_hardening_candidates.jsonl`

Each candidate report records:

- `candidate_name`
- `eligible_for_pure_generation`
- `row_count`
- `distinct_state_count`
- `distinct_state_ratio`
- `collision_count`
- `collision_rate`
- `max_bucket_size`
- `mean_bucket_size`
- `singleton_bucket_count`
- `singleton_bucket_rate`
- `state_entropy_estimate`
- `uses_anchor_value`
- `uses_future_boundary`
- `uses_prime_marker`
- `uses_full_divisor_count`
- `uses_exact_factorization`
- `uses_scan_to_first_prime`
- `uses_old_walker`
- `first_collision_examples`
- `table_like_state`
- `hardening_gate_status`
- `passes_hardening_gate`

The hardening gate marks a zero-conflict candidate as quarantined when
`distinct_state_ratio >= 0.95` or `singleton_bucket_rate >= 0.95`.

## Surfaces

The required hardening surfaces were:

- input primes `11..100_000`, prefix `32`
- input primes `11..1_000_000`, prefix `32`
- input primes `11..1_000_000`, prefix `16`
- input primes `11..1_000_000`, prefix `64`
- input primes `100_000..200_000`, prefix `32`
- input primes `1_000_000..1_100_000`, prefix `32`

## Results

### Input Primes 11..100,000, Prefix 32

Rows: `9588`

| Candidate | Conflicts | Distinct Ratio | Singleton Rate | Status |
|---|---:|---:|---:|---|
| `multiplicity_pressure_without_primality` | `0` | `1.0` | `1.0` | `quarantined_table_like_state` |
| `power_signature_pressure` | `0` | `1.0` | `1.0` | `quarantined_table_like_state` |
| `bounded_composite_witness_pressure` | `0` | `1.0` | `1.0` | `quarantined_table_like_state` |

Hardening candidates: none.

### Input Primes 11..1,000,000, Prefix 32

Rows: `78494`

| Candidate | Conflicts | Distinct Ratio | Singleton Rate | Status |
|---|---:|---:|---:|---|
| `multiplicity_pressure_without_primality` | `0` | `1.0` | `1.0` | `quarantined_table_like_state` |
| `power_signature_pressure` | `8` | `0.99986` | `0.99986` | `failed_collision_gate` |
| `bounded_composite_witness_pressure` | `2` | `0.999949` | `0.999949` | `failed_collision_gate` |

Hardening candidates: none.

### Input Primes 11..1,000,000, Prefix 16

Rows: `78494`

| Candidate | Conflicts | Distinct Ratio | Singleton Rate | Status |
|---|---:|---:|---:|---|
| `multiplicity_pressure_without_primality` | `0` | `1.0` | `1.0` | `quarantined_table_like_state` |
| `power_signature_pressure` | `9` | `0.999834` | `0.999834` | `failed_collision_gate` |
| `bounded_composite_witness_pressure` | `329` | `0.993668` | `0.993718` | `failed_collision_gate` |

Hardening candidates: none.

### Input Primes 11..1,000,000, Prefix 64

Rows: `78494`

| Candidate | Conflicts | Distinct Ratio | Singleton Rate | Status |
|---|---:|---:|---:|---|
| `multiplicity_pressure_without_primality` | `0` | `1.0` | `1.0` | `quarantined_table_like_state` |
| `power_signature_pressure` | `8` | `0.99986` | `0.99986` | `failed_collision_gate` |
| `bounded_composite_witness_pressure` | `0` | `1.0` | `1.0` | `quarantined_table_like_state` |

Hardening candidates: none.

### Input primes 100,000..200,000, Prefix 32

Rows: `8392`

| Candidate | Conflicts | Distinct Ratio | Singleton Rate | Status |
|---|---:|---:|---:|---|
| `multiplicity_pressure_without_primality` | `0` | `1.0` | `1.0` | `quarantined_table_like_state` |
| `power_signature_pressure` | `0` | `1.0` | `1.0` | `quarantined_table_like_state` |
| `bounded_composite_witness_pressure` | `0` | `1.0` | `1.0` | `quarantined_table_like_state` |

Hardening candidates: none.

### Input primes 1,000,000..1,100,000, Prefix 32

Rows: `7216`

| Candidate | Conflicts | Distinct Ratio | Singleton Rate | Status |
|---|---:|---:|---:|---|
| `multiplicity_pressure_without_primality` | `0` | `1.0` | `1.0` | `quarantined_table_like_state` |
| `power_signature_pressure` | `0` | `1.0` | `1.0` | `quarantined_table_like_state` |
| `bounded_composite_witness_pressure` | `0` | `1.0` | `1.0` | `quarantined_table_like_state` |

Hardening candidates: none.

## Interpretation

The conflict evidence did not promote a Next-Prime Law 005 candidate.

`power_signature_pressure` and `bounded_composite_witness_pressure` fail the
conflict gate on the full `11..1_000_000` surface for at least one tested
prefix.

`multiplicity_pressure_without_primality` keeps zero conflicts, but it also
keeps a fully singleton state partition. The state is too specific to count as
a reusable transition law. Its zero-conflict result is quarantined as
table-like evidence.

The legal candidate family therefore remains useful as a diagnostic signal, but
not as a next-prime-forcing law.

## Status

Milestone 1 remains blocked.

Next-Prime Law 005 is not approved.

The next admissible search should reduce state dimensionality before testing
new mathematics. A lower-resolution multiplicity or witness-pressure state
would be preferable to adding more features.
