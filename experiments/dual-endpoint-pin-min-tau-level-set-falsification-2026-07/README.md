# Dual endpoint pin: multi-tie right-clearance falsification

## Executive summary

**P2 is falsified.** On left primes \(p \le 10^7\), multi-tie max clearance is **34** with **1** gap above 32 / above the P2 bound. P1 holds on \(p \le 2\cdot 10^6\) (max 22). P3 median stays 4.0. Dual right-pin is not a certificate invariant; bulk tendency remains tight (p95 \(\le 9\)). Theorems untouched. **Measured on regime only.**

Full narrative: [FINDINGS.md](FINDINGS.md) · claims: [HYPOTHESIS.md](HYPOTHESIS.md) · design: [experiment_design.md](experiment_design.md)

### Axis status

| Axis | Status |
| --- | --- |
| P1 (clearance \(\le 32\), \(p\le 2e6\)) | **holds** |
| P2 (bound through \(p\le 1e7\)) | **falsified** (1 CE at \(p=9725087\)) |
| P3 (median flat, \(g\ge 20\)) | **holds** on measured regimes |
| Dual pin as universal rule | **falsified** |
| Dual pin as bulk tendency | still true mid-scale |
| GWR / NLS / left compression | **theorem** |
| Program verified / validated | **not claimed** |

Insight parent: `experiments/dual-endpoint-pin-min-tau-level-set-2026-07/`

---

## Package

| Path | Role |
| --- | --- |
| `HYPOTHESIS.md` | P1–P3 |
| `experiment_design.md` | Protocol |
| `probe_dual_pin.py` | Deterministic scan |
| `test_probe_dual_pin.py` | 4 unit tests |
| `artifacts/results_pmax_*.json` | Regimes 2e6 / 5e6 / 1e7 |
| `artifacts/counterexamples_p1_pmax_10000000.csv` | clear\(>32\) samples |
| `FINDINGS.md` | Report |
| `README.md` | This file |

## Repro

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

## Headline CE

```text
p=9725087 q=9725141 g=54 m=4 w=9725097 w_R=9725107 clearance=34 L_size=5
```

## Exact limits

- Max regime \(p \le 10^7\). Not \(10^{18}\).
- Soft bulk tendency is not a theorem and is not program-validated.
