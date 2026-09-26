# Test-Scale Live-Solver Evolution (<=80-bit)

Status: measured-on-regime / hypothesis / unresolved. Not a factorization claim.
No RSA-scale resolver theorem is claimed.

Long-lived branch: `feat/test-modulus-evolution-le80`
All daily automation work stays on that branch. Never push `main` from this track.

## Frame

```text
locked PGS endpoint chain
  -> floor transport through N
  -> reciprocal endpoint closure
  -> modulus-link residual
  -> structural certificate | unresolved
```

Start anchor is `floor(sqrt(N))` unless a slice is explicitly flagged as a
family-specific probe. Public inference reads public fixtures only. Audit is
physically separate and does not choose the endpoint class.

## Current phase

```text
PHASE: A
NEXT_SLICE: A1-rebuild-and-pin-baseline
```

## Public cases in scope

- `rsa_v2_40bit_static_001` (v2 audit `factor_found=true`)
- `rsa_v2_50bit_static_001` (v2 pin `factor_found=false`)
- `rsa_v2_64bit_static_001` (v2 audit `factor_found=true`)
- later 70-80-bit fixtures curated from `scaleup_corpus` only

V3 50-bit pair `(32047633, 32059651)` is measured-on-regime / hypothesis.
Historical false class `(32047651, 32059633)` stays blocked.
First-tail window stays `[-12, 6]`. Do not widen it. Do not edit `boundD`.

## Slice list

Check a slice only after its exit criterion is met on this branch.

### Phase A. Reproducibility baseline

- [ ] A1-rebuild-and-pin-baseline
      Rebuild `research/06-cryptology-rsa/experiments/data-ladder/rsa-v2`
      fixtures. Run `run_experiment.py` then `audit_experiment.py`.
      Capture inference, survivor, diagnostic, and structural-cert rows.
      Exit: 40-bit audit true, 50-bit v2 audit false, 64-bit audit true,
      fixture hashes recorded in the daily log. No discriminator edits.

### Phase B. 50-bit residual taxonomy

- [ ] B1-name-discriminator-D
      Formalize discriminator D that cleared the old carrier residual on
      joint cell `C1T2L1` with `R=(1,2,1)` and `pinch_S=54`.
- [ ] B2-stability-under-fixed-tail-window
      Log first-tail window `[-12, 6]` and evaluate public-geometry stability.
      Dual audit required. A class that fails `factor_found` stays hypothesis.

### Phase C. Transport diagnostics (sidecars only)

- [ ] C1-measure-filter-responses-70-80
      On curated 70-80-bit public fixtures measure strict reset closure,
      `reciprocal_carrier_alignment_holds` with bound `max(20, 1.2*gap)`,
      and `lower_lock_dominance_holds`.
- [ ] C2-sidecar-budget-probes
      Run sidecar probes only; record budget exhaustion and exclusion debt;
      do not promote sidecars into the resolver.

### Phase D. Recall and precision

- [ ] D1-endpoint-class-recall
      Endpoint-class recall, audit precision, historical false-class rate.
      A rung is resolved only if recall and audit precision are both 1.0 on
      physically separate fixtures.

## Forbidden

- gcd, divisibility selectors, product closure, hidden factors, primality APIs
- seeded factor-ratio anchors as general law
- window widening, boundD edits, per-rung special cases
- 128-bit, 256-bit, or production-grade moduli
- RSA-scale theorem language
- the words verified or validated (this track has no executed 10^18 surface)

## Issue alignment

- #69 residual taxonomy / C1T2L1 honesty
- #70 reciprocal endpoint-closure law
- #72 anti-false-positive guards

## Daily log

Append every run to
`research/06-cryptology-rsa/docs/test-modulus-evolution-le80-daily-log.md`.

## Blockers

- 2026-08-22 A1: rsa_v2_64bit_static_001 public inference closed as `unresolved_by_profile_count_mismatch` (chain steps 1162); audit factor_found=false. Exit needs 64-true. Fixture rebuild hashes recorded in daily log. No discriminator edits. NEXT_SLICE remains A1-rebuild-and-pin-baseline.
- 2026-08-23 A1: re-confirmed same profile_count_mismatch surface on rsa_v2_64bit_static_001; fixtures hashes stable; 40-bit closes as expected; no code or discriminator change. NEXT_SLICE remains A1-rebuild-and-pin-baseline.
- 2026-08-24 A1: fixtures hashes stable; 40-bit closes as expected; matched_profile_counts_hold rejection path remains active for 64-bit (active_count / unresolved_count mismatch after high chain steps); no discriminator, boundD or window edits. NEXT_SLICE remains A1-rebuild-and-pin-baseline.
- 2026-08-25 A1: fixtures hashes stable; 40-bit closes as expected; profile_count_mismatch rejection path remains active for 64-bit; no discriminator, boundD or window edits. NEXT_SLICE remains A1-rebuild-and-pin-baseline.
- 2026-08-26 A1: fixtures hashes stable; 40-bit and 50-bit close as expected (true / unresolved carrier); profile_count_mismatch rejection path remains active for 64-bit; no discriminator, boundD or window edits. NEXT_SLICE remains A1-rebuild-and-pin-baseline.
- 2026-08-27 A1: fixtures hashes stable; 40-bit and 50-bit close as expected; profile_count_mismatch rejection path remains active for 64-bit; no discriminator, boundD or window edits. NEXT_SLICE remains A1-rebuild-and-pin-baseline.
- 2026-08-28 A1: fixtures hashes stable; 40-bit closes as expected; profile_count_mismatch rejection path remains active for 64-bit; no discriminator, boundD or window edits. NEXT_SLICE remains A1-rebuild-and-pin-baseline.
- 2026-08-29 A1: fixtures hashes stable; 40-bit closes as expected; profile_count_mismatch rejection path remains active for 64-bit; no discriminator, boundD or window edits. NEXT_SLICE remains A1-rebuild-and-pin-baseline.
- 2026-08-30 A1: fixtures hashes stable; 40-bit closes as expected; profile_count_mismatch rejection path remains active for 64-bit; no discriminator, boundD or window edits. NEXT_SLICE remains A1-rebuild-and-pin-baseline.
- 2026-08-31 A1: fixtures hashes stable; 40-bit closes as expected; profile_count_mismatch rejection path remains active for 64-bit; no discriminator, boundD or window edits. NEXT_SLICE remains A1-rebuild-and-pin-baseline.
