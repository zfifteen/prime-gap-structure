# Mersenne Prime Adjacent Gap-Type Probe

This note records one narrow test of a specific hypothesis:

Do known Mersenne primes sit next to distinctive `GWR`/`DNI` gap types?

The strongest supported finding is:

On the current exact tractable surface of known Mersenne primes, the
**following** gap shows a clear one-sided regularity, while the
**preceding** gap does not collapse nearly as tightly.

More concretely:

- the tested exact surface contains the known Mersenne primes
  `2^p - 1` with `p in {2, 3, 5, 7, 13, 17, 19, 31, 61}`;
- for every tested Mersenne prime with `p >= 5`, the **following** selected interior integer
  is an odd-semiprime `d = 4` integer;
- those `7` following gaps collapse to only `2` exact type signatures:
  `o6_d4_a2_odd_semiprime` (`4` cases) and
  `o4_d4_a2_odd_semiprime` (`3` cases);
- the **preceding** side remains more varied, with `6` exact type signatures
  across `8` defined preceding gaps.

So the current test supports a **one-sided following-gap regularity** on the
tractable Mersenne surface. It does **not** support a symmetric claim that
both adjacent sides collapse to one unique Mersenne-specific gap type.

## Artifacts

- runner:
  [`../../benchmarks/python/predictor/gwr_dni_mersenne_gap_type_probe.py`](../../benchmarks/python/predictor/gwr_dni_mersenne_gap_type_probe.py)
- tests:
  [`../../tests/python/predictor/test_gwr_dni_mersenne_gap_type_probe.py`](../../tests/python/predictor/test_gwr_dni_mersenne_gap_type_probe.py)
- JSON summary:
  [`../../output/gwr_dni_mersenne_gap_type_probe_summary.json`](../../output/gwr_dni_mersenne_gap_type_probe_summary.json)
- detail CSV:
  [`../../output/gwr_dni_mersenne_gap_type_probe_details.csv`](../../output/gwr_dni_mersenne_gap_type_probe_details.csv)

## Exact Tractable Surface

The current exact probe uses the repo's divisor-field gap typing directly.

That executable path is presently limited by the `int64` segment representation
used in the exact divisor-field scan, so this note stops at the tractable
known Mersenne primes through exponent `61`. This is an implementation-surface
limit of the current exact probe, not a claim about the mathematics itself.

The tested Mersenne primes are therefore:

- `3 = 2^2 - 1`
- `7 = 2^3 - 1`
- `31 = 2^5 - 1`
- `127 = 2^7 - 1`
- `8191 = 2^13 - 1`
- `131071 = 2^17 - 1`
- `524287 = 2^19 - 1`
- `2147483647 = 2^31 - 1`
- `2305843009213693951 = 2^61 - 1`

For each tested prime `q`, the probe classifies:

- the preceding gap ending at `q`, when that gap has an interior;
- the following gap beginning at `q`.

## Measured Adjacent Types

| Exponent | Mersenne prime | Preceding type | Following type |
|---|---:|---|---|
| `2` | `3` | — | `o4_d3_a1_prime_square` |
| `3` | `7` | `o2_d4_a1_even_semiprime` | `o4_d3_a2_prime_square` |
| `5` | `31` | `o2_d8_a1_higher_divisor_even` | `o6_d4_a2_odd_semiprime` |
| `7` | `127` | `o6_d3_a8_prime_square` | `o4_d4_a2_odd_semiprime` |
| `13` | `8191` | `o4_d4_a3_even_semiprime` | `o6_d4_a2_odd_semiprime` |
| `17` | `131071` | `o6_d4_a6_odd_semiprime` | `o6_d4_a2_odd_semiprime` |
| `19` | `524287` | `o4_d4_a4_odd_semiprime` | `o4_d4_a2_odd_semiprime` |
| `31` | `2147483647` | `o4_d4_a4_odd_semiprime` | `o4_d4_a2_odd_semiprime` |
| `61` | `2305843009213693951` | `o6_d4_a6_odd_semiprime` | `o6_d4_a2_odd_semiprime` |

The visible asymmetry is immediate:

- the preceding side spreads across higher-divisor, square, even-semiprime,
  and odd-semiprime regimes;
- the following side collapses to prime-square behavior only at `3` and `7`,
  then to odd-semiprime `d = 4` behavior for every tested exponent `p >= 5`.

## Distribution Summary

On the `8` defined preceding gaps:

- odd-semiprime family: `4 / 8`
- even-semiprime family: `2 / 8`
- prime-square family: `1 / 8`
- higher-divisor-even family: `1 / 8`
- distinct exact preceding types: `6`

On the `9` following gaps:

- odd-semiprime family: `7 / 9`
- prime-square family: `2 / 9`
- distinct exact following types: `4`

Restricting to the `7` Mersenne primes with exponent `p >= 5`:

- following odd-semiprime family: `7 / 7`
- following exact type `o6_d4_a2_odd_semiprime`: `4 / 7`
- following exact type `o4_d4_a2_odd_semiprime`: `3 / 7`

So the tested regularity lives almost entirely on the following side.

## Nearby-Prime Context

Repetition alone does not make a type distinctive. The probe therefore also
measures a fixed nearby-prime window of radius `20` around each tested
Mersenne prime and asks how common the same exact adjacent type is inside that
local neighborhood.

For the `7` cases with exponent `p >= 5`:

- the matching following exact type never ranked first in its local window
  (`0 / 7` rank-one hits);
- the local exact-type share ranged from `2.44%` through `12.20%`.

So the observed following-gap regularity is real on the tested Mersenne
surface, but the repeated types are **not** locally dominant signatures around
those primes. The current evidence supports repetition, not local exoticity.

## Reading The Hypothesis Carefully

Attached to the tested scope, the current result is:

- **supported:** tractable Mersenne primes show a repeated following-gap
  pattern;
- **not supported:** a unique symmetric adjacent-gap signature on both sides;
- **not yet tested here:** larger known Mersenne primes beyond the current
  exact `int64` probe surface.

That means the clean current statement is narrower than
"Mersenne primes are preceded or followed by a unique distinct gap type."

The measured statement is:

Known tractable Mersenne primes through exponent `61` show a one-sided
following-gap regularity: after the small edge cases `3` and `7`, every tested
Mersenne prime is followed by an odd-semiprime `d = 4` selected integer gap, but the
preceding side stays heterogeneous.

## Conclusion

The current exact probe does not justify a broad symmetric Mersenne-gap
duality claim.

It does justify a narrower and more interesting observation:

on the tractable exact surface, the **following** gap after a Mersenne prime
stabilizes far more strongly than the **preceding** gap.

That is the part worth carrying forward.
