# Candidate-Constraint Graph Abstention Analysis

## Status

This is offline graph-solver analysis. It is not pure production output and
does not approve cryptographic use.

Next-Prime Law 005 remains candidate-grade. Next-Prime Law 005B remains
quarantined. Classical labels are used only after the graph solver has already
produced its graph state, and only for reporting.

## Purpose

Candidate-Constraint Graph Solver v0 safely outputted 36 experimental graph
diagnostic records on input primes `11..10_000`, but did not improve coverage beyond the
005A-R outputter. The abstention analysis identified why the solver stopped and
which graph relation should be added next.

The accepted v0 graph rules are:

- positive composite witness rejection;
- single-hole positive witness closure;
- selected-integer-locked pressure ceiling;
- 005A-R higher-divisor locked absorption.

The analysis does not add 005B, broad resolved-interval absorption,
earliest-candidate dominance, scalar ranking, or any new output path.

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

The graph solver usually has already resolved the true next prime, but it cannot
output because later unresolved alternatives remain live.

```text
TRUE_BOUNDARY_RESOLVED_BUT_UNRESOLVED_LATER_REMAIN: 1137
TRUE_BOUNDARY_UNRESOLVED: 52
```

The true-next-prime status split is:

```text
RESOLVED: 1137
UNRESOLVED: 52
REJECTED: 0
ABSORBED: 0
NOT_IN_CANDIDATE_SET: 0
```

No true next prime was rejected or absorbed by the accepted v0 graph rules.

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

## v2 Follow-Up

The v2 refinement kept the same unresolved-later domination family and changed
only the reset-evidence lens. It evaluates reset evidence over the active
candidate graph after rejected and absorbed nodes have been removed, while
still requiring selected-integer preservation and abstaining on positive or unknown
reset evidence.

```text
graph_solved_count: 130
graph_abstain_count: 1095
graph_confirmed_count: 130
graph_failed_count: 0
v2_relation_correct_count_after_audit: 88
v2_relation_wrong_count_after_audit: 0
```

The remaining abstention split is:

```text
TRUE_BOUNDARY_RESOLVED_BUT_UNRESOLVED_LATER_REMAIN: 1040
TRUE_BOUNDARY_RESOLVED_WITH_MULTIPLE_RESOLVED_SURVIVORS: 3
TRUE_BOUNDARY_UNRESOLVED: 52
```

The dominant missing pattern remains unresolved-later domination, but the
v2 result shows that active-graph reset awareness is the right refinement path.

## v3 Follow-Up

The v3 refinement stayed inside unresolved-later domination. It added a narrow
empty-selected-integer extension relation that fires only when the active graph has
exactly one resolved candidate, that source has no legal integer, and the
nearest later unresolved extension has a first legal integer after the source.

On the same surface:

```text
graph_solved_count: 211
graph_abstain_count: 1014
graph_confirmed_count: 211
graph_failed_count: 0
v3_relation_correct_count_after_audit: 81
v3_relation_wrong_count_after_audit: 0
```

The remaining abstention split is:

```text
TRUE_BOUNDARY_RESOLVED_BUT_UNRESOLVED_LATER_REMAIN: 959
TRUE_BOUNDARY_RESOLVED_WITH_MULTIPLE_RESOLVED_SURVIVORS: 3
TRUE_BOUNDARY_UNRESOLVED: 52
```

The true-next-prime status split after v3 is:

```text
RESOLVED: 962
UNRESOLVED: 52
REJECTED: 0
ABSORBED: 0
NOT_IN_CANDIDATE_SET: 0
```

The dominant missing pattern remains:

```text
NEED_UNRESOLVED_LATER_DOMINATION: 959
```

## v4 Follow-Up

The v4 refinement stayed inside unresolved-later domination. It added the
target-no-selected-integer reset discriminator identified by the v4 abstention profile.
The relation absorbs only the nearest later unresolved target when the active
graph has exactly one resolved candidate, the source is not single-hole
dependent, the target has no legal integer, and the active graph contains no
positive reset evidence between source and target.

On the same surface:

```text
graph_solved_count: 447
graph_abstain_count: 778
graph_confirmed_count: 447
graph_failed_count: 0
v4_relation_correct_count_after_audit: 236
v4_relation_wrong_count_after_audit: 0
```

The remaining abstention split is:

```text
TRUE_BOUNDARY_RESOLVED_BUT_UNRESOLVED_LATER_REMAIN: 723
TRUE_BOUNDARY_RESOLVED_WITH_MULTIPLE_RESOLVED_SURVIVORS: 3
TRUE_BOUNDARY_UNRESOLVED: 52
```

The true-next-prime status split after v4 is:

```text
RESOLVED: 726
UNRESOLVED: 52
REJECTED: 0
ABSORBED: 0
NOT_IN_CANDIDATE_SET: 0
```

The dominant missing pattern remains:

```text
NEED_UNRESOLVED_LATER_DOMINATION: 723
```

## v5 Follow-Up

The v5 refinement stayed inside unresolved-later domination. It re-evaluated
the v3 empty-source legal-integer extension after v4 had removed the no-selected-integer
nearest blockers. The relation absorbs only the nearest later unresolved
target when the active graph has exactly one resolved candidate, the source has
no legal integer, the source is not single-hole dependent, and the target has
its first legal integer after the source.

On the same surface:

```text
graph_solved_count: 995
graph_abstain_count: 230
graph_confirmed_count: 995
graph_failed_count: 0
v5_relation_correct_count_after_audit: 548
v5_relation_wrong_count_after_audit: 0
```

The remaining abstention split is:

```text
TRUE_BOUNDARY_RESOLVED_BUT_UNRESOLVED_LATER_REMAIN: 175
TRUE_BOUNDARY_RESOLVED_WITH_MULTIPLE_RESOLVED_SURVIVORS: 3
TRUE_BOUNDARY_UNRESOLVED: 52
```

The true-next-prime status split after v5 is:

```text
RESOLVED: 178
UNRESOLVED: 52
REJECTED: 0
ABSORBED: 0
NOT_IN_CANDIDATE_SET: 0
```

The dominant missing pattern remains:

```text
NEED_UNRESOLVED_LATER_DOMINATION: 175
NEED_TRUE_BOUNDARY_CLOSURE: 52
NEED_FALSE_RESOLVED_SURVIVOR_REJECTION: 3
```

## Interpretation

The main blocker is not false resolved candidates and not candidate-bound
coverage. After v5, the graph solves 995 of 1225 tested input primes with no audit
failure. In the remaining abstentions, the graph still contains the actual
endpoint as a resolved candidate in 178 rows and leaves it unresolved in 52
rows.

The graph still needs a stronger unresolved-later domination discriminator.
The v1 through v5 relations prove that this path can increase coverage, but
175 rows still retain later unresolved alternatives after a resolved true
endpoint. Any next relation must stay label-free and must not become broad
resolved-interval absorption.

## Next Implementation Step

The next refinement should still start from this family:

```text
unresolved_later_domination_from_existing_graph_facts
```

Before integration, define the refinement as a label-free predicate over graph
facts, then test whether it increases `graph_solved_count` above 995 with:

```text
graph_failed_count: 0
true_boundary_rejected_or_absorbed: 0
```

If no label-free discriminator can be found, the relation should abstain rather
than absorb.
