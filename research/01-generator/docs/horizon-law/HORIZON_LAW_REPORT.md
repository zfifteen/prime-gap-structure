# Horizon Law Probe Report (v3)

Nodes: 200  |  Promotion ready: False (ratio gate is scale-sensitive; absolute closure is the signal)

## Scale stats (max least-factor)

- 10^6: max=16573, mean=10891.5, p95=14821
- 10^7: max=14821, mean=10918.9, p95=14389
- 10^8: max=17203, mean=11032.8, p95=15619
- 10^9: max=14951, mean=10952.4, p95=14557
- 10^10: max=15551, mean=10857.0, p95=14159

## Candidate scores

- `H0_visible`: closed 0/200  mean H/√n=0.9148
- `H1_visible_plus_2maxgap`: closed 18/200  mean H/√n=0.9186
- `H_Cq`: closed 0/200  mean H/√n=0.0158
- `H_visible_plus_Cq`: closed 91/200  mean H/√n=0.9306
- `H_chamber_gap`: closed 41/200  mean H/√n=0.9224
- `H_lock_scaled`: closed 133/200  mean H/√n=0.9423
- `H_tail_scaled`: closed 158/200  mean H/√n=0.9675
- `H_combined_state`: closed 158/200  mean H/√n=0.9675
- `H_combined_v2`: closed 176/200  mean H/√n=1.2442
- `H_visible_x2`: closed 200/200  mean H/√n=1.8296
- `H_fixed_1e5`: closed 200/200  mean H/√n=9.1480

Max LPF remains O(10^4) across five orders of magnitude and does not track √q. H_visible_x2 (2 × visible_divisor_bound) is the first pure-PGS expression that achieves 100 % closure on this surface. On true 10^18 scales the same rule yields H/√q ≈ 2e-5. H_combined_v2 reaches 176/200. Leading candidate for promotion: H_visible_x2.
