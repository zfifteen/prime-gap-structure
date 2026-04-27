# Closure-Constraint Findings

This note records the current measured closure surface for the
closure-constraint reading of the Gap Winner Rule.

## Statement Tested

For each prime gap $(p, q)$, let $w$ be the implemented log-score maximizer on the
interior composites. The tested closure constraint is:

$$
\text{there is no later interior composite } n \text{ with } w < n < q
\text{ and } d(n) < d(w).
$$

Equivalently:

$$
q
\text{ occurs before the first later strictly simpler composite.}
$$

This is not a tautology, because the script defines $w$ from the implemented
log-score argmax and then separately checks the later divisor profile.

## Current Artifacts

- runner:
  [`benchmarks/python/gap_ridge/gwr_closure_constraint.py`](../../benchmarks/python/gap_ridge/gwr_closure_constraint.py)
- tests:
  [`tests/python/gap_ridge/test_gwr_closure_constraint.py`](../../tests/python/gap_ridge/test_gwr_closure_constraint.py)
- JSON summary:
  [`output/gwr_closure_constraint_summary.json`](../../output/gwr_closure_constraint_summary.json)
- even-band ladder through $10^{18}$:
  [`output/gwr_closure_constraint_even_bands_through_1e18.json`](../../output/gwr_closure_constraint_even_bands_through_1e18.json)
- sampled CSV:
  [`output/gwr_closure_constraint_sampled.csv`](../../output/gwr_closure_constraint_sampled.csv)

## Tested Surface

The strongest current documented run used:

- exact full scan to $10^6$,
- even windows only at every decade from $10^8$ through $10^{18}$,
- window size $2 \times 10^6$,
- $2$ even windows per scale.

An additional corroborating run used:

- exact full scan to $10^6$,
- sampled scales $10^8$ and $10^9$,
- window size $2 \times 10^6$,
- $2$ even windows per sampled scale,
- $2$ fixed seeds: $20260331$ and $20260401$,
- $2$ seeded windows per seed and sampled scale.

## Closure Results

The deterministic even-band sweep through $10^{18}$ also returned zero closure
violations at every tested scale.

| Scale | Gap count | Violations | Match rate | Max gap |
|---|---:|---:|---:|---:|
| exact $10^6$ | 70,327 | 0 | 1.0 | 114 |
| $10^8$ | 234,639 | 0 | 1.0 | 176 |
| $10^9$ | 224,237 | 0 | 1.0 | 190 |
| $10^{10}$ | 215,807 | 0 | 1.0 | 288 |
| $10^{11}$ | 208,766 | 0 | 1.0 | 268 |
| $10^{12}$ | 202,949 | 0 | 1.0 | 306 |
| $10^{13}$ | 197,687 | 0 | 1.0 | 300 |
| $10^{14}$ | 193,665 | 0 | 1.0 | 358 |
| $10^{15}$ | 189,602 | 0 | 1.0 | 436 |
| $10^{16}$ | 186,494 | 0 | 1.0 | 432 |
| $10^{17}$ | 183,355 | 0 | 1.0 | 448 |
| $10^{18}$ | 180,447 | 0 | 1.0 | 448 |

So the current extended deterministic band ladder shows zero observed
counterexamples from $10^8$ through $10^{18}$.

The strongest supported finding on the current surface is therefore:

The closure constraint held exactly on every tested gap in the deterministic
even-band ladder through $10^{18}$.

## Mixed-Window Corroboration At $10^8$ And $10^9$

The mixed-window corroboration run also returned zero closure violations in
every tested regime.

| Regime | Gap count | Violations | Match rate | Max gap |
|---|---:|---:|---:|---:|
| even $10^8$ | 234,639 | 0 | 1.0 | 176 |
| even $10^9$ | 224,237 | 0 | 1.0 | 190 |
| seeded $10^8$, seed $20260331$ | 208,733 | 0 | 1.0 | 168 |
| seeded $10^9$, seed $20260331$ | 189,058 | 0 | 1.0 | 224 |
| seeded $10^8$, seed $20260401$ | 206,515 | 0 | 1.0 | 164 |
| seeded $10^9$, seed $20260401$ | 184,649 | 0 | 1.0 | 186 |

## Threat-Horizon Summary For $d=4$ Selected integers

For the dominant selected divisor-count class $d(w) = 4$, the first later strictly simpler
composite must have $d = 3$. That means the first possible later threat is the
next prime square after the selected integer.

For each $d=4$ selected integer, the run recorded:

- threat distance:
  the distance from the selected integer to the next prime square,
- prime-arrival margin:
  the distance from the right prime $q$ to that next prime square.

A positive margin means the gap closed before the first later $d=3$ threat
could appear.

| Regime | $d=4$ selected-integer share | Mean threat distance | Mean prime-arrival margin | Min margin |
|---|---:|---:|---:|---:|
| exact $10^6$ | 0.8290 | 5,869.6 | 5,857.5 | 2 |
| even $10^8$ | 0.8256 | 89,705.6 | 89,690.6 | 2 |
| even $10^9$ | 0.8251 | 212,536.9 | 212,521.2 | 2 |
| seeded $10^8$, seed $20260331$ | 0.8241 | 93,307.4 | 93,290.2 | 2 |
| seeded $10^9$, seed $20260331$ | 0.8241 | 415,484.3 | 415,465.2 | 2 |
| seeded $10^8$, seed $20260401$ | 0.8234 | 92,275.3 | 92,258.0 | 2 |
| seeded $10^9$, seed $20260401$ | 0.8228 | 207,755.0 | 207,735.3 | 2 |

These margins are all positive on the tested surface. In the current run, every
observed $d=4$ selected integer was followed by a right prime before the first later
prime-square threat.

On the extended even-band ladder, the same pattern persists through $10^{18}$.
Selected rows:

| Scale | $d=4$ selected-integer share | Mean threat distance | Mean prime-arrival margin | Min margin |
|---|---:|---:|---:|---:|
| $10^{10}$ | 0.8271 | 522,403.0 | 522,386.5 | 2 |
| $10^{12}$ | 0.8257 | 2,371,908.1 | 2,371,890.4 | 2 |
| $10^{14}$ | 0.8270 | 117,070,590.7 | 117,070,572.2 | 2 |
| $10^{16}$ | 0.8273 | 393,506,966.3 | 393,506,946.9 | 2 |
| $10^{18}$ | 0.8273 | 3,595,291,803.7 | 3,595,291,783.5 | 2 |

The tracked $d=3$ selected integers are rare throughout the ladder. At $10^{18}$, the
even-band run recorded $222$ such selected integers across $180{,}447$ tested gaps, a
share of about $0.00123$. So the dominance of $d=4$ selected integers remains a large-
scale structural feature on the tested surface rather than a small-number
artifact.

## Interpretation

These findings support the closure reading of GWR:

- once the score maximizer appears, the gap closes before any later strictly
  simpler composite arrives;
- for the dominant $d=4$ selected divisor-count class, the next-prime closure occurs well
  before the first later $d=3$ threat on every tested regime;
- the gap appears to be locally terminated before a strictly simpler late
  challenger can enter the interior.

This is the measured form of the exact `GWR` corollary tracked by the
recursive-walk surface: once the selected integer is fixed, the gap closes before any
later strictly simpler interior composite appears.

## Status Note For The $d=4$ Case

When $d(w)=4$, the first later strictly simpler threat is the next prime
square, so this measured closure surface reduces to comparing:

- the distance from the selected integer to the next prime square, and
- the distance from the selected integer to the next prime.

That makes the $d=4$ case a concrete analytic observable on the tested surface.
What this note adds is margin data, not a competing proof-status claim. The
repo's proof-facing status remains the closed `GWR` surface summarized in
`GWR_PROOF.md` and `claim_hierarchy.md`. What the present measurements show is
that the $d=4$ margins stay positive and large on every tested regime,
including the even-band ladder through $10^{18}$.

## Scope

This note documents the current closure-constraint runs only. It does not
replace the main proof summary, and it does not claim a separate asymptotic
prime-distribution theorem beyond the proved maximizer rule. The $d=4$ threat
summary is exact for the dominant $d=4$ selected divisor-count class because the next lower
divisor class is $d=3$, which occurs at prime squares. More general threat
summaries for other selected divisor-count classes remain follow-on measurement work rather
than headline proof-status claims.
