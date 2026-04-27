# Resolved Candidate Dominance Forensics

The integrated eliminator now resolves more true-next-prime search intervals, but it also
creates competing resolved false-endpoint search intervals. The dominance forensics test
shows that no tested ordering rule is safe.

Next-Prime Law 005 is not approved by this note.

## Objective

Study input primes where the integrated composite-exclusion eliminator produces at
least one resolved false-endpoint candidate.

The question is:

Which PGS-native dominance rule can select the true next prime from multiple
resolved candidate candidates without using primality labels?

A rule may abstain. A rule with any wrong selection is rejected.

## Instrument

Script:

- `benchmarks/python/prime_inference_generator/resolved_survivor_dominance_forensics.py`

Artifacts:

- `resolved_survivor_dominance_forensics_records.jsonl`
- `resolved_survivor_dominance_forensics_summary.json`

The script runs the composite-exclusion probe with:

- `single_hole_positive_witness_closure`
- `witness_bound: 97`

It then inspects only input primes with resolved false-endpoint alternatives.

## Surface

Run:

- input primes: `11..10_000`
- candidate bound: `64`
- witness bound: `97`

## Candidate Metadata

For each resolved candidate candidate, the probe records:

- `candidate_offset`
- `candidate_width`
- `gwr_carrier_offset`
- `gwr_carrier_divisor_count`
- `gwr_carrier_family`
- `first_open_offset`
- `resolved_interior_count`
- `single_hole_closure_used`
- `closure_count`
- `square_pressure`
- `power_closure_count`
- `small_factor_witness_closure_count`
- `lower_divisor_threat_count`
- `no_later_simpler_status`
- `previous_chamber_pressure`

Exact integer and divisor-family fields are offline diagnostics for forensics.
They are not generator rules.

## Result

Summary:

- `row_count: 1225`
- `anchors_with_false_resolved_survivors: 230`
- `true_boundary_rejected_count: 0`

Resolved-candidate count distribution:

| Resolved Candidates | Input primes |
|---:|---:|
| `2` | `230` |

Candidate dominance observable counts:

| Observable | Count |
|---|---:|
| `false_less_closure_than_true` | `178` |
| `false_survivor_before_true` | `178` |
| `true_boundary_not_resolved` | `52` |
| `true_requires_closure` | `178` |

The `52` cases where the true next prime is not resolved are still outside
dominance selection. The other `178` are the cases where the true next prime and
one false endpoint are both resolved.

## Dominance Rules Tested

| Rule | Made | Correct | Wrong | Abstain | Accuracy | Status |
|---|---:|---:|---:|---:|---:|---|
| `earliest_resolved_boundary` | `230` | `0` | `230` | `0` | `0.0` | rejected |
| `minimal_chamber_width` | `230` | `0` | `230` | `0` | `0.0` | rejected |
| `strongest_gwr_carrier` | `74` | `54` | `20` | `156` | `0.7297` | rejected |
| `no_later_simpler_margin` | `230` | `0` | `230` | `0` | `0.0` | rejected |
| `minimal_closure_support` | `230` | `0` | `230` | `0` | `0.0` | rejected |
| `previous_chamber_transition_compatibility` | `230` | `62` | `168` | `0` | `0.2696` | rejected |

No tested rule passes the hard gate:

- `selection_wrong_count == 0`

## Interpretation

The false resolved candidate is usually earlier than the true next prime. That
kills earliest-endpoint and minimal-width dominance outright.

The true next prime often requires the single-hole closure rule, while the false
remaining candidate requires less closure support. That kills minimal-closure dominance in
this surface.

GWR-selected-divisor-count dominance has some signal, but it is not safe:

- `selection_wrong_count: 20`

Previous-search-interval transition compatibility is also not safe:

- `selection_wrong_count: 168`

The current blocker is not search-interval closure. The blocker is resolved-interval
dominance. Multiple resolved diagnostic records can coexist, and the tested local
ordering rules do not select the true next prime safely.

## Status

Milestone 1 remains blocked.

Next-Prime Law 005 is not approved.

The next admissible work should focus on why the false earlier resolved
remaining candidate remains structurally plausible. A safe dominance rule must either
reject that earlier search interval or abstain, never select it incorrectly.
