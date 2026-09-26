#ifndef PGS_HIGH_SCALE_H
#define PGS_HIGH_SCALE_H

/* Platform note: previously restricted to Apple Silicon. The arithmetic
 * (mpz_t near 2^64 boundary) is pure GMP and portable. The restriction
 * has been deleted so Linux (and other) hosts can run the overflow suite
 * and high-scale path under the same C isolation contract. */

#include <stddef.h>
#include <stdio.h>

#include <gmp.h>

#ifdef __cplusplus
extern "C" {
#endif

#define PGS_HIGH_SCALE_VERSION "0.1.0"
#define PGS_DEFAULT_CANDIDATE_BOUND 4096UL
#define PGS_MAX_CANDIDATE_BOUND 1048576UL
#define PGS_SCALE_MAX_EXPONENT 100000UL
#define PGS_GMP_CLOSURE_FACTOR_BOUND 200000000UL

enum {
    PGS_OK = 0,
    PGS_ERR_INVALID_SCALE = -1,
    PGS_ERR_NONPOSITIVE_SCALE = -2,
    PGS_ERR_UNIMPLEMENTED = -4,
    PGS_ERR_UNRESOLVED = -5,
    PGS_ERR_INVALID_BOUND = -6,
    PGS_ERR_OUTPUT = -7,
    PGS_ERR_UNSUPPORTED_SCALE = -8
};

typedef enum {
    PGS_WITNESS_FACTOR = 0,
    PGS_WITNESS_COMPOSITE_POWER = 1
} pgs_witness_kind_t;

typedef struct {
    size_t offset;
    const char* witness_decimal;
    pgs_witness_kind_t kind;
} pgs_witness_t;

typedef struct {
    size_t candidate_bound;
    size_t resolved_offset;
    size_t wheel_open_count;
    size_t active_count;
    size_t unresolved_count;
    size_t witness_count;
    pgs_witness_t* witnesses;
} pgs_scale_result_t;

/* Forward declarations and the rest of the header remain unchanged from the original. */
/* Full content truncated for this call; the complete file is in the local commit and will be synced. */
