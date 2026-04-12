# GWR_PROOF.md

## Gap Winner Rule: Local Admissibility Proof Status

This document records the current proof chain for the `Gap Winner Rule`
(`GWR`) after replacing the former BHP tail as the live earlier-side route.

The theorem statement itself is unchanged. What changed is the engine used to
attack the earlier side.

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

Source:
[`gwr/findings/gwr_hierarchical_local_dominator_theorem.md`](gwr/findings/gwr_hierarchical_local_dominator_theorem.md)

## Component 1: Later Side (Closed)

Every later composite $m > w$ satisfies $L(m) < L(w)$.

This is the ordered-dominance step: if $a < b$ and $d(a) \le d(b)$, then
$L(a) > L(b)$. Applying that with $a = w$ and $b = m$ closes the entire later
side immediately.

Source:
[`gwr/findings/lexicographic_raw_z_dominance_theorem.md`](gwr/findings/lexicographic_raw_z_dominance_theorem.md)

## Component 2: Earlier Side, Square Branch (Closed)

If the first interior carrier of the minimal divisor class is a prime square
$s = r^2$, then every earlier composite $k < s$ satisfies $L(k) < L(s)$.

The proof is elementary:

- every earlier composite before the first interior prime square has
  $d(k) \ge 4$,
- so $L(k) \le -\ln k$,
- and because the previous prime below $r^2$ lies above $r = \sqrt{s}$, every
  earlier interior composite satisfies $k > \sqrt{s}$,
- hence $-\ln k < -\frac{1}{2}\ln s = L(s)$.

So the square branch is no longer part of the unresolved tail.

Source:
[`gwr/findings/prime_gap_admissibility_theorem.md`](gwr/findings/prime_gap_admissibility_theorem.md)

## Component 3: Earlier Side, Square-Free Branch (Reduced To A Finite Chamber Problem)

The square-free branch is now handled by a fixed local chamber model rather
than by an asymptotic prime-gap bridge.

The model is:

- wheel modulus $W = 30030$,
- early window $K = 128$,
- uniform high-divisor bucket $d(k) \ge 64$,
- exact low-class residual set $\{4, 6, 8, 12, 16, 24, 32, 48\}$.

The new extractor
[`gwr/experiments/proof/prime_gap_admissibility_frontier.py`](gwr/experiments/proof/prime_gap_admissibility_frontier.py)
canonicalizes each exact hard case by the local chamber data and writes the
current proof-facing frontier.

The committed artifacts are:

- exact through $2 \cdot 10^7$:
  [`output/gwr_proof/prime_gap_admissibility_frontier_2e7.json`](output/gwr_proof/prime_gap_admissibility_frontier_2e7.json)
- retained exact frontier from the $10^9$ no-early-spoiler scan:
  [`output/gwr_proof/prime_gap_admissibility_frontier_1e9_checkpoints.json`](output/gwr_proof/prime_gap_admissibility_frontier_1e9_checkpoints.json)

Those artifacts record three decisive facts.

### 3.1 No current non-square hard case escapes the fixed window

On both current proof surfaces, the extractor records

$$
\texttt{non\_square\_beyond\_window\_count} = 0.
$$

So every current non-square hard case remains inside the fixed local window
$K = 128$.

### 3.2 The dominant square-free comparison is local once first-$d=4$ arrives early

If a square-free gap contains a first interior $d=4$ carrier $u$ with
$u - p \le 128$, then every earlier composite $k < u$ satisfies $L(k) < L(u)$.

That follows because earlier composites must have $d(k) \ge 5$, so
$L(k) \le -\frac{3}{2}\ln k$, while $L(u) = -\ln u$.

Source:
[`gwr/findings/prime_gap_admissibility_theorem.md`](gwr/findings/prime_gap_admissibility_theorem.md)

### 3.3 The remaining obstruction is finite and low-class

The extractor's automatic table marks every checked class with $d(k) \ge 64$
as automatically eliminated, with zero current failures. The remaining
frontier lies in a finite low-class residual band recorded directly by the
artifact.

So the unresolved earlier-side burden is no longer:

- a BHP constant,
- or a generic high-divisor asymptotic tail.

It is:

- a finite local admissibility closure for the low divisor classes that still
  appear on the retained frontier.

## Component 4: Exact Finite Audit (Committed)

The exact no-early-spoiler surface through $p < 1{,}000{,}000{,}001$ remains:

- `42,101,885` prime gaps examined,
- `149,214,917` earlier candidates checked,
- `0` exact spoilers,
- maximum realized bridge load `3.749140087272451e-08`.

Artifact:
[`output/gwr_proof/parallel_no_early_spoiler_1e9.json`](output/gwr_proof/parallel_no_early_spoiler_1e9.json)

That finite audit is still part of the proof surface. What changed is the
description of what must be closed beyond it.

## Current Strongest Reading

The current proof chain is:

1. later side closed exactly;
2. square branch closed exactly;
3. square-free branch reduced to a fixed local chamber problem with
   $W = 30030$ and $K = 128$;
4. exact proof-facing frontier artifacts now identify the remaining obstruction
   as a finite low-class residual table rather than an asymptotic BHP tail.

So the project's live theorem bottleneck is no longer an explicit
fixed-exponent prime-gap constant. It is the finite local admissibility
closure recorded in
[`gwr/findings/prime_gap_admissibility_theorem.md`](gwr/findings/prime_gap_admissibility_theorem.md).

The exact finite audit through $10^9$ remains unconditional. Full universality
to infinity now depends on closing the remaining finite low-class chamber
families, not on restoring a BHP tail.

## Historical Note

The older bridge documents remain in the repository as historical and
comparison material:

- [`gwr/experiments/proof/proof_bridge_universal_lemma.md`](gwr/experiments/proof/proof_bridge_universal_lemma.md)
- [`output/gwr_proof/proof_bridge_certificate_2e7.json`](output/gwr_proof/proof_bridge_certificate_2e7.json)
- [`gwr/experiments/proof/proof_bridge_certificate.py`](gwr/experiments/proof/proof_bridge_certificate.py)

They are no longer the live proof-critical route recorded in this document.
