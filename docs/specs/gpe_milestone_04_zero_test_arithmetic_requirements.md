# GPE Milestone 4: Zero-Test Arithmetic Requirements

## Purpose

Milestone 4 resolves the dependency between the exact DNI/GWR oracle and the
current divisor field.

The present exact path detects the right endpoint by scanning until:

$$d(n)=2$$

That is exact for the current oracle, but it does not satisfy the GPE zero-test
contract.

## Forbidden Runtime Dependencies

The GPE runtime path must not use:

- Miller-Rabin,
- probabilistic primality tests,
- `sympy.isprime`,
- `sympy.nextprime`,
- `gmpy2.is_prime` as a hidden endpoint detector,
- trial division of gap interiors,
- candidate sieving lists,
- full Eratosthenes-style marking.

## Required Arithmetic Replacement

The implementation must compute selected integer and endpoint placement from rulebook
arithmetic:

- fixed GPE state,
- explicit modular constraints,
- branch-specific selector laws,
- NLSC threat horizons,
- and deterministic integer arithmetic.

Any use of divisor counts must be justified as a construction-time validation
tool, not as part of the final GPE runtime contract.

## Development Gate

During development, validation may compare against the existing exact
divisor-field oracle. The production GPE path must not call that oracle to
decide the endpoint.

The code must keep these paths separate:

- `oracle`: exact validation surface, allowed to inspect divisor counts;
- `gpe`: target runtime path, not allowed to inspect candidate primality.

There must be no silent downgrade from `gpe` to `oracle`.

## Acceptance Gate

Milestone 4 is complete when:

- the target GPE function emits exact primes on the validation surface,
- the call graph for that function contains no forbidden runtime dependency,
- the validation oracle remains available only as an external checker,
- and the documentation identifies every arithmetic ingredient used by the
  runtime path.

## Non-Goals

This milestone does not add fallback paths, retries, or safety modes. If the
zero-test arithmetic path cannot decide a endpoint, it fails explicitly.
