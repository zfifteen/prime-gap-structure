# Graph v4 Repair Guard Probe

## Status

This began as an offline repair probe for the graph v4 scale failure. The
viable guard has now been integrated as graph v6. The integration does not
re-enable old v4/v5 as a broad default, add pure production output, or
integrate 005B.

Classical labels and first-endpoint audit are used only after each candidate
guard has acted.

Graph v4 and v5 are quarantined outside the last clean surface:

```text
input primes: 11..10_000
candidate_bound: 128
witness_bound: 127
```

The scale failure showed that this v4 inference is false:

```text
target has no legal selected integer
+ no active reset evidence
=> target may be absorbed
```

Future no-selected-integer target domination requires positive non-endpoint evidence.

## Probe Target

The probe tests this repaired relation shape:

```text
unresolved_later_domination_target_no_carrier_with_positive_nonboundary_guard
```

The repaired relation keeps the v4 graph constraints:

- active graph has exactly one resolved candidate;
- source has no single-hole closure dependency;
- target is the nearest later unresolved candidate;
- target has no legal integer;
- active graph shows no positive reset evidence between source and target.

It adds one candidate positive guard over the target.

## Guards Tested

```text
target_positive_composite_witness
target_power_witness
target_wheel_closed
target_independently_rejected
target_beyond_locked_pressure_ceiling
target_has_positive_nonboundary_certificate
```

The umbrella guard `target_has_positive_nonboundary_certificate` fires when
any label-free positive target evidence is present:

- bounded composite witness;
- power witness;
- certified divisor-class diagnostic record;
- wheel-closed target;
- independently rejected target;
- target beyond a selected selected-integer-locked pressure ceiling.

## Input prime 10193 Gate

All guards block the known bad absorption at input prime `10193`.

```text
input_prime_p: 10193
actual_next_prime: 10211
actual_boundary_offset: 18
bad v4 source_offset: 8
bad v4 target_offset: 18
```

The true next prime target does not satisfy the positive non-endpoint guard.

## Surface Results

Configuration:

```text
start_anchor: 11
small_surface: 11..10_000
large_surface: 11..100_000
candidate_bound: 128
witness_bound: 127
```

Baseline v3:

```text
11..10_000: 211 solved
11..100_000: 216 solved
```

Guard results:

| Guard | Blocks 10193 | 11..10k solved | 11..10k failed | 11..100k solved | 11..100k failed | Viable |
|---|---:|---:|---:|---:|---:|---:|
| `target_positive_composite_witness` | true | 211 | 0 | 216 | 0 | false |
| `target_power_witness` | true | 211 | 0 | 216 | 0 | false |
| `target_wheel_closed` | true | 211 | 0 | 216 | 0 | false |
| `target_independently_rejected` | true | 211 | 0 | 216 | 0 | false |
| `target_beyond_locked_pressure_ceiling` | true | 211 | 0 | 216 | 0 | false |
| `target_has_positive_nonboundary_certificate` | true | 212 | 0 | 217 | 0 | true |

Only `target_has_positive_nonboundary_certificate` passes the stated gate:

```text
blocks_anchor_10193_failure_bool: true
audit_failed_count_11_10k_if_integrated: 0
audit_failed_count_11_100k_if_integrated: 0
solved_count improves over v3: true
```

## Interpretation

The repair probe confirms the safety correction:

```text
absence of reset evidence alone is not enough
positive target non-endpoint evidence is required
```

The viable guard is narrow. It recovers only one additional solved input prime on
each tested surface compared with v3. That is still a valid repair candidate
because it blocks the known failure and produces zero audited failures on both
surfaces.

## v6 Integration

Do not patch input prime `10193`.

Graph v6 integrates only this repaired v4 candidate:

```text
unresolved_later_domination_target_no_carrier_with_positive_nonboundary_guard
```

It is v3 plus the repaired relation. It does not run the old v4 or v5
relations.

Configuration:

```text
candidate_bound: 128
witness_bound: 127
```

Integration results:

```text
11..10_000:
  graph_solved_count: 212
  audited_count: 212
  confirmed_count: 212
  failed_count: 0
  v4_relation_applied_count: 0
  v5_relation_applied_count: 0
  repaired_relation_solution_count: 1
  repaired_relation_wrong_count_after_audit: 0

11..100_000:
  graph_solved_count: 217
  audited_count: 217
  confirmed_count: 217
  failed_count: 0
  v4_relation_applied_count: 0
  v5_relation_applied_count: 0
  repaired_relation_solution_count: 1
  repaired_relation_wrong_count_after_audit: 0
```

Graph v4/v5 remain quarantined outside the last clean surface. Graph v6 is the
safe repaired solver line, with narrow coverage gain over v3.
