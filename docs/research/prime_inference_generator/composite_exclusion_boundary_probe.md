# Composite-Exclusion Endpoint Probe

The composite-exclusion probe now has three-status candidate accounting:

- `RESOLVED_SURVIVOR`
- `UNRESOLVED`
- `REJECTED`

The safety result remains intact:

- `true_boundary_rejected_count: 0`

The strengthened accounting also shows why the probe still cannot emit:

- `unique_survivor_count: 1225`
- `unique_resolved_survivor_count: 0`

Every anchor has exactly one resolved survivor, but every anchor also has
unresolved alternatives. That is not a unique endpoint.

Next-Prime Law 005 is not approved by this note.

## Objective

Build a safe eliminator before a generator.

The probe does not predict the next prime and does not emit inferred primes. It
constructs a finite wheel-open candidate set for each anchor, applies legal
candidate statuses, and attaches the classical next-gap label afterward for
reporting.

The default outcome remains fail-closed.

## Instrument

Script:

- `benchmarks/python/prime_inference_generator/composite_exclusion_boundary_probe.py`

Artifacts:

- `composite_exclusion_boundary_probe_rows.jsonl`
- `composite_exclusion_boundary_probe_summary.json`

Each row records:

- `anchor_p`
- `candidate_offsets`
- `candidate_count`
- `rejected_count`
- `unresolved_count`
- `survives_count`
- `survivor_count`
- `survivors`
- `unresolved`
- `rejection_reasons_by_candidate`
- `unresolved_reasons_by_candidate`
- `candidate_status_by_offset`
- `actual_boundary_offset_label`
- `true_boundary_status`
- `unique_resolved_survivor`
- `unique_survivor_matches_label`
- `failure_reason`

The summary records:

- `row_count`
- `unique_survivor_count`
- `unique_resolved_survivor_count`
- `no_unique_boundary_count`
- `true_boundary_rejected_count`
- `unique_survivor_match_count`
- `unique_survivor_match_rate`
- `average_rejected_count`
- `average_unresolved_count`
- `average_survives_count`
- `true_boundary_status_counts`
- `rule_family_reports`
- `first_failure_examples`

## Rule Families

The summary reports these rule families:

- `wheel_closed_rejection`
- `positive_composite_witness_rejection`
- `interior_open_unclosed_rejection`
- `gwr_incompatibility_rejection`
- `no_later_simpler_violation_rejection`
- `square_pressure_rejection`
- `carrier_absence_rejection`

Only two families are active in this probe:

1. `positive_composite_witness_rejection`
   - Rejects a candidate next prime if the candidate itself has a bounded
     positive composite witness.
2. `interior_open_unclosed_rejection`
   - Marks a candidate `UNRESOLVED` if a wheel-open interior offset lacks a
     bounded positive composite witness.

The second rule is not a rejection rule. It prevents unresolved interior
positions from being silently treated as closed.

## Bounded Witnesses

For each wheel-open candidate `q = p + k`, reject only when `q` has a concrete
bounded composite witness from:

- `7, 11, 13, 17, 19, 23, 29, 31`

The eliminator does not treat absence of a witness as primality evidence. If no
witness is found and the proposed chamber has unresolved wheel-open interior
positions, the candidate is `UNRESOLVED`.

The eliminator does not use:

- `isprime`
- `nextprime`
- Miller-Rabin
- actual gap width
- future next-prime offset
- scan-to-first-prime behavior
- the old recursive walker
- full divisor-count ladders

Classical labels are attached after elimination for measurement only.

## Surface

Run:

- anchors: `11..10_000`
- candidate bound: `64`
- rows: `1225`

## Result

Summary:

- `unique_survivor_count: 1225`
- `unique_resolved_survivor_count: 0`
- `no_survivor_count: 0`
- `no_unique_boundary_count: 1225`
- `true_boundary_rejected_count: 0`
- `unique_survivor_match_count: 995`
- `unique_survivor_match_rate: 0.8122448979591836`
- `average_candidate_count: 16.749387755102042`
- `average_rejected_count: 7.3428571428571425`
- `average_unresolved_count: 8.406530612244898`
- `average_survives_count: 1.0` for resolved survivors

True-endpoint status counts:

| Status | Anchors |
|---|---:|
| `RESOLVED_SURVIVOR` | `995` |
| `UNRESOLVED` | `230` |
| `REJECTED` | `0` |

Survivor-count distribution:

| Survivor Count | Anchors |
|---:|---:|
| `1` | `1225` |

Unresolved-count distribution:

| Unresolved Count | Anchors |
|---:|---:|
| `4` | `3` |
| `5` | `19` |
| `6` | `83` |
| `7` | `254` |
| `8` | `321` |
| `9` | `266` |
| `10` | `164` |
| `11` | `84` |
| `12` | `19` |
| `13` | `8` |
| `14` | `3` |
| `15` | `1` |

## Rule-Family Reports

`positive_composite_witness_rejection`:

- `rejected_count: 8995`
- `true_boundary_rejected_count: 0`
- `average_survivor_count_after_rule: 9.406530612244898`
- `marginal_rejection_count: 8995`
- `unique_survivor_count_after_rule: 0`

`interior_open_unclosed_rejection`:

- `rejected_count: 0`
- `unresolved_count: 10298`
- `true_boundary_rejected_count: 0`
- `average_survivor_count_after_rule: 8.342857142857143`
- `marginal_rejection_count: 0`
- `unique_survivor_count_after_rule: 0`

The remaining rule families are placeholders with zero marginal rejection in
this probe.

## Interpretation

The first safety gate still succeeds:

- the true next prime is never `REJECTED`.

The probe now exposes a stronger structure:

- bounded positive witnesses reduce the average candidate count from `16.75` to
  `9.41`;
- interior-open accounting prevents unresolved chambers from being counted as
  closed;
- the combined status model leaves one resolved survivor per anchor, but every
  anchor still has unresolved alternatives.

The `995` unique-survivor label matches are not generator emissions. They are
cases where the single resolved survivor equals the classical label while
unresolved alternatives remain. Pure generation cannot emit from that state.

## Status

Milestone 1 remains blocked.

Next-Prime Law 005 is not approved.

The next admissible step is to add one legal exclusion rule at a time and keep
`true_boundary_rejected_count = 0` as the primary safety gate.

## Integrated Single-Hole Closure Run

The next integrated run enabled:

- `single_hole_positive_witness_closure`
- `witness_bound: 97`

Surface:

- anchors: `11..10_000`
- candidate bound: `64`
- rows: `1225`

Before closure:

- `true_boundary_status_counts: {RESOLVED_SURVIVOR: 995, UNRESOLVED: 230}`
- `unique_resolved_survivor_count: 0`
- `average_unresolved_count: 8.406530612244898`
- `average_resolved_survivor_count: 1.0`

After closure:

- `true_boundary_rejected_count: 0`
- `true_boundary_status_counts: {RESOLVED_SURVIVOR: 1173, UNRESOLVED: 52}`
- `unique_resolved_survivor_count: 0`
- `average_rejected_count: 7.3428571428571425`
- `average_unresolved_count: 8.218775510204082`
- `average_resolved_survivor_count: 1.1877551020408164`

Rule attribution:

- `single_hole_positive_witness_closure_applied_count: 230`
- `single_hole_positive_witness_true_boundary_closures: 178`
- `single_hole_positive_witness_false_boundary_closures: 52`
- `power_closure_subset_count: 13`

The rule improved true-next-prime resolution:

- unresolved true next primes fell from `230` to `52`;
- resolved true next primes rose from `995` to `1173`;
- no true next prime was rejected.

It did not produce unique resolved endpoints. The integrated rule also closes
`52` false-candidate next primes, so the resolved-survivor count rises from `1.0`
to `1.1877551020408164` on average. The eliminator remains fail-closed.

Next-Prime Law 005 is still not approved.
