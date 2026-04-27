# Proof Bridge for the No-Early-Spoiler Condition

This note records the analytic bridge used on the earlier side of the
`Gap Winner Rule` (`GWR`) proof surface.

## Status Note

This note is retained as bridge-era comparison material.

It is not the current public proof-status source of truth for `GWR`, and it is
not the current proof-critical path described in the repo headline files.

For live theorem status, use:

- [`../../../GWR_PROOF.md`](../../../GWR_PROOF.md)
- [`../../../docs/current_headline_results.md`](../../../docs/current_headline_results.md)
- [`../../findings/prime_gap_admissibility_theorem.md`](../../findings/prime_gap_admissibility_theorem.md)

The current explicit picture has two distinct regimes:

- a bounded unconditional bridge from Dusart's explicit prime-gap bound and
  Nicolas-Robin divisor majoration;
- a conditional tail from BHP's fixed exponent $\theta = 0.525$ once an
  explicit leading constant $A$ is supplied.

Its job is:

- restate the exact no-early-spoiler target in one normalized quantity,
- derive a fully non-empirical large-$p$ bridge from gap geometry and divisor
  growth bounds,
- record the explicit certificate showing what is already covered
  unconditionally and what still depends on a provisional tail assumption.

## 1. Reduction Already Established

The ordered dominance theorem is already proved in
[`../../findings/lexicographic_raw_z_dominance_theorem.md`](../../findings/lexicographic_raw_z_dominance_theorem.md):

for composite integers $a < b$, if $d(a) \le d(b)$, then

$$L(a) > L(b).$$

where

$$L(n) = \left(1 - \frac{d(n)}{2}\right)\ln(n).$$

So inside a prime gap, once the leftmost minimum-divisor carrier $w$ appears,
every later candidate is already eliminated.

The earlier side is the bridge target:

for every earlier interior candidate $k < w$ with

$$\delta = d(k) - d_{\min} \ge 1.$$

prove

$$L(k) < L(w).$$

Equivalently,

$$\frac{\ln w}{\ln k} < 1 + \frac{\delta}{d_{\min} - 2}.$$

## 2. Normalized Bridge Load

Define the dimensionless bridge quantity

$$B(k,w) = \frac{\frac{\ln w}{\ln k} - 1}{\frac{\delta}{d_{\min} - 2}}.$$

$$B(k,w) < 1.$$

This is equivalent to $L(k) < L(w)$.

This is the normalized quantity measured directly by
[`asymptotic_bridge_load_scan.py`](./asymptotic_bridge_load_scan.py).

## 3. Deterministic Upper Bound On The Numerator

Let $g(p) = q - p$ denote the prime gap.

For any earlier candidate $k$ and selected integer $w$ in the gap interior,

$$w - k \le g(p).$$

For $x > -1$, use

$$\ln(1 + x) \le x.$$

one has

$$\ln\frac{w}{k} = \ln\left(1 + \frac{w - k}{k}\right) \le \frac{w - k}{k} \le \frac{g(p)}{p+1} < \frac{g(p)}{p}.$$

Because $\ln k > \ln p$, it follows that

$$\frac{\ln w}{\ln k} - 1 = \frac{\ln(w/k)}{\ln k} < \frac{g(p)}{p \ln p}.$$

So the bridge numerator is controlled purely by gap geometry.

## 4. Deterministic Lower Bound On The Denominator

For every earlier candidate,

$$\delta \ge 1.$$

So

$$\frac{\delta}{d_{\min} - 2} \ge \frac{1}{d_{\min} - 2}.$$

Now use the explicit Nicolas-Robin majoration

$$d(n) \le \exp\left(c \frac{\ln n}{\ln\ln n}\right)$$

for all $n \ge 3$, with conservative constant $c = 1.5379$.

Since $w$ lies in the gap interior near $p$, this gives

$$d_{\min} - 2 \le \exp\left(c \frac{\ln p}{\ln\ln p}\right)$$

for all sufficiently large $p$, hence

$$\frac{\delta}{d_{\min} - 2} \ge \exp\left(-c \frac{\ln p}{\ln\ln p}\right).$$

So the bridge denominator is bounded below by a subpolynomial term.

## 5. Conditional Large-$p$ Tail Under Fixed-Exponent Gap Bounds

Combine the numerator and denominator bounds:

$$B(k,w) < \frac{g(p)}{p \ln p} \cdot \exp\left(c \frac{\ln p}{\ln\ln p}\right).$$

Now assume any proved prime-gap upper bound of the form

$$g(p) \le p^\theta$$

for all sufficiently large $p$, with some fixed $\theta < 1$.

Then

$$B(k,w) < p^{\theta - 1} (\ln p)^{-1} \exp\left(c \frac{\ln p}{\ln\ln p}\right) = p^{\theta - 1 + o(1)}.$$

Because $\theta < 1$, the exponent $\theta - 1 + o(1)$ is eventually
negative. Therefore

$$B(k,w) \to 0.$$

as $p \to \infty$.

So there exists an effective threshold $N_{bridge}$ such that for all
prime gaps with left endpoint $p \ge N_{bridge}$,

$$B(k,w) < 1.$$

for every earlier candidate $k$.

This is the large-$p$ tail lemma once a fixed-exponent gap bound with explicit
constants is available.

## 6. Monotone Envelope And Explicit $A$ Budgets

For the conditional bridge envelope

$$E_{\theta,c,A}(p) = A p^{\theta - 1} (\ln p)^{-1}\exp\left(c \frac{\ln p}{\ln\ln p}\right),$$

let $L = \ln p$. Then

$$\frac{d}{dL}\ln E_{\theta,c,A} = \theta - 1 - \frac{1}{L} + \frac{c(\ln L - 1)}{(\ln L)^2}.$$

The factor

$$f(u) = \frac{u - 1}{u^2}$$

has global maximum $1/4$ on $u > 0$, attained at $u = 2$. So for every
$p > e^e$,

$$\frac{d}{dL}\ln E_{\theta,c,A} < \theta - 1 + \frac{c}{4}.$$

Hence a sufficient monotone-tail condition is

$$\theta < 1 - \frac{c}{4}.$$

For the conservative Nicolas-Robin constant $c = 1.5379$, this ceiling is

$$\theta < 0.615525.$$

So BHP's fixed exponent $\theta = 0.525$ lies safely inside the monotone
regime. In that regime the bridge envelope is strictly decreasing for all
$p > e^e$, so the missing large-$p$ step reduces to a one-point budget on the
leading constant:

$$A < A_{\max}(P_0; \theta, c) := P_0^{1-\theta}\ln P_0 \exp\left(-c \frac{\ln P_0}{\ln\ln P_0}\right).$$

If an explicit gap bound $g(p) \le A p^\theta$ is available from some handoff
point $p \ge P_0 > e^e$, then $B(k,w) < 1$ for all larger $p$ whenever
$A < A_{\max}(P_0; \theta, c)$.

For BHP's $\theta = 0.525$, the certificate script now reports these concrete
budgets:

| Handoff point $P_0$ | Conservative $c = 1.5379$ | Theoretical $c = \ln 2 \cdot e^\gamma$ |
|---|---:|---:|
| exact bridge-load base $P_0 = 20{,}000{,}000$ | $A < 5.185946985729438$ | $A < 31.597212393146396$ |
| exact no-spoiler audit $P_0 = 5{,}000{,}000{,}000$ | $A < 14.246224287129907$ | $A < 126.17003339952021$ |
| end of Dusart bridge window $P_0 = 5{,}571{,}362{,}243{,}795$ | $A < 52.627783539395274$ | $A < 733.5315973776145$ |

So the open constant question is narrower than "find some explicit $A$." On
the repo's current proof surface it is enough to supply any explicit
$g(p) \le A p^{0.525}$ theorem with:

- $A < 14.246224287129907$ once the exact no-spoiler audit through
  $p < 5 \cdot 10^9$ is taken as the finite base, or
- $A < 52.627783539395274$ if the handoff is postponed to the conservative
  end of Dusart's unconditional bridge window.

## 7. Explicit Unconditional Bounded Bridge Via Dusart (2018)

Dusart (2018, Proposition 6.8) supplies the strongest explicit unconditional
prime-gap bound currently used in this repo:

$$
g(p) \le \frac{p}{25 (\ln p)^2}, \qquad p \ge 396{,}738.
$$

Substituting into the bridge upper bound gives the explicit envelope

$$
U(p,c) = \frac{1}{25} \cdot
\frac{\exp\left(c \frac{\ln p}{\ln\ln p}\right)}{(\ln p)^3}.
$$

Let $L = \ln p$. Then

$$
\frac{d}{dL}\ln U =
\frac{c(\ln L - 1)}{(\ln L)^2} - \frac{3}{L}.
$$

At the Dusart threshold $p = 396{,}738$, this derivative is already positive
for both constants used in the certificate:

- conservative $c = 1.5379$: derivative `0.13353517567182743`,
- theoretical $c = \ln 2 \cdot e^\gamma$: derivative `0.061290426084355254`.

So the Dusart envelope is increasing from the start of the explicit regime. It
does not furnish an eventual tail. Instead it stays below `1` on a bounded
interval and then crosses the bridge threshold at explicit upper limits:

- conservative $c = 1.5379$:
  $p \le 5{,}571{,}362{,}243{,}795$,
- theoretical $c = \ln 2 \cdot e^\gamma$:
  $p \le 45{,}301{,}724{,}985{,}788{,}829{,}696$.

So Dusart yields a large unconditional bridge window, not a universal tail.

## 8. Explicit Certificate

The explicit certificate artifact is
[`../../../output/gwr_proof/proof_bridge_certificate_2e7.json`](../../../output/gwr_proof/proof_bridge_certificate_2e7.json).

The certificate script records both the provisional BHP tail and the bounded
Dusart coverage. For the BHP form it evaluates

$$B(k,w) < A p^{\theta-1}(\ln p)^{-1}\exp(c\ln p/\ln\ln p).$$

Against BHP's $\theta = 0.525$ with provisional $A = 1$, the evaluated tail
thresholds are:

| Constants | Raw threshold where bridge is below `1` | Relation to finite base |
|---|---:|---|
| $A=1$, $c=\ln(2)e^\gamma$ | `102` | inside $p < 20{,}000{,}001$ |
| $A=1$, $c=1.5379$ | `3,544` | inside $p < 20{,}000{,}001$ |

For Dusart's explicit unconditional bound, the bridge stays below `1` on:

| Constants | Bounded unconditional coverage | Relation to finite base |
|---|---:|---|
| $c=\ln(2)e^\gamma$ | $396{,}738 \le p \le 45{,}301{,}724{,}985{,}788{,}829{,}696$ | fully covers $p < 20{,}000{,}001$ |
| $c=1.5379$ | $396{,}738 \le p \le 5{,}571{,}362{,}243{,}795$ | fully covers $p < 20{,}000{,}001$ |

The exact finite bridge-load base through $p < 20{,}000{,}001$ records:

- `3,349,874` earlier candidates,
- `0` bridge failures,
- maximum realized bridge load `0.05664166714743768`.

So the finite computation overlaps the start of the Dusart regime by a wide
margin and also lies above the provisional $A = 1$ BHP thresholds.

## 9. Current Role Of The Exact Artifacts

The exact artifacts no longer serve only as evidence.

They serve three proof roles:

- they certify the finite base already covered exactly in the repo;
- they overlap the entire beginning of the unconditional Dusart regime;
- they provide the base case below the provisional BHP tail threshold.

The current strongest conclusion is:

- the bridge is closed unconditionally on the concrete interval
  $396{,}738 \le p \le 5.571 \times 10^{12}$ under Dusart and conservative
  Nicolas-Robin constants;
- the bridge has a conditional tail to infinity under BHP's $\theta = 0.525$
  once an explicit leading constant $A$ is supplied.

So the exact finite computation, the unconditional bounded bridge, and the
provisional BHP tail are now separated cleanly rather than merged into one
overstated universal claim.
