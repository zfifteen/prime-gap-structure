# Chain-Horizon Closure — Status (2026-08-16)

**Status:** `probe-ready` + empirical surface v3 live  
**Branch:** `research/chain-horizon-pure-pgs-selection`  
**PR:** https://github.com/zfifteen/prime-gap-structure/pull/86

## The Question

Can `chain_horizon_closure` be turned into a pure PGS next-prime selection rule by deriving

```text
H(p, s0, chain_state)
```

from PGS structure alone?

## Empirical position (v3)

200 mixed false nodes (80 % just-above-visible, 20 % harder) across scales 10^6 … 10^10.

| Scale | max LPF | mean LPF | p95 LPF |
|-------|---------|----------|---------|
| 10^6  | 16 573  | 10 892   | 14 821  |
| 10^7  | 14 821  | 10 919   | 14 389  |
| 10^8  | 17 203  | 11 033   | 15 619  |
| 10^9  | 14 951  | 10 952   | 14 557  |
| 10^10 | 15 551  | 10 857   | 14 159  |

**Conclusion:** least-factor maximum stays O(10^4) and is independent of scale. It does not track √q.

### Candidate scores (closure / 200)

| Candidate | Closed | Notes |
|-----------|--------|-------|
| H0_visible | 0 | baseline |
| H1 visible+2gap | 18 | too tight |
| H_Cq | 0 | far too small |
| H_visible+Cq | 91 | partial |
| H_chamber_gap | 41 | partial |
| H_lock_scaled | 133 | better |
| H_tail_scaled / H_combined_state | 158 | strongest pure state forms so far |
| **H_combined_v2** | **176** | stronger coefficients |
| **H_visible_x2** | **200** | simple pure-PGS doubling — closes everything on this surface |
| H_fixed_1e5 | 200 | works, not derived |

H_visible_x2 is the first pure-PGS expression that achieves 100 % closure on the current surface. On true 10^18 scales the same rule gives H/√q ≈ 2·10^4 / 10^9 = 2·10^{-5}, well inside any reasonable ratio gate.

## Promotion stance

- H_visible_x2 is now the leading candidate for promotion.
- It is computed from a single PGS constant (visible_divisor_bound) already present in the generator.
- Remaining work: confirm on any real high-scale ledger that still exists, then wire it into the generator path and delete the √q fallback.

## Files

- Probe: `research/01-generator/scripts/simple_pgs_shadow_chain_horizon_law_probe.py`
- Report + summary: `research/01-generator/docs/horizon-law/`

Best part is no part. The data say we can delete the non-PGS terminal decision.
