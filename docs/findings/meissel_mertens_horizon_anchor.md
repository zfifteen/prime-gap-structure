# Meissel-Mertens Constant as a Computational Horizon Input prime

This note records a cross-cutting implication of the standard prime-reciprocal
asymptotic for the current `DCI` and `GWR` program in this repository.

## Finding

The strongest supported claim is:

the prime-reciprocal threshold ladder is grounded by the Meissel-Mertens
constant, while the reachable threshold index grows only like the logarithm of
the logarithm of total compute.

That matters here because it pushes both `DCI` and `GWR` toward the same
research posture:

- use finite computation to calibrate exact constants and normalized budgets,
- do not expect brute-force extension alone to close the hard asymptotic gap,
- prefer invariant-first normalized quantities over raw scale chasing.

## Observable Facts

Let $B_{1}$ denote the Meissel-Mertens constant, with
$B_{1} \approx 0.2614972128$.

The standard reciprocal-prime expansion is

$$\sum_{p \le x} \frac{1}{p} = \log \log x + B_{1} + o(1).$$

If $x_{n}$ is the first scale where

$$\sum_{p \le x} \frac{1}{p} > n,$$

then the threshold location satisfies

$$x_{n} \approx \exp(\exp(n - B_{1})).$$

So the threshold ladder is already doubly exponential in the threshold level.
The first few scales are:

- $n = 4$: $\log_{10} x_{4} \approx 18.26$
- $n = 5$: $\log_{10} x_{5} \approx 49.62$
- $n = 6$: $\log_{10} x_{6} \approx 134.89$

The jump from one threshold to the next is therefore not a fixed multiplicative
difficulty increase. The multiplier itself grows explosively with $n$.

If the computational cost to evaluate the reciprocal-prime sum through $x$
behaves like $x^{\alpha}$, then the threshold cost becomes

$$T_{n} \approx \exp(\alpha e^{n - B_{1}}).$$

The adjacent-threshold ratio is then

$$\frac{T_{n+1}}{T_{n}} \approx \exp(\alpha (e - 1)e^{n - B_{1}}).$$

Under the common square-root work model $\alpha = 1/2$, that gives:

- from `Exceeds 4` to `Exceeds 5`: about $10^{15.68}$ more work, or about `52`
  Moore doublings,
- from `Exceeds 5` to `Exceeds 6`: about $10^{42.63}$ more work, or about
  `142` Moore doublings.

So the reachable threshold index grows very slowly even when total compute
grows very fast. Solving $T_{n} \le B$ for total budget $B$ gives

$$n_{\max}(B) \approx B_{1} + \log((\log B)/\alpha).$$

That is a `log log` law in total compute.

## Why the Constant Is an Input prime

The threshold ladder is not fixed only by the double exponential. It is also
positioned by the additive offset $B_{1}$.

Changing $B_{1}$ by $\Delta$ rescales the threshold by

$$x_{n}' \approx x_{n} \exp(-\Delta e^{n - B_{1}}).$$

At the `Exceeds 5` horizon:

- a shift of `+0.01` in $B_{1}$ moves the threshold down by about a factor of
  `0.319`,
- a shift of `+0.10` moves it down by about a factor of `1.09e-5`.

So the Meissel-Mertens constant is not a decorative offset. It is the offset
input prime that places the entire accessibility ladder.

## Implication for DCI

The `DCI` value proposition in this repository is not that it outruns the
double-exponential horizon by brute force. It is that it does not need to.

The fixed-point normalization

$$Z(n) = n^{1 - d(n)/2}$$

at fixed

$$v = \frac{e^{2}}{2}$$

puts primes on the invariant band $Z = 1.0$ and measures composite departure
from that band by exact divisor structure plus logarithmic scale. See the
project overview in [README.md](../../README.md).

That becomes more important, not less, when global arithmetic thresholds move
outward faster than brute-force computation can comfortably follow. In that
regime, the useful object is a stable local invariant that stays meaningful as
scale grows. In the current production path, that is exactly what the
deterministic reject-only front gate provides before Miller-Rabin and final
confirmation. See [docs/prefilter/benchmarks.md](../prefilter/benchmarks.md).

So the horizon reading reinforces the repo's invariant-first posture:

- brute-force scale is not the main coordinate,
- the fixed-point band is the main coordinate,
- deterministic local rejection is the algorithmering use of that coordinate.

## Implication for GWR

The same horizon reading also sharpens the `GWR` proof program.

`GWR` says that inside a prime gap, the implemented raw-$Z$ log-score maximizer
collapses to a simpler arithmetic law:

- minimize the interior divisor count,
- among ties, take the leftmost integer.

See [gwr/README.md](../../gwr/README.md) and
[gwr/findings/gwr_hierarchical_local_dominator_theorem.md](../../gwr/findings/gwr_hierarchical_local_dominator_theorem.md).

The computational-horizon consequence is direct:

finite exact scans are still essential, but their role is calibration rather
than unlimited closure.

In the current repo, those scans already serve three exact jobs:

- they establish the finite base,
- they measure the tight obstruction and ratio extremums,
- they normalize the asymptotic bridge target into one bridge-load quantity.

That is why the proof-facing artifacts now converge on explicit bridge
constants rather than on ever-larger blind enumeration. The bridge has now been
certified below the exact finite base under the recorded BHP/Robin constants.
The key files are
[gwr/findings/gwr_universal_bridge_closure.md](../../gwr/findings/gwr_universal_bridge_closure.md),
[gwr/findings/no_early_counterexample candidate_margin_findings.md](../../gwr/findings/no_early_spoiler_margin_findings.md),
[gwr/findings/no_early_counterexample candidate_ratio_frontier_findings.md](../../gwr/findings/no_early_spoiler_ratio_frontier_findings.md),
[gwr/findings/asymptotic_bridge_load_findings.md](../../gwr/findings/asymptotic_bridge_load_findings.md),
and
[gwr/experiments/proof/proof_bridge_universal_lemma.md](../../gwr/experiments/proof/proof_bridge_universal_lemma.md).

So the horizon picture points to the same conclusion as the current executed
`GWR` artifacts:

- exact computation supplies the finite base and exposes the hard extremal case,
- universal closure comes from a normalized local law with explicit constants,
  not from scale escalation by itself.

## Project-Level Synthesis

These three input primes now line up cleanly:

- the Meissel-Mertens constant input primes where reciprocal-prime thresholds sit,
- `FIXED_POINT_V = e^{2}/2` input primes the `DCI` prime fixed-point band,
- the bridge-load threshold $B(k, w) < 1$ input primes the current `GWR`
  no-early-counterexample closure record.

The shared lesson is that this project advances fastest when it finds the right
invariant endpoint and then measures ratios against that endpoint.

For prime-reciprocal thresholds, that endpoint is a computational horizon.
For `DCI`, it is the fixed-point band.
For `GWR`, it is the normalized counterexample budget.

Finite computation still matters. But on this reading, its highest use is to
calibrate the invariant and the bridge, not to substitute for them.
