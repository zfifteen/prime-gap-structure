---
title: "Bouncy Castle RSA Upper-Band Acceleration"
subtitle: "Technical Note on the Divisor Normalization Identity, Exact RSA Square-Bound Geometry, and a Measured 1.652x Speedup from Early Elimination of Doomed Prime Candidates"
author: "Dionisio Alberto Lopez III"
date: "April 4, 2026"
documentclass: article
fontsize: 11pt
geometry: margin=1in
numbersections: true
link-citations: true
colorlinks: true
abstract: |
  This note records a measured Bouncy Castle RSA key-generation acceleration obtained from one narrow RSA-local change. The mathematical frame comes from the Divisor Normalization Identity (DNI) $Z(n) = n^{1 - d(n)/2}$ at $v = e^2 / 2$, which in this repository yields a deterministic computational lesson: preserve the survivor convention, remove doomed work early, and do not change the final confirmation path. A direct late-stage port of the repository's deeper deterministic factor gating into Bouncy Castle was tested first and rejected no additional candidates on the measured 4096-bit RSA surface. The profitable invariant instead came from Bouncy Castle's own RSA square-bound rule. For 4096-bit RSA, the BC condition $p^2 \ge 2^{4095}$ is equivalent to the exact lower-band constraint $p \ge \sqrt{2}\,2^{2047}$ for each 2048-bit prime candidate, leaving an accepted fraction $2 - \sqrt{2} \approx 58.58\%$ of the 2048-bit interval and a rejected fraction $\sqrt{2} - 1 \approx 41.42\%$. The modified BC build moves that exact acceptance rule earlier in the RSA candidate path while leaving the later probable-prime and key-validation logic in place. On the direct-core benchmark surface used in this repository, the modified build reduced 100 runs of 4096-bit RSA key generation from 169.032 s to 102.305 s for a measured 1.652x speedup and a 39.48% wall-time reduction.
---

**Keywords:** Divisor Normalization Identity; DNI; RSA key generation; Bouncy Castle; accepted-band sampling; square-bound geometry; deterministic acceleration

# Opening Statement

One RSA-local change cut direct-core Bouncy Castle `4096`-bit RSA key generation from `169.032093` seconds to `102.305074` seconds on the fixed `100`-run benchmark surface in this repository.

That is a measured `1.652236x` speedup and a `39.475947%` wall-time reduction.

The change is narrow.

- the baseline vendored Bouncy Castle source tree remains untouched,
- only the copied [RSAKeyPairGenerator.java](../../tests/performance-comparisons/bouncycastle-keygen-baseline/vendor/bc-java-r1rv83-rsa-upper-band-v1/core/src/main/java/org/bouncycastle/crypto/generators/RSAKeyPairGenerator.java) differs,
- the later RSA probable-prime and key-assembly logic remain in place,
- the profitable move is not a new heuristic but the early use of an exact failure condition that BC already applied later.

This note explains the mathematics behind that change, why the first direct transfer of the repository's earlier deterministic screening mechanism did not help on BC's late surface, and why BC's own square-bound geometry did.

# The Mathematical Frame From This Repository

The mathematical starting point in this repository is the **Divisor Normalization Identity** (DNI).

The three arithmetic ingredients are

$$
d(n), \qquad
\kappa(n) = \frac{d(n)\ln(n)}{e^2}, \qquad
Z(n) = \frac{n}{\exp(v \cdot \kappa(n))}.
$$

Here $d(n)$ is divisor count, $\kappa(n)$ is the divisor-normalization load, and $Z(n)$ is the resulting normalization field.

At the distinguished normalization scaling parameter

$$
v = \frac{e^2}{2},
$$

the expression collapses exactly:

$$
\begin{aligned}
Z(n)
&= \frac{n}{\exp\left(\frac{e^2}{2}\cdot \frac{d(n)\ln(n)}{e^2}\right)} \\
&= \frac{n}{\exp\left(\frac{d(n)}{2}\ln(n)\right)} \\
&= \frac{n}{n^{d(n)/2}} \\
&= n^{1 - d(n)/2}.
\end{aligned}
$$

That is the DNI.

Its first arithmetic reading is immediate:

- if $n$ is prime, then $d(n) = 2$ and $Z(n) = 1$,
- if $n$ is composite, then $d(n) > 2$ and $Z(n) < 1$.

The repository's production Python path does not compute exact divisor count for cryptographic-scale candidates. That would be the wrong runtime mechanism. What the identity supplies is the invariant. It tells the implementation what has to be preserved:

- primes live on the fixed-point survivor convention,
- composites are the doomed work,
- the job of the prefilter is to move exact rejection earlier without altering final confirmation semantics.

That invariant-first stance is the important transfer principle.

# What the Repository Had Already Established

Before the BC modification work began, the repository had already established a measured deterministic acceleration surface on its own normative Python path.

The curated benchmark summary in [benchmarks.md](../benchmarks.md) and the formal note in [technical_note.md](../../technical-note/technical_note.md) report the following validated production-surface results:

- about `91%` candidate rejection before Miller-Rabin on the tested `2048`-bit and `4096`-bit corpora,
- `2.09x` end-to-end deterministic RSA key-generation speedup on the curated `2048`-bit benchmark surface,
- `2.82x` end-to-end deterministic RSA key-generation speedup on the curated `4096`-bit benchmark surface.

That existing result mattered for the BC work in two ways.

First, it showed that the invariant-first method could produce real cryptographic wall-clock gains, not just local classification wins.

Second, it suggested a natural first transfer hypothesis: perhaps the repository's deeper deterministic factor gating could be inserted into BC's RSA prime-candidate path and recover a similar benefit there.

That hypothesis was the right first thing to test. It was also wrong on the specific BC surface where it was first tried.

# Bouncy Castle Baseline Path

In the vendored `r1rv83` source snapshot, the RSA prime-choice loop lives in [RSAKeyPairGenerator.java](../../tests/performance-comparisons/bouncycastle-keygen-baseline/vendor/bc-java-r1rv83/core/src/main/java/org/bouncycastle/crypto/generators/RSAKeyPairGenerator.java).

At the relevant level, baseline BC does this inside `chooseRandomPrime(bitlength, e, sqrdBound)`:

1. generate a candidate with `BigIntegers.createRandomPrime(bitlength, 1, random)`,
2. reject if `p mod e = 1`,
3. reject if `p^2 < sqrdBound`,
4. reject if the later BC probable-prime test fails,
5. reject if `gcd(e, p - 1) != 1`,
6. otherwise accept `p`.

The important fact is step 1. In [BigIntegers.java](../../tests/performance-comparisons/bouncycastle-keygen-baseline/vendor/bc-java-r1rv83/core/src/main/java/org/bouncycastle/util/BigIntegers.java), `createRandomPrime(bitlength, 1, random)` already does nontrivial cleanup before RSA sees the candidate at all:

- it makes the candidate odd and full-width,
- it screens against the product of odd primes from `3` through `743`,
- it applies `rv.isProbablePrime(1)`.

So by the time RSA's later loop sees the candidate, BC has already removed a large amount of cheap composite structure.

That observation is what made the direct late-stage factor-gate port a falsifiable question rather than an article of faith.

# Why the First Direct Port Failed

The first BC transfer attempt was the most obvious one: add the repository's deeper deterministic factor tables after BC's existing `createRandomPrime()` work and see whether that removes additional doomed candidates before the later randomized probable-prime path.

That attempt was tested directly in [BouncyCastleKeygenStrategyProbe.java](../../tests/performance-comparisons/bouncycastle-keygen-baseline/src/BouncyCastleKeygenStrategyProbe.java), with results recorded in [the canonical strategy probe JSON](../../tests/performance-comparisons/bouncycastle-keygen-baseline/results/bcprov-jdk18on-1.83-source-r1rv83-rsa4096-strategy-probe-seed-byte-42.json) and summarized in [BC_STRATEGY_DEEP_DIVE.md](../../tests/performance-comparisons/bouncycastle-keygen-baseline/BC_STRATEGY_DEEP_DIVE.md).

The result was decisive.

- deeper repo-style chunked-GCD tables through `300,007` rejected `0` additional candidates,
- extending the same idea through `1,000,003` also rejected `0` additional candidates,
- both additions only increased cost on the measured BC post-`createRandomPrime()` surface.

The direct transfer mechanism therefore failed exactly where it was first inserted.

That does not weaken the repository's earlier result. It localizes it. The earlier Python win was a win on a different candidate surface, with different upstream work already done before the late-stage test. BC had already consumed most of the easy small-factor opportunity before the point where the first port was attempted.

The no-patch strategy probe also revealed something much more important.

On a fixed corpus of `4096` BC-generated `2048`-bit prime candidates:

- `2376 / 4096 = 58.0078125%` survived the later `mod e` and square-bound checks,
- `1720 / 4096 = 41.9921875%` were rejected on that surface,
- the dominant rejector was the square-bound rule, not late extra factor discovery.

That is the observation that changed the direction of the work.

# Exact Square-Bound Geometry

For `4096`-bit RSA, Bouncy Castle generates two `2048`-bit primes and then requires

$$
p^2 \ge 2^{4095}.
$$

This is the later `sqrdBound` rejection rule in BC's RSA prime loop.

Let the prime-candidate bit length be $b = 2048$. Then the full raw `2048`-bit candidate interval is

$$
[2^{b-1}, 2^b) = [2^{2047}, 2^{2048}).
$$

The BC square-bound rule is equivalent to

$$
p \ge \sqrt{2^{4095}} = 2^{4095/2} = \sqrt{2}\,2^{2047}.
$$

So the exact accepted band is

$$
\left[\sqrt{2}\,2^{2047}, 2^{2048}\right).
$$

The accepted fraction of the full `2048`-bit interval is therefore

$$
\frac{2^{2048} - \sqrt{2}\,2^{2047}}{2^{2047}}
= 2 - \sqrt{2}
\approx 0.5857864376.
$$

The rejected fraction is

$$
1 - (2 - \sqrt{2})
= \sqrt{2} - 1
\approx 0.4142135624.
$$

This is an exact arithmetic statement. It is not a heuristic estimate.

It also matches the probe data closely. The strategy probe measured an observed accepted fraction of `58.0078125%` and an observed rejected fraction of `41.9921875%` on BC's actual candidate stream, which is close to the exact geometric split above.

That geometry yields a simple ceiling estimate for the maximum speedup obtainable from removing only this loss while leaving all other work unchanged:

$$
\text{ideal speedup ceiling} = \frac{1}{2 - \sqrt{2}} \approx 1.7071067812.
$$

That ceiling becomes a useful benchmark for interpreting the later measured experiment.

# The Modification

The modified BC build lives in a sibling vendored tree:

- baseline tree: [bc-java-r1rv83](../../tests/performance-comparisons/bouncycastle-keygen-baseline/vendor/bc-java-r1rv83/)
- modified tree: [bc-java-r1rv83-rsa-upper-band-v1](../../tests/performance-comparisons/bouncycastle-keygen-baseline/vendor/bc-java-r1rv83-rsa-upper-band-v1/)

Only one source file differs between those trees:

- [RSAKeyPairGenerator.java](../../tests/performance-comparisons/bouncycastle-keygen-baseline/vendor/bc-java-r1rv83-rsa-upper-band-v1/core/src/main/java/org/bouncycastle/crypto/generators/RSAKeyPairGenerator.java)

The change is local to `chooseRandomPrime()`.

## Baseline Logic

In baseline BC, the prime-selection core is logically:

$$
\text{candidate} \leftarrow \texttt{createRandomPrime(bitlength, 1, random)}
$$

followed by the later RSA-local rejection checks.

## Modified Logic

In the modified tree, `chooseRandomPrime()` first computes

$$
\text{minPrime} = \left\lceil \sqrt{\text{sqrdBound}} \right\rceil.
$$

It then replaces the original prime source with an RSA-local helper that generates only from the accepted band:

1. generate a `bitlength` random integer,
2. set the top bit and the low odd bit,
3. reject immediately if the candidate is below `minPrime`,
4. apply the same odd-prime-product GCD screen from `3` through `743`,
5. apply the same certainty-`1` `isProbablePrime(1)` screen,
6. return only a candidate already inside the later BC accepted band.

After that, the later BC logic is still executed:

- reject if `p mod e = 1`,
- reject if the later BC probable-prime test fails,
- reject if `gcd(e, p - 1) != 1`,
- return the candidate otherwise.

The old square-bound line is still present, but it is converted from a late retry path into an invariant assertion. If it ever triggers, the modified build fails immediately because the new helper has violated the exact band contract it was supposed to enforce. On the measured benchmark surface, that invariant did not fail.

The patch therefore does not introduce a new primality rule. It moves an exact BC acceptance condition earlier.

# Why This Change Follows the Repository's Theory

The repository's mathematics and the BC patch mathematics are related, but they are not the same formula.

The DNI does not contain the number $2 - \sqrt{2}$. That number comes from BC's own RSA size geometry.

What the DNI supplies is the method:

- identify the invariant that defines the survivor set,
- locate a large doomed region,
- eliminate that region earlier,
- keep the final confirmation path intact.

The first BC transfer attempt used the repository's immediate runtime mechanism, namely deeper deterministic factor gating. The probe falsified that particular insertion point on BC's late candidate surface.

The successful BC patch still follows the same invariant-first method, but it does so on a different arithmetic object:

- the repository supplied the screening philosophy,
- BC's square-bound rule supplied the exact doomed slice,
- the modification moved that exact slice endpoint earlier.

This is why the patch belongs to the same mathematical program without pretending that the DNI itself directly generates the upper-band formula.

# Accuracy, Semantics, and the Real Remaining Question

The ordinary accuracy question for a prime-generation patch is whether the patch starts accepting composites or returning invalid keys.

That is not what this patch does.

The modified build keeps the later BC probable-prime logic in place. It keeps the later RSA key-assembly logic in place. The benchmark harness in [BouncyCastleKeygenUpperBandV1Benchmark.java](../../tests/performance-comparisons/bouncycastle-keygen-baseline/src/BouncyCastleKeygenUpperBandV1Benchmark.java) validates, for every measured keypair:

- modulus bit length `4096`,
- public exponent `65537`,
- equality of public and private modulus.

So the ordinary correctness surface is preserved on the benchmarked regime.

The real remaining question is narrower and more specific: distribution.

Baseline BC begins from a full-width `2048`-bit candidate, then later discards candidates below the square-bound. The modified helper instead resamples immediately when the full-width candidate lands below the lower accepted-band edge.

That means the experiment establishes all of the following:

- the later square-bound acceptance predicate is preserved,
- the later BC probable-prime path is preserved,
- the measured wall-clock gain is real,
- the patch does not introduce an obvious primality-classification failure.

But the experiment does not yet prove full distributional identity with baseline BC over the accepted band.

That distinction matters because the remaining review question is not "does this still generate primes?" It clearly does on the measured surface. The remaining question is "does it sample the final accepted prime space in a way that BC would consider equivalent enough for a production cryptographic patch?"

That is a different question from primality accuracy, and it should be treated separately.

# Experimental Method

The modified benchmark harness is [BouncyCastleKeygenUpperBandV1Benchmark.java](../../tests/performance-comparisons/bouncycastle-keygen-baseline/src/BouncyCastleKeygenUpperBandV1Benchmark.java), run by [run_upper_band_v1.sh](../../tests/performance-comparisons/bouncycastle-keygen-baseline/run_upper_band_v1.sh).

The measurement contract matches the source-built baseline:

- direct BC core path via `org.bouncycastle.crypto.generators.RSAKeyPairGenerator`,
- source-built BC `1.83` from vendored tag `r1rv83`,
- `4096`-bit RSA,
- `100` timed iterations,
- `0` warmups,
- public exponent `65537`,
- certainty `144`,
- `SHA1PRNG`,
- fixed seed bytes `[42]`,
- build under Homebrew JDK `25.0.2`,
- run under Homebrew JDK `21.0.10`.

The canonical baseline artifact is [bcprov-jdk18on-1.83-source-r1rv83-rsa4096-direct-core-seed-byte-42-runs-100.json](../../tests/performance-comparisons/bouncycastle-keygen-baseline/results/bcprov-jdk18on-1.83-source-r1rv83-rsa4096-direct-core-seed-byte-42-runs-100.json).

The canonical modified artifact is [bcprov-jdk18on-1.83-source-r1rv83-rsa-upper-band-v1-rsa4096-direct-core-seed-byte-42-runs-100.json](../../tests/performance-comparisons/bouncycastle-keygen-baseline/results/bcprov-jdk18on-1.83-source-r1rv83-rsa-upper-band-v1-rsa4096-direct-core-seed-byte-42-runs-100.json).

The experiment report is [BOUNCY_CASTLE_RSA_UPPER_BAND_V1_REPORT.md](../../tests/performance-comparisons/bouncycastle-keygen-baseline/results/BOUNCY_CASTLE_RSA_UPPER_BAND_V1_REPORT.md).

# Results

The measured result is:

| Metric | Baseline | RSA upper-band v1 |
|---|---:|---:|
| Total wall time (ms) | `169032.092789` | `102305.073667` |
| Mean time per keypair (ms) | `1690.320928` | `1023.050737` |
| Median time per keypair (ms) | `1498.037208` | `954.640542` |
| Throughput (keypairs/s) | `0.591604` | `0.977469` |

From those values:

- measured speedup = `1.652236x`,
- wall-time reduction = `39.475947%`,
- throughput increase = `65.223568%`.

This is not a marginal effect. It is a large wall-clock recovery from a one-file RSA-local patch.

# Interpreting the Result Against the Exact Ceiling

The exact accepted-band fraction is

$$
2 - \sqrt{2} \approx 0.5857864376,
$$

so the simple ideal ceiling from removing only that geometric loss is

$$
\frac{1}{2 - \sqrt{2}} \approx 1.7071067812.
$$

The measured speedup was

$$
1.6522356784.
$$

That is about `96.79%` of the simple ceiling.

That closeness matters. It means the result behaves much more like the recovery of a real dominant wasted-work slice than like a loose secondary tuning effect.

The measured result stays below the simple ceiling because the upper-band change does not remove everything else in RSA key generation:

- modulus assembly still happens,
- modulus-length checks still happen,
- NAF-weight checks still happen,
- CRT construction still happens,
- all accepted-band candidate work still happens.

But the patch removes enough of the dominated discarded-candidate work that the measured speedup lands close to the direct geometric ceiling.

# Why This Result Matters

This repository now has two distinct cryptographic acceleration demonstrations.

The first is the existing Python deterministic prefilter built directly from the DNI survivor logic and concrete factor discovery.

The second is this BC result:

- the same invariant-first method was applied to a different implementation surface,
- the first direct transfer mechanism was tested and falsified where it did not work,
- a different exact arithmetic bottleneck was isolated,
- one narrow RSA-local patch then recovered a large measured wall-clock gain.

That changes the status of the BC question.

It is no longer merely plausible that BC has meaningful optimization room on this surface. It now has a measured optimization path with a large captured gain on direct-core `4096`-bit RSA key generation.

# Next Work

The natural next step is not to widen the claim. It is to tighten it.

The next precise questions are:

1. Can the remaining gap between the measured `1.652236x` and the simple geometric ceiling `1.707107x` be decomposed into fixed downstream work versus residual accepted-band candidate variation?
2. Can the repository's deterministic factor gating now be profitably inserted earlier, inside or before the new upper-band helper rather than after BC's existing `createRandomPrime()` path?
3. Can the distributional consequences of the earlier resampling rule be characterized precisely enough for a stronger semantic claim than the present performance result?

Those are next-phase questions. They do not weaken the result already established here.

# Reproduction

Run the modified benchmark with:

```bash
./tests/performance-comparisons/bouncycastle-keygen-baseline/run_upper_band_v1.sh
```

Run the source-built baseline benchmark with:

```bash
./tests/performance-comparisons/bouncycastle-keygen-baseline/run_baseline.sh
```

Run the no-patch strategy probe that isolated the square-bound opportunity with:

```bash
./tests/performance-comparisons/bouncycastle-keygen-baseline/run_strategy_probe.sh
```
