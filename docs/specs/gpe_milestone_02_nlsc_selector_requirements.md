# GPE Milestone 2: NLSC Selector Requirements

## Purpose

Milestone 2 resolves the gap between an NLSC ceiling and an exact boundary
selector.

NLSC gives:

$$q^+ \le T_{<}(w)$$

That is a hard upper boundary. It is not yet an exact emission rule.

## Required Branch Order

The branch order is fixed:

1. Solve the dominant $d(w)=4$ branch.
2. Solve the $d(w)=3$ branch.
3. Solve higher-divisor winner branches in increasing observed pressure order.

The first branch uses the concrete invariant:

$$q^+ \le S_{+}(w)$$

where $S_{+}(w)$ is the next prime-square threat after $w$.

## Required Behavior

For each branch, define a deterministic selector:

$$q^+=B_d(q,S,w)$$

where $d=d(w)$.

The selector must:

- return the exact right boundary prime,
- remain inside the NLSC threat horizon,
- avoid candidate primality testing,
- use only explicitly named state and arithmetic ingredients,
- and fail explicitly on any row where the branch law is not defined.

## Dominant Branch Acceptance Gate

The $d(w)=4$ branch is complete when:

- the selector returns exact $q^+$ on the committed exact surface,
- no selected boundary exceeds $S_{+}(w)$,
- every collision is either eliminated by a documented state ingredient or
  reported as an unresolved blocker,
- and the proof note states why the chosen ingredients select the boundary
  rather than merely bounding it.

## Full Milestone Acceptance Gate

Milestone 2 is complete when every observed winner class has a branch selector
or an explicit unresolved theorem target.

The milestone is not complete if the only result is a smaller search interval.
The required outcome is exact boundary selection.

## Non-Goals

This milestone does not introduce randomized repair steps, heuristic fallback
paths, or alternate selector modes. Each branch gets one deterministic rule.
