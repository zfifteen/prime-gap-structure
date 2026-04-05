# GWR Proof Scripts

This folder is for executable scripts that probe, stress-test, and support
proof work on the `Gap Winner Rule` (`GWR`).

The current scripts in this folder are research instruments.
They are not part of the validation registry, and none of them by itself is a
mandatory proof gate for `GWR`.

They target the exact missing universal step identified in the findings notes:

- the ordered-dominance theorem already proves that the `GWR` candidate beats
  every later interior composite,
- the remaining proof task is to eliminate every earlier higher-divisor
  spoiler.

## Current Entry Point

- [`earlier_spoiler_scan.py`](./earlier_spoiler_scan.py):
  exact interval scan that
  - identifies the `GWR` candidate in each tested prime gap,
  - checks every earlier interior composite against that candidate using exact
    integer-power score comparison,
  - and records which earlier candidates are already eliminated by the current
    spoiler-bound reduction.
- [`finite_remainder_attempt.py`](./finite_remainder_attempt.py):
  deterministic class-only route test that
  - attempts to derive an explicit finite remainder bound from the current
    spoiler reduction,
  - and emits the exact obstruction family showing that the current reduction
    alone does not close the infinite tail.
- [`large_prime_reducer.py`](./large_prime_reducer.py):
  deterministic proof-pursuit reducer that
  - exhaustively scans every prime gap below a fixed explicit large-prime
    threshold,
  - then tests a fixed-factor large-prime class table against the exact
    earlier-spoiler inequality,
  - and emits the remaining large-prime divisor classes, if any.
- [`large_prime_tail_obstruction.py`](./large_prime_tail_obstruction.py):
  deterministic tail-obstruction script that
  - uses the exact family $D = 2^k$ with primorial witnesses,
  - finds the first exact class witness against the fixed large-prime reducer,
  - and finds the eventual cutoff after which the elementary Bertrand bound
    alone keeps that family unresolved forever.
- [`earlier_spoiler_local_dominator_scan.py`](./earlier_spoiler_local_dominator_scan.py):
  exact prime-gap admissibility scan that
  - takes each actual earlier spoiler candidate before the `GWR` winner,
  - finds the first later interior composite that beats it exactly,
  - and records the offset law and per-class offset frontier.
- [`no_early_spoiler_margin_scan.py`](./no_early_spoiler_margin_scan.py):
  exact no-early-spoiler scan that
  - compares every earlier interior candidate directly to the actual `GWR`
    carrier,
  - records the smallest winner-minus-earlier log-score margin,
  - and records the smallest critical-ratio slack in the exact spoiler
    inequality.
- [`no_early_spoiler_ratio_frontier.py`](./no_early_spoiler_ratio_frontier.py):
  exact pair-frontier extractor that
  - finds the tightest realized case for each winner/earlier divisor-class
    pair,
  - ranks those pairs by critical-ratio slack,
  - and emits the current ratio-form frontier of the no-early-spoiler
    condition.
- [`large_gap_margin_scan.py`](./large_gap_margin_scan.py):
  exact large-gap extractor that
  - records the worst realized no-early-spoiler case inside each of the
    largest gaps,
  - records the worst realized case for each exact gap size,
  - and tests directly whether large gap length is where the current margin
    surface tightens.
- [`asymptotic_bridge_load_scan.py`](./asymptotic_bridge_load_scan.py):
  exact normalized bridge extractor that
  - rewrites the no-early-spoiler inequality as a dimensionless load,
  - records the maximum realized bridge load on the exact surface,
  - and emits pair and gap-size frontiers in that normalized coordinate.
- [`proof_bridge_universal_lemma.md`](./proof_bridge_universal_lemma.md):
  theorem-facing bridge note that
  - derives a non-empirical large-$p$ upper bound for the normalized
    no-early-spoiler load,
  - isolates the exact remaining dependence on explicit literature constants,
  - and states the remaining finite verification obligation precisely.
