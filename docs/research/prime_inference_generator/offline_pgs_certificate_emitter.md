# Offline PGS Diagnostic-Record Outputter

The offline diagnostic-record outputter produced 36 PGS endpoint diagnostic records
from the 005A-R candidate rule. A separate downstream audit confirmed all 36.

This is Milestone 1A evidence. It is not pure generator output. Pure output
remains forbidden.

## Status

```text
PGS Prime Generator: not complete
Milestone 1: still blocked
Milestone 1A: offline diagnostic-record output produced
Pure prime output: forbidden
005A-R: candidate-grade refined diagnostic-record rule
005B: quarantined
```

## Rule Set

The outputter uses:

```text
rule_set: 005A-R
candidate_bound: 128
witness_bound: 127
input primes: 11..1000000
```

The 005A-R selection condition is:

```text
005A activation
and single_hole_closure_used = false
and the post-absorption candidate set has exactly one resolved candidate
and no unresolved candidates
```

The outputter does not approve pure output. It writes generator-shaped records
with:

```text
record_type: OFFLINE_PGS_BOUNDARY_CERTIFICATE
certificate_status: CANDIDATE_CERTIFICATE
pure_output_approved: false
classical_audit_status: NOT_RUN
```

## Output Summary

The output pass wrote:

```text
offline_pgs_boundary_certificates.jsonl
offline_pgs_certificate_outputter_summary.json
```

Summary:

| field | value |
|---|---:|
| rule_set | 005A-R |
| anchor_range | 11..1000000 |
| candidate_bound | 128 |
| witness_bound | 127 |
| diagnostic record_count | 36 |
| pure_output_approved | false |
| classical_audit_required | true |
| classical_audit_status | NOT_RUN |
| first_failure_example | null |

The label-dependent counters are unset in the output summary because
classical audit has not run at that stage:

```text
wrong_count: null
false_selected_count: null
true_boundary_rejected_count: null
absorption_wrong_count: null
```

## Diagnostic Record Shape

Each diagnostic record includes:

```text
record_type
certificate_status
pure_output_approved
classical_audit_status
input_prime_p
candidate_q_hat
boundary_offset
rule_set
candidate_bound
witness_bound
gwr_carrier
gwr_carrier_offset
gwr_carrier_d
gwr_carrier_family
higher_divisor_pressure_lock
single_hole_closure_used
absorbed_alternative_count
rejected_candidate_count
unresolved_candidate_count
resolved_survivor_count
action_population_audited
selection_wrong_count
absorption_wrong_count
true_boundary_rejected_count
```

The outputted records set:

```text
single_hole_closure_used: false
action_population_audited: false
selection_wrong_count: null
absorption_wrong_count: null
true_boundary_rejected_count: null
```

Those fields remain unset until a downstream audit or action-population audit
has been run.

## Downstream Audit

The audit pass reads the outputted JSONL and writes:

```text
offline_pgs_certificate_audit_summary.json
```

Audit summary:

| field | value |
|---|---:|
| audited_count | 36 |
| confirmed_count | 36 |
| failed_count | 0 |
| first_failure | null |
| validation_backend | sympy.primerange_first_boundary |

Classical validation is downstream of diagnostic-record output. It is not used to
select diagnostic records.

## Result

005A-R now has a generator-facing offline artifact:

```text
36 OFFLINE_PGS_BOUNDARY_CERTIFICATE records
36 downstream audit confirmations
0 downstream audit failures
pure_output_approved: false
```

This is the first diagnostic-record output of the composite-exclusion path.
It is not a proof of the general generator law and it does not approve pure
prime output.

## Falsification Conditions

Quarantine or restrict 005A-R if any later run shows:

```text
audit failed_count > 0
wrong_count > 0
absorption_wrong_count > 0
true_boundary_rejected_count > 0
kept_non_unique_activations > 0
action_population_match = false
```

One wrong diagnostic record kills generator eligibility for the refinement.

## Next Gate

The next safe gate is an action-population audit for 005A-R as an outputter rule:

```text
rule_set: 005A-R
candidate_bound: 128
witness_bound: 127
input primes: 11..1000000
shifted windows:
  100000..200000
  1000000..1100000
```

That audit must confirm that the hardening population matches the population
that can produce diagnostic records. Pure output remains forbidden.
