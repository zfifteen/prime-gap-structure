# PNT/GWR Prime Formula Audit

This note records the first local audit pass on
[the Perplexity handoff paper](./pnt_gwr_prime_formula_paper.md).

The packaged implementation now lives in
[`src/python/z_band_prime_predictor/predictor.py`](../../../src/python/z_band_prime_predictor/predictor.py).
The original research-path script at
[`pnt_gwr_predictor.py`](./pnt_gwr_predictor.py) is now a thin wrapper around
that production surface.

The strongest supported correction is concrete:

- if an integer seed $s$ already lies inside the gap $(p_{n-1}, p_n)$, then
  `nextprime(s - 1)` returns $p_n$ exactly;
- the paper's witness map $W_\delta(s)$, defined as the first composite at or
  after $s$ with divisor count $\delta$, is not exact for arbitrary in-gap
  seeds;
- the witness path is exact only when a target integer with divisor count
  $\delta$ still lies in $[s, p_n)$.

That last condition is necessary and sufficient. If the search starts after the
last in-gap integer of the requested divisor class, the witness leaves the gap
and the recovered prime is no longer $p_n$.

## First Counterexamples

The first seed-level counterexample to the paper's stated $W_{d_{\min}}$
zero-residual claim appears in the gap $(7, 11)$:

- interior composites: $8$ with $d=4$, $9$ with $d=3$, $10$ with $d=4$;
- $d_{\min} = 3$;
- seed $s = 10$ lies inside the gap but to the right of the only $d=3$ integer;
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
must lie at or before the last interior $d_{\min}$ integer. For the dominant
$d=4$ specialization, the seed must lie at or before the last interior
$d=4$ integer.

For gap prediction in the dominant $d=4$ regime, there is a sharper exact
statement. Let $\sigma^-_4(p, q)$ be the last $d=4$ composite below $p$, and
let $\sigma^+_4(p, q)$ be the last $d=4$ composite in $(p, q)$. Then the
first $d=4$ witness after an integer seed $s$ lies in $(p, q)$ if and only if

$$\sigma^-_4(p, q) < s \le \sigma^+_4(p, q).$$

This is the exact dominant-regime seed corridor. Seeds at or below
$\sigma^-_4$ are blocked by a pre-gap spoiler. Seeds above $\sigma^+_4$ miss
the target gap because no in-gap $d=4$ integer remains.

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
- exact $d=4$ seed-corridor hit rate: $0.0000$;
- blocked by a pre-gap $d=4$ spoiler: $0.7185$;
- target gaps with no interior $d=4$ integer: $0.2815$;
- mean deficit from the left corridor edge: $50.42$;
- mean exact corridor width: $11.09$;
- mean prime offset: $-52.07$;
- mean absolute rank offset: $6.55$.

The earlier forward-only admissibility count was too loose because it asked
only whether some in-gap $d=4$ integer lay ahead of the seed. Gap recovery
also requires the seed to start to the right of the last pre-gap $d=4$
integer. On this corrected exact corridor metric, the result is stronger:
whenever the target gap contains $d=4$ integers at all, the current PNT seed is
still blocked by a pre-gap spoiler. The remaining problem is therefore not
witness recovery inside the target gap. It is crossing the lower exclusion
endpoint.

## Practical Consequence

The nontrivial open problem is no longer "find a seed inside the correct gap
and then recover $p_n$ with a witness." Once the seed is inside the gap,
`nextprime` already recovers $p_n$ exactly.

The nontrivial problem is stricter:

- either predict the exact dominant-regime corridor
  $(\sigma^-_4(p, q), \sigma^+_4(p, q)]$ from $n$;
- or enlarge the admissible seed region so the witness map can start
  outside the final gap but still cross the last pre-gap spoiler and land on
  an in-gap integer;
- or predict a seed that lands before a certified in-gap integer, not merely
  somewhere inside the gap.
