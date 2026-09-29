# Findings: dual right-pin falsification

## Executive summary

**The dual right-pin claim is falsified as a universal multi-tie rule.** On left primes through \(p \le 10^7\), multi-tie max clearance reaches **34**, with **1** gap exceeding both the hard threshold 32 and the registered P2 bound \(\max(32,\lfloor 0.25 C(q)\rfloor)\). P1 still holds on its original window (\(p_{\max}=2\cdot 10^6\), max clearance 22). P3 (flat median for \(g\ge 20\)) still holds (median 4.0 on all three regimes). Theorems are untouched. Status: **measured on mid-scale regimes only** (no \(10^{18}\) surface; not verified/validated).

---

## Hypothesis

From `experiments/dual-endpoint-pin-min-tau-level-set-2026-07/` and [HYPOTHESIS.md](HYPOTHESIS.md): multi-tie min-\(\tau\) level sets have small right clearance \(q - w_R\) as a hard structural dual of left compression.

## Results

| Regime \(p_{\max}\) | Multi-tie | Max clearance | clear \(> 32\) | P1 | P2 | P3 (median \(g\ge 20\)) |
| ---: | ---: | ---: | ---: | --- | --- | --- |
| \(2\cdot 10^6\) | 90,846 | 22 | 0 | **holds** | holds | holds (4.0) |
| \(5\cdot 10^6\) | 215,476 | 26 | 0 | out of P1 window | holds | holds (4.0) |
| \(10^7\) | 414,444 | **34** | **1** | out of P1 window | **falsified** | holds (4.0) |

Bulk at \(p_{\max}=10^7\): mean clearance \(\approx 3.80\), median 3.0, p95 9.0. Left theorem breaks: 0.

### Concrete P2 counter-example

```text
p = 9725087
q = 9725141
g = 54
m = 4
w = 9725097   (alpha = 10)
w_R = 9725107
clearance = 34
L_size = 5
C(q) = 130
P2 bound = 32
```

Artifacts: `artifacts/results_pmax_*.json`, `artifacts/counterexamples_p1_pmax_10000000.csv`.

## Interpretation

| Claim | Outcome |
| --- | --- |
| P1 clearance \(\le 32\) on \(p\le 2e6\) | **holds** on registered window |
| P2 clearance \(\le \max(32,\lfloor 0.25 C\rfloor)\) on \(p\le 1e7\) | **falsified** (1 CE) |
| P3 flat median for multi-tie \(g\ge 20\) | **holds** on measured regimes |
| Dual right-pin as universal certificate rule | **falsified** |
| Dual right-pin as high-probability tendency | still true on the bulk surface (p95 \(\le 9\)) |
| GWR / NLS / left compression | **theorem**, untouched |
| Residual-mean elevation | already **falsified** (valve package) |

**Program update:** treat floor-class bridges as a **strong statistical regularity**, not a hard invariant. Truncation after \(w_R\) may remain a heuristic for the majority of multi-tie gaps; it must not be used as a certificate property.

## Exact limits

- Highest left-prime regime: \(10^7\).
- One hard CE kills universal P2; denser CE rate at higher scale is unresolved.
- No verified / validated language for this package.

## Provenance

| Path | Role |
| --- | --- |
| `probe_dual_pin.py` | Deterministic probe |
| `test_probe_dual_pin.py` | 4 unit tests |
| `artifacts/` | JSON + CE CSV |
| Insight parent | `experiments/dual-endpoint-pin-min-tau-level-set-2026-07/` |

## Repro

```bash
python3 -m pytest experiments/dual-endpoint-pin-min-tau-level-set-falsification-2026-07/test_probe_dual_pin.py -q
python3 experiments/dual-endpoint-pin-min-tau-level-set-falsification-2026-07/probe_dual_pin.py \
  --p-max 10000000 \
  --out experiments/dual-endpoint-pin-min-tau-level-set-falsification-2026-07/artifacts/results_pmax_10000000.json \
  --csv-ce experiments/dual-endpoint-pin-min-tau-level-set-falsification-2026-07/artifacts/counterexamples_p1_pmax_10000000.csv
```
