# Next-Prime Law 005A-R Refinement Probe

The 005A refinement kept all 36 unique successes, dropped all 12 non-unique
activations, and selected 0 wrong cases on the tested surfaces.

This is offline theorem discovery. Next-Prime Law 005A-R remains candidate-grade
only. Pure generator output remains forbidden. Classical labels are external
audit only.

## Candidate Refinement

The tested refinement is:

```text
005A activation
and single_hole_closure_used = false
```

The intent is to retain higher-divisor locked absorption cases whose resolved
candidate did not depend on single-hole positive witness closure support.

This is not integrated into pure generation. It is a zero-wrong refinement
test over the observed 005A activation population.

## Configuration

```text
candidate_bound: 128
witness_bound: 127
surfaces:
  11..1000000
  100000..200000
  1000000..1100000
single_hole_positive_witness_closure: enabled
carrier_locked_pressure_ceiling: enabled
carrier_lock_predicate: unresolved_alternatives_before_threat
005B: disabled
```

## Summary Metrics

| field | value |
|---|---:|
| activation_count | 48 |
| selected_activation_count | 36 |
| dropped_activation_count | 12 |
| unique_success_count | 36 |
| non_unique_activation_count | 0 |
| wrong_count | 0 |
| false_selected_count | 0 |
| true_boundary_rejected_count | 0 |
| absorption_wrong_count | 0 |
| safe_abstain_count | 114186 |
| kept_unique_successes | 36 |
| dropped_unique_successes | 0 |
| kept_non_unique_activations | 0 |
| dropped_non_unique_activations | 12 |

## Surface Rows

| surface | activations | selected | dropped | kept unique | kept non-unique | wrong | true next prime rejected | safe abstains |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 11..1000000 | 48 | 36 | 12 | 36 | 0 | 0 | 0 | 95269 |
| 100000..200000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10163 |
| 1000000..1100000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 8754 |

The shifted windows safely abstained. They produced no 005A-R activations and
no wrong cases.

## Hard Gate

The required gate was:

```text
wrong_count = 0
absorption_wrong_count = 0
true_boundary_rejected_count = 0
kept_non_unique_activations = 0
kept_unique_successes > 0
```

The origin surface passed. The shifted windows passed by safe abstention.

## Result

005A-R is a cleaner candidate refinement than unrefined 005A on this tested
horizon:

```text
005A-R: candidate-grade, all selected origin-surface activations unique, shifted windows safe-abstain, safe so far, narrow
```

The result does not approve generator output. It only shows that the
single-hole closure filter separated the tested 005A activation population into
36 selected unique successes and 12 dropped non-unique activations.

## Interpretation

The profile showed that non-unique 005A activations were exactly the cases whose
resolved candidate used single-hole closure support. The refinement probe
confirmed that dropping those activations removes all non-unique action cases
on the tested horizon while preserving every unique success.

The observed rule is narrower than 005A. It is also more generator-shaped on
the tested origin surface because every selected activation yielded a unique
resolved candidate after absorption.

This remains a candidate pattern. A future integration gate must verify that
the refined action population matches the hardening population before any pure
generation discussion.

## Falsification Conditions

Quarantine or restrict 005A-R if any later run shows:

```text
wrong_count > 0
absorption_wrong_count > 0
true_boundary_rejected_count > 0
kept_non_unique_activations > 0
action_population_match = false
```

One wrong absorption kills generator eligibility for the refinement.

## Next Gate

The next safe gate is action-population auditing for 005A-R:

```text
lock: 005A activation and single_hole_closure_used = false
candidate_bound: 128
witness_bound: 127
surfaces:
  11..1000000
  100000..200000
  1000000..1100000
```

The audit must confirm that the population used to harden 005A-R matches the
population it can act on during flagged offline integration. Pure output
remains forbidden.
