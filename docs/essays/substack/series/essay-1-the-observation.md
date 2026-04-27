# Every Prime Gap Has a Selected integer

*Essay 1 in a series about a pattern hiding inside prime numbers. No advanced number theory required. Start with consecutive primes, count divisors, and the pattern appears.*

---

## Start with the gap

Take two consecutive primes: 23 and 29.

There is no prime between them, so the interior integers

24, 25, 26, 27, 28

are all composite.

That gives a very concrete question:

**Among the composite integers inside a prime gap, is there one that stands out in a consistent way?**

On the tested surface behind this project, the answer is yes.

And the rule that picks the selected integer is simpler than it has any obvious right to be.

---

## Count divisors

For each integer in the gap, count how many positive divisors it has.

A prime has exactly 2 divisors: 1 and itself.

A composite has more. The exact count depends on its factor structure.

Here is the gap between 23 and 29:

| Number | Divisors | Count |
|--------|----------|-------|
| 24 | 1, 2, 3, 4, 6, 8, 12, 24 | 8 |
| 25 | 1, 5, 25 | 3 |
| 26 | 1, 2, 13, 26 | 4 |
| 27 | 1, 3, 9, 27 | 4 |
| 28 | 1, 2, 4, 7, 14, 28 | 6 |

One number is visibly simpler than the rest in divisor structure: 25.

It has only 3 divisors because it is a prime square: 5 squared. Prime squares are the unique composite integers with divisor count 3.

So in this gap, the smallest divisor count is 3, and 25 carries it.

That makes 25 the selected integer.

---

## Try another gap

Now look at the gap between 89 and 97. Its interior is

90, 91, 92, 93, 94, 95, 96.

| Number | Divisors | Count |
|--------|----------|-------|
| 90 | 1, 2, 3, 5, 6, 9, 10, 15, 18, 30, 45, 90 | 12 |
| 91 | 1, 7, 13, 91 | 4 |
| 92 | 1, 2, 4, 23, 46, 92 | 6 |
| 93 | 1, 3, 31, 93 | 4 |
| 94 | 1, 2, 47, 94 | 4 |
| 95 | 1, 5, 19, 95 | 4 |
| 96 | 1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 96 | 12 |

This time the minimum divisor count is 4, and several integers carry it:

91, 93, 94, 95.

The selected integer is the leftmost one.

So the selected integer of this gap is 91.

At this point the rule looks almost too plain:

**Take the smallest divisor count present in the gap, then take the leftmost integer carrying it.**

That is the whole selection rule.

---

## What "selected integer" means

The word "selected integer" is not decorative. It comes from an exact score.

For each interior integer `n`, define

> score(n) = (1 - d(n)/2) * ln(n)

where `d(n)` is the divisor count of `n`.

For primes, `d(n) = 2`, so the score is exactly 0.

For composites, `d(n) > 2`, so the coefficient `(1 - d(n)/2)` is negative. That makes the score negative.

So inside a prime gap, every interior number has a negative score, and the selected integer is the integer with the score closest to zero.

In the gap from 23 to 29:

- `score(25) = (1 - 3/2) * ln(25) = -0.5 * ln(25)`
- every other interior integer has divisor count at least 4, so its score is more negative

In the gap from 89 to 97:

- 91, 93, 94, and 95 all have divisor count 4
- among equal divisor counts, the leftmost integer wins automatically, because the same negative coefficient is multiplied by a smaller logarithm

So the divisor rule is not a shortcut that usually works.

It is the exact ordering rule on the tested surface:

**the highest-scoring interior integer is the leftmost carrier of the smallest divisor count present in the gap.**

This is the Gap Winner Rule.

---

## Why this is surprising

The score mixes two different things:

- divisor count, which measures factor structure
- logarithm, which measures size

There is no obvious reason in advance that the selected integer should always be selected by such a clean lexicographic rule:

1. minimize divisor count
2. break ties by taking the leftmost carrier

But that is exactly what the tested surface shows.

The complicated-looking score collapses to a very simple local decision.

---

## What I actually checked

This is not based on a few nice examples.

In the current public repository, the rule matches the exact score maximizer on

- exact scans through `10^6`
- exact scans through `10^7`
- sampled windows from `10^8` through `10^18`

That adds up to **4,423,459 tested prime gaps** with **0 counterexamples observed**.

So the strongest supported claim is:

**On the current tested surface, every checked prime gap has a canonical interior selected integer, and the selected integer is exactly the leftmost carrier of the smallest divisor count present in the gap.**

That is finite evidence, not an unconditional theorem for all primes. But it is already much stronger than a handful of numerical coincidences.

---

## Why I think this matters

Prime gaps usually get described only by their length: how many integers sit between one prime and the next.

This pattern says the interior has a sharper structure than that.

It says each tested gap contains a distinguished composite landmark: one interior integer that sits highest under the score, and that landmark can be found by an elementary arithmetic rule.

Once you see the rule, several visible features of the data start to line up:

- selected integers are usually near the left edge of the gap
- selected integers are often low-divisor composites
- the selected integer is not found by a floating-point optimization first, but by a discrete divisor hierarchy

So this is not just a curiosity about one formula. It is a claim that prime-gap interiors carry an unexpectedly rigid local ordering.

---

## Run it yourself

Here is a plain Python check for the first 1,000 prime gaps:

```python
from sympy import divisor_count, isprime, nextprime
import math


def gwr_winner(p, q):
    interior = [n for n in range(p + 1, q) if not isprime(n)]
    if not interior:
        return None
    min_d = min(divisor_count(n) for n in interior)
    return next(n for n in interior if divisor_count(n) == min_d)


def score(n):
    return (1 - divisor_count(n) / 2) * math.log(n)


def verify_gap(p, q):
    interior = [n for n in range(p + 1, q) if not isprime(n)]
    if not interior:
        return True
    winner = gwr_winner(p, q)
    winner_score = score(winner)
    return all(score(n) <= winner_score for n in interior)


p = 2
violations = 0
for _ in range(1000):
    q = nextprime(p)
    if not verify_gap(p, q):
        violations += 1
        print(f"Violation at gap ({p}, {q})")
    p = q

print(f"Violations found: {violations}")
```

You should get:

```text
Violations found: 0
```

The full codebase and validation artifacts are in the public repository:

[zfifteen/prime-gap-structure](https://github.com/zfifteen/prime-gap-structure)

---

*Next essay: why this score is not arbitrary, and why every prime collapses to exactly the same value under the underlying normalization.*
