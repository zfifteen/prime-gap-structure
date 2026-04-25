# Experimental PGS Prime Emitter

The experimental PGS prime emitter produced 36 inferred next-prime boundary
records under 005A-R on anchors 11..1000000. A separate downstream classical
audit confirmed 36 out of 36.

This is Milestone 1B evidence. It is not production emission. Cryptographic use
is not approved.

## Status

```text
PGS Prime Generator: experimental mode ready
Production pure emission: forbidden
Milestone 1A: complete
Milestone 1B: experimental inferred emission produced
005A-R: candidate-grade refined emission rule
005B: quarantined
```

## Rule Set

The emitter uses the 005A-R refined rule:

```text
rule_set: 005A-R
candidate_bound: 128
witness_bound: 127
anchors: 11..1000000
```

The emitted records are generator-facing experimental records, not certificates
only:

```text
record_type: PGS_INFERRED_PRIME_EXPERIMENTAL
inference_status: INFERRED_BY_005A_R
production_approved: false
cryptographic_use_approved: false
classical_audit_required: true
classical_audit_status: NOT_RUN
```

## Emission Summary

| field | value |
|---|---:|
| record_type | PGS_EXPERIMENTAL_INFERENCE_SUMMARY |
| rule_set | 005A-R |
| anchor_range | 11..1000000 |
| candidate_bound | 128 |
| witness_bound | 127 |
| emitted_count | 36 |
| production_approved | false |
| cryptographic_use_approved | false |
| classical_audit_required | true |
| classical_audit_status | NOT_RUN |

## Audit Summary

The audit reads the emitted experimental JSONL after emission. It is not part of
record selection.

| field | value |
|---|---:|
| audited_count | 36 |
| confirmed_count | 36 |
| failed_count | 0 |
| first_failure | null |
| validation_backend | sympy.primerange_first_boundary |

## First Ten Records

| anchor_p | inferred_prime_q_hat | boundary_offset | carrier_family | carrier_d |
|---:|---:|---:|---|---:|
| 19 | 23 | 4 | known_basis_semiprime | 4 |
| 23 | 29 | 6 | known_basis_prime_power | 3 |
| 31 | 37 | 6 | known_basis_prime_power | 6 |
| 43 | 47 | 4 | known_basis_semiprime | 4 |
| 47 | 53 | 6 | known_basis_prime_power | 3 |
| 53 | 59 | 6 | known_basis_semiprime | 4 |
| 61 | 67 | 6 | known_basis_semiprime | 4 |
| 67 | 71 | 4 | known_basis_semiprime | 4 |
| 73 | 79 | 6 | known_basis_semiprime | 4 |
| 163 | 167 | 4 | known_basis_semiprime | 4 |

## Last Ten Records

| anchor_p | inferred_prime_q_hat | boundary_offset | carrier_family | carrier_d |
|---:|---:|---:|---|---:|
| 661 | 673 | 12 | known_basis_semiprime | 4 |
| 677 | 683 | 6 | known_basis_semiprime | 4 |
| 683 | 691 | 8 | known_basis_semiprime | 4 |
| 691 | 701 | 10 | known_basis_semiprime | 4 |
| 701 | 709 | 8 | known_basis_semiprime | 4 |
| 709 | 719 | 10 | known_basis_semiprime | 4 |
| 839 | 853 | 14 | known_basis_prime_power | 3 |
| 953 | 967 | 14 | known_basis_prime_power | 3 |
| 2287 | 2293 | 6 | known_basis_semiprime | 4 |
| 3001 | 3011 | 10 | known_basis_semiprime | 4 |

## Supported Claim

The experimental PGS prime emitter produced 36 inferred next-prime boundary
records under 005A-R on anchors 11..1000000. A separate downstream classical
audit confirmed 36 out of 36.

The supported claim is limited to this experimental regime. The result does not
approve production pure emission, cryptographic use, or validation-free
operation.

## Falsification Conditions

Quarantine or restrict the experimental mode if any later run shows:

```text
audit failed_count > 0
wrong_count > 0
absorption_wrong_count > 0
true_boundary_rejected_count > 0
kept_non_unique_activations > 0
```

One failed emitted prime requires immediate autopsy before further expansion.

## Next Scale Run

The target-driven run kept the same rule and bounds, started at anchor 11, and
scanned to the 10,000,000 cap.

```text
rule_set: 005A-R
emit_target: 100
candidate_bound: 128
witness_bound: 127
anchor_range: 11..10000000
max_scan_cap: 10000000
final_anchor_scanned: 9999991
max_anchor_scanned: 9999991
emitted_count: 36
reason: EMIT_TARGET_NOT_REACHED
runtime_seconds: 1775.3614568330813
```

The separate downstream audit confirmed all emitted records:

```text
audited_count: 36
confirmed_count: 36
failed_count: 0
first_failure: null
validation_backend: sympy.primerange_first_boundary
```

The run did not increase coverage. Under the current 005A-R rule and fixed
bounds, the emission island remains the same 36 records through the 10,000,000
cap.

The next generator-facing run should therefore add a lawful deduction relation
or a structurally justified adjacent lock family before attempting another
larger scan. A shifted-window scale option remains useful after such a relation
exists:

```text
candidate_bound: 128
witness_bound: 127
anchors: 1000000..2000000
```

That tests post-origin coverage without changing the rule or bounds after the
rule set itself gains a new accepted relation.
