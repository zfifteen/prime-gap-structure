# Higher-Divisor Pressure Lock Activation Profile, Candidate Bound 128, Witness Bound 127

The strongest safe horizon produced 48 higher-divisor pressure lock activations
on anchors 11..1000000, with 36 unique resolved survivors after absorption and
0 wrong activations.

This is offline theorem discovery. Boundary Law 005A remains candidate-grade
only. Pure generator emission remains forbidden. Classical labels are external
audit only.

## Configuration

The profile used the strongest safe horizon:

```text
candidate_bound: 128
witness_bound: 127
anchors: 11..1000000
single_hole_positive_witness_closure: enabled
carrier_locked_pressure_ceiling: enabled
carrier_lock_predicate: unresolved_alternatives_before_threat
005A higher-divisor locked absorption: enabled only in offline profiling
005B: disabled
```

The shifted-window comparison used the same horizon on:

```text
anchors: 100000..200000
anchors: 1000000..1100000
```

## Record Fields

Each activation record includes:

```text
anchor_p
resolved_candidate_offset
actual_boundary_offset_label
unique_resolved_after_absorption_bool
candidate_bound
witness_bound
carrier_offset
carrier_divisor_count
carrier_family
higher_divisor_pressure_signature
higher_divisor_pressure_offset
higher_divisor_pressure_d
previous_gap_width
previous_chamber_type
first_open_offset
single_hole_closure_used
locked_absorption_count
absorbed_unresolved_offsets
nearest_unresolved_offsets_before_absorption
```

## Headline Metrics

| field | value |
|---|---:|
| activation_count | 48 |
| unique_success_count | 36 |
| non_unique_activation_count | 12 |
| wrong_count | 0 |
| safe_abstain_count | 95257 |
| candidate_bound | 128 |
| witness_bound | 127 |

The activation anchors run from 19 through 6229. Every activation is in the
0..99999 anchor bucket.

## Surface Summary

| surface | rows | activations | unique successes | safe abstains | wrong |
|---|---:|---:|---:|---:|---:|
| 11..1000000 | 78494 | 48 | 36 | 95257 | 0 |
| 100000..200000 | 8392 | 0 | 0 | 10163 | 0 |
| 1000000..1100000 | 7216 | 0 | 0 | 8754 | 0 |

The shifted windows did not activate 005A. In the sampled shifted-window
near-misses, all 200 abstentions had:

```text
why_lock_did_not_fire: NO_HIGHER_DIVISOR_PRESSURE
missing_pressure_component: higher_divisor_pressure
```

## Activation By Anchor Bucket

| anchor bucket | count |
|---|---:|
| 0..99999 | 48 |

This profile does not show shifted-window activation. The current evidence is
consistent with a small-origin activation regime under this horizon.

## Activation By Carrier Family

| carrier family | count |
|---|---:|
| known_basis_semiprime | 31 |
| known_basis_prime_power | 17 |

## Activation By Carrier Divisor Count

| carrier divisor count | count |
|---:|---:|
| 3 | 16 |
| 4 | 31 |
| 6 | 1 |

## Activation By Resolved Candidate Offset

| resolved candidate offset | count |
|---:|---:|
| 4 | 5 |
| 6 | 17 |
| 8 | 4 |
| 10 | 8 |
| 12 | 7 |
| 14 | 3 |
| 16 | 1 |
| 18 | 2 |
| 22 | 1 |

## Activation By First Open Offset

| first open offset | count |
|---:|---:|
| 2 | 14 |
| 4 | 21 |
| 6 | 13 |

## Activation By Previous Gap Width Class

| previous gap width class | count |
|---|---:|
| G_LE_4 | 22 |
| G_LE_8 | 17 |
| G_LE_16 | 9 |

Every activation had previous gap width at most 16.

## Activation By Pressure Signature

The pressure signature format is:

```text
H<higher-divisor-count>_R<reset-count>_S<square-count>_SP<semiprime-count>
```

The most common signature was:

| pressure signature | count |
|---|---:|
| H1_R10_S0_SP10 | 11 |

All other observed signatures had count 3 or less. The lock does not reduce to
one repeated pressure signature at this horizon. It most often fires with one
higher-divisor pressure offset plus a matching semiprime/reset field, but
several early activations have dense pressure fields.

## Unique Versus Non-Unique Activations

The 36 unique successes and 12 non-unique activations separate cleanly on
single-hole closure usage:

| group | single_hole_closure_used=false | single_hole_closure_used=true |
|---|---:|---:|
| unique successes | 36 | 0 |
| non-unique activations | 0 | 12 |

Carrier structure also differs:

| group | known_basis_semiprime | known_basis_prime_power |
|---|---:|---:|
| unique successes | 29 | 7 |
| non-unique activations | 2 | 10 |

Carrier divisor count differs in the same direction:

| group | d=3 | d=4 | d=6 |
|---|---:|---:|---:|
| unique successes | 6 | 29 | 1 |
| non-unique activations | 10 | 2 | 0 |

The observed split is:

```text
unique success: mostly semiprime carrier, usually d=4, no single-hole closure
non-unique activation: mostly prime-power carrier, usually d=3, single-hole closure used
```

This is a profile result, not an approved selector. It identifies a possible
future refinement target without authorizing any rule broadening.

## Interpretation

The 005A lock fires only when a resolved candidate has later unresolved
alternatives and a positive higher-divisor pressure offset appears before those
alternatives. At the strongest safe horizon, that condition appears 48 times on
the origin surface and nowhere in the tested shifted windows.

The shifted windows abstain because the required higher-divisor pressure
component does not fire in the sampled resolved-candidate near-misses. That is
safe behavior. It also confirms that 005A remains narrow.

The 36 unique successes are structurally different from the 12 non-unique
activations on this surface. The strongest observed separator is not another
pressure signature; it is whether the resolved candidate required single-hole
closure support. That needs a separate zero-wrong test before it can become a
rule condition.

## Status

```text
PGS Prime Generator: not complete
Pure prime emission: forbidden
Milestone 1: still blocked
005A: candidate-grade, activation-profiled at candidate_bound=128 and witness_bound=127, safe so far, narrow
005B: quarantined
```

## Falsification Conditions

Quarantine or restrict 005A if any later run shows:

```text
wrong_count > 0
true_boundary_rejected_count > 0
absorption_wrong_count > 0
false_resolved_survivor_absorbed_count > 0
action_population_match = false
```

One wrong absorption kills generator eligibility for the rule.

## Next Gate

The zero-wrong refinement probe over the 48 activation records has a separate
result note:

```text
docs/research/prime_inference_generator/boundary_law_005a_refinement.md
```

The next safe action is action-population auditing for that refinement:

```text
candidate condition: 005A activation and single_hole_closure_used = false
candidate_bound: 128
witness_bound: 127
```

It must not be integrated into generation until it passes the same hardening and
action-population gates as 005A.
