# Single-Hole Chamber Closure

The single-hole probe found legal closure candidates for every one-hole
unresolved true-boundary case on the tested surface.

Result:

- `single_hole_case_count: 178`
- `single_hole_closure_candidate_count: 178`
- `true_boundary_rejected_count: 0`

Boundary Law 005 is not approved by this note.

## Objective

The composite-exclusion unresolved forensics found `230` cases where the true
boundary remained `UNRESOLVED`. In `178` of those cases, the true-boundary
candidate had exactly one unresolved wheel-open interior offset.

This probe asks whether that one hole has a legal closure candidate.

It does not emit primes. It does not add the rule to the generator. It records
closure evidence for the one-hole cases and leaves integration to a later
ablation step.

## Instrument

Script:

- `benchmarks/python/prime_inference_generator/single_hole_closure_probe.py`

Artifacts:

- `single_hole_closure_probe_records.jsonl`
- `single_hole_closure_probe_summary.json`

Each case records:

- `anchor_p`
- `actual_boundary_offset_label`
- `unresolved_open_offset`
- `unresolved_open_n`
- `resolved_survivor_offset`
- `candidate_chamber_width`
- `known_composite_witnesses_before_hole`
- `known_composite_witnesses_after_hole`
- `gwr_carrier_w`
- `gwr_carrier_offset`
- `gwr_carrier_divisor_count`
- `hole_relative_to_carrier`
- `hole_wheel_residue`
- `hole_square_status`
- `hole_power_status`
- `hole_small_factor_witness_status`
- `hole_semiprime_pressure`
- `hole_higher_divisor_pressure`
- `candidate_missing_rule`

## Closure Candidates

The probe tests only positive closure evidence:

1. `power_closure`
   - The hole is a perfect square, cube, or higher integer power.
2. `small_factor_positive_witness_closure`
   - The hole has a concrete bounded factor witness from the extended witness
     set.

The active eliminator uses witnesses:

- `7, 11, 13, 17, 19, 23, 29, 31`

The single-hole probe tests additional positive witness factors:

- `37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97`

This is still positive composite evidence. Absence of a witness is not used as
primality evidence.

Offline exact factorization fields are included only as diagnostics for
semiprime and higher-divisor pressure. They are not closure rules.

## Surface

Run:

- anchors: `11..10_000`
- candidate bound: `64`
- rows: `1225`

## Result

Summary:

- `true_boundary_unresolved_count: 230`
- `single_hole_case_count: 178`
- `single_hole_closure_candidate_count: 178`
- `power_closure_count: 13`
- `small_factor_positive_witness_closure_count: 178`
- `true_boundary_rejected_count: 0`

Candidate missing-rule counts:

| Candidate Missing Rule | Count |
|---|---:|
| `LEGAL_CLOSURE_CANDIDATE_AVAILABLE` | `178` |

Closure candidate counts:

| Closure Candidate | Count |
|---|---:|
| `small_factor_positive_witness_closure` | `178` |
| `power_closure` | `13` |

Hole position relative to GWR carrier:

| Position | Count |
|---|---:|
| `AFTER_CARRIER` | `124` |
| `BEFORE_CARRIER` | `54` |

Offline exact family:

| Family | Count |
|---|---:|
| `semiprime` | `165` |
| `prime_power` | `13` |

Offline exact divisor-count distribution:

| Divisor Count | Count |
|---:|---:|
| `3` | `13` |
| `4` | `165` |

Extended witness-factor distribution:

| Factor | Count |
|---:|---:|
| `37` | `29` |
| `41` | `29` |
| `43` | `23` |
| `47` | `15` |
| `53` | `17` |
| `59` | `15` |
| `61` | `14` |
| `67` | `11` |
| `71` | `8` |
| `73` | `4` |
| `79` | `5` |
| `83` | `4` |
| `89` | `3` |
| `97` | `1` |

## Interpretation

The one-hole failure mode is not mathematically scattered.

Every one-hole true-boundary case is closable by a positive bounded witness
extension through `97`. The `13` power cases are a subset of those closures.
The exact offline diagnostics show the holes are:

- semiprimes with divisor count `4`, or
- prime squares with divisor count `3`.

This does not make the current generator emit. It identifies the next safe
rule-family candidate:

- extend positive composite witnesses for unresolved interior holes.

The rule must still be tested inside the composite-exclusion eliminator with
ablation. The safety gate remains:

- `true_boundary_rejected_count == 0`

## Status

Milestone 1 remains blocked.

Boundary Law 005 is not approved.

The next admissible implementation is an ablation run that incorporates this
closure rule into the eliminator and measures whether:

- `true_boundary_unresolved_count` decreases;
- `unique_resolved_survivor_count` increases;
- `true_boundary_rejected_count` remains `0`.
