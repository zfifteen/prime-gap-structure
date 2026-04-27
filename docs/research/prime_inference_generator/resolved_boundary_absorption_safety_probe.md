# Resolved Next Prime Absorption Safety Probe

Resolved-chamber absorption is not selective on the tested surface.

Next-Prime Law 005 is not approved by this note.

## Objective

Test the offline hypothesis:

> If $q_1$ is a resolved chamber endpoint and $q_2 > q_1$ is unresolved, then
> $q_2$ is absorbed by $q_1$.

This is Rule A. The probe tests Rule A as forensics only. It does not add a
generator rule and does not permit prime emission.

## Measured Mode

The probe uses the strongest safe eliminator configuration:

- anchors: `11..10_000`
- `candidate_bound: 64`
- `witness_bound: 97`
- `single_hole_positive_witness_closure: enabled`
- `carrier_locked_pressure_ceiling: enabled`
- `carrier_lock_predicate: unresolved_alternatives_before_threat`

Labels are attached after the eliminator runs, because this is offline
forensics.

## Instrument

Script:

- `../../../benchmarks/python/prime_inference_generator/resolved_boundary_absorption_safety_probe.py`

Artifacts:

- `resolved_boundary_absorption_safety_probe_records.jsonl`
- `resolved_boundary_absorption_safety_probe_summary.json`

Command:

```bash
python3 benchmarks/python/prime_inference_generator/resolved_boundary_absorption_safety_probe.py --start-anchor 11 --max-anchor 10000 --candidate-bound 64 --witness-bound 97 --output-dir /tmp/pgs_resolved_absorption_safety_10000_b64_w97
```

## Result

Summary:

- `row_count: 1225`
- `resolved_candidate_count: 1455`
- `true_resolved_candidate_count: 1173`
- `false_resolved_candidate_count: 282`
- `true_absorbs_all_later_count: 1173`
- `false_absorbs_all_later_count: 282`
- `rule_a_safe_absorption_count: 995`
- `rule_a_wrong_count: 282`
- `rule_a_abstain_count: 0`
- `would_rule_a_select_false_resolved_survivor_count: 282`
- `would_rule_a_eliminate_true_boundary_candidate_count: 104`
- `absorption_pattern_separates_true_from_false: false`
- `true_boundary_rejected_count: 0`
- `unique_resolved_survivor_count: 0`

Absorption status counts:

| Status | Count |
|---|---:|
| `ABSORPTION_SAFE_TRUE` | `995` |
| `ABSORPTION_NONSELECTIVE` | `178` |
| `ABSORPTION_UNSAFE_FALSE` | `282` |

Integer and reset feature counts:

| Feature | True candidates | False candidates |
|---|---:|---:|
| `carrier_identity_shared_with_later` | `642` | `146` |
| `extension_changes_carrier` | `531` | `136` |
| `extension_reset_evidence` | `150` | `7` |

## Interpretation

Rule A fails the safety gate.

Every true resolved candidate absorbs all later unresolved alternatives, but
every false resolved survivor does the same. Absorption alone does not
distinguish true resolved endpoints from false resolved survivors.

The fatal counts are:

- `would_rule_a_select_false_resolved_survivor_count: 282`
- `would_rule_a_eliminate_true_boundary_candidate_count: 104`

Those counts reject direct resolved-chamber absorption as a generator rule. A
locally resolved chamber cannot absorb later unresolved alternatives unless an
additional legal lock condition separates true resolved endpoints from false
resolved survivors.

The integer/reset features also do not provide an immediate separator. Both
true and false resolved candidates occur with shared selected-integer identity, integer
change, and reset evidence. Those features may still be useful in combination,
but none of the measured single features licenses Rule A.

## Status

Milestone 1 remains blocked.

Next-Prime Law 005 is not approved.

Prime emission remains forbidden.

The next target is not absorption integration. The next target is a stricter
selected-integer-lock or reset condition that can make absorption selective.
