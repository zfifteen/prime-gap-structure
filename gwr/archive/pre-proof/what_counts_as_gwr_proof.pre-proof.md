# Retired Note: Former GWR Proof Gate

This file is kept only as historical context.

It is **not** the current contract for how the repo talks about proof.

## What Went Wrong

This note was previously used as a gating document for the claim that `GWR` is
proven.

In practice, that was an error.

The error was not that finite-reduction proofs are invalid.
The error was treating one specific script-first finite-reduction route as if
it were the required gateway for the theorem itself.

That created the wrong operational target:

- instead of asking whether the mathematics already supports a universal
  proof-level claim,
- it pushed the work into a narrow computer-assisted route that turned out not
  to be the right forcing function for this project.

## Current Status

The repo no longer uses this file as a mandatory proof bar.

The current proof-status note is
[`gwr_universal_bridge_closure.md`](./gwr_universal_bridge_closure.md), backed
by the committed certificate artifact
[`../../output/gwr_proof/proof_bridge_certificate_2e7.json`](../../output/gwr_proof/proof_bridge_certificate_2e7.json).

In particular:

- `Route B` style finite-remainder reduction is optional, not required,
- `Route B3` is not a mandatory gateway,
- and no script in `gwr/experiments/proof/` should be treated as the deciding
  authority for whether a mathematical proof claim is reasonable.

Those scripts are research instruments.
They can strengthen, stress-test, or clarify a proof attempt.
They do not replace the proof itself.

## Direct Mathematical Target

The direct mathematical target that replaced this retired gate was:

- the ordered-dominance theorem already handles later candidates,
- the remaining structural question is the elimination of earlier
  higher-divisor competing integers inside prime gaps.

That question is now addressed by the no-early-counterexample bridge verification record under
the recorded BHP/Robin constants.

No single proof style is imposed by this repo.

## Repo Wording Reset

This file must not be cited as a blocking contract against ordinary
proof-language drafting.

If a note or message needs to describe the state of the project, it should do
so directly from the mathematics and executed artifacts, not by appealing to a
retired script-first gate.
