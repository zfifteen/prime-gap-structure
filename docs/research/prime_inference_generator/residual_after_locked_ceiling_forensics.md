# Residual After Locked Ceiling Forensics

After the strongest safe selected-integer-locked ceiling mode, the remaining blocker is
mostly unresolved alternatives, not unsafe pruning.

Next-Prime Law 005 is not approved by this note.

## Objective

Classify the residual failures after the best safe integrated mode:

- `single_hole_positive_witness_closure`
- `carrier_locked_pressure_ceiling`
- `carrier_lock_predicate: unresolved_alternatives_before_threat`
- `candidate_bound: 64`
- `witness_bound: 97`
- input primes: `11..10_000`

The probe does not add a new rule. It only reads the integrated eliminator
output and reports what remains.

## Instrument

Script:

- `../../../benchmarks/python/prime_inference_generator/residual_after_locked_ceiling_forensics.py`

Artifacts:

- `residual_after_locked_ceiling_forensics_records.jsonl`
- `residual_after_locked_ceiling_forensics_summary.json`

Command:

```bash
python3 benchmarks/python/prime_inference_generator/residual_after_locked_ceiling_forensics.py --start-anchor 11 --max-anchor 10000 --candidate-bound 64 --witness-bound 97 --output-dir /tmp/pgs_residual_after_locked_ceiling_10000_b64_w97
```

## Result

Summary:

- `row_count: 1225`
- `unique_resolved_survivor_count: 0`
- `true_boundary_rejected_count: 0`
- `true_boundary_unresolved_count: 52`
- `true_boundary_resolved_not_unique_count: 1173`
- `average_resolved_survivor_count: 1.1877551020408164`
- `average_unresolved_count: 7.8277551020408165`
- `carrier_locked_ceiling_applied_count: 111`
- `carrier_locked_ceiling_false_candidate_pruned_count: 479`

Residual pattern counts:

| Pattern | Count |
|---|---:|
| `true_resolved_not_unique_unresolved_alternatives` | `995` |
| `true_resolved_not_unique_multiple_resolved_and_unresolved` | `178` |
| `true_boundary_unresolved_chamber_completion` | `52` |

## Interpretation

The locked ceiling is safe and prunes false candidates, but it does not complete
the diagnostic record.

The largest residual class is:

- true next prime is resolved;
- only one resolved candidate remains;
- unresolved alternatives still exist.

That points to stronger legal closure or unresolved-alternative domination as
the next target.

The second residual class has:

- true next prime resolved;
- multiple resolved candidates;
- unresolved alternatives still exist.

That class needs both completion and absorption/dominance work. A selector alone
is not enough while unresolved alternatives remain live.

The smallest residual class has:

- true next prime still unresolved.

Those rows are search-interval-completion failures. They need additional legal closure
evidence before any dominance rule can help.

## Status

Milestone 1 remains blocked.

Next-Prime Law 005 is not approved.

The next target should be residual unresolved-alternative closure or domination.
The current evidence does not support prime output.
