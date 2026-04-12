# GWR_PROOF.md

## Gap Winner Rule: Proof Status Summary

This document assembles the four-component proof chain for the
**Gap Winner Rule (GWR)**. Every claim points to a committed artifact.
Nothing here is new reasoning; it is the assembly of what is already in
the repo.

---

## Theorem Statement

Let \(p < q\) be consecutive primes with composite interior
\(I = \{p+1, \ldots, q-1\}\). Define

$$
\delta_{\min}(p,q) := \min_{n \in I} d(n), \qquad
w := \min\{n \in I : d(n) = \delta_{\min}(p,q)\}.
$$

Then \(w\) is the unique maximizer of the log-score

$$
L(n) = \left(1 - \frac{d(n)}{2}\right)\ln(n)
$$

over the entire gap interior \(I\).

Source:
[`gwr/findings/gwr_hierarchical_local_dominator_theorem.md`](gwr/findings/gwr_hierarchical_local_dominator_theorem.md)

---

## Component 1: Later Side (Closed)

**Claim.** Every composite \(m \in I\) with \(m > w\) satisfies
\(L(m) < L(w)\).

**Proof.** By definition of \(w\), every later candidate \(m > w\) satisfies
\(d(m) \ge d(w) = \delta_{\min}\). Since \(w < m\), the
**Lexicographic Raw-Z Dominance Theorem** applies directly: for composite
integers \(a < b\) with \(d(a) \le d(b)\), one has \(L(a) > L(b)\). Setting
\(a = w\) and \(b = m\) gives \(L(w) > L(m)\).

The dominance theorem proof is fully elementary (two monotonicity steps,
no appeal to number theory). Status: **closed**.

Source:
[`gwr/findings/lexicographic_raw_z_dominance_theorem.md`](gwr/findings/lexicographic_raw_z_dominance_theorem.md)

---

## Component 2: Earlier Side, Analytic Bridge (Large p)

**Claim.** For every earlier composite \(k < w\) in the gap interior,
\(L(k) < L(w)\) holds under explicit prime-gap bounds that make the
dimensionless bridge quantity \(B(k,w) < 1\).

**Reduction.** The condition \(L(k) < L(w)\) is equivalent to

$$
B(k,w) = \frac{\dfrac{\ln w}{\ln k} - 1}{\dfrac{\delta}{d_{\min} - 2}} < 1,
\qquad \delta = d(k) - d_{\min} \ge 1.
$$

**Numerator bound.** Gap geometry and \(\ln(1+x) \le x\) give

$$
\frac{\ln w}{\ln k} - 1 < \frac{g(p)}{p \ln p}.
$$

**Denominator bound.** Nicolas-Robin (1983) explicit majoration, valid for
all \(n \ge 3\), with conservative constant \(c = 1.5379\) yields

$$
d_{\min} - 2 \le \exp\!\left(c \frac{\ln p}{\ln\ln p}\right)
\implies \frac{\delta}{d_{\min} - 2} \ge
\exp\!\left(-c \frac{\ln p}{\ln\ln p}\right).
$$

**Explicit unconditional case (Dusart 2018).** For \(p \ge 396{,}738\),

$$
g(p) \le \frac{p}{25 (\ln p)^2}.
$$

The resulting upper envelope is

$$
U(p,c) = \frac{1}{25} \cdot
\frac{\exp\!\left(c \frac{\ln p}{\ln\ln p}\right)}{(\ln p)^3}.
$$

With the conservative \(c = 1.5379\), this envelope stays strictly below `1`
on the bounded interval

$$
396{,}738 \le p \le 5{,}571{,}362{,}243{,}795.
$$

The envelope is monotonically increasing in this regime and crosses `1` at the
stated upper limit.

**Conditional asymptotic case (BHP).** Under Baker-Harman-Pintz (2001)
\(\theta = 0.525\) with leading constant \(A\),

$$
B(k,w) < A \cdot p^{-0.475} \cdot (\ln p)^{-1}
\cdot \exp\!\left(c \frac{\ln p}{\ln\ln p}\right)
= A \cdot p^{-0.475 + o(1)} \to 0.
$$

So the BHP bridge still gives an eventual tail once an explicit \(A\) is
supplied. The current headline certificate records the provisional \(A = 1\)
tail, but BHP itself does not state an explicit leading constant.

Source:
[`gwr/experiments/proof/proof_bridge_universal_lemma.md`](gwr/experiments/proof/proof_bridge_universal_lemma.md)

---

## Component 3: Earlier Side, Finite Base (Exact Scan)

**Claim.** For every prime gap with left endpoint \(p < 1{,}000{,}000{,}001\),
no earlier composite \(k < w\) satisfies \(L(k) \ge L(w)\).

**Evidence.** The committed parallel no-early-spoiler scan verified:

- **42,101,885** prime gaps examined
- **149,214,917** earlier candidates checked
- **0** exact spoilers
- **0** bridge failures
- maximum realized bridge load **3.749140087272451e-08**

Artifact:
`output/gwr_proof/parallel_no_early_spoiler_1e9.json`

Script:
[`gwr/experiments/proof/parallel_no_early_spoiler_scan.py`](gwr/experiments/proof/parallel_no_early_spoiler_scan.py)

---

## Component 4: Certificate Computation

**Claim.** The certificate records two analytic bridge regimes: a bounded
unconditional Dusart interval and a provisional BHP tail under explicit
\(A\)-assumptions.

**Computation** (recorded in
[`output/gwr_proof/proof_bridge_certificate_2e7.json`](output/gwr_proof/proof_bridge_certificate_2e7.json)
and executed against
[`gwr/experiments/proof/proof_bridge_certificate.py`](gwr/experiments/proof/proof_bridge_certificate.py)):

| Gap bound | Constants | Regime | Coverage | Status |
|---|---|---|---|---|
| BHP (\(\theta = 0.525\)) | \(A = 1\), \(c = 1.2345\) (theo) | asymptotic | \(p \ge 102\) | conditional on explicit \(A\) |
| BHP (\(\theta = 0.525\)) | \(A = 1\), \(c = 1.5379\) (cons) | asymptotic | \(p \ge 3{,}544\) | conditional on explicit \(A\) |
| Dusart (2018) | \(c = 1.5379\) | explicit unconditional | \(396{,}738 \le p \le 5.571 \times 10^{12}\) | unconditional (bounded) |

The exact finite bridge-load base through \(p < 1{,}000{,}000{,}001\) records:

- `149,214,917` earlier candidates,
- `0` bridge failures,
- maximum realized bridge load `3.749140087272451e-08`.

So the finite scan overlaps the entire start of the Dusart regime by a much
larger margin and lies far above the provisional \(A = 1\) BHP thresholds.

---

## Current Strongest Claim (Unconditional To \(p < 10^9\) + Bounded Dusart Tail To \(5.571 \times 10^{12}\) + Conditional Asymptotic Tail)

- For \(p < 1{,}000{,}000{,}001\): Component 3 (exact parallel scan,
  `42,101,885` gaps, `149,214,917` earlier candidates, `0` failures),
  unconditional.
- For \(1{,}000{,}000{,}001 \le p \le 5.571 \times 10^{12}\): Component 2 under
  Dusart (2018) and Nicolas-Robin (1983), unconditional and bounded.
- For \(p > 5.571 \times 10^{12}\): Component 2 under BHP
  \((\theta = 0.525)\) with provisional \(A = 1\), conditional.

The two unconditional regimes overlap with a large margin. So the Gap Winner
Rule holds unconditionally for all prime gaps with left endpoint
\(p \le 5.571 \times 10^{12}\). Full universality to infinity still depends on
an explicit leading constant for a fixed-exponent gap bound such as effective
BHP.

---

## References

| Item | Source |
|---|---|
| GWR theorem statement | [`gwr/findings/gwr_hierarchical_local_dominator_theorem.md`](gwr/findings/gwr_hierarchical_local_dominator_theorem.md) |
| Dominance theorem (later side) | [`gwr/findings/lexicographic_raw_z_dominance_theorem.md`](gwr/findings/lexicographic_raw_z_dominance_theorem.md) |
| Bridge lemma (earlier side) | [`gwr/experiments/proof/proof_bridge_universal_lemma.md`](gwr/experiments/proof/proof_bridge_universal_lemma.md) |
| Finite no-early-spoiler artifact | `output/gwr_proof/parallel_no_early_spoiler_1e9.json` |
| Bridge-load finite base | `output/gwr_proof/parallel_no_early_spoiler_1e9.json` |
| Certificate artifact | `output/gwr_proof/proof_bridge_certificate_2e7.json` |
| Certificate script | [`gwr/experiments/proof/proof_bridge_certificate.py`](gwr/experiments/proof/proof_bridge_certificate.py) |
| BHP prime-gap bound | Baker, Harman, Pintz (2001). *Proc. London Math. Soc.* 83(3), 532-562 |
| Dusart explicit gap bound | Dusart (2010/2018), Proposition 6.8: \(x < p \le x(1 + 1/(25\ln^2 x))\) for \(x \ge 396{,}738\) |
| Nicolas-Robin divisor majoration | Nicolas, Robin (1983). *Canad. Math. Bull.* 26(4), 485-492 |
