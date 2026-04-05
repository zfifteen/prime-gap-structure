# Proof Bridge for the No-Early-Spoiler Condition

This note isolates the remaining analytic bridge needed for a universal proof
of the `Gap Winner Rule` (`GWR`).

It does **not** claim that the full universal theorem is already closed in this
repo. Its job is narrower:

- restate the exact no-early-spoiler target in one normalized quantity,
- derive a fully non-empirical large-$p$ bridge from gap geometry and divisor
  growth bounds,
- and state precisely what finite verification obligation remains.

## 1. Reduction Already Established

The ordered dominance theorem is already proved in
[`../../gwr/findings/lexicographic_raw_z_dominance_theorem.md`](../../gwr/findings/lexicographic_raw_z_dominance_theorem.md):

for composite integers $a < b$, if $d(a) \le d(b)$, then

$$
L(a) > L(b),
$$

where

$$
L(n) = \left(1 - \frac{d(n)}{2}\right)\ln(n).
$$

So inside a prime gap, once the leftmost minimum-divisor carrier $m^*$ appears,
every later candidate is already eliminated.

The only missing universal step is the earlier side:

for every earlier interior candidate $k < m^*$ with

$$
\delta = d(k) - d_{\min} \ge 1,
$$

prove

$$
L(k) < L(m^*).
$$

Equivalently,

$$
\frac{\ln m^*}{\ln k} < 1 + \frac{\delta}{d_{\min} - 2}.
$$

## 2. Normalized Bridge Load

Define the dimensionless bridge load

$$
\operatorname{bridge\_load}(k,m^*)
=
\frac{\frac{\ln m^*}{\ln k} - 1}{\frac{\delta}{d_{\min} - 2}}.
$$

Then the no-early-spoiler condition is exactly

$$
\operatorname{bridge\_load}(k,m^*) < 1.
$$

This is the normalized quantity measured directly by
[`asymptotic_bridge_load_scan.py`](./asymptotic_bridge_load_scan.py).

## 3. Deterministic Upper Bound On The Numerator

Let $g(p) = q - p$ denote the prime gap.

For any earlier candidate $k$ and winner $m^*$ in the gap interior,

$$
m^* - k \le g(p).
$$

Since

$$
\ln\!\left(1 + x\right) \le x \qquad (x > -1),
$$

one has

$$
\ln\frac{m^*}{k}
=
\ln\!\left(1 + \frac{m^* - k}{k}\right)
\le
\frac{m^* - k}{k}
\le
\frac{g(p)}{p+1}
<
\frac{g(p)}{p}.
$$

Because $\ln k > \ln p$, it follows that

$$
\frac{\ln m^*}{\ln k} - 1
=
\frac{\ln(m^*/k)}{\ln k}
<
\frac{g(p)}{p \ln p}.
$$

So the bridge numerator is controlled purely by gap geometry.

## 4. Deterministic Lower Bound On The Denominator

For every earlier candidate,

$$
\delta \ge 1.
$$

So

$$
\frac{\delta}{d_{\min} - 2}
\ge
\frac{1}{d_{\min} - 2}.
$$

Now use any explicit maximal-order upper bound for the divisor function, for
example a Nicolas-Robin style majoration of the form

$$
d(n)
\le
\exp\!\left(
c \frac{\ln n}{\ln\ln n}
\right)
$$

for all sufficiently large $n$, with an effective absolute constant $c > 0$.

Since $m^*$ lies in the gap interior near $p$, this gives

$$
d_{\min} - 2
\le
\exp\!\left(
c \frac{\ln p}{\ln\ln p}
\right)
$$

for all sufficiently large $p$, hence

$$
\frac{\delta}{d_{\min} - 2}
\ge
\exp\!\left(
-c \frac{\ln p}{\ln\ln p}
\right).
$$

So the bridge denominator is bounded below by a subpolynomial term.

## 5. Universal Large-$p$ Bridge

Combine the numerator and denominator bounds:

$$
\operatorname{bridge\_load}(k,m^*)
<
\frac{g(p)}{p \ln p}
\cdot
\exp\!\left(
c \frac{\ln p}{\ln\ln p}
\right).
$$

Now assume any proved prime-gap upper bound of the form

$$
g(p) \le p^\theta
$$

for all sufficiently large $p$, with some fixed $\theta < 1$.

Then

$$
\operatorname{bridge\_load}(k,m^*)
<
p^{\theta - 1}
(\ln p)^{-1}
\exp\!\left(
c \frac{\ln p}{\ln\ln p}
\right)
=
p^{\theta - 1 + o(1)}.
$$

Because $\theta < 1$, the exponent $\theta - 1 + o(1)$ is eventually
negative. Therefore

$$
\operatorname{bridge\_load}(k,m^*) \to 0
\qquad\text{as } p \to \infty.
$$

So there exists an effective threshold $N_{\mathrm{bridge}}$ such that for all
prime gaps with left endpoint $p \ge N_{\mathrm{bridge}}$,

$$
\operatorname{bridge\_load}(k,m^*) < 1
$$

for every earlier candidate $k$.

This is the universal large-$p$ lemma.

## 6. What Remains To Close The Universal Theorem

This note does **not** by itself finish the theorem in repo-proof form.

To close the universal statement of `GWR`, two concrete tasks remain:

1. choose explicit literature constants for
   - one effective divisor-function majoration, and
   - one effective prime-gap upper bound with exponent $\theta < 1$;
2. compute an explicit numerical threshold $N_{\mathrm{bridge}}$ and verify
   every gap up to that threshold.

The current repo already supplies exact finite verification through
$2 \cdot 10^7$ via the committed no-early-spoiler artifacts. If the explicit
bridge threshold comes out below that bound, the universal theorem closes
immediately. If it comes out above, the remaining work is a finite deterministic
extension of the exact scan up to that threshold.

## 7. Current Role Of The Exact Artifacts

The exact artifacts do not replace the bridge proof.

They serve two narrower roles:

- they certify the finite base already covered exactly in the repo,
- and they identify the right normalized quantity for the remaining large-$p$
  argument.

That is enough to make the remaining gap precise:

the universal theorem is reduced to one explicit-constant bridge computation
plus finite verification up to the resulting threshold.
