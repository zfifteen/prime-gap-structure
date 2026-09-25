# Lean core-stack program DONE

**Owner:** Hermes  
**Recorded:** 2026-08-06 (heartbeat close after live re-verify)  
**Program exit:** M5 / D1-D7 (first recorded 2026-07-23)

## Accept

A cold-path green build of `lean-4` machine-checks the PROOF.md core-stack **mirror**:

- **D4.1** tau / prime characterization (`PGS.Basic`)
- **D4.2** next-prime / weak L_FCL under tau-scan hyps (`ChamberReset`, `NextPrime`)
- **D4.3** GWR Ordered Comparison + leftmost min-tau maximizer (`GWR`)
- **D4.4 / D4.4b** non-vacuous UBC + Prime-Square Proximity via `dynamicCutoff` (`BoundedCompression`)
- **D4.6** named finite-base hypothesis bundles (`FiniteBases`) linked to certificate ids/hashes

## What a green build proves

- `cd lean-4 && lake build` succeeds (re-checked 2026-08-06).
- `lake env lean smoke-test.lean` succeeds (re-checked 2026-08-06).
- Core path `lean-4/PGS/*.lean`: **0** `sorry`.
- Core `axiom` allowlist: only `Placement.tau_prime_square_eq_three` (**audit premise** CL-003).
- No empty-shell PSP (`∃ C, dist ≤ C := dist`); bound shape is `C(n) = max(64, ⌈½(log n)²⌉)`.

## What it does **not** claim

- Does **not** edit or replace `PROOF.md` theorem status.
- Does **not** re-prove finite exhaustions; certificates remain named hypotheses.
- Does **not** select primes or feed generators.
- Does **not** use program-level “validated” implementation language for the generator.

## Authority pins

| Artifact | Role |
| --- | --- |
| `PROOF.md` | theorem status (unchanged by Lean) |
| `lean-4/DEFINITION_OF_DONE.md` | program DoD |
| `lean-4/SORRY_AXIOM_INVENTORY.md` | living axiom/sorry map |
| `lean-4/peer/M5_DOD_ACCEPT.md` | peer D1-D7 accept |
| `docs/lean-pgs-verification/index.html` | public status surface |
| Merge SHA (M5 on main) | `3d5b74c7` (PR #62) |
| Re-verify HEAD | `5a1c080d` (2026-08-06) |

Heartbeat disable: `scripts/lean-heartbeat/LEAN_HEARTBEAT_STATE.md` → `enabled: false`.

*Hermes  -  program goal met; further work is extension under D7.3 only.*
