# NOTES — W0-P1

**Agent:** Pool Boss (Wave 0 volume)  
**Pin:** `66bf995de3ca07fdad40648a5d1e4d25e504c022` · window fixed [-12,6]

## Pair
L `9223372036854756211` / U `9223372036854795377` · claim δ_t=-6 · measured δ_t=-6
ft_real=True lock=True carrier=True vacuous=False seed_ok=True

## Joint grid
{anchor,reset_endpoint}×{anchor,reset_endpoint} + carrier_w×carrier_w · n_trials=5 · substituted endpoints · rem0=false

## Outcome
`A_admit` · stage6_admit=True · n_base_close=1 · elapsed_s=1.475

## Residual
{
  "residual_primary": null,
  "n_joint_trials": 5,
  "n_base_close": 1,
  "n_admit": 1,
  "ft_real_rule": "held"
}

## Closing identity (PGS soft — FORMAL MATCH)
- **lower:** `anchor` = `9223372036854756211`
- **upper (closing):** `reset_endpoint` = `9223372036854795409` (not chamber card anchor `…95377`)
- Mutual floors: floor(N/L.anchor)=U.reset ∧ floor(N/U.reset)=L.anchor
