# Integer-Locked Pressure Ceiling Integration

Selected-integer-locked pressure ceilings prune false candidates safely on the tested
surface, but they do not yet create a unique inferred next prime.

Next-Prime Law 005 is not approved by this note.

## Objective

Integrate the zero-wrong selected-integer-lock predicates into the composite-exclusion
probe and measure whether they improve next-prime inference without rejecting the
true next prime.

The integrated conditional ceiling is:

1. find a candidate GWR lower-divisor pressure event;
2. require an explicit selected-integer-lock predicate;
3. reject candidate next primes at or beyond the pressure threat;
4. attach the classical endpoint label only after elimination.

## Instrument

Script:

- `../../../benchmarks/python/prime_inference_generator/composite_exclusion_boundary_probe.py`

New flags:

- `--enable-carrier-locked-pressure-ceiling`
- `--carrier-lock-predicate unresolved_alternatives_before_threat`
- `--carrier-lock-predicate higher_divisor_pressure_before_threat`
- `--carrier-lock-predicate either`
- `--carrier-lock-predicate both`

The integration uses:

- `single_hole_positive_witness_closure`
- `witness_bound: 97`

## Surface

Run:

- anchors: `11..10_000`
- candidate bound: `64`
- witness bound: `97`

Each mode was run with:

```bash
python3 benchmarks/python/prime_inference_generator/composite_exclusion_boundary_probe.py --start-anchor 11 --max-anchor 10000 --candidate-bound 64 --enable-single-hole-positive-witness-closure --witness-bound 97 --enable-carrier-locked-pressure-ceiling --carrier-lock-predicate <predicate> --output-dir <output-dir>
```

## Baseline

Before selected-integer-locked ceiling integration, with single-hole closure enabled:

- `true_boundary_rejected_count: 0`
- `true_boundary_unresolved_count: 52`
- `true_boundary_resolved_survivor_count: 1173`
- `unique_resolved_survivor_count: 0`
- `average_rejected_count: 7.3428571428571425`
- `average_unresolved_count: 8.218775510204082`
- `average_resolved_survivor_count: 1.1877551020408164`

## Result Matrix

| Predicate | Unsafe | Applied | True safe | False pruned | True unresolved | Unique resolved | Avg rejected | Avg unresolved |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `higher_divisor_pressure_before_threat` | `0` | `10` | `10` | `33` | `52` | `0` | `7.369795918367347` | `8.191836734693878` |
| `unresolved_alternatives_before_threat` | `0` | `111` | `111` | `479` | `52` | `0` | `7.7338775510204085` | `7.8277551020408165` |
| `either` | `0` | `111` | `111` | `479` | `52` | `0` | `7.7338775510204085` | `7.8277551020408165` |
| `both` | `0` | `10` | `10` | `33` | `52` | `0` | `7.369795918367347` | `8.191836734693878` |

All four modes pass the hard safety gate:

- `true_boundary_rejected_count: 0`

No mode creates a unique resolved next prime:

- `unique_resolved_survivor_count: 0`

## Interpretation

The selected-integer-lock filters repair the safety failure of the naive ceiling. When
the tested lock predicates fire, the integrated ceiling does not reject the
true next prime on this surface.

The ceiling also performs real pruning:

- `higher_divisor_pressure_before_threat` prunes `33` false candidates;
- `unresolved_alternatives_before_threat` prunes `479` false candidates.

The stronger operational predicate is `unresolved_alternatives_before_threat`,
but it is a certificate-state condition, not a standalone number-theoretic
law. The cleaner structural predicate is `higher_divisor_pressure_before_threat`,
but it applies to only `10` anchors here.

Neither predicate resolves the remaining core blocker. True-endpoint unresolved
count stays at `52`, and multiple resolved survivors remain possible.

## Status

Milestone 1 remains blocked.

Next-Prime Law 005 is not approved.

Selected-integer-locked pressure ceilings are safe and useful as pruning rules on this
surface, but they are not next-prime-forcing rules yet. The next missing piece is
a completion or domination rule for the alternatives that remain after the
safe ceiling is applied.
