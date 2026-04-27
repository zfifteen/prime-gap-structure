# Higher-Divisor Pressure Lock Hardening

The higher-divisor pressure lock survives the staged zero-wrong hardening
surface through input primes `11..1_000_000`.

Next-Prime Law 005 is not approved by this note.

## Objective

The resolved-endpoint lock separator probe found one zero-wrong candidate:

```text
higher_divisor_pressure_lock
```

This note hardens that candidate across larger exact surfaces, then records the
first flagged integration test. The rule remains offline theorem discovery. It
is not part of pure generation.

## Hardening Instrument

Script:

- `../../../benchmarks/python/prime_inference_generator/higher_divisor_pressure_lock_hardening.py`

Artifacts:

- `higher_divisor_pressure_lock_hardening_rows.jsonl`
- `higher_divisor_pressure_lock_hardening_summary.json`

Command:

```bash
python3 benchmarks/python/prime_inference_generator/higher_divisor_pressure_lock_hardening.py --start-anchor 11 --max-anchors 10000 100000 1000000 --candidate-bound 64 --witness-bound 97 --output-dir /tmp/pgs_hd_lock_hardening_1m
```

## Hardening Result

| Surface | Rows | True resolved | False resolved | True selected | False selected | Wrong |
|---|---:|---:|---:|---:|---:|---:|
| `11..10_000` | `1225` | `1173` | `282` | `31` | `0` | `0` |
| `11..100_000` | `9588` | `7431` | `4354` | `31` | `0` | `0` |
| `11..1_000_000` | `78494` | `49019` | `46286` | `31` | `0` | `0` |

The selected true count does not grow after the early surface. The important
hardening result is safety under a much larger false-resolved pool:

```text
higher_divisor_pressure_lock_false_selected: 0
```

on every staged surface.

## Flagged Integration Instrument

The composite-exclusion probe now has an explicit offline flag:

```text
--enable-higher-divisor-pressure-locked-absorption
```

This flag absorbs later unresolved candidates only when the resolved candidate
satisfies `higher_divisor_pressure_lock`. It does not select among multiple
resolved candidates and does not touch the pure generator.

Command:

```bash
python3 benchmarks/python/prime_inference_generator/composite_exclusion_boundary_probe.py --start-anchor 11 --max-anchor 100000 --candidate-bound 64 --witness-bound 97 --enable-single-hole-positive-witness-closure --enable-carrier-locked-pressure-ceiling --carrier-lock-predicate unresolved_alternatives_before_threat --enable-higher-divisor-pressure-locked-absorption --output-dir /tmp/pgs_hd_locked_absorption_integration_100000
```

## Integration Result

| Surface | Unique resolved candidates | True rejected | Applied | Correct | Wrong | False absorber |
|---|---:|---:|---:|---:|---:|---:|
| `11..10_000` | `25` | `0` | `31` | `31` | `0` | `0` |
| `11..100_000` | `25` | `0` | `31` | `31` | `0` | `0` |

The integration passes the first candidate gate:

```text
unique_resolved_survivor_count > 0
true_boundary_rejected_count == 0
higher_divisor_locked_absorption_wrong_count == 0
```

Coverage remains narrow. The rule applies `31` times and produces `25` unique
resolved candidates because some locked rows still retain multiple resolved
remaining candidates after unresolved alternatives are absorbed.

## Interpretation

The candidate has now passed two separate checks:

- lock-separator hardening through input primes `11..1_000_000`;
- flagged absorption integration through input primes `11..100_000`.

This is candidate material for Next-Prime Law 005, not approval. The current
candidate shape is:

```text
resolved interval
+ higher-divisor pressure lock
=> later unresolved extension intervals may be absorbed
```

The next artifact should be a candidate law note only if the project lead
accepts this integration result as enough to draft one. It should remain
explicitly labeled as a candidate law until a theorem or broader hardening
surface is established.

## Status

Milestone 1 remains blocked.

Next-Prime Law 005 is not approved.

Prime output remains forbidden.
