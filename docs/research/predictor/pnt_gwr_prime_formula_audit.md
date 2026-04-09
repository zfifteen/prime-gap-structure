# PNT/GWR Prime Formula Audit

This note records the first local audit pass on
[the Perplexity handoff paper](./pnt_gwr_prime_formula_paper.md).

The strongest supported correction is concrete:

- if an integer seed $s$ already lies inside the gap $(p_{n-1}, p_n)$, then
  `nextprime(s - 1)` returns $p_n$ exactly;
- the paper's witness map $W_\delta(s)$, defined as the first composite at or
  after $s$ with divisor count $\delta$, is not exact for arbitrary in-gap
  seeds;
- the witness path is exact only when a target carrier with divisor count
  $\delta$ still lies in $[s, p_n)$.

That last condition is necessary and sufficient. If the search starts after the
last in-gap carrier of the requested divisor class, the witness leaves the gap
and the recovered prime is no longer $p_n$.

## First Counterexamples

The first seed-level counterexample to the paper's stated $W_{d_{\min}}$
zero-residual claim appears in the gap $(7, 11)$:

- interior composites: $8$ with $d=4$, $9$ with $d=3$, $10$ with $d=4$;
- $d_{\min} = 3$;
- seed $s = 10$ lies inside the gap but to the right of the only $d=3$ carrier;
- $W_{d_{\min}}(10) = 25$ and `nextprime(25 - 1)` returns $29 \ne 11$.

The first counterexample to the hardcoded dominant-regime path
`nextprime(W_4(s) - 1)` appears even earlier in the gap $(3, 5)$:

- interior composite: $4$ with $d=3$;
- seed $s = 4$;
- $W_4(4) = 6$ and `nextprime(6 - 1)` returns $7 \ne 5$.

## Corrected Witness Statement

Let $(p, q)$ be a prime gap, let $s$ be an integer with $p < s < q$, and let
$\delta \ge 3$. Then `nextprime(W_\delta(s) - 1)` returns $q$ if and only if
there exists at least one composite $k$ with divisor count $d(k) = \delta$ in
the interval $[s, q)$.

For the paper's special case $\delta = d_{\min}(p, q)$, this means the seed
must lie at or before the last interior $d_{\min}$ carrier. For the dominant
$d=4$ specialization, the seed must lie at or before the last interior
$d=4$ carrier.

## Small Exact Surface

The executable audit lives in
[`benchmarks/python/predictor/pnt_gwr_formula_audit.py`](../../../benchmarks/python/predictor/pnt_gwr_formula_audit.py).

On the exact surface up to $10^4$, it reports:

- direct placed recovery by `nextprime(s - 1)` succeeds on every interior
  seed;
- the paper's $W_{d_{\min}}$ map succeeds on $80.6359\%$ of interior seeds;
- the hardcoded $W_4$ map succeeds on $74.8256\%$ of interior seeds.

Those rates are not failures of the gap findings. They show that the current
witness theorem in the paper is stronger than the executable behavior.

## Current PNT-Seeded d=4 Surface

The current dominant-regime sweep lives in
[`benchmarks/python/predictor/pnt_gwr_d4_candidate_sweep.py`](../../../benchmarks/python/predictor/pnt_gwr_d4_candidate_sweep.py).

On the deterministic sweep $n = 10$ through $1000$, it reports:

- exact hit rate: $0.0000$;
- seed-in-target-gap rate: $0.0000$;
- witness-in-target-gap rate: $0.0000$;
- target-gap $d=4$ availability rate: $0.7185$;
- admissible target-gap $d=4$ rate from the seed position: $0.7185$;
- mean prime offset: $-52.07$;
- mean absolute rank offset: $6.55$.

On that surface, the current PNT seed undershoots enough that the first global
$d=4$ witness is always reached before the target gap begins. The remaining
problem is therefore not witness recovery inside the target gap. It is seed
tightening.

## Practical Consequence

The nontrivial open problem is no longer "find a seed inside the correct gap
and then recover $p_n$ with a witness." Once the seed is inside the gap,
`nextprime` already recovers $p_n$ exactly.

The nontrivial problem is stricter:

- either enlarge the admissible seed region so the witness map can start
  outside the final gap and still land on an in-gap carrier;
- or predict a seed that lands before a certified in-gap carrier, not merely
  somewhere inside the gap.
