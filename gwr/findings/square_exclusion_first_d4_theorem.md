# Square-Exclusion First-$d=4$ Theorem

This note records the theorem-shaped form of the dominant $d=4$ reduction.

The core idea is:

in the dominant winner regime, a prime gap first has to avoid admitting any
interior prime square, and then the winner is the first interior carrier with
$d(n)=4$.

That idea can be stated at two different levels.

## 1. Exact Conditional Corollary of GWR

Let $(p, q)$ be a prime gap, and let $w$ be the implemented log-score winner on
the interior composites:

$$
w = \arg\max_{p < n < q} L(n),
$$

where

$$
L(n) = \left(1 - \frac{d(n)}{2}\right)\ln(n).
$$

Assume that GWR holds on the gap and that

$$
d(w)=4.
$$

Then two exact consequences follow.

### Square-exclusion consequence

There is no interior integer $n$ with

$$
p < n < q
\qquad\text{and}\qquad
d(n)=3.
$$

Equivalently, the gap contains no interior prime square.

### First-$d=4$ consequence

If

$$
u = \min \{\, n : p < n < q \text{ and } d(n)=4 \,\},
$$

then

$$
w = u.
$$

In words:

if the GWR winner has divisor class $4$, then the winner is exactly the first
interior $d=4$ carrier, and no prime square appears anywhere inside the gap.

### Why This Is Immediate

Under GWR, the winner is the leftmost interior carrier with minimal divisor
count.

If some interior prime square existed, then some interior integer would have
$d(n)=3<4$, so a $d=4$ carrier could not be the GWR winner.

If some earlier interior integer had $d(n)=4$, then the leftmost tie-break
would force that earlier carrier to win instead.

So once a GWR winner has divisor count $4$, the whole gap is forced into the
shape:

$$
>4,\ >4,\ \ldots,\ >4,\ 4,\ \ge 4,\ \ge 4,\ \ldots,\ \ge 4,
$$

with no interior $3$ anywhere.

This is an exact corollary of GWR, not a new theorem.

## 2. The Actual Theorem Candidate

The stronger statement is to treat this dominant reduction directly as a
prime-gap law.

## Square-Exclusion First-$d=4$ Theorem Candidate

Let $(p, q)$ be a prime gap. Suppose:

1. the interior of the gap contains no prime square;
2. the interior of the gap contains at least one integer with $d(n)=4$.

Then the implemented log-score winner on the interior composites is the first
interior integer with divisor count $4$.

Equivalently, if

$$
u = \min \{\, n : p < n < q \text{ and } d(n)=4 \,\},
$$

then

$$
u = \arg\max_{p < n < q} L(n).
$$

In plain language:

once the gap excludes prime squares, the dominant winner law collapses to first
arrival in the $d=4$ class.

## Why This Is Interesting

This candidate is narrower than full GWR, but it captures the dominant winner
regime on the current tested surface.

It does not say:

- that every gap winner has divisor count $4$,
- that full GWR is proved,
- or that semiprimes alone explain the dominant regime.

It says one precise thing:

in the no-interior-prime-square regime, the implemented winner is the first
interior $d=4$ carrier.

That turns most of the observed winner surface from a global-looking score
optimization into a local exclusion-and-arrival law.

## Why The Class Has To Be $d=4$

The stricter semiprime-only wording is false.

The current exact surface already contains $d=4$ winners that are prime cubes,
for example:

- gap $(6857, 6863)$,
- winner $6859 = 19^3$.

So the correct formulation is about the divisor class $d=4$, not about
semiprimes as a factorization type.

## Current Evidence

The dedicated validation run is documented in
[`dominant_d4_arrival_reduction_findings.md`](./dominant_d4_arrival_reduction_findings.md).

On the current documented surface:

- exact full scan to $10^6$,
- exact full scan to $2 \times 10^7$,
- deterministic even-band windows at every decade from $10^8$ through
  $10^{18}$,

the observed dominant-case result was:

- zero tested $d=4$ winner gaps containing an interior prime square,
- first-$d=4$ match rate exactly $1.0$ on every documented regime,
- thin prime-cube exception family inside the broader $d=4$ winner class.

At the top of the current even-band ladder:

- scale $10^{18}$,
- `180,447` gaps tested,
- `149,279` $d=4$ winner gaps,
- `0` interior-prime-square violations,
- `149,279 / 149,279` first-$d=4$ matches.

So the current status is:

- exact corollary of GWR when the winner class is $4$,
- evidence-backed dominant-case law on the current tested surface,
- theorem candidate if stated independently as a direct prime-gap law.

## Why This Framing Helps

This framing isolates two concrete observables:

1. square exclusion:
   whether any interior prime square occurs at all;
2. first-$d=4$ arrival:
   the location of the earliest interior carrier with divisor count $4$.

That makes the dominant regime much easier to analyze than the full score field.

It also gives the proof program a cleaner form:

- control prime-square intrusion,
- then control the first $d=4$ arrival.

## Safe Summary

The safest way to state the candidate is:

If GWR holds on a gap and its winner has divisor class $4$, then the gap
contains no interior prime square and the winner is the first interior
$d=4$ carrier. Independently of that corollary, the same dominant reduction can
be treated as a standalone theorem candidate: in prime gaps with no interior
prime square and at least one interior $d=4$ carrier, the implemented winner is
the first such $d=4$ carrier.
