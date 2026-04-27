# Dominant $d=4$ Arrival-Reduction Findings

This note records the current measured status of the dominant-case reduction
behind the Gap Winner Rule.

## Statement Tested

The broad dominant-case claim is:

1. if the implemented score maximizer in a prime gap has divisor count $d(w)=4$, then
   the gap contains no interior prime square;
2. if a prime gap contains no interior prime square and does contain at least
   one interior integer with $d(n)=4$, then the implemented score maximizer is the
   first such interior $d=4$ carrier.

The implementation defines the selected integer from the log-score

$$
L(n)=\left(1-\frac{d(n)}{2}\right)\ln(n)
$$

and then checks the local divisor profile separately. So this is not a
tautological restatement of GWR.

The stricter semiprime-only wording was tested separately:

- stronger claim:
  every $d=4$ selected integer is a semiprime;
- competing possibility:
  a thin prime-cube exception family survives inside the broader $d=4$ class.

## Current Artifacts

- runner:
  [`benchmarks/python/gap_ridge/gwr_d4_arrival_validation.py`](../../benchmarks/python/gap_ridge/gwr_d4_arrival_validation.py)
- tests:
  [`tests/python/gap_ridge/test_gwr_d4_arrival_validation.py`](../../tests/python/gap_ridge/test_gwr_d4_arrival_validation.py)
- JSON summary:
  [`output/gwr_d4_arrival_validation_summary.json`](../../output/gwr_d4_arrival_validation_summary.json)
- exact-surface CSV:
  [`output/gwr_d4_arrival_validation_exact.csv`](../../output/gwr_d4_arrival_validation_exact.csv)
- even-band CSV:
  [`output/gwr_d4_arrival_validation_even_bands.csv`](../../output/gwr_d4_arrival_validation_even_bands.csv)

## Tested Surface

The current documented surface used:

- exact full scan to $10^6$,
- exact full scan to $2 \times 10^7$,
- deterministic even-band windows at every decade from $10^8$ through
  $10^{18}$,
- window size $2 \times 10^6$,
- $2$ even windows per scale.

This is the same deterministic style used for the current closure note: full
small exact scans plus a fixed even-band ladder at higher scales.

## Main Results

The broad dominant-case reduction held exactly on the full documented surface.

| Scale | Gap count | $d=4$ selected integer gaps | Interior-square violations | First-$d=4$ matches | Prime-cube selected integers |
|---|---:|---:|---:|---:|---:|
| exact $10^6$ | 70,327 | 58,303 | 0 | 58,303 | 7 |
| exact $2 \times 10^7$ | 1,163,198 | 959,730 | 0 | 959,730 | 15 |
| $10^8$ | 234,639 | 193,728 | 0 | 193,728 | 8 |
| $10^9$ | 224,237 | 185,013 | 0 | 185,013 | 8 |
| $10^{10}$ | 215,807 | 178,500 | 0 | 178,500 | 8 |
| $10^{11}$ | 208,766 | 172,443 | 0 | 172,443 | 8 |
| $10^{12}$ | 202,949 | 167,575 | 0 | 167,575 | 8 |
| $10^{13}$ | 197,687 | 163,487 | 0 | 163,487 | 8 |
| $10^{14}$ | 193,665 | 160,154 | 0 | 160,154 | 8 |
| $10^{15}$ | 189,602 | 156,752 | 0 | 156,752 | 8 |
| $10^{16}$ | 186,494 | 154,278 | 0 | 154,278 | 8 |
| $10^{17}$ | 183,355 | 151,823 | 0 | 151,823 | 8 |
| $10^{18}$ | 180,447 | 149,279 | 0 | 149,279 | 8 |

The strongest supported statement on the current surface is therefore:

For every tested gap whose selected integer has $d(w)=4$, no interior prime square
appears anywhere in the gap, and the selected integer is exactly the first interior
$d=4$ carrier.

The `first-$d=4$` rate is $1.0$ on every documented regime above.

## What Failed

The semiprime-only wording is false.

The exact scan to $2 \times 10^7$ recorded $15$ $d=4$ selected integers that are prime
cubes rather than semiprimes. The first explicit counterexample is:

- gap $(6857, 6863)$,
- selected integer $6859 = 19^3$,
- selected-integer offset $2$.

So the supported dominant-case reduction is:

- no interior prime square,
- then first interior $d=4$ wins.

It is not:

- no interior prime square,
- then first interior semiprime wins.

The broader $d=4$ class is the right one.

## What This Changes

This finding changes the dominant GWR regime from a global-looking score
optimization problem into a local exclusion-and-arrival mechanism.

Instead of asking:

- which interior composite maximizes the full log-score?

the dominant $d=4$ regime now reads:

- did the gap admit any interior prime square at all?
- if not, where is the first interior $d=4$ carrier?

On the current documented surface, that local mechanism already recovers the
true selected integer exactly for every tested $d=4$ selected integer gap.

## Implications For The Project

### 1. The dominant regime now has a visible mechanism

Most of the selected integer surface is carried by $d=4$ selected integers. On the current exact
and even-band runs, that dominant regime no longer needs to be described as a
full gap-wide score search. It can be described as:

- square exclusion first,
- then first-$d=4$ arrival.

That is a much cleaner internal explanation of why GWR looks so rigid.

### 2. The explanatory program gets narrower

The main follow-on explanation for the dominant regime now splits naturally
into two questions:

- why do prime gaps with $d=4$ selected integers avoid interior prime squares?
- once no interior prime square is present, why does the first interior
  $d=4$ carrier always win?

That is a more focused program than treating the dominant regime as a full
gap-wide score search.

### 3. The right class is $d=4$, not semiprimes

The semiprime-only version would have been cleaner rhetorically, but it is not
the truth of the current surface. The exact $2 \times 10^7$ run already shows
that a thin prime-cube exception family survives. So the correct formulation is
class-based:

- first interior $d=4$ carrier,

not factorization-type-based:

- first interior semiprime.

### 4. $d=4$ selected integer dominance looks structural

The exact $2 \times 10^7$ run recorded $959{,}730$ $d=4$ selected integers out of
$1{,}163{,}198$ tested gaps, a share of about $0.8251$. At the same time, the
prime-cube exceptions stayed thin:

$$
\frac{15}{959{,}730} \approx 1.56 \times 10^{-5}.
$$

So the dominant $d=4$ layer is not a small-number artifact on the current
surface. It remains the main large-scale regime.

## Reading The Prime-Cube Counts Carefully

The exact runs are the right place to read the prime-cube exception family.

The even-band ladder always includes the leftmost window starting at $2$, so
its repeated prime-cube counts are not an asymptotic frequency estimate. They
mainly show that the same early exceptions keep reappearing in the fixed first
window. The exact $2 \times 10^7$ run is the better measure of how thin the
prime-cube family is on a full surface.

## Scope

This note documents the dominant $d=4$ arrival reduction only. It does not
replace the main `GWR` proof summary, and it does not claim that every
non-`d=4` selected divisor-count class admits an equally simple local reduction. What it does
support is narrower and still strong:

On the current documented surface, the dominant $d=4$ GWR regime is exactly
captured by a local rule: no interior prime square, then first interior
$d=4$ wins.
