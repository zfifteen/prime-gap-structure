# Boundary Certificate Graph Abstention Analysis

## Status

This is offline graph-solver analysis. It is not pure production emission and
does not approve cryptographic use.

Boundary Law 005 remains candidate-grade. Boundary Law 005B remains
quarantined. Classical labels are used only after the graph solver has already
produced its graph state, and only for reporting.

## Purpose

Boundary Certificate Graph Solver v0 safely emits 36 experimental graph
certificates on anchors `11..10_000`, but it does not improve coverage beyond
the 005A-R emitter. The abstention analysis identifies why the solver stops and
which graph relation should be added next.

The accepted v0 graph rules are:

- positive composite witness rejection;
- single-hole positive witness closure;
- carrier-locked pressure ceiling;
- 005A-R higher-divisor locked absorption.

The analysis does not add 005B, broad resolved-chamber absorption,
earliest-candidate dominance, scalar ranking, or any new emission path.

## Target Run

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

## Interpretation

The main blocker is not false resolved survivors and not candidate-bound
coverage. The graph already contains the actual boundary as a resolved
candidate in most abstentions. It abstains because unresolved candidates after
that resolved boundary remain live.

The next graph relation should therefore target later unresolved alternatives
after a resolved true-boundary-shaped certificate, using only existing legal
graph facts. It must not become broad resolved-chamber absorption. The rejected
Rule A showed that local resolution alone is nonselective.

## Next Implementation Step

Add exactly one candidate relation to the graph solver:

```text
unresolved_later_domination_from_existing_graph_facts
```

Before integration, define the relation as a label-free predicate over graph
facts, then test whether it increases `graph_solved_count` above 36 with:

```text
graph_failed_count: 0
true_boundary_rejected_or_absorbed: 0
```

If no label-free discriminator can be found, the relation should abstain rather
than absorb.
