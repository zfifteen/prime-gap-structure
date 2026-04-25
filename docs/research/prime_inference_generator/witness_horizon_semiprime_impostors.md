# Witness-Horizon Semiprime Impostors

## Status

This note documents an experimental generator finding from the PGS Prime
Inference Generator line. It is an offline, audit-backed finding. It is not
production pure emission, not cryptographic approval, and not a proof that the
current generator is complete.

The finding is reproducible from the generator-facing CLI:

```text
benchmarks/python/prime_inference_generator/experimental_graph_prime_generator.py
```

Classical factorization and first-boundary validation are used only after
emission, as downstream audit and failure classification. They are not solver
inputs.

## Headline Finding

Filtered risky-v5 failures are not random on the tested surface. After the
generator filters candidates with positive composite evidence up to the active
witness bound, the remaining false emissions concentrate at semiprimes whose
factors sit just beyond that bound.

Observed moving frontier:

```text
witness_bound = 127:
  first remaining failure: 17947 = 131 * 137

witness_bound = 149:
  first remaining failure: 24613 = 151 * 163
  first 100 remaining failures: 100 / 100 semiprimes
  factor_min: 151

witness_bound = 197:
  first remaining failure: 41989 = 199 * 211
  first 100 remaining failures: 100 / 100 semiprimes
  factor_min: 199
```

The observed failure front tracks the first unseen semiprime band above the
active witness horizon.

The companion note
[`semiprime_shadow_reorientation.md`](semiprime_shadow_reorientation.md)
records the stronger right-neighborhood finding: on the `witness_bound = 251`
surface, the semiprime shadows are left-side landmarks before nearby true
boundaries, not arbitrary false emissions.

## Definitions

The witness horizon is the active value of `witness_bound` used by the
experimental graph generator and its positive nonboundary filter.

A semiprime impostor is a false emitted boundary candidate whose emitted value
is composite with exactly two prime factors, while the generator has not seen
positive nonboundary evidence for those factors under the current witness
horizon.

The phenomenon is the observed movement of the first false-emission band as the
witness horizon increases.

## Generator Configuration

All runs below used:

```text
solver_version: filtered-v5
start_anchor: 11
max_anchor: 100000
candidate_bound: 128
audit: enabled
production_approved: false
cryptographic_use_approved: false
```

The number of anchors scanned was:

```text
anchors_scanned: 9588
```

The risky-v5 input stream was stable across these runs:

```text
risky_input_count: 7391
```

## Reproduction Commands

The automated measurement harness is:

```text
benchmarks/python/prime_inference_generator/witness_horizon_semiprime_analysis.py
```

Run the documented horizon sequence:

```bash
python3 benchmarks/python/prime_inference_generator/witness_horizon_semiprime_analysis.py \
  --start-anchor 11 \
  --max-anchor 100000 \
  --candidate-bound 128 \
  --witness-bounds 127,149,197,251,307 \
  --output-dir output/prime_inference_generator/witness_horizon_semiprime_analysis
```

The harness writes:

```text
witness_horizon_semiprime_analysis_summary.json
witness_horizon_semiprime_analysis_rows.jsonl
```

Each row includes `failed_count`, `semiprime_rate`, `factor_min`,
`factor_max`, `least_factor_delta_min`, `least_factor_delta_median`, and
`least_factor_delta_max`.

Run `filtered-v5` with `witness_bound = 149`:

```bash
rm -rf output/prime_inference_generator/filtered_v5_w149
python3 benchmarks/python/prime_inference_generator/experimental_graph_prime_generator.py \
  --solver-version filtered-v5 \
  --start-anchor 11 \
  --max-anchor 100000 \
  --candidate-bound 128 \
  --witness-bound 149 \
  --audit \
  --output-dir output/prime_inference_generator/filtered_v5_w149
```

Run `filtered-v5` with `witness_bound = 197`:

```bash
rm -rf output/prime_inference_generator/filtered_v5_w197
python3 benchmarks/python/prime_inference_generator/experimental_graph_prime_generator.py \
  --solver-version filtered-v5 \
  --start-anchor 11 \
  --max-anchor 100000 \
  --candidate-bound 128 \
  --witness-bound 197 \
  --audit \
  --output-dir output/prime_inference_generator/filtered_v5_w197
```

The same command with `--witness-bound 127` reproduces the lower-horizon run.

## Failure Factor Analysis

Use this downstream-only script after a generator run. It reads emitted records,
audits each emitted `inferred_prime_q_hat` against first-boundary semantics, and
factors only the records that fail audit.

```bash
python3 - <<'PY'
import json
from collections import Counter
from pathlib import Path
from sympy import factorint, primerange

records_path = Path(
    "output/prime_inference_generator/filtered_v5_w149/"
    "experimental_graph_prime_generator_records.jsonl"
)

failures = []
for line in records_path.read_text(encoding="utf-8").splitlines():
    if not line.strip():
        continue
    record = json.loads(line)
    anchor = int(record["anchor_p"])
    q_hat = int(record["inferred_prime_q_hat"])
    first = next(primerange(anchor + 1, q_hat + 1), None)
    if first == q_hat:
        continue
    factorization = factorint(q_hat)
    factors = []
    for prime, exponent in factorization.items():
        factors.extend([int(prime)] * int(exponent))
    failures.append(
        {
            "anchor_p": anchor,
            "inferred_prime_q_hat": q_hat,
            "first_prime_after_anchor": first,
            "factors": factors,
            "factorization": {int(k): int(v) for k, v in factorization.items()},
        }
    )
    if len(failures) >= 100:
        break

all_factors = [factor for row in failures for factor in row["factors"]]
summary = {
    "sample_failure_count": len(failures),
    "semiprime_count": sum(1 for row in failures if len(row["factors"]) == 2),
    "prime_power_count": sum(
        1
        for row in failures
        if len(set(row["factors"])) == 1 and len(row["factors"]) > 1
    ),
    "factor_min": min(all_factors) if all_factors else None,
    "factor_max": max(all_factors) if all_factors else None,
    "factor_distribution": dict(sorted(Counter(all_factors).items())),
    "first_10_failures": failures[:10],
}
print(json.dumps(summary, indent=2, sort_keys=True))
PY
```

Change `filtered_v5_w149` to `filtered_v5_w197` to reproduce the higher-horizon
failure distribution.

## Observed Run Results

### Witness Bound 127

```text
risky_input_count: 7391
filtered_count: 482
emitted_count: 6909
confirmed_count: 6039
failed_count: 870
filter_reason_counts:
  bounded_composite_witness: 463
  power_witness: 25
first_failure:
  anchor_p: 17939
  inferred_prime_q_hat: 17947
  factorization: 131 * 137
```

### Witness Bound 149

```text
risky_input_count: 7391
filtered_count: 707
emitted_count: 6684
confirmed_count: 6039
failed_count: 645
filter_reason_counts:
  bounded_composite_witness: 690
  power_witness: 25
first_failure:
  anchor_p: 24611
  inferred_prime_q_hat: 24613
  factorization: 151 * 163
```

First 100 failed emissions after downstream audit:

```text
sample_failure_count: 100
semiprime_count: 100
prime_power_count: 0
factor_min: 151
factor_max: 283
```

Factor distribution in that first-100 failure sample:

```text
151: 17
157: 18
163: 16
167: 13
173: 13
179: 8
181: 11
191: 12
193: 10
197: 5
199: 13
211: 6
223: 6
227: 5
229: 7
233: 5
239: 6
241: 4
251: 7
257: 4
263: 4
269: 3
271: 2
277: 3
281: 1
283: 1
```

The first ten failures:

```text
24611 -> 24613 = 151 * 163
25589 -> 25591 = 157 * 163
26119 -> 26123 = 151 * 173
26209 -> 26219 = 157 * 167
27143 -> 27161 = 157 * 173
27211 -> 27221 = 163 * 167
27329 -> 27331 = 151 * 181
28099 -> 28103 = 157 * 179
28411 -> 28417 = 157 * 181
28837 -> 28841 = 157 * 191
```

### Witness Bound 197

```text
risky_input_count: 7391
filtered_count: 1100
emitted_count: 6291
confirmed_count: 6039
failed_count: 252
filter_reason_counts:
  bounded_composite_witness: 1088
  power_witness: 25
first_failure:
  anchor_p: 41983
  inferred_prime_q_hat: 41989
  factorization: 199 * 211
```

First 100 failed emissions after downstream audit:

```text
sample_failure_count: 100
semiprime_count: 100
prime_power_count: 0
factor_min: 199
factor_max: 373
```

Factor distribution in that first-100 failure sample:

```text
199: 20
211: 18
223: 13
227: 13
229: 12
233: 14
239: 13
241: 8
251: 6
257: 9
263: 7
269: 7
271: 8
277: 5
281: 6
283: 9
293: 5
307: 5
311: 6
313: 4
317: 4
331: 2
337: 1
347: 1
349: 1
353: 1
359: 1
373: 1
```

The first ten failures:

```text
41983 -> 41989 = 199 * 211
44371 -> 44377 = 199 * 223
45161 -> 45173 = 199 * 227
45569 -> 45571 = 199 * 229
47051 -> 47053 = 211 * 223
47543 -> 47561 = 199 * 239
48313 -> 48319 = 211 * 229
49157 -> 49163 = 211 * 233
49943 -> 49949 = 199 * 251
50423 -> 50429 = 211 * 239
```

## Interpretation

The filtered-v5 generator is not making arbitrary false emissions on these
runs. Its remaining false emissions sit at the moving edge of its positive
composite evidence. When the witness bound increases, the earliest failure
moves to a semiprime whose factors are just above the new bound.

The confirmed count stays fixed across the tested witness horizons:

```text
confirmed_count: 6039
```

The false count falls as more semiprime impostors become visible to the
positive filter:

```text
witness_bound 127: failed_count 870
witness_bound 149: failed_count 645
witness_bound 197: failed_count 252
```

This shows a witness-front effect:

```text
PGS graph inference + finite witness horizon
```

The current generator can emit many correct boundaries, but the risky-v5
relation also emits semiprime impostors when their factors are beyond the
active witness horizon.

## Safety Boundary

This finding does not approve filtered-v5 for generator status. Filtered-v5
still fails downstream audit at every horizon documented here.

Current safe status:

```text
v6:
  current safe experimental generator
  low coverage
  zero downstream audit failures on 11..100000

filtered-v5:
  research-only
  high coverage
  failure stream dominated by witness-horizon semiprimes

risky-v5:
  quarantined research mode
```

## Reproduction Checklist

1. Run `experimental_graph_prime_generator.py` with `--solver-version
   filtered-v5`, `--candidate-bound 128`, and the chosen `--witness-bound`.
2. Use `--audit` so the generator writes the downstream audit summary.
3. Confirm the summary fields:
   `risky_input_count`, `filtered_count`, `emitted_count`,
   `audit_confirmed`, `audit_failed`, `first_failure`, and
   `filter_reason_counts`.
4. Run the downstream factor-analysis snippet against the emitted JSONL.
5. Verify that factorization is used only after emission and audit.

## Next Useful Measurement

The next generator-facing measurement is not another theorem note. It is a
full failure-factor distribution for filtered-v5 at higher witness horizons,
for example:

```text
witness_bound: 251
witness_bound: 307
```

The question is whether `failed_count` continues falling by exposing the next
semiprime band, and whether the first failed emission continues to move to
factors just above the active witness horizon.
