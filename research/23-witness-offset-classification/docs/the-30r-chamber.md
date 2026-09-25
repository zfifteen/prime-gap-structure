# The 30r chamber

Repository: [https://github.com/zfifteen/prime-gap-structure](https://github.com/zfifteen/prime-gap-structure)

Measurement home: `research/23-witness-offset-classification/` on branch `research/witness-offset-classification`, commit `362d95e6`.

Status: measured on left primes below `10^8`. The proofs in `PROOF.md` stay as they are.

## The phenomenon

Start with a prime that sits one step before a multiple of 30. The next whole number is divisible by 2, 3, and 5, so it has a crowd of divisors. Between this prime and the following prime there is a short row of whole numbers. Pick the leftmost number in that row whose divisor count is smallest.

For a long stretch of the number line, the multiple of 30 loses that pick whenever the row contains anything besides itself. A neighbor has fewer divisors, and the pick moves there.

Below one hundred million that stops being true, twenty times. Each time the picture has the same frame. The next prime is exactly eight steps later. The chosen number is thirty times a prime, and it has exactly sixteen divisors. The six whole numbers after it each have at least sixteen divisors, and at least one of them has exactly sixteen. The multiple of thirty wins because it is the leftmost member of that tie.

The smallest case is the prime 17,666,309. Thirty times 588,877 is 17,666,310. The next prime is 17,666,317. The row between them looks like this.

| Step | Number | What it is | Divisors |
| --- | --- | --- | ---: |
| 0 | 17,666,309 | the left prime | 2 |
| 1 | 17,666,310 | 2 · 3 · 5 · 588,877 | 16 |
| 2 | 17,666,311 | 13 · 31 · 59 · 743 | 16 |
| 3 | 17,666,312 | 2³ · 569 · 3,881 | 16 |
| 4 | 17,666,313 | 3 · 7² · 47 · 2,557 | 24 |
| 5 | 17,666,314 | 2 · 19 · 101 · 4,603 | 16 |
| 6 | 17,666,315 | 5 · 17 · 307 · 677 | 16 |
| 7 | 17,666,316 | 2² · 3³ · 37 · 4,421 | 48 |
| 8 | 17,666,317 | the next prime | 2 |

The chosen number is 17,666,310. Five numbers in the row have 16 divisors. It is the first of them.

The same frame occurs for twenty primes below 100 million. The factors inside the six neighboring seats change from chamber to chamber. The frame does not: gap 8, witness equal to 30 times a prime, sixteen divisors, and a tie.

Two shorter landings are closed by arithmetic, for every prime of this kind. Four steps ahead is divisible by 3. Six steps ahead is divisible by 5. Neither can be the next prime. Eight steps is the first distance at which the next prime is still possible, once the two-step gap is set aside. Every one of the twenty wins uses that first open distance. A longer win remains possible past this range. This run produced none.

## Technical account

### Objects

Let `p < q` be consecutive primes, with `p > 5`. The interior of the gap is the set of integers strictly between them. The divisor count `tau(n)` is the number of positive divisors of `n`. The selected witness `w` is the leftmost interior integer whose divisor count is minimal:

```text
w = min{ n : p < n < q and tau(n) = min{ tau(m) : p < m < q } }
```

The offset is `w - p`. This selection is the Gap Winner Rule. The universal ceiling on the offset is already proved in `PROOF.md`:

```text
w - p <= max(64, ceil(0.5 * log(q)^2))
```

with `log` the natural logarithm. The chambers in this note sit inside that ceiling. They are a separate measured pattern about one remainder class.

### The remainder class

The class under study is

```text
p ≡ 29 (mod 30).
```

Then `p = 30r - 1` for an integer `r >= 1`, and the next integer is

```text
p + 1 = 30r = 2 · 3 · 5 · r.
```

The predicate tested here, called L4 in `CONTRACT.md`, was frozen before any aggregate was computed:

```text
If p > 5, p ≡ 29 (mod 30), and q >= p + 4,
then w is not equal to p + 1.
```

The two-step gap `q = p + 2` has a single interior integer, namely `p + 1`, so that integer is the witness for a structural reason. L4 speaks only about longer chambers.

### Why the gap cannot be 4 or 6

For every integer `r >= 1`,

```text
p + 4 = 30r + 3 = 3(10r + 1),
p + 6 = 30r + 5 = 5(6r + 1).
```

Both are composite and larger than the prime that divides them. So if `p ≡ 29 (mod 30)` and `p > 5`, the next prime is never `p + 4` and never `p + 6`.

The same residue arithmetic lists the admissible even distances. The landing `p + d` can be prime only when `p + d` shares no factor with 30. Since `p ≡ -1 (mod 30)`, that condition is `gcd(d - 1, 30) = 1`. The admissible distances begin

```text
2, 8, 12, 14, 18, 20, 24, 30, ...
```

Distance 2 is the one-point chamber, outside L4. Distance 8 is the least admissible distance inside L4. Its right endpoint is `p + 8 = 30r + 7`, which is coprime to 30.

### When the witness has exactly 16 divisors

If `r` is prime and `r > 5`, then `r` is coprime to 30, and

```text
tau(30r) = tau(2) tau(3) tau(5) tau(r) = 2 · 2 · 2 · 2 = 16.
```

The sixteen divisors are the products of distinct subsets of `{2, 3, 5, r}`.

An audit by trial division, run after selection on the twenty witnesses below `10^8`, found that each witness is of this form. The scanner itself selected `w` by divisor counts. The primality of `r` is that later reading of the twenty stored witnesses.

### The six-neighbor condition

Suppose `q = p + 8`. The interior is

```text
30r, 30r + 1, 30r + 2, 30r + 3, 30r + 4, 30r + 5, 30r + 6.
```

The witness is `30r` if and only if each of the six later integers has divisor count at least `tau(30r)`. In the twenty chambers, `tau(30r) = 16`, and each of those six counts is at least 16. At least one of them equals 16, so the minimum is tied, and `30r` wins by being leftmost.

The seat of the tie is not fixed. Across the twenty chambers there are 11 distinct subsets of `{1, 2, 3, 4, 5, 6, 7}` on which the divisor count equals 16. Seat 1 is in every subset, because that seat is the witness. Two chambers tie on all six later seats. One chamber ties only on seat 2. The common measured statement is the inequality, together with the existence of at least one tie.

### What the counts say

Applicable chambers are those with left prime in the tested range, `p ≡ 29 (mod 30)`, and `q >= p + 4`.

| Left primes | All gaps | Applicable chambers | Times `p + 1` wins |
| --- | ---: | ---: | ---: |
| 10 to `10^6` | 78,493 | 7,108 | 0 |
| 10 to `10^7` | 664,574 | 63,515 | 0 |
| 10 to `10^8` | 5,761,450 | 573,516 | 20 |

Below `10^8`, the applicable chambers split by which integer first undercuts the divisor count of `p + 1`:

| | Below `10^7` | Below `10^8` |
| --- | ---: | ---: |
| `p + 2` has fewer divisors | 63,017 | 566,849 |
| `p + 3` has fewer divisors, and `p + 2` does not | 297 | 3,892 |
| A later interior integer carries the minimum | 201 | 2,755 |
| `p + 1` is the witness | 0 | 20 |

The twenty wins are the entire fourth row. Each has gap 8 and divisor count 16. The least left prime is 17,666,309. The greatest in this range is 99,688,829.

### The twenty chambers

`r = (p + 1) / 30`. The right prime is `p + 8`. Multiplicity is the number of interior integers whose divisor count equals 16.

| `r` | Left prime `p` | Multiplicity |
| ---: | ---: | ---: |
| 588,877 | 17,666,309 | 5 |
| 742,801 | 22,284,029 | 5 |
| 1,303,669 | 39,110,069 | 4 |
| 1,517,179 | 45,515,369 | 5 |
| 1,637,261 | 49,117,829 | 5 |
| 1,775,867 | 53,276,009 | 5 |
| 1,788,949 | 53,668,469 | 3 |
| 2,004,131 | 60,123,929 | 3 |
| 2,037,829 | 61,134,869 | 6 |
| 2,166,221 | 64,986,629 | 5 |
| 2,225,501 | 66,765,029 | 5 |
| 2,229,349 | 66,880,469 | 5 |
| 2,250,901 | 67,527,029 | 4 |
| 2,260,729 | 67,821,869 | 2 |
| 2,551,433 | 76,542,989 | 4 |
| 2,588,129 | 77,643,869 | 5 |
| 2,793,569 | 83,807,069 | 3 |
| 2,972,429 | 89,172,869 | 6 |
| 3,073,229 | 92,196,869 | 3 |
| 3,322,961 | 99,688,829 | 3 |

### What this leaves open

A win with gap greater than 8 would require `30r + 7` to be composite, and every interior integer out to the true next prime to have divisor count at least 16. The admissible distances after 8 include 12, 14, 18, 20, 24, and 30. No such longer win appears below `10^8`. Whether one appears further out is unresolved.

The sentence "every L4 win has gap 8 and divisor count 16" is measured on left primes below `10^8`. The sentences about `p + 4` and `p + 6` are arithmetic and hold for every prime in the class.

### Reproduction

From the repository root:

```text
python3 -m pytest research/23-witness-offset-classification/tests/test_classify_offsets.py -q
python3 research/23-witness-offset-classification/scripts/classify_offsets.py --scan --limit 100000000
```

The twenty records, with multiplicity, are the `L4` counterexamples in `classification_scan_100000000.json`. The factor table for `r = 588877` was checked by a separate divisor enumeration of that one chamber.
