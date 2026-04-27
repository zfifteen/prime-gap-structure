# GPE Milestone 2: NLSC Selection-Rule Requirements

## Purpose

Milestone 2 resolves the gap between an NLSC ceiling and an exact endpoint
selection rule.

NLSC gives:

$$q^+ \le T_{<}(w)$$

That is a hard upper endpoint. It is not yet an exact output rule.

## Required Branch Order

The branch order is fixed:

1. Solve the dominant $d(w)=4$ branch.
2. Solve the $d(w)=3$ branch.
3. Solve higher-divisor selection branches in increasing observed pressure order.

The first branch uses the concrete invariant:

$$q^+ \le S_{+}(w)$$

where $S_{+}(w)$ is the next prime-square threat after $w$.

## Required Behavior

For each branch, define a deterministic selection rule:

$$q^+=B_d(q,S,w)$$

where $d=d(w)$.

The selection rule must:

- return the exact right endpoint prime,
- remain inside the NLSC threat horizon,
- avoid candidate primality testing,
- use only explicitly named state and arithmetic ingredients,
- and fail explicitly on any row where the branch law is not defined.

## Dominant Branch Acceptance Gate

The $d(w)=4$ branch is complete when:

- the selection rule returns exact $q^+$ on the committed exact surface,
- no selected endpoint exceeds $S_{+}(w)$,
- every conflict is either eliminated by a documented state ingredient or
  reported as an unresolved blocker,
- and the proof note states why the chosen ingredients select the endpoint
  rather than merely bounding it.

## Full Milestone Acceptance Gate

Milestone 2 is complete when every observed selected divisor-count class has a branch selection rule
or an explicit unresolved theorem target.

The milestone is not complete if the only result is a smaller search interval.
The required outcome is exact next-prime selection.

## Non-Goals

This milestone does not introduce randomized repair steps, heuristic fallback
paths, or alternate selection modes. Each branch gets one deterministic rule.
