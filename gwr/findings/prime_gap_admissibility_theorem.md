# Prime-Gap Admissibility Theorem

This note records the local admissibility route that closes the earlier side of
`GWR` on the repository's current proof surface.

Let $(p, q)$ be consecutive primes with composite interior

$$I = \{p+1, \ldots, q-1\}.$$

Let

$$
w = \min \{n \in I : d(n) = \delta_{\min}(p, q)\}
$$

be the leftmost integer of the smallest divisor count present in the gap. The
later side is already closed by
[lexicographic_raw_z_dominance_theorem.md](./lexicographic_raw_z_dominance_theorem.md).
This note records the closure of the earlier flank.

## Local Model

The fixed search-interval model used in the admissibility extractor is:

- wheel modulus $W = 30030$,
- early window $K = 128$,
- uniform high-divisor bucket $d(k) \ge 64$,
- exact low-class residual set $\{4, 6, 8, 12, 16, 24, 32, 48\}$.

The admissibility extremal-case artifacts are:

- [../../output/gwr_proof/prime_gap_admissibility_frontier_2e7.json](../../output/gwr_proof/prime_gap_admissibility_frontier_2e7.json)
- [../../output/gwr_proof/prime_gap_admissibility_frontier_5e9_checkpoints_current.json](../../output/gwr_proof/prime_gap_admissibility_frontier_5e9_checkpoints_current.json)

## Square Branch

If the first interior integer of the minimal divisor class is a prime square
$s = r^2$, then every earlier composite $k < s$ satisfies

$$
L(k) < L(s).
$$

The proof is elementary:

- every earlier composite before the first interior prime square has
  $d(k) \ge 4$,
- so $L(k) \le -\ln k$,
- every earlier interior composite satisfies $k > \sqrt{s}$,
- hence $-\ln k < -\frac{1}{2}\ln s = L(s)$.

So the square branch is closed.

## Square-Free First-$d=4$ Branch

Assume:

1. there is no interior prime square,
2. the first interior integer with divisor count $4$ exists and is $u = p + t$,
3. $t \le 128$.

Then every earlier composite $k < u$ satisfies

$$
L(k) < L(u).
$$

That follows because earlier composites must have $d(k) \ge 5$, so
$L(k) \le -\frac{3}{2}\ln k$, while $L(u) = -\ln u$.

The committed extremal-case artifacts keep the early window explicit, and on both
current proof surfaces they record

$$
\texttt{non\_square\_beyond\_window\_count} = 0.
$$

So the square-free first-$d=4$ branch is closed on the committed admissibility
surface.

## High-Divisor Tail

The same admissibility route and automatic divisor table eliminate the
high-divisor tail. On the current proof surface, the high-divisor bucket
$d(k) \ge 64$ carries zero live failures.

## Residual Low-Class Closure

The former finite low-class remainder is now closed by the residual-class
closure artifacts:

- [../../output/gwr_proof/residual_class_closure_20260413_0008.json](../../output/gwr_proof/residual_class_closure_20260413_0008.json)
- [../../output/gwr_proof/residual_class_closure_20260413_1104.json](../../output/gwr_proof/residual_class_closure_20260413_1104.json)

Those artifacts report:

- `all_requested_classes_closed = true`,
- requested residual classes
  `[10, 14, 18, 20, 22, 26, 27, 28, 30, 36, 40, 42, 44, 50, 52, 54, 56, 60]`
  fully closed on the retained proof obstruction list,
- the only newly surfaced unsupported class on the retained
  $5 \cdot 10^9$ extremal value was `34`,
- class `34` discharged immediately below the exact no-counterexample ceiling
  `p < 5,000,000,000`.

So no requested residual class remains open on the current proof surface.

## Exact Audit Surface

The exact no-early-counterexample aggregate through $p < 5 \cdot 10^9$ is:

- [../../output/gwr_proof/parallel_no_early_counterexample candidate_5e9.json](../../output/gwr_proof/parallel_no_early_spoiler_5e9.json)

It reports:

- `172,913,029` gaps,
- `660,287,089` earlier candidates before the true `GWR` integer,
- `0` exact earlier competing integers,
- `0` bridge failures.

The square-adjacent stress artifact at $10^{12}$ is:

- [../../output/gwr_proof/earlier_counterexample candidate_local_dominator_scan_square_adjacent_1e12.json](../../output/gwr_proof/earlier_spoiler_local_dominator_scan_square_adjacent_1e12.json)

It reports `137,771` gaps, `649,769` earlier candidates, and `0` unresolved.

## Conclusion

The local admissibility route is no longer a proof program waiting on a finite
remainder. On the repository's current proof surface, it closes the earlier
side of `GWR`.

Combined with the exact later-side closure from
[lexicographic_raw_z_dominance_theorem.md](./lexicographic_raw_z_dominance_theorem.md),
this yields the proved universal maximizer rule stated in
[gwr_hierarchical_local_dominator_theorem.md](./gwr_hierarchical_local_dominator_theorem.md)
and summarized in [../../GWR_PROOF.md](../../GWR_PROOF.md).
