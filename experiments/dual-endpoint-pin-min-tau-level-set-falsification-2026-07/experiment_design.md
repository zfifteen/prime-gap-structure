# Experiment design: dual right-pin falsification

## Purpose

Falsify the universal multi-tie right-pin claims P1–P3 from the dual-endpoint-pin insight package.

## Method

1. Build exact \(\tau[n]\) on \(0..\mathrm{hard\_limit}\) by linear accumulation.
2. Primes as \(\tau(n)=2\).
3. For each consecutive \((p,q)\) with \(p \in [p_{\min}, p_{\max}]\):
   - form \(L\), \(w\), \(w_R\), clearance \(= q - w_R\);
   - if \(\lvert L\rvert \ge 2\), score P1/P2/P3 aggregates.
4. Emit JSON summary + optional CE CSV.

## Regime pins

| Regime | \(p_{\max}\) | Role |
| --- | ---: | --- |
| A | \(2\cdot 10^6\) | P1 window |
| B | \(5\cdot 10^6\) | intermediate extension |
| C | \(10^7\) | P2 window |

## Pass / fail

| ID | Fail condition |
| --- | --- |
| P1 | On regime A (\(p_{\max}=2e6\)): multi-tie clearance \(> 32\) count \(> 0\) |
| P2 | On regime C (\(p_{\max}=1e7\)): multi-tie clearance \(> \max(32, \lfloor 0.25 C(q)\rfloor)\) count \(> 0\) |
| P3 | On each regime: among multi-tie \(g \ge 20\), median clearance \(> 8\), or linear climb of median across \(g\)-bins with \(n \ge 100\) |

## Commands

```bash
python3 -m pytest experiments/dual-endpoint-pin-min-tau-level-set-falsification-2026-07/test_probe_dual_pin.py -q

python3 experiments/dual-endpoint-pin-min-tau-level-set-falsification-2026-07/probe_dual_pin.py \
  --p-max 2000000 \
  --out experiments/dual-endpoint-pin-min-tau-level-set-falsification-2026-07/artifacts/results_pmax_2000000.json

python3 experiments/dual-endpoint-pin-min-tau-level-set-falsification-2026-07/probe_dual_pin.py \
  --p-max 5000000 \
  --out experiments/dual-endpoint-pin-min-tau-level-set-falsification-2026-07/artifacts/results_pmax_5000000.json

python3 experiments/dual-endpoint-pin-min-tau-level-set-falsification-2026-07/probe_dual_pin.py \
  --p-max 10000000 \
  --out experiments/dual-endpoint-pin-min-tau-level-set-falsification-2026-07/artifacts/results_pmax_10000000.json \
  --csv-ce experiments/dual-endpoint-pin-min-tau-level-set-falsification-2026-07/artifacts/counterexamples_p1_pmax_10000000.csv
```

Note: CSV name retains `p1` as historical label for clearance\(>32\) samples; P2 also uses those rows when they violate the P2 bound.

## Reproducibility

- Python 3 stdlib only
- Deterministic scan (no seed)
- Field prep: divisor accumulation; inference: \(\tau\) level-set only
