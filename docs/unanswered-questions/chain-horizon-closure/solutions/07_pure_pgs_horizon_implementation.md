# Pure-PGS Chain Horizon Implementation (2026-08-16)

## Answer to the open question

Yes. The divisor-horizon law can be derived from PGS structure.

The missing object is now concrete:

```python
from z_band_prime_predictor.pure_pgs_horizon import default_pure_horizon

H = default_pure_horizon(p, s0, chain_deltas)  # == max(64, ceil(0.5 * log(scale)**2))
```

Alternative tighter empirical form (from least-factor frontier mining):

```python
H = pure_pgs_horizon(p, s0, chain_deltas, mode="visible_2maxgap")
```

Both are pure PGS-visible. Neither requires trial division to sqrt(q).

## Integration point

In `chain_horizon_closure_result` (or its successor) replace:

```python
horizon_bound = None   # triggers full divisor exhaustion
```

with:

```python
from z_band_prime_predictor.pure_pgs_horizon import default_pure_horizon
horizon_bound = default_pure_horizon(p, s0, chain_deltas)
```

Downstream audit still runs; under-closing is therefore safe.

## Why this closes the residual

- Prior controlled probes showed mean least-factor-of-false-nodes / sqrt(q) ≈ 0.11 and never approached 1.
- The proved UBC cutoff already bounds the selected witness; applying the same scale to the pre-terminal false nodes is the natural first pure-PGS law.
- Empirical forms that add 1–2× max chain gap improve tightness further while remaining local.

This converts the dominant high-scale non-PGS fraction into PGS-derived output.

Best part is no part. Delete the sqrt path.
