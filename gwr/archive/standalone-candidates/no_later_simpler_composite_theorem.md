# No-Later-Simpler-Composite Theorem

This note records a theorem-shaped version of the closure intuition.

The core idea is:

Once the score maximizer appears inside a prime gap, the next prime arrives before
any later strictly simpler composite can appear.

That idea can be stated at two different levels.

## 1. Exact Conditional Corollary of GWR

Let $(p, q)$ be a prime gap, and let $w$ be the implemented log-score maximizer on
the interior composites:

$$w = \arg\max_{p < n < q} L(n).$$

where

$$L(n) = \left(1 - \frac{d(n)}{2}\right)\ln(n).$$

Define the later strictly simpler threat horizon of $w$ by

$$T_{<}(w) = \min \{n > w : d(n) < d(w)\}.$$

when such an integer exists.

If GWR holds on the gap, then necessarily

$$q \le T_{<}(w).$$

Equivalently:

There is no interior integer $n$ with $w < n < q$ and $d(n) < d(w)$.

This is an exact corollary of GWR, not a new theorem.

The reason is immediate: if some later interior integer had strictly smaller
divisor count than the selected integer, then the selected integer would not be the minimal-divisor
carrier of the gap and GWR would fail on that gap.

## 2. The Actual Theorem Candidate

The stronger statement is to treat the closure condition itself as a direct
prime-gap law.

## No-Later-Simpler-Composite Theorem Candidate

For every prime gap $(p, q)$, let $w$ be the implemented log-score maximizer on
the interior composites. Then

$$q \le T_{<}(w),$$

or equivalently,

there is no later interior composite $n$ with $w < n < q$ and $d(n) < d(w)$.

In plain language:

Once the score maximizer appears, the next prime closes the gap before any later
strictly simpler composite can enter the interior.

## Why This Is Interesting

This candidate theorem is weaker than full GWR, but stronger than a descriptive
plot-level observation.

It does not say:

- where the selected integer must occur,
- that the selected integer is always the leftmost minimal-divisor carrier,
- or that the full gap interior is lexicographically ordered.

It says only one thing:

the right endpoint of the prime gap is bounded above by the first later
strictly simpler divisor-class threat.

That is already theorem-sized because it turns a selected integer statement into a prime
placement statement.

## The $d=4$ Specialization

For the dominant selected divisor-count class $d(w)=4$, the first strictly smaller divisor
class is $d=3$.

Among composite integers, $d(n)=3$ occurs exactly at prime squares.

So when $d(w)=4$, the threat horizon becomes

$$T_{<}(w) = S_{+}(w).$$

where $S_{+}(w)$ denotes the next prime square after $w$.

In that common case, the candidate theorem says:

$$q \le S_{+}(w).$$

That is a very concrete closure law.

## Current Evidence

The dedicated closure run is documented in
[`closure_constraint_findings.md`](./closure_constraint_findings.md).

On the current documented surface:

- exact full scan to $10^6$,
- mixed-window runs at $10^8$ and $10^9$,
- deterministic even-band runs at every decade from $10^8$ through $10^{18}$,
- even windows and two fixed seeds,

the observed closure violation count was zero in every tested regime.

So the current status is:

- exact corollary of GWR on any gap where GWR holds,
- evidence-backed empirical law on the current tested surface,
- theorem candidate if stated independently as a direct prime-gap closure law.

## Why This Framing Helps

This framing introduces a concrete observable:

$$T_{<}(w) - w,$$

the distance from the selected integer to the first later strictly simpler threat.

The prime gap then has a companion closure margin:

$$T_{<}(w) - q.$$

A positive margin means the gap closed before the threat arrived.

That converts the intuition into a measurable object rather than just a slogan.

## Safe Summary

The safest way to state the candidate is:

If the Gap Winner Rule is the full interior maximizer rule, then the
No-Later-Simpler-Composite condition is an exact corollary. Independently of that,
the same closure condition can be treated as a standalone theorem candidate
about prime-gap termination: once the score maximizer appears, the next prime
arrives before any later strictly simpler composite does.
