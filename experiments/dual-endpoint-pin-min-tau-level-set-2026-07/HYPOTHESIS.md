# Hypothesis: Dual Endpoint Pin of the Min-Tau Level Set

## Status

| Layer | Status |
| --- | --- |
| Dual endpoint pin (multi-tie clearance) | **hypothesis** |
| Local mid-scale pressure (\(q \le 2\cdot 10^6\)) | **measured on regime only** (session scan; not a committed ladder) |
| GWR leftmost min-\(\tau\) / NLS / left compression \(w-p \le C(q)\) | **theorem** (`PROOF.md`; untouched) |
| Full level-set compression (every co-minimal in left \(C\)) | **invalidated** (see LSC package) |
| Residual-mean elevation after Gap Winner | **falsified** (2026-07-24 valve package) |
| Program verified / validated | **not claimed** (no executed \(10^{18}\) surface for this claim) |

## Source

Novel Insight Engine run against the live prime-gap-structure codebase after:

- merge of residual-mean valve falsification (PR #63);
- `docs/RESULTS.md` falsified-claim row (2026-07-24);
- existing LSC / LSCD package under `experiments/min-tau-level-set-compression-2026-07/`.

## PGS frame

```text
ordered prime-gap (p, q)
  -> divisor-count field tau on the interior
  -> min level m = min tau on (p, q)
  -> level set L = { n in (p, q) : tau(n) = m }
  -> w = min L (GWR), w_R = max L
  -> left offset alpha = w - p
  -> right clearance = q - w_R
  -> dual pin when |L| >= 2
```

Classical sieve / divisor accumulation is field prep only. It does not choose \(w\), \(w_R\), or the decision.

## Definitions

| Symbol | Meaning |
| --- | --- |
| \(p, q\) | consecutive primes, \(q > p \ge 11\) |
| \(m\) | minimum of \(\tau\) on the open interior \((p, q)\) |
| \(L\) | co-minimal level set \(\{n : p < n < q,\ \tau(n) = m\}\) |
| \(w\) | leftmost member of \(L\) (GWR witness) |
| \(w_R\) | rightmost member of \(L\) |
| \(\alpha = w - p\) | left offset (proved \(\alpha \le C(q)\)) |
| \(\mathrm{clearance} = q - w_R\) | right distance from last floor hit to next prime |
| \(C(q) = \max(64, \lceil 0.5 \log(q)^2 \rceil)\) | proved left compression window |
| multi-tie | \(\lvert L\rvert \ge 2\) |
| singleton | \(\lvert L\rvert = 1\) (then \(w_R = w\)) |

## Claims

### H-DEP (core, multi-tie only)

When \(\lvert L\rvert \ge 2\), the min-\(\tau\) level set is **dual-pinned**:

1. **Left pin (theorem):** \(w - p \le C(q)\).
2. **Right pin (hypothesis):** clearance \(q - w_R\) stays small and does not track full residual length after the first hit; multi-tie gaps stretch \(L\) as a **bridge** across the interior rather than a left-local clump only.

### Registered predictions (falsifiers)

| ID | Statement | Falsifier |
| --- | --- | --- |
| **P1** | On consecutive multi-tie gaps with \(p \ge 11\) and \(q \le 2\cdot 10^6\), clearance \(\le 32\). | Any multi-tie row with clearance \(> 32\). |
| **P2** | On extension \(q \le 10^7\), multi-tie max clearance \(\le \max(32, \lfloor 0.25\cdot C(q)\rfloor)\). | Any multi-tie row exceeding that bound. |
| **P3** | Among multi-tie gaps with gap length \(g \ge 20\), median clearance stays \(\le 8\) and does not grow linearly with \(g\) (gap bins of width 10, \(n \ge 100\)). | Median clearance climbs linearly with \(g\)-bin, or median \(> 8\) on those bins. |

### Decision rule (implementation hypothesis)

When \(\lvert L\rvert \ge 2\) and \(w\) is known, treat the residual after \(w\) as floor-class live until \(w_R\) is found. After \(w_R\), only the short clearance strip \((w_R, q)\) remains for non-floor checks. When \(\lvert L\rvert = 1\), do **not** apply right-pin truncation.

## Explicit non-claims

- Does not restore residual-mean elevation after \(w\).
- Does not promote dual pin to theorem.
- Does not bound raw gap size \(q - p\).
- Does not alter GWR maximizer, NLS, or left compression status.
- Singleton and empty interiors are out of H-DEP scope.

## Relation to near packages

| Package | Relation |
| --- | --- |
| `experiments/min-tau-level-set-compression-2026-07/` | LSC invalidated; LSCD is left-spill of \(w_R\). Dual pin is **right clearance**, compatible with spill. |
| `experiments/gap-winner-one-way-complexity-valve-falsification-2026-07/` | Killed mean-\(\tau\) residual elevation. Dual pin uses floor **locations**, not means. |
