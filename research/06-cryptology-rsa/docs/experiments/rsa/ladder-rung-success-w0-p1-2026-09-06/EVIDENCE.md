# Evidence tables — W0-P1

## Identities

| Role | Integer |
|------|--------:|
| Card L (anchor) | 9223372036854756211 |
| Card U (anchor) | 9223372036854795377 |
| Closing U (reset_endpoint) | 9223372036854795409 |
| δ_t | -6 |
| Pin | 66bf995de3ca07fdad40648a5d1e4d25e504c022 |
| Fixture | rsa_v2_128bit_static_001 |
| Window | [-12, 6] |

## Mutual floor (joint-identity)

| Check | Result |
|-------|--------|
| floor(N/L_anchor) == U_reset | TRUE |
| floor(N/U_reset) == L_anchor | TRUE |
| rem0 selector used | false |
| endpoints_are_stock_resets | false |

## Stock eval_strict (audit)

| Check | Result |
|-------|--------|
| floor(N/x=anchor) == upper.reset | true |
| floor(N/upper.reset) == lower.reset | **false** |
| stock passed | **false** |

## Reviewer verdicts

| Reviewer | Verdict |
|----------|---------|
| Pool Boss VERIFY | MATCH |
| PGS FORMAL MATCH (admit) | MATCH |
| PGS MATCH (stock vs joint) | MATCH on distinction |
| Hermes VERIFY | MATCH · n_diff=0 |
