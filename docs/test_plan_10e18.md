# 10^18 Near-Endpoint Raw-Z Peak Test Plan

## Objective

The project proof bar for structural near-endpoint raw-Z peak claims is `10^18` minimum.

This document separates two different surfaces:

- **Configured band coverage**: the regime ladder recognized by the code, tests, JSON payloads, and plotting pipeline.
- **Executed high-scale validation**: bands that have actually been run and committed with artifacts.

This pass expands configured band coverage through `10^18`, upgrades the exact interval implementation to support `10^18`-class windows, and reruns the main raw gap-edge, lexicographic, and composite-structure validation campaigns on that widened surface.

## Current State

The current committed execution surface for the near-endpoint raw-Z peak program is:

- exact full runs at `10^6` and `10^7`,
- sampled regime bands by decade from `10^8` through `10^18`.

The former blocking constraint in `src/python/z_band_prime_composite_field/field.py`
has now been removed. The interval implementation no longer walks primes up to
`sqrt(hi)`. It strips factors only through `cuberoot(hi)` and uses `gmpy2` to
classify the residual exactly as `1`, prime, prime square, or semiprime.

## Canonical Regime Ladder

Exact full runs remain:

- `10^6`
- `10^7`

Sampled regime bands extend by decade through the project proof bar:

- `10^8`
- `10^9`
- `10^10`
- `10^11`
- `10^12`
- `10^13`
- `10^14`
- `10^15`
- `10^16`
- `10^17`
- `10^18`

## Validation Surfaces

The regime ladder must be recognized consistently by:

- raw gap-edge enrichment runs,
- lexicographic peak validation,
- composite-structure falsification and validation,
- plot generation and artifact loading.

Fast pytest should cover the shape of that ladder without attempting real
`10^18` interval analysis.

## Stage Split

### Stage 1: Band Coverage Through `10^18`

- expand the shared sampled-scale defaults through `10^18`,
- make all near-endpoint raw-Z peak CLIs inherit that shared ladder,
- update tests so defaults, parsers, JSON fixtures, and plot pipelines all recognize the full decade ladder through `10^18`,
- keep exact full runs capped at `10^7`,
- keep smoke tests on tiny custom scales so ordinary pytest remains fast.

### Stage 2: High-Scale Execution Infrastructure

- completed: implement a deterministic segmented factor and prime supply suitable for `10^18`-class windows,
- completed: preserve exact interval semantics for divisor counts,
- completed: make the high-scale execution path auditable and deterministic.

### Stage 3: Committed `10^18` Artifacts

- completed: run the higher-band raw gap-edge, lexicographic, and composite-structure campaigns with the new model,
- completed: regenerate the main `10^18`-grade artifacts,
- completed: upgrade README and supporting notes from “configured through `10^18`” to “executed through `10^18`” where the data support it.

## Acceptance Criteria

- all near-endpoint raw-Z peak defaults and tests recognize the full sampled decade ladder through `10^18`,
- no public near-endpoint raw-Z peak docs describe `10^10` as the terminal validation horizon,
- fast pytest remains fast,
- high-scale execution is no longer blocked on the old exact interval implementation.
