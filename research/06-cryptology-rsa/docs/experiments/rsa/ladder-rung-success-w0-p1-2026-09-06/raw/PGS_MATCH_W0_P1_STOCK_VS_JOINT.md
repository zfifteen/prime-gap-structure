# PGS MATCH — W0-P1 stock eval_strict vs joint-identity mutual floor

**Verdict: MATCH** on the distinction (and on admit as **joint-identity** close)  
**Date:** 2026-09-06  
**VERIFY:** `/workspace/agent-boards/poolboss-w0-p1-admit-verify-2026-09-06/VERIFY.json`  
**Prior admit MATCH:** `PGS_MATCH_W0_P1_ADMIT.md`

## Distinction (Measured)

### A — Stock `eval_strict` (chamber resets)
Uses `x=lower.anchor` but reciprocal check against **stock** `lower.reset` / `upper.reset`:
- `floor(N/x) == upper.reset` → TRUE (`…95409`)
- `floor(N/upper.reset) == lower.reset` → **FALSE** (`…56211` ≠ lower.reset `…56227`)
- `passed=false`

### B — Joint substituted endpoints (admit path)
Uses lower_id=**anchor** `…56211` × upper_id=**reset_endpoint** `…95409` as **both** sides of the mutual floor:
- `floor(N/…56211) == …95409` → TRUE
- `floor(N/…95409) == …56211` → TRUE
- Independent PGS recompute → TRUE · `rem0_used=false`

## Taxonomy
| Claim | PGS |
| --- | --- |
| Stock eval_strict admits this pair | **DIFF / false** — stock path fails |
| Joint anchor×reset_endpoint mutual floor closes | **MATCH** |
| Label `stage6_admit` for Colony/Fate | **MATCH with REVISE language**: say **joint-identity Stage-6 admit** (ft_real∧lock∧carrier + mutual floor on substituted ids), not “stock eval_strict passed” |
| Closing U published as reset `…95409` | Required soft fix (Pool ack) |

## Non-implications
- Does not claim stock resolver `eval_strict` alone would emit
- Does not claim factorization / rem-0
- No next-wave naming (Fate/Howard gate)
