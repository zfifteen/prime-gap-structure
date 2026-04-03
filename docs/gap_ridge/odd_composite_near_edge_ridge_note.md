# Odd-Composite Near-Edge Ridge

This note records the narrower phenomenon that survives after direct validation
against the broader "Prime Insulation Principle" framing.

## Name

The surviving result is best named the **Odd-Composite Near-Edge Ridge**.

That name is narrow on purpose.

It says:

- the structure concerns odd composite interior points,
- the effect is strongest near the gap edge rather than across the whole edge
  band,
- the phenomenon is a ridge in the raw DNI field and not a general claim that
  prime-gap edges are globally simple.

## What Survives

The repository already had a measured and reproducible result for the exact raw
DNI field on prime-gap interiors:

- the gap-local raw-`Z` maximum is strongly enriched at edge distance `2`,
- that local peak is overwhelmingly carried by `d(n) = 4` composites,
- the carrier enrichment strengthens with scale across the tested regimes.

That is the near-edge ridge result documented in:

- [docs/dni_gap_ridge.md](../dni_gap_ridge.md)
- [docs/gap_ridge/raw_composite_z_gap_edge.md](./raw_composite_z_gap_edge.md)
- [docs/gap_ridge/raw_composite_z_gap_edge_figures.md](./raw_composite_z_gap_edge_figures.md)

## What Was Tested

The broader claim tested here was stronger than the existing ridge result.

It claimed that prime-gap edges form a general low-complexity insulation zone
and that gap centers form a high-complexity graveyard.

That stronger claim was tested with a deterministic validation harness that
compared edge zones to center zones across:

- exact `10^6` and `10^7` full runs,
- evenly spaced sampled windows at `10^8`, `10^9`, and `10^10`,
- all composite interiors,
- odd-composite-only controls,
- exact gap-size bins.

The artifacts are:

- [validation_results.json](../../benchmarks/output/python/gap_ridge/composite_structure_validation/validation_results.json)
- [validation_summary_panel.svg](../../benchmarks/output/python/gap_ridge/composite_structure_validation/validation_summary_panel.svg)
- [validation_detail_panel.svg](../../benchmarks/output/python/gap_ridge/composite_structure_validation/validation_detail_panel.svg)
- [validation_gap_bin_heatmaps.svg](../../benchmarks/output/python/gap_ridge/composite_structure_validation/validation_gap_bin_heatmaps.svg)

The deterministic harness is:

- [composite_structure_validation.py](../../benchmarks/python/gap_ridge/composite_structure_validation.py)

## Outcome

The broad insulation claim was falsified on the tested surface.

The literal edge zone is not globally simpler than the center zone.
Across the tested regimes, edge zones show:

- higher mean divisor count than center zones,
- lower `d(n) = 4` share than center zones,
- higher high-divisor share than center zones.

This remains true in the odd-composite control and in the exact gap-size bins
that had sufficient support.

## Interpretation

The tested structure is therefore not:

- "prime-gap edges are generally simple,"
- "gap centers are generally reserved for high complexity,"
- or a general prime-edge insulation law.

The surviving structure is narrower:

- the raw-`Z` winner inside a prime gap is strongly pulled toward the first odd
  interior positions,
- that winner is usually carried by a `d(n) = 4` composite,
- the effect is a local near-edge ridge in the raw DNI field.

That is why the narrower name is better.

It preserves the measured result and drops the part that failed direct
validation.

## Plain Summary

The number line did not support the broad statement that prime-gap edges are
simple insulation bands.

It did support a narrower and still interesting statement:

inside prime gaps, the exact raw DNI field has a strong odd-composite
near-edge ridge, and that ridge is usually carried by semiprime-class
`d(n) = 4` composites.
