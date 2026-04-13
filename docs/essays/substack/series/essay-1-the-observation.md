# Every Prime Gap Has a Winner

*This is the first essay in a series about a pattern I found hiding inside prime numbers. No advanced math required. Just arithmetic, curiosity, and a willingness to run some code.*

---

## Start with the gap

Pick any two consecutive prime numbers. Say, 23 and 29.

Between them sit five composite integers: 24, 25, 26, 27, 28. None of them are prime. Each one has more divisors than a prime does, because that is exactly what makes them composite.

Now here is the question that started all of this:

**Is there something special about one of those five numbers? Does one of them stand out from the rest in a consistent, lawful way?**

The answer, it turns out, is yes. And the rule that picks it is simpler than you might expect.

---

## Counting divisors

Every positive integer has divisors: the whole numbers that divide it evenly. The count of those divisors tells you something fundamental about the integer's structure.

A prime number has exactly 2 divisors: 1 and itself. That is the definition of a prime.

A composite number has more. How many more depends on its factor structure.

Look at the five composites in the gap between 23 and 29:

| Number | Divisors | Count |
|--------|----------|-------|
| 24 | 1, 2, 3, 4, 6, 8, 12, 24 | 8 |
| 25 | 1, 5, 25 | 3 |
| 26 | 1, 2, 13, 26 | 4 |
| 27 | 1, 3, 9, 27 | 4 |
| 28 | 1, 2, 4, 7, 14, 28 | 6 |

Notice anything? One of these numbers has only 3 divisors. That is 25, which is 5 squared. A prime square always has exactly 3 divisors: 1, the prime, and the square itself. So 25 is the integer in this gap with the least internal factor structure.

Now here is the rule: **the winner is the leftmost integer carrying the minimum divisor count.**

In this gap, the minimum divisor count is 3, carried only by 25. So 25 is the winner.

---

## Try another gap

Take the gap between 89 and 97. The interior is: 90, 91, 92, 93, 94, 95, 96.

| Number | Divisors | Count |
|--------|----------|-------|
| 90 | 1,2,3,5,6,9,10,15,18,30,45,90 | 12 |
| 91 | 1,7,13,91 | 4 |
| 92 | 1,2,4,23,46,92 | 6 |
| 93 | 1,3,31,93 | 4 |
| 94 | 1,2,47,94 | 4 |
| 95 | 1,5,19,95 | 4 |
| 96 | 1,2,3,4,6,8,12,16,24,32,48,96 | 12 |

Minimum divisor count is 4. Several numbers carry it: 91, 93, 94, 95. The rule says take the leftmost. That is 91.

91 is the winner of this gap.

---

## What "winning" actually means

I have not told you what winning means yet. Here is the precise statement.

Assign each integer in the gap a score. The score is:

> score = (1 minus half the divisor count) times the natural log of the number

In symbols, if *d(n)* is the divisor count of *n*:

> score(n) = (1 - d(n)/2) * ln(n)

For a prime, *d = 2*, so the score is (1 - 1) * ln(n) = 0. Primes score exactly zero.

For composites, *d > 2*, so the score is negative. More divisors means a more negative score. Larger numbers push the score further negative too, but the divisor term is stronger.

The **Gap Winner Rule** says: the integer with the highest score in any prime gap is always the leftmost carrier of the minimum divisor count. Every other integer in the gap scores strictly lower.

In the gap between 89 and 97, 91 has the highest score. Check it against 90, 92, 93, 94, 95, 96. It wins every comparison.

---

## Why this is surprising

There is no obvious reason this should work. The score mixes two things: divisor count (a number theory property) and logarithm (a size measure). The claim is that minimizing divisor count, then picking the leftmost tie, perfectly replicates what the score formula would select, across every prime gap.

It is a simplification. Instead of computing the score for every interior integer, you just need to find the integer with the fewest divisors and, among ties, the first one.

And it has no known exceptions.

---

## The scan

I wrote a program to check this rule across every prime gap up to one billion. That means every consecutive prime pair (p, q) where both primes are below one billion.

Results:

- **42,101,885** prime gaps examined
- **149,214,917** earlier candidates checked against the rule
- **0** counterexamples found

Not a single gap, anywhere in the first billion integers, where the rule fails.

You can reproduce this yourself. The code is open source and runs in Python. The full scan artifacts are committed to the repository with exact checksums so the result is verifiable independently.

---

## What I am not claiming

I am not claiming this is proven for all primes everywhere, to infinity.

The proof is mostly written. The later side (why nothing after the winner can beat it) is fully closed. The branch where the winner is a prime square is fully closed. The dominant case is reduced to a local arithmetic problem with a window of 128 integers. What remains is a finite list of 18 specific divisor-count configurations that need one more structural argument.

But the empirical record is clean. Zero exceptions in the first billion.

That is the observation. The proof is catching up to it.

---

## Run it yourself

Here is the core of the check in plain Python. You will need a prime sieve and a divisor counter, both standard:

```python
from sympy import isprime, nextprime, divisor_count
import math

def gwr_winner(p, q):
    """Return the Gap Winner Rule selection for the gap (p, q)."""
    interior = range(p + 1, q)
    composites = [n for n in interior if not isprime(n)]
    if not composites:
        return None
    min_d = min(divisor_count(n) for n in composites)
    return next(n for n in composites if divisor_count(n) == min_d)

def score(n):
    return (1 - divisor_count(n) / 2) * math.log(n)

def verify_gap(p, q):
    """Check that the GWR winner has the highest score in (p, q)."""
    interior = range(p + 1, q)
    composites = [n for n in interior if not isprime(n)]
    if not composites:
        return True
    winner = gwr_winner(p, q)
    winner_score = score(winner)
    return all(score(n) <= winner_score for n in composites)

# Check the first 1000 prime gaps
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

Run it. You will get zero violations.

The full repository, with the billion-scale scan artifacts and the proof documentation, is at:

**https://github.com/zfifteen/prime-gap-structure**

---

*Next essay: Why the scoring formula is not arbitrary, and what it means that every prime collapses to exactly the same value under it.*
