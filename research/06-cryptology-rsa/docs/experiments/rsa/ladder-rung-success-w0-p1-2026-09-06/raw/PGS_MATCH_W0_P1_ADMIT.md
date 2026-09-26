# PGS MATCH — Wave 0 shard W0-P1 Stage-6 admit

**Verdict: MATCH** (Measured admit on fixture `rsa_v2_128bit_static_001`)  
**Date:** 2026-09-06  
**Land:** `/workspace/pools/crew-wave0-w0-p1/out/wave0-w0-p1/`  
**Shard:** `W0-P1`  
**Pin:** `66bf995de3ca07fdad40648a5d1e4d25e504c022`  
**Window:** fixed `[-12,6]`

## Admit identity (Measured)
| field | value |
| --- | ---: |
| pair anchors (shard card) | L `9223372036854756211` / U `9223372036854795377` |
| closing lower_id | **anchor** = `9223372036854756211` |
| closing upper_id | **reset_endpoint** = `9223372036854795409` |
| δ_t | **-6** ∈ window |
| ft_real / lock / carrier | T / T / T |
| vacuous FT | false |
| base_close strict | **true** |
| base_close correction | false |
| rem0_used | **false** |
| not_x_only | true |
| stage6_admit | **true** |

## Independent PGS recompute
```
floor(N / 9223372036854756211) = 9223372036854795409  ✓
floor(N / 9223372036854795409) = 9223372036854756211  ✓
```
Product remainder `N - L*U = 384120072` (audit only; **not** used as inference). Mutual floor close holds without rem-0 selector.

## Checks
| Predicate | Result |
| --- | --- |
| ft_real standing rule | PASS |
| Substituted endpoints in strict_detail | PASS |
| Independent mutual floors | PASS |
| rem0_used=false | PASS |
| Window unchanged | PASS |
| Fake-close / classical-primary | FAIL not observed |

## Soft clarity (not DIFF)
Shard card quotes upper **anchor** `…95377`; closing upper identity is upper **reset_endpoint** `…95409`. Keep both explicit in Colony/Fate copy.

## Non-claims
- Not a theorem · not factorization language · PROOF.md untouched
- Wave-0 other shards: out of scope for this MATCH (hard-stopped)

## Next
**Do not name next compute wave** until Fate/Howard asks. Standing by.
