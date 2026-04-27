# Next-Prime Law 005A Stress Tests

## Status

Next-Prime Law 005A passed two controlled one-axis stress tests, the stronger
candidate-horizon shifted-window stress, the combined-bound origin stress, and
the combined-bound shifted-window stress.

This is offline theorem discovery. Next-Prime Law 005A remains candidate-grade only. Pure generator emission remains forbidden. Classical labels are external audit only.

## Configuration

All stresses used the same base eliminator regime:

- single-hole positive witness closure: enabled
- selected-integer-locked pressure ceiling: enabled
- selected-integer-lock predicate: unresolved_alternatives_before_threat
- 005A higher-divisor locked absorption: enabled only in offline stress
- 005B: disabled

## Candidate-Bound Stress

The first stress changed one variable:

- candidate bound: 64 -> 128

The witness basis did not change:

- witness bound: 97

The input prime surface did not change:

- input primes: 11..1000000

## Candidate-Bound Stress Metrics

| field | value |
|---|---:|
| candidate_bound | 128 |
| witness_bound | 97 |
| anchor_range | 11..1000000 |
| row_count | 78494 |
| true_boundary_rejected_count | 0 |
| absorption_wrong_count | 0 |
| false_resolved_survivor_absorbed_count | 0 |
| unique_resolved_survivor_count | 36 |
| 005A_applied_count | 48 |
| 005A_correct_count | 48 |
| 005A_wrong_count | 0 |
| action_population_match | true |
| action_population_missed_count | 0 |
| first_failure_example | null |

## Witness-Bound Stress

The second stress changed one variable:

- witness bound: 97 -> 127

The candidate horizon returned to the prior audited value:

- candidate bound: 64

The input prime surface did not change:

- input primes: 11..1000000

## Witness-Bound Stress Metrics

| field | value |
|---|---:|
| candidate_bound | 64 |
| witness_bound | 127 |
| anchor_range | 11..1000000 |
| row_count | 78494 |
| true_boundary_rejected_count | 0 |
| absorption_wrong_count | 0 |
| false_resolved_survivor_absorbed_count | 0 |
| unique_resolved_survivor_count | 25 |
| 005A_applied_count | 31 |
| 005A_correct_count | 31 |
| 005A_wrong_count | 0 |
| action_population_match | true |
| action_population_missed_count | 0 |
| first_failure_example | null |

## Shifted-Window Stress

The shifted-window stress used the stronger candidate horizon from the first
stress:

- candidate bound: 128
- witness bound: 97

It changed only the input prime surface:

- input primes: 100000..200000
- input primes: 1000000..1100000

Activation was not required. Safe abstention was acceptable.

## Shifted-Window Stress Metrics

| anchor_range | candidate_bound | witness_bound | row_count | true_boundary_rejected_count | absorption_wrong_count | false_resolved_survivor_absorbed_count | action_population_match | action_population_missed_count | 005A_applied_count | 005A_correct_count | 005A_wrong_count | unique_resolved_survivor_count | safe_abstain_count | first_failure_example |
|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---|
| 100000..200000 | 128 | 97 | 8392 | 0 | 0 | 0 | true | 0 | 0 | 0 | 0 | 0 | 8392 | null |
| 1000000..1100000 | 128 | 97 | 7216 | 0 | 0 | 0 | true | 0 | 0 | 0 | 0 | 0 | 7216 | null |

## Combined-Bound Origin Stress

The combined-bound origin stress used both previously passed expansions:

- candidate bound: 128
- witness bound: 127
- input primes: 11..1000000

This changed both axes together. It remained an offline stress of the same
candidate rule, not an emission gate.

## Combined-Bound Origin Stress Metrics

| field | value |
|---|---:|
| candidate_bound | 128 |
| witness_bound | 127 |
| anchor_range | 11..1000000 |
| row_count | 78494 |
| true_boundary_rejected_count | 0 |
| absorption_wrong_count | 0 |
| false_resolved_survivor_absorbed_count | 0 |
| unique_resolved_survivor_count | 36 |
| 005A_applied_count | 48 |
| 005A_correct_count | 48 |
| 005A_wrong_count | 0 |
| safe_abstain_count | 78446 |
| action_population_match | true |
| action_population_missed_count | 0 |
| first_failure_example | null |

## Combined-Bound Shifted-Window Stress

The combined-bound shifted-window stress used the same combined horizon off the
origin surface:

- candidate bound: 128
- witness bound: 127
- input primes: 100000..200000
- input primes: 1000000..1100000

Activation was not required. Safe abstention was acceptable.

## Combined-Bound Shifted-Window Stress Metrics

| anchor_range | candidate_bound | witness_bound | row_count | true_boundary_rejected_count | absorption_wrong_count | false_resolved_survivor_absorbed_count | action_population_match | action_population_missed_count | 005A_applied_count | 005A_correct_count | 005A_wrong_count | unique_resolved_survivor_count | safe_abstain_count | first_failure_example |
|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---|
| 100000..200000 | 128 | 127 | 8392 | 0 | 0 | 0 | true | 0 | 0 | 0 | 0 | 0 | 8392 | null |
| 1000000..1100000 | 128 | 127 | 7216 | 0 | 0 | 0 | true | 0 | 0 | 0 | 0 | 0 | 7216 | null |

## Hard Gate

The hard pass condition was:

```text
true_boundary_rejected_count = 0
absorption_wrong_count = 0
false_resolved_survivor_absorbed_count = 0
action_population_match = true
```

All recorded stress rows passed all four requirements.

## Result

005A remains candidate-grade and is stronger than before:

```text
005A: candidate-grade, action-population audited, single-axis stresses passed, shifted-window stresses passed, combined-bound origin stress passed, combined-bound shifted-window stress passed, safe so far, narrow
```

Coverage under the larger candidate horizon improved:

- bound 64 integration: 31 applications, 25 unique resolved survivors
- bound 128 stress: 48 applications, 36 unique resolved survivors

Coverage under the larger witness basis did not broaden:

- witness bound 97 integration: 31 applications, 25 unique resolved survivors
- witness bound 127 stress: 31 applications, 25 unique resolved survivors

The stronger candidate horizon abstained safely on shifted windows:

- 100000..200000: 0 applications, 8392 safe abstentions
- 1000000..1100000: 0 applications, 7216 safe abstentions

The combined-bound origin stress preserved the larger candidate-bound coverage:

- candidate bound 128, witness bound 127: 48 applications, 36 unique resolved survivors

The combined-bound horizon also abstained safely on shifted windows:

- 100000..200000: 0 applications, 8392 safe abstentions
- 1000000..1100000: 0 applications, 7216 safe abstentions

The rule remains narrow. It is not a complete generator.

## Why Pure Emission Remains Forbidden

These stresses do not approve pure generator emission because:

- 005A is still a candidate law, not a theorem
- the tests are offline
- labels are still used after action for audit
- coverage is still narrow
- shifted-window activation remains absent on the tested shifted windows
- no pure emission contract has been approved

The pure generator must remain fail-closed.

## Falsification Conditions

Quarantine or restrict 005A if any future run shows:

```text
true_boundary_rejected_count > 0
absorption_wrong_count > 0
false_resolved_survivor_absorbed_count > 0
action_population_match = false
```

One wrong absorption kills generator eligibility for the rule.

## Next Gate

The activation-regime profile and 005A-R refinement probe now have separate
result notes. The next safe gate is action-population auditing for 005A-R under
the strongest safe horizon:

```text
candidate_bound: 128
witness_bound: 127
input primes: 11..1000000
```

Pure emission remains forbidden.
