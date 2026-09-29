# Unique Floor Dichotomy: falsification package

## Executive summary

**U2 is falsified on the executed \(10^8..10^{18}\) decade ladder** (multi-tie rate among \(m=4\), \(g\ge 20\) gaps = **0.9429**, below 0.99). U1 and U3 still hold under high-scale ceilings on that ladder. Mid-scale consecutive scans through \(p\le 10^7\) still pass U1–U3. The Core Insight’s hard “long non-square \(\Rightarrow\) multi-tie” arm is dead at high scale.

Full narrative: [FINDINGS.md](FINDINGS.md) · claims: [HYPOTHESIS.md](HYPOTHESIS.md)

### Axis status

| Axis | Mid-scale \(p\le 10^7\) | Ladder incl. \(10^{18}\) |
| --- | --- | --- |
| U1 unique \(m=4\) short vs ceiling | holds | **holds** |
| U2 long \(m=4\) multi \(\ge 0.99\) | holds | **falsified** |
| U3 unique high floor short | holds | **holds** |
| U4 square long unique | contrast ok | missing on ladder sample |
| Dichotomy as theorem | not claimed | not claimed |
| GWR / NLS / compression | theorem | theorem |

---

## Surfaces

| Artifact | Surface |
| --- | --- |
| `artifacts/results_pmax_*.json` | Consecutive \(p\le 2e6,5e6,1e7\) |
| `artifacts/results_decade_ladder_1e8_1e18.json` | 256 primes/decade, \(10^8..10^{18}\) + large-gap CSV |

## Ladder headline

| Quantity | Value |
| --- | ---: |
| Gaps | 2805 |
| Multi rate \(m=4\), \(g\ge 20\) | **0.9429** |
| Unique \(m=4\) max \(g\) | 52 |
| Unique \(m\ge 8\) max \(g\) | 16 |
| U1 / U3 hard hits | 0 / 0 |
| Profile mismatches | 0 |

## Repro

```bash
python3 -m pytest experiments/unique-floor-dichotomy-falsification-2026-07/test_probe_unique_floor.py -q

PYTHONPATH=src/python python3 experiments/unique-floor-dichotomy-falsification-2026-07/probe_unique_floor_decade_ladder.py \
  --min-exp 8 --max-exp 18 --primes-per-decade 256 \
  --out experiments/unique-floor-dichotomy-falsification-2026-07/artifacts/results_decade_ladder_1e8_1e18.json
```

## Exact limits

- Ladder is sampled decade anchors, not a full prime table to \(10^{18}\).
- Partial U1/U3 survival is not validation of the full insight.
- Not verified / validated as a universal dichotomy.
