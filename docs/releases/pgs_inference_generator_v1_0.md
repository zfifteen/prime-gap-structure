# PGS Inference Generator v1.0

PGS Inference Generator v1.0 is the frozen reference release for the current
successor-prime inference generator.

This release is superseded by
[PGS Inference Generator v1.1](pgs_inference_generator_v1_1_pgs_only.md),
which removes the displaced trial-division and fallback code paths from the
generator.

The frozen generator starts from an input prime `p` and emits exactly
one minimal record:

```json
{"p": 89, "q": 97}
```

The generator version is:

```text
PGS_GENERATOR_VERSION = 1.0.0
PGS_GENERATOR_FREEZE_ID = pgs_inference_generator_v1_0
```

## Frozen Object

The frozen object is the narrow production generator in:

- [../../src/python/z_band_prime_predictor/simple_pgs_generator.py](../../src/python/z_band_prime_predictor/simple_pgs_generator.py)

The frozen selector is:

```text
rule_id: pgs_chamber_reset_v1
state input: exact divisor-count field
next-prime selection rule: GWR/NLSC chamber-reset state
emitted record: p, q only
```

The generator labels a row `PGS` only when the GWR/NLSC chamber-reset selector
chooses the endpoint. Trial-division fallback remains present as an explicit
last-resort path, but it is not used on the frozen validation surfaces and is
not counted as `PGS`.

## Headline Freeze Metrics

Low exact production surfaces:

| Surface | Bound | Input primes | PGS | Fallback | Audit failures |
|---|---:|---:|---:|---:|---:|
| `11..1000` | `128` | `164` | `164` | `0` | `0` |
| `11..10000` | `128` | `1225` | `1225` | `0` | `0` |
| `11..100000` | `128` | `9588` | `9588` | `0` | `0` |
| `11..1000000` | `128` | `78494` | `78494` | `0` | `0` |

High-scale decade-window production surface:

| Surface | Bound | Input primes | PGS | Fallback | Audit failures |
|---|---:|---:|---:|---:|---:|
| `10^8` through `10^18` | `1024` | `2816` | `2816` | `0` | `0` |

The high-scale surface uses `256` consecutive input primes per decade.

## Trial-Division Audit

On `11..100000` with `candidate_bound = 128`, the production PGS path emitted
all `9588` rows as `PGS` with zero audit failures and made zero calls to the
generator trial-division helpers:

```text
sources: {"PGS": 9588}
audit_failures: 0
trial_calls: {}
```

This freezes the source-accounting contract:

```text
PGS means selected by the PGS selector.
Fallback means selected by fallback arithmetic.
Downstream audit confirms q after emission.
```

## Validation Command

The frozen generator test surface is:

```bash
pytest -q tests/python/predictor/test_simple_pgs_generator.py
```

Current result:

```text
21 passed
```

## Scope

This is a production-generator freeze for the tested surfaces above.

The freeze does not claim a proof that every future input prime at every scale is
covered by the current bounded selector. It records the exact generator
iteration, the exact rule id, the exact source accounting, and the exact
validation surfaces that are audit-clean at freeze time.
