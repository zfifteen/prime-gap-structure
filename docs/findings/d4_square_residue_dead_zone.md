# `d=4` Square-Residue Dead Zone

This note records the finding that the live non-floor square-ceiling branch on
the earliest-`d=4` semiprime surface is residue-locked by the next prime
square modulo `30`.

## Finding

The strongest supported claim is:

once the floor package `q = r^2 - 2` fails on the live earliest-`d=4`
semiprime branch, the first possible non-floor closure margin is not universal.
It splits by the residue of the next prime square:

- if `r^2 ≡ 19 (mod 30)`, the branch can close first at margin `6`;
- if `r^2 ≡ 1 (mod 30)`, the branch cannot close at margin `6` and starts at
  margin `8`.

So the previously isolated missing branch `q = r^2 - 4` is not merely absent
on the scanned surface. It is wheel-forbidden on the live branch.

## Exact Executed Surface

Artifacts:

- [d4_square_residue_dead_zone_summary.json](../../output/d4_square_residue_dead_zone_summary.json)
- [d4_square_residue_dead_zone.csv](../../output/d4_square_residue_dead_zone.csv)
- runner:
  [benchmarks/python/gap_ridge/d4_square_residue_dead_zone_probe.py](../../benchmarks/python/gap_ridge/d4_square_residue_dead_zone_probe.py)
- tests:
  [tests/python/gap_ridge/test_d4_square_residue_dead_zone_probe.py](../../tests/python/gap_ridge/test_d4_square_residue_dead_zone_probe.py)

The current executed run is an exact scan through `10^7` on the same live
branch used by the earlier obstruction note:

- selected integer is the earliest interior non-cube `d=4` semiprime,
- floor package `r^2 - 2` is filtered out by direct primality check,
- the remaining non-floor rows are split by `r^2 mod 30`.

Measured counts on that exact surface:

- `r^2 ≡ 1 (mod 30)`: `196,581` rows, minimum observed margin `8`,
  margin-`6` count `0`, margin-`8` count `35`
- `r^2 ≡ 19 (mod 30)`: `201,377` rows, minimum observed margin `6`,
  margin-`6` count `45`, margin-`8` count `39`

So the first non-floor margin already separates exactly on the current exact
surface.

## Why The Split Happens

Let `s = r^2` be the next prime square above the live selected integer `w`.

On the non-floor branch, `s - 2` is composite by construction. For odd primes
`r > 5`, prime squares satisfy

$$s \equiv 1 \text{ or } 19 \pmod{30}.$$

That gives two distinct predecessor ladders.

### Case 1: `s ≡ 19 (mod 30)`

Then:

- `s - 4 ≡ 15 (mod 30)`, so `s - 4` is composite;
- `s - 6 ≡ 13 (mod 30)`, so `s - 6` is wheel-open.

So after floor failure, margin `6` is the first residue-admissible non-floor
closure.

### Case 2: `s ≡ 1 (mod 30)`

Then:

- `s - 4 ≡ 27 (mod 30)`, so `s - 4` is composite;
- `s - 6 ≡ 25 (mod 30)`, so `s - 6` is composite;
- `s - 8 ≡ 23 (mod 30)`, so `s - 8` is the first wheel-open non-floor
  candidate.

So the `1` branch has a built-in two-step dead zone below the square ceiling:
it cannot close at margins `4` or `6`, and starts at `8`.

## What Is New Here

The earlier obstruction note established that `r^2 - 4` never appeared on the
exact scanned branch. This note identifies the structural reason and adds a
new split:

- `r^2 - 4` is wheel-forbidden on both residue branches;
- `r^2 - 6` is allowed only on the `19` branch;
- the first non-floor margin is therefore residue-dependent.

That is a stricter statement than “the branch seems to jump from `2` to `6`.”
It says the jump is not one branch. It is a residue-gated phase split.

## Decision Rule

On the live earliest-`d=4` semiprime branch, after `r^2 - 2` fails:

- if `r^2 ≡ 19 (mod 30)`, test `r^2 - 6` as the first live non-floor closure;
- if `r^2 ≡ 1 (mod 30)`, skip directly to `r^2 - 8`.

Do not spend search effort on `r^2 - 4` on either branch, or on `r^2 - 6` on
the `1` branch.

## Scope

This is a bounded statement about the live earliest-`d=4` semiprime branch
under the square-ceiling framing used in this repository.

It does not claim that every later margin is residue-determined, and it does
not by itself close the deeper tail. What it does close is the formerly open
`r^2 - 4` obstruction, and it sharpens the first non-floor branch into a
two-regime modular law.
