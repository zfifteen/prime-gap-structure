# Resolved Next Prime Lock Separator

Higher-divisor pressure is the first zero-wrong lock separator on the tested
absorption surface.

Next-Prime Law 005 is not approved by this note.

## Objective

Resolved-interval absorption alone failed because true resolved endpoints and
false resolved candidates both absorb later unresolved alternatives.

This probe asks whether any legal lock/reset feature separates true resolved
endpoints from false resolved candidates before absorption is allowed.

## Measured Mode

The probe uses the strongest safe eliminator configuration:

- input primes: `11..10_000`
- `candidate_bound: 64`
- `witness_bound: 97`
- `single_hole_positive_witness_closure: enabled`
- `carrier_locked_pressure_ceiling: enabled`
- `carrier_lock_predicate: unresolved_alternatives_before_threat`

Labels are used only after the candidate records are produced.

## Instrument

Script:

- `../../../benchmarks/python/prime_inference_generator/resolved_boundary_lock_separator_probe.py`

Artifacts:

- `resolved_boundary_lock_separator_probe_records.jsonl`
- `resolved_boundary_lock_separator_probe_summary.json`

Command:

```bash
python3 benchmarks/python/prime_inference_generator/resolved_boundary_lock_separator_probe.py --start-anchor 11 --max-anchor 10000 --candidate-bound 64 --witness-bound 97 --output-dir /tmp/pgs_resolved_lock_separator_10000_b64_w97
```

## Result

Summary:

- `row_count: 1225`
- `resolved_candidate_count: 1455`
- `true_resolved_candidate_count: 1173`
- `false_resolved_candidate_count: 282`
- `zero_wrong_lock_candidates: ["higher_divisor_pressure_lock"]`
- `true_boundary_rejected_count: 0`

Candidate lock separator counts:

| Feature | Count |
|---|---:|
| `true_at_true` | `1173` |
| `false_before_true` | `282` |
| `true_extension_preserves_carrier` | `642` |
| `false_extension_preserves_carrier` | `146` |
| `true_extension_changes_carrier` | `531` |
| `false_extension_changes_carrier` | `136` |
| `true_reset_evidence_to_later` | `150` |
| `false_reset_evidence_to_later` | `7` |
| `true_higher_divisor_pressure_to_later` | `31` |
| `true_zero_closure_support` | `995` |
| `false_zero_closure_support` | `230` |
| `true_positive_closure_support` | `178` |
| `false_positive_closure_support` | `52` |

Predicate reports:

| Predicate | Locked | True locked | False locked | Zero-wrong |
|---|---:|---:|---:|---|
| `carrier_preservation_no_reset_lock` | `631` | `492` | `139` | `false` |
| `no_reset_lock` | `1298` | `1023` | `275` | `false` |
| `carrier_shared_lock` | `788` | `642` | `146` | `false` |
| `extension_changes_carrier_lock` | `667` | `531` | `136` | `false` |
| `reset_evidence_lock` | `157` | `150` | `7` | `false` |
| `higher_divisor_pressure_lock` | `31` | `31` | `0` | `true` |
| `no_higher_divisor_pressure_lock` | `1424` | `1142` | `282` | `false` |
| `zero_closure_support_lock` | `1225` | `995` | `230` | `false` |
| `positive_closure_support_lock` | `230` | `178` | `52` | `false` |
| `previous_gap_exact_match_lock` | `75` | `64` | `11` | `false` |
| `previous_gap_bucket_match_lock` | `356` | `294` | `62` | `false` |

## Interpretation

Most simple lock predicates fail the zero-wrong gate. Integer preservation,
no-reset status, integer change, reset evidence, closure support, and previous
gap compatibility all select false resolved candidates.

The one zero-wrong predicate on this surface is:

```text
higher_divisor_pressure_lock
```

It selects `31` true resolved endpoints and `0` false resolved candidates.
That is not Next-Prime Law 005. It is a candidate lock separator worth hardening.

The observed shape is:

```text
resolved interval
+ higher-divisor pressure between the candidate and later unresolved alternatives
=> absorption is zero-wrong on 11..10_000
```

The next test is scale and anti-leakage hardening for this predicate. It must
survive larger surfaces and shifted windows before it can become a Next-Prime Law
005 candidate.

## Status

Milestone 1 remains blocked.

Next-Prime Law 005 is not approved.

Prime output remains forbidden.

The next target is higher-divisor pressure lock hardening, not generator
integration.
