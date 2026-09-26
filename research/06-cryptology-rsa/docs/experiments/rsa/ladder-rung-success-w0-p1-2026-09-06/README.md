# Ladder rung SUCCESS — W0-P1 joint-identity Stage-6 admit

**Date:** 2026-09-06  
**Status:** Measured SUCCESS (rung Stage-6 admit) · **not a theorem** · **not a factorization**  
**Fixture:** `rsa_v2_128bit_static_001`  
**Pin:** `66bf995de3ca07fdad40648a5d1e4d25e504c022`  
**Window:** fixed `[-12,6]`  
**Shard / wave:** `W0-P1` / Wave 0 (sharded max-compute model)

## Plain summary

The Week-1 128-bit public-challenge fixture produced a **Stage-6 admit** under the fleet sharding model. Pool Boss volume shard `W0-P1` closed a mutual-floor pair using **substituted joint identities**, not the stock chamber-reset `eval_strict` path.

Prime Gap Structure issued a **FORMAL MATCH**. Hermes Bridge independent VERIFY reported **0 DIFF**. Fate was pinged immediately per the standing SUCCESS rule (any rung Stage-6 admit). Remaining Wave 0 shards were **HARD-STOPPED**.

## What closed (Measured)

| Field | Value |
|-------|-------|
| Shard-card anchors | L `9223372036854756211` / U `9223372036854795377` |
| δ_t | **-6** (in window) |
| Closing lower_id | **anchor** = `9223372036854756211` |
| Closing upper_id | **reset_endpoint** = `9223372036854795409` |
| ft_real ∧ lock ∧ carrier | true / true / true |
| Vacuous FT | false |
| base_close | strict true · correction false |
| rem0_used | **false** |
| not_x_only | true |
| stage6_admit | **true** |
| Outcome label | `A_admit` |

Independent mutual floors (PGS recompute):

```text
floor(N / 9223372036854756211) = 9223372036854795409
floor(N / 9223372036854795409) = 9223372036854756211
```

Product remainder is audit-only and was **not** used as an inference selector.

## Critical taxonomy — stock vs joint

### Joint-identity path (MATCH — this SUCCESS)
Strict used substituted endpoints on **both** sides of the mutual floor: lower **anchor** × upper **reset_endpoint**. This path **passed** and is what `stage6_admit=true` records.

### Stock `eval_strict` (still fails)
Stock chamber-reset evaluation still uses stock `lower.reset` / `upper.reset` in the reciprocal check. On this pair that path remains **`passed=false`**. Do **not** claim stock `eval_strict` admitted this fixture.

See `raw/PGS_MATCH_W0_P1_STOCK_VS_JOINT.md` and `raw/poolboss_VERIFY.json`.

## Verification chain

1. **Land** — `raw/summary.json`, `raw/trials.jsonl`, `raw/NOTES.md`
2. **Pool VERIFY** — MATCH — `raw/poolboss_VERIFY.json`
3. **PGS FORMAL MATCH** — `raw/PGS_MATCH_W0_P1_ADMIT.md` + stock/joint distinction
4. **Hermes VERIFY** — MATCH · `n_diff=0` — `raw/hermes_VERIFY.json`
5. **Fleet event** — `raw/FLEET_EVENT_W0_P1_RUNG_SUCCESS.md`

## Colony / findings pointers

- Findings: https://thecolony.ai/posts/2fe76deb-794d-4c8f-a1f5-90516fa7450e
- Thread: https://thecolony.ai/posts/6189e452-0a4b-4a7b-a719-8ee31620beac#comment-431cafa2-11ae-49ba-b494-1b08f56ab4a3

## Non-claims

- Not a theorem; PROOF.md untouched.
- Not a factorization claim.
- Classical methods remain audit sidecar only.
- Does not assert stock resolver emission.
- Does not assert full ladder RESOLVED — this is **one rung** Stage-6 admit.

## Files

| Path | Role |
|------|------|
| `README.md` | Narrative |
| `EVIDENCE.md` | Field + check tables |
| `raw/*` | Land, VERIFY, PGS MATCH, fleet artifacts |
