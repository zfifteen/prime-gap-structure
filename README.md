# Geodesic Prime Prefilter

![Geodesic Prime Prefilter hero](docs/assets/geodesic-prime-prefilter-hero.jpg)

Deterministic cryptographic prime prefiltering derived from the sweet-spot Z-band at $v = e^{2}/2$.

This repository presents the geodesic prime prefilter as a deterministic cryptographic primitive. It gives the mathematical basis of the method, a production Python implementation, and the validation vectors and benchmarks needed to reproduce the result.

## Overview

Every positive integer has a divisor pattern.

- A prime has exactly two positive divisors: 1 and itself.
- A composite has additional positive divisors.

This distinction is the starting point. A number with more exact divisors carries more internal factor structure than a number with fewer. Divisor count alone, however, is not enough, because the same divisor count does not mean the same thing at different scales. The approach therefore combines divisor structure with logarithmic size.

The logarithmic term accounts for magnitude in a balanced way. It registers growth in size without letting raw magnitude overwhelm the structural signal. Moving from $10$ to $100$ to $1000$ produces steady increments, so divisor structure can be compared meaningfully across small and large integers.

The resulting combined quantity is called curvature. Curvature measures the departure of an integer from the minimal divisor case. This is the simplest structure represented by a prime. Primes have the lowest curvature. As additional exact divisors appear, the integer carries more internal branching relative to that baseline. When divisor structure and logarithmic scale are taken together, this accumulated departure is the quantity denoted by $\kappa(n)$.

We call the resulting law the **Divisor Curvature Equation**:

$$
\kappa(n) = \frac{d(n) \cdot \ln(n)}{e^{2}}
$$

where:

- $d(n)$ is the divisor count of $n$
- $\ln(n)$ is the natural logarithm of $n$
- $e^{2}$ is the normalization constant

This equation measures how much factor structure an integer carries once scale is taken into account. With curvature defined, primes are the minimal case under this measure, while composites carry increasingly more structural load. This is the sense in which the framework speaks of straightness, distortion, or curvature in integer space.

## Sweet-Spot Derivation

The curvature signal becomes useful when it is passed through the Z-transform:

$$
Z(n) = \frac{n}{\exp(v \cdot \kappa(n))}
$$

where $v$ is a traversal rate.

For the geodesic prime prefilter, the distinguished value is

$$
v = \frac{e^{2}}{2}
$$

because it produces an exact cancellation. Substitute the Divisor Curvature Equation into the Z-transform:

$$
Z(n) = \frac{n}{\exp\left(v \cdot \frac{d(n) \cdot \ln(n)}{e^{2}}\right)}
$$

Now set $v = e^{2}/2$:

$$
\begin{align*}
Z(n) &= \frac{n}{\exp\left(\frac{e^{2}}{2} \cdot \frac{d(n) \cdot \ln(n)}{e^{2}}\right)} \\
&= \frac{n}{\exp\left(\frac{d(n)}{2} \cdot \ln(n)\right)} \\
&= \frac{n}{n^{d(n)/2}} \\
&= n^{1 - d(n)/2}
\end{align*}
$$

So the sweet-spot closed form is

$$
Z(n) = n^{1 - d(n)/2}
$$

This has an immediate effect:

- Prime: $d(p) = 2$, so $Z(p) = 1$
- Semiprime with two distinct prime factors: $d(n) = 4$, so $Z(n) = 1/n$
- Composite in general: $d(n) > 2$, so $Z(n) < 1$

Under the exact sweet-spot model, the entire prime class collapses to the invariant band $Z = 1.0$. Composites are pushed strictly below that band.

## Why This Becomes a Prefilter

This effect is the practical core of the method. Cryptographic prime generation spends most of its time on candidates that are composite and never need a full probable-prime path. Standard Miller-Rabin pipelines are fast, but they do not provide a structural invariant of this kind. The sweet-spot band does.

Because confirmed primes live at $Z = 1.0$ and composites contract below it, the prefilter creates a clean structural separation in normalized space. That separation makes it possible to reject many candidates before paying the full cost of the survivor regime.

## Production Filter

The exact sweet-spot closed form depends on exact divisor count. That exact path is valuable as the derivation and as the oracle, but it is not the runtime path for cryptographic-scale key generation.

The production implementation in this repository therefore uses a deterministic surrogate with the same invariant target:

- generate deterministic odd candidates from a SHA-256 namespace/index stream
- reject immediately when a concrete factor appears in the gated prime tables
- keep survivors on the band convention `proxy_z = 1.0`
- run fixed-base Miller-Rabin on survivors
- apply final `sympy.isprime` confirmation in the current Python path

So the logic flows in one direction:

- the Divisor Curvature Equation defines the structural signal
- the sweet-spot traversal rate turns that signal into the prime fixed-point band
- the band creates a usable structural separation
- the production filter exploits that separation to reduce Miller-Rabin work

Empirically, this extracted Python path produced:

- $2.09\times$ end-to-end speedup across $300$ deterministic $2048$-bit RSA keypairs
- $2.82\times$ end-to-end speedup across $50$ deterministic $4096$-bit RSA keypairs
- $90.97\,\%$ to $91.07\,\%$ Miller-Rabin reduction while preserving the prime band

## Empirical Results

### End-to-End RSA Key Generation

- $2048$ bits, $300$ deterministic keypairs:  
  baseline $291938.126792$ ms  
  accelerated $139942.831833$ ms  
  speedup $2.09\times$  
  Miller-Rabin reduction $90.97\,\%$
- $4096$ bits, $50$ deterministic keypairs:  
  baseline $757750.922792$ ms  
  accelerated $268557.631625$ ms  
  speedup $2.82\times$  
  Miller-Rabin reduction $91.07\,\%$

### Candidate-Loop Screening

- $2048$-bit control corpus:  
  proxy rejection $91.02\,\%$  
  pipeline speedup $2.95\times$
- $4096$-bit control corpus:  
  proxy rejection $91.41\,\%$  
  pipeline speedup $3.33\times$

### Fixed-Point Calibration

- $29/29$ calibration primes stayed on $Z = 1.0$
- $0$ composite false fixed points

See [docs/benchmarks.md](docs/benchmarks.md) for the curated benchmark summary and [docs/manual_validation.md](docs/manual_validation.md) for the exact reproduction commands.

## Python API

Install the Python package from the repo root:

```bash
python3 -m pip install -e ./src/python
