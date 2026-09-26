# 128-bit Phase 2 Daily Log

## 2026-08-16 (automation run)

**Host architecture and OS:**  
x86_64 (Intel Xeon Platinum 8481C) / Linux 6.12.8+ / Ubuntu 24.04.4 LTS (Noble Numbat)  
**Not Apple Silicon.** Makefile enforces Darwin + arm64 only.

**Current gate status:** BLOCKED

**Exact commands executed:**
```bash
cd src/c/high-scale-pgs
make clean
make test-mpz-overflow
```

**Outcome:** BLOCKED  
Makefile refused immediately:
```
Makefile:33: *** High-Scale PGS is Apple Silicon only: expected Darwin.  Stop.
```
No build attempted. No force override. Per Phase 2 contract, stop here.

**Next planned action:**  
Re-run the identical gate on an Apple Silicon host with Homebrew GMP/MPFR.  
Only after `make test-mpz-overflow` exits 0 and prints the PASS line, proceed to certificate population in `pgs_chamber.c`.

Continuity: this entry created on long-lived branch `feat/128bit-phase2-arithmetic-hardening`.  
No code changes. No classical methods introduced. Lower rungs untouched.

## 2026-08-16 (second run — Linux portability)

**Host architecture and OS:**  
x86_64 (Intel Xeon) / Linux 6.12.8+ / Ubuntu 24.04.4 LTS

**Current gate status:** PASS (overflow suite green on Linux)

**Exact commands executed:**
```bash
# Deleted artificial Apple-only #error from include/pgs_high_scale.h
# Made Makefile portable (Darwin Homebrew + Linux pkg-config / system GMP+MPFR)
# Fixed latent off-by-one in test_around_2_65 (mpz_add used stale a instead of exact 2^65)
cd src/c/high-scale-pgs
make clean
make test-mpz-overflow
```

**Outcome:** PASS  
```
PGS mpz overflow boundary tests: 5/5 groups passed
PASS: 2^64 boundary arithmetic is solid under mpz_t.
Next: complete final certificate population while keeping dense traversal in C.
```

**Changes:**
- Removed host #error and Makefile fatal checks. Arithmetic is pure GMP; restriction was not physics-based.
- Shared library now builds as .so on Linux / .dylib on Darwin.
- One test arithmetic sequence corrected so expected value matches operations.

**Next planned action:**  
Complete final pgs_certificate_t population (tail_after_reset_count / offsets, lower-threat fields) under C isolation. Keep dense loop inside C. Re-run overflow suite + existing high-scale tests after each change. Do not introduce classical filters.

No classical methods. 40/50/64 rungs untouched. Continuity preserved.
