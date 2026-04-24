# Unresolved Alternative Closure Forensics

After locked-ceiling integration, the remaining live alternatives are all
post-boundary alternatives on the tested surface.

Boundary Law 005 is not approved by this note.

## Objective

Classify unresolved alternatives in rows where the true boundary is already
resolved but cannot be emitted because unresolved alternatives remain live.

The measured mode is:

- `single_hole_positive_witness_closure`
- `carrier_locked_pressure_ceiling`
- `carrier_lock_predicate: unresolved_alternatives_before_threat`
- `candidate_bound: 64`
- `witness_bound: 97`
- anchors: `11..10_000`

The probe does not add a new elimination rule. It reports the unresolved
alternatives after the strongest safe integrated eliminator.

## Instrument

Script:

- `../../../benchmarks/python/prime_inference_generator/unresolved_alternative_closure_forensics.py`

Artifacts:

- `unresolved_alternative_closure_forensics_records.jsonl`
- `unresolved_alternative_closure_forensics_summary.json`

Command:

```bash
python3 benchmarks/python/prime_inference_generator/unresolved_alternative_closure_forensics.py --start-anchor 11 --max-anchor 10000 --candidate-bound 64 --witness-bound 97 --output-dir /tmp/pgs_unresolved_alt_closure_10000_b64_w97
```

## Result

Summary:

- `target_row_count: 1173`
- `unresolved_alternative_count: 9206`
- `before_true_count: 0`
- `after_true_count: 9206`
- `single_hole_count: 995`
- `multi_hole_count: 8211`
- `true_boundary_rejected_count: 0`
- `unique_resolved_survivor_count: 0`

Hole-count distribution:

| Unclosed open interiors | Count |
|---:|---:|
| `1` | `995` |
| `2` | `1159` |
| `3` | `1143` |
| `4` | `1129` |
| `5` | `1112` |
| `6` | `1084` |
| `7` | `997` |
| `8` | `761` |
| `9` | `469` |
| `10` | `235` |
| `11` | `92` |
| `12` | `22` |
| `13` | `7` |
| `14` | `1` |

Closure status counts:

| Candidate closure status | Count |
|---|---:|
| `NO_POSITIVE_WITNESS_CLOSURE` | `4466` |
| `PARTIAL_POSITIVE_WITNESS_CLOSURE` | `4740` |

Unresolved reason patterns:

| Pattern | Count |
|---|---:|
| `UNRESOLVED_INTERIOR_OPEN` | `9206` |

Missing witness distribution:

| Witness marker | Count |
|---|---:|
| `NO_WITNESS` | `36686` |
| `37` | `1280` |
| `41` | `1054` |
| `43` | `994` |
| `47` | `780` |
| `53` | `726` |
| `59` | `660` |
| `61` | `476` |
| `71` | `402` |
| `67` | `360` |
| `73` | `286` |
| `79` | `221` |
| `89` | `175` |
| `83` | `168` |
| `97` | `73` |

## Interpretation

The residual unresolved alternatives are not premature candidates. On the audit
surface, every unresolved alternative lies after the actual boundary label.

That changes the next target. Multi-hole positive witness closure is not the
immediate completion rule, because no unresolved alternative has every open
interior slot closable by positive witness evidence through `97`. The current
candidate statuses are either no positive witness closure or partial positive
witness closure.

The unresolved alternatives remain live because their proposed interiors include
open positions that the pure eliminator cannot lawfully close as composites.
After audit, those positions are post-boundary prime positions in many records,
which means positive composite evidence cannot be expected to close them.

The blocker is now post-boundary alternative elimination:

- pressure ceilings that cut off after-true alternatives earlier;
- extension or absorption logic that marks post-boundary chambers as dominated;
- a legal rule that prevents later unresolved alternatives from staying live
  after the true boundary chamber is already resolved.

## Status

Milestone 1 remains blocked.

Boundary Law 005 is not approved.

The current evidence does not support prime emission. The next rule search
should target after-true unresolved alternatives, not broader positive witness
closure.
