# Continuity: Chain-Horizon Pure-PGS Attack — 2026-08-16

**Branch:** research/chain-horizon-pure-pgs-selection
**Owner:** active session (Fate / zfifteen)
**Goal:** Resolve the most significant unanswered question by deriving H(p, s0, chain_state).

## Current state

The question file `docs/unanswered-questions/chain-horizon-closure/00_question.md` still correctly states the problem.
Multiple LLM solution drafts exist under `solutions/` and already converge on the same experiment:
mine the least-factor maximum of false shadow-chain nodes and test whether a PGS-visible bound exists that is ≪ √q.

Prior pilots (simulation + bounded runs) have already falsified the null that the horizon tracks √q.
The least-factor maximum stays local.

What is missing is the production-grade probe + promotion decision on the real high-scale surfaces.

## Immediate deliverables on this branch

1. STATUS.md under the unanswered-questions folder (status language upgraded to probe-ready).
2. A clean probe script that can be pointed at any existing or regenerated high-scale ledger.
3. Explicit promotion gate language that matches AGENTS.md status vocabulary.

## First-principles constraint

- No classical inference inside the generator path.
- H must be computed from quantities already present in the chamber-reset certificate / chain_state.
- Downstream audit remains allowed; generation must not require it.

## Success definition

Either:

A. A concrete H is promoted and the high-scale pure-PGS fraction jumps above 90 % with zero new audit failures, or

B. A sharp, named residual is recorded showing exactly which PGS-visible quantities are insufficient, tightening the taxonomy.

Both outcomes advance the program. Mediocrity is not an option.

Next commit will add the probe script itself.
