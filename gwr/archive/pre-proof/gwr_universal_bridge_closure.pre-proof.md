# GWR Universal Bridge Closure

This note records the current headline proof result for the `Gap Winner Rule`
(`GWR`): the no-early-spoiler bridge closes below the repo's exact verified
finite base under explicit literature constants.

## Finding

The strongest supported claim is:

`GWR` holds universally for all prime gaps, conditional on the Baker-Harman-Pintz
prime-gap exponent $\theta = 0.525$ and an explicit Robin-style divisor-function
majoration.

The proof has two parts:

1. the exact finite base verifies every relevant gap below
   $p < 20{,}000{,}001$;
2. the analytic bridge bound falls below the spoiler threshold before that
   finite base ends.

So there is no unverified interval between the exact computation and the
large-$p$ argument under the stated constants.

## Analytic Bridge

For an earlier interior candidate $k$ and the true `GWR` carrier $w$, define

$$B(k,w)=\frac{\frac{\ln w}{\ln k}-1}{\frac{\delta}{d_{\min}-2}}.$$

The no-early-spoiler condition is exactly

$$B(k,w)<1.$$

The large-$p$ proof bridge bounds this load by

$$B(k,w) < A p^{\theta-1}(\ln p)^{-1}\exp(c\ln p/\ln\ln p).$$

With BHP's $\theta = 0.525$:

| Constants | Raw threshold where bridge is below `1` | Relation to finite base |
|---|---:|---|
| $A=1$, $c=\ln(2)e^\gamma$ | `102` | inside $p < 20{,}000{,}001$ |
| $A=1$, $c=1.5379$ | `3,544` | inside $p < 20{,}000{,}001$ |
| $A=10$, $c=\ln(2)e^\gamma$ | `220,725` | inside $p < 20{,}000{,}001$ |
| $A=10$, $c=1.5379$ | `727,330,778` | outside current finite base |

The headline closure uses $A=1$. The $A=10$ robustness variant closes under
Robin's $c=\ln(2)e^\gamma$ constant, but not under the conservative
$c=1.5379$ constant with the current $2 \cdot 10^7$ finite base.

## Exact Finite Base

The committed no-early-spoiler bridge artifact through
$p < 20{,}000{,}001$ records:

- `1,163,198` prime gaps with composite interior,
- `3,349,874` earlier candidates before the true `GWR` carrier,
- `0` bridge failures,
- maximum realized bridge load `0.05664166714743768`.

The executed finite artifact is
[asymptotic_bridge_load_scan_2e7.json](../../output/gwr_proof/asymptotic_bridge_load_scan_2e7.json).

The certificate helper is
[proof_bridge_certificate.py](../experiments/proof/proof_bridge_certificate.py).

## Consequence

The finite scan is no longer only evidence for `GWR`. It is the base case for
the analytic closure.

The ordered dominance theorem eliminates every later candidate after the
leftmost minimum-divisor carrier. The bridge load eliminates every earlier
higher-divisor candidate before that carrier. Together with the exact finite
base and the explicit large-$p$ constants, the prime-selected interior integer law closes
under the stated assumptions.
