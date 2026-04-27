# PGS Inference Generator v1.1

PGS Inference Generator v1.1 is the PGS-only production iteration.

The generator starts from an accepted anchor prime `p` and emits exactly one
minimal record when the PGS selector resolves:

```json
{"p": 89, "q": 97}
```

The generator version is:

```text
PGS_GENERATOR_VERSION = 1.1.0
PGS_GENERATOR_FREEZE_ID = pgs_inference_generator_v1_1_pgs_only
```

## Change From v1.0

Version `1.0` still carried trial-division and fallback helpers as explicit
last-resort code paths, although the frozen validation surfaces did not use
them.

Version `1.1` removes those paths from the generator. The generator now has one
execution path:

```text
accepted anchor p -> GWR/NLSC chamber-reset selector -> emit {"p": p, "q": q}
```

If the selector does not resolve inside the supplied chamber bound, generation
raises `PGSUnresolvedError`. It does not run a backup prime search.

## Frozen Selector

```text
rule_id: pgs_chamber_reset_v1
state input: exact divisor-count field
next-prime selection rule: GWR/NLSC chamber-reset state
emitted record: p, q only
```

The generator file no longer contains:

- trial division;
- fallback prime search;
- divisor-witness search;
- shadow-seed recovery;
- chain fallback;
- inline validation of emitted `q`.

Downstream audit remains external.

## Headline Metrics

Low exact production surfaces:

| Surface | Bound | Anchors | PGS | Audit failures |
|---|---:|---:|---:|---:|
| `11..1000` | `128` | `164` | `164` | `0` |
| `11..10000` | `128` | `1225` | `1225` | `0` |
| `11..100000` | `128` | `9588` | `9588` | `0` |
| `11..1000000` | `128` | `78494` | `78494` | `0` |

High-scale decade-window production surface:

| Surface | Bound | Anchors | PGS | Audit failures |
|---|---:|---:|---:|---:|
| `10^8` through `10^18` | `1024` | `2816` | `2816` | `0` |

The high-scale surface uses `256` consecutive prime anchors per decade.

## Validation Command

```bash
pytest -q tests/python/predictor/test_simple_pgs_generator.py
```

Current result:

```text
16 passed
```

## Scope

This is a production-generator refactor for the tested surfaces above. It does
not claim a proof that every future anchor at every scale is covered by the
current bounded selector.
