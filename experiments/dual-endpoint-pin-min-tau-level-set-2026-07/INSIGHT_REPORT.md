# Insight report: Dual Endpoint Pin of the Min-Tau Level Set

**Status:** prompt-derived research insight + formalized hypothesis. **Not a theorem.**  
**Engine:** Novel Insight Engine against live `prime-gap-structure` codebase (post residual-mean falsification).  
**Date context:** 2026-07-24 / 2026-07-25 session documentation.

---

## Phase 0 (lock-in)

**Domain:** Prime Gap Structure: ordered gaps \((p,q)\), divisor field \(\tau\), GWR leftmost min-\(\tau\) witness \(w\), co-minimal level set \(L\), proved left compression \(w-p \le C(q)\), NLS, residual geometry after the killed residual-mean elevation claim.

**In scope:** multi-tie co-minimal geometry (left first vs right last of \(L\)), mid-scale measured structure, falsifiable dual-pin claims.

**Out of scope:** residual-mean elevation (falsified 2026-07-24); theorem promotion; RSA residual cells; classical primality as inference.

**Cheap mid-scale pressure (local session scan, not program validation):** on gaps with \(p \ge 11\), \(q \le 2\cdot 10^6\), multi-tie gaps had median clearance \(q - w_R = 3\), max \(22\), p95 \(8\); multi-tie mean span covered about half the gap; unique-min gaps were shorter on average.

---

## Part 1: Core Insight

```insight
Dual Endpoint Pin of the Min-Tau Level Set

When the same lowest divisor count appears more than once inside a prime gap, that level set is pinned at both ends of the gap: the first hit is forced near the earlier prime, and the last hit is forced near the next prime, so the shared minimum class forms a bridge across the interior rather than a single left-local clump.

This changes the view of multi-hit gaps from "left witness plus free residual" to "two structural endpoints of one floor class," with the interior filled by optional intermediate floor hits.

The non-obvious element is that right-end pin of the last floor hit is as tight in ordinary scale as the familiar left offset of the first hit, even though only the left pin is a proved universal bound.

We would not have predicted that multi-hit gaps systematically stretch the floor class across the gap while singleton floor hits live mostly in short gaps with little room for a second endpoint story.

The concrete pattern expected is that, whenever the floor class appears at least twice, the distance from the last floor hit to the next prime stays small and stable while gap length grows, and that distance stays far below the proved left compression window size.

The principle is scoped to multi-hit interiors (level set size at least 2). It is silent on empty interiors and on singleton floor hits. It is likely to break if large multi-hit gaps appear whose last floor hit sits deep in the middle with a long high-complexity tail before the next prime.

The mechanism is robust relative to the killed residual-mean story because it tracks locations of the floor class itself, not averages of divisor counts. Multiplicity of the floor turns the gap into a corridor whose first and last floor visits are both endpoint-local; residual search after the last floor visit is then only a short clearance strip, while residual search after the first visit alone can still be long.
```

---

## Part 2: Falsifiable Prediction / Decision Rule

```prediction
Prediction (multi-tie only):
Let L = { n in (p,q) : tau(n) = min tau on (p,q) }.
Let w = min L, w_R = max L, clearance = q - w_R, C(q) = max(64, ceil(0.5 * log(q)^2)).
Whenever |L| >= 2 and p >= 11:
  (P1) clearance <= 32 on every consecutive gap with q <= 2e6 (session mid-scale scan: max clearance 22).
  (P2) On any extension of the same scan with q <= 1e7, max multi-tie clearance remains <= max(32, floor(0.25 * C(q))).
  (P3) Among multi-tie gaps with gap length g >= 20, median clearance stays <= 8 and does not grow linearly with g (slope of median clearance vs g-bin is near 0).

Disconfirmation:
  Any multi-tie gap with clearance > 32 on the 2e6 surface, or clearance > max(32, floor(0.25*C(q))) on a 1e7 surface, or a clear linear climb of multi-tie median clearance with g across bins of width 10 with at least 100 samples each.

False-insight expected pattern (if dual pin is illusory):
  Multi-tie clearances behave like residual lengths after a left-only lock: scale with g/2 or with C(q), and max clearance tracks the largest gaps.

Distinguishing signature vs LSCD (level-set spill past left C from p):
  LSCD concerns w_R - p > C(q). Dual pin concerns q - w_R staying small. Both can be true at once: the level set can spill past the left window while still ending near q.

Decision rule:
  When |L| >= 2 and the first floor hit w is known, certificate work may treat the residual after w as "floor-class live" until w_R is found; after w_R is identified, only the short clearance strip (w_R, q) remains for non-floor checks. When |L| = 1, do not apply right-pin truncation.

Local check outcome (pressure only, regime q <= 2e6): multi-tie n around 90k, max clearance 22, p95=8, mean about 3.5; multi clear>24 count = 0. Status: measured-on-regime only; not verified/validated.
```

---

## Part 3: Prior Art & Novelty Delta

- **GWR + bounded compression (`PROOF.md`):** left pin of first min-\(\tau\) is theorem. Delta: dual claim is about the **last** co-minimal's distance to \(q\), conditional on multi-tie, not a new left bound.
- **LSCD package** (`experiments/min-tau-level-set-compression-2026-07/`): rightmost co-minimal can spill past left \(C(q)\). Delta: spill is compatible with dual pin; the new object is **right clearance**, not left utilization of \(w_R\).
- **Residual-mean valve (falsified 2026-07-24):** claimed residual mean \(\tau\) elevation after \(w\). Delta: dual pin uses **floor-class locations**, not mean \(\tau\); avoids the killed distributional claim.
- **Classical prime-gap / last-composite folklore:** studies gap length and composite runs, not ordered min-\(\tau\) level sets with a proved left maximizer. Delta: PGS floor class \(L\) with dual endpoints is not standard gap length theory.
- **Poisson / last-arrival intuition:** last rare event near an interval end. Delta: here both ends pin at similar ordinary scale, multi-tie bridges half the gap on average, and left pin is theorem-backed rather than random-arrival only.

**Facet novelty:** new **mechanism** (dual endpoint pin of the min-\(\tau\) level set) and new **evaluation** (clearance \(q-w_R\) stratified by multi-tie / gap bins), applied inside the existing PGS object stack.

---

## Part 4: Adversarial Audit Summary

**Conventional attack:** "This is just LSCD or just last-arrival." Forced revision: separate clearance \(q-w_R\) from left spill \(w_R-p>C\); require multi-tie scope; treat residual-mean language as off-limits after the 2026-07-24 kill.

**Methodological attack:** short multi-tie gaps make small clearance trivial. Forced revision: add \(g \ge 20\) median stability (P3) and max-clearance growth vs \(C(q)\) (P2), not only raw max on all multi-tie rows.

**Edge attack:** singleton \(L\) has no dual pin; twins empty; high-\(\tau\) multi-ties may be even tighter and dominate the story. Accepted: scope multi-tie only; high-\(\tau\) tightness is a sub-hypothesis, not required for the core dual-pin claim.

**So-what attack:** if true, residual after \(w_R\) is a short strip and multi-tie certificates get a second structural marker; if false, \(w_R\) can sit mid-gap and residual truncation after first hit remains the only safe story (NLS + left compression). Survives as decision-relevant.

**Status after attack:** **hypothesis**, mid-scale pressure supportive, not theorem, not program-validated. Residual-mean elevation stays **falsified**. GWR / NLS / left compression stay **theorem**.

---

## Session pressure numbers (not committed artifacts)

These numbers came from a local deterministic scan during the insight session. They are **pressure only**. A future committed probe should re-emit JSON under `artifacts/`.

| Regime | Multi-tie \(n\) | Max clearance | p95 | Mean clearance | clear \(> 24\) |
| --- | ---: | ---: | ---: | ---: | ---: |
| \(q \le 2\cdot 10^5\) | ~10k | 14 | 6 | ~3.1 | 0 |
| \(q \le 10^6\) | ~47k | 22 | 6 | ~3.4 | 0 |
| \(q \le 2\cdot 10^6\) | ~90k | 22 | 8 | ~3.5 | 0 |

Additional structural notes from the same scans:

- Multi-tie mean gap length larger than singleton mean gap length (longer corridors for bridges).
- Multi-tie mean span \((w_R - w)/g\) around one half of the gap.
- High-\(\tau\) multi-ties tended to show **tighter** clearance than \(\tau(w)=4\) multi-ties (sub-hypothesis).

---

## Optional next pressure

Minimal falsification package: reuse the LSC probe's \(w_R\) and `clearance` fields, restrict to \(\lvert L\rvert \ge 2\), register P1–P3, run through \(q \le 10^7\), commit JSON. That is the natural successor to the residual-mean kill: **geometry of the floor class**, not means.

---

## Sources

**Repo artifacts:**

- `PROOF.md` (GWR, NLS, bounded compression)
- `docs/RESULTS.md` (falsified residual-mean elevation row, 2026-07-24)
- `experiments/gap-winner-one-way-complexity-valve-falsification-2026-07/`
- `experiments/min-tau-level-set-compression-2026-07/`
- Local mid-scale Python scans on consecutive gaps up to \(q \le 2\cdot 10^6\) (pressure only)

**External:** classical prime-gap surveys (gap length, composite runs) as prior-art contrast only; no external source uses GWR co-minimal dual pin language.
