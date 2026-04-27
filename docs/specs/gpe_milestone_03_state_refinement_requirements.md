# GPE Milestone 3: State Refinement Requirements

## Purpose

Milestone 3 resolves the fact that the current reduced 14-state selected integer type is
not sufficient to output the exact next prime.

The state must be sharpened until the next-prime selection rule is single-valued:

$$B(q,S,w,d(w))=q^+$$

## Known Conflict

The committed catalog surface contains rows with the same reduced selected integer type
and different next-prime offsets:

| $q$ | $w$ | reduced selected integer type | $q^+$ | gap |
|---:|---:|---|---:|---:|
| $13$ | $14$ | `o4_d4_a1_even_semiprime` | $17$ | $4$ |
| $73$ | $74$ | `o4_d4_a1_even_semiprime` | $79$ | $6$ |

Therefore the reduced type alone cannot be the full GPE state.

## Required State Rule

Add only state ingredients that remove real selection-rule conflicts.

Candidate ingredients must be measured as ratios or invariant coordinates when
possible, including:

- current residue and wheel-open offset,
- previous reduced state,
- lag-2 transition rule state,
- prime-square interval utilization for $d(w)=4$,
- controller lock state,
- and any explicitly derived modular constraint needed by the selection rule.

No ingredient is accepted merely because it improves a statistical score. It
must reduce or eliminate exact selection-rule conflicts.

## Conflict Audit

For any proposed state $S$, the audit must group validation rows by:

$$q,S,w,d(w)$$

and verify that each group maps to one endpoint $q^+$.

Since $q$ itself is unique, the practical audit must also report reduced keys
with $q$ removed, so the state compression is visible rather than tautological.

## Acceptance Gate

Milestone 3 is complete when:

- the proposed state has no endpoint selection-rule conflicts on the validation
  surface,
- each state ingredient has a documented reason for inclusion,
- dropping any accepted ingredient reintroduces a measured conflict or fails a
  branch proof obligation,
- and the resulting state remains small enough to audit manually from one row.

## Non-Goals

This milestone does not create a generalized state framework or a configurable
feature search. It identifies the smallest state needed by the GPE selection rule.
