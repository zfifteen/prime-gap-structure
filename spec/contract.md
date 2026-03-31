# Geodesic Prime Prefilter Contract

This contract defines the deterministic behavior each implementation must satisfy. Its mathematical core is the **Divisor Curvature Identity** (DCI) `Z(n) = n^(1 - d(n)/2)`.

## Core Invariants

- The fixed-point traversal rate is fixed at `v = e^2 / 2`.
- The exact identity is the Divisor Curvature Identity (DCI) `Z(n) = n^(1 - d(n)/2)`.
- Confirmed primes lie on the fixed-point band `Z = 1.0`.
- The production prefilter rejects a candidate only when it has found a concrete factor in one of the gated prime tables.
- Survivor status is not a primality proof. Survivors advance to fixed-base Miller-Rabin and then final confirmation in the production Python path.

## Deterministic Inputs

- Candidate generation uses the SHA-256 namespace/index stream already defined by the Python implementation.
- The fixed Miller-Rabin base set is `2, 3, 5, 7, 11, 13, 17, 19`.
- RSA public exponents must be odd integers greater than `1`.

## Vector Families

- `candidate_stream_*.json`
  deterministic candidate generation by index
- `prefilter_decisions_*.json`
  reject/survive decisions plus factor provenance
- `fixed_points_small_n.json`
  exact calibration checks for the fixed-point band
- `generate_prime_*.json`
  deterministic prime-generation outputs

## Porting Rule

- Python is the initial normative executable implementation.
- Java must match the committed vectors exactly.
- Apple-Silicon-only C99/GMP/MPFR becomes the reference implementation only after vector parity and manual benchmark parity are achieved.
