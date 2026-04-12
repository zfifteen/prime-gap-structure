# Prime-Gap Admissibility Theorem

This note fixes the local admissibility proof engine that replaces the former
large-$p$ BHP tail as the live route for the earlier side of `GWR`.

The governing question is concrete.

Let $(p, q)$ be consecutive primes with composite interior

$$I = \{p+1, \ldots, q-1\}.$$

Let

$$w = \min \{n \in I : d(n) = \delta_{\min}(p, q)\}$$

be the leftmost carrier of the smallest divisor count present in the gap. The
later side is already closed by
[`lexicographic_raw_z_dominance_theorem.md`](./lexicographic_raw_z_dominance_theorem.md).
The only remaining issue is the left flank:

for every earlier composite $k < w$, why must

$$L(k) < L(w), \qquad L(n) = \left(1 - \frac{d(n)}{2}\right)\ln n?$$

The local admissibility route says the answer should not be an asymptotic prime
gap bound. It should be a local description of which pre-winner chamber states
actual prime gaps are allowed to realize.

## The Target

The theorem target is:

1. real consecutive-prime gaps realize only a finite family of dangerous local
   chamber states before the winner;
2. every such state is closed either by the square theorem, the square-free
   first-$d=4$ theorem, or a finite residual lemma.

That is the replacement for the former BHP tail. The problem is now local and
deterministic rather than asymptotic.

## Local Model

The chamber model used in the extractor
[`../experiments/proof/prime_gap_admissibility_frontier.py`](../experiments/proof/prime_gap_admissibility_frontier.py)
is fixed up front:

- wheel modulus $W = 30030$,
- early window $K = 128$,
- uniform high-divisor bucket $d(k) \ge 64$,
- exact low-class residual set $\{4, 6, 8, 12, 16, 24, 32, 48\}$.

Each exact hard case is canonicalized by

$$
(\text{gap},\ p \bmod W,\ d_{\min},\ d(k),\ \operatorname{off}(k),\ \operatorname{off}(w),\ \operatorname{off}_{d=4},\ \operatorname{sq\_margin},\ \operatorname{off}_{\mathrm{dom}})
$$

where:

- $\operatorname{off}(k) = k - p$,
- $\operatorname{off}(w) = w - p$,
- $\operatorname{off}_{d=4}$ is the first interior $d=4$ offset when present,
- $\operatorname{sq\_margin}$ is the signed distance from the winner to the
  first later interior prime square, measured against the right boundary,
- $\operatorname{off}_{\mathrm{dom}}$ is the offset from $k$ to the first later
  interior composite that beats it exactly.

The committed artifacts are:

- exact through $2 \cdot 10^7$:
  [`../../output/gwr_proof/prime_gap_admissibility_frontier_2e7.json`](../../output/gwr_proof/prime_gap_admissibility_frontier_2e7.json),
- retained exact frontier from the $10^9$ no-early-spoiler scan:
  [`../../output/gwr_proof/prime_gap_admissibility_frontier_1e9_checkpoints.json`](../../output/gwr_proof/prime_gap_admissibility_frontier_1e9_checkpoints.json).

## Square Branch Theorem

The square branch closes cleanly.

### Theorem

Let $(p, q)$ be consecutive primes, and let $s = r^2$ be the first interior
prime square in the gap. Then every earlier composite $k$ with $p < k < s$
satisfies

$$L(k) < L(s).$$

So when a prime square is the first interior carrier of the minimal divisor
class, it already beats the entire earlier left flank.

### Proof

Because $s$ is the first interior prime square, no earlier interior composite
has divisor count $3$. So every earlier composite $k < s$ satisfies

$$d(k) \ge 4.$$

Hence

$$L(k) = \left(1 - \frac{d(k)}{2}\right)\ln k \le -\ln k.$$

Now $s = r^2$ with $r$ prime. Since there are no primes in $(p, q)$ and
$s < q$, the left boundary prime $p$ is also the previous prime below $s$.
Bertrand's theorem gives a prime in $(r, 2r)$, and for $r \ge 3$ one has
$2r < r^2 = s$. Therefore the previous prime below $s$ lies strictly above
$r$, so

$$p > r = \sqrt{s}.$$

Every earlier interior composite satisfies $k > p$, hence $k > \sqrt{s}$.
Therefore

$$-\ln k < -\ln \sqrt{s} = -\frac{1}{2}\ln s = L(s).$$

Combining the two inequalities gives $L(k) < L(s)$.

The tiny case $s = 4$ is vacuous because the gap $(3, 5)$ has no earlier
interior composite.

## Square-Free First-$d=4$ Window Lemma

The dominant square-free branch also has a clean local comparison once the
first $d=4$ arrival is known to occur early.

### Lemma

Let $(p, q)$ be consecutive primes. Assume:

1. there is no interior prime square;
2. the first interior carrier with divisor count $4$ exists and is
   $u = p + t$;
3. $t \le 128$.

Then every earlier composite $k$ with $p < k < u$ satisfies

$$L(k) < L(u).$$

So under square exclusion, an early first-$d=4$ arrival is already enough to
close the earlier left flank.

### Proof

Because the gap contains no interior prime square and $u$ is the first
interior $d=4$ carrier, every earlier composite $k < u$ satisfies

$$d(k) \ge 5.$$

Therefore

$$L(k) \le -\frac{3}{2}\ln k.$$

Also

$$L(u) = -\ln u.$$

So it is enough to show $k^{3/2} > u$. Since $k > p$, it is enough to show

$$p^{3/2} > p + 128.$$

This holds for every prime $p \ge 31$. The finitely many smaller prime gaps can
be checked directly, and they already lie inside the exact base.

Hence every earlier composite before $u$ has smaller score than $u$.

## Exact Frontier Status

The new admissibility extractor records three facts that change the proof
program materially.

### 1. The square-free branch stays inside the fixed window

On the exact $2 \cdot 10^7$ surface and on the retained exact $10^9$ frontier,
the extractor records

$$\texttt{non\_square\_beyond\_window\_count} = 0.$$

So on both current proof surfaces, every non-square hard case stays inside the
fixed window $K = 128$.

### 2. The large-divisor tail is no longer the live obstruction

The same extractor writes a deterministic `w < k + K` elimination table using
the exact minimal witness `min_n_with_tau(D)`. On the current artifacts, every
checked class with $D \ge 64$ is marked automatically eliminated, with zero
table failures.

That matches the earlier exact local-dominator findings in
[`earlier_spoiler_local_dominator_findings.md`](./earlier_spoiler_local_dominator_findings.md):
the required dominator offset collapses sharply as the earlier divisor count
rises.

### 3. The remaining obstruction is finite and low-class

The raw low-class remainder has not yet collapsed all the way to the target
residual set. The exact $2 \cdot 10^7$ surface still realizes a broader low
remainder, while the retained $10^9$ frontier already narrows that remainder
substantially.

On the retained $10^9$ frontier, the unsupported classes recorded by the new
summary are

$$
\{10, 14, 18, 20, 22, 26, 27, 28, 30, 36, 40, 42, 44, 50, 52, 54, 56, 60\}.
$$

So the route has changed in a precise way:

- the BHP tail is no longer the live bottleneck,
- the high-divisor tail is no longer the live bottleneck,
- the remaining obstruction is a finite low-class residual table whose exact
  membership is now visible to direct computation.

That is exactly the kind of obstruction this route was designed to expose.

## Present Closure Status

The current status is:

1. later side: closed;
2. square branch: closed by the theorem above;
3. square-free first-$d=4$ branch: closed once early arrival is known, and the
   fixed window $K = 128$ is now the measured exact frontier on both current
   surfaces;
4. high-divisor tail: reduced to a deterministic automatic table, with zero
   current failures;
5. remaining work: close the finite low-class residual lemma.

So the universal theorem is no longer waiting on an explicit BHP constant.
It is waiting on a finite local admissibility closure.

That is the point of this note.
