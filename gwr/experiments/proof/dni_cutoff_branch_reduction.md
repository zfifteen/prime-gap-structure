# DNI Cutoff Branch Reduction

This note records the exact branch obstruction picture for the cutoff theorem.

It is not a proof of the theorem. It identifies which branch families actually
carry the frontier on the current exact surface, and therefore which symbolic
lemmas are worth proving.

The branch frontier artifact used here is:

- summary:
  [`../../../output/gwr_proof/dni_cutoff_branch_frontier_1e6.json`](../../../output/gwr_proof/dni_cutoff_branch_frontier_1e6.json)
- frontier rows:
  [`../../../output/gwr_proof/dni_cutoff_branch_frontier_1e6_rows.csv`](../../../output/gwr_proof/dni_cutoff_branch_frontier_1e6_rows.csv)

That artifact scans every consecutive prime gap whose current right prime is at
most $10^6$ and records the exact branch extrema.

## 1. What The Exact Branch Frontier Says

On the exact through-$10^6$ surface:

- tested gaps: $78{,}494$,
- branch count: $74$,
- no cutoff counterexample occurred,
- the global frontier branch is $(o(q),d_{\min})=(4,3)$ with
  $E(q)=48$ and cutoff utilization $48/60=0.8$.

The branchwise maxima that matter are:

| branch | max exact peak offset | cutoff utilization |
|---|---:|---:|
| $o(q)=4,\ d_{\min}=3$ | $48$ | $0.8$ |
| $o(q)=2,\ d_{\min}=3$ | $32$ | $0.7272727$ |
| $o(q)=6,\ d_{\min}=3$ | $38$ | $0.6333333$ |
| $o(q)=4,\ d_{\min}=4$ | $22$ | $0.3666667$ |
| $o(q)=6,\ d_{\min}=4$ | $20$ | $0.3333333$ |
| $o(q)=2,\ d_{\min}=4$ | $18$ | $0.4090909$ |
| $o(q)=4,\ d_{\min}=6$ | $14$ | $0.2333333$ |
| $o(q)=6,\ d_{\min}=6$ | $14$ | $0.2333333$ |
| $o(q)=2,\ d_{\min}=6$ | $12$ | $0.2727273$ |
| every branch with $d_{\min}\ge 8$ | $\le 8$ | $\le 0.1590909$ |

So the exact frontier is not led by the high-divisor remainder.

It is led overwhelmingly by the square branch:

$$d_{\min}=3.$$

## 2. The First Correction To The Proof Program

An earlier sketch of the proof program treated the $d_{\min}\ge 6$ branch as
an eventual-impossibility family that should disappear in the tail.

That is not the right reduction.

On the exact surface through $10^6$, the $d_{\min}\ge 6$ classes do persist.
Many of them are tiny-gap cases with very early peaks, especially width-$2$ and
width-$4$ gaps whose only or earliest interior composite already determines the
minimum divisor class.

So the right statement is:

- the high-divisor remainder is not the dangerous family,
- but it is also not absent.

What must be proved is not eventual nonexistence. What must be proved is a
uniform early-arrival bound.

## 3. The Real Pressure Family

The current obstruction picture says:

1. the live branch is $o(q)=4,\ d_{\min}=3$;
2. the next strongest branches are the other square branches
   $(2,3)$ and $(6,3)$;
3. the $d_{\min}=4$ layer is real, but it carries much more slack;
4. everything with $d_{\min}\ge 6$ is currently deep inside the cutoff.

So the proof order should be:

1. prove the square branch,
2. prove the first-$d=4$ branch under square exclusion,
3. prove a small early-arrival bound for the remaining $d_{\min}\ge 6$ branch.

## 4. What Each Lemma Must Say

### 4.1 Square Branch

When $d_{\min}(q)=3$, the exact next-gap minimum is a prime square.

So the branch theorem becomes:

prove that the first interior prime square in the next gap appears before the
branch cutoff.

This is the main live obstruction.

### 4.2 First-$d=4$ Branch

The existing dominant reduction already says:

- if no interior prime square appears,
- and the next-gap minimum divisor class is $4$,
- then the exact next-gap minimum is the first interior integer with $d(n)=4$.

So this branch reduces to:

prove that under square exclusion, the first interior integer with $d(n)=4$ appears
before the branch cutoff.

This branch is not currently close to failure on the exact surface, but it
still needs a theorem.

### 4.3 High-Divisor Remainder

For $d_{\min}\ge 6$, the proof target is no longer “show this branch
disappears.”

The correct target is:

prove that every such branch reaches its lex-min integer very early, with a
uniform bound far below the cutoff.

The exact $10^6$ branch frontier suggests that this remainder should be a small
local-combinatorial lemma, not the main asymptotic obstruction.

## 5. What The Frontier Rows Are For

The frontier CSV records each new exact extremum together with:

- $(o(q), d_{\min})$,
- the exact peak offset,
- the gap endpoint offset,
- and the full divisor ladder through the peak.

That means the proof does not have to reason from scratch about all prime gaps.
It has to explain why the specific extremal ladders appearing in those rows
cannot continue past the branch cutoffs.

So the frontier is not another benchmark report. It is the obstruction list for
the theorem.

## 6. Current Safe Conclusion

The strongest safe conclusion at this stage is:

- the bounded walker theorem has been reduced to one offset theorem;
- the exact branch frontier through $10^6$ shows that the proof should focus
  first on the $d_{\min}=3$ square branch, especially $o(q)=4$;
- the high-divisor remainder is not the main obstruction and should be treated
  as a small-slack local remainder rather than as the dominant tail.
