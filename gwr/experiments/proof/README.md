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
- the older bridge verification record remains in the folder as historical comparison
  material rather than as the proof-critical path.

## Current Entry Point

## Latest Scan Milestone (April 2026)

The parallel scanner has now been extended through the tranche
$10^9 < p < 5 \times 10^9$.

- Aggregate artifact:
  [`../../../output/gwr_proof/parallel_no_early_spoiler_5e9.json`](../../../output/gwr_proof/parallel_no_early_spoiler_5e9.json)
- Key statistics:
  `172,913,029` gaps,
  `660,287,089` earlier candidates,
  `0` exact counterexamples,
  `0` bridge failures,
  maximum bridge load `3.7231970839712858e-09`
- Load comparison:
  about `10.07x` tighter than the committed $10^9$ tranche
- Next target:
  $p < 10^{10}$

- [`earlier_spoiler_scan.py`](./earlier_spoiler_scan.py):
  exact interval scan that
  - identifies the `GWR` candidate in each tested prime gap,
  - checks every earlier interior composite against that candidate using exact
    integer-power score comparison,
  - and records which earlier candidates are already eliminated by the current
    counterexample-bound reduction.
- [`finite_remainder_attempt.py`](./finite_remainder_attempt.py):
  deterministic class-only route test that
  - attempts to derive an explicit finite remainder bound from the current
    counterexample reduction,
  - and writes the exact obstruction family showing that the current reduction
    alone does not close the infinite tail.
- [`large_prime_reducer.py`](./large_prime_reducer.py):
  deterministic proof-pursuit reducer that
  - exhaustively scans every prime gap below a fixed explicit large-prime
    threshold,
  - then tests a fixed-factor large-prime class table against the exact
    earlier-competing-integer inequality,
  - and writes the remaining large-prime divisor classes, if any.
- [`large_prime_tail_obstruction.py`](./large_prime_tail_obstruction.py):
  deterministic tail-obstruction script that
  - uses the exact family $D = 2^k$ with primorial witnesses,
  - finds the first exact class witness against the fixed large-prime reducer,
  - and finds the eventual cutoff after which the elementary Bertrand bound
    alone keeps that family unresolved forever.
- [`earlier_spoiler_local_dominator_scan.py`](./earlier_spoiler_local_dominator_scan.py):
  exact prime-gap admissibility scan that
  - takes each actual earlier competing integer before the `GWR` selected integer,
  - finds the first later interior composite that beats it exactly,
  - and records the offset law and per-class offset extremal case.
- [`no_early_spoiler_margin_scan.py`](./no_early_spoiler_margin_scan.py):
  exact no-early-counterexample scan that
  - compares every earlier interior candidate directly to the actual `GWR`
    integer,
  - records the smallest selected integer-minus-earlier log-score margin,
  - and records the smallest critical-ratio slack in the exact counterexample candidate
    inequality.
- [`no_early_spoiler_ratio_frontier.py`](./no_early_spoiler_ratio_frontier.py):
  exact pair-extremal-case extractor that
  - finds the tightest realized case for each selected integer/earlier divisor-class
    pair,
  - ranks those pairs by critical-ratio slack,
  - and writes the current ratio-form ratio extremum of the no-early-counterexample
    condition.
- [`large_gap_margin_scan.py`](./large_gap_margin_scan.py):
  exact large-gap extractor that
  - records the worst realized no-early-counterexample case inside each of the
    largest gaps,
  - records the worst realized case for each exact gap size,
  - and tests directly whether large gap length is where the current margin
    surface tightens.
- [`asymptotic_bridge_load_scan.py`](./asymptotic_bridge_load_scan.py):
  exact normalized bridge extractor that
  - rewrites the no-early-counterexample inequality as a dimensionless load,
  - records the maximum realized bridge load on the exact surface,
  - and writes pair and gap-size extremal cases in that normalized coordinate.
- [`parallel_no_early_spoiler_scan.py`](./parallel_no_early_spoiler_scan.py):
  deterministic segmented scanner that
  - partitions the left-endpoint prime range into fixed-width segments,
  - writes one JSON checkpoint per completed segment,
  - aggregates exact counterexample counts and bridge-load extrema across segments,
  - and provides the straight execution path for extending the finite GWR base
  beyond the current $10^9$ surface.
- [`prime_gap_admissibility_frontier.py`](./prime_gap_admissibility_frontier.py):
  deterministic local-extremal-case extractor that
  - canonicalizes each exact hard case by the local search interval variables,
  - splits the earlier-side problem into square and square-free branches,
  - records the retained finite residual classes below the high-divisor cutoff,
  - and writes the proof-facing artifacts for the local admissibility route.
- [`proof_bridge_universal_lemma.md`](./proof_bridge_universal_lemma.md):
  theorem-facing bridge note that
  - derives a non-empirical large-$p$ upper bound for the normalized
  no-early-counterexample load,
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
  exact branch-extremal-case extractor that
  - compares the bounded DNI cutoff rule to the exact unbounded next-gap
    oracle,
  - groups the exact extrema by `(first_open_offset, next_dmin)`,
  - and writes the branch obstruction rows the cutoff theorem must explain.
- [`dni_cutoff_theorem_reduction.md`](./dni_cutoff_theorem_reduction.md):
  theorem-facing reduction note that
  - defines the cutoff theorem precisely,
  - shows that it is equivalent to all-prime exactness of the bounded walker,
  - and fixes the role of finite computation as certification rather than
    empirical persuasion.
- [`dni_cutoff_branch_reduction.md`](./dni_cutoff_branch_reduction.md):
  branch-obstruction note that
  - reads the exact branch extremum,
  - identifies which branch families actually carry the theorem pressure,
  - and records the current reduction target for the symbolic tail proof.
