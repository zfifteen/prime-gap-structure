# Witness Offset Classification

Session mode: `insight`.

Status of every claim in this chapter: hypothesis until `FINDINGS.md` records a regime result. `PROOF.md` stays the theorem authority. This chapter does not edit it.

## Object

Start at a prime `p` at least 10. Let `q` be the next prime. The interior is every integer strictly between them. The selected witness `w` is the leftmost integer in that interior whose divisor count is minimal. The offset is the distance `w - p`.

The proved ceiling on that distance is `max(64, ceil(0.5 * log(q)^2))`. The d=4 chamber note already identifies the fractional position `(w - p) / (q - p)`. The August cloud in `research/22-gwr-witness-offset-structure/` describes the same offsets up to `10^6` and leaves the winner's arithmetic type unconditioned.

## Frozen predicates

These sentences were written before the `10^6` aggregate. A later table does not rewrite them.

**L1.** If the winner kind is `two_prime_product`, the offset is in `{2, 4, 6, 8, 10}`.

**L2.** The set of gaps whose offset lies in `{1, 2, 3, 4, 5}` equals the set of gaps whose selected witness has divisor count 4.

**L3.** Trichotomy on offsets strictly above 20:

1. Killed, when any such offset has divisor count at least 5.
2. Survived on the regime, when every such offset has divisor count at most 4 and at least one of them has fractional position at least `1/2`.
3. Abstained, when every such offset has divisor count at most 4 and fractional position below `1/2`.
4. Abstained, when the regime contains no offset above 20.

Branch 3 is the abstention the sprint plan names: the extreme offsets are a large gap with a small fraction, which restates left arrival inside the proved bound.

**L4.** If the left prime is greater than 5, congruent to 29 modulo 30, and the next prime is at least 4 larger, the offset is not 1.

L4 is the novel wheel claim. When the left prime is 29 mod 30, the integer `p + 1` is divisible by 30, so its divisor count is at least 8. L4 says that integer is not the selected witness once the chamber holds anything besides that single point.

## Winner kind

The kind is read from the same smallest-prime-factor walk that builds the divisor count:

| Walk | Kind |
| --- | --- |
| Pure prime power `p^2` | `prime_square` |
| Pure prime power `p^3` | `prime_cube` |
| Pure prime power `p^k` with `k >= 4` | `higher_prime_power` |
| Product of two distinct primes | `two_prime_product` |
| Every other integer | `other` |

Primes themselves are endpoints. They are labeled `other` because they are not interior winners.

## Prior-art gate

A result abstains when its table restates one of these:

- the proved offset ceiling in `PROOF.md`;
- the identity `(w - p) / (q - p)` in `research/pgs-rh-placement-empirics-2026-06/d4_fractional_position_bound.md`;
- the reduced gap-type state in `research/03-gap-types/docs/gap_type_sequence_grammar_findings.md`;
- parity of an odd witness minus an odd prime (even offset).

## Regime label

The first aggregate is measured on primes from 10 inclusive to `10^6` exclusive. That surface is the one already counted in chapter 22 (78,493 gaps, max offset 48, median 2). Matching those three numbers is the sanity check for this sieve. Program-level verified or validated wording waits on an executed `10^18` anchor, and only for a predicate that is still alive after a `10^8` band.

## Sentence read off the first kind table

After the first `10^6` kind table, and before any larger limit, one more sentence was frozen for later regimes only:

**Square envelope.** Every witness with offset at least 24 has winner kind `prime_square`.

The `10^6` count for this sentence is the observation that produced it. A limit above `10^6` is the test. A failure there is a kill. A zero count there is measured on that later regime.

## Abstention sentence

L1 or L2 abstains only when the prior-art gate names the column that reproduced the table. A counterexample is a kill, with the first `(p, q, w)` written down. L3 abstains on branch 3 or 4 above. L4 with zero applicable gaps is unresolved on that regime, not a survival.
