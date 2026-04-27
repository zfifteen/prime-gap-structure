# Previous-Chamber Reset Lock Probe

Previous-chamber memory produced zero-wrong lock candidates in the abstention
regime left by Next-Prime Law 005A.

This note documents offline theorem discovery only. It does not approve pure
generator emission and does not integrate a new absorption rule.

## Status

Current status:

- Milestone 0: accepted.
- Milestone 1: blocked for generator output.
- Next-Prime Law 005A: higher-divisor pressure lock, candidate-grade only.
- Next-Prime Law 005B: previous-chamber reset lock, candidate lead found.
- Pure emission: forbidden.

The previous-chamber signal is legal for a future pure walk only if the prior
endpoint has already been emitted and accepted in the generator's trust chain.
In this probe, labels are used only after record construction to classify true
and false resolved candidates.

## Target Population

The probe targets rows where:

```text
true next prime is resolved
later unresolved alternatives remain
higher_divisor_pressure_lock does not activate
previous_chamber_signal is present
```

The run used:

```text
surfaces:
  11..1_000_000
  100_000..200_000
  1_000_000..1_100_000
candidate_bound: 64
witness_bound: 97
single_hole_positive_witness_closure: enabled
carrier_locked_pressure_ceiling: enabled
carrier_lock_predicate: unresolved_alternatives_before_threat
```

## Headline Result

The probe produced `50941` resolved-candidate records from the target
population:

```text
true_candidate_count: 43219
false_candidate_count: 7722
previous_chamber_signal_count: 50941
```

Three previous-chamber predicates passed the zero-wrong gate:

```text
previous_to_current_carrier_shift_lock: true 21, false 0, wrong 0
previous_higher_divisor_reset_lock: true 6, false 0, wrong 0
previous_chamber_signature_lock: true 4, false 0, wrong 0
```

The best candidate by true selections is:

```text
previous_to_current_carrier_shift_lock
```

## Surface Summary

| Surface | Rows | Target rows | Candidate records |
|---|---:|---:|---:|
| `11..1_000_000` | `78494` | `36149` | `42632` |
| `100_000..200_000` | `8392` | `4212` | `4941` |
| `1_000_000..1_100_000` | `7216` | `2858` | `3368` |

The previous-chamber signal appears in both shifted windows. Unlike the
higher-divisor pressure lock, this family does not simply abstain on shifted
windows.

## Predicate Results

| Predicate | True selected | False selected | Wrong | Accuracy when made | Status |
|---|---:|---:|---:|---:|---|
| `previous_to_current_carrier_shift_lock` | `21` | `0` | `0` | `1.0` | live |
| `previous_higher_divisor_reset_lock` | `6` | `0` | `0` | `1.0` | live |
| `previous_chamber_signature_lock` | `4` | `0` | `0` | `1.0` | live |
| `previous_carrier_family_lock` | `32` | `1` | `1` | `0.9697` | rejected |
| `previous_square_pressure_reset_lock` | `3` | `1` | `1` | `0.75` | rejected |
| `previous_first_open_transition_lock` | `9092` | `1653` | `1653` | `0.8462` | rejected |
| `previous_gap_width_class_lock` | `11999` | `2115` | `2115` | `0.8501` | rejected |

The broad previous-gap and first-open transition predicates are not safe. They
select many true candidates, but they also select many false resolved
survivors.

The narrow integer-shift and previous-reset predicates are the useful results.

## Best Candidate

The best candidate predicate is:

```text
previous_to_current_carrier_shift_lock
```

Operationally, this predicate selects a resolved candidate only when:

```text
later unresolved alternatives exist
previous chamber has a legal selected integer
current candidate has a legal selected integer
previous selected-integer identity != current selected-integer identity
```

On the tested surface, that condition selected `21` true resolved candidates
and `0` false resolved survivors.

## Interpretation

The near-miss profile said previous-chamber memory was the dominant adjacent
signal. This probe shows that raw previous memory is too broad, but a narrow
integer-reset form is selective on the tested surface.

The result supports a candidate family:

```text
005B: Previous-Chamber Selected Integer-Shift Reset Lock
```

This is still candidate material only. It is not a theorem and not a generator
rule.

## Pure-Rule Dependency Caveat

Previous-chamber evidence is available to a pure generator only if the previous
endpoint is already trusted. A pure implementation would need an explicit
history contract:

```text
accepted previous endpoint
accepted previous chamber certificate
current resolved candidate
previous-to-current selected-integer shift
```

Without that prior-endpoint trust chain, previous-chamber memory is offline
evidence, not pure-generation evidence.

## Falsification Condition

Quarantine this candidate family if a later run reports:

```text
lock_false_selected > 0
lock_wrong_count > 0
true_boundary_rejected_count > 0
absorption_wrong_count > 0
```

One false selection kills generator eligibility.

## Next Gate

The next step is not integration. The next step is hardening:

```text
previous_to_current_carrier_shift_lock
previous_higher_divisor_reset_lock
previous_chamber_signature_lock
```

must be tested as candidate lock separators across larger and shifted surfaces.
Only predicates that remain zero-wrong may be considered for flagged
integration.

The pure generator remains fail-closed.
