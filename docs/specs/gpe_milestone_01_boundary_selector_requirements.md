# GPE Milestone 1: Endpoint Selection-Rule Requirements

## Purpose

Milestone 1 resolves the false closure rule:

$$q^+=w+1$$

The GPE must output the next prime from an explicit next-prime selection rule instead:

$$q^+=B(q,S,w,d(w))$$

## Observable Inputs

The selection rule receives:

- $q$: the current known prime,
- $S$: the current GPE state,
- $w$: the GWR-selected integer for the next gap,
- $d(w)$: the divisor class of the selected integer.

The selection rule returns:

- $q^+$: the exact next prime after $q$.

## Required Behavior

1. The implementation must not use `winner + 1` as a closure rule.
2. The selection rule must return the exact next prime prime on every validation
   row.
3. The selection rule must fail explicitly when the required state is insufficient.
4. The selection rule must preserve one deterministic execution path.
5. The selection rule interface must be narrow enough to audit from a single current
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

- a documented selection-rule contract for $B(q,S,w,d(w))$,
- a deterministic validation harness comparing selection rule output to the exact
  DNI/GWR oracle,
- regression coverage for the examples above,
- and no implementation path that outputs `winner + 1` as the general endpoint.

## Non-Goals

This milestone does not prove the final selection-rule theorem. It creates the exact
interface and failure gate that later milestones must satisfy.
