# GWR Proof Scripts

This folder is for executable scripts that probe, stress-test, and support
proof work on the `Gap Winner Rule` (`GWR`).

The current scripts in this folder are research instruments.
They are not part of the validation registry, and none of them by itself is a
mandatory proof gate for `GWR`.

They target the exact earlier-side closure step identified in the findings
notes:

- the ordered-dominance theorem already proves that the `GWR` candidate beats
  every later interior composite,
- the current live earlier-side route is the local admissibility program in
  [`../findings/prime_gap_admissibility_theorem.md`](../findings/prime_gap_admissibility_theorem.md),
- the older bridge certificate remains in the folder as historical comparison
  material rather than as the proof-critical path.

## Current Entry Point

## Latest Scan Milestone (April 2026)

The parallel scanner has now been extended to $p < 1{,}000{,}000{,}001$.

- Aggregate artifact:
  [`../../../output/gwr_proof/parallel_no_early_spoiler_1e9.json`](../../../output/gwr_proof/parallel_no_early_spoiler_1e9.json)
- Key statistics:
  `42,101,885` gaps,
  `149,214,917` earlier candidates,
  `0` exact spoilers,
  `0` bridge failures,
  maximum bridge load `3.749140087272451e-08`
- Next target:
  $p < 10^{10}$

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
- [`parallel_no_early_spoiler_scan.py`](./parallel_no_early_spoiler_scan.py):
  deterministic segmented scanner that
  - partitions the left-endpoint prime range into fixed-width segments,
  - writes one JSON checkpoint per completed segment,
  - aggregates exact spoiler counts and bridge-load extrema across segments,
  - and provides the straight execution path for extending the finite GWR base
  beyond the current $10^9$ surface.
- [`prime_gap_admissibility_frontier.py`](./prime_gap_admissibility_frontier.py):
  deterministic local-frontier extractor that
  - canonicalizes each exact hard case by the local chamber variables,
  - splits the earlier-side problem into square and square-free branches,
  - records the retained finite residual classes below the high-divisor cutoff,
  - and emits the proof-facing artifacts for the local admissibility route.
- [`proof_bridge_universal_lemma.md`](./proof_bridge_universal_lemma.md):
  theorem-facing bridge note that
  - derives a non-empirical large-$p$ upper bound for the normalized
  no-early-spoiler load,
  - records the exact dependence on explicit literature constants,
  - separates the bounded unconditional Dusart regime from the provisional BHP
    tail,
  - and records the verified overlap with the committed finite base.
- [`proof_bridge_certificate.py`](./proof_bridge_certificate.py):
  explicit-constant certificate helper that
  - loads the exact finite bridge artifact,
  - computes the provisional BHP tail threshold for one chosen fixed-exponent
    gap bound and divisor majoration,
  - computes the bounded unconditional Dusart coverage interval for the same
    divisor constant,
  - and reports how those regimes overlap the verified finite base.
- [`../../../output/gwr_proof/proof_bridge_certificate_2e7.json`](../../../output/gwr_proof/proof_bridge_certificate_2e7.json):
  committed certificate artifact recording the evaluated constants and closure
  status for the $2 \cdot 10^7$ finite base.
- [`dni_cutoff_branch_frontier.py`](./dni_cutoff_branch_frontier.py):
  exact branch-frontier extractor that
  - compares the bounded DNI cutoff rule to the exact unbounded next-gap
    oracle,
  - groups the exact extrema by `(first_open_offset, next_dmin)`,
  - and emits the branch obstruction rows the cutoff theorem must explain.
- [`dni_cutoff_theorem_reduction.md`](./dni_cutoff_theorem_reduction.md):
  theorem-facing reduction note that
  - defines the cutoff theorem precisely,
  - shows that it is equivalent to all-prime exactness of the bounded walker,
  - and fixes the role of finite computation as certification rather than
    empirical persuasion.
- [`dni_cutoff_branch_reduction.md`](./dni_cutoff_branch_reduction.md):
  branch-obstruction note that
  - reads the exact branch frontier,
  - identifies which branch families actually carry the theorem pressure,
  - and records the current reduction target for the symbolic tail proof.
