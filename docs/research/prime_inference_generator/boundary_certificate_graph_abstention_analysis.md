# Boundary Certificate Graph Abstention Analysis

## Status

This is offline graph-solver analysis. It is not pure production emission and
does not approve cryptographic use.

Boundary Law 005 remains candidate-grade. Boundary Law 005B remains
quarantined. Classical labels are used only after the graph solver has already
produced its graph state, and only for reporting.

## Purpose

Boundary Certificate Graph Solver v0 safely emitted 36 experimental graph
certificates on anchors `11..10_000`, but did not improve coverage beyond the
005A-R emitter. The abstention analysis identified why the solver stopped and
which graph relation should be added next.

The accepted v0 graph rules are:

- positive composite witness rejection;
- single-hole positive witness closure;
- carrier-locked pressure ceiling;
- 005A-R higher-divisor locked absorption.

The analysis does not add 005B, broad resolved-chamber absorption,
earliest-candidate dominance, scalar ranking, or any new emission path.

## Target Run

The v0 abstention run showed:

```text
anchor_range: 11..10000
candidate_bound: 128
witness_bound: 127
anchors_evaluated: 1225
graph_solved_count: 36
graph_abstain_count: 1189
graph_confirmed_count: 36
graph_failed_count: 0
```

## Dominant Abstention Structure

The graph solver usually has already resolved the true boundary, but it cannot
emit because later unresolved alternatives remain live.

```text
TRUE_BOUNDARY_RESOLVED_BUT_UNRESOLVED_LATER_REMAIN: 1137
TRUE_BOUNDARY_UNRESOLVED: 52
```

The true-boundary status split is:

```text
RESOLVED: 1137
UNRESOLVED: 52
REJECTED: 0
ABSORBED: 0
NOT_IN_CANDIDATE_SET: 0
```

No true boundary was rejected or absorbed by the accepted v0 graph rules.

## Missing Relation Patterns

The primary missing relation pattern counts are:

```text
NEED_UNRESOLVED_LATER_DOMINATION: 1137
NEED_TRUE_BOUNDARY_CLOSURE: 52
```

The dominant pattern is:

```text
NEED_UNRESOLVED_LATER_DOMINATION
```

The recommended next relation is:

```text
unresolved_later_domination_from_existing_graph_facts
```

## v1 Follow-Up

The recommended relation was added as a single label-free graph relation. On
the same surface, the solver moved from 36 solved graphs to 42 solved graphs
with zero audit failures.

```text
graph_solved_count: 42
graph_abstain_count: 1183
graph_confirmed_count: 42
graph_failed_count: 0
```

The remaining abstention split is:

```text
TRUE_BOUNDARY_RESOLVED_BUT_UNRESOLVED_LATER_REMAIN: 1131
TRUE_BOUNDARY_UNRESOLVED: 52
```

The dominant missing pattern remains:

```text
NEED_UNRESOLVED_LATER_DOMINATION
```

## Interpretation

The main blocker is not false resolved survivors and not candidate-bound
coverage. The graph already contains the actual boundary as a resolved
candidate in most abstentions. It abstains because unresolved candidates after
that resolved boundary remain live.

The graph still needs a stronger unresolved-later domination discriminator.
The v1 relation proves that this path can increase coverage, but most later
unresolved alternatives remain live. Any next relation must stay label-free and
must not become broad resolved-chamber absorption.

## Next Implementation Step

The next candidate relation should refine unresolved-later domination rather
than switch to an unrelated signal:

```text
unresolved_later_domination_from_existing_graph_facts_v2
```

Before integration, define the refinement as a label-free predicate over graph
facts, then test whether it increases `graph_solved_count` above 42 with:

```text
graph_failed_count: 0
true_boundary_rejected_or_absorbed: 0
```

If no label-free discriminator can be found, the relation should abstain rather
than absorb.
