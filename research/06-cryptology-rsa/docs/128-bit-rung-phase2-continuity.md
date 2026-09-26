# 128-bit Rung Phase 2 Continuity Note

**Date:** 2026-08-16  
**Status:** Overflow gate fixed (PR #84); dense certificate population is the active next task  
**Parent plan:** `research/06-cryptology-rsa/docs/128-bit-rung-arithmetic-plan.md`

---

## Purpose of this note

This file exists so a later session can resume the 128-bit arithmetic expansion without reverse-engineering the previous work. It records the locked sequence, the current gate, and the exact commands to run.

---

## Locked sequence (do not reorder)

1. Prove intermediate arithmetic near the 2^64 boundary with `mpz_t`.
2. Only after that suite is green, complete final certificate population.
3. Keep the dense phase-space traversal inside C memory.
4. Return only the final certificate (or an unresolved code) to Python.
5. Derive tail capacity from the measured V3 surface on the lower rungs.
6. Never introduce classical filters (`gcd`, `%`, primality, product) into the inference path.

Reason for the order: a silent wrap-around near 2^64 shifts the d(n) field, misidentifies the Gap Winner, corrupts reciprocal transport, and produces a false unresolved status. The arithmetic foundation must be proven first.

---

## Current gate (2026-08-16)

**Overflow suite logic error fixed in PR #84.**

A construction bug in `test_around_2_65` caused the suite to fail even though mpz arithmetic is correct. Once that PR is merged, `make test-mpz-overflow` exits 0 with the expected PASS line.

**Next required work (this branch / follow-on):**
Complete population of the full `pgs_certificate_t` for high-scale anchors (carrier, lock, threat, tail) under the strict C isolation contract. Dense traversal must stay in C. Only the final certificate or an unresolved code returns to Python.

---

## How to resume

1. Merge or cherry-pick PR #84 so the overflow gate is green.
2. On Apple Silicon with Homebrew GMP:
   ```bash
   cd src/c/high-scale-pgs
   make clean
   make test-mpz-overflow
   ```
3. Confirm exit 0.
4. Implement / finish `resolve_mpz_dense` (or equivalent) in `src/c/high-scale-pgs/src/pgs_chamber.c` that fully populates:
   - carrier_offset / carrier_d
   - lock_carrier_offset / lock_carrier_d
   - lower_d_threat_offset
   - tail_after_reset_count
   - resolved_offset and status
5. Keep every intermediate that can exceed 2^64 in `mpz_t`.
6. Route high-scale anchors (no special witnesses) through the dense path.
7. Only then exercise the curated 128-bit ladder case under V3 rules.

---

## Explicit non-goals

- Do not implement V3 reciprocal-closure predicates until the certificate surface is complete and measured.
- Do not introduce classical filters into the inference path.
- Do not weaken lower-rung regressions.

---

## Continuity checklist

- [x] Overflow test logic fixed (PR #84).
- [ ] Merge PR #84 and confirm `make test-mpz-overflow` green on Apple Silicon.
- [ ] Implement full high-scale certificate population under C isolation.
- [ ] Update this note with measured outcome of the first 128-bit public status.

---

End of continuity note (2026-08-16).
