---
title: "The Geodesic Prime Prefilter"
subtitle: "Technical Note on the Divisor Curvature Identity, Deterministic Factor-Gated Filtering, Candidate-Loop Screening, and RSA Key Generation Acceleration"
author: "Dionisio Alberto Lopez III"
date: "March 31, 2026"
documentclass: article
fontsize: 11pt
geometry: margin=1in
numbersections: true
bibliography: references.bib
link-citations: true
colorlinks: true
abstract: |
  The Geodesic Prime Prefilter is a deterministic cryptographic prime prefilter derived from the fixed-point traversal rate $v = e^2 / 2$ of the divisor-curvature normalization $Z(n) = n / \exp(v \cdot \kappa(n))$ with $\kappa(n) = d(n)\ln(n) / e^2$. At that rate the **Divisor Curvature Identity** (DCI) \(Z(n) = n^{1 - d(n)/2}\) holds exactly, so confirmed primes collapse to the invariant band $Z = 1.0$ and composites contract below that band. Validation in this repository shows 29/29 calibration primes on the fixed-point band, 0 composite false fixed points, and an exact-calibration curvature separation ratio of 4.54× on the tractable corpus. The production Python path replaces exact divisor counting with a deterministic factor-gated surrogate that preserves the fixed-point survivor convention before fixed-base Miller-Rabin and final sympy.isprime confirmation. The curated repo benchmark summary reports 91.02 % and 91.41 % candidate rejection before Miller-Rabin on 2048-bit and 4096-bit corpora, candidate-loop speedups of 2.95× and 3.33×, and end-to-end deterministic RSA key-generation speedups of 2.09× over 300 2048-bit keypairs and 2.82× over 50 4096-bit keypairs while reducing Miller-Rabin work by 90.97 % to 91.07 %. The repository therefore establishes the mathematically derived DCI, a deterministic production prefilter built from it, and a measured cryptographic payoff in the tested Python regime.
---

**Keywords:** divisor count; Divisor Curvature Identity; prime generation; Miller-Rabin prefilter; deterministic screening; RSA key generation

# Opening Statement

The Geodesic Prime Prefilter is a deterministic cryptographic prefilter derived from the **Divisor Curvature Identity** (DCI) \(Z(n) = n^{1 - d(n)/2}\) in divisor-curvature normalization.

At the distinguished traversal rate $v = e^2 / 2$, the exact normalization sends every prime to the invariant band $Z = 1.0$ and pushes composites below that band.

The repository establishes four concrete results:

- the exact DCI holds numerically on the tractable calibration corpus,
- the production path preserves the DCI as its survivor convention,
- candidate-loop screening removes about 91 % of tested cryptographic candidates before Miller-Rabin,
- the current Python implementation yields measured end-to-end RSA key-generation gains on deterministic streams.

# Core Proposal

The claim begins with three arithmetic ingredients:

$$
d(n),\qquad
\kappa(n) = \frac{d(n)\ln(n)}{e^2},\qquad
Z(n) = \frac{n}{\exp(v \cdot \kappa(n))}.
$$

Here $d(n)$ is the divisor count, $\kappa(n)$ is the divisor-curvature load, and $Z(n)$ is the curvature-weighted normalization.

At the distinguished fixed-point traversal rate

$$
v = \frac{e^2}{2},
$$

the normalization yields the exact DCI

$$
Z(n) = n^{1 - d(n)/2}.
$$

That identity has immediate arithmetic consequences:

- if $n$ is prime, then $d(n) = 2$ and $Z(n) = 1$,
- if $n$ is semiprime with two distinct prime factors, then $d(n) = 4$ and $Z(n) = 1/n$,
- if $n$ is composite in general, then $d(n) > 2$ and $Z(n) < 1$.

Divisor structure and logarithmic scale determine a traversal rate at which primes occupy a fixed-point band and composites contract below it.

This note describes what the repository establishes when that law is turned into a deterministic prime-screening pipeline.

# Why This Matters Computationally

The DCI supplies an exact invariant target for prime candidates. It separates the mathematical derivation from the runtime production filter without breaking the logic that connects them. It lets the implementation reject many composites before the probable-prime path rather than after it. It yields a deterministic screening front end for prime search inside RSA-style key construction.

The repository presents a deterministic structural prefilter whose payoff can be measured on the same candidate streams and the same final confirmation path.

# Mathematical Core: Fixed-Point Collapse

The divisor-count background belongs to classical multiplicative number theory. The repository uses that arithmetic structure directly.

Start from

$$
\kappa(n) = \frac{d(n)\ln(n)}{e^2}
$$

and

$$
Z(n) = \frac{n}{\exp(v \cdot \kappa(n))}.
$$

Set

$$
v = \frac{e^2}{2}.
$$

Then

$$
\begin{aligned}
Z(n) &= \frac{n}{\exp\left(\frac{e^2}{2} \cdot \frac{d(n)\ln(n)}{e^2}\right)} \\
&= \frac{n}{\exp\left(\frac{d(n)}{2}\ln(n)\right)} \\
&= \frac{n}{n^{d(n)/2}} \\
&= n^{1 - d(n)/2}.
\end{aligned}
$$

That is the exact Divisor Curvature Identity.

The tractable calibration corpus in the repo shows:

- 29/29 calibration primes on the numeric band $Z = 1.0$,
- 0 composite false fixed points,
- prime mean $\kappa = 3.6883$,
- composite mean $\kappa = 16.7545$,
- separation ratio 4.54×.

On that same 20-bit calibration corpus, fixed-base Miller-Rabin matches exact primality with 100 % accuracy in the committed benchmark report.

Under exact divisor counting, the DCI is algebraically exact and numerically clean on the tractable calibration regime tested in this repository.

# Operational Evidence in the Exact Setting

The exact DCI is the derivation surface and the calibration oracle. Exact divisor counting still uses $O(\sqrt{n})$ enumeration in the current executable path. For arbitrary 2048-bit candidates the benchmark report describes the implied worst-case trial space as about $2^{1024}$ divisibility checks per candidate.

That scale boundary cleanly separates two jobs:

- the exact path establishes the law and the calibration band,
- the production path exploits that law without pretending exact divisor counting is the right runtime mechanism at cryptographic scale.

The same calibration corpus shows that the deterministic proxy still preserves the fixed-point reading operationally. On the committed small-panel proxy calibration, it hits 29 fixed points with 0 composite false fixed points and 100 % classification accuracy.

The exact regime therefore anchors the invariant target that the production filter is built to preserve.

# From Exact DCI to Deterministic Production Filter

The runtime pipeline in this repository is intentionally narrow.

1. Generate deterministic odd candidates from a SHA-256 namespace/index stream.
2. Scan the candidate against factor-gated prime tables in primary, tail, and deep-tail intervals.
3. Reject immediately only when a concrete factor is found.
4. Keep survivors on the band convention `proxy_z = 1.0`.
5. Run fixed-base Miller-Rabin on survivors.
6. Apply final `sympy.isprime` confirmation in the current Python implementation.

This is a deterministic prefilter that treats the fixed-point band as the survivor convention and concrete factor discovery as the rejection trigger.

The contract surface is equally narrow:

- `spec/contract.md` fixes the deterministic behavior,
- `spec/vectors/` commits the candidate stream, prefilter decisions, fixed-point checks, and prime-generation vectors,
- Python is the initial normative executable implementation,
- future Java and Apple-Silicon C ports are required to match that same parity surface before any reference-status claim changes.

The exact DCI supplies the invariant. The production path keeps one deterministic execution flow that respects that invariant while moving the expensive work farther down the pipeline.

# Candidate-Loop Screening and RSA Key Generation

The cryptographic screening result appears at two levels.

The first is the candidate loop itself. In the curated repo benchmark summary:

- the 2048-bit control corpus rejects 91.02 % of candidates before Miller-Rabin and reports 2.95× pipeline speedup,
- the 4096-bit control corpus rejects 91.41 % of candidates before Miller-Rabin and reports 3.33× pipeline speedup.

Most candidates never reach the probable-prime path.

The second level is end-to-end deterministic RSA key generation.

For 300 deterministic 2048-bit keypairs, the committed benchmark summary reports:

- baseline 291938.126792 ms,
- accelerated 139942.831833 ms,
- speedup 2.09×,
- Miller-Rabin reduction 90.97 %.

For 50 deterministic 4096-bit keypairs, the same summary reports:

- baseline 757750.922792 ms,
- accelerated 268557.631625 ms,
- speedup 2.82×,
- Miller-Rabin reduction 91.07 %.

The benchmark harness requires the baseline and accelerated paths to produce identical deterministic keypairs. The measured gain therefore comes from screening away composite work earlier on the same deterministic search.

# What The Repository Establishes

The repository establishes the following results.

1. The divisor-curvature normalization has a distinguished fixed-point traversal rate $v = e^2 / 2$ at which the **Divisor Curvature Identity** (DCI) \(Z(n) = n^{1 - d(n)/2}\) holds exactly.
2. Under exact divisor counting on the tractable calibration corpus, confirmed primes lie on $Z = 1.0$, composites contract below that band, and the observed curvature separation ratio is 4.54×.
3. The production Python path converts the DCI into a deterministic factor-gated prefilter with one narrow survivor convention and one narrow rejection rule.
4. On the committed cryptographic candidate corpora, the prefilter removes about 91 % of candidates before Miller-Rabin and yields about threefold candidate-loop speedup in the curated summary surface.
5. On deterministic RSA key generation, the current Python implementation achieves 2.09× speedup at 2048 bits and 2.82× speedup at 4096 bits while cutting Miller-Rabin work by 90.97 % to 91.07 %.
6. The contract, vectors, tests, and benchmark artifacts make the result reproducible and portable across future implementations.

That is the mathematically derived DCI, a deterministic production prefilter built from it, and a measured cryptographic acceleration artifact in the regime the repository has validated.

# Limits and Scope

The current note is strong on the tested Python regime. The DCI is exact, but the executable exact divisor-count path is only practical on the small calibration regime. The production prefilter rejects only when one of the gated prime tables finds a concrete factor. The validated implementation surface is Python. Java and Apple-Silicon C ports are planned in the repo architecture but are not yet parity-complete. The benchmark settings do not exhaust the performance envelope across all bit sizes, machines, or table configurations.

# Practical Interpretation

The practical use of the Geodesic Prime Prefilter is to use the exact DCI as the derivation and audit surface, use the deterministic factor-gated surrogate as the runtime screen, preserve the fixed-point band as the invariant survivor target, and reduce probable-prime workload without changing the deterministic candidate stream or the final confirmation semantics.

In the current repository the mathematical law and the engineering path stay connected. The prefilter is structured around the DCI. That makes the artifact useful both as research code and as a foundation for future ports. Its behavior is compact enough to audit, explicit enough to reproduce, and narrow enough to defend.

# Open Technical Targets

The strongest next steps are:

1. bring the planned Java implementation to committed vector parity,
2. bring the planned Apple-Silicon C99/GMP/MPFR implementation to vector parity and manual benchmark parity,
3. broaden the benchmark surface beyond the current 2048-bit and 4096-bit deterministic corpora,
4. map screening efficiency more explicitly as a function of prime-table limits, chunk sizes, and deep-tail thresholds,
5. tighten the analytic number-theory side of the contraction story beyond the current small-panel exact calibration.

# Conclusion

The narrow mathematical heart of the project is the **Divisor Curvature Identity** (DCI) \(Z(n) = n^{1 - d(n)/2}\)

$$
Z(n) = n^{1 - d(n)/2}
$$

at the traversal rate

$$
v = \frac{e^2}{2}.
$$

The repository now establishes a broader operational result set around that core. The exact DCI is real on the tractable calibration corpus. The production path turns it into a deterministic factor-gated prefilter. The tested Python implementation then converts that screening advantage into measured end-to-end RSA key-generation gains on deterministic streams.

The Geodesic Prime Prefilter now stands as a deterministic production filter built from the DCI and a measured cryptographic acceleration artifact in the regime the repository has validated.

# Artifact References

- [Repository README](../README.md)
- [Benchmark Summary](../docs/benchmarks.md)
- [Architecture Note](../docs/architecture.md)
- [Contract](../spec/contract.md)
- [Benchmark Report](../benchmarks/output/python/BENCHMARK_REPORT.md)
- [Manual Validation](../docs/manual_validation.md)
- [Python Implementation](../src/python/geodesic_prime_prefilter/prefilter.py)
