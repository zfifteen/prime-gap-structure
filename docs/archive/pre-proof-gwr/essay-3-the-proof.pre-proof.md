# How Close Is the Proof?

*Essay 3 in a series about a pattern hiding inside prime numbers. Essays 1 and 2 introduced the Gap Winner Rule and the Divisor Normalization Identity. This essay is about the proof: what is closed, what is open, and what the remaining problem actually looks like.*

---

## The question on the table

The Gap Winner Rule says: inside every prime gap, the integer with the highest DNI score is always the leftmost integer of the minimum divisor count. Zero exceptions found across 42 million prime gaps through one billion.

But "no exceptions found" is not a proof. A pattern that holds for the first billion integers might fail at a trillion, or a quadrillion, or somewhere astronomers cannot yet count to. Mathematics requires certainty, not just a very long run of good luck.

So what does the proof look like? How much is done?

The honest answer is: most of it. The structure of the remaining problem is now visible, and it is finite. That is not a vague promise. It is a precise statement about what kind of mathematics is left to do.

---

## Splitting the problem in two

The Gap Winner Rule makes a claim about every integer in a prime gap. But "every integer" actually splits cleanly into two groups: integers that come after the selected integer, and integers that come before it.

These two cases have completely different characters.

**The later side** asks: why can't something after the selected integer beat it? This turns out to be easy. If integer *w* is the selected integer and *m* comes after it in the gap, then *m > w*. Because *w* was chosen as the leftmost minimum-divisor integer, *m* either has more divisors than *w* or it also has the minimum divisor count but sits to the right. Either way, the DNI score comparison goes in *w*'s favor: smaller divisor count at a smaller position always wins. This direction is fully proved. No remaining work.

**The earlier side** asks: why can't something before the selected integer beat it? This is harder. An integer *k* before the selected integer is smaller than *w*, which helps its score somewhat. The question is whether that size advantage can overcome the divisor-count disadvantage. Can a composite with more divisors, sitting slightly to the left, outscore the selected integer?

The entire remaining proof effort lives on the earlier side.

---

## The earlier side: three cases

The earlier side splits into three sub-cases, and two of them are already closed.

### Case 1: The selected integer is a prime square

Sometimes the first interior integer with the fewest divisors is a prime square, like 25 = 5² or 49 = 7². Prime squares have exactly 3 divisors, which is the minimum possible for a composite. When this happens, every earlier composite in the gap has at least 4 divisors.

Here is why this case closes cleanly. Every earlier composite *k* has at least 4 divisors, so its score satisfies:

> score(k) = (1 - d(k)/2) * ln(k) ≤ -ln(k)

And the selected integer *w = r²* is a prime square. Because there are no primes inside the gap, the left endpoint prime *p* is the nearest prime below *r²*. By a classical theorem (Bertrand's postulate), there is always a prime between *r* and *2r*, which means the prime *p* lies above *r*. So every earlier interior composite satisfies *k > p > r = √w*, which gives:

> score(k) ≤ -ln(k) < -ln(√w) = -(1/2)ln(w) = score(w)

The selected integer beats every earlier composite. Closed. Fully proved. Elementary mathematics only.

### Case 2: The selected integer has 4 divisors and arrives early

The dominant case in practice is when the selected integer is the first interior integer with exactly 4 divisors. Integers with exactly 4 divisors are either semiprimes (products of two distinct primes, like 6 = 2×3 or 15 = 3×5) or prime cubes (like 8 = 2³ or 27 = 3³).

In this case, every earlier composite has at least 5 divisors, giving it a score at most:

> score(k) ≤ -(3/2) * ln(k)

The selected integer *u* with 4 divisors has score -ln(u). So the question reduces to: is -(3/2)*ln(k) < -ln(u), equivalently, is k^(3/2) > u?

Since k > p (every interior composite is greater than the left endpoint prime), it is enough to ask whether p^(3/2) > p + 128. This holds for every prime p ≥ 31. The finitely many gaps with p < 31 can be checked directly by hand.

The "128" is not arbitrary. It is the measured exact frontier: on both the 20-million scan and the billion-scale scan, every hard case in this branch has the selected integer arriving within the first 128 positions after the left endpoint. The scan confirms this ceiling with zero exceptions.

So once the first 4-divisor integer appears within 128 positions, the earlier side is closed for that gap. Closed. Fully proved.

### Case 3: The remaining cases

What is left? The cases where the selected integer has more than 4 divisors, and the earlier composite also has a moderately high divisor count.

Specifically: after removing the prime-square branch and the first-d=4-early-arrival branch, there remain 18 divisor-count classes that need individual attention. These are divisor counts like 10, 14, 18, 20, 22, and so on up to 60.

This is where the proof currently stands.

---

## What the remaining 18 classes look like

The most recent computational run examined the billion-scale frontier carefully and found something important: the score inequality for every one of the 18 classes is already resolved. For each class, there is an explicit inequality showing that if the selected integer is close enough to the earlier candidate, the selected integer wins. The arithmetic is done.

What is not yet done is a universal structural argument for why the selected integer is always close enough.

Concretely, the measured windows from the billion-scale scan are:

| Divisor count of earlier candidate | Maximum observed selected-integer distance |
|---|---|
| 10 | 14 |
| 14 | 7 |
| 18 | 5 |
| 20 | 4 |
| 22 | 1 |
| 26 | 2 |
| 27 | 1 |
| 28 | 4 |
| 30 | 1 |
| 36 | 4 |
| 40 | 2 |
| 42 | 1 |
| 44 | 1 |
| 50 | 2 |
| 52 | 1 |
| 54 | 2 |
| 56 | 2 |
| 60 | 1 |

Every single one of these windows is tiny. The hardest case, divisor count 10, has the selected integer never more than 14 positions away from the earlier candidate, across the entire billion-scale surface. For 12 of the 18 classes, the selected integer is never more than 2 positions away.

The remaining mathematical task is to prove that these windows are structural ceilings, not just empirical observations. For the classes with window 1 (selected integer always immediately adjacent), the question reduces to something about consecutive integers: can two adjacent composites have the left one carrying divisor count D while the right one carries a strictly smaller count? That is a question about divisor structure of consecutive integers, which is tractable.

---

## What "finite" means here

It is worth being precise about what makes this problem finite.

The original formulation of the proof challenge was phrased as an asymptotic question: for large enough primes, does the Gap Winner Rule hold? That framing required bounding how large "large enough" had to be, which connected to deep and unresolved conjectures about prime gap sizes.

The current formulation is different. It is not asking about large primes. It is asking about a finite list of specific divisor-count configurations. Each configuration either can or cannot occur in a prime gap with a selected integer outside the observed window. That is a local question about arithmetic structure, not an asymptotic question about prime distributions.

The difference matters. A finite local problem has a definite answer that can in principle be found by direct computation or elementary argument. An asymptotic problem may require machinery that does not yet exist.

The proof program has moved from the second kind of problem to the first kind. That is the progress.

---

## The honest status summary

| Component | Status |
|---|---|
| Later side (nothing after the selected integer can beat it) | Closed |
| Earlier side: prime square branch | Closed |
| Earlier side: first 4-divisor arrival within 128 positions | Closed |
| Earlier side: divisor count ≥ 64 | Auto-eliminated by exact table |
| Earlier side: 18 low-divisor residual classes | Open (window theorem needed) |

The theorem is not yet proved universally. That is the honest statement.

What has changed is the shape of the remaining problem. It is no longer "we need to bound prime gaps at large scale using unresolved conjectures." It is "we need a structural argument for 18 specific finite window constraints, the tightest of which is a window of 14 and most of which are windows of 1 or 2."

That is the difference between a conjecture and a theorem under active construction.

---

## Why this matters beyond the math

A proof of the Gap Winner Rule would establish that prime gaps have deterministic internal structure under the DNI measure. That is a statement about prime numbers that does not appear in the existing literature under any other framing.

It would also complete the theoretical foundation for the cryptographic prefilter described in the next essay. The prefilter already works empirically, producing a 2x speedup in RSA key generation. A completed proof would make it a theorem-backed construction rather than an empirically calibrated heuristic.

The full proof documentation, including all scan artifacts and the current status of every proof component, is at:

**https://github.com/zfifteen/prime-gap-structure**

---

*Next essay: The engineering payoff. How the same identity that identifies selected interior integers also accelerates RSA key generation by a factor of 2.*
