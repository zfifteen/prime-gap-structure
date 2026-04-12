# Prime Gap Structure

![Prime Gap Structure hero](docs/assets/prime-gap-structure-hero.jpg)

This repository carries two linked results from the same divisor-normalized
arithmetic program.

The executable artifact is a deterministic cryptographic prime prefilter whose
invariant target is the exact **Divisor Normalization Identity** (DNI)

$$
Z_{\mathrm{raw}}(n) = n^{1 - d(n)/2}
$$

at normalization scaling parameter

$$
v = \frac{e^{2}}{2}.
$$

The headline mathematical result now carried by the repository is the
committed theorem statement
[Gap Winner Rule — Hierarchical Local-Dominator Law](gwr/findings/gwr_hierarchical_local_dominator_theorem.md).
Inside a prime gap, the implemented log-score

$$
L(n) = \ln Z_{\mathrm{raw}}(n) = \left(1 - \frac{d(n)}{2}\right)\ln(n)
$$

is maximized exactly at the leftmost interior carrier of the smallest divisor
class present in the gap. The same theorem statement records the two flank
conditions used throughout the repo: every earlier composite is beaten by a
later admissible composite, and no later strictly simpler composite appears
before the gap closes.

The live earlier-side proof route is now the local admissibility program in
[gwr/findings/prime_gap_admissibility_theorem.md](gwr/findings/prime_gap_admissibility_theorem.md).
That route closes the square branch directly, fixes the square-free branch in a
deterministic chamber model with $W = 30030$ and $K = 128$, and records the
remaining obstruction as a finite low-class residual table rather than an
asymptotic BHP tail. The exact finite audit through
$p < 1{,}000{,}000{,}001$ still records `42,101,885` gaps,
`149,214,917` earlier candidates, `0` exact spoilers, and maximum realized
bridge load `3.749140087272451e-08`. See
[GWR_PROOF.md](GWR_PROOF.md) and
[docs/current_headline_results.md](docs/current_headline_results.md).

For the current headline results, see
[docs/current_headline_results.md](docs/current_headline_results.md).

## Overview

Every positive integer has a divisor pattern.

- A prime has exactly two positive divisors: 1 and itself.
- A composite has additional positive divisors.

This distinction is the starting point. A number with more exact divisors
carries more internal factor structure than a number with fewer. Divisor count
alone is not enough, because the same divisor count does not mean the same
thing at different scales. The approach therefore combines divisor structure
with logarithmic size.

The logarithmic term accounts for magnitude in a balanced way. It registers
growth in size without letting raw magnitude overwhelm the structural signal.
Moving from $10$ to $100$ to $1000$ produces steady increments, so divisor
structure can be compared meaningfully across small and large integers.

The resulting combined quantity is called the divisor normalization load. This
load measures the departure of an integer from the minimal divisor case. This
is the simplest structure represented by a prime. Primes have the lowest load.
As additional exact divisors appear, the integer carries more internal
branching relative to that baseline. When divisor structure and logarithmic
scale are taken together, this accumulated departure is the quantity denoted
by $\kappa(n)$.

We call the resulting law the **Divisor Normalization Equation**:

$$
\kappa(n) = \frac{d(n) \cdot \ln(n)}{e^{2}}
$$

where:

- $d(n)$ is the divisor count of $n$
- $\ln(n)$ is the natural logarithm of $n$
- $e^{2}$ is the normalization constant

This equation measures how much factor structure an integer carries once scale
is taken into account. With the divisor normalization load defined, primes are
the minimal case under this measure, while composites carry increasingly more
structural load.

## Terminology

This repository uses precise language to name structural roles inside one
discrete arithmetic normalization. The terminology is intended literally
within that setting.

- **Divisor normalization load** names the scalar quantity
  $\kappa(n) = d(n)\ln(n)/e^2$. It measures how far an integer has moved away
  from the minimal-divisor prime case once divisor structure and logarithmic
  scale are combined.
- **Z-Band** names the straight fixed-point regime selected by the
  normalization. Under the exact DNI, primes occupy the fixed-point locus
  $Z = 1.0$, while composites deviate below it as additional factor structure
  appears.
- **Normalization scaling parameter** names the scalar $v$ in the Z-transform
  $Z(n) = n / \exp(v \cdot \kappa(n))$. The distinguished value $v = e^2/2$
  is the fixed-point parameter because it produces the exact collapse
  $Z(n) = n^{1 - d(n)/2}$.
- **Fixed-point locus** names the normalized set $Z = 1.0$ picked out by the
  exact identity for the prime class.
- **Ridge** names a measured concentration of local maxima in the exact raw
  composite Z-field inside prime gaps.

## Novel Structures in This Repository

Five structures introduced here do not appear under these names in the
literature:

- **Divisor Normalization Identity (DNI):** `Z(n) = n^(1 - d(n)/2)` is an
  exact arithmetic identity collapsing all primes to `Z = 1.0`.
- **Gap Winner Rule (GWR):** inside any prime gap, the log-score argmax is
  exactly the leftmost carrier of the minimum interior divisor class. The live
  proof route is now the local admissibility program recorded in
  [gwr/findings/prime_gap_admissibility_theorem.md](gwr/findings/prime_gap_admissibility_theorem.md).
- **No-Later-Simpler-Composite (NLSC) condition:** once the GWR winner
  appears, no later interior composite with strictly smaller divisor count
  precedes the next prime. Zero violations observed through `10^18`.
- **Dominant d=4 arrival reduction:** under square exclusion, the GWR winner
  is exactly the first interior `d=4` carrier. Exact on full scans through
  `2x10^7`.
- **Dynamic cutoff conjecture:** `C(q) = max(64, ceil(0.5 * log(q)^2))` bounds
  the GWR winner offset for the bounded walker. Empirically calibrated through
  `p <= 10^6`. The fixed map `{2:44, 4:60, 6:60}` is falsified at
  `q = 24,098,209`.

## Divisor Normalization Identity

The divisor normalization load signal becomes useful when it is passed through the Z-transform:

$$
Z(n) = \frac{n}{\exp(v \cdot \kappa(n))}
$$

where $v$ is the normalization scaling parameter.

For the prime-gap structure program in this repository, the distinguished value is

$$
v = \frac{e^{2}}{2}
$$

because it produces an exact cancellation. Substitute the Divisor Normalization Equation into the Z-transform:

$$
Z(n) = \frac{n}{\exp\left(v \cdot \frac{d(n) \cdot \ln(n)}{e^{2}}\right)}
$$

Now set $v = e^{2}/2$:

$$Z(n) = \frac{n}{\exp\left(\frac{e^{2}}{2} \cdot \frac{d(n) \cdot \ln(n)}{e^{2}}\right)}$$

$$Z(n) = \frac{n}{\exp\left(\frac{d(n)}{2} \cdot \ln(n)\right)}$$

$$Z(n) = \frac{n}{n^{d(n)/2}}$$

$$Z(n) = n^{1 - d(n)/2}$$

So the **Divisor Normalization Identity** (DNI) $Z(n) = n^{1 - d(n)/2}$ is

$$
Z(n) = n^{1 - d(n)/2}
$$

This has an immediate effect:

- Prime: $d(p) = 2$, so $Z(p) = 1$
- Semiprime with two distinct prime factors: $d(n) = 4$, so $Z(n) = 1/n$
- Composite in general: $d(n) > 2$, so $Z(n) < 1$

Under the exact DNI, the entire prime class collapses to the fixed-point locus $Z = 1.0$. Composites are pushed strictly below that locus.

This fixed-point collapse is the mathematical base of the repository. It is
the invariant behind both the prime-gap structure line and the deterministic
prefilter line.

## Gap Winner Rule

The central winner law in this repository is that the log-score argmax inside
a prime gap collapses to a simpler arithmetic choice:

1. minimize the interior divisor count $d(n)$,
2. among ties, take the leftmost interior carrier.

That is the Gap Winner Rule.

The formal theorem file expresses this as a hierarchical local-dominator law.
The current proof chain combines elementary later-side lexicographic raw-$Z$
dominance, the exact finite earlier-side audit through $p < 10^9$, the closed
square branch, and the local chamber reduction of the square-free branch. The
remaining live obstruction is a finite low-class residual table rather than an
asymptotic BHP constant.

The newer no-early-spoiler artifacts close the left flank against the actual
winner itself on the exact base and now feed the local admissibility frontier.
On the full exact through-$2 \times 10^7$ surface, the repo records zero exact
earlier spoilers against the true `GWR` carrier, identifies the tightest
realized winner/earlier divisor-class frontier, and packages the remaining
left-side burden as a finite local chamber problem.

See [gwr/story/README.md](gwr/story/README.md),
[gwr/findings/gwr_hierarchical_local_dominator_theorem.md](gwr/findings/gwr_hierarchical_local_dominator_theorem.md),
[gwr/findings/gap_winner_rule.md](gwr/findings/gap_winner_rule.md), and
[gwr/findings/prime_gap_admissibility_theorem.md](gwr/findings/prime_gap_admissibility_theorem.md).

## Exact Recursive Prime Walk

The most jarring combined predictor result in the repository is this: once the
implemented winner appears inside a prime gap, the next prime arrives before
any later interior composite with strictly smaller divisor count can appear.
That closure law is what lets the unbounded DNI/GWR walker recover the next
prime exactly from the ordered divisor structure of the next-gap interior.

Given a known prime `q`, the oracle scans divisor counts to the right until the
first prime boundary, takes the lexicographic minimum over the composite
interior, and recovers the next prime by the witness map. That mechanism is
exact by construction. No cutoff theorem is involved.

On the current verified surface, that mechanism supports an exact deterministic
no-skip sequential walk. The transition rule is exact on `743,075 / 743,075`
rows from the combined $10^6 + 10^7$ next-gap surface, and the recursive walk
records `664,578 / 664,578` exact consecutive next-prime recoveries from prime
`11` through prime `10,000,121` with `0` skipped gaps. The sampled decade
ladder from $10^2$ through $10^18$ also stayed at exact hit rate `1.0` with
`0` skipped gaps across `860` measured recursive steps.

The predictor note is documented in
[docs/research/predictor/gwr_dni_exact_recursive_prime_walk_note.md](docs/research/predictor/gwr_dni_exact_recursive_prime_walk_note.md),
and the live implementation is
[benchmarks/python/predictor/gwr_dni_recursive_walk.py](benchmarks/python/predictor/gwr_dni_recursive_walk.py).

![Exact DNI recursive-walk performance](docs/research/predictor/figures/gwr_dni_recursive_gap_scaling_performance.png)

## Dynamic Cutoff and Square-Branch Falsification

The old fixed cutoff theorem `{2:44, 4:60, 6:60}` is false. It fails at
`q = 24,098,209`, where the square branch gives `E(q) = 72 > 60`. The bounded
walker in the repo no longer treats that fixed map as live.

The current bounded compression is empirical:
`C(q) = max(64, ceil(0.5 * log(q)^2))`. Through the direct square-branch audit
at `p <= 10^6`, the repo tested `78,498` prime squares, found `7,477`
violations of the old fixed map, and observed maximum square offset `246`.
The compare mode in the recursive walker is the live falsification instrument:
it runs the bounded and unbounded walkers in lockstep and records any bounded
miss immediately.

See
[benchmarks/python/predictor/square_branch_gap_audit.py](benchmarks/python/predictor/square_branch_gap_audit.py),
[benchmarks/python/predictor/gwr_dni_recursive_walk.py](benchmarks/python/predictor/gwr_dni_recursive_walk.py),
and
[docs/research/predictor/gwr_dni_exact_recursive_prime_walk_note.md](docs/research/predictor/gwr_dni_exact_recursive_prime_walk_note.md).

## No-Later-Simpler-Composite

The strongest closure consequence currently documented in the repository is
this: once the implemented winner appears inside a prime gap, the next prime
arrives before any later interior composite with strictly smaller divisor
count can appear.

This is the closure law behind the exact recursive walk. After the winner
appears, the gap interior does not later produce a simpler composite before
the next prime closes the interval.

In symbols, if $w$ is the implemented log-score winner in the gap $(p, q)$ and

$$
T_{<}(w) = \min \{\, n > w : d(n) < d(w) \,\},
$$

then the closure condition is

$$
q \le T_{<}(w).
$$

This is an exact corollary of the conditionally proven GWR theorem. The separate
question is whether it can stand on its own as a direct prime-gap theorem without
using GWR as the parent result. The current documented surface includes a
deterministic even-band ladder at every decade from $10^8$ through $10^{18}$
with zero observed violations.

See
[gwr/findings/no_later_simpler_composite_theorem.md](gwr/findings/no_later_simpler_composite_theorem.md)
and
[gwr/findings/closure_constraint_findings.md](gwr/findings/closure_constraint_findings.md).

## Dominant d=4 Reduction

In the dominant winner regime, the tested gaps admit no interior prime square,
and the implemented winner is exactly the first interior carrier with
$d(n)=4$.

That gives the leading regime a visible mechanism: square exclusion first,
then first-`d=4` arrival. The stricter semiprime-only slogan is false; a thin
prime-cube exception family survives inside the broader `d=4` class.

See
[gwr/findings/dominant_d4_arrival_reduction_findings.md](gwr/findings/dominant_d4_arrival_reduction_findings.md)
and
[gwr/findings/square_exclusion_first_d4_theorem.md](gwr/findings/square_exclusion_first_d4_theorem.md).

## Deterministic Prefilter Performance

This fixed-point separation is the practical core of the method. Cryptographic prime generation spends most of its time on candidates that are composite and never need a full probable-prime path. The exact DNI provides the invariant target. The production implementation below is the bounded deterministic surrogate calibrated against that target rather than a runtime exact-divisor evaluator.

Because confirmed primes live at $Z = 1.0$ under the DNI and composites contract below it, the prefilter creates a clean structural separation in normalized space. That separation makes it possible to reject many candidates before paying the full cost of the survivor regime.

Empirically, this extracted Python path produced:

- $2.09\times$ end-to-end speedup across $300$ deterministic $2048$-bit RSA keypairs
- $2.82\times$ end-to-end speedup across $50$ deterministic $4096$-bit RSA keypairs
- $90.97\,\%$ to $91.07\,\%$ Miller-Rabin reduction in the current covered-table configuration

Those numbers are not a side note. They are the production consequence of the
same invariant program, carried through a narrow deterministic runtime path
that rejects many doomed candidates before Miller-Rabin.

See [docs/prefilter/benchmarks.md](docs/prefilter/benchmarks.md) and
[technical-note/technical_note.md](technical-note/technical_note.md).

## Production Filter

The exact DNI depends on exact divisor count. That exact path is valuable as
the derivation and as the oracle, but it is not the runtime path for
cryptographic-scale key generation.

The production implementation in this repository therefore uses a deterministic
surrogate with the same invariant target:

- generate deterministic odd candidates from a SHA-256 namespace/index stream
- reject immediately when a concrete factor appears in the gated prime tables
- keep survivors on the locus convention `proxy_z = 1.0`
- run fixed-base Miller-Rabin on survivors
- apply final `sympy.isprime` confirmation in the current Python path

In the production path, `proxy_z = 1.0` means only that the candidate survived
the current gated factor tables and therefore advances to Miller-Rabin. It is
not a primality proof by itself.

The current measured rejection rate comes from the covered prime-table depth of
this implementation. The repository includes deterministic table-depth sweeps
to show that dependence directly rather than attributing the `~91%` figure to
runtime exact DNI evaluation.

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

### DNI Calibration

- $29/29$ calibration primes stayed on $Z = 1.0$
- $0$ composite false fixed points

### Exact Raw Composite Z Field

- This is a separate exact-field concern from the production prefilter.
- Up to $10^6$ on the natural number line, the strongest exact raw composite
  $Z$ value inside a prime gap lands at edge-distance $2$ in $43.6006\%$ of
  gaps versus an exact within-gap baseline of $22.1859\%$, and is carried by a
  $d(n)=4$ composite in $82.9027\%$ of gaps versus a baseline of $20.1401\%$.
- Later repository notes sharpen that ridge picture into the current winner
  theorem: GWR says the implemented log-score winner is the arithmetic choice
  “minimize interior divisor count, then take the leftmost carrier,” and the
  current proof route reduces the remaining earlier-side burden to a finite
  local admissibility closure. The tested surfaces
  remain the finite base, stress surface, and audit record for that proof chain.
- The dedicated closure study then strengthens the right-edge reading further:
  on the current documented even-band ladder through $10^{18}$, once the
  winner appears, no later strictly simpler composite is observed before the
  next prime closes the gap.

See [docs/gap_ridge/raw_composite_z_gap_edge.md](docs/gap_ridge/raw_composite_z_gap_edge.md),
[gwr/findings/gap_winner_rule.md](gwr/findings/gap_winner_rule.md), and
[gwr/findings/no_later_simpler_composite_theorem.md](gwr/findings/no_later_simpler_composite_theorem.md).

See [docs/prefilter/benchmarks.md](docs/prefilter/benchmarks.md) for the curated benchmark summary and [docs/prefilter/manual_validation.md](docs/prefilter/manual_validation.md) for the exact reproduction commands.

## Python API

Install the Python package from the repo root:

```bash
python3 -m pip install -e ./src/python
```
