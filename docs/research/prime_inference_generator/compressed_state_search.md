# Compressed Legal State Search

The first compression search did not produce a Next-Prime Law 005 candidate.

The result is a clean frontier:

- zero-collision compressed states still have no bucket reuse;
- states with measurable compression introduce endpoint-offset collisions.

Next-Prime Law 005 is not approved by this note.

## Objective

The rejected `multiplicity_pressure_without_primality` signal was legal-looking
and collision-free, but it produced one distinct state per input prime. This probe
coarsens that signal and asks whether any compressed version can keep the
endpoint labels separated while grouping many input primes into reusable buckets.

A candidate must satisfy both:

- low or zero endpoint-offset collisions;
- nontrivial state compression.

## Instrument

Script:

- `benchmarks/python/prime_inference_generator/compressed_state_search.py`

Artifacts:

- `compressed_state_search_summary.json`
- `compressed_state_search_candidates.jsonl`

Each candidate report records:

- `candidate_name`
- `row_count`
- `distinct_state_count`
- `distinct_state_ratio`
- `singleton_bucket_rate`
- `max_bucket_size`
- `mean_bucket_size`
- `collision_count`
- `collision_rate`
- `compression_score`
- `collision_examples`
- `passes_collision_gate`
- `passes_compression_gate`
- `passes_frontier_gate`

The first compression gate is:

- `collision_count == 0`
- `distinct_state_ratio <= 0.5`
- `singleton_bucket_rate <= 0.75`

## Candidates

The probe starts from the legal multiplicity ladder and tests:

- `multiplicity_pressure_bucketed`
- `multiplicity_pressure_mod_wheel`
- `multiplicity_pressure_histogram`
- `multiplicity_pressure_run_lengths`
- `multiplicity_pressure_coarse_counts`
- `multiplicity_pressure_quantized`
- `multiplicity_pressure_family_only`
- `multiplicity_pressure_without_offsets`
- `multiplicity_pressure_prefix_histogram`
- `multiplicity_pressure_low_medium_high`

No candidate uses prime markers, full divisor counts, exact factorization,
future next-prime offset, scan-to-first-prime behavior, or the old recursive
walker.

## Surface

The first frontier run used:

- input primes: `11..100_000`
- prefix: `32`
- rows: `9588`

## Result

No candidate passed the frontier gate.

Summary:

- `frontier_survivors: []`
- `lowest_collision_count: 0`
- `best_compression_score: 0.154777`

| Candidate | Collisions | Distinct Ratio | Singleton Rate | Max Bucket | Compression |
|---|---:|---:|---:|---:|---:|
| `multiplicity_pressure_bucketed` | `0` | `1.0` | `1.0` | `1` | `0.0` |
| `multiplicity_pressure_mod_wheel` | `0` | `1.0` | `1.0` | `1` | `0.0` |
| `multiplicity_pressure_histogram` | `0` | `1.0` | `1.0` | `1` | `0.0` |
| `multiplicity_pressure_run_lengths` | `0` | `1.0` | `1.0` | `1` | `0.0` |
| `multiplicity_pressure_quantized` | `0` | `1.0` | `1.0` | `1` | `0.0` |
| `multiplicity_pressure_family_only` | `0` | `1.0` | `1.0` | `1` | `0.0` |
| `multiplicity_pressure_without_offsets` | `0` | `1.0` | `1.0` | `1` | `0.0` |
| `multiplicity_pressure_low_medium_high` | `0` | `1.0` | `1.0` | `1` | `0.0` |
| `multiplicity_pressure_coarse_counts` | `734` | `0.88496` | `0.891927` | `6` | `0.11504` |
| `multiplicity_pressure_prefix_histogram` | `956` | `0.845223` | `0.855997` | `7` | `0.154777` |

## Interpretation

The multiplicity signal has a sharp compression/collision tradeoff on this
surface.

When enough multiplicity detail remains to keep collisions at zero, the state
partition is fully singleton. The state is still acting as a row fingerprint.

When the signal is coarsened enough to reuse buckets, collisions appear
immediately. The two most compressed candidates are:

- `multiplicity_pressure_coarse_counts`
- `multiplicity_pressure_prefix_histogram`

Both fail the collision gate.

This does not falsify the transition-state approach. It does reject this first
local multiplicity-compression family as a Next-Prime Law 005 candidate.

## Status

Milestone 1 remains blocked.

Next-Prime Law 005 is not approved.

The next admissible search should not add richer state. It should either:

- analyze the collision buckets from the compressed candidates that reuse
  buckets; or
- introduce a new invariant that compresses before it predicts, rather than
  adding more local fingerprint detail.
