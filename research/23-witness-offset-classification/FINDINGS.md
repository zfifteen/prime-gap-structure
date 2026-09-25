# Findings

Status of this chapter: measured on named regimes, with four frozen predicates killed and one wheel claim holding only up to a named bound. `PROOF.md` is unchanged.

The object is the selected witness inside a prime gap. For consecutive primes `p < q`, that witness is the leftmost integer strictly between them whose divisor count is smallest. The offset is the distance from `p` to that integer.

## The scale break

Predicate L4, frozen in `CONTRACT.md` before the first aggregate, says: when `p > 5`, `p ≡ 29 (mod 30)`, and `q >= p + 4`, the selected witness is not `p + 1`. The integer `p + 1` is then divisible by 30, so its divisor count is at least 8.

| Left primes | Gaps | Applicable L4 gaps | L4 counterexamples | Least counterexample |
| --- | ---: | ---: | ---: | --- |
| 10 to `10^6` | 78,493 | 7,108 | 0 | none on this regime |
| 10 to `10^7` | 664,574 | 63,515 | 0 | none on this regime |
| 10 to `10^8` | 5,761,450 | 573,516 | 20 | `p = 17666309` |

Through `10^7` the multiple of 30 never wins. Below `10^8` it wins 20 times. The least such chamber is

```text
p = 17666309, q = 17666317, w = 17666310, offset = 1, divisor count = 16
```

An independent divisor enumeration of that chamber agrees: both endpoints are prime, the interior minimum is 16, and the leftmost integer at that minimum is `17666310`. The same audit on all 20 stored witnesses shows one shape:

- the gap is exactly 8, so `q = p + 8`;
- the witness is `p + 1 = 30r` with divisor count 16;
- `r` is prime (trial division on these 20 cofactors, after selection);
- the minimum is tied: between 2 and 6 interior integers share divisor count 16, and `30r` wins because it is leftmost.

The 20 left primes are 17666309, 22284029, 39110069, 45515369, 49117829, 53276009, 53668469, 60123929, 61134869, 64986629, 66765029, 66880469, 67527029, 67821869, 76542989, 77643869, 83807069, 89172869, 92196869, and 99688829.

How the other applicable chambers avoid `p + 1`, counted by the compact scanner:

| Left primes | `p + 2` has fewer divisors | `p + 3` has fewer divisors | a later integer carries the minimum | `p + 1` itself is the witness |
| --- | ---: | ---: | ---: | ---: |
| 10 to `10^7` | 63,017 | 297 | 201 | 0 |
| 10 to `10^8` | 566,849 | 3,892 | 2,755 | 20 |

The shortest later-integer save on both regimes is the gap from 551549 to 551557. Its witness is 551555, offset 6, divisor count 4, one integer at that minimum.

## The offset-20 claim breaks in the same decade

Predicate L3 says that every offset above 20 has divisor count at most 4, and then separates a large fractional position from a small one. On primes below `10^7` every offset above 20 does have divisor count at most 4, and 121 of those extremes sit at or past the middle of their gap. On primes below `10^8` the claim dies 61 times. The least witness is

```text
p = 10012703, q = 10012727, w = 10012724, offset = 21, divisor count = 6
```

The minimum there is unique. The winner kind is `other`. An independent divisor enumeration matches that count and that leftmost integer.

The kind maxima show the same crossing. Maximum offset by winner kind:

| Kind | Below `10^6` | Below `10^7` | Below `10^8` |
| --- | ---: | ---: | ---: |
| `prime_square` | 48 | 60 | 98 |
| `two_prime_product` | 22 | 30 | 40 |
| `other` | 14 | 20 | 27 |
| `prime_cube` | 4 | 4 | 6 |
| `higher_prime_power` | 4 | 4 | 4 |

`other` reaches offset 20 below `10^7` and offset 27 below `10^8`. That single step past 20 is the L3 kill.

## Predicates that die at once

L1 required every product of two distinct primes to land in the offset set `{2, 4, 6, 8, 10}`. The least counterexample is `p = 13`, `q = 17`, `w = 14`, offset 1. Below `10^6` there are 13,481 such witnesses.

L2 required the offsets `{1, 2, 3, 4, 5}` to be exactly the witnesses of divisor count 4. The least counterexample is `p = 11`, `q = 13`, `w = 12`, divisor count 6. Below `10^6` the two sets differ on 31,761 gaps.

The square-envelope sentence was read off the `10^6` kind table, where every offset of 24 or more is a prime square, and then tested on later limits. It dies at `p = 1039429`, `q = 1039463`, `w = 1039453`, offset 24, divisor count 4, kind `two_prime_product`. Below `10^7` there are 27 such witnesses. Below `10^8` there are 1,398.

## What these regimes still show

On each of the three regimes the maximum offset belongs to a prime square, and the scanner records zero offsets above the proved ceiling `max(64, ceil(0.5 * log(q)^2))`.

| Regime | Maximum offset | Witness | Square |
| --- | ---: | ---: | --- |
| below `10^6` | 48 | 259081 | `509^2` |
| below `10^7` | 60 | 1885129 and 6355441 | both prime squares |
| below `10^8` | 98 | 15437041 | `3929^2` |

The `10^8` maximum sits at offset 98 in a gap of 110, so the square is past the middle of the chamber, and it is the only integer in that chamber with divisor count 3. The chapter 22 sanity check matches on the `10^6` run: 78,493 gaps, maximum offset 48, median offset 2.

## Next pressure

The 20 L4 chambers below `10^8` share gap 8, divisor count 16, and a tied minimum. The next measurement is whether a regime above `10^8` still keeps that shape, or produces a longer chamber in which `p + 1` wins. That regime is not executed here. Program-level verified or validated wording is not available for these predicates.

## Reproduce

From the repository root:

```text
python3 -m pytest research/23-witness-offset-classification/tests/test_classify_offsets.py -q
python3 research/23-witness-offset-classification/scripts/classify_offsets.py --limit 1000000
python3 research/23-witness-offset-classification/scripts/classify_offsets.py --limit 10000000
python3 research/23-witness-offset-classification/scripts/classify_offsets.py --scan --limit 10000000
python3 research/23-witness-offset-classification/scripts/classify_offsets.py --scan --limit 100000000
```

The `10^6` command checks itself against the chapter 22 counts and exits nonzero on a mismatch. Summaries live beside this file. The path segment `output/` is reserved by the repo thinness gate, so these JSON files stay in the chapter directory.
