# DCI Prefilter

Most cryptographic prime candidates are composite.

That is the practical starting point. Prime generation spends most of its work on numbers that will never survive the full probable-prime path. A useful prefilter therefore does not need to prove primality early. It needs to remove composite work early, deterministically, and without breaking the final confirmation path.

In this repository, that front end is the DCI prefilter. It is the deterministic production filter built from the fixed-point band implied by the **Divisor Curvature Identity** (DCI) \(Z(n) = n^{1 - d(n)/2}\) at

$$
v = \frac{e^{2}}{2}.
$$

At that traversal rate, confirmed primes lie on the invariant band \(Z = 1.0\), while composites contract below it under exact divisor counting. The production prefilter keeps that band as its survivor convention and uses concrete factor discovery as its rejection rule.

## Why A Prefilter Matters

The computational problem is straightforward.

When prime generation runs at cryptographic bit lengths, most odd candidates are composite. Sending every one of them through the full probable-prime path wastes work. Miller-Rabin is fast, but it still costs more than discovering an early concrete factor.

The DCI gives the pipeline an invariant target. Under the exact identity, primes occupy the fixed-point band \(Z = 1.0\). That makes it possible to organize the production path around a narrow distinction:

- reject when a concrete factor is found,
- preserve the survivor band when no such factor has yet been found.

This is the role of the prefilter. It is not a replacement for the final probable-prime path. It is the deterministic front end that reduces how much composite work reaches that path.

## Relation To The Exact DCI

The exact DCI is

$$
Z(n) = n^{1 - d(n)/2}.
$$

This identity is exact under exact divisor count, and it is the mathematical source of the invariant band. A prime has \(d(p) = 2\), so \(Z(p) = 1\). A composite has \(d(n) > 2\), so \(Z(n) < 1\).

That exact law is the derivation and the audit surface for the prefilter. It is not the runtime mechanism used for cryptographic-scale candidate loops. Exact divisor counting remains too expensive at that scale.

The production path in this repository therefore does something narrower. It keeps the fixed-point band as the invariant survivor target, but it does not attempt to compute exact divisor count for each cryptographic candidate. Instead it uses deterministic factor-gated discovery to decide whether a candidate can already be pushed below the band.

## Deterministic Production Path

The runtime path is intentionally straight.

1. Generate deterministic odd candidates from the SHA-256 namespace/index stream.
2. Scan each candidate against the gated prime tables.
3. Reject immediately only when a concrete factor is found.
4. Keep survivors on the band convention `proxy_z = 1.0`.
5. Run fixed-base Miller-Rabin on survivors.
6. Apply final `sympy.isprime` confirmation in the current Python path.

The gated tables are organized in three intervals in the normative Python implementation:

- a primary table,
- a tail table,
- a deep-tail table used only from the configured bit threshold upward.

The implementation searches those intervals deterministically. If one interval finds a factor, the candidate is rejected on that concrete arithmetic evidence. If no interval finds a factor, the candidate remains on the survivor convention `proxy_z = 1.0` and advances.

This is a single deterministic execution path. It does not widen into alternate rejection rules, probabilistic proxy gates, or backup modes.

## Survivor Semantics

The production prefilter uses the fixed-point band as a survivor convention.

That convention is narrow. In this repository, `proxy_z() == 1.0` means the candidate survived the gated factor tables used by the prefilter. It does not by itself prove primality.

The distinction matters because the production pipeline has separate stages:

- the prefilter removes candidates when it has found a concrete factor,
- Miller-Rabin evaluates the surviving candidate under the fixed base set,
- `sympy.isprime` gives final confirmation in the current Python implementation.

The prefilter and Miller-Rabin therefore play complementary roles. The prefilter is the deterministic screening front end. Miller-Rabin and final confirmation resolve the surviving candidates. The pipeline remains one connected path from deterministic candidate generation through confirmed prime output.

## Contract Surface

The contract is deliberately narrow.

The repository commits to the following production behavior:

- the fixed-point traversal rate is fixed at `v = e^2 / 2`,
- candidate generation uses the deterministic SHA-256 namespace/index stream,
- the prefilter rejects only when it has found a concrete factor in one of the gated prime tables,
- survivor status is not a primality proof,
- the fixed Miller-Rabin base set is `2, 3, 5, 7, 11, 13, 17, 19`.

That contract is recorded in [spec/contract.md](../spec/contract.md), and the parity surface is committed in [spec/vectors/](../spec/vectors/). The normative executable implementation of this concern is [src/python/geodesic_prime_prefilter/prefilter.py](../src/python/geodesic_prime_prefilter/prefilter.py), with the public API exported through [src/python/geodesic_prime_prefilter/__init__.py](../src/python/geodesic_prime_prefilter/__init__.py).

The public Python surface for this concern includes:

- `CDLPrimeGeodesicPrefilter`
- `generate_prime`
- `generate_rsa_prime`
- `FIXED_POINT_V`
- `DEFAULT_MR_BASES`

At the class level, the survivor-facing interface includes `proxy_z()` and `is_prime_candidate()`.

## Measured Results

The current validated Python regime shows that the deterministic production path removes most tested cryptographic candidates before Miller-Rabin while preserving the invariant survivor convention.

In the curated benchmark summary:

- the `2048`-bit control corpus rejects `91.02%` of candidates before Miller-Rabin and reports `2.95x` candidate-loop speedup,
- the `4096`-bit control corpus rejects `91.41%` of candidates before Miller-Rabin and reports `3.33x` candidate-loop speedup.

The same production path also yields measured end-to-end RSA key-generation gains on deterministic streams.

- `2048` bits, `300` deterministic keypairs:
  baseline `291938.126792` ms
  accelerated `139942.831833` ms
  speedup `2.09x`
  Miller-Rabin reduction `90.97%`
- `4096` bits, `50` deterministic keypairs:
  baseline `757750.922792` ms
  accelerated `268557.631625` ms
  speedup `2.82x`
  Miller-Rabin reduction `91.07%`

The calibration surface remains aligned with the fixed-point band:

- `29/29` calibration primes stayed on `Z = 1.0`
- `0` composite false fixed points

These results describe the production prefilter concern only. The exact invariant derivation and the exact raw composite field studies belong to separate concerns in the repository.

## Reproduction Surface

The prefilter concern is reproducible from the committed contract, vectors, tests, and benchmark notes.

For manual validation, see [docs/prefilter/manual_validation.md](./prefilter/manual_validation.md).

For the curated benchmark summary, see [docs/prefilter/benchmarks.md](./prefilter/benchmarks.md).

The main reproduction surfaces for this concern are:

- install the Python package from `./src/python`,
- run `pytest tests/python -q`,
- verify the golden vectors directly with `pytest tests/python/test_vectors.py -q`,
- run the candidate benchmark and RSA benchmark commands recorded in the manual validation and benchmark notes.

Those artifacts keep the runtime claim bounded to the validated Python regime while preserving a direct audit path from contract, to vectors, to implementation, to measured result.
