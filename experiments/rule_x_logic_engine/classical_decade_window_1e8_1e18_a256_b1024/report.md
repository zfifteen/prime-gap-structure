# Classical Decade Window Baseline: 10^8 Through 10^18

## Executive Summary

The classical baseline tested the same decade ladder as the Rule X run:

```text
decade windows: 11
anchors tested: 2816
window candidate hypotheses: 768077
classically tested candidates before first prime: 22685
exact matches: 2816
false emissions: 0
candidate-bound misses: 0
total runtime: 0.280352 seconds
```

The classical method found the next prime for every anchor because it directly
tests rightward candidates for primality and stops at the first prime.

## Classical Test Definition

For each accepted anchor prime `p`, the baseline enumerates the same wheel-open
candidate offsets used by the Rule X decade ladder:

```text
p < n <= p + 1024
n mod 30 in {1, 7, 11, 13, 17, 19, 23, 29}
```

It then applies ordinary primality testing from left to right and emits the
first prime candidate as `q`.

## Results By Decade

| decade | anchors | window candidates | tested candidates | exact matches | false emits | bound misses | seconds | tested/sec |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `10^8` | `256` | `69826` | `1204` | `256` | `0` | `0` | `0.018810` | `64008.51` |
| `10^9` | `256` | `69824` | `1419` | `256` | `0` | `0` | `0.018769` | `75604.06` |
| `10^10` | `256` | `69825` | `1716` | `256` | `0` | `0` | `0.022697` | `75604.29` |
| `10^11` | `256` | `69826` | `1653` | `256` | `0` | `0` | `0.038354` | `43099.02` |
| `10^12` | `256` | `69825` | `1978` | `256` | `0` | `0` | `0.023823` | `83030.46` |
| `10^13` | `256` | `69830` | `1902` | `256` | `0` | `0` | `0.023862` | `79709.72` |
| `10^14` | `256` | `69825` | `2302` | `256` | `0` | `0` | `0.025245` | `91184.87` |
| `10^15` | `256` | `69830` | `2549` | `256` | `0` | `0` | `0.026230` | `97178.49` |
| `10^16` | `256` | `69821` | `2525` | `256` | `0` | `0` | `0.026959` | `93662.05` |
| `10^17` | `256` | `69826` | `2603` | `256` | `0` | `0` | `0.027604` | `94297.64` |
| `10^18` | `256` | `69819` | `2834` | `256` | `0` | `0` | `0.028000` | `101212.93` |

## Rule X Comparison

| decade | Rule X matches | Classical matches | Rule X seconds | Classical seconds | Runtime ratio |
|---:|---:|---:|---:|---:|---:|
| `10^8` | `61` | `256` | `0.335441` | `0.018810` | `17.83x` |
| `10^9` | `48` | `256` | `0.475338` | `0.018769` | `25.33x` |
| `10^10` | `44` | `256` | `0.791562` | `0.022697` | `34.87x` |
| `10^11` | `43` | `256` | `1.007429` | `0.038354` | `26.27x` |
| `10^12` | `51` | `256` | `1.442697` | `0.023823` | `60.56x` |
| `10^13` | `50` | `256` | `1.762805` | `0.023862` | `73.88x` |
| `10^14` | `47` | `256` | `2.512229` | `0.025245` | `99.51x` |
| `10^15` | `45` | `256` | `3.562428` | `0.026230` | `135.81x` |
| `10^16` | `38` | `256` | `4.789365` | `0.026959` | `177.66x` |
| `10^17` | `49` | `256` | `7.174530` | `0.027604` | `259.91x` |
| `10^18` | `37` | `256` | `12.167169` | `0.028000` | `434.54x` |

## Aggregate Comparison

| Metric | Rule X | Classical |
|---|---:|---:|
| Anchors tested | `2816` | `2816` |
| Window candidate hypotheses | `768077` | `768077` |
| Exact matches | `513` | `2816` |
| Match rate | `18.217330%` | `100.000000%` |
| False emissions | `0` | `0` |
| Candidate-bound misses | `0` | `0` |
| Total runtime | `36.020993` seconds | `0.280352` seconds |

## Interpretation

The classical baseline is faster and complete on this benchmark because it uses
direct primality testing to identify the next prime boundary.

Rule X is measuring a different quantity: how often the boundary can be
selected from local structural consistency without promoting unresolved
interior landmarks into false boundaries. On this ladder, Rule X resolves
`513 / 2816` anchors with zero true-boundary rejections; classical testing
resolves `2816 / 2816` by directly testing primality.

## Artifacts

- Runner:
  [../run_classical_decade_window.py](../run_classical_decade_window.py)
- Aggregate summary:
  [summary.json](summary.json)
- Per-decade directories:
  [10e8](10e8/summary.json),
  [10e9](10e9/summary.json),
  [10e10](10e10/summary.json),
  [10e11](10e11/summary.json),
  [10e12](10e12/summary.json),
  [10e13](10e13/summary.json),
  [10e14](10e14/summary.json),
  [10e15](10e15/summary.json),
  [10e16](10e16/summary.json),
  [10e17](10e17/summary.json),
  [10e18](10e18/summary.json)
