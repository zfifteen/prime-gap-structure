# The Prime Number Speedup

*Essay 4 in a series about a pattern hiding inside prime numbers. The first three essays built up the math: the Gap Winner Rule, the Divisor Normalization Identity, and the proof status. This essay is about what happens when you point the same identity at a practical engineering problem.*

---

## A problem cryptographers care about

Every time you connect to a website over HTTPS, your browser and the server exchange keys. Those keys are built from prime numbers. Specifically, they are built from pairs of very large primes, each hundreds of digits long.

Generating those primes is not free. The standard method is to pick a large random odd number and test whether it is prime. If it is not, discard it and try another. Repeat until you find one.

The test used to check primality is called Miller-Rabin. It is fast and reliable, but it is not free. Running it costs time. And for a 2048-bit RSA key, you might run it on dozens of candidates before finding a prime. For a 4096-bit key, you might run it on hundreds.

The question the Divisor Normalization Identity raises is: can you filter out some of those composite candidates before paying the full Miller-Rabin cost?

---

## What the DNI says about composites

Recall from Essay 2: under the DNI, every prime maps to Z = 1 exactly. Composites map to values strictly below 1. The more divisors a composite has, the further below 1 it lands.

This gives a structural separation. Primes occupy a fixed point. Composites are displaced from it. The displacement is not random: it is determined by the integer's factor structure.

The practical consequence is that many composites have small prime factors. An integer divisible by 2, 3, 5, 7, or 11 has a lot of divisors, which means a lot of displacement from the prime fixed point. These integers are easy to identify without running Miller-Rabin: just check whether they are divisible by small primes.

This is not a new idea. Trial division against a table of small primes is a standard prefilter in prime generation. What the DNI contributes is a principled framework for calibrating exactly how deep that table should go, and a theoretical basis for why the filtered candidates are structurally closer to primes.

The implementation in this repository builds a deterministic prefilter using exactly that logic. Candidates that survive the small-prime table are passed to Miller-Rabin. Candidates that fail are discarded immediately.

---

## The benchmark numbers

The prefilter was tested against deterministic corpora of RSA keypairs at two key sizes.

For **2048-bit RSA keys**, tested over 300 deterministic keypairs:

- Baseline (no prefilter): 291,938 ms total
- Accelerated (with prefilter): 139,943 ms total
- Speedup: **2.09x**
- Fraction of Miller-Rabin calls eliminated: **90.97%**

For **4096-bit RSA keys**, tested over 50 deterministic keypairs:

- Baseline (no prefilter): 757,751 ms total
- Accelerated (with prefilter): 268,558 ms total
- Speedup: **2.82x**
- Fraction of Miller-Rabin calls eliminated: **91.07%**

Those are end-to-end numbers. They include all overhead: candidate generation, prefilter evaluation, Miller-Rabin on survivors, and final confirmation. The speedup is real and reproducible from the committed benchmark corpus.

The 91% rejection rate means roughly 9 out of every 10 composite candidates get discarded before the expensive test runs. The primes that remain are the only ones that pay full cost.

---

## Where the math and the engineering connect

The prefilter itself is not mysterious. Small-prime tables are standard practice. What is new is the theoretical grounding.

The DNI says the prime class is the fixed point of a specific normalization. That fixed point is exact: Z(p) = 1 for every prime, no exceptions, no approximation. The prefilter is a deterministic approximation to that fixed point, using the covered prime table as the proxy.

The 29 calibration primes tested against the exact DNI all stayed at Z = 1.0. Zero composite false positives on the calibration set. That is not a statistical result: it is the arithmetic identity working exactly as derived.

The practical path from the identity to the speedup is:

1. The DNI establishes that primes are structurally distinguished by their divisor count.
2. Integers with small prime factors have high divisor counts and map far from the fixed point.
3. A prefilter based on small-prime divisibility eliminates those integers cheaply.
4. The survivors are structurally similar to primes, so Miller-Rabin rarely wastes effort.

The Gap Winner Rule is what connects the DNI to prime gap structure. The prefilter is what connects it to cryptographic practice. They are downstream of the same identity.

---

## What a completed proof would add

Right now the prefilter is empirically calibrated. The 91% rejection rate comes from measuring how many candidates the prime table eliminates at the tested bit sizes. The speedup is real, but the theoretical claim is "this works at these sizes" rather than "this works for all inputs."

A completed proof of the Gap Winner Rule would change that. It would establish that the DNI fixed-point structure is exact and universal, not just empirically reliable. The prefilter would become a theorem-backed construction: a deterministic screening mechanism with a provable structural basis.

That distinction matters for security-critical applications. A heuristic that performs well in testing is one thing. A heuristic grounded in a proved identity about prime structure is another. The latter is what belongs in cryptographic standards.

The proof is not finished yet. Essay 3 described exactly where it stands. But the engineering result does not wait for the proof: the benchmark numbers are what they are, and anyone can reproduce them.

---

## Try it yourself

The implementation is in Python and installs from the repository root:

```bash
git clone https://github.com/zfifteen/prime-gap-structure
cd prime-gap-structure
python3 -m pip install -e ./src/python
```

The benchmark reproduction commands are documented in:

`docs/prefilter/manual_validation.md`

The exact benchmark corpus, the timing data, and the Miller-Rabin reduction measurements are all committed to the repository. The numbers above are not estimates: they are the committed output of a deterministic run against a fixed corpus.

---

## The two results, stated plainly

This repository carries two linked results from the same arithmetic identity.

The first is mathematical: inside every prime gap, the Divisor Normalization Identity selects a unique selected integer by a simple two-step rule, with zero known exceptions across 42 million prime gaps through one billion. The proof is mostly complete.

The second is engineering: a prefilter derived from the same identity eliminates 91% of composite candidates before Miller-Rabin, producing a 2x to 2.8x end-to-end speedup in RSA key generation at standard bit sizes. The benchmark is fully reproducible.

Neither result depends on the other being finished. The engineering result is live now. The mathematical proof is the work in progress.

The full repository, with all benchmark data, proof artifacts, and documentation, is at:

**https://github.com/zfifteen/prime-gap-structure**

---

*This is the fourth and final essay in the current series. Future posts will cover proof progress as the remaining 18 residual classes are closed, and will go deeper on the structure of the Divisor Normalization Identity and its connections to other areas of number theory.*
