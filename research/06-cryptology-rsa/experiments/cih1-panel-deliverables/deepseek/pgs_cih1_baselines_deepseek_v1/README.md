# pgs_cih1_baselines_deepseek_v1

DeepSeek sandbox package for CIH‑1 negative controls and contamination baselines.

**Status:** audit/baseline tooling only – no PGS factorisation claims.

## Purpose

Before interpreting CIH‑1 results, the Research Assistant must run this package to:

- Confirm that bidirectional floor reciprocity near √N is extremely common (≈99.9%) and therefore **not a discriminating signal**.
- Flag near‑square semiprimes (fermat_steps = 0) that must be excluded from “general RSA hardness” claims.
- Demonstrate that “reciprocal class” pairs (V3 style) can be composite and not the true factors.
- Validate the official ladder fixture classifications.

## Requirements

- Python 3.10+
- No external dependencies (standard library only)

## CLI usage

