# Previous-to-Current Integer Shift Lock Hardening

The previous-to-current selected-integer shift lock remained zero-wrong on all tested
surfaces and abstained on both shifted windows.

This note hardens the leading Next-Prime Law 005B candidate. It does not approve
integration and does not approve pure generator emission.

## Status

Current status:

- Next-Prime Law 005A: higher-divisor pressure lock, candidate-grade only.
- Next-Prime Law 005B lead: previous-to-current selected-integer shift lock.
- Milestone 1: blocked for generator output.
- Pure emission: forbidden.

Previous-chamber evidence is history-dependent. A pure generator may use it only
after the previous endpoint and previous chamber certificate are already trusted.

## Tested Configuration

The hardening run used:

```text
candidate_bound: 64
witness_bound: 97
single_hole_positive_witness_closure: enabled
carrier_locked_pressure_ceiling: enabled
higher_divisor_locked_absorption: disabled
previous_to_current_carrier_shift_lock: selector only
```

The lock was evaluated on the previous-chamber near-miss target population:

```text
true next prime is resolved
later unresolved alternatives remain
higher_divisor_pressure_lock does not activate
previous_chamber_signal is present
```

## Headline Result

The lock selected no false resolved survivors on any tested surface:

```text
all_surfaces_zero_wrong: true
first_failed_surface: None
```

The origin-scaled surfaces selected `21` true resolved candidates and `0` false
resolved candidates. The shifted windows selected `0` candidates and remained
safe by abstention.

## Hardening Matrix

| Surface | Candidate count | True candidates | False candidates | True selected | False selected | Wrong | Positive selections |
|---|---:|---:|---:|---:|---:|---:|---:|
| `11..10_000` | `1187` | `1036` | `151` | `21` | `0` | `0` | `21` |
| `11..100_000` | `7215` | `6068` | `1147` | `21` | `0` | `0` | `21` |
| `11..1_000_000` | `42632` | `36149` | `6483` | `21` | `0` | `0` | `21` |
| `100_000..200_000` | `4941` | `4212` | `729` | `0` | `0` | `0` | `0` |
| `1_000_000..1_100_000` | `3368` | `2858` | `510` | `0` | `0` | `0` | `0` |

The shifted windows are safety-passing abstentions, not positive evidence for
coverage.

## Interpretation

The previous-to-current selected-integer shift lock survives the same safety pressure
that killed broader previous-memory predicates:

```text
previous_gap_width_class_lock
previous_first_open_transition_lock
```

Those broader predicates selected many true candidates and many false
survivors. The integer-shift lock selected far fewer candidates and selected no
false survivors on this hardening surface.

The result supports candidate status:

```text
005B Candidate: Previous-to-Current Selected-Integer Shift Lock
```

It does not support pure generator emission.

## Coverage

The current coverage is narrow:

```text
origin-scaled surfaces: 21 selections
shifted windows: 0 selections
```

This resembles Next-Prime Law 005A: safe where it fires, but sparse.

## Integration Gate

Before integration, the candidate needs a separate flagged eliminator mode:

```text
--enable-previous-selected integer-shift-locked-absorption
```

The integration tests should run separately:

```text
005A only
005B only
005A OR 005B
005A THEN 005B
```

with hard gates:

```text
true_boundary_rejected_count == 0
absorption_wrong_count == 0
false_resolved_survivor_absorbed_count == 0
```

## Falsification Condition

Quarantine this candidate if any future run reports:

```text
previous_to_current_carrier_shift_lock_false_selected > 0
previous_to_current_carrier_shift_lock_wrong_count > 0
true_boundary_rejected_count > 0
absorption_wrong_count > 0
```

One false selection kills generator eligibility.

## Current Conclusion

Next-Prime Law 005B is hardened as a narrow candidate lead:

```text
safety: zero false selections on tested surfaces
coverage: 21 origin-surface selections, 0 shifted-window selections
generator readiness: no
```

The pure generator remains fail-closed.
