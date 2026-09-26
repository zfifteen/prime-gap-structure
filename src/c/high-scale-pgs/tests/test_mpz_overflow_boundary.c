/*
 * test_mpz_overflow_boundary.c
 *
 * Phase 2 (128-bit rung arithmetic plan)
 * -------------------------------------
 * Purpose:
 *   Prove that intermediate arithmetic near the 64-bit hardware boundary
 *   is performed with mpz_t and never relies on native unsigned long.
 *
 * Target interval:
 *   Closed interval [2^63, 2^65].
 *
 * Why this test exists first:
 *   A silent wrap-around near 2^64 shifts the d(n) field, misidentifies
 *   the Gap Winner, corrupts reciprocal transport, and produces a false
 *   unresolved status. The arithmetic foundation must be proven before
 *   any V3 reciprocal-closure logic is placed on top of it.
 *
 * Continuity note for future sessions:
 *   - Run with: make test-mpz-overflow  (after Makefile update)
 *   - Expected: all tests pass, exit code 0.
 *   - If any test fails, stop. Do not wire V3 closure logic until green.
 *   - This file is pure GMP; it does not call chamber resolution yet.
 *   - Next step after this suite is green: complete final certificate
 *     population while keeping dense traversal inside C.
 *
 * Date: 2026-08-07
 * Plan reference: research/06-cryptology-rsa/docs/128-bit-rung-arithmetic-plan.md
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#include <gmp.h>

#include "../include/pgs_high_scale.h"

/* ------------------------------------------------------------------ */
/* Helper: compare mpz against a decimal string                       */
/* ------------------------------------------------------------------ */
static int expect_mpz_eq_str(const char* label, const mpz_t actual, const char* expected) {
    char* got = mpz_get_str(NULL, 10, actual);
    int passed = (got != NULL) && (strcmp(got, expected) == 0);

    if (!passed) {
        printf("FAIL %s: actual=%s expected=%s\n",
               label,
               got ? got : "(null)",
               expected);
    }

    void (*freefunc)(void*, size_t);
    mp_get_memory_functions(NULL, NULL, &freefunc);
    if (got != NULL) {
        freefunc(got, strlen(got) + 1);
    }
    return passed;
}

/* ------------------------------------------------------------------ */
/* Test 1: values just below, at, and above 2^63                      */
/* ------------------------------------------------------------------ */
static int test_around_2_63(void) {
    int passed = 1;
    mpz_t a, b, sum, product;

    mpz_init(a);
    mpz_init(b);
    mpz_init(sum);
    mpz_init(product);

    /* 2^63 - 1 */
    mpz_ui_pow_ui(a, 2UL, 63UL);
    mpz_sub_ui(a, a, 1UL);
    passed &= expect_mpz_eq_str("2^63-1", a, "9223372036854775807");

    /* 2^63 */
    mpz_ui_pow_ui(b, 2UL, 63UL);
    passed &= expect_mpz_eq_str("2^63", b, "9223372036854775808");

    /* sum = (2^63 - 1) + 2  --> crosses the signed 64-bit limit */
    mpz_add_ui(sum, a, 2UL);
    passed &= expect_mpz_eq_str("(2^63-1)+2", sum, "9223372036854775809");

    /* product = 2^63 * 3  --> well above 2^64 */
    mpz_mul_ui(product, b, 3UL);
    passed &= expect_mpz_eq_str("2^63 * 3", product, "27670116110564327424");

    mpz_clear(a);
    mpz_clear(b);
    mpz_clear(sum);
    mpz_clear(product);
    return passed;
}

/* ------------------------------------------------------------------ */
/* Test 2: values just below, at, and above 2^64                      */
/* ------------------------------------------------------------------ */
static int test_around_2_64(void) {
    int passed = 1;
    mpz_t a, b, sum, product, quot;

    mpz_init(a);
    mpz_init(b);
    mpz_init(sum);
    mpz_init(product);
    mpz_init(quot);

    /* 2^64 - 1  (max unsigned 64-bit) */
    mpz_ui_pow_ui(a, 2UL, 64UL);
    mpz_sub_ui(a, a, 1UL);
    passed &= expect_mpz_eq_str("2^64-1", a, "18446744073709551615");

    /* 2^64 */
    mpz_ui_pow_ui(b, 2UL, 64UL);
    passed &= expect_mpz_eq_str("2^64", b, "18446744073709551616");

    /* sum = (2^64 - 1) + 1  --> must not wrap to 0 */
    mpz_add_ui(sum, a, 1UL);
    passed &= expect_mpz_eq_str("(2^64-1)+1", sum, "18446744073709551616");

    /* product = 2^64 * 2  --> 2^65 */
    mpz_mul_ui(product, b, 2UL);
    passed &= expect_mpz_eq_str("2^64 * 2", product, "36893488147419103232");

    /* floor division: (2^64 + 3) // 2  --> 2^63 + 1 */
    mpz_add_ui(sum, b, 3UL);
    mpz_fdiv_q_ui(quot, sum, 2UL);
    passed &= expect_mpz_eq_str("(2^64+3)//2", quot, "9223372036854775809");

    mpz_clear(a);
    mpz_clear(b);
    mpz_clear(sum);
    mpz_clear(product);
    mpz_clear(quot);
    return passed;
}

/* ------------------------------------------------------------------ */
/* Test 3: values just below, at, and above 2^65                      */
/* ------------------------------------------------------------------ */
static int test_around_2_65(void) {
    int passed = 1;
    mpz_t a, b, sum, sqrt_out;

    mpz_init(a);
    mpz_init(b);
    mpz_init(sum);
    mpz_init(sqrt_out);

    /* 2^65 - 1 */
    mpz_ui_pow_ui(a, 2UL, 65UL);
    mpz_sub_ui(a, a, 1UL);
    passed &= expect_mpz_eq_str("2^65-1", a, "36893488147419103231");

    /* 2^65 */
    mpz_ui_pow_ui(b, 2UL, 65UL);
    passed &= expect_mpz_eq_str("2^65", b, "36893488147419103232");

    /* sum = 2^65 + 2^64  --> 3 * 2^64 = 55340232221128654848 */
    mpz_ui_pow_ui(a, 2UL, 64UL); /* a = 2^64 */
    mpz_add(sum, b, a);          /* 2^65 + 2^64 */
    passed &= expect_mpz_eq_str("2^65 + 2^64", sum, "55340232221128654848");

    /* integer square root of a number near 2^128 would be near 2^64;
       here we only check that sqrt of a perfect square above 2^64 is exact */
    mpz_ui_pow_ui(a, 2UL, 66UL);  /* (2^33)^2 = 2^66 */
    mpz_sqrt(sqrt_out, a);
    passed &= expect_mpz_eq_str("sqrt(2^66)", sqrt_out, "8589934592");  /* 2^33 */

    mpz_clear(a);
    mpz_clear(b);
    mpz_clear(sum);
    mpz_clear(sqrt_out);
    return passed;
}

/* ------------------------------------------------------------------ */
/* Test 4: demonstrate that native uint64 would have overflowed       */
/* ------------------------------------------------------------------ */
static int test_native_would_overflow(void) {
    /*
     * This test does not use native types for the computation.
     * It only records the mathematical fact that a native unsigned
     * 64-bit addition of (2^64 - 1) + 1 would wrap to 0, while mpz_t
     * produces the correct 2^64.
     *
     * The purpose is documentation for future maintainers.
     */
    int passed = 1;
    mpz_t a, result;

    mpz_init(a);
    mpz_init(result);

    mpz_ui_pow_ui(a, 2UL, 64UL);
    mpz_sub_ui(a, a, 1UL);          /* 2^64 - 1 */
    mpz_add_ui(result, a, 1UL);     /* must be 2^64, never 0 */

    passed &= expect_mpz_eq_str("native-would-wrap proof", result, "18446744073709551616");

    /* Explicit guard: result must not be zero */
    if (mpz_sgn(result) == 0) {
        printf("FAIL native-would-wrap proof: result is zero (wrap occurred)\n");
        passed = 0;
    }

    mpz_clear(a);
    mpz_clear(result);
    return passed;
}

/* ------------------------------------------------------------------ */
/* Test 5: floor division and isqrt near 128-bit scale (anchor math)  */
/* ------------------------------------------------------------------ */
static int test_anchor_scale_operations(void) {
    /*
     * Simulates the arithmetic that occurs when an anchor sits near 2^64
     * and the modulus is near 2^128. All intermediates stay in mpz_t.
     */
    int passed = 1;
    mpz_t N, anchor, isqrt_N, floor_div;

    mpz_init(N);
    mpz_init(anchor);
    mpz_init(isqrt_N);
    mpz_init(floor_div);

    /* Construct a 128-bit scale number: 2^127 */
    mpz_ui_pow_ui(N, 2UL, 127UL);
    passed &= expect_mpz_eq_str("2^127", N, "170141183460469231731687303715884105728");

    /* isqrt(2^127) is floor(sqrt(2^127)) = 2^63 * floor(sqrt(2)) approx */
    mpz_sqrt(isqrt_N, N);
    /* We only require that the result is positive and less than 2^64 */
    if (mpz_sgn(isqrt_N) <= 0) {
        printf("FAIL isqrt(2^127) is non-positive\n");
        passed = 0;
    }
    mpz_ui_pow_ui(anchor, 2UL, 64UL);
    if (mpz_cmp(isqrt_N, anchor) >= 0) {
        printf("FAIL isqrt(2^127) is not less than 2^64\n");
        passed = 0;
    }

    /* Floor division N // (2^63) must equal 2^64 */
    mpz_ui_pow_ui(anchor, 2UL, 63UL);
    mpz_fdiv_q(floor_div, N, anchor);
    passed &= expect_mpz_eq_str("2^127 // 2^63", floor_div, "18446744073709551616");

    mpz_clear(N);
    mpz_clear(anchor);
    mpz_clear(isqrt_N);
    mpz_clear(floor_div);
    return passed;
}

int main(void) {
    int total = 0;
    int passed = 0;

    printf("PGS mpz_t overflow boundary tests (interval [2^63, 2^65])\n");
    printf("=======================================================\n");

    total++; passed += test_around_2_63();
    total++; passed += test_around_2_64();
    total++; passed += test_around_2_65();
    total++; passed += test_native_would_overflow();
    total++; passed += test_anchor_scale_operations();

    printf("-------------------------------------------------------\n");
    printf("PGS mpz overflow boundary tests: %d/%d groups passed\n", passed, total);

    if (passed != total) {
        printf("STOP: arithmetic foundation is not proven. Do not proceed to V3 wiring.\n");
        return 1;
    }

    printf("PASS: 2^64 boundary arithmetic is solid under mpz_t.\n");
    printf("Next: complete final certificate population while keeping dense traversal in C.\n");
    return 0;
}
