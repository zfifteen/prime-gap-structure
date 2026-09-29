# Dual endpoint pin of the min-tau level set

## Executive summary

**Hypothesis (not theorem):** when the min-\(\tau\) level set inside a prime gap has size at least 2, it is **dual-pinned**: the first floor hit is left-compressed near \(p\) (proved GWR + \(C(q)\)), and the last floor hit sits near \(q\) with **small right clearance** \(q - w_R\), so multi-tie gaps form a **bridge** of the floor class across the interior.

This insight was produced by a Novel Insight Engine pass on the live codebase **after** residual-mean elevation was falsified. It deliberately replaces a killed mean-\(\tau\) story with **geometry of floor-class locations**.

| Layer | Status |
| --- | --- |
| Left pin \(w - p \le C(q)\) | **theorem** |
| Right pin (multi-tie clearance tight) | **hypothesis** |
| Session mid-scale pressure | **measured on regime only** (\(q \le 2e6\); max multi clearance 22) |
| Residual-mean elevation after Gap Winner | **falsified** (separate package) |
| Program verified / validated | **not claimed** |

Full prose: [INSIGHT_REPORT.md](INSIGHT_REPORT.md) · formal claims: [HYPOTHESIS.md](HYPOTHESIS.md)

---

## Why this is not the residual-mean valve

| Valve claim (killed) | Dual pin claim |
| --- | --- |
| Residual mean \(\tau\) > pre-valve mean \(\tau\) | Last floor hit near \(q\) when \(\lvert L\rvert \ge 2\) |
| Distributional averages | Locations of co-minimals |
| Universal both-sided means | Multi-tie only |

---

## Why this is not only LSCD

| LSCD (existing package) | Dual pin (this package) |
| --- | --- |
| Asks whether \(w_R - p > C(q)\) (left spill) | Asks whether \(q - w_R\) stays small (right clearance) |
| Spill can be true while dual pin holds | Both can hold: \(L\) spills past left \(C\) yet ends near \(q\) |

LSC package: `experiments/min-tau-level-set-compression-2026-07/`

---

## Package contents

| Path | Role |
| --- | --- |
| `README.md` | This entry |
| `HYPOTHESIS.md` | Formal H-DEP, P1–P3, decision rule, non-claims |
| `INSIGHT_REPORT.md` | Full NIE Parts 1–4, audit, session pressure numbers |

No probe script is committed in this documentation PR. Next step is an optional committed falsification runner for P1–P3.

---

## Registered falsifiers (for a future probe)

1. **P1:** multi-tie clearance \(> 32\) with \(q \le 2e6\).
2. **P2:** multi-tie clearance \(> \max(32, \lfloor 0.25\cdot C(q)\rfloor)\) with \(q \le 1e7\).
3. **P3:** multi-tie median clearance climbs linearly with gap length for \(g \ge 20\).

---

## Exact limits

- Insight documentation only in this PR.
- Session pressure is not a committed \(10^{18}\) surface and does not support verified/validated language.
- Theorems in `PROOF.md` are not demoted.
