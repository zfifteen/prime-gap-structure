# Absorption Lock Action-Population Audit

## Status

This is offline theorem discovery.

Next-Prime Law 005 remains candidate-grade only. Pure generator emission remains forbidden. Classical labels are attached only after the tested rule action is computed, for audit and forensics.

## Purpose

The audit checks whether a lock's hardening population covers the candidates that the same lock can act on during integration.

The required invariant is:

$$\text{missed action candidates} = 0$$

If a lock can act on a candidate that was not represented in its hardening population, the hardening result is incomplete. If that missed action is wrong or rejects the true next prime, the lock is quarantined as integration logic.

## Configuration

The audit used the strongest safe pre-absorption eliminator:

- candidate bound: 64
- witness bound: 97
- single-hole positive witness closure: enabled
- carrier-locked pressure ceiling: enabled
- carrier-lock predicate: unresolved_alternatives_before_threat

Surfaces:

- 11..1000000
- 100000..200000
- 1000000..1100000

Locks audited:

- 005A higher_divisor_pressure_lock
- 005B previous_to_current_carrier_shift_lock

## Summary

| lock | hardening candidates | integration actions | missed actions | missed false absorbers | missed with true next prime unresolved | wrong absorptions | true next prime rejected | status |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 005A higher_divisor_pressure_lock | 114222 | 31 | 0 | 0 | 0 | 0 | 0 | candidate-grade, action-covered |
| 005B previous_to_current_carrier_shift_lock | 50941 | 43 | 22 | 1 | 1 | 1 | 1 | quarantined |

## Surface Rows

| lock | surface | hardening candidates | integration actions | missed actions | wrong absorptions | true next prime rejected |
|---|---:|---:|---:|---:|---:|---:|
| 005A | 11..1000000 | 95305 | 31 | 0 | 0 | 0 |
| 005A | 100000..200000 | 10163 | 0 | 0 | 0 | 0 |
| 005A | 1000000..1100000 | 8754 | 0 | 0 | 0 | 0 |
| 005B | 11..1000000 | 42632 | 43 | 22 | 1 | 1 |
| 005B | 100000..200000 | 4941 | 0 | 0 | 0 | 0 |
| 005B | 1000000..1100000 | 3368 | 0 | 0 | 0 | 0 |

## 005A Result

005A has full action-population coverage on the tested surfaces:

- missed_action_candidate_count: 0
- wrong_absorption_count: 0
- true_boundary_rejected_count: 0

The 005A hardening population covers every absorber that 005A can trigger in integration on these surfaces. This does not approve generator emission. It preserves 005A as a narrow candidate-grade lock.

## 005B Result

005B fails the action-population audit:

- missed_action_candidate_count: 22
- missed_action_false_absorber_count: 1
- missed_action_true_boundary_unresolved_count: 1
- wrong_absorption_count: 1
- true_boundary_rejected_count: 1

The wrong action is the known anchor 3137 failure:

- anchor: 3137
- false absorber offset: 12
- actual next prime offset: 26
- absorbed offsets: 26, 30, 32, 44, 50, 54

The hardening population did not cover this action because the true next prime was unresolved before absorption. That is exactly the mismatch the audit was designed to expose.

## Decision

005A remains live as candidate-grade:

- action-population covered
- zero wrong actions
- zero true-next-prime rejections
- narrow coverage
- no pure emission

005B remains quarantined:

- action-population mismatch
- missed false absorber
- wrong absorption
- true-next-prime rejection

Combined 005A/005B modes remain rejected because they inherit the 005B action failure.

## Next Safe Action

Profile adjacent 005A-like lock regimes only after preserving the same action-population audit requirement:

$$\text{missed action candidates} = 0,\quad \text{wrong absorptions} = 0,\quad \text{true next prime rejections} = 0$$

Do not revisit 005B as integration logic until a structural guard is proposed and tested across the full matrix.
