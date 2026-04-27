# Higher-Divisor Pressure Lock Activation Profile

The higher-divisor pressure lock is safe where it fires, and it fires only in
the initial anchor surface tested here.

This note profiles the activation regime for Next-Prime Law 005 Candidate:
Higher-Divisor Locked Resolved-Endpoint Absorption. It does not approve pure
generator emission.

## Status

Current status:

- Next-Prime Law 005: candidate-grade offline rule.
- Pure generator emission: forbidden.
- Milestone 1: blocked for generator output.
- Probe role: offline activation profiling only.

The activation profile was run with:

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

The profiler computes lock features from the pre-absorption eliminator state
and reads uniqueness from the post-absorption state.

## Headline Result

The lock fired `31` times across the tested profile, produced `25` unique
resolved survivors after flagged absorption, and produced `0` wrong selections.

All `31` activations occurred on the `11..1_000_000` surface. Both shifted
windows abstained:

```text
activation_count: 31
unique_success_count: 25
safe_abstain_count: 114191
wrong_count: 0
```

## Surface Summary

| Surface | Rows | Activations | Unique successes | Safe abstains | Wrong |
|---|---:|---:|---:|---:|---:|
| `11..1_000_000` | `78494` | `31` | `25` | `95274` | `0` |
| `100_000..200_000` | `8392` | `0` | `0` | `10163` | `0` |
| `1_000_000..1_100_000` | `7216` | `0` | `0` | `8754` | `0` |

The shifted windows did not falsify the lock. They did not activate it.

## Activation By Endpoint Offset

The activations are concentrated in small resolved offsets:

| Resolved candidate offset | Count |
|---:|---:|
| `4` | `4` |
| `6` | `13` |
| `8` | `4` |
| `10` | `3` |
| `12` | `4` |
| `14` | `3` |

The current activation regime is not a broad large-gap rule. It is a narrow
small-offset lock.

## Activation By Carrier Family

| Carrier family | Count |
|---|---:|
| `known_basis_semiprime` | `19` |
| `known_basis_prime_power` | `12` |

The lock fires in two carrier families on this surface. It is not tied to one
carrier class alone.

## Activation By First Open Offset

| First open offset | Count |
|---:|---:|
| `2` | `12` |
| `4` | `10` |
| `6` | `9` |

The lock activates across the first three wheel-open offset classes, with no
activation outside those classes in this profile.

## Activation By Previous Gap Class

| Previous gap width class | Count |
|---|---:|
| `G_LE_4` | `13` |
| `G_LE_8` | `11` |
| `G_LE_16` | `7` |

Every activation had previous gap width at most `16` in this run.

## Pressure Signature

The corrected profiler records pressure signatures before absorption. The
activation set is not the all-zero post-absorption signature.

The signature format is:

```text
H<higher-divisor-count>_R<reset-count>_S<square-count>_SP<semiprime-count>
```

Observed activation signatures:

| Pressure signature | Count |
|---|---:|
| `H1_R0_S0_SP1` | `3` |
| `H1_R3_S0_SP3` | `4` |
| `H1_R4_S0_SP4` | `2` |
| `H3_R0_S0_SP3` | `2` |
| all other observed signatures | `1` each |

The activation condition is usually triggered by one higher-divisor pressure
offset, but several cases have dense higher-divisor pressure before later
unresolved alternatives.

## Near-Miss Pattern

The sampled near-misses are dominated by:

```text
why_lock_did_not_fire: NO_HIGHER_DIVISOR_PRESSURE
missing_pressure_component: higher_divisor_pressure
```

This explains the shifted-window abstention in the measured profile: resolved
candidates still exist, but the higher-divisor pressure component required by
the lock does not fire.

## Interpretation

The activation profile supports three facts:

1. The lock remains zero-wrong on the tested profile.
2. The lock is narrow and origin-local on these surfaces.
3. The missing activation component in sampled abstentions is higher-divisor
   pressure, not candidate closure.

The result preserves the candidate-law status. It does not justify broadening
the lock, enabling pure emission, or treating shifted-window abstention as
next-prime inference.

## Falsification Condition

Quarantine the candidate immediately if a later profile reports:

```text
wrong_count > 0
true_boundary_rejected_count > 0
absorption_wrong_count > 0
false_resolved_survivor_absorbed_count > 0
```

One wrong case kills generator eligibility.

## Next Gate

The next research question is why higher-divisor pressure appears in the
initial surface activations but not in the shifted windows. The next probe
should compare non-firing resolved candidates against the `31` firing cases and
identify whether the absence is caused by:

- the strictness of the pressure predicate;
- absence of higher-divisor offsets between candidate and later alternatives;
- carrier-family differences;
- previous-gap regime differences;
- or a small-origin activation artifact.

The pure generator remains fail-closed.
