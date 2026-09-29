# Hypothesis under falsification: Unique Floor Dichotomy

## Source insight

Novel Insight Engine session (2026-07-25): *Unique Floor Dichotomy*.

Core claim: if the min-\(\tau\) level set inside a prime gap is a singleton, that unique floor hit can sit in a long gap only when it is a prime square (\(\tau=3\)). Unique semiprime floors (\(\tau=4\)) and higher unique floors force short gaps. Long non-square corridors are multi-tie.

## PGS frame

```text
gap (p, q) -> tau field on interior
  -> m = min tau, L = level set of m
  -> w = min L (GWR)
  -> uniqueness |L| = 1 vs multi-tie |L| >= 2
  -> branch by m (3 square / 4 semiprime / >=8 high)
  -> gap length g = q - p
```

## Registered claims

| ID | Statement | Hard falsifier |
| --- | --- | --- |
| **U1** | On \(11 \le p \le p_{\max}\), if \(\lvert L\rvert=1\) and \(m=4\), then \(g \le G_4(p_{\max})\). | Any unique \(m=4\) row with \(g > G_4\). |
| **U2** | On the same regime, among gaps with \(g \ge 20\) and \(m=4\), multi-tie rate \(\lvert L\rvert\ge 2\) is \(\ge 0.99\). | Multi-tie rate \(< 0.99\) on that set (with \(n \ge 1000\)). |
| **U3** | On the same regime, if \(\lvert L\rvert=1\) and \(m \ge 8\), then \(g \le 16\). | Any unique \(m\ge 8\) row with \(g > 16\). |
| **U4** | Contrast arm (must remain true for the dichotomy): unique \(m=3\) may have \(g > 40\) on mid-scale regimes. | Failure of U4 does not falsify U1–U3; it weakens the “square is the long-unique exception” story. Report only. |

### Bound schedule for U1

| Surface | \(G_4\) (hard ceiling under test) |
| --- | --- |
| Consecutive \(p_{\max}\le 5\cdot 10^6\) | 40 |
| Consecutive \(p_{\max}=10^7\) | \(\max(48, \lfloor 0.5\cdot C(q)\rfloor)\) per row |
| Decade ladder \(10^8..10^{18}\) | \(\max(48, \lfloor 0.5\cdot C(q)\rfloor)\) per row |

### High-scale U3 ceiling (ladder)

Unique \(m\ge 8\): \(g \le \max(16, \lfloor 0.15\cdot C(q)\rfloor)\).

### Mandatory high-scale surface

Program-style decade ladder: **256 consecutive primes per decade**, decades **\(10^8\) through \(10^{18}\)** (11 anchors). This is the package’s executed \(10^{18}\) surface for U1–U4 pressure. It is a sampled ladder, not a full consecutive scan of all primes to \(10^{18}\).

\(C(q)=\max(64,\lceil 0.5\log(q)^2\rceil)\).

## Non-claims

- GWR / NLS / left compression: **theorem** (`PROOF.md`).
- Residual-mean elevation: **already falsified**.
- Dual right-pin as universal rule: **already falsified**.
- Program verified / validated: **forbidden** without executed \(10^{18}\) surface.

## Outcome language

| Word | When |
| --- | --- |
| **falsified** | Hard U1/U2/U3 fails on a stated regime |
| **holds on regime** | Zero hard hits; rates meet thresholds |
| **measured only** | Always with exact \(p_{\max}\) |
