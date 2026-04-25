# Boundary Certificate Graph v4 Abstention Profile

## Status

This is offline graph-solver analysis. It does not add a v4 relation, pure
production emission, cryptographic approval, 005B, broad resolved-chamber
absorption, earliest-candidate dominance, or scalar ranking.

Boundary Law 005 remains candidate-grade. Classical labels are used only after
Graph Solver v3 has already produced its graph state, and only for reporting.

## Target Surface

```text
anchor_range: 11..10000
candidate_bound: 128
witness_bound: 127
solver_version: v3
```

## v3 State

Graph Solver v3 is confirmed as the current generator-facing baseline on this
surface:

```text
anchors_evaluated: 1225
v3_graph_solved_count: 211
v3_graph_abstain_count: 1014
v3_graph_confirmed_count: 211
v3_graph_failed_count: 0
```

The remaining primary abstention split is:

```text
TRUE_BOUNDARY_RESOLVED_BUT_UNRESOLVED_LATER_REMAIN: 959
TRUE_BOUNDARY_RESOLVED_WITH_MULTIPLE_RESOLVED_SURVIVORS: 3
TRUE_BOUNDARY_UNRESOLVED: 52
```

The true-boundary status split remains safe:

```text
RESOLVED: 962
UNRESOLVED: 52
REJECTED: 0
ABSORBED: 0
NOT_IN_CANDIDATE_SET: 0
```

## v1/v2/v3 Abstention Causes

For the selected source-target pairs in the remaining v3 abstentions:

```text
v1_abstain_reason_counts:
  RESET_STATUS_UNKNOWN: 836
  SOURCE_SINGLE_HOLE_CLOSURE_USED_TRUE: 175
  NO_TARGET_CANDIDATE: 3

v2_abstain_reason_counts:
  ACTIVE_RESET_STATUS_UNKNOWN: 836
  SOURCE_SINGLE_HOLE_CLOSURE_USED_TRUE: 175
  NO_TARGET_CANDIDATE: 3

v3_abstain_reason_counts:
  TARGET_HAS_NO_LEGAL_CARRIER: 784
  ACTIVE_GRAPH_NOT_SINGLE_RESOLVED: 230
```

The dominant remaining unresolved-later blocker is not carrier preservation.
It is a missing reset discriminator for nearest unresolved targets that have no
legal carrier.

## Candidate v4 Hints

The observed hint counts are:

```text
UNKNOWN_RESET_STATE_DISCRIMINATOR: 784
FALSE_RESOLVED_SURVIVOR_REJECTION_PROFILE: 178
TRUE_BOUNDARY_CLOSURE_PROFILE: 52
```

The recommended next relation is:

```text
unresolved_later_domination_target_no_carrier_reset_discriminator
```

This recommendation comes from the dominant observed v3 abstention structure.
It is not a v4 implementation approval. A v4 relation must still be defined as
a label-free graph predicate, then audited downstream after graph emission.

## Interpretation

Graph Solver v3 already solves 211 anchors on this surface. In most remaining
abstentions, the true boundary is resolved and later unresolved alternatives
remain live. The nearest unresolved target after the resolved source often has
no legal carrier, which leaves v1 and v2 in an unknown reset state and leaves
v3 without its target-carrier condition.

The next implementation step should stay inside unresolved-later domination:
define a target-no-carrier reset discriminator that can absorb a nearest later
unresolved target only when existing graph facts supply positive legal support.
If the discriminator cannot be made label-free, it must abstain.
