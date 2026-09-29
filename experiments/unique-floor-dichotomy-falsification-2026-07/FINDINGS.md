# Findings: Unique Floor Dichotomy (mid-scale + \(10^{18}\) ladder)

## Executive summary

**U2 is falsified on the executed decade ladder \(10^8\) through \(10^{18}\).** Among ladder gaps with \(m=4\) and \(g \ge 20\), the multi-tie rate is **0.9429** (\(1421/1507\)), below the registered 0.99 floor. Unique semiprime floors with \(g \ge 20\) are common at high scale (86 such rows on the ladder), so “long non-square corridors are almost surely multi-tie” fails as a hard rule.

**U1 and U3 still hold** under their high-scale ceilings on that ladder (unique \(m=4\) max \(g=52 \ll 0.5\,C(q)\); unique \(m \ge 8\) max \(g=16\)). Mid-scale consecutive scans through \(p \le 10^7\) still show U1–U3 hold under the original mid-scale schedule. U4 square contrast is **missing on the ladder sample** (zero unique \(m=3\) in 2805 gaps). Theorems untouched.

Status: **measured on executed surfaces including a \(10^{18}\) decade ladder**. Not theorem. Dichotomy is **partially falsified** (U2). Do not use verified/validated language for the dichotomy as a whole.

---

## Surfaces executed

| Surface | Form | Result |
| --- | --- | --- |
| Consecutive mid-scale | \(p \le 2\cdot 10^6, 5\cdot 10^6, 10^7\) | U1–U3 **hold**; U4 contrast ok |
| Decade ladder | 256 primes/decade, \(10^8..10^{18}\) (2805 gaps) | **U2 falsified**; U1/U3 hold; U4 missing |
| Large-gap CSV supplement | 40 widest listed gaps \(g \ge 100\) near \(10^{12}..10^{18}\) | All 40 with \(m=4\) multi-tie (rate 1.0); 0 unique \(m=4\) |

Ladder artifact: `artifacts/results_decade_ladder_1e8_1e18.json`  
Mid-scale artifacts: `artifacts/results_pmax_*.json`

---

## Mid-scale consecutive (unchanged outcome)

| \(p_{\max}\) | Unique \(m=4\) max \(g\) | Unique \(m=3\) max \(g\) | Unique \(m\ge 8\) max \(g\) | Multi rate \(m=4\), \(g\ge 20\) | U1 | U2 | U3 | U4 |
| ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| \(2\cdot 10^6\) | 30 | 82 | 10 | 0.9981 | holds | holds | holds | ok |
| \(5\cdot 10^6\) | 34 | 102 | 12 | 0.9960 | holds | holds | holds | ok |
| \(10^7\) | 34 | 102 | 12 | 0.9941 | holds | holds | holds | ok |

---

## Decade ladder \(10^8..10^{18}\) (new)

| Quantity | Value |
| --- | ---: |
| Gaps | 2805 |
| Profile match vs GWR walk | 2805 / 2805 (0 mismatches) |
| Unique \(m=4\) | 470 |
| Unique \(m=3\) | 0 |
| Unique \(m \ge 8\) | 347 |
| \(m=4\), \(g \ge 20\) | 1507 |
| Multi among those | 1421 |
| Multi rate (U2) | **0.9429** |
| Unique \(m=4\) max \(g\) | **52** |
| Unique \(m \ge 8\) max \(g\) | 16 |
| U1 hits (over high-scale ceiling) | 0 |
| U3 hits | 0 |
| Wall time | ~70 s |

### Per-decade multi rates (\(m=4\), \(g \ge 20\))

| Decade | Multi rate | Unique \(m=4\) max \(g\) |
| ---: | ---: | ---: |
| \(10^8\) | 1.000 | 18 |
| \(10^9\) | 0.981 | 28 |
| \(10^{10}\) | 0.967 | 28 |
| \(10^{11}\) | 0.968 | 36 |
| \(10^{12}\) | 0.971 | 24 |
| \(10^{13}\) | 0.964 | 32 |
| \(10^{14}\) | 0.954 | 26 |
| \(10^{15}\) | 0.901 | 38 |
| \(10^{16}\) | 0.917 | 42 |
| \(10^{17}\) | 0.889 | 52 |
| \(10^{18}\) | 0.916 | 36 |

Rates fall below 0.99 from \(10^9\) onward and sit near 0.89–0.92 at the highest decades.

### Extremal unique \(m=4\) on ladder

```text
p = 100000000000002649   (~10^17)
q = 100000000000002701
g = 52
m = 4
w = 100000000000002677
alpha = 28
L_size = 1
C(q) = 767
u1_ceiling = 383
```

### Large-gap CSV supplement

Top 40 listed gaps with \(g \ge 100\) from `data/external/primegap_list_records_1e12_1e18.csv`: all analyzed endpoints prime under the field; all 40 had \(m=4\) and \(\lvert L\rvert \ge 2\). Very wide gaps still look multi-tie. That does **not** rescue U2 at the registered threshold \(g \ge 20\), multi \(\ge 0.99\).

---

## Interpretation

| Claim | Mid-scale \(p\le 10^7\) | Ladder incl. \(10^{18}\) |
| --- | --- | --- |
| U1 unique \(m=4\) short vs ceiling | holds (max 34) | **holds** (max 52 \(\ll\) high-scale ceiling) |
| U2 long \(m=4\) multi \(\ge 0.99\) | holds (\(\ge 0.994\)) | **falsified** (0.943 overall; decades to 0.89) |
| U3 unique high floor short | holds | **holds** (max 16 under soft high-scale ceiling) |
| U4 square long unique | contrast ok | **missing on ladder sample** |

**What dies:** the hard claim that non-square long corridors (\(g \ge 20\), \(m=4\)) are multi-tie at \(\ge 99\%\). At high scale, unique semiprime floors with moderate length are ordinary.

**What survives as softer measured structure:** unique \(m=4\) lengths stay far below \(C(q)\); unique high floors stay small; **record-scale** gaps in the external list remain multi-tie on the 40-row sample.

**Program update:** Unique Floor Dichotomy is **not** a package-level survivor. Split status: U2 **falsified** on the mandatory high-scale ladder; U1/U3 **not falsified** under stated ceilings. Certificate rules that assumed near-certain multi-tie on every \(g \ge 20\) non-square floor are invalid.

---

## High-scale claim ceilings (registered for ladder)

| ID | High-scale rule |
| --- | --- |
| U1 | unique \(m=4\) \(\Rightarrow\) \(g \le \max(48, \lfloor 0.5 C(q)\rfloor)\) |
| U2 | among \(m=4\), \(g \ge 20\): multi rate \(\ge 0.99\) (**failed**) |
| U3 | unique \(m \ge 8\) \(\Rightarrow\) \(g \le \max(16, \lfloor 0.15 C(q)\rfloor)\) |

---

## Exact limits

- Ladder is **sampled** consecutive primes at decade anchors, not all primes to \(10^{18}\).
- Field uses repo `divisor_counts_segment` (same stack as recursive walk; residual primality classification is field prep).
- Dichotomy is not a theorem. Partial hold of U1/U3 is not program-level validation of the full insight.
- Forbidden for the full dichotomy: verified / validated language.

## Repro

```bash
# Mid-scale consecutive
python3 experiments/unique-floor-dichotomy-falsification-2026-07/probe_unique_floor.py --p-max 10000000 \
  --out experiments/unique-floor-dichotomy-falsification-2026-07/artifacts/results_pmax_10000000.json

# Decade ladder including 10^18
PYTHONPATH=src/python python3 experiments/unique-floor-dichotomy-falsification-2026-07/probe_unique_floor_decade_ladder.py \
  --min-exp 8 --max-exp 18 --primes-per-decade 256 \
  --out experiments/unique-floor-dichotomy-falsification-2026-07/artifacts/results_decade_ladder_1e8_1e18.json

python3 -m pytest experiments/unique-floor-dichotomy-falsification-2026-07/test_probe_unique_floor.py -q
```
