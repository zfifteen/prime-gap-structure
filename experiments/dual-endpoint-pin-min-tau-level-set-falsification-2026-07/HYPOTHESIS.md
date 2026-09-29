# Hypothesis under falsification: Dual right-pin of multi-tie min-tau level sets

## Source insight

`experiments/dual-endpoint-pin-min-tau-level-set-2026-07/` (NIE documentation; PR #64 line).

Core claim: when the min-\(\tau\) level set \(L\) has size \(\ge 2\), the rightmost co-minimal \(w_R\) is tightly pinned near \(q\) (small clearance \(q - w_R\)), dual to the proved left pin of \(w = \min L\).

## PGS frame

```text
gap (p, q) -> tau field -> L = argmin level set
  -> w = min L, w_R = max L
  -> clearance = q - w_R
  -> multi-tie only (|L| >= 2)
```

## Registered claims (from insight package)

| ID | Statement | Hard falsifier |
| --- | --- | --- |
| **P1** | Multi-tie clearance \(\le 32\) for all consecutive gaps with \(p \ge 11\) and \(q \le 2\cdot 10^6\) (equivalently left primes through the \(2e6\) regime used in the insight pressure). | Any multi-tie row with clearance \(> 32\) in that regime. |
| **P2** | Multi-tie clearance \(\le \max(32, \lfloor 0.25\cdot C(q)\rfloor)\) for gaps with left prime \(p \le 10^7\). | Any multi-tie row exceeding that bound. |
| **P3** | Among multi-tie gaps with \(g \ge 20\), median clearance \(\le 8\) and does not grow linearly with \(g\) (bins of width 10, \(n \ge 100\)). | Median \(> 8\) on those bins, or clear linear climb of median vs \(g\)-bin. |

\(C(q) = \max(64, \lceil 0.5 \log(q)^2 \rceil)\).

## Non-claims

- Left pin \(w - p \le C(q)\): **theorem** (`PROOF.md`).
- Residual-mean elevation: **already falsified** (valve package).
- Dual pin as high-probability tendency: separate soft reading; not the hard rule under test.
- Program verified / validated language: **forbidden** without executed \(10^{18}\) surface.

## Outcome language

| Word | When |
| --- | --- |
| **falsified** | Hard P1/P2/P3 criterion fails on the stated regime |
| **holds on regime** | Zero hits on that criterion and regime |
| **measured only** | Always pair with exact \(p_{\max}\) / counts |
