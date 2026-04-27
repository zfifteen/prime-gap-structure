# GWR_PROOF.md

## Gap Winner Rule: Closed Proof Surface

This document records the closed proof surface for the `Gap Winner Rule`
(`GWR`) and points to the canonical theorem and closure artifacts now used on
the visible surface of the repository.

## Theorem Statement

Let $p < q$ be consecutive primes with composite interior

$$I = \{p+1, \ldots, q-1\}.$$

Define

$$
\delta_{\min}(p, q) := \min_{n \in I} d(n), \qquad
w := \min \{n \in I : d(n) = \delta_{\min}(p, q)\}.
$$

Then $w$ is the unique maximizer of

$$
L(n) = \left(1 - \frac{d(n)}{2}\right)\ln n
$$

over the entire gap interior $I$.

Canonical theorem file:
[gwr/findings/gwr_hierarchical_local_dominator_theorem.md](gwr/findings/gwr_hierarchical_local_dominator_theorem.md)

## Closed Components

### 1. Later Side

Every later composite $m > w$ satisfies $L(m) < L(w)$.

This is the ordered-dominance step: if $a < b$ and $d(a) \le d(b)$, then
$L(a) > L(b)$. Applying that with $a = w$ and $b = m$ closes the entire later
side immediately.

Source:
[gwr/findings/lexicographic_raw_z_dominance_theorem.md](gwr/findings/lexicographic_raw_z_dominance_theorem.md)

### 2. Earlier Side, Square Branch

If the first interior integer of the minimal divisor class is a prime square
$s = r^2$, then every earlier composite $k < s$ satisfies $L(k) < L(s)$.

That branch is closed in the local admissibility note.

Source:
[gwr/findings/prime_gap_admissibility_theorem.md](gwr/findings/prime_gap_admissibility_theorem.md)

### 3. Earlier Side, Square-Free Early-Arrival Branch

The local admissibility note also closes the square-free first-$d=4$ branch
once the first interior integer with $d(n)=4$ arrives inside the fixed early window
$K = 128$.

The committed admissibility frontier artifacts keep that window explicit on the
exact through-$2 \cdot 10^7$ surface and on the retained $5 \cdot 10^9$
checkpoint surface:

- [output/gwr_proof/prime_gap_admissibility_frontier_2e7.json](output/gwr_proof/prime_gap_admissibility_frontier_2e7.json)
- [output/gwr_proof/prime_gap_admissibility_frontier_5e9_checkpoints_current.json](output/gwr_proof/prime_gap_admissibility_frontier_5e9_checkpoints_current.json)

### 4. Residual Low-Class Closure

The finite low-class remainder that was previously tracked as an open residual
table is now closed on the repo's proof surface.

The closing artifacts are:

- [output/gwr_proof/residual_class_closure_20260413_0008.json](output/gwr_proof/residual_class_closure_20260413_0008.json)
- [output/gwr_proof/residual_class_closure_20260413_1104.json](output/gwr_proof/residual_class_closure_20260413_1104.json)

The latest retained summary reports:

- `all_requested_classes_closed = true`
- `requested_residual_classes = [10, 14, 18, 20, 22, 26, 27, 28, 30, 36, 40, 42, 44, 50, 52, 54, 56, 60]`
- the only newly surfaced unsupported class on the retained $5 \cdot 10^9$
  frontier was `34`
- that class is discharged below the committed exact no-counterexample ceiling
  `p < 5,000,000,000`

So no requested residual class remains open on the retained proof frontier.

### 5. Exact Audit Surface

The proof chain is backed by exact no-spoiler audit surfaces rather than by a
live open remainder.

The strongest committed aggregate through $p < 5 \cdot 10^9$ is:

- [output/gwr_proof/parallel_no_early_spoiler_5e9.json](output/gwr_proof/parallel_no_early_spoiler_5e9.json)

That artifact reports:

- `172,913,029` prime gaps
- `660,287,089` earlier candidates before the true `GWR` integer
- `0` exact earlier spoilers
- `0` bridge failures

The square-adjacent stress surface remains:

- [output/gwr_proof/earlier_spoiler_local_dominator_scan_square_adjacent_1e12.json](output/gwr_proof/earlier_spoiler_local_dominator_scan_square_adjacent_1e12.json)

That artifact reports:

- `137,771` gaps
- `649,769` earlier candidates
- `0` unresolved

## Conclusion

On the repository's current proof surface, `GWR` is proved and closed.

The visible proof chain is:

1. theorem statement by hierarchical local-dominator law;
2. exact later-side closure by lexicographic raw-$Z$ dominance;
3. exact earlier-side square closure;
4. exact square-free early-arrival closure on the committed admissibility
   frontier;
5. residual low-class closure by the committed residual-class artifacts;
6. exact no-spoiler audit through $p < 5 \cdot 10^9$ plus square-adjacent
   stress coverage at $10^{12}$.

Older bridge-era and proof-progress notes are retained only in the archive:

- [gwr/archive/pre-proof/README.md](gwr/archive/pre-proof/README.md)
- [docs/archive/pre-proof-gwr/README.md](docs/archive/pre-proof-gwr/README.md)
