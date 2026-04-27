# Which Composite Wins Inside a Prime Gap, and What That Would Mean for the Next Prime

## A paper about divisor counts between consecutive primes

**Author:** Dionisio Alberto Lopez III (`zfifteen`)
**Repository:** [zfifteen/prime-gap-structure](https://github.com/zfifteen/prime-gap-structure)
**Document Type:** Scientific White Paper — Plain-Language Draft
**Date:** April 2026

---

## Abstract

This paper studies a simple question.

Take two consecutive primes `p < q`.
Look at the composite numbers between them.
If we score each interior number by

$$L(n) = \left(1 - \frac{d(n)}{2}\right)\ln n,$$

which interior number wins?

The Gap Winner Rule (GWR) theorem says that the selected integer is always the first
interior number with the smallest divisor count that appears in the gap, under
the recorded BHP/Robin assumptions.

Because GWR is conditionally proved for every prime gap, it does more than
identify one special composite inside the gap. It also puts a limit on where the
next prime can be. In the common case where the winning interior number has
exactly four divisors, the next prime must arrive before the next prime square
after that selected integer.

This paper explains that statement in ordinary English. It separates three
things clearly:

- what follows exactly from GWR,
- what has already been checked by computation in this repository,
- and how the conditional proof closes under the recorded BHP/Robin assumptions.

---

## 1. Start With One Concrete Gap

Take the consecutive primes `19` and `23`.

The integers between them are:

$$20,\ 21,\ 22.$$

Their divisor counts are:

- `d(20) = 6`
- `d(21) = 4`
- `d(22) = 4`

So the smallest divisor count that appears inside this gap is `4`, and the
first interior number with that divisor count is `21`.

Now compare `21` and `22` under the score

$$L(n) = \left(1 - \frac{d(n)}{2}\right)\ln n.$$

Since both have the same divisor count, the smaller number wins. So `21`
outranks `22`.

That is the local picture this project keeps finding:

- first look for the smallest divisor count that actually appears in the gap,
- then take the first number in the gap with that divisor count.

In this example, the next prime after `21` is `23`.
The next prime square after `21` is `25 = 5^2`.
So the next prime arrives before the next prime square.

That is not yet a proof of anything general.
It is just one small example.

But it shows the kind of statement this project is aiming at.

---

## 2. The Basic Setup

Let `p < q` be consecutive primes.

The **prime gap** is the interval between them.
The **interior** of that gap is the set of integers `n` with

$$p < n < q.$$

Since `p` and `q` are consecutive primes, every interior number is composite.

For each positive integer `n`, let `d(n)` be the number of positive divisors of
`n`.

Examples:

- `d(7) = 2`
- `d(9) = 3`
- `d(10) = 4`

The score used in this project is

$$L(n) = \left(1 - \frac{d(n)}{2}\right)\ln n.$$

This is the logarithm of

$$Z(n) = n^{1 - d(n)/2}.$$

For the prime-gap question in this paper, it is enough to work with `L(n)`.

Inside a given gap, let

$$d_{\min}(p,q) = \min_{p < n < q} d(n).$$

This is the smallest divisor count that actually appears in the gap.

Now define

$$w = \min\{n : p < n < q,\ d(n) = d_{\min}(p,q)\}.$$

This is the first interior number that reaches the smallest divisor count
present in the gap.

The main theorem studied in this repository is:

> the number `w` is always the score maximizer inside the gap.

In other words, the first interior number with the smallest divisor count is
the number that maximizes `L(n)` across the gap under the conditional GWR proof.

This theorem is the **Gap Winner Rule (GWR)**.

---

## 3. What Follows Exactly From GWR

This section states direct consequences of GWR.

Under the recorded BHP/Robin assumptions, GWR is conditionally proved for every
prime gap with composite interior. The following statements are immediate
corollaries of that theorem.

### 3.1 Nothing Earlier Can Be Equally Simple Or Simpler

Suppose the selected integer is `w`, and let

$$\delta = d(w).$$

Then every earlier interior number `n < w` must satisfy

$$d(n) > \delta.$$

Why?

Because if some earlier interior number had fewer than `δ` divisors, then the
selected integer would not have the smallest divisor count in the gap.
And if some earlier interior number had exactly `δ` divisors, then `w` would
not be the first such number.

So before the selected integer appears, the gap must avoid all divisor counts less than
or equal to the selected integer's divisor count.

### 3.2 Nothing Later Can Be Simpler

Every later interior number `n > w` must satisfy

$$d(n) \ge \delta.$$

Why?

Because if some later interior number had fewer than `δ` divisors, then the
selected integer would not have the smallest divisor count in the gap.

So once the selected integer appears, the rest of the gap cannot contain a strictly
simpler interior number.

### 3.3 The Interior Has A Forced Shape

Putting those two facts together, the interior divisor counts must have the
form

$$>\delta,\ >\delta,\ \ldots,\ >\delta,\ \delta,\ \ge \delta,\ \ge \delta,\ \ldots,\ \ge \delta.$$

That is the cleanest plain statement of the consequence:

- before the selected integer, every interior number is more complicated in divisor
  count,
- at the selected integer, the smallest divisor count appears for the first time,
- after the selected integer, nothing simpler ever appears before the gap closes.

This is already more than a statement about one interior composite.
It is a statement about what kinds of interiors the bounding primes are allowed
to leave behind.

---

## 4. Why This Becomes A Statement About The Next Prime

The previous section tells us something about the numbers **after** the selected integer.

Once the selected integer appears, the next prime has to arrive before any later
interior number with fewer divisors can appear.

To write this carefully, define

$$T_{<}(w) = \min\{n > w : d(n) < d(w)\}.$$

This is the first later integer whose divisor count is strictly smaller than
the selected integer's divisor count.

By GWR on the gap `(p, q)`, the next prime must
satisfy

$$q \le T_{<}(w).$$

This is the key shift in viewpoint.

GWR is not only saying which interior composite comes out on top.
It is also saying where the next prime is allowed to be.

Once the winning interior number is fixed, the right endpoint prime has to
arrive before the first later number that is strictly simpler.

---

## 5. The Common Case Where The Selected integer Has Four Divisors

In the tested ranges in this repository, the most common selected integer has exactly
four divisors.

That case is especially concrete.

If `d(w) = 4`, then a later number can be strictly simpler only if it has
divisor count `3`.

Among composite integers, divisor count `3` occurs exactly at prime squares.

So in this common case, the first later number with fewer divisors than `w` is
the next prime square after `w`.

If we write that next prime square as `S_+(w)`, then

$$q \le S_+(w).$$

This is the clearest consequence for the next prime:

> in the common case where the selected integer has four divisors, the next prime must arrive before the next
> prime square after the winning interior number.

That is a very unusual statement.

It says a composite number inside the gap can give an upper bound on where the
next prime is allowed to be.

---

## 6. What The Repository Has Actually Checked

This section records the finite base and stress surface behind the proof chain.
It is not the whole proof by itself; the universal closure also uses the
analytic bridge and verification record.

### 6.1 The Finite Selected integer Surface

The repository reports zero counterexamples in its current set of validation
runs,
which includes:

- exact runs at `10^6` and `10^7`,
- and deterministic sampled windows up to `10^18`.

In total, the cases checked so far contain more than `4.6` million tested gaps
with no observed counterexample to GWR.

### 6.2 Earlier Interior Candidates

The hardest part of the proof is not the later side of the gap.
It is the earlier side.

The exact scan file in `output/gwr_proof/` checks every earlier interior
candidate against the actual selected integer on the full exact range through
`2 × 10^7`.

That file reports:

- `1163198` prime gaps with composite interior,
- `3349874` earlier interior candidates before the selected integer,
- `0` exact earlier candidates beating the selected integer.

So on that full exact range, every earlier interior candidate already loses to
the actual selected integer.

### 6.3 How Close The Hardest Earlier Cases Come

The repository also measures, for each earlier interior candidate, how close it
comes to the exact failure threshold.

One useful ratio for that comparison, which does not depend on the overall
size of the numbers, is

$$C(k, w) = \frac{\frac{\ln w}{\ln k} - 1}{\frac{d(k) - d_{\min}}{d_{\min} - 2}}.$$

For this ratio:

- values below `1` are safe,
- values at or above `1` would signal failure.

On the exact range through `2 × 10^7`, the largest observed value is only
about `0.0566`.

That means the hardest observed exact case uses only about `5.66%` of what
would be needed to fail.

So the current exact data do not show a result barely hanging on.
They show a result with a lot of room to spare.

### 6.4 The Hardest Cases Are Not The Largest Gaps

Another checked result is that the hardest observed exact cases are not the
largest prime gaps in the tested range.

They occur in very small local patterns, especially gaps of length `4` and
nearby tiny configurations.

That matters because it suggests the main difficulty is local, not a broad
scale effect that simply gets worse and worse as numbers grow.

### 6.5 The Common Four-Divisor Case Remains Clean At High Scale

The closure checks for the common case where the selected integer has four divisors
extend through the checked sequence of runs to `10^18`.

The closure-check file in `output/` reports zero closure failures on that
checked sequence.

In the common case where the selected integer has four divisors, the repository records:

- the mean distance from the selected integer to the next prime stays only about `12`
  at exact `10^6` and about `20` near `10^18`,
- while the mean distance from the selected integer to the next prime square grows from
  about `5869.6` to about `3595291803.7`.

So in the checked large-scale runs, the next prime is arriving far earlier than
the next prime-square threat.

That is not a standalone proof of the dominant $d=4$ mechanism. It is strong
evidence that this common case is not close to failure in the ranges checked so
far.

---

## 7. How The Proof Closes

The later side of the argument is elementary and already proved in the
repository notes.

For composite numbers `a < b`, if

$$d(a) \le d(b),$$

then

$$L(a) > L(b).$$

This says something simple about order:

- if the earlier composite has no more divisors than the later one,
- then the earlier composite has the larger score.

This already settles the later side of the gap once the selected integer appears.

Why?

Because after the selected integer, every later interior number has divisor count at
least as large as the selected integer's divisor count.
So this proved ordering result already forces the selected integer to beat every
later interior competitor.

The earlier side is closed by the committed bridge chain:

- exact finite scan through $p < 20{,}000{,}001$;
- zero earlier competing integers across `1,163,198` prime gaps and `3,349,874` earlier
  candidates;
- analytic BHP/Robin bridge for the large-$p$ tail;
- verification-record thresholds `102` and `3,544`, both below the exact finite base.

Together, these pieces prove GWR conditionally for all prime gaps under the
recorded BHP/Robin assumptions.

---

## 8. What The Current Evidence Suggests About The Bridge Geometry

Here is where the project becomes more interesting than it first appears.

At the level of divisor counts alone, the comparison inequality leaves many
formal patterns to consider.

But when the repository looks at **actual** interiors of gaps between
consecutive primes, those patterns do not show up as a broad hard region.

Instead, the checked data show:

- no exact earlier failures through `2 × 10^7`,
- a largest observed value of only `0.0566` for the ratio defined above,
- hardest cases concentrated in tiny local configurations,
- and zero closure failures through the checked sequence of runs to `10^18`.

That contrast suggests something important.

The bridge is not only a better inequality. It also tracks which divisor-count
patterns can actually happen
inside a real gap between consecutive primes.

In other words:

- many patterns may be possible on paper,
- but far fewer may be possible inside actual prime gaps.

That is now the geometric reading of the conditional proof surface: the exact
finite base is not merely a validation table, but the overlap region where the
analytic bridge lands.

---

## 9. Why This Matters

Because GWR is conditionally proved for every prime gap under the recorded
BHP/Robin assumptions, the result says
something unusual about primes.

It would say that the interior composite structure of a gap is not just a by-
product of where the primes happened to land.

It would say that once the winning interior number is fixed, the next prime is
also constrained.

In the common case where the selected integer has four divisors, that would mean:

> the next prime must appear before the next prime square after the winning
> interior number.

That is a local statement about prime placement derived from the structure of
the composite interior.

That is why this project is worth taking seriously.

It is not only proposing a pattern. It carries a conditional theorem with exact
local consequences, a finite base, and an explicit analytic bridge.

---

## 10. What Still Needs Work

The remaining tasks are now narrower than proving GWR itself.

1. Strengthen or replace the conditional BHP/Robin bridge if an unconditional
   GWR proof is desired.

2. Explain why the common case where the selected integer has four divisors stays so far away from the next
   prime-square threat in the checked high-scale runs.

3. Explain why the hardest checked cases seem to live in tiny local patterns
   rather than in the largest gaps.

4. Decide whether the next independent theorem should target only a sharper
   comparison argument, or whether it should also describe which divisor-count
   patterns can actually occur inside real prime gaps.

Those are hard problems.

But they are much narrower than “explain all prime gaps at once.”

---

## 11. Conclusion

This paper has tried to say one thing plainly.

Inside a gap between consecutive primes, GWR says the winning interior composite
is the first number in the gap with the smallest divisor count present.

Because that is conditionally proved for every prime gap under the recorded
BHP/Robin assumptions, the theorem does more than identify one special
composite.

It also tells us something about where the next prime can be.

In the common case where the selected integer has four divisors, the next prime must
arrive before the next prime square after that selected integer.

The repository has checked this picture on exact finite ranges and checked runs
at large scale, and those artifacts now feed the finite side of the proof chain.

The later side is elementary. The earlier side is closed by the exact finite
base plus the BHP/Robin bridge verification record.

That is the state of the project in the simplest honest language I know.

---

## References

All mathematical claims and measured results in this paper come from source
files already present in this repository.

The main sources are:

- the gap-selected integer notes in `gwr/findings/`
- the notes on exact consequences for later interior numbers and for the next
  prime in `gwr/findings/`
- the notes that summarize exact scans, large-scale checks, and hardest
  observed cases in `gwr/findings/`
- the exact scan files in `output/gwr_proof/`
- the closure-check files in `output/`
