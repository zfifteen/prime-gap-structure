# Elevation card: 30-witness in a longer 29-chamber

## Ordinary object

Take a prime that leaves remainder 29 on division by 30. The next integer is divisible by 2, 3, and 5. When the following prime is at least four steps away, ask whether that highly divisible integer is the leftmost minimum-divisor point of the chamber.

## Formal predicate

L4 from `CONTRACT.md`: if `p > 5`, `p ≡ 29 (mod 30)`, and the next prime `q` satisfies `q >= p + 4`, the GWR witness is not `p + 1`.

## Status

Killed on left primes below `10^8`.

Zero counterexamples on the 7,108 applicable gaps below `10^6` and on the 63,515 applicable gaps below `10^7`. Twenty counterexamples below `10^8`. The least is `p = 17666309`, `w = 17666310`, gap 8, divisor count 16, minimum tied by 5 interior integers.

All 20 counterexamples below `10^8` have gap 8, witness `30r` with `r` prime, divisor count 16, and a tied minimum. That shared shape is measured on this kill set. It is a hypothesis for any larger regime.

## Regime

Left primes from 10 inclusive to `10^8` exclusive. Compact scanner summary: `classification_scan_100000000.json`.

## Next pressure

Run the same frozen predicate above `10^8` and record whether any counterexample has gap different from 8 or divisor count different from 16.

## Authority

This card does not enter `PROOF.md`. The proved offset ceiling is untouched. The scanner recorded zero ceiling breaches on the three regimes it ran.
