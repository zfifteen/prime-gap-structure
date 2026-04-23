# Square-Phase Handoff

This note records the finding that current-gap square-phase depletion carries
across one gap on the `d(n)=4` winner surface.

## Finding

The strongest supported claim is:

on gaps whose current exact next-gap minimum is `d(n)=4`, the fraction of the
winner-to-next-prime-square corridor consumed before the gap closes predicts
the next gap's return to the odd-semiprime triad.

Low square-phase utilization is followed by more next-gap triad returns.
High square-phase utilization is followed by fewer triad returns and more
higher-divisor or even-semiprime next-gap states.

This is not explained away by the obvious current-gap geometry labels alone.
The lift survives after matching on:

- current carrier family
- current peak offset
- current first wheel-open offset
- current gap width
- current right-prime residue modulo `30`

## Exact Executed Surface

Artifacts:

- [gwr_square_phase_handoff_summary.json](../../output/gwr_square_phase_handoff_summary.json)
- [gwr_square_phase_handoff_strata.csv](../../output/gwr_square_phase_handoff_strata.csv)
- source catalog:
  [gwr_dni_gap_type_catalog_details.csv](../../output/gwr_dni_gap_type_catalog_details.csv)
- runner:
  [gwr_square_phase_handoff_probe.py](../../benchmarks/python/predictor/gwr_square_phase_handoff_probe.py)
- tests:
  [test_gwr_square_phase_handoff_probe.py](../../tests/python/predictor/test_gwr_square_phase_handoff_probe.py)

The committed run uses:

- exact baseline through right prime `<= 10^6`
- sampled `256`-gap windows at each decade anchor from `10^7` through `10^18`

The executed transition counts are:

- exact baseline `d=4` transitions: `58,304`
- sampled `10^7 .. 10^18` `d=4` transitions: `2,413`
- total measured `d=4` transitions: `60,717`

## Definition

Let:

- `w` be the current exact `d=4` winner
- `q^+` be the current next right prime
- `s` be the next prime square above `w`

Define square-phase utilization by

$$u_{\square} = \frac{q^+ - w}{s - w}.$$

This is the fraction of the winner-to-square corridor that the current gap
uses before the right prime arrives.

Low `u_square` means the current gap closes early relative to the next prime
square.
High `u_square` means the current gap runs much farther toward that square
ceiling before closing.

## Measured Support

### Exact Baseline Through `10^6`

The unmatched tail split already points in one direction:

- low-utilization tail next-triad share: `59.62%`
- high-utilization tail next-triad share: `55.75%`

After matching on carrier family, peak offset, first-open offset, gap width,
and residue modulo `30`, the lift remains positive:

- low half next-triad share: `58.61%`
- high half next-triad share: `56.93%`
- matched lift: `1.68` percentage points
- matched strata: `507`
- matched weight per side: `28,346`

On this exact baseline, the high-utilization tail also carries more
prime-square and higher-divisor next states than the low-utilization tail.

### Sampled Windows `10^7 .. 10^18`

The same direction strengthens on the pooled decade windows:

- low-utilization tail next-triad share: `70.95%`
- high-utilization tail next-triad share: `59.96%`

Under the same residue-controlled matched split:

- low half next-triad share: `69.15%`
- high half next-triad share: `62.06%`
- matched lift: `7.09` percentage points
- matched strata: `55`
- matched weight per side: `282`

So the sign does not flip when the current gap is matched against the obvious
local shape controls. The effect survives that attack and gets larger on the
pooled higher-scale surface.

## Reading

The non-obvious part is that the next gap is not behaving as if only its own
opening residue and width matter.

The current `d=4` carrier leaves a measurable one-gap memory in the system.
If the current winner arrived early relative to the next prime square, the
next gap is more likely to fall back into the low-divisor odd-semiprime triad.
If the current gap spent more of that square corridor before closing, the next
gap is more likely to land outside that triad.

This is a handoff law, not a within-gap winner law.
It says the current square-phase state helps sort the next gap's coarse regime.

## Decision Rule

On the current `d=4` winner surface:

- if `u_square` falls in the lower half of its matched local stratum, expect a
  higher next-gap odd-semiprime-triad rate
- if `u_square` falls in the upper half, expect a lower triad rate and a
  thicker higher-divisor or even-semiprime share

So a next-gap regime model should not treat all current `d=4` gaps as one
state. It should at least split them by square-phase utilization.

## Scope

This is a one-gap carryover statement on the current `d=4` winner surface
measured in this repository.

It does not claim a universal theorem for every current divisor class, and it
does not by itself predict the exact next winner. What it provides is a
surprising, measurable state variable that survives local matching and changes
the next-gap regime odds in a consistent direction.
