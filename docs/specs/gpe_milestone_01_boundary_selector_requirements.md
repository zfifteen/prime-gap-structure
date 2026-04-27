# GPE Milestone 1: Endpoint Selector Requirements

## Purpose

Milestone 1 resolves the false closure rule:

$$q^+=w+1$$

The GPE must emit the next prime from an explicit next-prime selector instead:

$$q^+=B(q,S,w,d(w))$$

## Observable Inputs

The selector receives:

- $q$: the current known prime,
- $S$: the current GPE state,
- $w$: the GWR-selected integer for the next gap,
- $d(w)$: the divisor class of the selected integer.

The selector returns:

- $q^+$: the exact next prime after $q$.

## Required Behavior

1. The implementation must not use `winner + 1` as a closure rule.
2. The selector must return the exact next prime prime on every validation
   row.
3. The selector must fail explicitly when the required state is insufficient.
4. The selector must preserve one deterministic execution path.
5. The selector interface must be narrow enough to audit from a single current
   prime, state, selected integer, and selected divisor-count class.

## Validation Surface

The first hard-coded regression examples are:

| $q$ | $w$ | $d(w)$ | Required $q^+$ |
|---:|---:|---:|---:|
| $13$ | $14$ | $4$ | $17$ |
| $23$ | $25$ | $3$ | $29$ |
| $73$ | $74$ | $4$ | $79$ |

The row $q=23$ is the immediate guard against `winner + 1`.

## Acceptance Gate

Milestone 1 is complete when the repo has:

- a documented selector contract for $B(q,S,w,d(w))$,
- a deterministic validation harness comparing selector output to the exact
  DNI/GWR oracle,
- regression coverage for the examples above,
- and no implementation path that emits `winner + 1` as the general endpoint.

## Non-Goals

This milestone does not prove the final selector theorem. It creates the exact
interface and failure gate that later milestones must satisfy.
