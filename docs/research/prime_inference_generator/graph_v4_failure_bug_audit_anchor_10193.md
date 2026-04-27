# Graph v4 Failure Bug Audit: Anchor 10193

## Status

This is an offline bug audit for the first observed graph v4/v5 scale failure.
It does not repair the solver, add v6, change graph rules, add pure emission,
or approve production use.

The audit uses classical labels only after the graph state has been produced.
Those labels are reporting-only.

## Observed Failure

The scale run over anchors `11..100_000` with `candidate_bound = 128` and
`witness_bound = 127` found a failed graph emission at anchor `10193`.

```text
anchor_p: 10193
emitted_q_hat: 10201
emitted_offset: 8
actual_next_prime: 10211
actual_boundary_offset: 18
emitted_matches_actual_bool: false
```

The emitted value is not the next prime endpoint. It factors as:

```text
10201 = 101^2
```

## Bug-Audit Result

The single-anchor run reproduces the range failure:

```text
single_anchor_reproduces_range_failure: true
candidate_set_contains_true_boundary: true
audit_checks_first_prime_not_just_primality: true
true_boundary_absorbed_by_v4: true
v4_absorbed_resolved_candidate: false
v4_absorbed_unresolved_true_boundary: true
v4_ignored_raw_reset_evidence: false
```

The failure is not explained by range-order state leakage, missing true
candidate next prime generation, or an audit that checks only primality. The
single-anchor graph reaches the same false result.

## Phase Location

The true next prime offset `18` has this status by phase:

```text
base: UNRESOLVED
after_005A_R: UNRESOLVED
after_v1: UNRESOLVED
after_v2: UNRESOLVED
after_v3: UNRESOLVED
after_v4: REJECTED, absorbed_by 8
after_v5: REJECTED, absorbed_by 8
```

The false source offset `8` is locally resolved through the whole run:

```text
base: RESOLVED_SURVIVOR
after_005A_R: RESOLVED_SURVIVOR
after_v1: RESOLVED_SURVIVOR
after_v2: RESOLVED_SURVIVOR
after_v3: RESOLVED_SURVIVOR
after_v4: RESOLVED_SURVIVOR
after_v5: RESOLVED_SURVIVOR
```

## v4 Absorption Event

v4 directly absorbs the true next prime:

```text
relation: unresolved_later_domination_target_no_carrier_reset_discriminator
source_offset: 8
target_offset: 18
target_is_true_boundary: true
active_resolved_count: 1
source_single_hole_closure_used: false
target_has_legal_carrier: false
target_no_carrier_reset_status: NO_ACTIVE_RESET_EVIDENCE
```

The target was unresolved, not resolved, when v4 absorbed it. So the bug audit
does not show a status-mutation error where v4 accidentally targeted a resolved
candidate. It shows v4's predicate authorizing absorption of an unresolved true
endpoint.

## Reset Evidence Check

For the interval from source offset `8` to true next prime offset `18`, the audit
found:

```text
raw_reset_evidence_between_source_and_true: []
active_reset_evidence_between_source_and_true: []
ignored_rejected_or_absorbed_nodes_between_source_and_true: []
```

So this first failure is not caused by active-graph pruning hiding a raw
certified reset witness. The v4 relation fails because the absence of active
reset evidence is too weak when both the source and target have no legal
integer.

## Classification

The likely cause is:

```text
unsafe_v4_relation_active_graph_reset_too_permissive
```

This is not currently classified as an implementation bug. The phase snapshots
show the code doing what v4 says to do. The problem is that the v4 relation's
legal preconditions are insufficient at anchor `10193`.

## Consequence

Graph v4 and v5 must be quarantined outside the last clean surface until a
structural reset guard is found and the full matrix is rerun. The last clean
surface remains:

```text
anchors: 11..10_000
candidate_bound: 128
witness_bound: 127
graph_v5: 995 emitted / 995 confirmed / 0 failed
```

The scale surface `11..100_000` is not clean:

```text
graph_solved_count: 7391
confirmed_count: 6039
failed_count: 1352
v4_relation_wrong_count_after_audit: 1352
v5_relation_wrong_count_after_audit: 16
```

## Next Action

Do not patch anchor `10193`. Do not add v6 until the unsafe v4 condition is
replaced by a structural, label-free reset guard.

The next concrete task is to design a v4 guard that rejects this condition:

```text
source has no legal selected integer
target has no legal selected integer
target_no_carrier_reset_status: NO_ACTIVE_RESET_EVIDENCE
```

The guard must be tested first against the original `11..10_000` surface and
then the failed `11..100_000` scale surface.
