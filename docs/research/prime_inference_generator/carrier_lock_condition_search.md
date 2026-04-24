# Carrier-Lock Condition Search

The naive right-boundary ceiling failed because a later lower-divisor composite
can reset the active carrier instead of proving that the boundary occurred
earlier. The carrier-lock search found two zero-wrong safety separators on the
tested surface, but neither is an emission rule.

Boundary Law 005 is not approved by this note.

## Objective

Start from the candidate pressure ceilings found by the rejected right-boundary
ceiling rule and classify them into:

- `safe_ceiling`: the audited next boundary is before the pressure event;
- `unsafe_reset`: the audited next boundary is at or after the pressure event.

Then compare label-free PGS metadata between the two classes and test
conservative lock predicates.

A predicate may abstain. A predicate fails if it classifies any unsafe reset as
safe.

## Instrument

Script:

- `../../../benchmarks/python/prime_inference_generator/carrier_lock_condition_probe.py`

Artifacts:

- `carrier_lock_condition_probe_records.jsonl`
- `carrier_lock_condition_probe_summary.json`

The probe consumes the same integrated composite-exclusion surface as the
right-boundary pressure ceiling probe:

- `single_hole_positive_witness_closure`
- `witness_bound: 97`

The lock predicates are label-blind. Labels are used only after records are
formed to classify safe ceilings and unsafe resets.

## Recorded Fields

Each candidate ceiling record includes:

- `anchor_p`
- `carrier_w`
- `carrier_d`
- `carrier_family`
- `carrier_offset`
- `threat_t`
- `threat_d`
- `threat_offset`
- `threat_family`
- `actual_boundary_offset_label`
- `ceiling_safe_bool`
- `reset_bool`
- `previous_chamber_state`
- `carrier_ladder_legal_features`
- `square_pressure`
- `higher_divisor_pressure`
- `semiprime_pressure`
- `resolved_survivor_pair_status`
- `extension_preserves_carrier_bool`
- `extension_changes_carrier_bool`

The `extension_*` fields use the audited boundary and are diagnostic only. They
are not generator predicates.

## Surface

Run:

- anchors: `11..10_000`
- candidate bound: `64`
- witness bound: `97`

Command:

```bash
python3 benchmarks/python/prime_inference_generator/carrier_lock_condition_probe.py --start-anchor 11 --max-anchor 10000 --candidate-bound 64 --witness-bound 97 --output-dir /tmp/pgs_carrier_lock_10000_b64_w97
```

## Result

Summary:

- `row_count: 139`
- `safe_ceiling_count: 128`
- `unsafe_reset_count: 11`
- `candidate_lock_predicates: ["unresolved_alternatives_before_threat", "higher_divisor_pressure_before_threat"]`
- `first_candidate_lock_predicate: "unresolved_alternatives_before_threat"`

The two zero-wrong predicates are:

| Rule | Safe classified | Unsafe misclassified | Abstain | Status |
|---|---:|---:|---:|---|
| `unresolved_alternatives_before_threat` | `111` | `0` | `28` | candidate |
| `higher_divisor_pressure_before_threat` | `10` | `0` | `129` | candidate |

Rejected predicates:

| Rule | Safe classified | Unsafe misclassified | Status |
|---|---:|---:|---|
| `single_resolved_no_unresolved_before_threat` | `16` | `1` | rejected |
| `all_resolved_candidates_before_threat` | `8` | `1` | rejected |
| `semiprime_carrier_square_threat` | `102` | `5` | rejected |
| `no_higher_divisor_pressure_before_threat` | `118` | `11` | rejected |

The rejected single-resolved predicates fail at anchor `6883`, where the
candidate ceiling would select an earlier survivor while the audited boundary
is at offset `16`.

## Observable Split

The strongest legal separator is:

- `has_unresolved_before_threat: True`
- safe ceilings: `111`
- unsafe resets: `0`

The second legal separator is:

- `has_higher_divisor_pressure: True`
- safe ceilings: `10`
- unsafe resets: `0`

The inverse observations are not safe:

- `has_unresolved_before_threat: False` includes all `11` unsafe resets;
- `has_higher_divisor_pressure: False` includes all `11` unsafe resets.

## Interpretation

The first separator does not produce a boundary emission. It says that when
unresolved alternatives remain before the pressure event, the event has been
safe as a ceiling on this surface. The generator still cannot emit because the
same unresolved alternatives remain to be closed or dominated.

The second separator is more structurally PGS-like: higher-divisor pressure
before the lower-divisor threat may indicate a carrier environment where the
later threat behaves as a ceiling. It covers only `10` cases here, so it is a
small candidate, not a theorem.

The unsafe reset cases are concentrated where the pre-threat candidate region
is already fully resolved. That is the trap: a clean early resolved candidate
does not imply a locked carrier.

## Status

Milestone 1 remains blocked.

Boundary Law 005 is not approved.

The right-boundary squeeze path is still live, but the next step is not prime
emission. The next step is to harden the two candidate lock predicates on larger
surfaces and then ask whether they reduce unresolved alternatives enough to
support unique inference.
