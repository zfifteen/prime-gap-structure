# Why Every Prime Lands on the Same Spot

*Essay 2 in a series about a pattern hiding inside prime numbers. You do not need to have read Essay 1, but it helps. The short version: inside every prime gap, one integer consistently outscores all others under a specific formula. This essay explains where that formula comes from and why primes behave so unusually under it.*

---

## A formula that treats every prime the same

Here is an arithmetic formula. Plug in any positive integer *n*:

> Z(n) = n raised to the power (1 minus half its divisor count)

In more compact notation: Z(n) = n^(1 - d(n)/2), where d(n) is the number of positive divisors of n.

Try it on a few integers.

**n = 7** (a prime, d = 2):
Z(7) = 7^(1 - 2/2) = 7^0 = **1**

**n = 11** (a prime, d = 2):
Z(11) = 11^(1 - 2/2) = 11^0 = **1**

**n = 997** (a prime, d = 2):
Z(997) = 997^(1 - 2/2) = 997^0 = **1**

Every prime, no matter how large, produces exactly 1. Not approximately 1. Exactly.

Now try a composite.

**n = 6** (d = 4: divisors are 1, 2, 3, 6):
Z(6) = 6^(1 - 4/2) = 6^(-1) = **0.1667**

**n = 12** (d = 6: divisors are 1, 2, 3, 4, 6, 12):
Z(12) = 12^(1 - 6/2) = 12^(-2) = **0.00694**

**n = 24** (d = 8):
Z(24) = 24^(1 - 8/2) = 24^(-3) = **0.0000723**

The more divisors an integer has, the harder it gets pushed below 1. Primes sit at exactly 1. Composites scatter below it, the highly composite ones pushed furthest down.

This is called the **Divisor Normalization Identity**, or DNI for short.

---

## Why this is not just a curiosity

Most formulas that distinguish primes from composites do so by testing divisibility. You check whether a number has small factors, or you run a probabilistic test, or you apply a sieve. The result is a yes/no answer: prime or not prime.

The DNI does something structurally different. It does not test for primality. It assigns every integer a position on a continuous scale, and the entire prime class collapses to a single fixed point at Z = 1.

That fixed point is not chosen to make the math tidy. It falls out of the arithmetic automatically once you pick the right scaling parameter. Let me show you where it comes from.

---

## Building the formula from scratch

Start with the idea that numbers have "factor load": the more divisors a number carries, the more internal structure it has relative to the prime baseline. Define that load as:

> load(n) = d(n) * ln(n) / e²

where ln(n) is the natural logarithm of n and e² is Euler's number squared (approximately 7.389).

This load measures how far an integer has moved from the minimal-divisor case, once size is accounted for. A prime has d = 2, so its load grows slowly with size. A highly composite number has many divisors, so its load grows much faster.

Now define a normalization transform: take the integer n and divide it by an exponential of its load:

> Z(n) = n / exp(v * load(n))

where v is a free parameter. Different choices of v give different transforms.

Ask: is there a value of v that makes every prime land at exactly the same Z value?

For a prime p, d(p) = 2, so load(p) = 2 * ln(p) / e². Substitute:

> Z(p) = p / exp(v * 2 * ln(p) / e²)
> Z(p) = p / p^(2v / e²)
> Z(p) = p^(1 - 2v/e²)

For this to equal 1 for every prime, the exponent must be zero:

> 1 - 2v/e² = 0
> v = e²/2

That is the unique fixed-point parameter. It is not guessed or chosen for elegance. It is the one value that makes the prime class collapse exactly to 1.

Substitute v = e²/2 back into the general formula and the load cancels cleanly:

> Z(n) = n^(1 - d(n)/2)

That is the DNI. It falls out of the requirement that primes be a fixed point of the transform.

---

## What the fixed point means geometrically

Think of all positive integers plotted on a line by their Z value. Composites spread out below 1, sorted roughly by how much factor structure they carry. Primes all pile up at exactly 1.0, every single one of them, regardless of size.

This is unusual. Most arithmetic functions that grow with n produce values that drift as n grows. The DNI is calibrated so that the growth of ln(n) is exactly cancelled by the divisor-count term for primes, at every scale.

The Z value of a composite shrinks as its divisors increase. The integer 720 has 30 divisors, so Z(720) = 720^(1 - 15) = 720^(-14), an astronomically small number. The integer 2 has 2 divisors, just like a prime, so Z(2) = 2^0 = 1. Wait, 2 is prime. Every prime is exactly 1. Every composite is strictly less than 1.

---

## The connection to the Gap Winner Rule

In Essay 1, the scoring formula for the Gap Winner Rule was:

> score(n) = (1 - d(n)/2) * ln(n)

That is just the natural logarithm of Z(n). The two formulas are the same object:

> score(n) = ln(Z(n)) = ln(n^(1 - d(n)/2)) = (1 - d(n)/2) * ln(n)

So the Gap Winner Rule is not using an arbitrary score. It is finding the integer in the gap with the highest Z value, which means the integer closest to the prime fixed point at 1. Among all the composites in a prime gap, the selected integer is the one most similar to a prime under the DNI measure.

That reframes the whole observation from Essay 1. The rule is not "minimize divisor count and pick the leftmost tie." That is the mechanical selection procedure. The deeper statement is: **inside every prime gap, the integer closest to the prime fixed point under the DNI is always the leftmost minimum-divisor carrier.**

---

## Why the formula is not arbitrary: a symmetry argument

One way to see why this particular formula is natural is to notice what it preserves.

Under the DNI, a prime p always maps to 1. If you take two primes p and q, their ratio Z(p)/Z(q) = 1/1 = 1. The formula treats them as equivalent. That is not true of any simpler function: p/q is not 1, ln(p)/ln(q) is not 1, p^2/q^2 is not 1.

The DNI is the unique power-law normalization that makes the prime class invariant under scaling. It treats primality itself as the reference point, and measures every other integer by how far its factor structure departs from that reference.

That is why it is the right formula for studying prime gaps. The gap between two primes is the interval between two instances of the reference point. The composites inside the gap are departures from that reference. The DNI measures those departures on a consistent scale.

---

## What comes next

The next essay turns to the proof question. The observation is clean and the formula is natural. But does the Gap Winner Rule hold for every prime gap everywhere, or only in the first billion integers where it has been checked?

The short answer is: the proof is mostly written, the remaining piece is a finite local problem, and the structure of that problem is now visible. That is more progress than "we checked a lot of cases." It is the difference between a conjecture and a theorem under construction.

The full repository, including the DNI derivation, the scan artifacts, and the current proof status, is at:

**https://github.com/zfifteen/prime-gap-structure**

---

*Next essay: The proof. What is closed, what is open, and what the remaining problem actually looks like.*
