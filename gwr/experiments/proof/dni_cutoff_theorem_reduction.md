# DNI Cutoff Theorem Reduction

This note fixes the exact theorem whose proof would close the bounded
DNI/GWR walker.

It does not claim that the theorem is already proved. Its job is narrower:

- define the offset theorem precisely,
- show that it is equivalent to exactness of the bounded walker,
- and isolate the computational role of the proof scripts.

## 1. Exact Objects

Let $q$ be a prime and let $q^+$ be the immediate next prime.

Write

$$d(n)$$

for the divisor count of $n$.

Define the exact next-gap minimum-divisor offset

$$E(q)=\min\{\,k \ge 1 : q+k < q^+,\, d(q+k)=d_{\min}(q)\,\},$$

where

$$d_{\min}(q)=\min\{\,d(n): q<n<q^+,\ n\text{ composite}\,\}.$$

So $E(q)$ is the offset of the leftmost minimum-divisor carrier in the next
gap.

Define also

$$o(q)$$

to be the first even offset after $q$ whose residue class is open modulo $30$.
For odd primes this means

$$o(q)\in\{2,4,6\}.$$

Finally define the bounded cutoff map

$$
C(q)=
\begin{cases}
44,& o(q)=2,\\
60,& o(q)\in\{4,6\}.
\end{cases}
$$

## 2. The Cutoff Theorem

The theorem to prove is:

$$E(q)\le C(q)\qquad\text{for every prime }q.$$

Branchwise, this is

- $E(q)\le 44$ when $o(q)=2$,
- $E(q)\le 60$ when $o(q)\in\{4,6\}$.

## 3. Why This Is The Whole Bounded-Walker Problem

The repository now contains two next-gap transition laws.

The exact unbounded transition scans the integers to the right of $q$ until
the first prime boundary appears, then takes the lexicographic minimum over the
composite interior.

That mechanism is exact by construction.

The bounded walker in
[`../../../benchmarks/python/predictor/gwr_dni_recursive_walk.py`](../../../benchmarks/python/predictor/gwr_dni_recursive_walk.py)
uses the same lexicographic rule, but stops after the branch cutoff $C(q)$.

So:

- if the cutoff theorem holds, the bounded and unbounded transitions are
  identical on every prime;
- if the cutoff theorem fails at some prime $q$, the bounded and unbounded
  walkers differ at that prime.

Therefore:

The bounded walker is exact for all primes if and only if the cutoff theorem
holds for all primes.

That is the full reduction.

## 4. Branch Split

The theorem naturally splits first by wheel branch:

- branch $o(q)=2$,
- branch $o(q)=4$,
- branch $o(q)=6$.

Inside each branch the exact next-gap minimum divisor class gives a second
split:

- $d_{\min}(q)=3$,
- $d_{\min}(q)=4$,
- $d_{\min}(q)\ge 6$.

This second split is not a cosmetic classification. The exact frontier surface
shows that the obstruction profile changes materially across these classes.

## 5. Computational Role

The proof scripts do not replace the theorem.

Their role is only:

1. isolate the exact obstruction families the theorem must eliminate,
2. and certify the finite base once an explicit tail lemma is proved.

The relevant executable artifacts are:

- the exact/bounded comparison in
  [`../../../benchmarks/python/predictor/gwr_dni_recursive_walk.py`](../../../benchmarks/python/predictor/gwr_dni_recursive_walk.py),
- the first-counterexample scan in
  [`../../../benchmarks/python/predictor/gwr_dni_cutoff_counterexample_scan.py`](../../../benchmarks/python/predictor/gwr_dni_cutoff_counterexample_scan.py),
- the branch frontier extractor in
  [`./dni_cutoff_branch_frontier.py`](./dni_cutoff_branch_frontier.py).

The counterexample scan answers:

- is the cutoff theorem already false on the tested finite range?

The branch frontier answers:

- which branch and divisor-class families are currently closest to the cutoff?

That makes the remaining proof target precise without confusing exact finite
verification for the theorem itself.

## 6. Closure Style

The accepted closure style for this theorem is:

- derive a symbolic tail lemma that proves $E(q)\le C(q)$ beyond an explicit
  threshold,
- then verify the remaining finite range exactly below that threshold.

So the proof does not require a purely symbolic all-scale argument with no
finite computation. It requires:

- one explicit theorem for the infinite tail,
- one exact finite certificate for the remainder.
