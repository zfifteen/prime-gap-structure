# 128-bit Rung Phase 2 Continuity Note

**Date:** 2026-08-16 (updated from 2026-08-07)  
**Status:** Overflow gate green after test fix  
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

**Overflow suite is now green.**

A logic error in the original `test_around_2_65` constructed `2^66 + 2^64` instead of `2^65 + 2^64`. That made the gate fail even though the underlying mpz arithmetic was correct. The construction is fixed.

- Test: `src/c/high-scale-pgs/tests/test_mpz_overflow_boundary.c`
- Makefile target: `make test-mpz-overflow`
- Expected terminal line:
  ```
  PASS: 2^64 boundary arithmetic is solid under mpz_t.
  Next: complete final certificate population while keeping dense traversal in C.
  ```
- Exit code must be 0.

**Stop condition:** if the suite fails, do not wire any V3 reciprocal-closure logic.

**Go condition:** suite exits 0 → proceed to complete final certificate population under the C-side isolation contract.

---

## How to resume in a new session

From the repository root on an Apple Silicon machine with Homebrew GMP/MPFR:

```bash
cd src/c/high-scale-pgs
make clean
make test-mpz-overflow
```

Confirm exit 0 and the PASS line above. Then begin final certificate field completion in `src/c/high-scale-pgs/src/pgs_chamber.c`.

---

## Files touched so far

| Path | Role |
|------|------|
| `research/06-cryptology-rsa/docs/128-bit-rung-arithmetic-plan.md` | Master plan |
| `research/06-cryptology-rsa/docs/128-bit-rung-phase2-continuity.md` | This continuity note |
| `src/c/high-scale-pgs/tests/test_mpz_overflow_boundary.c` | Overflow suite (bug fixed 2026-08-16) |
| `src/c/high-scale-pgs/Makefile` | Target `test-mpz-overflow` |

---

## Next concrete tasks (gate is now green)

1. Complete population of the final `pgs_certificate_t` fields for high-scale anchors (carrier, lock, threat, tail).
2. Enforce that every intermediate calculation that can exceed 2^64 uses `mpz_t`.
3. Keep the dense candidate/chamber loop entirely inside C.
4. Add instrumentation on the final certificate path only.
5. Only then route the curated 128-bit ladder case and capture the measured public status under V3 rules.

---

## Explicit non-goals that remain

- Do not implement V3 reciprocal-closure predicates yet.
- Do not change the Python inference path yet.
- Do not alter the public-versus-audit separation.
- Do not introduce classical pre-filters.

---

## Continuity checklist

- [x] Run `make test-mpz-overflow` and confirm exit code 0 (after the 2^65 sum fix).
- [x] Record the terminal output / commit message.
- [ ] Open `src/c/high-scale-pgs/src/pgs_chamber.c` and complete final certificate field population under the C-side isolation contract.
- [ ] Update this continuity note with the new stop/go gate after that step.

---

End of continuity note (2026-08-16).
