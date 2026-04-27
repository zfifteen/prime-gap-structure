# Explicit-A Bridge Completion Task

## Status

This is an open analytic bridge task.

The current Gap Winner Rule proof surface is closed by the local-dominator,
local-admissibility, residual-closure, and exact-audit route documented in:

- [`../../../GWR_PROOF.md`](../../../GWR_PROOF.md)
- [`../../../docs/current_headline_results.md`](../../../docs/current_headline_results.md)

The normalized bridge path remains comparison material in
[`./proof_bridge_universal_lemma.md`](./proof_bridge_universal_lemma.md). It
would become a fully analytic alternative route if one explicit external
prime-gap theorem supplies the missing tail bound below.

## Target Theorem

Find or extract from the literature an unconditional explicit bound

$$g(p) \le A p^{0.525}$$

for every prime $p \ge x_0$, with

$$x_0 \le 5 \cdot 10^9$$

and

$$A < 14.246224287129907.$$

Here $g(p)$ is the next-prime gap after $p$. The constant budget is the
conservative bridge budget after the exact no-early-counterexample audit base
$P_0 = 5 \cdot 10^9$.

If the handoff is postponed to the conservative end of the Dusart bridge
window,

$$P_0 = 5{,}571{,}362{,}243{,}795,$$

then the budget relaxes to

$$A < 52.627783539395274.$$

## Bridge Budget

The bridge note gives the monotone envelope

$$E_{\theta,c,A}(p) = A p^{\theta - 1}(\ln p)^{-1}\exp\left(c\frac{\ln p}{\ln\ln p}\right),$$

with $\theta = 0.525$ and conservative Nicolas-Robin constant $c = 1.5379$.
For $p > e^e$, this envelope is decreasing because

$$\theta < 1 - \frac{c}{4}.$$

So the whole tail reduces to the one-point budget

$$A < A_{\max}(P_0;\theta,c) = P_0^{1-\theta}\ln P_0\exp\left(-c\frac{\ln P_0}{\ln\ln P_0}\right).$$

At the exact audit base,

$$A_{\max}(5 \cdot 10^9;0.525,1.5379) = 14.246224287129907.$$

Thus any explicit theorem with $A$ below that value gives

$$B(k,w) < 1$$

for every earlier-side bridge comparison in the asymptotic tail.

## Present Obstruction

Baker-Harman-Pintz supplies the exponent $\theta = 0.525$ and a leading scale
that would correspond to $A = 1$, but the published theorem is stated for
sufficiently large $x$ and does not provide a public numerical $x_0$ at or
below $5 \cdot 10^9$.

The missing ingredient is not a smaller numerical coefficient. It is a fully
effective threshold for a $\theta = 0.525$ prime-gap theorem, or a different
explicit theorem with coefficient below the bridge budget from one of the
accepted handoff points.

## Success Criteria

A completed bridge result must provide:

1. an unconditional explicit theorem of the form
   $$g(p) \le A p^{0.525}$$
   with a numerical $A$ and numerical threshold $x_0$;
2. $A < 14.246224287129907$ with $x_0 \le 5 \cdot 10^9$, or else
   $A < 52.627783539395274$ with
   $x_0 \le 5{,}571{,}362{,}243{,}795$;
3. a direct substitution into the bridge envelope above showing
   $E_{0.525,1.5379,A}(P_0) < 1$;
4. a short citation chain or proof note that can be audited independently;
5. no change to the live GWR proof status unless the explicit theorem is
   actually supplied.

## Scope

This task does not alter the current GWR proof surface. It does not rework the
hierarchical local-dominator theorem, lexicographic raw-$Z$ dominance,
earlier-side local admissibility, residual-class closure, or exact
no-early-counterexample audit.

The only target is the external analytic prime-gap input needed to turn the
retained normalized bridge into a uniform analytic alternative proof.

## Candidate Literature

Primary sources to inspect:

- Baker-Harman-Pintz, "The difference between consecutive primes, II".
- Effective or computer-assisted versions of the Baker-Harman-Pintz sieve.
- Runbo Li, arXiv:2308.04458.
- Visser, arXiv:2508.18786.
- Public discussion of explicit Baker-Harman-Pintz thresholds.

## Submission Form

A useful submission can be any one of:

- a self-contained LaTeX note;
- a GitHub Markdown note in this directory;
- a pull request updating the bridge note after the explicit theorem is
  supplied;
- a verification script that evaluates the bridge envelope at the stated
  handoff.

The preferred issue or pull-request subject is:

```text
[Bridge] Explicit A for theta = 0.525
```
