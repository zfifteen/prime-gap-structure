# Rule X Logic Engine Performance Report

## Executive Summary

The Rule X summary engine evaluated the scale ladder through `10^7` quickly
while preserving the correctness invariant:

```text
true_boundary_rejected_count = 0
```

The largest timed run was:

```text
prime anchors: 11..10000000
candidate_bound: 256
witness_bound: 3163
anchors tested: 664575
candidate hypotheses: 45108041
exact unique matches: 140984
total runtime: 85.368115 seconds
candidate throughput: 528394.49 candidates/second
anchor throughput: 7784.82 anchors/second
```

The timed ladder shows that the engine remains near `0.53M` to `0.76M`
candidate hypotheses per second on this local run, including setup and CSV/JSON
artifact writing.

## Timing Method

The runner is:

```text
experiments/rule_x_logic_engine/run_scale_summary.py
```

Each run records:

- setup time: prime sieve, divisor-count table, witness table;
- evaluation time: Rule X candidate-hypothesis evaluation;
- write time: CSV and JSON artifact writing;
- total time;
- anchors per second;
- candidate hypotheses per second.

The runner uses the same Rule X decision layer as the documented engine:

```text
positive witness rejection
unresolved interior hold
semiprime-shadow landmark hold
carrier lock after resolved survivor
lower-divisor threat ceiling
unique resolved survivor emission
```

## Timed Scale Ladder

| max anchor | candidate bound | witness bound | anchors | candidates | exact unique matches | true rejected | total seconds | anchors/sec | candidates/sec |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `10000` | `128` | `101` | `1225` | `41502` | `305` | `0` | `0.054571` | `22447.67` | `760508.60` |
| `100000` | `128` | `317` | `9588` | `324809` | `2231` | `0` | `0.445153` | `21538.66` | `729656.99` |
| `200000` | `128` | `449` | `17980` | `609110` | `4121` | `0` | `0.850754` | `21134.20` | `715964.97` |
| `500000` | `128` | `709` | `41534` | `1407044` | `9279` | `0` | `2.007887` | `20685.43` | `700758.56` |
| `1000000` | `128` | `1009` | `78494` | `2659011` | `17249` | `0` | `4.756453` | `16502.63` | `559032.33` |
| `2000000` | `256` | `1423` | `148929` | `10108602` | `32446` | `0` | `18.159460` | `8201.18` | `556657.63` |
| `5000000` | `256` | `2239` | `348509` | `23655109` | `74934` | `0` | `43.619785` | `7989.70` | `542302.29` |
| `10000000` | `256` | `3163` | `664575` | `45108041` | `140984` | `0` | `85.368115` | `7784.82` | `528394.49` |

## Phase Timing

| max anchor | setup seconds | evaluation seconds | write seconds |
|---:|---:|---:|---:|
| `10000` | `0.004372` | `0.047024` | `0.002639` |
| `100000` | `0.054273` | `0.370573` | `0.016138` |
| `200000` | `0.113485` | `0.700746` | `0.028612` |
| `500000` | `0.306101` | `1.615454` | `0.066760` |
| `1000000` | `0.858710` | `3.714360` | `0.133590` |
| `2000000` | `1.994720` | `15.698807` | `0.261759` |
| `5000000` | `6.213452` | `36.618069` | `0.594174` |
| `10000000` | `14.820818` | `69.067020` | `1.090375` |

## Interpretation

The speed is real for the summary engine. The largest run evaluated
`45108041` candidate hypotheses in `85.368115` seconds while writing summary
artifacts.

The main cost is candidate evaluation. Setup grows with the sieve, divisor
table, and witness table, but evaluation remains the dominant phase. Artifact
writing is small compared with evaluation.

The throughput drop after `10^6` is expected because the ladder raises
`candidate_bound` from `128` to `256`, roughly doubling candidate hypotheses per
anchor.

## Exact Current Claim

On this local timed ladder, Rule X was:

- deterministic;
- fail-closed;
- audit-clean on every timed surface;
- fast enough to evaluate tens of millions of candidate hypotheses in minutes;
- resolving about one fifth of anchors on the scale-matched witness ladder.

The result is a performance report for the summary experiment runner, not a
claim that the current Minimal PGS Generator has the same runtime profile.
