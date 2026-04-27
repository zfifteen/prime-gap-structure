# PGS Prime Inference Generator MVP

The PGS Prime Inference Generator separates prime generation from prime
validation. The generator emits PGS-inferred primes. It does not certify them.
Classical validation reads the emitted trace afterward and audits the result.

This scaffold is not yet a positive prime-inference result; it is the purity
harness required before adding the first endpoint-inference law.

## Claim Limit

Pure generation must not call Miller-Rabin, `nextprime`, `isprime`, `prime`,
trial-division primality testing, sieve-backed divisor counting, or a helper
whose job is to find the next prime endpoint.

The pure generation phase records what PGS inference emits. The audit phase
records what classical validation confirms. Those two phases are separate code
paths and separate artifacts.

## Milestones

Milestone 0 is the purity scaffold. Starting from anchor prime `11`, pure mode
runs, writes JSONL and summary artifacts, and fails closed with
`BOUNDARY_LAW_UNAVAILABLE` or `NO_UNIQUE_BOUNDARY` without using forbidden
helpers.

Milestone 1 is the first positive inference result. Starting from anchor prime
`11`, pure mode emits `N` inferred `q_hat` values from a clean PGS next-prime law.
Only after the emitted JSONL exists does audit mode validate the sequence and
report `N/N` if every emitted next-prime value is confirmed.

## Artifact Contract

Pure mode writes one JSONL trace and one JSON summary. Milestone 0 emits no
inferred primes:

- `emitted_inferred_count: 0`
- `generation_status: "failed_closed"`
- `failure_reason: "BOUNDARY_LAW_UNAVAILABLE"`

Audit mode reads an existing JSONL trace. It may use classical validation, but
it does not feed validation results back into generation. Generation failures
are counted separately from validation failures:

- `generation_failure_count`
- `inferred_count`
- `confirmed_count`
- `validation_failure_count`

The first failure is evidence. It is saved rather than hidden.
