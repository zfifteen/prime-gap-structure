# Boundary Certificate Graph Solver

## Status

The boundary certificate graph solver is an offline experimental inference
artifact. It is not production pure emission. It does not approve
cryptographic use. Classical validation remains a separate downstream audit
over records that have already been emitted.

Boundary Law 005 remains candidate-grade. The only live rule family used here
is 005A-R. Boundary Law 005B remains quarantined.

## Purpose

The previous emitter produced inferred-prime records from a single refined
activation rule. The graph solver keeps the same accepted rule set but changes
the implementation shape:

1. build candidate boundary nodes for an anchor prime;
2. attach accepted PGS facts to each node;
3. attach rule relations between nodes;
4. propagate accepted eliminations until stable;
5. emit only when one resolved candidate remains and no unresolved alternatives
   remain.

The solver asks whether the existing PGS facts already force a boundary when
they are composed as a small deduction graph.

## Accepted Rule Families

The graph uses only rule families already admitted into the experimental
pipeline:

- positive composite witness rejection;
- single-hole positive witness closure;
- carrier-locked pressure ceiling;
- 005A-R higher-divisor locked absorption with
  `single_hole_closure_used = false`.
- unresolved-later domination from existing graph facts.

It does not use 005B, broad resolved-chamber absorption, earliest-candidate
dominance, scalar ranking, prime-marker identity, `nextprime`, `isprime`, or
classical labels during solving.

## v1 Relation

The v1 addition was one relation:

```text
unresolved_later_domination_from_existing_graph_facts
```

It absorbs only the nearest later unresolved candidate after a resolved source
when the source has no single-hole closure dependency, the target chamber
preserves the same first legal carrier, and the existing graph facts contain no
same-or-lower divisor reset evidence between the source and target.

The relation abstains when reset evidence is positive or unknown. It does not
use labels, candidate ranking, 005B, or broad resolved-chamber absorption.

## v2 Relation

The v2 refinement stays inside the same relation family:

```text
unresolved_later_domination_from_existing_graph_facts_v2
```

It keeps the resolved-source, nearest-later-unresolved, no-single-hole, and
carrier-preservation requirements. The controlled expansion is the reset
check: v2 computes reset evidence over the active candidate graph after
rejected and absorbed nodes have been removed. It still abstains when the active
graph contains positive reset evidence or when the reset state is unknown.

This is not broad resolved-chamber absorption. It is a reset-aware active-graph
refinement of unresolved-later domination.

## v3 Relation

The v3 refinement remains inside the same relation family:

```text
unresolved_later_domination_from_existing_graph_facts_v3
```

It targets active graphs with exactly one resolved survivor. If that resolved
source has no legal carrier, no single-hole closure dependency, and the
nearest later unresolved candidate has a first legal carrier after the source,
v3 absorbs that nearest later unresolved candidate. It then repeats on the
active graph.

This relation does not say there is no reset in the number-theoretic sense. It
says the existing active graph has one resolved source, that source is an
empty-carrier chamber, and the next unresolved extension has a positive carrier
fact after the source. The single-resolved-source guard is load-bearing; a
broader empty-carrier version absorbed true boundaries in abstaining
multiple-resolved graphs during development and was not retained.

## Record Contract

Each emitted JSONL record uses:

- `record_type: PGS_INFERRED_PRIME_EXPERIMENTAL_GRAPH`
- `inference_status: INFERRED_BY_BOUNDARY_CERTIFICATE_GRAPH_V3`
- `production_approved: false`
- `cryptographic_use_approved: false`
- `classical_audit_required: true`
- `classical_audit_status: NOT_RUN`

The inferred value is emitted as an experimental graph certificate. It is not a
production prime-generation result.

## Audit Boundary

The solver writes graph records without classical validation. The audit mode
reads the emitted JSONL later and confirms whether `inferred_prime_q_hat` is
the first classical prime after `anchor_p`.

Classical validation is therefore downstream evidence, not a rule input.

## v0 Result

On anchors `11..10_000` with `candidate_bound = 128` and
`witness_bound = 127`, v0 emitted 36 experimental graph records.

Separate downstream audit confirmed 36/36 records with 0 failures.

This was safe but not a coverage breakthrough. Under the accepted v0 rule set,
the graph solver was operationally equivalent to the 005A-R emitter on this
surface.

## v1 Target

- anchors `11..10_000`;
- `candidate_bound = 128`;
- `witness_bound = 127`;
- rule set `005A-R` plus the single unresolved-later domination relation.

## v1 Result

```text
graph_solved_count: 42
graph_abstain_count: 1183
new_relation_applied_count: 169
new_relation_solution_count: 6
```

Separate downstream audit:

```text
audited_count: 42
confirmed_count: 42
failed_count: 0
new_relation_correct_count_after_audit: 6
new_relation_wrong_count_after_audit: 0
```

This is the first graph-solver coverage improvement beyond the 36-record
005A-R island while keeping downstream audit failures at zero.

## v2 Result

On the same surface:

```text
graph_solved_count: 130
graph_abstain_count: 1095
new_relation_applied_count: 1181
new_relation_solution_count: 94
v1_relation_applied_count: 169
v2_relation_applied_count: 1012
v2_relation_solution_count: 88
```

Separate downstream audit:

```text
audited_count: 130
confirmed_count: 130
failed_count: 0
new_relation_correct_count_after_audit: 94
new_relation_wrong_count_after_audit: 0
v2_relation_correct_count_after_audit: 88
v2_relation_wrong_count_after_audit: 0
```

This is a generator-facing coverage gain from 42 to 130 solved graph records
without any downstream audit failures.

## v3 Result

On the same surface:

```text
graph_solved_count: 211
graph_abstain_count: 1014
new_relation_applied_count: 2277
new_relation_solution_count: 175
v1_relation_applied_count: 169
v2_relation_applied_count: 1012
v2_relation_solution_count: 88
v3_relation_applied_count: 1096
v3_relation_solution_count: 81
```

Separate downstream audit:

```text
audited_count: 211
confirmed_count: 211
failed_count: 0
new_relation_correct_count_after_audit: 175
new_relation_wrong_count_after_audit: 0
v2_relation_correct_count_after_audit: 88
v2_relation_wrong_count_after_audit: 0
v3_relation_correct_count_after_audit: 81
v3_relation_wrong_count_after_audit: 0
```

The follow-up abstention analysis found no true-boundary rejection or
absorption in the remaining graph states:

```text
true_boundary_status_counts:
  RESOLVED: 962
  UNRESOLVED: 52
  REJECTED: 0
  ABSORBED: 0
  NOT_IN_CANDIDATE_SET: 0
```

Graph v3 is the first solver version to exceed 200 emitted experimental graph
records on anchors `11..10_000` while preserving zero downstream audit
failures on the tested surface.

## Failure Handling

Any audit failure is research evidence and must be recorded directly. It is not
a hidden error to patch around. A failed graph emission blocks the corresponding
rule composition from generator eligibility until the failure has a structural
explanation and the full matrix is rerun.
