# Composite-Exclusion Unresolved Forensics

The unresolved-endpoint forensics show a tight failure mode.

All `230` cases where the true next prime remained `UNRESOLVED` share the same
missing-evidence pattern:

- unclosed wheel-open interior evidence;
- insufficient bounded composite witness coverage;
- chamber closure not certified;
- unresolved alternatives not dominated by the resolved survivor.

Next-Prime Law 005 is not approved by this note.

## Objective

Study the cases where the composite-exclusion probe did not reject the true
endpoint, but also did not resolve it.

The probe focuses only on rows with:

- `true_boundary_status: UNRESOLVED`

For each row it records:

- `anchor_p`
- `resolved_survivor`
- `actual_boundary_label`
- `unresolved_true_boundary_candidate`
- `why_resolved_survivor_survived`
- `why_true_boundary_was_unresolved`
- `which_evidence_was_missing`
- `which_pgs_rule_would_resolve_it`

## Instrument

Script:

- `benchmarks/python/prime_inference_generator/composite_exclusion_unresolved_forensics.py`

Artifacts:

- `composite_exclusion_unresolved_forensics_records.jsonl`
- `composite_exclusion_unresolved_forensics_summary.json`

The script is offline theorem discovery. It runs the label-free eliminator,
then attaches classical labels only to select and inspect true-next-prime
unresolved cases.

## Surface

Run:

- anchors: `11..10_000`
- candidate bound: `64`
- rows: `1225`

## Result

Summary:

- `true_boundary_unresolved_count: 230`
- `true_boundary_rejected_count: 0`
- `resolved_survivor_count: 1225`
- `unique_resolved_survivor_count: 0`

Missing-evidence counts:

| Missing Evidence | Count |
|---|---:|
| `closure_not_certified` | `230` |
| `insufficient_composite_witness` | `230` |
| `unclosed_open_interior` | `230` |
| `unresolved_alternative_domination` | `230` |

Candidate resolving-rule counts:

| Candidate Rule | Count |
|---|---:|
| `bounded_witness_extension` | `230` |
| `legal_composite_closure_certificate` | `230` |
| `unresolved_alternative_domination_lemma` | `230` |

Unresolved interior count distribution:

| Unresolved Interior Count | Anchors |
|---:|---:|
| `1` | `178` |
| `2` | `37` |
| `3` | `13` |
| `4` | `2` |

Resolved-survivor to actual-endpoint delta:

| Delta | Anchors |
|---:|---:|
| `2` | `31` |
| `4` | `39` |
| `6` | `54` |
| `8` | `15` |
| `10` | `23` |
| `12` | `26` |
| `14` | `12` |
| `16` | `3` |
| `18` | `7` |
| `20` | `8` |
| `22` | `4` |
| `24` | `4` |
| `28` | `2` |
| `30` | `1` |
| `34` | `1` |

## Interpretation

The `230` unresolved true-next-prime cases are not scattered. They all fail for
the same structural reason:

- the proposed true-next-prime chamber contains one or more wheel-open interior
  offsets that the active bounded witness set cannot close.

Most of the unresolved true-next-prime chambers are close to resolution:

- `178 / 230` have exactly one unresolved interior offset.

The current resolved survivor is therefore not an inferred next prime. It is a
candidate with no unresolved interior under the active bounded witness set.
When the actual next prime is farther right, the true chamber often needs one
additional legal composite closure certificate before it can compete.

## Next Lemma Shape

The next theorem target is not a direct next-prime law. It is an unresolved
alternative bridge:

If one candidate is a resolved survivor and another candidate is unresolved
only because of unclosed wheel-open interior offsets, then either:

- a legal composite closure certificate resolves those offsets; or
- a domination rule proves the unresolved alternative cannot be the endpoint.

Until that bridge exists, pure generation must fail closed whenever unresolved
alternatives remain.

## Status

Milestone 1 remains blocked.

Next-Prime Law 005 is not approved.

The next admissible experiment should focus on legal closure certificates for
the unresolved interior offsets, beginning with the `178` one-offset cases.
