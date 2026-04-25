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

The v1 addition is exactly one relation:

```text
unresolved_later_domination_from_existing_graph_facts
```

It absorbs only the nearest later unresolved candidate after a resolved source
when the source has no single-hole closure dependency, the target chamber
preserves the same first legal carrier, and the existing graph facts contain no
same-or-lower divisor reset evidence between the source and target.

The relation abstains when reset evidence is positive or unknown. It does not
use labels, candidate ranking, 005B, or broad resolved-chamber absorption.

## Record Contract

Each emitted JSONL record uses:

- `record_type: PGS_INFERRED_PRIME_EXPERIMENTAL_GRAPH`
- `inference_status: INFERRED_BY_BOUNDARY_CERTIFICATE_GRAPH_V1`
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

## Failure Handling

Any audit failure is research evidence and must be recorded directly. It is not
a hidden error to patch around. A failed graph emission blocks the corresponding
rule composition from generator eligibility until the failure has a structural
explanation and the full matrix is rerun.
