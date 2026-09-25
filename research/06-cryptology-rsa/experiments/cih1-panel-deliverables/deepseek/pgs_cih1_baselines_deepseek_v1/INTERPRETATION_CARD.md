# CIH‑1 Interpretation Card (DeepSeek baselines)

The Research Assistant must attach this checklist to the CIH‑1 report.

| Check | Pass criterion | What failure means for CIH‑1 claims |
|-------|----------------|--------------------------------------|
| **Official fixture replay** | 40/64 classified near‑square, 50 non‑near‑square | Baseline logic is broken; all derived metrics unreliable. |
| **Floor density on corpus** | Median pass_rate > 0.95 (window 50000, stride 1) | Reciprocity is not a discriminating signal; any method relying on it as “evidence” is contaminated. |
| **Near‑square contamination rate** | Report `near_square_rate`; if > 0.0, those cases must be excluded from “hardness” interpretations. | CIH‑1 success rate may be inflated by trivial Fermat instances. |
| **Fermat median steps on non‑near‑square** | Should be > 0 (ideally > 1000) for any modulus labelled “non‑near‑square”. | If median steps = 0 even for “non‑near‑square” by our gate, the gate is too weak; re‑examine classification. |
| **Audit integrity** | All `audit_integrity_failures` == 0. | Corrupted hold‑out data; do not proceed. |
| **Decoy reciprocal existence** | At least one case has a decoy reciprocal pair not equal to the true factors. | If no decoys found, the reciprocal‑only “class” might spuriously match factors; CIH‑1 false‑positive risk is high. |
| **V3‑style mis‑match** (decoy product ≠ N) | For every decoy x, x*(N//x) ≠ N. | A “reciprocal closure” that ignores product equality is not factorisation; any claim equating them is invalid. |
