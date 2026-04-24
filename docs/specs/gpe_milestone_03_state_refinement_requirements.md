# GPE Milestone 3: State Refinement Requirements

## Purpose

Milestone 3 resolves the fact that the current reduced 14-state winner type is
not sufficient to emit the exact next prime.

The state must be sharpened until the boundary selector is single-valued:

$$B(q,S,w,d(w))=q^+$$

## Known Collision

The committed catalog surface contains rows with the same reduced winner type
and different boundary offsets:

| $q$ | $w$ | reduced winner type | $q^+$ | gap |
|---:|---:|---|---:|---:|
| $13$ | $14$ | `o4_d4_a1_even_semiprime` | $17$ | $4$ |
| $73$ | $74$ | `o4_d4_a1_even_semiprime` | $79$ | $6$ |

Therefore the reduced type alone cannot be the full GPE state.

## Required State Rule

Add only state ingredients that remove real selector collisions.

Candidate ingredients must be measured as ratios or invariant coordinates when
possible, including:

- current residue and wheel-open offset,
- previous reduced state,
- lag-2 scheduler state,
- square-phase utilization for $d(w)=4$,
- controller lock state,
- and any explicitly derived modular constraint needed by the selector.

No ingredient is accepted merely because it improves a statistical score. It
must reduce or eliminate exact selector collisions.

## Collision Audit

For any proposed state $S$, the audit must group validation rows by:

$$q,S,w,d(w)$$

and verify that each group maps to one boundary $q^+$.

Since $q$ itself is unique, the practical audit must also report reduced keys
with $q$ removed, so the state compression is visible rather than tautological.

## Acceptance Gate

Milestone 3 is complete when:

- the proposed state has no boundary-selector collisions on the validation
  surface,
- each state ingredient has a documented reason for inclusion,
- dropping any accepted ingredient reintroduces a measured collision or fails a
  branch proof obligation,
- and the resulting state remains small enough to audit manually from one row.

## Non-Goals

This milestone does not create a generalized state framework or a configurable
feature search. It identifies the smallest state needed by the GPE selector.
