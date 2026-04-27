# Rule X Decade Window Report: 10^8 Through 10^18

## Executive Summary

The Rule X decade-window ladder tested `256` consecutive prime anchors at each
decade from `10^8` through `10^18`.

Across the full ladder:

```text
decade windows: 11
anchors tested: 2816
candidate hypotheses evaluated: 768077
exact unique matches: 513
true next prime rejections: 0
candidate-bound misses: 0
total runtime: 36.020993 seconds
```

Every decade window preserved the hard safety invariant:

```text
true_boundary_rejected_count = 0
```

The `10^18` window produced:

```text
anchors tested: 256
candidate hypotheses evaluated: 69819
exact unique matches: 37
match rate: 14.453125%
true next prime rejections: 0
runtime: 12.167169 seconds
```

## Important Scope Note

This is a high-scale window experiment, not exhaustive coverage of every prime
through `10^18`.

For this decade ladder, the experiment uses exact factorization as the
positive-witness oracle inside each finite window. That lets the same Rule X
candidate-elimination logic be measured at `10^18` without requiring a
trial-division witness horizon near `sqrt(10^18)`.

The Rule X decision shape is unchanged:

```text
candidate hypotheses
positive composite witnesses
unresolved interior holds
carrier lock after resolved survivor
lower-divisor threat ceiling
unique resolved survivor emission
downstream audit
```

Classical labels are used for anchor selection and audit. The reported result
is a decade-window measurement of the logic engine, not a production generator
claim.

## Results By Decade

| decade | anchors | candidates | exact unique matches | match rate | true rejected | bound misses | seconds | candidates/sec |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `10^8` | `256` | `69826` | `61` | `23.828125%` | `0` | `0` | `0.335441` | `208161.56` |
| `10^9` | `256` | `69824` | `48` | `18.750000%` | `0` | `0` | `0.475338` | `146893.25` |
| `10^10` | `256` | `69825` | `44` | `17.187500%` | `0` | `0` | `0.791562` | `88211.66` |
| `10^11` | `256` | `69826` | `43` | `16.796875%` | `0` | `0` | `1.007429` | `69311.11` |
| `10^12` | `256` | `69825` | `51` | `19.921875%` | `0` | `0` | `1.442697` | `48398.94` |
| `10^13` | `256` | `69830` | `50` | `19.531250%` | `0` | `0` | `1.762805` | `39613.01` |
| `10^14` | `256` | `69825` | `47` | `18.359375%` | `0` | `0` | `2.512229` | `27794.04` |
| `10^15` | `256` | `69830` | `45` | `17.578125%` | `0` | `0` | `3.562428` | `19601.80` |
| `10^16` | `256` | `69821` | `38` | `14.843750%` | `0` | `0` | `4.789365` | `14578.34` |
| `10^17` | `256` | `69826` | `49` | `19.140625%` | `0` | `0` | `7.174530` | `9732.48` |
| `10^18` | `256` | `69819` | `37` | `14.453125%` | `0` | `0` | `12.167169` | `5738.31` |

## Aggregate Totals

| Metric | Value |
|---|---:|
| Decade windows | `11` |
| Anchors tested | `2816` |
| Candidate hypotheses | `768077` |
| Exact unique matches | `513` |
| Aggregate match rate | `18.217330%` |
| True endpoint rejections | `0` |
| Candidate-bound misses | `0` |
| Total runtime | `36.020993` seconds |

## Interpretation

The decade ladder supports the high-scale stability of the Rule X
consistency-collapse mechanism on deterministic windows through `10^18`.

The match rate varies by decade but remains nontrivial at every scale. The
`10^18` window resolves `37 / 256` anchors while rejecting the true next prime
zero times.

Runtime increases with scale because high-scale exact factorization is used to
materialize positive witnesses in the window. The logic engine itself remains
small and deterministic; the high-scale measurement cost is dominated by the
classical witness oracle used for this experiment.

## Artifacts

- Runner:
  [../run_decade_window.py](../run_decade_window.py)
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
